# -*- coding: utf-8 -*-
"""
SQLite 持久化缓存层。
提供公司别名解析、数据缓存（24h TTL）、后台异步刷新。
"""

import json
import logging
import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── 数据库路径 ────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(  # src/company_lookup/db/ → src/ → 项目根
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
DB_PATH = os.path.join(_PROJECT_ROOT, "company_data.db")

# ── 缓存 TTL ──────────────────────────────────────────
CACHE_TTL_HOURS = 24  # 缓存有效期

# ── 线程锁 ────────────────────────────────────────────
_write_lock = threading.Lock()


# ═══════════════════════════════════════════════════════
#  数据库初始化
# ═══════════════════════════════════════════════════════

def _get_conn() -> sqlite3.Connection:
    """获取数据库连接（自动创建表）。"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection):
    """创建表（如不存在）。"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,          -- 规范名
            aliases     TEXT    NOT NULL DEFAULT '[]',     -- JSON 数组，如 ["vivo","维沃"]
            created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS company_cache (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id  INTEGER NOT NULL UNIQUE,           -- 一个公司只有一条缓存记录
            data_json   TEXT    NOT NULL,                   -- 完整数据（JSON）
            fetched_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            expires_at  TEXT    NOT NULL,                   -- 过期时间
            FOREIGN KEY (company_id) REFERENCES companies(id)
        );

        CREATE TABLE IF NOT EXISTS query_log (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            query               TEXT    NOT NULL,
            matched_company_id  INTEGER,
            matched_name        TEXT,
            cache_hit           INTEGER NOT NULL DEFAULT 0,
            response_time_ms    INTEGER NOT NULL DEFAULT 0,
            created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
        CREATE INDEX IF NOT EXISTS idx_cache_expires ON company_cache(expires_at);
    """)
    conn.commit()


# ═══════════════════════════════════════════════════════
#  种子数据：从 BRAND_MAPPING 预填别名
# ═══════════════════════════════════════════════════════

def _seed_known_companies():
    """将 entity_resolver.BRAND_MAPPING 中的别名写入 companies 表。"""
    try:
        from ..services.entity_resolver import BRAND_MAPPING
    except ImportError:
        return  # 首次初始化时可能还没加载完

    # 按规范名聚合别名
    alias_map: Dict[str, List[str]] = {}
    for alias, full_name in BRAND_MAPPING.items():
        if alias == full_name:
            continue  # 跳过自身
        alias_map.setdefault(full_name, []).append(alias)
        # 同时添加小写变体
        lower = alias.lower()
        if lower != alias:
            alias_map.setdefault(full_name, []).append(lower)

    if not alias_map:
        return

    conn = _get_conn()
    try:
        for full_name, aliases in alias_map.items():
            existing = conn.execute(
                "SELECT id, aliases FROM companies WHERE name = ?", (full_name,)
            ).fetchone()

            if existing:
                # 合并已有别名
                existing_aliases = set(json.loads(existing["aliases"]))
                merged = sorted(existing_aliases | set(aliases))
                conn.execute(
                    "UPDATE companies SET aliases = ?, updated_at = datetime('now','localtime') WHERE id = ?",
                    (json.dumps(merged, ensure_ascii=False), existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT OR IGNORE INTO companies (name, aliases) VALUES (?, ?)",
                    (full_name, json.dumps(aliases, ensure_ascii=False)),
                )
        conn.commit()
    except Exception as e:
        logger.warning(f"种子数据写入失败: {e}")
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════
#  缓存操作
# ═══════════════════════════════════════════════════════

class DatabaseCache:
    """SQLite 持久化缓存。所有操作线程安全。"""

    def __init__(self):
        # 首次使用时尝试写入种子数据
        try:
            _seed_known_companies()
        except Exception:
            pass

    # ── 别名解析 ────────────────────────────────────

    def resolve_alias(self, query: str) -> Optional[str]:
        """
        解析用户输入 → 规范公司名。
        匹配规则：先精确匹配 name，再搜索 aliases JSON（不区分大小写）。
        """
        query_lower = query.lower()
        conn = _get_conn()
        try:
            # 1. 精确匹配规范名（不区分大小写）
            rows = conn.execute("SELECT name FROM companies").fetchall()
            for r in rows:
                if r["name"].lower() == query_lower:
                    return r["name"]

            # 2. 在 aliases 中搜索（不区分大小写）
            rows = conn.execute(
                "SELECT name, aliases FROM companies"
            ).fetchall()
            for r in rows:
                aliases = json.loads(r["aliases"])
                if any(a.lower() == query_lower for a in aliases):
                    return r["name"]

            return None
        finally:
            conn.close()

    def get_or_create_company(self, name: str) -> int:
        """
        获取或创建 company 记录，返回 company_id。
        同时自动将 BRAND_MAPPING 中的别名关联到此公司。
        """
        conn = _get_conn()
        try:
            row = conn.execute(
                "SELECT id FROM companies WHERE name = ?", (name,)
            ).fetchone()
            if row:
                return row["id"]

            # 创建新记录时，尝试从 BRAND_MAPPING 找别名
            aliases = []
            try:
                from ..services.entity_resolver import BRAND_MAPPING
                for alias, full_name in BRAND_MAPPING.items():
                    if full_name == name and alias != name:
                        aliases.append(alias)
            except ImportError:
                pass

            conn.execute(
                "INSERT INTO companies (name, aliases) VALUES (?, ?)",
                (name, json.dumps(aliases, ensure_ascii=False)),
            )
            conn.commit()
            return conn.execute(
                "SELECT id FROM companies WHERE name = ?", (name,)
            ).fetchone()["id"]
        finally:
            conn.close()

    # ── 数据缓存 ────────────────────────────────────

    def get_cached_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存数据。
        返回 None = 无缓存或已过期。
        """
        conn = _get_conn()
        try:
            row = conn.execute("""
                SELECT c.data_json, c.fetched_at, c.expires_at, co.name
                FROM company_cache c
                JOIN companies co ON co.id = c.company_id
                WHERE co.name = ?
            """, (company_name,)).fetchone()

            if not row:
                return None

            # 检查是否过期
            expires_at = row["expires_at"]
            if expires_at and expires_at <= datetime.now().isoformat():
                logger.info(f"[DB Cache EXPIRED] {company_name} (expired at {expires_at})")
                return None

            data = json.loads(row["data_json"])
            data["_cache_fetched_at"] = row["fetched_at"]
            data["_cache_expires_at"] = row["expires_at"]
            return data
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None
        finally:
            conn.close()

    def get_cached_data_stale_ok(self, company_name: str) -> Tuple[Optional[Dict], bool]:
        """
        获取缓存数据（过期也返回）。
        返回 (data, is_stale)。
        """
        conn = _get_conn()
        try:
            row = conn.execute("""
                SELECT c.data_json, c.fetched_at, c.expires_at, co.name
                FROM company_cache c
                JOIN companies co ON co.id = c.company_id
                WHERE co.name = ?
            """, (company_name,)).fetchone()

            if not row:
                return None, False

            data = json.loads(row["data_json"])
            data["_cache_fetched_at"] = row["fetched_at"]
            data["_cache_expires_at"] = row["expires_at"]

            expires_at = row["expires_at"]
            is_stale = expires_at and expires_at <= datetime.now().isoformat()
            return data, is_stale
        except Exception as e:
            logger.warning(f"读取缓存(含过期)失败: {e}")
            return None, False
        finally:
            conn.close()

    def set_cached_data(self, company_name: str, data: Dict[str, Any]):
        """写入缓存数据（覆盖旧数据）。"""
        company_id = self.get_or_create_company(company_name)
        now = datetime.now()
        expires_at = now + timedelta(hours=CACHE_TTL_HOURS)

        # 移除内部字段
        data_to_store = {k: v for k, v in data.items() if not k.startswith("_cache_")}

        conn = _get_conn()
        try:
            # 使用 REPLACE 确保唯一性（company_id 有 UNIQUE 约束）
            conn.execute("""
                INSERT OR REPLACE INTO company_cache
                    (company_id, data_json, fetched_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                company_id,
                json.dumps(data_to_store, ensure_ascii=False, default=str),
                now.isoformat(),
                expires_at.isoformat(),
            ))
            conn.commit()
            logger.info(f"[DB Cache STORE] {company_name} ({len(json.dumps(data_to_store, default=str))}B)")
        except Exception as e:
            logger.error(f"写入缓存失败: {e}")
        finally:
            conn.close()

    def invalidate(self, company_name: Optional[str] = None):
        """清除缓存。"""
        conn = _get_conn()
        try:
            if company_name:
                company_id = conn.execute(
                    "SELECT id FROM companies WHERE name = ?", (company_name,)
                ).fetchone()
                if company_id:
                    conn.execute("DELETE FROM company_cache WHERE company_id = ?", (company_id["id"],))
                    logger.info(f"[DB Cache INVALIDATE] {company_name}")
            else:
                conn.execute("DELETE FROM company_cache")
                logger.info("[DB Cache INVALIDATE] ALL")
            conn.commit()
        finally:
            conn.close()

    # ── 查询日志 ────────────────────────────────────

    def log_query(self, query: str, matched_name: str, cache_hit: bool, response_time_ms: int):
        """记录查询日志。"""
        connected_company_id = None
        conn = _get_conn()
        try:
            row = conn.execute(
                "SELECT id FROM companies WHERE name = ?", (matched_name,)
            ).fetchone()
            if row:
                connected_company_id = row["id"]

            conn.execute(
                "INSERT INTO query_log (query, matched_company_id, matched_name, cache_hit, response_time_ms) "
                "VALUES (?, ?, ?, ?, ?)",
                (query, connected_company_id, matched_name, 1 if cache_hit else 0, response_time_ms),
            )
            conn.commit()
        finally:
            conn.close()

    # ── 诊断 ────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        """返回缓存统计。"""
        conn = _get_conn()
        try:
            total_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            cached = conn.execute("SELECT COUNT(*) FROM company_cache").fetchone()[0]
            expired = conn.execute(
                "SELECT COUNT(*) FROM company_cache WHERE expires_at <= datetime('now','localtime')"
            ).fetchone()[0]
            recent_queries = conn.execute(
                "SELECT COUNT(*) FROM query_log WHERE created_at >= datetime('now','-1 day')"
            ).fetchone()[0]
            return {
                "total_companies": total_companies,
                "cached": cached,
                "expired": expired,
                "fresh": cached - expired,
                "queries_last_24h": recent_queries,
            }
        finally:
            conn.close()


# 全局单例
db_cache = DatabaseCache()

# -*- coding: utf-8 -*-
"""
企业知识库数据库（company_knowledge.db）
结构化存储 + 采集任务队列，区别于缓存层（company_data.db）。
"""

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── 数据库路径 ────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(  # services/ → src/ → 项目根
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DB_PATH = os.path.join(_PROJECT_ROOT, "company_knowledge.db")

_write_lock = threading.Lock()


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _ensure_tables(conn)
    return conn


def _ensure_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_name  TEXT    UNIQUE NOT NULL,
            aliases         TEXT    NOT NULL DEFAULT '[]',
            industry        TEXT    DEFAULT '',
            province        TEXT    DEFAULT '',
            city            TEXT    DEFAULT '',
            scale           TEXT    DEFAULT '',
            status          TEXT    DEFAULT '',
            hotness         TEXT    DEFAULT 'medium',
            discovery_source TEXT   DEFAULT '',
            query_count     INTEGER DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_verified_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS company_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id  INTEGER NOT NULL,
            data_type   TEXT NOT NULL,
            content     TEXT NOT NULL,
            source      TEXT DEFAULT '',
            confidence  REAL DEFAULT 0.8,
            fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            UNIQUE(company_id, data_type, source)
        );

        CREATE TABLE IF NOT EXISTS fetch_tasks (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'pending',
            priority        INTEGER NOT NULL DEFAULT 0,
            retry_count     INTEGER DEFAULT 0,
            error_msg       TEXT    DEFAULT '',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at    TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS fetch_log (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id             INTEGER,
            company_id          INTEGER,
            source              TEXT,
            success             BOOLEAN,
            response_time_ms    INTEGER DEFAULT 0,
            data_size_bytes     INTEGER DEFAULT 0,
            error_msg           TEXT DEFAULT '',
            fetched_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    # 迁移：为老表添加新字段（如果不存在）
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN hotness TEXT DEFAULT 'medium'")
    except sqlite3.OperationalError:
        pass  # 字段已存在
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN discovery_source TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN query_count INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN province TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    # 自动补全 province 字段（基于 city → province 映射）
    _auto_fill_province(conn)


# 城市 → 省份映射表
CITY_TO_PROVINCE_MAP = {
    "北京": "北京市", "上海": "上海市", "天津": "天津市", "重庆": "重庆市",
    "广州": "广东省", "深圳": "广东省", "珠海": "广东省", "佛山": "广东省",
    "东莞": "广东省", "惠州": "广东省", "中山": "广东省", "汕头": "广东省",
    "杭州": "浙江省", "宁波": "浙江省", "温州": "浙江省", "嘉兴": "浙江省",
    "绍兴": "浙江省", "金华": "浙江省", "台州": "浙江省", "湖州": "浙江省",
    "南京": "江苏省", "苏州": "江苏省", "无锡": "江苏省", "常州": "江苏省",
    "南通": "江苏省", "徐州": "江苏省", "扬州": "江苏省", "镇江": "江苏省",
    "成都": "四川省", "绵阳": "四川省",
    "武汉": "湖北省", "宜昌": "湖北省",
    "长沙": "湖南省", "株洲": "湖南省", "湘潭": "湖南省",
    "厦门": "福建省", "福州": "福建省", "泉州": "福建省",
    "合肥": "安徽省", "芜湖": "安徽省",
    "青岛": "山东省", "济南": "山东省", "烟台": "山东省", "潍坊": "山东省",
    "西安": "陕西省", "咸阳": "陕西省",
    "郑州": "河南省", "洛阳": "河南省",
    "石家庄": "河北省", "唐山": "河北省",
    "沈阳": "辽宁省", "大连": "辽宁省",
    "长春": "吉林省",
    "哈尔滨": "黑龙江省",
    "南昌": "江西省", "九江": "江西省",
    "太原": "山西省",
    "贵阳": "贵州省",
    "昆明": "云南省",
    "兰州": "甘肃省",
    "南宁": "广西壮族自治区", "桂林": "广西壮族自治区", "柳州": "广西壮族自治区",
    "海口": "海南省", "三亚": "海南省",
    "呼和浩特": "内蒙古自治区", "包头": "内蒙古自治区",
    "乌鲁木齐": "新疆维吾尔自治区",
    "拉萨": "西藏自治区",
    "银川": "宁夏回族自治区",
    "西宁": "青海省",
    "香港": "香港特别行政区",
    "澳门": "澳门特别行政区",
}


def _city_to_province(city: str) -> str:
    """根据城市名推省份。"""
    if not city:
        return ""
    # 排除占位文本
    placeholders = ["暂无公开数据", "未公开", "未知", "无", "none", ""]
    if city.strip() in placeholders or city.strip().lower() in placeholders:
        return ""
    # 精确匹配
    p = CITY_TO_PROVINCE_MAP.get(city)
    if p:
        return p
    # 模糊匹配
    for c, p in CITY_TO_PROVINCE_MAP.items():
        if c in city or city in c:
            return p
    return ""


def _auto_fill_province(conn):
    """根据城市自动补全省份字段（使用共享 CITY_TO_PROVINCE_MAP）。"""
    rows = conn.execute(
        "SELECT id, city FROM companies WHERE city != '' AND (province IS NULL OR province = '')"
    ).fetchall()
    fixed = 0
    for r in rows:
        province = _city_to_province(r["city"])
        if province:
            conn.execute("UPDATE companies SET province=? WHERE id=?", (province, r["id"]))
            fixed += 1
    if fixed:
        conn.commit()
        import logging
        logging.getLogger(__name__).info(f"[Province] 自动补全了 {fixed} 家公司的省份")


class KnowledgeDB:
    """企业知识库数据库操作。"""

    # ── 公司主表 ────────────────────────────────────

    def upsert_company(self, canonical_name: str, aliases: List[str] = None,
                       industry: str = "", scale: str = "", city: str = "",
                       status: str = "", hotness: str = "medium",
                       discovery_source: str = "",
                       province: str = "") -> int:

        conn = _get_conn()
        try:
            # 自动推省份
            if not province and city:
                province = _city_to_province(city)

            existing = conn.execute(
                "SELECT id, aliases FROM companies WHERE canonical_name = ?",
                (canonical_name,)
            ).fetchone()
            if existing:
                existing_aliases = set(json.loads(existing["aliases"]))
                new_aliases = set(aliases or [])
                merged = sorted(existing_aliases | new_aliases)
                conn.execute("""
                    UPDATE companies SET aliases=?, industry=?, scale=?, city=?, status=?,
                        hotness=?, discovery_source=?, province=?,
                        updated_at=CURRENT_TIMESTAMP, last_verified_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (json.dumps(merged, ensure_ascii=False), industry, scale, city, status,
                     hotness, discovery_source, province, existing["id"]))
                conn.commit()
                return existing["id"]
            else:
                cur = conn.execute("""
                    INSERT INTO companies (canonical_name, aliases, industry, scale, city, status, hotness, discovery_source, province, last_verified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (canonical_name, json.dumps(aliases or [], ensure_ascii=False),
                      industry, scale, city, status, hotness, discovery_source, province))
                conn.commit()
                return cur.lastrowid
        finally:
            conn.close()

    def find_company(self, query: str) -> Optional[Dict]:
        """通过规范名或别名查找公司。返回公司记录 dict 或 None。"""
        conn = _get_conn()
        try:
            # 精确匹配规范名
            row = conn.execute(
                "SELECT * FROM companies WHERE canonical_name = ?", (query,)
            ).fetchone()
            if row:
                return dict(row)

            # 别名匹配
            rows = conn.execute("SELECT * FROM companies").fetchall()
            for r in rows:
                aliases = json.loads(r["aliases"])
                if query in aliases:
                    return dict(r)

            # 模糊匹配
            for r in rows:
                if query in r["canonical_name"] or r["canonical_name"] in query:
                    return dict(r)

            return None
        finally:
            conn.close()

    def get_company_freshness(self, company_id: int) -> Tuple[int, int, int]:
        """返回 (fresh_days, stale_days, total_days) 含动态 TTL。
        
        高频公司 (hot):  新鲜窗口 3天，刷新窗口 14天
        常规公司 (normal): 新鲜窗口 7天，刷新窗口 30天
        低频公司 (cold):  新鲜窗口 14天，刷新窗口 60天
        """
        conn = _get_conn()
        try:
            row = conn.execute("""
                SELECT last_verified_at FROM companies WHERE id=?
            """, (company_id,)).fetchone()
            if not row or not row["last_verified_at"]:
                return (0, 0, 0)
            verified = datetime.strptime(row["last_verified_at"][:19], "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            days = (now - verified).days

            # 动态 TTL
            freq = self.get_frequency_bucket(company_id)
            if freq == "hot":
                fresh_limit = 3
                stale_limit = 14
            elif freq == "cold":
                fresh_limit = 14
                stale_limit = 60
            else:
                fresh_limit = 7
                stale_limit = 30

            if days <= fresh_limit:
                return (fresh_limit - days, 0, days)
            elif days <= stale_limit:
                return (0, days - fresh_limit, days)
            else:
                return (0, stale_limit - fresh_limit, days)
        finally:
            conn.close()

    def increment_query_count(self, company_id: int):
        """增加公司查询次数。"""
        conn = _get_conn()
        try:
            conn.execute("""
                UPDATE companies SET query_count = COALESCE(query_count, 0) + 1
                WHERE id=?
            """, (company_id,))
            conn.commit()
        finally:
            conn.close()

    def get_frequency_bucket(self, company_id: int) -> str:
        """
        根据查询频率返回热度分类: 'hot' / 'normal' / 'cold'
        hot = 查询频率前 20%
        cold = 查询频率后 20%
        normal = 中间
        """
        conn = _get_conn()
        try:
            row = conn.execute("SELECT query_count FROM companies WHERE id=?", (company_id,)).fetchone()
            if not row or row["query_count"] is None or row["query_count"] == 0:
                return "cold"

            total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            if total < 5:
                return "normal"

            count = row["query_count"]
            less_than = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE COALESCE(query_count,0) < ?", (count,)
            ).fetchone()[0]
            pct = less_than / total * 100

            if pct >= 80:
                return "hot"
            elif pct <= 20:
                return "cold"
            else:
                return "normal"
        finally:
            conn.close()

    # ── 公司数据 ────────────────────────────────────

    def get_company_data(self, company_id: int) -> Dict[str, Dict]:
        """获取公司所有维度的数据。返回 {data_type: {content, source, confidence}}。"""
        conn = _get_conn()
        try:
            rows = conn.execute(
                "SELECT data_type, content, source, confidence, fetched_at FROM company_data WHERE company_id=?",
                (company_id,)
            ).fetchall()
            result = {}
            for r in rows:
                try:
                    parsed = json.loads(r["content"])
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"company_data JSON 解析失败: company_id={company_id}, data_type={r['data_type']}, content_preview={str(r['content'])[:100]}")
                    continue
                result[r["data_type"]] = {
                    "content": parsed,
                    "source": r["source"],
                    "confidence": r["confidence"],
                    "fetched_at": r["fetched_at"],
                }
            return result
        finally:
            conn.close()

    def set_company_data(self, company_id: int, data_type: str, content: Any,
                         source: str = "", confidence: float = 0.8):
        """写入一个维度的数据。"""
        conn = _get_conn()
        try:
            conn.execute("""
                INSERT OR REPLACE INTO company_data (company_id, data_type, content, source, confidence, fetched_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, data_type, json.dumps(content, ensure_ascii=False, default=str),
                  source, confidence))
            conn.commit()
        finally:
            conn.close()

    def has_complete_data(self, company_id: int, min_dimensions: int = 3) -> bool:
        """检查公司是否有至少 N 个维度的完整数据。"""
        conn = _get_conn()
        try:
            # 算上 distilled 也算一个维度
            count = conn.execute(
                "SELECT COUNT(DISTINCT data_type) FROM company_data WHERE company_id=?",
                (company_id,)
            ).fetchone()[0]
            return count >= min_dimensions
        finally:
            conn.close()

    def get_distilled(self, company_id: int) -> Optional[Dict]:
        """获取蒸馏数据（如果存在）。"""
        conn = _get_conn()
        try:
            row = conn.execute(
                "SELECT content, source, fetched_at FROM company_data "
                "WHERE company_id=? AND data_type='distilled'",
                (company_id,)
            ).fetchone()
            if row:
                try:
                    data = json.loads(row["content"])
                except (json.JSONDecodeError, TypeError):
                    logger.warning(f"distilled JSON 解析失败: company_id={company_id}, preview={str(row['content'])[:100]}")
                    return None
                data["_source"] = row["source"]
                data["_fetched_at"] = row["fetched_at"]
                return data
            return None
        finally:
            conn.close()

    # ── 采集任务 ────────────────────────────────────

    def create_task(self, company_name: str, priority: int = 0) -> int:
        """创建采集任务，返回 task_id。如果已有 pending 任务则返回已有 id。"""
        conn = _get_conn()
        try:
            # 检查是否已有 pending 或 running 任务
            existing = conn.execute(
                "SELECT id FROM fetch_tasks WHERE company_name=? AND status IN ('pending','running')",
                (company_name,)
            ).fetchone()
            if existing:
                return existing["id"]

            cur = conn.execute(
                "INSERT INTO fetch_tasks (company_name, status, priority) VALUES (?, 'pending', ?)",
                (company_name, priority)
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def claim_task(self) -> Optional[Dict]:
        """领取下一个待处理任务（高优先级优先）。返回任务 dict 或 None。"""
        conn = _get_conn()
        try:
            row = conn.execute("""
                SELECT * FROM fetch_tasks
                WHERE status='pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """).fetchone()
            if row:
                conn.execute(
                    "UPDATE fetch_tasks SET status='running' WHERE id=?",
                    (row["id"],)
                )
                conn.commit()
                return dict(row)
            return None
        finally:
            conn.close()

    def complete_task(self, task_id: int, success: bool, error_msg: str = ""):
        """完成任务。"""
        conn = _get_conn()
        try:
            conn.execute("""
                UPDATE fetch_tasks SET status=?, error_msg=?, completed_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, ("completed" if success else "failed", error_msg, task_id))
            conn.commit()
        finally:
            conn.close()

    def fail_task_retry(self, task_id: int, error_msg: str, max_retries: int = 3):
        """失败后递增重试计数，超过上限则标记为 failed。"""
        conn = _get_conn()
        try:
            task = conn.execute(
                "SELECT retry_count FROM fetch_tasks WHERE id=?", (task_id,)
            ).fetchone()
            if task:
                new_count = task["retry_count"] + 1
                if new_count >= max_retries:
                    conn.execute(
                        "UPDATE fetch_tasks SET status='failed', retry_count=?, error_msg=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                        (new_count, error_msg, task_id)
                    )
                else:
                    conn.execute(
                        "UPDATE fetch_tasks SET status='pending', retry_count=?, error_msg=? WHERE id=?",
                        (new_count, error_msg, task_id)
                    )
                conn.commit()
        finally:
            conn.close()

    def pending_task_count(self) -> int:
        """待处理任务数。"""
        conn = _get_conn()
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM fetch_tasks WHERE status='pending'"
            ).fetchone()[0]
        finally:
            conn.close()

    def cleanup_stale_tasks(self, max_retries: int = 3):
        """清理废弃任务。"""
        conn = _get_conn()
        try:
            conn.execute("""
                UPDATE fetch_tasks SET status='failed', error_msg='超过最大重试次数'
                WHERE status='pending' AND retry_count>=?
            """, (max_retries,))
            conn.execute("""
                DELETE FROM fetch_tasks
                WHERE status IN ('completed','failed')
                AND created_at < datetime('now', '-30 days')
            """)
            conn.commit()
        finally:
            conn.close()

    # ── 需要刷新的公司 ──────────────────────────────

    def get_stale_companies(self, max_days: int = 30) -> List[Dict]:
        """返回超过 N 天未核验的公司列表。"""
        conn = _get_conn()
        try:
            rows = conn.execute("""
                SELECT c.* FROM companies c
                WHERE c.last_verified_at IS NULL
                   OR c.last_verified_at < datetime('now', '-' || ? || ' days')
                ORDER BY c.last_verified_at ASC NULLS FIRST
                LIMIT 20
            """, (max_days,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # ── 统计 ────────────────────────────────────────

    def stats(self) -> Dict:
        """知识库统计。"""
        conn = _get_conn()
        try:
            total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            with_data = conn.execute(
                "SELECT COUNT(DISTINCT company_id) FROM company_data"
            ).fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM fetch_tasks WHERE status='pending'"
            ).fetchone()[0]
            stale = conn.execute("""
                SELECT COUNT(*) FROM companies
                WHERE last_verified_at < datetime('now', '-7 days')
                   OR last_verified_at IS NULL
            """).fetchone()[0]
            niche = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE discovery_source='niche'"
            ).fetchone()[0]
            hot_count = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE coalesce(query_count,0) > 0"
            ).fetchone()[0]
            top_10 = conn.execute(
                "SELECT canonical_name, query_count FROM companies WHERE coalesce(query_count,0) > 0 ORDER BY query_count DESC LIMIT 10"
            ).fetchall()
            return {
                "total_companies": total,
                "companies_with_data": with_data,
                "pending_tasks": pending,
                "stale_companies": stale,
                "niche_companies": niche,
                "queried_companies": hot_count,
                "top_queried": [{"name": r["canonical_name"], "count": r["query_count"]} for r in top_10],
            }
        finally:
            conn.close()

    def set_hotness(self, company_id: int, hotness: str = "medium",
                    discovery_source: str = ""):
        """更新热度标签和发现来源。"""
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE companies SET hotness=?, discovery_source=? WHERE id=?",
                (hotness, discovery_source, company_id)
            )
            conn.commit()
        finally:
            conn.close()


# 全局单例
knowledge_db = KnowledgeDB()

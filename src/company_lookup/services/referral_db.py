# -*- coding: utf-8 -*-
"""
Referral DB — referral_codes 表管理。
归属于 jobboard.db，与求职看板共用同一数据库文件。
"""
import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "jobboard.db")


def get_db() -> sqlite3.Connection:
    """获取 SQLite 连接，自动建表。"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS referral_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            company_name TEXT NOT NULL,
            platform TEXT NOT NULL CHECK(platform IN ('脉脉','知乎','用户提交','其他')),
            platform_url TEXT DEFAULT '',
            code TEXT NOT NULL,
            referral_link TEXT DEFAULT '',
            recruiter_name TEXT DEFAULT '',
            recruiter_title TEXT DEFAULT '',
            description TEXT DEFAULT '',
            positions TEXT DEFAULT '[]',
            posted_at TEXT,
            collected_at TEXT DEFAULT (datetime('now','localtime')),
            expires_at TEXT,
            status TEXT CHECK(status IN ('有效','可能已过期','已过期','待验证')) DEFAULT '待验证',
            source_type TEXT CHECK(source_type IN ('采集','用户提交','请求追踪')) DEFAULT '采集',
            expire_reports INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS referral_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_id INTEGER NOT NULL,
            feedback TEXT NOT NULL CHECK(feedback IN ('有效','已失效')),
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (code_id) REFERENCES referral_codes(id)
        )
    """)
    conn.commit()


def insert_referral(conn: sqlite3.Connection, data: dict) -> int:
    cursor = conn.execute("""
        INSERT INTO referral_codes
            (company_id, company_name, platform, platform_url, code, referral_link,
             recruiter_name, recruiter_title, description, positions,
             posted_at, status, source_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("company_id"),
        data["company_name"],
        data.get("platform", "其他"),
        data.get("platform_url", ""),
        data["code"],
        data.get("referral_link", ""),
        data.get("recruiter_name", ""),
        data.get("recruiter_title", ""),
        data.get("description", ""),
        data.get("positions", "[]"),
        data.get("posted_at"),
        data.get("status", "待验证"),
        data.get("source_type", "采集"),
    ))
    conn.commit()
    return cursor.lastrowid


def update_status(conn: sqlite3.Connection, code_id: int, status: str):
    conn.execute(
        "UPDATE referral_codes SET status=?, updated_at=datetime('now','localtime') WHERE id=?",
        (status, code_id),
    )
    conn.commit()


def add_feedback(conn: sqlite3.Connection, code_id: int, feedback: str):
    conn.execute(
        "INSERT INTO referral_feedback (code_id, feedback) VALUES (?, ?)",
        (code_id, feedback),
    )
    conn.execute(
        "UPDATE referral_codes SET expire_reports = expire_reports + 1, updated_at=datetime('now','localtime') WHERE id=?",
        (code_id,),
    )
    conn.commit()


def get_by_company(conn: sqlite3.Connection, company_name: str, limit: int = 20):
    cursor = conn.execute(
        "SELECT * FROM referral_codes WHERE company_name LIKE ? ORDER BY collected_at DESC LIMIT ?",
        (f"%{company_name}%", limit),
    )
    return [dict(r) for r in cursor.fetchall()]


def search(conn: sqlite3.Connection, keyword: str = "", category: str = "", limit: int = 50):
    query = "SELECT * FROM referral_codes WHERE 1=1"
    params = []
    if keyword:
        query += " AND (company_name LIKE ? OR description LIKE ? OR code LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    if category:
        query += " AND positions LIKE ?"
        params.append(f"%{category}%")
    query += " ORDER BY collected_at DESC LIMIT ?"
    params.append(limit)
    cursor = conn.execute(query, params)
    return [dict(r) for r in cursor.fetchall()]


def get_all_active(conn: sqlite3.Connection, limit: int = 100):
    cursor = conn.execute(
        "SELECT * FROM referral_codes WHERE status IN ('有效','待验证') ORDER BY collected_at DESC LIMIT ?",
        (limit,),
    )
    return [dict(r) for r in cursor.fetchall()]


def get_expired_feedback_count(conn: sqlite3.Connection, code_id: int) -> int:
    cursor = conn.execute(
        "SELECT COUNT(*) as cnt FROM referral_feedback WHERE code_id=? AND feedback='已失效'",
        (code_id,),
    )
    row = cursor.fetchone()
    return row["cnt"] if row else 0

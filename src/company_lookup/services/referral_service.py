# -*- coding: utf-8 -*-
"""
ReferralService — 内推码统一接口层。

路由（以及测试）只通过这个 Service 与内推码系统交互。
所有复杂逻辑（过期判定、去重、请求追踪入队）封装在此。
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from . import referral_db as db

logger = logging.getLogger(__name__)

# 有效期内推码超过此天数自动标为"可能已过期"
STALE_DAYS = 30
# 用户反馈超过此数量标记"已失效"
MAX_EXPIRE_REPORTS = 3

# 职位分类列表（用于前端筛选）
POSITION_CATEGORIES = [
    "技术", "产品", "设计", "运营",
    "市场", "销售", "职能", "其他",
]


def evaluate_expiry(code: dict) -> str:
    """
    评估单条内推码的过期状态。
    组合策略：时间阈值 + 用户反馈计数。
    返回 '有效' | '可能已过期' | '已过期'
    """
    # 用户反馈优先
    reports = code.get("expire_reports", 0)
    if reports >= MAX_EXPIRE_REPORTS:
        return "已过期"

    status = code.get("status", "待验证")
    if status == "已过期":
        return "已过期"

    # 时间推测
    collected_str = code.get("collected_at", "")
    if collected_str:
        try:
            # 尝试解析多种日期格式
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    collected = datetime.strptime(collected_str[:19], fmt)
                    break
                except ValueError:
                    continue
            else:
                # 解析失败，用当前时间
                collected = datetime.now()

            if datetime.now() - collected > timedelta(days=STALE_DAYS):
                return "可能已过期" if status != "已过期" else "已过期"
        except (ValueError, TypeError):
            pass

    return status


def get_by_company(company_name: str) -> List[Dict]:
    """获取某公司所有内推码，附带过期评估。"""
    conn = db.get_db()
    try:
        codes = db.get_by_company(conn, company_name)
        for code in codes:
            code["_status_display"] = evaluate_expiry(code)
            # 反序列化 positions
            if isinstance(code.get("positions"), str):
                try:
                    code["positions"] = json.loads(code["positions"])
                except (json.JSONDecodeError, TypeError):
                    code["positions"] = []
        return codes
    finally:
        conn.close()


def search(keyword: str = "", category: str = "") -> List[Dict]:
    """搜索内推码，附带过期评估。"""
    conn = db.get_db()
    try:
        codes = db.search(conn, keyword=keyword, category=category)
        for code in codes:
            code["_status_display"] = evaluate_expiry(code)
            if isinstance(code.get("positions"), str):
                try:
                    code["positions"] = json.loads(code["positions"])
                except (json.JSONDecodeError, TypeError):
                    code["positions"] = []
        return codes
    finally:
        conn.close()


def get_all_active() -> List[Dict]:
    """获取所有有效内推码。"""
    conn = db.get_db()
    try:
        codes = db.get_all_active(conn)
        for code in codes:
            code["_status_display"] = evaluate_expiry(code)
            if isinstance(code.get("positions"), str):
                try:
                    code["positions"] = json.loads(code["positions"])
                except (json.JSONDecodeError, TypeError):
                    code["positions"] = []
        return codes
    finally:
        conn.close()


def submit_entry(
    company_name: str,
    code: Optional[str] = None,
    platform: str = "用户提交",
    platform_url: str = "",
    referral_link: str = "",
    recruiter_name: str = "",
    recruiter_title: str = "",
    description: str = "",
    positions: Optional[List[str]] = None,
    posted_at: str = "",
) -> int:
    """
    统一提交入口。
    - code=None → 请求追踪（不存码，通知采集引擎）
    - code=有值 → 用户提交/采集入库
    返回新记录的 id。
    """
    conn = db.get_db()
    try:
        data = {
            "company_name": company_name,
            "platform": platform,
            "platform_url": platform_url,
            "code": code or "",
            "referral_link": referral_link,
            "recruiter_name": recruiter_name,
            "recruiter_title": recruiter_title,
            "description": description,
            "positions": json.dumps(positions or ["其他"], ensure_ascii=False),
            "posted_at": posted_at,
            "status": "待验证",
            "source_type": "用户提交" if code else "请求追踪",
        }
        if code:
            row_id = db.insert_referral(conn, data)
            logger.info(f"[Referral] 用户提交内推码 #{row_id}: {company_name} - {code}")
            return row_id
        else:
            logger.info(f"[Referral] 请求追踪: {company_name}")
            return 0
    finally:
        conn.close()


def report_expired(code_id: int) -> bool:
    """用户反馈内推码已失效。"""
    conn = db.get_db()
    try:
        db.add_feedback(conn, code_id, "已失效")
        reports = db.get_expired_feedback_count(conn, code_id)
        if reports >= MAX_EXPIRE_REPORTS:
            db.update_status(conn, code_id, "已过期")
        logger.info(f"[Referral] 反馈 #{code_id} 已失效 ({reports}/{MAX_EXPIRE_REPORTS})")
        return True
    except Exception as e:
        logger.error(f"[Referral] 反馈失败 #{code_id}: {e}")
        return False
    finally:
        conn.close()


def request_track(company_name: str) -> bool:
    """用户请求采集某公司的内推码。"""
    return submit_entry(company_name=company_name) == 0


def get_position_categories() -> List[str]:
    """获取职位分类列表。"""
    return POSITION_CATEGORIES

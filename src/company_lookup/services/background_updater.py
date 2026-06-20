# -*- coding: utf-8 -*-
"""
后台异步刷新模块。
当缓存过期时，先返回旧数据，后台线程刷新缓存。
"""

import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

# 正在刷新中的公司（防止重复刷新）
_refreshing: set = set()
_refresh_lock = threading.Lock()


def _do_refresh(company_name: str):
    """后台实际执行刷新。"""
    try:
        from ..services.aggregator import fetch_company_report_sync_no_ai
        from ..services.ai_analyzer import analyze_company

        logger.info(f"[Background Refresh] 开始刷新 {company_name}")

        # 1. 获取多源数据（无 AI）
        report = fetch_company_report_sync_no_ai(company_name)
        raw_data = {}
        from ..routes.company import _serialize_source_data
        for source in report.sources:
            if source.available and source.data:
                raw_data[source.id] = _serialize_source_data(source)

        # 2. AI 分析
        ai_result = analyze_company(company_name, raw_data) if raw_data else {"success": False, "error": "No data"}

        # 3. 组装数据
        data = {
            "company_name": company_name,
            "normalized_name": report.normalized_name or company_name,
            "raw_data": raw_data,
            "ai_result": ai_result,
            "data_sources": [s.id for s in report.sources if s.available],
        }

        # 4. 写入数据库缓存
        from ..db.cache_db import db_cache
        db_cache.set_cached_data(company_name, data)

        # 5. 也更新内存缓存
        from ..services.unified_data_service import UnifiedDataService
        svc = UnifiedDataService()
        svc._cache[company_name] = {
            "data": data,
            "expires": time.time() + svc._cache_ttl,
            "created": time.time(),
        }

        logger.info(f"[Background Refresh] 完成刷新 {company_name} ({len(raw_data)} data sources)")
    except Exception as e:
        logger.error(f"[Background Refresh] 刷新失败 {company_name}: {e}", exc_info=True)
    finally:
        with _refresh_lock:
            _refreshing.discard(company_name)


def trigger_background_refresh(company_name: str):
    """触发后台刷新（非阻塞）。"""
    with _refresh_lock:
        if company_name in _refreshing:
            logger.info(f"[Background Refresh] {company_name} 正在刷新中，跳过重复请求")
            return
        _refreshing.add(company_name)

    thread = threading.Thread(target=_do_refresh, args=(company_name,), daemon=True)
    thread.start()
    logger.info(f"[Background Refresh] 已启动后台线程刷新 {company_name}")

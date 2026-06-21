# -*- coding: utf-8 -*-
"""
ReferralCollector — 内推码后台采集引擎。

复用项目现有的 daemon-thread + stop_event 模式，
与 KnowledgeMaintainer / OptimizationEngine 结构一致。
"""
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

from . import referral_db as db
from .referral_service import evaluate_expiry, STALE_DAYS

logger = logging.getLogger(__name__)

# 采集周期（秒）
COLLECT_INTERVAL = 3600  # 每 1 小时采集一轮
# 热度阈值：只采集热度高于此值的公司
HOTNESS_THRESHOLD = 30
# 每轮最多采集的公司数
MAX_COMPANIES_PER_ROUND = 50


class ReferralCollector:
    """内推码后台采集引擎。"""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._scrapers: List = []
        self._stats: Dict = {
            "is_running": False,
            "started_at": None,
            "last_collect_time": None,
            "total_collected": 0,
            "total_errors": 0,
            "last_error": None,
            "crash_count": 0,
        }

    def set_scrapers(self, scrapers: List):
        """注入采集适配器列表。"""
        self._scrapers = scrapers

    # ═══════════════════════════════════════════════
    #  公共接口（与 Maintainer 模式一致）
    # ═══════════════════════════════════════════════

    def start(self):
        if self.is_running():
            logger.info("[ReferralCollector] 已在运行中")
            return
        self._stop_event.clear()
        self._stats["started_at"] = datetime.now().isoformat()
        self._stats["is_running"] = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("[ReferralCollector] ✅ 内推码采集引擎已启动")

    def stop(self):
        if not self.is_running():
            return
        self._stop_event.set()
        self._stats["is_running"] = False
        logger.info("[ReferralCollector] ⏹ 内推码采集引擎已停止")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> Dict:
        s = dict(self._stats)
        s["is_running"] = self.is_running()
        s["scraper_count"] = len(self._scrapers)
        return s

    # ═══════════════════════════════════════════════
    #  内部循环
    # ═══════════════════════════════════════════════

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self._collect_round()
                self._stats["last_collect_time"] = datetime.now().isoformat()
            except Exception as e:
                logger.exception(f"[ReferralCollector] 主循环异常: {e}")
                self._stats["last_error"] = f"{type(e).__name__}: {e}"
                self._stats["crash_count"] = self._stats.get("crash_count", 0) + 1
                crash_count = self._stats["crash_count"]
                backoff = min(10 * 3 ** (crash_count - 1), 300)
                logger.warning(f"[ReferralCollector] 第 {crash_count} 次崩溃，{backoff}s 后重试")
                self._stop_event.wait(backoff)
                continue

            self._stop_event.wait(COLLECT_INTERVAL)

    def _collect_round(self):
        """执行一轮采集。"""
        if not self._scrapers:
            logger.info("[ReferralCollector] 无采集适配器，跳过")
            return

        # 1. 获取需要采集的公司列表（热度高的 + 被请求追踪的）
        companies = self._get_target_companies()

        if not companies:
            logger.info("[ReferralCollector] 本轮无待采集公司")
            return

        logger.info(f"[ReferralCollector] 本轮采集 {len(companies)} 家公司")

        # 2. 每个适配器采集
        total_new = 0
        for scraper in self._scrapers:
            try:
                results = scraper.collect(companies)
                new_count = self._save_results(results, scraper.platform_name)
                total_new += new_count
                logger.info(f"[ReferralCollector] {scraper.platform_name}: 新增 {new_count} 条")
            except Exception as e:
                logger.error(f"[ReferralCollector] {scraper.platform_name} 采集失败: {e}")
                self._stats["total_errors"] += 1

        # 3. 更新过期状态
        self._refresh_expiry_status()

        self._stats["total_collected"] += total_new
        if total_new > 0:
            logger.info(f"[ReferralCollector] 本轮共新增 {total_new} 条内推码")

    def _get_target_companies(self) -> List[str]:
        """
        获取需要采集的公司列表。
        策略：知识库中热度高的 + 被请求追踪的。
        """
        companies = []

        # 从知识库获取热度高的公司
        try:
            from .knowledge_db import get_db as get_kdb
            kconn = get_kdb()
            try:
                cursor = kconn.execute(
                    "SELECT standard_name FROM companies WHERE hotness >= ? ORDER BY hotness DESC LIMIT ?",
                    (HOTNESS_THRESHOLD, MAX_COMPANIES_PER_ROUND),
                )
                companies.extend([r["standard_name"] for r in cursor.fetchall()])
            finally:
                kconn.close()
        except Exception as e:
            logger.warning(f"[ReferralCollector] 读取知识库失败: {e}")

        # 加上被请求追踪但尚未采集的公司
        conn = db.get_db()
        try:
            tracked = db.search(conn, keyword="", limit=200)
            tracked_names = {r["company_name"] for r in tracked if r.get("source_type") == "请求追踪"}
            if tracked_names:
                logger.info(f"[ReferralCollector] 请求追踪: {tracked_names}")
                companies.extend(list(tracked_names))
        finally:
            conn.close()

        # 去重
        seen = set()
        unique = []
        for c in companies:
            if c and c not in seen:
                seen.add(c)
                unique.append(c)

        return unique[:MAX_COMPANIES_PER_ROUND]

    def _save_results(self, results: List[Dict], platform: str) -> int:
        """将采集结果存入数据库（去重）。"""
        new_count = 0
        conn = db.get_db()
        try:
            for item in results:
                code = item.get("code", "")
                if not code:
                    continue
                # 去重：检查是否已存在相同 company + code
                existing = conn.execute(
                    "SELECT id FROM referral_codes WHERE company_name=? AND code=? AND platform=?",
                    (item.get("company_name", ""), code, platform),
                ).fetchone()
                if existing:
                    continue
                data = {
                    "company_name": item.get("company_name", ""),
                    "platform": platform,
                    "platform_url": item.get("platform_url", ""),
                    "code": code,
                    "referral_link": item.get("referral_link", ""),
                    "recruiter_name": item.get("recruiter_name", ""),
                    "recruiter_title": item.get("recruiter_title", ""),
                    "description": item.get("description", ""),
                    "positions": item.get("positions", "[]"),
                    "posted_at": item.get("posted_at", ""),
                    "status": "有效",
                    "source_type": "采集",
                }
                db.insert_referral(conn, data)
                new_count += 1
        finally:
            conn.close()
        return new_count

    def _refresh_expiry_status(self):
        """刷新所有内推码的过期状态。"""
        conn = db.get_db()
        try:
            codes = db.get_all_active(conn, limit=500)
            updated = 0
            for code in codes:
                new_status = evaluate_expiry(code)
                if new_status != code.get("status"):
                    db.update_status(conn, code["id"], new_status)
                    updated += 1
            if updated:
                logger.info(f"[ReferralCollector] 更新了 {updated} 条过期状态")
        finally:
            conn.close()


# 全局单例
collector = ReferralCollector()

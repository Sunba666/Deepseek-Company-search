# -*- coding: utf-8 -*-
"""
知识库自动维护引擎 — 后台守护线程。
职责：
  1. 验证关键字段（经营状态、重大新闻、融资）
  2. 刷新超过30天未更新的公司
  3. 检查数据完整性，补充缺漏字段
  4. 输出知识库健康报告
"""
import json
import logging
import random
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 维护周期（秒）
COMPLETENESS_INTERVAL = 3600       # 1小时检查完整性
STALE_REFRESH_INTERVAL = 21600     # 6小时刷新过期数据
HEALTH_REPORT_INTERVAL = 86400     # 每天出健康报告
VERIFY_INTERVAL = 600              # 10分钟验证刚查过的公司

# 蒸馏数据必须字段
REQUIRED_DISTILL_FIELDS = [
    "one_liner", "key_facts", "sentiment_top3",
    "risk_summary", "job_seeker_note",
]

# 关键字段（变化时需要通知）
CRITICAL_FIELDS = ["status", "registered_capital", "legal_person"]


class KnowledgeMaintainer:
    """知识库维护引擎 — 后台循环运行。"""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._stats = {
            "total_checks": 0,
            "verified": 0,
            "refreshed": 0,
            "completeness_fixed": 0,
            "reports": [],
            "last_health_report": None,
            "is_running": False,
            "started_at": None,
            "last_heartbeat": None,
        }
        # 待验证队列（公司名 → 时间戳）
        self._verify_queue: Dict[str, float] = {}

    # ═══════════════════════════════════════════════
    #  公共接口
    # ═══════════════════════════════════════════════

    def start(self):
        if self.is_running():
            logger.info("[Maintainer] 已在运行中")
            return
        self._stop_event.clear()
        self._stats["started_at"] = datetime.now().isoformat()
        self._stats["is_running"] = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("[Maintainer] ✅ 维护引擎已启动")

    def stop(self):
        if not self.is_running():
            return
        self._stop_event.set()
        self._stats["is_running"] = False
        logger.info("[Maintainer] ⏹ 维护引擎已停止")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> Dict:
        s = dict(self._stats)
        s["is_running"] = self.is_running()
        s["queue_size"] = len(self._verify_queue)
        return s

    def enqueue_verify(self, company_name: str):
        """加入待验证队列（查询后调用）。"""
        self._verify_queue[company_name] = time.time()
        # 限制队列大小
        if len(self._verify_queue) > 200:
            # 清除最旧的
            sorted_items = sorted(self._verify_queue.items(), key=lambda x: x[1])
            for k, _ in sorted_items[:50]:
                self._verify_queue.pop(k, None)

    # ═══════════════════════════════════════════════
    #  内部循环
    # ═══════════════════════════════════════════════

    def _run_loop(self):
        last_completeness = 0
        last_stale_refresh = 0
        last_health_report = 0

        while not self._stop_event.is_set():
            try:
                now = time.time()

                # 1. 处理验证队列（每10分钟）
                if self._verify_queue and (now - last_completeness) % VERIFY_INTERVAL < 60:
                    self._process_verify_queue()

                # 2. 完整性检查（每小时）
                if now - last_completeness > COMPLETENESS_INTERVAL:
                    self._check_completeness()
                    last_completeness = now

                # 3. 刷新过期数据（每6小时）
                if now - last_stale_refresh > STALE_REFRESH_INTERVAL:
                    self._refresh_stale_companies()
                    last_stale_refresh = now

                # 4. 健康报告（每天）
                if now - last_health_report > HEALTH_REPORT_INTERVAL:
                    report = self._generate_health_report()
                    self._stats["last_health_report"] = report
                    self._stats["reports"].append({
                        "time": datetime.now().isoformat(),
                        "report": report,
                    })
                    last_health_report = now
            except Exception as e:
                logger.exception(f"[Maintainer] 主循环异常: {e}")
                self._stats["last_error"] = f"{type(e).__name__}: {e}"
                self._stats["crash_count"] = self._stats.get("crash_count", 0) + 1
                crash_count = self._stats["crash_count"]
                # 指数退避：第一次 10s，然后 30s，然后 60s ...
                backoff = min(10 * 3 ** (crash_count - 1), 300)
                logger.warning(f"[Maintainer] 第 {crash_count} 次崩溃，{backoff}s 后重试")
                self._stop_event.wait(backoff)
                continue

            self._stop_event.wait(60)  # 每分钟唤醒一次
            # 心跳标记
            self._stats["last_heartbeat"] = datetime.now().isoformat()
            logger.debug("[Maintainer] [HEARTBEAT] alive")

    # ═══════════════════════════════════════════════
    #  1. 后台验证（关键字段变化检测）
    # ═══════════════════════════════════════════════

    def _process_verify_queue(self):
        """处理待验证队列（批量验证）。"""
        from ..services.knowledge_db import knowledge_db

        if not self._verify_queue:
            return

        batch = list(self._verify_queue.keys())[:10]
        for name in batch:
            if self._stop_event.is_set():
                return
            self._verify_company_fields(name)
            self._verify_queue.pop(name, None)
            self._stats["verified"] += 1
            time.sleep(0.2)

    def _verify_company_fields(self, company_name: str):
        """
        验证公司关键字段是否变化。
        检查经营状态、注册资本、法定代表人等关键工商信息。
        """
        from ..services.knowledge_db import knowledge_db

        company = knowledge_db.find_company(company_name)
        if not company:
            return

        company_id = company["id"]
        distilled = knowledge_db.get_distilled(company_id)
        if not distilled:
            return

        kf = distilled.get("key_facts", {})

        # 检查蒸馏数据中的关键字段是否有值
        changes = []
        for field in CRITICAL_FIELDS:
            if field not in kf or not kf.get(field):
                changes.append(field)

        if changes:
            logger.info(f"[Verify] {company_name} 缺关键字段: {changes}")
            # 标记需要刷新
            knowledge_db.create_task(company_name, priority=1)

        self._stats["total_checks"] += 1

    # ═══════════════════════════════════════════════
    #  2. 数据完整性检查
    # ═══════════════════════════════════════════════

    def _check_completeness(self):
        """检查所有公司数据完整性，补充缺漏。"""
        from ..services.knowledge_db import knowledge_db, _get_conn
        import sqlite3

        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        try:
            # 查出所有未蒸馏的公司
            distilled_ids = set(
                r[0] for r in conn.execute(
                    "SELECT DISTINCT company_id FROM company_data WHERE data_type='distilled'"
                ).fetchall()
            )
            all_companies = conn.execute(
                "SELECT id, canonical_name FROM companies ORDER BY id"
            ).fetchall()

            fixed = 0
            for r in all_companies:
                if self._stop_event.is_set():
                    break
                if r["id"] not in distilled_ids:
                    # 有数据但没蒸馏？触发蒸馏
                    data_count = conn.execute(
                        "SELECT COUNT(*) FROM company_data WHERE company_id=? AND data_type!='distilled'",
                        (r["id"],)
                    ).fetchone()[0]
                    if data_count >= 2:  # 至少有2个维度才蒸馏
                        knowledge_db.create_task(r["canonical_name"], priority=0)
                        fixed += 1
                    elif data_count == 0:
                        # 完全没数据的，标记采集
                        knowledge_db.create_task(r["canonical_name"], priority=0)
                        fixed += 1
                else:
                    # 已蒸馏但缺字段的
                    distilled_data = knowledge_db.get_distilled(r["id"])
                    if distilled_data:
                        missing = [f for f in REQUIRED_DISTILL_FIELDS
                                   if f not in distilled_data or not distilled_data.get(f)]
                        if missing:
                            logger.info(f"[Completeness] {r['canonical_name']} 缺 {missing}")
                            knowledge_db.create_task(r["canonical_name"], priority=0)
                            fixed += 1

            if fixed:
                logger.info(f"[Completeness] 创建了 {fixed} 个补充任务")
                self._stats["completeness_fixed"] += fixed
        finally:
            conn.close()

    # ═══════════════════════════════════════════════
    #  3. 刷新过期数据
    # ═══════════════════════════════════════════════

    def _refresh_stale_companies(self):
        """刷新超过30天未更新的公司数据。"""
        from ..services.knowledge_db import knowledge_db, _get_conn

        conn = _get_conn()
        try:
            stale = conn.execute("""
                SELECT id, canonical_name FROM companies
                WHERE last_verified_at < datetime('now', '-30 days')
                   OR last_verified_at IS NULL
                ORDER BY last_verified_at ASC
                LIMIT 20
            """).fetchall()
            conn.close()

            if not stale:
                logger.info("[Refresh] 无过期数据")
                return

            logger.info(f"[Refresh] 发现 {len(stale)} 家过期公司，提交刷新任务")
            for r in stale:
                if self._stop_event.is_set():
                    break
                from ..services.knowledge_collector import trigger_collection
                trigger_collection(r["canonical_name"], priority=0)
                self._stats["refreshed"] += 1
                time.sleep(0.1)
        except Exception as e:
            logger.warning(f"[Refresh] 异常: {e}")

    # ═══════════════════════════════════════════════
    #  4. 知识库健康报告
    # ═══════════════════════════════════════════════

    def _generate_health_report(self) -> Dict:
        """生成知识库健康报告。"""
        from ..services.knowledge_db import knowledge_db, _get_conn
        import sqlite3

        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        try:
            total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]

            # 行业分布
            ind_rows = conn.execute("""
                SELECT industry, COUNT(*) as c FROM companies
                WHERE industry IS NOT NULL AND industry != ''
                GROUP BY industry ORDER BY c DESC
            """).fetchall()
            industry_dist = {r["industry"]: r["c"] for r in ind_rows}
            no_industry = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE industry IS NULL OR industry=''"
            ).fetchone()[0]

            # 数据分布
            with_data = conn.execute(
                "SELECT COUNT(DISTINCT company_id) FROM company_data"
            ).fetchone()[0]
            with_distilled = conn.execute("""
                SELECT COUNT(DISTINCT company_id) FROM company_data WHERE data_type='distilled'
            """).fetchone()[0]

            # 维度覆盖
            dim_rows = conn.execute("""
                SELECT data_type, COUNT(DISTINCT company_id) as c
                FROM company_data GROUP BY data_type ORDER BY c DESC
            """).fetchall()
            dim_coverage = {r["data_type"]: r["c"] for r in dim_rows}

            # 新鲜度
            fresh = conn.execute("""
                SELECT COUNT(*) FROM companies
                WHERE last_verified_at >= datetime('now', '-7 days')
            """).fetchone()[0]
            stale_7_30 = conn.execute("""
                SELECT COUNT(*) FROM companies
                WHERE last_verified_at >= datetime('now', '-30 days')
                  AND last_verified_at < datetime('now', '-7 days')
            """).fetchone()[0]
            old = conn.execute("""
                SELECT COUNT(*) FROM companies
                WHERE last_verified_at < datetime('now', '-30 days')
                   OR last_verified_at IS NULL
            """).fetchone()[0]

            # 热度分布
            hot_rows = conn.execute("""
                SELECT hotness, COUNT(*) as c FROM companies GROUP BY hotness
            """).fetchall()
            hotness_dist = {r["hotness"] or "未标": r["c"] for r in hot_rows}

            # 发现来源
            src_rows = conn.execute("""
                SELECT discovery_source, COUNT(*) as c FROM companies
                GROUP BY discovery_source
            """).fetchall()
            source_dist = {r["discovery_source"] or "seed": r["c"] for r in src_rows}

            # 待处理任务
            pending = conn.execute(
                "SELECT COUNT(*) FROM fetch_tasks WHERE status='pending'"
            ).fetchone()[0]

            report = {
                "generated_at": datetime.now().isoformat(),
                "total_companies": total,
                "with_data": with_data,
                "with_distilled": with_distilled,
                "industry_distribution": industry_dist,
                "no_industry": no_industry,
                "dimension_coverage": dim_coverage,
                "freshness": {
                    "fresh_≤7d": fresh,
                    "stale_7_30d": stale_7_30,
                    "old_>30d": old,
                },
                "hotness_distribution": hotness_dist,
                "discovery_sources": source_dist,
                "pending_tasks": pending,
                "completeness_score": round(with_distilled / total * 100, 1) if total > 0 else 0,
                "dimension_avg": round(
                    conn.execute("""
                        SELECT AVG(dc) FROM (
                            SELECT COUNT(DISTINCT data_type) as dc
                            FROM company_data GROUP BY company_id
                        )
                    """).fetchone()[0], 1
                ) if with_data > 0 else 0,
            }
            return report
        finally:
            conn.close()


# 全局单例
maintainer = KnowledgeMaintainer()

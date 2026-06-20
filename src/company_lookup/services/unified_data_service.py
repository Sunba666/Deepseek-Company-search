"""Unified data service - knowledge-base-first query flow with freshness tiers.

Flow:
  1. Knowledge DB check (structured data)
     a. ≤7 days fresh → return directly (no network calls)
     b. 7-30 days → return + async refresh in background
     c. >30 days → return + mark "stale" 
  2. Cache check (raw cached data) — fallback
  3. Live fetch (cache miss + no knowledge)
  4. If company unknown → create async collection task → return "collecting" status
"""
import logging
import time
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class UnifiedDataService:
    """Singleton: knowledge-base-first query with multi-tier freshness."""

    _instance = None
    _cache: Dict[str, Dict] = {}
    _cache_ttl = 300  # in-memory 5 min

    _db_cache = None  # old cache db
    _kd = None  # knowledge db

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def db(self):
        if self._db_cache is None:
            from ..db.cache_db import db_cache
            self._db_cache = db_cache
        return self._db_cache

    @property
    def kd(self):
        if self._kd is None:
            from ..services.knowledge_db import knowledge_db
            self._kd = knowledge_db
        return self._kd

    def get_company_data(self, company_name: str, force_refresh: bool = False,
                         credit_data: dict = None) -> Dict[str, Any]:
        """Get company data. Knowledge-base-first, then cache, then live."""
        now = time.time()
        start = time.time()

        # ── 0. 知识库优先 ───────────────────────────
        if not force_refresh:
            result = self._try_knowledge_db(company_name)
            if result:
                return result

        # ── 1. 内存缓存 ──────────────────────────────
        if not force_refresh and company_name in self._cache:
            cached = self._cache[company_name]
            if now < cached["expires"]:
                logger.info(f"[MEM HIT] {company_name}")
                self._log_query(company_name, True, start)
                return cached["data"]

        # ── 2. SQLite 旧缓存 ────────────────────────
        if not force_refresh:
            db_data, is_stale = self.db.get_cached_data_stale_ok(company_name)
            if db_data is not None and not is_stale:
                logger.info(f"[DB HIT] {company_name}")
                self._cache[company_name] = {"data": db_data, "expires": now + self._cache_ttl, "created": now}
                self._log_query(company_name, True, start)
                return db_data
            if db_data is not None and is_stale:
                logger.info(f"[DB STALE] {company_name} — return old, async refresh")
                from .background_updater import trigger_background_refresh
                trigger_background_refresh(company_name)
                self._log_query(company_name, True, start)
                return db_data

        # ── 3. 未命中 → 全量采集 ────────────────────
        logger.info(f"[MISS] {company_name} — triggering collection...")

        # 先检查该名称是否有效
        from ..services.entity_resolver import BRAND_MAPPING
        from ..db.cache_db import db_cache
        from ..services.knowledge_collector import collect_company

        is_known = (
            company_name in BRAND_MAPPING
            or db_cache.resolve_alias(company_name) is not None
        )

        # ── 尝试同步采集（无论已知与否）──────────────
        # 未知公司也尝试实时采集，给用户带回结果而不是"采集中"
        logger.info(f"[MISS] {company_name} — collecting synchronously")
        collect_result = collect_company(company_name, priority=1)

        # 检查采集结果
        if collect_result.get("success") and collect_result.get("company_id"):
            company = self.kd.find_company(company_name)
            if company:
                kb_data = self._build_from_knowledge(company["id"], company_name, company["canonical_name"])
                if kb_data:
                    self._cache[company_name] = {"data": kb_data, "expires": now + self._cache_ttl, "created": now}
                    self._log_query(company_name, False, start)
                    # 注册查询频率
                    self._increment_query_count(company["id"])
                    return kb_data

        # 采集成功但知识库还没生效 → 用 live_fetch 兜底
        if collect_result.get("success"):
            logger.info(f"[MISS] {company_name} — collected but not in KB yet, live fetch")
            data = self._live_fetch(company_name, credit_data, start)
            # 仍标记到知识库
            return data

        # 完全失败 → 记录查询并返回失败
        logger.info(f"[MISS] {company_name} — collection failed, returning error")
        from .knowledge_collector import trigger_collection
        trigger_collection(company_name, priority=1)

        return {
            "company_name": company_name,
            "normalized_name": company_name,
            "raw_data": {},
            "ai_result": {"success": False, "collecting": True, "error": "正在采集中，请稍后再查"},
            "data_sources": [],
            "_collecting": True,
        }

    def _try_knowledge_db(self, company_name: str) -> Optional[Dict]:
        """尝试从知识库获取数据，含新鲜度判断。"""
        company = self.kd.find_company(company_name)
        if not company:
            return None

        company_id = company["id"]
        freshness = self.kd.get_company_freshness(company_id)
        fresh_days, stale_days, total_days = freshness

        logger.info(f"[KNOWLEDGE] {company_name} (fresh={fresh_days}d, stale={stale_days}d, total={total_days}d)")

        # 获取所有维度数据
        data_dict = self.kd.get_company_data(company_id)
        if not data_dict:
            return None

        kb_data = self._build_from_knowledge(company_id, company_name, company["canonical_name"], data_dict)

        # ── 加入后台验证队列（返回后异步验证关键字段） ──
        from ..services.knowledge_maintainer import maintainer
        maintainer.enqueue_verify(company["canonical_name"])

        if fresh_days > 0 or total_days <= 7:
            # ≤7天 → 直接返回
            logger.info(f"[KNOWLEDGE HIT] {company_name} (fresh, {total_days}d old)")
            self._cache[company_name] = {
                "data": kb_data, "expires": time.time() + self._cache_ttl, "created": time.time(),
            }
            self._log_query(company_name, True, time.time())
            self._increment_query_count(company_id)
            return kb_data
        elif stale_days > 0 or (7 < total_days <= 30):
            # 7-30天 → 返回旧数据 + 后台刷新
            logger.info(f"[KNOWLEDGE STALE] {company_name} ({total_days}d old) — return old, async refresh")
            from .background_updater import trigger_background_refresh
            trigger_background_refresh(company_name)
            kb_data["_freshness_warning"] = f"数据 {total_days} 天前采集，后台刷新中"
            self._cache[company_name] = {
                "data": kb_data, "expires": time.time() + self._cache_ttl, "created": time.time(),
            }
            self._increment_query_count(company_id)
            return kb_data
        else:
            # >30天 → 标记待更新
            logger.info(f"[KNOWLEDGE OLD] {company_name} ({total_days}d old) — 可能过时，创建刷新任务")
            from .knowledge_collector import trigger_collection
            trigger_collection(company["canonical_name"], priority=0)
            kb_data["_freshness_warning"] = f"⚠️ 数据超过 {total_days} 天未更新，可能已过时"
            self._increment_query_count(company_id)
            return kb_data

    def _build_from_knowledge(self, company_id: int, query_name: str,
                              canonical_name: str,
                              data_dict: Dict = None) -> Dict:
        """从知识库构建标准响应。优先使用蒸馏数据（0 AI token 消耗）。"""
        if data_dict is None:
            data_dict = self.kd.get_company_data(company_id)

        raw_data = {}
        for dtype, d in data_dict.items():
            raw_data[dtype] = d["content"]

        # ── 键名映射：知识库内部维度名 → 聚合器层期望的键名 ──
        _KEY_MAP = {
            "basic": "tianyacha",      # 企业工商/信用数据
            "culture": "reputation",    # 员工口碑
            "risk": "wenshu",           # 司法风险
            "sentiment": "sentiment",   # 舆情
            "salary": "salary",         # 薪资（已一致）
            "interview": "interview",   # 面试经验
            "ai_summary": "ai_summary", # AI分析
        }
        for internal_key, external_key in _KEY_MAP.items():
            if internal_key in raw_data and external_key != internal_key:
                raw_data[external_key] = raw_data[internal_key]

        company = self.kd.find_company(canonical_name) or {}
        basic = data_dict.get("basic", {}).get("content", {})
        fetched_at = data_dict.get("basic", {}).get("fetched_at", "")

        # ── 优先使用蒸馏数据 ─────────────────────────
        distilled = self.kd.get_distilled(company_id)
        if distilled and distilled.get("one_liner"):
            return self._render_distilled(canonical_name, distilled, company, fetched_at, raw_data)

        # ── 传统方式兜底 ─────────────────────────────
        return self._render_from_dimensions(canonical_name, data_dict, company, basic, fetched_at, raw_data)

    def _render_distilled(self, canonical_name: str, distilled: dict,
                          company: dict, fetched_at: str, raw_data: dict) -> Dict:
        """蒸馏数据渲染（0 AI token）。"""
        kf = distilled.get("key_facts", {})
        sentiments = distilled.get("sentiment_top3", [])
        risk = distilled.get("risk_summary", "")
        note = distilled.get("job_seeker_note", "")
        one_liner = distilled.get("one_liner", "")

        info_lines = []
        if kf.get("registered_capital"): info_lines.append(f"<strong>注册资本</strong>：{kf['registered_capital']}")
        if kf.get("legal_person"): info_lines.append(f"<strong>法定代表人</strong>：{kf['legal_person']}")
        if kf.get("founded"): info_lines.append(f"<strong>成立日期</strong>：{kf['founded']}")
        if kf.get("status"):
            badge = 'success' if kf['status'] == '存续' else 'danger'
            info_lines.append(f"<strong>经营状态</strong>：<span class='badge bg-{badge}'>{kf['status']}</span>")
        if kf.get("industry"): info_lines.append(f"<strong>行业</strong>：{kf['industry']}")
        if kf.get("city"): info_lines.append(f"<strong>总部</strong>：{kf['city']}")
        if kf.get("scale"): info_lines.append(f"<strong>规模</strong>：{kf['scale']}")

        s_html = ""
        if sentiments:
            items = "".join(f'<li class="mb-1"><i class="bi bi-chat-quote text-muted me-1"></i>{s["point"]} <small class="text-muted">— {s.get("source","")}</small></li>' for s in sentiments[:3])
            s_html = f'<ul class="list-unstyled small mb-0">{items}</ul>'

        r_html = ""
        if risk and risk not in ("暂无已知风险", ""):
            r_html = f'<div class="p-2 mt-1" style="background:var(--warning-bg);border-radius:var(--radius-sm);"><small><i class="bi bi-exclamation-triangle" style="color:var(--warning);"></i> {risk}</small></div>'

        n_html = ""
        if note:
            n_html = f'<div class="mt-2 small p-2" style="background:var(--primary-light);border-radius:var(--radius-sm);"><i class="bi bi-lightbulb" style="color:var(--primary);"></i> {note}</div>'

        src = "<strong>预采集知识库 · DeepSeek 蒸馏</strong>"
        if fetched_at:
            src += f" · 更新于 {fetched_at[:10]}"

        report_html = f"""
        <div class="card shadow-sm mb-3">
            <div class="card-body">
                <h5 class="mb-2"><i class="bi bi-building"></i> {canonical_name}</h5>
                <p class="text-muted mb-3" style="font-size:1.05rem;">{one_liner}</p>
                <div class="info-grid mb-3">
                    {'<div class="info-item">' + '</div><div class="info-item">'.join(info_lines) + '</div>' if info_lines else '<p class="text-muted">暂无详细数据</p>'}
                </div>
                {s_html}{r_html}{n_html}
                <div class="mt-3 small text-muted"><i class="bi bi-database"></i> 来源：{src}</div>
            </div>
        </div>"""

        ai_result = {"success": True, "company_name": canonical_name,
                     "summary": one_liner, "report_html": report_html,
                     "raw_data": raw_data, "data_sources": ["prebuilt_knowledge"],
                     "analysis_time": fetched_at or ""}
        return {"company_name": canonical_name, "normalized_name": canonical_name,
                "raw_data": raw_data, "ai_result": ai_result,
                "data_sources": ["prebuilt_knowledge"]}

    def _render_from_dimensions(self, canonical_name: str, data_dict: dict,
                                company: dict, basic: dict,
                                fetched_at: str, raw_data: dict) -> Dict:
        """从多个维度拼接报告（无蒸馏数据时兜底）。"""
        ai_summary = data_dict.get("ai_summary", {}).get("content", {})

        info_lines = []
        if basic.get("registered_capital"):
            info_lines.append(f"<strong>注册资本</strong>：{basic['registered_capital']}")
        if basic.get("paid_in_capital"):
            info_lines.append(f"<strong>实缴资本</strong>：{basic['paid_in_capital']}")
        if basic.get("legal_representative"):
            info_lines.append(f"<strong>法定代表人</strong>：{basic['legal_representative']}")
        if basic.get("establishment_date"):
            info_lines.append(f"<strong>成立日期</strong>：{basic['establishment_date']}")
        if basic.get("company_status"):
            badge = 'success' if basic['company_status'] == '存续' else 'danger'
            info_lines.append(f"<strong>经营状态</strong>：<span class='badge bg-{badge}'>{basic['company_status']}</span>")
        if company.get("industry"):
            info_lines.append(f"<strong>行业</strong>：{company['industry']}")
        if company.get("city"):
            info_lines.append(f"<strong>总部</strong>：{company['city']}")

        dim_labels = {"sentiment": "舆情口碑", "salary": "薪资福利", "risk": "司法风险",
                      "culture": "员工口碑", "interview": "面试经验", "ai_summary": "AI解读"}
        dim_tags = "".join(f"<span class='badge bg-info me-1'>{dim_labels.get(d, d)}</span>"
                           for d in data_dict if d in dim_labels)

        ai_html = ""
        if ai_summary and ai_summary.get("summary"):
            ai_html = f"""
            <div class="mt-3 p-3" style="background:var(--primary-light);border-radius:var(--radius-md);">
                <small class="text-muted d-block mb-1"><i class="bi bi-robot"></i> 求职者视角解读</small>
                <p class="mb-1" style="line-height:1.7;">{ai_summary['summary']}</p>
                <small class="text-muted">AI 生成于 {ai_summary.get('generated_at', '')[:10]}</small>
            </div>"""

        source_labels = set()
        for d in data_dict.values():
            src = d.get("source", "")
            if src in ("gsxt", "gsxt_mock"): source_labels.add("国家企业信用信息公示系统")
            elif src == "tianyacha": source_labels.add("天眼查")
            elif src in ("tavily", "deepseek_light"): source_labels.add("AI 分析")
            elif src == "wenshu": source_labels.add("司法数据")
            elif src == "mock": pass
            else: source_labels.add(src)

        report_html = f"""
        <div class="card shadow-sm mb-3">
            <div class="card-body">
                <h5 class="mb-3"><i class="bi bi-building"></i> {canonical_name}</h5>
                <div class="info-grid mb-2">
                    {'<div class="info-item">' + '</div><div class="info-item">'.join(info_lines) + '</div>' if info_lines else '<p class="text-muted">暂无工商信息</p>'}
                </div>
                {dim_tags}
                {'<small class="text-muted">数据采集于 ' + (fetched_at[:16] if fetched_at else '未知') + '</small>' if fetched_at else ''}
                {ai_html}
                <div class="mt-2 small text-muted"><i class="bi bi-database"></i> 数据来源：{'、'.join(f'<strong>{s}</strong>' for s in source_labels if s) or '知识库'}</div>
            </div>
        </div>"""

        ai_result = {"success": True, "company_name": canonical_name,
                     "summary": ai_summary.get("summary", "知识库数据") if ai_summary else "知识库数据",
                     "report_html": report_html, "raw_data": raw_data,
                     "data_sources": [d.get("source", "knowledge") for d in data_dict.values()],
                     "analysis_time": fetched_at or ""}
        return {"company_name": canonical_name, "normalized_name": canonical_name,
                "raw_data": raw_data, "ai_result": ai_result,
                "data_sources": [d.get("source", "knowledge") for d in data_dict.values()]}

    def get_company_data_cached_only(self, company_name: str) -> Optional[Dict]:
        """仅从缓存/知识库读取（不触发网络）。"""
        now = time.time()

        # Knowledge DB
        company = self.kd.find_company(company_name)
        if company and self.kd.has_complete_data(company["id"], min_dimensions=2):
            data_dict = self.kd.get_company_data(company["id"])
            return self._build_from_knowledge(company["id"], company_name, company["canonical_name"], data_dict)

        # Memory cache
        if company_name in self._cache:
            cached = self._cache[company_name]
            if now < cached["expires"]:
                return cached["data"]

        # Old cache
        data, is_stale = self.db.get_cached_data_stale_ok(company_name)
        if data is not None:
            return data

        return None

    def _live_fetch(self, company_name: str, credit_data: dict, start: float) -> Dict:
        """实时抓取（原逻辑），同时存入知识库。"""
        from ..services.aggregator import fetch_company_report_sync_no_ai
        from ..services.ai_analyzer import analyze_company

        report = fetch_company_report_sync_no_ai(company_name)
        raw_data = {}
        from ..routes.company import _serialize_source_data
        for source in report.sources:
            if source.available and source.data:
                raw_data[source.id] = _serialize_source_data(source)

        ai_result = analyze_company(company_name, raw_data, credit_data) if raw_data else {"success": False, "error": "No data"}

        data = {
            "company_name": company_name,
            "normalized_name": report.normalized_name or company_name,
            "raw_data": raw_data,
            "ai_result": ai_result,
            "data_sources": [s.id for s in report.sources if s.available],
        }

        # 存入双缓存
        now = time.time()
        self._cache[company_name] = {"data": data, "expires": now + self._cache_ttl, "created": now}
        self.db.set_cached_data(company_name, data)

        # 同时填充知识库（异步，不阻塞返回）
        try:
            self._populate_knowledge(company_name, report, raw_data)
        except Exception as e:
            logger.warning(f"[KNOWLEDGE POPULATE] 失败: {e}")

        logger.info(f"[LIVE] {company_name} ({len(raw_data)} sources)")
        self._log_query(company_name, False, start)
        return data

    def _populate_knowledge(self, company_name: str, report, raw_data: dict):
        """将实时抓取的结果写入知识库维度表 + 更新时间戳。

        C 变体策略：
        - 公司已在知识库中 → 用 API 返回的维度数据覆盖写入，更新 last_verified_at
        - 公司不在知识库中 → 启动后台全量采集（原逻辑不变）
        - 不动 distilled 数据（不触发 DeepSeek 重新蒸馏）
        """
        from ..services.knowledge_collector import collect_company

        # 反向映射：API 层 source_id → 知识库 data_type
        _REVERSE_KEY_MAP = {
            "tianyacha": "basic", "qichacha": "basic", "gsxt": "basic",
            "tavily": "sentiment", "bing": "sentiment",
            "wenshu": "risk", "qixinbao": "risk",
        }

        company = self.kd.find_company(company_name)
        if not company:
            # 新公司 → 后台全量采集（原逻辑不变）
            logger.info(f"[KNOWLEDGE POPULATE] 新公司 {company_name}，启动后台采集")
            import threading
            thread = threading.Thread(
                target=collect_company,
                args=(company_name,),
                kwargs={"priority": 0},
                daemon=True,
            )
            thread.start()
            return

        company_id = company["id"]
        written = 0
        for source_id, data in raw_data.items():
            dtype = _REVERSE_KEY_MAP.get(source_id, source_id)
            if dtype in ("deepseek", "mock", "ai_summary"):
                continue
            self.kd.set_company_data(company_id, dtype, data,
                                     source=source_id, confidence=0.7)
            written += 1

        if written > 0:
            self.kd.update_verified_at(company_id)
            logger.info(f"[KNOWLEDGE POPULATE] {company_name}: 更新 {written} 个维度 ✅")
        else:
            logger.info(f"[KNOWLEDGE POPULATE] {company_name}: 无有效维度写入")

    def invalidate_cache(self, company_name: Optional[str] = None):
        if company_name:
            self._cache.pop(company_name, None)
            self.db.invalidate(company_name)
        else:
            self._cache.clear()
            self.db.invalidate()

    def _log_query(self, company_name: str, cache_hit: bool, start: float):
        try:
            elapsed = int((time.time() - start) * 1000)
            self.db.log_query(company_name, company_name, cache_hit, elapsed)
        except Exception:
            pass

    def _increment_query_count(self, company_id: int):
        """增加公司查询次数（用于高频/低频分类）。"""
        try:
            self.kd.increment_query_count(company_id)
        except Exception:
            pass

    def stats(self) -> dict:
        return {
            "mem_cache_entries": len(self._cache),
            "mem_cache_ttl": self._cache_ttl,
            "db": self.db.stats(),
            "knowledge": self.kd.stats(),
        }


unified_service = UnifiedDataService()

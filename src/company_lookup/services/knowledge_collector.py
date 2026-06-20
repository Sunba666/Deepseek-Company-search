# -*- coding: utf-8 -*-
"""
知识采集器：多源并行采集 → AI 蒸馏 → 结构化存储。
采集流程：
  公司名 → 实体解析 → 并行数据源 → AI提炼压缩 → 打标签 → 存入知识库
"""

import json
import logging
import time
from typing import Dict, List, Any
import threading

logger = logging.getLogger(__name__)


def _compact(data: Any) -> Any:
    """将数据压缩为可序列化结构（移除无关字段）。"""
    if hasattr(data, "__dict__"):
        return {k: v for k, v in data.__dict__.items()
                if not k.startswith("_") and v is not None}
    if isinstance(data, dict):
        return {k: _compact(v) for k, v in data.items()
                if v is not None and v != ""}
    if isinstance(data, list):
        return [_compact(item) for item in data[:10]]
    return data


def _call_light_ai(summary_text: str) -> str:
    """轻量 AI 解读生成（~500 tokens）。"""
    try:
        from ..services.ai_analyzer import _call_deepseek_api
        prompt = (
            "你是一位求职顾问。以下是一家公司的多维度数据，"
            "请写一段150字以内的求职者视角总结。"
            "要求：说人话、有洞察、给出明确建议。只输出总结内容。\n\n数据："
            + summary_text[:800]
        )
        return (_call_deepseek_api(prompt) or "").strip()[:300]
    except Exception:
        return ""


_DISTILL_PROMPT = """你是一个企业数据蒸馏器。请将以下企业信息压缩为≤1500 token的结构化摘要。
严格按以下 JSON 格式输出（只输出 JSON，不要其他文字）：

{
  "one_liner": "一句话简介（≤30字）",
  "key_facts": {
    "registered_capital": "注册资本",
    "legal_person": "法定代表人",
    "founded": "成立日期",
    "status": "经营状态",
    "industry": "行业",
    "scale": "规模描述",
    "city": "总部城市"
  },
  "sentiment_top3": [
    {"point": "舆情要点1", "source": "来源"},
    {"point": "舆情要点2", "source": "来源"},
    {"point": "舆情要点3", "source": "来源"}
  ],
  "risk_summary": "风险摘要（≤50字，无风险则写'暂无已知风险'）",
  "job_seeker_note": "求职者视角（≤80字）：这家公司值不值得去、注意什么"
}

要求：压缩到极致，只保留对求职者有参考价值的信息。
"""


def distill_company(company_name: str, raw_data: dict = None) -> dict:
    """
    DeepSeek 深度蒸馏一家公司 → ≤1500 token 结构化数据。
    结果存入 knowledge DB company_data 的 "distilled" 维度。
    """
    from ..services.ai_analyzer import _call_deepseek_api

    # 构造输入数据摘要
    if raw_data is None:
        raw_data_str = company_name
    else:
        raw_data_str = json.dumps(raw_data, ensure_ascii=False, default=str)[:2000]

    prompt = _DISTILL_PROMPT + f"\n企业名称：{company_name}\n原始数据：{raw_data_str}"
    response = _call_deepseek_api(prompt)

    if not response:
        return {"one_liner": "", "key_facts": {}, "sentiment_top3": [], "risk_summary": "", "job_seeker_note": ""}

    try:
        # 清理 markdown 标记
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)
    except Exception:
        return {"one_liner": "", "key_facts": {}, "sentiment_top3": [],
                "risk_summary": "", "job_seeker_note": "", "_raw": response[:500]}


def collect_and_distill(company_name: str, industry: str = "", priority: int = 1,
                        hotness: str = "medium", discovery_source: str = "") -> Dict:
    """
    全量采集 + AI 深度蒸馏。
    支持热度标签和发现来源（用于小众公司标记）。
    """
    start = time.time()

    result = collect_company(company_name, priority=priority)
    if not result["success"]:
        return result

    company_id = result["company_id"]

    from ..services.knowledge_db import knowledge_db

    # 写入热度标签
    if hotness != "medium" or discovery_source:
        try:
            knowledge_db.set_hotness(company_id, hotness, discovery_source)
        except Exception:
            pass

    data_dict = knowledge_db.get_company_data(company_id)

    raw_for_distill = {}
    for dtype, d in data_dict.items():
        if dtype != "ai_summary":
            raw_for_distill[dtype] = d.get("content", {})

    distilled = distill_company(company_name, raw_for_distill)

    if distilled.get("one_liner"):
        knowledge_db.set_company_data(
            company_id=company_id,
            data_type="distilled",
            content=distilled,
            source="deepseek_distill",
            confidence=0.85,
        )

    if industry and industry != "其他":
        company = knowledge_db.find_company(company_name)
        if company:
            existing_industry = company.get("industry", "")
            if not existing_industry or existing_industry == "其他":
                knowledge_db.upsert_company(
                    canonical_name=company["canonical_name"],
                    industry=industry,
                )

    result["distilled"] = bool(distilled.get("one_liner"))
    result["duration_s"] = round(time.time() - start, 1)
    result["company_name"] = company_name
    return result


def collect_company(company_name: str, priority: int = 1) -> Dict:
    """全量采集一家公司的数据。"""
    start = time.time()
    result = {
        "success": False, "company_name": company_name,
        "company_id": None, "error": "", "duration_s": 0, "dimensions": [],
    }

    try:
        from ..services.entity_resolver import BRAND_MAPPING, entity_resolver
        from ..services.knowledge_db import knowledge_db
        from ..services.aggregator import fetch_company_report_sync_no_ai
        from ..services.official_credit import official_credit_service
        from ..db.cache_db import db_cache

        # ── 1. 实体解析 ──────────────────────────────
        canonical = db_cache.resolve_alias(company_name) or BRAND_MAPPING.get(company_name, company_name)
        try:
            resolved = entity_resolver.resolve(company_name, auto_confirm=True)
            if resolved and resolved.get("canonical_name"):
                canonical = resolved["canonical_name"]
        except Exception:
            pass

        # ── 2. 写入/更新公司主表 ──────────────────────
        aliases = list(set(
            [k for k, v in BRAND_MAPPING.items() if v == canonical]
            + ([company_name] if company_name != canonical else [])
            + ([company_name.lower()] if company_name.lower() != company_name else [])
        ))
        company_id = knowledge_db.upsert_company(canonical_name=canonical, aliases=aliases)
        result["company_id"] = company_id

        # ── 3. 并行采集多源数据 ──────────────────────
        all_dim_content = {}
        dimensions_collected = []

        # 3a. 工商信息
        try:
            credit = official_credit_service.get_credit_report(canonical)
            if credit and credit.is_valid:
                content = {k: getattr(credit, k, "") for k in [
                    "unified_credit_code", "legal_representative", "registered_capital",
                    "paid_in_capital", "establishment_date", "company_status",
                    "company_type", "registered_address", "business_scope",
                ]}
                source_lbl = "gsxt" if "gsxt" in credit.source else "tianyacha"
                knowledge_db.set_company_data(company_id=company_id, data_type="basic",
                    content=content, source=source_lbl, confidence=0.95)
                dimensions_collected.append("basic")
                all_dim_content["官方信用"] = content

                # 行业 / 城市粗提
                kw_map = {"互联网": ["互联网","科技","软件"], "金融": ["金融","支付"],
                          "电商": ["电商","零售"], "游戏": ["游戏"], "通信": ["通信","移动"]}
                industry = next((k for k, vs in kw_map.items()
                                 if any(v in (credit.business_scope or "") for v in vs)), "")
                city = next((c for c in ["北京","上海","广州","深圳","杭州","成都"]
                             if c in (credit.registered_address or "")), "")
                knowledge_db.upsert_company(canonical_name=canonical,
                    industry=industry, city=city, status=credit.company_status)
        except Exception as e:
            logger.warning(f"[Collector] 工商信息采集失败: {e}")

        # 3b. 舆情/薪资/风控/口碑/面试
        try:
            report = fetch_company_report_sync_no_ai(canonical)
            if report:
                for s in report.sources:
                    dtype_map = {
                        "tavily": ("sentiment", "tavily"),
                        "wenshu": ("risk", "wenshu"),
                    }
                    if s.id in dtype_map and s.available and s.data:
                        dt, src = dtype_map[s.id]
                        knowledge_db.set_company_data(company_id=company_id,
                            data_type=dt, content=_compact(s.data),
                            source=src, confidence=0.8)
                        dimensions_collected.append(dt)
                        all_dim_content[s.id] = _compact(s.data)
                    elif s.id == "salary" and s.available and s.data:
                        knowledge_db.set_company_data(company_id=company_id,
                            data_type="salary", content=_compact(s.data),
                            source="tavily", confidence=0.6)
                        dimensions_collected.append("salary")
                        all_dim_content["salary"] = _compact(s.data)
                    elif s.id == "reputation" and s.available and s.data:
                        knowledge_db.set_company_data(company_id=company_id,
                            data_type="culture", content=_compact(s.data),
                            source="tavily", confidence=0.6)
                        dimensions_collected.append("culture")
                        all_dim_content["culture"] = _compact(s.data)
                    elif s.id == "interview" and s.available and s.data:
                        knowledge_db.set_company_data(company_id=company_id,
                            data_type="interview", content=_compact(s.data),
                            source="tavily", confidence=0.6)
                        dimensions_collected.append("interview")
                        all_dim_content["interview"] = _compact(s.data)
        except Exception as e:
            logger.warning(f"[Collector] 多维数据采集失败: {e}")

        # ── 4. 轻量 AI 解读 ─────────────────────────
        try:
            summary_text = json.dumps(all_dim_content, ensure_ascii=False, default=str)[:800]
            ai_note = _call_light_ai(summary_text)
            if ai_note:
                knowledge_db.set_company_data(company_id=company_id,
                    data_type="ai_summary",
                    content={"summary": ai_note, "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")},
                    source="deepseek_light", confidence=0.7)
                dimensions_collected.append("ai_summary")
        except Exception as e:
            logger.warning(f"[Collector] AI 解读失败: {e}")

        result["dimensions"] = dimensions_collected
        result["success"] = True
        result["duration_s"] = round(time.time() - start, 1)
        logger.info(f"[Collector] 完成: {canonical} ({len(dimensions_collected)} dims in {result['duration_s']}s)")
        return result

    except Exception as e:
        result["error"] = str(e)
        result["duration_s"] = round(time.time() - start, 1)
        logger.error(f"[Collector] 采集失败 {company_name}: {e}", exc_info=True)
        return result


def process_queue():
    """处理采集队列中的任务（在后台线程运行）。"""
    from ..services.knowledge_db import knowledge_db
    logger.info("[Collector Queue] 开始处理队列...")
    count = 0
    while True:
        task = knowledge_db.claim_task()
        if not task:
            break
        try:
            r = collect_company(task["company_name"], priority=task["priority"])
            knowledge_db.complete_task(task["id"], success=r["success"])
            if r["success"]:
                count += 1
                logger.info(f"[Queue] 完成: {task['company_name']} ({r.get('duration_s',0)}s, {len(r.get('dimensions',[]))}维)")
        except Exception as e:
            knowledge_db.fail_task_retry(task["id"], str(e))
    logger.info(f"[Collector Queue] 队列处理完毕，共处理 {count} 个任务")


def trigger_collection(company_name: str, priority: int = 1):
    """触发异步采集（不阻塞当前请求）。"""
    from ..services.knowledge_db import knowledge_db
    task_id = knowledge_db.create_task(company_name, priority=priority)
    logger.info(f"[Collector] 已创建采集任务: {company_name} (task_id={task_id}, priority={priority})")
    threading.Thread(target=process_queue, daemon=True).start()
    return task_id

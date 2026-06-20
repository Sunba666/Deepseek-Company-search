# -*- coding: utf-8 -*-
import logging

from flask import Blueprint, render_template, request

from ..htmx_utils import error_alert, route_errors

logger = logging.getLogger(__name__)

bp = Blueprint("compare", __name__)


@bp.route("/compare", methods=["GET"])
def compare_page():
    return render_template("compare.html")


@bp.route("/compare/search", methods=["POST"])
@route_errors("对比分析失败")
def compare_search():
    """同步对比分析入口 - 使用缓存优先"""
    companies = [c.strip() for c in request.form.getlist("companies") if c.strip()]

    if len(companies) < 2:
        return error_alert("至少输入两家公司才能对比哦")

    logger.info(f"开始对比分析: {companies[0]} vs {companies[1]}")

    from ..services.unified_data_service import UnifiedDataService
    from ..services.aggregator import fetch_company_report_sync_no_ai

    def _get_raw(company):
        uds = UnifiedDataService()
        cached = uds.get_company_data_cached_only(company)
        if cached and cached.get("raw_data"):
            return cached["raw_data"]
        report = fetch_company_report_sync_no_ai(company)
        raw = {}
        for source in report.sources:
            if source.available and source.data:
                raw[source.id] = _serialize_source_data(source)
        return raw

    data_a = _get_raw(companies[0])
    data_b = _get_raw(companies[1])

    from ..services.ai_analyzer import compare_companies

    ai_result = compare_companies(companies[0], companies[1], data_a, data_b)

    if isinstance(ai_result, dict) and ai_result.get("success"):
        return render_template("partials/ai_report.html", **ai_result)
    else:
        return error_alert(ai_result.get("error", "AI今天有点卡，待会再试试"))


def _serialize_source_data(source):
    """序列化数据源数据"""
    if not source.data:
        return None

    data = source.data

    if hasattr(data, "company_name"):
        return {
            "company_name": data.company_name,
            "unified_credit_code": data.unified_credit_code,
            "legal_representative": data.legal_representative,
            "registered_capital": data.registered_capital,
            "company_status": data.company_status,
            "company_type": data.company_type,
            "business_scope": data.business_scope,
            "establishment_date": data.establishment_date,
        }

    if isinstance(data, dict) and "items" in data:
        items = []
        for item in data["items"]:
            if hasattr(item, "to_dict"):
                items.append(item.to_dict())
            elif hasattr(item, "__dict__"):
                items.append({k: v for k, v in item.__dict__.items() if not k.startswith("_")})
            else:
                items.append(item)
        return {"items": items, "count": data.get("count", len(items))}

    if isinstance(data, list):
        items = []
        for item in data:
            if hasattr(item, "to_dict"):
                items.append(item.to_dict())
            elif hasattr(item, "__dict__"):
                items.append({k: v for k, v in item.__dict__.items() if not k.startswith("_")})
            else:
                items.append(item)
        return {"items": items, "count": len(items)}

    if hasattr(data, "to_dict"):
        return data.to_dict()
    elif hasattr(data, "__dict__"):
        return {k: v for k, v in data.__dict__.items() if not k.startswith("_")}

    # 修复：处理普通字典（薪酬福利、员工口碑、面试经验等纯数据字典）
    if isinstance(data, dict):
        return data

    return data


@bp.route("/compare/ai", methods=["POST"])
@bp.route("/compare_ai", methods=["POST"])
@route_errors("对比分析失败")
def compare_ai():
    """对比分析 - 使用真实API数据和AI分析（缓存优先）"""
    companies = [c.strip() for c in request.form.getlist("companies") if c.strip()]

    if len(companies) < 2:
        return error_alert("至少输入两家公司才能对比哦")

    logger.info(f"compare_ai: {companies[0]} vs {companies[1]}")

    from ..services.aggregator import fetch_company_report_sync_no_ai
    from ..routes.company import _serialize_source_data
    from ..services.unified_data_service import UnifiedDataService

    uds = UnifiedDataService()

    # Try cache first; if miss, fetch raw + save to DB cache
    reports = []
    all_data = {}
    for company in companies:
        cached = uds.get_company_data_cached_only(company)
        if cached and cached.get("raw_data"):
            logger.info(f"[Compare CACHE HIT] {company}")
            raw = cached["raw_data"]
        else:
            logger.info(f"[Compare CACHE MISS] {company} — fetching raw...")
            report = fetch_company_report_sync_no_ai(company)
            raw = {}
            for source in report.sources:
                if source.available and source.data:
                    raw[source.id] = _serialize_source_data(source)
            # 存一份 raw_data 到 DB cache（不含 AI，但后续查询可受益）
            uds.db.set_cached_data(company, {
                "company_name": company,
                "normalized_name": report.normalized_name or company,
                "raw_data": raw,
                "ai_result": {"success": False, "note": "Compare-mode: AI analysis deferred"},
                "data_sources": [s.id for s in report.sources if s.available],
            })

        reports.append({
            "company_name": company,
            "normalized_name": cached.get("normalized_name", company) if cached else company,
            "raw_data": raw,
        })
        all_data[company] = raw
    comparison_table = []
    for i, company in enumerate(companies):
        report = reports[i]
        raw = report.get("raw_data", {})
        entity_data = raw.get("tianyacha", {})
        salary_data = raw.get("salary", {})
        reputation_data = raw.get("reputation", {})

        def _val(v, default="暂无公开数据"):
            return v if v and str(v).strip() else default

        # 融资状态映射（mock数据补充）
        FUNDING_MAP = {
            "腾讯": "已上市", "tencent": "已上市",
            "阿里巴巴": "已上市", "alibaba": "已上市",
            "字节跳动": "未上市", "bytedance": "未上市",
            "美团": "已上市", "meituan": "已上市",
            "京东": "已上市", "小米": "已上市",
            "百度": "已上市", "网易": "已上市",
            "华为": "未上市", "oppo": "未上市", "vivo": "未上市",
            "米哈游": "未上市", "柠檬微趣": "未上市",
        }

        entry = {"name": company, "full_name": report.get("normalized_name", company)}
        funding_status = None
        for k, v in FUNDING_MAP.items():
            if k.lower() in company.lower() or company.lower() in k.lower():
                funding_status = v
                break

        entry.update({
            "industry": _val(entity_data.get("company_type", "")),
            "scale": _val(entity_data.get("company_status", "")),
            "funding_status": funding_status or "暂无公开数据",
            "rating": _val(reputation_data.get("overall_rating", "") if isinstance(reputation_data, dict) else ""),
            "recommendation_rate": _val(reputation_data.get("recommendation_rate", "") if isinstance(reputation_data, dict) else ""),
            "avg_salary": _val(salary_data.get("avg_monthly", "") if isinstance(salary_data, dict) else ""),
            "risk_level": "低",
        })
        comparison_table.append(entry)

    # AI对比分析（仅对比前两家公司）

    from ..services.ai_analyzer import compare_companies

    ai_report_html = ""
    if len(companies) >= 2:
        ai_result = compare_companies(companies[0], companies[1],
                                       all_data.get(companies[0], {}),
                                       all_data.get(companies[1], {}))
        ai_report_html = ai_result.get("report_html", "") if ai_result.get("success") else ""
    detailed_analysis = []
    for i, company in enumerate(companies):
        raw = all_data.get(company, {})
        entity = raw.get("tianyacha", {})
        salary = raw.get("salary", {})
        reputation = raw.get("reputation", {})
        risk = raw.get("wenshu", {})

        industry = entity.get("company_type", "") or entity.get("company_status", "") or ""
        salary_str = salary.get("avg_monthly", "") if isinstance(salary, dict) else ""
        rating_str = reputation.get("overall_rating", "") if isinstance(reputation, dict) else ""
        risk_lvl = risk.get("risk_level", "") if isinstance(risk, dict) else ""

        overview_parts = []
        if industry: overview_parts.append(f"所属行业：{industry}")
        if entity.get("company_status"): overview_parts.append(f"状态：{entity['company_status']}")
        if salary_str: overview_parts.append(f"平均薪资：{salary_str}")
        if rating_str: overview_parts.append(f"综合评分：{rating_str}")
        if risk_lvl: overview_parts.append(f"风险等级：{risk_lvl}")

        overview = "、".join(overview_parts) if overview_parts else f"{company}是一家企业"

        strengths = []
        if salary_str: strengths.append(f"薪资水平较为主流（{salary_str}）")
        if rating_str: strengths.append(f"员工评分较高（{rating_str}）")
        if not strengths: strengths.append("请参考上方数据源详情")

        weaknesses = []
        if risk_lvl == "高": weaknesses.append("风险较高，需警惕")
        if not weaknesses: weaknesses.append("请参考上方数据源详情")

        entry = {
            "company": company,
            "full_name": reports[i].get("normalized_name", "") or company,
            "overview": overview,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "career_outlook": "请参考AI对比分析报告中的详细内容。",
            "fit_for": ["技术人才", "求职者"],
        }
        detailed_analysis.append(entry)

    analysis_result = {
        "comparison_table": comparison_table,
        "best_for": {
            "salary": companies[0] if len(companies) >= 1 else "暂无",
            "stability": companies[-1] if len(companies) >= 2 else "暂无公开数据",
            "growth": companies[0] if len(companies) >= 1 else "暂无",
            "culture": companies[1] if len(companies) >= 2 else "暂无",
            "work_life_balance": companies[-1] if len(companies) >= 2 else "暂无公开数据",
        },
        "detailed_analysis": detailed_analysis,
        "recommendation": "请参考下方的AI深度分析报告。建议结合个人职业规划和偏好进行选择。",
        "tips": [
            "建议在面试前详细了解目标公司的具体业务团队",
            "可以通过在职员工了解真实的日常工作状态",
            "关注公司的长期发展趋势而非短期利益",
            "结合个人职业规划和兴趣爱好做出选择",
        ],
        "risk_warnings": [
            "以上数据仅供参考，请以实际情况为准",
            "薪资水平可能因岗位、地区、工作经验等因素有所差异",
        ],
        "ai_report": ai_report_html,
    }

    return render_template("partials/compare_result.html", comparison=analysis_result)


@bp.route("/offer-compare", methods=["GET"])
def offer_compare_page():
    return render_template("offer_compare.html", result=None)


@bp.route("/offer-compare/analyze", methods=["POST"])
@bp.route("/offer-compare", methods=["POST"])
@route_errors("Offer对比分析失败")
def offer_compare():
    """Offer对比分析 - 使用真实AI分析"""
    offers = [o.strip() for o in request.form.getlist("offers") if o.strip()]
    if len(offers) < 2:
        return error_alert("至少输入两个 Offer 才能比哦")

    logger.info(f"开始对比 {len(offers)} 个Offer")

    from ..ai_analyzer import analyze_offers

    # 如果传入的是纯字符串列表，拆分成 dict
    processed = []
    for o in offers:
        if isinstance(o, str):
            # 支持简单格式: "公司名，薪资，福利"
            parts = [p.strip() for p in o.replace('，', ',').split(',')]
            entry = {'company_name': parts[0]}
            if len(parts) > 1:
                entry['salary'] = parts[1]
            if len(parts) > 2:
                entry['benefits'] = ','.join(parts[2:])
            processed.append(entry)
        else:
            processed.append(o)
    result = analyze_offers(processed)

    if result.get("error"):
        return error_alert(result["error"])

    winner = result.get("winner", "待定")
    reason = result.get("reason", "综合评估中")
    comparison = result.get("comparison", [])

    comparison_html = (
        '<div class="alert alert-success mb-4">'
        '<h4>🏆 最优选择：' + winner + '</h4>'
        '<p>' + reason + '</p></div>'
    )

    comparison_html += '<table class="table table-striped mb-4"><thead><tr><th>公司</th><th>综合评分</th><th>优点</th><th>缺点</th></tr></thead><tbody>'

    for offer in comparison:
        name = offer.get("company_name", offer.get("name", "未知"))
        score = offer.get("score", 0)
        pros = offer.get("pros", [])
        cons = offer.get("cons", [])
        if isinstance(pros, str):
            pros = [pros]
        if isinstance(cons, str):
            cons = [cons]
        pros_html = "".join('<span class="badge bg-success me-1">' + p + '</span>' for p in pros)
        cons_html = "".join('<span class="badge bg-danger me-1">' + c + '</span>' for c in cons)
        comparison_html += (
            '<tr><td>' + name + '</td><td>' + str(score) + '分</td><td>' + pros_html + '</td><td>' + cons_html + '</td></tr>'
        )

    comparison_html += '</tbody></table>'

    tips = result.get("negotiation_tips", result.get("tips", []))
    if tips:
        comparison_html += '<div class="card card-body mb-3"><h5>💬 谈判建议</h5><ul class="mb-0">'
        for tip in tips:
            comparison_html += '<li>' + tip + '</li>'
        comparison_html += '</ul></div>'

    summary = result.get("summary", result.get("conclusion", ""))
    if summary:
        comparison_html += (
            '<div class="p-3 bg-light rounded">'
            '<h5>📋 综合总结</h5>'
            '<p class="mb-0">' + summary + '</p></div>'
        )

    return comparison_html

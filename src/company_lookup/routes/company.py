# -*- coding: utf-8 -*-
import io
import re
import logging
import json
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from ..htmx_utils import error_alert, route_errors
from ..services import ai_service, company_service
from ..services.compare_service import calculate_radar_data, personalized_score

logger = logging.getLogger(__name__)

bp = Blueprint("company", __name__)


@bp.route("/api/resolve-entity", methods=["POST"])
def api_resolve_entity():
    query = request.form.get("query", "").strip()

    if not query:
        return jsonify({"code": 1, "status": "error", "message": "请输入公司名称"})

    try:
        from ..services import resolve_entity

        result = resolve_entity(query)

        return jsonify({"code": 0, "status": "success", "data": result})

    except Exception as e:
        logger.error(f"实体解析失败: {e}", exc_info=True)
        return jsonify({"code": 1, "status": "error", "message": f"解析失败: {str(e)}"})


@bp.route("/api/simplify-name", methods=["POST"])
def api_simplify_name():
    query = request.form.get("query", "").strip()

    if not query:
        return jsonify({"code": 1, "status": "error", "message": "请输入公司名称"})

    try:
        from ..services.entity_resolver import EntityResolver

        resolver = EntityResolver()
        simplified = resolver.extract_core_keyword(query)

        return jsonify(
            {"code": 0, "status": "success", "data": {"original": query, "simplified": simplified}}
        )

    except Exception as e:
        logger.error(f"名称简化失败: {e}", exc_info=True)
        return jsonify({"code": 1, "status": "error", "message": f"简化失败: {str(e)}"})


@bp.route("/api/report-missing-company", methods=["POST"])
def api_report_missing_company():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        return jsonify({"code": 1, "status": "error", "message": "请输入公司名称"})

    try:
        from ..services.entity_resolver import log_missing_company

        user_ip = request.remote_addr or ""

        log_missing_company(company_name, user_ip)

        logger.info(f"📝 用户反馈公司存在: {company_name} (IP: {user_ip})")

        return jsonify(
            {"code": 0, "status": "success", "message": "感谢您的反馈！我们会尽快处理。"}
        )

    except Exception as e:
        logger.error(f"反馈记录失败: {e}", exc_info=True)
        return jsonify({"code": 1, "status": "error", "message": f"反馈提交失败: {str(e)}"})


@bp.route("/report/aggregate", methods=["GET"])
def aggregate_report_page():
    company_name = request.args.get("company", "")
    return render_template("aggregate_report.html", company_name=company_name or "未知公司")


@bp.route("/api/aggregate-report", methods=["POST"])
def api_aggregate_report():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        return jsonify({"error": "请输入公司名称"})

    try:
        from ..services.aggregator import fetch_company_report_sync

        report = fetch_company_report_sync(company_name)

        return jsonify({"code": 0, "status": "success", "data": report.to_dict()})

    except Exception as e:
        logger.exception("Aggregate report failed")
        return jsonify({"code": 1, "status": "error", "message": f"报告生成失败: {str(e)}"})


@bp.route("/api/aggregate-report-htmx", methods=["POST"])
def api_aggregate_report_htmx():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        return error_alert("写个公司名字才能查呀")

    try:
        from ..services.aggregator import fetch_company_report_sync

        report = fetch_company_report_sync(company_name)

        sources = []
        for source in report.sources:
            sources.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "available": source.available,
                    "data": _serialize_source_data(source),
                    "error_msg": source.error_msg,
                    "is_mock": source.is_mock,
                    "fetch_time": source.fetch_time,
                    "source_url": source.source_url,
                }
            )

        return render_template(
            "partials/company_result.html",
            query=report.query,
            normalized_name=report.normalized_name,
            sources=sources,
        )

    except Exception as e:
        logger.exception("Aggregate report HTMX failed")
        return error_alert(f"报告生成失败: {str(e)}")




def _safe_val(v):
    """Convert enum/non-serializable values to strings."""
    if hasattr(v, "value"):
        return v.value
    if hasattr(v, "__dict__"):
        return str(v)
    return v


def _serialize_source_data(source):
    """Serialize DataSourceStatus data to dict for template rendering."""
    if not source.data:
        return None

    data = source.data

    if hasattr(data, "company_name"):
        return {
            "company_name": data.company_name,
            "unified_credit_code": data.unified_credit_code,
            "registration_number": data.registration_number,
            "legal_representative": data.legal_representative,
            "registered_capital": data.registered_capital,
            "paid_in_capital": data.paid_in_capital,
            "establishment_date": data.establishment_date,
            "company_status": data.company_status,
            "company_type": data.company_type,
            "registered_address": data.registered_address,
            "business_scope": data.business_scope,
            "shareholders": data.shareholders,
            "is_valid": data.is_valid,
            "error_message": data.error_message,
            "source": _safe_val(data.source),
            "fetch_time": data.fetch_time,
        }

    if isinstance(data, dict) and "items" in data:
        items = _serialize_items(data["items"])
        return {"items": items, "count": data.get("count", len(items))}

    if isinstance(data, list):
        items = _serialize_items(data)
        return {"items": items, "count": len(items)}

    if hasattr(data, "to_dict"):
        return data.to_dict()

    # 修复：处理普通字典（薪酬福利、员工口碑、面试经验等纯数据字典）
    if isinstance(data, dict):
        return data

def _serialize_items(items):
    """Serialize a list of data items, converting enums to strings."""
    result = []
    for item in items:
        if hasattr(item, "to_dict"):
            result.append(item.to_dict())
        elif hasattr(item, "__dict__"):
            result.append({k: _safe_val(v) for k, v in item.__dict__.items() if not k.startswith("_")})
        else:
            result.append(item)
    return result



@bp.route("/report/multi-source", methods=["GET"])
def multi_source_report_page():
    company_name = request.args.get("company", "")
    return render_template("report_multi_source.html", company_name=company_name or "未知公司")


@bp.route("/api/multi-source-report", methods=["POST"])
def api_multi_source_report():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        return jsonify({"error": "请输入公司名称", "terminated": True})

    try:
        from ..services import ReportService

        # 【修复】使用 generate_report_sync() 替代手动创建事件循环，
        # 避免在 Flask 同步路由中直接操作 asyncio 事件循环。
        report = ReportService().generate_report_sync(company_name)

        return jsonify(
            {
                "original_query": report.original_query,
                "normalized_name": report.normalized_name,
                "terminated": report.terminated,
                "termination_reason": report.termination_reason,
                "api_status": report.api_status,
                "errors": report.errors,
                "entity": {
                    "company_name": report.entity.company_name if report.entity else None,
                    "unified_credit_code": report.entity.unified_credit_code
                    if report.entity
                    else None,
                    "registration_number": report.entity.registration_number
                    if report.entity
                    else None,
                    "legal_representative": report.entity.legal_representative
                    if report.entity
                    else None,
                    "registered_capital": report.entity.registered_capital
                    if report.entity
                    else None,
                    "paid_in_capital": report.entity.paid_in_capital if report.entity else None,
                    "establishment_date": report.entity.establishment_date
                    if report.entity
                    else None,
                    "company_status": report.entity.company_status if report.entity else None,
                    "company_type": report.entity.company_type if report.entity else None,
                    "registered_address": report.entity.registered_address
                    if report.entity
                    else None,
                    "business_scope": report.entity.business_scope if report.entity else None,
                    "shareholders": report.entity.shareholders if report.entity else [],
                    "is_valid": report.entity.is_valid if report.entity else False,
                    "error_message": report.entity.error_message if report.entity else None,
                    "source": report.entity.source.value if report.entity else None,
                    "fetch_time": report.entity.fetch_time if report.entity else None,
                }
                if report.entity
                else None,
                "sentiments": [
                    {
                        "id": s.id,
                        "title": s.title,
                        "summary": s.summary,
                        "source_name": s.source_name,
                        "url": s.url,
                        "publish_date": s.publish_date,
                        "category": s.category,
                        "sentiment": s.sentiment,
                        "mentioned_salary": s.mentioned_salary,
                        "mentioned_pros": s.mentioned_pros,
                        "mentioned_cons": s.mentioned_cons,
                        "confidence": s.confidence.value,
                        "confidence_note": s.confidence_note,
                    }
                    for s in report.sentiments
                ],
                "risks": [
                    {
                        "id": r.id,
                        "case_type": r.case_type,
                        "case_number": r.case_number,
                        "title": r.title,
                        "summary": r.summary,
                        "judgment_date": r.judgment_date,
                        "judgment_amount": r.judgment_amount,
                        "risk_level": r.risk_level,
                        "risk_category": r.risk_category,
                        "source_name": r.source_name,
                        "url": r.url,
                    }
                    for r in report.risks
                ],
                "conflicts": [
                    {
                        "category": c.category,
                        "description": c.description,
                        "sources": c.sources,
                        "resolution_hint": c.resolution_hint,
                    }
                    for c in report.conflicts
                ],
                "total_sentiment_count": report.total_sentiment_count,
                "total_risk_count": report.total_risk_count,
            }
        )

    except Exception as e:
        logger.exception("Multi-source report failed")
        return jsonify(
            {"error": f"报告生成失败: {str(e)}", "terminated": True, "termination_reason": str(e)}
        )


def _invalid_company_response(query: str):
    return render_template("partials/invalid_company.html", query=query)


def _company_lookup_error_response(query: str, lookup: dict, *, result_template: str, **ctx):
    if lookup.get("invalid_entity"):
        return _invalid_company_response(query)
    if lookup.get("error"):
        return render_template(result_template, error=lookup["error"], **ctx)
    return None


@bp.route("/company/search", methods=["POST", "GET"])
def search_company():
    """同步搜索入口 - 先AI消歧再获取数据+AI分析"""
    if request.method == "GET":
        company_name = request.args.get("name", "").strip()
        if not company_name:
            return render_template("index.html")
    else:
        company_name = request.form.get("company_name", "").strip()
    if not company_name:
        return render_template("partials/error_alert.html", message="输入公司名字才能搜哦")

    try:
        logger.info(f"开始查询公司: {company_name}")

        # 步骤0: 快速缓存检查（绕过 AI 消歧，加速别名/热门公司）
        from ..db.cache_db import db_cache
        from ..services.unified_data_service import unified_service as uds
        from ..services.entity_resolver import BRAND_MAPPING

        # 尝试多种缓存键：别名解析结果、原始输入、品牌映射
        cache_keys = set()
        canonical = db_cache.resolve_alias(company_name)
        if canonical:
            cache_keys.add(canonical)
        if company_name in BRAND_MAPPING:
            cache_keys.add(BRAND_MAPPING[company_name])
        cache_keys.add(company_name)  # 兜底

        for key in cache_keys:
            cached = uds.get_company_data_cached_only(key)
            if cached and cached.get("ai_result", {}).get("success"):
                logger.info(f"[CACHE FAST PATH] {company_name} -> {key} (hit)")
                # 同时获取官方信用档案
                from ..services.official_credit import official_credit_service
                cr = official_credit_service.get_credit_report(key)
                cd = cr.to_dict() if cr and cr.is_valid else {}

                # 后台填充知识库（不阻塞返回）
                try:
                    from ..services.knowledge_db import knowledge_db
                    if not knowledge_db.find_company(key):
                        from ..services.knowledge_collector import trigger_collection
                        trigger_collection(key, priority=0)
                except Exception:
                    pass

                ai_data = dict(cached.get("ai_result", {}))
                ai_data.pop("company_name", None)  # 避免与下方参数冲突
                return render_template(
                    "partials/ai_report.html",
                    **ai_data,
                    company_name=key,
                    credit=cd,
                )

        # 步骤1: 检查记忆库
        memory = _load_json(MEMORY_FILE)
        if company_name in memory:
            info = memory[company_name]
            logger.info(f"步骤0: 记忆库命中: {company_name}")
            from datetime import datetime
            return render_template(
                "partials/ai_report.html",
                success=True,
                company_name=info.get("canonical_name", company_name),
                summary=info.get("known_info", "记忆库数据"),
                report_html=f'<div class="card"><div class="card-body"><h5>企业信息</h5>'
                          f'<p><strong>行业：</strong>{info.get("industry", "未知")}</p>'
                          f'<p>{info.get("known_info", "")}</p>'
                          f'<p class="text-muted small">来源：用户反馈 + AI验证</p></div></div>',
                raw_data={},
                analysis_time=datetime.now().isoformat(),
                data_sources=["memory"]
            )
        for canonical_name, info in memory.items():
            if company_name in info.get("aliases", []):
                logger.info(f"步骤0: 记忆库别名匹配: {company_name} -> {canonical_name}")
                from datetime import datetime
                return render_template(
                    "partials/ai_report.html", success=True, company_name=canonical_name,
                    summary=info.get("known_info", "记忆库数据"),
                    report_html=f'<div class="card"><div class="card-body"><h5>企业信息</h5>'
                              f'<p><strong>行业：</strong>{info.get("industry", "未知")}</p>'
                              f'<p>{info.get("known_info", "")}</p>'
                              f'<p class="text-muted small">来源：用户反馈 + AI验证</p></div></div>',
                    raw_data={}, analysis_time=datetime.now().isoformat(), data_sources=["memory"]
                )


        # 步骤1: 六层递进实体解析
        logger.info(f"步骤1: 多级实体解析...")
        from ..services.entity_resolver import entity_resolver as resolver, BRAND_MAPPING
        resolve_result = resolver.resolve(company_name)

        if resolve_result.get("status") in ("error", "not_company"):
            return render_template(
                "partials/not_found_with_suggestions.html",
                query=company_name,
                resolve={"exists": False, "canonical_name": "",
                         "reason": resolve_result.get("message", "请输入有效的公司名称"),
                         "suggestion": resolve_result.get("message", "")}
            )

        if resolve_result.get("status") == "candidates":
            return render_template(
                "partials/not_found_with_suggestions.html",
                query=company_name,
                resolve={
                    "exists": False,
                    "canonical_name": "",
                    "reason": resolve_result.get("message", "找到多个候选"),
                    "candidates": [c["name"] for c in resolve_result.get("candidates", [])],
                    "suggestion": "请从以下候选公司中选择："
                }
            )

        if resolve_result.get("status") == "not_found":
            # AI 消歧兜底
            from ..services.ai_analyzer import resolve_with_ai
            ai_result = resolve_with_ai(company_name)
            if ai_result.get("exists", False):
                full_name = ai_result.get("canonical_name", company_name) or company_name
                logger.info(f"步骤1 AI兜底: {company_name} -> {full_name}")
            else:
                suggestions = resolve_result.get("suggestions", [])
                return render_template(
                    "partials/not_found_with_suggestions.html",
                    query=company_name,
                    resolve={
                        "exists": False,
                        "canonical_name": "",
                        "reason": resolve_result.get("message", ""),
                        "suggestion": suggestions[0] if suggestions else "请尝试使用更完整的公司名称",
                    }
                )
        else:
            full_name = resolve_result.get("matched_name", company_name) or company_name

        logger.info(f"使用规范名称: {full_name}")

        # 品牌映射补全（如果返回的仍是简称）
        if full_name == company_name or not any(
            s in full_name for s in ["有限公司", "集团", "股份", "公司"]
        ):
            brand_match = None
            for alias, full in BRAND_MAPPING.items():
                if alias.lower() == company_name.lower():
                    brand_match = full
                    break
            if brand_match:
                logger.info(f"品牌映射补全: {full_name} -> {brand_match}")
                full_name = brand_match
            else:
                from ..db.cache_db import db_cache
                db_name = db_cache.resolve_alias(company_name)
                if db_name:
                    full_name = db_name
                    logger.info(f"数据库别名补全: {company_name} -> {full_name}")

        # 步骤2: 获取官方信用档案（优先获取，供 AI 分析使用）
        logger.info(f"步骤2: 获取官方信用档案...")
        from ..services.official_credit import official_credit_service
        credit_report = official_credit_service.get_credit_report(full_name)
        credit_dict = credit_report.to_dict() if credit_report and credit_report.is_valid else {}
        logger.info(f"步骤2: 信用数据 is_valid={credit_report.is_valid if credit_report else False}, dict_keys={list(credit_dict.keys()) if credit_dict else 'empty'}")

        # 步骤3: 获取多源数据 + AI分析（传入信用数据增强AI分析）
        logger.info(f"步骤3: 正在获取多源数据...")
        from ..services.unified_data_service import unified_service
        data = unified_service.get_company_data(full_name, credit_data=credit_dict)
        raw_data = data["raw_data"]
        ai_result = data["ai_result"]
        data_sources = data["data_sources"]

        # 检查是否正在采集中
        if data.get("_collecting") or (isinstance(ai_result, dict) and ai_result.get("collecting")):
            logger.info(f"[COLLECTING] {full_name} — 返回采集中状态")
            return render_template("partials/collecting_status.html",
                                   company_name=full_name)

        # 后台填充知识库（如果未命中缓存）
        try:
            from ..services.knowledge_db import knowledge_db
            if not knowledge_db.find_company(full_name):
                from ..services.knowledge_collector import trigger_collection
                trigger_collection(full_name, priority=0)
        except Exception:
            pass

        # 如果 AI 分析未成功但信用数据有效，仍展示信用档案
        if isinstance(ai_result, dict) and ai_result.get("success"):
            # 避免 ai_result 中的 company_name 与下方参数冲突
            ai_data = dict(ai_result)
            ai_data.pop("company_name", None)
            return render_template("partials/ai_report.html", **ai_data,
                                   company_name=full_name,
                                   credit=credit_dict)
        else:
            return render_template("partials/ai_report.html", success=True, company_name=full_name,
                                   summary="分析完成", raw_data=raw_data,
                                   credit=credit_dict)


    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        return render_template("partials/error_alert.html", message=f"查询失败: {str(e)[:100]}")
@bp.route("/dashboard", methods=["GET"])
def dashboard():
    company = request.args.get("company", "")
    data = None
    error = None
    if company:
        data = company_service.query_company_info(company)
        if data.get("invalid_entity"):
            return render_template(
                "dashboard.html",
                company=company,
                data=None,
                error=None,
                invalid_entity=True,
            )
        if data.get("error"):
            error = data["error"]
            data = {}
    return render_template(
        "dashboard.html", company=company or None, data=data, error=error, invalid_entity=False
    )


@bp.route("/dashboard/search", methods=["POST"])
@route_errors("仪表盘查询失败")
def dashboard_search():
    query = request.form.get("query", "") or request.form.get("company_name", "")
    query = (query or "").strip()
    if not query:
        return error_alert("搜公司要先输入名字哦")

    # Dashboard uses generate_mock_company_data format
    from ..services.company_service import query_company_info
    data = query_company_info(query)
    blocked = _company_lookup_error_response(
        query,
        data,
        result_template="partials/dashboard_result.html",
        company=query,
        data={},
    )
    if blocked:
        return blocked

    return render_template(
        "partials/dashboard_result.html",
        company=query,
        data=data,
        error=None,
    )


@bp.route("/analyze", methods=["POST"])
@route_errors("AI 分析失败")
def analyze():
    query = request.form.get("query", "").strip()
    user_context = request.form.get("user_context", "").strip()
    if not query:
        return error_alert("请输入公司名称")

    if not company_service.is_likely_company_name(query):
        return _invalid_company_response(query)

    analysis = ai_service.analyze_company(query, user_context)
    if analysis.get("error"):
        return error_alert(f"分析失败：{analysis['error']}")

    return render_template("partials/analysis_result.html", analysis=analysis)


@bp.route("/personalize", methods=["POST"])
@route_errors("个性化评分失败")
def personalize():
    query = request.form.get("query", "").strip()
    preferences = {
        "expected_salary": request.form.get("expected_salary", "20K"),
        "wl_balance": request.form.get("wl_balance", "important"),
        "location": request.form.get("location", ""),
    }
    if not query:
        return error_alert("搜公司要先输入名字哦")

    data = company_service.query_company_info(query)
    blocked = _company_lookup_error_response(
        query,
        data,
        result_template="partials/score_card.html",
        score={},
        company=query,
    )
    if blocked:
        return blocked

    score_card = personalized_score(data, preferences)
    return render_template("partials/score_card.html", score=score_card, company=query)


@bp.route("/resume-optimizer", methods=["GET"])
def resume_optimizer_page():
    return render_template("resume_optimizer.html")


@bp.route("/resume-optimizer/analyze", methods=["POST"])
@bp.route("/resume-optimizer", methods=["POST"])
@route_errors("简历分析失败")
def resume_optimizer():
    """Upload and analyze resume - extract text, optimize via AI."""
    import io
    resume_text = ""
    file = request.files.get("resume_file")

    if file and file.filename:
        # --- File upload path ---
        filename = file.filename.lower()
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""

        # Validate extension
        allowed_exts = {"pdf", "docx", "txt"}
        if ext not in allowed_exts:
            return f'<div class="alert alert-danger">不支持的文件格式 (.{ext})，请上传 PDF、Word 或 TXT 文档</div>'

        # Validate file size (5MB max)
        file_data = file.read()
        if len(file_data) > 5 * 1024 * 1024:
            return '<div class="alert alert-danger">文件大小超过 5MB 限制</div>'

        # Validate MIME type by reading file header
        header = file_data[:8]
        is_pdf = header[:4] == b'%PDF'
        is_docx = header[:2] == b'PK' and b'[Content_Types]' in file_data[:200]
        is_txt = False
        if not is_pdf and not is_docx:
            try:
                file_data.decode('utf-8')
                is_txt = True
            except:
                pass

        if not is_pdf and not is_docx and not is_txt:
            return '<div class="alert alert-danger">文件类型不匹配（真实格式与扩展名不一致），请上传真实简历文档</div>'

        # Extract text based on format
        try:
            if is_pdf:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(file_data)) as pdf:
                        resume_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                except ImportError:
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(io.BytesIO(file_data))
                        resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    except ImportError:
                        return '<div class="alert alert-warning">PDF 解析库未安装，请使用 txt 格式上传</div>'
            elif is_docx:
                try:
                    from docx import Document
                    doc = Document(io.BytesIO(file_data))
                    resume_text = "\n".join(p.text for p in doc.paragraphs)
                except ImportError:
                    return '<div class="alert alert-warning">DOCX 解析库未安装，请使用 txt 格式上传</div>'
            else:  # txt
                resume_text = file_data.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"简历文件解析失败: {e}")
            return f'<div class="alert alert-danger">文件解析失败，请确认内容可读</div>'

    else:
        # --- Manual text input path ---
        resume_text = request.form.get("resume_text", "").strip()

    # Validate content
    if not resume_text or len(resume_text.strip()) < 30:
        return '<div class="alert alert-warning">简历内容过短（需至少30字符），请确认上传了完整的简历文档</div>'

    # Resume structure detection
    resume_keywords = ["教育背景", "工作经历", "项目经验", "技能", "学历", "毕业", "经验"]
    has_resume_structure = any(kw in resume_text for kw in resume_keywords)
    if not has_resume_structure:
        return '<div class="alert alert-warning">未检测到标准简历结构（缺少"教育背景/工作经历/项目经验"等关键词），请确认上传了有效的简历文件</div>'

    # Clean text
    resume_text = re.sub(r'<[^>]+>', '', resume_text)  # Strip HTML
    resume_text = re.sub(r'\s+', ' ', resume_text).strip()
    resume_text = resume_text[:8000]  # Length limit

    # Call AI for optimization
    from ..services.ai_analyzer import _call_deepseek_api

    system_prompt = (
        "You are a professional resume consultant and HR expert. "
        "Analyze the provided resume and give structured optimization suggestions.\n\n"
        "Output in the following Markdown format ONLY:\n"
        "## 总体评价\n"
        "(Brief overall assessment)\n\n"
        "## 优点\n"
        "- Point 1\n"
        "- Point 2\n\n"
        "## 优化建议\n"
        "- Suggestion 1\n"
        "- Suggestion 2\n\n"
        "## 优化后简历\n"
        "(The optimized full resume text)\n\n"
        "IMPORTANT:\n"
        "- Only analyze content provided, never fabricate.\n"
        "- Keep the candidate's original experience and facts intact.\n"
        "- Improve wording, format, and keyword optimization.\n"
        "- Chinese output preferred.\n"
    )
    user_prompt = f"请分析并优化以下简历内容：\n\n{resume_text}"

    ai_result = _call_deepseek_api(user_prompt, system_prompt)
    if ai_result:
        import markdown
        result_html = markdown.markdown(ai_result)
        return render_template(
            "partials/resume_result.html",
            result={"success": True, "report_html": result_html, "original_length": len(resume_text)}
        )
    else:
        return '<div class="alert alert-danger">AI 暂时不在线，换个时间试试看</div>'
@bp.route("/negotiate", methods=["GET"])
def negotiate_page():
    return render_template("negotiate.html")


@bp.route("/negotiate/generate", methods=["POST"])
@bp.route("/negotiate", methods=["POST"])
@route_errors("谈判建议生成失败")
def negotiate():
    company_name = request.form.get("company_name", "").strip()
    if not company_name:
        return error_alert("请输入目标公司")

    if not company_service.is_likely_company_name(company_name):
        return _invalid_company_response(company_name)

    result = ai_service.generate_negotiation_script(
        {
            "company_name": company_name,
            "current_salary": request.form.get("current_salary", ""),
            "other_offers": request.form.get("other_offers", ""),
        },
        request.form.get("expected_salary", ""),
    )
    payload = {
        "salary_range": f"{request.form.get('current_salary') or '当前面议'} → {request.form.get('expected_salary') or '期望待议'}",
        "scripts": [
            result.get("opening", ""),
            result.get("justification", ""),
            result.get("closing", ""),
        ],
        "benefits": ["年终奖", "股票/期权", "弹性办公", "补充医疗", "带薪年假"],
        "tips": result.get("tips", []),
    }
    return render_template("partials/negotiate_result.html", result=payload)


@bp.route("/api/suggest-companies", methods=["POST"])
def api_suggest_companies():
    query = request.form.get("query", "").strip()
    suggestions = company_service.suggest_companies(query)
    if not suggestions:
        return jsonify([])

    html = '<ul class="suggestions">'
    for company in suggestions[:8]:
        html += f'<li class="suggestion-item" data-company="{company}">{company}</li>'
    html += "</ul>"
    return html


@bp.route("/api/suggest-companies-json", methods=["POST"])
def api_suggest_companies_json():
    query = request.form.get("query", "").strip()
    return jsonify(company_service.suggest_companies(query)[:8])


@bp.route("/api/radar-data", methods=["POST"])
def api_radar_data():
    company_data = request.json.get("company_data", {}) if request.is_json else {}
    radar_data = calculate_radar_data(company_data)
    return jsonify(
        {
            "dimensions": list(radar_data.keys()),
            "values": list(radar_data.values()),
        }
    )


@bp.route("/api/interview-questions", methods=["POST"])
def api_interview_questions():
    company_name = request.json.get("company_name", "")
    job_type = request.json.get("job_type", "软件工程师")
    result = ai_service.generate_interview_questions(company_name, job_type)
    all_questions = []
    if result.get("technical_questions"):
        all_questions.extend(result["technical_questions"])
    if result.get("behavioral_questions"):
        all_questions.extend(result["behavioral_questions"])
    return jsonify({"questions": all_questions, "suggestions": result.get("suggestions", [])})


@bp.route("/api/mock-interview", methods=["POST"])
def api_mock_interview():
    result = ai_service.mock_interview(
        request.json.get("question", ""),
        request.json.get("answer", ""),
        request.json.get("company_name", ""),
    )
    return jsonify(result)


@bp.route("/api/refresh-data", methods=["POST"])
def api_refresh_data():
    company_name = request.json.get("company_name", "")
    if not company_name:
        return jsonify({"error": "请提供公司名称"})
    data = company_service.query_company_info(company_name, force_refresh=True)
    return jsonify(data)


@bp.route("/api/api-status", methods=["GET"])
def api_api_status():
    import logging

    logger = logging.getLogger(__name__)

    try:
        logger.info("🔍 正在获取API状态...")

        from ..services import ReportService

        service = ReportService()
        status = service.get_api_status()

        logger.info(f"📦 获取到的状态: {status}")

        configured_count = 0
        total_count = 0

        api_layers = ["entity_apis", "sentiment_apis", "risk_apis", "ai_apis"]
        for layer in api_layers:
            if layer in status:
                apis = status[layer]
                for api_name, api_info in apis.items():
                    total_count += 1
                    if api_info.get("configured"):
                        configured_count += 1

        has_any_api = configured_count > 0
        mode = "production" if has_any_api else "mock"

        deepseek_status = status.get("ai_apis", {}).get("deepseek", {})
        if deepseek_status.get("configured"):
            tip = "✅ DeepSeek AI已配置，可进行智能分析"
        elif has_any_api:
            tip = "⚠️ 部分API已配置，可获得更准确的数据"
        else:
            tip = "🔴 所有API均未配置，当前使用模拟数据"

        logger.info(f"✅ API状态获取成功: {configured_count}/{total_count} 已配置, 模式: {mode}")

        return jsonify(
            {
                "code": 0,
                "status": "success",
                "message": "API状态获取成功",
                "data": {
                    "mode": mode,
                    "mode_label": "生产模式" if has_any_api else "模拟模式",
                    "configured_count": configured_count,
                    "total_count": total_count,
                    "status": status,
                    "tip": tip,
                },
            }
        )

    except ImportError as e:
        logger.error(f"❌ 导入模块失败: {str(e)}")
        return jsonify(
            {"code": 1, "status": "error", "message": f"服务模块导入失败: {str(e)}", "data": None}
        )

    except Exception as e:
        logger.error(f"❌ API状态获取异常: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return jsonify(
            {"code": 1, "status": "error", "message": f"获取API状态失败: {str(e)}", "data": None}
        )



@bp.route("/api/ocr-resume", methods=["POST"])
def api_ocr_resume():
    """Deprecated OCR endpoint - file upload now handled by resume_optimizer."""
    return jsonify({"error": "请使用 /resume-optimizer 上传文档类型简历"})


# ========== 记忆库 ==========
import os
import json
MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data")
MEMORY_FILE = os.path.join(MEMORY_DIR, "company_memory.json")
PENDING_FILE = os.path.join(MEMORY_DIR, "pending_feedback.json")


def _load_json(filepath: str) -> dict:
    """Load JSON file, return empty dict if not exists."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}
    return {}


def _save_json(filepath: str, data: dict):
    """Save dict to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@bp.route("/company/feedback", methods=["POST"])
def submit_feedback():
    """User feedback: company exists -> AI verifies -> stored in memory."""
    company_name = request.form.get("company_name", "").strip()
    user_input = request.form.get("user_input", company_name).strip()

    if not company_name:
        return '<div class="alert alert-danger">请输入公司名称</div>'

    # Check memory first
    memory = _load_json(MEMORY_FILE)
    found = None
    for key, info in memory.items():
        if key == company_name or company_name in info.get("aliases", []):
            found = info
            break

    if found:
        return render_template(
            "partials/feedback_result.html",
            status="already_known",
            company_name=found.get("canonical_name", company_name),
            info=found,
        )

    # Call AI for verification
    from ..services.ai_analyzer import verify_company_with_ai
    verification = verify_company_with_ai(company_name, user_input)

    if verification.get("verified", False):
        canonical = verification.get("canonical_name", company_name) or company_name

        # Use DataMerger to merge with any existing memory entry
        from ..services.data_merger import DataMerger
        existing = memory.get(canonical, {})
        merger = DataMerger(existing)
        merger.merge({
            "canonical_name": canonical,
            "aliases": list(set([user_input] + verification.get("aliases", []))),
            "company_profile": verification.get("known_info", ""),
            "industry": verification.get("industry", "unknown"),
        }, source="user_feedback")
        merged = merger.data
        merged["verified_at"] = __import__("datetime").datetime.now().isoformat()
        merged["verification_confidence"] = verification.get("confidence", "medium")
        merged["feedback_count"] = 1
        merged["status"] = "verified"

        memory[canonical] = merged
        _save_json(MEMORY_FILE, memory)
        logger.info(f"FAQ: Company verified and stored via DataMerger: {canonical}")

        return render_template(
            "partials/feedback_result.html",
            status="verified",
            company_name=canonical,
            info=verification,
        )
        # Store in pending queue
        pending = _load_json(PENDING_FILE)
        pending[company_name] = {
            "user_input": user_input,
            "submitted_at": __import__("datetime").datetime.now().isoformat(),
            "ai_analysis": verification,
            "status": "pending",
        }
        _save_json(PENDING_FILE, pending)
        logger.info(f"FAQ: Company verification pending: {company_name}")

        return render_template(
            "partials/feedback_result.html",
            status="pending",
            company_name=company_name,
            reason=verification.get("reason", "AI未能确认该公司存在"),
        )


# ========== 知识库 API ==========
@bp.route("/api/knowledge/stats", methods=["GET"])
def api_knowledge_stats():
    """知识库统计。"""
    from ..services.knowledge_db import knowledge_db
    stats = knowledge_db.stats()
    return jsonify({"code": 0, "data": stats})


@bp.route("/api/knowledge/refresh", methods=["POST"])
def api_knowledge_refresh():
    """触发知识库定期维护。"""
    from ..services.knowledge_db import knowledge_db
    from ..services.knowledge_collector import process_queue, collect_company

    knowledge_db.cleanup_stale_tasks()

    # 对陈旧公司创建刷新任务
    stale = knowledge_db.get_stale_companies(max_days=30)
    for company in stale[:5]:  # 一次最多5个
        knowledge_db.create_task(company["canonical_name"], priority=0)

    # 处理队列
    import threading
    thread = threading.Thread(target=process_queue, daemon=True)
    thread.start()

    return jsonify({
        "code": 0,
        "message": f"已创建 {len(stale[:5])} 个刷新任务，后台处理中",
        "stale_count": len(stale),
    })


@bp.route("/api/knowledge/discover", methods=["POST"])
def api_knowledge_discover():
    """触发小众公司发现（创建采集任务）。"""
    from ..services.knowledge_db import knowledge_db
    from ..services.niche_companies import get_niche_companies
    from ..services.knowledge_collector import collect_and_distill
    import threading as _t

    company_name = request.json.get("company_name", "") if request.is_json else ""
    industry = request.json.get("industry", "") if request.is_json else ""

    if company_name:
        # 采集单个小众公司
        _t.Thread(target=collect_and_distill, args=(company_name, industry),
                  kwargs={"hotness": "low", "discovery_source": "niche"},
                  daemon=True).start()
        return jsonify({"code": 0, "message": f"已触发采集: {company_name}"})

    # 批量创建任务
    all_niche = get_niche_companies()
    created = 0
    for name, ind, city, scale, desc in all_niche:
        if not knowledge_db.find_company(name):
            knowledge_db.create_task(name, priority=0)
            created += 1
            if created >= 20:  # 一次最多 20
                break

    return jsonify({
        "code": 0,
        "message": f"已创建 {created} 个小众公司采集任务",
        "niche_total": len(all_niche),
    })


# ========== 持续发现引擎 API ==========
@bp.route("/api/discovery/start", methods=["POST"])
def api_discovery_start():
    """启动持续发现引擎。"""
    from ..services.discovery_engine import discovery_engine
    discovery_engine.start()
    return jsonify({"code": 0, "message": "持续发现引擎已启动", "status": discovery_engine.status()})


@bp.route("/api/discovery/stop", methods=["POST"])
def api_discovery_stop():
    """停止持续发现引擎。"""
    from ..services.discovery_engine import discovery_engine
    discovery_engine.stop()
    return jsonify({"code": 0, "message": "持续发现引擎已停止", "status": discovery_engine.status()})


@bp.route("/api/discovery/status", methods=["GET"])
def api_discovery_status():
    """查看持续发现引擎状态。"""
    from ..services.discovery_engine import discovery_engine
    return jsonify({"code": 0, "data": discovery_engine.status()})


# ========== 知识库维护引擎 API ==========
@bp.route("/api/maintainer/start", methods=["POST"])
def api_maintainer_start():
    """启动知识库维护引擎。"""
    from ..services.knowledge_maintainer import maintainer
    maintainer.start()
    return jsonify({"code": 0, "message": "维护引擎已启动", "status": maintainer.status()})


@bp.route("/api/maintainer/stop", methods=["POST"])
def api_maintainer_stop():
    """停止知识库维护引擎。"""
    from ..services.knowledge_maintainer import maintainer
    maintainer.stop()
    return jsonify({"code": 0, "message": "维护引擎已停止", "status": maintainer.status()})


@bp.route("/api/maintainer/status", methods=["GET"])
def api_maintainer_status():
    """查看维护引擎状态。"""
    from ..services.knowledge_maintainer import maintainer
    return jsonify({"code": 0, "data": maintainer.status()})


@bp.route("/api/knowledge/health-report", methods=["GET"])
def api_knowledge_health_report():
    """生成知识库健康报告。"""
    from ..services.knowledge_maintainer import maintainer
    report = maintainer._generate_health_report()
    return jsonify({"code": 0, "data": report})


@bp.route("/admin/knowledge-health")
def admin_knowledge_health():
    """知识库健康报告页面。"""
    from ..services.knowledge_maintainer import maintainer
    from ..services.knowledge_db import knowledge_db
    report = maintainer._generate_health_report()
    ms = maintainer.status()
    stats = knowledge_db.stats()
    return render_template("knowledge_health.html",
                           report=report, stats=stats, title="知识库健康报告",
                           maintainer_status=ms)


# ========== 求职匹配 API ==========
@bp.route("/api/job-match", methods=["POST"])
def api_job_match():
    """求职匹配：根据偏好推荐公司。"""
    from ..services.job_matcher import job_matcher

    data = request.get_json(silent=True) or {}
    preferences = {
        "industry": data.get("industry", ""),
        "province": data.get("province", ""),
        "city": data.get("city", ""),
        "min_salary": int(data.get("min_salary", 0)),
        "risk_tolerance": data.get("risk_tolerance", "中"),
        "growth_stage": data.get("growth_stage", ""),
    }
    top_n = int(data.get("top_n", 10))
    result = job_matcher.match(preferences, top_n=top_n)
    return jsonify({"code": 0, "data": result})


# ========== 省份-城市数据（求职匹配用） ==========
PROVINCE_CITIES = {
    "北京市": ["北京市"],
    "上海市": ["上海市"],
    "天津市": ["天津市"],
    "重庆市": ["重庆市"],
    "广东省": ["广州", "深圳", "珠海", "佛山", "东莞", "惠州", "中山", "汕头", "湛江", "肇庆"],
    "浙江省": ["杭州", "宁波", "温州", "嘉兴", "绍兴", "金华", "台州", "湖州", "衢州", "舟山"],
    "江苏省": ["南京", "苏州", "无锡", "常州", "南通", "徐州", "扬州", "镇江", "泰州", "盐城", "淮安", "连云港"],
    "四川省": ["成都", "绵阳", "德阳", "宜宾", "南充", "泸州", "乐山", "眉山"],
    "湖北省": ["武汉", "宜昌", "襄阳", "荆州", "黄冈", "十堰", "孝感"],
    "湖南省": ["长沙", "株洲", "湘潭", "衡阳", "岳阳", "常德", "郴州"],
    "福建省": ["厦门", "福州", "泉州", "漳州", "莆田", "宁德", "龙岩"],
    "安徽省": ["合肥", "芜湖", "蚌埠", "马鞍山", "安庆", "滁州", "阜阳"],
    "山东省": ["青岛", "济南", "烟台", "潍坊", "临沂", "淄博", "威海", "济宁"],
    "陕西省": ["西安", "咸阳", "宝鸡", "延安", "渭南", "汉中"],
    "河南省": ["郑州", "洛阳", "南阳", "开封", "新乡", "许昌", "安阳"],
    "河北省": ["石家庄", "唐山", "保定", "邯郸", "廊坊", "秦皇岛", "沧州"],
    "辽宁省": ["沈阳", "大连", "鞍山", "抚顺", "锦州", "营口"],
    "吉林省": ["长春", "吉林", "四平", "延吉", "通化"],
    "黑龙江省": ["哈尔滨", "大庆", "齐齐哈尔", "牡丹江", "佳木斯"],
    "江西省": ["南昌", "赣州", "九江", "景德镇", "吉安", "宜春"],
    "山西省": ["太原", "大同", "长治", "晋中", "临汾", "运城"],
    "贵州省": ["贵阳", "遵义", "六盘水", "安顺", "黔东南"],
    "云南省": ["昆明", "大理", "丽江", "曲靖", "玉溪", "红河"],
    "甘肃省": ["兰州", "天水", "酒泉", "庆阳", "白银"],
    "广西壮族自治区": ["南宁", "桂林", "柳州", "北海", "玉林", "梧州"],
    "海南省": ["海口", "三亚", "儋州"],
    "内蒙古自治区": ["呼和浩特", "包头", "赤峰", "通辽", "鄂尔多斯"],
    "新疆维吾尔自治区": ["乌鲁木齐", "喀什", "伊犁", "克拉玛依"],
    "西藏自治区": ["拉萨", "日喀则"],
    "宁夏回族自治区": ["银川", "石嘴山", "吴忠"],
    "青海省": ["西宁", "海东"],
    "香港特别行政区": ["香港"],
    "澳门特别行政区": ["澳门"],
    "台湾省": ["台北", "高雄", "台中", "台南"],
}


@bp.route("/job-match", methods=["GET"])
def job_match_page():
    """求职匹配页面。"""
    from ..services.knowledge_db import knowledge_db
    stats = knowledge_db.stats()
    return render_template("job_match.html", title="求职匹配", stats=stats,
                           provinces=PROVINCE_CITIES)


@bp.route("/api/job-match/hot-industries", methods=["GET"])
def api_hot_industries():
    """返回库中活跃的行业列表。"""
    from ..services.knowledge_db import _get_conn
    import sqlite3
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT industry, COUNT(*) as c FROM companies
            WHERE industry IS NOT NULL AND industry != ''
            GROUP BY industry ORDER BY c DESC
        """).fetchall()
        return jsonify({"code": 0, "data": [{"name": r["industry"], "count": r["c"]} for r in rows]})
    finally:
        conn.close()


# ========== 企业名录（分页浏览） ==========
@bp.route("/companies")
def company_directory():
    """企业名录页面（分页浏览）。"""
    from ..services.knowledge_db import _get_conn
    import sqlite3

    page = request.args.get("page", 1, type=int)
    per_page = 20
    sort = request.args.get("sort", "name")
    industry_filter = request.args.get("industry", "")

    conn = _get_conn()
    conn.row_factory = sqlite3.Row
    try:
        where = ""
        params = []
        if industry_filter:
            where = "WHERE c.industry LIKE ?"
            params.append(f"%{industry_filter}%")

        # 总数
        total = conn.execute(
            f"SELECT COUNT(*) FROM companies c {where}", params
        ).fetchone()[0]
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))

        # 数据
        if sort == "name":
            order = "c.canonical_name ASC"
        elif sort == "newest":
            order = "c.created_at DESC"
        else:
            order = "c.canonical_name ASC"

        offset = (page - 1) * per_page
        rows = conn.execute(f"""
            SELECT c.id, c.canonical_name, c.industry, c.city, c.province,
                   cd.content as distilled_content
            FROM companies c
            LEFT JOIN company_data cd ON c.id=cd.company_id AND cd.data_type='distilled'
            {where}
            ORDER BY {order}
            LIMIT ? OFFSET ?
        """, params + [per_page, offset]).fetchall()

        # 行业列表（过滤用）
        industries = conn.execute("""
            SELECT industry, COUNT(*) as c FROM companies
            WHERE industry IS NOT NULL AND industry != ''
            GROUP BY industry ORDER BY c DESC
        """).fetchall()

        companies_data = []
        for r in rows:
            one_liner = ""
            if r["distilled_content"]:
                try:
                    d = json.loads(r["distilled_content"])
                    one_liner = d.get("one_liner", "")
                except Exception:
                    pass
            companies_data.append({
                "id": r["id"],
                "name": r["canonical_name"],
                "industry": r["industry"] or "",
                "city": r["city"] or "",
                "province": r["province"] or "",
                "one_liner": one_liner,
            })

        return render_template("company_directory.html",
                               companies=companies_data,
                               page=page, total_pages=total_pages,
                               total=total, per_page=per_page,
                               sort=sort,
                               industries=[{"name": r["industry"], "count": r["c"]} for r in industries],
                               selected_industry=industry_filter,
                               title="企业名录")
    except Exception as e:
        logger.error(f"企业名录加载失败: {e}")
        return render_template("error.html", message="企业名录加载失败"), 500
    finally:
        conn.close()


@bp.route("/company/detail/<int:company_id>")
def company_detail(company_id):
    """企业详情页：展示所有蒸馏字段。"""
    from ..services.knowledge_db import knowledge_db

    try:
        # 查找公司
        from ..services.knowledge_db import _get_conn
        import sqlite3
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
        conn.close()

        if not row:
            return render_template("error.html", message="未找到该公司"), 404

        company = dict(row)

        # 获取蒸馏数据
        distilled = knowledge_db.get_distilled(company_id)
        if not distilled:
            # 没蒸馏数据但有基本数据
            data_dict = knowledge_db.get_company_data(company_id)
            if data_dict:
                # 从维度数据构建简单信息
                basic = data_dict.get("basic", {}).get("content", {})
                ai_summary = data_dict.get("ai_summary", {}).get("content", {})
                return render_template("company_detail.html",
                                       company=company,
                                       has_distilled=False,
                                       basic=basic,
                                       ai_summary=ai_summary,
                                       title=company.get("canonical_name", ""))
            return render_template("error.html", message="该公司暂无数据"), 404

        kf = distilled.get("key_facts", {})
        return render_template("company_detail.html",
                               company=company,
                               has_distilled=True,
                               one_liner=distilled.get("one_liner", ""),
                               key_facts=kf,
                               sentiments=distilled.get("sentiment_top3", []),
                               risk_summary=distilled.get("risk_summary", ""),
                               job_seeker_note=distilled.get("job_seeker_note", ""),
                               title=company.get("canonical_name", ""))
    except Exception as e:
        logger.error(f"公司详情加载失败: company_id={company_id}, {e}")
        return render_template("error.html", message="公司详情加载失败"), 500


# ========== 永续优化引擎 API ==========
@bp.route("/api/optimizer/start", methods=["POST"])
def api_optimizer_start():
    """启动永续优化引擎。"""
    from ..services.optimization_engine import optimizer
    optimizer.start()
    return jsonify({"code": 0, "message": "优化引擎已启动", "status": optimizer.status()})


@bp.route("/api/optimizer/stop", methods=["POST"])
def api_optimizer_stop():
    """停止优化引擎。"""
    from ..services.optimization_engine import optimizer
    optimizer.stop()
    return jsonify({"code": 0, "message": "优化引擎已停止", "status": optimizer.status()})


@bp.route("/api/optimizer/status", methods=["GET"])
def api_optimizer_status():
    """查看优化引擎状态。"""
    from ..services.optimization_engine import optimizer
    return jsonify({"code": 0, "data": optimizer.status()})


@bp.route("/api/optimizer/scan-now", methods=["POST"])
def api_optimizer_scan_now():
    """触发立即全量扫描。"""
    from ..services.optimization_engine import optimizer
    import threading
    def _run_scan():
        optimizer._full_scan(optimizer._stats["total_scans"] + 1)
    threading.Thread(target=_run_scan, daemon=True).start()
    return jsonify({"code": 0, "message": "全量扫描已触发"})

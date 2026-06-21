# -*- coding: utf-8 -*-
"""
内推码 Blueprint — 聚合页 + 搜索 + 提交 + 反馈。
"""
import logging
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from ..services import referral_service as svc
from ..services.referral_collector import collector

logger = logging.getLogger(__name__)

bp = Blueprint("referral", __name__, url_prefix="/referral")


@bp.route("")
def referral_page():
    """内推码聚合首页。"""
    codes = svc.get_all_active()
    categories = svc.get_position_categories()
    return render_template("referral.html",
                           codes=codes,
                           categories=categories,
                           now=datetime.now())


@bp.route("/search")
def referral_search():
    """HTMX 搜索内推码，返回片段。"""
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "").strip()
    codes = svc.search(keyword=keyword, category=category)
    return render_template("partials/referral_list.html",
                           codes=codes,
                           now=datetime.now())


@bp.route("/company/<company_name>")
def referral_by_company(company_name: str):
    """公司详情页嵌入的内推码片段。"""
    codes = svc.get_by_company(company_name)
    return render_template("partials/referral_codes.html",
                           codes=codes,
                           company_name=company_name,
                           now=datetime.now())


@bp.route("/submit", methods=["POST"])
def referral_submit():
    """
    提交内推码 / 请求追踪。
    POST 参数:
        company_name (必填)
        code (可选，为空=请求追踪)
        platform, platform_url, recruiter_name, description, positions
    """
    company_name = request.form.get("company_name", "").strip()
    if not company_name:
        return jsonify({"success": False, "error": "请输入公司名称"}), 400

    code = request.form.get("code", "").strip() or None
    positions_raw = request.form.get("positions", "")
    positions = [p.strip() for p in positions_raw.split(",") if p.strip()] if positions_raw else None

    svc.submit_entry(
        company_name=company_name,
        code=code,
        platform=request.form.get("platform", "用户提交"),
        platform_url=request.form.get("platform_url", ""),
        referral_link=request.form.get("referral_link", ""),
        recruiter_name=request.form.get("recruiter_name", ""),
        recruiter_title=request.form.get("recruiter_title", ""),
        description=request.form.get("description", ""),
        positions=positions,
    )

    if code:
        msg = f"✅ 感谢提交！内推码 {code} 已收录，审核后展示。"
    else:
        msg = f"📡 已记录你对「{company_name}」的追踪请求，采集引擎将在下一轮处理。"

    return jsonify({"success": True, "message": msg})


@bp.route("/expired/<int:code_id>", methods=["POST"])
def report_expired(code_id: int):
    """反馈内推码已失效。"""
    success = svc.report_expired(code_id)
    return jsonify({"success": success, "message": "已反馈，感谢！" if success else "反馈失败"})


@bp.route("/request-track", methods=["POST"])
def request_track():
    """请求采集某公司的内推码。"""
    company_name = request.form.get("company_name", "").strip()
    if not company_name:
        return jsonify({"success": False, "error": "请输入公司名称"}), 400
    svc.request_track(company_name)
    # 如果采集器不在运行中，尝试启动
    if not collector.is_running():
        try:
            collector.start()
        except Exception:
            pass
    return jsonify({"success": True, "message": f"📡 已记录对「{company_name}」的追踪请求"})

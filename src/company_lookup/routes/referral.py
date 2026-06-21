# -*- coding: utf-8 -*-
"""
内推码 Blueprint — 聚合页 + 搜索 + 反馈。
仅展示 AI 验证通过的内推码，不接受用户提交。
"""
import logging
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request

from ..services import referral_service as svc

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


@bp.route("/expired/<int:code_id>", methods=["POST"])
def report_expired(code_id: int):
    """反馈内推码已失效。"""
    success = svc.report_expired(code_id)
    return jsonify({"success": success, "message": "已反馈，感谢！" if success else "反馈失败"})

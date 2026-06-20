# -*- coding: utf-8 -*-
"""API 配置管理路由：状态查询、保存、验证。"""

import logging
from flask import Blueprint, jsonify, request, render_template

from ..services.config_manager import get_status, save_key, validate_key, load_env, API_META

logger = logging.getLogger(__name__)

bp = Blueprint("config", __name__, url_prefix="/api/config")


@bp.route("/status", methods=["GET"])
def api_status():
    """获取所有 API 的配置状态（HTML 片段，供 HTMX 渲染）"""
    status = get_status()
    # 按 sort_order 排序
    apis = sorted(status.values(), key=lambda x: x["sort_order"])
    return render_template("partials/api_config_status.html", apis=apis)


@bp.route("/status-json", methods=["GET"])
def api_status_json():
    """获取所有 API 的配置状态（JSON 格式）"""
    return jsonify({"code": 0, "data": get_status()})


@bp.route("/validate", methods=["POST"])
def api_validate():
    """验证 API Key（不保存）"""
    api_type = request.form.get("api_type", "")
    api_key = request.form.get("api_key", "").strip()

    if not api_type:
        return jsonify({"valid": False, "message": "缺少 API 类型"})
    if not api_key:
        return jsonify({"valid": False, "message": "请输入 API Key"})

    meta = API_META.get(api_type)
    if not meta:
        return jsonify({"valid": False, "message": f"未知的 API 类型: {api_type}"})

    result = validate_key(api_type, api_key)
    return jsonify(result)


@bp.route("/save", methods=["POST"])
def api_save():
    """保存并验证 API Key"""
    api_type = request.form.get("api_type", "")
    api_key = request.form.get("api_key", "").strip()

    if not api_type:
        return '<div class="alert alert-danger">缺少 API 类型</div>'
    if not api_key:
        return '<div class="alert alert-danger">请输入 API Key</div>'

    meta = API_META.get(api_type)
    if not meta:
        return f'<div class="alert alert-danger">未知的 API 类型: {api_type}</div>'

    # 先验证
    validation = validate_key(api_type, api_key)
    if not validation.get("valid"):
        return f'<div class="alert alert-danger">{validation.get("message", "验证失败")}</div>'

    # 保存到 .env
    try:
        save_key(api_type, api_key)
        # 重新加载环境变量
        load_env()
        logger.info(f"API Key 已保存并生效: {meta['name']}")

        # 返回成功 HTML + 触发全局事件刷新状态
        return (
            '<div class="alert alert-success">✅ 验证成功，配置已保存！</div>'
            '<script>'
            '  setTimeout(function() {'
            '    var modal = bootstrap.Modal.getInstance(document.getElementById("apiConfigModal"));'
            '    if (modal) modal.hide();'
            '    document.body.dispatchEvent(new Event("config-updated"));'
            '  }, 800);'
            '</script>'
        )
    except Exception as e:
        logger.error(f"保存 API Key 失败: {e}")
        return f'<div class="alert alert-danger">保存失败: {str(e)[:80]}</div>'


@bp.route("/modal/<api_id>", methods=["GET"])
def config_modal(api_id):
    """渲染 API 配置弹窗内容（HTMX 片段）"""
    meta = API_META.get(api_id)
    if not meta:
        return f'<div class="alert alert-danger">未知的 API 类型: {api_id}</div>'

    from ..services.config_manager import get_status
    status = get_status()
    api_info = status.get(api_id, {})
    api_info["id"] = api_id
    api_info["name"] = meta["name"]
    api_info["icon"] = meta["icon"]
    api_info["description"] = meta["description"]
    api_info["apply_url"] = meta["apply_url"]
    return render_template("partials/api_config_modal.html", api=api_info)

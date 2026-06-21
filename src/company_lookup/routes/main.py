# -*- coding: utf-8 -*-
import json
import re
import logging
import os
import sqlite3
import uuid
from datetime import datetime

from flask import Blueprint, Response, current_app, jsonify, render_template, request

from ..services.company_service import clear_cache

logger = logging.getLogger(__name__)

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/company")
def company_page():
    return render_template("index.html")


@bp.route("/pipeline")
def pipeline():
    return render_template(
        "pipeline.html",
        pipeline={
            "intentional": [],
            "applied": [],
            "interviewing": [],
            "offer": [],
            "rejected": [],
        },
    )


@bp.route("/hybridaction/zybTrackerStatisticsAction", methods=["GET"])
def zyb_tracker():
    # SDK 可能使用 __callback__ / __callback / _callback 等不同参数名
    callback = (
        request.args.get("__callback__")
        or request.args.get("__callback")
        or request.args.get("_callback")
        or request.args.get("callback")
        or request.args.get("jsonp")
    )

    # 安全验证：只允许合法 JS 标识符
    if callback and not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$.]*$', callback):
        callback = None

    data = {
        "code": 0,
        "retcode": 0,
        "msg": "success",
        "message": "ok",
        "status": 200,
        "success": True,
        "data": {},
        "result": {"success": True, "rate": 1, "is_in_white_list": False},
        "list": [],
        "records": [],
        "ttl": 864000,
    }

    # iframe 模式（Network 中 Sec-Fetch-Dest: iframe）：body 内仅放纯 JSON 供 JSON.parse
    is_iframe = request.headers.get("Sec-Fetch-Dest") == "iframe"
    if is_iframe or not callback or (callback and callback.startswith("__cb__")):
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        html = (
            f'<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>{payload}</body></html>'
        )
        return Response(html, mimetype="text/html; charset=utf-8")

    if callback:
        response_text = f"""{callback}((function() {{
            var base = {{
                code: 0, retcode: 0, msg: "success", message: "ok", status: 200,
                success: true, data: {{}}, result: {{success: true}}, list: [], records: [],
                ttl: 864000,
                callback: function() {{}}, done: function() {{}}, complete: function() {{}},
                fail: function() {{}}, error: function() {{}}, always: function() {{}},
                __noop: function() {{}}
            }};
            return new Proxy(base, {{
                get: function(t, k) {{
                    if (k in t) return t[k];
                    if (typeof k === "string" && k !== "then") return function() {{ return true; }};
                    return t[k];
                }}
            }});
        }})());"""
        return Response(
            response_text,
            mimetype="application/javascript; charset=utf-8",
        )

    return jsonify(data)



DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_PATH = os.path.join(DB_DIR, "jobboard.db")


def _get_db():
    """Get SQLite connection, create table if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            status TEXT CHECK(status IN ('意向','已投递','面试中','Offer')) DEFAULT '意向',
            note TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    return conn


def _get_user_id():
    """Get or create a session-based user ID (stored on request context, thread-safe)."""
    if not hasattr(request, "_jobboard_uid"):
        uid = request.cookies.get("jobboard_uid", "")
        if not uid or len(uid) < 8:
            uid = str(uuid.uuid4())[:12]
        request._jobboard_uid = uid
    return request._jobboard_uid


@bp.route("/jobboard", methods=["GET"])
def jobboard_page():
    """求职看板主页"""
    return render_template("pipeline.html")


@bp.route("/jobboard/list", methods=["GET"])
def jobboard_list():
    """获取求职看板列表"""
    uid = _get_user_id()
    conn = _get_db()
    rows = conn.execute(
        "SELECT id, company_name, status, note, created_at, updated_at FROM job_applications WHERE user_id=? ORDER BY updated_at DESC",
        (uid,)
    ).fetchall()
    conn.close()

    # Count by status
    counts = {"意向": 0, "已投递": 0, "面试中": 0, "Offer": 0}
    cards = []
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        cards.append(dict(r))

    # Sanitize notes
    from markupsafe import escape
    for c in cards:
        c["note"] = escape(c.get("note", ""))
        c["company_name"] = escape(c["company_name"][:100])

    return render_template(
        "partials/jobboard_list.html",
        cards=cards,
        counts=counts,
    )


@bp.route("/jobboard/add", methods=["POST"])
def jobboard_add():
    """添加公司到求职看板"""
    company = request.form.get("company_name", "").strip()[:100]
    note = request.form.get("note", "").strip()[:500]

    if not company:
        return '<div class="alert alert-danger">请输入公司名称</div>'

    # Filter HTML
    from markupsafe import escape
    company = escape(company)
    note = escape(note)

    uid = _get_user_id()
    conn = _get_db()

    # Check duplicate
    existing = conn.execute(
        "SELECT id FROM job_applications WHERE user_id=? AND company_name=?",
        (uid, company)
    ).fetchone()
    if existing:
        conn.close()
        return f'<div class="alert alert-warning">「{company}」已在看板中</div>'

    conn.execute(
        "INSERT INTO job_applications (user_id, company_name, status, note) VALUES (?, ?, '意向', ?)",
        (uid, company, note)
    )
    conn.commit()
    conn.close()

    # Return the updated list
    from flask import Response as FlaskResponse
    resp = FlaskResponse(
        _render_jobboard_list(uid),
        mimetype="text/html"
    )
    # Set cookie for user identification
    resp.set_cookie("jobboard_uid", uid, max_age=365*24*3600)
    return resp


@bp.route("/jobboard/update", methods=["POST"])
def jobboard_update():
    """更新公司状态"""
    record_id = request.form.get("id", "").strip()
    new_status = request.form.get("status", "").strip()

    if not record_id or new_status not in ("意向", "已投递", "面试中", "Offer"):
        return '<div class="alert alert-danger">参数错误</div>'

    uid = _get_user_id()
    conn = _get_db()
    conn.execute(
        "UPDATE job_applications SET status=?, updated_at=datetime('now','localtime') WHERE id=? AND user_id=?",
        (new_status, record_id, uid)
    )
    conn.commit()
    conn.close()

    return _render_jobboard_list(uid)


@bp.route("/jobboard/delete", methods=["POST"])
def jobboard_delete():
    """删除公司记录"""
    record_id = request.form.get("id", "").strip()
    if not record_id:
        return '<div class="alert alert-danger">参数错误</div>'

    uid = _get_user_id()
    conn = _get_db()
    conn.execute("DELETE FROM job_applications WHERE id=? AND user_id=?", (record_id, uid))
    conn.commit()
    conn.close()

    return _render_jobboard_list(uid)


def _render_jobboard_list(uid):
    """Renders the job board list HTML fragment."""
    conn = _get_db()
    rows = conn.execute(
        "SELECT id, company_name, status, note, created_at, updated_at FROM job_applications WHERE user_id=? ORDER BY updated_at DESC",
        (uid,)
    ).fetchall()
    conn.close()

    counts = {"意向": 0, "已投递": 0, "面试中": 0, "Offer": 0}
    cards = []
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
        cards.append(dict(r))

    from markupsafe import escape
    for c in cards:
        c["note"] = escape(c.get("note", ""))
        c["company_name"] = escape(c["company_name"][:100])

    from flask import render_template as _r
    return _r("partials/jobboard_list.html", cards=cards, counts=counts)

@bp.route("/api/clear-cache", methods=["POST"])
def api_clear_cache():
    clear_cache()
    logger.info("Cache cleared via API")
    return jsonify({"success": True, "message": "缓存已清除"})


@bp.route("/test", methods=["GET"])
def test_route():
    return "test ok"


@bp.route("/api/debug/routes", methods=["GET"])
def debug_routes():
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append(
            {
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "path": str(rule),
            }
        )
    return jsonify(routes)

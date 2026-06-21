# -*- coding: utf-8 -*-
"""应用工厂：配置、日志、蓝图注册。"""

import logging
import os
import sys
import time

from flask import Flask, request, render_template

# 尝试加载.env文件
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # 手动读取.env文件（位于项目根目录）
    current_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(current_dir))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

from .config import config_by_name
from .routes.register import register_blueprints


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_class)

    # 设置编码
    app.config["JSON_AS_ASCII"] = False

    _setup_logging(app)
    _register_middleware(app)
    _register_error_handlers(app)
    register_blueprints(app)

    # 注入外部查询链接到所有模板
    @app.context_processor
    def inject_external_links():
        from .config import EXTERNAL_LINKS
        return dict(external_links=EXTERNAL_LINKS)

    # ═══════════════════════════════════════════════
    #  自动启动后台维护引擎
    # ═══════════════════════════════════════════════
    def _start_background_services():
        """启动后台守护服务（发现引擎 + 维护引擎 + 优化引擎）。"""
        if os.environ.get("DISABLE_BACKGROUND_SERVICES", "").lower() in ("true", "1"):
            return
        import logging
        log = logging.getLogger(__name__)
        try:
            from .services.knowledge_maintainer import maintainer
            maintainer.start()
            log.info("[App] ✅ 知识库维护引擎已自动启动")
        except Exception as e:
            log.warning(f"[App] 维护引擎启动失败: {e}")
        try:
            from .services.optimization_engine import optimizer
            optimizer.start()
            log.info("[App] ✅ 永续优化引擎已自动启动")
        except Exception as e:
            log.warning(f"[App] 优化引擎启动失败: {e}")
        try:
            from .services.referral_collector import collector
            from .services.scrapers.maimai import MaimaiScraper
            from .services.scrapers.zhihu import ZhihuScraper
            collector.set_scrapers([MaimaiScraper(), ZhihuScraper()])
            collector.start()
            log.info("[App] ✅ 内推码采集引擎已自动启动")
        except Exception as e:
            log.warning(f"[App] 内推码采集引擎启动失败: {e}")
        try:
            from .services.discovery_engine import discovery_engine
            discovery_engine.start()
            log.info("[App] ✅ 持续发现引擎已自动启动")
        except Exception as e:
            log.warning(f"[App] 持续发现引擎启动失败: {e}")

    # 使用 Flask 的 first_request 或 after_request 来避免阻塞
    import threading
    threading.Thread(target=_start_background_services, daemon=True).start()

    return app


def _setup_logging(app):
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    app.logger.setLevel(log_level)


def _register_middleware(app):


    @app.before_request
    def before_request():
        # 记录请求开始时间
        request._start_time = time.time()

    @app.after_request
    def after_request(response):
        # 仅对无 Content-Type 或 text/html 的响应设置 charset
        ct = response.content_type or ""
        if not ct or ct == "text/html":
            response.headers["Content-Type"] = "text/html; charset=utf-8"
        # 记录请求耗时
        if hasattr(request, "_start_time"):
            elapsed = time.time() - request._start_time
            if elapsed > 1:
                app.logger.warning(f"耗时较长: {request.method} {request.path} - {elapsed:.2f}s")
            elif elapsed > 0.1:
                app.logger.info(f"请求耗时: {request.method} {request.path} - {elapsed:.2f}s")
        return response


def _register_error_handlers(app):
    """注册全局错误处理器，避免 HTMX 请求收到默认 HTML 错误页。"""

    @app.errorhandler(404)
    def not_found(e):
        app.logger.warning(f"404: {request.path}")
        if request.headers.get("HX-Request"):
            return _htmx_error("请求的资源不存在"), 200
        return render_template("error.html", code=404, message="页面未找到"), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Internal server error")
        if request.headers.get("HX-Request"):
            return _htmx_error("服务器内部错误，请稍后重试"), 200
        return render_template("error.html", code=500, message="服务器内部错误"), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.exception("Unhandled exception")
        if request.headers.get("HX-Request"):
            return _htmx_error("操作失败，请稍后重试"), 200
        return render_template("error.html", code=500, message="服务器内部错误"), 500


def _htmx_error(message: str) -> str:
    """为 HTMX 请求生成 HTML 错误片段。"""
    return f'<div class="alert alert-danger alert-dismissible fade show m-3" role="alert">' \
           f'<i class="bi bi-exclamation-triangle me-2"></i>{message}' \
           f'<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>'

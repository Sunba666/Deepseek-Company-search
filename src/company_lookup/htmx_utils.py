# -*- coding: utf-8 -*-
import logging
from functools import wraps

from flask import render_template

logger = logging.getLogger(__name__)


def error_alert(message: str, status: int = 200):
  """HTMX 请求统一返回 HTML 错误片段，避免白屏。"""
  return render_template("partials/error_alert.html", message=message), status


def route_errors(default_message: str = "操作失败，请稍后重试"):
  """路由异常装饰器：捕获异常并返回 alert 片段。"""

  def decorator(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
      try:
        return fn(*args, **kwargs)
      except Exception as exc:
        try:
            logger.exception("%s: %s", fn.__name__, exc)
        except Exception:
            pass
        try:
            return error_alert(f"{default_message}：{str(exc)[:200]}")
        except Exception:
            return error_alert(default_message)

    return wrapper

  return decorator

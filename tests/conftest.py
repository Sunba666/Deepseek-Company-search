# -*- coding: utf-8 -*-
"""pytest fixtures for Company Lookup integration tests."""

import os
import pytest

# ── 测试环境：强制使用模拟数据，不依赖外部API ──
# 必须在 import app 之前设置，因为 app.py 在模块级加载 .env
os.environ.setdefault("FLASK_ENV", "development")
os.environ.setdefault("TESTING", "true")


@pytest.fixture(scope="session")
def app():
    """Create a Flask application for testing."""
    # 关闭后台守护线程（测试环境下不启动知识库维护/优化引擎）
    os.environ["DISABLE_BACKGROUND_SERVICES"] = "true"
    from company_lookup.app import create_app
    application = create_app()
    application.config.update({
        "TESTING": True,
    })
    return application


@pytest.fixture
def client(app):
    """Flask test client — 用于直接模拟 HTTP 请求."""
    return app.test_client()


# ── 常用测试数据 ──────────────────────────────────

# 应能正常返回数据的公司简称
KNOWN_COMPANIES = [
    "米哈游",
    "腾讯",
    "字节跳动",
    "阿里巴巴",
    "华为",
    "美团",
    "京东",
    "百度",
    "网易",
    "拼多多",
    "快手",
    "滴滴",
    "莉莉丝",
    "鹰角",
    "B站",
]

# 预期失败的公司（未收录/非企业实体）
INVALID_INPUTS = [
    "张三",         # 人名
    "天气",         # 非公司
    "小明",         # 人名
    "",             # 空字符串
    "a",            # 单字符
]

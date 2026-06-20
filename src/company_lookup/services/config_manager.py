# -*- coding: utf-8 -*-
"""
API Key 配置管理器：读写 .env 文件 + 在线验证 Key 有效性。
"""
import os
import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ==================== API 元信息 ====================

API_META = {
    "deepseek": {
        "name": "DeepSeek AI",
        "icon": "🤖",
        "description": "深度求索 AI 大模型，用于生成智能分析报告",
        "apply_url": "https://platform.deepseek.com/api_keys",
        "env_key": "DEEPSEEK_API_KEY",
        "sort_order": 0,
    },
    "tianyacha": {
        "name": "天眼查",
        "icon": "📋",
        "description": "企业工商信息查询，获取注册信息、股东结构等",
        "apply_url": "https://open.tianyancha.com/",
        "env_key": "TIANYACHA_API_KEY",
        "sort_order": 1,
    },
    "qichacha": {
        "name": "企查查",
        "icon": "📋",
        "description": "企业信用信息查询（天眼查的备选方案）",
        "apply_url": "https://www.qcc.com/",
        "env_key": "QICHACHA_API_KEY",
        "sort_order": 2,
    },
    "tavily": {
        "name": "Tavily 搜索",
        "icon": "🔍",
        "description": "AI 搜索引擎，用于员工评价、薪资爆料等舆情搜索",
        "apply_url": "https://app.tavily.com/",
        "env_key": "TAVILY_API_KEY",
        "sort_order": 3,
    },
    "bing_news": {
        "name": "必应新闻",
        "icon": "📰",
        "description": "微软必应新闻搜索，获取公司最新动态",
        "apply_url": "https://portal.azure.com/#create/microsoft.bingsearch",
        "env_key": "BING_API_KEY",
        "sort_order": 4,
    },
    "qixinbao": {
        "name": "启信宝",
        "icon": "⚖️",
        "description": "企业司法风险查询，包括涉诉、失信记录等",
        "apply_url": "https://www.qixin.com/",
        "env_key": "QIXINBAO_API_KEY",
        "sort_order": 5,
    },
}

ENV_FILE = None  # 延迟初始化


def _get_env_path() -> str:
    global ENV_FILE
    if ENV_FILE is None:
        # 从项目根目录查找 .env
        current = os.path.dirname(os.path.abspath(__file__))
        # src/company_lookup/services/ -> src/company_lookup/ -> src/ -> 项目根
        ENV_FILE = os.path.abspath(os.path.join(current, "..", "..", "..", ".env"))
    return ENV_FILE


def load_env():
    """重新加载 .env 到 os.environ"""
    env_path = _get_env_path()
    if not os.path.exists(env_path):
        logger.warning(f".env 文件不存在: {env_path}")
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def get_status() -> Dict:
    """获取所有 API 的配置状态"""
    status = {}
    for api_id, meta in API_META.items():
        key = meta["env_key"]
        value = os.environ.get(key, "")
        status[api_id] = {
            "id": api_id,
            "name": meta["name"],
            "icon": meta["icon"],
            "description": meta["description"],
            "apply_url": meta["apply_url"],
            "configured": bool(value),
            "key_preview": value[:8] + "..." if value and len(value) > 10 else "",
            "sort_order": meta["sort_order"],
        }
    return status


def save_key(api_id: str, api_key: str) -> bool:
    """保存 API Key 到 .env 文件"""
    meta = API_META.get(api_id)
    if not meta:
        raise ValueError(f"未知的 API 类型: {api_id}")

    env_key = meta["env_key"]
    env_path = _get_env_path()

    # 读取当前 .env 内容
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # 查找并替换或追加
    found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{env_key}=") or stripped.startswith(f"{env_key} ="):
            new_lines.append(f"{env_key}={api_key}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        # 在文件末尾追加注释分组
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines.append("\n")
        new_lines.append(f"\n# ===== {meta['name']} =====\n")
        new_lines.append(f"{env_key}={api_key}\n")

    # 写回 .env
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    # 更新当前进程的环境变量
    os.environ[env_key] = api_key

    logger.info(f"✅ API Key 已保存: {meta['name']}")
    return True


def validate_key(api_id: str, api_key: str) -> Dict:
    """在线验证 API Key 有效性"""
    import requests

    meta = API_META.get(api_id)
    if not meta:
        return {"valid": False, "message": f"未知的 API 类型: {api_id}"}

    try:
        if api_id == "deepseek":
            return _validate_deepseek(api_key)
        elif api_id == "tavily":
            return _validate_tavily(api_key)
        elif api_id == "tianyacha":
            return _validate_tianyacha(api_key)
        elif api_id == "qichacha":
            return _validate_qichacha(api_key)
        elif api_id in ("bing_news",):
            return _validate_bing(api_key)
        elif api_id == "qixinbao":
            return _validate_qixinbao(api_key)
        else:
            # 无法在线验证，仅格式校验
            return {"valid": True, "message": "已保存（无法在线验证此 API）"}
    except requests.exceptions.Timeout:
        return {"valid": False, "message": "验证请求超时，请检查网络连接"}
    except requests.exceptions.ConnectionError:
        return {"valid": False, "message": "无法连接到验证服务器，请检查网络"}
    except Exception as e:
        logger.error(f"验证 {meta['name']} 失败: {e}")
        return {"valid": False, "message": f"验证失败: {str(e)[:80]}"}


def _validate_deepseek(api_key: str) -> Dict:
    """验证 DeepSeek API Key"""
    import requests
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(
        "https://api.deepseek.com/models",
        headers=headers,
        timeout=10,
    )
    if resp.status_code == 200:
        return {"valid": True, "message": "✅ API Key 有效"}
    elif resp.status_code == 401:
        return {"valid": False, "message": "❌ API Key 无效（认证失败）"}
    else:
        return {"valid": False, "message": f"❌ 返回状态码 {resp.status_code}"}


def _validate_tavily(api_key: str) -> Dict:
    """验证 Tavily API Key"""
    import requests
    resp = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": api_key, "query": "test", "max_results": 1},
        timeout=10,
    )
    if resp.status_code == 200:
        return {"valid": True, "message": "✅ API Key 有效"}
    elif resp.status_code == 401 or resp.status_code == 403:
        return {"valid": False, "message": "❌ API Key 无效（认证失败）"}
    elif resp.status_code == 432:
        return {"valid": False, "message": "❌ 使用额度已耗尽（需升级套餐或续费）"}
    else:
        return {"valid": False, "message": f"❌ 返回状态码 {resp.status_code}"}


def _validate_tianyacha(api_key: str) -> Dict:
    """验证天眼查 API Key"""
    import requests
    resp = requests.get(
        "https://open.tianyancha.com/api/open/v4/baseinfo/getByName",
        params={"name": "test"},
        headers={"Authorization": api_key},
        timeout=10,
    )
    ct = resp.headers.get("Content-Type", "")
    if resp.status_code == 200 and "json" in ct:
        data = resp.json()
        if data.get("error_code") == 0:
            return {"valid": True, "message": "✅ API Key 有效"}
        else:
            return {"valid": False, "message": f"❌ API 返回错误: {data.get('message', resp.text[:100])}"}
    elif resp.status_code == 200:
        return {"valid": False, "message": "❌ 返回 HTML 而非数据（API 端点或 Key 无效，请确认从 https://open.tianyancha.com 申请的正确 Key）"}
    else:
        return {"valid": False, "message": f"❌ 返回状态码 {resp.status_code}"}


def _validate_qichacha(api_key: str) -> Dict:
    """验证企查查 API Key"""
    import requests
    resp = requests.get(
        "https://api.qcc.com/api/entdetail/getByName",
        params={"keyWord": "test"},
        headers={"Token": api_key},
        timeout=10,
    )
    if resp.status_code == 200:
        return {"valid": True, "message": "✅ API Key 有效"}
    else:
        return {"valid": False, "message": f"❌ 返回状态码 {resp.status_code}"}


def _validate_bing(api_key: str) -> Dict:
    """验证必应搜索 API Key"""
    import requests
    resp = requests.get(
        "https://api.bing.microsoft.com/v7.0/news/search",
        params={"q": "test", "count": 1},
        headers={"Ocp-Apim-Subscription-Key": api_key},
        timeout=10,
    )
    if resp.status_code == 200:
        return {"valid": True, "message": "✅ API Key 有效"}
    else:
        return {"valid": False, "message": f"❌ 返回状态码 {resp.status_code}"}




def _validate_qixinbao(api_key: str) -> Dict:
    """验证启信宝 API Key（无法在线验证，仅检查格式）"""
    if len(api_key) >= 8:
        return {"valid": True, "message": "已保存（启信宝暂不支持在线验证）"}
    return {"valid": False, "message": "Key 格式不正确（长度不足）"}

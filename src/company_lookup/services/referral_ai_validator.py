# -*- coding: utf-8 -*-
"""
ReferralAIValidator — 内推码 AI 批量验证器。

将一批未经验证的内推码（含原始帖子内容）发给 DeepSeek，
由 AI 判断每条内推码是否真实有效。
只标记明确的判断结果，不确定的不处理。
"""
import json
import logging
import os
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

VALIDATOR_SYSTEM_PROMPT = (
    "你是一个专注判断内推码真伪的审核助手。\n\n"
    "你会收到一批从脉脉、知乎采集的内推帖信息，每条包含："
    "公司名、内推码、发帖人、发帖内容摘要（或全文）。\n\n"
    "请判断每条内推码是否真实有效，输出 JSON 格式。\n\n"
    "判断标准：\n"
    "1. 帖子内容看起来是真实的员工/HR 内推帖 → '有效'\n"
    "2. 帖子内容很可能是营销号、广告、过期搬运 → '可疑'\n"
    "3. 信息不足以判断 → '待验证'\n\n"
    "注意：\n"
    "- 仅当内容明显不可信（如全是广告词、无实质内容、过期搬运）时才标'可疑'\n"
    "- 内容看起来真诚、有具体信息、有内推码则标'有效'\n"
    "- 模糊不清或信息太少则标'待验证'\n"
    "- 对每条给出简短理由（10字以内）\n\n"
    "返回格式（纯 JSON，不要 markdown 代码块标记）：\n"
    "{\"results\": [\n"
    "  {\"index\": 0, \"judgment\": \"有效\", \"reason\": \"员工本人发帖，描述具体\"},\n"
    "  {\"index\": 1, \"judgment\": \"可疑\", \"reason\": \"纯广告文案，无实质内容\"},\n"
    "  {\"index\": 2, \"judgment\": \"待验证\", \"reason\": \"信息太少无法判断\"}\n"
    "]}\n"
)


def _call_deepseek(system_prompt: str, prompt: str) -> Optional[str]:
    """调用 DeepSeek API。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        logger.warning("[AI验证] DEEPSEEK_API_KEY 未配置")
        return None

    try:
        import openai
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=30,
            max_retries=1,
        )
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"[AI验证] DeepSeek 调用失败: {e}")
        return None


def build_batch_prompt(items: List[Dict]) -> str:
    """构建批量验证的 prompt。"""
    lines = ["请判断以下内推码的真伪：\n"]
    for i, item in enumerate(items):
        content = item.get("raw_content", "") or item.get("description", "")
        # 截断以防超 token
        if len(content) > 600:
            content = content[:600] + "…"
        lines.append(
            f"[{i}] 公司：{item.get('company_name', '')}\n"
            f"    内推码：{item.get('code', '')}\n"
            f"    平台：{item.get('platform', '')}\n"
            f"    发帖人：{item.get('recruiter_name', '')}\n"
            f"    内容：{content}\n"
        )
    return "\n".join(lines)


def validate_batch(items: List[Dict]) -> List[Tuple[int, str, str]]:
    """
    批量验证一批内推码。
    返回 List[(index_in_input, judgment, reason)]
    judgment: '有效' | '可疑' | '待验证'
    如果 API 调用失败，返回空列表。
    """
    if not items:
        return []

    prompt = build_batch_prompt(items)
    logger.info(f"[AI验证] 批量验证 {len(items)} 条内推码")

    result = _call_deepseek(VALIDATOR_SYSTEM_PROMPT, prompt)
    if not result:
        logger.warning("[AI验证] API 返回空，跳过本轮")
        return []

    # 解析 JSON 响应
    try:
        # 清理可能的 markdown 包围
        cleaned = result.strip()
        if cleaned.startswith("```"):
            # 去掉 ```json ... ```
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0].strip()
        data = json.loads(cleaned)

        judgments = []
        for r in data.get("results", []):
            idx = r.get("index")
            judgment = r.get("judgment", "待验证")
            reason = r.get("reason", "")
            if idx is not None and 0 <= idx < len(items):
                judgments.append((idx, judgment, reason))

        logger.info(f"[AI验证] 完成：{len(judgments)} 条有结果")
        return judgments

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"[AI验证] 解析 AI 返回失败: {e}\n返回内容: {result[:200]}")
        return []

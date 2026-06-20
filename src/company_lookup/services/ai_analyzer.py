# -*- coding: utf-8 -*-
"""AI分析模块 - 统一分析入口"""

import os
import json
import markdown
from datetime import datetime
import logging
from .api_client import retry_on_failure, log_api_call, API_TIMEOUT

logger = logging.getLogger(__name__)

# 【注意】DEEPSEEK_API_KEY 不再使用模块级变量，改为 _get_api_key() 动态读取。
# 原因：app.py 手动加载 .env 发生在 import 之后，模块级变量在 import 时已绑定空值。
# 保留常量仅用于文档引用，实际 API 调用使用 _get_api_key()。
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def build_company_analysis_prompt(company_name: str, raw_data: dict, credit_data: dict = None) -> str:
    """
    构建公司分析Prompt - 查询场景

    :param company_name: 公司名称
    :param raw_data: 原始数据字典
    :param credit_data: 官方信用档案数据
    :return: 完整的Prompt字符串
    """
    # 【修复】raw_data 的 key 与 aggregator 返回的 source id 对齐
    # aggregator 返回: tianyacha, tavily, wenshu, deepseek
    # 之前 prompt 中误用 'court' 而非 'wenshu'，导致司法风险数据丢失
    
    # 构建官方信用摘要
    credit_summary = ""
    if credit_data and credit_data.get("is_valid"):
        credit_summary = f"""
【官方信用档案（来自国家企业信用信息公示系统）】
- 注册资本：{credit_data.get('registered_capital', '未公开')}
- 实缴资本：{credit_data.get('paid_in_capital', '未公开')}
- 法定代表人：{credit_data.get('legal_representative', '未公开')}
- 成立日期：{credit_data.get('establishment_date', '未知')}
- 经营状态：{credit_data.get('company_status', '未知')}
- 企业类型：{credit_data.get('company_type', '未知')}
- 统一社会信用代码：{credit_data.get('unified_credit_code', '未公开')}
- 注册地址：{credit_data.get('registered_address', '未公开')}

信用风险记录：
- 行政处罚：{'有' if credit_data.get('punishment_records') else '无'}
- 经营异常：{'有' if credit_data.get('abnormal_operation_records') else '无'}
- 严重违法失信：{'有' if credit_data.get('serious_discredit_records') else '无'}
- 其他经营风险：{'有' if credit_data.get('risk_records') else '无'}

请在下方的报告中增加一段「官方信用评估」模块，基于以上官方数据给出求职者视角的解读。
解读时注意：
- 如果官方数据和网络舆情有矛盾（如官方显示"存续"但网络传闻"裁员"），如实呈现并给出建议
- 注册资本实缴说明资金实力可靠
- 无行政处罚说明合规经营
- 让求职者理解这些工商层面的数据对入职决策意味着什么
"""
    
    return f"""
你是一位资深职场顾问，帮求职者看懂一家公司值不值得去。
请基于以下数据，为「{company_name}」写一份分析报告。

【参考数据】
- 工商信息：{raw_data.get("tianyacha", "无")}
- 网络舆情：{raw_data.get("tavily", "无")}
- 司法风险：{raw_data.get("wenshu", "无")}
{credit_summary}

【写作要求】
写报告时记住这四条：
1. **说人话** — 别像机器翻译，别用"基于以上数据，我们可以得出"。就像跟朋友聊天一样说重点。
2. **有洞察** — 不要复述数据。要告诉求职者："这对你意味着什么"。比如薪资高但不加班 vs 薪资低但稳定。
3. **有行动** — 每段结论后面跟一句具体建议。"适合谁投、面试时注意什么、怎么谈薪资"。
4. **简洁** — 能一句话说清楚的事，不说两句。

【结构要求】
严格按以下 Markdown 结构输出，总-分-总：

### 📊 一句话总结
用一句话说清楚这家公司是做什么的、对求职者意味着什么。

### ⭐ 核心亮点 vs 风险
列出 2-3 个亮点和 1-2 个风险点，每条不超过 30 字。
亮点要说明"这对求职者有什么好处"，风险要说明"面试时可以怎么核实"。

### 💬 口碑速览
如果数据里有员工评价，用一两句话说清楚大家怎么看这家公司。
如果数据不足，就写"目前公开评价较少，建议面试时多问团队情况"——别硬编。

### 🎯 适合人群 + 行动建议
- 适合哪类求职者（想冲的/求稳的/转行的…）
- 面试时重点核实什么
- 谈薪资时有什么筹码

### 📋 官方信用评估
基于官方信用档案数据，从求职者角度解读：
- 注册资本实缴 → 资金实力判断
- 经营状态 → 公司稳定性
- 行政处罚/经营异常 → 合规风险
- 如果官方数据与网络舆情有矛盾，如实呈现
- 一句话总结：这家公司在工商层面靠不靠谱

### 💬 HR 视角 Q&A
生成 6-8 个求职者常问的问题和回答。
覆盖薪资福利、晋升、文化、稳定性、招聘流程等维度。
回答要实在，数据有就引用，没有就写"建议面试时直接问对方"。
"""


def build_compare_analysis_prompt(
    company_a: str, company_b: str, data_a: dict, data_b: dict
) -> str:
    """
    构建公司对比分析Prompt - 对比场景

    :param company_a: 公司A名称
    :param company_b: 公司B名称
    :param data_a: 公司A的原始数据
    :param data_b: 公司B的原始数据
    :return: 完整的Prompt字符串
    """
    return f"""
你是一位职场顾问，帮求职者对比两家公司哪家更适合。

对比「{company_a}」和「{company_b}」：

【参考数据】
{company_a}：{data_a}
{company_b}：{data_b}

【写作要求】
1. 说人话 — 别像机器翻译，别用"基于以上数据"这种废话。
2. 有洞察 — 数据差异对求职者意味着什么，说出来。
3. 有行动 — 每段结论后跟一句具体建议。
4. 简洁 — 一句话能说清楚就不说两句。

【结构要求】

### 📊 一句话定位
各用一句话说清楚两家公司分别适合什么样的求职者。

### 📋 四维对比（表格）
从这四个维度对比：薪酬待遇、职业发展、工作氛围、公司稳定性
每个维度写清楚"哪家更好、好在哪、对你意味着什么"。

### 🏆 结论
直接说：建议选哪家，以及为什么。
如果各有优劣，说清楚"什么情况下选A、什么情况下选B"。

### 💡 面试准备建议
- 如果面A，重点准备什么
- 如果面B，重点准备什么
- 两家之间怎么谈薪资筹码
"""


def build_trend_analysis_prompt(company_name: str, historical_data: list) -> str:
    """
    构建趋势分析Prompt - 趋势场景

    :param company_name: 公司名称
    :param historical_data: 历史舆情数据列表
    :return: 完整的Prompt字符串
    """
    return f"""
你是一位舆情分析师，用大白话帮求职者看懂一家公司的舆论风向。

分析「{company_name}」的最新舆情趋势：

【参考数据】
{json.dumps(historical_data, ensure_ascii=False, indent=2)}

【要求】
1. 别啰嗦 — 直接说趋势是变好了还是变差了。
2. 别只说现象 — 要告诉求职者"这对他意味着什么"。
3. 给建议 — 面试时可以借这个话题问对方什么。

### 舆情走向
一句话总结是上升、下降还是平稳。

### 关键事件
最近有什么值得关注的事，对求职者是机会还是风险。

### 面试小贴士
跟面试官聊这个话题时，注意什么、怎么问。
"""


def _get_api_key() -> str:
    """
    动态获取 DeepSeek API Key。
    【修复】原实现使用模块级变量 DEEPSEEK_API_KEY，在 import 时即绑定，
    若 .env 在 import 之后才加载（如 Flask app.py 中的手动加载），
    则模块变量仍为空字符串。改为每次调用时从 os.environ 动态读取。
    """
    return os.environ.get("DEEPSEEK_API_KEY", "").strip()


# ========== System Prompt ==========
_HR_ANALYST_PROMPT = (
    "You are a career advisor helping job seekers evaluate companies.\n"
    "Speak naturally — like a friend giving honest advice, not a corporate report.\n\n"
    "WRITING RULES:\n"
    "1. BE HUMAN. No 'based on the above data', no 'it is recommended that'. Just say what matters.\n"
    "2. BE INSIGHTFUL. Don't repeat data — tell them what it MEANS for a job seeker.\n"
    "   'High registered capital' → 'They have money, less layoff risk'\n"
    "   'Many lawsuits' → 'Check if these are labor disputes, ask in interview'\n"
    "3. BE ACTIONABLE. Every section ends with something the reader can DO.\n"
    "4. BE CONCISE. One clear sentence beats two vague ones.\n\n"
    "STRUCTURE (总-分-总):\n"
    "- One-Sentence Summary\n"
    "- Key Highlights vs Risks (2-3 each, with job seeker insight)\n"
    "- Reputation Snapshot (natural, not mechanical)\n"
    "- Who this is for + Action Steps\n"
    "- HR FAQ (6-8 Q&A, honest answers)\n\n"
    "IMPORTANT: Never fabricate. When data is missing, say 'Not much public info on this — ask directly in the interview.'\n"
    "Don't say 'data insufficient' as an excuse — turn absence into actionable advice.\n"
)

def _call_deepseek_api(
    prompt: str,
    system_prompt: str = _HR_ANALYST_PROMPT,
):
    """
    调用DeepSeek API生成内容（带重试+超时）

    :param prompt: 用户提示
    :param system_prompt: 系统提示
    :return: AI生成的内容，失败返回None
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        import openai

        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=API_TIMEOUT,
            max_retries=2,
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
            timeout=API_TIMEOUT,
        )

        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"DeepSeek API调用失败: {e}", exc_info=True)
        return None


@retry_on_failure(max_retries=1, api_name="analyze_company")
def analyze_company(company_name: str, raw_data: dict, credit_data: dict = None) -> dict:
    """
    分析单个公司 - 统一分析入口

    :param company_name: 公司名称
    :param raw_data: 原始数据字典
    :param credit_data: 官方信用档案数据（可选）
    :return: 分析结果字典
    """
    prompt = build_company_analysis_prompt(company_name, raw_data, credit_data)
    ai_result = _call_deepseek_api(prompt)

    if ai_result:
        return {
            "success": True,
            "report": ai_result,
            "report_html": markdown.markdown(ai_result),
            "raw_data": raw_data,
            "analysis_time": datetime.now().isoformat(),
            "data_sources": list(raw_data.keys()),
        }
    else:
        return {
            "success": False,
            "error": "AI分析暂时不可用",
            "raw_data": raw_data,
            "analysis_time": datetime.now().isoformat(),
        }


@retry_on_failure(max_retries=1, api_name="compare_companies")
def compare_companies(company_a: str, company_b: str, data_a: dict, data_b: dict) -> dict:
    """
    对比分析两家公司

    :param company_a: 公司A名称
    :param company_b: 公司B名称
    :param data_a: 公司A的原始数据
    :param data_b: 公司B的原始数据
    :return: 对比分析结果字典
    """
    prompt = build_compare_analysis_prompt(company_a, company_b, data_a, data_b)
    ai_result = _call_deepseek_api(prompt)

    if ai_result:
        return {
            "success": True,
            "report": ai_result,
            "report_html": markdown.markdown(ai_result),
            "company_a": company_a,
            "company_b": company_b,
            "raw_data": {"company_a": data_a, "company_b": data_b},
            "analysis_time": datetime.now().isoformat(),
        }
    else:
        return {
            "success": False,
            "error": "AI分析暂时不可用",
            "company_a": company_a,
            "company_b": company_b,
            "raw_data": {"company_a": data_a, "company_b": data_b},
            "analysis_time": datetime.now().isoformat(),
        }


def analyze_trend(company_name: str, historical_data: list) -> dict:
    """
    分析公司舆情趋势

    :param company_name: 公司名称
    :param historical_data: 历史舆情数据列表
    :return: 趋势分析结果字典
    """
    prompt = build_trend_analysis_prompt(company_name, historical_data)
    ai_result = _call_deepseek_api(prompt)

    if ai_result:
        return {
            "success": True,
            "report": ai_result,
            "report_html": markdown.markdown(ai_result),
            "company_name": company_name,
            "raw_data": historical_data,
            "analysis_time": datetime.now().isoformat(),
        }
    else:
        return {
            "success": False,
            "error": "AI分析暂时不可用",
            "company_name": company_name,
            "raw_data": historical_data,
            "analysis_time": datetime.now().isoformat(),
        }


def resolve_with_ai(user_input: str) -> dict:
    """
    使用 DeepSeek 对用户输入进行智能公司名消歧。
    判断公司是否存在、匹配官方全称、提供已知信息。

    :param user_input: 用户输入的公司名称（简称、昵称、全称等）
    :return: 消歧结果字典
    """
    system_prompt = """你是一个专业的企业信息查询助手。请对用户输入的企业名称进行智能分析和消歧。

    请按以下 JSON 格式回复（只输出 JSON，不要有其他内容）：
    {
        "exists": true/false,
        "canonical_name": "若存在，输出官方全称；若不存在，输出空字符串",
        "confidence": "high/medium/low",
        "industry": "所属行业或领域，若无法判断则输出 unknown",
        "known_info": "简短的公司简介（不超过50字），基于你的知识库，若无则输出空字符串",
        "related": ["可能相关的公司名或品牌名，若没有则输出空数组"],
        "suggestion": "给用户的查询建议，如'建议尝试使用某公司作为关键词'",
        "reason": "你做出上述判断的理由（一句话）"
    }

    **重要规则：**
    1. 如果你不确定该公司是否存在，请将 exists 设为 false，并在 reason 中说明不确定
    2. 不要编造信息，只基于你的训练数据中的已知信息
    3. 如果用户输入的是简称或昵称（如"大疆"对应"大疆创新"），请输出 canonical_name
    4. 如果用户输入的是明显的人名或非公司实体，请将 exists 设为 false
    """

    user_prompt = f'用户输入的公司名称是："{user_input}"，请进行分析。'
    response = _call_deepseek_api(user_prompt, system_prompt)

    import json
    if response:
        try:
            # 尝试提取 JSON（DeepSeek 有时会在 markdown 代码块中输出）
            result = response.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            parsed = json.loads(result)
            # 确保所有字段都存在
            defaults = {
                "exists": False, "canonical_name": "",
                "confidence": "low", "industry": "unknown",
                "known_info": "", "related": [],
                "suggestion": "请尝试输入更完整的公司名称",
                "reason": "AI响应解析失败"
            }
            defaults.update(parsed)
            return defaults
        except (json.JSONDecodeError, Exception):
            logger.error(f"AI消歧JSON解析失败: {response[:200]}")
    return {
        "exists": False,
        "canonical_name": "",
        "confidence": "low",
        "industry": "unknown",
        "known_info": "",
        "related": [],
        "suggestion": "系统暂时无法识别，请尝试输入更完整的公司名称",
        "reason": "AI服务暂时不可用，请稍后重试"
    }


def generate_company_info_with_ai(company_name: str, resolve_result: dict = None) -> str:
    """Use DeepSeek AI to generate company info report in Markdown."""
    sp = "你是一个专业的企业信息分析师。"
    sp += "请按Markdown格式输出：\n\n## 公司概况\n\n## 行业地位\n\n## 相关信息\n\n**注意：只输出你确知的信息，不要编造。**"
    extra = ""
    if resolve_result:
        ind = resolve_result.get("industry", "未知")
        info = resolve_result.get("known_info", "")
        extra = " 消歧信息：行业=" + str(ind) + " 简介=" + str(info)
    prompt = "请介绍公司：" + str(company_name) + extra
    resp = _call_deepseek_api(prompt, sp)
    if resp:
        return markdown.markdown(resp)
    return "<p>AI分析暂不可用</p>"


def verify_company_with_ai(company_name: str, user_input: str) -> dict:
    """Use DeepSeek to verify if a company actually exists."""
    import json
    
    system_prompt = (
        'You are a rigorous corporate information verifier. A user reports that a company exists. '
        'Verify its authenticity based on your training data.\n\n'
        'Reply in JSON format ONLY:\n'
        '{\n'
        '    "verified": true/false,\n'
        '    "canonical_name": "official full name if verified, else empty",\n'
        '    "aliases": ["list of known aliases"],\n'
        '    "industry": "industry category",\n'
        '    "known_info": "short description under 100 chars",\n'
        '    "confidence": "high/medium/low",\n'
        '    "reason": "explanation of the decision"\n'
        '}\n\n'
        'Rules:\n'
        '1. If you are SURE the company exists, set verified=true\n'
        '2. If unsure, set verified=false\n'
        '3. NEVER fabricate information\n'
        '4. For obvious person names or fake names, set verified=false\n'
        '5. Well-known companies (Tencent, miHoYo): verified=true\n'
        '6. Niche but real companies (Yostar): verified=true\n'
    )
    
    user_prompt = f'User searched for: {user_input}\nUser reports official name as: {company_name}'
    response = _call_deepseek_api(user_prompt, system_prompt)
    
    if response:
        try:
            result = response.strip()
            if result.startswith("```"):
                result = result.split('\n', 1)[-1]
                if result.endswith("```"):
                    result = result[:-3]
                result = result.strip()
            parsed = json.loads(result)
            defaults = {
                "verified": False, "canonical_name": "", "aliases": [],
                "industry": "unknown", "known_info": "", "confidence": "low",
                "reason": "AI response parsing failed"
            }
            defaults.update(parsed)
            return defaults
        except (json.JSONDecodeError, Exception):
            logger.error(f"verify_company_with_ai JSON parse failed: {response[:200]}")
    
    return {
        "verified": False, "canonical_name": "", "aliases": [],
        "industry": "unknown", "known_info": "", "confidence": "low",
        "reason": "AI service temporarily unavailable"
    }

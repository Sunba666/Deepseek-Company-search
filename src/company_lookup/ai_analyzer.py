# -*- coding: utf-8 -*-
"""AI分析模块"""

import os
import json
import re
from datetime import datetime
from .data_store import get_cache, set_cache, delete_cache

# 预设公司名称列表用于搜索建议
COMPANY_NAMES = [
    '米哈游',
    '米哈游科技',
    '悠星网络',
    '悠星',
    '悠星网络科技',
    '鹰角网络',
    '鹰角',
    '柠檬微趣',
    "腾讯",
    "腾讯控股",
    "腾讯科技",
    "字节跳动",
    "字节跳动科技",
    "阿里巴巴",
    "阿里",
    "阿里巴巴集团",
    "华为",
    "华为技术",
    "小米",
    "小米科技",
    "美团",
    "美团点评",
    "京东",
    "京东集团",
    "百度",
    "百度公司",
    "网易",
    "网易公司",
    "拼多多",
    "拼多多集团",
    "快手",
    "快手科技",
    "滴滴",
    "滴滴出行",
    "携程",
    "携程旅行",
    "小红书",
    "小红书科技",
    "蚂蚁集团",
    "支付宝",
    "微信",
    "微信支付",
    "新浪",
    "新浪微博",
    "搜狐",
    "搜狐公司",
    "网易",
    "网易游戏",
    "盛大",
    "盛大游戏",
    "完美世界",
    "完美游戏",
    "巨人网络",
    "三七互娱",
    "吉比特",
    "心动网络",
    "B站",
    "哔哩哔哩",
    "爱奇艺",
    "爱奇艺视频",
    "腾讯视频",
    "优酷",
    "优酷视频",
    "芒果TV",
    "快手",
    "快手短视频",
    "抖音",
    "抖音短视频",
    "腾讯音乐",
    "QQ音乐",
    "网易云音乐",
    "喜马拉雅",
    "阅文集团",
    "起点中文网",
    "晋江文学城",
    "腾讯新闻",
    "今日头条",
    "澎湃新闻",
    "财新网",
    "界面新闻",
    "虎嗅",
    "36氪",
    "创业邦",
    "钛媒体",
    "爱分析",
    "动脉网",
    "投中",
    "清科",
    "IT桔子",
    "猎云网",
    "亿欧",
    "砍柴网",
    "Donews",
    "TechWeb",
    "中关村在线",
    "太平洋电脑网",
    "手机中国",
    "爱范儿",
    "果壳网",
    "知乎",
    "豆瓣",
    "小红书",
    "脉脉",
    "领英",
    "领英中国",
    "拉勾",
    "拉勾网",
    "BOSS直聘",
    "智联招聘",
    "前程无忧",
    "看准网",
    "职友集",
    "玻璃门",
    "职查查",
    "天眼查",
    "企查查",
    "启信宝",
    "国家企业信用信息公示系统",
    "中国裁判文书网",
    "中国执行信息公开网",
    "信用中国",
    "黑猫投诉",
    "聚投诉",
    "12315",
    "中国互联网违法和不良信息举报中心",
    "扫黄打非",
    "网信办",
    "工信部",
    "商务部",
    "发改委",
    "证监会",
    "银保监会",
    "央行",
    "财政部",
    "税务总局",
    "海关总署",
    "统计局",
    "知识产权局",
    "专利局",
    "商标局",
    "版权局",
    "工信部",
    "科技部",
    "教育部",
    "人社部",
    "民政部",
    "司法部",
    "最高人民法院",
    "最高人民检察院",
    "公安部",
    "安全部",
    "国防部",
    "外交部",
    "发改委",
    "财政部",
    "商务部",
    "文化部",
    "卫健委",
    "环保部",
    "自然资源部",
    "住建部",
    "交通部",
    "水利部",
    "农业农村部",
    "林业局",
    "气象局",
    "地震局",
    "航天局",
    "原子能机构",
    "国家电网",
    "南方电网",
    "中国石油",
    "中国石化",
    "中国海油",
    "中粮集团",
    "中储粮",
    "中国烟草",
    "中国邮政",
    "中国电信",
    "中国移动",
    "中国联通",
    "中国铁塔",
    "中国广电",
    "中信集团",
    "光大集团",
    "中投公司",
    "国投集团",
    "华润集团",
    "招商局",
    "港中旅",
    "中旅集团",
    "中国建筑",
    "中国中铁",
    "中国铁建",
    "中国交建",
    "中国电建",
    "中国能建",
    "中国中冶",
    "中国五矿",
    "中国铝业",
    "中国黄金",
    "中国建材",
    "中国中化",
    "中国化工",
    "国药集团",
    "中国医药",
    "中国船舶",
    "中国重工",
    "中国航天",
    "中国航空",
    "中国商飞",
    "中国兵器",
    "中国核工业",
    "中国电科",
    "中国电子",
    "中国普天",
    "中国中车",
    "中国通号",
    "中国中铁",
    "中国铁建",
    "中国交建",
    "中国建筑",
    "中国能建",
    "中国电建",
    "中国中冶",
    "中国五矿",
    "中国铝业",
    "中国黄金",
    "中国建材",
    "中国中化",
    "中国化工",
    "国药集团",
    "中国医药",
    "中国船舶",
    "中国重工",
    "中国航天",
    "中国航空",
    "中国商飞",
    "中国兵器",
    "中国核工业",
    "中国电科",
    "中国电子",
    "中国普天",
    "中国中车",
    "中国通号",
]


def suggest_companies(query):
    """
    根据查询词建议公司名称（智能匹配）
    :param query: 查询词
    :return: 匹配的公司名称列表
    """
    if not query:
        return []

    query = query.lower()
    suggestions = []

    # 1. 精确匹配
    exact_matches = [name for name in COMPANY_NAMES if query == name.lower()]
    suggestions.extend(exact_matches)

    # 2. 包含匹配
    contains_matches = [
        name for name in COMPANY_NAMES if query in name.lower() and name not in suggestions
    ]
    suggestions.extend(contains_matches)

    # 3. 拼音首字母匹配（简单实现）
    pinyin_matches = []
    for name in COMPANY_NAMES:
        if name not in suggestions:
            # 简单的拼音首字母映射
            pinyin_map = {
                "t": ["腾讯", "头条", "天弘"],
                "a": ["阿里", "阿里巴巴", "安踏"],
                "b": ["百度", "字节", "宝能", "比亚迪"],
                "h": ["华为", "海康", "华泰"],
                "m": ["美团", "小米", "民生"],
                "j": ["京东", "京东数科", "金蝶"],
                "n": ["网易", "宁德时代"],
                "d": ["滴滴", "大疆", "达达"],
                "k": ["快手", "科大讯飞"],
                "p": ["拼多多", "平安"],
                "s": ["顺丰", "苏宁", "商汤"],
            }
            if query[0] in pinyin_map:
                for pinyin_company in pinyin_map[query[0]]:
                    if pinyin_company in name and name not in suggestions:
                        pinyin_matches.append(name)

    suggestions.extend(pinyin_matches)

    # 4. 行业相关推荐
    industry_keywords = {
        "互联网": ["腾讯", "阿里巴巴", "字节跳动", "百度", "美团", "京东", "网易"],
        "游戏": ["腾讯", "网易", "米哈游", "完美世界"],
        "电商": ["阿里巴巴", "京东", "拼多多", "美团"],
        "金融": ["蚂蚁集团", "陆金所", "京东数科"],
        "汽车": ["比亚迪", "蔚来", "小鹏", "理想"],
        "手机": ["华为", "小米", "OPPO", "vivo"],
        "通信": ["华为", "中兴"],
        "短视频": ["字节跳动", "快手", "腾讯"],
        "云计算": ["阿里云", "腾讯云", "华为云"],
        "物流": ["京东", "顺丰", "菜鸟"],
    }

    for industry, companies in industry_keywords.items():
        if query in industry or any(
            keyword in query
            for keyword in [
                "互联",
                "电商",
                "游戏",
                "金融",
                "汽车",
                "手机",
                "通信",
                "视频",
                "云",
                "物流",
            ]
        ):
            for company in companies:
                if company not in suggestions:
                    suggestions.append(company)

    # 5. 热门公司推荐（当查询词较短时）
    if len(query) <= 2:
        hot_companies = [
            "腾讯",
            "阿里巴巴",
            "字节跳动",
            "华为",
            "美团",
            "京东",
            "百度",
            "网易",
            "小米",
            "拼多多",
        ]
        for company in hot_companies:
            if company not in suggestions:
                suggestions.append(company)

    return suggestions[:15]  # 返回最多15个建议


# DeepSeek API配置
# 【修复】移除模块级 DEEPSEEK_API_KEY 变量，改为 _get_api_key() 动态读取。
# 原因：app.py 手动加载 .env 发生在 import 之后，模块级变量在 import 时已绑定空值。
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


def _get_api_key():
    """动态获取 DeepSeek API Key，每次从 os.environ 读取"""
    return os.environ.get("DEEPSEEK_API_KEY", "")


def _call_deepseek_api(prompt, system_prompt="你是一个专业的求职顾问，擅长公司分析和职业规划。"):
    """
    调用DeepSeek API生成内容（带重试机制）
    :param prompt: 用户提示
    :param system_prompt: 系统提示
    :return: AI生成的内容
    """
    # 检查API Key（动态读取）
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("DeepSeek API Key未配置，请检查.env文件中的DEEPSEEK_API_KEY")

    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            import openai

            client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
                timeout=30,  # 30秒超时
            )

            return response.choices[0].message.content
        except Exception as e:
            try:
                print(f"DeepSeek API调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            except:
                pass
            if attempt < max_retries - 1:
                import time

                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
            else:
                try:
                    print(f"DeepSeek API调用最终失败: {e}")
                except:
                    pass
                return None


def _calculate_overall_score(company_data):
    """计算公司综合评分"""
    score = 50  # 基础分

    # 口碑评分
    reputation = company_data.get("reputation", {})
    if isinstance(reputation, dict):
        rating_raw = reputation.get("overall_rating", "")
        if rating_raw:
            if "/" in str(rating_raw):
                rating = float(str(rating_raw).split("/")[0])
            else:
                rating = float(rating_raw)
            score += rating * 10

    # 融资状态加分
    funding_status = company_data.get("funding_status", "")
    if funding_status == "上市":
        score += 15
    elif "C轮" in funding_status:
        score += 10

    # 公司规模加分
    scale = company_data.get("scale", "")
    if "10000人" in scale:
        score += 10

    # 劳动风险扣分
    labor_risk = company_data.get("labor_risk", {})
    if isinstance(labor_risk, dict):
        risk_level = labor_risk.get("risk_level", "")
        if risk_level == "高":
            score -= 20
        elif risk_level == "中":
            score -= 10

    # 限制分数范围
    score = max(0, min(100, score))
    return int(score)


def _get_company_full_name(company_name):
    """获取公司全名"""
    company_full_names = {
        "腾讯": "腾讯控股有限公司",
        "阿里巴巴": "阿里巴巴集团控股有限公司",
        "字节跳动": "字节跳动有限公司",
        "华为": "华为技术有限公司",
        "小米": "小米科技有限责任公司",
        "京东": "北京京东世纪贸易有限公司",
        "美团": "三快在线科技有限公司",
        "网易": "网易集团",
        "百度": "百度在线网络技术有限公司",
        "滴滴": "北京嘀嘀无限科技发展有限公司",
        "快手": "北京快手科技有限公司",
        "拼多多": "上海寻梦信息技术有限公司",
        "蚂蚁集团": "蚂蚁科技集团股份有限公司",
        "商汤科技": "北京市商汤科技开发有限公司",
        "科大讯飞": "科大讯飞股份有限公司",
        "米哈游": "上海米哈游网络科技股份有限公司",
        "中国石油": "中国石油天然气集团有限公司",
        "中国石化": "中国石油化工集团有限公司",
        "中国移动": "中国移动通信集团有限公司",
        "中国电信": "中国电信集团有限公司",
        "中国联通": "中国联合网络通信集团有限公司",
        "特斯拉": "特斯拉（上海）有限公司",
        "苹果": "苹果公司",
        "谷歌": "谷歌公司",
        "微软": "微软公司",
        "亚马逊": "亚马逊公司",
        "英伟达": "英伟达公司",
        "OpenAI": "OpenAI公司",
    }
    return company_full_names.get(company_name, company_name)


def _find_closest_company_name(input_name):
    """
    查找最接近的公司名称（模糊匹配）
    :param input_name: 输入的公司名称
    :return: 匹配的公司名称
    """
    input_name = input_name.strip().lower()

    # 1. 精确匹配
    for company in COMPANY_NAMES:
        if company.lower() == input_name:
            return company

    # 2. 包含匹配
    for company in COMPANY_NAMES:
        if input_name in company.lower() or company.lower() in input_name:
            return company

    # 3. 拼音首字母匹配
    pinyin_map = {
        "tx": "腾讯",
        "ali": "阿里",
        "zj": "字节",
        "hw": "华为",
        "mt": "美团",
        "jd": "京东",
        "wy": "网易",
        "bd": "百度",
        "xm": "小米",
        "mhy": "米哈游",
        "pdd": "拼多多",
        "dd": "滴滴",
        "ks": "快手",
    }

    for key, value in pinyin_map.items():
        if key in input_name or input_name in key:
            for company in COMPANY_NAMES:
                if value in company:
                    return company

    # 4. 简称匹配
    abbreviations = {
        "阿里": "阿里巴巴",
        "腾讯": "腾讯",
        "字节": "字节跳动",
        "华为": "华为",
        "美团": "美团",
        "京东": "京东",
        "百度": "百度",
        "网易": "网易",
        "小米": "小米",
        "拼多多": "拼多多",
    }

    for abbr, full in abbreviations.items():
        if abbr in input_name or input_name in abbr:
            return full

    # 5. 检查 BRAND_MAPPING 品牌白名单（不区分大小写）
    from .services.entity_resolver import BRAND_MAPPING
    input_lower = input_name.lower()
    for brand, full_name in BRAND_MAPPING.items():
        if input_lower == brand.lower():
            return full_name
        if len(input_name) >= 2 and (input_lower in brand.lower() or brand.lower() in input_lower):
            return full_name
    
    # 6. 如果没有匹配，返回原始输入
    return input_name


def query_company_info(company_name, force_refresh=False):
    """
    查询公司信息（支持模糊匹配）
    :param company_name: 公司名称
    :param force_refresh: 是否强制刷新缓存
    :return: 公司信息字典
    """
    from .services.search_service import is_likely_company_name, validation_error_payload

    name = (company_name or "").strip()
    if not is_likely_company_name(name):
        return validation_error_payload(name)

    # 模糊匹配：查找最接近的公司名
    matched_name = _find_closest_company_name(company_name)
    if matched_name != company_name:
        try:
            print(f"模糊匹配: '{company_name}' -> '{matched_name}'")
        except:
            pass
        company_name = matched_name

    cache_key = f"company_info_{company_name}"

    # 如果不强制刷新且有缓存，返回缓存数据（确保包含综合评分）
    if not force_refresh:
        cached_data = get_cache(cache_key)
        if cached_data:
            # 确保缓存数据包含综合评分
            if "overall_score" not in cached_data:
                cached_data["overall_score"] = _calculate_overall_score(cached_data)
                set_cache(cache_key, cached_data)
            return cached_data

    # 如果强制刷新，先删除缓存
    if force_refresh:
        delete_cache(cache_key)

    # 生成模拟数据
    result = generate_mock_company_data(company_name)
    if not result.get("invalid_entity"):
        set_cache(cache_key, result)

    return result


def analyze_company(company_name, user_context=""):
    """
    分析公司并生成尽调报告
    :param company_name: 公司名称
    :param user_context: 用户上下文（字符串或字典）
    :return: AI分析结果
    """
    # 处理字典类型的user_context，生成可哈希的缓存键
    if isinstance(user_context, dict):
        context_hash = hash(str(sorted(user_context.items())))
    else:
        context_hash = hash(user_context)
    cache_key = f"analysis_{company_name}_{context_hash}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    # 获取公司基础信息
    company_data = query_company_info(company_name)
    if company_data.get("invalid_entity") or company_data.get("error"):
        return company_data
    company_full_name = _get_company_full_name(company_name)

    # 使用DeepSeek API生成深度分析
    system_prompt = """你是一个专业的公司尽调分析师，擅长从求职者角度分析公司。
    你需要提供客观、详细、有深度的分析，包括公司优势、劣势、职业发展前景等。
    分析要站在求职者的角度，考虑工作体验、成长空间、薪资待遇、工作生活平衡等因素。

【最高优先级：主语校验】
在总结任何信息之前，你必须先确认公司基本信息中描述的「主体」是否与用户查询的公司名称一致，且该主体明确为一家企业/公司。
如果用户查询的关键词仅作为个人姓名或产品名称出现，而并非公司主体，你必须立即终止总结，
直接回复 JSON 中 overview 字段为：「公开信息显示该关键词并非活跃企业实体，请核对公司全称。」
严禁将「某公司员工张三」中提到的「张三」曲解为要搜索的公司。"""

    prompt = f"""请对{company_full_name}（简称{company_name}）进行深度分析：
    
公司基本信息：
- 行业：{company_data.get("industry", "互联网")}
- 子行业：{company_data.get("sub_industry", "")}
- 规模：{company_data.get("scale", "")}
- 融资阶段：{company_data.get("funding_status", "")}
- 总部：{company_data.get("headquarters", "")}
- 成立时间：{company_data.get("established_year", "")}
- 主营业务：{company_data.get("main_business", "")}

员工口碑：
- 综合评分：{company_data.get("reputation", {}).get("overall_rating", "")}
- 推荐率：{company_data.get("reputation", {}).get("recommendation_rate", "")}
- 优势：{", ".join(company_data.get("reputation", {}).get("pros", []))}
- 劣势：{", ".join(company_data.get("reputation", {}).get("cons", []))}

薪资水平：
- 平均月薪：{company_data.get("salary", {}).get("avg_monthly", "")}
- 薪资范围：{company_data.get("salary", {}).get("salary_range", "")}

请从以下几个方面进行分析：
1. 公司概述和业务前景
2. 员工真实工作体验
3. 职业发展前景和成长空间
4. 薪资竞争力分析
5. 适合加入的人群特征
6. 潜在风险和注意事项

请用JSON格式返回，包含以下字段：
- overview: 公司概述（100字以内）
- business_prospects: 业务前景分析
- work_experience: 工作体验分析
- career_prospects: 职业前景分析
- salary_analysis: 薪资竞争力分析
- suitable_candidates: 适合人群
- risk_warnings: 风险提示
- recommendations: 求职建议（3-5条）"""

    ai_result = _call_deepseek_api(prompt, system_prompt)

    # 解析AI返回的JSON结果
    import json

    try:
        if ai_result:
            # 尝试提取JSON
            json_str = ai_result
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]

            ai_analysis = json.loads(json_str)
        else:
            ai_analysis = {}
    except Exception as e:
        try:
            print(f"AI分析JSON解析失败: {e}")
        except:
            pass
        # 如果解析失败，使用基础分析
        ai_analysis = {
            "overview": f"{company_full_name}是一家知名的互联网科技公司。",
            "business_prospects": "业务发展稳定，前景良好。",
            "work_experience": f"员工评价{company_data.get('reputation', {}).get('overall_rating', '')}。",
            "career_prospects": "职业发展通道清晰。",
            "salary_analysis": f"薪资水平{company_data.get('salary', {}).get('avg_monthly', '')}。",
            "suitable_candidates": "适合有相关经验的求职者。",
            "risk_warnings": [],
            "recommendations": ["建议详细了解公司文化", "关注具体岗位要求"],
        }

    # 确保risk_warnings是列表格式
    risk_warnings = ai_analysis.get("risk_warnings", [])
    if not isinstance(risk_warnings, list):
        risk_warnings = []

    # 如果AI没有返回风险提示，根据公司数据生成
    if not risk_warnings:
        risk_warnings = _generate_risk_warnings(company_data)

    # 确保recommendations是列表格式
    recommendations = ai_analysis.get("recommendations", [])
    if not isinstance(recommendations, list):
        recommendations = []

    # 如果AI没有返回建议，使用默认建议
    if not recommendations:
        recommendations = [
            "建议进行多维度背景调查",
            "与在职/离职员工交流获取真实信息",
            "评估自身职业发展与公司匹配度",
            "关注公司近期动态和发展方向",
        ]

    # 构建分析结果 - 确保公司名称不会被AI返回的数据覆盖
    # 先构建分析结果，确保公司名称在最后设置，不会被AI数据覆盖
    analysis = {
        "analysis_time": datetime.now().isoformat(),
        "overview": ai_analysis.get("overview", ""),
        "business_prospects": ai_analysis.get("business_prospects", ""),
        "work_experience": ai_analysis.get("work_experience", ""),
        "career_prospects": ai_analysis.get("career_prospects", ""),
        "salary_analysis": ai_analysis.get("salary_analysis", ""),
        "suitable_candidates": ai_analysis.get("suitable_candidates", ""),
        "risk_warnings": risk_warnings,
        "recommendations": recommendations,
        "perspective_analysis": _generate_perspective_analysis(company_data),
        "skill_requirements": _generate_skill_requirements(company_data),
        "raw_data": company_data,  # 保留原始数据供其他功能使用
    }

    # 最后设置公司名称，确保不会被AI返回的数据覆盖
    analysis["company_name"] = company_name
    analysis["company_full_name"] = company_full_name

    set_cache(cache_key, analysis)
    return analysis


def analyze_offers(offers_data):
    """
    分析多个Offer
    :param offers_data: Offer列表
    :return: 分析结果
    """
    import sys

    # 保存原始stdout
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    # 创建安全的输出流
    class SafeStream:
        def write(self, data):
            pass

        def flush(self):
            pass

    sys.stdout = SafeStream()
    sys.stderr = SafeStream()

    try:
        if len(offers_data) < 2:
            return {"error": "至少需要2个Offer进行对比"}

        result = {
            "comparison": [],
            "ranking": [],
            "winner": "",
            "reason": "",
            "negotiation_tips": [],
            "summary": "",
        }

        for i, offer in enumerate(offers_data):
            company_name = offer.get("company_name", "")
            company_data = query_company_info(company_name) if company_name else {}
            offer["company_info"] = company_data
            offer["name"] = company_name or f"Offer {i + 1}"

            # 计算评分
            score = _calculate_offer_score(offer)
            offer["score"] = score

            # 生成优点和缺点
            offer["pros"] = _generate_offer_pros(offer)
            offer["cons"] = _generate_offer_cons(offer)

            result["comparison"].append(offer)
            result["ranking"].append({"name": offer["name"], "score": score})

        # 排序找出最优
        result["ranking"].sort(key=lambda x: x["score"], reverse=True)
        result["winner"] = result["ranking"][0]["name"]

        # 生成选择理由
        winner_offer = result["comparison"][0]
        for offer in result["comparison"]:
            if offer["name"] == result["winner"]:
                winner_offer = offer
                break
        result["reason"] = f"{winner_offer['name']}综合评分{winner_offer['score']}分，薪资和发展空间都更占优。适合看重长期回报的你。"

        # 生成谈判建议
        result["negotiation_tips"] = [
            "手上有其他 Offer 的话，大胆用来谈薪，但别撒谎",
            "别只看月薪——年终奖、股票、公积金、补贴加起来才是总包",
            "面试时顺口问一句调薪机制和晋升节奏，这比起薪更重要",
            "通勤时间×2才是真实成本，太远的工作再高的薪资也要算这笔账",
        ]

        # 生成总结
        result["summary"] = _generate_offer_summary(result)

        return result
    finally:
        # 恢复原始stdout
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def _calculate_offer_score(offer):
    """计算Offer评分"""
    score = 50  # 基础分

    # 薪资评分
    salary_str = offer.get("monthly_salary", "")
    if "K" in salary_str or "k" in salary_str:
        try:
            # 提取数字
            import re

            nums = re.findall(r"\d+", salary_str)
            if nums:
                salary_num = int(nums[0])
                if salary_num >= 40:
                    score += 30
                elif salary_num >= 30:
                    score += 20
                elif salary_num >= 20:
                    score += 10
        except:
            pass

    # 公司信息加分
    company_info = offer.get("company_info", {})
    if company_info.get("funding_status") == "上市":
        score += 10
    if company_info.get("scale") and "10000人" in company_info.get("scale", ""):
        score += 5

    # 地点加分
    location = offer.get("location", "")
    if location in ["北京", "上海", "深圳", "杭州"]:
        score += 5

    return min(100, score)


def _generate_offer_pros(offer):
    """生成Offer优点"""
    pros = []
    if offer.get("monthly_salary"):
        pros.append("薪资待遇好")
    if offer.get("benefits"):
        pros.append("福利完善")
    company_info = offer.get("company_info", {})
    if company_info.get("funding_status") == "上市":
        pros.append("已上市，抗风险能力强")
    if company_info.get("scale") and "大" in company_info.get("scale", ""):
        pros.append("平台大，跳槽背书强")
    if not pros:
        pros.append("整体条件不错，建议进一步了解")
    return pros


def _generate_offer_cons(offer):
    """生成Offer缺点"""
    cons = []
    commute = offer.get("commute", "")
    if commute and ("60" in commute or "45" in commute):
        cons.append("通勤时间较长")

    company_info = offer.get("company_info", {})

    # 从公司口碑中获取缺点
    reputation = company_info.get("reputation", {})
    if reputation.get("cons"):
        cons.extend(reputation["cons"][:2])  # 最多取2个缺点

    # 检查劳动风险
    if company_info.get("labor_risk", {}).get("risk_level") == "高":
        cons.append("劳动风险较高")

    # 检查薪资竞争力
    monthly_salary = offer.get("monthly_salary", "")
    if monthly_salary:
        # 简单判断薪资水平
        if "15K" in monthly_salary or ("10K" in monthly_salary and "20K" not in monthly_salary):
            cons.append("薪资水平相对较低")

    # 如果没有找到缺点，根据公司信息生成一些合理的缺点
    if not cons:
        industry = company_info.get("sub_industry", "")
        if "游戏" in industry:
            cons.append("游戏行业项目制为主，稳定性看产品生命周期")
        elif "电商" in industry:
            cons.append("大促期加班多，节奏偏快")
        elif "社交" in industry:
            cons.append("产品迭代快，需要快速学习适应")
        else:
            cons.append("建议面试时多了解团队氛围和工作节奏")

    return cons[:3]  # 最多返回3个缺点


def _generate_offer_summary(result):
    """生成Offer总结"""
    winner = result.get("winner", "")
    comparison = result.get("comparison", [])

    summary = f"总的来说，{winner}更值得去。"
    if comparison:
        scores = [o.get("score", 0) for o in comparison]
        avg_score = sum(scores) / len(scores) if scores else 0
        summary += f"几家Offer平均分{avg_score:.1f}，差距不算太大。最终选哪个，还得看你更在意薪资、成长还是生活节奏——想清楚优先级再做决定。"

    return summary


def generate_interview_questions(company_name, position_type=""):
    """
    生成面试问题
    :param company_name: 公司名称
    :param position_type: 职位类型
    :return: 面试问题列表
    """
    cache_key = f"interview_{company_name}_{position_type}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    company_data = query_company_info(company_name)

    questions = {
        "technical_questions": _generate_technical_questions(company_data, position_type),
        "behavioral_questions": _generate_behavioral_questions(),
        "suggestions": _generate_interview_suggestions(company_data),
    }

    set_cache(cache_key, questions)
    return questions


def mock_interview(question, answer, company_name=""):
    """
    模拟面试评分
    :param question: 问题
    :param answer: 回答
    :param company_name: 公司名称
    :return: 评分和反馈
    """
    feedback = {"score": 0, "strengths": [], "weaknesses": [], "suggestions": []}

    # 简单的评分逻辑
    answer_length = len(answer.strip())

    if answer_length == 0:
        feedback["score"] = 0
        feedback["weaknesses"].append("回答为空")
        return feedback

    # 根据回答长度评分
    if answer_length < 50:
        feedback["score"] = 30
        feedback["weaknesses"].append("回答过于简短")
    elif answer_length < 150:
        feedback["score"] = 50
        feedback["weaknesses"].append("回答可以更详细")
    elif answer_length < 300:
        feedback["score"] = 70
        feedback["strengths"].append("回答内容适中")
    else:
        feedback["score"] = 85
        feedback["strengths"].append("回答内容丰富")

    # 检查是否包含STAR要素
    if any(keyword in answer for keyword in ["项目", "任务", "目标"]):
        feedback["strengths"].append("提及了具体经历")
        feedback["score"] += 5
    else:
        feedback["weaknesses"].append("建议使用STAR法则描述经历")

    if any(keyword in answer for keyword in ["结果", "成果", "数据"]):
        feedback["strengths"].append("包含量化成果")
        feedback["score"] += 5
    else:
        feedback["weaknesses"].append("建议加入量化数据")

    feedback["score"] = min(100, feedback["score"])

    # 添加通用建议
    feedback["suggestions"].append("保持回答结构清晰")
    feedback["suggestions"].append("提前准备常见问题")
    feedback["suggestions"].append("了解目标公司业务")

    return feedback


def generate_negotiation_script(offer_data, target_salary):
    """
    生成薪资谈判脚本
    :param offer_data: Offer数据
    :param target_salary: 目标薪资
    :return: 谈判脚本
    """
    script = {
        "opening": _generate_opening_line(offer_data),
        "justification": _generate_justification(offer_data, target_salary),
        "closing": _generate_closing_line(),
        "tips": ["保持专业态度", "做好充分准备", "了解市场行情"],
    }
    return script


def analyze_resume(resume_text):
    """
    分析简历
    :param resume_text: 简历文本
    :return: 分析结果和优化建议
    """
    result = {
        "match_score": 60,
        "keywords": [],
        "suggestions": [],
        "cover_letter": "",
        "diagnosis": [],
        "optimized_text": "",
    }

    # 计算匹配度
    score = 60

    # 诊断逻辑
    if len(resume_text.strip()) < 100:
        result["diagnosis"].append("简历内容过于简短")
        score -= 10

    # 检查关键词
    keywords = [
        "项目经验",
        "工作经历",
        "技能",
        "学历",
        "职责",
        "成就",
        "Python",
        "Java",
        "JavaScript",
        "MySQL",
        "Redis",
    ]
    found_keywords = []
    for keyword in keywords:
        if keyword in resume_text:
            found_keywords.append(keyword)
            score += 5
        else:
            if keyword in ["项目经验", "工作经历", "技能", "学历"]:
                result["diagnosis"].append(f'缺少"{keyword}"相关内容')

    result["keywords"] = (
        found_keywords if found_keywords else ["项目经验", "技术技能", "团队协作", "问题解决"]
    )

    # 检查量化数据
    if not any(char.isdigit() for char in resume_text):
        result["diagnosis"].append("缺少量化成果描述")
        score -= 10

    # 生成优化建议
    result["suggestions"] = [
        "使用STAR法则描述工作经历（情境-任务-行动-结果）",
        '加入量化成果数据，如"提升效率30%"',
        "突出核心技能和项目亮点",
        "保持简历简洁，控制在1-2页",
        "针对目标公司调整关键词",
    ]

    # 生成求职信
    result["cover_letter"] = _generate_cover_letter(resume_text)

    # 设置最终匹配度
    result["match_score"] = max(30, min(95, score))

    # 生成优化示例
    result["optimized_text"] = _generate_optimized_resume(resume_text)

    return result


def _generate_cover_letter(resume_text):
    """生成求职信"""
    # 提取关键信息
    lines = resume_text.strip().split("\n")
    name = ""
    for line in lines:
        if "姓名" in line or "名字" in line:
            name = line.split(":")[-1].strip() if ":" in line else line.split("：")[-1].strip()
            break

    if not name:
        name = "申请人"

    cover_letter = f"""
尊敬的招聘负责人：

您好！我是{name}，非常荣幸能有机会申请贵公司的职位。

通过仔细研究贵公司的业务和发展方向，我深感自己的专业技能和职业发展目标与贵公司的需求高度契合。我相信我的加入能为贵公司带来实质性的价值贡献。

在过往的工作经历中，我积累了丰富的项目经验和专业技能。我具备良好的团队协作能力和问题解决能力，能够快速适应新环境并高效完成工作任务。我始终保持着学习的心态，不断提升自己的专业水平。

我期待能够有机会与您进一步交流，详细介绍我的能力和经验。感谢您抽出宝贵时间阅读我的申请材料。

诚挚地，
{name}
"""
    return cover_letter.strip()


def _generate_opening_line(offer_data):
    """生成开场话术"""
    company_name = offer_data.get("company_name", "贵公司")
    return f"您好，很高兴能有这个机会加入{company_name}。想跟您聊一下薪资方面，看能不能找到一个双方都满意的方案。"


def _generate_justification(offer_data, target_salary):
    """生成薪资理由"""
    current_salary = offer_data.get("salary", "")
    return f"结合当前的行情和我自己的经验，我的期望是{target_salary}左右。当然，除了薪资我也很看重团队和成长空间，这些都很匹配的话，待遇上我们可以再细聊。"


def _generate_closing_line():
    """生成结束语"""
    return "期待您的反馈。不管结果如何，都感谢这次沟通的机会。"


def _generate_optimized_resume(resume_text):
    """生成优化后的简历示例"""
    if not resume_text.strip():
        return """【优化简历示例】

个人信息
- 姓名：XXX | 电话：XXX | 邮箱：XXX

工作经历
- [公司名称] | [职位] | [时间]
  - 负责XXX项目，性能提升了30%，团队规模5人
  - 主导XXX流程改进，帮团队节省20%时间

专业技能
- 技术栈：Python, JavaScript, SQL
- 经验：3年+全栈开发

教育背景
- [学校名称] | [专业] | [学历] | [时间]

💡 写简历的小技巧：
- 每段经历都写一个「做了什么 + 做出了什么效果」
- 多用数字（提升30%、节省20%、覆盖10万用户）
- 动词开头：主导、负责、推动、优化"""

    return (
        resume_text + "\n\n【优化建议】\n- 增加量化成果描述\n- 使用行动动词开头\n- 突出核心竞争力"
    )


def _generate_overview(company_data):
    """生成公司概述"""
    name = company_data.get("name", "")
    industry = company_data.get("industry", "")
    scale = company_data.get("scale", "")
    return f"{name}是一家做{industry}的公司，目前团队规模{scale}。{'大厂光环对跳槽有帮助' if '上市' in company_data.get('funding_status', '') else ''}"


def _generate_perspective_analysis(company_data):
    """生成双方视角分析"""
    rep = company_data.get("reputation", {})
    pros = rep.get("pros", [])
    cons = rep.get("cons", [])

    analysis = {
        "from_company": {
            "strengths": ["人才需求明确", "业务发展稳定"] if pros else [],
            "concerns": ["需要评估候选人能力匹配度"],
        },
        "from_candidate": {
            "opportunities": pros[:3] if pros else [],
            "concerns": cons[:2] if cons else [],
        },
    }
    return analysis


def _generate_skill_requirements(company_data):
    """生成技能要求"""
    industry = company_data.get("industry", "")

    skills = {
        "互联网": ["Java/Python/Go", "分布式系统", "微服务架构", "数据库优化"],
        "人工智能": ["机器学习", "深度学习", "Python", "TensorFlow/PyTorch"],
        "金融": ["金融知识", "风控经验", "数据分析", "合规意识"],
        "游戏": ["游戏引擎", "图形编程", "性能优化", "用户体验"],
    }

    return skills.get(industry, ["行业通用技能"])


def _generate_risk_warnings(company_data):
    """生成风险预警"""
    warnings = []

    # 劳动风险检查
    risk = company_data.get("labor_risk", {})
    level = risk.get("risk_level", "中")

    if level == "高":
        warnings.append("⚠️ 劳动风险等级较高，建议谨慎评估")
    elif level == "中":
        warnings.append("⚠️ 存在一定劳动风险，建议详细了解")

    # 员工口碑检查
    rep = company_data.get("reputation", {})
    try:
        rating = float(rep.get("overall_rating", "0").split("/")[0])
        if rating < 3.5:
            warnings.append(f"⚠️ 员工评分较低（{rating}/5），建议进一步了解工作环境")
    except:
        pass

    try:
        rec_rate = float(rep.get("recommendation_rate", "0").replace("%", ""))
        if rec_rate < 60:
            warnings.append(f"⚠️ 员工推荐率较低（{rec_rate}%），建议深入了解企业文化")
    except:
        pass

    # 检查差评点
    cons = rep.get("cons", [])
    if cons:
        # 提取关键风险点
        risk_keywords = ["加班", "压力", "裁员", "降薪", "管理", "文化"]
        for con in cons:
            for keyword in risk_keywords:
                if keyword in con:
                    warnings.append(f"⚠️ 需要注意：{con}")
                    break

    # 如果没有生成任何风险提示，添加通用提示
    if not warnings:
        warnings.append("ℹ️ 暂未发现重大风险，建议进一步了解具体岗位情况")

    return warnings


def _generate_recommendations(company_data):
    """生成建议"""
    return [
        "建议进行多维度背景调查",
        "与在职/离职员工交流获取真实信息",
        "评估自身职业发展与公司匹配度",
        "关注公司近期动态和发展方向",
    ]


def _generate_technical_questions(company_data, position_type):
    """生成技术问题"""
    position_questions = {
        "前端": [
            {
                "question": "请介绍你最熟悉的前端框架及其优缺点",
                "category": "框架",
                "difficulty": "中等",
            },
            {"question": "如何优化网页加载性能？", "category": "性能", "difficulty": "中等"},
            {
                "question": "实现一个响应式布局有哪些方法？",
                "category": "布局",
                "difficulty": "简单",
            },
            {
                "question": "JavaScript中的闭包是什么？有什么应用场景？",
                "category": "基础",
                "difficulty": "中等",
            },
            {"question": "如何处理跨域问题？", "category": "网络", "difficulty": "中等"},
        ],
        "后端": [
            {
                "question": "请介绍你熟悉的数据库及其适用场景",
                "category": "数据库",
                "difficulty": "中等",
            },
            {"question": "如何设计高可用系统？", "category": "架构", "difficulty": "困难"},
            {"question": "RESTful API设计原则有哪些？", "category": "API", "difficulty": "中等"},
            {
                "question": "分布式系统中的一致性问题如何解决？",
                "category": "分布式",
                "difficulty": "困难",
            },
            {"question": "如何进行接口性能优化？", "category": "性能", "difficulty": "中等"},
        ],
        "产品": [
            {"question": "你如何进行需求分析？", "category": "需求", "difficulty": "中等"},
            {"question": "如何处理需求变更？", "category": "管理", "difficulty": "中等"},
            {"question": "产品上线后如何进行效果评估？", "category": "运营", "difficulty": "中等"},
            {
                "question": "你做过的最成功的产品案例是什么？",
                "category": "案例",
                "difficulty": "中等",
            },
            {
                "question": "如何平衡用户体验和技术实现难度？",
                "category": "权衡",
                "difficulty": "困难",
            },
        ],
        "算法": [
            {
                "question": "常见的排序算法有哪些？时间复杂度如何？",
                "category": "基础",
                "difficulty": "简单",
            },
            {
                "question": "动态规划的适用场景是什么？举个例子",
                "category": "DP",
                "difficulty": "困难",
            },
            {
                "question": "图算法中最短路径有哪些实现方式？",
                "category": "图",
                "difficulty": "中等",
            },
            {
                "question": "如何处理大规模数据的算法优化？",
                "category": "大规模",
                "difficulty": "困难",
            },
            {
                "question": "机器学习中的过拟合问题如何解决？",
                "category": "ML",
                "difficulty": "中等",
            },
        ],
    }

    return position_questions.get(position_type, position_questions["后端"])


def _generate_behavioral_questions():
    """生成行为问题"""
    return [
        {
            "question": "请描述一次你遇到的最大挑战以及如何解决的",
            "key_points": ["挑战", "行动", "结果"],
        },
        {"question": "你为什么选择离开上一家公司？", "key_points": ["原因", "职业规划"]},
        {"question": "你如何处理团队中的冲突？", "key_points": ["沟通", "解决策略"]},
        {"question": "请分享一个你引以为傲的项目经历", "key_points": ["贡献", "成果"]},
        {"question": "你未来3-5年的职业规划是什么？", "key_points": ["目标", "计划"]},
    ]


def _generate_interview_suggestions(company_data):
    """生成面试建议"""
    suggestions = [
        "提前了解公司业务和产品",
        "准备项目案例和技术亮点",
        "熟悉常见面试问题",
        "准备好反问面试官的问题",
        "注意着装和礼仪",
    ]

    industry = company_data.get("industry", "")
    if "游戏" in industry:
        suggestions.append("了解公司主要游戏产品")
    elif "AI" in industry:
        suggestions.append("关注公司AI技术方向")

    return suggestions


def _calculate_offer_score(offer):
    """计算Offer评分"""
    score = 0

    # 薪资评分
    salary = offer.get("salary", "")
    try:
        num_str = "".join([c for c in salary if c.isdigit()])
        if num_str:
            salary_val = int(num_str)
            score += min(40, salary_val // 1000)
    except:
        pass

    # 公司评分
    company_info = offer.get("company_info", {})
    rep = company_info.get("reputation", {})
    rating = rep.get("overall_rating", "0")
    try:
        rating_val = float(rating.split("/")[0])
        score += int(rating_val * 10)
    except:
        pass

    return min(100, score)


def _generate_offer_summary(result):
    """生成Offer对比总结"""
    if not result["ranking"]:
        return ""

    top_offer = result["ranking"][0]
    return f"{top_offer['name']}的综合条件更优，值得优先考虑。建议用它作为基准去跟其他家谈。"


def generate_mock_company_data(company_name):
    """
    生成模拟公司数据
    :param company_name: 公司名称
    :return: 公司数据字典
    """
    # 根据公司名称关键词生成不同数据
    company_keywords = {
        "腾讯": {
            "name": "腾讯控股有限公司",
            "english_name": "Tencent Holdings Limited",
            "industry": "互联网",
            "sub_industry": "社交/游戏",
            "scale": "10000人以上",
            "established_year": "1998",
            "registered_capital": "65000万人民币",
            "business_scope": "互联网服务、社交网络、游戏开发",
            "headquarters": "广东省深圳市",
            "funding_status": "上市",
            "stock_code": "HKEX:00700",
            "website": "https://www.tencent.com",
            "careers_url": "https://careers.tencent.com",
            "key_products": ["微信", "QQ", "王者荣耀", "和平精英"],
            "competitors": ["阿里巴巴", "字节跳动"],
            "market_position": "中国互联网行业龙头企业",
            "recent_news": "近期发布了多款新游戏产品",
            "salary": {
                "avg_monthly": "28000元",
                "salary_range": "15000-50000元",
                "year_end_bonus": "3-6个月",
                "salary_adjustment": "一年两次",
                "benefits": ["五险一金", "补充医疗保险", "免费班车", "健身房", "游戏内购折扣"],
            },
            "reputation": {
                "overall_rating": "4.2/5",
                "recommendation_rate": "78%",
                "ceo_approval_rate": "90%",
                "pros": ["福利完善", "团队氛围好", "技术积累深厚", "内部转岗机会多"],
                "cons": ["部分项目加班严重", "晋升竞争激烈", "流程逐渐变复杂"],
                "culture_keywords": ["用户为本", "科技向善", "赛马机制", "游戏化"],
            },
            "interview": {
                "interview_difficulty": "中等偏上",
                "interview_rounds": "3-4轮",
                "positive_rate": "25%",
                "avg_interview_duration": "1.5小时",
                "common_questions": [
                    "为什么选择腾讯？",
                    "介绍一个你参与的最有挑战性的项目",
                    "如何处理项目中的技术难题？",
                    "你对游戏行业的看法？",
                    "如何保证代码质量？",
                ],
                "common_answers": {
                    "为什么选择腾讯？": "腾讯拥有丰富的用户场景和技术积累，在社交和游戏领域处于领先地位，我希望能够在这样的平台上发挥自己的技术能力。",
                    "介绍一个你参与的最有挑战性的项目": "我参与过一个高并发系统的重构项目，通过引入分布式缓存和异步处理，将系统吞吐量提升了300%。",
                    "如何处理项目中的技术难题？": "首先分析问题根源，查阅相关文档和社区解决方案，与团队讨论后制定实施方案，最后进行充分测试验证。",
                    "你对游戏行业的看法？": "游戏行业正在从娱乐向多元化发展，元宇宙和云游戏是未来的重要方向，技术创新将持续推动行业发展。",
                    "如何保证代码质量？": "通过代码审查、单元测试、自动化测试等手段，同时遵循团队的编码规范和最佳实践。",
                },
                "interview_tips": [
                    "深入了解腾讯产品",
                    "准备项目细节",
                    "展示技术深度",
                    "了解游戏行业",
                ],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，无重大风险记录。",
                "risk_items": [],
            },
        },
        "字节跳动": {
            "name": "北京字节跳动科技有限公司",
            "english_name": "ByteDance",
            "industry": "互联网",
            "sub_industry": "内容/短视频",
            "scale": "10000人以上",
            "established_year": "2012",
            "registered_capital": "10000万人民币",
            "business_scope": "短视频、资讯、教育",
            "headquarters": "北京市",
            "funding_status": "上市",
            "stock_code": "HKEX:9961",
            "website": "https://www.bytedance.com",
            "careers_url": "https://jobs.bytedance.com",
            "key_products": ["抖音", "今日头条", "TikTok"],
            "competitors": ["腾讯", "快手"],
            "market_position": "全球短视频行业领导者",
            "recent_news": "TikTok在全球用户突破10亿",
            "salary": {
                "avg_monthly": "30000元",
                "salary_range": "18000-55000元",
                "year_end_bonus": "4-8个月",
                "salary_adjustment": "一年两次",
                "benefits": ["六险一金", "房补", "餐补", "年度体检", "学习基金"],
            },
            "reputation": {
                "overall_rating": "4.0/5",
                "recommendation_rate": "72%",
                "ceo_approval_rate": "85%",
                "pros": ["薪资竞争力强", "成长空间大", "扁平化管理", "国际化视野"],
                "cons": ["工作节奏快", "KPI压力大", "部分岗位加班多"],
                "culture_keywords": ["始终创业", "坦诚清晰", "多元兼容", "追求极致"],
            },
            "interview": {
                "interview_difficulty": "较高",
                "interview_rounds": "3-5轮",
                "positive_rate": "20%",
                "avg_interview_duration": "2小时",
                "common_questions": [
                    "为什么选择字节跳动？",
                    "介绍一个你最满意的项目",
                    "如何处理数据量较大的场景？",
                    "你对短视频行业的理解？",
                    "如何应对快速变化的业务需求？",
                ],
                "common_answers": {
                    "为什么选择字节跳动？": "字节跳动以技术驱动产品增长，在内容推荐和短视频领域有深厚积累，我希望能在高速成长的环境中快速提升自己。",
                    "介绍一个你最满意的项目": "我负责过一个推荐系统的优化项目，通过改进算法模型，将用户点击率提升了25%。",
                    "如何处理数据量较大的场景？": "采用分布式计算框架、数据分片、缓存策略等方式来处理大规模数据。",
                    "你对短视频行业的理解？": "短视频已经成为重要的内容消费形式，算法推荐和内容生态是核心竞争力，全球化是重要趋势。",
                    "如何应对快速变化的业务需求？": "保持敏捷开发，注重代码模块化和可扩展性，及时与产品团队沟通理解需求变化。",
                },
                "interview_tips": [
                    "关注算法和数据",
                    "准备系统设计",
                    "展示学习能力",
                    "了解推荐系统",
                ],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，注重员工福利保障。",
                "risk_items": [],
            },
        },
        "阿里巴巴": {
            "name": "阿里巴巴集团控股有限公司",
            "english_name": "Alibaba Group",
            "industry": "互联网",
            "sub_industry": "电商/云计算",
            "scale": "10000人以上",
            "established_year": "1999",
            "registered_capital": "100000万人民币",
            "business_scope": "电子商务、云计算、数字媒体",
            "headquarters": "浙江省杭州市",
            "funding_status": "上市",
            "stock_code": "NYSE:BABA",
            "website": "https://www.alibaba.com",
            "careers_url": "https://talent.alibaba.com",
            "key_products": ["淘宝", "天猫", "阿里云"],
            "competitors": ["京东", "拼多多"],
            "market_position": "中国电商行业龙头",
            "recent_news": "阿里云市场份额持续增长",
            "salary": {
                "avg_monthly": "26000元",
                "salary_range": "14000-45000元",
                "year_end_bonus": "2-6个月",
                "salary_adjustment": "一年一次",
                "benefits": ["五险一金", "房补", "餐补", "节日福利", "阿里日活动"],
            },
            "reputation": {
                "overall_rating": "4.1/5",
                "recommendation_rate": "75%",
                "ceo_approval_rate": "88%",
                "pros": ["平台大机会多", "技术体系完善", "企业文化好", "晋升体系透明"],
                "cons": ["部分业务加班较多", "层级较多", "流程较长"],
                "culture_keywords": ["客户第一", "团队合作", "拥抱变化", "诚信"],
            },
            "interview": {
                "interview_difficulty": "中等偏上",
                "interview_rounds": "3-4轮",
                "positive_rate": "28%",
                "avg_interview_duration": "1.5小时",
                "common_questions": [
                    "为什么选择阿里巴巴？",
                    "介绍一个复杂业务系统的设计经验",
                    "如何处理高并发场景？",
                    "你对电商行业的理解？",
                    "如何与业务方协作？",
                ],
                "common_answers": {
                    "为什么选择阿里巴巴？": "阿里巴巴在电商和云计算领域有深厚积累，业务场景丰富，能够提供广阔的发展空间和技术挑战。",
                    "介绍一个复杂业务系统的设计经验": "我参与过电商订单系统的设计，通过分布式架构和消息队列保证系统的高可用和扩展性。",
                    "如何处理高并发场景？": "通过负载均衡、缓存策略、异步处理、数据库优化等方式来应对高并发。",
                    "你对电商行业的理解？": "电商正在从交易平台向新零售和数字商业演进，技术驱动和数据智能是关键。",
                    "如何与业务方协作？": "建立良好的沟通机制，深入理解业务需求，提供技术方案支持业务目标达成。",
                },
                "interview_tips": ["准备电商场景", "了解分布式系统", "展示业务理解", "了解阿里云"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，员工权益保障完善。",
                "risk_items": [],
            },
        },
        "华为": {
            "name": "华为技术有限公司",
            "english_name": "Huawei Technologies",
            "industry": "通信",
            "sub_industry": "5G/智能手机",
            "scale": "10000人以上",
            "established_year": "1987",
            "registered_capital": "405000万人民币",
            "business_scope": "通信设备、智能手机、云计算",
            "headquarters": "广东省深圳市",
            "funding_status": "未上市",
            "stock_code": "-",
            "website": "https://www.huawei.com",
            "careers_url": "https://career.huawei.com",
            "key_products": ["Mate系列手机", "5G设备", "HarmonyOS"],
            "competitors": ["苹果", "三星", "爱立信"],
            "market_position": "全球领先的ICT基础设施提供商",
            "recent_news": "发布新一代麒麟芯片",
            "salary": {
                "avg_monthly": "25000元",
                "salary_range": "12000-40000元",
                "year_end_bonus": "1-4个月",
                "salary_adjustment": "一年一次",
                "benefits": ["六险一金", "班车", "餐补", "购房补贴", "员工持股"],
            },
            "reputation": {
                "overall_rating": "4.3/5",
                "recommendation_rate": "82%",
                "ceo_approval_rate": "92%",
                "pros": ["技术实力强", "研发投入大", "薪酬竞争力强", "民族自豪感"],
                "cons": ["工作强度大", "出差频繁", "海外派遣多"],
                "culture_keywords": ["以客户为中心", "以奋斗者为本", "长期艰苦奋斗", "自我批判"],
            },
            "interview": {
                "interview_difficulty": "较高",
                "interview_rounds": "3-5轮",
                "positive_rate": "18%",
                "avg_interview_duration": "2小时",
                "common_questions": [
                    "为什么选择华为？",
                    "介绍一个攻克技术难题的经历",
                    "如何看待技术创新？",
                    "你对通信行业的理解？",
                    "是否接受海外派遣？",
                ],
                "common_answers": {
                    "为什么选择华为？": "华为在通信领域技术领先，注重研发投入，我希望能够参与到核心技术的研发中。",
                    "介绍一个攻克技术难题的经历": "我曾带领团队解决了一个性能瓶颈问题，通过深入分析和优化算法，将系统响应时间降低了60%。",
                    "如何看待技术创新？": "技术创新是企业发展的核心动力，需要持续投入和人才培养，同时注重知识产权保护。",
                    "你对通信行业的理解？": "5G正在推动万物互联，通信技术正在从连接向智能演进，算力网络是未来方向。",
                    "是否接受海外派遣？": "我愿意接受海外派遣，这是宝贵的国际工作经验，能够提升我的跨文化沟通能力。",
                },
                "interview_tips": ["准备通信知识", "展示技术深度", "了解企业文化", "体能准备"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，注重员工发展和激励。",
                "risk_items": [],
            },
        },
        "悠星": {
            "name": "悠星网络科技有限公司",
            "english_name": "Yostar Networks Technology Co., Ltd.",
            "industry": "游戏",
            "sub_industry": "二次元游戏/出海",
            "scale": "500-2000人",
            "established_year": "2014",
            "registered_capital": "5000万元人民币",
            "business_scope": "网络游戏开发、发行、运营",
            "headquarters": "上海市浦东新区",
            "funding_status": "未上市",
            "stock_code": "",
            "website": "https://www.yostar.jp",
            "careers_url": "",
            "key_products": ["明日方舟", "蔚蓝档案", "碧蓝航线(日服)"],
            "competitors": ["米哈游", "鹰角网络"],
            "market_position": "中国二次元游戏出海领先企业",
            "recent_news": "旗下《明日方舟》和《蔚蓝档案》在日本市场表现优异",
            "salary": {
                "avg_monthly": "20k-35k",
                "salary_range": "15k-45k",
                "year_end_bonus": "13-16薪",
                "salary_adjustment": "每年1次调薪",
                "benefits": ["五险一金", "补充医疗", "带薪年假", "加班补贴"],
            },
            "reputation": {
                "overall_rating": 3.8,
                "recommendation_rate": "68%",
                "ceo_approval_rate": "80%",
                "pros": ["出海业务前景好", "团队年轻", "项目成功"],
                "cons": ["规模较小", "国内知名度不高"],
                "culture_keywords": ["二次元", "国际化", "创业氛围"],
            },
            "interview": {
                "interview_difficulty": "中等",
                "interview_rounds": "3-4轮",
                "positive_rate": "70%",
                "avg_interview_duration": "1-2周",
                "common_questions": ["项目经验", "技术基础", "日语能力", "游戏理解"],
                "common_answers": ["展示语言能力优势", "体现对二次元文化的理解"],
                "interview_tips": ["了解日本游戏市场", "展示跨文化交流能力"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好",
                "risk_items": [],
            },
            "overall_score": 72,
        },
        "柠檬微趣": {
            "name": "北京柠檬微趣科技股份有限公司",
            "english_name": "Beijing Lemon Micro Fun Technology Co., Ltd.",
            "industry": "游戏",
            "sub_industry": "休闲游戏/社交游戏",
            "scale": "200-500人",
            "established_year": "2008",
            "registered_capital": "1000万元人民币",
            "business_scope": "游戏开发、手机游戏发行、互联网技术服务",
            "headquarters": "北京市海淀区",
            "funding_status": "未上市",
            "stock_code": "",
            "website": "",
            "key_products": ["宾果消消消", "梦幻花园", "梦幻家园"],
            "competitors": ["腾讯", "网易"],
            "market_position": "国内休闲游戏领域知名开发商",
            "recent_news": "旗下产品《宾果消消消》持续运营中",
            "salary": {
                "avg_monthly": "15k-30k",
                "salary_range": "12k-40k",
                "year_end_bonus": "13-15薪",
                "salary_adjustment": "每年1次调薪",
                "benefits": ["五险一金", "补充医疗", "带薪年假", "弹性工作"],
            },
            "reputation": {
                "overall_rating": 3.6,
                "recommendation_rate": "65%",
                "ceo_approval_rate": "78%",
                "pros": ["项目稳定", "团队协作好", "产品用户量大"],
                "cons": ["薪资竞争力一般", "创新空间有限"],
                "culture_keywords": ["休闲娱乐", "产品导向", "稳定发展"],
            },
            "interview": {
                "interview_difficulty": "中等",
                "interview_rounds": "2-3轮",
                "positive_rate": "60%",
                "avg_interview_duration": "1-2周",
                "common_questions": ["游戏设计理念", "技术方案", "项目经验"],
                "interview_tips": ["了解公司产品", "展示游戏开发经验"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好",
                "risk_items": [],
            },
            "overall_score": 68,
        },
        "鹰角": {
            "name": "上海鹰角网络科技有限公司",
            "english_name": "Hypergryph Network Technology Co., Ltd.",
            "industry": "游戏",
            "sub_industry": "二次元游戏",
            "scale": "1000-5000人",
            "established_year": "2017",
            "registered_capital": "1000万元人民币",
            "business_scope": "网络游戏开发、动漫设计、软件开发",
            "headquarters": "上海市徐汇区",
            "funding_status": "未上市",
            "stock_code": "",
            "website": "https://www.hypergryph.com",
            "careers_url": "",
            "key_products": ["明日方舟", "来自星尘"],
            "competitors": ["米哈游", "腾讯"],
            "market_position": "中国二次元游戏行业新锐企业",
            "recent_news": "《明日方舟》持续运营，新作《来自星尘》已上线",
            "salary": {
                "avg_monthly": "20k-40k",
                "salary_range": "15k-50k",
                "year_end_bonus": "13-17薪",
                "salary_adjustment": "每年1次调薪",
                "benefits": ["五险一金", "补充医疗", "免费晚餐", "弹性工作"],
            },
            "reputation": {
                "overall_rating": 4.2,
                "recommendation_rate": "78%",
                "ceo_approval_rate": "88%",
                "pros": ["产品口碑好", "团队氛围好", "发展潜力大"],
                "cons": ["加班较常见", "核心产品单一"],
                "culture_keywords": ["二次元", "独立精神", "创意驱动"],
            },
            "interview": {
                "interview_difficulty": "中等偏难",
                "interview_rounds": "3-4轮",
                "positive_rate": "68%",
                "avg_interview_duration": "2-3周",
                "common_questions": ["技术方案设计", "项目经验", "游戏理解"],
                "common_answers": ["展示技术深度", "体现对产品的理解"],
                "interview_tips": ["深入体验鹰角产品", "准备技术方案设计案例"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好",
                "risk_items": [],
            },
            "overall_score": 75,
        },
        "米哈游": {
            "name": "米哈游科技（上海）有限公司",
            "english_name": "miHoYo Co., Ltd.",
            "industry": "游戏",
            "sub_industry": "二次元游戏",
            "scale": "5000-10000人",
            "established_year": "2013",
            "registered_capital": "65000万元人民币",
            "business_scope": "游戏开发、计算机软硬件技术开发",
            "headquarters": "上海市徐汇区",
            "funding_status": "未上市",
            "stock_code": "",
            "website": "https://www.mihoyo.com",
            "careers_url": "https://www.mihoyo.com/careers",
            "key_products": ["原神", "崩坏3", "崩坏：星穹铁道", "绝区零"],
            "competitors": ["腾讯", "网易"],
            "market_position": "中国二次元游戏头部企业，全球知名游戏公司",
            "recent_news": "旗下《原神》持续全球运营，《崩坏：星穹铁道》表现优异",
            "salary": {
                "avg_monthly": "25k-45k",
                "salary_range": "20k-60k",
                "year_end_bonus": "12-18薪",
                "salary_adjustment": "每年1-2次调薪",
                "benefits": ["五险一金", "补充医疗", "免费三餐", "健身房", "股票期权"],
            },
            "reputation": {
                "overall_rating": 4.0,
                "recommendation_rate": "72%",
                "ceo_approval_rate": "85%",
                "pros": ["技术氛围好", "项目影响力大", "薪资竞争力强"],
                "cons": ["加班较多", "项目管理有待提升"],
                "culture_keywords": ["技术驱动", "二次元文化", "年轻化"],
            },
            "interview": {
                "interview_difficulty": "较难",
                "interview_rounds": "3-5轮",
                "positive_rate": "65%",
                "avg_interview_duration": "2-4周",
                "common_questions": ["算法基础", "项目经验", "系统设计", "技术深度"],
                "common_answers": ["建议准备扎实的技术基础", "突出项目中的技术难点", "展示学习能力和热情"],
                "interview_tips": ["深入了解游戏开发技术栈", "准备作品集或技术博客", "了解米哈游的产品和技术方向"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，无重大劳动纠纷记录",
                "risk_items": [],
            },
            "overall_score": 78,
        },
        "小米": {
            "name": "小米科技有限责任公司",
            "english_name": "Xiaomi Corporation",
            "industry": "消费电子",
            "sub_industry": "智能手机/IoT",
            "scale": "10000人以上",
            "established_year": "2010",
            "registered_capital": "103000万人民币",
            "business_scope": "智能手机、IoT设备、互联网服务",
            "headquarters": "北京市",
            "funding_status": "上市",
            "stock_code": "HKEX:1810",
            "website": "https://www.mi.com",
            "careers_url": "https://hr.xiaomi.com",
            "key_products": ["小米手机", "米家IoT产品"],
            "competitors": ["苹果", "华为", "OPPO"],
            "market_position": "全球领先的消费电子品牌",
            "recent_news": "进军汽车行业",
            "salary": {
                "avg_monthly": "22000元",
                "salary_range": "10000-35000元",
                "year_end_bonus": "1-3个月",
                "salary_adjustment": "一年一次",
                "benefits": ["五险一金", "餐补", "年度体检", "产品内购"],
            },
            "reputation": {
                "overall_rating": "3.9/5",
                "recommendation_rate": "68%",
                "ceo_approval_rate": "82%",
                "pros": ["产品理念好", "团队年轻", "成长空间大", "扁平化管理"],
                "cons": ["薪资竞争力一般", "部分业务波动大", "流程不够完善"],
                "culture_keywords": ["和用户做朋友", "感动人心", "厚道价格", "效率优先"],
            },
            "interview": {
                "interview_difficulty": "中等",
                "interview_rounds": "2-3轮",
                "positive_rate": "35%",
                "avg_interview_duration": "1小时",
                "common_questions": [
                    "为什么选择小米？",
                    "介绍一个产品相关的项目经验",
                    "你对IoT的理解？",
                    "如何看待性价比？",
                    "你使用过哪些小米产品？",
                ],
                "common_answers": {
                    "为什么选择小米？": "小米的产品理念和商业模式很吸引我，用科技改善生活的愿景让我很认同。",
                    "介绍一个产品相关的项目经验": "我参与过一款IoT设备的开发，从用户需求出发，优化了产品的用户体验和性能。",
                    "你对IoT的理解？": "IoT正在连接万物，打造智能生活场景，数据和AI是IoT的核心驱动力。",
                    "如何看待性价比？": "性价比不是低价，而是用合理的价格提供超出预期的产品体验和品质。",
                    "你使用过哪些小米产品？": "我使用过小米手机、智能音箱和智能家居设备，对MIUI系统和米家生态很熟悉。",
                },
                "interview_tips": ["了解小米产品", "准备产品思维", "展示学习能力", "关注IoT"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，注重员工培养。",
                "risk_items": [],
            },
        },
        "京东": {
            "name": "北京京东世纪贸易有限公司",
            "english_name": "JD.com",
            "industry": "互联网",
            "sub_industry": "电商/物流",
            "scale": "10000人以上",
            "established_year": "2004",
            "registered_capital": "139798万人民币",
            "business_scope": "电子商务、物流配送、数字科技",
            "headquarters": "北京市",
            "funding_status": "上市",
            "stock_code": "NASDAQ:JD",
            "website": "https://www.jd.com",
            "careers_url": "https://campus.jd.com",
            "key_products": ["京东商城", "京东物流", "京东健康"],
            "competitors": ["阿里巴巴", "拼多多"],
            "market_position": "中国电商行业第二",
            "recent_news": "京东物流上市",
            "salary": {
                "avg_monthly": "24000元",
                "salary_range": "12000-40000元",
                "year_end_bonus": "2-4个月",
                "salary_adjustment": "一年一次",
                "benefits": ["五险一金", "房补", "餐补", "员工购", "物流补贴"],
            },
            "reputation": {
                "overall_rating": "4.0/5",
                "recommendation_rate": "73%",
                "ceo_approval_rate": "85%",
                "pros": ["物流体系强", "福利待遇好", "技术栈完善", "晋升机会多"],
                "cons": ["部分岗位加班多", "物流一线辛苦", "组织变革频繁"],
                "culture_keywords": ["客户为先", "诚信", "协作", "拼搏"],
            },
            "interview": {
                "interview_difficulty": "中等",
                "interview_rounds": "2-4轮",
                "positive_rate": "30%",
                "avg_interview_duration": "1.5小时",
                "common_questions": [
                    "为什么选择京东？",
                    "介绍一个高可用系统的设计经验",
                    "如何处理大数据场景？",
                    "你对电商物流的理解？",
                    "如何应对促销大促？",
                ],
                "common_answers": {
                    "为什么选择京东？": "京东在电商和物流领域有独特优势，技术体系完善，能够提供丰富的技术实践机会。",
                    "介绍一个高可用系统的设计经验": "我参与过订单系统的高可用改造，通过多活部署和熔断机制提升了系统稳定性。",
                    "如何处理大数据场景？": "采用Hadoop/Spark等大数据技术栈，结合数据仓库和实时计算来处理海量数据。",
                    "你对电商物流的理解？": "物流是电商的核心竞争力之一，智能化和自动化是物流发展的重要方向。",
                    "如何应对促销大促？": "通过容量规划、弹性伸缩、流量控制等方式来保障系统在大促期间的稳定性。",
                },
                "interview_tips": ["了解电商业务", "准备系统设计", "关注高可用", "了解物流"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，注重物流员工权益保障。",
                "risk_items": [],
            },
        },
        "美团": {
            "name": "北京三快在线科技有限公司",
            "english_name": "Meituan",
            "industry": "互联网",
            "sub_industry": "本地生活服务",
            "scale": "10000人以上",
            "established_year": "2010",
            "registered_capital": "50000万人民币",
            "business_scope": "外卖、到店餐饮、旅游",
            "headquarters": "北京市",
            "funding_status": "上市",
            "stock_code": "HKEX:3690",
            "website": "https://www.meituan.com",
            "careers_url": "https://zhaopin.meituan.com",
            "key_products": ["美团外卖", "美团点评", "美团优选"],
            "competitors": ["饿了么", "抖音本地生活"],
            "market_position": "本地生活服务龙头",
            "recent_news": "布局社区团购",
            "salary": {
                "avg_monthly": "25000元",
                "salary_range": "13000-42000元",
                "year_end_bonus": "2-5个月",
                "salary_adjustment": "一年一次",
                "benefits": ["五险一金", "餐补", "打车补贴", "年度体检"],
            },
            "reputation": {
                "overall_rating": "3.8/5",
                "recommendation_rate": "70%",
                "ceo_approval_rate": "80%",
                "pros": ["业务场景丰富", "技术挑战大", "成长速度快", "团队氛围好"],
                "cons": ["外卖业务压力大", "部分岗位加班多", "竞争激烈"],
                "culture_keywords": ["以客户为中心", "长期主义", "坦诚沟通", "追求卓越"],
            },
            "interview": {
                "interview_difficulty": "中等偏上",
                "interview_rounds": "3-4轮",
                "positive_rate": "26%",
                "avg_interview_duration": "1.5小时",
                "common_questions": [
                    "为什么选择美团？",
                    "介绍一个地理相关的项目经验",
                    "如何处理实时数据？",
                    "你对本地生活的理解？",
                    "如何优化配送效率？",
                ],
                "common_answers": {
                    "为什么选择美团？": "美团在本地生活服务领域处于领先地位，业务场景贴近用户，技术挑战丰富。",
                    "介绍一个地理相关的项目经验": "我参与过配送路径优化系统的开发，通过图算法优化配送路线，提升了配送效率。",
                    "如何处理实时数据？": "使用Kafka/Flink等实时流处理技术，结合Redis缓存来处理实时数据。",
                    "你对本地生活的理解？": "本地生活正在从线上线下融合向即时零售演进，即时配送是核心基础设施。",
                    "如何优化配送效率？": "通过算法优化路径规划、动态调度骑手、预测订单需求等方式来提升配送效率。",
                },
                "interview_tips": ["了解LBS技术", "准备算法知识", "关注实时数据", "了解外卖业务"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，注重骑手权益保障。",
                "risk_items": [],
            },
        },
        "网易": {
            "name": "网易(杭州)网络有限公司",
            "english_name": "NetEase",
            "industry": "互联网",
            "sub_industry": "游戏/音乐/教育",
            "scale": "10000人以上",
            "established_year": "1997",
            "registered_capital": "70000万人民币",
            "business_scope": "游戏、音乐、教育、电商",
            "headquarters": "浙江省杭州市",
            "funding_status": "上市",
            "stock_code": "NASDAQ:NTES",
            "website": "https://www.163.com",
            "careers_url": "https://hr.163.com",
            "key_products": ["网易云音乐", "梦幻西游", "网易严选"],
            "competitors": ["腾讯", "字节跳动"],
            "market_position": "中国领先的互联网公司",
            "recent_news": "网易云音乐上市",
            "salary": {
                "avg_monthly": "27000元",
                "salary_range": "14000-48000元",
                "year_end_bonus": "3-6个月",
                "salary_adjustment": "一年两次",
                "benefits": ["五险一金", "房补", "餐补", "免费班车", "健身房"],
            },
            "reputation": {
                "overall_rating": "4.1/5",
                "recommendation_rate": "76%",
                "ceo_approval_rate": "87%",
                "pros": ["企业文化好", "福利完善", "工作生活平衡", "技术氛围浓厚"],
                "cons": ["晋升较慢", "部分游戏项目压力大", "业务分散"],
                "culture_keywords": ["匠心", "创新", "务实", "分享"],
            },
            "interview": {
                "interview_difficulty": "中等",
                "interview_rounds": "2-3轮",
                "positive_rate": "32%",
                "avg_interview_duration": "1.5小时",
                "common_questions": [
                    "为什么选择网易？",
                    "介绍一个娱乐相关的项目经验",
                    "如何处理音频/视频数据？",
                    "你对游戏行业的看法？",
                    "如何保证项目进度？",
                ],
                "common_answers": {
                    "为什么选择网易？": "网易注重产品品质和用户体验，在游戏和音乐领域有深厚积累，工作氛围也很吸引人。",
                    "介绍一个娱乐相关的项目经验": "我参与过音乐推荐系统的开发，通过深度学习模型提升了推荐准确率。",
                    "如何处理音频/视频数据？": "使用FFmpeg等工具进行音视频处理，结合CDN分发来保障内容传输。",
                    "你对游戏行业的看法？": "游戏正在从娱乐向多元化发展，电竞、云游戏、元宇宙是重要方向。",
                    "如何保证项目进度？": "通过敏捷开发、定期同步、风险预判等方式来保证项目按时交付。",
                },
                "interview_tips": ["了解网易产品", "准备项目案例", "展示技术深度", "关注游戏"],
            },
            "labor_risk": {
                "risk_level": "低",
                "risk_analysis": "公司劳动合规情况良好，注重员工福利。",
                "risk_items": [],
            },
        },
    }

    # 查找匹配的公司数据
    for keyword, data in company_keywords.items():
        if keyword in company_name:
            base_data = data.copy()
            break
    else:
        # 尝试从 BRAND_MAPPING 获取品牌对应的工商全称
        from .services.entity_resolver import BRAND_MAPPING
        matched = False
        # 先检查 key（品牌名称）
        for brand, full_name in BRAND_MAPPING.items():
            if brand.lower() in company_name.lower() or company_name.lower() in brand.lower():
                base_data = {
                    "name": full_name,
                    "english_name": "",
                    "industry": "未知",
                    "sub_industry": "未知",
                    "scale": "未知",
                    "established_year": "",
                    "registered_capital": "",
                    "business_scope": "",
                    "headquarters": "",
                    "funding_status": "",
                    "stock_code": "",
                    "website": "",
                    "careers_url": "",
                    "key_products": [],
                    "competitors": [],
                    "market_position": "",
                    "data_source": "品牌匹配",
                }
                matched = True
                break
        # 再检查 value（工商全称）—— _find_closest_company_name 可能已将简称解析为全称
        if not matched:
            cl = company_name.lower()
            for brand, full_name in BRAND_MAPPING.items():
                fnl = full_name.lower()
                if cl == fnl or (len(cl) >= 4 and (cl in fnl or fnl in cl)):
                    base_data = {
                        "name": full_name,
                        "english_name": "",
                        "industry": "未知",
                        "sub_industry": "未知",
                        "scale": "未知",
                        "established_year": "",
                        "registered_capital": "",
                        "business_scope": "",
                        "headquarters": "",
                        "funding_status": "",
                        "stock_code": "",
                        "website": "",
                        "careers_url": "",
                        "key_products": [],
                        "competitors": [],
                        "market_position": "",
                        "data_source": "品牌匹配",
                    }
                    matched = True
                    break
        
        if not matched:
            # 未知公司且不在任何数据源中：标记为无效实体
            base_data = {
                "name": company_name,
                "english_name": "",
                "industry": "未知",
                "sub_industry": "未知",
                "scale": "未知",
                "established_year": "",
                "registered_capital": "",
                "business_scope": "",
                "headquarters": "",
                "funding_status": "",
                "stock_code": "",
                "website": "",
                "careers_url": "",
                "key_products": [],
                "competitors": [],
                "market_position": "",
                "data_source": "用户输入",
                "invalid_entity": True,
                "error": f'未找到「{company_name}」的公开企业信息，请检查输入是否准确。',
            }

    base_data["overall_score"] = _calculate_overall_score(base_data)

    return base_data


def analyze_companies_for_job_seeker(companies_data, preferences=""):
    """
    站在求职者角度深度分析多家公司
    :param companies_data: 公司数据列表，每个元素包含{'name': '公司名', 'data': {...}}
    :param preferences: 用户偏好（如薪资、稳定性、发展空间等）
    :return: 详细的对比分析结果
    """
    if len(companies_data) < 2:
        return {"error": "至少需要对比两家公司"}

    # 构建公司信息摘要
    companies_info = []
    for company in companies_data:
        name = company["name"]
        data = company["data"]
        full_name = _get_company_full_name(name)
        companies_info.append(
            {
                "name": name,
                "full_name": full_name,
                "industry": data.get("industry", "-"),
                "sub_industry": data.get("sub_industry", "-"),
                "scale": data.get("scale", "-"),
                "funding_status": data.get("funding_status", "-"),
                "headquarters": data.get("headquarters", "-"),
                "rating": data.get("reputation", {}).get("overall_rating", "-"),
                "recommendation_rate": data.get("reputation", {}).get("recommendation_rate", "-"),
                "avg_salary": data.get("salary", {}).get("avg_monthly", "-"),
                "risk_level": data.get("labor_risk", {}).get("risk_level", "-"),
                "pros": ", ".join(data.get("reputation", {}).get("pros", [])),
                "cons": ", ".join(data.get("reputation", {}).get("cons", [])),
            }
        )

    # 使用DeepSeek API生成对比分析
    system_prompt = """你是一个专业的求职顾问，擅长对比分析多家公司的优劣，为求职者提供客观、有价值的建议。
    你需要站在求职者的角度，考虑薪资、发展空间、工作生活平衡、稳定性等多个维度。

【最高优先级：主语校验】
在总结之前，必须确认每家对比对象均为真实企业实体，而非个人姓名或无关关键词。
若某关键词并非企业主体，不得为其生成公司分析，应在结果中明确标注「非有效企业实体」。"""

    companies_lines = []
    for i, c in enumerate(companies_info):
        companies_lines.append(
            f"{i + 1}. {c['full_name']}（{c['name']}）\n   行业: {c['industry']} {c['sub_industry']}\n   规模: {c['scale']}\n   融资: {c['funding_status']}\n   总部: {c['headquarters']}\n   评分: {c['rating']}\n   推荐率: {c['recommendation_rate']}\n   平均薪资: {c['avg_salary']}\n   风险等级: {c['risk_level']}\n   优势: {c['pros']}\n   劣势: {c['cons']}"
        )
    companies_text = "\n".join(companies_lines)

    prompt = f"""请对以下{len(companies_info)}家公司进行深度对比分析，用户偏好：{preferences or "综合考虑"}

公司信息：
{companies_text}

请从以下维度进行分析并给出JSON格式结果：

1. comparison_table: 对比表格数据（包含公司名、行业、规模、融资、评分、薪资、风险等）
2. detailed_analysis: 每家公司的详细分析（包含overview、strengths、weaknesses、career_outlook、fit_for）
3. best_for: 各维度最佳选择（salary/stability/growth/culture/work_life_balance）
4. recommendation: 综合推荐建议（结合用户偏好）
5. risk_warnings: 风险警告列表
6. tips: 求职建议列表

请确保分析：
- 客观对比各公司的优劣
- 结合用户偏好给出针对性建议
- 突出各公司适合的人群特征
- 给出实用的求职建议

返回格式为JSON：
{{
  "comparison_table": [...],
  "detailed_analysis": [...],
  "best_for": {{"salary": "", "stability": "", "growth": "", "culture": "", "work_life_balance": ""}},
  "recommendation": "",
  "risk_warnings": [...],
  "tips": [...]
}}"""

    ai_result = _call_deepseek_api(prompt, system_prompt)

    # 解析AI返回结果
    import json

    result = {
        "comparison_table": [],
        "detailed_analysis": [],
        "best_for": {},
        "recommendation": "",
        "risk_warnings": [],
        "tips": [],
    }

    # 先构建基础的comparison_table（确保公司名称显示）
    for company in companies_data:
        name = company.get("name", "") or "未知公司"
        data = company.get("data", {})
        full_name = _get_company_full_name(name) if name != "未知公司" else "未知公司"

        # 安全获取各字段值，确保不为空
        industry = data.get("industry", "") or data.get("sub_industry", "") or "互联网"
        sub_industry = data.get("sub_industry", "") or ""
        scale = data.get("scale", "") or "未知"
        funding_status = data.get("funding_status", "") or "未知"

        # 获取评分 - 处理 "3.8/5" 格式
        reputation = data.get("reputation", {})
        if isinstance(reputation, dict):
            rating_raw = reputation.get("overall_rating", "")
            if rating_raw:
                # 如果是 "3.8/5" 格式，只取数字部分
                if "/" in str(rating_raw):
                    rating = str(rating_raw).split("/")[0]
                else:
                    rating = str(rating_raw)
            else:
                rating = "-"
            recommendation_rate = reputation.get("recommendation_rate", "") or "-"
        else:
            rating = "-"
            recommendation_rate = "-"

        # 获取薪资
        salary = data.get("salary", {})
        if isinstance(salary, dict):
            avg_salary = salary.get("avg_monthly", "") or "-"
        else:
            avg_salary = "-"

        # 获取风险等级
        labor_risk = data.get("labor_risk", {})
        if isinstance(labor_risk, dict):
            risk_level = labor_risk.get("risk_level", "") or "-"
        else:
            risk_level = "-"

        comp_item = {
            "name": name,
            "full_name": full_name,
            "industry": f"{industry} {sub_industry}" if sub_industry else industry,
            "scale": scale,
            "funding_status": funding_status,
            "rating": rating,
            "recommendation_rate": recommendation_rate,
            "avg_salary": avg_salary,
            "risk_level": risk_level,
        }
        result["comparison_table"].append(comp_item)

    try:
        if ai_result:
            json_str = ai_result
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]

            ai_data = json.loads(json_str)

            # 更新其他字段，但保留我们构建的comparison_table
            # 注意：不更新comparison_table，确保公司名称正确显示
            if "detailed_analysis" in ai_data:
                # 处理详细分析数据，确保格式正确
                for analysis in ai_data["detailed_analysis"]:
                    # 确保strengths是列表
                    if "strengths" in analysis:
                        if isinstance(analysis["strengths"], str):
                            text = analysis["strengths"]
                            # 尝试多种分隔符分割
                            if "；" in text:
                                parts = text.split("；")
                            elif ";" in text:
                                parts = text.split(";")
                            elif "，" in text:
                                parts = text.split("，")
                            elif "," in text:
                                parts = text.split(",")
                            else:
                                parts = [text]  # 无法分割则作为整体

                            # 过滤并清理
                            analysis["strengths"] = [
                                s.strip() for s in parts if s.strip() and len(s.strip()) > 2
                            ]

                            # 如果分割后仍为空或只有很少内容，尝试按句子分割
                            if len(analysis["strengths"]) <= 1 and len(text) > 20:
                                if "。" in text:
                                    parts = text.split("。")
                                    analysis["strengths"] = [
                                        s.strip() for s in parts if s.strip() and len(s.strip()) > 5
                                    ]
                        elif isinstance(analysis["strengths"], list):
                            # 过滤掉单字符元素
                            analysis["strengths"] = [
                                s
                                for s in analysis["strengths"]
                                if isinstance(s, str) and len(s.strip()) > 2
                            ]

                    # 确保weaknesses是列表
                    if "weaknesses" in analysis:
                        if isinstance(analysis["weaknesses"], str):
                            text = analysis["weaknesses"]
                            if "；" in text:
                                parts = text.split("；")
                            elif ";" in text:
                                parts = text.split(";")
                            elif "，" in text:
                                parts = text.split("，")
                            elif "," in text:
                                parts = text.split(",")
                            else:
                                parts = [text]

                            analysis["weaknesses"] = [
                                s.strip() for s in parts if s.strip() and len(s.strip()) > 2
                            ]

                            if len(analysis["weaknesses"]) <= 1 and len(text) > 20:
                                if "。" in text:
                                    parts = text.split("。")
                                    analysis["weaknesses"] = [
                                        s.strip() for s in parts if s.strip() and len(s.strip()) > 5
                                    ]
                        elif isinstance(analysis["weaknesses"], list):
                            analysis["weaknesses"] = [
                                s
                                for s in analysis["weaknesses"]
                                if isinstance(s, str) and len(s.strip()) > 2
                            ]

                    # 确保fit_for是列表
                    if "fit_for" in analysis:
                        if isinstance(analysis["fit_for"], str):
                            text = analysis["fit_for"]
                            if "；" in text:
                                parts = text.split("；")
                            elif "；" in text:
                                parts = text.split("；")
                            elif "、" in text:
                                parts = text.split("、")
                            elif "，" in text:
                                parts = text.split("，")
                            elif "," in text:
                                parts = text.split(",")
                            else:
                                parts = [text]

                            analysis["fit_for"] = [
                                s.strip() for s in parts if s.strip() and len(s.strip()) > 2
                            ]
                        elif isinstance(analysis["fit_for"], list):
                            analysis["fit_for"] = [
                                s
                                for s in analysis["fit_for"]
                                if isinstance(s, str) and len(s.strip()) > 2
                            ]

                    # 确保公司名使用全名
                    if "company" in analysis:
                        analysis["full_name"] = _get_company_full_name(analysis["company"])

                result["detailed_analysis"] = ai_data["detailed_analysis"]
            if "best_for" in ai_data:
                result["best_for"] = ai_data["best_for"]
            if "recommendation" in ai_data:
                result["recommendation"] = ai_data["recommendation"]
            if "risk_warnings" in ai_data:
                result["risk_warnings"] = ai_data["risk_warnings"]
            if "tips" in ai_data:
                result["tips"] = ai_data["tips"]
        else:
            raise ValueError("AI返回为空")
    except Exception as e:
        try:
            print(f"AI分析解析失败: {e}，使用备用分析")
        except:
            pass
        # 使用备用分析逻辑补充其他字段
        fallback = _fallback_company_comparison(companies_data, preferences)
        result["detailed_analysis"] = fallback["detailed_analysis"]
        result["best_for"] = fallback["best_for"]
        result["recommendation"] = fallback["recommendation"]
        result["risk_warnings"] = fallback["risk_warnings"]
        result["tips"] = fallback["tips"]

    return result


def _fallback_company_comparison(companies_data, preferences):
    """备用对比分析（当AI不可用时）"""
    result = {
        "comparison_table": [],
        "detailed_analysis": [],
        "best_for": {},
        "recommendation": "",
        "risk_warnings": [],
        "tips": [],
    }

    # 构建对比表格
    for company in companies_data:
        name = company.get("name", "") or "未知公司"
        data = company.get("data", {})
        full_name = _get_company_full_name(name) if name != "未知公司" else "未知公司"

        # 安全获取各字段值
        industry = data.get("industry", "") or "互联网"
        sub_industry = data.get("sub_industry", "") or ""
        scale = data.get("scale", "") or "未知"
        funding_status = data.get("funding_status", "") or "未知"

        # 获取评分
        reputation = data.get("reputation", {})
        if isinstance(reputation, dict):
            rating_raw = reputation.get("overall_rating", "")
            if rating_raw:
                if "/" in str(rating_raw):
                    rating = str(rating_raw).split("/")[0]
                else:
                    rating = str(rating_raw)
            else:
                rating = "-"
            recommendation_rate = reputation.get("recommendation_rate", "") or "-"
        else:
            rating = "-"
            recommendation_rate = "-"

        # 获取薪资
        salary = data.get("salary", {})
        if isinstance(salary, dict):
            avg_salary = salary.get("avg_monthly", "") or "-"
        else:
            avg_salary = "-"

        # 获取风险等级
        labor_risk = data.get("labor_risk", {})
        if isinstance(labor_risk, dict):
            risk_level = labor_risk.get("risk_level", "") or "-"
        else:
            risk_level = "-"

        comp_item = {
            "name": name,
            "full_name": full_name,
            "industry": f"{industry} {sub_industry}" if sub_industry else industry,
            "scale": scale,
            "funding_status": funding_status,
            "rating": rating,
            "recommendation_rate": recommendation_rate,
            "avg_salary": avg_salary,
            "risk_level": risk_level,
            "pros": reputation.get("pros", []) if isinstance(reputation, dict) else [],
            "cons": reputation.get("cons", []) if isinstance(reputation, dict) else [],
        }
        result["comparison_table"].append(comp_item)

    # 生成详细分析
    for company in companies_data:
        name = company.get("name", "") or "未知公司"
        data = company.get("data", {})
        rep = data.get("reputation", {})
        salary = data.get("salary", {})
        full_name = _get_company_full_name(name) if name != "未知公司" else "未知公司"

        analysis = {
            "company": name,
            "full_name": full_name,
            "overview": f"{full_name}是一家位于{data.get('headquarters', '未知')}的{data.get('industry', '互联网')}行业公司，规模{data.get('scale', '未知')}。",
            "strengths": rep.get("pros", ["团队氛围好", "发展空间大"])
            if isinstance(rep, dict)
            else ["团队氛围好", "发展空间大"],
            "weaknesses": rep.get("cons", ["部分岗位加班"])
            if isinstance(rep, dict)
            else ["部分岗位加班"],
            "career_outlook": f"公司处于{data.get('sub_industry', '互联网')}行业，发展前景良好。",
            "fit_for": _determine_fit_for(data) if data else ["追求成长的求职者"],
        }
        result["detailed_analysis"].append(analysis)

    # 找出各维度最佳
    result["best_for"] = {
        "salary": _find_best_for_salary(companies_data),
        "stability": _find_best_for_stability(companies_data),
        "growth": _find_best_for_growth(companies_data),
        "culture": _find_best_for_culture(companies_data),
        "work_life_balance": _find_best_for_work_life(companies_data),
    }

    # 生成建议
    names = [c["name"] for c in companies_data]
    result["recommendation"] = (
        f"根据您的偏好「{preferences or '综合考虑'}」，建议综合评估{', '.join(names)}后做出选择。"
    )
    result["risk_warnings"] = _generate_comparison_risk_warnings(companies_data)
    result["tips"] = [
        "建议在做出决定前与在职员工深入交流",
        "关注具体岗位的团队氛围和直属领导",
        "综合考虑薪资、发展、通勤等因素",
    ]

    return result


def _get_career_outlook(sub_industry):
    """根据子行业获取职业前景"""
    outlook_map = {
        "游戏": "行业发展成熟，但竞争激烈，项目成败影响较大",
        "电商": "行业稳定增长，技术栈丰富，跳槽机会多",
        "云计算": "未来趋势，技术积累价值高",
        "短视频": "高速增长期，发展空间大但变化快",
        "社交": "用户粘性高，但监管风险需关注",
        "金融科技": "行业监管严格，合规要求高",
        "企业服务": "B端市场稳定，客户需求持续",
    }
    return outlook_map.get(sub_industry, "行业发展稳定，适合长期发展")


def _determine_fit_for(company_data):
    """判断公司适合的人群"""
    fit_for = []
    industry = company_data.get("sub_industry", "")
    scale = company_data.get("scale", "")
    rep = company_data.get("reputation", {})

    if "10000人" in scale:
        fit_for.append("追求大平台、完善体系的求职者")
    elif "100-500人" in scale or "500-1000人" in scale:
        fit_for.append("希望快速成长、承担更多职责的求职者")

    if "游戏" in industry:
        fit_for.append("对游戏行业有热情的从业者")
    elif "电商" in industry:
        fit_for.append("喜欢快节奏业务的从业者")
    elif "云计算" in industry:
        fit_for.append("专注技术深度的工程师")

    if rep.get("pros"):
        if "扁平化" in " ".join(rep["pros"]):
            fit_for.append("喜欢扁平化管理的求职者")
        if "国际化" in " ".join(rep["pros"]):
            fit_for.append("有国际化视野的求职者")

    if not fit_for:
        fit_for.append("综合能力较强的求职者")

    return fit_for


def _find_best_for_salary(companies_data):
    """找出薪资最优的公司"""
    best = None
    max_salary = 0

    for company in companies_data:
        salary_str = company["data"].get("salary", {}).get("avg_monthly", "")
        try:
            salary = int("".join([c for c in salary_str if c.isdigit()]))
            if salary > max_salary:
                max_salary = salary
                best = company["name"]
        except:
            pass

    return best or companies_data[0]["name"]


def _find_best_for_stability(companies_data):
    """找出最稳定的公司"""
    best = None
    best_score = 0

    for company in companies_data:
        data = company["data"]
        score = 0

        if data.get("funding_status") == "上市":
            score += 3
        elif data.get("funding_status") in ["D轮", "C轮"]:
            score += 2

        if "10000人" in data.get("scale", ""):
            score += 2

        if data.get("labor_risk", {}).get("risk_level") == "低":
            score += 1

        if score > best_score:
            best_score = score
            best = company["name"]

    return best or companies_data[0]["name"]


def _find_best_for_growth(companies_data):
    """找出成长空间最大的公司"""
    best = None
    best_score = 0

    for company in companies_data:
        data = company["data"]
        score = 0

        industry = data.get("sub_industry", "")
        if "短视频" in industry or "AI" in industry or "云计算" in industry:
            score += 2

        if data.get("funding_status") in ["B轮", "C轮"]:
            score += 1

        if "500-1000人" in data.get("scale", "") or "1000-5000人" in data.get("scale", ""):
            score += 1

        rep = data.get("reputation", {})
        if rep.get("pros") and "成长" in " ".join(rep["pros"]):
            score += 1

        if score > best_score:
            best_score = score
            best = company["name"]

    return best or companies_data[0]["name"]


def _find_best_for_culture(companies_data):
    """找出文化氛围最好的公司"""
    best = None
    best_score = 0

    for company in companies_data:
        data = company["data"]
        rep = data.get("reputation", {})
        score = 0

        try:
            rating = float(rep.get("overall_rating", "0").split("/")[0])
            score += rating * 2
        except:
            pass

        try:
            rec_rate = float(rep.get("recommendation_rate", "0").replace("%", ""))
            score += rec_rate / 10
        except:
            pass

        if score > best_score:
            best_score = score
            best = company["name"]

    return best or companies_data[0]["name"]


def _find_best_for_work_life(companies_data):
    """找出工作生活平衡最好的公司"""
    best = None
    best_score = 0

    for company in companies_data:
        data = company["data"]
        rep = data.get("reputation", {})
        score = 0

        if rep.get("cons"):
            cons_str = " ".join(rep["cons"])
            if "加班" not in cons_str or "加班较少" in cons_str:
                score += 2
            elif "部分加班" in cons_str:
                score += 1

        industry = data.get("sub_industry", "")
        if "教育" in industry or "金融" in industry:
            score += 1

        if score > best_score:
            best_score = score
            best = company["name"]

    return best or companies_data[0]["name"]


def _generate_company_recommendation(companies_data, preferences):
    """生成综合推荐"""
    names = [c["name"] for c in companies_data]

    if not preferences:
        preferences = "综合考虑"

    recommendation = f"基于你的偏好「{preferences}」，以下是对{', '.join(names)}的综合分析：\n\n"

    # 简单的推荐逻辑
    best_stability = _find_best_for_stability(companies_data)
    best_salary = _find_best_for_salary(companies_data)

    recommendation += f"🏆 稳定性最佳：{best_stability}\n"
    recommendation += f"💰 薪资最优：{best_salary}\n\n"

    # 根据偏好给出建议
    if "薪资" in preferences or "钱" in preferences:
        recommendation += f"根据你的偏好，{best_salary}可能是更适合你的选择。"
    elif "稳定" in preferences or "安全" in preferences:
        recommendation += f"根据你的偏好，{best_stability}可能是更适合你的选择。"
    elif "成长" in preferences or "发展" in preferences:
        best_growth = _find_best_for_growth(companies_data)
        recommendation += (
            f"根据你的偏好，{best_growth}可能是更适合你的选择，该公司所在行业发展潜力大。"
        )
    else:
        recommendation += "建议根据你的具体职业规划和生活需求做最终决定。"

    return recommendation


def _generate_comparison_risk_warnings(companies_data):
    """生成风险警告（用于公司对比）"""
    warnings = []

    for company in companies_data:
        data = company["data"]
        name = company["name"]

        if data.get("labor_risk", {}).get("risk_level") == "高":
            warnings.append(f"⚠️ {name}存在较高劳动风险，建议谨慎评估")

        rep = data.get("reputation", {})
        try:
            rating = float(rep.get("overall_rating", "0").split("/")[0])
            if rating < 3.5:
                warnings.append(f"⚠️ {name}员工评分较低（{rating}/5），建议进一步了解")
        except:
            pass

        try:
            rec_rate = float(rep.get("recommendation_rate", "0").replace("%", ""))
            if rec_rate < 60:
                warnings.append(f"⚠️ {name}员工推荐率较低（{rec_rate}%）")
        except:
            pass

    return warnings


def _generate_job_seeker_tips(companies_data, preferences):
    """生成求职建议"""
    tips = []

    tips.append("💡 建议在面试前深入了解目标公司的业务方向和企业文化")
    tips.append("💡 关注薪资结构，除月薪外还要考虑年终奖、股票、福利等")
    tips.append("💡 与在职员工交流可以获得更真实的公司信息")
    tips.append("💡 结合个人职业规划选择最适合的发展平台")

    if len(companies_data) >= 2:
        tips.append("💡 可以将多个Offer作为谈判筹码，争取更好的待遇")

    if "薪资" in preferences:
        tips.append("💡 薪资谈判时可以参考同行业薪资水平，有理有据地提出期望")
    if "稳定" in preferences:
        tips.append("💡 建议关注公司的融资状况和业务稳定性")

    return tips


def generate_company_info_with_ai(company_name: str) -> dict:
    """
    当所有API都无法获取公司数据时，调用AI知识库生成公司简介和求职建议。
    返回 dict 格式兼容 DataSourceStatus.data。
    """
    try:
        prompt = f'''你是专业的求职顾问AI。用户查询了一家公司"{company_name}"，但系统中没有该公司的公开数据。
请基于你的知识生成以下内容：
1. 这家公司可能的行业和业务范围（基于名称推断，诚实注明是推测）
2. 如果这是一个知名公司，提供你所知的简介
3. 求职建议：求职者应如何进一步了解这家公司
4. 风险提示：数据来源于AI知识库，并非官方工商数据

请输出JSON格式，字段：company_name, industry, business_scope, company_summary, job_search_tips, risk_disclaimer
不要编造不存在的公司。如果不确定，诚实说"未找到相关信息"。'''

        system_prompt = "你是一个诚实的AI知识库，不要编造不存在的信息。"
        import json
        response = _call_deepseek_api(prompt, system_prompt)
        
        if not response:
            return {
                "company_name": company_name,
                "summary": f"未找到{company_name}的公开企业信息。",
                "ai_generated": True,
                "fallback": True
            }
        
        text = response.strip()
        # 尝试解析JSON
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        try:
            result = json.loads(text)
            result["company_name"] = company_name
            result["ai_generated"] = True
            result["fallback"] = True
            return result
        except json.JSONDecodeError:
            return {
                "company_name": company_name,
                "summary": text[:500],
                "raw_text": text,
                "ai_generated": True,
                "fallback": True
            }
    except Exception as e:
        logger.error(f"[AI Fallback] AI 知识库出错: {e}")
        return {
            "company_name": company_name,
            "summary": f"未找到{company_name}的公开企业信息。",
            "ai_generated": True,
            "fallback": True
        }

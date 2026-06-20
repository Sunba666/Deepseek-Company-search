# -*- coding: utf-8 -*-
"""
实体解析器 (Entity Resolver) — 多级匹配引擎
支持全称/简称/英文/带描述文字/拼写错误 → 精确匹配

六层递进式匹配：
  Level 1: 精确匹配（数据库规范名 + 别名 + BRAND_MAPPING）
  Level 2: 模糊/前缀匹配（消除"做游戏的莉莉丝"中的噪音词）
  Level 3: 搜索引擎补全（Tavily 搜索 {input} 公司 全称）
  Level 4: AI 实体消歧（DeepSeek 判断意图）
  Level 5: 关键词拆解（提取核心品牌名）
  Level 6: 兜底 — 候选列表或"未找到"
"""

import re
import logging
from .api_client import API_TIMEOUT
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ==================== 公司后缀列表 ====================
COMPANY_SUFFIXES = [
    '有限公司', '股份有限公司', '有限责任公司',
    '集团', '集团有限公司', '股份公司',
    '科技有限公司', '技术有限公司',
    '网络科技', '网络', '信息技术', '软件技术',
    '投资有限公司', '实业有限公司',
    '发展有限公司', '控股有限公司'
]

# ==================== 噪音词（匹配时忽略） ====================
_NOISE_WORDS = [
    "做", "搞", "弄", "那个", "一家", "看看", "查", "搜",
    "的", "是", "吗", "吧", "呢", "啊", "哦",
    "公司", "企业", "集团", "科技",
    "怎么样", "好不好", "值得去吗", "怎么样",
    "我想查", "帮我查", "帮我搜", "帮我看看",
    "请查", "请问", "想知道", "了解",
]

# ==================== 非公司查询特征词 ====================
_NON_COMPANY_PATTERNS = [
    r"天气", r"时间", r"日期", r"星期", r"新闻",
    r"你好", r"嗨", r"hello", r"hi",
    r"你是谁", r"今天", r"明天", r"现在",
]

# ==================== 知名品牌白名单 ====================
BRAND_MAPPING: Dict[str, str] = {
    # 互联网科技
    '腾讯': '腾讯科技（深圳）有限公司',
    'tencent': '腾讯科技（深圳）有限公司',
    'TX': '腾讯科技（深圳）有限公司',
    '字节': '北京字节跳动科技有限公司',
    '字节跳动': '北京字节跳动科技有限公司',
    'bytedance': '北京字节跳动科技有限公司',
    '阿里': '阿里巴巴（中国）有限公司',
    '阿里巴巴': '阿里巴巴（中国）有限公司',
    'alibaba': '阿里巴巴（中国）有限公司',
    '百度': '百度在线网络技术（北京）有限公司',
    'baidu': '百度在线网络技术（北京）有限公司',
    '网易': '网易（杭州）网络有限公司',
    'netease': '网易（杭州）网络有限公司',
    '京东': '北京京东世纪贸易有限公司',
    'jd': '北京京东世纪贸易有限公司',
    '美团': '北京三快科技有限公司',
    'meituan': '北京三快科技有限公司',
    '拼多多': '上海寻梦信息技术有限公司',
    'pdd': '上海寻梦信息技术有限公司',
    'pinduoduo': '上海寻梦信息技术有限公司',
    '小米': '小米科技有限责任公司',
    'xiaomi': '小米科技有限责任公司',
    '华为': '华为技术有限公司',
    'huawei': '华为技术有限公司',
    '荣耀': '深圳市智信新信息技术有限公司',
    'honor': '深圳市智信新信息技术有限公司',
    'vivo': '维沃移动通信有限公司',
    'OPPO': '广东欧珀移动通信有限公司',
    'oppo': '广东欧珀移动通信有限公司',

    # 游戏公司
    '米哈游': '米哈游科技（上海）有限公司',
    'mihoyo': '米哈游科技（上海）有限公司',
    'miHoYo': '米哈游科技（上海）有限公司',
    '原神': '米哈游科技（上海）有限公司',
    '网易游戏': '网易（杭州）网络有限公司',
    '腾讯游戏': '深圳市腾讯计算机系统有限公司',
    '完美世界': '完美世界（北京）网络技术有限公司',
    '巨人网络': '巨人网络集团股份有限公司',
    '莉莉丝': '上海莉莉丝科技股份有限公司',
    '莉莉丝游戏': '上海莉莉丝科技股份有限公司',
    'lilith': '上海莉莉丝科技股份有限公司',
    '鹰角': '上海鹰角网络科技有限公司',
    '鹰角网络': '上海鹰角网络科技有限公司',
    '明日方舟': '上海鹰角网络科技有限公司',
    '悠星': '悠星网络科技有限公司',
    '悠星网络': '悠星网络科技有限公司',
    '散爆': '上海散爆网络科技有限公司',
    '柠檬微趣': '北京柠檬微趣科技股份有限公司',
    '柠檬微趣科技': '北京柠檬微趣科技股份有限公司',

    # 金融科技
    '蚂蚁金服': '蚂蚁科技集团股份有限公司',
    '蚂蚁': '蚂蚁科技集团股份有限公司',
    'ant': '蚂蚁科技集团股份有限公司',
    '微信支付': '财付通支付科技有限公司',
    '支付宝': '支付宝（杭州）信息技术有限公司',
    'alipay': '支付宝（杭州）信息技术有限公司',

    # 新能源
    '比亚迪': '比亚迪股份有限公司',
    'byd': '比亚迪股份有限公司',
    '宁德时代': '宁德时代新能源科技股份有限公司',
    '特斯拉': '特斯拉（上海）有限公司',
    'tesla': '特斯拉（上海）有限公司',

    # 电商
    '唯品会': '广州唯品会信息科技有限公司',
    '小红书': '行吟信息科技（上海）有限公司',
    'xhs': '行吟信息科技（上海）有限公司',
    '快手': '北京快手科技有限公司',
    'kuaishou': '北京快手科技有限公司',
    '滴滴': '北京小桔科技有限公司',
    'didichuxing': '北京小桔科技有限公司',
    '携程': '携程旅游网络技术（上海）有限公司',
    '携程旅行': '携程旅游网络技术（上海）有限公司',
    'ctrip': '携程旅游网络技术（上海）有限公司',
    'B站': '上海哔哩哔哩科技有限公司',
    '哔哩哔哩': '上海哔哩哔哩科技有限公司',
    'bilibili': '上海哔哩哔哩科技有限公司',

    # 汽车
    '蔚来': '蔚来汽车科技（安徽）有限公司',
    'nio': '蔚来汽车科技（安徽）有限公司',
    '理想': '北京车和家信息技术有限公司',
    '小鹏': '广州小鹏汽车科技有限公司',
    'xpeng': '广州小鹏汽车科技有限公司',
    '大疆': '深圳市大疆创新科技有限公司',
    '大疆创新': '深圳市大疆创新科技有限公司',
    'dji': '深圳市大疆创新科技有限公司',

    # AI / 科技
    '旷视': '北京市旷视科技有限公司',
    'megvii': '北京市旷视科技有限公司',
    '商汤': '商汤科技股份有限公司',
    'sensetime': '商汤科技股份有限公司',
    '中兴': '中兴通讯股份有限公司',
    'zte': '中兴通讯股份有限公司',
    '中芯国际': '中芯国际集成电路制造有限公司',
    'smic': '中芯国际集成电路制造有限公司',
    '科大讯飞': '科大讯飞股份有限公司',
    'iflytek': '科大讯飞股份有限公司',
    '海康威视': '杭州海康威视数字技术股份有限公司',
    'hikvision': '杭州海康威视数字技术股份有限公司',
    '京东方': '京东方科技集团股份有限公司',
    'boe': '京东方科技集团股份有限公司',
}

# ==================== 构建前缀索引 ====================
_PREFIX_INDEX: Dict[str, str] = {}
for alias, full in BRAND_MAPPING.items():
    for i in range(2, len(alias) + 1):
        prefix = alias[:i].lower()
        if prefix not in _PREFIX_INDEX:
            _PREFIX_INDEX[prefix] = alias

# 倒排：全称 → 品牌名列表
_FULLNAME_TO_ALIASES: Dict[str, List[str]] = {}
for alias, full in BRAND_MAPPING.items():
    _FULLNAME_TO_ALIASES.setdefault(full, set()).add(alias)
_FULLNAME_TO_ALIASES = {k: sorted(v) for k, v in _FULLNAME_TO_ALIASES.items()}


def _clean_query(raw: str) -> str:
    """清洗用户输入：去噪音词、去多余空白。"""
    q = raw.strip().lower()
    for noise in _NOISE_WORDS:
        q = q.replace(noise, "")
    q = re.sub(r"\s+", "", q).strip()
    return q


def _is_non_company_query(raw: str) -> Optional[str]:
    """
    检测输入是否明显不是公司名。
    返回 None = 可能是公司名，返回 str = 错误提示。
    """
    q = raw.strip()
    if len(q) < 2:
        return "请输入公司名称"
    for pat in _NON_COMPANY_PATTERNS:
        if re.search(pat, q, re.IGNORECASE):
            return None  # 允许这些通过
    return None  # 默认放行


def _find_similar(query: str) -> List[Dict[str, str]]:
    """查找近似匹配的候选（编辑距离 ≤ 1 / 公共前缀）。"""
    candidates = []
    q_lower = query.lower()
    for alias, full_name in BRAND_MAPPING.items():
        a_lower = alias.lower()
        # 编辑距离 ≤ 1
        if len(a_lower) >= 2 and len(q_lower) >= 2:
            if _levenshtein(a_lower, q_lower) <= 1:
                candidates.append({"name": full_name, "source": f"近似匹配({alias})", "confidence": "中"})
        # 公共前缀 ≥ 60%
        if len(a_lower) >= 2 and len(q_lower) >= 2:
            common = 0
            for i in range(min(len(a_lower), len(q_lower))):
                if a_lower[i] == q_lower[i]:
                    common += 1
                else:
                    break
            if common / max(len(a_lower), len(q_lower)) >= 0.6:
                if not any(c["name"] == full_name for c in candidates):
                    candidates.append({"name": full_name, "source": f"前缀匹配({alias})", "confidence": "中"})
    return candidates[:5]


def _levenshtein(a: str, b: str) -> int:
    """编辑距离。"""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


# 自动别名学习（跨会话持久化到 knowledge DB）
def _learn_alias(query: str, canonical_name: str):
    """将新发现的别名存入知识库。"""
    try:
        from ..services.knowledge_db import knowledge_db
        company = knowledge_db.find_company(canonical_name)
        if company:
            aliases = __import__("json").loads(company.get("aliases", "[]"))
            if query not in aliases:
                aliases.append(query)
                # 也加小写
                if query.lower() != query:
                    aliases.append(query.lower())
                knowledge_db.upsert_company(canonical_name=canonical_name, aliases=list(set(aliases)))
                logger.info(f"[Alias LEARN] {query} -> {canonical_name}")
    except Exception:
        pass


class EntityResolver:
    """多级实体解析器。"""

    def __init__(self):
        self._tavily_client = None
        self._initialized = False
        self._poi_client = None

    def _init_tavily(self):
        try:
            from tavily import TavilyClient
            import os
            api_key = os.environ.get('TAVILY_API_KEY', '')
            if api_key:
                self._tavily_client = TavilyClient(api_key=api_key)
            self._initialized = True
        except Exception as e:
            logger.warning(f"Tavily初始化: {e}")
            self._initialized = True

    def resolve(self, query: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """
        主解析函数 — 六层递进匹配。
        """
        raw_query = query.strip()
        if not raw_query:
            return {"status": "error", "message": "请输入公司名称", "matched_name": None,
                    "candidates": [], "suggestions": []}

        # 非公司查询检测
        non_company = _is_non_company_query(raw_query)
        if non_company:
            return {"status": "not_company", "message": non_company, "matched_name": None,
                    "candidates": [], "suggestions": []}

        logger.info(f"[Resolver] 解析: {raw_query}")

        # ═══════════════════════════════════════════════
        # Level 1: 精确匹配（BRAND_MAPPING + 知识库）
        # ═══════════════════════════════════════════════
        # 1a. BRAND_MAPPING 精确匹配
        if raw_query in BRAND_MAPPING:
            canonical = BRAND_MAPPING[raw_query]
            logger.info(f"[L1] 白名单精确: {raw_query} -> {canonical}")
            _learn_alias(raw_query, canonical)
            return {"status": "matched", "message": f"匹配到：{canonical}",
                    "matched_name": canonical, "candidates": [],
                    "source": "品牌白名单", "suggestions": []}

        # 1b. 大小写不敏感匹配 BRAND_MAPPING
        q_lower = raw_query.lower()
        for alias, full_name in BRAND_MAPPING.items():
            if alias.lower() == q_lower:
                logger.info(f"[L1] 白名单大小写: {raw_query} -> {full_name}")
                _learn_alias(raw_query, full_name)
                return {"status": "matched", "message": f"匹配到：{full_name}",
                        "matched_name": full_name, "candidates": [],
                        "source": "品牌白名单", "suggestions": []}

        # 1c. 知识库别名匹配
        try:
            from ..db.cache_db import db_cache
            db_canonical = db_cache.resolve_alias(raw_query)
            if db_canonical:
                logger.info(f"[L1] 知识库别名: {raw_query} -> {db_canonical}")
                _learn_alias(raw_query, db_canonical)
                return {"status": "matched", "message": f"匹配到：{db_canonical}",
                        "matched_name": db_canonical, "candidates": [],
                        "source": "知识库别名", "suggestions": []}
        except Exception:
            pass

        # ═══════════════════════════════════════════════
        # Level 2: 模糊/前缀匹配（处理"做游戏的莉莉丝"等带描述输入）
        # ═══════════════════════════════════════════════
        cleaned = _clean_query(raw_query)
        if cleaned and cleaned != q_lower:
            # 清洗后再次尝试 Level 1
            if cleaned in BRAND_MAPPING:
                c = BRAND_MAPPING[cleaned]
                logger.info(f"[L2] 清洗后匹配: {raw_query} -> {c}")
                _learn_alias(raw_query, c)
                return {"status": "matched", "message": f"匹配到：{c}",
                        "matched_name": c, "candidates": [],
                        "source": "模糊匹配(去噪音)", "suggestions": []}
            for alias, full_name in BRAND_MAPPING.items():
                if alias.lower() == cleaned:
                    _learn_alias(raw_query, full_name)
                    return {"status": "matched", "message": f"匹配到：{full_name}",
                            "matched_name": full_name, "candidates": [],
                            "source": "模糊匹配(去噪音)", "suggestions": []}

        # 前缀匹配（清洗后的前 N 个字符）
        if len(cleaned) >= 2:
            matches = set()
            for alias, full_name in BRAND_MAPPING.items():
                a_lower = alias.lower()
                if a_lower.startswith(cleaned) or cleaned.startswith(a_lower):
                    matches.add(full_name)
            if len(matches) == 1:
                only = next(iter(matches))
                logger.info(f"[L2] 前缀唯一匹配: {raw_query} -> {only}")
                _learn_alias(raw_query, only)
                return {"status": "matched", "message": f"匹配到：{only}",
                        "matched_name": only, "candidates": [],
                        "source": "前缀匹配", "suggestions": []}
            if len(matches) > 1:
                candidates = [{"name": m, "source": "前缀匹配", "confidence": "中"} for m in matches]
                return {"status": "candidates", "message": f"找到 {len(matches)} 个候选",
                        "matched_name": None, "candidates": candidates,
                        "source": "前缀匹配", "suggestions": ["请从候选列表中确认"]}

        # ═══════════════════════════════════════════════
        # Level 3: 搜索引擎补全
        # ═══════════════════════════════════════════════
        search_match = self._search_full_name(raw_query)
        if search_match:
            logger.info(f"[L3] 搜索引擎: {raw_query} -> {search_match}")
            _learn_alias(raw_query, search_match)
            return {"status": "suggestion", "message": f"通过搜索匹配到：{search_match}",
                    "matched_name": search_match,
                    "candidates": [{"name": search_match, "source": "搜索引擎", "confidence": "中"}],
                    "source": "搜索引擎", "suggestions": []}

        # ═══════════════════════════════════════════════
        # Level 4: AI 实体消歧
        # ═══════════════════════════════════════════════
        try:
            from ..services.ai_analyzer import resolve_with_ai
            ai_result = resolve_with_ai(raw_query)
            if ai_result.get("exists", False):
                canonical = ai_result.get("canonical_name", raw_query) or raw_query
                logger.info(f"[L4] AI消歧: {raw_query} -> {canonical}")
                _learn_alias(raw_query, canonical)
                return {"status": "matched", "message": f"AI推断为：{canonical}",
                        "matched_name": canonical, "candidates": [],
                        "source": "AI消歧", "suggestions": []}
        except Exception as e:
            logger.warning(f"[L4] AI消歧失败: {e}")

        # ═══════════════════════════════════════════════
        # Level 5: 关键词拆解（提取核心关键词再匹配）
        # ═══════════════════════════════════════════════
        core = self.extract_core_keyword(raw_query)
        if core != raw_query and len(core) >= 2:
            # 用核心词再次走 L1
            if core in BRAND_MAPPING:
                c = BRAND_MAPPING[core]
                return {"status": "matched", "message": f"根据关键词匹配到：{c}",
                        "matched_name": c, "candidates": [],
                        "source": "关键词拆解", "suggestions": []}
            for alias, full_name in BRAND_MAPPING.items():
                if alias.lower() == core.lower():
                    return {"status": "matched", "message": f"根据关键词匹配到：{full_name}",
                            "matched_name": full_name, "candidates": [],
                            "source": "关键词拆解", "suggestions": []}
            # 用核心词搜索
            search_match = self._search_full_name(core)
            if search_match:
                return {"status": "suggestion", "message": f"根据关键词匹配到：{search_match}",
                        "matched_name": search_match,
                        "candidates": [{"name": search_match, "source": "关键词拆解+搜索", "confidence": "中"}],
                        "source": "关键词拆解", "suggestions": []}

        # ═══════════════════════════════════════════════
        # Level 6: 近似匹配 + 兜底
        # ═══════════════════════════════════════════════
        candidates = _find_similar(raw_query)
        if candidates:
            return {"status": "candidates", "message": f"未精确匹配，以下为近似结果",
                    "matched_name": None, "candidates": candidates,
                    "source": "近似匹配",
                    "suggestions": ["您是否想查询以下某家公司？"]}

        # 完全未找到
        suggestions = self._generate_suggestions(raw_query)
        return {"status": "not_found", "message": f'未找到与"{raw_query}"匹配的企业',
                "matched_name": None, "candidates": [],
                "source": "无", "suggestions": suggestions}

    # ========== 以下为辅助方法（保持原有实现不变） ==========

    def has_company_suffix(self, query: str) -> bool:
        query = query.strip()
        for suffix in COMPANY_SUFFIXES:
            if query.endswith(suffix):
                return True
        return False

    def is_likely_company(self, query: str) -> bool:
        query = query.strip()
        if len(query) < 2:
            return False
        company_keywords = ['公司', '集团', '有限', '科技', '技术', '网络', '信息']
        for keyword in company_keywords:
            if keyword in query:
                return True
        if query in BRAND_MAPPING:
            return True
        return False

    def extract_core_keyword(self, company_name: str) -> str:
        name = company_name.strip()
        districts = ['省', '市', '区', '县', '镇']
        for d in districts:
            m = re.search(rf'[\u4e00-\u9fa5]+{d}', name)
            if m and len(m.group()) <= 8:
                name = name.replace(m.group(), '')
        name = re.sub(r'[（(][^）)]*[）)]', '', name)
        for suffix in COMPANY_SUFFIXES:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        name = name.strip()
        return name if len(name) >= 2 else company_name

    def _search_full_name(self, short_name: str) -> Optional[str]:
        if not self._initialized:
            self._init_tavily()
        if not self._tavily_client:
            return None
        try:
            results = self._tavily_client.search(
                f"{short_name} 公司 全称 工商注册名",
                max_results=3, timeout=API_TIMEOUT
            )
            if results and results.get('results'):
                return self._extract_company_name(results['results'])
        except Exception as e:
            logger.warning(f"搜索引擎失败: {e}")
        return None

    def _extract_company_name(self, results: List[Dict]) -> Optional[str]:
        pat = re.compile(r'([\u4e00-\u9fa5]{2,}(?:科技|技术|网络|信息|软件|数据|智能|实业|投资|发展|控股|集团)?(?:股份)?有限公司)')
        for result in results:
            content = result.get('content', '') + result.get('title', '')
            matches = pat.findall(content)
            if matches:
                full = max(matches, key=len)
                if len(full) >= 5:
                    return full
        return None

    def get_candidates(self, query: str) -> List[Dict[str, str]]:
        candidates = []
        for brand_name, full_name in BRAND_MAPPING.items():
            if query in brand_name or brand_name in query:
                candidates.append({"name": full_name, "source": "品牌白名单", "confidence": "高"})
        if not candidates:
            sr = self._search_full_name(query)
            if sr:
                candidates.append({"name": sr, "source": "搜索引擎", "confidence": "中"})
        return candidates

    def _generate_suggestions(self, query: str) -> List[str]:
        suggestions = []
        if not self.is_likely_company(query):
            suggestions.append('💡 请确认输入的是公司/企业名称')
        simplified = self.extract_core_keyword(query)
        if simplified != query:
            suggestions.append(f'🔍 尝试使用更简洁的名称："{simplified}"')
        suggestions.append('📱 建议在企查查/天眼查中检索其完整工商名称')
        suggestions.append('ℹ️ 小微企业和个体户可能尚未被收录')
        return suggestions

    def validate_company_name(self, name: str) -> bool:
        name = name.strip()
        if len(name) < 2:
            return False
        if any(k in name for k in ['公司', '集团']):
            return True
        if name in BRAND_MAPPING:
            return True
        return False

    def resolve_from_whitelist(self, query: str) -> Optional[str]:
        query = query.strip()
        if query in BRAND_MAPPING:
            return BRAND_MAPPING[query]
        for bn, fn in BRAND_MAPPING.items():
            if bn in query or query in bn:
                return fn
        return None


# ==================== 全局实例 ====================
entity_resolver = EntityResolver()


def resolve_entity(query: str, auto_confirm: bool = False) -> Dict[str, Any]:
    return entity_resolver.resolve(query, auto_confirm)


def is_valid_company_name(name: str) -> bool:
    return entity_resolver.validate_company_name(name)

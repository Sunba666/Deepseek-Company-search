# -*- coding: utf-8 -*-
"""
多源API协同架构 - 数据模型定义
遵循"搜索-验证-补充-仲裁"全链路协同
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DataSource(Enum):
    """数据来源枚举"""
    TIANYA_CHECK = "tianyacha"      # 天眼查
    QICHACHA = "qichacha"           # 企查查
    TAVILY = "tavily"              # Tavily搜索
    BING_NEWS = "bing_news"        # 必应新闻
    WEIBO = "weibo"                # 微博
    ZHIHU = "zhihu"                # 知乎
    WENSHU = "wenshu"              # 中国裁判文书网
    QIXINBAO = "qixinbao"          # 启信宝
    MOCK = "mock"                  # 模拟数据


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"           # 高置信度（官方/权威来源）
    MEDIUM = "medium"       # 中置信度（媒体报道）
    LOW = "low"             # 低置信度（用户爆料/推测）
    UNVERIFIED = "unverified"  # 未验证


@dataclass
class SourceReference:
    """信息来源引用"""
    text: str                          # 原文内容
    url: str                           # 来源链接
    source: DataSource                  # 数据来源
    publish_date: Optional[str] = None  # 发布日期
    author: Optional[str] = None       # 作者/发布者


@dataclass
class ConflictItem:
    """矛盾点条目"""
    category: str                      # 矛盾类别（如"薪资与资本"、"传闻与事实"）
    description: str                   # 矛盾描述
    sources: List[Dict[str, str]]      # 涉及的源数据 [{source: str, content: str}]
    resolution_hint: str = ""          # 解决提示


@dataclass
class EntityInfo:
    """
    工商铁证数据（第一层）
    来自天眼查/企查查等权威工商数据源
    """
    # 核心标识
    company_name: str                  # 公司全称
    unified_credit_code: str = ""      # 统一社会信用代码
    registration_number: str = ""      # 注册号

    # 基本信息
    legal_representative: str = ""    # 法定代表人
    registered_capital: str = ""      # 注册资本
    paid_in_capital: str = ""        # 实缴资本
    establishment_date: str = ""      # 成立日期
    business_term_start: str = ""     # 营业期限开始
    business_term_end: str = ""       # 营业期限结束
    company_status: str = ""          # 企业状态（存续/吊销/注销等）
    company_type: str = ""           # 企业类型

    # 地址信息
    registered_address: str = ""      # 注册地址
    business_address: str = ""        # 经营地址

    # 业务范围
    business_scope: str = ""          # 经营范围

    # 股东信息（简要）
    shareholders: List[Dict] = field(default_factory=list)  # [{name, capital, percentage}]

    # 关联数据
    branches_count: int = 0          # 分公司数量
    lawsuits_count: int = 0           # 涉诉数量

    # 元数据
    source: DataSource = DataSource.MOCK
    fetch_time: str = ""
    is_valid: bool = True             # 是否有效查询
    error_message: str = ""          # 错误信息（如果查询失败）


@dataclass
class SentimentItem:
    """
    舆情数据条目（第二层）
    来自网络搜索的员工评价、薪资爆料等
    """
    id: str = ""
    title: str = ""                   # 标题
    summary: str = ""                 # 摘要
    content: str = ""                 # 完整内容
    source: DataSource = DataSource.MOCK
    source_name: str = ""             # 来源名称（如"脉脉"、"知乎"）
    url: str = ""                     # 原文链接
    author: str = ""                  # 作者
    publish_date: str = ""            # 发布日期
    category: str = ""                # 分类（评价/薪资/裁员/上市等）

    # 情感分析
    sentiment: str = ""               # 情感倾向（positive/negative/neutral）
    sentiment_score: float = 0.0      # 情感得分（-1到1）

    # 置信度
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    confidence_note: str = ""         # 置信度说明

    # 提取的关键信息
    mentioned_salary: str = ""        # 提及的薪资
    mentioned_benefits: List[str] = field(default_factory=list)
    mentioned_pros: List[str] = field(default_factory=list)
    mentioned_cons: List[str] = field(default_factory=list)


@dataclass
class RiskItem:
    """
    风险数据条目（第三层）
    来自裁判文书网、启信宝等
    """
    id: str = ""
    case_type: str = ""               # 案件类型
    case_number: str = ""             # 案号
    title: str = ""                   # 标题
    summary: str = ""                 # 摘要
    content: str = ""                 # 详细内容

    # 当事人
    plaintiff: str = ""               # 原告
    defendant: str = ""               # 被告

    # 判决信息
    judgment_date: str = ""           # 判决日期
    judgment_amount: str = ""          # 判决金额
    judgment_result: str = ""         # 判决结果

    # 风险等级
    risk_level: str = ""              # 风险等级（高/中/低）
    risk_category: str = ""            # 风险类别

    # 来源
    source: DataSource = DataSource.MOCK
    source_name: str = ""
    url: str = ""                     # 原文链接

    # 元数据
    fetch_time: str = ""


@dataclass
class CompanyReport:
    """
    统一报告DTO - 多源数据协同结果
    包含三层API数据、冲突检测结果、AI矛盾点提取
    """
    # 原始查询
    original_query: str = ""          # 用户原始输入
    normalized_name: str = ""         # 标准化后的公司名称
    search_timestamp: str = ""

    # 第一层：工商铁证
    entity: Optional[EntityInfo] = None

    # 第二层：网络舆情
    sentiments: List[SentimentItem] = field(default_factory=list)

    # 第三层：司法风险
    risks: List[RiskItem] = field(default_factory=list)

    # 冲突检测与仲裁
    conflicts: List[ConflictItem] = field(default_factory=list)

    # 各层API状态
    api_status: Dict[str, str] = field(default_factory=dict)
    # {
    #     "entity": "success" | "failed" | "timeout" | "not_found",
    #     "sentiments": "success" | "failed" | "timeout" | "partial",
    #     "risks": "success" | "failed" | "timeout" | "not_found"
    # }

    # 错误信息
    errors: List[str] = field(default_factory=list)

    # 统计信息
    total_sentiment_count: int = 0
    total_risk_count: int = 0

    # 是否终止后续搜索（实体校验失败时）
    terminated: bool = False
    termination_reason: str = ""


@dataclass
class SearchQuery:
    """搜索查询构建器"""
    company_name: str                 # 公司全称（标准化后）
    unified_credit_code: str = ""     # 统一社会信用代码
    search_suffixes: List[str] = field(
        default_factory=lambda: [
            "员工评价",
            "工资薪资",
            "裁员优化",
            "上市融资",
            "企业文化",
            "面试经验"
        ]
    )

    def build_queries(self) -> List[str]:
        """构建搜索关键词列表"""
        queries = []
        for suffix in self.search_suffixes:
            queries.append(f"{self.company_name} {suffix}")
        return queries


@dataclass
class APIResponse:
    """统一API响应格式"""
    success: bool
    data: Any = None
    error: str = ""
    source: DataSource = DataSource.MOCK
    fetch_time: str = ""
    cached: bool = False
    cache_key: str = ""

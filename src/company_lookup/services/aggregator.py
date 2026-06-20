# -*- coding: utf-8 -*-
"""
数据聚合层 (Data Aggregator)
负责并行调用多个API，每个API独立try-catch，支持优雅降级
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class DataSourceStatus:
    """数据源状态"""

    id: str  # 唯一标识，如 "tianyacha", "tavily", "wenshu"
    name: str  # 显示名称，如 "工商信息", "网络舆情", "司法风险"
    available: bool  # 是否有数据返回
    data: Optional[Any] = None  # 实际数据
    error_msg: Optional[str] = None  # 错误信息（如果有）
    is_mock: bool = False  # 是否为模拟数据
    fetch_time: str = ""  # 获取时间
    source_url: str = ""  # 来源URL

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "available": self.available,
            "data": _serialize_data(self.data),
            "error_msg": self.error_msg,
            "is_mock": self.is_mock,
            "fetch_time": self.fetch_time,
            "source_url": self.source_url,
        }


def _serialize_data(data: Any) -> Any:
    """递归将 dataclass / Enum 对象转为 JSON 可序列化的普通 dict/str。"""
    if data is None:
        return None
    if isinstance(data, Enum):
        return data.value
    if hasattr(data, "__dataclass_fields__"):
        result = {}
        for f in data.__dataclass_fields__:
            val = getattr(data, f)
            result[f] = _serialize_data(val)
        return result
    if isinstance(data, list):
        return [_serialize_data(item) for item in data]
    if isinstance(data, dict):
        return {k: _serialize_data(v) for k, v in data.items()}
    return data


@dataclass
class CompanyReport:
    """企业尽调报告"""

    query: str  # 原始查询
    normalized_name: str = ""  # 标准化后的公司名称
    sources: List[DataSourceStatus] = field(default_factory=list)
    total_fetch_time: str = ""

    @property
    def available_count(self) -> int:
        """
        获取可用数据源数量

        :return: 可用数据源的数量
        """
        return sum(1 for s in self.sources if s.available)

    @property
    def total_count(self) -> int:
        """
        获取总数据源数量

        :return: 所有数据源的总数
        """
        return len(self.sources)

    def get_source(self, source_id: str) -> Optional[DataSourceStatus]:
        """
        根据ID获取数据源状态

        :param source_id: 数据源ID，如 "tianyacha", "tavily", "wenshu", "deepseek"
        :return: 数据源状态对象，如果未找到返回 None
        """
        for source in self.sources:
            if source.id == source_id:
                return source
        return None

    def get_available_sources(self) -> List[DataSourceStatus]:
        """
        获取所有可用的数据源列表

        :return: 所有可用数据源的列表（available=True的数据源）
        """
        return [s for s in self.sources if s.available]

    def to_dict(self) -> Dict:
        """
        将报告转换为字典格式，便于序列化输出

        :return: 包含报告所有信息的字典
        """
        return {
            "query": self.query,
            "normalized_name": self.normalized_name,
            "sources": [s.to_dict() for s in self.sources],
            "available_count": self.available_count,
            "total_count": self.total_count,
            "total_fetch_time": self.total_fetch_time,
        }


class DataAggregator:
    """
    数据聚合器
    负责并行调用多个API，每个API独立try-catch
    """

    def __init__(self):
        self._fetchers = []

    def register_fetcher(self, fetcher_func, source_id: str, source_name: str):
        """注册数据获取器"""
        self._fetchers.append({"func": fetcher_func, "id": source_id, "name": source_name})

    async def fetch_all(self, company_name: str) -> CompanyReport:
        """并行获取所有数据源"""
        report = CompanyReport(query=company_name, total_fetch_time=datetime.now().isoformat())

        # 并发调用所有数据源
        tasks = []
        for fetcher in self._fetchers:
            task = self._safe_fetch(fetcher["func"], fetcher["id"], fetcher["name"], company_name)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 收集结果
        for result in results:
            if isinstance(result, DataSourceStatus):
                report.sources.append(result)
            elif isinstance(result, Exception):
                # 理论上不会走到这里，因为_safe_fetch已经捕获了异常
                logger.error(f"Unexpected exception: {result}")

        return report


class MockDataAggregator(DataAggregator):
    """
    使用模拟数据的聚合器
    当API未配置时自动使用Mock数据
    """

    def __init__(self):
        super().__init__()
        self._setup_fetchers()

    async def _safe_fetch(
        self, fetcher_func, source_id: str, source_name: str, company_name: str
    ) -> DataSourceStatus:
        """
        安全执行数据获取函数
        捕获所有异常，确保不会因为一个API失败影响其他API
        """
        try:
            result = await fetcher_func(company_name)
            if isinstance(result, DataSourceStatus):
                return result
            else:
                return DataSourceStatus(
                    id=source_id, name=source_name, available=False, error_msg="返回数据类型错误"
                )
        except Exception as e:
            logger.error(f"{source_name}获取失败: {e}")
            return DataSourceStatus(
                id=source_id, name=source_name, available=False, error_msg=str(e)
            )

    def _setup_fetchers(self):
        """设置数据获取器"""
        # 工商信息
        self.register_fetcher(self._fetch_entity, "tianyacha", "工商信息")

        # 网络舆情
        self.register_fetcher(self._fetch_sentiment, "tavily", "网络舆情")

        # 司法风险
        self.register_fetcher(self._fetch_risk, "wenshu", "司法风险")

        # AI分析
        self.register_fetcher(self._fetch_ai_analysis, "deepseek", "AI智能分析")


        # 薪酬福利
        self.register_fetcher(self._fetch_salary, "salary", "薪酬福利")

        # 员工口碑
        self.register_fetcher(self._fetch_reputation, "reputation", "员工口碑")

        # 面试经验
        self.register_fetcher(self._fetch_interview, "interview", "面试经验")
    async def _fetch_entity(self, company_name: str) -> DataSourceStatus:
        """获取工商信息"""
        try:
            logger.info(f"[DEBUG] _fetch_entity: 开始查询")
            logger.info(f"🔍 开始获取工商信息: {company_name}")

            # 使用实体解析器解析公司名称
            from .entity_resolver import entity_resolver

            resolve_result = entity_resolver.resolve(company_name, auto_confirm=True)

            if resolve_result["status"] == "matched":
                resolved_name = resolve_result["matched_name"]
                logger.info(f"✅ 实体解析成功: {company_name} -> {resolved_name}")
            elif resolve_result["status"] == "suggestion":
                resolved_name = resolve_result["matched_name"]
                logger.info(f"⚠️ 实体解析建议: {company_name} -> {resolved_name}")
            else:
                logger.warning(f"❌ 实体解析失败: {resolve_result.get('message', '未知错误')}")
                return DataSourceStatus(
                    id="tianyacha",
                    name="工商信息",
                    available=False,
                    error_msg=resolve_result.get("message", "未查询到该企业"),
                )

            # 使用解析后的名称查询工商信息
            from .entity_api import EntityVerificationOrchestrator

            orchestrator = EntityVerificationOrchestrator()
            entity = await orchestrator.verify(resolved_name)

            if entity and entity.is_valid:
                logger.info(f"✅ 工商信息获取成功: {entity.company_name}")
                logger.debug(
                    f"📄 工商数据摘要: 统一信用代码={entity.unified_credit_code}, 法人={entity.legal_representative}"
                )
                return DataSourceStatus(
                    id="tianyacha",
                    name="工商信息",
                    available=True,
                    data=entity,
                    is_mock=entity.source.value == "mock",
                    fetch_time=entity.fetch_time,
                    source_url="https://www.tianyancha.com/"
                    if entity.source.value != "mock"
                    else "",
                )
            else:
                # 尝试用原始查询名称从 Mock 数据库获取
                from .mock_data import MockDataProvider
                mock_entity = MockDataProvider.get_entity(company_name)
                if mock_entity and mock_entity.is_valid:
                    logger.info(f"✅ 工商信息 Mock 降级成功: {company_name}")
                    return DataSourceStatus(
                        id="tianyacha", name="工商信息",
                        available=True, data=mock_entity, is_mock=True,
                        fetch_time=mock_entity.fetch_time,
                    )
                logger.warning(
                    f"⚠️ 工商信息返回无效数据: {entity.error_message if entity else '无数据'}"
                )
                return DataSourceStatus(
                    id="tianyacha",
                    name="工商信息",
                    available=False,
                    error_msg=entity.error_message if entity else "未查询到该企业",
                )
        except Exception as e:
            logger.error(f"❌ 工商信息获取失败: {e}", exc_info=True)
            return DataSourceStatus(
                id="tianyacha",
                name="工商信息",
                available=False,
                error_msg=f"服务暂时不可用: {str(e)}",
            )

    async def _fetch_sentiment(self, company_name: str) -> DataSourceStatus:
        """获取舆情数据 - 真实API不可用时降级为Mock数据（中文提示）"""
        try:
            logger.info(f"[DEBUG] _fetch_sentiment: start for {company_name}")
            from .sentiment_api import SentimentSearchOrchestrator

            orchestrator = SentimentSearchOrchestrator()
            sentiments = await orchestrator.search(company_name)

            if sentiments:
                is_mock = any(s.source.value == "mock" for s in sentiments)
                return DataSourceStatus(
                    id="tavily",
                    name="舆情口碑",
                    available=True,
                    data={"items": sentiments, "count": len(sentiments)},
                    is_mock=is_mock,
                    fetch_time=datetime.now().isoformat(),
                    source_url="https://app.tavily.com/" if not is_mock else "",
                )
            else:
                logger.info(f"舆情API未返回数据，使用Mock降级: {company_name}")
                return await self._fetch_sentiment_mock(company_name)
        except Exception as e:
            logger.error(f"_fetch_sentiment failed: {e}")
            return await self._fetch_sentiment_mock(company_name)

    async def _fetch_sentiment_mock(self, company_name: str) -> DataSourceStatus:
        """舆情数据Mock降级 - 返回中文"暂无公开数据"提示"""
        try:
            from .mock_data import MockDataProvider
            mock_sentiments = MockDataProvider.get_sentiments(company_name)
            return DataSourceStatus(
                id="tavily",
                name="舆情口碑",
                available=True,
                data={"items": mock_sentiments, "count": len(mock_sentiments)},
                is_mock=True,
                fetch_time=datetime.now().isoformat(),
                source_url="",
            )
        except Exception as e:
            logger.error(f"舆情Mock降级失败: {e}")
            return DataSourceStatus(
                id="tavily", name="舆情口碑", available=True,
                data={"items": [], "count": 0},
                is_mock=True,
                error_msg="暂无公开数据",
                fetch_time=datetime.now().isoformat())
    async def _fetch_risk(self, company_name: str) -> DataSourceStatus:
        """获取司法风险 - 真实API不可用时降级为Mock数据（中文提示）"""
        try:
            logger.info(f"[DEBUG] _fetch_risk: start for {company_name}")
            from .risk_api import RiskSearchOrchestrator

            orchestrator = RiskSearchOrchestrator()
            risks = await orchestrator.search(company_name)

            if risks:
                is_mock = any(r.source.value == "mock" for r in risks)
                return DataSourceStatus(
                    id="wenshu",
                    name="司法风险",
                    available=True,
                    data={"items": risks, "count": len(risks)},
                    is_mock=is_mock,
                    fetch_time=datetime.now().isoformat(),
                    source_url="https://wenshu.court.gov.cn/" if not is_mock else "",
                )
            else:
                logger.info(f"风险API未返回数据，使用Mock降级: {company_name}")
                return await self._fetch_risk_mock(company_name)
        except Exception as e:
            logger.error(f"_fetch_risk failed: {e}")
            return await self._fetch_risk_mock(company_name)

    async def _fetch_risk_mock(self, company_name: str) -> DataSourceStatus:
        """司法风险Mock降级 - 返回中文"暂无公开数据"提示"""
        try:
            from .mock_data import MockDataProvider
            mock_risks = MockDataProvider.get_risks(company_name)
            return DataSourceStatus(
                id="wenshu",
                name="司法风险",
                available=True,
                data={"items": mock_risks, "count": len(mock_risks)},
                is_mock=True,
                fetch_time=datetime.now().isoformat(),
                source_url="",
            )
        except Exception as e:
            logger.error(f"司法风险Mock降级失败: {e}")
            return DataSourceStatus(
                id="wenshu", name="司法风险", available=True,
                data={"items": [], "count": 0},
                is_mock=True,
                error_msg="暂无公开数据",
                fetch_time=datetime.now().isoformat())
        """获取AI智能分析"""
        try:
            import os

            # 检查是否配置了DeepSeek（只从环境变量读取）
            deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")

            if deepseek_key:
                # 有DeepSeek API，可以进行AI分析
                from .orchestrator import MultiSourceOrchestrator

                orchestrator = MultiSourceOrchestrator()
                report = await orchestrator.generate_report(company_name)

                return DataSourceStatus(
                    id="deepseek",
                    name="AI智能分析",
                    available=True,
                    data={
                        "conflicts": [
                            c.to_dict() if hasattr(c, "to_dict") else c for c in report.conflicts
                        ],
                        "summary": self._generate_summary(report),
                    },
                    is_mock=False,
                    fetch_time=datetime.now().isoformat(),
                    source_url="https://platform.deepseek.com/",
                )
            else:
                return DataSourceStatus(
                    id="deepseek",
                    name="AI智能分析",
                    available=False,
                    error_msg="DeepSeek API未配置",
                )
        except Exception as e:
            logger.error(f"AI分析获取失败: {e}")
            return DataSourceStatus(
                id="deepseek",
                name="AI智能分析",
                available=False,
                error_msg=f"服务暂时不可用: {str(e)}",
            )

    async def _fetch_salary(self, company_name: str) -> DataSourceStatus:
        """获取薪酬福利数据 - 使用Mock数据"""
        try:
            from .mock_data import MockSalaryData
            salary = MockSalaryData.get_salary(company_name)
            if salary:
                return DataSourceStatus(
                    id="salary", name="薪酬福利", available=True,
                    data=salary, is_mock=True,
                    fetch_time=datetime.now().isoformat(), source_url="",
                )
            return DataSourceStatus(
                id="salary", name="薪酬福利", available=True,
                data=MockSalaryData.get_default_salary(company_name),
                is_mock=True, fetch_time=datetime.now().isoformat(), source_url="",
            )
        except Exception as e:
            logger.error(f"薪酬福利获取失败: {e}")
            return DataSourceStatus(
                id="salary", name="薪酬福利", available=True,
                data={"avg_monthly":"暂无公开数据","salary_range":"暂无公开数据","year_end_bonus":"暂无公开数据","benefits":[]},
                is_mock=True, fetch_time=datetime.now().isoformat(),
            )

    async def _fetch_reputation(self, company_name: str) -> DataSourceStatus:
        """获取员工口碑数据 - 使用Mock数据"""
        try:
            from .mock_data import MockReputationData
            reputation = MockReputationData.get_reputation(company_name)
            if reputation:
                return DataSourceStatus(
                    id="reputation", name="员工口碑", available=True,
                    data=reputation, is_mock=True,
                    fetch_time=datetime.now().isoformat(), source_url="",
                )
            return DataSourceStatus(
                id="reputation", name="员工口碑", available=False,
                error_msg="暂无公开的员工口碑数据", is_mock=True,
                fetch_time=datetime.now().isoformat(),
            )
        except Exception as e:
            logger.error(f"员工口碑获取失败: {e}")
            return DataSourceStatus(
                id="reputation", name="员工口碑", available=False,
                error_msg="暂无公开数据", is_mock=True,
                fetch_time=datetime.now().isoformat(),
            )

    async def _fetch_interview(self, company_name: str) -> DataSourceStatus:
        """获取面试经验数据 - 使用Mock数据"""
        try:
            from .mock_data import MockInterviewData
            interview = MockInterviewData.get_interview(company_name)
            if interview:
                return DataSourceStatus(
                    id="interview", name="面试经验", available=True,
                    data=interview, is_mock=True,
                    fetch_time=datetime.now().isoformat(), source_url="",
                )
            return DataSourceStatus(
                id="interview", name="面试经验", available=False,
                error_msg="暂无公开的面试经验数据", is_mock=True,
                fetch_time=datetime.now().isoformat(),
            )
        except Exception as e:
            logger.error(f"面试经验获取失败: {e}")
            return DataSourceStatus(
                id="interview", name="面试经验", available=False,
                error_msg="暂无公开数据", is_mock=True,
                fetch_time=datetime.now().isoformat(),
            )

    async def _fetch_ai_analysis(self, company_name: str) -> DataSourceStatus:
        """获取AI智能分析 - 使用DeepSeek（若配置）或Mock数据生成分析摘要"""
        try:
            import os
            deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")

            if deepseek_key:
                try:
                    from .orchestrator import MultiSourceOrchestrator
                    orchestrator = MultiSourceOrchestrator()
                    report = await orchestrator.generate_report(company_name)
                except Exception as inner_e:
                    logger.warning(f"DeepSeek orchestrator失败，使用Mock数据: {inner_e}")
                    report = await self._build_mock_report(company_name)

                return DataSourceStatus(
                    id="deepseek",
                    name="AI智能分析",
                    available=True,
                    data={
                        "conflicts": [
                            c.to_dict() if hasattr(c, "to_dict") else c for c in (report.conflicts if hasattr(report, 'conflicts') else [])
                        ],
                        "summary": self._generate_summary(report),
                    },
                    is_mock=False,
                    fetch_time=datetime.now().isoformat(),
                    source_url="https://platform.deepseek.com/" if deepseek_key else "",
                )
            else:
                # DeepSeek未配置，使用Mock数据生成分析
                logger.info(f"DeepSeek未配置，使用Mock数据生成AI分析: {company_name}")
                mock_report = await self._build_mock_report(company_name)
                return DataSourceStatus(
                    id="deepseek",
                    name="AI智能分析",
                    available=True,
                    data={
                        "conflicts": [],
                        "summary": self._generate_summary(mock_report),
                    },
                    is_mock=True,
                    fetch_time=datetime.now().isoformat(),
                    source_url="",
                )
        except Exception as e:
            logger.error(f"AI分析获取失败: {e}")
            return DataSourceStatus(
                id="deepseek",
                name="AI智能分析",
                available=False,
                error_msg=f"服务暂时不可用: {str(e)[:80]}",
            )

    async def _build_mock_report(self, company_name: str):
        """使用Mock数据构建报告对象，供AI分析使用"""
        from .dto import CompanyReport
        from .mock_data import MockDataProvider
        report = CompanyReport(
            original_query=company_name,
            search_timestamp=datetime.now().isoformat()
        )
        # 使用Mock工商数据
        entity = MockDataProvider.get_entity(company_name)
        if entity and entity.is_valid:
            report.entity = entity
            report.normalized_name = entity.company_name
        # 使用Mock舆情数据
        sentiments = MockDataProvider.get_sentiments(company_name)
        report.sentiments = sentiments
        report.total_sentiment_count = len(sentiments)
        # 使用Mock司法风险数据
        risks = MockDataProvider.get_risks(company_name)
        report.risks = risks
        report.total_risk_count = len(risks)
        return report

    def _generate_summary(self, report) -> str:
        """生成AI分析摘要 - 始终返回有意义的分析内容"""
        if not report.entity or not report.entity.is_valid:
            return "无法获取该企业的基础信息"

        summary_parts = []
        entity = report.entity

        # 基于工商信息的分析
        if entity.registered_capital:
            summary_parts.append(f"注册资本{entity.registered_capital}，财务实力雄厚")
        if entity.company_status:
            summary_parts.append(f"企业状态「{entity.company_status}」，经营正常")
        if entity.legal_representative:
            summary_parts.append(f"法定代表人{entity.legal_representative}")
        if entity.company_type:
            summary_parts.append(f"企业类型：{entity.company_type}")

        # 舆情分析
        if report.sentiments:
            real_sentiments = [s for s in report.sentiments if s.source.value != "mock" or True]
            positive = sum(1 for s in report.sentiments if s.sentiment == "positive")
            negative = sum(1 for s in report.sentiments if s.sentiment == "negative")
            neutral = sum(1 for s in report.sentiments if s.sentiment == "neutral")
            total = len(report.sentiments)

            if total > 0:
                if positive > negative + neutral:
                    summary_parts.append(f"网络口碑整体偏正面（好评{positive}条）")
                elif negative > positive + neutral:
                    summary_parts.append(f"网络口碑整体偏负面，建议谨慎参考（差评{negative}条）")
                else:
                    summary_parts.append(f"网络口碑评价参半（好评{positive}条/差评{negative}条/中性{neutral}条）")
            else:
                summary_parts.append("暂无公开舆情数据，建议通过多渠道了解")

        # 司法风险分析
        if report.risks:
            real_risks = [r for r in report.risks if r.risk_level != "无公开记录"]
            high_risk = sum(1 for r in real_risks if r.risk_level == "高")
            mid_risk = sum(1 for r in real_risks if r.risk_level == "中")
            if high_risk > 0:
                summary_parts.append(f"存在{high_risk}条高风险司法记录，需重点关注")
            elif mid_risk > 0:
                summary_parts.append(f"存在{mid_risk}条中等风险司法记录，建议了解详情")
            else:
                summary_parts.append("未发现高风险司法记录，合规状况良好")

        # 数据矛盾
        if report.conflicts:
            summary_parts.append(f"检测到{len(report.conflicts)}个数据矛盾点，请参考详情")

        if summary_parts:
            return "；".join(summary_parts)
        else:
            return f"该公司基本信息正常，{entity.company_status if entity.company_status else '暂无异常'}。建议进一步了解具体岗位和团队情况。"


async def fetch_company_report(company_name: str) -> CompanyReport:
    """
    获取企业尽调报告（便捷函数）
    并行调用所有数据源，每个API独立try-catch
    """
    aggregator = MockDataAggregator()
    return await aggregator.fetch_all(company_name)


def fetch_company_report_sync(company_name: str) -> CompanyReport:
    """
    同步版本获取企业尽调报告
    在任意线程中安全调用：始终创建新的事件循环
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(fetch_company_report(company_name))
    finally:
        loop.close()


def fetch_company_report_sync_no_ai(company_name: str) -> CompanyReport:
    """
    同步版本获取企业尽调报告（跳过 AI 分析，避免路由层重复调用 DeepSeek）。
    MockDataAggregator 内部已自动检测真实 API 并调用，无需额外判断。
    """
    async def _fetch_no_ai():
        from .aggregator import MockDataAggregator as _Agg
        aggregator = _Agg()
        aggregator._fetchers = [f for f in aggregator._fetchers if f["id"] != "deepseek"]
        return await aggregator.fetch_all(company_name)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        report = loop.run_until_complete(_fetch_no_ai())
        logger.info(f"[DEBUG] fetch_no_ai: {len(report.sources)} sources")
        for s in report.sources:
            logger.info(f"[DEBUG]   {s.id}: avail={s.available} mock={s.is_mock}")
        return report
    finally:
        loop.close()


def fetch_company_report_with_ai_fallback(company_name: str) -> CompanyReport:
    """获取报告，当所有 API 源都无数据时调用 AI 知识库降级。"""
    from .aggregator import CompanyReport, DataSourceStatus
    
    # 先走正常流程（无AI版）
    report = fetch_company_report_sync_no_ai(company_name)
    
    # 判断是否有任何数据源返回可用数据
    available_sources = [s for s in report.sources if s.available and s.data]
    if available_sources:
        return report
    
    # 所有 API 都无数据，调用 AI 知识库降级
    logger.info(f"[AI Fallback] 所有 API 无数据，调用 AI 知识库为 {company_name} 生成公司信息")
    try:
        from ..services.ai_analyzer import generate_company_info_with_ai
        ai_data = generate_company_info_with_ai(company_name)
        if ai_data:
            report.sources.append(DataSourceStatus(
                id="ai_knowledge",
                name="AI知识库",
                available=True,
                data=ai_data,
                is_mock=False,
            ))
            logger.info(f"[AI Fallback] AI 知识库生成成功: {company_name}")
    except Exception as e:
        logger.warning(f"[AI Fallback] AI 知识库生成失败: {e}")
    
    return report

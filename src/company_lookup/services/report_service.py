# -*- coding: utf-8 -*-
"""
统一报告服务
对外暴露的简单接口，内部处理多源协同逻辑
"""

import asyncio
from typing import Optional

from .dto import CompanyReport
from .orchestrator import MultiSourceOrchestrator
from .mock_data import MockDataProvider


class ReportService:
    """
    统一报告服务

    使用示例:
    ```python
    from services import ReportService

    service = ReportService()
    report = await service.generate_report("腾讯")

    # 检查是否终止（实体校验失败）
    if report.terminated:
        try:
            print(f"查询终止: {report.termination_reason}")
        except Exception:
            pass
        return

    # 展示三层数据
    try:
        print(f"公司名称: {report.entity.company_name}")
    except Exception:
        pass
    try:
        print(f"舆情数量: {report.total_sentiment_count}")
    except Exception:
        pass
    try:
        print(f"风险数量: {report.total_risk_count}")
    except Exception:
        pass

    # 展示矛盾点
    for conflict in report.conflicts:
        try:
            print(f"矛盾: {conflict.description}")
        except Exception:
            pass
    ```
    """

    def __init__(self, use_mock_if_unavailable: bool = True):
        """
        :param use_mock_if_unavailable: API不可用时是否使用Mock数据
        """
        self.use_mock_if_unavailable = use_mock_if_unavailable
        self._orchestrator = MultiSourceOrchestrator()

    async def generate_report(self, company_name: str) -> CompanyReport:
        """
        生成企业尽调报告

        :param company_name: 公司名称（支持简称、关键词）
        :return: CompanyReport 统一报告对象
        """
        try:
            report = await self._orchestrator.generate_report(company_name)

            # 如果使用了Mock数据，在报告中标注
            if self.use_mock_if_unavailable and MockDataProvider.is_mock_mode():
                if report.entity and report.entity.source.value == "mock":
                    report.errors.append(
                        "【系统提示】当前使用Mock数据，请配置真实API以获取准确信息"
                    )

            return report

        except Exception as e:
            # 异常处理：返回错误报告
            return CompanyReport(
                original_query=company_name,
                terminated=True,
                termination_reason=f"系统异常: {str(e)}",
                errors=[f"generate_report异常: {str(e)}"],
            )

    def generate_report_sync(self, company_name: str) -> CompanyReport:
        """
        同步版本：在同步环境中安全调用异步的 generate_report。
        【修复】原实现用了 await 但方法名是 sync，导致在同步上下文中返回 coroutine 而非结果。
        现改为正确创建事件循环并 run_until_complete。
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.generate_report(company_name))
        finally:
            loop.close()

    def get_api_status(self) -> dict:
        """
        获取各API的配置状态

        :return: API状态字典
        """
        import os
        from .entity_api import EntityVerificationOrchestrator
        from .sentiment_api import SentimentSearchOrchestrator
        from .risk_api import RiskSearchOrchestrator

        # 检查DeepSeek API配置（只从环境变量读取）
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
        deepseek_configured = bool(deepseek_key)
        deepseek_source = "环境变量" if deepseek_configured else "未配置"

        return {
            "entity_apis": {
                "tianyacha": {
                    **EntityVerificationOrchestrator().clients[0].get_status(),
                    "apply_url": "https://open.tianyancha.com/",
                },
                "qichacha": {
                    **EntityVerificationOrchestrator().clients[1].get_status(),
                    "apply_url": "https://www.qcc.com/",
                },
            },
            "sentiment_apis": {
                "tavily": {
                    **SentimentSearchOrchestrator().clients[0].get_status(),
                    "apply_url": "https://app.tavily.com/",
                },
            },
            "risk_apis": {
                "qixinbao": {
                    **RiskSearchOrchestrator().clients[0].get_status(),
                    "apply_url": "https://www.qixin.com/",
                },
                "wenshu": {
                    **RiskSearchOrchestrator().clients[1].get_status(),
                    "apply_url": "https://wenshu.court.gov.cn/",
                },
            },
            "ai_apis": {
                "deepseek": {
                    "name": "DeepSeek",
                    "source": "deepseek",
                    "configured": deepseek_configured,
                    "available": deepseek_configured,
                    "source_type": deepseek_source,
                    "apply_url": "https://platform.deepseek.com/",
                    "circuit_breaker": {"state": "closed", "failure_count": 0},
                }
            },
            "mock_mode": MockDataProvider.is_mock_mode(),
        }

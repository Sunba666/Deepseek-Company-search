# -*- coding: utf-8 -*-
"""
第三层API：司法风险核查
支持中国裁判文书网、启信宝等
"""

import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_client import AsyncBaseAPIClient
from .dto import (
    DataSource, APIResponse, RiskItem
)


class WenShuClient(AsyncBaseAPIClient):
    """
    中国裁判文书网 API 客户端
    注意：裁判文书网官方未提供公开API，这里使用公开接口模拟
    实际生产环境需要通过爬虫或官方合作渠道获取数据
    """

    def __init__(self):
        super().__init__(
            name="裁判文书网",
            source=DataSource.WENSHU,
            api_key=None,  # 公开接口无需KEY
            base_url="https://wenshu.court.gov.cn",
            timeout=30
        )

    async def search(self, company_name: str, **kwargs) -> APIResponse:
        """
        搜索企业涉诉信息
        注意：裁判文书网需要登录才能获取完整数据
        此接口为公开查询接口，可能受限
        """
        # 裁判文书网公开接口查询（有限制）
        # 实际使用建议通过其他数据源或合作渠道

        try:
            # 尝试公开查询接口
            response = await self._async_request(
                method="GET",
                url="/website/JudgmentDetail/Index4.do",
                params={
                    "caseinfo": "undefined",
                    "queryTxt": company_name,
                    "PageIndex": 1,
                    "PageSize": 10
                }
            )

            if response.success:
                items = self._parse_response(response.data, company_name)
                return APIResponse(
                    success=True,
                    data=items,
                    source=self.source,
                    fetch_time=response.fetch_time
                )

            # 接口受限时的处理
            return APIResponse(
                success=False,
                error="裁判文书网公开接口访问受限，建议使用启信宝等其他数据源",
                source=self.source
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=f"裁判文书网查询失败: {str(e)}",
                source=self.source
            )

    def _parse_response(self, data: Any, company_name: str) -> List[RiskItem]:
        """解析裁判文书网响应"""
        items = []

        if not isinstance(data, dict):
            return items

        # 裁判文书网返回结构解析（如果有数据）
        try:
            case_list = data.get("data", [])
            for case in case_list:
                item = RiskItem(
                    id=str(uuid.uuid4()),
                    case_type=case.get("caseType", ""),
                    case_number=case.get("caseNo", ""),
                    title=case.get("caseName", ""),
                    summary=case.get("caseAbstract", ""),
                    plaintiff=case.get("pname", ""),
                    defendant=case.get("rname", ""),
                    judgment_date=case.get("judgmentDate", ""),
                    judgment_amount=case.get("money", ""),
                    risk_level=self._assess_risk_level(case),
                    risk_category=self._categorize_case(case.get("caseType", "")),
                    source=DataSource.WENSHU,
                    source_name="中国裁判文书网",
                    url=f"https://wenshu.court.gov.cn/website/parse/rest/page/1?json.cookie=&conditions=searchYear=&queryJson=",
                    fetch_time=datetime.now().isoformat()
                )
                items.append(item)
        except Exception:
            pass

        return items

    def _assess_risk_level(self, case: Dict) -> str:
        """评估风险等级"""
        case_type = case.get("caseType", "").lower()

        # 高风险类型
        high_risk_types = ["执行", "失信", "限消"]
        medium_risk_types = ["劳动", "人事", "合同"]

        if any(t in case_type for t in high_risk_types):
            return "高"
        elif any(t in case_type for t in medium_risk_types):
            return "中"
        return "低"

    def _categorize_case(self, case_type: str) -> str:
        """案件分类"""
        mapping = {
            "民事": "民事纠纷",
            "刑事": "刑事案件",
            "行政": "行政案件",
            "执行": "强制执行",
            "赔偿": "国家赔偿",
            "劳动": "劳动争议",
            "人事": "人事争议"
        }

        for key, value in mapping.items():
            if key in case_type:
                return value
        return "其他"


class QiXinBaoClient(AsyncBaseAPIClient):
    """
    启信宝 API 客户端
    启信宝提供企业风险信息查询服务
    """

    def __init__(self):
        super().__init__(
            name="启信宝",
            source=DataSource.QIXINBAO,
            api_key=os.getenv("QIXINBAO_API_KEY"),
            base_url="https://api.qixin.com/api/v2",
            timeout=30
        )

    async def search(self, company_name: str, **kwargs) -> APIResponse:
        """
        搜索企业风险信息
        """
        if not self.is_configured():
            return APIResponse(
                success=False,
                error="启信宝API未配置或已熔断",
                source=self.source
            )

        try:
            # 启信宝公开查询接口
            response = await self._async_request(
                method="GET",
                url="/search/commercial",
                params={
                    "keyWord": company_name,
                    "pageSize": 10,
                    "pageNum": 1
                },
                headers={
                    "Authorization": self.api_key
                }
            )

            if response.success:
                items = self._parse_response(response.data, company_name)
                return APIResponse(
                    success=True,
                    data=items,
                    source=self.source,
                    fetch_time=response.fetch_time
                )
            return response

        except Exception as e:
            return APIResponse(
                success=False,
                error=f"启信宝查询失败: {str(e)}",
                source=self.source
            )

    def _parse_response(self, data: Dict, company_name: str) -> List[RiskItem]:
        """解析启信宝响应"""
        items = []

        try:
            # 根据启信宝实际返回结构调整
            company_list = data.get("result", {}).get("company_list", [])

            for company in company_list:
                # 提取风险信息
                risk_list = company.get("risk_list", [])

                for risk in risk_list:
                    item = RiskItem(
                        id=str(uuid.uuid4()),
                        case_type=risk.get("risk_type", ""),
                        case_number=risk.get("case_no", ""),
                        title=risk.get("risk_title", ""),
                        summary=risk.get("risk_summary", ""),
                        plaintiff=risk.get("plaintiff", ""),
                        defendant=risk.get("defendant", ""),
                        judgment_date=risk.get("pub_date", ""),
                        judgment_amount=risk.get("amount", ""),
                        risk_level=risk.get("risk_level", "中"),
                        risk_category=self._categorize_risk(risk.get("risk_type", "")),
                        source=DataSource.QIXINBAO,
                        source_name="启信宝",
                        url=risk.get("detail_url", ""),
                        fetch_time=datetime.now().isoformat()
                    )
                    items.append(item)

        except Exception:
            pass

        return items

    def _categorize_risk(self, risk_type: str) -> str:
        """风险分类"""
        mapping = {
            "被执行人": "强制执行",
            "失信被执行人": "失信惩戒",
            "行政处罚": "行政监管",
            "严重违法": "严重违法",
            "经营异常": "经营异常",
            "司法协助": "司法协助"
        }
        return mapping.get(risk_type, "其他风险")


class RiskSearchOrchestrator:
    """
    司法风险搜索调度器
    协调多个风险数据源
    """

    def __init__(self):
        self.clients = [
            QiXinBaoClient(),
            WenShuClient()
        ]

    async def search(self, company_name: str, unified_credit_code: str = "") -> List[RiskItem]:
        """
        执行司法风险搜索
        """
        all_items = []
        seen_ids = set()

        # 并发查询所有客户端
        import asyncio

        async def search_with_client(client):
            if client.is_available():
                response = await client.search(company_name)
                if response.success and response.data:
                    return response.data
            return []

        results = await asyncio.gather(
            *[search_with_client(client) for client in self.clients],
            return_exceptions=True
        )

        # 合并结果
        for result in results:
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, RiskItem) and item.id not in seen_ids:
                        seen_ids.add(item.id)
                        all_items.append(item)

        # 按风险等级和日期排序
        risk_order = {"高": 0, "中": 1, "低": 2}
        all_items.sort(
            key=lambda x: (risk_order.get(x.risk_level, 3), x.judgment_date or ""),
            reverse=False
        )

        return all_items[:20]  # 最多返回20条

# -*- coding: utf-8 -*-
"""
第一层API：工商信息验证
支持天眼查、企查查、高德POI等
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime

from .base_client import BaseAPIClient, AsyncBaseAPIClient
from .dto import (
    DataSource, APIResponse, EntityInfo,
    ConfidenceLevel
)


class TianYaChaClient(AsyncBaseAPIClient):
    """
    天眼查API客户端
    注意：天眼查官方API需要企业认证，具体接入方式需联系天眼查
    """

    def __init__(self):
        super().__init__(
            name="天眼查",
            source=DataSource.TIANYA_CHECK,
            api_key=os.getenv("TIANYACHA_API_KEY"),
            base_url="https://open.tianyancha.com/api/open",
            timeout=30
        )

    async def search(self, company_name: str, **kwargs) -> APIResponse:
        """
        搜索企业工商信息
        :param company_name: 公司名称
        :return: APIResponse with EntityInfo
        """
        if not self.is_configured():
            return APIResponse(
                success=False,
                error="天眼查API未配置或已熔断",
                source=self.source
            )

        try:
            response = await self._async_request(
                method="GET",
                url="/v4/baseinfo/getByName",
                params={
                    "name": company_name
                },
                headers={
                    "Authorization": self.api_key
                }
            )

            if response.success:
                data = self._parse_response(response.data, company_name)
                return APIResponse(
                    success=True,
                    data=data,
                    source=self.source,
                    fetch_time=response.fetch_time
                )
            return response

        except Exception as e:
            return APIResponse(
                success=False,
                error=f"天眼查查询失败: {str(e)}",
                source=self.source
            )

    def _parse_response(self, data: Dict, original_query: str) -> EntityInfo:
        """解析天眼查API响应"""
        company = data.get("data", {})
        return EntityInfo(
            company_name=company.get("name", original_query),
            unified_credit_code=company.get("creditCode", ""),
            registration_number=company.get("regNumber", ""),
            legal_representative=company.get("legalPersonName", ""),
            registered_capital=company.get("registeredCapital", ""),
            paid_in_capital=company.get("actualCapital", ""),
            establishment_date=company.get("establishtime", ""),
            company_status=company.get("businessStatus", ""),
            company_type=company.get("companyType", ""),
            registered_address=company.get("regLocation", ""),
            business_scope=company.get("businessScope", ""),
            source=DataSource.TIANYA_CHECK,
            fetch_time=datetime.now().isoformat(),
            is_valid=True
        )


class QiChaChaClient(AsyncBaseAPIClient):
    """
    企查查API客户端
    """

    def __init__(self):
        super().__init__(
            name="企查查",
            source=DataSource.QICHACHA,
            api_key=os.getenv("QICHACHA_API_KEY"),
            base_url="https://api.qcc.com/api",
            timeout=30
        )

    async def search(self, company_name: str, **kwargs) -> APIResponse:
        """
        搜索企业工商信息
        """
        if not self.is_configured():
            return APIResponse(
                success=False,
                error="企查查API未配置或已熔断",
                source=self.source
            )

        try:
            response = await self._async_request(
                method="GET",
                url="/entdetail/getByName",
                params={
                    "keyWord": company_name
                },
                headers={
                    "Token": self.api_key
                }
            )

            if response.success:
                data = self._parse_response(response.data, company_name)
                return APIResponse(
                    success=True,
                    data=data,
                    source=self.source,
                    fetch_time=response.fetch_time
                )
            return response

        except Exception as e:
            return APIResponse(
                success=False,
                error=f"企查查查询失败: {str(e)}",
                source=self.source
            )

    def _parse_response(self, data: Dict, original_query: str) -> EntityInfo:
        """解析企查查API响应"""
        company = data.get("Result", {})
        basic_info = company.get("BaseInfo", {})

        return EntityInfo(
            company_name=basic_info.get("Name", original_query),
            unified_credit_code=basic_info.get("CreditCode", ""),
            registration_number=basic_info.get("No", ""),
            legal_representative=basic_info.get("LegalPersonName", ""),
            registered_capital=basic_info.get("RegisteredCapital", ""),
            paid_in_capital=basic_info.get("ActualCapital", ""),
            establishment_date=basic_info.get("StartDate", ""),
            company_status=basic_info.get("BusinessStatus", ""),
            company_type=basic_info.get("CompanyType", ""),
            registered_address=basic_info.get("Address", ""),
            business_scope=basic_info.get("BusinessScope", ""),
            source=DataSource.QICHACHA,
            fetch_time=datetime.now().isoformat(),
            is_valid=True
        )


class AmapPOIClient(AsyncBaseAPIClient):
    """
    高德地图POI搜索API
    用于通过公司名称搜索获取标准地址和位置信息
    """

    def __init__(self):
        super().__init__(
            name="高德地图",
            source=DataSource.MOCK,  # 高德不属于企业数据源，这里仅作补充
            api_key=os.getenv("AMAP_API_KEY"),
            base_url="https://restapi.amap.com/v3",
            timeout=15
        )

    async def search(self, company_name: str, **kwargs) -> APIResponse:
        """
        搜索企业POI信息
        """
        if not self.is_configured():
            return APIResponse(
                success=False,
                error="高德API未配置",
                source=self.source
            )

        try:
            response = await self._async_request(
                method="GET",
                url="/place/text",
                params={
                    "key": self.api_key,
                    "keywords": company_name,
                    "types": "商务住宅|风景名胜|科教文化",
                    "city": "全国",
                    "offset": 1,
                    "extensions": "all"
                }
            )

            if response.success and response.data.get("pois"):
                poi = response.data["pois"][0]
                entity = EntityInfo(
                    company_name=poi.get("name", company_name),
                    business_address=poi.get("address", ""),
                    registered_address=poi.get("cityname", ""),
                    source=DataSource.MOCK,
                    fetch_time=datetime.now().isoformat(),
                    is_valid=True
                )
                return APIResponse(
                    success=True,
                    data=entity,
                    source=self.source,
                    fetch_time=response.fetch_time
                )

            return APIResponse(
                success=False,
                error="未找到相关位置信息",
                source=self.source
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=f"高德POI查询失败: {str(e)}",
                source=self.source
            )


class EntityVerificationOrchestrator:
    """
    实体验证调度器
    协调多个工商API，优先使用天眼查，失败则尝试企查查
    """

    def __init__(self):
        self.clients = [
            TianYaChaClient(),
            QiChaChaClient()
        ]

    async def verify(self, company_name: str) -> EntityInfo:
        """
        验证企业实体
        按优先级尝试各API，找到第一个有效结果即返回
        如果所有API都不可用，降级到Mock数据
        """
        import logging
        logger = logging.getLogger(__name__)
        for client in self.clients:
            if client.is_available():
                logger.info(f"[DEBUG] EntityVerification: 尝试 {client.name} (source={client.source.value})")
                response = await client.search(company_name)
                if response.success and response.data:
                    logger.info(f"[DEBUG] EntityVerification: {client.name} 返回成功")
                    return response.data
                else:
                    logger.info(f"[DEBUG] EntityVerification: {client.name} 返回失败: {response.error}")
            else:
                logger.info(f"[DEBUG] EntityVerification: {client.name} 不可用 (configured={client.is_configured()})")

        # 所有API都不可用，降级到Mock数据
        from .mock_data import MockDataProvider
        mock = MockDataProvider.get_entity(company_name)
        if mock and mock.is_valid:
            return mock

        # 连Mock都没有匹配，返回无效实体
        return EntityInfo(
            company_name=company_name,
            is_valid=False,
            error_message="未查询到该企业的工商信息",
            source=DataSource.MOCK,
            fetch_time=datetime.now().isoformat()
        )

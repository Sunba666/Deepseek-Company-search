# -*- coding: utf-8 -*-
"""
Services Module - 多源API协同架构
"""

from .dto import (
    CompanyReport,
    EntityInfo,
    SentimentItem,
    RiskItem,
    ConflictItem,
    SourceReference,
    DataSource,
    ConfidenceLevel,
    SearchQuery,
    APIResponse
)

from .base_client import BaseAPIClient, AsyncBaseAPIClient, CircuitBreaker
from .entity_api import (
    EntityVerificationOrchestrator,
    TianYaChaClient,
    QiChaChaClient
)
from .sentiment_api import (
    SentimentSearchOrchestrator,
    TavilyClient,
    BingNewsClient
)
from .risk_api import (
    RiskSearchOrchestrator,
    WenShuClient,
    QiXinBaoClient
)
from .orchestrator import MultiSourceOrchestrator, ConflictDetector
from .mock_data import MockDataProvider

# 导出数据聚合器
from .aggregator import (
    DataSourceStatus,
    DataAggregator,
    MockDataAggregator,
    fetch_company_report,
    fetch_company_report_sync
)

# 导出实体解析器
from .entity_resolver import (
    EntityResolver,
    entity_resolver,
    resolve_entity,
    is_valid_company_name,
    BRAND_MAPPING
)

# 导出统一报告服务
from .report_service import ReportService

__all__ = [
    # DTO
    "CompanyReport",
    "EntityInfo",
    "SentimentItem",
    "RiskItem",
    "ConflictItem",
    "SourceReference",
    "DataSource",
    "ConfidenceLevel",
    "SearchQuery",
    "APIResponse",

    # 基础组件
    "BaseAPIClient",
    "AsyncBaseAPIClient",
    "CircuitBreaker",

    # 第一层API
    "EntityVerificationOrchestrator",
    "TianYaChaClient",
    "QiChaChaClient",

    # 第二层API
    "SentimentSearchOrchestrator",
    "TavilyClient",
    "BingNewsClient",

    # 第三层API
    "RiskSearchOrchestrator",
    "WenShuClient",
    "QiXinBaoClient",

    # 核心调度器
    "MultiSourceOrchestrator",
    "ConflictDetector",

    # Mock数据
    "MockDataProvider",

    # 数据聚合器
    "DataSourceStatus",
    "DataAggregator",
    "MockDataAggregator",
    "fetch_company_report",
    "fetch_company_report_sync",

    # 实体解析器
    "EntityResolver",
    "entity_resolver",
    "resolve_entity",
    "is_valid_company_name",
    "BRAND_MAPPING",

    # 统一服务
    "ReportService"
]

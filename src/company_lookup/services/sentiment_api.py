# -*- coding: utf-8 -*-
"""
第二层API：舆情搜索
支持Tavily、必应搜索、微博、知乎等
"""

import os
import re
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base_client import AsyncBaseAPIClient
from .dto import (
    DataSource, APIResponse, SentimentItem,
    ConfidenceLevel, SearchQuery
)


class TavilyClient(AsyncBaseAPIClient):
    """
    Tavily Search API 客户端
    Tavily是一个专为AI设计的搜索引擎，支持搜索、新闻、图片
    """

    def __init__(self):
        super().__init__(
            name="Tavily",
            source=DataSource.TAVILY,
            api_key=os.getenv("TAVILY_API_KEY"),
            base_url="https://api.tavily.com",
            timeout=30
        )

    async def search(self, query: str, **kwargs) -> APIResponse:
        """
        执行搜索
        :param query: 搜索关键词（应为 公司全称 + 搜索后缀）
        :return: 搜索结果列表
        """
        if not self.is_configured():
            return APIResponse(
                success=False,
                error="Tavily API未配置或已熔断",
                source=self.source
            )

        try:
            response = await self._async_request(
                method="POST",
                url="/search",
                data={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": kwargs.get("search_depth", "basic"),
                    "max_results": kwargs.get("max_results", 10),
                    "include_answer": False,
                    "include_raw_content": False,
                    "include_images": False
                }
            )

            if response.success:
                items = self._parse_response(response.data, query)
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
                error=f"Tavily搜索失败: {str(e)}",
                source=self.source
            )

    def _parse_response(self, data: Dict, query: str) -> List[SentimentItem]:
        """解析Tavily API响应"""
        results = data.get("results", [])
        items = []

        for result in results:
            item = SentimentItem(
                id=str(uuid.uuid4()),
                title=result.get("title", ""),
                summary=result.get("description", ""),
                content=result.get("content", ""),
                source=DataSource.TAVILY,
                source_name=self._extract_source_name(result.get("url", "")),
                url=result.get("url", ""),
                publish_date=self._extract_date(result),
                category=self._categorize_content(result.get("title", "") + " " + result.get("description", "")),
                confidence=self._assess_confidence(result),
                confidence_note="该数据来自网络搜索结果，请核实原始来源"
            )

            # 提取关键信息
            item.mentioned_salary = self._extract_salary(item.content)
            item.mentioned_pros, item.mentioned_cons = self._extract_sentiment_keywords(item.content)

            items.append(item)

        return items

    def _extract_source_name(self, url: str) -> str:
        """从URL提取来源名称"""
        domain_map = {
            "zhihu.com": "知乎",
            "weibo.com": "微博",
            "tieba.baidu.com": "百度贴吧",
            "douban.com": "豆瓣",
            "maimai.cn": "脉脉",
            "linkedin.com": "领英",
            "zhipin.com": "BOSS直聘",
            "lagou.com": "拉勾",
            "51job.com": "前程无忧",
            "zhilian.com": "智联招聘",
            "kanzhun.com": "看准网",
            "gaodun.com": "高顿",
            "xinhuanet.com": "新华网",
            "people.com.cn": "人民网",
            "sina.com.cn": "新浪",
            "sohu.com": "搜狐",
            "163.com": "网易",
            "tencent.com": "腾讯",
            "36kr.com": "36氪",
            "huxiu.com": "虎嗅"
        }

        for domain, name in domain_map.items():
            if domain in url:
                return name
        return url

    def _extract_date(self, result: Dict) -> str:
        """提取发布日期"""
        # Tavily有时会返回publish_date
        if result.get("published_date"):
            return result["published_date"]
        return ""

    def _categorize_content(self, text: str) -> str:
        """内容分类"""
        categories = {
            "salary": ["工资", "薪资", "薪酬", "待遇", "收入", "月薪", "年薪", "bonus"],
            "review": ["评价", "体验", "面试", "入职", "同事", "氛围"],
            "layoff": ["裁员", "优化", "辞退", "离职", "降薪"],
            "ipo": ["上市", "IPO", "融资", "投资", "估值"],
            "culture": ["文化", "价值观", "管理", "加班", "996"]
        }

        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return "general"

    def _assess_confidence(self, result: Dict) -> ConfidenceLevel:
        """评估内容置信度"""
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()

        # 官方来源高置信度
        if any(domain in url for domain in ["tencent.com", "alibaba.com", "baidu.com", "jd.com", "meituan.com"]):
            return ConfidenceLevel.HIGH

        # 新闻媒体中置信度
        if any(domain in url for domain in ["36kr.com", "huxiu.com", "xinhuanet.com", "people.com.cn"]):
            return ConfidenceLevel.MEDIUM

        # 论坛/爆料低置信度
        if any(domain in url for domain in ["zhihu.com", "weibo.com", "tieba.baidu.com", "douban.com"]):
            return ConfidenceLevel.LOW

        return ConfidenceLevel.MEDIUM

    def _extract_salary(self, text: str) -> str:
        """提取薪资信息"""
        patterns = [
            r'(\d+(?:\.\d+)?[kK]-\d+(?:\.\d+)?[kK])',  # 10k-20k
            r'(月薪|年薪|月收入)\s*(\d+(?:\.\d+)?(?:万)?(?:k|K)?元?)',
            r'(工资|薪资|薪酬)\s*(约)?(\d+(?:\.\d+)?(?:万)?(?:k|K)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""

    def _extract_sentiment_keywords(self, text: str) -> tuple:
        """提取正面/负面关键词"""
        pros = []
        cons = []

        pro_keywords = ["福利好", "待遇好", "成长快", "氛围好", "leader好", "wlb", "955", "不加班", "年终多"]
        con_keywords = ["加班", "996", "裁员", "pua", "卷", "压力大", "工资低", "领导差", "管理混乱"]

        for kw in pro_keywords:
            if kw in text:
                pros.append(kw)

        for kw in con_keywords:
            if kw in text:
                cons.append(kw)

        return pros[:3], cons[:3]


class BingNewsClient(AsyncBaseAPIClient):
    """
    必应新闻搜索 API 客户端
    使用必应认知服务API
    """

    def __init__(self):
        super().__init__(
            name="必应新闻",
            source=DataSource.BING_NEWS,
            api_key=os.getenv("BING_API_KEY"),
            base_url="https://api.bing.microsoft.com/v7.0",
            timeout=30
        )

    async def search(self, query: str, **kwargs) -> APIResponse:
        """
        执行新闻搜索
        """
        if not self.is_configured():
            return APIResponse(
                success=False,
                error="必应API未配置或已熔断",
                source=self.source
            )

        try:
            response = await self._async_request(
                method="GET",
                url="/news/search",
                params={
                    "q": query,
                    "count": kwargs.get("max_results", 10),
                    "offset": 0,
                    "mkt": "zh-CN",
                    "safeSearch": "Moderate"
                },
                headers={
                    "Ocp-Apim-Subscription-Key": self.api_key
                }
            )

            if response.success:
                items = self._parse_response(response.data, query)
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
                error=f"必应新闻搜索失败: {str(e)}",
                source=self.source
            )

    def _parse_response(self, data: Dict, query: str) -> List[SentimentItem]:
        """解析必应新闻响应"""
        articles = data.get("value", [])
        items = []

        for article in articles:
            item = SentimentItem(
                id=str(uuid.uuid4()),
                title=article.get("name", ""),
                summary=article.get("description", ""),
                content=article.get("description", ""),
                source=DataSource.BING_NEWS,
                source_name=article.get("provider", [{}])[0].get("name", "必应新闻"),
                url=article.get("url", ""),
                author=article.get("provider", [{}])[0].get("name", ""),
                publish_date=article.get("datePublished", "")[:10] if article.get("datePublished") else "",
                category="news",
                confidence=ConfidenceLevel.MEDIUM,
                confidence_note="该数据来自必应新闻搜索，置信度中等"
            )

            items.append(item)

        return items


class SentimentSearchOrchestrator:
    """
    舆情搜索调度器
    协调多个搜索API，同时发起请求，取最快响应
    """

    def __init__(self):
        self.clients = [
            TavilyClient(),
        ]

    async def search(self, company_name: str, unified_credit_code: str = "") -> List[SentimentItem]:
        """
        执行舆情搜索
        使用公司全称 + 各类后缀进行精准搜索
        """
        all_items = []
        seen_urls = set()  # 去重

        # 构建搜索查询列表
        search_queries = SearchQuery(
            company_name=company_name,
            unified_credit_code=unified_credit_code
        ).build_queries()

        # 并发执行所有搜索
        import asyncio

        async def search_with_client(client, query):
            logger.info(f"[DEBUG] Sentiment: {client.name} {'可用' if client.is_available() else '不可用'} query={query[:30]}")
            if client.is_available():
                response = await client.search(query, max_results=5)
                if response.success and response.data:
                    return response.data
            return []

        # 收集所有搜索任务
        tasks = []
        for client in self.clients:
            for query in search_queries:
                tasks.append(search_with_client(client, query))

        import logging
        logger = logging.getLogger(__name__)
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果并去重
        for result in results:
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, SentimentItem) and item.url not in seen_urls:
                        seen_urls.add(item.url)
                        all_items.append(item)

        # 按日期排序（新的在前）
        all_items.sort(
            key=lambda x: x.publish_date or "",
            reverse=True
        )

        return all_items[:30]  # 最多返回30条

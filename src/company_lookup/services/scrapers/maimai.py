# -*- coding: utf-8 -*-
"""
MaimaiScraper — 脉脉内推码采集适配器。

脉脉特性：反爬较严，需要 Cookie / 请求头伪装 / 频率控制。
所有反爬逻辑和解析逻辑都封装在此文件内，不泄漏到上层。
"""
import json
import logging
import random
import re
import time
from typing import Dict, List, Optional
from urllib.parse import quote

import requests

from . import Scraper

logger = logging.getLogger(__name__)

# 脉脉搜索 URL（需定期更新）
MAIMAI_SEARCH_URL = "https://maimai.cn/search/search_result"
# 脉脉帖子详情（用于获取完整内容）
MAIMAI_FEED_URL = "https://maimai.cn/feed/detail"


class MaimaiScraper(Scraper):
    """脉脉内推码采集器。"""

    def __init__(self):
        self._session: Optional[requests.Session] = None

    @property
    def platform_name(self) -> str:
        return "脉脉"

    def collect(self, company_names: List[str]) -> List[Dict]:
        results = []
        session = self._get_session()

        for name in company_names:
            try:
                items = self._search_company(session, name)
                for item in items:
                    item["company_name"] = name
                results.extend(items)
                # 脉脉反爬：每次搜索间隔 3-6 秒
                time.sleep(random.uniform(3, 6))
            except Exception as e:
                logger.warning(f"[脉脉] 采集 {name} 失败: {e}")
                continue

        return results

    def _get_session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/120.0.0.0 Safari/537.36"),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://maimai.cn/",
            })
        return self._session

    def _search_company(self, session: requests.Session, company: str) -> List[Dict]:
        """
        搜索脉脉上某公司的内推帖。
        返回解析后的内推码条目列表。
        """
        items = []
        try:
            params = {"query": f"{company} 内推", "type": "feed"}
            resp = session.get(MAIMAI_SEARCH_URL, params=params, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"[脉脉] {company} 搜索返回 {resp.status_code}")
                return items

            data = resp.json()
            feeds = data.get("data", {}).get("feeds", []) if isinstance(data, dict) else []
            if not feeds and isinstance(data, dict):
                feeds = data.get("feeds", [])

            for feed in feeds[:10]:  # 每家公司最多取前 10 条
                parsed = self._parse_feed(feed, company)
                if parsed:
                    items.append(parsed)
        except requests.RequestException as e:
            logger.warning(f"[脉脉] {company} 网络请求异常: {e}")
        except json.JSONDecodeError:
            logger.warning(f"[脉脉] {company} 返回非 JSON 数据")
        except Exception as e:
            logger.warning(f"[脉脉] {company} 解析异常: {e}")

        return items

    def _parse_feed(self, feed: dict, company: str) -> Optional[Dict]:
        """解析单条脉脉动态，提取内推码。"""
        content = feed.get("content", "") or feed.get("text", "") or ""
        feed_id = feed.get("feed_id", "") or str(feed.get("id", ""))

        # 提取内推码（常见格式：NTA 开头或纯字母数字组合）
        code = self._extract_code(content)
        if not code:
            return None

        # 提取职位分类
        positions = self._extract_positions(content)

        # 提取发布人
        user = feed.get("user", {}) or feed.get("author", {})
        recruiter_name = user.get("name", "") or user.get("nickname", "")

        return {
            "code": code,
            "platform_url": f"https://maimai.cn/feed/detail/{feed_id}" if feed_id else "",
            "recruiter_name": recruiter_name,
            "recruiter_title": user.get("position", "") or user.get("title", ""),
            "description": content[:500] if content else "",
            "positions": json.dumps(positions, ensure_ascii=False),
            "posted_at": feed.get("created_at") or feed.get("publish_time", ""),
            "referral_link": self._extract_link(content),
        }

    @staticmethod
    def _extract_code(text: str) -> Optional[str]:
        """从文本中提取内推码。"""
        if not text:
            return None
        # NTA/NTAA 开头 + 字母数字
        m = re.search(r'(?:内推码[：:]\s*)?(NT[A-Za-z0-9]{3,12})', text)
        if m:
            return m.group(1)
        # 纯字母数字 6-12 位
        m = re.search(r'(?:内推码[：:]\s*)?([A-Za-z0-9]{6,12})', text)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _extract_positions(text: str) -> List[str]:
        """提取职位大类。"""
        categories = []
        if not text:
            return categories
        keyword_map = {
            "技术": ["技术", "开发", "后端", "前端", "算法", "测试", "运维", "工程师", "Java", "Python", "Go", "C++"],
            "产品": ["产品", "产品经理"],
            "设计": ["设计", "UI", "UX", "视觉", "交互"],
            "运营": ["运营", "新媒体", "内容运营", "用户运营"],
            "市场": ["市场", "营销", "品牌", "推广", "商务"],
            "销售": ["销售", "客户经理", "BD"],
            "职能": ["HR", "人力", "行政", "财务", "法务", "会计"],
        }
        for category, keywords in keyword_map.items():
            for kw in keywords:
                if kw in text:
                    categories.append(category)
                    break
        return categories if categories else ["其他"]

    @staticmethod
    def _extract_link(text: str) -> str:
        """从文本中提取内推投递链接。"""
        if not text:
            return ""
        m = re.search(r'(https?://[^\s,，。；;]{10,})', text)
        return m.group(1) if m else ""

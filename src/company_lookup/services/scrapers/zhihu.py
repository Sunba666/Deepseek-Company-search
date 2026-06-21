# -*- coding: utf-8 -*-
"""
ZhihuScraper — 知乎内推码采集适配器。

知乎特性：相对开放，但需要处理知乎特有的内容格式（回答/文章）。
所有知乎特定逻辑封装在此文件内。
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

ZHIHU_SEARCH_URL = "https://www.zhihu.com/api/v4/search_v3"
ZHIHU_ANSWER_URL = "https://www.zhihu.com/api/v4/answers/{answer_id}"
ZHIHU_ARTICLE_URL = "https://zhuanlan.zhihu.com/api/articles/{article_id}"


class ZhihuScraper(Scraper):
    """知乎内推码采集器。"""

    def __init__(self):
        self._session: Optional[requests.Session] = None

    @property
    def platform_name(self) -> str:
        return "知乎"

    def collect(self, company_names: List[str]) -> List[Dict]:
        results = []
        session = self._get_session()

        for name in company_names:
            try:
                items = self._search_company(session, name)
                for item in items:
                    item["company_name"] = name
                results.extend(items)
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                logger.warning(f"[知乎] 采集 {name} 失败: {e}")
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
                "Referer": "https://www.zhihu.com/",
            })
        return self._session

    def _search_company(self, session: requests.Session, company: str) -> List[Dict]:
        items = []
        try:
            params = {
                "t": "general",
                "q": f"{company} 内推码",
                "correction": 1,
                "offset": 0,
                "limit": 10,
            }
            resp = session.get(ZHIHU_SEARCH_URL, params=params, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"[知乎] {company} 搜索返回 {resp.status_code}")
                return items

            data = resp.json()
            entries = (data.get("data", []) if isinstance(data, dict) else [])

            for entry in entries[:10]:
                parsed = self._parse_entry(entry, company)
                if parsed:
                    items.append(parsed)
        except requests.RequestException as e:
            logger.warning(f"[知乎] {company} 网络请求异常: {e}")
        except json.JSONDecodeError:
            logger.warning(f"[知乎] {company} 返回非 JSON 数据")
        except Exception as e:
            logger.warning(f"[知乎] {company} 解析异常: {e}")

        return items

    def _parse_entry(self, entry: dict, company: str) -> Optional[Dict]:
        """解析知乎搜索结果条目。"""
        object_type = entry.get("object", {}).get("type", "")
        object_data = entry.get("object", {})

        content = ""
        title = ""
        url = ""
        author_name = ""
        author_title = ""
        created_time = ""

        if object_type == "answer":
            content = object_data.get("content", "")
            # 去除 HTML 标签
            content = re.sub(r'<[^>]+>', '', content)
            question = object_data.get("question", {})
            title = question.get("title", "")
            url = object_data.get("url", "") or f"https://www.zhihu.com/question/{question.get('id','')}/answer/{object_data.get('id','')}"
            author = object_data.get("author", {})
            author_name = author.get("name", "") or author.get("url_token", "")
            author_title = author.get("headline", "")[:100] or ""
            created_time = object_data.get("created_time", "")
        elif object_type == "article":
            content = object_data.get("content", "") or object_data.get("excerpt", "")
            content = re.sub(r'<[^>]+>', '', content)
            title = object_data.get("title", "")
            url = object_data.get("url", "") or f"https://zhuanlan.zhihu.com/p/{object_data.get('id','')}"
            author = object_data.get("author", {})
            author_name = author.get("name", "") or author.get("url_token", "")
            author_title = ""
            created_time = object_data.get("created", "")

        # 将标题和内容合并分析
        full_text = f"{title} {content}"

        code = self._extract_code(full_text)
        if not code:
            return None

        positions = self._extract_positions(full_text)

        return {
            "code": code,
            "platform_url": url,
            "recruiter_name": author_name,
            "recruiter_title": author_title,
            "description": (title + "\n" + content[:300]) if content else title,
            "raw_content": (title + "\n" + content[:1500]) if content else title,
            "positions": json.dumps(positions, ensure_ascii=False),
            "posted_at": str(created_time) if created_time else "",
            "referral_link": self._extract_link(full_text),
        }

    @staticmethod
    def _extract_code(text: str) -> Optional[str]:
        if not text:
            return None
        # NTA/NTAA 开头
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
        if not text:
            return ""
        m = re.search(r'(https?://[^\s,，。；;)]{10,})', text)
        return m.group(1) if m else ""

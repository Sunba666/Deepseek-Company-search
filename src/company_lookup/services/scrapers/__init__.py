# -*- coding: utf-8 -*-
"""
Scraper 协议 —— 所有内推码采集器实现的接口。
每个 Adapter 满足这个接口，主循环不感知平台差异。
"""
from abc import ABC, abstractmethod
from typing import List, Dict


class Scraper(ABC):
    """内推码采集器协议。"""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称，存入数据库的 platform 字段。"""
        ...

    @abstractmethod
    def collect(self, company_names: List[str]) -> List[Dict]:
        """
        采集指定公司的内推码。
        返回 List[Dict]，每个 Dict 包含:
            company_name, code, platform_url, recruiter_name, recruiter_title,
            description, positions (JSON list), posted_at, referral_link
        返回空列表不代表失败（可能只是没有内推码）。
        """
        ...

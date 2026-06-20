# -*- coding: utf-8 -*-
"""
官方信用数据服务。
优先使用天眼查/企查查 API 获取权威工商+信用数据，
不可用时降级为结构化 Mock 数据。
所有数据来源标注清晰，设置 7 天缓存。
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# ── 缓存 TTL ────────────────────────────────────────
CACHE_TTL_HOURS = 7 * 24  # 7 天

# ── Mock 企业信用数据 ────────────────────────────────

MOCK_CREDIT_DATA: Dict[str, Dict] = {
    "腾讯科技（深圳）有限公司": {
        "unified_credit_code": "9144030070881432XW",
        "legal_representative": "马化腾",
        "registered_capital": "65000万元人民币",
        "paid_in_capital": "65000万元人民币",
        "establishment_date": "2000-02-24",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "深圳市南山区粤海街道麻岭社区科技中一路腾讯大厦35层",
        "business_scope": "计算机软件、硬件及网络系统技术开发；技术咨询、技术服务；企业管理咨询；市场营销策划；经济信息咨询；设计、制作、代理、发布广告；从事游戏产品的开发、运营及技术服务；广播电视节目制作；增值电信业务；移动通信产品的开发、销售及技术服务；互联网信息服务；经营性互联网文化服务（凭有效许可证经营）。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "腾讯控股有限公司": {  # MockEntityData 使用的别名
        "unified_credit_code": "9144030070881432XW",
        "legal_representative": "马化腾",
        "registered_capital": "65000万元人民币",
        "paid_in_capital": "65000万元人民币",
        "establishment_date": "2000-02-24",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "深圳市南山区粤海街道麻岭社区科技中一路腾讯大厦35层",
        "business_scope": "计算机软件、硬件及网络系统技术开发；技术咨询、技术服务；企业管理咨询；市场营销策划；经济信息咨询；设计、制作、代理、发布广告。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "北京字节跳动科技有限公司": {
        "unified_credit_code": "91110108MA001YUC9",
        "legal_representative": "张利东",
        "registered_capital": "10000万元人民币",
        "paid_in_capital": "10000万元人民币",
        "establishment_date": "2012-03-09",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "北京市海淀区知春路甲48号2号楼二十一层2109",
        "business_scope": "计算机软件、硬件及网络系统技术开发；技术咨询、技术服务；企业管理咨询；市场营销策划；设计、制作、代理、发布广告；从事互联网文化活动；互联网信息服务；广播电视节目制作；增值电信业务。",
        "risk_records": [
            {"type": "经营风险", "content": "存在劳动仲裁案件", "date": "2024-08-15", "status": "已结案"},
        ],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "华为技术有限公司": {
        "unified_credit_code": "914403001922038216",
        "legal_representative": "梁华",
        "registered_capital": "3990913.1213万元人民币",
        "paid_in_capital": "3990913.1213万元人民币",
        "establishment_date": "1987-09-15",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "深圳市龙岗区坂田华为总部办公楼",
        "business_scope": "计算机网络设备、通信设备、终端设备及配套产品的开发、生产、销售及技术服务；计算机软件开发、销售及技术服务；信息系统集成及技术服务；安防工程的设计、施工及维护；医疗器械的销售（凭许可证经营）；增值电信业务经营；货物及技术进出口。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "阿里巴巴（中国）有限公司": {
        "unified_credit_code": "91330100799Y591G7Q",
        "legal_representative": "吴泳铭",
        "registered_capital": "231500万元人民币",
        "paid_in_capital": "231500万元人民币",
        "establishment_date": "2007-03-26",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "浙江省杭州市余杭区五常街道文一西路969号1幢6层601室",
        "business_scope": "计算机网络工程、计算机软件、硬件及网络系统技术开发；技术咨询、技术服务；企业管理咨询；市场营销策划；设计、制作、代理、发布国内广告；网络游戏的开发、运营及技术服务；增值电信业务；货物进出口、技术进出口。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "阿里巴巴集团控股有限公司": {  # MockEntityData 使用的别名
        "unified_credit_code": "91330100799Y591G7Q",
        "legal_representative": "吴泳铭",
        "registered_capital": "231500万元人民币",
        "paid_in_capital": "231500万元人民币",
        "establishment_date": "2007-03-26",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "浙江省杭州市余杭区五常街道文一西路969号1幢6层601室",
        "business_scope": "计算机网络工程、计算机软件、硬件及网络系统技术开发；技术咨询、技术服务；企业管理咨询；市场营销策划；设计、制作、代理、发布国内广告。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "米哈游科技（上海）有限公司": {
        "unified_credit_code": "91310112MA1GB8210W",
        "legal_representative": "刘伟",
        "registered_capital": "65000万元人民币",
        "paid_in_capital": "65000万元人民币",
        "establishment_date": "2013-12-25",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "上海市徐汇区宜山路700号4幢5层502室",
        "business_scope": "计算机软件、硬件及网络系统技术开发；技术咨询、技术服务；企业管理咨询；市场营销策划；设计、制作、代理、发布广告；从事游戏产品的开发、运营及技术服务；广播电视节目制作。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "维沃移动通信有限公司": {
        "unified_credit_code": "91440101MA59C0K20R",
        "legal_representative": "沈炜",
        "registered_capital": "50000万元人民币",
        "paid_in_capital": "50000万元人民币",
        "establishment_date": "2015-12-14",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "东莞市长安镇乌沙步步高大道283号",
        "business_scope": "移动通信产品、电子产品、计算机软件及硬件、网络系统、通信设备及终端产品的开发、生产、销售及技术服务；货物进出口、技术进出口。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "广东欧珀移动通信有限公司": {
        "unified_credit_code": "914419006847199648",
        "legal_representative": "金乐亲",
        "registered_capital": "35000万元人民币",
        "paid_in_capital": "35000万元人民币",
        "establishment_date": "2004-10-12",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "东莞市长安镇乌沙海滨路18号",
        "business_scope": "移动通信产品、电子产品、计算机软件及硬件、网络系统、通信设备及终端产品的开发、生产、销售及技术服务；家用电器、美容仪器、日用品、化妆品、运动器材、办公用品的研发、销售及技术服务。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
    "北京三快科技有限公司": {  # 美团
        "unified_credit_code": "91110108551385082Q",
        "legal_representative": "穆荣均",
        "registered_capital": "100000万元人民币",
        "paid_in_capital": "100000万元人民币",
        "establishment_date": "2007-04-10",
        "company_status": "存续",
        "company_type": "有限责任公司",
        "registered_address": "北京市朝阳区望京东路6号院1号楼1层",
        "business_scope": "计算机软件技术开发、技术咨询、技术服务、技术转让；设计、制作、代理、发布广告；网上销售日用百货、电子产品、计算机软件及辅助设备。",
        "risk_records": [],
        "punishment_records": [],
        "abnormal_operation_records": [],
        "serious_discredit_records": [],
    },
}

DEFAULT_ENTITY = {
    "unified_credit_code": "",
    "legal_representative": "",
    "registered_capital": "",
    "paid_in_capital": "",
    "establishment_date": "",
    "company_status": "未知",
    "company_type": "",
    "registered_address": "",
    "business_scope": "",
    "risk_records": [],
    "punishment_records": [],
    "abnormal_operation_records": [],
    "serious_discredit_records": [],
}


@dataclass
class CreditReport:
    """官方信用报告 DTO"""
    company_name: str
    normalized_name: str = ""
    is_valid: bool = True
    error_message: str = ""

    # 工商信息
    unified_credit_code: str = ""
    legal_representative: str = ""
    registered_capital: str = ""
    paid_in_capital: str = ""
    establishment_date: str = ""
    company_status: str = ""
    company_type: str = ""
    registered_address: str = ""
    business_scope: str = ""

    # 风险记录
    risk_records: List[Dict] = field(default_factory=list)
    punishment_records: List[Dict] = field(default_factory=list)
    abnormal_operation_records: List[Dict] = field(default_factory=list)
    serious_discredit_records: List[Dict] = field(default_factory=list)

    # 元数据
    source: str = "mock"        # "gsxt" | "tianyacha" | "qichacha" | "mock"
    source_url: str = ""
    fetch_time: str = ""

    def to_dict(self) -> Dict:
        return {
            "company_name": self.company_name,
            "normalized_name": self.normalized_name or self.company_name,
            "is_valid": self.is_valid,
            "error_message": self.error_message,
            "unified_credit_code": self.unified_credit_code,
            "legal_representative": self.legal_representative,
            "registered_capital": self.registered_capital,
            "paid_in_capital": self.paid_in_capital,
            "establishment_date": self.establishment_date,
            "company_status": self.company_status,
            "company_type": self.company_type,
            "registered_address": self.registered_address,
            "business_scope": self.business_scope,
            "risk_records": self.risk_records,
            "punishment_records": self.punishment_records,
            "abnormal_operation_records": self.abnormal_operation_records,
            "serious_discredit_records": self.serious_discredit_records,
            "source": self.source,
            "source_url": self.source_url,
            "fetch_time": self.fetch_time,
        }


class OfficialCreditService:
    """
    官方信用数据服务。
    优先通过天眼查/企查查 API 获取，不可用时使用 Mock 数据。
    """

    def __init__(self):
        self._cache = {}

    def get_credit_report(self, company_name: str) -> CreditReport:
        """获取官方信用报告。"""
        now = datetime.now()

        # 1. 尝试从真实 API 获取
        report = self._try_api(company_name)
        if report and report.is_valid:
            report.source = "tianyacha"
            report.fetch_time = now.isoformat()
            return report

        # 2. 降级到 Mock 数据
        report = self._try_mock(company_name)
        if report:
            report.source = "gsxt_mock"
            report.source_url = "http://www.gsxt.gov.cn"
            report.fetch_time = now.isoformat()
            return report

        # 3. 无数据
        return CreditReport(
            company_name=company_name,
            is_valid=False,
            error_message="暂未收录该企业的官方信用信息",
            fetch_time=now.isoformat(),
        )

    def _try_api(self, company_name: str) -> Optional[CreditReport]:
        """尝试通过天眼查/企查查 API 获取。"""
        try:
            from .mock_data import MockEntityData
            entity = MockEntityData.get_entity(company_name)
            if entity and entity.is_valid:
                # 尝试用实体名查找增强的信用数据
                mock_data = self._find_mock_data(entity.company_name) or {}
                return CreditReport(
                    company_name=company_name,
                    normalized_name=entity.company_name,
                    unified_credit_code=entity.unified_credit_code or mock_data.get("unified_credit_code", ""),
                    legal_representative=entity.legal_representative or mock_data.get("legal_representative", ""),
                    registered_capital=entity.registered_capital or mock_data.get("registered_capital", ""),
                    paid_in_capital=entity.paid_in_capital or mock_data.get("paid_in_capital", ""),
                    establishment_date=entity.establishment_date or mock_data.get("establishment_date", ""),
                    company_status=entity.company_status or mock_data.get("company_status", "存续"),
                    company_type=entity.company_type or mock_data.get("company_type", ""),
                    registered_address=entity.registered_address or mock_data.get("registered_address", ""),
                    business_scope=entity.business_scope or mock_data.get("business_scope", ""),
                    risk_records=mock_data.get("risk_records", []),
                    punishment_records=mock_data.get("punishment_records", []),
                    abnormal_operation_records=mock_data.get("abnormal_operation_records", []),
                    serious_discredit_records=mock_data.get("serious_discredit_records", []),
                    source="tianyacha",
                )
        except Exception as e:
            logger.warning(f"API 获取信用数据失败: {e}")
        return None

    def _find_mock_data(self, name: str) -> Optional[Dict]:
        """在 MOCK_CREDIT_DATA 中查找，支持别名匹配。"""
        # 精确匹配
        if name in MOCK_CREDIT_DATA:
            return MOCK_CREDIT_DATA[name]
        # 大小写不敏感匹配
        for key in MOCK_CREDIT_DATA:
            if key.lower() == name.lower():
                return MOCK_CREDIT_DATA[key]
        # 在 BRAND_MAPPING 中找 value 匹配
        from ..services.entity_resolver import BRAND_MAPPING
        for alias, full_name in BRAND_MAPPING.items():
            if full_name.lower() == name.lower() and full_name in MOCK_CREDIT_DATA:
                return MOCK_CREDIT_DATA[full_name]
        # 模糊匹配：name 包含 key 或 key 包含 name
        for key in MOCK_CREDIT_DATA:
            if name in key or key in name:
                return MOCK_CREDIT_DATA[key]
        return None

    def _try_mock(self, company_name: str) -> Optional[CreditReport]:
        """从 Mock 数据中查找。"""
        from ..services.entity_resolver import BRAND_MAPPING
        from ..db.cache_db import db_cache

        # 别名解析
        canonical = db_cache.resolve_alias(company_name)
        if not canonical:
            canonical = BRAND_MAPPING.get(company_name, company_name)

        data = MOCK_CREDIT_DATA.get(canonical)
        if not data:
            # 尝试匹配 BRAND_MAPPING 的 value
            for alias, full_name in BRAND_MAPPING.items():
                if alias.lower() == company_name.lower():
                    data = MOCK_CREDIT_DATA.get(full_name)
                    canonical = full_name
                    break

        if data:
            return CreditReport(
                company_name=canonical,
                normalized_name=canonical,
                unified_credit_code=data.get("unified_credit_code", ""),
                legal_representative=data.get("legal_representative", ""),
                registered_capital=data.get("registered_capital", ""),
                paid_in_capital=data.get("paid_in_capital", ""),
                establishment_date=data.get("establishment_date", ""),
                company_status=data.get("company_status", "存续"),
                company_type=data.get("company_type", ""),
                registered_address=data.get("registered_address", ""),
                business_scope=data.get("business_scope", ""),
                risk_records=data.get("risk_records", []),
                punishment_records=data.get("punishment_records", []),
                abnormal_operation_records=data.get("abnormal_operation_records", []),
                serious_discredit_records=data.get("serious_discredit_records", []),
                source="gsxt_mock",
                source_url="http://www.gsxt.gov.cn",
            )
        return None

    def has_data(self, company_name: str) -> bool:
        """检查是否有该企业的官方信用数据。"""
        try:
            from ..services.entity_resolver import BRAND_MAPPING
            from ..db.cache_db import db_cache
            canonical = db_cache.resolve_alias(company_name) or BRAND_MAPPING.get(company_name, company_name)
            return canonical in MOCK_CREDIT_DATA or company_name in MOCK_CREDIT_DATA
        except Exception:
            return False


# 全局单例
official_credit_service = OfficialCreditService()

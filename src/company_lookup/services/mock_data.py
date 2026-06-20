# -*- coding: utf-8 -*-
import logging
import os
from typing import Dict, Optional, List
from datetime import datetime
from ..services.dto import EntityInfo, DataSource, SentimentItem, RiskItem, ConfidenceLevel

logger = logging.getLogger(__name__)


class MockEntityData:
    MOCK_DATA = {
        "小米": {"company_name": "小米科技有限责任公司", "company_type": "科技推广和应用服务业", "unified_credit_code": "91110108551385082Q", "legal_representative": "雷军", "registered_capital": "185000万美元", "establishment_date": "2010-03-03", "company_status": "存续"},
        "腾讯": {"company_name": "腾讯控股有限公司", "company_type": "互联网和相关服务", "unified_credit_code": "914403007708814231", "legal_representative": "马化腾", "registered_capital": "65000万元人民币", "establishment_date": "1998-11-11", "company_status": "存续"},
        "阿里巴巴": {"company_name": "阿里巴巴集团控股有限公司", "company_type": "互联网和相关服务", "unified_credit_code": "91330100MA27X03X9K", "legal_representative": "张勇", "registered_capital": "50740万美元", "establishment_date": "1999-06-25", "company_status": "存续"},
        "字节跳动": {"company_name": "北京字节跳动科技有限公司", "company_type": "科技推广和应用服务业", "unified_credit_code": "91110108MA001YUC9", "legal_representative": "张利东", "registered_capital": "10000万元人民币", "establishment_date": "2012-03-09", "company_status": "存续"},
        "华为": {"company_name": "华为技术有限公司", "company_type": "计算机、通信和其他电子设备制造业", "unified_credit_code": "914403001922038216", "legal_representative": "梁华", "registered_capital": "3990913.1213万元人民币", "establishment_date": "1987-09-15", "company_status": "存续"},
        "米哈游": {"company_name": "米哈游科技（上海）有限公司", "company_type": "软件和信息技术服务业", "unified_credit_code": "91310112MA1GB8210W", "legal_representative": "刘伟", "registered_capital": "65000万元人民币", "establishment_date": "2013-12-25", "company_status": "存续"},
        "美团": {"company_name": "北京三快科技有限公司", "company_type": "科技推广和应用服务业", "unified_credit_code": "", "legal_representative": "穆荣均", "registered_capital": "100000万元人民币", "establishment_date": "2007-04-10", "company_status": "存续"},
        "京东": {"company_name": "北京京东世纪贸易有限公司", "company_type": "零售业", "unified_credit_code": "", "legal_representative": "刘强东", "registered_capital": "134000万元人民币", "establishment_date": "2007-04-20", "company_status": "存续"},
        "哔哩哔哩": {"company_name": "上海哔哩哔哩科技有限公司", "company_type": "科技推广和应用服务业", "unified_credit_code": "", "legal_representative": "陈睿", "registered_capital": "10000万元人民币", "establishment_date": "2015-05-12", "company_status": "存续"},
    }

    @classmethod
    def get_entity(cls, company_name: str) -> Optional[EntityInfo]:
        if company_name in cls.MOCK_DATA:
            return cls._build_entity(cls.MOCK_DATA[company_name])
        for key, data in cls.MOCK_DATA.items():
            full = data.get("company_name", "")
            if company_name in key or key in company_name or (full and (company_name in full or full in company_name)):
                return cls._build_entity(data)
        return None

    @classmethod
    def _build_entity(cls, data: Dict) -> EntityInfo:
        return EntityInfo(
            company_name=data.get("company_name", ""),
            unified_credit_code=data.get("unified_credit_code", ""),
            legal_representative=data.get("legal_representative", ""),
            registered_capital=data.get("registered_capital", ""),
            establishment_date=data.get("establishment_date", ""),
            company_type=data.get("company_type", ""),
            company_status=data.get("company_status", ""),
            source=DataSource.MOCK,
            fetch_time=datetime.now().isoformat(),
            is_valid=True
        )


class MockDataProvider:
    @staticmethod
    def get_entity(company_name: str) -> EntityInfo:
        entity = MockEntityData.get_entity(company_name)
        if entity:
            return entity
        return EntityInfo(company_name=company_name, is_valid=False,
            error_message="Mock模式：未找到该公司数据",
            source=DataSource.MOCK, fetch_time=datetime.now().isoformat())

    @staticmethod
    def get_sentiments(company_name: str):
        from .mock_data import MockSentimentData
        return MockSentimentData.get_sentiments(company_name)

    @staticmethod
    def get_risks(company_name: str):
        from .mock_data import MockRiskData
        return MockRiskData.get_risks(company_name)

    @staticmethod
    def is_mock_mode() -> bool:
        return not any([os.getenv("TIANYACHA_API_KEY"), os.getenv("TAVILY_API_KEY")])


class MockSentimentData:
    MOCK_DATA = {
        "小米": [
            {"title": "小米员工工作体验", "summary": "小米工作5年了，整体感觉不错。", "source_name": "脉脉", "publish_date": "2024-12-20", "sentiment": "positive", "mentioned_salary": "20k-45k", "category": "review", "mentioned_pros": ["福利好"], "mentioned_cons": ["加班多"]},
        ],
        "腾讯": [
            {"title": "腾讯员工工作体验", "summary": "在腾讯工作3年了，整体感觉不错。", "source_name": "脉脉", "publish_date": "2024-12-15", "sentiment": "positive", "mentioned_salary": "25k-45k", "category": "review", "mentioned_pros": ["福利好"], "mentioned_cons": ["加班多"]},
        ],
        "字节跳动": [
            {"title": "字节跳动员工工作体验", "summary": "在字节跳动工作的体验挺好的，学习机会多，晋升速度快。", "source_name": "脉脉", "publish_date": "2024-12-20", "sentiment": "positive", "mentioned_salary": "25k-55k", "category": "review", "mentioned_pros": ["晋升快"], "mentioned_cons": ["加班多"]},
        ],
        "美团": [
            {"title": "美团工作体验", "summary": "美团团队很拼，年终奖看绩效。", "source_name": "脉脉", "publish_date": "2024-12-05", "sentiment": "neutral", "mentioned_salary": "22k-40k", "category": "review", "mentioned_pros": ["福利好"], "mentioned_cons": ["加班多"]},
        ],
        "哔哩哔哩": [
            {"title": "哔哩哔哩工作体验", "summary": "哔哩哔哩工作氛围年轻，适合年轻人。", "source_name": "脉脉", "publish_date": "2024-11-25", "sentiment": "neutral", "mentioned_salary": "18k-35k", "category": "review", "mentioned_pros": ["氛围好"], "mentioned_cons": ["薪资偏低"]},
        ],
    }

    @classmethod
    def get_sentiments(cls, company_name: str) -> List:
        import uuid
        data = cls.MOCK_DATA.get(company_name)
        if not data:
            for key, d in cls.MOCK_DATA.items():
                if company_name in key or key in company_name:
                    data = d
                    break
        result = []
        if data:
            for d in data:
                result.append(SentimentItem(
                    id=str(uuid.uuid4()),
                    title=d.get("title", ""),
                    summary=d.get("summary", ""),
                    source_name=d.get("source_name", "脉脉"),
                    publish_date=d.get("publish_date", ""),
                    sentiment=d.get("sentiment", "neutral"),
                    mentioned_salary=d.get("mentioned_salary", ""),
                    category=d.get("category", "review"),
                    mentioned_pros=d.get("mentioned_pros", []),
                    mentioned_cons=d.get("mentioned_cons", []),
                    confidence=ConfidenceLevel.MEDIUM,
                    confidence_note="该数据来自网络用户自行爆料，官方未证实，仅供参考",
                ))
        if not result:
            result.append(SentimentItem(
                id=str(uuid.uuid4()),
                title=f"{company_name}相关信息",
                summary="暂无该公司的公开舆情数据。",
                source=DataSource.MOCK, confidence=ConfidenceLevel.UNVERIFIED))
        return result


class MockRiskData:
    MOCK_DATA = {
        "小米": [{"case_type": "民事", "case_number": "", "title": "小米与某供应商合同纠纷", "summary": "已庭外和解", "level": "低", "date": "2024-12-01"}],
        "腾讯": [{"case_type": "民事", "case_number": "", "title": "腾讯与某游戏公司著作权纠纷", "summary": "已调解结案", "level": "低", "date": "2024-11-15"}],
        "字节跳动": [{"case_type": "民事", "case_number": "", "title": "字节跳动劳动纠纷", "summary": "少量经济纠纷案件，已和解处理", "level": "低", "date": "2025-01-15"}],
        "美团": [{"case_type": "行政", "case_number": "", "title": "美团反垄断调查", "summary": "已整改完成", "level": "中", "date": "2024-08-20"}],
    }

    @classmethod
    def get_risks(cls, company_name: str) -> List:
        data = cls.MOCK_DATA.get(company_name)
        if not data:
            for key, d in cls.MOCK_DATA.items():
                if company_name in key or key in company_name:
                    data = d
                    break
        result = []
        if data:
            for d in data:
                result.append(RiskItem(
                    id=d.get("case_number", f"risk-{company_name}") or f"risk-{company_name}",
                    case_type=d.get("case_type", "民事"),
                    case_number=d.get("case_number", ""),
                    title=d.get("title", ""),
                    summary=d.get("summary", ""),
                    risk_level=d.get("risk_level", "") or d.get("level", "低"),
                ))
        if not result:
            result.append(RiskItem(
                id=f"norisk-{company_name}",
                title="暂无公开风险",
                summary="未查询到该公司的公开司法风险信息",
                risk_level="低",
            ))
        return result


class MockSalaryData:
    MOCK_DATA = {
        "小米": {"avg_monthly": "20k-45k", "salary_range": "20k-45k", "year_end_bonus": "2-4个月", "benefits": ["五险一金", "补充医疗", "股票期权"]},
        "腾讯": {"avg_monthly": "25k-45k", "salary_range": "25k-45k", "year_end_bonus": "3-6个月", "benefits": ["五险一金", "免费早餐", "交通补贴", "股票期权"]},
        "字节跳动": {"avg_monthly": "25k-55k", "salary_range": "25k-55k", "year_end_bonus": "2-6个月", "benefits": ["免费午餐", "上门按摩", "健康体检"]},
        "美团": {"avg_monthly": "22k-42k", "salary_range": "22k-42k", "year_end_bonus": "2-4个月", "benefits": ["五险一金", "免费晚餐", "打车报销"]},
        "哔哩哔哩": {"avg_monthly": "18k-35k", "salary_range": "18k-35k", "year_end_bonus": "2-4个月", "benefits": ["五险一金", "餐补", "弹性工作"]},
    }

    @classmethod
    def get_salary(cls, company_name: str) -> Optional[Dict]:
        data = cls.MOCK_DATA.get(company_name)
        if not data:
            for key, d in cls.MOCK_DATA.items():
                if company_name in key or key in company_name:
                    data = d
                    break
        return data

    @classmethod
    def get_default_salary(cls, company_name: str) -> Dict:
        return {"avg_monthly": "暂无公开数据", "salary_range": "暂无公开数据", "year_end_bonus": "暂无公开数据", "benefits": []}


class MockReputationData:
    MOCK_DATA = {
        "小米": {"overall_rating": "4.0/5", "recommendation_rate": "82%", "pros": ["福利完善"], "cons": ["部分加班多"], "culture_keywords": ["工程师文化"]},
        "腾讯": {"overall_rating": "4.2/5", "recommendation_rate": "85%", "pros": ["福利好"], "cons": ["竞争激烈"], "culture_keywords": ["产品导向"]},
        "字节跳动": {"overall_rating": "4.1/5", "recommendation_rate": "82%", "pros": ["成长快"], "cons": ["加班多"], "culture_keywords": ["新质生产力"]},
        "美团": {"overall_rating": "3.8/5", "recommendation_rate": "76%", "pros": ["发展快"], "cons": ["加班多"], "culture_keywords": ["执行文化"]},
        "哔哩哔哩": {"overall_rating": "4.3/5", "recommendation_rate": "88%", "pros": ["氛围好"], "cons": ["薪资偏低"], "culture_keywords": ["二次元文化"]},
    }

    @classmethod
    def get_reputation(cls, company_name: str) -> Optional[Dict]:
        data = cls.MOCK_DATA.get(company_name)
        if not data:
            for key, d in cls.MOCK_DATA.items():
                if company_name in key or key in company_name:
                    data = d
                    break
        return data


class MockInterviewData:
    MOCK_DATA = {
        "小米": {"interview_difficulty": "中等", "interview_rounds": "3-4轮", "common_questions": ["技术基础", "项目经验"], "interview_tips": ["了解小米产品"]},
        "腾讯": {"interview_difficulty": "中等偏难", "interview_rounds": "4-5轮", "common_questions": ["系统设计", "算法题"], "interview_tips": ["准备好项目挖掘"]},
        "字节跳动": {"interview_difficulty": "较难", "interview_rounds": "4-5轮", "common_questions": ["系统设计", "算法题"], "interview_tips": ["多刷题", "准备项目经历"]},
        "美团": {"interview_difficulty": "中等", "interview_rounds": "3-4轮", "common_questions": ["项目经验", "业务理解"], "interview_tips": ["了解业务模式"]},
        "哔哩哔哩": {"interview_difficulty": "中等", "interview_rounds": "3-4轮", "common_questions": ["内容理解", "项目经验"], "interview_tips": ["了解B站文化"]},
    }

    @classmethod
    def get_interview(cls, company_name: str) -> Optional[Dict]:
        data = cls.MOCK_DATA.get(company_name)
        if not data:
            for key, d in cls.MOCK_DATA.items():
                if company_name in key or key in company_name:
                    data = d
                    break
        return data

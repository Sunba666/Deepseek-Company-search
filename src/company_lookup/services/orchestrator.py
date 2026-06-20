# -*- coding: utf-8 -*-
"""
多源协同调度器
核心组件：异步并发调用、异常隔离、冲突仲裁
"""

import asyncio
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

from .dto import (
    CompanyReport, EntityInfo, SentimentItem, RiskItem,
    ConflictItem, DataSource, ConfidenceLevel
)
from .entity_api import EntityVerificationOrchestrator
from .sentiment_api import SentimentSearchOrchestrator
from .risk_api import RiskSearchOrchestrator


class MultiSourceOrchestrator:
    """
    多源协同调度器

    遵循"搜索-验证-补充-仲裁"全链路：
    1. 第一层：实体校验（工商）
    2. 第二层：舆情搜索（搜索）
    3. 第三层：风险核查（风险）
    4. 冲突仲裁（矛盾检测）

    特性：
    - 异步并发调用三层API
    - 异常隔离（熔断机制）
    - 实体校验失败时立即终止
    - 矛盾点自动检测
    """

    def __init__(self):
        # 初始化各层调度器
        self.entity_orchestrator = EntityVerificationOrchestrator()
        self.sentiment_orchestrator = SentimentSearchOrchestrator()
        self.risk_orchestrator = RiskSearchOrchestrator()

        # AI冲突检测器
        self.conflict_detector = ConflictDetector()

    async def generate_report(self, company_name: str) -> CompanyReport:
        """
        生成完整的企业尽调报告

        :param company_name: 公司名称（可以是简称、关键词）
        :return: CompanyReport 统一报告DTO
        """
        report = CompanyReport(
            original_query=company_name,
            search_timestamp=datetime.now().isoformat()
        )

        # ========== 第一层：实体校验 ==========
        # 必须先验证这是不是一个真实的企业
        entity_info = await self.entity_orchestrator.verify(company_name)
        report.entity = entity_info
        report.api_status["entity"] = "success" if entity_info.is_valid else "not_found"

        if not entity_info.is_valid:
            # 实体校验失败，立即终止后续搜索
            report.terminated = True
            report.termination_reason = entity_info.error_message or "未查询到该企业主体"
            report.errors.append(f"【第一层-工商校验】终止：{report.termination_reason}")
            return report

        # 实体校验通过，使用标准化名称
        report.normalized_name = entity_info.company_name

        # ========== 第二层 + 第三层：并发获取舆情和风险 ==========
        # 使用asyncio.gather同时发起两个请求，不增加加载时间

        sentiment_task = self._safe_get_sentiments(
            entity_info.company_name,
            entity_info.unified_credit_code
        )
        risk_task = self._safe_get_risks(
            entity_info.company_name,
            entity_info.unified_credit_code
        )

        sentiments, risks = await asyncio.gather(
            sentiment_task,
            risk_task,
            return_exceptions=True
        )

        # 处理舆情结果
        if isinstance(sentiments, list):
            report.sentiments = sentiments
            report.api_status["sentiments"] = "success"
            report.total_sentiment_count = len(sentiments)
        else:
            report.api_status["sentiments"] = "failed"
            report.errors.append(f"【第二层-舆情搜索】异常: {str(sentiments)}")

        # 处理风险结果
        if isinstance(risks, list):
            report.risks = risks
            report.api_status["risks"] = "success"
            report.total_risk_count = len(risks)
        else:
            report.api_status["risks"] = "failed"
            report.errors.append(f"【第三层-风险核查】异常: {str(risks)}")

        # ========== 第四层：冲突检测与仲裁 ==========
        if report.entity.is_valid:
            report.conflicts = self.conflict_detector.detect_conflicts(
                entity=report.entity,
                sentiments=report.sentiments,
                risks=report.risks
            )

        return report

    async def _safe_get_sentiments(
        self,
        company_name: str,
        unified_credit_code: str
    ) -> List[SentimentItem]:
        """
        安全获取舆情数据（带异常隔离）
        即使此API失败，也不影响其他数据展示
        """
        try:
            return await self.sentiment_orchestrator.search(
                company_name,
                unified_credit_code
            )
        except Exception as e:
            try:
                print(f"[舆情搜索异常] {e}")
            except:
                pass
            return []

    async def _safe_get_risks(
        self,
        company_name: str,
        unified_credit_code: str
    ) -> List[RiskItem]:
        """
        安全获取风险数据（带异常隔离）
        即使此API失败，也不影响其他数据展示
        """
        try:
            return await self.risk_orchestrator.search(
                company_name,
                unified_credit_code
            )
        except Exception as e:
            try:
                print(f"[风险核查异常] {e}")
            except:
                pass
            return []


class ConflictDetector:
    """
    冲突检测器

    职责：
    - 对比不同来源的数据
    - 识别矛盾点
    - 生成矛盾描述（AI风格的矛盾点提取）

    注意：此模块只提取矛盾，不编造"统一答案"
    """

    # 薪资相关关键词
    SALARY_PATTERNS = [
        r'(\d+(?:\.\d+)?[kK]-\d+(?:\.\d+)?[kK])',
        r'(月薪|年薪)\s*(\d+(?:\.\d+)?(?:万)?)',
        r'(工资|薪资)\s*(约)?(\d+(?:\.\d+)?(?:万)?(?:k|K)?)'
    ]

    # 裁员相关关键词
    LAYOFF_PATTERNS = [
        r'裁员',
        r'优化',
        r'辞退',
        r'降薪',
        r'缩.?编',
        r'人员调整'
    ]

    # 资本相关关键词
    CAPITAL_PATTERNS = [
        r'注册资本.*?(\d+(?:\.\d+)?(?:万|亿)?)',
        r'实缴资本.*?(\d+(?:\.\d+)?(?:万|亿)?)',
        r'融资.*?(A轮|B轮|C轮|D轮|Pre-IPO|上市)'
    ]

    def detect_conflicts(
        self,
        entity: EntityInfo,
        sentiments: List[SentimentItem],
        risks: List[RiskItem]
    ) -> List[ConflictItem]:
        """
        检测数据冲突
        """
        conflicts = []

        # 冲突1：薪资传闻 vs 资本实力
        salary_conflict = self._check_salary_vs_capital(entity, sentiments)
        if salary_conflict:
            conflicts.append(salary_conflict)

        # 冲突2：裁员传闻 vs 公司状态
        layoff_conflict = self._check_layoff_vs_status(entity, sentiments)
        if layoff_conflict:
            conflicts.append(layoff_conflict)

        # 冲突3：网络评价 vs 司法风险
        risk_conflict = self._check_reputation_vs_risk(sentiments, risks)
        if risk_conflict:
            conflicts.append(risk_conflict)

        # 冲突4：薪资差异（不同来源说法不一）
        salary_diff_conflict = self._check_salary_discrepancy(sentiments)
        if salary_diff_conflict:
            conflicts.append(salary_diff_conflict)

        return conflicts

    def _check_salary_vs_capital(
        self,
        entity: EntityInfo,
        sentiments: List[SentimentItem]
    ) -> Optional[ConflictItem]:
        """检测薪资传闻与资本实力的矛盾"""
        # 从舆情中提取薪资信息
        mentioned_salaries = []
        for s in sentiments:
            if s.mentioned_salary:
                mentioned_salaries.append(s.mentioned_salary)

        if not mentioned_salaries or not entity.registered_capital:
            return None

        # 检查是否有"低薪资 + 高资本"或"高薪资 + 零资本"的矛盾
        salary_text = " ".join(mentioned_salaries)

        # 提取数字判断
        try:
            salary_nums = re.findall(r'(\d+(?:\.\d+)?)', salary_text)
            if salary_nums:
                avg_salary = sum(float(n) for n in salary_nums) / len(salary_nums)
            else:
                return None
        except:
            return None

        # 注册资本
        capital_text = entity.registered_capital
        capital_nums = re.findall(r'(\d+(?:\.\d+)?)', capital_text)
        if not capital_nums:
            return None

        try:
            capital = float(capital_nums[0])
            # 如果提到"万"则乘以10000
            if '万' in capital_text:
                capital *= 10000
            elif '亿' in capital_text:
                capital *= 100000000
        except:
            return None

        # 检测矛盾
        # 情况1：网络说薪资很低，但注册资本很高
        if avg_salary < 15 and capital > 100000000:  # 薪资<15k，资本>1亿
            return ConflictItem(
                category="薪资与资本",
                description="网络公开讨论中提及薪资较低，但工商信息显示注册资本较高。两者可能存在矛盾，请用户自行核实具体情况。",
                sources=[
                    {"source": "网络舆情", "content": f"薪资: {', '.join(mentioned_salaries)}"},
                    {"source": "工商信息", "content": f"注册资本: {entity.registered_capital}"}
                ],
                resolution_hint="薪资水平受岗位、地区、工作年限等因素影响较大，建议参考同岗位同地区的市场水平。"
            )

        # 情况2：实缴资本为0
        if entity.paid_in_capital and '0' in entity.paid_in_capital:
            return ConflictItem(
                category="资本实缴",
                description="网络有薪资相关讨论，但工商信息显示实缴资本为0或未明确。需注意该公司可能存在注册资本认缴但未实缴的情况。",
                sources=[
                    {"source": "网络舆情", "content": f"薪资: {', '.join(mentioned_salaries)}"},
                    {"source": "工商信息", "content": f"实缴资本: {entity.paid_in_capital}"}
                ],
                resolution_hint="实缴资本与公司实际运营资金无直接关联，员工薪资由公司实际经营状况决定。"
            )

        return None

    def _check_layoff_vs_status(
        self,
        entity: EntityInfo,
        sentiments: List[SentimentItem]
    ) -> Optional[ConflictItem]:
        """检测裁员传闻与公司状态的矛盾"""
        # 检查舆情中是否有裁员相关
        has_layoff_mention = False
        layoff_contents = []

        for s in sentiments:
            for pattern in self.LAYOFF_PATTERNS:
                if re.search(pattern, s.content):
                    has_layoff_mention = True
                    layoff_contents.append(s.summary)
                    break

        if not has_layoff_mention:
            return None

        # 检查公司状态
        status = entity.company_status.lower()
        fund_status = getattr(entity, "funding_status", "")
        is_ipo = "上市" in fund_status if fund_status else False
        # 裁员传闻 + 上市公司
        if is_ipo:
            return ConflictItem(
                category="经营状况矛盾",
                description="网络有裁员/优化相关传闻，但公司显示为上市公司。上市公司通常有定期披露义务，重大裁员需公告。如传闻属实，可能是业务调整而非经营困难。",
                sources=[
                    {"source": "网络舆情", "content": " / ".join(layoff_contents[:2])},
                    {"source": "工商信息", "content": f"上市状态: {getattr(entity, "funding_status", "")}"}
                ],
                resolution_hint="建议查看公司最近财报和公告，了解真实经营状况。"
            )

        # 裁员传闻 + 存续状态
        if '存续' in entity.company_status:
            return ConflictItem(
                category="经营状况矛盾",
                description="网络有裁员相关传闻，但工商登记状态显示为存续。需注意：'存续'仅表示工商登记有效，不代表经营正常。",
                sources=[
                    {"source": "网络舆情", "content": " / ".join(layoff_contents[:2])},
                    {"source": "工商信息", "content": f"企业状态: {entity.company_status}"}
                ],
                resolution_hint="建议多方面核实公司当前经营状况。"
            )

        return None

    def _check_reputation_vs_risk(
        self,
        sentiments: List[SentimentItem],
        risks: List[RiskItem]
    ) -> Optional[ConflictItem]:
        """检测口碑与司法风险的矛盾"""
        if not risks:
            return None

        # 计算舆情平均情感
        positive_count = sum(1 for s in sentiments if s.sentiment == "positive")
        negative_count = sum(1 for s in sentiments if s.sentiment == "negative")

        # 有高风险案件
        high_risk_cases = [r for r in risks if r.risk_level == "高"]

        if high_risk_cases and positive_count > negative_count:
            return ConflictItem(
                category="口碑与风险矛盾",
                description="网络评价整体偏正面，但存在高风险司法案件记录。请注意：员工评价多反映工作体验，司法记录反映合规风险，两者维度不同。",
                sources=[
                    {"source": "网络口碑", "content": f"正面评价{positive_count}条 / 负面评价{negative_count}条"},
                    {"source": "司法风险", "content": f"高风险案件{len(high_risk_cases)}起"}
                ],
                resolution_hint="高风险司法案件需具体分析类型和影响范围。"
            )

        return None

    def _check_salary_discrepancy(
        self,
        sentiments: List[SentimentItem]
    ) -> Optional[ConflictItem]:
        """检测不同来源薪资差异"""
        salary_data = []

        for s in sentiments:
            if s.mentioned_salary:
                salary_data.append({
                    "salary": s.mentioned_salary,
                    "source": s.source_name,
                    "url": s.url
                })

        if len(salary_data) < 2:
            return None

        # 提取所有薪资数字
        all_salaries = []
        for item in salary_data:
            nums = re.findall(r'(\d+(?:\.\d+)?)', item["salary"])
            for n in nums:
                try:
                    val = float(n)
                    # 统一单位（万）
                    if '万' in item["salary"]:
                        val *= 10000
                    elif 'k' in item["salary"].lower() or 'K' in item["salary"]:
                        val *= 1000
                    all_salaries.append((val, item))
                except:
                    pass

        if len(all_salaries) < 2:
            return None

        # 计算差异
        min_salary = min(s[0] for s in all_salaries)
        max_salary = max(s[0] for s in all_salaries)

        # 如果差异超过2倍，视为有矛盾
        if max_salary > 0 and min_salary > 0 and max_salary / min_salary > 2:
            return ConflictItem(
                category="薪资信息差异",
                description=f"不同来源对薪资的描述存在较大差异，最低{self._format_salary(min_salary)}，最高{self._format_salary(max_salary)}。薪资差异可能因岗位、地区、年限、补贴等因素造成。",
                sources=[
                    {"source": d[1]["source"], "content": d[1]["salary"]}
                    for d in all_salaries[:3]
                ],
                resolution_hint="建议查看多个来源的具体岗位描述，了解薪资结构。"
            )

        return None

    def _format_salary(self, amount: float) -> str:
        """格式化薪资显示"""
        if amount >= 10000:
            return f"{amount/10000:.1f}万"
        return f"{amount:.0f}"

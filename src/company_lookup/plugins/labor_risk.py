from .base import BasePlugin

class LaborRiskPlugin(BasePlugin):
    @property
    def name(self):
        return "labor_risk"

    @property
    def display_name(self):
        return "劳动风险"

    def fetch(self, company_name, credit_code=None):
        # 模拟裁判文书数据，实际应爬取 wenshu.court.gov.cn
        cases = [
            {"date": "2025-01-15", "type": "违法解除劳动合同", "result": "原告胜诉", "amount": "5万"},
            {"date": "2024-09-10", "type": "未足额支付工资", "result": "调解结案", "amount": "2万"}
        ]
        return {
            "total_cases": len(cases),
            "cases": cases,
            "trend": "近三年劳动纠纷数量持平",
            "risk_level": "中" if len(cases) > 1 else "低",
            "notice": "建议关注入职后的社保缴纳情况"
        }
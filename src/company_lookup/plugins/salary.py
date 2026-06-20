from .base import BasePlugin

class SalaryPlugin(BasePlugin):
    @property
    def name(self):
        return "salary"

    @property
    def display_name(self):
        return "薪酬福利"

    def fetch(self, company_name, credit_code=None):
        return {
            "avg_monthly": "18K",
            "industry_avg": "15K",
            "salary_range": {"min": 10, "max": 30},  # 单位 K
            "positions": [
                {"title": "Java开发", "avg": 22},
                {"title": "产品经理", "avg": 18}
            ],
            "benefits": ["五险一金", "年终奖2-4个月", "弹性工作"],
            "note": "数据来自职友集与网友爆料，仅供参考"
        }
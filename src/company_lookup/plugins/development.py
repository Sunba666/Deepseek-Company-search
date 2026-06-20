from .base import BasePlugin

class DevelopmentPlugin(BasePlugin):
    @property
    def name(self):
        return "development"

    @property
    def display_name(self):
        return "发展前景"

    def fetch(self, company_name, credit_code=None):
        return {
            "financing": "B轮，累计融资3亿元",
            "latest_investors": ["红杉中国", "经纬中国"],
            "job_growth": "近6个月新增岗位+25%",
            "tech_team_size": "150人",
            "news_sentiment": "正面",
            "source": "IT桔子/新闻聚合"
        }
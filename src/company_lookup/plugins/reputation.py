from .base import BasePlugin

class ReputationPlugin(BasePlugin):
    @property
    def name(self):
        return "reputation"

    @property
    def display_name(self):
        return "员工口碑"

    def fetch(self, company_name, credit_code=None):
        return {
            "rating": 3.5,            # 1-5
            "recommend_rate": 0.62,   # 内部推荐率
            "ceo_approval": 0.75,
            "pros": ["同事关系融洽", "加班有调休"],
            "cons": ["晋升慢", "薪资竞争力低"],
            "review_count": 128,
            "source": "看准网/脉脉"
        }
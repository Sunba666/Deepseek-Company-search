from .base import BasePlugin

class InterviewPlugin(BasePlugin):
    @property
    def name(self):
        return "interview"

    @property
    def display_name(self):
        return "面试经验"

    def fetch(self, company_name, credit_code=None):
        return {
            "process": "3轮技术面 + 1轮HR",
            "difficulty": "中等",
            "common_questions": [
                "项目中最有挑战的部分？",
                "系统设计：高并发秒杀",
                "MySQL 优化案例"
            ],
            "feedback": "面试官专业，流程快，但HR薪资压价严重",
            "source": "牛客/看准"
        }
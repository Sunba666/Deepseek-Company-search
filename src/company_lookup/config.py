# -*- coding: utf-8 -*-
import os
from pathlib import Path


class Config:
  """应用配置基类"""

  BASE_DIR = Path(__file__).resolve().parent
  SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
  JSON_AS_ASCII = False
  RESTFUL_JSON = {"ensure_ascii": False}
  TEMPLATES_AUTO_RELOAD = True
  SESSION_COOKIE_SAMESITE = "Lax"
  SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
  PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", "3600"))

  DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
  COMPANY_INFO_API = os.getenv("COMPANY_INFO_API", "")
  LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
  DEBUG = True


class ProductionConfig(Config):
  DEBUG = False
  TEMPLATES_AUTO_RELOAD = False


config_by_name = {
  "development": DevelopmentConfig,
  "production": ProductionConfig,
  "default": DevelopmentConfig,
}


# ========== 外部查询链接 ==========
EXTERNAL_LINKS = {
    "tianyancha": {
        "name": "天眼查",
        "icon": "bi bi-building",
        "url": "https://www.tianyancha.com/search?key={company}",
    },
    "qichacha": {
        "name": "企查查",
        "icon": "bi bi-shield-check",
        "url": "https://www.qichacha.com/search?key={company}",
    },
    "boss_zhipin": {
        "name": "BOSS直聘",
        "icon": "bi bi-briefcase",
        "url": "https://www.zhipin.com/web/geek/jobs?query={company}",
    },
    "maimai": {
        "name": "脉脉",
        "icon": "bi bi-chat-dots",
        "url": "https://maimai.cn/search?keyword={company}",
    },
    "kanzhun": {
        "name": "看准网",
        "icon": "bi bi-star",
        "url": "https://www.kanzhun.com/search/?key={company}",
    },
    "baidu": {
        "name": "百度搜索",
        "icon": "bi bi-search",
        "url": "https://www.baidu.com/s?wd={company}",
    },
    "zhihu": {
        "name": "知乎",
        "icon": "bi bi-question-circle",
        "url": "https://www.zhihu.com/search?type=content&q={company}",
    },
}

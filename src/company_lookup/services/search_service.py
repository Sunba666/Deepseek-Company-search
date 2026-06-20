# -*- coding: utf-8 -*-
"""企业搜索与实体校验。"""
import logging
import re

from ..ai_analyzer import COMPANY_NAMES
from ..services.entity_resolver import BRAND_MAPPING

logger = logging.getLogger(__name__)

COMPANY_SUFFIXES = (
  "公司",
  "集团",
  "股份",
  "有限",
  "企业",
  "厂",
  "中心",
  "局",
  "所",
  "社",
  "行",
  "院",
  "馆",
  "店",
  "铺",
  "科技",
  "网络",
  "控股",
  "投资",
  "银行",
  "证券",
  "保险",
  "基金",
  "Corp",
  "Inc",
  "Ltd",
  "Co.",
  "Group",
  "Holdings",
)

# 常见人名（明确拦截）
BLOCKED_PERSON_NAMES = frozenset(
  {
    "张三",
    "李四",
    "王五",
    "赵六",
    "刘洋",
    "李娜",
    "王伟",
    "王芳",
    "李伟",
    "张敏",
    "陈静",
    "杨洋",
  }
)

# 常见中文姓氏（用于短词人名特征判断）
COMMON_SURNAMES = frozenset(
  "张王李赵刘陈杨黄周吴徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤欧阳司马"
)

INVALID_COMPANY_MESSAGE = (
  "未匹配到公开企业主体。请确认输入的是完整的公司全称（如「华为技术有限公司」）。"
)


def _normalize(query: str) -> str:
  """规范化查询字符串"""
  return (query or "").strip()


def _matches_known_company(query: str) -> bool:
  """检查是否匹配已知公司（含不区分大小写的品牌名匹配）"""
  try:
    q = _normalize(query)
    if len(q) < 2:
      return False
    ql = q.lower()
    for name in COMPANY_NAMES:
      nl = name.lower()
      if q == name or ql == nl:
        return True
      if len(q) >= 2 and (q in name or name in q):
        return True
    # 检查 BRAND_MAPPING 品牌白名单（不区分大小写）
    if q in BRAND_MAPPING:
      return True
    ql = q.lower()
    for brand in BRAND_MAPPING:
      if ql == brand.lower():
        return True
      if q in brand or brand in q:
        return True
    return False
  except Exception as e:
    logger.error(f"匹配已知公司失败: {e}", exc_info=True)
    return False


def _looks_like_person_name(query: str) -> bool:
  """检查是否像人名"""
  try:
    q = _normalize(query)
    if q in BLOCKED_PERSON_NAMES:
      return True
    # 2-3 个纯汉字、无企业后缀、不在白名单 → 高概率为人名
    if re.fullmatch(r"[\u4e00-\u9fff]{2,3}", q):
      if not any(suffix in q for suffix in COMPANY_SUFFIXES):
        if q[0] in COMMON_SURNAMES and not _matches_known_company(q):
          return True
    return False
  except Exception as e:
    logger.error(f"判断人名失败: {e}", exc_info=True)
    return False


def is_likely_company_name(query: str) -> bool:
  """
  硬规则校验：判断输入是否为合格的企业名称。
  返回 True 继续查询，False 直接拦截。
  
  :param query: 查询字符串
  :return: 是否为合格的企业名称
  """
  try:
    q = _normalize(query)

    if len(q) < 2:
      return False

    if _looks_like_person_name(q):
      return False

    if _matches_known_company(q):
      return True

    if any(suffix in q for suffix in COMPANY_SUFFIXES):
      return True

    if re.fullmatch(r"^[A-Za-z&\s\.]{2,}$", q):
      return True

    return False
  except Exception as e:
    logger.error(f"企业名称校验失败: {e}", exc_info=True)
    return False


def build_forced_search_query(query: str) -> str:
  """
  为外部搜索 API 强制加上企业语境，降低命中个人新闻的概率。
  
  :param query: 查询字符串
  :return: 增强后的搜索词
  """
  try:
    q = _normalize(query).replace('"', "")
    return f'"{q}" AND (公司 OR 集团 OR 员工 OR 企业)'
  except Exception as e:
    logger.error(f"构建搜索查询失败: {e}", exc_info=True)
    return query


def validation_error_payload(query: str) -> dict:
  """
  生成校验错误响应
  
  :param query: 查询字符串
  :return: 错误响应字典
  """
  return {
    "error": INVALID_COMPANY_MESSAGE,
    "invalid_entity": True,
    "query": _normalize(query),
  }

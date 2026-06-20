# -*- coding: utf-8 -*-
import logging
from ..ai_analyzer import query_company_info as _query_company_info
from ..ai_analyzer import suggest_companies as _suggest_companies
from ..data_store import clear_cache, delete_cache, get_cache, set_cache
from .search_service import is_likely_company_name, validation_error_payload

logger = logging.getLogger(__name__)

__all__ = [
  "query_company_info",
  "suggest_companies",
  "clear_cache",
  "get_cache",
  "set_cache",
  "delete_cache",
  "is_likely_company_name",
  "validation_error_payload",
]


def query_company_info(company_name, force_refresh=False):
  """
  查询公司信息
  
  :param company_name: 公司名称
  :param force_refresh: 是否强制刷新缓存
  :return: 公司信息字典或错误信息
  """
  try:
    name = (company_name or "").strip()
    if not is_likely_company_name(name):
      return validation_error_payload(name)
    return _query_company_info(name, force_refresh=force_refresh)
  except Exception as e:
    logger.error(f"查询公司信息失败: {e}", exc_info=True)
    return {"error": f"查询公司信息失败: {str(e)}"}


def suggest_companies(query):
  """
  推荐公司
  
  :param query: 查询关键词
  :return: 公司名称列表
  """
  try:
    q = (query or "").strip()
    if not q or not is_likely_company_name(q):
      return []
    return _suggest_companies(query)
  except Exception as e:
    logger.error(f"推荐公司失败: {e}", exc_info=True)
    return []

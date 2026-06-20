# -*- coding: utf-8 -*-
import logging
import re

logger = logging.getLogger(__name__)


def parse_offer_text(offer_text: str) -> dict:
    """
    解析 offer 文本为结构化字典
    
    :param offer_text: offer 文本内容
    :return: 结构化的 offer 字典，包含 company_name, position, monthly_salary 等字段
    """
    try:
        offer = {
            "raw_text": offer_text,
            "company_name": "",
            "position": "",
            "monthly_salary": "",
            "annual_salary": "",
            "benefits": "",
            "location": "",
            "commute": "",
        }

        parts = re.split(r'[,，]', offer_text)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            words = part.split()
            if words and not offer["company_name"]:
                offer["company_name"] = words[0]
                if len(words) > 1:
                    offer["position"] = words[1]
            elif "月薪" in part:
                offer["monthly_salary"] = part
            elif "K" in part or "k" in part:
                if not offer["monthly_salary"]:
                    offer["monthly_salary"] = part
            elif "薪" in part and "月薪" not in part:
                offer["annual_salary"] = part
            elif "公积金" in part:
                offer["benefits"] = part
            elif "福利" in part:
                offer["benefits"] = part
            elif "通勤" in part:
                offer["commute"] = part
            elif not offer["location"]:
                offer["location"] = part

        return offer
    except Exception as e:
        logger.error(f"解析offer文本失败: {e}", exc_info=True)
        return {"error": f"解析失败: {str(e)}"}

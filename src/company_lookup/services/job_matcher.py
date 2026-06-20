# -*- coding: utf-8 -*-
"""
求职匹配引擎 — 根据用户偏好推荐知识库中的公司。
输入：行业偏好、城市、薪资期望、风险容忍度
输出：匹配评分 Top N 公司 + 推荐理由
"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class JobMatcher:
    """求职匹配引擎。"""

    def __init__(self):
        self._label_map = {
            "互联网": ["互联网", "软件", "电商", "金融科技"],
            "游戏": ["游戏"],
            "AI": ["AI", "人工智能"],
            "新能源": ["新能源"],
            "生物医药": ["生物医药", "生物科技"],
            "硬件/制造": ["半导体", "制造", "硬件"],
            "金融": ["金融科技"],
        }

    def match(self, preferences: Dict, top_n: int = 10) -> Dict:
        """
        匹配流程：
        1. 从知识库获取所有公司
        2. 按行业过滤（如果指定）
        3. 按城市过滤（如果指定）
        4. 计算综合评分
        5. 返回 Top N
        """
        from ..services.knowledge_db import _get_conn
        import sqlite3

        industry_pref = preferences.get("industry", "")
        province_pref = preferences.get("province", "")
        city_pref = preferences.get("city", "")
        salary_pref = preferences.get("min_salary", 0)  # 最低月薪 K
        risk_tolerance = preferences.get("risk_tolerance", "中")  # 高/中/低
        growth_stage = preferences.get("growth_stage", "")  # 初创/成长/成熟

        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        try:
            # 取所有公司 + 蒸馏数据
            companies = conn.execute("""
                SELECT c.id, c.canonical_name, c.industry, c.province, c.city, c.scale, c.hotness
                FROM companies c
                ORDER BY c.id
            """).fetchall()

            scored = []
            for c in companies:
                # 省份过滤：指定了省份时跳过非该省份公司
                if province_pref:
                    company_prov = c["province"] or ""
                    if not company_prov or not (province_pref in company_prov or company_prov in province_pref):
                        continue

                score, reasons = self._score_company(c, conn, industry_pref, province_pref, city_pref,
                                                      salary_pref, risk_tolerance, growth_stage)
                if score > 0:
                    # 获取蒸馏 one_liner
                    one_liner = ""
                    row = conn.execute(
                        "SELECT content FROM company_data WHERE company_id=? AND data_type='distilled'",
                        (c["id"],)
                    ).fetchone()
                    if row:
                        try:
                            parsed = json.loads(row["content"])
                            one_liner = parsed.get("one_liner", "")
                        except (json.JSONDecodeError, TypeError):
                            pass

                    scored.append({
                        "id": c["id"],
                        "name": c["canonical_name"],
                        "industry": c["industry"] or "",
                        "province": c["province"] or "",
                        "city": c["city"] or "",
                        "scale": c["scale"] or "",
                        "hotness": c["hotness"] or "medium",
                        "one_liner": one_liner,
                        "score": round(score, 1),
                        "reasons": reasons[:3],  # top 3 理由
                    })

            # 按分数排序
            scored.sort(key=lambda x: x["score"], reverse=True)

            return {
                "preferences": preferences,
                "total_matched": len(scored),
                "results": scored[:top_n],
            }
        finally:
            conn.close()

    def _score_company(self, company: sqlite3.Row, conn,
                       industry_pref: str, province_pref: str, city_pref: str,
                       salary_pref: int, risk_tolerance: str,
                       growth_stage: str) -> Tuple[float, List[str]]:
        """计算单公司匹配分数。"""
        score = 0.0
        reasons = []

        # ── 1. 行业匹配 (权重 30%) ──
        if industry_pref:
            industry_match = self._industry_matches(industry_pref, company["industry"] or "")
            if industry_match:
                score += 30
                reasons.append("行业匹配")
        else:
            score += 20  # 未指定行业则给基础分

        # ── 2. 城市/省份匹配 (权重 20%) ──
        if city_pref:
            matched = False
            placeholders = ["暂无公开数据", "未公开", "未知", "无"]
            if company["city"] and company["city"] not in placeholders:
                if city_pref in company["city"] or company["city"] in city_pref:
                    matched = True
            if not matched and company["province"]:
                if city_pref in company["province"] or company["province"] in city_pref:
                    matched = True
            if matched:
                score += 20
                reasons.append("城市匹配")
        elif province_pref:
            # 省份过滤：公司所在省份与用户选择省份匹配
            if company["province"] and (province_pref in company["province"] or company["province"] in province_pref):
                score += 20
                reasons.append("省份匹配")
        else:
            score += 10

        # ── 3. 薪资匹配 (权重 20%) ──
        if salary_pref > 0:
            salary_score, salary_reason = self._get_salary_score(company["id"], conn, salary_pref)
            score += salary_score
            if salary_reason:
                reasons.append(salary_reason)
        else:
            score += 10

        # ── 4. 风险容忍度 (权重 15%) ──
        risk_score, risk_reason = self._get_risk_score(company["id"], conn, risk_tolerance)
        score += risk_score
        if risk_reason:
            reasons.append(risk_reason)

        # ── 5. 热度/规模 (权重 15%) ──
        hot_score, hot_reason = self._get_hotness_score(company, growth_stage)
        score += hot_score
        if hot_reason:
            reasons.append(hot_reason)

        return score, reasons

    def _industry_matches(self, pref: str, company_ind: str) -> bool:
        """检查行业是否匹配。支持分类映射。"""
        if not company_ind:
            return False
        pref_lower = pref.lower()
        ind_lower = company_ind.lower()

        # 精确匹配
        if pref_lower == ind_lower:
            return True
        if pref_lower in ind_lower or ind_lower in pref_lower:
            return True

        # 分类映射
        pref_labels = self._label_map.get(pref, [pref])
        for label in pref_labels:
            if label.lower() in ind_lower or ind_lower in label.lower():
                return True

        return False

    def _get_salary_score(self, company_id: int, conn, min_salary_k: int) -> Tuple[float, str]:
        """从薪资维度计算匹配分。"""
        row = conn.execute(
            "SELECT content FROM company_data WHERE company_id=? AND data_type='salary'",
            (company_id,)
        ).fetchone()
        if not row:
            return (8, "")  # 无数据给基础分

        try:
            data = json.loads(row["content"])
            # 尝试获取各字段
            monthly = data.get("monthly_avg", data.get("average", data.get("avg", 0)))
            if monthly:
                monthly_val = float(monthly)
                if monthly_val >= min_salary_k * 1000:
                    ratio = monthly_val / (min_salary_k * 1000)
                    if ratio >= 1.5:
                        return (20, "薪资有竞争力")
                    elif ratio >= 1.0:
                        return (18, "薪资达标")
                    else:
                        return (5, "")
                elif monthly_val >= min_salary_k * 1000 * 0.8:
                    return (10, "薪资略低")
                else:
                    return (3, "薪资偏低")
        except (ValueError, TypeError, json.JSONDecodeError):
            pass
        return (8, "")

    def _get_risk_score(self, company_id: int, conn, tolerance: str) -> Tuple[float, str]:
        """从风险维度计算匹配分。"""
        row = conn.execute(
            "SELECT content FROM company_data WHERE company_id=? AND data_type='distilled'",
            (company_id,)
        ).fetchone()
        if not row:
            return (10, "")

        try:
            data = json.loads(row["content"])
            risk_summary = data.get("risk_summary", "")
            if not risk_summary or risk_summary == "暂无已知风险":
                return (15, "风险低")

            # 根据风险描述判断级别
            risk_lower = risk_summary.lower()
            has_high_risk = any(kw in risk_lower for kw in ["严重", "大量", "高风险", "破产", "退市", "巨额"])
            has_medium_risk = any(kw in risk_lower for kw in ["诉讼", "纠纷", "亏损", "裁员", "下滑"])

            if tolerance == "高":
                return (15, "") if not has_high_risk else (5, "存在高风险")
            elif tolerance == "低":
                return (15, "风险低") if not has_high_risk and not has_medium_risk else (8, "有一定风险")
            else:  # 中
                return (15, "") if has_medium_risk or has_high_risk else (12, "风险较低")
        except (json.JSONDecodeError, KeyError):
            pass
        return (10, "")

    def _get_hotness_score(self, company: sqlite3.Row, growth_stage: str) -> Tuple[float, str]:
        """根据公司热度和规模评分。"""
        hotness = company["hotness"] or "medium"
        scale = company["scale"] or ""

        score = 0
        reason = ""

        if not growth_stage:
            score = 10
        elif growth_stage == "初创":
            if hotness == "low":
                score = 15
                reason = "小众公司有潜力"
            elif scale and "创业" in scale:
                score = 13
                reason = "创业型公司"
            else:
                score = 8
        elif growth_stage == "成长":
            if hotness == "medium":
                score = 14
                reason = "成长型公司"
            elif scale and "中型" in scale:
                score = 13
                reason = "中型企业"
            else:
                score = 10
        elif growth_stage == "成熟":
            if hotness == "high":
                score = 15
                reason = "成熟大厂"
            elif scale and "大型" in scale:
                score = 14
                reason = "大型企业"
            else:
                score = 8

        return (score, reason)


# 全局单例
job_matcher = JobMatcher()

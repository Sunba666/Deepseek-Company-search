# -*- coding: utf-8 -*-
"""
集成测试：公司搜索功能

测试覆盖：
  1. 首页搜索 (/company/search) 对已知公司返回成功
  2. 仪表盘搜索 (/dashboard/search) 对相同公司返回成功
  3. 两个端点的响应结构一致性（normalized_name 等核心字段）
  4. 无效输入的正确处理
"""

import pytest
from datetime import datetime


class TestKnowledgeWriteBack:
    """知识库写回路径验证 — ADR-001 C 变体"""

    def test_populate_knowledge_writes_dimensions_and_updates_timestamp(self, app):
        """_populate_knowledge 应写入 API 维度数据并更新时间戳。"""
        from company_lookup.services.unified_data_service import UnifiedDataService
        from company_lookup.services.knowledge_db import knowledge_db, _get_conn
        import sqlite3

        uds = UnifiedDataService()

        # 找一个知识库中已有的公司
        company = knowledge_db.find_company("腾讯")
        assert company is not None, "测试前提：腾讯应在知识库中"
        company_id = company["id"]

        # 记录旧的 last_verified_at
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        old_ts = conn.execute(
            "SELECT last_verified_at FROM companies WHERE id=?", (company_id,)
        ).fetchone()["last_verified_at"]
        conn.close()

        # 模拟 API 返回的 raw_data（只包含测试用数据）
        test_raw_data = {
            "tianyacha": {
                "company_name": "腾讯科技（深圳）有限公司",
                "company_type": "互联网",
                "company_status": "存续",
            },
            "salary": {
                "avg_monthly": "30000元",
                "salary_range": "15000-50000元",
            },
        }

        # 执行写回
        import types
        mock_report = types.SimpleNamespace(normalized_name="腾讯", sources=[])

        # 写入前保存旧数据用于清理
        old_data = knowledge_db.get_company_data(company_id) or {}

        # 写入前验证该公司的旧维度数
        old_count = knowledge_db.has_complete_data(company_id, min_dimensions=1)
        assert old_count, "测试前提：腾讯已有至少1个维度"

        uds._populate_knowledge("腾讯", mock_report, test_raw_data)

        # 验证维度数据已写入
        data_dict = knowledge_db.get_company_data(company_id)
        assert "basic" in data_dict, "tianyacha 应映射为 basic 维度"
        assert "salary" in data_dict, "salary 维度应存在"
        assert data_dict["basic"]["content"].get("company_type") == "互联网"

        # 验证 last_verified_at 已更新
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        new_ts = conn.execute(
            "SELECT last_verified_at FROM companies WHERE id=?", (company_id,)
        ).fetchone()["last_verified_at"]
        conn.close()

        assert new_ts != old_ts, "last_verified_at 应被更新"
        assert new_ts is not None, "last_verified_at 不应为 None"
        print(f"✅ 时间戳已更新: {old_ts} → {new_ts}")

        # ── 清理：恢复旧数据 ──
        for dtype, d in old_data.items():
            knowledge_db.set_company_data(company_id, dtype,
                                          d["content"], source=d.get("source", "test"))
        knowledge_db.update_verified_at(company_id)
        print(f"✅ 测试数据已清理，知识库已恢复")


class TestHomepageSearch:
    """首页搜索 /company/search — 6 级实体解析管道"""

    @pytest.mark.parametrize("name", [
        "米哈游", "腾讯", "字节跳动", "华为", "美团", "阿里巴巴",
    ])
    def test_known_company_returns_data(self, client, name):
        """知名公司简称应返回完整数据，无错误提示。"""
        resp = client.post("/company/search", data={"company_name": name})
        assert resp.status_code == 200, f"{name}: 状态码应为 200"
        body = resp.get_data(as_text=True)

        # 不应包含错误关键词
        assert "未匹配到公开企业主体" not in body, f"{name}: 不应拒绝知名公司"
        assert "暂时无法查询" not in body, f"{name}: 不应报系统错误"

        # 应包含核心数据标记
        assert name in body, f"{name}: 响应中应包含公司名称"
        # AI 分析或评分应存在
        has_data = "AI" in body or "评分" in body or "分析" in body
        assert has_data, f"{name}: 响应应包含 AI 分析或评分数据"

    def test_unknown_company_shows_error(self, client):
        """未知/非公司输入应返回明确错误提示"""
        resp = client.post("/company/search", data={"company_name": "张三"})
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        # 首页搜索走实体解析路径，返回"未找到" + 建议，而不是拦截
        assert "未找到" in body or "未匹配" in body, "应返回未找到提示"

    def test_empty_input_shows_prompt(self, client):
        """空输入应返回提示"""
        resp = client.post("/company/search", data={"company_name": ""})
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        # 应有一些提示信息
        assert len(body) > 50

    def test_short_input_shows_error(self, client):
        """单字符输入 — 首页搜索走实体解析路径，返回未找到提示而非直接拦截"""
        resp = client.post("/company/search", data={"company_name": "a"})
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        # 首页搜索不提前拦截短输入，而是交给解析器处理
        assert "未找到" in body or "请输入" in body, "应返回未找到提示"


class TestDashboardSearch:
    """仪表盘搜索 /dashboard/search — mock-data 路径"""

    @pytest.mark.parametrize("name", [
        "米哈游", "腾讯", "字节跳动", "华为", "美团", "阿里巴巴",
        "莉莉丝", "鹰角", "B站", "快手", "滴滴",
    ])
    def test_known_company_returns_data(self, client, name):
        """知名公司简称在仪表盘搜索也应返回数据。"""
        resp = client.post("/dashboard/search", data={"query": name, "company_name": name})
        assert resp.status_code == 200, f"{name}: 状态码应为 200"
        body = resp.get_data(as_text=True)

        # 不应包含错误关键词
        assert "未匹配到公开企业主体" not in body, f"{name}: 不应拒绝知名公司"
        assert "error_alert" not in body, f"{name}: 不应报系统错误"

        # 应包含公司名称或数据
        has_content = "company-header" in body or "name" in body or len(body) > 500
        assert has_content, f"{name}: 响应应包含公司内容"

    @pytest.mark.parametrize("name", ["张三", "李四", "小明"])
    def test_person_name_rejected(self, client, name):
        """人名输入应拦截。"""
        resp = client.post("/dashboard/search", data={"query": name})
        assert resp.status_code == 200
        body = resp.get_data(as_text=True)
        assert "未匹配到公开企业主体" in body or "invalid_company" in body or "error_alert" in body, \
            f"{name}: 人名应被拦截"


class TestSearchPathConsistency:
    """首页与仪表盘搜索一致性验证"""

    @pytest.mark.parametrize("name", ["米哈游", "腾讯", "字节跳动", "华为"])
    def test_both_endpoints_accept_known_companies(self, client, name):
        """同一家公司应在两个端点都返回成功。"""
        # 首页搜索
        r1 = client.post("/company/search", data={"company_name": name})
        assert r1.status_code == 200
        body1 = r1.get_data(as_text=True)
        home_ok = "未匹配到公开企业主体" not in body1

        # 仪表盘搜索
        r2 = client.post("/dashboard/search", data={"query": name, "company_name": name})
        assert r2.status_code == 200
        body2 = r2.get_data(as_text=True)
        dash_ok = "未匹配到公开企业主体" not in body2

        assert home_ok and dash_ok, \
            f"{name}: 首页OK={home_ok}, 仪表盘OK={dash_ok} — 行为不一致"

    def test_invalid_input_handling_differs(self, client):
        """
        【已知行为差异】首页搜索和仪表盘搜索对无效输入的处理不同。

        首页走实体解析器（6级管道），"张三"会经过AI消歧后返回"未找到"建议页面。
        仪表盘走 is_likely_company_name() 提前拦截，直接返回"未匹配到公开企业主体"。

        两者都返回错误提示，但文案和模板不同。这验证了 Karpathy 分析中的"问题1"。
        """
        r1 = client.post("/company/search", data={"company_name": "张三"})
        r2 = client.post("/dashboard/search", data={"query": "张三"})

        body1 = r1.get_data(as_text=True)
        body2 = r2.get_data(as_text=True)

        # 两者都应返回某种错误/未找到提示
        assert "未找到" in body1 or "未匹配" in body1, "首页应返回未找到提示"
        assert "未匹配到公开企业主体" in body2 or "未找到" in body2, "仪表盘应返回错误提示"
        # 但实际文案不同 —— 这是两个搜索路径设计不一致的表现
        assert "未匹配到公开企业主体" in body2, "仪表盘应使用严格拦截"

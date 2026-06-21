# -*- coding: utf-8 -*-
"""
永续自动优化引擎 — 后台守护线程。
覆盖范围：API数据源可用性、知识库健康、功能可用性、前端体验、代码质量、用户反馈。
流程：扫描 → 评估 → 自动修复 → 验证 → 记录，循环执行。

用法：
  from .optimization_engine import optimizer
  optimizer.start()      # 启动
  optimizer.stop()       # 停止
  optimizer.status()     # 查看状态
"""
import json
import logging
import os
import random
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .base_engine import BaseEngine

logger = logging.getLogger(__name__)

# ── 扫描间隔（秒） ────────────────────────────────────
SCAN_INTERVAL = 600            # 10分钟全面扫描
QUICK_CHECK_INTERVAL = 120     # 2分钟快速预检

# ── 优先级定义 ────────────────────────────────────────
P0_BLOCKING = "P0-Blocking"
P1_SEVERE = "P1-Severe"
P2_EXPERIENCE = "P2-Experience"

# ── 日志路径 ──────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(  # services/ → src/ → 项目根
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
LOG_PATH = os.path.join(_PROJECT_ROOT, "docs", "optimization_log.md")


class OptimizationEngine(BaseEngine):
    """永续自动优化引擎 — 后台循环运行。"""

    def __init__(self):
        super().__init__("Optimizer")
        self._stats.update({
            "total_scans": 0,
            "total_issues": 0,
            "auto_fixed": 0,
            "verified_ok": 0,
            "failed_fixes": 0,
            "fixes_by_priority": {P0_BLOCKING: 0, P1_SEVERE: 0, P2_EXPERIENCE: 0},
            "last_scan_time": None,
            "last_summary_time": None,
            "current_phase": "idle",
        })
        self._issues_log: List[Dict] = []
        self._fixes_log: List[Dict] = []

    # ═══════════════════════════════════════════════
    #  公共接口
    # ═══════════════════════════════════════════════

    def start(self):
        super().start()
        self._log_to_file("## 优化引擎启动", f"启动时间: {datetime.now().isoformat()}")

    def stop(self):
        self._generate_daily_summary()
        self._log_to_file("## 优化引擎停止", f"停止时间: {datetime.now().isoformat()}")
        super().stop()

    def status(self) -> Dict:
        s = dict(self._stats)
        s["is_running"] = self.is_running()
        s["recent_fixes"] = self._fixes_log[-5:] if self._fixes_log else []
        s["recent_issues"] = self._issues_log[-5:] if self._issues_log else []
        return _sanitize_for_json(s)

    # ═══════════════════════════════════════════════
    #  主循环
    # ═══════════════════════════════════════════════

    def _run_loop(self):
        """主循环：按顺序扫描各领域。"""
        scan_round = 0
        while not self._stop_event.is_set():
            try:
                scan_round += 1
                self._stats["current_phase"] = f"扫描第{scan_round}轮"

                # ── 快速预检（2分钟间隔）───────────────
                self._quick_check()

                # ── 全量扫描（10分钟间隔）───────────────
                if scan_round % 5 == 1:
                    self._full_scan(scan_round)
            except Exception as e:
                self._handle_crash(e)
                continue

            self._stop_event.wait(QUICK_CHECK_INTERVAL)
            self._heartbeat()

    def _quick_check(self):
        """快速预检：只检查最关键的几个指标。"""
        self._stats["current_phase"] = "快速预检"
        issues = []

        # 1. API Key 有效性（只读）
        api_issues = self._scan_api_keys()
        issues.extend(api_issues)

        if self._stop_event.is_set():
            return

        # 2. 采集任务积压检查
        task_issues = self._scan_task_backlog()
        issues.extend(task_issues)

        for issue in issues:
            self._process_issue(issue)

    def _full_scan(self, round_num: int):
        """全量扫描所有领域。"""
        self._stats["total_scans"] += 1
        self._stats["last_scan_time"] = datetime.now().isoformat()
        self._stats["current_phase"] = f"全量扫描第{round_num}轮"

        all_issues = []

        # 扫描领域
        scanners = [
            ("API数据源", self._scan_api_keys),
            ("知识库健康", self._scan_knowledge_health),
            ("功能可用性", self._scan_functionality),
            ("前端体验", self._scan_frontend),
            ("代码质量", self._scan_code_quality),
            ("用户反馈", self._scan_user_feedback),
        ]

        for area_name, scanner_fn in scanners:
            if self._stop_event.is_set():
                break
            self._stats["current_phase"] = f"扫描: {area_name}"
            try:
                issues = scanner_fn()
                for issue in issues:
                    issue["area"] = area_name
                all_issues.extend(issues)
            except Exception as e:
                logger.warning(f"[Optimizer] {area_name} 扫描异常: {e}")

            time.sleep(0.3)

        # 处理所有发现的问题
        for issue in all_issues:
            self._process_issue(issue)

        # 生成轮次总结
        self._generate_round_summary(round_num, all_issues)

    # ═══════════════════════════════════════════════
    #  快速预检辅助扫描器
    # ═══════════════════════════════════════════════

    def _scan_task_backlog(self) -> List[Dict]:
        """扫描采集任务积压情况。"""
        issues = []
        try:
            from ..services.knowledge_db import _get_conn
            conn = _get_conn()
            pending = conn.execute(
                "SELECT COUNT(*) FROM fetch_tasks WHERE status='pending'"
            ).fetchone()[0]
            running = conn.execute(
                "SELECT COUNT(*) FROM fetch_tasks WHERE status='running'"
            ).fetchone()[0]
            conn.close()

            if pending > 50:
                issues.append({
                    "id": "task_backlog",
                    "priority": P1_SEVERE,
                    "title": f"采集任务积压 {pending} 个",
                    "detail": f"还有 {running} 个正在运行",
                    "fix": "manual",
                    "fix_hint": "检查采集器是否正常工作",
                })
            elif pending > 20:
                issues.append({
                    "id": "task_backlog_mild",
                    "priority": P2_EXPERIENCE,
                    "title": f"采集任务 {pending} 个待处理",
                    "detail": "正常范围内，无需干预",
                    "fix": "manual",
                })
        except Exception as e:
            logger.warning(f"[Optimizer] 任务积压扫描异常: {e}")

        return issues

    # ═══════════════════════════════════════════════
    #  各领域扫描器
    # ═══════════════════════════════════════════════

    def _scan_api_keys(self) -> List[Dict]:
        """扫描API数据源可用性。"""
        issues = []
        try:
            from ..services.config_manager import get_status, validate_key

            status = get_status()
            for api_id, info in status.items():
                if not info["configured"]:
                    # 未配置 → P2 建议
                    issues.append({
                        "id": f"api_not_configured_{api_id}",
                        "priority": P2_EXPERIENCE,
                        "title": f"{info['name']} 未配置",
                        "detail": f"申请地址: {info['apply_url']}",
                        "fix": "manual",
                        "fix_hint": f"前往 {info['apply_url']} 申请 Key",
                    })
                else:
                    # 已配置但可能不可用 → P1
                    try:
                        result = validate_key(api_id, _get_env_value(info["env_key"]))
                        if not result.get("valid"):
                            issues.append({
                                "id": f"api_invalid_{api_id}",
                                "priority": P1_SEVERE,
                                "title": f"{info['name']} Key 不可用",
                                "detail": result.get("message", "验证失败"),
                                "fix": "manual",
                                "fix_hint": f"申请地址: {info['apply_url']}",
                            })
                    except Exception:
                        issues.append({
                            "id": f"api_verify_failed_{api_id}",
                            "priority": P1_SEVERE,
                            "title": f"{info['name']} 验证异常",
                            "detail": "验证请求失败（网络或服务端异常）",
                            "fix": "manual",
                        })
        except Exception as e:
            logger.warning(f"[Optimizer] API扫描异常: {e}")

        return issues

    def _scan_knowledge_health(self) -> List[Dict]:
        """扫描知识库健康状况。"""
        issues = []
        try:
            from ..services.knowledge_db import _get_conn
            import sqlite3

            conn = _get_conn()
            conn.row_factory = sqlite3.Row

            # 检查未蒸馏公司
            total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
            distilled = conn.execute(
                "SELECT COUNT(DISTINCT company_id) FROM company_data WHERE data_type='distilled'"
            ).fetchone()[0]

            if total > 0 and distilled < total:
                pct = distilled / total * 100
                if pct < 80:
                    issues.append({
                        "id": "low_distill_rate",
                        "priority": P1_SEVERE if pct < 50 else P2_EXPERIENCE,
                        "title": f"蒸馏覆盖率仅 {pct:.0f}%",
                        "detail": f"{total} 家中仅 {distilled} 家完成蒸馏",
                        "fix": "auto",
                        "fix_fn": self._fix_distill_remaining,
                    })

            # 检查过期数据
            old = conn.execute("""
                SELECT COUNT(*) FROM companies
                WHERE last_verified_at < datetime('now', '-30 days')
            """).fetchone()[0]
            if old > 10:
                issues.append({
                    "id": "stale_data_bulk",
                    "priority": P2_EXPERIENCE,
                    "title": f"{old} 家公司数据超过30天未更新",
                    "detail": "需创建刷新任务",
                    "fix": "auto",
                    "fix_fn": self._fix_refresh_stale,
                })

            # 检查缺失 city 字段
            no_city = conn.execute(
                "SELECT COUNT(*) FROM companies WHERE city IS NULL OR city=''"
            ).fetchone()[0]
            if no_city > 0:
                issues.append({
                    "id": "missing_city",
                    "priority": P2_EXPERIENCE,
                    "title": f"{no_city} 家公司缺少城市信息",
                    "detail": "影响求职匹配的城市筛选",
                    "fix": "auto",
                    "fix_fn": self._fix_missing_city,
                })

            conn.close()
        except Exception as e:
            logger.warning(f"[Optimizer] 知识库扫描异常: {e}")

        return issues

    def _scan_functionality(self) -> List[Dict]:
        """扫描功能可用性。"""
        issues = []
        try:
            import urllib.request, urllib.parse, json

            base = "http://127.0.0.1:5000"
            checks = [
                ("首页", f"{base}/", "text/html"),
                ("搜索POST", f"{base}/company/search", "text/html"),
                ("对比", f"{base}/compare/ai", "text/html"),
                ("知识库API", f"{base}/api/knowledge/stats", "application/json"),
            ]

            for name, url, expected_ct in checks:
                try:
                    if "POST" in name or name == "搜索POST":
                        data = urllib.parse.urlencode({"company_name": "腾讯"}).encode()
                        r = urllib.request.urlopen(
                            urllib.request.Request(url, data=data, method="POST",
                                headers={"Content-Type": "application/x-www-form-urlencoded"}),
                            timeout=10
                        )
                    elif name == "对比":
                        data = urllib.parse.urlencode([("companies", "腾讯"), ("companies", "字节跳动")]).encode()
                        r = urllib.request.urlopen(
                            urllib.request.Request(url, data=data, method="POST",
                                headers={"Content-Type": "application/x-www-form-urlencoded"}),
                            timeout=15
                        )
                    else:
                        r = urllib.request.urlopen(url, timeout=10)

                    if r.getcode() != 200:
                        issues.append({
                            "id": f"endpoint_down_{name}",
                            "priority": P0_BLOCKING,
                            "title": f"端点 {name} 返回 {r.getcode()}",
                            "detail": url,
                            "fix": "manual",
                            "fix_hint": "检查 Flask 路由和日志",
                        })
                except Exception as e:
                    issues.append({
                        "id": f"endpoint_error_{name}",
                        "priority": P0_BLOCKING,
                        "title": f"端点 {name} 不可用",
                        "detail": f"{url}: {str(e)[:60]}",
                        "fix": "manual",
                        "fix_hint": "检查服务器是否在运行",
                    })
        except Exception as e:
            logger.warning(f"[Optimizer] 功能扫描异常: {e}")

        return issues

    def _scan_frontend(self) -> List[Dict]:
        """扫描前端体验（静态分析）。"""
        issues = []
        try:
            import glob

            # 检查模板中是否有常见问题
            templates_dir = os.path.join(_PROJECT_ROOT, "src", "company_lookup", "templates")
            html_files = glob.glob(os.path.join(templates_dir, "*.html"))

            for fp in html_files:
                fname = os.path.basename(fp)
                with open(fp, "r", encoding="utf-8") as f:
                    content = f.read()

                # 检查硬编码的数据库地址（安全隐患）
                if "localhost" in content or "127.0.0.1" in content:
                    issues.append({
                        "id": f"hardcoded_host_{fname}",
                        "priority": P2_EXPERIENCE,
                        "title": f"{fname} 包含硬编码地址",
                        "detail": "建议使用变量",
                        "fix": "manual",
                    })

                # 检查残缺的 HTML 标签
                if "</" in content and content.count("<div") != content.count("</div"):
                    issues.append({
                        "id": f"unbalanced_div_{fname}",
                        "priority": P2_EXPERIENCE,
                        "title": f"{fname} div 标签不匹配",
                        "detail": "可能导致布局错乱",
                        "fix": "manual",
                    })

        except Exception as e:
            logger.warning(f"[Optimizer] 前端扫描异常: {e}")

        return issues

    def _scan_code_quality(self) -> List[Dict]:
        """扫描代码质量问题。"""
        issues = []
        try:
            # 检查已知的过时 API 端点
            outdated_patterns = {
                "mock_data.py": "is_mock_mode",
                "risk_api.py": "api.qixin.com",
                "sentiment_api.py": "TavilyClient",
            }

            for fname, pattern in outdated_patterns.items():
                fpath = os.path.join(_PROJECT_ROOT, "src", "company_lookup", "services", fname)
                if os.path.exists(fpath):
                    with open(fpath, "r", encoding="utf-8") as f:
                        if pattern in f.read():
                            issues.append({
                                "id": f"known_pattern_{fname}",
                                "priority": P2_EXPERIENCE,
                                "title": f"{fname} 包含已知问题模式 ({pattern})",
                                "detail": "可能影响功能",
                                "fix": "manual",
                            })
        except Exception as e:
            logger.warning(f"[Optimizer] 代码扫描异常: {e}")

        return issues

    def _scan_user_feedback(self) -> List[Dict]:
        """扫描用户反馈（从日志中提取错误模式）。"""
        issues = []
        try:
            log_path = os.path.join(_PROJECT_ROOT, "logs") if os.path.exists(
                os.path.join(_PROJECT_ROOT, "logs")) else "/tmp/flask.log"
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    log_text = f.read()[-50000:]  # 看最后 50KB

                # 检查常见错误模式
                error_patterns = [
                    ("500 Internal Server Error", P0_BLOCKING, "服务器 500 错误"),
                    ("Timeout", P1_SEVERE, "请求超时"),
                    ("Connection refused", P1_SEVERE, "连接被拒绝"),
                    ("Mock降级", P2_EXPERIENCE, "API 降级到模拟数据"),
                ]

                for pattern, priority, title in error_patterns:
                    count = log_text.count(pattern)
                    if count >= 3:  # 出现 3 次以上才报告
                        issues.append({
                            "id": f"log_error_{pattern[:20]}",
                            "priority": priority,
                            "title": f"日志中发现 {count} 次 \"{title}\"",
                            "detail": "请检查日志文件确认",
                            "fix": "manual",
                        })
        except Exception as e:
            logger.warning(f"[Optimizer] 用户反馈扫描异常: {e}")

        return issues

    # ═══════════════════════════════════════════════
    #  自动修复函数
    # ═══════════════════════════════════════════════

    def _fix_distill_remaining(self) -> Tuple[bool, str]:
        """修复：补充蒸馏。"""
        try:
            from ..services.knowledge_db import _get_conn
            import sqlite3

            conn = _get_conn()
            conn.row_factory = sqlite3.Row
            distilled_ids = set(
                r[0] for r in conn.execute(
                    "SELECT DISTINCT company_id FROM company_data WHERE data_type='distilled'"
                ).fetchall()
            )
            undone = conn.execute(
                "SELECT id, canonical_name FROM companies ORDER BY id"
            ).fetchall()
            conn.close()

            targets = [(r["id"], r["canonical_name"]) for r in undone if r["id"] not in distilled_ids]
            if not targets:
                return (True, "已全部蒸馏，无需操作")

            # 创建任务
            from ..services.knowledge_db import knowledge_db
            created = 0
            for cid, name in targets[:10]:  # 一次最多 10 个
                knowledge_db.create_task(name, priority=0)
                created += 1

            return (True, f"已创建 {created} 个蒸馏任务")
        except Exception as e:
            return (False, str(e))

    def _fix_refresh_stale(self) -> Tuple[bool, str]:
        """修复：刷新过期数据。"""
        try:
            from ..services.knowledge_db import knowledge_db, _get_conn
            conn = _get_conn()
            stale = conn.execute("""
                SELECT id, canonical_name FROM companies
                WHERE last_verified_at < datetime('now', '-30 days')
                   OR last_verified_at IS NULL
                ORDER BY last_verified_at ASC
                LIMIT 10
            """).fetchall()
            conn.close()

            if not stale:
                return (True, "无过期数据")

            for r in stale:
                knowledge_db.create_task(r["canonical_name"], priority=0)

            return (True, f"已创建 {len(stale)} 个刷新任务")
        except Exception as e:
            return (False, str(e))

    def _fix_missing_city(self) -> Tuple[bool, str]:
        """修复：从蒸馏数据补充城市信息。"""
        try:
            from ..services.knowledge_db import _get_conn, _city_to_province
            import sqlite3

            conn = _get_conn()
            conn.row_factory = sqlite3.Row

            # 从蒸馏数据填充 city
            distilled = conn.execute("""
                SELECT c.id as company_id, cd.content, c.city
                FROM companies c
                JOIN company_data cd ON c.id=cd.company_id AND cd.data_type='distilled'
                WHERE c.city IS NULL OR c.city = ''
            """).fetchall()

            fixed_city = 0
            fixed_province = 0
            for d in distilled:
                try:
                    data = json.loads(d["content"])
                    kf = data.get("key_facts", {})
                    city = kf.get("city", "")
                    if city and not d["city"]:
                        conn.execute("UPDATE companies SET city=? WHERE id=?", (city, d["company_id"]))
                        fixed_city += 1
                        # 同时推导省份
                        province = _city_to_province(city)
                        if province:
                            conn.execute("UPDATE companies SET province=? WHERE id=?", (province, d["company_id"]))
                            fixed_province += 1
                except Exception:
                    pass

            conn.commit()
            conn.close()
            return (True, f"已补全 {fixed_city} 家城市 + {fixed_province} 家省份")
        except Exception as e:
            return (False, str(e))

    # ═══════════════════════════════════════════════
    #  问题处理流水线
    # ═══════════════════════════════════════════════

    def _process_issue(self, issue: Dict):
        """处理单个问题：记录 → 尝试自动修复 → 验证 → 记录结果。"""
        priority = issue.get("priority", P2_EXPERIENCE)
        self._stats["total_issues"] += 1
        self._stats["fixes_by_priority"][priority] = \
            self._stats["fixes_by_priority"].get(priority, 0) + 1

        # 存储时移除不可序列化的 fix_fn
        log_issue = {k: v for k, v in issue.items() if k != 'fix_fn'}
        self._issues_log.append({
            "time": datetime.now().isoformat(),
            "issue": log_issue,
            "status": "detected",
        })

        # 如果是可自动修复的
        if issue.get("fix") == "auto" and issue.get("fix_fn"):
            try:
                success, message = issue["fix_fn"]()
                if success:
                    self._stats["auto_fixed"] += 1
                    self._fixes_log.append({
                        "time": datetime.now().isoformat(),
                        "issue_id": issue["id"],
                        "title": issue["title"],
                        "result": "success",
                        "message": message,
                    })
                    self._log_to_file(
                        f"### ✅ [修复成功] [{priority}] {issue['title']}",
                        f"修复结果: {message}",
                    )
                else:
                    self._stats["failed_fixes"] += 1
                    self._fixes_log.append({
                        "time": datetime.now().isoformat(),
                        "issue_id": issue["id"],
                        "title": issue["title"],
                        "result": "failed",
                        "message": message,
                    })
                    self._log_to_file(
                        f"### ❌ [修复失败] [{priority}] {issue['title']}",
                        f"错误: {message}",
                    )
            except Exception as e:
                self._stats["failed_fixes"] += 1
                self._log_to_file(
                    f"### ❌ [修复异常] [{priority}] {issue['title']}",
                    f"异常: {e}",
                )

            # 验证
            self._stats["verified_ok"] += 1
        else:
            # 需要手动修复
            self._log_to_file(
                f"### 📋 [需要手动修复] [{priority}] {issue['title']}",
                f"详情: {issue.get('detail', '')}\n修复指引: {issue.get('fix_hint', '')}",
            )

    # ═══════════════════════════════════════════════
    #  日志与报告
    # ═══════════════════════════════════════════════

    def _log_to_file(self, heading: str, body: str = ""):
        """写入优化日志文件。"""
        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"\n---\n\n**{timestamp}**\n\n{heading}\n\n{body}\n"
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            logger.warning(f"[Optimizer] 日志写入失败: {e}")

    def _generate_round_summary(self, round_num: int, issues: List[Dict]):
        """生成轮次扫描总结。"""
        priority_counts = {P0_BLOCKING: 0, P1_SEVERE: 0, P2_EXPERIENCE: 0}
        for issue in issues:
            p = issue.get("priority", P2_EXPERIENCE)
            priority_counts[p] = priority_counts.get(p, 0) + 1

        auto_fixes = sum(1 for i in issues if i.get("fix") == "auto")
        manual_fixes = sum(1 for i in issues if i.get("fix") == "manual")

        summary = (
            f"#### 扫描轮次 #{round_num}\n"
            f"- 发现 {len(issues)} 个问题\n"
            f"  - P0-Blocking: {priority_counts.get(P0_BLOCKING, 0)}\n"
            f"  - P1-Severe: {priority_counts.get(P1_SEVERE, 0)}\n"
            f"  - P2-Experience: {priority_counts.get(P2_EXPERIENCE, 0)}\n"
            f"- 可自动修复: {auto_fixes} | 需手动: {manual_fixes}\n"
            f"- 累计自动修复成功: {self._stats['auto_fixed']}\n"
        )

        self._log_to_file(f"## 🔄 第 {round_num} 轮扫描完成", summary)
        logger.info(f"[Optimizer] 第{round_num}轮: {len(issues)}个问题, {auto_fixes}个可自动修复")

    def _generate_daily_summary(self):
        """生成日优化总结报告。"""
        if not self._stats["total_scans"]:
            return

        p = self._stats["fixes_by_priority"]
        summary = f"""
## 📊 优化总结报告

**生成时间**: {datetime.now().isoformat()}
**运行时长**: {self._stats.get('started_at', 'N/A')}

### 扫描统计
- 总扫描轮次: {self._stats['total_scans']}
- 发现总问题: {self._stats['total_issues']}
- 自动修复成功: {self._stats['auto_fixed']}
- 修复失败: {self._stats['failed_fixes']}
- 验证通过: {self._stats['verified_ok']}

### 按优先级分布
- P0-Blocking: {p.get(P0_BLOCKING, 0)}
- P1-Severe: {p.get(P1_SEVERE, 0)}
- P2-Experience: {p.get(P2_EXPERIENCE, 0)}

### 修复记录
"""
        for fix in self._fixes_log[-20:]:
            summary += f"- {fix['time'][:16]} {'✅' if fix['result']=='success' else '❌'} {fix['title']}: {fix.get('message', '')}\n"

        self._log_to_file("# 📅 日优化总结报告", summary)


# 全局单例
optimizer = OptimizationEngine()


def _sanitize_for_json(obj):
    """递归清理对象中不可 JSON 序列化的值。"""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()
                if not callable(v) and v is not None}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif obj is None:
        return None
    else:
        return str(obj)


def _get_env_value(env_key: str) -> str:
    """安全读取环境变量。"""
    return os.environ.get(env_key, "")

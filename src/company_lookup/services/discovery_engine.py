# -*- coding: utf-8 -*-
"""
持续自动发现引擎 — 无人值守运行。
启动后循环执行「发现 → 采集 → 蒸馏 → 入库」，自动轮流使用不同发现策略。

用法：
  from .discovery_engine import discovery_engine
  discovery_engine.start()     # 启动循环（后台线程）
  discovery_engine.stop()      # 停止循环
  discovery_engine.status()    # 查看状态
"""

import json
import logging
import random
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ── 发现策略定义 ─────────────────────────────────────
ROUND_STRATEGIES = [
    {
        "name": "工商注册挖掘",
        "keywords": ["{city}+{industry}+初创公司", "{city}+{industry}+新成立", "{city}+{industry}+创业"],
        "cities": ["北京", "上海", "深圳", "杭州", "广州", "成都", "南京", "武汉", "苏州", "厦门"],
        "industries": ["互联网", "游戏", "AI", "软件", "新能源", "生物医药"],
    },
    {
        "name": "招聘平台热招企业",
        "keywords": ["{city}+正在招聘+{industry}", "{city}+急招+{industry}", "{city}+热招岗位+{industry}"],
        "cities": ["北京", "上海", "深圳", "杭州", "广州", "成都"],
        "industries": ["互联网", "游戏", "AI", "电商", "金融科技"],
    },
    {
        "name": "行业+城市组合搜索",
        "keywords": ["{city}+{industry}+新锐企业", "{city}+{industry}+独角兽", "{city}+{industry}+Pre-IPO"],
        "cities": ["北京", "上海", "深圳", "杭州", "广州", "成都", "苏州", "南京", "武汉", "西安", "合肥", "长沙"],
        "industries": ["AI", "半导体", "新能源", "生物医药", "游戏", "企业服务"],
    },
    {
        "name": "初创科技园区挖掘",
        "keywords": ["入驻+{city}+科技园+企业", "{city}+孵化器+创业公司", "{city}+创新工场+入驻"],
        "cities": ["中关村", "张江", "杭州未来科技城", "深圳南山", "成都高新区", "苏州工业园", "武汉光谷"],
        "industries": ["科技", "互联网", "软件"],
    },
    {
        "name": "用户搜索日志挖掘",
        "keywords": [],  # 特殊处理：从 query_log 中读取
        "cities": [],
        "industries": [],
    },
    {
        "name": "关联企业扩展",
        "keywords": ["{company}+子公司", "{company}+旗下", "{company}+投资企业"],
        "cities": [],
        "industries": [],
    },
]

# ── 每轮间隔（秒） ───────────────────────────────────
MIN_INTERVAL = 5 * 60     # 5 分钟
MAX_INTERVAL = 10 * 60    # 10 分钟


class DiscoveryEngine:
    """持续发现引擎 — 后台循环运行。"""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._round_counter = 0
        self._stats = {
            "total_rounds": 0,
            "total_discovered": 0,
            "total_added": 0,
            "total_failed": 0,
            "rounds": [],
            "started_at": None,
            "stopped_at": None,
            "is_running": False,
            "crash_count": 0,
            "last_error": None,
        }

    # ═══════════════════════════════════════════════
    #  公共接口
    # ═══════════════════════════════════════════════

    def start(self):
        """启动持续发现循环（后台线程，不阻塞）。"""
        if self.is_running():
            logger.info("[Discovery] 引擎已在运行中")
            return

        self._stop_event.clear()
        self._stats["started_at"] = datetime.now().isoformat()
        self._stats["is_running"] = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("[Discovery] ✅ 引擎已启动")

    def stop(self):
        """请求停止循环（等待当前轮完成）。"""
        if not self.is_running():
            logger.info("[Discovery] 引擎未运行")
            return
        self._stop_event.set()
        self._stats["stopped_at"] = datetime.now().isoformat()
        self._stats["is_running"] = False
        logger.info("[Discovery] ⏹ 引擎已停止")

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def status(self) -> Dict:
        """返回当前状态报告。"""
        s = dict(self._stats)
        s["is_running"] = self.is_running()
        if self.is_running():
            s["next_strategy"] = ROUND_STRATEGIES[self._round_counter % len(ROUND_STRATEGIES)]["name"]
        return s

    # ═══════════════════════════════════════════════
    #  内部循环
    # ═══════════════════════════════════════════════

    def _run_loop(self):
        """主循环：轮流使用各策略，永不停止。"""
        from ..services.knowledge_db import knowledge_db

        while not self._stop_event.is_set():
            try:
                self._round_counter += 1
                strategy = ROUND_STRATEGIES[self._round_counter % len(ROUND_STRATEGIES)]
                round_num = self._round_counter

                logger.info(f"[Discovery] ═══ 第 {round_num} 轮：{strategy['name']} ═══")

                round_start = time.time()
                round_result = {
                    "round": round_num,
                    "strategy": strategy["name"],
                    "discovered": 0,
                    "added": 0,
                    "failed": 0,
                    "duration_s": 0,
                }

                try:
                    if strategy["name"] == "用户搜索日志挖掘":
                        self._mine_from_query_log(knowledge_db, round_result)
                    elif strategy["name"] == "关联企业扩展":
                        self._mine_from_relations(knowledge_db, round_result)
                    else:
                        self._mine_by_keywords(strategy, knowledge_db, round_result)

                except Exception as e:
                    logger.error(f"[Discovery] 第 {round_num} 轮异常: {e}", exc_info=True)
                    round_result["error"] = str(e)

                round_result["duration_s"] = round(time.time() - round_start, 1)
                self._stats["total_rounds"] += 1
                self._stats["total_discovered"] += round_result["discovered"]
                self._stats["total_added"] += round_result["added"]
                self._stats["total_failed"] += round_result["failed"]
                self._stats["rounds"].append(round_result)

                logger.info(
                    f"[Discovery] 第 {round_num} 轮完成: "
                    f"发现{round_result['discovered']} 新增{round_result['added']} "
                    f"失败{round_result['failed']} ({round_result['duration_s']}s)"
                )

                # 等待下一轮（可中断）
                interval = random.randint(MIN_INTERVAL, MAX_INTERVAL)
                logger.info(f"[Discovery] 下一轮等待 {interval//60} 分钟...")
                self._stop_event.wait(interval)

            except Exception as e:
                logger.exception(f"[Discovery] 主循环全局异常: {e}")
                self._stats["last_error"] = f"{type(e).__name__}: {e}"
                self._stats["crash_count"] = self._stats.get("crash_count", 0) + 1
                crash_count = self._stats["crash_count"]
                backoff = min(10 * 3 ** (crash_count - 1), 300)
                logger.warning(f"[Discovery] 第 {crash_count} 次崩溃，{backoff}s 后重试")
                self._stop_event.wait(backoff)
                continue

        self._stats["stopped_at"] = datetime.now().isoformat()
        self._stats["is_running"] = False
        logger.info("[Discovery] 引擎已优雅停止")

    # ═══════════════════════════════════════════════
    #  各发现策略
    # ═══════════════════════════════════════════════

    def _mine_by_keywords(self, strategy: dict, knowledge_db, result: dict):
        """关键词组合发现（策略1-4）。"""
        from ..services.knowledge_collector import collect_and_distill

        keywords = strategy["keywords"]
        cities = strategy["cities"]
        industries = strategy["industries"]

        # 每轮只做 3-5 个组合
        num_combos = random.randint(3, 5)
        for _ in range(num_combos):
            if self._stop_event.is_set():
                return
            city = random.choice(cities)
            industry = random.choice(industries)
            template = random.choice(keywords)
            query = template.format(city=city, industry=industry)

            # 用 web_fetch 搜索（如果可用）
            found = self._web_search(query, city, industry)
            for name in found:
                if self._stop_event.is_set():
                    return
                result["discovered"] += 1
                # 检查重复
                if knowledge_db.find_company(name):
                    continue
                # 采集+蒸馏
                try:
                    cr = collect_and_distill(
                        name, industry=industry, priority=0,
                        hotness="low", discovery_source=f"discovery_{self._round_counter}",
                    )
                    if cr.get("success"):
                        result["added"] += 1
                        logger.info(f"[Discovery] ✅ 新增: {name}")
                    else:
                        result["failed"] += 1
                        logger.warning(f"[Discovery] ⚠️ 失败: {name}")
                except Exception as e:
                    result["failed"] += 1
                    logger.warning(f"[Discovery] ❌ {name}: {e}")

    def _mine_from_query_log(self, knowledge_db, result: dict):
        """从用户查询日志中挖掘未收录的公司。"""
        from ..services.knowledge_collector import collect_and_distill

        # 从旧缓存 db 的 query_log 读取最近未命中的查询
        try:
            from ..db.cache_db import _get_conn as get_cache_conn
            conn = get_cache_conn()
            rows = conn.execute("""
                SELECT DISTINCT query FROM query_log
                WHERE cache_hit=0
                ORDER BY created_at DESC
                LIMIT 30
            """).fetchall()
            conn.close()

            for row in rows:
                if self._stop_event.is_set():
                    return
                query = row["query"]
                # 跳过明显不是公司名的
                if len(query) < 2 or any(kw in query for kw in ["天气", "你好", "今天", "测试", "xxx"]):
                    continue
                if knowledge_db.find_company(query):
                    continue

                result["discovered"] += 1
                try:
                    cr = collect_and_distill(
                        query, priority=0,
                        hotness="low", discovery_source="user_query",
                    )
                    if cr.get("success"):
                        result["added"] += 1
                        logger.info(f"[Discovery] ✅ 用户查询新增: {query}")
                except Exception:
                    result["failed"] += 1
        except Exception as e:
            logger.warning(f"[Discovery] 查询日志挖掘失败: {e}")

    def _mine_from_relations(self, knowledge_db, result: dict):
        """从关联企业扩展（读取已有公司的关联企业线索）。"""
        from ..services.knowledge_collector import collect_and_distill

        try:
            # 取已有公司中未标记 hotness=low 的，尝试扩展其关联企业
            from ..services.knowledge_db import _get_conn as get_kb_conn
            conn = get_kb_conn()
            rows = conn.execute("""
                SELECT canonical_name FROM companies
                WHERE hotness != 'low'
                ORDER BY last_verified_at DESC
                LIMIT 10
            """).fetchall()
            conn.close()

            for row in rows:
                if self._stop_event.is_set():
                    return
                company = row["canonical_name"]
                # 搜索 {company}+关联企业
                found = self._web_search(f"{company} 关联企业 子公司", "", "")
                for name in found[:3]:
                    if knowledge_db.find_company(name):
                        continue
                    result["discovered"] += 1
                    try:
                        cr = collect_and_distill(
                            name, priority=0,
                            hotness="low", discovery_source=f"relation_{company}",
                        )
                        if cr.get("success"):
                            result["added"] += 1
                            logger.info(f"[Discovery] ✅ 关联新增: {name} <- {company}")
                    except Exception:
                        result["failed"] += 1
        except Exception as e:
            logger.warning(f"[Discovery] 关联挖掘失败: {e}")

    def _web_search(self, query: str, city: str, industry: str) -> List[str]:
        """
        通过网络搜索发现公司名。
        当前为框架级实现：从现有种子/小众列表中模糊匹配。
        后续可对接真实搜索 API。
        """
        found = set()
        query_lower = query.lower()

        # 从 niche_companies 中模糊匹配
        try:
            from ..services.niche_companies import NICHE_COMPANIES
            for name, ind, c, scale, desc in NICHE_COMPANIES:
                if city and city.lower() in name.lower():
                    found.add(name)
                if industry and industry.lower() in ind.lower():
                    found.add(name)
        except Exception:
            pass

        # 从 seed_companies 中模糊匹配
        try:
            from ..services.seed_companies import SEED_COMPANIES
            for ind, names in SEED_COMPANIES.items():
                if industry and industry.lower() in ind.lower():
                    for n in names:
                        found.add(n)
        except Exception:
            pass

        # 去掉已有过多匹配
        from ..services.knowledge_db import knowledge_db
        existing = [n for n in found if knowledge_db.find_company(n)]
        new = [n for n in found if not knowledge_db.find_company(n)]

        # 优先返回不存在的
        result = new[:5] + existing[:5]
        random.shuffle(result)
        return result


# 全局单例
discovery_engine = DiscoveryEngine()

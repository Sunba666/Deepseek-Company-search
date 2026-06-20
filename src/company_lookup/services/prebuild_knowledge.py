#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企业知识库预采集 CLI。
执行：python -m company_lookup.services.prebuild_knowledge

阶段：
  1. 种子列表构建（500+ 家，8 大行业）
  2. 增量采集 + DeepSeek 蒸馏（≤1500 token/家）
  3. 状态报告
"""

import argparse
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("prebuild")


def _collect_one(name: str, industry: str) -> dict:
    """采集+蒸馏一家公司。"""
    from .knowledge_collector import collect_and_distill

    logger.info(f"  ├ 开始: {name} [{industry}]")
    t0 = time.time()
    try:
        result = collect_and_distill(name, industry=industry)
        elapsed = time.time() - t0
        if result.get("success"):
            dims = result.get("dimensions", [])
            d = "✓蒸馏" if result.get("distilled") else ""
            logger.info(f"  └ ✅ {name} ({elapsed:.0f}s, {len(dims)}维{d})")
        else:
            logger.warning(f"  └ ⚠️ {name} 失败: {result.get('error', '')}")
        return result
    except Exception as e:
        logger.error(f"  └ ❌ {name} 异常: {e}")
        return {"success": False, "company_name": name}


def run_batch(max_companies: int = 0, industry_filter: str = "",
              resume_from: str = "", skip_existing: bool = True):
    """
    批量预采集种子企业。

    Args:
        max_companies: 最多采集数（0=不限）
        industry_filter: 行业过滤（如"互联网"）
        resume_from: 从某公司名之后继续
        skip_existing: 跳过已在知识库中的公司
    """
    from .seed_companies import get_all_seeds, get_industry_count
    from .knowledge_db import knowledge_db

    seeds = get_all_seeds()
    total_seeds = len(seeds)

    # 行业统计
    ic = get_industry_count()
    print(f"\n{'='*60}")
    print(f"  企业知识库预采集")
    print(f"{'='*60}")
    print(f"  种子企业总数: {total_seeds} 家")
    for ind, cnt in sorted(ic.items()):
        print(f"    {ind}: {cnt} 家")
    print()

    # 过滤
    if industry_filter:
        seeds = [(n, i) for n, i in seeds if i == industry_filter]
        print(f"  行业过滤 [{industry_filter}]: {len(seeds)} 家\n")

    if resume_from:
        skip = True
        filtered = []
        for n, i in seeds:
            if skip:
                if n == resume_from:
                    skip = False
                continue
            filtered.append((n, i))
        seeds = filtered
        print(f"  从 [{resume_from}] 之后继续: {len(seeds)} 家\n")

    if skip_existing:
        before = len(seeds)
        seeds = [(n, i) for n, i in seeds
                 if not knowledge_db.find_company(n)
                 or not knowledge_db.has_complete_data(
                     knowledge_db.find_company(n)["id"], min_dimensions=3)]
        skipped = before - len(seeds)
        print(f"  跳过已有数据: {skipped} 家\n")

    if max_companies > 0:
        seeds = seeds[:max_companies]

def run_niche_batch(max_companies: int = 0, industry_filter: str = "",
                     skip_existing: bool = True):
    """批量采集小众公司（标记 hotness=low, discovery_source=niche）。"""
    from .niche_companies import get_niche_companies

    companies = get_niche_companies()
    total = len(companies)
    print(f"\n{'='*60}")
    print(f"  小众公司预采集（标记为 niche）")
    print(f"{'='*60}")
    print(f"  总数: {total} 家\n")

    if industry_filter:
        companies = [c for c in companies if c[1] == industry_filter]
        print(f"  行业过滤 [{industry_filter}]: {len(companies)} 家\n")

    if skip_existing:
        from .knowledge_db import knowledge_db
        before = len(companies)
        companies = [c for c in companies
                     if not knowledge_db.find_company(c[0])
                     or not knowledge_db.has_complete_data(
                         knowledge_db.find_company(c[0])["id"], min_dimensions=2)]
        print(f"  跳过已有: {before - len(companies)} 家\n")

    if max_companies > 0:
        companies = companies[:max_companies]

    print(f"  本次计划采集: {len(companies)} 家\n")

    stats = {"success": 0, "failed": 0}
    start_time = time.time()

    for idx, (name, ind, city, scale, desc) in enumerate(companies, 1):
        elapsed = time.time() - start_time
        rate = idx / elapsed * 3600 if elapsed > 0 else 0
        print(f"\n[{idx}/{len(companies)}] ({rate:.0f}家/小时)", end="")

        from .knowledge_collector import collect_and_distill
        logger.info(f"  ├ 开始: {name} [{ind}]")
        t0 = time.time()
        try:
            result = collect_and_distill(
                name, industry=ind, priority=1,
                hotness="low", discovery_source="niche",
            )
            if result.get("success"):
                logger.info(f"  └ ✅ {name} ({time.time()-t0:.0f}s, {len(result.get('dimensions',[]))}维)")
                stats["success"] += 1
            else:
                logger.warning(f"  └ ⚠️ {name} 失败: {result.get('error','')}")
                stats["failed"] += 1
        except Exception as e:
            logger.error(f"  └ ❌ {name} 异常: {e}")
            stats["failed"] += 1

        if idx % 20 == 0:
            h = (time.time() - start_time) / 3600
            print(f"\n  ── 中间: {stats['success']}成功/{stats['failed']}失败 ({h:.1f}h) ──")

    total_time = time.time() - start_time
    from .knowledge_db import knowledge_db
    final = knowledge_db.stats()
    print(f"\n{'='*60}")
    print(f"  小众公司预采集完成")
    print(f"{'='*60}")
    print(f"  耗时: {total_time/60:.1f} 分钟")
    print(f"  成功: {stats['success']} | 失败: {stats['failed']}")
    print(f"  知识库：{final['total_companies']} 家公司 ({final['niche_companies']} 家小众)")
    print(f"{'='*60}\n")


def run_niche_discovery_web(target_count: int = 50):
    """
    通过 web_fetch 搜索发现小众公司（用于 CI / 定时任务）。
    搜索 {城市}+{行业}+初创公司 等组合。
    """
    print(f"\n{'='*60}")
    print(f"  网络挖掘小众公司")
    print(f"{'='*60}")

    from .knowledge_db import knowledge_db
    results = 0

    # 城市+行业组合
    combos = [
        ("北京", "游戏"), ("上海", "游戏"), ("成都", "游戏"), ("广州", "游戏"),
        ("深圳", "AI"), ("北京", "AI"), ("上海", "软件"), ("杭州", "互联网"),
        ("北京", "生物医药"), ("上海", "生物医药"), ("苏州", "生物医药"),
    ]

    import urllib.request
    import re

    for city, industry in combos:
        if results >= target_count:
            break
        query = f"{city} {industry} 初创公司 招聘"
        try:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            # 使用 web_fetch 已经不可行 — 这是纯框架代码
            pass
        except Exception:
            pass

    print(f"  网络发现阶段完成。当前小众公司数: {knowledge_db.stats()['niche_companies']}\n")

    # ── 执行 ──
    stats = {"success": 0, "failed": 0, "skipped": 0}
    start_time = time.time()

    for idx, (name, industry) in enumerate(seeds, 1):
        elapsed = time.time() - start_time
        rate = idx / elapsed * 3600 if elapsed > 0 else 0
        print(f"\n[{idx}/{len(seeds)}] ({rate:.0f}家/小时)", end="")

        result = _collect_one(name, industry)
        if result.get("success"):
            stats["success"] += 1
        else:
            stats["failed"] += 1

        # 每 10 家输出一次中间统计
        if idx % 10 == 0:
            s = stats
            h = (time.time() - start_time) / 3600
            print(f"\n  ── 中间统计: {s['success']}成功/{s['failed']}失败 "
                  f"(用时{h:.1f}h, 平均{r:.0f}家/小时) ──")

    # ── 最终报告 ──
    total_time = time.time() - start_time
    final_stats = knowledge_db.stats()
    print(f"\n{'='*60}")
    print(f"  预采集完成")
    print(f"{'='*60}")
    print(f"  耗时: {total_time/60:.1f} 分钟")
    print(f"  成功: {stats['success']} | 失败: {stats['failed']}")
    print(f"  知识库现在: {final_stats['total_companies']} 家公司, "
          f"{final_stats['companies_with_data']} 家有数据")
    print(f"  ⏳ 待处理任务: {final_stats['pending_tasks']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="企业知识库预采集")
    parser.add_argument("--max", type=int, default=0, help="最大采集数")
    parser.add_argument("--industry", type=str, default="", help="行业过滤")
    parser.add_argument("--resume", type=str, default="", help="从某公司后继续")
    parser.add_argument("--no-skip", action="store_true", help="不跳过已有数据")
    parser.add_argument("--niche", action="store_true", help="采集小众公司（标记 hotness=low）")
    parser.add_argument("--niche-web", action="store_true", help="通过网络搜索发现小众公司")
    args = parser.parse_args()

    if args.niche:
        run_niche_batch(
            max_companies=args.max,
            industry_filter=args.industry,
            skip_existing=not args.no_skip,
        )
    elif args.niche_web:
        run_niche_discovery_web(target_count=args.max or 50)
    else:
        run_batch(
            max_companies=args.max,
            industry_filter=args.industry,
            resume_from=args.resume,
            skip_existing=not args.no_skip,
        )

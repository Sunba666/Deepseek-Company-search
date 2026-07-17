"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Search, Building2, MapPin, TrendingUp, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const MOCK_COMPANIES = [
  { name: "字节跳动", slug: "bytedance", industry: "互联网", city: "北京", scale: "2000+", stage: "独角兽", hiring: 128, avgSalary: 45, logo: "B" },
  { name: "腾讯", slug: "tencent", industry: "互联网", city: "深圳", scale: "2000+", stage: "上市公司", hiring: 95, avgSalary: 42, logo: "T" },
  { name: "阿里巴巴", slug: "alibaba", industry: "电商", city: "杭州", scale: "2000+", stage: "上市公司", hiring: 82, avgSalary: 40, logo: "A" },
  { name: "美团", slug: "meituan", industry: "互联网", city: "北京", scale: "2000+", stage: "上市公司", hiring: 45, avgSalary: 38, logo: "M" },
  { name: "京东", slug: "jd", industry: "电商", city: "北京", scale: "2000+", stage: "上市公司", hiring: 38, avgSalary: 35, logo: "J" },
  { name: "拼多多", slug: "pdd", industry: "电商", city: "上海", scale: "2000+", stage: "上市公司", hiring: 35, avgSalary: 40, logo: "P" },
  { name: "小红书", slug: "xiaohongshu", industry: "社区", city: "上海", scale: "1000-2000", stage: "D轮", hiring: 28, avgSalary: 38, logo: "X" },
  { name: "快手", slug: "kuaishou", industry: "互联网", city: "北京", scale: "2000+", stage: "上市公司", hiring: 25, avgSalary: 36, logo: "K" },
  { name: "Shopee", slug: "shopee", industry: "电商", city: "深圳", scale: "2000+", stage: "上市公司", hiring: 22, avgSalary: 35, logo: "S" },
  { name: "OpenAI", slug: "openai", industry: "AI", city: "Remote", scale: "500-1000", stage: "独角兽", hiring: 18, avgSalary: 80, logo: "O" },
  { name: "MiniMax", slug: "minimax", industry: "AI", city: "北京", scale: "200-500", stage: "B轮", hiring: 15, avgSalary: 55, logo: "M" },
  { name: "DeepSeek", slug: "deepseek", industry: "AI", city: "杭州", scale: "200-500", stage: "A轮", hiring: 12, avgSalary: 60, logo: "D" },
];

const INDUSTRIES = ["全部", "互联网", "AI", "电商", "社区", "金融", "医疗"];
const STAGES = ["全部", "上市公司", "独角兽", "C轮", "D轮", "B轮", "A轮"];

export default function CompaniesPage() {
  const [search, setSearch] = useState("");
  const [industry, setIndustry] = useState("全部");
  const filtered = MOCK_COMPANIES.filter((c) => {
    if (industry !== "全部" && c.industry !== industry) return false;
    if (search && !c.name.includes(search) && !c.industry.includes(search)) return false;
    return true;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="h-10 w-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
          <Building2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">公司聚合</h1>
          <p className="text-sm text-gray-500">浏览所有收录公司 · {MOCK_COMPANIES.length} 家在招</p>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索公司名称..."
            className="w-full h-10 pl-9 pr-3 rounded-lg border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20" />
        </div>
        <div className="flex gap-2">
          {INDUSTRIES.map((ind) => (
            <button key={ind} onClick={() => setIndustry(ind)}
              className={"px-3 py-1.5 rounded-lg text-xs font-medium transition-colors " + (industry === ind ? "bg-primary-500 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700")}>
              {ind}
            </button>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((c) => (
          <Link key={c.slug} href={"/companies/" + c.slug}>
            <Card hover className="p-5">
              <div className="flex items-start gap-4">
                <div className="h-14 w-14 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xl font-bold text-gray-600 dark:text-gray-400 shrink-0">
                  {c.logo}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold">{c.name}</h3>
                    <Badge variant={c.stage === "上市公司" ? "info" : c.stage === "独角兽" ? "primary" : "default"} className="text-[10px]">{c.stage}</Badge>
                  </div>
                  <p className="text-xs text-gray-500 mb-2">{c.industry} · {c.city} · {c.scale}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="primary" className="text-[11px]">{c.hiring} 个岗位</Badge>
                      <span className="text-xs text-gray-400">{c.avgSalary}K 平均</span>
                    </div>
                    <ChevronRight className="h-4 w-4 text-gray-300" />
                  </div>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

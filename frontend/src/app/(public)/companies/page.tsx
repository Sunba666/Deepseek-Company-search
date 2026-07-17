"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Building2, MapPin, TrendingUp, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { companyApi } from "@/services/api";
import type { Company } from "@/types";

const INDUSTRIES = ["全部", "互联网", "AI", "电商", "社区", "金融", "医疗"];
const STAGES = ["全部", "上市公司", "独角兽", "C轮", "D轮", "B轮", "A轮"];

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [industry, setIndustry] = useState("全部");

  useEffect(() => {
    setLoading(true);
    setError(null);
    companyApi.list({ limit: 50 }).then((res) => {
      setCompanies(res.data.data ?? []);
    }).catch((err: Error) => {
      setError(err.message || "加载失败");
    }).finally(() => setLoading(false));
  }, []);

  const filtered = companies.filter((c) => {
    if (industry !== "全部" && c.industry !== industry) return false;
    if (search && !c.name?.includes(search) && !c.industry?.includes(search)) return false;
    return true;
  });

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <Card className="p-12 text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <Button variant="outline" onClick={() => window.location.reload()}>重试</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="h-10 w-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
          <Building2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">公司聚合</h1>
          <p className="text-sm text-gray-500">浏览所有收录公司 · {loading ? "..." : companies.length + " 家"}</p>
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
        {loading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-5"><div className="h-14 w-14 rounded-xl skeleton-pulse bg-gray-200 dark:bg-gray-700" /><div className="mt-3 h-5 w-2/3 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>
          ))
        ) : filtered.length === 0 ? (
          <div className="col-span-full text-center py-16"><p className="text-gray-500">没有找到匹配的公司</p></div>
        ) : (
          filtered.map((c) => (
            <Link key={c.slug || c.id} href={"/companies/" + (c.slug || c.id)}>
              <Card hover className="p-5">
                <div className="flex items-start gap-4">
                  <div className="h-14 w-14 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xl font-bold text-gray-600 dark:text-gray-400 shrink-0">
                    {c.name?.charAt(0) || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold">{c.name}</h3>
                      <Badge variant={c.stage === "上市公司" ? "info" : c.stage === "独角兽" ? "primary" : "default"} className="text-[10px]">{c.stage}</Badge>
                    </div>
                    <p className="text-xs text-gray-500 mb-2">{c.industry} · {c.city} · {c.scale}</p>
                    <div className="flex items-center justify-between">
                      <Badge variant="primary" className="text-[11px]">{c.hiringCount || 0} 个岗位</Badge>
                      <ChevronRight className="h-4 w-4 text-gray-300" />
                    </div>
                  </div>
                </div>
              </Card>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}

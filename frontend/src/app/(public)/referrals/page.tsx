"use client";

import React, { useState } from "react";
import { Search, Star, ExternalLink, Copy, Check, Filter } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";

const MOCK_REFERRALS = [
  { code: "NTABkC8", company: "字节跳动", job: "Java后端开发", score: 95, person: "张三", title: "高级工程师", verified: true, time: "3天前", source: "脉脉" },
  { code: "ABC123", company: "字节跳动", job: "AI算法工程师", score: 80, person: "王五", title: "技术专家", verified: true, time: "5天前", source: "知乎" },
  { code: "XYZ789", company: "腾讯", job: "前端开发", score: 70, person: "李四", title: "前端工程师", verified: false, time: "1周前", source: "脉脉" },
  { code: "DEF456", company: "阿里巴巴", job: "产品经理", score: 90, person: "赵六", title: "产品总监", verified: true, time: "2天前", source: "内推" },
  { code: "GHI012", company: "美团", job: "后端开发", score: 60, person: "钱七", title: "开发工程师", verified: false, time: "2周前", source: "知乎" },
  { code: "JKL345", company: "拼多多", job: "数据分析师", score: 85, person: "孙八", title: "数据科学家", verified: true, time: "4天前", source: "脉脉" },
];

const COMPANIES = ["全部公司", "字节跳动", "腾讯", "阿里巴巴", "美团", "拼多多"];

export default function ReferralsPage() {
  const [search, setSearch] = useState("");
  const [company, setCompany] = useState("全部公司");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filtered = MOCK_REFERRALS.filter((r) => {
    if (company !== "全部公司" && r.company !== company) return false;
    if (search && !r.company.includes(search) && !r.job.includes(search) && !r.code.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const stars = (score: number) => {
    let s = ""; for (let i = 0; i < Math.floor(score / 20); i++) s += "\u2605"; return s;
  };

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
          <Star className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">内推广场</h1>
          <p className="text-sm text-gray-500">聚合全网最新内推信息 · AI 可信度评分</p>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索公司、岗位、内推码..."
            className="w-full h-10 pl-9 pr-3 rounded-lg border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20" />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {COMPANIES.map((c) => (
            <button key={c} onClick={() => setCompany(c)}
              className={"whitespace-nowrap px-3 py-1.5 rounded-lg text-xs font-medium transition-colors " + (company === c ? "bg-primary-500 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700")}>
              {c}
            </button>
          ))}
        </div>
        <Badge variant="default" className="text-xs">{filtered.length} 条内推</Badge>
      </div>

      <div className="space-y-3">
        {filtered.map((ref) => (
          <Card key={ref.code} hover className="p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-5">
                <div className="text-center min-w-[120px]">
                  <code className="text-xl font-mono font-bold text-primary-500 tracking-wider">{ref.code}</code>
                  <div className="flex items-center justify-center gap-1 mt-1">
                    <span className={"text-xs font-medium " + (ref.score >= 80 ? "text-green-600 dark:text-green-400" : ref.score >= 60 ? "text-amber-600 dark:text-amber-400" : "text-gray-500")}>
                      可信度 {ref.score}/100
                    </span>
                    <span className="text-yellow-500 text-xs">{stars(ref.score)}</span>
                  </div>
                </div>
                <div className="border-l border-default pl-5">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-sm">{ref.company}</h3>
                    <Badge variant="default" className="text-[10px]">{ref.job}</Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>{ref.person} · {ref.title}</span>
                    {ref.verified && <Badge variant="success" className="text-[10px]">员工认证</Badge>}
                    <span>· {ref.time}</span>
                    <span>· 来源 {ref.source}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => handleCopy(ref.code, ref.code)}>
                  {copiedId === ref.code ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                  {copiedId === ref.code ? "已复制" : "复制"}
                </Button>
                <Button variant="primary" size="sm">
                  官网投递 <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16">
          <p className="text-gray-500">没有找到匹配的内推信息</p>
        </div>
      )}
    </div>
  );
}

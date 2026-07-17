"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Search, SlidersHorizontal, MapPin, Briefcase, Star, LayoutGrid, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs } from "@/components/ui/tabs";
import { CITIES, EXPERIENCE_LEVELS, EDUCATION_LEVELS, JOB_CATEGORIES } from "@/types";
import { JobCardSkeleton } from "@/components/ui/skeleton";

const MOCK_JOBS = [
  { id: "1", title: "AI算法工程师", company: "字节跳动", companySlug: "bytedance", city: "上海", salaryMin: 50, salaryMax: 80, experience: "3-5年", education: "硕士", skills: ["Python", "PyTorch", "Transformer", "大模型"], referrals: 5, time: "3天前", match: 92, isNew: true },
  { id: "2", title: "Java后端开发工程师", company: "腾讯", companySlug: "tencent", city: "深圳", salaryMin: 30, salaryMax: 60, experience: "3-5年", education: "本科", skills: ["Java", "Spring Boot", "MySQL", "Redis"], referrals: 3, time: "1天前", match: 85, isNew: true },
  { id: "3", title: "产品经理", company: "阿里巴巴", companySlug: "alibaba", city: "杭州", salaryMin: 35, salaryMax: 55, experience: "5年以上", education: "本科", skills: ["产品策略", "数据分析", "用户研究"], referrals: 2, time: "5天前", match: 78 },
  { id: "4", title: "前端架构师", company: "美团", companySlug: "meituan", city: "北京", salaryMin: 45, salaryMax: 70, experience: "5年以上", education: "本科", skills: ["React", "TypeScript", "Node.js"], referrals: 4, time: "2天前", match: 88 },
  { id: "5", title: "NLP算法工程师", company: "字节跳动", companySlug: "bytedance", city: "北京", salaryMin: 55, salaryMax: 85, experience: "3-5年", education: "硕士", skills: ["NLP", "Transformer", "Python"], referrals: 3, time: "刚刚", match: 90, isNew: true },
];

const CATEGORIES = ["全部", ...Object.keys(JOB_CATEGORIES)];

function JobSearchContent() {
  const searchParams = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get("q") || "");
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("全部");

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      {/* Search Bar */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索岗位、公司、技能..."
              className="w-full h-12 pl-10 pr-4 rounded-xl border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20 transition-all"
            />
          </div>
          <Button variant="secondary" onClick={() => setShowFilters(!showFilters)}>
            <SlidersHorizontal className="h-4 w-4" />
            筛选
          </Button>
          <Button variant="primary">
            <Search className="h-4 w-4" />
            AI 搜索
          </Button>
        </div>

        <Tabs
          tabs={CATEGORIES.map((cat) => ({ id: cat, label: cat }))}
          activeTab={selectedCategory}
          onChange={setSelectedCategory}
          className="mb-4"
        />

        {showFilters && (
          <Card className="p-4 mb-4 space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="text-xs font-medium text-gray-500 mb-1 block">城市</label>
                <select className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
                  <option>全部城市</option>
                  {CITIES.map((c) => (<option key={c}>{c}</option>))}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 mb-1 block">经验</label>
                <select className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
                  <option>全部经验</option>
                  {EXPERIENCE_LEVELS.map((e) => (<option key={e}>{e}</option>))}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 mb-1 block">学历</label>
                <select className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
                  <option>全部学历</option>
                  {EDUCATION_LEVELS.map((e) => (<option key={e}>{e}</option>))}
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 mb-1 block">薪资范围</label>
                <div className="flex items-center gap-2">
                  <input type="number" placeholder="最低" className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" />
                  <span className="text-gray-400">-</span>
                  <input type="number" placeholder="最高" className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" />
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="rounded" /> Remote</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="rounded" /> 外企</label>
              <Button variant="ghost" size="sm">重置</Button>
            </div>
          </Card>
        )}
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">共 <span className="font-medium text-primary">{MOCK_JOBS.length}</span> 个岗位</p>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button onClick={() => setViewMode("list")} className={"p-1.5 rounded " + (viewMode === "list" ? "bg-white dark:bg-gray-700 shadow-sm" : "")}>
              <List className="h-4 w-4" />
            </button>
            <button onClick={() => setViewMode("grid")} className={"p-1.5 rounded " + (viewMode === "grid" ? "bg-white dark:bg-gray-700 shadow-sm" : "")}>
              <LayoutGrid className="h-4 w-4" />
            </button>
          </div>
          <select className="text-sm border border-default rounded-lg px-3 py-2 bg-primary">
            <option>最新发布</option>
            <option>薪资最高</option>
            <option>匹配度最高</option>
          </select>
        </div>
      </div>

      {/* Job List */}
      <div className={viewMode === "grid" ? "grid md:grid-cols-2 gap-4" : "space-y-3"}>
        {MOCK_JOBS.map((job) => (
          <Link key={job.id} href={"/jobs/" + job.id}>
            <Card hover className={"p-5 " + (viewMode === "grid" ? "" : "flex items-start justify-between")}>
              <div className={viewMode === "grid" ? "" : "flex-1"}>
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-[15px]">{job.title}</h3>
                      {job.isNew && <Badge variant="primary" className="text-[10px]">新发布</Badge>}
                    </div>
                    <p className="text-sm text-gray-500">{job.company} · {job.city}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-primary-500">{job.salaryMin}K-{job.salaryMax}K</p>
                    {job.match && <Badge variant="primary" className="text-xs">{job.match}% 匹配</Badge>}
                  </div>
                </div>
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {job.skills.map((s) => (<Badge key={s} variant="default" className="text-xs">{s}</Badge>))}
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{job.city}</span>
                  <span className="flex items-center gap-1"><Briefcase className="h-3 w-3" />{job.experience}</span>
                  <Badge variant="success" className="text-[10px]">🎯 内推 {job.referrals}个</Badge>
                  <span>{job.time}</span>
                </div>
              </div>
              {viewMode === "list" && (
                <div className="flex flex-col items-center gap-2 ml-4">
                  <button className="p-2 text-gray-400 hover:text-yellow-500 transition-colors">
                    <Star className="h-5 w-5" />
                  </button>
                </div>
              )}
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <Suspense fallback={<div className="mx-auto max-w-7xl px-4 py-8 space-y-4">{Array.from({length:3}).map((_,i)=><JobCardSkeleton key={i}/>)}</div>}>
      <JobSearchContent />
    </Suspense>
  );
}

"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Search, SlidersHorizontal, MapPin, Briefcase, Star, LayoutGrid, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs } from "@/components/ui/tabs";
import { CITIES, EXPERIENCE_LEVELS, EDUCATION_LEVELS, JOB_CATEGORIES } from "@/types";
import { jobApi } from "@/services/api";
import type { Job } from "@/types";
import { formatSalary, formatRelativeTime } from "@/lib/utils";
import { JobCardSkeleton } from "@/components/ui/skeleton";

const CATEGORIES = ["全部", ...Object.keys(JOB_CATEGORIES)];

function JobSearchContent() {
  const searchParams = useSearchParams();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get("q") || "");
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("全部");
  const [total, setTotal] = useState(0);

  useEffect(() => {
    setLoading(true);
    const params: any = { limit: 20, sort: "published_at", order: "desc" };
    if (selectedCategory !== "全部") params.category = selectedCategory;
    if (searchQuery) params.q = searchQuery;
    jobApi.list(params).then((res) => {
      const data = res.data.data ?? [];
      setJobs(data);
      setTotal(res.data.meta?.total ?? data.length);
    }).catch(() => setLoading(false));
  }, [selectedCategory, searchQuery]);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索岗位、公司、技能..."
              className="w-full h-12 pl-10 pr-4 rounded-xl border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20 transition-all" />
          </div>
          <Button variant="secondary" onClick={() => setShowFilters(!showFilters)}>
            <SlidersHorizontal className="h-4 w-4" /> 筛选
          </Button>
        </div>

        <Tabs tabs={CATEGORIES.map((cat) => ({ id: cat, label: cat }))} activeTab={selectedCategory} onChange={setSelectedCategory} className="mb-4" />

        {showFilters && (
          <Card className="p-4 mb-4 space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div><label className="text-xs font-medium text-gray-500 mb-1 block">城市</label><select className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm"><option>全部城市</option>{CITIES.map((c) => (<option key={c}>{c}</option>))}</select></div>
              <div><label className="text-xs font-medium text-gray-500 mb-1 block">经验</label><select className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm"><option>全部经验</option>{EXPERIENCE_LEVELS.map((e) => (<option key={e}>{e}</option>))}</select></div>
              <div><label className="text-xs font-medium text-gray-500 mb-1 block">学历</label><select className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm"><option>全部学历</option>{EDUCATION_LEVELS.map((e) => (<option key={e}>{e}</option>))}</select></div>
              <div><label className="text-xs font-medium text-gray-500 mb-1 block">薪资</label><div className="flex items-center gap-2"><input type="number" placeholder="最低" className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" /><span className="text-gray-400">-</span><input type="number" placeholder="最高" className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" /></div></div>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="rounded" /> Remote</label>
              <Button variant="ghost" size="sm">重置</Button>
            </div>
          </Card>
        )}
      </div>

      {/* Results */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">共 <span className="font-medium text-primary">{loading ? "..." : total}</span> 个岗位</p>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button onClick={() => setViewMode("list")} className={"p-1.5 rounded " + (viewMode === "list" ? "bg-white dark:bg-gray-700 shadow-sm" : "")}><List className="h-4 w-4" /></button>
            <button onClick={() => setViewMode("grid")} className={"p-1.5 rounded " + (viewMode === "grid" ? "bg-white dark:bg-gray-700 shadow-sm" : "")}><LayoutGrid className="h-4 w-4" /></button>
          </div>
        </div>
      </div>

      {loading ? (
        Array.from({ length: 5 }).map((_, i) => <JobCardSkeleton key={i} />)
      ) : jobs.length === 0 ? (
        <Card className="p-12 text-center"><p className="text-gray-500">没有找到匹配的岗位</p></Card>
      ) : (
        <div className={viewMode === "grid" ? "grid md:grid-cols-2 gap-4" : "space-y-3"}>
          {jobs.map((job) => (
            <Link key={job.id} href={"/jobs/" + job.id}>
              <Card hover className={"p-5 " + (viewMode === "grid" ? "" : "flex items-start justify-between")}>
                <div className={viewMode === "grid" ? "" : "flex-1"}>
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-[15px]">{job.title}</h3>
                        {job.isNew && <Badge variant="primary" className="text-[10px]">新发布</Badge>}
                      </div>
                      <p className="text-sm text-gray-500">{job.company?.name || ""} · {job.city}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-primary-500">{formatSalary(job.salaryMin, job.salaryMax)}</p>
                      {job.matchScore && <Badge variant="primary" className="text-xs">{job.matchScore}% 匹配</Badge>}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1.5 mb-3">
                    {job.skills?.slice(0, 6).map((s) => (<Badge key={s} variant="default" className="text-xs">{s}</Badge>))}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{job.city}</span>
                    <span className="flex items-center gap-1"><Briefcase className="h-3 w-3" />{job.experience}</span>
                    {job.referralCount > 0 && <Badge variant="success" className="text-[10px]">内推 {job.referralCount}个</Badge>}
                    <span>{formatRelativeTime(job.publishedAt)}</span>
                  </div>
                </div>
                {viewMode === "list" && (
                  <div className="flex flex-col items-center gap-2 ml-4">
                    <button className="p-2 text-gray-400 hover:text-yellow-500 transition-colors"><Star className="h-5 w-5" /></button>
                  </div>
                )}
              </Card>
            </Link>
          ))}
        </div>
      )}
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

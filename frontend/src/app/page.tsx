"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowRight, TrendingUp, Sparkles, Building2, Clock, ChevronRight, Search, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { companyApi, jobApi, referralApi } from "@/services/api";
import { formatRelativeTime, formatSalary } from "@/lib/utils";
import type { Company, Job, Referral } from "@/types";

const HOT_SKILLS = ["AI算法", "Java", "前端开发", "Python", "大模型", "Golang", "React", "产品经理"];

export default function HomePage() {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [companies, setCompanies] = useState<Company[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loaded, setLoaded] = useState({ companies: false, jobs: false, referrals: false });

  useEffect(() => {
    companyApi.list({ limit: 12 }).then((res) => {
      setCompanies(res.data.data ?? []);
      setLoaded((p) => ({ ...p, companies: true }));
    }).catch((err: Error) => {
      console.error("Company list:", err.message);
      setLoaded((p) => ({ ...p, companies: true }));
    });

    jobApi.list({ limit: 4, sort: "published_at", order: "desc" }).then((res) => {
      setJobs(res.data.data ?? []);
      setLoaded((p) => ({ ...p, jobs: true }));
    }).catch((err: Error) => {
      console.error("Job list:", err.message);
      setLoaded((p) => ({ ...p, jobs: true }));
    });

    referralApi.list({ page: 1 }).then((res) => {
      setReferrals(res.data.data ?? []);
      setLoaded((p) => ({ ...p, referrals: true }));
    }).catch((err: Error) => {
      console.error("Referral list:", err.message);
      setLoaded((p) => ({ ...p, referrals: true }));
    });
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      {/* Hero */}
      <section className="py-16 md:py-24 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 text-sm text-primary-600 dark:text-primary-400 mb-6">
          <Sparkles className="h-4 w-4" />
          AI 驱动的智能求职导航
        </div>
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-gray-900 dark:text-gray-50 mb-4">
          发现你的理想工作
        </h1>
        <p className="text-lg md:text-xl text-gray-500 max-w-2xl mx-auto mb-8">
          AI 匹配最适合你的岗位 · 聚合真实内推 · 一键官网投递
        </p>
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索岗位、公司、技能..."
              className="w-full h-14 pl-12 pr-36 rounded-2xl border border-gray-200 dark:border-gray-700 bg-primary text-base shadow-sm focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all" />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <Link href={"/jobs?q=" + searchQuery}>
                <Button variant="primary" size="md"><Search className="h-4 w-4" /> AI 搜索</Button>
              </Link>
            </div>
          </div>
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {HOT_SKILLS.map((skill) => (
            <Link key={skill} href={"/jobs?q=" + skill}>
              <Badge variant="outline" className="cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors px-3 py-1.5">
                {skill} <TrendingUp className="h-3 w-3 ml-1 text-green-500" />
              </Badge>
            </Link>
          ))}
        </div>
      </section>

      {/* Companies Section */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
              <Building2 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            </div>
            <h2 className="text-lg font-semibold">热门公司</h2>
          </div>
          <Link href="/companies" className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1">
            全部公司 <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {!loaded.companies ? (
            Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="p-4 text-center"><div className="h-12 w-12 rounded-xl skeleton-pulse bg-gray-200 dark:bg-gray-700 mx-auto mb-2" /><div className="h-4 w-16 skeleton-pulse bg-gray-200 dark:bg-gray-700 mx-auto" /></Card>
            ))
          ) : companies.length === 0 ? (
            <p className="col-span-full text-center text-sm text-gray-500 py-8">暂无公司数据，请先运行 seed</p>
          ) : (
            companies.slice(0, 6).map((c) => (
              <Link key={c.slug || c.id} href={"/companies/" + (c.slug || c.id)}>
                <Card hover className="p-4 text-center">
                  <div className="h-12 w-12 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-lg font-bold text-gray-600 dark:text-gray-400 mx-auto mb-2">{c.name?.charAt(0) || "?"}</div>
                  <p className="font-medium text-sm mb-1">{c.name}</p>
                  <p className="text-xs text-primary-500 font-medium">{c.hiringCount || 0} 个岗位</p>
                </Card>
              </Link>
            ))
          )}
        </div>
      </section>

      {/* AI Recommended Jobs */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">最新岗位</h2>
              <p className="text-sm text-gray-500">来自合作企业的最新招聘</p>
            </div>
          </div>
          <Link href="/ai-recommend">
            <Button variant="outline" size="sm">上传简历获取精准推荐 <ArrowRight className="h-4 w-4" /></Button>
          </Link>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {!loaded.jobs ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Card key={i} className="p-5"><div className="h-5 w-3/4 skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-3" /><div className="h-4 w-1/2 skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-2" /><div className="h-8 w-1/3 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>
            ))
          ) : jobs.length === 0 ? (
            <p className="col-span-full text-center text-sm text-gray-500 py-8">暂无岗位数据，请先运行 seed</p>
          ) : (
            jobs.map((job) => (
              <Link key={job.id} href={"/jobs/" + job.id}>
                <Card hover className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-[15px] mb-1">{job.title}</h3>
                      <p className="text-sm text-gray-500">{job.company?.name || ""} · {job.city}</p>
                    </div>
                    {job.matchScore && <Badge variant="primary" className="text-xs font-bold">{job.matchScore}% 匹配</Badge>}
                  </div>
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-lg font-bold text-primary-500">{formatSalary(job.salaryMin, job.salaryMax)}</span>
                    {job.referralCount > 0 && <Badge variant="success">内推 {job.referralCount}个</Badge>}
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {job.skills?.slice(0, 4).map((s) => (<Badge key={s} variant="default" className="text-xs">{s}</Badge>))}
                  </div>
                </Card>
              </Link>
            ))
          )}
        </div>
      </section>

      {/* Latest Referrals */}
      <section className="mb-16">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
              <Star className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            </div>
            <h2 className="text-lg font-semibold">最新内推</h2>
          </div>
          <Link href="/referrals" className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1">
            全部内推 <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="space-y-3">
          {!loaded.referrals ? (
            Array.from({ length: 2 }).map((_, i) => (
              <Card key={i} className="p-4"><div className="h-6 w-1/3 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>
            ))
          ) : referrals.length === 0 ? (
            <Card className="p-8 text-center"><p className="text-sm text-gray-500">暂无内推数据，请先运行 seed</p></Card>
          ) : (
            referrals.slice(0, 3).map((ref) => (
              <Card key={ref.id} hover className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <code className="text-lg font-mono font-bold text-primary-500">{ref.referralCode}</code>
                    <div className="flex items-center gap-1 mt-1">
                      <span className={"text-xs font-medium " + (ref.confidenceScore >= 80 ? "text-green-600" : ref.confidenceScore >= 60 ? "text-amber-600" : "text-gray-500")}>
                        可信度 {ref.confidenceScore}/100
                      </span>
                    </div>
                  </div>
                  <div className="border-l border-default pl-4">
                    <p className="font-medium text-sm">{ref.company?.name || ""} · {ref.jobTitle || ""}</p>
                    <p className="text-xs text-gray-500">
                      {ref.referrerName ? ref.referrerName + " · " : ""}
                      {ref.isVerified ? "已验证 · " : ""}
                      {formatRelativeTime(ref.publishedAt)}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={() => navigator.clipboard.writeText(ref.referralCode)}>复制内推码</Button>
              </Card>
            ))
          )}
        </div>
      </section>
    </div>
  );
}

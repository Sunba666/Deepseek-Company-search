"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Building2, MapPin, Users, TrendingUp, ChevronRight, ExternalLink, Star, ArrowLeft } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { companyApi } from "@/services/api";
import type { Company, Job, Referral } from "@/types";
import { formatSalary, formatRelativeTime } from "@/lib/utils";

export default function CompanyDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [company, setCompany] = useState<Company | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("jobs");

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    setError(null);
    Promise.all([
      companyApi.detail(slug).then((r) => setCompany(r.data.data ?? r.data)),
      companyApi.jobs(slug).then((r) => setJobs(r.data.data ?? r.data ?? [])),
    ]).catch((err: Error) => setError(err.message || "加载失败"))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-20 w-20 rounded-2xl skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-6" />
        <div className="h-8 w-48 skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-4" />
        <div className="h-4 w-72 skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-8" />
        <div className="space-y-3">{[1,2,3].map(i => <Card key={i} className="p-5"><div className="h-6 w-3/4 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>)}</div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-16">
          <Building2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">{error || "公司未找到"}</p>
          <Link href="/companies"><Button variant="outline">返回公司列表</Button></Link>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "jobs", label: "在招岗位", count: jobs.length },
    { id: "about", label: "公司介绍" },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/companies" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 mb-6">
        <ArrowLeft className="h-4 w-4" /> 返回公司列表
      </Link>

      {/* Company Header */}
      <div className="flex items-start gap-6 mb-8">
        <div className="h-20 w-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-3xl font-bold text-gray-600 dark:text-gray-400 shrink-0">
          {company.name?.charAt(0) || "?"}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold">{company.name}</h1>
            {company.stage && <Badge variant={company.stage === "上市公司" ? "info" : "primary"}>{company.stage}</Badge>}
          </div>
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-4">
            <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{company.city}</span>
            <span className="flex items-center gap-1"><Users className="h-4 w-4" />{company.scale}</span>
            <span>{company.industry}</span>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="primary" className="text-sm px-3 py-1">{company.hiringCount || 0} 个在招岗位</Badge>
            {company.averageSalary && <span className="text-sm text-gray-500">平均 {company.averageSalary}K</span>}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-default">
        {tabs.map((t) => (
          <button key={t.id} onClick={() => setActiveTab(t.id)}
            className={"px-4 py-3 text-sm font-medium border-b-2 transition-colors " + (activeTab === t.id ? "border-primary-500 text-primary-500" : "border-transparent text-gray-500 hover:text-gray-700")}>
            {t.label}{t.count ? " (" + t.count + ")" : ""}
          </button>
        ))}
      </div>

      {/* Jobs Tab */}
      {activeTab === "jobs" && (
        <div className="space-y-3">
          {jobs.length === 0 ? (
            <Card className="p-8 text-center"><p className="text-gray-500">暂无在招岗位</p></Card>
          ) : (
            jobs.map((job) => (
              <Link key={job.id} href={"/jobs/" + job.id}>
                <Card hover className="p-5 flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold mb-1">{job.title}</h3>
                    <p className="text-sm text-gray-500">{job.city} · {job.experience} · {job.education}</p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {job.skills?.slice(0, 4).map((s) => <Badge key={s} variant="default" className="text-xs">{s}</Badge>)}
                    </div>
                  </div>
                  <div className="text-right shrink-0 ml-4">
                    <p className="text-lg font-bold text-primary-500">{formatSalary(job.salaryMin, job.salaryMax)}</p>
                    {job.referralCount > 0 && <Badge variant="success" className="text-xs mt-1">内推 {job.referralCount}</Badge>}
                  </div>
                </Card>
              </Link>
            ))
          )}
        </div>
      )}

      {/* About Tab */}
      {activeTab === "about" && (
        <Card className="p-6">
          <h3 className="font-semibold mb-4">公司档案</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {[
              { label: "行业", value: company.industry },
              { label: "城市", value: company.city },
              { label: "规模", value: company.scale },
              { label: "阶段", value: company.stage },
            ].map((item) => (
              <div key={item.label} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <p className="text-gray-500 mb-1">{item.label}</p>
                <p className="font-medium">{item.value}</p>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

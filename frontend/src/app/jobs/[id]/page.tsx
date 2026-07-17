"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Star, ClipboardList, Bot, Clock, MapPin, Briefcase, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { jobApi } from "@/services/api";
import type { Job } from "@/types";
import { formatSalary, formatRelativeTime } from "@/lib/utils";

export default function JobDetailPage() {
  const params = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    setLoading(true);
    setError(null);
    jobApi.detail(params.id as string)
      .then((res) => {
        setJob(res.data.data ?? res.data);
      })
      .catch((err: Error) => setError(err.message || "加载失败"))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-4 w-32 skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-6" />
        <div className="h-8 w-2/3 skeleton-pulse bg-gray-200 dark:bg-gray-700 mb-4" />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">{[1,2,3,4,5].map(i => <Card key={i} className="p-3"><div className="h-10 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>)}</div>
        <Card className="p-5"><div className="h-40 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8 text-center">
        <p className="text-gray-500 mb-4">{error || "岗位未找到"}</p>
        <Link href="/jobs"><Button variant="outline">返回岗位列表</Button></Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/jobs" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 mb-6">
        <ArrowLeft className="h-4 w-4" /> 返回搜索结果
      </Link>

      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold mb-1">{job.title}</h1>
            <p className="text-gray-500">{job.company?.name || ""} · {job.city}</p>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-400 hover:text-yellow-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"><Star className="h-5 w-5" /></button>
            <Link href="/pipeline"><Button variant="outline" size="sm"><ClipboardList className="h-4 w-4" /> 投递管理</Button></Link>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          {[
            { label: "城市", value: job.city, icon: MapPin },
            { label: "薪资", value: formatSalary(job.salaryMin, job.salaryMax), accent: true },
            { label: "经验", value: job.experience, icon: Briefcase },
            { label: "学历", value: job.education, icon: GraduationCap },
            { label: "AI 匹配", value: job.matchScore ? job.matchScore + "%" : "—", accent: true },
          ].map((item, i) => (
            <Card key={i} className={"p-3 text-center " + (item.accent ? "border-primary-200 dark:border-primary-800" : "")}>
              <p className="text-xs text-gray-500 mb-1">{item.label}</p>
              <p className={"text-sm font-semibold " + (item.accent ? "text-primary-500" : "")}>
                {item.icon && <item.icon className="h-3 w-3 inline mr-1" />}{item.value}
              </p>
            </Card>
          ))}
        </div>
      </div>

      {/* Skills */}
      <Card className="mb-6 p-5">
        <h2 className="font-semibold mb-4">技能要求</h2>
        <div className="flex flex-wrap gap-2">
          {job.skills?.map((s) => (<Badge key={s} variant="default" className="text-sm px-3 py-1">{s}</Badge>)) || <p className="text-sm text-gray-500">暂无技能要求</p>}
        </div>
      </Card>

      {/* Career Timeline */}
      {job.publishedAt && (
        <Card className="mb-6 p-5">
          <div className="flex items-center gap-2 mb-4"><Clock className="h-4 w-4 text-gray-400" /><h2 className="font-semibold">职位时间轴</h2></div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2"><div className="h-2 w-2 rounded-full bg-green-500" /><span className="text-gray-500">{formatRelativeTime(job.publishedAt)}</span></div>
            <Badge variant="success">招聘中</Badge>
          </div>
        </Card>
      )}

      {/* AI Quick */}
      <Card className="p-5 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/10 border-primary-200 dark:border-primary-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="h-6 w-6 text-primary-500" />
            <div><p className="font-medium text-sm">AI 求职助手</p><p className="text-sm text-gray-500">分析这个岗位是否适合你？</p></div>
          </div>
          <Button variant="primary" size="sm"><Bot className="h-4 w-4" /> 咨询 AI</Button>
        </div>
      </Card>
    </div>
  );
}

"use client";

import React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Building2, ExternalLink, Star, MapPin, TrendingUp, Bot, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";

const MOCK = {
  name: "字节跳动", slug: "bytedance", industry: "互联网", city: "北京", scale: "2000+", stage: "独角兽",
  website: "https://www.bytedance.com", description: "字节跳动是一家全球化的科技公司，旗下产品包括今日头条、抖音、TikTok 等。",
  hiringCount: 128, avgSalary: 45, interviewDifficulty: "困难", educationReq: "本科",
  profile: { overall: 8.5, salary: 8.0, culture: 7.5, growth: 9.0, stability: 7.0, hiringTrend: "增长", heat: 85 },
  jobs: [
    { id: "1", title: "AI算法工程师", city: "上海", salary: "50K-80K", match: 92, referrals: 5 },
    { id: "2", title: "Java后端开发", city: "深圳", salary: "30K-60K", match: 85, referrals: 3 },
    { id: "3", title: "产品经理", city: "北京", salary: "35K-55K", match: 78, referrals: 2 },
  ],
  referrals: [
    { code: "NTABkC8", score: 95, person: "张三", job: "Java后端", verified: true, time: "3天前" },
    { code: "XYZ789", score: 80, person: "王五", job: "AI算法", verified: true, time: "5天前" },
  ],
};

const COMP_TABS = [
  { id: "jobs", label: "全部岗位", count: MOCK.jobs.length },
  { id: "referrals", label: "内推", count: MOCK.referrals.length },
  { id: "profile", label: "AI 公司画像" },
];

export default function CompanyDetailPage() {
  const params = useParams();
  const [activeTab, setActiveTab] = React.useState("jobs");

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/companies" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 mb-6">
        <ArrowLeft className="h-4 w-4" /> 返回公司列表
      </Link>

      <div className="flex items-start justify-between mb-8">
        <div className="flex items-center gap-5">
          <div className="h-20 w-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-3xl font-bold text-gray-600 dark:text-gray-400 shrink-0">
            {MOCK.name.charAt(0)}
          </div>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold">{MOCK.name}</h1>
              <Badge variant={MOCK.stage === "上市公司" ? "info" : "primary"} className="text-xs">{MOCK.stage}</Badge>
            </div>
            <p className="text-sm text-gray-500 mb-2">{MOCK.industry} · {MOCK.city} · {MOCK.scale}人</p>
            <div className="flex items-center gap-2">
              <Badge variant="primary">{MOCK.hiringCount} 个岗位</Badge>
              <a href={MOCK.website} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs text-primary-500 hover:text-primary-600">
                官网 <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm"><Star className="h-4 w-4" /> 关注</Button>
          <Button variant="primary" size="sm"><Building2 className="h-4 w-4" /> 查看全部岗位</Button>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
        <Card className="p-4 text-center">
          <p className="text-2xl font-bold text-primary-500">{MOCK.hiringCount}</p>
          <p className="text-xs text-gray-500 mt-1">在招岗位</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-2xl font-bold text-green-500">{MOCK.avgSalary}K</p>
          <p className="text-xs text-gray-500 mt-1">平均薪资</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-lg font-bold">{"\u2605".repeat(4)}</p>
          <p className="text-xs text-gray-500 mt-1">面试难度</p>
        </Card>
        <Card className="p-4 text-center">
          <p className="text-lg font-bold text-amber-500">{MOCK.profile.heat}/100</p>
          <p className="text-xs text-gray-500 mt-1">招聘热度</p>
        </Card>
      </div>

      {/* AI Company Profile */}
      <Card className="mb-8 p-6 border-primary-200 dark:border-primary-800">
        <div className="flex items-center gap-2 mb-6">
          <div className="h-8 w-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
            <Bot className="h-4 w-4 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="font-semibold">AI 公司画像</h2>
          <Badge variant="primary" className="text-xs">{MOCK.profile.overall}/10 综合评分</Badge>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-3">
            {[
              { label: "薪资", score: MOCK.profile.salary, color: "bg-blue-500" },
              { label: "文化", score: MOCK.profile.culture, color: "bg-green-500" },
              { label: "成长", score: MOCK.profile.growth, color: "bg-purple-500" },
              { label: "稳定", score: MOCK.profile.stability, color: "bg-amber-500" },
            ].map((dim) => (
              <div key={dim.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">{dim.label}</span>
                  <span className="font-medium">{dim.score}/10</span>
                </div>
                <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
                  <div className={"h-2 rounded-full " + dim.color} style={{ width: dim.score * 10 + "%" }} />
                </div>
              </div>
            ))}
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium mb-1">招聘趋势</p>
              <p className="text-sm text-green-600 dark:text-green-400 flex items-center gap-1">
                <TrendingUp className="h-4 w-4" /> {MOCK.profile.hiringTrend}中 · 热度 {MOCK.profile.heat}/100
              </p>
            </div>
            <div>
              <p className="text-sm font-medium mb-2">内推活跃度</p>
              <Badge variant="success" className="text-xs">高 ({MOCK.referrals.length} 个有效内推)</Badge>
            </div>
            <div>
              <p className="text-sm font-medium mb-1">面试难度</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{MOCK.interviewDifficulty} · 平均 4 轮</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <Tabs tabs={COMP_TABS} activeTab={activeTab} onChange={setActiveTab} className="mb-6" />

      {activeTab === "jobs" && (
        <div className="space-y-3">
          {MOCK.jobs.map((job) => (
            <Link key={job.id} href={"/jobs/" + job.id}>
              <Card hover className="p-5 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold mb-1">{job.title}</h3>
                  <p className="text-sm text-gray-500">{job.city} · {job.salary}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="primary" className="text-xs">{job.match}% 匹配</Badge>
                  <Badge variant="success" className="text-xs">内推 {job.referrals}个</Badge>
                  <ChevronRight className="h-4 w-4 text-gray-300" />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {activeTab === "referrals" && (
        <div className="space-y-3">
          {MOCK.referrals.map((ref, i) => (
            <Card key={i} hover className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-center min-w-[90px]">
                  <code className="text-base font-mono font-bold text-primary-500">{ref.code}</code>
                  <p className="text-xs text-gray-500">{ref.score}/100</p>
                </div>
                <div>
                  <p className="text-sm font-medium">{ref.person} · {ref.job}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {ref.verified ? <Badge variant="success" className="text-[10px]">员工认证</Badge> : null}
                    <span className="text-xs text-gray-400">{ref.time}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">复制</Button>
                <Button variant="primary" size="sm">投递</Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {activeTab === "profile" && (
        <Card className="p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            {MOCK.name}目前处于快速扩张期，在 AI、推荐算法等领域持续投入。公司薪资高于行业平均 20%，技术氛围浓厚，但加班较多、竞争激烈。
            建议关注其 AI 算法和后端开发岗位，内推成功率较高。
          </p>
          <div className="mt-4 flex flex-wrap gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">优点</p>
              <Badge variant="success" className="text-xs">薪资高</Badge>
              <Badge variant="success" className="text-xs ml-1">成长快</Badge>
              <Badge variant="success" className="text-xs ml-1">技术氛围好</Badge>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">缺点</p>
              <Badge variant="warning" className="text-xs">加班多</Badge>
              <Badge variant="warning" className="text-xs ml-1">竞争激烈</Badge>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}

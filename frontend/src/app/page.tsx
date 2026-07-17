"use client";

import React from "react";
import Link from "next/link";
import { ArrowRight, TrendingUp, Sparkles, Building2, Clock, ChevronRight, Search, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const HOT_COMPANIES = [
  { name: "字节跳动", slug: "bytedance", count: 128, logo: "B" },
  { name: "腾讯", slug: "tencent", count: 95, logo: "T" },
  { name: "阿里巴巴", slug: "alibaba", count: 82, logo: "A" },
  { name: "美团", slug: "meituan", count: 45, logo: "M" },
  { name: "京东", slug: "jd", count: 38, logo: "J" },
  { name: "拼多多", slug: "pdd", count: 35, logo: "P" },
];

const DAILY_NEW = [
  { company: "字节跳动", count: 31, color: "bg-blue-500" },
  { company: "腾讯", count: 12, color: "bg-green-500" },
  { company: "阿里巴巴", count: 18, color: "bg-orange-500" },
  { company: "OpenAI", count: 5, color: "bg-purple-500" },
];

const HOT_SKILLS = ["AI算法", "Java", "前端开发", "Python", "大模型", "Golang", "React", "产品经理"];

const RECOMMENDED_JOBS = [
  { title: "AI算法工程师", company: "字节跳动", city: "上海", salary: "50K-80K", match: 92, referrals: 5, skills: ["Python", "PyTorch"] },
  { title: "Java后端开发", company: "腾讯", city: "深圳", salary: "30K-60K", match: 85, referrals: 3, skills: ["Java", "Spring Boot"] },
  { title: "产品经理", company: "阿里巴巴", city: "杭州", salary: "35K-55K", match: 78, referrals: 2, skills: ["产品策略", "数据分析"] },
  { title: "前端架构师", company: "美团", city: "北京", salary: "45K-70K", match: 88, referrals: 4, skills: ["React", "TypeScript"] },
];

export default function HomePage() {
  const [searchQuery, setSearchQuery] = React.useState("");

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
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索岗位、公司、技能..."
              className="w-full h-14 pl-12 pr-36 rounded-2xl border border-gray-200 dark:border-gray-700 bg-primary text-base shadow-sm focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <Link href={"/jobs?q=" + searchQuery}>
                <Button variant="primary" size="md">
                  <Search className="h-4 w-4" />
                  AI 搜索
                </Button>
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

      {/* AI Daily Opportunities */}
      <section className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <Clock className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">今日新增岗位</h2>
              <p className="text-sm text-gray-500">AI 实时监测 · 156 个新岗位今日发布</p>
            </div>
          </div>
          <Link href="/daily" className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1">
            查看全部 <ChevronRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {DAILY_NEW.map((item) => (
            <Link key={item.company} href={"/companies/" + item.company}>
              <Card hover className="p-4">
                <div className="flex items-center gap-3">
                  <div className={"h-10 w-10 rounded-xl " + item.color + " flex items-center justify-center text-white font-bold text-sm"}>
                    {item.company.charAt(0)}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{item.company}</p>
                    <p className="text-2xl font-bold text-primary-500">{item.count}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">今日新增岗位</p>
              </Card>
            </Link>
          ))}
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
              <h2 className="text-lg font-semibold">AI 推荐岗位</h2>
              <p className="text-sm text-gray-500">根据你的浏览记录智能推荐</p>
            </div>
          </div>
          <Link href="/ai-recommend">
            <Button variant="outline" size="sm">
              上传简历获取精准推荐 <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {RECOMMENDED_JOBS.map((job, i) => (
            <Link key={i} href={"/jobs/" + (i + 1)}>
              <Card hover className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-[15px] mb-1">{job.title}</h3>
                    <p className="text-sm text-gray-500">{job.company} · {job.city}</p>
                  </div>
                  <Badge variant="primary" className="text-xs font-bold">{job.match}% 匹配</Badge>
                </div>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-lg font-bold text-primary-500">{job.salary}</span>
                  <Badge variant="success">内推 {job.referrals}个</Badge>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {job.skills.map((s) => (<Badge key={s} variant="default" className="text-xs">{s}</Badge>))}
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Hot Companies */}
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
          {HOT_COMPANIES.map((c) => (
            <Link key={c.name} href={"/companies/" + c.slug}>
              <Card hover className="p-4 text-center">
                <div className="h-12 w-12 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-lg font-bold text-gray-600 dark:text-gray-400 mx-auto mb-2">{c.logo}</div>
                <p className="font-medium text-sm mb-1">{c.name}</p>
                <p className="text-xs text-primary-500 font-medium">{c.count} 个岗位</p>
              </Card>
            </Link>
          ))}
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
          {[
            { code: "NTABkC8", company: "字节跳动", job: "Java后端", score: 95, person: "张三", badge: "员工认证" },
            { code: "ABC123", company: "腾讯", job: "前端开发", score: 80, person: "李四", badge: "已认证" },
          ].map((ref, i) => (
            <Card key={i} hover className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <code className="text-lg font-mono font-bold text-primary-500">{ref.code}</code>
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-xs text-gray-500">可信度 {ref.score}/100</span>
                    <span className="text-yellow-500 text-xs">{new Array(Math.floor(ref.score / 20) + 1).join("\u2605")}</span>
                  </div>
                </div>
                <div className="border-l border-default pl-4">
                  <p className="font-medium text-sm">{ref.company} · {ref.job}</p>
                  <p className="text-xs text-gray-500">{ref.person} · {ref.badge} · 3天前发布</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">复制内推码</Button>
                <Button variant="primary" size="sm">官网投递</Button>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}

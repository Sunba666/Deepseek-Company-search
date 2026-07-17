"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Star, Share2, ClipboardList, ExternalLink, Copy, Check, Bot, Clock, MapPin, Briefcase, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const MOCK_JOB = {
  title: "AI算法工程师",
  company: "字节跳动",
  companySlug: "bytedance",
  city: "上海",
  salaryMin: 50,
  salaryMax: 80,
  experience: "3-5年",
  education: "硕士",
  skills: ["Python", "PyTorch", "Transformer", "大模型", "NLP", "分布式训练"],
  description: "负责大模型的训练、优化和落地应用，参与公司核心AI产品的算法研发。",
  requirements: "1. 扎实的机器学习/深度学习基础\n2. 熟悉Transformer架构\n3. 有大模型训练经验优先",
  sourceUrl: "https://jobs.bytedance.com",
  publishedAt: "2024-01-15",
  updatedAt: "2024-01-20",
  referrals: [
    { code: "NTABkC8", score: 95, person: "张三", title: "高级工程师", verified: true, time: "3天前" },
    { code: "ABC123", score: 60, person: "李四", title: "工程师", verified: false, time: "10天前" },
  ],
};

export default function JobDetailPage() {
  const params = useParams();
  const [copied, setCopied] = React.useState(false);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const stars = (score: number) => {
    const count = Math.floor(score / 20);
    let result = "";
    for (let i = 0; i < count; i++) result += "\u2605";
    return result;
  };

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/jobs" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 mb-6">
        <ArrowLeft className="h-4 w-4" /> 返回搜索结果
      </Link>

      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold mb-1">{MOCK_JOB.title}</h1>
            <p className="text-gray-500">{MOCK_JOB.company} · {MOCK_JOB.city}</p>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-400 hover:text-yellow-500 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
              <Star className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
              <Share2 className="h-5 w-5" />
            </button>
            <Link href="/pipeline">
              <Button variant="outline" size="sm">
                <ClipboardList className="h-4 w-4" /> 投递管理
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
          {[
            { label: "城市", value: MOCK_JOB.city, icon: MapPin },
            { label: "薪资", value: MOCK_JOB.salaryMin + "K-" + MOCK_JOB.salaryMax + "K", accent: true },
            { label: "经验", value: MOCK_JOB.experience, icon: Briefcase },
            { label: "学历", value: MOCK_JOB.education, icon: GraduationCap },
            { label: "AI 匹配", value: "92%", accent: true },
          ].map((item, i) => (
            <Card key={i} className={"p-3 text-center " + (item.accent ? "border-primary-200 dark:border-primary-800" : "")}>
              <p className="text-xs text-gray-500 mb-1">{item.label}</p>
              <p className={"text-sm font-semibold " + (item.accent ? "text-primary-500" : "")}>
                {item.icon && React.createElement(item.icon, { className: "h-3 w-3 inline mr-1" })}
                {item.value}
              </p>
            </Card>
          ))}
        </div>
      </div>

      {/* AI Analysis */}
      <Card className="mb-6 p-5 border-primary-200 dark:border-primary-800">
        <div className="flex items-center gap-2 mb-4">
          <div className="h-8 w-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
            <Bot className="h-4 w-4 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="font-semibold">AI JD 分析</h2>
        </div>
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">匹配度</span>
            <span className="text-sm font-bold text-primary-500">92% · 非常匹配</span>
          </div>
          <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className="h-2 rounded-full bg-primary-500" style={{ width: "92%" }} />
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-sm font-medium text-green-600 dark:text-green-400 mb-2">已具备技能</h4>
            <div className="flex flex-wrap gap-1.5">
              {["Python", "PyTorch", "Transformer", "NLP"].map((s) => (<Badge key={s} variant="success" className="text-xs">{s}</Badge>))}
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-amber-600 dark:text-amber-400 mb-2">缺失技能</h4>
            <Badge variant="warning" className="text-xs">推荐系统</Badge>
            <p className="text-xs text-gray-500 mt-1">学习建议: Andrew Ng 推荐系统课程</p>
          </div>
        </div>
      </Card>

      {/* Description */}
      <Card className="mb-6 p-5">
        <h2 className="font-semibold mb-4">职位描述</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">{MOCK_JOB.description}</p>
        <h3 className="text-sm font-semibold mb-2">任职要求</h3>
        <pre className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap font-sans">{MOCK_JOB.requirements}</pre>
      </Card>

      {/* Timeline */}
      <Card className="mb-6 p-5">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="h-4 w-4 text-gray-400" />
          <h2 className="font-semibold">职位时间轴</h2>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            <span className="text-gray-500">发布 {MOCK_JOB.publishedAt}</span>
          </div>
          <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-blue-500" />
            <span className="text-gray-500">更新 {MOCK_JOB.updatedAt}</span>
          </div>
          <Badge variant="success">招聘中</Badge>
        </div>
      </Card>

      {/* Referrals */}
      <Card className="mb-6 p-5">
        <h2 className="font-semibold mb-4">内推码（共 {MOCK_JOB.referrals.length} 个）</h2>
        <div className="space-y-3">
          {MOCK_JOB.referrals.map((ref, i) => (
            <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-default hover:border-primary-300 dark:hover:border-primary-700 transition-colors">
              <div className="flex items-center gap-4">
                <div className="text-center min-w-[100px]">
                  <code className="text-lg font-mono font-bold text-primary-500 tracking-wider">{ref.code}</code>
                  <div className="flex items-center justify-center gap-1 mt-0.5">
                    <span className="text-xs text-gray-500">{ref.score}/100</span>
                    <span className="text-yellow-500 text-xs">{stars(ref.score)}</span>
                  </div>
                </div>
                <div className="border-l border-default pl-4">
                  <p className="text-sm font-medium">{ref.person} · {ref.title}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {ref.verified
                      ? <Badge variant="success" className="text-[10px]">员工认证</Badge>
                      : <Badge variant="warning" className="text-[10px]">未认证</Badge>
                    }
                    <span className="text-xs text-gray-400">{ref.time}发布</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => handleCopy(ref.code)}>
                  {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                  {copied ? "已复制" : "复制"}
                </Button>
                <a href={MOCK_JOB.sourceUrl} target="_blank" rel="noopener noreferrer">
                  <Button variant="primary" size="sm">官网投递 <ExternalLink className="h-4 w-4" /></Button>
                </a>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* AI Quick */}
      <Card className="p-5 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/10 border-primary-200 dark:border-primary-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot className="h-6 w-6 text-primary-500" />
            <div>
              <p className="font-medium text-sm">AI 求职助手</p>
              <p className="text-sm text-gray-500">分析这个岗位是否适合你？</p>
            </div>
          </div>
          <Button variant="primary" size="sm"><Bot className="h-4 w-4" /> 咨询 AI</Button>
        </div>
      </Card>
    </div>
  );
}

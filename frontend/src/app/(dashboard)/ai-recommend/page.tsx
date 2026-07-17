"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Upload, Sparkles, Briefcase, MapPin, DollarSign, GraduationCap, Target, ChevronRight, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { FileUpload } from "@/components/common/file-upload";
import { cn } from "@/lib/utils";

export default function AIRecommendPage() {
  const [step, setStep] = useState<"upload" | "form" | "result">("upload");
  const [form, setForm] = useState({ skills: "", experience: "", education: "", city: "", salaryMin: "", salaryMax: "" });
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileUpload = (file: File) => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setForm({ skills: "Python, PyTorch, Java, Spring Boot", experience: "3", education: "本科", city: "上海", salaryMin: "30", salaryMax: "50" });
      setIsAnalyzing(false);
      setStep("form");
    }, 1500);
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      setStep("result");
    }, 2000);
  };

  const MOCK_RESULTS = [
    { title: "AI算法工程师", company: "字节跳动", city: "上海", salary: "50K-80K", match: 92, reason: "Python/PyTorch 经验高度匹配", skills: ["Python", "PyTorch", "大模型"] },
    { title: "Java后端开发", company: "腾讯", city: "深圳", salary: "30K-60K", match: 85, reason: "Java/Spring Boot 经验匹配", skills: ["Java", "Spring Boot", "MySQL"] },
    { title: "数据分析师", company: "美团", city: "上海", salary: "25K-45K", match: 78, reason: "数据处理经验匹配", skills: ["Python", "SQL", "数据分析"] },
    { title: "后端开发工程师", company: "字节跳动", city: "上海", salary: "35K-60K", match: 82, reason: "后端开发经验丰富", skills: ["Go", "Redis", "Kafka"] },
  ];

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="h-10 w-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
          <Sparkles className="h-5 w-5 text-green-600 dark:text-green-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">AI 岗位推荐</h1>
          <p className="text-sm text-gray-500">上传简历或填写信息，AI 为你智能匹配最适合的岗位</p>
        </div>
      </div>

      {/* Steps */}
      <div className="flex items-center gap-2 mb-8 text-sm">
        {[{ id: "upload", label: "上传简历" }, { id: "form", label: "确认信息" }, { id: "result", label: "匹配结果" }].map((s, i) => (
          <React.Fragment key={s.id}>
            <div className={"flex items-center gap-2 " + (step === s.id ? "text-primary-500 font-semibold" : "text-gray-400")}>
              <div className={"h-7 w-7 rounded-full flex items-center justify-center text-xs font-bold " + (step === s.id ? "bg-primary-100 dark:bg-primary-900/30 text-primary-500" : "bg-gray-100 dark:bg-gray-800")}>
                {i + 1}
              </div>
              {s.label}
            </div>
            {i < 2 && <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />}
          </React.Fragment>
        ))}
      </div>

      {step === "upload" && (
        <Card className="p-8">
          <FileUpload onUpload={handleFileUpload} />
          <div className="mt-6 text-center">
            <div className="flex items-center gap-2 justify-center mb-4">
              <div className="h-px w-12 bg-gray-200 dark:bg-gray-700" />
              <span className="text-xs text-gray-400">或</span>
              <div className="h-px w-12 bg-gray-200 dark:bg-gray-700" />
            </div>
            <Button variant="outline" onClick={() => setStep("form")}>
              手动填写信息 <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          {isAnalyzing && (
            <div className="mt-6 text-center">
              <div className="flex items-center justify-center gap-2 text-sm text-primary-500">
                <Bot className="h-5 w-5 animate-pulse" />
                AI 正在分析简历...
              </div>
            </div>
          )}
        </Card>
      )}

      {step === "form" && (
        <Card className="p-6">
          <h2 className="font-semibold mb-4">确认求职信息</h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div>
              <label className="text-sm font-medium mb-1 block">技能（逗号分隔）</label>
              <Input value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} placeholder="Python, Java, ..." />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">工作经验（年）</label>
              <Input type="number" value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">学历</label>
              <select value={form.education} onChange={(e) => setForm({ ...form, education: e.target.value })}
                className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
                <option>本科</option><option>硕士</option><option>博士</option><option>大专</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">目标城市</label>
              <select value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })}
                className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
                <option>上海</option><option>北京</option><option>深圳</option><option>杭州</option><option>广州</option><option>成都</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">期望最低薪资（K）</label>
              <Input type="number" value={form.salaryMin} onChange={(e) => setForm({ ...form, salaryMin: e.target.value })} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">期望最高薪资（K）</label>
              <Input type="number" value={form.salaryMax} onChange={(e) => setForm({ ...form, salaryMax: e.target.value })} />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => setStep("upload")}>返回</Button>
            <Button variant="primary" onClick={handleAnalyze} loading={isAnalyzing}>
              <Sparkles className="h-4 w-4" /> AI 匹配岗位
            </Button>
          </div>
        </Card>
      )}

      {step === "result" && (
        <div className="space-y-6">
          {isAnalyzing ? (
            <Card className="p-8 text-center">
              <Bot className="h-12 w-12 text-primary-500 animate-pulse mx-auto mb-4" />
              <p className="text-lg font-semibold mb-2">AI 正在分析...</p>
              <p className="text-sm text-gray-500">正在根据你的信息匹配最适合的岗位</p>
            </Card>
          ) : (
            <>
              {/* Match Overview */}
              <Card className="p-6 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/10 border-primary-200 dark:border-primary-800">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold mb-1">匹配分析完成</h2>
                    <p className="text-sm text-gray-500">为你找到 4 个高度匹配的岗位</p>
                  </div>
                  <div className="text-center">
                    <p className="text-3xl font-bold text-primary-500">85%</p>
                    <p className="text-xs text-gray-500">综合匹配度</p>
                  </div>
                </div>
              </Card>

              {/* Skill Analysis */}
              <Card className="p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="h-5 w-5 text-primary-500" />
                  <h3 className="font-semibold">技能分析</h3>
                </div>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium text-green-600 dark:text-green-400 mb-2">核心技能匹配</p>
                    <div className="flex flex-wrap gap-1.5">
                      {["Python", "Java", "Spring Boot", "PyTorch", "SQL"].map((s) => (<Badge key={s} variant="success" className="text-xs">{s}</Badge>))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-amber-600 dark:text-amber-400 mb-2">建议补充</p>
                    <div className="flex flex-wrap gap-1.5">
                      {["Redis", "Kafka", "Kubernetes", "AWS"].map((s) => (<Badge key={s} variant="warning" className="text-xs">{s}</Badge>))}
                    </div>
                    <p className="text-xs text-gray-500 mt-2">学习建议: Redis 官方文档 + Kafka 入门教程（预计 2 周）</p>
                  </div>
                </div>
              </Card>

              {/* Results */}
              <h3 className="font-semibold text-lg">推荐岗位（按匹配度排序）</h3>
              {MOCK_RESULTS.map((job, i) => (
                <Link key={i} href={"/jobs/" + (i + 1)}>
                  <Card hover className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{job.title}</h3>
                          <Badge variant="primary" className="text-xs font-bold">{job.match}%</Badge>
                        </div>
                        <p className="text-sm text-gray-500 mb-2">{job.company} · {job.city} · {job.salary}</p>
                        <p className="text-xs text-gray-400 mb-2">{job.reason}</p>
                        <div className="flex flex-wrap gap-1.5">
                          {job.skills.map((s) => (<Badge key={s} variant="default" className="text-xs">{s}</Badge>))}
                        </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-gray-300 shrink-0 mt-2" />
                    </div>
                  </Card>
                </Link>
              ))}

              {/* Resume Tips */}
              <Card className="p-5 border-primary-200 dark:border-primary-800">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="h-5 w-5 text-primary-500" />
                  <h3 className="font-semibold">简历优化建议</h3>
                </div>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li className="flex items-start gap-2">· 突出大模型落地项目经验，用数据量化成果</li>
                  <li className="flex items-start gap-2">· 补充 Redis/Kafka 相关项目经验</li>
                  <li className="flex items-start gap-2">· 使用 STAR 法则重写项目经历</li>
                  <li className="flex items-start gap-2">· 建议投递顺序: 字节跳动AI算法 {">"} 腾讯后端 {">"} 字节跳动后端</li>
                </ul>
              </Card>

              <div className="flex items-center gap-3">
                <Button variant="outline" onClick={() => setStep("upload")}>重新上传简历</Button>
                <Button variant="outline" onClick={() => setStep("form")}>修改信息</Button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

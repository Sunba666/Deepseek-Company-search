"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Upload, Sparkles, Briefcase, MapPin, Target, ChevronRight, Bot, Building2, BookOpen, TrendingUp, Loader2, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { FileUpload } from "@/components/common/file-upload";
import { useAuthStore } from "@/store";
import { aiApi, jobApi } from "@/services/api";
import { cn } from "@/lib/utils";
import type { Job } from "@/types";

export default function AIRecommendPage() {
  const { user } = useAuthStore();
  const [tab, setTab] = useState<"personalized" | "manual">("personalized");
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<any>(null);
  const [rawContent, setRawContent] = useState("");
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState("");

  // Manual form
  const [form, setForm] = useState({ skills: "", experience: "", education: "", city: "", salaryMin: "", salaryMax: "" });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [manualResult, setManualResult] = useState("");

  // Load personalized recommendations
  useEffect(() => {
    if (tab === "personalized") loadPersonalized();
  }, [tab]);

  const loadPersonalized = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await aiApi.personalizedRecommend({ userId: user?.id || "anonymous" });
      const data = res.data.data ?? res.data;
      setRecommendations(data.recommendations);
      setRawContent(data.raw || "");
      setStats(data.stats);
    } catch (err: any) {
      setError(err.message || "加载推荐失败");
    } finally {
      setLoading(false);
    }
  };

  const handleManualAnalyze = async () => {
    setIsAnalyzing(true);
    setManualResult("");
    try {
      // Fetch recent jobs for AI context
      const jobsRes = await jobApi.list({ limit: 10, sort: "published_at", order: "desc" });
      const jobs = jobsRes.data.data ?? [];
      const jobsStr = jobs.map((j: Job) => `${j.title} @ ${j.company?.name || ""} ${j.city} ${j.salaryMin}K-${j.salaryMax}K`).join("; ");

      const res = await aiApi.recommendJobs({ resume_text: "技能: " + form.skills + ", 经验: " + form.experience + "年, 城市: " + form.city, skills: form.skills.split(",").map((s) => s.trim()), city: form.city });
      setManualResult(JSON.stringify(res.data?.data || res.data || "分析完成", null, 2));
    } catch (err: any) {
      setManualResult("AI 分析暂时不可用: " + (err.message || "请稍后重试"));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const formFields = [
    { key: "skills" as const, label: "核心技能", placeholder: "例: Python, Java, React" },
    { key: "experience" as const, label: "工作经验", placeholder: "例: 3", hint: "年" },
    { key: "education" as const, label: "最高学历", placeholder: "例: 本科" },
    { key: "city" as const, label: "期望城市", placeholder: "例: 北京" },
    { key: "salaryMin" as const, label: "期望薪资(最低K)", placeholder: "例: 20" },
    { key: "salaryMax" as const, label: "期望薪资(最高K)", placeholder: "例: 50" },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="h-10 w-10 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
          <Sparkles className="h-5 w-5 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">AI 智能推荐</h1>
          <p className="text-sm text-gray-500">基于你的背景智能匹配最合适的岗位、公司和学习方向</p>
        </div>
      </div>

      {/* Tab selector */}
      <div className="flex gap-1 mb-6 border-b border-default">
        <button onClick={() => setTab("personalized")}
          className={"flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors " + (tab === "personalized" ? "border-primary-500 text-primary-500" : "border-transparent text-gray-500")}>
          <Bot className="h-4 w-4" /> 个性化推荐
        </button>
        <button onClick={() => setTab("manual")}
          className={"flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors " + (tab === "manual" ? "border-primary-500 text-primary-500" : "border-transparent text-gray-500")}>
          <Upload className="h-4 w-4" /> 手动填写
        </button>
      </div>

      {/* Personalized Tab */}
      {tab === "personalized" && (
        <div>
          {loading && (
            <Card className="p-12 text-center">
              <Loader2 className="h-12 w-12 text-primary-500 animate-spin mx-auto mb-4" />
              <p className="text-gray-500">AI 正在分析你的背景并生成推荐...</p>
            </Card>
          )}

          {error && (
            <Card className="p-8 text-center">
              <p className="text-gray-500 mb-4">{error}</p>
              <Button variant="outline" onClick={loadPersonalized}>重试</Button>
              <Button variant="ghost" onClick={() => setTab("manual")} className="ml-2">手动填写</Button>
            </Card>
          )}

          {!loading && !error && stats && (
            <Card className="p-4 mb-6 bg-gray-50 dark:bg-gray-800/50 flex items-center justify-around text-sm">
              <span>📊 <span className="font-medium">{stats.totalJobs || 0}</span> 个可投递岗位</span>
              <span>🔧 <span className="font-medium">{stats.userSkills || 0}</span> 项技能</span>
              <span>🔍 <span className="font-medium">{stats.recentSearches || 0}</span> 次近期搜索</span>
            </Card>
          )}

          {!loading && !error && recommendations && (
            <div className="space-y-6">
              {/* Summary */}
              {recommendations.summary && (
                <Card className="p-6 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/10 border-primary-200">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="h-5 w-5 text-primary-500" />
                    <h2 className="font-semibold">推荐总结</h2>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{recommendations.summary}</p>
                </Card>
              )}

              {/* Job Recommendations */}
              {recommendations.jobRecommendations?.length > 0 && (
                <div>
                  <h2 className="font-semibold mb-4 flex items-center gap-2"><Briefcase className="h-5 w-5 text-primary-500" /> 推荐岗位</h2>
                  <div className="grid md:grid-cols-2 gap-3">
                    {recommendations.jobRecommendations.map((rec: any, i: number) => (
                      <Card key={i} className="p-5">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-semibold">{rec.jobTitle}</h3>
                            <p className="text-sm text-gray-500">{rec.company}</p>
                          </div>
                          {rec.matchScore && (
                            <div className="text-center">
                              <div className={"h-10 w-10 rounded-full flex items-center justify-center text-sm font-bold " + (rec.matchScore >= 80 ? "bg-green-100 text-green-600" : rec.matchScore >= 60 ? "bg-amber-100 text-amber-600" : "bg-gray-100 text-gray-500")}>
                                {rec.matchScore}
                              </div>
                              <p className="text-[10px] text-gray-400 mt-0.5">匹配</p>
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 leading-relaxed mb-3">{rec.matchReason}</p>
                        {rec.actionable && <Badge variant="success" className="text-[10px]">可投递</Badge>}
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Company Recommendations */}
              {recommendations.companyRecommendations?.length > 0 && (
                <div>
                  <h2 className="font-semibold mb-4 flex items-center gap-2"><Building2 className="h-5 w-5 text-amber-500" /> 推荐公司</h2>
                  <div className="grid md:grid-cols-2 gap-3">
                    {recommendations.companyRecommendations.map((rec: any, i: number) => (
                      <Card key={i} className="p-4 flex items-center gap-4">
                        <div className={"h-12 w-12 rounded-xl flex items-center justify-center text-lg font-bold " + (rec.priority === "high" ? "bg-green-100 text-green-600" : "bg-amber-100 text-amber-600")}>
                          {rec.companyName?.charAt(0) || "?"}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-sm">{rec.companyName}</h3>
                          <p className="text-xs text-gray-500">{rec.industry}</p>
                          <p className="text-xs text-gray-400 mt-1">{rec.reason}</p>
                          {rec.priority === "high" && <Badge variant="success" className="text-[9px] mt-1">强烈推荐</Badge>}
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Learning Suggestions */}
              {recommendations.learningSuggestions?.length > 0 && (
                <div>
                  <h2 className="font-semibold mb-4 flex items-center gap-2"><BookOpen className="h-5 w-5 text-purple-500" /> 学习建议</h2>
                  <div className="grid md:grid-cols-2 gap-3">
                    {recommendations.learningSuggestions.map((sug: any, i: number) => (
                      <Card key={i} className="p-4">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge variant={sug.importance === "high" ? "error" : sug.importance === "medium" ? "warning" : "default"} className="text-[10px]">
                            {sug.importance === "high" ? "优先" : sug.importance === "medium" ? "建议" : "可选"}
                          </Badge>
                          <h3 className="font-medium text-sm">{sug.skill}</h3>
                        </div>
                        {sug.resources?.length > 0 && (
                          <ul className="text-xs text-gray-500 space-y-1">
                            {sug.resources.map((r: any, j: number) => <li key={j} className="flex items-start gap-1">• {typeof r === 'string' ? r : r.name || r}</li>)}
                          </ul>
                        )}
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {!recommendations.jobRecommendations && !recommendations.companyRecommendations && !recommendations.learningSuggestions && rawContent && (
                <Card className="p-6">
                  <h2 className="font-semibold mb-4">AI 分析结果</h2>
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">{rawContent}</div>
                </Card>
              )}
            </div>
          )}
        </div>
      )}

      {/* Manual Tab */}
      {tab === "manual" && (
        <Card className="p-6">
          <h2 className="font-semibold mb-4">填写你的信息</h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            {formFields.map((f) => (
              <div key={f.key}>
                <label className="text-sm font-medium mb-1 block">{f.label}</label>
                <Input value={form[f.key]} onChange={(e) => setForm((p) => ({ ...p, [f.key]: e.target.value }))} placeholder={f.placeholder} />
                {f.hint && <p className="text-xs text-gray-400 mt-1">{f.hint}</p>}
              </div>
            ))}
          </div>
          <Button onClick={handleManualAnalyze} loading={isAnalyzing} size="lg">
            {isAnalyzing ? "AI 分析中..." : <><Sparkles className="h-4 w-4" /> AI 智能推荐</>}
          </Button>
        </Card>
      )}

      {/* Manual Result */}
      {manualResult && tab === "manual" && (
        <Card className="mt-6 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-5 w-5 text-primary-500" />
            <h2 className="font-semibold">AI 推荐结果</h2>
          </div>
          <div className="text-sm whitespace-pre-wrap leading-relaxed">{manualResult}</div>
          <Link href="/jobs"><Button variant="outline" className="mt-4">浏览全部岗位</Button></Link>
        </Card>
      )}
    </div>
  );
}

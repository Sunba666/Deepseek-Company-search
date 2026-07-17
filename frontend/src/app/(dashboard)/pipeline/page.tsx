"use client";

import React, { useState } from "react";
import { ClipboardList, Plus, TrendingUp, Target, Award, Clock, Bot } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/common/empty-state";
import { useApplicationStore } from "@/store";
import { APPLICATION_STATUS_LABELS, APPLICATION_STATUS_COLORS } from "@/constants";

const STATUS_FLOW = ["saved", "ready_to_apply", "applied", "hr_viewed", "written_test", "interview_1", "interview_2", "hr_interview", "offer", "rejected"];

const MOCK_APPS = [
  { id: "1", job: { id: "1", title: "AI算法工程师", company: { id: "1", name: "字节跳动" } }, status: "saved" as const, updatedAt: "2024-01-20" },
  { id: "2", job: { id: "2", title: "Java后端开发", company: { id: "2", name: "腾讯" } }, status: "ready_to_apply" as const, appliedAt: "2024-01-18", updatedAt: "2024-01-20" },
  { id: "3", job: { id: "3", title: "前端开发", company: { id: "3", name: "字节跳动" } }, status: "applied" as const, appliedAt: "2024-01-19", updatedAt: "2024-01-20" },
  { id: "4", job: { id: "4", title: "产品经理", company: { id: "4", name: "阿里巴巴" } }, status: "hr_viewed" as const, appliedAt: "2024-01-15", updatedAt: "2024-01-22" },
  { id: "5", job: { id: "5", title: "后端开发", company: { id: "5", name: "美团" } }, status: "interview_1" as const, appliedAt: "2024-01-10", updatedAt: "2024-01-24" },
  { id: "6", job: { id: "6", title: "数据开发", company: { id: "6", name: "拼多多" } }, status: "offer" as const, appliedAt: "2024-01-05", updatedAt: "2024-01-25" },
];

const STAGE_ICONS: Record<string, string> = {
  saved: "\uD83D\uDCCC", ready_to_apply: "\uD83D\uDCCB", applied: "\uD83D\uDCE4",
  hr_viewed: "\uD83D\uDC40", written_test: "\u270D\uFE0F", interview_1: "\uD83C\uDF99\uFE0F",
  interview_2: "\uD83C\uDF99\uFE0F", hr_interview: "\uD83E\uDD1D", offer: "\u2705", rejected: "\u274C",
};

export default function PipelinePage() {
  const [view, setView] = useState<"kanban" | "list" | "stats">("kanban");
  const { applications } = useApplicationStore();
  const apps = applications.length > 0 ? applications : MOCK_APPS;

  const stats: Record<string, number> = {
    total: apps.length,
    applied: apps.filter((a) => !["saved", "ready_to_apply", "rejected", "withdrawn"].includes(a.status)).length,
    interviewing: apps.filter((a) => ["interview_1", "interview_2", "hr_interview"].includes(a.status)).length,
    offer: apps.filter((a) => a.status === "offer").length,
    rejected: apps.filter((a) => a.status === "rejected").length,
  };
  stats.interviewRate = stats.applied > 0 ? Math.round((stats.interviewing / stats.applied) * 100) : 0;
  stats.offerRate = stats.applied > 0 ? Math.round((stats.offer / stats.applied) * 100) : 0;

  const renderKanban = () => (
    <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: "400px" }}>
      {STATUS_FLOW.map((status) => {
        const columnApps = apps.filter((a) => a.status === status);
        return (
          <div key={status} className="flex-shrink-0 w-64">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span>{STAGE_ICONS[status]}</span>
                <span className="text-sm font-medium">{APPLICATION_STATUS_LABELS[status]}</span>
              </div>
              <span className="text-xs text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">{columnApps.length}</span>
            </div>
            <div className="space-y-2">
              {columnApps.map((app) => (
                <Card key={app.id} className="p-3 cursor-grab active:cursor-grabbing card-hover">
                  <p className="text-sm font-medium mb-1">{app.job.title}</p>
                  <p className="text-xs text-gray-500 mb-2">{app.job.company.name}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-gray-400">{app.updatedAt}</span>
                    <div className="flex gap-1">
                      <button className="p-1 text-gray-400 hover:text-primary-500 transition-colors text-xs">\u2190</button>
                      <button className="p-1 text-gray-400 hover:text-primary-500 transition-colors text-xs">\u2192</button>
                    </div>
                  </div>
                </Card>
              ))}
              {columnApps.length === 0 && (
                <div className="h-20 rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-700 flex items-center justify-center">
                  <span className="text-xs text-gray-400">拖拽到此</span>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );

  const renderStats = () => (
    <div className="grid md:grid-cols-4 gap-4 mb-8">
      <Card className="p-5 text-center">
        <div className="h-10 w-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mx-auto mb-3">
          <ClipboardList className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        </div>
        <p className="text-3xl font-bold">{stats.total}</p>
        <p className="text-xs text-gray-500 mt-1">总投递</p>
      </Card>
      <Card className="p-5 text-center">
        <div className="h-10 w-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center mx-auto mb-3">
          <TrendingUp className="h-5 w-5 text-green-600 dark:text-green-400" />
        </div>
        <p className="text-3xl font-bold">{stats.interviewRate}%</p>
        <p className="text-xs text-gray-500 mt-1">面试率</p>
      </Card>
      <Card className="p-5 text-center">
        <div className="h-10 w-10 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mx-auto mb-3">
          <Target className="h-5 w-5 text-amber-600 dark:text-amber-400" />
        </div>
        <p className="text-3xl font-bold">{stats.offerRate}%</p>
        <p className="text-xs text-gray-500 mt-1">Offer 率</p>
      </Card>
      <Card className="p-5 text-center">
        <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mx-auto mb-3">
          <Award className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        </div>
        <p className="text-3xl font-bold text-green-500">{stats.offer}</p>
        <p className="text-xs text-gray-500 mt-1">Offer 数</p>
      </Card>
    </div>
  );

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
            <ClipboardList className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">投递管理</h1>
            <p className="text-sm text-gray-500">管理你的求职进度 · AI 智能建议</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            {(["kanban", "list", "stats"] as const).map((v) => (
              <button key={v} onClick={() => setView(v)}
                className={"px-3 py-1.5 rounded-md text-xs font-medium transition-colors " + (view === v ? "bg-white dark:bg-gray-700 shadow-sm" : "text-gray-500")}>
                {v === "kanban" ? "\uD83D\uDCCB 看板" : v === "list" ? "\uD83D\uDCCB 列表" : "\uD83D\uDCCA 统计"}
              </button>
            ))}
          </div>
          <Button variant="primary" size="sm"><Plus className="h-4 w-4" /> 添加投递</Button>
        </div>
      </div>

      {view === "stats" && renderStats()}

      <div className="flex items-center gap-6 mb-6 text-sm">
        <span>总投递 <strong>{stats.total}</strong></span>
        <span>面试率 <strong className="text-green-600">{stats.interviewRate}%</strong></span>
        <span>Offer率 <strong className="text-green-600">{stats.offerRate}%</strong></span>
        <span className="text-gray-400 flex items-center gap-1"><Clock className="h-3 w-3" /> 平均响应 5天</span>
      </div>

      {view === "kanban" && renderKanban()}

      {view === "list" && (
        <div className="space-y-2">
          {apps.map((app) => (
            <Card key={app.id} className="p-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-sm">{app.job.title}</p>
                <p className="text-xs text-gray-500">{app.job.company.name}</p>
              </div>
              <Badge className={"text-xs " + (APPLICATION_STATUS_COLORS[app.status] || "")}>
                {STAGE_ICONS[app.status]} {APPLICATION_STATUS_LABELS[app.status]}
              </Badge>
            </Card>
          ))}
        </div>
      )}

      {/* AI Suggestions */}
      <Card className="mt-8 p-5 bg-gradient-to-r from-primary-50 to-transparent dark:from-primary-900/10 border-primary-200 dark:border-primary-800">
        <div className="flex items-center gap-2 mb-3">
          <Bot className="h-5 w-5 text-primary-500" />
          <h3 className="font-semibold text-sm">AI 建议</h3>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          你的面试率 {stats.interviewRate}%，高于平均水平。建议关注字节跳动 AI 算法工程师岗位，匹配度 92%，内推码 NTABkC8 可信度 95/100。
        </p>
      </Card>
    </div>
  );
}

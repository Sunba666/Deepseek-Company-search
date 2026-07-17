"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { ClipboardList, Plus, TrendingUp, Target, Award, Clock, Bot, MapPin, DollarSign, GraduationCap, Briefcase, Calendar, FileText, Star, X, Edit3, ChevronDown, ChevronUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/common/empty-state";
import { APPLICATION_STATUS_LABELS, APPLICATION_STATUS_COLORS } from "@/constants";
import { applicationApi } from "@/services/api";
import type { Application } from "@/types";
import { formatRelativeTime, formatSalary } from "@/lib/utils";

const STATUS_FLOW = ["saved", "ready_to_apply", "applied", "hr_viewed", "written_test", "interview_1", "interview_2", "hr_interview", "offer", "rejected"];

const STAGE_ICONS: Record<string, string> = {
  saved: "📌", ready_to_apply: "📋", applied: "📤",
  hr_viewed: "👀", written_test: "✍️", interview_1: "🎙️",
  interview_2: "🎙️", hr_interview: "🤝", offer: "✅", rejected: "❌",
};

const NEXT_ACTIONS: Record<string, string[]> = {
  saved: ["ready_to_apply"], ready_to_apply: ["applied"], applied: ["hr_viewed"],
  hr_viewed: ["written_test"], written_test: ["interview_1"],
  interview_1: ["interview_2"], interview_2: ["hr_interview"],
  hr_interview: ["offer"], offer: ["rejected", "accepted"],
  rejected: [], withdrawn: [],
};

export default function PipelinePage() {
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"kanban" | "list" | "stats">("kanban");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [detailApp, setDetailApp] = useState<Application | null>(null);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [noteText, setNoteText] = useState("");

  const loadApps = () => {
    setLoading(true);
    applicationApi.list().then((res) => {
      setApps(res.data.data ?? []);
    }).catch((err: Error) => { setError(err.message || "加载失败"); setLoading(false); });
  };

  useEffect(() => { loadApps(); }, []);

  const stats = {
    total: apps.length,
    active: apps.filter((a) => !["saved", "rejected", "withdrawn", "offer", "accepted"].includes(a.status)).length,
    interviewing: apps.filter((a) => ["interview_1", "interview_2", "hr_interview"].includes(a.status)).length,
    offer: apps.filter((a) => a.status === "offer").length,
    rejected: apps.filter((a) => a.status === "rejected").length,
  };

  const advanceStatus = async (id: string, newStatus: string) => {
    try {
      await applicationApi.updateStatus(id, { status: newStatus as any });
      loadApps();
    } catch (err: any) {
      alert("状态更新失败: " + (err.message || "请重试"));
    }
  };

  const viewDetail = async (app: Application) => {
    setDetailApp(app);
    try {
      const res = await applicationApi.getInterviews(app.id);
      setInterviews(res.data.data ?? []);
    } catch {
      setInterviews([]);
    }
  };

  const saveNote = async () => {
    if (!detailApp) return;
    try {
      await applicationApi.updateNotes(detailApp.id, { notes: noteText });
      setShowNoteModal(false);
      loadApps();
    } catch {}
  };

  
  if (error) {
    return (
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-16">
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="text-primary-500 hover:text-primary-600 text-sm">重试</button>
        </div>
      </div>
    );
  }

if (loading) {
    return (
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">{Array.from({length:4}).map((_,i) => <Card key={i} className="p-4"><div className="h-10 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>)}</div>
        <Card className="p-8"><div className="h-32 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>
      </div>
    );
  }

  if (apps.length === 0) {
    return (
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-8">
        <EmptyState icon={<ClipboardList />} title="暂无投递记录" description="开始浏览岗位并建立你的求职管线吧" action={{ label: "浏览岗位", onClick: () => { window.location.href = "/jobs"; } }} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <ClipboardList className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">求职管线</h1>
            <p className="text-sm text-gray-500">管理你的全部求职进度 · {apps.length} 个申请</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {(["kanban", "list", "stats"] as const).map((v) => (
            <button key={v} onClick={() => setView(v)}
              className={"px-3 py-1.5 rounded-lg text-xs font-medium " + (view === v ? "bg-primary-500 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600")}>
              {v === "kanban" ? "看板" : v === "list" ? "列表" : "统计"}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {[
          { label: "全部投递", value: stats.total, icon: ClipboardList, color: "text-blue-500", bg: "bg-blue-50 dark:bg-blue-900/20" },
          { label: "进行中", value: stats.active, icon: TrendingUp, color: "text-green-500", bg: "bg-green-50 dark:bg-green-900/20" },
          { label: "面试中", value: stats.interviewing, icon: Target, color: "text-amber-500", bg: "bg-amber-50 dark:bg-amber-900/20" },
          { label: "Offer", value: stats.offer, icon: Award, color: "text-purple-500", bg: "bg-purple-50 dark:bg-purple-900/20" },
        ].map((s) => (
          <Card key={s.label} className="p-4 flex items-center gap-3">
            <div className={"h-10 w-10 rounded-xl " + s.bg + " flex items-center justify-center " + s.color}>
              <s.icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold">{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          </Card>
        ))}
      </div>

      {/* Kanban Board */}
      {view === "kanban" && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 overflow-x-auto">
          {STATUS_FLOW.filter((s) => s !== "rejected").map((status) => {
            const columnApps = apps.filter((a) => a.status === status);
            return (
              <div key={status} className="min-w-[200px]">
                <div className="flex items-center justify-between mb-3 sticky top-0 bg-primary z-10 py-1">
                  <div className="flex items-center gap-2">
                    <span>{STAGE_ICONS[status]}</span>
                    <span className="text-sm font-medium">{APPLICATION_STATUS_LABELS[status]}</span>
                  </div>
                  <Badge variant="default" className="text-xs">{columnApps.length}</Badge>
                </div>
                <div className="space-y-2 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
                  {columnApps.map((a) => (
                    <Card key={a.id} className="p-3 cursor-pointer hover:border-primary-300 transition-colors" onClick={() => viewDetail(a)}>
                      <div className="flex items-start justify-between mb-1">
                        <p className="font-medium text-sm leading-tight">{a.job?.title || ""}</p>
                        <button onClick={(e) => { e.stopPropagation(); setSelectedApp(a); setDetailApp(a); }}
                          className="p-0.5 text-gray-300 hover:text-primary-500 shrink-0">
                          <Edit3 className="h-3 w-3" />
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">{a.job?.company?.name || ""}</p>
                      {a.job && <p className="text-xs font-bold text-primary-500">{formatSalary(a.job.salaryMin, a.job.salaryMax)}</p>}
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-[10px] text-gray-400">{a.updatedAt ? formatRelativeTime(a.updatedAt) : ""}</span>
                        {a._count?.interviewRecords ? <Badge variant="primary" className="text-[9px]">面试{a._count.interviewRecords}</Badge> : null}
                      </div>
                      {/* Quick advance */}
                      {NEXT_ACTIONS[a.status]?.length > 0 && (
                        <div className="flex gap-1 mt-2 pt-2 border-t border-default">
                          {NEXT_ACTIONS[a.status].map((next) => (
                            <button key={next} onClick={(e) => { e.stopPropagation(); advanceStatus(a.id, next); }}
                              className="text-[10px] px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 hover:bg-primary-100 dark:hover:bg-primary-900/30 text-gray-600 dark:text-gray-400 hover:text-primary-600 transition-colors">
                              → {APPLICATION_STATUS_LABELS[next]}
                            </button>
                          ))}
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* List View */}
      {view === "list" && (
        <div className="space-y-2">
          {apps.map((a) => (
            <Card key={a.id} hover className="p-4 flex items-center justify-between" onClick={() => viewDetail(a)}>
              <div className="flex items-center gap-4">
                <div className="text-center min-w-[60px]">
                  <span className="text-lg">{STAGE_ICONS[a.status]}</span>
                  <Badge variant={APPLICATION_STATUS_COLORS[a.status]?.includes("green") ? "success" : "default"} className="text-[9px] block mt-1">{APPLICATION_STATUS_LABELS[a.status]}</Badge>
                </div>
                <div>
                  <p className="font-medium text-sm">{a.job?.title || ""}</p>
                  <p className="text-xs text-gray-500">{a.job?.company?.name || ""} · {a.job?.city || ""}</p>
                  {a.updatedAt && <p className="text-[10px] text-gray-400 mt-0.5">{formatRelativeTime(a.updatedAt)}</p>}
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-bold text-primary-500">{formatSalary(a.job?.salaryMin, a.job?.salaryMax)}</p>
                {a._count?.interviewRecords ? <Badge variant="primary" className="text-[9px]">{a._count.interviewRecords} 轮面试</Badge> : null}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Stats View */}
      {view === "stats" && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="font-semibold mb-4">状态分布</h2>
            <div className="space-y-3">
              {STATUS_FLOW.map((s) => {
                const cnt = apps.filter((a) => a.status === s).length;
                const pct = apps.length > 0 ? (cnt / apps.length * 100) : 0;
                return (
                  <div key={s}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span>{STAGE_ICONS[s]} {APPLICATION_STATUS_LABELS[s]}</span>
                      <span className="font-medium">{cnt}</span>
                    </div>
                    <div className="h-2 rounded-full bg-gray-100 dark:bg-gray-800">
                      <div className={"h-2 rounded-full transition-all " + (s === "offer" ? "bg-green-500" : s === "rejected" ? "bg-red-500" : "bg-primary-500")} style={{ width: pct + "%" }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="font-semibold mb-4">投递时间线</h2>
            <div className="space-y-3">
              {apps.slice(0, 10).map((a) => (
                <div key={a.id} className="flex items-start gap-3">
                  <div className="flex flex-col items-center">
                    <div className={"h-3 w-3 rounded-full " + (a.status === "offer" ? "bg-green-500" : a.status === "rejected" ? "bg-red-500" : "bg-primary-500")} />
                    <div className="w-px flex-1 bg-gray-200 dark:bg-gray-700" />
                  </div>
                  <div className="pb-3">
                    <p className="text-sm font-medium">{a.job?.title}</p>
                    <p className="text-xs text-gray-500">{a.job?.company?.name} · {APPLICATION_STATUS_LABELS[a.status]}</p>
                    <p className="text-[10px] text-gray-400">{a.updatedAt ? formatRelativeTime(a.updatedAt) : ""}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Detail Modal */}
      <Modal isOpen={!!detailApp} onClose={() => { setDetailApp(null); setInterviews([]); }} title={detailApp?.job?.title || ""} size="lg">
        {detailApp && (
          <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
            {/* Basic info */}
            <div className="grid grid-cols-2 gap-3">
              <div className="text-sm"><span className="text-gray-500">公司</span><p className="font-medium">{detailApp.job?.company?.name}</p></div>
              <div className="text-sm"><span className="text-gray-500">状态</span><Badge variant={detailApp.status === "offer" ? "success" : detailApp.status === "rejected" ? "error" : "info"}>{APPLICATION_STATUS_LABELS[detailApp.status]}</Badge></div>
              {detailApp.job?.city && <div className="text-sm"><span className="text-gray-500">城市</span><p className="font-medium">{detailApp.job.city}</p></div>}
              <div className="text-sm"><span className="text-gray-500">薪资</span><p className="font-bold text-primary-500">{formatSalary(detailApp.job?.salaryMin, detailApp.job?.salaryMax)}</p></div>
              {detailApp.expectedSalary && <div className="text-sm"><span className="text-gray-500">期望薪资</span><p className="font-medium">{detailApp.expectedSalary}K</p></div>}
              {detailApp.appliedAt && <div className="text-sm"><span className="text-gray-500">投递时间</span><p className="font-medium">{formatRelativeTime(detailApp.appliedAt)}</p></div>}
            </div>

            {/* Status actions */}
            <div>
              <p className="text-xs font-medium text-gray-500 mb-2">状态推进</p>
              <div className="flex flex-wrap gap-2">
                {NEXT_ACTIONS[detailApp.status]?.map((next) => (
                  <button key={next} onClick={() => { advanceStatus(detailApp.id, next); setDetailApp(null); }}
                    className="px-3 py-1.5 rounded-lg text-xs font-medium bg-primary-500 text-white hover:bg-primary-600">
                    {STAGE_ICONS[next]} {APPLICATION_STATUS_LABELS[next]}
                  </button>
                ))}
                {NEXT_ACTIONS[detailApp.status]?.length === 0 && <p className="text-xs text-gray-400">该状态无下一步操作</p>}
              </div>
            </div>

            {/* Notes */}
            <div>
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-gray-500 mb-1">备注</p>
                <button onClick={() => { setNoteText(detailApp.notes || ""); setShowNoteModal(true); }} className="text-xs text-primary-500">编辑</button>
              </div>
              <p className="text-sm">{detailApp.notes || "暂无备注"}</p>
            </div>

            {/* Salary record */}
            {detailApp.actualSalary && (
              <div className="text-sm"><span className="text-gray-500">实际薪资</span><p className="font-bold text-green-500">{detailApp.actualSalary}K</p></div>
            )}

            {/* Interview records */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-gray-500">面试记录 ({interviews.length})</p>
                <Link href={"/pipeline?app=" + detailApp.id + "&addInterview=true"} className="text-xs text-primary-500">+ 添加</Link>
              </div>
              {interviews.length === 0 ? (
                <p className="text-xs text-gray-400">暂无面试记录</p>
              ) : (
                <div className="space-y-2">
                  {interviews.map((iv: any, i: number) => (
                    <Card key={iv.id || i} className="p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">第 {iv.round} 轮 · {iv.interviewType === "technical" ? "技术面" : iv.interviewType === "hr" ? "HR面" : iv.interviewType === "manager" ? "主管面" : "其他"}</span>
                        {iv.result && <Badge variant={iv.result === "pass" ? "success" : iv.result === "fail" ? "error" : "warning"} className="text-[9px]">{iv.result === "pass" ? "通过" : iv.result === "fail" ? "未过" : "待定"}</Badge>}
                      </div>
                      {iv.interviewer && <p className="text-[10px] text-gray-500">面试官: {iv.interviewer} {iv.duration ? "· " + iv.duration + "分钟" : ""}</p>}
                      {iv.scheduledAt && <p className="text-[10px] text-gray-400">{new Date(iv.scheduledAt).toLocaleDateString("zh-CN")}</p>}
                      {iv.feedback && <p className="text-xs mt-1">{iv.feedback}</p>}
                    </Card>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-2">
              <Link href={"/jobs/" + detailApp.job?.id}><Button variant="outline" size="sm">查看岗位</Button></Link>
              <Button variant="outline" size="sm" onClick={() => { setDetailApp(null); }}>关闭</Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Note Edit Modal */}
      <Modal isOpen={showNoteModal} onClose={() => setShowNoteModal(false)} title="编辑备注">
        <div className="space-y-4">
          <textarea value={noteText} onChange={(e) => setNoteText(e.target.value)} rows={5}
            className="w-full rounded-lg border border-default bg-primary px-4 py-3 text-sm focus:outline-none focus:border-focused resize-y"
            placeholder="记录你的备注信息..." />
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setShowNoteModal(false)}>取消</Button>
            <Button onClick={saveNote}>保存</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

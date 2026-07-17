"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Search, Star, ExternalLink, Copy, Check, AlertCircle, Plus, Heart, Flag, ThumbsUp, Building2, User, ShieldCheck, TrendingUp, MessageSquare } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { referralApi, companyApi } from "@/services/api";
import type { Referral, Company } from "@/types";
import { formatRelativeTime } from "@/lib/utils";

export default function ReferralsPage() {
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [company, setCompany] = useState("鍏ㄩ儴鍏徃");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [favoritedIds, setFavoritedIds] = useState<Set<string>>(new Set());
  const [showModal, setShowModal] = useState<string | null>(null); // 'create' | referralId-rate | referralId-report
  const [successMsg, setSuccessMsg] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    referralApi.list({ page: 1 })
      .then((res) => {
        if (!cancelled) setReferrals(res.data.data ?? []);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message || "鍔犺浇澶辫触");
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  const companies = useMemo(() => {
    const names = Array.from(new Set(referrals.map((r) => r.company?.name).filter(Boolean)));
    return ["鍏ㄩ儴鍏徃", ...names.sort()] as string[];
  }, [referrals]);

  const filtered = useMemo(() => {
    return referrals.filter((r) => {
      if (company !== "鍏ㄩ儴鍏徃" && r.company?.name !== company) return false;
      if (search) {
        const q = search.toLowerCase();
        if (!r.company?.name?.toLowerCase().includes(q) &&
            !r.jobTitle?.toLowerCase().includes(q) &&
            !r.referralCode?.toLowerCase().includes(q) &&
            !r.referrerName?.toLowerCase().includes(q)) return false;
      }
      return true;
    });
  }, [referrals, company, search]);

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(code);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFavorite = async (id: string) => {
    try {
      const res = await referralApi.toggleFavorite(id);
      const fav = res.data.data?.favorited ?? false;
      setFavoritedIds((prev) => {
        const next = new Set(prev);
        if (fav) next.add(id); else next.delete(id);
        return next;
      });
    } catch {}
  };

  const showSuccess = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(""), 3000);
  };

  const confidenceColor = (score: number) =>
    score >= 80 ? "text-green-600 dark:text-green-400" :
    score >= 60 ? "text-amber-600 dark:text-amber-400" :
    "text-gray-500";

  const confidenceBg = (score: number) =>
    score >= 80 ? "bg-green-100 dark:bg-green-900/30 border-green-200 dark:border-green-800" :
    score >= 60 ? "bg-amber-100 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800" :
    "bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700";

  const stars = (score: number) => {
    let s = "";
    for (let i = 0; i < Math.floor(score / 20); i++) s += "★";
    return s;
  };

  if (error) {
    return (
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <Star className="h-5 w-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div><h1 className="text-2xl font-bold">鍐呮帹骞垮満</h1><p className="text-sm text-gray-500">鑱氬悎鍏ㄧ綉鏈€鏂板唴鎺ㄤ俊鎭?路 AI 鍙俊搴﹁瘎鍒</p></div>
        </div>
        <Card className="p-12 text-center">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">{error}</p>
          <Button variant="outline" onClick={() => window.location.reload()}>閲嶈瘯</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
            <Star className="h-5 w-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">鍐呮帹骞垮満</h1>
            <p className="text-sm text-gray-500">鑱氬悎鍏ㄧ綉鏈€鏂板唴鎺ㄤ俊鎭?路 AI 鍙俊搴﹁瘎鍒</p>
          </div>
        </div>
        <Button variant="primary" onClick={() => setShowModal("create")}>
          <Plus className="h-4 w-4" /> 鍙戝竷鍐呮帹
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="鎼滅储鍏徃銆佸矖浣嶃€佸唴鎺ㄧ爜銆佹帹鑽愪汉..."
            className="w-full h-10 pl-9 pr-3 rounded-lg border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20" />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {companies.map((c) => (
            <button key={c} onClick={() => setCompany(c)}
              className={"whitespace-nowrap px-3 py-1.5 rounded-lg text-xs font-medium transition-colors " + (company === c ? "bg-primary-500 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700")}>
              {c}
            </button>
          ))}
        </div>
        <Badge variant="default" className="text-xs">{loading ? "..." : filtered.length + " 条内推"}</Badge>
      </div>

      {/* Success message */}
      {successMsg && (
        <Card className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
          <p className="text-sm text-green-700 dark:text-green-300 flex items-center gap-2"><Check className="h-4 w-4" />{successMsg}</p>
        </Card>
      )}

      {/* Loading */}
      {loading && (
        <div className="space-y-3">
          {[1,2,3].map((i) => (
            <Card key={i} className="p-5">
              <div className="flex items-center gap-5">
                <div className="min-w-[100px]"><div className="h-7 w-24 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700" /><div className="h-4 w-16 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700 mt-2" /></div>
                <div className="border-l border-default pl-5 space-y-2"><div className="h-5 w-48 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700" /><div className="h-4 w-36 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700" /></div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Referral List */}
      {!loading && (
        <div className="space-y-3">
          {filtered.map((ref) => (
            <Card key={ref.id} hover className={"p-5 border-l-4 " + (ref.confidenceScore >= 80 ? "border-l-green-500" : ref.confidenceScore >= 60 ? "border-l-amber-500" : "border-l-gray-300 dark:border-l-gray-600")}>
              <div className="flex items-start justify-between flex-wrap gap-3">
                {/* Left section */}
                <div className="flex items-start gap-5 flex-1 min-w-0">
                  {/* Code & Score */}
                  <div className="text-center min-w-[100px] shrink-0">
                    <code className="text-xl font-mono font-bold text-primary-500 tracking-wider">{ref.referralCode}</code>
                    <div className="mt-1">
                      <div className={"inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border " + confidenceBg(ref.confidenceScore)}>
                        <span className={confidenceColor(ref.confidenceScore)}>{ref.confidenceScore}</span>
                        <span className="text-yellow-500 text-[10px]">{stars(ref.confidenceScore)}</span>
                      </div>
                      <p className="text-[10px] text-gray-400 mt-0.5">{ref.confidenceLevel}</p>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="border-l border-default pl-5 flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h3 className="font-semibold text-sm">{ref.company?.name || "鏈煡鍏徃"}</h3>
                      {ref.jobTitle && <Badge variant="default" className="text-[10px]">{ref.jobTitle}</Badge>}
                      {ref.isEmployee && <Badge variant="info" className="text-[10px]">鍛樺伐</Badge>}
                      {ref.isVerified && <Badge variant="success" className="text-[10px]">宸查獙璇</Badge>}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500 flex-wrap mb-2">
                      {ref.referrerName && <span className="flex items-center gap-1"><User className="h-3 w-3" />{ref.referrerName}{ref.referrerTitle ? " 路 " + ref.referrerTitle : ""}</span>}
                      <span>路 {formatRelativeTime(ref.publishedAt)}</span>
                      {ref.source && <span>路 鏉ユ簮 {ref.source}</span>}
                    </div>
                    {/* Stats */}
                    <div className="flex items-center gap-3 text-[11px] text-gray-400">
                      <span className="flex items-center gap-1"><ShieldCheck className="h-3 w-3" />楠岃瘉 {ref.verifiedCount || 0}</span>
                      <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3 text-green-500" />鎴愬姛 {ref.successCount || 0}</span>
                      {ref._count && <span className="flex items-center gap-1"><Heart className="h-3 w-3" />鏀惰棌 {ref._count.referralFavorites || 0}</span>}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 shrink-0">
                  <button onClick={() => handleFavorite(ref.id)}
                    className={"p-2 rounded-lg transition-colors " + (favoritedIds.has(ref.id) ? "text-red-500 bg-red-50 dark:bg-red-900/20" : "text-gray-400 hover:text-red-500 hover:bg-gray-100 dark:hover:bg-gray-800")}>
                    <Heart className={"h-4 w-4 " + (favoritedIds.has(ref.id) ? "fill-current" : "")} />
                  </button>
                  <Button variant="outline" size="sm" onClick={() => handleCopy(ref.referralCode)}>
                    {copiedId === ref.referralCode ? <><Check className="h-4 w-4 text-green-500" /> 已复制</> : <><Copy className="h-4 w-4" /> 复制</>}
                  </Button>
                  <a href={ref.referralLink || "#"} target="_blank" rel="noopener noreferrer"
                    className="inline-flex items-center justify-center rounded-lg font-medium transition-all duration-150 focus-ring h-9 px-3 text-xs gap-1.5 bg-primary-500 text-white hover:bg-primary-600 shadow-sm">
                    瀹樼綉鎶曢€?<ExternalLink className="h-3.5 w-3.5" />
                  </a>
                  <div className="flex flex-col gap-1">
                    <button onClick={() => setShowModal(ref.id + "-rate")} className="text-xs text-gray-400 hover:text-primary-500">璇勪环</button>
                    <button onClick={() => setShowModal(ref.id + "-report")} className="text-xs text-gray-400 hover:text-red-500 flex items-center gap-0.5"><Flag className="h-3 w-3" />涓炬姤</button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && filtered.length === 0 && (
        <div className="text-center py-16">
          <Star className="h-12 w-12 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500">{referrals.length === 0 ? "暂无内推信息" : "没有找到匹配的内推信息"}</p>
        </div>
      )}

      {/* Create Modal */}
      <Modal isOpen={showModal === "create"} onClose={() => setShowModal(null)} title="鍙戝竷鍐呮帹">
        <CreateReferralForm
          onSubmit={async (data) => {
            try {
              await referralApi.create(data);
              setShowModal(null);
              showSuccess("内推信息发布成功！");
              // Refresh
              const res = await referralApi.list({ page: 1 });
              setReferrals(res.data.data ?? []);
            } catch (err: any) {
              showSuccess("发布失败: " + (err.message || "请重试"));
            }
          }}
          onCancel={() => setShowModal(null)}
        />
      </Modal>

      {/* Rate Modal */}
      <Modal isOpen={showModal?.endsWith("-rate") ?? false} onClose={() => setShowModal(null)} title="璇勪环鍐呮帹">
        <RateReferralForm
          referralId={showModal?.replace("-rate", "") || ""}
          onSubmit={async (data) => {
            try {
              const res = await referralApi.rate(showModal?.replace("-rate", "") || "", data);
              setShowModal(null);
              showSuccess("评价成功！可信度: " + res.data.data?.confidenceScore);
              // Refresh
              const r = await referralApi.list({ page: 1 });
              setReferrals(r.data.data ?? []);
            } catch (err: any) {
              showSuccess("评价失败: " + (err.message || "请重试"));
            }
          }}
          onCancel={() => setShowModal(null)}
        />
      </Modal>

      {/* Report Modal */}
      <Modal isOpen={showModal?.endsWith("-report") ?? false} onClose={() => setShowModal(null)} title="涓炬姤鍐呮帹">
        <ReportReferralForm
          onSubmit={async (data) => {
            try {
              await referralApi.report(showModal?.replace("-report", "") || "", data);
              setShowModal(null);
              showSuccess("举报已提交，我们会尽快处理。");
            } catch (err: any) {
              showSuccess("举报失败: " + (err.message || "请重试"));
            }
          }}
          onCancel={() => setShowModal(null)}
        />
      </Modal>
    </div>
  );
}

// ===== Sub-components =====

function CreateReferralForm({ onSubmit, onCancel }: { onSubmit: (d: any) => void; onCancel: () => void }) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [form, setForm] = useState({ companyId: "", referralCode: "", referrerName: "", jobId: "", referralLink: "", isEmployee: false, notes: "" });

  useEffect(() => {
    companyApi.list({ limit: 50 }).then((res) => setCompanies(res.data.data ?? [])).catch(() => {});
  }, []);

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form); }} className="space-y-4">
      <div>
        <label className="text-sm font-medium block mb-1">公司 *</label>
        <select value={form.companyId} onChange={(e) => setForm((p) => ({ ...p, companyId: e.target.value }))}
          className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" required>
          <option value="">选择公司</option>
          {companies.map((c) => (<option key={c.id} value={c.id}>{c.name}</option>))}
        </select>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">内推码 *</label>
        <Input value={form.referralCode} onChange={(e) => setForm((p) => ({ ...p, referralCode: e.target.value }))} placeholder="请输入内推码" required />
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">推荐人</label>
        <Input value={form.referrerName} onChange={(e) => setForm((p) => ({ ...p, referrerName: e.target.value }))} placeholder="您的名字" />
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">岗位/链接</label>
        <Input value={form.referralLink} onChange={(e) => setForm((p) => ({ ...p, referralLink: e.target.value }))} placeholder="官网投递链接" />
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={form.isEmployee} onChange={(e) => setForm((p) => ({ ...p, isEmployee: e.target.checked }))} />
        我是该公司员工
      </label>
      <div className="flex justify-end gap-3 pt-3">
        <Button variant="outline" type="button" onClick={onCancel}>取消</Button>
        <Button type="submit">发布</Button>
      </div>
    </form>
  );
}

function RateReferralForm({ referralId, onSubmit, onCancel }: { referralId: string; onSubmit: (d: any) => void; onCancel: () => void }) {
  const [score, setScore] = useState(5);
  const [responseTime, setResponseTime] = useState("");
  const [isSuccess, setIsSuccess] = useState<boolean | undefined>(undefined);
  const [comment, setComment] = useState("");

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit({ score, responseTime, isSuccess, comment }); }} className="space-y-4">
      <div>
        <label className="text-sm font-medium block mb-2">评分 (1-5)</label>
        <div className="flex gap-2">
          {[1,2,3,4,5].map((n) => (
            <button key={n} type="button" onClick={() => setScore(n)}
              className={"h-10 w-10 rounded-lg text-lg " + (n <= score ? "text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20" : "text-gray-300 bg-gray-50 dark:bg-gray-800")}>
              ★
            </button>
          ))}
        </div>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">响应速度</label>
        <select value={responseTime} onChange={(e) => setResponseTime(e.target.value)} className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
          <option value="">请选择</option>
          <option value="fast">快速回复</option>
          <option value="normal">正常</option>
          <option value="slow">响应慢</option>
        </select>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">是否成功入职</label>
        <div className="flex gap-3">
          <label className="flex items-center gap-2 text-sm"><input type="radio" name="success" onChange={() => setIsSuccess(true)} /> 是</label>
          <label className="flex items-center gap-2 text-sm"><input type="radio" name="success" onChange={() => setIsSuccess(false)} /> 否</label>
          <label className="flex items-center gap-2 text-sm"><input type="radio" name="success" defaultChecked onChange={() => setIsSuccess(undefined)} /> 不确定</label>
        </div>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">评价（选填）</label>
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={3}
          className="w-full rounded-lg border border-default bg-primary px-3 py-2 text-sm focus:outline-none focus:border-focused"
          placeholder="分享你的使用体验..." />
      </div>
      <div className="flex justify-end gap-3 pt-3">
        <Button variant="outline" type="button" onClick={onCancel}>取消</Button>
        <Button type="submit">提交评价</Button>
      </div>
    </form>
  );
}

function ReportReferralForm({ onSubmit, onCancel }: { onSubmit: (d: any) => void; onCancel: () => void }) {
  const [reason, setReason] = useState("");
  const [detail, setDetail] = useState("");

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit({ reason, detail }); }} className="space-y-4">
      <div>
        <label className="text-sm font-medium block mb-1">举报原因 *</label>
        <select value={reason} onChange={(e) => setReason(e.target.value)} className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" required>
          <option value="">请选择</option>
          <option value="invalid_code">内推码无效</option>
          <option value="spam">垃圾信息</option>
          <option value="expired">已过期</option>
          <option value="other">其他</option>
        </select>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1">详细描述</label>
        <textarea value={detail} onChange={(e) => setDetail(e.target.value)} rows={3}
          className="w-full rounded-lg border border-default bg-primary px-3 py-2 text-sm focus:outline-none focus:border-focused"
          placeholder="请详细描述问题..." />
      </div>
      <div className="flex justify-end gap-3 pt-3">
        <Button variant="outline" type="button" onClick={onCancel}>取消</Button>
        <Button type="submit" variant="danger">提交举报</Button>
      </div>
    </form>
  );
}

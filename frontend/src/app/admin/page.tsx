"use client";

import React, { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { Users, Briefcase, Building2, Star, FileText, Activity, RefreshCw, Shield, Ban, Check, Eye, EyeOff, Plus, X, ChevronDown, ChevronUp, Search as SearchIcon } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api/v1";

export default function AdminPage() {
  const [tab, setTab] = useState("overview");
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);

  // Users
  const [users, setUsers] = useState<any[]>([]);
  const [usersLoading, setUsersLoading] = useState(false);

  // Jobs
  const [jobs, setJobs] = useState<any[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);

  // Logs
  const [logs, setLogs] = useState<any[]>([]);
  const [logsLoading, setLogsLoading] = useState(false);

  // Create job modal
  const [showCreateJob, setShowCreateJob] = useState(false);
  const [jobForm, setJobForm] = useState({ companyId: "", title: "", category: "", city: "", salaryMin: "", salaryMax: "", experience: "", education: "", skills: "", description: "" });

  // Companies list for job creation
  const [companies, setCompanies] = useState<any[]>([]);

  useEffect(() => {
    loadDashboard();
    fetch(API + "/companies?limit=50").then(r => r.json()).then(d => setCompanies(d.data?.data ?? [])).catch(() => console.error("Failed to load companies"));
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const res = await fetch(API + "/admin/dashboard");
      const data = await res.json();
      setStats(data.data?.stats || {});
    } catch {} finally { setLoading(false); }
  };

  const loadUsers = async () => {
    setUsersLoading(true);
    try {
      const res = await fetch(API + "/admin/users?limit=50");
      const data = await res.json();
      setUsers(data.data?.data ?? []);
    } catch {} finally { setUsersLoading(false); }
  };

  const loadJobs = async () => {
    setJobsLoading(true);
    try {
      const res = await fetch(API + "/admin/jobs?limit=50");
      const data = await res.json();
      setJobs(data.data?.data ?? []);
    } catch {} finally { setJobsLoading(false); }
  };

  const loadLogs = async () => {
    setLogsLoading(true);
    try {
      const res = await fetch(API + "/admin/logs?limit=20");
      const data = await res.json();
      setLogs(data.data?.data ?? []);
    } catch {} finally { setLogsLoading(false); }
  };

  const handleTabChange = (t: string) => {
    setTab(t);
    if (t === "users" && users.length === 0) loadUsers();
    if (t === "jobs" && jobs.length === 0) loadJobs();
    if (t === "logs" && logs.length === 0) loadLogs();
  };

  const toggleUserStatus = async (id: string) => {
    await fetch(API + "/admin/users/" + id + "/toggle-status", { method: "PATCH" });
    loadUsers();
  };

  const updateUserRole = async (id: string, role: string) => {
    await fetch(API + "/admin/users/" + id + "/role", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role }),
    });
    loadUsers();
  };

  const toggleJobStatus = async (id: string) => {
    await fetch(API + "/admin/jobs/" + id + "/toggle-status", { method: "PATCH" });
    loadJobs();
  };

  const createJob = async () => {
    try {
      await fetch(API + "/admin/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...jobForm,
          salaryMin: parseInt(jobForm.salaryMin) || 0,
          salaryMax: parseInt(jobForm.salaryMax) || 0,
          skills: jobForm.skills.split(",").map(s => s.trim()).filter(Boolean),
        }),
      });
      setShowCreateJob(false);
      setJobForm({ companyId: "", title: "", category: "", city: "", salaryMin: "", salaryMax: "", experience: "", education: "", skills: "", description: "" });
      loadJobs();
    } catch {}
  };

  const TABS = [
    { id: "overview", label: "概览", icon: Activity },
    { id: "users", label: "用户管理", icon: Users },
    { id: "jobs", label: "岗位管理", icon: Briefcase },
    { id: "logs", label: "系统日志", icon: FileText },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
            <Shield className="h-5 w-5 text-gray-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">企业管理后台</h1>
            <p className="text-sm text-gray-500">管理用户、岗位和系统状态</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={() => { handleTabChange(tab); loadDashboard(); }}>
          <RefreshCw className="h-4 w-4" /> 刷新
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-default overflow-x-auto">
        {TABS.map((t) => (
          <button key={t.id} onClick={() => handleTabChange(t.id)}
            className={"flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors " + (tab === t.id ? "border-primary-500 text-primary-500" : "border-transparent text-gray-500 hover:text-gray-700")}>
            <t.icon className="h-4 w-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {tab === "overview" && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {loading ? (
              Array.from({length:5}).map((_,i) => <Card key={i} className="p-4"><div className="h-12 skeleton-pulse bg-gray-200 dark:bg-gray-700" /></Card>)
            ) : (
              [
                { label: "用户数", value: stats.users || 0, icon: Users, color: "text-blue-500" },
                { label: "公司", value: stats.companies || 0, icon: Building2, color: "text-amber-500" },
                { label: "活跃岗位", value: stats.jobs || 0, icon: Briefcase, color: "text-green-500" },
                { label: "内推", value: stats.referrals || 0, icon: Star, color: "text-purple-500" },
                { label: "投递", value: stats.applications || 0, icon: FileText, color: "text-rose-500" },
              ].map((s) => (
                <Card key={s.label} className="p-4 flex items-center gap-3">
                  <div className={"h-10 w-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center " + s.color}>
                    <s.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{s.value}</p>
                    <p className="text-xs text-gray-500">{s.label}</p>
                  </div>
                </Card>
              ))
            )}
          </div>

          {/* Role Management */}
          <Card className="p-6">
            <h2 className="font-semibold mb-4">角色说明</h2>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <Badge variant="info">user</Badge>
                <p className="text-gray-500 mt-1 text-xs">普通求职者：浏览岗位、投递、管理管线</p>
              </div>
              <div className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                <Badge variant="primary">admin</Badge>
                <p className="text-gray-500 mt-1 text-xs">企业管理员：发布岗位、查看候选人、管理内推</p>
              </div>
              <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-900/20">
                <Badge variant="error">super_admin</Badge>
                <p className="text-gray-500 mt-1 text-xs">超级管理员：系统设置、用户管理、全部权限</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Users Tab */}
      {tab === "users" && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">用户列表 ({users.length})</h2>
            <Button variant="outline" size="sm" onClick={loadUsers}><RefreshCw className="h-3 w-3" /> 刷新</Button>
          </div>
          {usersLoading ? (
            <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-12 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700" />)}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-default text-left text-gray-500">
                  <th className="pb-2 font-medium">邮箱</th>
                  <th className="pb-2 font-medium">昵称</th>
                  <th className="pb-2 font-medium">角色</th>
                  <th className="pb-2 font-medium">状态</th>
                  <th className="pb-2 font-medium">注册时间</th>
                  <th className="pb-2 font-medium">操作</th>
                </tr></thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b border-default">
                      <td className="py-3">{u.email}</td>
                      <td className="py-3">{u.nickname || "-"}</td>
                      <td className="py-3">
                        <select value={u.role} onChange={(e) => updateUserRole(u.id, e.target.value)}
                          className="text-xs border border-default rounded px-1 py-0.5 bg-primary">
                          <option value="user">user</option>
                          <option value="admin">admin</option>
                          <option value="super_admin">super_admin</option>
                        </select>
                      </td>
                      <td className="py-3"><Badge variant={u.status === "active" ? "success" : "error"}>{u.status}</Badge></td>
                      <td className="py-3 text-xs text-gray-500">{u.createdAt ? new Date(u.createdAt).toLocaleDateString("zh-CN") : "-"}</td>
                      <td className="py-3">
                        <button onClick={() => toggleUserStatus(u.id)}
                          className={"text-xs px-2 py-1 rounded " + (u.status === "active" ? "bg-red-50 text-red-600 hover:bg-red-100" : "bg-green-50 text-green-600 hover:bg-green-100")}>
                          {u.status === "active" ? "禁用" : "启用"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {users.length === 0 && <p className="text-center text-gray-500 py-8">暂无用户</p>}
            </div>
          )}
        </Card>
      )}

      {/* Jobs Tab */}
      {tab === "jobs" && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">岗位管理 ({jobs.length})</h2>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={loadJobs}><RefreshCw className="h-3 w-3" /></Button>
              <Button variant="primary" size="sm" onClick={() => setShowCreateJob(true)}>
                <Plus className="h-3 w-3" /> 发布岗位
              </Button>
            </div>
          </div>
          {jobsLoading ? (
            <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-12 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700" />)}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-default text-left text-gray-500">
                  <th className="pb-2 font-medium">岗位</th>
                  <th className="pb-2 font-medium">公司</th>
                  <th className="pb-2 font-medium">城市</th>
                  <th className="pb-2 font-medium">状态</th>
                  <th className="pb-2 font-medium">发布时间</th>
                  <th className="pb-2 font-medium">操作</th>
                </tr></thead>
                <tbody>
                  {jobs.map((j) => (
                    <tr key={j.id} className="border-b border-default">
                      <td className="py-3 font-medium">{j.title}</td>
                      <td className="py-3">{j.company?.name || "-"}</td>
                      <td className="py-3 text-xs">{j.city}</td>
                      <td className="py-3"><Badge variant={j.isActive ? "success" : "warning"}>{j.isActive ? "招聘中" : "已关闭"}</Badge></td>
                      <td className="py-3 text-xs text-gray-500">{j.publishedAt ? new Date(j.publishedAt).toLocaleDateString("zh-CN") : "-"}</td>
                      <td className="py-3">
                        <button onClick={() => toggleJobStatus(j.id)}
                          className={"text-xs px-2 py-1 rounded " + (j.isActive ? "bg-amber-50 text-amber-600" : "bg-green-50 text-green-600")}>
                          {j.isActive ? "下架" : "上架"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {jobs.length === 0 && <p className="text-center text-gray-500 py-8">暂无岗位</p>}
            </div>
          )}
        </Card>
      )}

      {/* Logs Tab */}
      {tab === "logs" && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">系统日志</h2>
            <Button variant="outline" size="sm" onClick={loadLogs}><RefreshCw className="h-3 w-3" /></Button>
          </div>
          {logsLoading ? (
            <div className="space-y-1">{[1,2,3].map(i => <div key={i} className="h-6 skeleton-pulse rounded bg-gray-200 dark:bg-gray-700" />)}</div>
          ) : (
            <div className="space-y-1 max-h-[60vh] overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-center text-gray-500 py-8">暂无日志</p>
              ) : (
                logs.map((log: any, i: number) => (
                  <div key={log.id || i} className="flex items-start gap-3 text-xs py-2 border-b border-default last:border-0">
                    <Badge variant={log.level === "error" ? "error" : log.level === "warn" ? "warning" : "default"} className="text-[9px] w-10 text-center">
                      {log.level || "info"}
                    </Badge>
                    <span className="text-gray-400 w-16 shrink-0">{log.createdAt ? new Date(log.createdAt).toLocaleTimeString("zh-CN") : ""}</span>
                    <span className="text-gray-600 dark:text-gray-400 flex-1">{log.message || log.action || "-"}</span>
                    <span className="text-gray-400 w-20">{log.module || ""}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </Card>
      )}

      {/* Create Job Modal */}
      <Modal isOpen={showCreateJob} onClose={() => setShowCreateJob(false)} title="发布新岗位" size="lg">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
          <div><label className="text-sm font-medium block mb-1">公司 *</label>
            <select value={jobForm.companyId} onChange={(e) => setJobForm(p => ({ ...p, companyId: e.target.value }))}
              className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm" required>
              <option value="">选择公司</option>
              {companies.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="text-sm font-medium block mb-1">岗位名称 *</label><Input value={jobForm.title} onChange={(e) => setJobForm(p => ({ ...p, title: e.target.value }))} placeholder="例: AI算法工程师" /></div>
            <div><label className="text-sm font-medium block mb-1">类别</label><Input value={jobForm.category} onChange={(e) => setJobForm(p => ({ ...p, category: e.target.value }))} placeholder="例: AI" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="text-sm font-medium block mb-1">城市</label><Input value={jobForm.city} onChange={(e) => setJobForm(p => ({ ...p, city: e.target.value }))} placeholder="例: 北京" /></div>
            <div><label className="text-sm font-medium block mb-1">经验要求</label><Input value={jobForm.experience} onChange={(e) => setJobForm(p => ({ ...p, experience: e.target.value }))} placeholder="例: 3-5年" /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="text-sm font-medium block mb-1">薪资最低(K)</label><Input type="number" value={jobForm.salaryMin} onChange={(e) => setJobForm(p => ({ ...p, salaryMin: e.target.value }))} /></div>
            <div><label className="text-sm font-medium block mb-1">薪资最高(K)</label><Input type="number" value={jobForm.salaryMax} onChange={(e) => setJobForm(p => ({ ...p, salaryMax: e.target.value }))} /></div>
          </div>
          <div><label className="text-sm font-medium block mb-1">技能（逗号分隔）</label>
            <Input value={jobForm.skills} onChange={(e) => setJobForm(p => ({ ...p, skills: e.target.value }))} placeholder="Python, Java, React" />
          </div>
          <div><label className="text-sm font-medium block mb-1">职位描述</label>
            <textarea value={jobForm.description} onChange={(e) => setJobForm(p => ({ ...p, description: e.target.value }))} rows={4}
              className="w-full rounded-lg border border-default bg-primary px-3 py-2 text-sm focus:outline-none focus:border-focused resize-y" />
          </div>
          <div className="flex justify-end gap-3 pt-3">
            <Button variant="outline" onClick={() => setShowCreateJob(false)}>取消</Button>
            <Button onClick={createJob} disabled={!jobForm.companyId || !jobForm.title}>发布</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { User, Settings, Mail, Lock, Camera, Save, Upload, FileText, Trash2, Briefcase, GraduationCap, MapPin, DollarSign, Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/store";
import { SITE_NAME } from "@/constants";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api/v1";

export default function SettingsPage() {
  const router = useRouter();
  const { user, token, logout } = useAuthStore();
  const [tab, setTab] = useState("profile");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Profile form
  const [form, setForm] = useState({
    nickname: "", yearsExp: "", education: "", currentCity: "", currentCompany: "",
    currentTitle: "", salaryMin: "", salaryMax: "", skills: "",
  });

  // Password form
  const [pwForm, setPwForm] = useState({ oldPassword: "", newPassword: "", confirmPassword: "" });

  // Resumes
  const [resumes, setResumes] = useState<any[]>([]);

  useEffect(() => {
    if (!user) { router.push("/login"); return; }
    setForm({
      nickname: user.nickname || "",
      yearsExp: (user as any).yearsExp?.toString() || "",
      education: user.education || "",
      currentCity: user.currentCity || "",
      currentCompany: (user as any).currentCompany || "",
      currentTitle: (user as any).currentTitle || "",
      salaryMin: (user as any).salaryMin?.toString() || "",
      salaryMax: (user as any).salaryMax?.toString() || "",
      skills: (user.skills || []).join(", "),
    });
    loadResumes();
  }, [user]);

  const loadResumes = async () => {
    try {
      const res = await fetch(API + "/users/me/resumes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: user?.id }),
      });
      const json = await res.json();
      setResumes(json.data ?? []);
    } catch {}
  };

  const saveProfile = async () => {
    setSaving(true);
    setMessage("");
    try {
      const body = {
        userId: user?.id,
        nickname: form.nickname,
        yearsExp: parseInt(form.yearsExp) || 0,
        education: form.education,
        currentCity: form.currentCity,
        currentCompany: form.currentCompany,
        currentTitle: form.currentTitle,
        salaryMin: parseInt(form.salaryMin) || 0,
        salaryMax: parseInt(form.salaryMax) || 0,
        skills: form.skills.split(",").map((s) => s.trim()).filter(Boolean),
      };
      const res = await fetch(API + "/users/me", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error("保存失败");
      setMessage("个人信息已保存");
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setSaving(false);
    }
  };

  const changePassword = async () => {
    if (pwForm.newPassword !== pwForm.confirmPassword) { setMessage("两次密码不一致"); return; }
    if (pwForm.newPassword.length < 6) { setMessage("密码至少6位"); return; }
    setSaving(true);
    setMessage("");
    try {
      const res = await fetch(API + "/auth/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId: user?.id, oldPassword: pwForm.oldPassword, newPassword: pwForm.newPassword }),
      });
      if (!res.ok) { const e = await res.json(); throw new Error(e.message || "修改失败"); }
      setPwForm({ oldPassword: "", newPassword: "", confirmPassword: "" });
      setMessage("密码修改成功");
    } catch (err: any) {
      setMessage(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!user) return null;

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="h-10 w-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <Settings className="h-5 w-5 text-gray-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">账号设置</h1>
          <p className="text-sm text-gray-500">管理你的个人信息和偏好</p>
        </div>
      </div>

      {message && (
        <Card className={"mb-4 p-3 text-sm " + (message.includes("成功") ? "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700" : "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-600")}>
          {message}
        </Card>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 border-b border-default">
        {[
          { id: "profile", label: "个人信息", icon: User },
          { id: "password", label: "密码", icon: Lock },
          { id: "resumes", label: "简历管理", icon: FileText },
        ].map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={"flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors " + (tab === t.id ? "border-primary-500 text-primary-500" : "border-transparent text-gray-500 hover:text-gray-700")}>
            <t.icon className="h-4 w-4" /> {t.label}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {tab === "profile" && (
        <Card className="p-6">
          <div className="flex items-center gap-4 mb-8">
            <div className="relative">
              <div className="h-20 w-20 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-2xl font-bold text-primary-500">
                {user.nickname?.charAt(0) || (user as any).email?.charAt(0) || "?"}
              </div>
              <label className="absolute -bottom-1 -right-1 h-7 w-7 rounded-full bg-primary-500 text-white flex items-center justify-center cursor-pointer shadow-md hover:bg-primary-600">
                <Camera className="h-3.5 w-3.5" />
                <input type="file" className="hidden" accept="image/*" />
              </label>
            </div>
            <div>
              <p className="text-lg font-semibold">{user.nickname || "未设置昵称"}</p>
              <p className="text-sm text-gray-500">{user.email}</p>
              <Badge variant={(user as any).role === "super_admin" ? "info" : "default"} className="mt-1 text-[10px]">{user.role}</Badge>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div><label className="text-sm font-medium mb-1 block">昵称</label><Input value={form.nickname} onChange={(e) => setForm((p) => ({ ...p, nickname: e.target.value }))} icon={<User className="h-4 w-4" />} /></div>
            <div><label className="text-sm font-medium mb-1 block">工作年限</label><Input type="number" value={form.yearsExp} onChange={(e) => setForm((p) => ({ ...p, yearsExp: e.target.value }))} icon={<Briefcase className="h-4 w-4" />} /></div>
            <div><label className="text-sm font-medium mb-1 block">最高学历</label><select value={form.education} onChange={(e) => setForm((p) => ({ ...p, education: e.target.value }))} className="w-full h-10 rounded-lg border border-default bg-primary px-3 text-sm">
              <option value="">请选择</option><option>大专</option><option>本科</option><option>硕士</option><option>博士</option>
            </select></div>
            <div><label className="text-sm font-medium mb-1 block">当前城市</label><Input value={form.currentCity} onChange={(e) => setForm((p) => ({ ...p, currentCity: e.target.value }))} icon={<MapPin className="h-4 w-4" />} /></div>
            <div><label className="text-sm font-medium mb-1 block">当前公司</label><Input value={form.currentCompany} onChange={(e) => setForm((p) => ({ ...p, currentCompany: e.target.value }))} /></div>
            <div><label className="text-sm font-medium mb-1 block">当前职位</label><Input value={form.currentTitle} onChange={(e) => setForm((p) => ({ ...p, currentTitle: e.target.value }))} /></div>
            <div><label className="text-sm font-medium mb-1 block">期望薪资（最低K）</label><Input type="number" value={form.salaryMin} onChange={(e) => setForm((p) => ({ ...p, salaryMin: e.target.value }))} icon={<DollarSign className="h-4 w-4" />} /></div>
            <div><label className="text-sm font-medium mb-1 block">期望薪资（最高K）</label><Input type="number" value={form.salaryMax} onChange={(e) => setForm((p) => ({ ...p, salaryMax: e.target.value }))} icon={<DollarSign className="h-4 w-4" />} /></div>
          </div>
          <div className="mb-6">
            <label className="text-sm font-medium mb-1 block">技能（逗号分隔）</label>
            <textarea value={form.skills} onChange={(e) => setForm((p) => ({ ...p, skills: e.target.value }))} rows={2}
              className="w-full rounded-lg border border-default bg-primary px-3 py-2 text-sm focus:outline-none focus:border-focused resize-y"
              placeholder="Python, Java, React..." />
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={saveProfile} loading={saving}><Save className="h-4 w-4" /> 保存</Button>
            <Button variant="ghost" onClick={handleLogout} className="text-red-500">退出登录</Button>
          </div>
        </Card>
      )}

      {/* Password Tab */}
      {tab === "password" && (
        <Card className="p-6">
          <h2 className="font-semibold mb-6">修改密码</h2>
          <div className="space-y-4 max-w-md">
            <div><label className="text-sm font-medium mb-1 block">原密码</label><Input type="password" value={pwForm.oldPassword} onChange={(e) => setPwForm((p) => ({ ...p, oldPassword: e.target.value }))} icon={<Lock className="h-4 w-4" />} /></div>
            <div><label className="text-sm font-medium mb-1 block">新密码</label><Input type="password" value={pwForm.newPassword} onChange={(e) => setPwForm((p) => ({ ...p, newPassword: e.target.value }))} icon={<Lock className="h-4 w-4" />} /></div>
            <div><label className="text-sm font-medium mb-1 block">确认新密码</label><Input type="password" value={pwForm.confirmPassword} onChange={(e) => setPwForm((p) => ({ ...p, confirmPassword: e.target.value }))} icon={<Lock className="h-4 w-4" />} /></div>
            <Button onClick={changePassword} loading={saving}>修改密码</Button>
          </div>
        </Card>
      )}

      {/* Resumes Tab */}
      {tab === "resumes" && (
        <div className="space-y-4">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">我的简历</h2>
              <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary-500 text-white text-sm cursor-pointer hover:bg-primary-600">
                <Upload className="h-4 w-4" /> 上传简历
                <input type="file" className="hidden" accept=".pdf,.doc,.docx,.txt" onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  const reader = new FileReader();
                  reader.onload = async (ev) => {
                    try {
                      await fetch(API + "/users/me/resumes", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ userId: user?.id, fileName: file.name, fileUrl: "", content: ev.target?.result as string || "", title: file.name.replace(/\\.[^.]+$/, "") }),
                      });
                      loadResumes();
                    } catch {}
                  };
                  reader.readAsText(file);
                }} />
              </label>
            </div>
            {resumes.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">暂无简历，点击上方按钮上传</p>
            ) : (
              <div className="space-y-2">
                {resumes.map((r) => (
                  <Card key={r.id} className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="font-medium text-sm">{r.title}</p>
                        <p className="text-xs text-gray-500">{r.fileName || ""} · {r.createdAt ? new Date(r.createdAt).toLocaleDateString("zh-CN") : ""}</p>
                      </div>
                    </div>
                    <button onClick={async () => {
                      await fetch(API + "/users/me/resumes/" + r.id, {
                        method: "DELETE",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ userId: user?.id }),
                      });
                      loadResumes();
                    }} className="p-1 text-gray-400 hover:text-red-500">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </Card>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}

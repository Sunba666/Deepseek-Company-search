"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, Code2, Mail, Lock, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { SITE_NAME } from "@/constants";
import { useAuthStore } from "@/store";

export default function LoginPage() {
  const router = useRouter();
  const { setUser, setToken } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api/v1";
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const body = isLogin ? { email, password } : { email, password, nickname: nickname || email.split("@")[0] };
      const res = await fetch(API + endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message || (isLogin ? "登录失败" : "注册失败"));
      }
      const data = await res.json();
      if (data.data) {
        setUser(data.data.user);
        setToken(data.data.access_token);
      }
      router.push("/");
    } catch (err: any) {
      setError(err.message || "请求失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-secondary">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="h-10 w-10 rounded-xl bg-primary-500 flex items-center justify-center">
              <span className="text-xl font-bold text-white">J</span>
            </div>
            <span className="text-2xl font-bold">{SITE_NAME}</span>
          </Link>
          <h1 className="text-2xl font-bold mb-1">{isLogin ? "欢迎回来" : "创建账号"}</h1>
          <p className="text-sm text-gray-500">{isLogin ? "登录以继续管理你的求职进度" : "注册以开始你的 AI 求职之旅"}</p>
        </div>

        <Card className="p-6">
          {error && <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-400">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">邮箱</label>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com" icon={<Mail className="h-4 w-4" />} required />
            </div>
            {!isLogin && (
              <div>
                <label className="text-sm font-medium mb-1 block">昵称</label>
                <Input type="text" value={nickname} onChange={(e) => setNickname(e.target.value)}
                  placeholder="你的昵称（选填）" />
              </div>
            )}
            <div>
              <label className="text-sm font-medium mb-1 block">密码</label>
              <div className="relative">
                <Input type={showPassword ? "text" : "password"} value={password}
                  onChange={(e) => setPassword(e.target.value)} placeholder="输入密码" required />
                <button type="button" onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            {isLogin && (
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm"><input type="checkbox" className="rounded border-gray-300" /> 记住我</label>
                <Link href="/forgot-password" className="text-sm text-primary-500 hover:text-primary-600">忘记密码？</Link>
              </div>
            )}
            <Button type="submit" variant="primary" className="w-full h-12" loading={loading}>
              {isLogin ? "登录" : "注册"}
            </Button>
          </form>
        </Card>

        <p className="text-center text-sm text-gray-500 mt-6">
          {isLogin ? "还没有账号？" : "已有账号？"}
          <button onClick={() => { setIsLogin(!isLogin); setError(""); }} className="text-primary-500 hover:text-primary-600 font-medium ml-1">
            {isLogin ? "立即注册" : "立即登录"}
          </button>
        </p>
      </div>
    </div>
  );
}

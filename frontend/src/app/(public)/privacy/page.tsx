import React from "react";
import { Card } from "@/components/ui/card";
import { Shield, Lock, Eye, Cookie } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "隐私政策",
  description: "JobNav AI 隐私政策 — 我们如何收集、使用和保护您的个人信息",
};

const SECTIONS = [
  {
    icon: Eye,
    title: "信息收集",
    content: "我们收集您在使用平台时主动提供的信息，包括但不限于：注册时提供的邮箱地址、用户名；投递简历时上传的简历文件；使用 AI 功能时输入的求职偏好和问题。我们也会自动收集设备信息、浏览记录等匿名数据以优化服务体验。",
  },
  {
    icon: Lock,
    title: "信息使用",
    content: "收集的信息仅用于提供和改善平台服务，包括：为您推荐匹配的岗位和内推机会；分析使用趋势以改进产品功能；通过邮件或站内通知推送重要更新。我们不会将您的个人信息出售给第三方。",
  },
  {
    icon: Shield,
    title: "信息安全",
    content: "我们采用业界标准的安全措施保护您的数据，包括 SSL/TLS 加密传输、数据存储加密、访问权限控制等。但请注意，互联网传输无法保证 100% 安全，我们会尽力保护但无法绝对保证。",
  },
  {
    icon: Cookie,
    title: "Cookie 与追踪",
    content: "我们使用必要的 Cookie 来维持网站正常运行，以及分析型 Cookie 来了解使用情况。您可以通过浏览器设置管理 Cookie 偏好。我们不会使用 Cookie 进行跨站追踪广告投放。",
  },
];

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="h-10 w-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
          <Shield className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">隐私政策</h1>
          <p className="text-sm text-gray-500">最后更新：2025 年 1 月</p>
        </div>
      </div>
      <Card className="mb-8 p-8">
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
          JobNav AI（以下简称"我们"）深知个人信息对您的重要性。本隐私政策说明了
          我们如何收集、使用、存储和保护您的个人信息。使用本平台即表示您同意本政策所述的收集和使用方式。
        </p>
      </Card>
      <div className="grid md:grid-cols-2 gap-4">
        {SECTIONS.map((section) => (
          <Card key={section.title} className="p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-8 w-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                <section.icon className="h-4 w-4 text-gray-600 dark:text-gray-400" />
              </div>
              <h2 className="font-semibold">{section.title}</h2>
            </div>
            <p className="text-sm text-gray-500 leading-relaxed">{section.content}</p>
          </Card>
        ))}
      </div>
      <Card className="mt-8 p-6 bg-gray-50 dark:bg-gray-800/50 border-dashed">
        <p className="text-sm text-gray-500 leading-relaxed">
          如有隐私相关疑问，请通过反馈页面或发送邮件至 privacy@jobnav.ai 联系我们。我们会尽快回复您的关切。
        </p>
      </Card>
    </div>
  );
}

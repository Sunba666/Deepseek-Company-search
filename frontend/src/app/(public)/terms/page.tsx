import React from "react";
import { Card } from "@/components/ui/card";
import { FileText, Scale, AlertCircle, RefreshCw } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "服务条款",
  description: "JobNav AI 服务条款 — 使用本平台前请仔细阅读",
};

const SECTIONS = [
  {
    icon: Scale,
    title: "服务说明",
    content: "JobNav AI 提供企业信息查询、内推聚合、岗位搜索等求职辅助服务。平台上的企业信息和内推信息由用户提交和 AI 采集，我们不对信息的准确性、完整性和时效性作绝对保证。",
  },
  {
    icon: AlertCircle,
    title: "用户责任",
    content: "用户应合法使用本平台，不得利用平台从事任何违法违规活动，包括但不限于发布虚假信息、恶意刷屏、侵犯他人权益等。用户需对自己发布的内容负责。",
  },
  {
    icon: RefreshCw,
    title: "知识产权",
    content: "平台自身的产品设计、代码、品牌标识等知识产权归 JobNav AI 所有。用户发布的内容，其知识产权归用户所有，但授予平台在服务范围内使用的许可。",
  },
  {
    icon: FileText,
    title: "免责声明",
    content: "在适用法律允许的最大范围内，本平台按“现状”提供，不作出任何明示或暗示的保证。我们不承担因使用本平台而产生的任何间接、附带或后果性损失。",
  },
];

export default function TermsPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="h-10 w-10 rounded-xl bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
          <FileText className="h-5 w-5 text-rose-600 dark:text-rose-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">服务条款</h1>
          <p className="text-sm text-gray-500">最后更新：2025 年 1 月</p>
        </div>
      </div>
      <Card className="mb-8 p-8">
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
          欢迎使用 JobNav AI。使用本平台前，请仔细阅读以下服务条款（以下简称“本条款”）。
          通过访问或使用本平台，即表示您同意受本条款的约束。
        </p>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
          如果您不同意本条款的任何内容，请停止使用本平台。
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
          我们保留随时修改本条款的权利。重大变更将通过站内通知或邮件告知。
          修改后的条款自发布之日起生效，继续使用本平台即表示您接受修改后的条款。
        </p>
      </Card>
    </div>
  );
}

"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MessageSquare, Send, ThumbsUp, Bug, Lightbulb, Sparkles } from "lucide-react";

const FEEDBACK_TYPES = [
  { value: "suggestion", label: "功能建议", icon: Lightbulb, color: "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400" },
  { value: "bug", label: "问题反馈", icon: Bug, color: "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400" },
  { value: "praise", label: "点赞鼓励", icon: ThumbsUp, color: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400" },
  { value: "other", label: "其他", icon: Sparkles, color: "bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400" },
];

export default function FeedbackPage() {
  const [type, setType] = useState("suggestion");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await new Promise((r) => setTimeout(r, 800));
    setLoading(false);
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 py-8">
        <Card className="p-12 text-center">
          <div className="h-16 w-16 rounded-2xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-4">
            <ThumbsUp className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h2 className="text-xl font-semibold mb-2">感谢您的反馈！</h2>
          <p className="text-gray-500 mb-6">
            我们已收到您的建议，团队会认真评估。您的每一条反馈都让 JobNav AI 变得更好。
          </p>
          <Button variant="outline" onClick={() => setSubmitted(false)}>
            再写一条
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="h-10 w-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
          <MessageSquare className="h-5 w-5 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">意见反馈</h1>
          <p className="text-sm text-gray-500">帮助我们做得更好 — 您的每一条建议都很重要</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        {FEEDBACK_TYPES.map((item) => (
          <button
            key={item.value}
            onClick={() => setType(item.value)}
            className={
              "flex flex-col items-center gap-2 p-4 rounded-xl border transition-all " +
              (type === item.value
                ? "border-primary-500 bg-primary-50 dark:bg-primary-900/10"
                : "border-default hover:border-gray-300 dark:hover:border-gray-600")
            }
          >
            <div className={"h-8 w-8 rounded-lg flex items-center justify-center " + item.color}>
              <item.icon className="h-4 w-4" />
            </div>
            <span className="text-xs font-medium">{item.label}</span>
          </button>
        ))}
      </div>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium mb-1.5">标题</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="用一句话概括您的建议..."
              required
              className="w-full h-10 px-3 rounded-lg border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">详细描述</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="请详细描述您的想法、遇到的问题或建议..."
              rows={5}
              required
              className="w-full px-3 py-2.5 rounded-lg border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20 resize-y"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">
              联系方式 <span className="text-gray-400 font-normal">（选填）</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="邮箱地址，方便我们回复您"
              className="w-full h-10 px-3 rounded-lg border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20"
            />
          </div>
          <Button
            type="submit"
            size="lg"
            icon={<Send className="h-4 w-4" />}
            loading={loading}
            disabled={!title || !content}
            className="w-full sm:w-auto"
          >
            提交反馈
          </Button>
        </form>
      </Card>
    </div>
  );
}

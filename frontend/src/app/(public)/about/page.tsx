import React from "react";
import { Card } from "@/components/ui/card";
import { Info, Target, Shield, Users } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "关于我们",
  description: "了解 JobNav AI — AI 驱动的智能求职导航平台",
};

const FEATURES = [
  {
    icon: Target,
    title: "我们的使命",
    content: "帮助求职者高效发现优质岗位、获取内推机会，借助 AI 技术让求职过程更智能、更透明。",
    color: "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400",
  },
  {
    icon: Shield,
    title: "数据驱动",
    content: "聚合全网企业信息与招聘动态，结合 AI 分析，为求职者提供精准的岗位匹配和公司洞察。",
    color: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400",
  },
  {
    icon: Users,
    title: "社区共建",
    content: "通过内推互助、面经分享，打造求职者互助社区，让每一次跳槽都更有把握。",
    color: "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400",
  },
  {
    icon: Info,
    title: "持续进化",
    content: "我们持续迭代产品功能，欢迎通过反馈渠道提出建议，一起打造更好的求职工具。",
    color: "bg-sky-100 dark:bg-sky-900/30 text-sky-600 dark:text-sky-400",
  },
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="h-10 w-10 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
          <Info className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">关于我们</h1>
          <p className="text-sm text-gray-500">了解 JobNav AI 的故事与愿景</p>
        </div>
      </div>
      <Card className="mb-8 p-8">
        <h2 className="text-xl font-semibold mb-4">让求职更简单</h2>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-4">
          JobNav AI 诞生于一个简单的想法：求职不应该是一场信息战。我们聚合企业信息、招聘动态和内推资源，
          结合 AI 技术为求职者提供一站式导航服务。
        </p>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
          无论你是应届生还是资深职场人，都能在这里找到值得投递的公司、真实的内推机会，
          以及 AI 提供的个性化求职建议。
        </p>
      </Card>
      <div className="grid md:grid-cols-2 gap-4">
        {FEATURES.map((feature) => (
          <Card key={feature.title} className="p-6">
            <div className="flex items-start gap-4">
              <div className={"h-10 w-10 rounded-xl flex items-center justify-center shrink-0 " + feature.color}>
                <feature.icon className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{feature.content}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

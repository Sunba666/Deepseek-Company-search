export const SITE_NAME = "JobNav AI";
export const SITE_DESCRIPTION = "AI 驱动的智能求职导航平台 · 内推聚合 · 官网直达";
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://jobnav.ai";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001/api/v1";
export const APP_VERSION = "1.0.0";

export const NAV_LINKS = [
  { label: "公司", href: "/companies" },
  { label: "岗位", href: "/jobs" },
  { label: "内推", href: "/referrals" },
  { label: "AI 推荐", href: "/ai-recommend" },
  { label: "投递管理", href: "/pipeline" },
  { label: "AI Copilot", href: "/ai-copilot" },
] as const;

export const APPLICATION_STATUS_LABELS: Record<string, string> = {
  saved: "收藏", ready_to_apply: "准备投递", applied: "已投递", hr_viewed: "HR 查看",
  written_test: "笔试", interview_1: "一面", interview_2: "二面", hr_interview: "HR 面",
  offer: "Offer", rejected: "拒绝", withdrawn: "已撤回",
};

export const APPLICATION_STATUS_COLORS: Record<string, string> = {
  saved: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
  ready_to_apply: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  applied: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300",
  hr_viewed: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
  written_test: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
  interview_1: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
  interview_2: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
  hr_interview: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
  offer: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
  withdrawn: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
};

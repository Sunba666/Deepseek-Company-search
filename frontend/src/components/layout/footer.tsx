import React from "react";
import Link from "next/link";
import { SITE_NAME } from "@/constants";

export function Footer() {
  return (
    <footer className="border-t border-default bg-secondary">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center">
                <span className="text-sm font-bold text-white">J</span>
              </div>
              <span className="text-lg font-semibold">{SITE_NAME}</span>
            </div>
            <p className="text-sm text-gray-500">
              AI 驱动的智能求职导航平台
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-3">产品</h3>
            <div className="flex flex-col gap-2 text-sm text-gray-500">
              <Link href="/jobs" className="hover:text-gray-700 dark:hover:text-gray-300">岗位搜索</Link>
              <Link href="/companies" className="hover:text-gray-700 dark:hover:text-gray-300">公司</Link>
              <Link href="/referrals" className="hover:text-gray-700 dark:hover:text-gray-300">内推</Link>
              <Link href="/ai-recommend" className="hover:text-gray-700 dark:hover:text-gray-300">AI 推荐</Link>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-3">支持</h3>
            <div className="flex flex-col gap-2 text-sm text-gray-500">
              <Link href="/about" className="hover:text-gray-700 dark:hover:text-gray-300">关于</Link>
              <Link href="/feedback" className="hover:text-gray-700 dark:hover:text-gray-300">反馈</Link>
              <Link href="/privacy" className="hover:text-gray-700 dark:hover:text-gray-300">隐私</Link>
              <Link href="/terms" className="hover:text-gray-700 dark:hover:text-gray-300">条款</Link>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-3">关注</h3>
            <div className="flex flex-col gap-2 text-sm text-gray-500">
              <a href="#" className="hover:text-gray-700 dark:hover:text-gray-300">GitHub</a>
              <a href="#" className="hover:text-gray-700 dark:hover:text-gray-300">公众号</a>
              <a href="#" className="hover:text-gray-700 dark:hover:text-gray-300">小红书</a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-default text-center text-sm text-gray-400">
          © {new Date().getFullYear()} {SITE_NAME}. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

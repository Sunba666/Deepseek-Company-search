import React from 'react';
import Link from 'next/link';

const ADMIN_LINKS = [
  { href: '/admin', label: '数据概览', icon: '📊' },
  { href: '/admin/users', label: '用户管理', icon: '👥' },
  { href: '/admin/jobs', label: '岗位管理', icon: '📋' },
  { href: '/admin/referrals', label: '内推管理', icon: '🔗' },
  { href: '/admin/ai-config', label: 'AI 配置', icon: '🤖' },
  { href: '/admin/logs', label: '日志管理', icon: '📜' },
  { href: '/admin/settings', label: '系统配置', icon: '⚙️' },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <aside className="w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 p-4">
        <Link href="/admin" className="flex items-center gap-2 mb-8">
          <div className="h-8 w-8 rounded-lg bg-primary-500 flex items-center justify-center">
            <span className="text-sm font-bold text-white">J</span>
          </div>
          <span className="font-semibold">Admin Panel</span>
        </Link>
        <nav className="space-y-1">
          {ADMIN_LINKS.map((link) => (
            <Link key={link.href} href={link.href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100 transition-colors">
              <span>{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  );
}

'use client';

import React from 'react';
import { Card } from '@/components/ui/card';

const STATS = [
  { label: '总用户', value: '0', change: '+0%', color: 'bg-blue-500' },
  { label: '总岗位', value: '0', change: '待同步', color: 'bg-green-500' },
  { label: '内推数', value: '0', change: '待同步', color: 'bg-purple-500' },
  { label: '投递数', value: '0', change: '+0%', color: 'bg-amber-500' },
];

export default function AdminDashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">数据概览</h1>
      <div className="grid grid-cols-4 gap-4 mb-8">
        {STATS.map((s) => (
          <Card key={s.label} className="p-5">
            <p className="text-sm text-gray-500 mb-1">{s.label}</p>
            <p className="text-3xl font-bold">{s.value}</p>
            <p className="text-xs text-green-500 mt-1">{s.change}</p>
          </Card>
        ))}
      </div>
      <Card className="p-6">
        <h2 className="font-semibold mb-4">系统状态</h2>
        <div className="space-y-3 text-sm">
          {[
            { service: 'PostgreSQL', status: '待连接', color: 'text-gray-400' },
            { service: 'Redis', status: '待连接', color: 'text-gray-400' },
            { service: 'Elasticsearch', status: '待连接', color: 'text-gray-400' },
            { service: 'AI Provider', status: '就绪', color: 'text-green-500' },
          ].map((s) => (
            <div key={s.service} className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-800">
              <span>{s.service}</span>
              <span className={'font-medium ' + s.color}>{s.status}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

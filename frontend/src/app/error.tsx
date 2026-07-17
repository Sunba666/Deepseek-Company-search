"use client";

import { Button } from "@/components/ui/button";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="h-20 w-20 rounded-3xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-6">
        <span className="text-4xl font-bold text-red-400">!</span>
      </div>
      <h1 className="text-2xl font-bold mb-2">服务器错误</h1>
      <p className="text-sm text-gray-500 mb-8">服务器遇到了一个错误，请稍后重试</p>
      <Button onClick={reset} variant="primary">重试</Button>
    </div>
  );
}

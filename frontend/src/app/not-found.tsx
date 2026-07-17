import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="h-20 w-20 rounded-3xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-6">
        <span className="text-4xl font-bold text-gray-300">404</span>
      </div>
      <h1 className="text-2xl font-bold mb-2">页面不存在</h1>
      <p className="text-sm text-gray-500 mb-8">你访问的页面可能已被移除或不存在</p>
      <Link href="/"><Button variant="primary">返回首页</Button></Link>
    </div>
  );
}

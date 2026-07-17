"use client";

import React from "react";
import { Button } from "@/components/ui/button";

interface Props { children: React.ReactNode; fallback?: React.ReactNode; }
interface State { hasError: boolean; error?: Error; }

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError(error: Error): State { return { hasError: true, error }; }
  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
          <div className="h-16 w-16 rounded-2xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-4 text-3xl">!</div>
          <h2 className="text-xl font-semibold mb-2">出了点问题</h2>
          <p className="text-sm text-gray-500 mb-6 text-center max-w-md">{this.state.error?.message ?? "发生了意外错误"}</p>
          <Button onClick={() => this.setState({ hasError: false })} variant="primary">重试</Button>
        </div>
      );
    }
    return this.props.children;
  }
}

"use client";

import React, { useEffect, useRef } from "react";
import { Send, Plus, Trash2, Star, MessageSquare, Upload, PanelRightOpen, Bot, Sparkles, FileText, Briefcase, Building2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useAIStore } from "@/store/ai";
import { cn } from "@/lib/utils";

const QUICK_ACTIONS = [
  { icon: Briefcase, label: "推荐岗位", query: "推荐适合我的岗位" },
  { icon: Search, label: "JD 分析", query: "帮我分析一下这个 JD" },
  { icon: Building2, label: "公司内推", query: "我想进字节跳动" },
  { icon: Sparkles, label: "简历优化", query: "帮我优化简历" },
];

export default function AICopilotPage() {
  const {
    sessions, currentSessionId, messages, isProcessing, streamingContent,
    createSession, switchSession, deleteSession, toggleStar, sendMessage, stopGeneration,
  } = useAIStore();
  const [input, setInput] = React.useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingContent]);

  const handleSend = () => {
    if (!input.trim() || isProcessing) return;
    sendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Left sidebar: History */}
      <div className="w-64 lg:w-72 border-r border-default bg-secondary hidden md:flex flex-col">
        <div className="p-4 border-b border-default">
          <Button variant="primary" className="w-full" onClick={createSession}>
            <Plus className="h-4 w-4" /> 新建对话
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => switchSession(s.id)}
              className={cn(
                "w-full text-left p-3 rounded-lg text-sm transition-colors flex items-center gap-2 group",
                s.id === currentSessionId
                  ? "bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300"
                  : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
              )}
            >
              <MessageSquare className="h-4 w-4 shrink-0 text-gray-400" />
              <span className="truncate flex-1">{s.title}</span>
              <button onClick={(e) => { e.stopPropagation(); toggleStar(s.id); }}
                className={cn("p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity", s.isStarred && "opacity-100 text-yellow-500")}>
                <Star className={"h-3 w-3 " + (s.isStarred ? "fill-current" : "")} />
              </button>
              <button onClick={(e) => { e.stopPropagation(); deleteSession(s.id); }}
                className="p-1 rounded opacity-0 group-hover:opacity-100 hover:text-red-500 transition-opacity">
                <Trash2 className="h-3 w-3" />
              </button>
            </button>
          ))}
          {sessions.length === 0 && (
            <p className="text-xs text-gray-400 text-center py-8">暂无对话记录</p>
          )}
        </div>
      </div>

      {/* Center: Chat */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4">
          {messages.length === 0 && !isProcessing && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="h-16 w-16 rounded-2xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mb-4">
                <Bot className="h-8 w-8 text-primary-500" />
              </div>
              <h2 className="text-xl font-semibold mb-2">AI 求职助手</h2>
              <p className="text-sm text-gray-500 mb-8 max-w-md">
                你好！我是 JobNav AI 求职助手，可以帮你推荐岗位、分析 JD、提供内推建议、优化简历、职业规划等。
              </p>
              <div className="grid grid-cols-2 gap-3 max-w-md w-full">
                {QUICK_ACTIONS.map((action) => (
                  <button key={action.label}
                    onClick={() => sendMessage(action.query)}
                    className="flex items-center gap-2 p-3 rounded-xl border border-default hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left">
                    <div className="h-8 w-8 rounded-lg bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center">
                      <action.icon className="h-4 w-4 text-primary-500" />
                    </div>
                    <span className="text-sm font-medium">{action.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={cn("flex gap-3", msg.role === "user" ? "justify-end" : "")}>
              {msg.role === "assistant" && (
                <div className="h-8 w-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-primary-500" />
                </div>
              )}
              <div className={cn(
                "max-w-[75%] rounded-2xl px-4 py-3 text-sm",
                msg.role === "user"
                  ? "bg-primary-500 text-white"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              )}>
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          ))}

          {isProcessing && streamingContent && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center shrink-0">
                <Bot className="h-4 w-4 text-primary-500" />
              </div>
              <div className="max-w-[75%] rounded-2xl px-4 py-3 text-sm bg-gray-100 dark:bg-gray-800">
                <div className="whitespace-pre-wrap">{streamingContent}</div>
                <span className="inline-block w-2 h-4 bg-primary-500 animate-pulse ml-0.5" />
              </div>
            </div>
          )}

          {isProcessing && !streamingContent && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center shrink-0">
                <Bot className="h-4 w-4 text-primary-500" />
              </div>
              <div className="flex items-center gap-1 px-4 py-3 rounded-2xl bg-gray-100 dark:bg-gray-800">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-default p-4">
          <div className="max-w-3xl mx-auto flex items-center gap-2">
            <label className="p-2 text-gray-400 hover:text-gray-600 cursor-pointer rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
              <Upload className="h-5 w-5" />
              <input type="file" className="hidden" accept=".pdf,.doc,.docx,.txt" />
            </label>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="输入你的问题..."
              className="flex-1 h-12 px-4 rounded-xl border border-default bg-primary text-sm focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20"
              disabled={isProcessing}
            />
            {isProcessing ? (
              <Button variant="ghost" onClick={stopGeneration} className="text-red-500">
                停止
              </Button>
            ) : (
              <Button variant="primary" onClick={handleSend} disabled={!input.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            )}
          </div>
          <p className="text-[10px] text-gray-400 text-center mt-2">
            AI 回复仅供参考，请自行核实信息准确性
          </p>
        </div>
      </div>

      {/* Right panel: Quick info */}
      <div className="w-64 xl:w-80 border-l border-default hidden xl:flex flex-col p-4">
        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <PanelRightOpen className="h-4 w-4" /> 快捷操作
        </h3>
        <div className="space-y-2 mb-6">
          {QUICK_ACTIONS.map((action) => (
            <button key={action.label}
              onClick={() => sendMessage(action.query)}
              className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-left">
              <div className="h-8 w-8 rounded-lg bg-primary-50 dark:bg-primary-900/20 flex items-center justify-center">
                <action.icon className="h-4 w-4 text-primary-500" />
              </div>
              <span className="text-sm font-medium">{action.label}</span>
            </button>
          ))}
        </div>

        <h3 className="text-sm font-semibold mb-3">推荐岗位</h3>
        <Card className="p-3 mb-2">
          <p className="text-sm font-medium">AI算法工程师</p>
          <p className="text-xs text-gray-500">字节跳动 · 92% 匹配</p>
        </Card>
        <Card className="p-3 mb-2">
          <p className="text-sm font-medium">Java后端开发</p>
          <p className="text-xs text-gray-500">腾讯 · 85% 匹配</p>
        </Card>

        <div className="mt-auto pt-4 border-t border-default">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Badge variant="default" className="text-[10px]">DeepSeek</Badge>
            <span>0 tokens</span>
          </div>
        </div>
      </div>
    </div>
  );
}

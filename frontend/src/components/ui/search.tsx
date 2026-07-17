"use client";

import React from "react";
import { Search as SearchIcon, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchProps {
  value: string;
  onChange: (value: string) => void;
  onSearch?: (value: string) => void;
  placeholder?: string;
  className?: string;
  ai?: boolean;
}

export function Search({
  value,
  onChange,
  onSearch,
  placeholder = "搜索岗位、公司、技能...",
  className,
  ai = false,
}: SearchProps) {
  return (
    <div className={cn("relative", className)}>
      <SearchIcon className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSearch?.(value)}
        placeholder={placeholder}
        className={cn(
          "flex h-12 w-full rounded-xl border border-default bg-primary pl-10 pr-12 text-sm text-primary",
          "placeholder:text-gray-400 focus:outline-none focus:border-focused focus:ring-2 focus:ring-primary-500/20",
          "transition-all duration-150"
        )}
      />
      <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
        {value && (
          <button onClick={() => onChange("")} className="p-1 text-gray-400 hover:text-gray-600">
            <X className="h-4 w-4" />
          </button>
        )}
        {ai && (
          <span className="text-[10px] font-medium text-primary-500 bg-primary-100 dark:bg-primary-900/30 px-1.5 py-0.5 rounded">
            AI
          </span>
        )}
      </div>
    </div>
  );
}

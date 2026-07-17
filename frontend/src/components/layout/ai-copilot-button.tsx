"use client";

import React from "react";
import { Bot, X } from "lucide-react";
import { useCopilotStore } from "@/store";
import { cn } from "@/lib/utils";

export function AICopilotButton() {
  const { isOpen, toggleOpen } = useCopilotStore();

  return (
    <button
      onClick={toggleOpen}
      className={cn(
        "fixed bottom-6 right-6 z-40 h-14 w-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300",
        isOpen
          ? "bg-gray-200 dark:bg-gray-700 rotate-90"
          : "bg-primary-500 hover:bg-primary-600 hover:scale-105"
      )}
    >
      {isOpen ? (
        <X className="h-6 w-6 text-gray-700 dark:text-gray-300" />
      ) : (
        <Bot className="h-6 w-6 text-white" />
      )}
    </button>
  );
}

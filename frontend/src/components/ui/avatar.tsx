import React from "react";
import { cn } from "@/lib/utils";

interface AvatarProps {
  src?: string;
  name?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
}

const sizeMap = { sm: "h-8 w-8 text-xs", md: "h-10 w-10 text-sm", lg: "h-12 w-12 text-base", xl: "h-16 w-16 text-lg" };

export function Avatar({ src, name, size = "md", className }: AvatarProps) {
  const initials = name?.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase() ?? "?";

  if (src) {
    return <img src={src} alt={name ?? "avatar"} className={cn("rounded-full object-cover", sizeMap[size], className)} />;
  }

  return (
    <div className={cn(
      "rounded-full bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-300 flex items-center justify-center font-medium",
      sizeMap[size], className
    )}>
      {initials}
    </div>
  );
}

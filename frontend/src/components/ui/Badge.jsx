import React from "react";
import { cn } from "@/utils/cn";

const variants = {
  default: "bg-secondary text-foreground hover:bg-secondary-hover",
  primary: "bg-primary text-white hover:bg-primary-hover",
  outline: "text-foreground border border-border",
  success:
    "bg-[rgba(16,185,129,0.1)] text-success border border-[rgba(16,185,129,0.2)]",
  warning:
    "bg-[rgba(245,158,11,0.1)] text-warning border border-[rgba(245,158,11,0.2)]",
  danger:
    "bg-[rgba(239,68,68,0.1)] text-danger border border-[rgba(239,68,68,0.2)]",

  // Track specific badges
  llm: "bg-[rgba(0,245,255,0.1)] text-[#00f5ff] border border-[rgba(0,245,255,0.2)]",
  rag: "bg-[rgba(157,78,221,0.1)] text-[#9d4edd] border border-[rgba(157,78,221,0.2)]",
  vision:
    "bg-[rgba(0,255,136,0.1)] text-[#00ff88] border border-[rgba(0,255,136,0.2)]",
  agents:
    "bg-[rgba(255,170,0,0.1)] text-[#ffaa00] border border-[rgba(255,170,0,0.2)]",
};

export function Badge({ className, variant = "default", ...props }) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}

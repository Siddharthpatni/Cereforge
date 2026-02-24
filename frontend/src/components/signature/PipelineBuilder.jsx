import React from "react";
import { cn } from "@/utils/cn";
import { ArrowRight } from "lucide-react";

// Static stub for PipelineBuilder
export function PipelineBuilder({ nodes, edges, className }) {
  // Simple layout for 3 nodes max just as a visual representation
  return (
    <div
      className={cn(
        "p-4 border border-dashed border-zinc-700 bg-zinc-900/30 rounded-xl flex items-center justify-between gap-4 overflow-x-auto",
        className,
      )}
    >
      {nodes.map((node, i) => (
        <React.Fragment key={node.id}>
          <div className="flex flex-col items-center shrink-0 w-32">
            <div
              className={cn(
                "p-3 rounded-lg border w-full text-center text-xs font-mono font-bold transition-all",
                node.active
                  ? "bg-primary/20 border-primary shadow-[0_0_15px_rgba(67,56,202,0.3)] text-white"
                  : "bg-zinc-900 border-zinc-800 text-zinc-500",
              )}
            >
              {node.label}
            </div>
            <div className="text-[10px] text-zinc-500 mt-2 text-center leading-tight h-8">
              {node.description}
            </div>
          </div>

          {i < nodes.length - 1 && (
            <div className="shrink-0 text-zinc-700">
              <ArrowRight
                className={cn(
                  "h-6 w-6",
                  edges[i]?.active && "text-primary animate-pulse",
                )}
              />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

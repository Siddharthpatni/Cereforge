import React from "react";
import { useUIStore } from "@/stores/uiStore";
import { X, CheckCircle, AlertCircle, Info, XCircle } from "lucide-react";
import { cn } from "@/utils/cn";

const icons = {
  success: <CheckCircle className="h-5 w-5 text-success" />,
  error: <XCircle className="h-5 w-5 text-danger" />,
  warning: <AlertCircle className="h-5 w-5 text-warning" />,
  info: <Info className="h-5 w-5 text-accent-secondary" />,
};

const bgColors = {
  success: "bg-[#0c1a16] border-success/20",
  error: "bg-[#1f0f0f] border-danger/20",
  warning: "bg-[#1f1a0d] border-warning/20",
  info: "bg-[#0f171f] border-accent-secondary/20",
};

export function ToastContainer() {
  const { toasts, removeToast } = useUIStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-0 right-0 z-50 p-4 sm:p-6 flex flex-col gap-3 w-full sm:max-w-md pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "pointer-events-auto flex w-full items-start gap-3 rounded-lg border p-4 shadow-lg animate-in slide-in-from-right-full fade-in duration-300",
            bgColors[toast.type || "info"],
          )}
        >
          <div className="shrink-0 mt-0.5">{icons[toast.type || "info"]}</div>

          <div className="flex-1 space-y-1">
            {toast.title && (
              <p className="text-sm font-semibold text-white">{toast.title}</p>
            )}
            <p className="text-sm text-zinc-300 opacity-90">{toast.message}</p>
          </div>

          <button
            onClick={() => removeToast(toast.id)}
            className="shrink-0 rounded-md p-1 text-zinc-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  );
}

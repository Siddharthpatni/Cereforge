import React from "react";
import { Brain } from "lucide-react";

export default function PageSkeleton() {
    return (
        <div className="flex h-screen w-full flex-col bg-[#050508] relative overflow-hidden">
            {/* Thin cyan progress bar animating across top */}
            <div className="absolute top-0 left-0 h-1 bg-cyan-500 w-full rounded-full overflow-hidden">
                <div className="h-full bg-white/50 w-1/3 animate-[translateX_1s_ease-in-out_infinite]" style={{ transform: "translateX(-100%)", animation: "progress 1.5s infinite ease-in-out" }} />
            </div>

            <style>{`
        @keyframes progress {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(300%); }
        }
      `}</style>

            {/* Centered pulsing Logo */}
            <div className="flex flex-1 flex-col items-center justify-center">
                <div className="relative flex items-center justify-center h-20 w-20 rounded-full bg-cyan-900/20 animate-pulse outline outline-1 outline-cyan-500/20">
                    <Brain className="h-10 w-10 text-cyan-400" />

                    <div className="absolute inset-0 rounded-full border border-cyan-400 opacity-20 animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite]"></div>
                </div>
                <p className="mt-4 text-sm font-medium text-cyan-400/60 font-mono tracking-widest uppercase animate-pulse">
                    Forging
                </p>
            </div>
        </div>
    );
}

import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, Bell, Menu, X, Search } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { XPCounter } from "../signature/XPCounter";
import { Button } from "../ui/Button";

export function Navbar() {
  const { user, rank, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const searchRef = useRef(null);

  // Global / or Cmd+K shortcut focuses the search field (navigates to /tasks)
  useEffect(() => {
    const handleKey = (e) => {
      const tag = document.activeElement?.tagName?.toLowerCase();
      const isTyping = tag === "input" || tag === "textarea" || tag === "select";
      if (isTyping) return;
      if (e.key === "/" || (e.key === "k" && (e.metaKey || e.ctrlKey))) {
        e.preventDefault();
        navigate("/tasks");
        setTimeout(() => {
          const input = document.querySelector("input[type='text'], input[placeholder*='Search'], input[placeholder*='search']");
          if (input) input.focus();
        }, 100);
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [navigate]);

  const handleLogout = () => {
    logout();
    navigate("/auth");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-border bg-background/80 backdrop-blur-md px-4 sm:px-6">
      {/* Brand & Mobile Toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 -ml-2 text-zinc-400 hover:text-white"
        >
          {mobileMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>

        <Link to="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded bg-primary flex items-center justify-center text-lg shadow-[0_0_15px_rgba(67,56,202,0.5)]">
            🧠
          </div>
          <span className="hidden sm:block text-lg font-bold tracking-tight text-white">
            CereForge
          </span>
        </Link>
      </div>

      {/* Global Search Pill */}
      <button
        ref={searchRef}
        onClick={() => navigate("/tasks")}
        className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-border bg-zinc-900/60 text-zinc-500 text-xs hover:border-zinc-600 hover:text-zinc-300 transition-colors cursor-pointer"
        title="Press / or ⌘K to search tasks"
      >
        <Search className="h-3.5 w-3.5" />
        <span>Search tasks...</span>
        <kbd className="hidden sm:flex ml-1 items-center gap-0.5 bg-zinc-800 border border-zinc-700 rounded px-1.5 py-0.5 font-mono text-[10px] text-zinc-400">
          ⌘K
        </kbd>
      </button>

      <div className="flex items-center gap-4 sm:gap-6">
        {/* Ranked XP Counter */}
        {user && (
          <div className="flex items-center gap-3 pr-4 border-r border-border">
            <div className="hidden sm:flex flex-col items-end">
              <span
                className="text-xs font-semibold"
                style={{ color: rank?.color || "#a1a1aa" }}
              >
                {rank?.name || "Trainee"}
              </span>
              <span className="text-[10px] text-zinc-500">Rank</span>
            </div>

            <div className="flex items-center gap-1 bg-secondary rounded-full px-3 py-1 border border-border">
              <span className="text-xs font-bold text-white">
                <XPCounter value={user?.xp || 0} />
              </span>
              <span className="text-[10px] text-zinc-400 font-mono">XP</span>
            </div>
          </div>
        )}

        {/* Notifications & Profile Menu Stub */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="relative text-zinc-400 hover:text-white"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-primary" />
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            className="text-zinc-400 hover:text-white"
            title="Logout"
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </nav>
  );
}

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, Bell, Menu, X, Search, CheckCheck } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { XPCounter } from "../signature/XPCounter";
import { Button } from "../ui/Button";
import apiClient from "@/api/client";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/utils/cn";

export function Navbar() {
  const { user, rank, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notifs, setNotifs] = useState([]);
  const [unread, setUnread] = useState(0);
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);
  const searchRef = useRef(null);

  // Fetch real notifications
  const fetchNotifications = useCallback(() => {
    if (!user) return;
    apiClient
      .get("/notifications")
      .then((res) => {
        setNotifs(res.data.notifications || []);
        setUnread(res.data.unread_count || 0);
      })
      .catch(() => { });
  }, [user]);

  useEffect(() => {
    fetchNotifications();
    // Poll every 60s for new notifications
    const interval = setInterval(fetchNotifications, 60000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

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
          const input = document.querySelector(
            "input[type='text'], input[placeholder*='Search'], input[placeholder*='search']"
          );
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

  const markAllRead = async () => {
    await apiClient.post("/notifications/read-all").catch(() => { });
    setUnread(0);
    setNotifs((prev) => prev.map((n) => ({ ...n, is_read: true })));
  };

  const typeColor = (type) => {
    const map = {
      badge: "text-yellow-400",
      xp: "text-primary",
      answer_accepted: "text-success",
      upvote: "text-blue-400",
      new_comment: "text-zinc-300",
    };
    return map[type] || "text-zinc-300";
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
          <div className="h-8 w-8 rounded bg-primary flex items-center justify-center text-sm font-bold shadow-[0_0_15px_rgba(67,56,202,0.5)]">
            CF
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
              <span className="text-[10px] font-bold text-white mb-0.5">{user?.username}</span>
              <div className="flex items-center gap-2">
                <span
                  className="text-[10px] font-bold uppercase tracking-wider"
                  style={{ color: rank?.color || "#a1a1aa" }}
                >
                  {rank?.name || "Trainee"}
                </span>
                <span className="text-[10px] text-zinc-500">Rank</span>
              </div>
            </div>

            <div className="flex items-center gap-1 bg-secondary rounded-full px-2.5 py-1 border border-border shadow-inner">
              <span className="text-xs font-bold text-white">
                <XPCounter value={user?.xp || 0} />
              </span>
              <span className="text-[10px] text-zinc-400 font-mono">XP</span>
            </div>
          </div>
        )}

        {/* Notification Bell */}
        <div className="relative" ref={notifRef}>
          <Button
            variant="ghost"
            size="icon"
            className="text-zinc-400 hover:text-white relative"
            onClick={() => setNotifOpen((prev) => !prev)}
          >
            <Bell className="h-5 w-5" />
            {unread > 0 && (
              <span className="absolute top-1.5 right-1.5 h-4 w-4 rounded-full bg-primary text-[9px] font-bold text-white flex items-center justify-center leading-none">
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </Button>

          {notifOpen && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-zinc-900 border border-border rounded-xl shadow-2xl z-50 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-border/50">
                <div className="flex items-center gap-2">
                  <Bell className="h-4 w-4 text-primary" />
                  <span className="text-sm font-bold text-white">Notifications</span>
                  {unread > 0 && (
                    <span className="bg-primary/20 text-primary text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                      {unread} new
                    </span>
                  )}
                </div>
                {unread > 0 && (
                  <button
                    onClick={markAllRead}
                    className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                  >
                    <CheckCheck className="h-3.5 w-3.5" />
                    All read
                  </button>
                )}
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-border/30">
                {notifs.length === 0 ? (
                  <div className="px-4 py-6 text-center text-zinc-500 text-sm">
                    You're all caught up! 🎉
                  </div>
                ) : (
                  notifs.map((n) => (
                    <div
                      key={n.id}
                      className={cn(
                        "px-4 py-3 transition-colors hover:bg-zinc-800/50",
                        !n.is_read && "bg-primary/5 border-l-2 border-primary"
                      )}
                    >
                      <p className={cn("text-sm font-medium", typeColor(n.type))}>{n.title}</p>
                      <p className="text-xs text-zinc-400 mt-0.5 leading-relaxed">{n.body}</p>
                      <p className="text-[10px] text-zinc-600 mt-1">
                        {formatDistanceToNow(new Date(n.created_at))} ago
                      </p>
                    </div>
                  ))
                )}
              </div>

              {notifs.length > 0 && (
                <div className="px-4 py-2 border-t border-border/50 text-center">
                  <button
                    onClick={() => { setNotifOpen(false); navigate("/profile"); }}
                    className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                  >
                    View profile activity →
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

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
    </nav>
  );
}

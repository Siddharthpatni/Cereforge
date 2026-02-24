import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogOut, Bell, Menu, X } from "lucide-react";
import { useAuthStore } from "@/stores/authStore";
import { XPCounter } from "../signature/XPCounter";
import { Button } from "../ui/Button";

export function Navbar() {
  const { user, rank, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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

      {/* Right Actions */}
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

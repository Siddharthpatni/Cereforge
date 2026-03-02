import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Trophy,
  Medal,
  Star,
  ChevronLeft,
  ChevronRight,
  Zap,
  AlertCircle,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import apiClient from "@/api/client";
import { useAuthStore } from "@/stores/authStore";
import { cn } from "@/utils/cn";

export function Leaderboard() {
  const { user } = useAuthStore();
  const [data, setData] = useState({ items: [], total: 0, pages: 1 });
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [currentUserRank, setCurrentUserRank] = useState(null);
  const [timeframe, setTimeframe] = useState("all");

  useEffect(() => {
    fetchLeaderboard(page);
  }, [page]);

  const fetchLeaderboard = async (pageNum) => {
    setLoading(true);
    setError(false);
    try {
      const res = await apiClient.get(`/leaderboard?page=${pageNum}&size=20`);
      setData({
        items: res.data.items,
        total: res.data.total,
        pages: res.data.pages,
      });
      if (res.data.current_user_rank) {
        setCurrentUserRank(res.data.current_user_rank);
      }
    } catch (err) {
      console.error(err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return <Trophy className="h-6 w-6 text-yellow-500" />;
      case 2:
        return <Medal className="h-6 w-6 text-zinc-300" />;
      case 3:
        return <Medal className="h-6 w-6 text-amber-700" />;
      default:
        return (
          <span className="text-zinc-500 font-mono font-bold w-6 text-center">
            {rank}
          </span>
        );
    }
  };

  if (error)
    return (
      <div className="p-8 text-center text-zinc-500 min-h-[60vh] flex flex-col items-center justify-center">
        <AlertCircle className="h-12 w-12 mb-4 opacity-20" />
        <p className="mb-4">Failed to load leaderboard.</p>
        <Button onClick={() => fetchLeaderboard(page)} variant="outline">Retry</Button>
      </div>
    );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Trophy className="h-8 w-8 text-primary" /> Global Leaderboard
          </h1>
          <p className="text-zinc-400 mt-1">
            Compete with AI engineers worldwide. Rank up by completing challenges.
          </p>
        </div>
        {/* Timeframe tabs */}
        <div className="flex gap-1 bg-zinc-900 border border-zinc-800 rounded-lg p-1">
          {["week", "month", "all"].map((tf) => (
            <button
              key={tf}
              onClick={() => { setTimeframe(tf); setPage(1); }}
              className={cn(
                "px-4 py-1.5 text-xs font-semibold rounded-md capitalize transition-colors",
                timeframe === tf
                  ? "bg-primary text-white"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-800"
              )}
            >
              {tf === "all" ? "All-Time" : tf === "week" ? "This Week" : "This Month"}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 space-y-4">
          <Card className="glass-panel overflow-hidden border-border/80">
            <div className="w-full overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse min-w-[600px]">
                <thead>
                  <tr className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400">
                    <th className="py-4 px-6 font-semibold w-24">Rank</th>
                    <th className="py-4 px-6 font-semibold">Engineer</th>
                    <th className="py-4 px-6 font-semibold text-right">
                      Badges
                    </th>
                    <th className="py-4 px-6 font-semibold text-right">
                      Tasks
                    </th>
                    <th className="py-4 px-6 font-semibold text-right text-primary">
                      Total XP
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/50 relative">
                  {loading && (
                    <tr>
                      <td colSpan="5" className="py-12 text-center">
                        <Zap className="h-8 w-8 animate-spin-slow text-primary mx-auto" />
                      </td>
                    </tr>
                  )}
                  {!loading &&
                    data.items.map((entry) => (
                      <tr
                        key={entry.user.id}
                        className={cn(
                          "hover:bg-zinc-900/40 transition-colors group",
                          user?.id === entry.user.id
                            ? "bg-primary/5 hover:bg-primary/10"
                            : "",
                        )}
                      >
                        <td className="py-4 px-6 flex items-center justify-center">
                          {getRankIcon(entry.position)}
                        </td>
                        <td className="py-4 px-6">
                          <Link
                            to={`/profile/${entry.user.username}`}
                            className="flex items-center gap-3 w-fit group-hover:text-primary transition-colors"
                          >
                            <div className="h-8 w-8 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-bold font-mono text-zinc-400 group-hover:border-primary/50 group-hover:text-white">
                              {entry.user.username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-semibold text-zinc-200 group-hover:text-white">
                                {entry.user.username}
                              </div>
                              <div className="text-xs text-primary font-mono">
                                {entry.rank?.name || "Initiate"}
                              </div>
                            </div>
                          </Link>
                        </td>
                        <td className="py-4 px-6 text-right text-zinc-400">
                          {entry.badges_count > 0 ? entry.badges_count : "-"}
                        </td>
                        <td className="py-4 px-6 text-right text-zinc-400">
                          {entry.tasks_completed}
                        </td>
                        <td className="py-4 px-6 text-right font-mono font-bold text-white">
                          {entry.xp.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  {!loading && data.items.length === 0 && (
                    <tr>
                      <td
                        colSpan="5"
                        className="py-12 text-center text-zinc-500"
                      >
                        No users found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {!loading && data.pages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 bg-zinc-900/30 border-t border-zinc-800">
                <span className="text-xs text-zinc-500">
                  Page {page} of {data.pages}
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={page === 1}
                    onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={page === data.pages}
                    onClick={() =>
                      setPage((prev) => Math.min(data.pages, prev + 1))
                    }
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <Card className="border-primary/30 bg-primary/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-400 uppercase tracking-wider font-semibold">
                Your Standing
              </CardTitle>
            </CardHeader>
            <CardContent>
              {currentUserRank ? (
                <div className="text-center">
                  <div className="text-5xl font-bold text-white mb-2 font-mono">
                    #{currentUserRank.rank}
                  </div>
                  <div className="text-sm text-primary mb-4">
                    Top{" "}
                    {Math.max(
                      1,
                      Math.round(
                        (currentUserRank.rank / Math.max(data.total, 1)) * 100,
                      ),
                    )}
                    % worldwide
                  </div>

                  <div className="pt-4 border-t border-primary/20 flex justify-between text-xs sm:text-sm text-zinc-300">
                    <span>{currentUserRank.total_xp} XP</span>
                    <span>{currentUserRank.tasks_completed} Tasks</span>
                  </div>
                </div>
              ) : (
                <div className="text-center text-zinc-400 text-sm py-4">
                  Complete a task to get placed on the leaderboard.
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="glass-panel">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-zinc-400 uppercase tracking-wider font-semibold">
                Rank Tiers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 mt-2 text-sm">
                <div className="flex justify-between items-center text-zinc-300">
                  <span className="text-pink-400">Archmage</span>{" "}
                  <span>10,000+ XP</span>
                </div>
                <div className="flex justify-between items-center text-zinc-300">
                  <span className="text-purple-400">Grandmaster</span>{" "}
                  <span>5,000 XP</span>
                </div>
                <div className="flex justify-between items-center text-zinc-300">
                  <span className="text-blue-400">Master</span>{" "}
                  <span>2,500 XP</span>
                </div>
                <div className="flex justify-between items-center text-zinc-300">
                  <span className="text-emerald-400">Adept</span>{" "}
                  <span>1,000 XP</span>
                </div>
                <div className="flex justify-between items-center text-zinc-300">
                  <span className="text-zinc-400">Initiate</span>{" "}
                  <span>0 XP</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

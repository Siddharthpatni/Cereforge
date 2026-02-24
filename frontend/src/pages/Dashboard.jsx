import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  Trophy,
  Activity,
  ArrowRight,
  Zap,
  Target,
  BookOpen,
} from "lucide-react";
import apiClient from "@/api/client";
import { formatDistanceToNow } from "date-fns";

export function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get("/dashboard")
      .then((res) => {
        setData(res.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin-slow text-primary">
          <Zap className="h-8 w-8" />
        </div>
      </div>
    );
  }

  if (!data)
    return (
      <div className="p-8 text-center text-zinc-500">
        Failed to load dashboard data.
      </div>
    );

  const {
    stats,
    rank,
    next_task,
    recent_completions,
    badges,
    enrolled_paths,
    activity_feed,
  } = data;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Dashboard
          </h1>
          <p className="text-zinc-400 mt-1">
            Track your progress and continue learning.
          </p>
        </div>
      </div>

      {/* Top Stats Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-400">Total XP</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <p className="text-3xl font-bold text-white">
                    {stats.xp.toLocaleString()}
                  </p>
                </div>
              </div>
              <div className="p-3 bg-primary/10 rounded-full text-primary">
                <Zap className="h-5 w-5" />
              </div>
            </div>

            <div className="mt-4 w-full bg-zinc-800 rounded-full h-1.5 mb-1 overflow-hidden">
              <div
                className="bg-primary h-1.5 rounded-full transition-all duration-1000"
                style={{
                  width: `${Math.min(100, (stats.xp / (rank.next_rank_xp || 1)) * 100)}%`,
                }}
              />
            </div>
            {rank.next_rank && (
              <p className="text-xs text-zinc-500">
                {rank.xp_needed} XP to {rank.next_rank}
              </p>
            )}
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-400">
                  Tasks Completed
                </p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats.tasks_completed}{" "}
                  <span className="text-sm text-zinc-500 font-normal">
                    / {stats.total_tasks}
                  </span>
                </p>
              </div>
              <div className="p-3 bg-success/10 rounded-full text-success">
                <Target className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-400">
                  Badges Earned
                </p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats.badges_earned}{" "}
                  <span className="text-sm text-zinc-500 font-normal">
                    / {stats.total_badges}
                  </span>
                </p>
              </div>
              <div className="p-3 bg-warning/10 rounded-full text-warning">
                <Trophy className="h-5 w-5" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card
          className="glass-panel border-l-4"
          style={{ borderLeftColor: rank.color }}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-zinc-400">
                  Current Rank
                </p>
                <p
                  className="text-xl font-bold mt-1"
                  style={{ color: rank.color }}
                >
                  {rank.name}
                </p>
              </div>
              <div
                className="h-10 w-10 rounded-lg flex items-center justify-center font-bold text-lg"
                style={{
                  backgroundColor: `${rank.color}20`,
                  color: rank.color,
                  border: `1px solid ${rank.color}40`,
                }}
              >
                {rank.name.charAt(0)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Column (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Featured Task */}
          <Card className="border-primary/20 bg-gradient-to-br from-card to-primary/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Zap className="h-5 w-5 text-primary" /> Recommended Next Task
              </CardTitle>
            </CardHeader>
            <CardContent>
              {next_task ? (
                <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-white">
                        {next_task.title}
                      </h3>
                      <Badge variant={next_task.track}>
                        {next_task.track.toUpperCase()}
                      </Badge>
                    </div>
                    <p className="text-sm text-zinc-400 line-clamp-2 max-w-xl">
                      {next_task.description}
                    </p>
                    <p className="text-xs font-mono text-primary pt-1">
                      +{next_task.xp_reward} XP
                    </p>
                  </div>
                  <Button
                    asChild
                    className="shrink-0 bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30"
                  >
                    <Link to={`/tasks/${next_task.slug}`}>
                      Start Task <ArrowRight className="h-4 w-4 ml-1" />
                    </Link>
                  </Button>
                </div>
              ) : (
                <p className="text-zinc-400">
                  You've completed all available tasks! Amazing work.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Enrolled Paths */}
          {enrolled_paths.length > 0 && (
            <Card>
              <CardHeader className="pb-3 border-b border-border/50">
                <CardTitle className="text-lg">Learning Paths</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="divide-y divide-border/50">
                  {enrolled_paths.map((path) => (
                    <div
                      key={path.slug}
                      className="p-4 flex items-center justify-between hover:bg-zinc-900/30 transition-colors"
                    >
                      <div className="max-w-[70%]">
                        <h4 className="font-medium text-zinc-200">
                          {path.title}
                        </h4>
                        <div className="flex items-center gap-3 mt-2">
                          <div className="w-full max-w-[200px] bg-zinc-800 rounded-full h-1.5 flex-1">
                            <div
                              className="bg-accent-secondary h-1.5 rounded-full"
                              style={{ width: `${path.progress}%` }}
                            />
                          </div>
                          <span className="text-xs text-zinc-500">
                            {path.completed_tasks}/{path.total_tasks} completed
                          </span>
                        </div>
                      </div>
                      <Button asChild variant="ghost" size="sm">
                        <Link to={`/paths/${path.slug}`}>Resume</Link>
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Completions */}
          <Card>
            <CardHeader className="pb-3 border-b border-border/50">
              <CardTitle className="text-lg">Recent Completions</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {recent_completions.length > 0 ? (
                <div className="divide-y divide-border/50">
                  {recent_completions.map((sub) => (
                    <div
                      key={sub.task_slug}
                      className="p-4 flex items-center justify-between"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-zinc-200">
                            {sub.task_title}
                          </h4>
                          <Badge
                            variant={sub.track}
                            className="scale-75 origin-left"
                          >
                            {sub.track}
                          </Badge>
                        </div>
                        <p className="text-xs text-zinc-500 mt-1">
                          Submitted{" "}
                          {formatDistanceToNow(new Date(sub.submitted_at))} ago
                        </p>
                      </div>
                      <span className="text-success text-sm font-mono flex items-center gap-1">
                        +{sub.xp_earned} XP
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-zinc-500">
                  <BookOpen className="h-8 w-8 mx-auto mb-3 opacity-20" />
                  <p>No tasks completed yet.</p>
                  <Button asChild variant="outline" size="sm" className="mt-4">
                    <Link to="/tasks">View Tasks</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Sidebar Column (1/3) */}
        <div className="space-y-6">
          {/* Badge Showcase */}
          <Card>
            <CardHeader className="pb-3 border-b border-border/50">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Badges</CardTitle>
                <Link
                  to="/profile"
                  className="text-xs text-primary hover:underline"
                >
                  View All
                </Link>
              </div>
            </CardHeader>
            <CardContent className="p-4">
              <div className="grid grid-cols-4 gap-2">
                {badges
                  .filter((b) => b.earned)
                  .slice(0, 8)
                  .map((badge) => (
                    <div
                      key={badge.slug}
                      className="aspect-square flex flex-col items-center justify-center rounded-lg bg-zinc-900 border border-zinc-800 p-2 text-center"
                      title={badge.name}
                    >
                      <span className="text-2xl filter drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]">
                        {badge.icon}
                      </span>
                    </div>
                  ))}

                {badges.filter((b) => b.earned).length === 0 && (
                  <div className="col-span-4 py-6 text-center text-zinc-500 text-sm">
                    Complete tasks to earn badges.
                  </div>
                )}

                {/* Empty slots for missing badges up to 4 */}
                {Array.from({
                  length: Math.max(
                    0,
                    4 - badges.filter((b) => b.earned).length,
                  ),
                }).map((_, i) => (
                  <div
                    key={`empty-${i}`}
                    className="aspect-square rounded-lg border border-dashed border-zinc-800 bg-zinc-950/50"
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Activity Feed */}
          <Card>
            <CardHeader className="pb-3 border-b border-border/50">
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity className="h-4 w-4 text-zinc-400" /> Activity Log
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y divide-border/50 max-h-[400px] overflow-y-auto scrollbar-hide">
                {activity_feed.length > 0 ? (
                  activity_feed.map((act, i) => (
                    <div key={i} className="p-4">
                      <p className="text-sm font-medium text-zinc-200">
                        {act.title}
                      </p>
                      <p className="text-xs text-zinc-400 mt-1">{act.body}</p>
                      <p className="text-[10px] text-zinc-500 mt-2 uppercase tracking-wider">
                        {formatDistanceToNow(new Date(act.created_at))} ago
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center text-sm text-zinc-500">
                    No recent activity.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

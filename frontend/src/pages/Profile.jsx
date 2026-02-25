import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  Trophy,
  Code,
  MessageSquare,
  Calendar,
  ChevronRight,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import apiClient from "@/api/client";
import { useAuthStore } from "@/stores/authStore";
import { formatDistanceToNow, format } from "date-fns";

export function Profile() {
  const { username } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();

  const [profileUser, setProfileUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // If no username provided, default to current user
  const targetUsername = username || currentUser?.username;

  useEffect(() => {
    if (!targetUsername) {
      navigate("/auth");
      return;
    }

    setTimeout(() => setLoading(true), 0);
    apiClient
      .get(`/users/${targetUsername}`)
      .then((res) => setProfileUser(res.data))
      .catch((err) => {
        console.error(err);
        setProfileUser(null);
      })
      .finally(() => setLoading(false));
  }, [targetUsername, navigate]);

  if (loading)
    return (
      <div className="p-12 text-center text-primary animate-pulse flex items-center justify-center min-h-[50vh]">
        <div className="animate-pulse flex flex-col items-center">
          <span className="text-4xl mb-4">🧠</span>
          <span>Loading Profile...</span>
        </div>
      </div>
    );
  if (!profileUser) return (
    <div className="p-12 text-center text-zinc-500 min-h-[50vh] flex flex-col items-center justify-center">
      <div className="text-6xl mb-4">👻</div>
      <h2 className="text-2xl font-bold text-white mb-2">User Not Found</h2>
      <p>The profile you are looking for does not exist.</p>
      <Button variant="outline" className="mt-6" onClick={() => navigate("/")}>Return Home</Button>
    </div>
  );

  const isCurrentUser = profileUser.id === currentUser?.id;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Profile Header Block */}
      <div className="relative rounded-2xl border border-border bg-card overflow-hidden">
        {/* Cover ambient effect */}
        <div className="h-32 bg-gradient-to-r from-primary/20 via-primary/5 to-transparent border-b border-border/50 relative overflow-hidden">
          <div className="absolute top-[-50%] left-[-10%] w-[40%] h-[200%] bg-primary/20 blur-[80px] rounded-full" />
        </div>

        <div className="p-6 sm:p-8 pt-0 relative flex flex-col sm:flex-row gap-6 sm:items-end -mt-12 sm:-mt-16">
          <div className="h-24 w-24 sm:h-32 sm:w-32 rounded-2xl bg-zinc-950 border-4 border-card flex items-center justify-center shadow-xl shrink-0 z-10">
            <span className="text-4xl sm:text-5xl font-bold font-mono text-zinc-400">
              {profileUser.user.username.charAt(0).toUpperCase()}
            </span>
          </div>

          <div className="flex-1 pb-2 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">
                {profileUser.user.username}
              </h1>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <Badge
                  variant="outline"
                  className="text-primary border-primary bg-primary/5"
                >
                  {profileUser.rank?.name || "Initiate"}
                </Badge>
                <span className="text-sm text-zinc-400 flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" /> Joined{" "}
                  {format(new Date(profileUser.user.created_at), "MMMM yyyy")}
                </span>
              </div>
            </div>

            {isCurrentUser && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  useAuthStore.getState().logout();
                  navigate("/auth");
                }}
              >
                Sign Out
              </Button>
            )}
          </div>
        </div>

        {/* Quick Stats Banner */}
        <div className="grid grid-cols-3 divide-x divide-border/50 border-t border-border/50 bg-zinc-900/30">
          <div className="p-4 text-center">
            <div className="text-2xl font-bold text-white font-mono">
              {profileUser.stats.xp.toLocaleString()}
            </div>
            <div className="text-xs text-zinc-500 uppercase font-semibold">
              Total XP
            </div>
          </div>
          <div className="p-4 text-center">
            <div className="text-2xl font-bold text-white font-mono">
              {profileUser.stats.tasks_completed || 0}
            </div>
            <div className="text-xs text-zinc-500 uppercase font-semibold">
              Tasks Completed
            </div>
          </div>
          <div className="p-4 text-center">
            <div className="text-2xl font-bold text-white font-mono">
              {profileUser.stats.badges_earned || 0}
            </div>
            <div className="text-xs text-zinc-500 uppercase font-semibold">
              Badges Earned
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-1 space-y-6">
          {/* Badges Collection */}
          <Card className="glass-panel">
            <CardContent className="p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Trophy className="h-5 w-5 text-primary" /> Badge Showcase
              </h3>

              {profileUser.badges && profileUser.badges.length > 0 ? (
                <div className="grid grid-cols-3 gap-3">
                  {profileUser.badges.map((badge) => (
                    <div
                      key={badge.slug}
                      className="group relative flex flex-col items-center p-3 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-primary/50 transition-colors"
                    >
                      <span className="text-3xl mb-1 group-hover:scale-110 transition-transform">
                        {badge.icon}
                      </span>
                      <span className="text-[10px] font-medium text-zinc-400 text-center line-clamp-2">
                        {badge.name}
                      </span>
                      <div className="absolute opacity-0 group-hover:opacity-100 bg-zinc-800 text-white text-xs p-2 rounded w-48 z-20 pointer-events-none -bottom-2 translate-y-full left-1/2 -translate-x-1/2 transition-opacity">
                        {badge.description}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-zinc-500 py-6 text-sm">
                  No badges unlocked yet.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Tasks */}
          <Card className="glass-panel">
            <CardContent className="p-0">
              <div className="p-6 border-b border-border/50">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary" /> Completed Challenges
                </h3>
              </div>

              <div className="divide-y divide-border/50">
                {profileUser.completions &&
                  profileUser.completions.length > 0 ? (
                  profileUser.completions.map((taskLog, idx) => (
                    <div
                      key={taskLog.task_slug || idx}
                      className="p-4 sm:p-6 hover:bg-zinc-900/30 transition-colors flex items-center justify-between"
                    >
                      <div>
                        <Link
                          to={`/tasks/${taskLog.task_slug}`}
                          className="text-white font-medium hover:text-primary transition-colors block mb-1"
                        >
                          {taskLog.task_title}
                        </Link>
                        <p className="text-xs text-zinc-500">
                          Completed{" "}
                          {formatDistanceToNow(new Date(taskLog.submitted_at))}{" "}
                          ago
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Badge
                          variant={taskLog.track}
                          className="text-[10px]"
                        >
                          {(taskLog.track || "mission").toUpperCase()}
                        </Badge>
                        <span className="text-xs text-primary font-mono bg-primary/10 px-2 py-1 rounded inline-flex items-center">
                          +{taskLog.xp_earned} XP
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-zinc-500 py-8">
                    No tasks completed yet.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Forum Activity */}
          <Card className="glass-panel">
            <CardContent className="p-0">
              <div className="p-6 border-b border-border/50">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-primary" /> Community
                  Contributions
                </h3>
              </div>

              <div className="divide-y divide-border/50">
                {profileUser.posts && profileUser.posts.length > 0 ? (
                  profileUser.posts.map((post) => (
                    <div
                      key={post.id}
                      className="p-4 sm:p-6 hover:bg-zinc-900/30 transition-colors"
                    >
                      <Link
                        to={`/community/${post.id}`}
                        className="block group"
                      >
                        <h4 className="text-zinc-200 font-medium group-hover:text-primary transition-colors">
                          {post.title}
                        </h4>
                        <div className="flex items-center gap-4 text-xs text-zinc-500 mt-2">
                          <span>
                            {formatDistanceToNow(new Date(post.created_at))} ago
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageSquare className="h-3 w-3" />{" "}
                            {post.comment_count || 0}
                          </span>
                          <span className="flex items-center gap-1">
                            Score: {post.vote_score || 0}
                          </span>
                        </div>
                      </Link>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-zinc-500 py-8">
                    No community posts yet.
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

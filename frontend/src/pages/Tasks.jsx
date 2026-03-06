import React, { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { CheckCircle, Zap, Filter, Search, AlertCircle, Bookmark, BookmarkCheck } from "lucide-react";
import apiClient from "@/api/client";
import { cn } from "@/utils/cn";
import { useUIStore } from "@/stores/uiStore";

const TRACKS = ["llm", "rag", "vision", "agents"];
const DIFFICULTIES = ["beginner", "intermediate", "expert"];

export function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedTrack, setSelectedTrack] = useState("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState("all");
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);
  const { addToast } = useUIStore();

  // Debounce search input: wait 400ms after typing before firing request
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(t);
  }, [search]);

  useEffect(() => {
    fetchTasks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTrack, selectedDifficulty, debouncedSearch, bookmarkedOnly]);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const params = new URLSearchParams();
      if (selectedTrack !== "all") params.append("track", selectedTrack);
      if (selectedDifficulty !== "all") params.append("difficulty", selectedDifficulty);
      if (debouncedSearch.trim()) params.append("search", debouncedSearch.trim());
      if (bookmarkedOnly) params.append("bookmarked", "true");
      const res = await apiClient.get(`/tasks?${params.toString()}`);
      setTasks(res.data);
    } catch (err) {
      console.error(err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [selectedTrack, selectedDifficulty, debouncedSearch, bookmarkedOnly]);

  const handleBookmark = async (e, slug) => {
    e.preventDefault(); // don't navigate to task
    e.stopPropagation();
    try {
      const res = await apiClient.post(`/tasks/${slug}/bookmark`);
      setTasks((prev) =>
        prev.map((t) =>
          t.slug === slug ? { ...t, bookmarked: res.data.bookmarked } : t
        )
      );
    } catch {
      addToast({ title: "Error", message: "Could not update bookmark", type: "error" });
    }
  };

  const completedCount = tasks.filter((t) => t.completed).length;
  const totalCount = tasks.length;

  if (error)
    return (
      <div className="p-8 text-center text-zinc-500 min-h-[60vh] flex flex-col items-center justify-center">
        <AlertCircle className="h-12 w-12 mb-4 opacity-20" />
        <p className="mb-4">Failed to load tasks.</p>
        <Button onClick={fetchTasks} variant="outline">Retry</Button>
      </div>
    );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Challenge Forge
          </h1>
          <p className="text-zinc-400 mt-1">
            Select an AI challenge, read the guide, and submit your solution.
          </p>
        </div>
        {!loading && totalCount > 0 && (
          <div className="flex items-center gap-3 shrink-0">
            <div className="text-right">
              <p className="text-2xl font-bold text-white">{completedCount}<span className="text-zinc-500 text-base font-normal"> / {totalCount}</span></p>
              <p className="text-xs text-zinc-500">tasks completed</p>
            </div>
            <div className="relative h-12 w-12">
              <svg className="h-12 w-12 -rotate-90" viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="#27272a" strokeWidth="3" />
                <circle
                  cx="18" cy="18" r="15.9" fill="none"
                  stroke="hsl(var(--primary))"
                  strokeWidth="3"
                  strokeDasharray={`${totalCount ? (completedCount / totalCount) * 100 : 0} 100`}
                  strokeLinecap="round"
                  style={{ transition: "stroke-dasharray 0.8s ease" }}
                />
              </svg>
              <CheckCircle className="h-4 w-4 text-primary absolute inset-0 m-auto" />
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between p-4 bg-card rounded-xl border border-border">
        <div className="flex items-center gap-2 w-full md:w-auto flex-wrap">
          <Filter className="h-4 w-4 text-zinc-400 shrink-0" />
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedTrack("all")}
              className={cn(
                "px-3 py-1 text-xs font-semibold rounded-full border transition-colors",
                selectedTrack === "all"
                  ? "bg-secondary text-white border-zinc-600"
                  : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
              )}
            >
              All Tracks
            </button>
            {TRACKS.map((track) => (
              <button
                key={track}
                onClick={() => setSelectedTrack(track)}
                className={cn(
                  "px-3 py-1 text-xs font-semibold rounded-full border transition-colors uppercase",
                  selectedTrack === track
                    ? `bg-primary/20 text-primary border-primary/40`
                    : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
                )}
              >
                {track}
              </button>
            ))}
          </div>

          <div className="w-px h-4 bg-zinc-700 mx-1 hidden md:block" />

          {/* Difficulty filter */}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedDifficulty("all")}
              className={cn(
                "px-3 py-1 text-xs font-semibold rounded-full border transition-colors",
                selectedDifficulty === "all"
                  ? "bg-secondary text-white border-zinc-600"
                  : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
              )}
            >
              All Levels
            </button>
            {DIFFICULTIES.map((diff) => (
              <button
                key={diff}
                onClick={() => setSelectedDifficulty(diff)}
                className={cn(
                  "px-3 py-1 text-xs font-semibold rounded-full border transition-colors capitalize",
                  selectedDifficulty === diff
                    ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                    : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
                )}
              >
                {diff}
              </button>
            ))}
          </div>

          {/* Bookmark filter */}
          <button
            onClick={() => setBookmarkedOnly((v) => !v)}
            className={cn(
              "px-3 py-1 text-xs font-semibold rounded-full border transition-colors flex items-center gap-1",
              bookmarkedOnly
                ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
            )}
          >
            <Bookmark className="h-3 w-3" />
            Saved
          </button>
        </div>

        <div className="relative w-full md:w-64">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-zinc-900 border border-zinc-800 rounded-md text-sm text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex justify-center p-12">
          <Zap className="h-8 w-8 animate-spin-slow text-primary" />
        </div>
      ) : tasks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {tasks.map((task) => (
            <Link
              key={task.id}
              to={`/tasks/${task.slug}`}
              className="block group"
            >
              <Card className="h-full glass-panel hover:border-primary/50 hover:shadow-[0_0_15px_rgba(67,56,202,0.15)] transition-all duration-300">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <Badge variant={task.track}>
                      {task.track.toUpperCase()}
                    </Badge>
                    <div className="flex items-center gap-2">
                      {/* Bookmark toggle */}
                      <button
                        onClick={(e) => handleBookmark(e, task.slug)}
                        className={cn(
                          "p-1 rounded transition-colors",
                          task.bookmarked
                            ? "text-amber-400 hover:text-amber-300"
                            : "text-zinc-600 hover:text-zinc-300"
                        )}
                        title={task.bookmarked ? "Remove bookmark" : "Save task"}
                      >
                        {task.bookmarked
                          ? <BookmarkCheck className="h-4 w-4" />
                          : <Bookmark className="h-4 w-4" />}
                      </button>

                      {task.completed ? (
                        <div className="flex items-center gap-1 text-success text-xs font-semibold bg-success/10 px-2 py-1 rounded-full border border-success/20">
                          <CheckCircle className="h-3.5 w-3.5" />
                          Done
                        </div>
                      ) : (
                        <div className="text-xs font-mono text-primary font-bold">
                          +{task.xp_reward} XP
                        </div>
                      )}
                    </div>
                  </div>
                  <CardTitle className="text-xl mt-3 text-white group-hover:text-primary transition-colors line-clamp-1">
                    {task.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-zinc-400 line-clamp-3 leading-relaxed">
                    {task.description}
                  </p>
                  <div className="mt-4 flex items-center justify-between text-xs text-zinc-500">
                    <span>
                      Difficulty:{" "}
                      <span className="text-zinc-300 font-medium capitalize">
                        {task.difficulty}
                      </span>
                    </span>
                    <span className="flex items-center gap-1 text-primary group-hover:underline">
                      View Challenge &rarr;
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center p-12 border border-dashed border-zinc-800 rounded-xl bg-zinc-900/20">
          <p className="text-zinc-400">
            No tasks found matching your criteria.
          </p>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => {
              setSearch("");
              setSelectedTrack("all");
              setSelectedDifficulty("all");
              setBookmarkedOnly(false);
            }}
          >
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  );
}

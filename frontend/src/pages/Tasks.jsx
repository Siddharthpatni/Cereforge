import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { CheckCircle, Zap, Filter, Search } from "lucide-react";
import apiClient from "@/api/client";
import { cn } from "@/utils/cn";

const TRACKS = ["llm", "rag", "vision", "agents"];

export function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedTrack, setSelectedTrack] = useState("all");

  useEffect(() => {
    fetchTasks();
  }, [selectedTrack]);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const url =
        selectedTrack === "all" ? "/tasks" : `/tasks?track=${selectedTrack}`;
      const res = await apiClient.get(url);
      setTasks(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter(
    (t) =>
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase()),
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
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between p-4 bg-card rounded-xl border border-border">
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="h-4 w-4 text-zinc-400" />
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
                    ? `bg-[rgba(255,255,255,0.1)] text-white border-zinc-600`
                    : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
                )}
              >
                {track}
              </button>
            ))}
          </div>
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
      ) : filteredTasks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTasks.map((task) => (
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
                    {task.is_completed ? (
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
            }}
          >
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  );
}

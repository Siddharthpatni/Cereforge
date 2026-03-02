import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Map, BookOpen, Layers, Clock, AlertCircle } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import apiClient from "@/api/client";

const SKILL_LABELS = {
  absolute_beginner: "Absolute Beginner",
  some_python: "Some Python",
  ml_familiar: "ML Familiar",
  advanced: "Advanced",
};

const PATH_ICONS = ["🧭", "🗄️", "🤖", "👁️", "🔮"];

export function Paths() {
  const [paths, setPaths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadPaths = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await apiClient.get("/paths");
      setPaths(res.data);
    } catch (err) {
      console.error(err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPaths();
  }, []);

  if (loading)
    return (
      <div className="p-12 text-center text-primary animate-pulse flex flex-col items-center justify-center min-h-[50vh]">
        <Map className="h-10 w-10 mb-3 text-primary/50" />
        <span>Loading Curriculums...</span>
      </div>
    );

  if (error)
    return (
      <div className="p-12 text-center text-zinc-500 min-h-[50vh] flex flex-col items-center justify-center">
        <AlertCircle className="h-12 w-12 mb-4 opacity-20" />
        <p className="mb-4">Failed to load learning paths.</p>
        <Button onClick={loadPaths} variant="outline">
          Retry
        </Button>
      </div>
    );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">
          Structured Learning Paths
        </h1>
        <p className="text-zinc-400 mt-1">
          Master specific domains of AI through curated sequences of challenges.{" "}
          <span className="text-primary font-medium">{paths.length} paths available.</span>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {paths.map((path, idx) => {
          const isEnrolled = path.enrolled;
          const progressPerc = path.progress || 0;
          const total = path.task_sequence?.length || 0;
          const moduleCount = path.modules?.length || 0;
          const icon = PATH_ICONS[idx % PATH_ICONS.length];

          return (
            <Card
              key={path.id}
              className="flex flex-col h-full glass-panel hover:border-primary/50 transition-all duration-200 hover:shadow-lg hover:shadow-primary/5"
            >
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-zinc-900 border border-zinc-800 text-2xl">
                    {icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-white text-lg leading-tight line-clamp-2">
                      {path.title}
                    </CardTitle>
                    <p className="text-xs text-primary font-mono mt-1">
                      {path.duration_days} days
                    </p>
                  </div>
                </div>

                {/* Skill level badges */}
                <div className="flex flex-wrap gap-1 mt-2">
                  {path.for_skill_levels?.map((level) => (
                    <Badge
                      key={level}
                      variant="outline"
                      className="text-[10px] px-1.5 py-0 border-zinc-700 text-zinc-400"
                    >
                      {SKILL_LABELS[level] || level}
                    </Badge>
                  ))}
                </div>
              </CardHeader>

              <CardContent className="flex flex-col flex-1">
                <CardDescription className="text-zinc-400 line-clamp-3 mb-5">
                  {path.description}
                </CardDescription>

                <div className="grid grid-cols-2 gap-3 text-sm text-zinc-300 mb-5 bg-zinc-900/50 p-3 rounded-xl border border-zinc-800/50">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-zinc-500 shrink-0" />
                    <span>{moduleCount} Modules</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-zinc-500 shrink-0" />
                    <span>{total} Tasks</span>
                  </div>
                </div>

                <div className="mt-auto pt-4 flex items-end justify-between border-t border-border/50">
                  {isEnrolled ? (
                    <div className="w-full">
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="text-zinc-400 font-medium">Your Progress</span>
                        <span className="text-white font-bold">{progressPerc}%</span>
                      </div>
                      <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden mb-4">
                        <div
                          className="bg-success h-2 rounded-full transition-all duration-700"
                          style={{ width: `${progressPerc}%` }}
                        />
                      </div>
                      <Button asChild fullWidth variant="secondary" className="bg-zinc-800 hover:bg-zinc-700">
                        <Link to={`/paths/${path.slug}`}>Continue Path</Link>
                      </Button>
                    </div>
                  ) : (
                    <Button asChild fullWidth>
                      <Link to={`/paths/${path.slug}`}>View &amp; Enroll</Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {paths.length === 0 && !loading && (
        <div className="text-center text-zinc-500 py-16">
          <Map className="h-12 w-12 mx-auto mb-4 opacity-20" />
          <p>No learning paths available yet.</p>
        </div>
      )}
    </div>
  );
}

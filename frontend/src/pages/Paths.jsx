import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Map, BookOpen, Layers, CheckCircle } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import apiClient from "@/api/client";

export function Paths() {
  const [paths, setPaths] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get("/paths")
      .then((res) => setPaths(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return (
      <div className="p-12 text-center text-primary animate-pulse">
        Loading Curriculums...
      </div>
    );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">
          Structured Learning Paths
        </h1>
        <p className="text-zinc-400 mt-1">
          Master specific domains of AI through curated sequences of challenges.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {paths.map((path) => {
          const isEnrolled = path.student_progress !== null;
          const completed = isEnrolled
            ? path.student_progress.completed_tasks
            : 0;
          const total = path.total_tasks;
          const progressPerc = total > 0 ? (completed / total) * 100 : 0;

          return (
            <Card
              key={path.id}
              className="flex flex-col h-full glass-panel hover:border-primary/50 transition-colors"
            >
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800 text-primary">
                    <Map className="h-6 w-6" />
                  </div>
                  <div>
                    <CardTitle className="text-white text-xl">
                      {path.title}
                    </CardTitle>
                    <p className="text-xs text-primary font-mono mt-1">
                      Difficulty:{" "}
                      <span className="capitalize">{path.difficulty}</span>
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex flex-col flex-1">
                <CardDescription className="text-zinc-400 line-clamp-3 mb-6">
                  {path.description}
                </CardDescription>

                <div className="grid grid-cols-2 gap-4 text-sm text-zinc-300 mb-6 bg-zinc-900/50 p-4 rounded-xl border border-zinc-800/50">
                  <div className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-zinc-500" />
                    <span>{path.total_modules} Modules</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-zinc-500" />
                    <span>{path.total_tasks} Tasks</span>
                  </div>
                </div>

                <div className="mt-auto pt-4 flex items-end justify-between border-t border-border/50">
                  {isEnrolled ? (
                    <div className="w-full">
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="text-zinc-400 font-medium">
                          Your Progress
                        </span>
                        <span className="text-white font-bold">
                          {completed} / {total}
                        </span>
                      </div>
                      <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden mb-4">
                        <div
                          className="bg-success h-2 rounded-full transition-all duration-500"
                          style={{ width: `${progressPerc}%` }}
                        />
                      </div>
                      <Button
                        asChild
                        fullWidth
                        variant="secondary"
                        className="bg-zinc-800 hover:bg-zinc-700"
                      >
                        <Link to={`/paths/${path.slug}`}>Continue Path</Link>
                      </Button>
                    </div>
                  ) : (
                    <Button asChild fullWidth>
                      <Link to={`/paths/${path.slug}`}>View & Enroll</Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

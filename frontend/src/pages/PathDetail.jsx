import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useUIStore } from "@/stores/uiStore";
import apiClient from "@/api/client";
import {
  ArrowLeft,
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Lock,
  PlayCircle,
} from "lucide-react";
import { cn } from "@/utils/cn";

export function PathDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { addToast } = useUIStore();

  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [expandedModules, setExpandedModules] = useState({});

  const fetchPath = async () => {
    try {
      const res = await apiClient.get(`/paths/${slug}`);
      setPath(res.data);
      // Auto expand first module
      if (res.data.modules && res.data.modules.length > 0) {
        setExpandedModules({ [res.data.modules[0].id]: true });
      }
    } catch {
      addToast({ title: "Error", message: "Path not found.", type: "error" });
      navigate("/paths");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPath();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      await apiClient.post(`/paths/${path.id}/enroll`);
      addToast({
        title: "Enrolled",
        message: `You have joined ${path.title}!`,
        type: "success",
      });
      fetchPath(); // refresh to get updated curriculum visibility
    } catch (err) {
      addToast({
        title: "Enrollment Failed",
        message: err.response?.data?.detail || "Try again later",
        type: "error",
      });
    } finally {
      setEnrolling(false);
    }
  };

  const toggleModule = (id) => {
    setExpandedModules((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (loading)
    return (
      <div className="p-12 text-center text-primary animate-pulse">
        Loading Curriculum...
      </div>
    );
  if (!path) return null;

  const isEnrolled = path.student_progress !== null;

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header section */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/paths")}
          className="text-zinc-400 hover:text-white px-0 hover:bg-transparent -ml-2 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Paths
        </Button>
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <Badge className="bg-zinc-800 text-zinc-300 border-zinc-700 capitalize">
                Difficulty: {path.difficulty}
              </Badge>
              <Badge className="bg-primary/10 text-primary border-primary/20">
                {path.total_modules} Modules
              </Badge>
              <Badge className="bg-accent-secondary/10 text-accent-secondary border-accent-secondary/20">
                {path.total_tasks} Tasks
              </Badge>
            </div>
            <h1 className="text-4xl font-bold text-white mb-4 tracking-tight">
              {path.title}
            </h1>
            <p className="text-lg text-zinc-400 max-w-3xl leading-relaxed">
              {path.description}
            </p>
          </div>

          <div className="shrink-0 w-full md:w-64 bg-card border border-border rounded-xl p-5 shadow-lg">
            {!isEnrolled ? (
              <div className="text-center">
                <p className="text-sm text-zinc-400 mb-4">
                  Join this path to track your progress and unlock lessons.
                </p>
                <Button
                  onClick={handleEnroll}
                  isLoading={enrolling}
                  fullWidth
                  size="lg"
                >
                  Enroll Now
                </Button>
              </div>
            ) : (
              <div>
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-zinc-400 font-medium">
                    Path Progress
                  </span>
                  <span className="text-white font-bold">
                    {path.student_progress.completed_tasks} / {path.total_tasks}
                  </span>
                </div>
                <div className="w-full bg-zinc-900 rounded-full h-2.5 overflow-hidden mb-4 border border-zinc-800">
                  <div
                    className="bg-primary h-2.5 rounded-full transition-all duration-700"
                    style={{
                      width: `${path.total_tasks > 0 ? (path.student_progress.completed_tasks / path.total_tasks) * 100 : 0}%`,
                    }}
                  />
                </div>
                {path.student_progress.completed_tasks === path.total_tasks ? (
                  <div className="flex items-center justify-center gap-2 text-success font-medium bg-success/10 py-2 rounded-lg border border-success/20">
                    <CheckCircle className="h-5 w-5" /> Path Completed
                  </div>
                ) : (
                  <Button
                    fullWidth
                    variant="outline"
                    className="border-primary/50 text-primary hover:bg-primary/10"
                  >
                    Resume Curriculum
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Curriculum Accordion */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          Curriculum Sequence
        </h2>

        <div className="space-y-4">
          {path.modules?.map((module, mIndex) => {
            const isExpanded = expandedModules[module.id];

            return (
              <Card
                key={module.id}
                className="overflow-hidden bg-transparent border-zinc-800"
              >
                <button
                  onClick={() => toggleModule(module.id)}
                  className="w-full flex items-center justify-between p-4 sm:p-6 bg-zinc-900/50 hover:bg-zinc-900 transition-colors text-left focus:outline-none"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 shrink-0 rounded-full bg-zinc-950 border border-zinc-800 flex items-center justify-center font-mono font-bold text-zinc-500">
                      {mIndex + 1}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        {module.title}
                      </h3>
                      <p className="text-sm text-zinc-400 mt-0.5 line-clamp-1">
                        {module.description}
                      </p>
                    </div>
                  </div>
                  <div className="shrink-0 text-zinc-500 ml-4">
                    {isExpanded ? (
                      <ChevronDown className="h-6 w-6" />
                    ) : (
                      <ChevronRight className="h-6 w-6" />
                    )}
                  </div>
                </button>

                {isExpanded && (
                  <div className="border-t border-zinc-800 bg-black/20 p-4 sm:p-6">
                    <div className="space-y-3 pl-2 sm:pl-6 border-l-2 border-zinc-800 ml-4">
                      {module.lessons?.map((lesson, lIndex) => {
                        // In a real app we'd map tasks to completions here.
                        // For styling purposes, let's assume if enrolled and task is completed (which we don't have direct mapping for in this payload without eager loading),
                        // but we'll just style them generally as locked/playable

                        return (
                          <div
                            key={lesson.id}
                            className="relative pl-6 sm:pl-8 py-3 group"
                          >
                            {/* Timeline dot */}
                            <div className="absolute left-[-5px] top-[20px] h-2 w-2 rounded-full bg-zinc-600 group-hover:bg-primary transition-colors" />

                            <div
                              className={cn(
                                "bg-zinc-900/80 border border-zinc-800/80 rounded-xl p-4 transition-all",
                                isEnrolled
                                  ? "hover:border-primary/50 hover:bg-zinc-900"
                                  : "opacity-80",
                              )}
                            >
                              <div className="flex items-start justify-between gap-4">
                                <div>
                                  <h4 className="text-base font-semibold text-zinc-200 mb-1">
                                    Lesson {mIndex + 1}.{lIndex + 1}:{" "}
                                    {lesson.title}
                                  </h4>
                                  <p className="text-sm text-zinc-400 mb-4">
                                    {lesson.content}
                                  </p>

                                  {lesson.tasks && lesson.tasks.length > 0 && (
                                    <div className="space-y-2 mt-4">
                                      {lesson.tasks.map((task) => (
                                        <div
                                          key={task.id}
                                          className="flex items-center gap-3"
                                        >
                                          {isEnrolled ? (
                                            <Link
                                              to={`/tasks/${task.slug}`}
                                              className="flex items-center gap-2 text-sm text-primary hover:underline group/link"
                                            >
                                              <PlayCircle className="h-4 w-4" />
                                              <span>{task.title}</span>
                                              <span className="text-xs text-zinc-500 font-mono ml-2 opacity-0 group-hover/link:opacity-100 transition-opacity">
                                                (+{task.xp_reward} XP)
                                              </span>
                                            </Link>
                                          ) : (
                                            <span className="flex items-center gap-2 text-sm text-zinc-500">
                                              <Lock className="h-3.5 w-3.5" />{" "}
                                              {task.title}
                                            </span>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                      {(!module.lessons || module.lessons.length === 0) && (
                        <div className="pl-8 text-sm text-zinc-500 italic py-4">
                          No content in this module yet.
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}

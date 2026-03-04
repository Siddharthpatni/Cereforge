import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { AIMentorPanel } from "@/components/tasks/AIMentorPanel";
import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import apiClient from "@/api/client";
import { ArrowLeft, CheckCircle, Flame, Send, Clock } from "lucide-react";
import { BenchmarkModal } from "@/components/ui/BenchmarkModal";

export function TaskDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { addToast, queueCinematic } = useUIStore();


  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);

  // Submission state
  const [solutionRaw, setSolutionRaw] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [isInvalidating, setIsInvalidating] = useState(false);
  const [localError, setLocalError] = useState("");

  // Benchmark Modal State
  const [showBenchmark, setShowBenchmark] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState(null);

  useEffect(() => {
    let isMounted = true;
    console.log("Cereforge System: Rendering Task Detail API payload.");

    const fetchTaskData = async () => {
      try {
        const resTask = await apiClient.get(`/tasks/${slug}`);
        if (isMounted) setTask(resTask.data);

        // Try to fetch existing submission
        try {
          const resSub = await apiClient.get(`/tasks/${slug}/submissions`);
          if (resSub.data && resSub.data.solution_text && isMounted) {
            setSolutionRaw(resSub.data.solution_text);
          }
        } catch {
          // If 404 or no submission, ignore
        }
      } catch {
        if (isMounted) {
          addToast({
            title: "Error",
            message: "Failed to load task",
            type: "error",
          });
          navigate("/tasks");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchTaskData();
    return () => { isMounted = false; };
  }, [slug, navigate, addToast]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!solutionRaw.trim()) return;

    setSubmitting(true);
    setLocalError("");
    try {
      const res = await apiClient.post(`/tasks/${slug}/submit`, {
        solution_text: solutionRaw,
      });

      setSubmitting(false); // Stop the submit spinner immediately

      // Show Benchmark Modal instead of immediately updating
      setBenchmarkResult(res.data);
      setShowBenchmark(true);

    } catch (error) {
      let msg = "Something went wrong.";
      const detail = error.response?.data?.detail;

      if (typeof detail === "string") {
        msg = detail;
      } else if (Array.isArray(detail)) {
        msg = detail.map(d => `${d.field}: ${d.message}`).join(", ");
      } else if (detail && typeof detail === "object") {
        msg = JSON.stringify(detail);
      }

      setLocalError(msg);
      addToast({
        title: "Submission Failed",
        message: msg.length > 100 ? msg.substring(0, 97) + "..." : msg,
        type: "error",
      });
      setIsInvalidating(false);
      setSubmitting(false);
    }
  };

  const handleBenchmarkContinue = async () => {
    if (!benchmarkResult) return;

    setShowBenchmark(false);
    setIsInvalidating(true);

    try {
      // 1. Invalidate React Query caches
      await queryClient.invalidateQueries(['task', slug]);
      await queryClient.invalidateQueries(['dashboard']);
      await queryClient.invalidateQueries(['paths']);

      // 2. Local state update
      setTask((prev) => ({ ...prev, is_completed: true }));
      // Sync XP and Rank to authStore so Navbar reflects changes immediately
      const { setUser } = useAuthStore.getState();
      setUser({ xp: benchmarkResult.total_xp }, benchmarkResult.rank);

      addToast({
        title: "Task Completed!",
        message: `Excellent work. You earned ${benchmarkResult.xp_earned} XP.`,
        type: "success",
      });

      // 3. Queue animations for badges unlocked (if any)
      if (benchmarkResult.newly_earned_badges && benchmarkResult.newly_earned_badges.length > 0) {
        benchmarkResult.newly_earned_badges.forEach((badge) => {
          queueCinematic({
            name: badge.name,
            description: "You've proven your skills. Keep building.",
            xp_bonus: badge.xp_bonus,
            track_color: "var(--accent-llm)",
            icon: badge.icon || "🏆",
          });
        });
      }
    } finally {
      setIsInvalidating(false);
      setSubmitting(false);
    }
  };

  if (loading || isInvalidating)
    return (
      <div className="p-12 text-center text-primary flex items-center justify-center min-h-[50vh]">
        <div className="animate-pulse flex flex-col items-center">
          <span className="text-4xl mb-4">🧠</span>
          <span>{loading ? "Initializing Environment..." : "Syncing Profile..."}</span>
        </div>
      </div>
    );
  if (!task) return null;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header Bar */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/tasks")}
          className="text-zinc-400 hover:text-white px-2"
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Back
        </Button>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col: Task Info & Guide */}
        <div className="lg:col-span-2 space-y-6">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <Badge variant={task.track}>{task.track.toUpperCase()}</Badge>
              <span className="text-sm font-medium text-zinc-500 capitalize">
                {task.difficulty}
              </span>
              {task.is_completed && (
                <span className="flex items-center gap-1 text-success text-xs font-semibold bg-success/10 px-2 py-1 rounded-full border border-success/20">
                  <CheckCircle className="h-3.5 w-3.5" /> Completed
                </span>
              )}
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">{task.title}</h1>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-4 text-sm text-primary font-mono bg-primary/10 inline-flex px-3 py-1 rounded-md border border-primary/20">
                <Flame className="h-4 w-4" /> Reward: {task.xp_reward} XP
              </div>
              {(() => {
                const text = [task.description, task.beginner_guide, task.hint].filter(Boolean).join(" ");
                const words = text.split(/\s+/).length;
                const mins = Math.max(1, Math.round(words / 200));
                return (
                  <div className="flex items-center gap-1.5 text-sm text-zinc-400 bg-zinc-800/60 px-3 py-1 rounded-md border border-zinc-700/50">
                    <Clock className="h-3.5 w-3.5" />
                    ~{mins} min read
                  </div>
                );
              })()}
            </div>
          </div>

          <Card className="glass-panel">
            <CardContent className="p-6 md:p-8 prose prose-invert max-w-none">
              <div className="mb-8">
                <h3 className="text-xl font-bold text-white mb-4" style={{ marginTop: 0 }}>Objective</h3>
                <div
                  dangerouslySetInnerHTML={{
                    __html: task.description
                      ?.replace(/\n\n/g, "<br/><br/>")
                      ?.replace(/`([^`]+)`/g, "<code>$1</code>") || "No description provided.",
                  }}
                />
              </div>

              {task.show_beginner_guide && task.beginner_guide && (
                <div className="mt-8 pt-8 border-t border-border/50">
                  <h3 className="text-lg font-bold text-white mb-4">Beginner Guide</h3>
                  <div
                    dangerouslySetInnerHTML={{
                      __html: task.beginner_guide
                        .replace(/\n\n/g, "<br/><br/>")
                        .replace(/### (.*?)\n/g, "<h3>$1</h3>")
                        .replace(/`([^`]+)`/g, "<code>$1</code>"),
                    }}
                  />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Submission Form */}
          <Card
            id="submit"
            className={
              task.is_completed ? "border-success/30 bg-success/5" : ""
            }
          >
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                {task.is_completed
                  ? "Submission Accepted"
                  : "Submit Your Solution"}
              </h3>

              {task.is_completed && (
                <div className="flex items-center gap-3 text-success mb-6 bg-success/10 p-4 border border-success/20 rounded-lg">
                  <CheckCircle className="h-5 w-5" />
                  <p className="text-sm font-medium">You have already completed this task and earned full XP. You can resubmit to improve your code benchmark score!</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                {localError && (
                  <div className="p-3 mb-2 text-sm text-red-400 bg-red-900/20 border border-red-900/50 rounded-lg flex items-start gap-2">
                    <div className="mt-0.5 font-bold">!</div>
                    <div>{localError}</div>
                  </div>
                )}
                <p className="text-sm text-zinc-400 mb-2">
                  Paste your code, Colab link, or GitHub Gist URL below.
                </p>
                <textarea
                  value={solutionRaw}
                  onChange={(e) => setSolutionRaw(e.target.value)}
                  required
                  rows={4}
                  className="w-full bg-input border border-border rounded-lg p-3 text-sm text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-mono"
                  placeholder="https://github.com/...&#10;OR&#10;def my_agent(): ..."
                />
                <div className="flex justify-end">
                  <Button
                    type="submit"
                    isLoading={submitting}
                    className="min-w-[120px]"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    {task.is_completed ? "Update Solution" : "Submit Code"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Right Col: AI Mentor Panel */}
        <div className="space-y-6">
          <div className="sticky top-20">
            <AIMentorPanel taskSlug={task.slug} />
          </div>
        </div>
      </div>

      <BenchmarkModal
        isOpen={showBenchmark}
        onClose={() => setShowBenchmark(false)}
        benchmarks={benchmarkResult?.benchmarks}
        xpEarned={benchmarkResult?.xp_earned}
        onContinue={handleBenchmarkContinue}
      />
    </div>
  );
}

import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Badge } from "@/components/ui/Badge";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { AIMentorPanel } from "@/components/tasks/AIMentorPanel";
import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import apiClient from "@/api/client";
import { ArrowLeft, CheckCircle, Flame, Send } from "lucide-react";

export function TaskDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { addToast, queueCinematic } = useUIStore();
  const { updateXP } = useAuthStore();

  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);

  // Submission state
  const [solutionRaw, setSolutionRaw] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    apiClient
      .get(`/tasks/${slug}`)
      .then((res) => setTask(res.data))
      .catch((err) => {
        addToast({
          title: "Error",
          message: "Failed to load task",
          type: "error",
        });
        navigate("/tasks");
      })
      .finally(() => setLoading(false));
  }, [slug, navigate, addToast]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!solutionRaw.trim()) return;

    setSubmitting(true);
    try {
      const res = await apiClient.post(`/tasks/${task.id}/submit`, {
        solution_raw: solutionRaw,
      });

      // Update local state and XP store
      setTask((prev) => ({ ...prev, is_completed: true }));
      updateXP(res.data.xp_awarded);

      addToast({
        title: "Task Completed!",
        message: `Excellent work. You earned ${res.data.xp_awarded} XP.`,
        type: "success",
      });

      // Queue animations for badges unlocked (if any)
      if (res.data.badges_unlocked && res.data.badges_unlocked.length > 0) {
        res.data.badges_unlocked.forEach((badge) => {
          // Simple stub data structure for the Cinematic queue
          queueCinematic({
            name: badge.name, // the API just returns string IDs unfortunately in this quick version, but assume it returns full object or we fetch it
            description: "You've proven your skills. Keep building.",
            xp_bonus: 50, // Hardcoded stub
            track_color: "var(--accent-llm)",
            icon: "🏆",
          });
        });
      }
    } catch (err) {
      addToast({
        title: "Submission Failed",
        message: err.response?.data?.detail || "Something went wrong.",
        type: "error",
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading)
    return (
      <div className="p-12 text-center text-primary animate-pulse">
        Initializing Environment...
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
            <div className="flex items-center gap-4 text-sm text-primary font-mono bg-primary/10 inline-flex px-3 py-1 rounded-md border border-primary/20">
              <Flame className="h-4 w-4" /> Reward: {task.xp_reward} XP
            </div>
          </div>

          <Card className="glass-panel">
            <CardContent className="p-6 md:p-8 prose prose-invert max-w-none">
              <div
                dangerouslySetInnerHTML={{
                  __html: task.beginner_guide
                    .replace(/\n\n/g, "<br/><br/>")
                    .replace(/### (.*?)\n/g, "<h3>$1</h3>")
                    .replace(/`([^`]+)`/g, "<code>$1</code>"),
                }}
              />
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

              {task.is_completed ? (
                <div className="flex items-center gap-3 text-success">
                  <CheckCircle className="h-6 w-6" />
                  <p>You have already completed this task and earned the XP.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
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
                      <Send className="h-4 w-4 mr-2" /> Submit Code
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Col: AI Mentor Panel */}
        <div className="space-y-6">
          <div className="sticky top-20">
            <AIMentorPanel taskId={task.id} />
          </div>
        </div>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MessageSquare,
  ChevronUp,
  CheckCircle,
  Plus,
  Search,
  Tag as TagIcon,
  Zap,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Modal } from "@/components/ui/Modal";
import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import apiClient from "@/api/client";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/utils/cn";
import { extractErrorMessage } from "@/utils/errorUtils";

const TRACKS = ["llm", "rag", "vision", "agents"];

export function Community() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState("");
  const [tagFilter, setTagFilter] = useState("");
  const [trackFilter, setTrackFilter] = useState("all");
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);

  // Ask Question Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newContent, setNewContent] = useState("");
  const [newTags, setNewTags] = useState("");
  const [newTrack, setNewTrack] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState("");

  const { addToast } = useUIStore();
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (tagFilter) params.append("tag", tagFilter);
      if (search) params.append("search", search);
      if (bookmarkedOnly) params.append("bookmarked_only", "true");
      if (trackFilter !== "all") params.append("track", trackFilter);

      const res = await apiClient.get(`/posts?${params.toString()}`);
      setPosts(res.data.items || res.data);
      setError(false);
    } catch (err) {
      console.error(err);
      setError(true);
      addToast({ title: "Error", message: "Failed to load community posts", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tagFilter, bookmarkedOnly, trackFilter]);

  const handleVote = async (postId, value) => {
    if (!user) {
      addToast({ title: "Sign in required", message: "You must be signed in to vote.", type: "warning" });
      return;
    }
    try {
      await apiClient.post("/vote", { target_id: postId, target_type: "post", value });
      fetchPosts();
    } catch (err) {
      addToast({
        title: "Vote Failed",
        message: extractErrorMessage(err, "Could not cast vote."),
        type: "warning",
      });
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!newTitle.trim() || !newContent.trim()) return;

    setSubmitting(true);
    setLocalError("");
    try {
      const tagsArray = newTags.split(",").map((t) => t.trim()).filter(Boolean);
      const res = await apiClient.post("/posts", {
        title: newTitle,
        body: newContent,
        tags: tagsArray,
        ...(newTrack && { track: newTrack }),
      });

      addToast({ title: "Success", message: "Question posted successfully.", type: "success" });
      setIsModalOpen(false);
      setNewTitle("");
      setNewContent("");
      setNewTags("");
      setNewTrack("");
      navigate(`/community/${res.data.post.id}`);
    } catch (err) {
      const errorMsg = extractErrorMessage(err, "Failed to post question. Please try again.");
      setLocalError(errorMsg);
      addToast({ title: "Error", message: errorMsg, type: "error" });
    } finally {
      setSubmitting(false);
    }
  };

  const filteredPosts = posts.filter(
    (p) =>
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.tags?.some((t) => t.toLowerCase().includes(search.toLowerCase())),
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Community</h1>
          <p className="text-zinc-400 mt-1">
            Discuss AI challenges, share solutions, and help fellow engineers.
          </p>
        </div>
        <Button
          onClick={() => setIsModalOpen(true)}
          className="shrink-0 bg-primary/20 text-primary hover:bg-primary border border-primary/30 hover:border-primary hover:text-white transition-all"
        >
          <Plus className="h-4 w-4 mr-2" /> Ask Question
        </Button>
      </div>

      {/* Track Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setTrackFilter("all")}
          className={cn(
            "px-3 py-1 text-xs font-semibold rounded-full border transition-colors",
            trackFilter === "all"
              ? "bg-secondary text-white border-zinc-600"
              : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
          )}
        >
          All Tracks
        </button>
        {TRACKS.map((track) => (
          <button
            key={track}
            onClick={() => setTrackFilter(track)}
            className={cn(
              "px-3 py-1 text-xs font-semibold rounded-full border transition-colors uppercase",
              trackFilter === track
                ? "bg-primary/20 text-primary border-primary/40"
                : "bg-transparent text-zinc-400 border-transparent hover:bg-zinc-800",
            )}
          >
            {track}
          </button>
        ))}
      </div>

      {/* Search/Tag Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between bg-card p-4 rounded-xl border border-border">
        <div className="relative w-full md:flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Search discussions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchPosts()}
            className="w-full bg-input border border-border pl-10 pr-4 py-2 rounded-lg text-sm text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
          />
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <TagIcon className="h-4 w-4 text-zinc-500" />
          <input
            type="text"
            placeholder="Filter by tag..."
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value)}
            className="w-full md:w-40 bg-input border border-border px-3 py-2 rounded-lg text-sm text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
          />
          <Button
            variant={bookmarkedOnly ? "default" : "outline"}
            size="sm"
            onClick={() => setBookmarkedOnly(!bookmarkedOnly)}
            className={
              bookmarkedOnly
                ? "bg-amber-500 hover:bg-amber-600 text-white border-amber-500 h-[38px]"
                : "border-border text-zinc-400 hover:text-white h-[38px]"
            }
          >
            <Star className={cn("h-4 w-4 mr-1.5", bookmarkedOnly && "fill-current")} />
            Favorites
          </Button>
        </div>
      </div>

      {/* Post List */}
      <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
        {error ? (
          <div className="p-12 text-center text-red-500">
            <p>Could not load posts. Try again.</p>
            <Button onClick={fetchPosts} variant="outline" className="mt-4">Retry</Button>
          </div>
        ) : loading ? (
          <div className="divide-y divide-border/50">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 sm:p-6 flex gap-4 animate-pulse">
                <div className="w-8 h-12 bg-zinc-800 rounded shrink-0"></div>
                <div className="flex-1 space-y-3">
                  <div className="h-5 bg-zinc-800 rounded w-3/4"></div>
                  <div className="h-4 bg-zinc-800 rounded w-full"></div>
                  <div className="h-3 bg-zinc-800 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : posts.length === 0 ? (
          <div className="p-12 text-center text-zinc-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-20" />
            <p className="mb-4">No community posts yet. Be the first to start a discussion!</p>
            <Button onClick={() => setIsModalOpen(true)}>Ask the First Question</Button>
          </div>
        ) : filteredPosts.length > 0 ? (
          <div className="divide-y divide-border/50">
            {filteredPosts.map((post) => (
              <div
                key={post.id}
                className="p-4 sm:p-6 hover:bg-zinc-900/40 transition-colors flex gap-4"
              >
                {/* Vote Counter — connected */}
                <div className="flex flex-col items-center shrink-0">
                  <button
                    onClick={() => handleVote(post.id, 1)}
                    className="text-zinc-400 hover:text-success cursor-pointer mb-1 transition-colors"
                    title="Upvote"
                  >
                    <ChevronUp className="h-6 w-6" />
                  </button>
                  <span className="font-mono font-bold text-white px-2">
                    {post.vote_score ?? 0}
                  </span>
                </div>

                {/* Post Info */}
                <div className="flex-1 min-w-0">
                  <Link to={`/community/${post.id}`} className="block">
                    <h3 className="text-lg font-semibold text-white hover:text-primary transition-colors line-clamp-2">
                      {post.status === "solved" && (
                        <CheckCircle
                          className="inline-block h-4 w-4 text-success mr-2 mb-1"
                          title="Solved"
                        />
                      )}
                      {post.title}
                    </h3>
                  </Link>
                  <p className="text-sm text-zinc-400 mt-1 line-clamp-1">
                    {post.body || ""}
                  </p>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-3">
                    <div className="flex items-center gap-1.5 text-xs">
                      {post.tags?.map((tag) => (
                        <Badge
                          key={tag}
                          variant="outline"
                          className="text-[10px] px-1.5 py-0 border-zinc-700 text-zinc-300"
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex items-center gap-4 text-xs text-zinc-500 ml-auto">
                      <span className="flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" /> {post.comment_count ?? 0}
                      </span>
                      <span>
                        By{" "}
                        <span className="text-zinc-300 font-medium">
                          {post.author?.username || "Unknown"}
                        </span>
                      </span>
                      <span>{formatDistanceToNow(new Date(post.created_at))} ago</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-zinc-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-20" />
            <p>No discussions found.</p>
            {(search || tagFilter || trackFilter !== "all") && (
              <Button
                variant="ghost"
                className="mt-4"
                onClick={() => {
                  setSearch("");
                  setTagFilter("");
                  setTrackFilter("all");
                }}
              >
                Clear Filters
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Ask Question Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Ask the Community">
        <form onSubmit={handleCreatePost} className="space-y-4">
          {localError && (
            <div className="p-3 mb-2 text-sm text-red-400 bg-red-900/20 border border-red-900/50 rounded-lg flex items-start gap-2">
              <div className="mt-0.5 font-bold">!</div>
              <div>{localError}</div>
            </div>
          )}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-300">Title</label>
            <input
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              className="w-full bg-input border border-border rounded-lg p-2.5 text-sm text-foreground focus:outline-none focus:border-primary"
              placeholder="E.g., How do I approach the reinforcement learning challenge?"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-300">Details</label>
            <textarea
              required
              rows={6}
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              className="w-full bg-input border border-border rounded-lg p-2.5 text-sm text-foreground focus:outline-none focus:border-primary resize-y"
              placeholder="Provide context, what you've tried, and any code blocks..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-zinc-300">
                Tags <span className="text-zinc-500 font-normal">(comma separated)</span>
              </label>
              <input
                value={newTags}
                onChange={(e) => setNewTags(e.target.value)}
                className="w-full bg-input border border-border rounded-lg p-2.5 text-sm text-foreground focus:outline-none focus:border-primary"
                placeholder="python, RL, dqn"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-zinc-300">
                Track <span className="text-zinc-500 font-normal">(optional)</span>
              </label>
              <select
                value={newTrack}
                onChange={(e) => setNewTrack(e.target.value)}
                className="w-full bg-input border border-border rounded-lg p-2.5 text-sm text-foreground focus:outline-none focus:border-primary"
              >
                <option value="">General</option>
                {TRACKS.map((t) => (
                  <option key={t} value={t}>{t.toUpperCase()}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-border mt-6">
            <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={submitting}>
              Post Question
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

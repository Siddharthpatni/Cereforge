import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  MessageSquare,
  ChevronUp,
  ChevronDown,
  CheckCircle,
  ArrowLeft,
  Sparkles,
  Trash2,
  Star,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { useUIStore } from "@/stores/uiStore";
import { useAuthStore } from "@/stores/authStore";
import apiClient from "@/api/client";
import { formatDistanceToNow } from "date-fns";
import { cn } from "@/utils/cn";

// Extract a human-readable string from whatever shape the API returns for errors.
// The backend can return: a plain string, or an array [{field, message, type}, ...] for 422s.
function extractErrorMessage(err, fallback = "Something went wrong") {
  const detail = err?.response?.data?.detail;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.message || d.msg || JSON.stringify(d)).join(", ");
  }
  return fallback;
}

// Subcomponent for comments tree
function CommentNode({ comment, postAuthorId, onVote, onAccept, onReply }) {
  const { user } = useAuthStore();
  const [showReplyBox, setShowReplyBox] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState("");

  const handleReplySubmit = async (e) => {
    e.preventDefault();
    if (!replyText.trim()) return;
    setSubmitting(true);
    setLocalError("");
    try {
      await onReply(comment.id, replyText);
      setReplyText("");
      setShowReplyBox(false);
    } catch (err) {
      setLocalError(extractErrorMessage(err, "Failed to post reply"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className={cn(
        "flex flex-col gap-2 mt-4",
        comment.parent_id ? "pl-6 sm:pl-10 border-l border-border/50" : "",
      )}
    >
      <div
        className={cn(
          "flex gap-4 p-4 rounded-xl border transition-colors",
          comment.is_accepted
            ? "bg-success/5 border-success/30"
            : "bg-zinc-900/30 border-border/50",
        )}
      >
        {/* Voting */}
        <div className="flex flex-col items-center shrink-0">
          <button
            onClick={() => onVote(comment.id, 1, "comment")}
            className="text-zinc-500 hover:text-success focus:outline-none"
          >
            <ChevronUp className="h-5 w-5" />
          </button>
          <span className="font-mono text-sm font-bold text-white py-1">
            {comment.vote_score}
          </span>
          <button
            onClick={() => onVote(comment.id, -1, "comment")}
            className="text-zinc-500 hover:text-danger focus:outline-none"
          >
            <ChevronDown className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-bold font-mono">
                {comment.author?.username?.charAt(0)?.toUpperCase()}
              </div>
              <span className="text-sm font-medium text-white">
                {comment.author?.username}
              </span>
              {comment.author_id === postAuthorId && (
                <Badge
                  variant="outline"
                  className="text-[9px] py-0 px-1 border-primary/50 text-primary"
                >
                  OP
                </Badge>
              )}
              <span className="text-xs text-zinc-500">
                • {formatDistanceToNow(new Date(comment.created_at))} ago
              </span>
            </div>
            {comment.is_accepted && (
              <span className="flex items-center gap-1 text-success text-xs font-bold">
                <CheckCircle className="h-4 w-4" /> Accepted Answer
              </span>
            )}
          </div>

          <div
            className="prose prose-sm prose-invert max-w-none text-zinc-300"
            dangerouslySetInnerHTML={{
              __html: (comment.body || "")
                .replace(/\n\n/g, "<br/><br/>")
                .replace(/`([^`]+)`/g, "<code>$1</code>"),
            }}
          />

          {/* Actions */}
          <div className="flex items-center gap-3 mt-3">
            <button
              onClick={() => setShowReplyBox(!showReplyBox)}
              className="text-xs font-medium text-zinc-400 hover:text-white transition-colors"
            >
              Reply
            </button>
            {user?.id === postAuthorId && !comment.is_accepted && (
              <button
                onClick={() => onAccept(comment.id)}
                className="text-xs font-medium text-success/70 hover:text-success transition-colors flex items-center gap-1"
              >
                <CheckCircle className="h-3 w-3" /> Mark as Answer
              </button>
            )}
          </div>

          {/* Reply Form */}
          {showReplyBox && (
            <form onSubmit={handleReplySubmit} className="mt-3 relative">
              {localError && (
                <div className="p-2 mb-2 text-xs text-red-400 bg-red-900/20 border border-red-900/50 rounded flex items-start gap-2">
                  <div className="font-bold">!</div>
                  <div>{localError}</div>
                </div>
              )}
              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                required
                rows={2}
                placeholder="Write your reply..."
                className="w-full bg-input border border-border rounded-lg p-2.5 pr-20 text-sm text-foreground focus:outline-none focus:border-primary"
              />
              <Button
                type="submit"
                size="sm"
                isLoading={submitting}
                className="absolute right-2 bottom-3"
              >
                Submit
              </Button>
            </form>
          )}
        </div>
      </div>

      {/* Render children recursively */}
      {comment.replies &&
        comment.replies.map((reply) => (
          <CommentNode
            key={reply.id}
            comment={reply}
            postAuthorId={postAuthorId}
            onVote={onVote}
            onAccept={onAccept}
            onReply={onReply}
          />
        ))}
    </div>
  );
}

export function PostDetail() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const { addToast } = useUIStore();
  const { user } = useAuthStore();

  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);

  // New Comment State
  const [newComment, setNewComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [localError, setLocalError] = useState("");

  // AI Summary
  const [aiSummary, setAiSummary] = useState(null);
  const [summarizing, setSummarizing] = useState(false);

  const fetchPost = async () => {
    try {
      const res = await apiClient.get(`/posts/${postId}`);
      setPost({ ...res.data.post, comments: res.data.comments });
    } catch {
      addToast({
        title: "Error",
        message: "Discussion not found",
        type: "error",
      });
      navigate("/community");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPost();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [postId]);

  const handleVote = async (id, value, targetType = "post") => {
    try {
      await apiClient.post("/vote", {
        target_id: id,
        target_type: targetType,
        value: value,
      });

      // Optimistic update would go here for a production app
      // For simplicity, just refetch
      fetchPost();
    } catch (error) {
      addToast({
        title: "Vote Failed",
        message: error.response?.data?.detail || "Try again.",
        type: "warning",
      });
    }
  };

  const handleAcceptAnswer = async (commentId) => {
    try {
      await apiClient.post(`/posts/${postId}/comments/${commentId}/accept`);
      addToast({
        title: "Answer Accepted",
        message: "You have rewarded the author with XP.",
        type: "success",
      });
      fetchPost();
    } catch {
      addToast({
        title: "Error",
        message: "Failed to accept answer",
        type: "error",
      });
    }
  };

  const handleDeletePost = async () => {
    if (!window.confirm("Are you sure you want to delete this post?")) return;
    try {
      await apiClient.delete(`/posts/${postId}`);
      addToast({
        title: "Deleted",
        message: "Post has been deleted.",
        type: "success",
      });
      navigate("/community");
    } catch (err) {
      addToast({
        title: "Delete Failed",
        message: err.response?.data?.detail || "Could not delete post.",
        type: "error",
      });
    }
  };

  const handleBookmarkPost = async () => {
    try {
      const res = await apiClient.post(`/posts/${postId}/bookmark`);
      addToast({
        title: res.data.bookmarked ? "Bookmarked" : "Bookmark Removed",
        message: res.data.bookmarked
          ? "Saved to your favorites."
          : "Removed from favorites.",
        type: "success",
      });
      fetchPost();
    } catch (err) {
      addToast({
        title: "Error",
        message: err.response?.data?.detail || "Could not toggle bookmark.",
        type: "error",
      });
    }
  };

  const handlePostComment = async (parentId, content) => {
    try {
      await apiClient.post(`/posts/${postId}/comments`, {
        body: content,
        parent_id: parentId,
      });
      addToast({
        title: "Posted",
        message: "Your comment was posted.",
        type: "success",
      });
      fetchPost();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to post comment";
      addToast({
        title: "Error",
        message: msg,
        type: "error",
      });
      throw err;
    }
  };

  const submitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setSubmitting(true);
    setLocalError("");
    try {
      await handlePostComment(null, newComment);
      setNewComment("");
    } catch (err) {
      setLocalError(extractErrorMessage(err, "Failed to post comment"));
    } finally {
      setSubmitting(false);
    }
  };

  const requestAISummary = async () => {
    setSummarizing(true);
    try {
      const res = await apiClient.post("/ai-mentor/community-assist", {
        post_id: postId,
      });
      setAiSummary(res.data.summary || res.data); // depending on backend structure
    } catch {
      addToast({
        title: "AI Unavailable",
        message: "Failed to generate summary.",
        type: "error",
      });
    } finally {
      setSummarizing(false);
    }
  };

  if (loading)
    return (
      <div className="p-12 text-center text-primary animate-pulse">
        Loading Discussion...
      </div>
    );
  if (!post) return null;

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/community")}
          className="text-zinc-400 hover:text-white px-0 hover:bg-transparent -ml-2 mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Community
        </Button>
        <div className="flex items-start justify-between">
          <h1 className="text-3xl font-bold text-white mb-3 tracking-tight">
            {post.is_resolved && (
              <span className="text-success mr-2">[Resolved]</span>
            )}
            {post.title}
          </h1>
          <div className="flex items-center gap-2">
            <Button
              variant={post.is_bookmarked ? "default" : "outline"}
              size="sm"
              onClick={handleBookmarkPost}
              className={
                post.is_bookmarked
                  ? "bg-amber-500 hover:bg-amber-600 text-white border-amber-500"
                  : "border-zinc-700 text-zinc-400 hover:text-white"
              }
            >
              <Star
                className={cn(
                  "h-4 w-4 mr-2",
                  post.is_bookmarked && "fill-current",
                )}
              />
              {post.is_bookmarked ? "Saved" : "Save"}
            </Button>
            {(user?.id === post.author?.id || user?.is_admin) && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDeletePost}
                className="border-red-900/50 text-red-500 hover:bg-red-950/30 hover:text-red-400"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            )}
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-zinc-500 border-b border-border/50 pb-6">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-bold font-mono text-white">
              {post.author?.username?.charAt(0)?.toUpperCase()}
            </div>
            <span className="text-zinc-300 font-medium">
              u/{post.author?.username}
            </span>
          </div>
          <span>•</span>
          <span>
            Posted {formatDistanceToNow(new Date(post.created_at))} ago
          </span>

          {post.tags && post.tags.length > 0 && (
            <>
              <span>•</span>
              <div className="flex items-center gap-1.5">
                {post.tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="outline"
                    className="border-border text-zinc-400 font-normal"
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Main Post Body */}
      <div className="flex gap-4">
        {/* Voting Sidebar */}
        <div className="flex flex-col items-center shrink-0 w-10">
          <button
            onClick={() => handleVote(post.id, 1, "post")}
            className="text-zinc-500 hover:text-success focus:outline-none"
          >
            <ChevronUp className="h-8 w-8" />
          </button>
          <span className="text-lg font-bold text-white py-1">
            {post.vote_score}
          </span>
          <button
            onClick={() => handleVote(post.id, -1, "post")}
            className="text-zinc-500 hover:text-danger focus:outline-none"
          >
            <ChevronDown className="h-8 w-8" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0 bg-transparent rounded-none">
          <div
            className="prose prose-invert max-w-none text-zinc-200"
            dangerouslySetInnerHTML={{
              __html: (post.body || "")
                .replace(/\n\n/g, "<br/><br/>")
                .replace(/`([^`]+)`/g, "<code>$1</code>"),
            }}
          />

          {/* AI Summary Button/Panel */}
          <div className="mt-8 border-t border-border pt-6">
            {!aiSummary ? (
              <Button
                onClick={requestAISummary}
                isLoading={summarizing}
                variant="outline"
                className="border-primary/50 text-primary hover:bg-primary/10"
              >
                <Sparkles className="h-4 w-4 mr-2" /> Request AI Analysis
              </Button>
            ) : (
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-6">
                <h4 className="flex items-center gap-2 text-primary font-bold mb-3">
                  <Sparkles className="h-4 w-4" /> AI Mentor Analysis
                </h4>
                <div
                  className="prose prose-sm prose-invert max-w-none text-zinc-300"
                  // primitive markdown
                  dangerouslySetInnerHTML={{
                    __html:
                      typeof aiSummary === "string"
                        ? aiSummary.replace(
                          /\*\*(.*?)\*\*/g,
                          "<strong>$1</strong>",
                        )
                        : aiSummary.message,
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Comments Section */}
      <div className="mt-12 pt-8 border-t border-border/80">
        <h3 className="text-xl font-bold text-white mb-6">
          {post.comments?.length || 0} Answers & Comments
        </h3>

        {/* Comment Input */}
        <form onSubmit={submitComment} className="mb-10">
          <div className="space-y-2">
            {localError && (
              <div className="p-3 mb-2 text-sm text-red-400 bg-red-900/20 border border-red-900/50 rounded-lg flex items-start gap-2">
                <div className="mt-0.5 font-bold">!</div>
                <div>{localError}</div>
              </div>
            )}
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              required
              rows={4}
              placeholder="Contribute your knowledge to this discussion..."
              className="w-full bg-input border border-border rounded-xl p-4 text-sm text-foreground focus:outline-none focus:border-primary transition-colors resize-y"
            />
            <div className="flex justify-end">
              <Button type="submit" isLoading={submitting}>
                Post Answer
              </Button>
            </div>
          </div>
        </form>

        {/* Comments Tree */}
        <div className="space-y-2">
          {post.comments &&
            post.comments.map((comment) => (
              <CommentNode
                key={comment.id}
                comment={comment}
                postAuthorId={post.author_id}
                onVote={handleVote}
                onAccept={handleAcceptAnswer}
                onReply={handlePostComment}
              />
            ))}
          {(!post.comments || post.comments.length === 0) && (
            <p className="text-center text-zinc-500 py-8 italic bg-zinc-900/20 rounded-xl border border-dashed border-zinc-800">
              No answers yet. Be the first to help out!
            </p>
          )}
        </div>
      </div>
    </div >
  );
}

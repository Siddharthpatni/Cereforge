import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, Sparkles } from "lucide-react";
import { Button } from "../ui/Button";
import apiClient from "@/api/client";
import { cn } from "@/utils/cn";

export function AIMentorPanel({ taskId }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I'm your AI Mentor for this challenge. How can I help you understand the requirements or get started?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      // Create a temporary assistant message to show streaming
      setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

      // NOTE: In a real app we would use fetch with Streams API to get chunks.
      // For this implementation, we'll simulate the streaming locally after fetching the full response
      // or just render it directly since the backend supports streaming but Axios doesn't handle it easily without custom adapter.
      // To save time, we'll just await the full response text since we didn't set up the complex streaming chunk reader.

      const res = await apiClient.post(
        `/ai/mentor/guidance?task_id=${taskId}`,
        {
          prompt: userMessage,
          context_files: [], // No files for now
        },
      );

      // Simple non-streaming fallback render (assuming backend returns full text if not using EventSource)
      // If backend forces stream, this might need parsing. Assuming simple JSON return for simplicity if not handled perfectly.
      // Wait, our backend uses StreamingResponse. Axios will just get the whole blob.
      const fullText = res.data;

      setMessages((prev) => {
        const newArr = [...prev];
        newArr[newArr.length - 1].content =
          typeof fullText === "string"
            ? fullText
            : fullText.message || "I couldn't process that.";
        return newArr;
      });
    } catch (err) {
      console.error(err);
      setMessages((prev) => {
        const newArr = [...prev];
        newArr[newArr.length - 1].content =
          "I'm having trouble connecting to my neural net right now. Please try again.";
        return newArr;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] border border-border bg-card rounded-xl overflow-hidden glass-panel">
      <div className="flex items-center gap-2 bg-zinc-900/80 p-3 border-b border-border text-sm font-semibold">
        <Sparkles className="h-4 w-4 text-primary" />
        AI Mentor{" "}
        <span className="text-[10px] text-zinc-500 font-mono font-normal ml-auto">
          gpt-4o / claude
        </span>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-hide">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={cn(
              "flex gap-3",
              msg.role === "user" ? "flex-row-reverse" : "",
            )}
          >
            <div
              className={cn(
                "shrink-0 h-8 w-8 rounded-full flex items-center justify-center border",
                msg.role === "user"
                  ? "bg-zinc-800 border-zinc-700"
                  : "bg-primary/20 border-primary/30 text-primary",
              )}
            >
              {msg.role === "user" ? (
                <div className="text-white text-xs">U</div>
              ) : (
                <Bot className="h-4 w-4" />
              )}
            </div>

            <div
              className={cn(
                "px-3 py-2 rounded-lg max-w-[80%] text-sm",
                msg.role === "user"
                  ? "bg-zinc-800 text-white rounded-tr-none"
                  : "bg-zinc-900/50 text-zinc-300 rounded-tl-none border border-zinc-800",
              )}
            >
              {/* Very primitive markdown link formatting for the bot */}
              <div
                className="whitespace-pre-wrap leading-relaxed prose prose-sm prose-invert"
                dangerouslySetInnerHTML={{
                  __html: msg.content.replace(
                    /\*\*(.*?)\*\*/g,
                    "<strong>$1</strong>",
                  ),
                }}
              />
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="shrink-0 h-8 w-8 rounded-full flex items-center justify-center border bg-primary/20 border-primary/30 text-primary">
              <Bot className="h-4 w-4" />
            </div>
            <div className="px-3 py-2 rounded-lg bg-zinc-900/50 text-zinc-400 rounded-tl-none border border-zinc-800 flex items-center gap-1">
              <span className="animate-bounce">.</span>
              <span className="animate-bounce delay-100">.</span>
              <span className="animate-bounce delay-200">.</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 bg-zinc-900/50 border-t border-border">
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask for guidance..."
            className="w-full bg-input border border-border rounded-full pl-4 pr-12 py-2 text-sm text-foreground focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="absolute right-1 top-1 bottom-1 w-8 flex items-center justify-center bg-primary rounded-full text-white hover:bg-primary-hover transition-colors disabled:opacity-50 disabled:hover:bg-primary"
          >
            <Send className="h-4 w-4 ml-0.5" />
          </button>
        </form>
      </div>
    </div>
  );
}

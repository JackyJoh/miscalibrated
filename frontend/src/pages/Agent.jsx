/**
 * pages/Agent.jsx — AI agent chat interface.
 *
 * The agent can:
 *   - Explain detected edges ("Why is this market mispriced?")
 *   - Surface relevant news ("What's in the news about Fed rate cuts?")
 *   - Help build strategies ("What edges are open on Kalshi right now?")
 *
 * Responses stream back from POST /api/v1/agent/chat via Server-Sent Events.
 *
 * TODO: Implement SSE streaming reader
 * TODO: Implement tool output rendering (market cards inline in chat)
 * TODO: Add session persistence
 */

import { useState, useRef, useEffect } from "react";

// Placeholder messages for the UI scaffold
const INITIAL_MESSAGES = [
  {
    role: "assistant",
    content: "Hi — I'm your prediction market assistant. Ask me about open markets, recent edges, or related news.",
  },
];

export default function Agent() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);

    // TODO: POST to /api/v1/agent/chat with the full message history
    // TODO: Read the SSE stream and append chunks to the last assistant message
    // Placeholder response:
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Agent streaming not yet implemented. Backend connection pending." },
      ]);
      setIsStreaming(false);
    }, 500);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen max-h-screen">
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="border-b border-white/10 px-6 py-4 bg-[#1a1f3a]">
        <h1 className="font-heading font-bold text-lg text-white tracking-tight">
          Agent
        </h1>
        <p className="text-xs text-slate-500">
          Ask about markets, edges, and news.
        </p>
      </div>

      {/* ── Message Thread ─────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} content={msg.content} />
        ))}
        {/* Streaming indicator */}
        {isStreaming && (
          <div className="flex gap-1 pl-2">
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce"
                style={{ animationDelay: `${i * 150}ms` }}
              />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Input Bar ──────────────────────────────────────────── */}
      <div className="border-t border-white/10 px-6 py-4 bg-[#1a1f3a]">
        <div className="flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about markets, edges, or strategy..."
            rows={1}
            className="flex-1 resize-none bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm
                       placeholder-slate-500 focus:border-cyan-400/50 focus:shadow-[0_0_12px_rgba(34,211,238,0.15)]
                       focus:outline-none transition-all duration-200"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isStreaming}
            className="bg-cyan-500 hover:bg-cyan-600 disabled:opacity-40 disabled:cursor-not-allowed
                       text-white font-heading font-semibold rounded-lg px-5
                       shadow-[0_0_20px_rgba(34,211,238,0.15)] hover:shadow-[0_0_30px_rgba(34,211,238,0.3)]
                       transition-all duration-200 text-sm"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-slate-600 mt-2">Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}

function MessageBubble({ role, content }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-cyan-500/20 border border-cyan-400/30 text-white"
            : "card-glow bg-white/5 border border-white/10 text-slate-300"
        }`}
      >
        {content}
      </div>
    </div>
  );
}

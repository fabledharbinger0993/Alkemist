"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { Bot, Send, Loader2, ChevronDown, ChevronRight } from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  reasoning?: ReasoningStep[];
  timestamp: Date;
}

interface ReasoningStep {
  stage: "awareness" | "literalist" | "congress" | "judge";
  label: string;
  summary: string;
}

interface AIChatSidebarProps {
  projectId: string;
  activeFile?: string;
  activeFileContent?: string;
}

// ─── Reasoning step display ───────────────────────────────────────────────────

function ReasoningSteps({ steps }: { steps: ReasoningStep[] }) {
  const [expanded, setExpanded] = useState(false);

  const stageColors: Record<ReasoningStep["stage"], string> = {
    awareness: "text-blue-400",
    literalist: "text-yellow-400",
    congress: "text-purple-400",
    judge: "text-green-400",
  };

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300"
      >
        {expanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
        Logic Ladder ({steps.length} steps)
      </button>
      {expanded && (
        <div className="mt-1 space-y-1 pl-3 border-l border-surface-600">
          {steps.map((step, i) => (
            <div key={i} className="text-xs">
              <span className={`font-semibold ${stageColors[step.stage]}`}>
                {step.label}:{" "}
              </span>
              <span className="text-gray-400">{step.summary}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Component ────────────────────────────────────────────────────────────────

export function AIChatSidebar({
  projectId,
  activeFile,
  activeFileContent,
}: AIChatSidebarProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [model, setModel] = useState("deepseek-v3.2");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.chat(projectId, {
        message: input,
        model,
        context_file: activeFile,
        context_content: activeFileContent,
      });

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.content,
        reasoning: response.reasoning_steps,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, projectId, model, activeFile, activeFileContent]);

  return (
    <div className="flex flex-col h-full bg-surface-900">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-surface-700">
        <div className="flex items-center gap-2">
          <Bot size={16} className="text-accent-400" />
          <span className="text-sm font-semibold text-gray-200">
            AI Assistant
          </span>
        </div>
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="text-xs bg-surface-800 text-gray-400 border border-surface-600 rounded px-1.5 py-0.5 focus:outline-none focus:border-accent-400"
        >
          <option value="deepseek-v3.2">deepseek-v3.2</option>
          <option value="qwen3:235b-a22b-q4_K_M">qwen3-235b</option>
          <option value="glm4:9b">glm-4</option>
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {messages.length === 0 && (
          <div className="text-xs text-gray-600 text-center mt-8">
            Ask Alkemist anything about your code.
            <br />
            <span className="text-gray-700">
              Uses Sovern Logic Ladder for structured reasoning.
            </span>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`text-sm ${msg.role === "user" ? "text-right" : "text-left"}`}
          >
            <div
              className={`inline-block max-w-full px-3 py-2 rounded-lg text-left whitespace-pre-wrap break-words ${
                msg.role === "user"
                  ? "bg-accent-500 text-white"
                  : "bg-surface-800 text-gray-200"
              }`}
            >
              {msg.content}
            </div>
            {msg.role === "assistant" && msg.reasoning && (
              <ReasoningSteps steps={msg.reasoning} />
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Loader2 size={14} className="animate-spin text-accent-400" />
            <span>Thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-surface-700">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Ask about your code... (Enter to send)"
            rows={3}
            className="flex-1 bg-surface-800 text-sm text-gray-100 px-2 py-1.5 rounded border border-surface-600 focus:outline-none focus:border-accent-400 resize-none placeholder:text-gray-600"
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            className="self-end p-2 bg-accent-500 hover:bg-accent-400 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

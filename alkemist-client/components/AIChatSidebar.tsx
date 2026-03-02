"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { api, type AgentPersona } from "@/lib/api";
import { HoverHint } from "@/components/HoverHint";
import { Bot, Send, Loader2, ChevronDown, ChevronRight, X } from "lucide-react";

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

const PERSONA_LABELS: Record<AgentPersona, string> = {
  visionary: "Visionary",
  engineer: "Engineer",
  contractor: "Contractor",
  finisher: "Finisher",
};

const PERSONA_HINTS: Record<AgentPersona, string> = {
  visionary: "Plans fast app structure and direction in plain language.",
  engineer: "Asks detailed questions and can draft README + contractor handoff.",
  contractor: "Builds quickly with testing loops and execution-focused steps.",
  finisher: "Polishes UX and visual style with consistent, intentional design.",
};

const PERSONA_DEFAULT_MODELS: Record<AgentPersona, string> = {
  visionary: "llama3.2:1b",
  engineer: "qwen2.5-coder:7b",
  contractor: "qwen2.5-coder:7b",
  finisher: "llama3.2:1b",
};

const QUICK_MODELS = [
  "llama3.2:1b",
  "qwen2.5-coder:7b",
  "qwen2.5-coder:14b",
  "deepseek-v3.2",
] as const;

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

export function AIChatSidebar({
  projectId,
  activeFile,
  activeFileContent,
}: AIChatSidebarProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [persona, setPersona] = useState<AgentPersona>("engineer");
  const [modelByPersona, setModelByPersona] = useState<Record<AgentPersona, string>>(
    PERSONA_DEFAULT_MODELS
  );
  const [model, setModel] = useState(PERSONA_DEFAULT_MODELS.engineer);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [isInstallingModel, setIsInstallingModel] = useState(false);
  const [modelInstallMessage, setModelInstallMessage] = useState<string | null>(null);
  const [appIdea, setAppIdea] = useState("");
  const [engineerGenerateReadme, setEngineerGenerateReadme] = useState(true);
  const [engineerGenerateContractorHandoff, setEngineerGenerateContractorHandoff] =
    useState(true);
  const [showOnboardingHint, setShowOnboardingHint] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const quickModelOptions = useMemo(
    () => QUICK_MODELS.filter((m) => availableModels.includes(m)),
    [availableModels]
  );

  const dropdownModels = useMemo(() => {
    if (availableModels.length === 0) {
      return [model];
    }
    return availableModels;
  }, [availableModels, model]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const dismissed = localStorage.getItem("alkemist-chat-onboarding-dismissed");
    if (!dismissed) {
      setShowOnboardingHint(true);
    }
  }, []);

  const refreshModels = useCallback(async () => {
    const { models } = await api.listModels();
    const installed = Array.from(new Set(models.filter(Boolean)));
    setAvailableModels(installed);

    if (installed.length === 0) return;

    setModelByPersona((prev) => {
      const next: Record<AgentPersona, string> = { ...prev };
      (Object.keys(PERSONA_LABELS) as AgentPersona[]).forEach((p) => {
        const preferred = prev[p] ?? PERSONA_DEFAULT_MODELS[p];
        next[p] = installed.includes(preferred) ? preferred : installed[0];
      });
      return next;
    });

    setModel((current) => (installed.includes(current) ? current : installed[0]));
  }, []);

  useEffect(() => {
    refreshModels().catch(() => setAvailableModels([]));
  }, [refreshModels]);

  const dismissOnboarding = useCallback(() => {
    setShowOnboardingHint(false);
    localStorage.setItem("alkemist-chat-onboarding-dismissed", "1");
  }, []);

  const handlePersonaChange = useCallback(
    (nextPersona: AgentPersona) => {
      setPersona(nextPersona);
      const preferred = modelByPersona[nextPersona] ?? PERSONA_DEFAULT_MODELS[nextPersona];
      if (availableModels.length === 0 || availableModels.includes(preferred)) {
        setModel(preferred);
      } else {
        setModel(availableModels[0]);
      }
    },
    [modelByPersona, availableModels]
  );

  const handleModelChange = useCallback(
    (nextModel: string) => {
      setModel(nextModel);
      setModelByPersona((prev) => ({ ...prev, [persona]: nextModel }));
      setModelInstallMessage(null);
    },
    [persona]
  );

  const suggestedModel = PERSONA_DEFAULT_MODELS[persona];
  const suggestedMissing =
    availableModels.length > 0 && !availableModels.includes(suggestedModel);

  const installSuggestedModel = useCallback(async () => {
    if (!suggestedMissing || isInstallingModel) return;
    setIsInstallingModel(true);
    setModelInstallMessage(`Installing ${suggestedModel}...`);
    try {
      const result = await api.installModel(suggestedModel);
      setModelInstallMessage(result.message);
      await refreshModels();
      setModel(suggestedModel);
      setModelByPersona((prev) => ({ ...prev, [persona]: suggestedModel }));
    } catch (err) {
      setModelInstallMessage(
        err instanceof Error ? err.message : "Model install failed"
      );
    } finally {
      setIsInstallingModel(false);
    }
  }, [
    suggestedMissing,
    isInstallingModel,
    suggestedModel,
    refreshModels,
    persona,
  ]);

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
        persona,
        app_idea: appIdea.trim() || undefined,
        engineer_generate_readme:
          persona === "engineer" ? engineerGenerateReadme : false,
        engineer_generate_contractor_handoff:
          persona === "engineer" ? engineerGenerateContractorHandoff : false,
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
  }, [
    input,
    isLoading,
    projectId,
    model,
    activeFile,
    activeFileContent,
    persona,
    appIdea,
    engineerGenerateReadme,
    engineerGenerateContractorHandoff,
  ]);

  return (
    <div className="flex flex-col h-full bg-surface-900">
      <div className="px-3 py-2 border-b border-surface-700 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot size={16} className="text-accent-400" />
            <span className="text-sm font-semibold text-gray-200">AI Assistant</span>
          </div>
          <select
            value={model}
            onChange={(e) => handleModelChange(e.target.value)}
            className="text-xs bg-surface-800 text-gray-400 border border-surface-600 rounded px-1.5 py-0.5 focus:outline-none focus:border-accent-400"
          >
            {dropdownModels.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {(Object.keys(PERSONA_LABELS) as AgentPersona[]).map((key) => (
            <HoverHint key={key} hint={PERSONA_HINTS[key]} side="left">
              <button
                onClick={() => handlePersonaChange(key)}
                className={`rounded px-2 py-1 text-xs transition-colors ${
                  persona === key
                    ? "bg-accent-500 text-white"
                    : "bg-surface-800 text-gray-300 hover:bg-surface-700"
                }`}
              >
                {PERSONA_LABELS[key]}
              </button>
            </HoverHint>
          ))}
        </div>

        <div className="rounded border border-surface-700 bg-surface-800/60 p-2">
          <div className="text-[11px] text-gray-400">Quick models (installed only)</div>
          <div className="mt-1 flex flex-wrap gap-1">
            {quickModelOptions.length === 0 ? (
              <span className="text-[11px] text-gray-500">No suggested models installed yet.</span>
            ) : (
              quickModelOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => handleModelChange(option)}
                  className={`rounded px-2 py-0.5 text-[11px] transition-colors ${
                    model === option
                      ? "bg-accent-500 text-white"
                      : "bg-surface-700 text-gray-300 hover:bg-surface-600"
                  }`}
                >
                  {option}
                </button>
              ))
            )}
          </div>
          <div className="mt-1 text-[11px] text-gray-500">
            Suggested for {PERSONA_LABELS[persona]}: {PERSONA_DEFAULT_MODELS[persona]}
          </div>
          {suggestedMissing && (
            <button
              onClick={installSuggestedModel}
              disabled={isInstallingModel}
              className="mt-1 rounded bg-accent-500 px-2 py-0.5 text-[11px] text-white hover:bg-accent-400 disabled:opacity-50"
            >
              {isInstallingModel ? "Installing..." : `Install ${suggestedModel}`}
            </button>
          )}
          {modelInstallMessage && (
            <div className="mt-1 text-[11px] text-gray-500">{modelInstallMessage}</div>
          )}
        </div>

        <textarea
          value={appIdea}
          onChange={(e) => setAppIdea(e.target.value)}
          rows={2}
          placeholder="App idea (helps agents choose code/tools/profile direction)"
          className="w-full bg-surface-800 text-xs text-gray-100 px-2 py-1.5 rounded border border-surface-600 focus:outline-none focus:border-accent-400 resize-none placeholder:text-gray-600"
        />

        {persona === "engineer" && (
          <div className="space-y-1 rounded border border-surface-700 bg-surface-800/60 p-2">
            <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={engineerGenerateReadme}
                onChange={(e) => setEngineerGenerateReadme(e.target.checked)}
              />
              Draft/update README while asking clarifying questions
            </label>
            <label className="flex items-center gap-2 text-xs text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={engineerGenerateContractorHandoff}
                onChange={(e) =>
                  setEngineerGenerateContractorHandoff(e.target.checked)
                }
              />
              Generate Contractor handoff instructions for fast execution
            </label>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-4">
        {messages.length === 0 && (
          <div className="text-xs text-gray-600 text-center mt-8">
            Ask Alkemist anything about your code.
            <br />
            <span className="text-gray-700">
              Pick any profile at any time — no locked order.
            </span>
          </div>
        )}

        {showOnboardingHint && messages.length === 0 && (
          <div className="rounded border border-surface-600 bg-surface-800/85 p-2 text-xs text-gray-200 backdrop-blur-sm">
            <div className="flex items-start gap-2">
              <div className="flex-1">
                Start with <span className="font-semibold text-accent-300">Visionary</span> for direction,
                then switch freely to Engineer/Contractor/Finisher whenever you want.
              </div>
              <button onClick={dismissOnboarding} className="text-gray-400 hover:text-gray-200">
                <X size={12} />
              </button>
            </div>
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

"use client";

import { useState, useCallback } from "react";
import { api } from "@/lib/api";
import {
  X,
  ChevronRight,
  ChevronLeft,
  CheckCircle,
  Loader2,
  XCircle,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface NewProjectWizardProps {
  onClose: () => void;
  onCreated: (project: {
    id: string;
    name: string;
    language: string;
    root_path: string;
    created_at: string;
  }) => void;
}

interface Template {
  id: string;
  label: string;
  description: string;
  technicalDescription: string;
  icon: string;
  accent: string;
  tags: string[];
}

type WizardStep = "template" | "configure" | "creating";
type OpenClawMode = "copilot" | "observer";

// ─── Template definitions ─────────────────────────────────────────────────────

const TEMPLATES: Template[] = [
  {
    id: "python",
    label: "Python",
    description:
      "Build a game, a website, or the structure behind an app.",
    technicalDescription:
      "FastAPI service scaffold with async endpoints and REST-style routing.",
    icon: "🐍",
    accent: "border-yellow-500 bg-yellow-500/5",
    tags: ["FastAPI", "REST", "async"],
  },
  {
    id: "typescript",
    label: "TypeScript / Node",
    description:
      "Build interactive websites, dashboards, and tools people use in a browser.",
    technicalDescription:
      "Node + Express scaffold with TypeScript strict mode and typed APIs.",
    icon: "🟦",
    accent: "border-blue-500 bg-blue-500/5",
    tags: ["Express", "Node.js", "strict"],
  },
  {
    id: "swift",
    label: "Swift / SwiftUI",
    description:
      "Build iPhone and iPad apps with native Apple look and feel.",
    technicalDescription:
      "SwiftUI app scaffold with App entry point and starter ContentView.",
    icon: "🍎",
    accent: "border-orange-500 bg-orange-500/5",
    tags: ["SwiftUI", "iOS", "App Store"],
  },
  {
    id: "rust",
    label: "Rust",
    description:
      "Build very fast tools, processors, and apps that need to be stable.",
    technicalDescription:
      "Cargo binary scaffold focused on memory safety and high performance.",
    icon: "🦀",
    accent: "border-red-500 bg-red-500/5",
    tags: ["Cargo", "systems", "safe"],
  },
  {
    id: "go",
    label: "Go",
    description:
      "Build backend services and command-line tools that are quick to run.",
    technicalDescription:
      "Go module scaffold using stdlib patterns and simple package layout.",
    icon: "🐹",
    accent: "border-cyan-500 bg-cyan-500/5",
    tags: ["module", "HTTP", "stdlib"],
  },
];

// ─── Log line ─────────────────────────────────────────────────────────────────

interface LogLine {
  id: string;
  message: string;
  type: "info" | "success" | "error";
}

function LogEntry({ line }: { line: LogLine }) {
  const cls =
    line.type === "success"
      ? "text-green-400"
      : line.type === "error"
        ? "text-red-400"
        : "text-gray-400";
  const prefix =
    line.type === "success" ? "✓" : line.type === "error" ? "✗" : "›";
  return (
    <div className={`font-mono text-xs flex gap-2 ${cls}`}>
      <span className="shrink-0">{prefix}</span>
      <span>{line.message}</span>
    </div>
  );
}

// ─── Step indicator ───────────────────────────────────────────────────────────

function StepDots({ step }: { step: WizardStep }) {
  const steps: WizardStep[] = ["template", "configure", "creating"];
  return (
    <div className="flex items-center gap-2">
      {steps.map((s, i) => (
        <div
          key={s}
          className={`rounded-full transition-all duration-200 ${
            s === step
              ? "w-6 h-2 bg-accent-400"
              : steps.indexOf(step) > i
                ? "w-2 h-2 bg-accent-500/60"
                : "w-2 h-2 bg-surface-600"
          }`}
        />
      ))}
    </div>
  );
}

// ─── Template card ────────────────────────────────────────────────────────────

function TemplateCard({
  template,
  selected,
  onSelect,
}: {
  template: Template;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left p-4 rounded-lg border transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-accent-400/50 ${
        selected
          ? `${template.accent} border-opacity-100`
          : "border-surface-600 bg-surface-800 hover:border-surface-500 hover:bg-surface-700"
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl leading-none mt-0.5" aria-hidden="true">
          {template.icon}
        </span>
        <div className="min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-semibold text-gray-100 text-sm">
              {template.label}
            </span>
            {selected && (
              <CheckCircle size={13} className="text-accent-400 shrink-0" />
            )}
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            {template.description}
          </p>
          <p className="mt-1 text-[11px] text-gray-500 leading-relaxed">
            {template.technicalDescription}
          </p>
          <div className="flex flex-wrap gap-1 mt-2">
            {template.tags.map((tag) => (
              <span
                key={tag}
                className="px-1.5 py-0.5 bg-surface-700 text-gray-500 text-[10px] rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </button>
  );
}

// ─── Wizard ───────────────────────────────────────────────────────────────────

export function NewProjectWizard({ onClose, onCreated }: NewProjectWizardProps) {
  const [step, setStep] = useState<WizardStep>("template");
  const [selectedTemplate, setSelectedTemplate] = useState<string>("python");
  const [openclawMode, setOpenclawMode] = useState<OpenClawMode>("observer");
  const [projectName, setProjectName] = useState("");
  const [nameError, setNameError] = useState("");
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [creationStatus, setCreationStatus] =
    useState<"running" | "success" | "error">("running");

  const appendLog = useCallback((message: string, type: LogLine["type"]) => {
    setLogs((prev) => [
      ...prev,
      { id: crypto.randomUUID(), message, type },
    ]);
  }, []);

  // ── Step: template selection ──────────────────────────────────────────────

  const handleTemplateNext = () => {
    setStep("configure");
  };

  // ── Step: configure ───────────────────────────────────────────────────────

  const handleConfigureBack = () => {
    setStep("template");
    setNameError("");
  };

  const handleCreate = async () => {
    const trimmed = projectName.trim();
    if (!trimmed) {
      setNameError("Project name is required.");
      return;
    }
    if (!/^[a-zA-Z0-9_\- ]+$/.test(trimmed)) {
      setNameError(
        "Only letters, numbers, spaces, hyphens and underscores are allowed."
      );
      return;
    }
    setNameError("");
    setStep("creating");
    setCreationStatus("running");

    const template = TEMPLATES.find((t) => t.id === selectedTemplate)!;
    appendLog(`Initialising ${template.label} project "${trimmed}"…`, "info");
    appendLog("Scaffolding template files…", "info");

    try {
      const project = await api.createProject(trimmed, selectedTemplate);
      appendLog("Git repository initialised.", "info");
      appendLog("Project created successfully.", "success");
      setCreationStatus("success");

      // Give the user a brief moment to read the success message, then close
      setTimeout(() => {
        onCreated(project);
      }, 600);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      appendLog(
        `Error: ${message}`,
        "error"
      );
      if (
        message.includes("HTTP 500") ||
        message.toLowerCase().includes("server") ||
        message.toLowerCase().includes("cannot reach")
      ) {
        appendLog(
          "Tip: Start the backend API first (uvicorn on port 8000), then retry.",
          "info"
        );
      }
      setCreationStatus("error");
    }
  };

  const handleRetry = () => {
    setLogs([]);
    setCreationStatus("running");
    setStep("configure");
  };

  // ── Render ────────────────────────────────────────────────────────────────

  const template = TEMPLATES.find((t) => t.id === selectedTemplate)!;

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="New project wizard"
    >
      {/* Panel */}
      <div className="relative w-full max-w-lg mx-4 bg-surface-900 border border-surface-600 rounded-xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-700">
          <div>
            <h2 className="font-semibold text-gray-100 text-base">
              New Project
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              {step === "template" && "Select your path"}
              {step === "configure" && "Configure your project"}
              {step === "creating" && "Creating your project…"}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <StepDots step={step} />
            {step !== "creating" && (
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-200 transition-colors"
                aria-label="Close wizard"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        {/* Body */}
        <div className="p-5">
          {/* ── Step 1: Template selection ────────────────────────────────── */}
          {step === "template" && (
            <div className="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
              <div className="rounded-lg border border-cyan-500/40 bg-cyan-500/5 p-3">
                <div className="text-xs font-semibold text-cyan-300 uppercase tracking-wide">
                  Meet OpenClaw
                </div>
                <p className="mt-1 text-xs text-gray-300 leading-relaxed">
                  OpenClaw is your strategist: it can refine prompts, give second opinions,
                  and keep your product vision clear while builders execute.
                </p>
                <p className="mt-1 text-[11px] text-gray-500 leading-relaxed">
                  Read-only advisor lane over builder chat context, focused on planning,
                  sequencing, and prompt optimization.
                </p>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => setOpenclawMode("copilot")}
                    className={`px-2.5 py-1 text-xs rounded border transition-colors ${
                      openclawMode === "copilot"
                        ? "border-cyan-400 bg-cyan-500/20 text-cyan-200"
                        : "border-surface-600 bg-surface-800 text-gray-300 hover:border-surface-500"
                    }`}
                  >
                    Start Copiloting
                  </button>
                  <button
                    onClick={() => setOpenclawMode("observer")}
                    className={`px-2.5 py-1 text-xs rounded border transition-colors ${
                      openclawMode === "observer"
                        ? "border-surface-400 bg-surface-700 text-gray-100"
                        : "border-surface-600 bg-surface-800 text-gray-300 hover:border-surface-500"
                    }`}
                  >
                    Silent Observer
                  </button>
                </div>
              </div>

              {TEMPLATES.map((t) => (
                <TemplateCard
                  key={t.id}
                  template={t}
                  selected={selectedTemplate === t.id}
                  onSelect={() => setSelectedTemplate(t.id)}
                />
              ))}
            </div>
          )}

          {/* ── Step 2: Configure ─────────────────────────────────────────── */}
          {step === "configure" && (
            <div className="space-y-5">
              {/* Selected template summary */}
              <div
                className={`flex items-center gap-3 p-3 rounded-lg border ${template.accent}`}
              >
                <span className="text-xl" aria-hidden="true">
                  {template.icon}
                </span>
                <div>
                  <div className="text-sm font-semibold text-gray-100">
                    {template.label}
                  </div>
                  <div className="text-xs text-gray-400">
                    {template.description}
                  </div>
                  <div className="text-[11px] text-gray-500 mt-1">
                    {template.technicalDescription}
                  </div>
                </div>
              </div>

              <div className="rounded-lg border border-surface-700 bg-surface-800 p-3">
                <div className="text-xs font-medium text-gray-300">OpenClaw mode</div>
                <div className="mt-1 text-xs text-gray-400">
                  {openclawMode === "copilot"
                    ? "Copilot active: OpenClaw can suggest steps and rewrite prompts before execution."
                    : "Silent observer: OpenClaw stays quiet until you ask for a second opinion."}
                </div>
              </div>

              {/* Project name */}
              <div>
                <label
                  htmlFor="project-name"
                  className="block text-xs font-medium text-gray-300 mb-1.5"
                >
                  Project Name <span className="text-red-400">*</span>
                </label>
                <input
                  id="project-name"
                  type="text"
                  value={projectName}
                  onChange={(e) => {
                    setProjectName(e.target.value);
                    if (nameError) setNameError("");
                  }}
                  onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                  placeholder={`my-${selectedTemplate}-app`}
                  autoFocus
                  className={`w-full bg-surface-800 text-sm text-gray-100 px-3 py-2 rounded border focus:outline-none transition-colors ${
                    nameError
                      ? "border-red-500 focus:border-red-400"
                      : "border-surface-600 focus:border-accent-400"
                  }`}
                />
                {nameError && (
                  <p className="mt-1 text-xs text-red-400">{nameError}</p>
                )}
                <p className="mt-1 text-xs text-gray-600">
                  Letters, numbers, spaces, hyphens and underscores only.
                </p>
              </div>

              {/* What will be created */}
              <div className="rounded-lg bg-surface-800 border border-surface-700 p-3">
                <p className="text-xs font-medium text-gray-400 mb-2">
                  Files that will be scaffolded
                </p>
                <ScaffoldPreview language={selectedTemplate} />
              </div>
            </div>
          )}

          {/* ── Step 3: Creating ──────────────────────────────────────────── */}
          {step === "creating" && (
            <div className="space-y-4">
              {/* Status icon */}
              <div className="flex items-center justify-center py-4">
                {creationStatus === "running" && (
                  <div className="flex flex-col items-center gap-3">
                    <Loader2
                      size={36}
                      className="animate-spin text-accent-400"
                    />
                    <span className="text-sm text-gray-400">
                      Scaffolding project…
                    </span>
                  </div>
                )}
                {creationStatus === "success" && (
                  <div className="flex flex-col items-center gap-3">
                    <CheckCircle size={36} className="text-green-400" />
                    <span className="text-sm text-gray-300">
                      Project ready!
                    </span>
                  </div>
                )}
                {creationStatus === "error" && (
                  <div className="flex flex-col items-center gap-3">
                    <XCircle size={36} className="text-red-400" />
                    <span className="text-sm text-red-300">
                      Something went wrong.
                    </span>
                  </div>
                )}
              </div>

              {/* Log output */}
              <div className="bg-surface-950 rounded-lg border border-surface-700 p-3 space-y-1.5 min-h-[80px]">
                {logs.map((line) => (
                  <LogEntry key={line.id} line={line} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-4 border-t border-surface-700 bg-surface-950/40">
          {/* Back */}
          <div>
            {step === "configure" && (
              <button
                onClick={handleConfigureBack}
                className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors"
              >
                <ChevronLeft size={15} />
                Back
              </button>
            )}
            {step === "creating" && creationStatus === "error" && (
              <button
                onClick={handleRetry}
                className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors"
              >
                <ChevronLeft size={15} />
                Back
              </button>
            )}
          </div>

          {/* Next / Create */}
          <div>
            {step === "template" && (
              <button
                onClick={handleTemplateNext}
                className="flex items-center gap-1.5 px-4 py-2 bg-accent-500 hover:bg-accent-400 text-white text-sm rounded-lg transition-colors"
              >
                Configure
                <ChevronRight size={15} />
              </button>
            )}
            {step === "configure" && (
              <button
                onClick={handleCreate}
                className="flex items-center gap-1.5 px-4 py-2 bg-accent-500 hover:bg-accent-400 text-white text-sm rounded-lg transition-colors font-medium"
              >
                Create Project
                <ChevronRight size={15} />
              </button>
            )}
            {step === "creating" && creationStatus === "error" && (
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Scaffold preview ─────────────────────────────────────────────────────────

function ScaffoldPreview({ language }: { language: string }) {
  const files: Record<string, string[]> = {
    python: ["main.py", "requirements.txt", "README.md"],
    typescript: ["index.ts", "package.json", "tsconfig.json", "README.md"],
    swift: ["ContentView.swift", "App.swift", "README.md"],
    rust: ["src/main.rs", "Cargo.toml", "README.md"],
    go: ["main.go", "go.mod", "README.md"],
  };

  const list = files[language] ?? files["python"];

  return (
    <ul className="space-y-0.5">
      {list.map((f) => (
        <li key={f} className="flex items-center gap-2 text-xs text-gray-400">
          <span className="text-blue-400 text-[10px]">▸</span>
          {f}
        </li>
      ))}
    </ul>
  );
}

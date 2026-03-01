"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import {
  Play,
  Square,
  Hammer,
  Upload,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface BuildPanelProps {
  projectId: string;
  projectLanguage: string;
}

interface BuildLog {
  timestamp: string;
  level: "info" | "warn" | "error" | "success";
  message: string;
}

type BuildStatus = "idle" | "running" | "success" | "error";

// ─── Component ────────────────────────────────────────────────────────────────

export function BuildPanel({ projectId, projectLanguage }: BuildPanelProps) {
  const [logs, setLogs] = useState<BuildLog[]>([]);
  const [status, setStatus] = useState<BuildStatus>("idle");
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const appendLog = useCallback(
    (level: BuildLog["level"], message: string) => {
      setLogs((prev) => [
        ...prev,
        {
          timestamp: new Date().toLocaleTimeString(),
          level,
          message,
        },
      ]);
    },
    []
  );

  const runAction = useCallback(
    async (action: string) => {
      if (status === "running") return;
      setActiveAction(action);
      setStatus("running");
      appendLog("info", `Starting: ${action}`);

      try {
        const result = await api.buildAction(projectId, action);
        appendLog("success", result.message ?? "Done");
        setStatus("success");
      } catch (err) {
        appendLog(
          "error",
          err instanceof Error ? err.message : "Build failed"
        );
        setStatus("error");
      } finally {
        setActiveAction(null);
      }
    },
    [projectId, status, appendLog]
  );

  const isSwift = projectLanguage === "swift";
  const isRunning = status === "running";

  const levelColors: Record<BuildLog["level"], string> = {
    info: "text-gray-400",
    warn: "text-yellow-400",
    error: "text-red-400",
    success: "text-green-400",
  };

  return (
    <div className="flex flex-col h-full bg-surface-900">
      {/* Header */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-surface-700">
        <Hammer size={14} className="text-accent-400" />
        <span className="text-sm font-semibold text-gray-200">Build</span>
        <div className="ml-auto">
          {status === "running" && (
            <Loader2 size={14} className="animate-spin text-accent-400" />
          )}
          {status === "success" && (
            <CheckCircle size={14} className="text-green-400" />
          )}
          {status === "error" && (
            <XCircle size={14} className="text-red-400" />
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="p-3 border-b border-surface-700 space-y-2">
        <button
          onClick={() => runAction("run")}
          disabled={isRunning}
          className="w-full flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white text-sm rounded transition-colors"
        >
          <Play size={13} />
          Run
        </button>

        <button
          onClick={() => runAction("build")}
          disabled={isRunning}
          className="w-full flex items-center gap-2 px-3 py-1.5 bg-surface-700 hover:bg-surface-600 disabled:opacity-50 text-gray-200 text-sm rounded transition-colors"
        >
          <Hammer size={13} />
          Build
        </button>

        {isSwift && (
          <>
            <button
              onClick={() => runAction("ios_archive")}
              disabled={isRunning}
              className="w-full flex items-center gap-2 px-3 py-1.5 bg-blue-700 hover:bg-blue-600 disabled:opacity-50 text-white text-sm rounded transition-colors"
            >
              <RefreshCw size={13} />
              Archive (iOS)
            </button>

            <button
              onClick={() => runAction("ios_submit")}
              disabled={isRunning}
              className="w-full flex items-center gap-2 px-3 py-1.5 bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 text-white text-sm rounded transition-colors"
            >
              <Upload size={13} />
              Submit to App Store
            </button>
          </>
        )}

        <button
          onClick={() => runAction("stop")}
          disabled={!isRunning}
          className="w-full flex items-center gap-2 px-3 py-1.5 bg-red-800 hover:bg-red-700 disabled:opacity-50 text-white text-sm rounded transition-colors"
        >
          <Square size={13} />
          Stop
        </button>
      </div>

      {/* Logs */}
      <div className="flex-1 overflow-y-auto p-3 font-mono text-xs space-y-0.5">
        {logs.length === 0 ? (
          <div className="text-gray-600">No build output yet.</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className={levelColors[log.level]}>
              <span className="text-gray-600">[{log.timestamp}]</span>{" "}
              {log.message}
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>

      {/* Clear button */}
      {logs.length > 0 && (
        <div className="p-2 border-t border-surface-700">
          <button
            onClick={() => {
              setLogs([]);
              setStatus("idle");
            }}
            className="text-xs text-gray-500 hover:text-gray-300"
          >
            Clear logs
          </button>
        </div>
      )}
    </div>
  );
}

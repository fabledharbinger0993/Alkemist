"use client";

import { useState, useCallback, useEffect } from "react";
import { FileTree, type FileNode } from "@/components/FileTree";
import { Editor } from "@/components/Editor";
import { Terminal } from "@/components/Terminal";
import { AIChatSidebar } from "@/components/AIChatSidebar";
import { BuildPanel } from "@/components/BuildPanel";
import { NewProjectWizard } from "@/components/NewProjectWizard";
import { HoverHint } from "@/components/HoverHint";
import { api } from "@/lib/api";
import {
  FolderOpen,
  Plus,
  GitBranch,
  Bot,
  Hammer,
  ChevronRight,
  X,
} from "lucide-react";

interface OpenTab {
  path: string;
  name: string;
  content: string;
  isDirty: boolean;
  language: string;
}

interface Project {
  id: string;
  name: string;
  language: string;
  root_path: string;
  created_at: string;
}

function detectLanguage(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  const map: Record<string, string> = {
    ts: "typescript",
    tsx: "typescript",
    js: "javascript",
    jsx: "javascript",
    py: "python",
    swift: "swift",
    rs: "rust",
    go: "go",
    sh: "shell",
    bash: "shell",
    json: "json",
    md: "markdown",
    toml: "toml",
    yaml: "yaml",
    yml: "yaml",
    css: "css",
    html: "html",
  };
  return map[ext] ?? "plaintext";
}

export default function IDEPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [openTabs, setOpenTabs] = useState<OpenTab[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [showAI, setShowAI] = useState(true);
  const [showBuild, setShowBuild] = useState(false);
  const [showProjects, setShowProjects] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const [gitBranch, setGitBranch] = useState("main");
  const [showActivityHint, setShowActivityHint] = useState(false);

  useEffect(() => {
    api.listProjects().then(setProjects).catch(console.error);
  }, []);

  useEffect(() => {
    const dismissed = localStorage.getItem("alkemist-activity-hints-dismissed");
    if (!dismissed) {
      setShowActivityHint(true);
    }
  }, []);

  useEffect(() => {
    if (!activeProject) return;
    api
      .getFileTree(activeProject.id)
      .then(setFileTree)
      .catch(console.error);

    api
      .gitStatus(activeProject.id)
      .then((status) => setGitBranch(status.branch || "main"))
      .catch(() => setGitBranch("main"));
  }, [activeProject]);

  const openFile = useCallback(
    async (path: string) => {
      if (!activeProject) return;
      const existing = openTabs.find((t) => t.path === path);
      if (existing) {
        setActiveTab(path);
        return;
      }
      try {
        const { content } = await api.readFile(activeProject.id, path);
        const name = path.split("/").pop() ?? path;
        setOpenTabs((prev) => [
          ...prev,
          {
            path,
            name,
            content,
            isDirty: false,
            language: detectLanguage(name),
          },
        ]);
        setActiveTab(path);
      } catch (err) {
        console.error("Failed to open file:", err);
      }
    },
    [activeProject, openTabs]
  );

  const saveFile = useCallback(
    async (path: string, content: string) => {
      if (!activeProject) return;
      await api.writeFile(activeProject.id, path, content);
      setOpenTabs((prev) =>
        prev.map((t) => (t.path === path ? { ...t, isDirty: false } : t))
      );
    },
    [activeProject]
  );

  const closeTab = useCallback(
    (path: string) => {
      setOpenTabs((prev) => {
        const remaining = prev.filter((t) => t.path !== path);
        if (activeTab === path) {
          setActiveTab(remaining.at(-1)?.path ?? null);
        }
        return remaining;
      });
    },
    [activeTab]
  );

  const handleEditorChange = useCallback((path: string, value: string) => {
    setOpenTabs((prev) =>
      prev.map((t) =>
        t.path === path ? { ...t, content: value, isDirty: true } : t
      )
    );
  }, []);

  const handleProjectCreated = useCallback((project: Project) => {
    setProjects((prev) => [project, ...prev]);
    setActiveProject(project);
    setShowWizard(false);
    setShowProjects(false);
    setOpenTabs([]);
    setActiveTab(null);
  }, []);

  const dismissActivityHint = useCallback(() => {
    setShowActivityHint(false);
    localStorage.setItem("alkemist-activity-hints-dismissed", "1");
  }, []);

  const activeTabData = openTabs.find((t) => t.path === activeTab);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-surface-950">
      <div className="relative flex flex-col items-center w-12 bg-surface-900 border-r border-surface-700 py-2 gap-1 shrink-0">
        {showActivityHint && (
          <div className="absolute left-full ml-2 top-2 z-50 w-56 rounded border border-surface-600 bg-surface-800/85 p-2 text-xs text-gray-200 backdrop-blur-sm">
            Hover the icons for quick hints. Profiles and commands are free-switch.
            <button
              onClick={dismissActivityHint}
              className="block mt-1 text-[11px] text-accent-300 hover:text-accent-200"
            >
              Dismiss
            </button>
          </div>
        )}

        <HoverHint hint="Open project list" side="right">
          <button
            onClick={() => setShowProjects((v) => !v)}
            className={`p-2 rounded hover:bg-surface-700 transition-colors ${showProjects ? "text-accent-400" : "text-gray-400"}`}
          >
            <FolderOpen size={18} />
          </button>
        </HoverHint>

        <HoverHint hint="Create a new project" side="right">
          <button
            onClick={() => setShowWizard(true)}
            className="p-2 rounded hover:bg-surface-700 transition-colors text-gray-400"
          >
            <Plus size={18} />
          </button>
        </HoverHint>

        <div className="flex-1" />

        <HoverHint hint="Open AI Assistant and switch personas anytime" side="right">
          <button
            onClick={() => setShowAI((v) => !v)}
            className={`p-2 rounded hover:bg-surface-700 transition-colors ${showAI ? "text-accent-400" : "text-gray-400"}`}
          >
            <Bot size={18} />
          </button>
        </HoverHint>

        <HoverHint hint="Open build/run command panel" side="right">
          <button
            onClick={() => setShowBuild((v) => !v)}
            className={`p-2 rounded hover:bg-surface-700 transition-colors ${showBuild ? "text-accent-400" : "text-gray-400"}`}
          >
            <Hammer size={18} />
          </button>
        </HoverHint>

        <HoverHint hint={`Current branch: ${gitBranch}`} side="right">
          <button className="p-2 rounded hover:bg-surface-700 transition-colors text-gray-400">
            <GitBranch size={18} />
          </button>
        </HoverHint>
      </div>

      {showProjects && (
        <div className="w-64 bg-surface-900 border-r border-surface-700 flex flex-col shrink-0">
          <div className="px-3 py-2 border-b border-surface-700 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Projects
          </div>

          <div className="p-3 border-b border-surface-700">
            <button
              onClick={() => setShowWizard(true)}
              className="w-full flex items-center justify-center gap-2 bg-accent-500 hover:bg-accent-400 text-white text-sm py-1.5 rounded transition-colors"
            >
              <Plus size={14} />
              New Project
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {projects.map((p) => (
              <button
                key={p.id}
                onClick={() => {
                  setActiveProject(p);
                  setOpenTabs([]);
                  setActiveTab(null);
                }}
                className={`w-full text-left px-3 py-2 text-sm flex items-center gap-2 hover:bg-surface-700 transition-colors ${
                  activeProject?.id === p.id
                    ? "bg-surface-700 text-accent-300"
                    : "text-gray-300"
                }`}
              >
                <ChevronRight size={12} className="text-gray-500" />
                <span className="truncate">{p.name}</span>
                <span className="ml-auto text-xs text-gray-500">{p.language}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {activeProject && (
        <div className="w-52 bg-surface-900 border-r border-surface-700 flex flex-col shrink-0">
          <div className="px-3 py-2 border-b border-surface-700 text-xs font-semibold text-gray-400 uppercase tracking-wider truncate">
            {activeProject.name}
          </div>
          <div className="flex-1 overflow-y-auto">
            <FileTree
              nodes={fileTree}
              onFileClick={openFile}
              activeFile={activeTab ?? undefined}
            />
          </div>
        </div>
      )}

      <div className="flex flex-col flex-1 min-w-0">
        <div className="flex items-center bg-surface-900 border-b border-surface-700 overflow-x-auto shrink-0">
          {openTabs.map((tab) => (
            <div
              key={tab.path}
              className={`flex items-center gap-2 px-3 py-1.5 text-sm border-r border-surface-700 cursor-pointer shrink-0 ${
                activeTab === tab.path
                  ? "bg-surface-800 text-gray-100"
                  : "text-gray-400 hover:bg-surface-800"
              }`}
              onClick={() => setActiveTab(tab.path)}
            >
              <span className="truncate max-w-32">{tab.name}</span>
              {tab.isDirty && (
                <span className="w-1.5 h-1.5 rounded-full bg-accent-400 shrink-0" />
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  closeTab(tab.path);
                }}
                className="text-gray-500 hover:text-gray-200 ml-1"
              >
                <X size={12} />
              </button>
            </div>
          ))}
        </div>

        <div className="flex flex-col flex-1 min-h-0">
          <div className="flex-1 min-h-0">
            {activeTabData ? (
              <Editor
                path={activeTabData.path}
                content={activeTabData.content}
                language={activeTabData.language}
                onChange={(val) => handleEditorChange(activeTabData.path, val)}
                onSave={(val) => saveFile(activeTabData.path, val)}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-600 select-none">
                <div className="text-center">
                  <div className="text-5xl mb-4">⚗️</div>
                  <div className="text-xl font-semibold text-gray-500">Alkemist</div>
                  <div className="text-sm mt-1 text-gray-600">
                    {activeProject
                      ? "Select a file to edit"
                      : "Create or open a project to start"}
                  </div>
                </div>
              </div>
            )}
          </div>

          {activeProject && (
            <div className="h-48 border-t border-surface-700 shrink-0">
              <Terminal projectId={activeProject.id} />
            </div>
          )}
        </div>
      </div>

      {showAI && activeProject && (
        <div className="w-80 border-l border-surface-700 shrink-0">
          <AIChatSidebar
            projectId={activeProject.id}
            activeFile={activeTab ?? undefined}
            activeFileContent={activeTabData?.content}
          />
        </div>
      )}

      {showBuild && activeProject && (
        <div className="w-72 border-l border-surface-700 shrink-0">
          <BuildPanel
            projectId={activeProject.id}
            projectLanguage={activeProject.language}
          />
        </div>
      )}

      {showWizard && (
        <NewProjectWizard
          onClose={() => setShowWizard(false)}
          onCreated={handleProjectCreated}
        />
      )}
    </div>
  );
}

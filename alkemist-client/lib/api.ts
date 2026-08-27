// Base URL for API calls (proxied via Next.js rewrites in dev)
const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Project {
  id: string;
  name: string;
  language: string;
  root_path: string;
  created_at: string;
}

export interface FileNode {
  id: string;
  name: string;
  path: string;
  isDirectory: boolean;
  children?: FileNode[];
}

export type AgentPersona = "visionary" | "engineer" | "contractor" | "finisher";

export interface ChatRequest {
  message: string;
  model: string;
  context_file?: string;
  context_content?: string;
  persona?: AgentPersona;
  app_idea?: string;
  engineer_generate_readme?: boolean;
  engineer_generate_contractor_handoff?: boolean;
}

export interface ReasoningStep {
  stage: "awareness" | "literalist" | "congress" | "judge";
  label: string;
  summary: string;
}

export interface ChatResponse {
  content: string;
  reasoning_steps?: ReasoningStep[];
  model: string;
}

export interface BuildActionResponse {
  success: boolean;
  message?: string;
  output?: string;
}

export interface ModelListResponse {
  models: string[];
}

export interface ModelInstallResponse {
  success: boolean;
  message: string;
  model: string;
}

// ─── HTTP helper ──────────────────────────────────────────────────────────────

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error(
      "Cannot reach Alkemist server. Make sure backend is running on port 8000."
    );
  }

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      message = body.detail ?? message;
    } catch {
      // ignore parse errors
    }

    if (response.status >= 500 && message === `HTTP ${response.status}`) {
      message =
        "Server error while processing request. Check backend logs and confirm API is running.";
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

// ─── API client ───────────────────────────────────────────────────────────────

export const api = {
  // Projects
  listProjects: () => request<Project[]>("/projects"),

  createProject: (name: string, language: string) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name, language }),
    }),

  deleteProject: (id: string) =>
    request<void>(`/projects/${id}`, { method: "DELETE" }),

  // Files
  getFileTree: (projectId: string) =>
    request<FileNode[]>(`/projects/${projectId}/files`),

  readFile: (projectId: string, path: string) =>
    request<{ content: string; path: string }>(
      `/projects/${projectId}/files/read?path=${encodeURIComponent(path)}`
    ),

  writeFile: (projectId: string, path: string, content: string) =>
    request<void>(`/projects/${projectId}/files/write`, {
      method: "PUT",
      body: JSON.stringify({ path, content }),
    }),

  // AI
  chat: (projectId: string, payload: ChatRequest) =>
    request<ChatResponse>(`/ai/${projectId}/chat`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  listModels: () => request<ModelListResponse>("/ai/models"),

  installModel: (model: string) =>
    request<ModelInstallResponse>("/ai/models/install", {
      method: "POST",
      body: JSON.stringify({ model }),
    }),

  // Build
  buildAction: (projectId: string, action: string) =>
    request<BuildActionResponse>(`/projects/${projectId}/build`, {
      method: "POST",
      body: JSON.stringify({ action }),
    }),

  // Git
  gitInit: (projectId: string) =>
    request<{ message: string }>(`/projects/${projectId}/git/init`, {
      method: "POST",
    }),

  gitCommit: (projectId: string, message: string) =>
    request<{ message: string; hash: string }>(
      `/projects/${projectId}/git/commit`,
      { method: "POST", body: JSON.stringify({ message }) }
    ),

  gitStatus: (projectId: string) =>
    request<{ branch: string; status: string[] }>(
      `/projects/${projectId}/git/status`
    ),
};

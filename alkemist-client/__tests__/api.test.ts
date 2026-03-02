/**
 * Unit tests for the API client module (lib/api.ts).
 *
 * `fetch` is mocked globally so no real network calls are made.
 */

import { api } from "../lib/api";

// ─── fetch mock helpers ───────────────────────────────────────────────────────

function mockFetch(body: unknown, status = 200): void {
  global.fetch = jest.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  } as Response);
}

function mockFetchError(status: number, detail: string): void {
  global.fetch = jest.fn().mockResolvedValue({
    ok: false,
    status,
    json: () => Promise.resolve({ detail }),
  } as Response);
}

afterEach(() => {
  jest.restoreAllMocks();
});

// ─── listProjects ─────────────────────────────────────────────────────────────

describe("api.listProjects", () => {
  it("returns an array of projects on success", async () => {
    const projects = [
      { id: "1", name: "App", language: "python", root_path: "/tmp/1", created_at: "" },
    ];
    mockFetch(projects);

    const result = await api.listProjects();

    expect(result).toEqual(projects);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("throws on HTTP error with detail message", async () => {
    mockFetchError(500, "Internal server error");

    await expect(api.listProjects()).rejects.toThrow("Internal server error");
  });

  it("throws with HTTP status when no detail is provided", async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: () => Promise.reject(new Error("not json")),
    } as unknown as Response);

    await expect(api.listProjects()).rejects.toThrow("HTTP 503");
  });
});

// ─── createProject ────────────────────────────────────────────────────────────

describe("api.createProject", () => {
  it("sends POST with name and language", async () => {
    const project = { id: "abc", name: "New App", language: "typescript", root_path: "/tmp", created_at: "" };
    mockFetch(project, 201);

    const result = await api.createProject("New App", "typescript");

    expect(result).toEqual(project);
    const call = (global.fetch as jest.Mock).mock.calls[0];
    expect(call[1].method).toBe("POST");
    expect(JSON.parse(call[1].body as string)).toEqual({ name: "New App", language: "typescript" });
  });

  it("throws on 422 validation error", async () => {
    mockFetchError(422, "name must be at least 1 character");

    await expect(api.createProject("", "python")).rejects.toThrow("name must be at least 1 character");
  });
});

// ─── deleteProject ────────────────────────────────────────────────────────────

describe("api.deleteProject", () => {
  it("sends DELETE to the correct URL", async () => {
    mockFetch(null, 204);

    await api.deleteProject("proj-123");

    const call = (global.fetch as jest.Mock).mock.calls[0];
    expect(call[0]).toContain("/projects/proj-123");
    expect(call[1].method).toBe("DELETE");
  });

  it("throws on 404", async () => {
    mockFetchError(404, "Project not found");

    await expect(api.deleteProject("missing")).rejects.toThrow("Project not found");
  });
});

// ─── getFileTree ──────────────────────────────────────────────────────────────

describe("api.getFileTree", () => {
  it("returns file nodes array", async () => {
    const nodes = [
      { id: "n1", name: "main.py", path: "main.py", isDirectory: false },
    ];
    mockFetch(nodes);

    const result = await api.getFileTree("proj-1");

    expect(result).toEqual(nodes);
    const call = (global.fetch as jest.Mock).mock.calls[0];
    expect(call[0]).toContain("/projects/proj-1/files");
  });
});

// ─── readFile ─────────────────────────────────────────────────────────────────

describe("api.readFile", () => {
  it("encodes the path query parameter", async () => {
    mockFetch({ path: "src/main.py", content: "x = 1" });

    await api.readFile("proj-1", "src/main.py");

    const call = (global.fetch as jest.Mock).mock.calls[0];
    expect(call[0]).toContain(encodeURIComponent("src/main.py"));
  });

  it("returns path and content", async () => {
    mockFetch({ path: "a.py", content: "hello" });

    const result = await api.readFile("proj-1", "a.py");

    expect(result.content).toBe("hello");
    expect(result.path).toBe("a.py");
  });
});

// ─── writeFile ────────────────────────────────────────────────────────────────

describe("api.writeFile", () => {
  it("sends PUT with path and content", async () => {
    mockFetch({ status: "ok", path: "a.py" });

    await api.writeFile("proj-1", "a.py", "print('hi')");

    const call = (global.fetch as jest.Mock).mock.calls[0];
    expect(call[1].method).toBe("PUT");
    const body = JSON.parse(call[1].body as string);
    expect(body.path).toBe("a.py");
    expect(body.content).toBe("print('hi')");
  });
});

// ─── chat ─────────────────────────────────────────────────────────────────────

describe("api.chat", () => {
  it("sends POST to the ai chat endpoint", async () => {
    const response = {
      content: "Here is your code.",
      reasoning_steps: [],
      model: "deepseek-v3.2",
    };
    mockFetch(response);

    const result = await api.chat("proj-1", {
      message: "Add a health endpoint",
      model: "deepseek-v3.2",
    });

    expect(result.content).toBe("Here is your code.");
    const call = (global.fetch as jest.Mock).mock.calls[0];
    expect(call[0]).toContain("/ai/proj-1/chat");
    expect(call[1].method).toBe("POST");
  });
});

// ─── buildAction ─────────────────────────────────────────────────────────────

describe("api.buildAction", () => {
  it("sends POST with action field", async () => {
    mockFetch({ success: true, output: "Built OK" });

    const result = await api.buildAction("proj-1", "build");

    expect(result.success).toBe(true);
    const call = (global.fetch as jest.Mock).mock.calls[0];
    const body = JSON.parse(call[1].body as string);
    expect(body.action).toBe("build");
  });
});

// ─── git helpers ──────────────────────────────────────────────────────────────

describe("api.gitCommit", () => {
  it("sends POST with commit message and returns hash", async () => {
    mockFetch({ message: "feat: add route", hash: "abc12345" });

    const result = await api.gitCommit("proj-1", "feat: add route");

    expect(result.hash).toBe("abc12345");
    const body = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body as string);
    expect(body.message).toBe("feat: add route");
  });
});

describe("api.gitStatus", () => {
  it("returns branch and status array", async () => {
    mockFetch({ branch: "main", status: ["M main.py"] });

    const result = await api.gitStatus("proj-1");

    expect(result.branch).toBe("main");
    expect(result.status).toContain("M main.py");
  });
});

# Alkemist — Copilot Coding Agent Instructions

## What This Repository Does

Alkemist is a local, AI-native IDE platform ("the app that builds apps"). It consists of:

- **`alkemist-server/`** — Python FastAPI backend with LangGraph-powered AI reasoning, SQLite persistence, ChromaDB vector memory, and an iOS build pipeline.
- **`alkemist-client/`** — Next.js 15 / React 19 / TypeScript frontend that provides an IDE-like UI (file tree, Monaco editor, xterm terminal, AI chat sidebar).
- **`docker-compose.yml`** — Runs ChromaDB for vector memory (port 8001).

The AI reasoning engine is called the **Sovern Logic Ladder** (`alkemist-server/ai/logic_ladder.py`): it has four LangGraph stages — Awareness (RAG retrieval), Literalist (requirements extraction), Congress (Advocate → Skeptic → Synthesizer), and Judge (final output + commit message).

---

## Backend (`alkemist-server/`)

**Runtime:** Python 3.12+, managed by [Poetry](https://python-poetry.org/).

**Key files:**
- `main.py` — FastAPI app entry point; registers routers and initialises DB/dirs.
- `pyproject.toml` — Dependencies and pytest config (`asyncio_mode = "auto"`, `testpaths = ["tests"]`).
- `routers/` — `projects.py`, `files.py`, `ai.py`, `terminal.py`.
- `ai/logic_ladder.py` — Sovern Logic Ladder (LangGraph state machine).
- `models/database.py` — SQLAlchemy async models; `init_db()` creates tables.
- `models/schemas.py` — Pydantic request/response schemas.
- `execution/docker_manager.py` — Docker-based sandbox execution.
- `ios/pipeline.py` — xcodebuild / notarytool wrapper (macOS only; fails gracefully on Linux).
- `tests/` — pytest suite; `conftest.py` adds the server root to `sys.path`.

**Bootstrap and run tests (always run from `alkemist-server/`):**
```bash
cd alkemist-server
poetry install          # install all dependencies including dev
poetry run pytest       # run all tests (fast; no live Ollama/ChromaDB needed)
```

**Run the server:**
```bash
cd alkemist-server
poetry run uvicorn main:app --reload --port 8000
```

**Linting (no dedicated linter configured; use standard Python tooling if adding one).**

**Environment variables (optional; defaults work for local dev):**
| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama inference server |
| `CHROMA_HOST` | `localhost` | ChromaDB host |
| `CHROMA_PORT` | `8001` | ChromaDB port |

**External services:** ChromaDB and Ollama are optional at test time — the code has `try/except` guards so tests pass without them. Start ChromaDB with `docker compose up -d`.

---

## Frontend (`alkemist-client/`)

**Runtime:** Node.js (LTS), npm.

**Key files:**
- `package.json` — Scripts: `dev`, `build`, `start`, `lint`, `type-check`.
- `next.config.ts` — Rewrites `/api/*` → `http://localhost:8000/*` and `/ws/*` → `http://localhost:8000/ws/*`.
- `tailwind.config.ts` — Custom dark IDE palette (`surface.*`, `accent.*`), `JetBrains Mono` font family.
- `app/` — Next.js App Router; `layout.tsx`, `page.tsx`, `globals.css`.
- `components/` — `Editor.tsx` (Monaco), `FileTree.tsx`, `Terminal.tsx` (xterm), `AIChatSidebar.tsx`, `BuildPanel.tsx`.
- `lib/` — Shared utilities.

**Bootstrap and validate (always run from `alkemist-client/`):**
```bash
cd alkemist-client
npm install             # always run before build or lint
npm run lint            # ESLint via next lint
npm run type-check      # tsc --noEmit (no emit, type errors only)
npm run build           # production build (also catches type errors)
```

**Run dev server:**
```bash
cd alkemist-client
npm install && npm run dev   # starts on http://localhost:3000
```

---

## Project Layout (root)

```
.github/
  copilot-instructions.md   ← this file
  instructions/             ← path-specific Copilot instructions
alkemist-client/            ← Next.js frontend
alkemist-server/            ← FastAPI backend
docker-compose.yml          ← ChromaDB service
README.md
LICENSE
ISSUE_TEMPLATE.md
```

---

## Coding Conventions

- **Python:** Type-annotated, async-first (FastAPI + SQLAlchemy async). Use `structlog` for logging. Follow the existing `# ─── Section ───` comment separator style.
- **TypeScript/React:** Functional components, Tailwind CSS utility classes, `clsx`/`tailwind-merge` for conditional classes. No CSS modules.
- **Tests:** Backend tests live in `alkemist-server/tests/`. Mock external services (`ollama`, `chromadb`, `docker`, `xcodebuild`) with `pytest-mock` / `unittest.mock`. All test functions are `async def` due to `asyncio_mode = "auto"`.
- **iOS pipeline:** All `ios/pipeline.py` functions must check `_is_macos()` and return a `PipelineResult(success=False)` on non-macOS platforms.

## Validation Checklist Before Submitting Changes

1. `cd alkemist-server && poetry run pytest` — all tests pass.
2. `cd alkemist-client && npm install && npm run type-check` — zero TypeScript errors.
3. `cd alkemist-client && npm run lint` — zero ESLint errors.
4. If modifying the FastAPI app, confirm `main.py` imports and router prefixes are consistent.

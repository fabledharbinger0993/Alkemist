# 🧪 Alkemist — The App that Builds Apps

**A local, AI-native, browser-based IDE** — Replit-scope, fully sovereign, offline-capable, powered by Ollama.

```
┌─────────────────────────────────────────────────────────────┐
│                     ALKEMIST ARCHITECTURE                    │
│                                                             │
│   Browser (Next.js 16)                                      │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  FileTree │ Monaco Editor │ xterm.js │ AI Sidebar    │  │
│   └──────────────────┬───────────────────────────────────┘  │
│                      │ REST + WebSocket                      │
│   FastAPI Server     ▼                                      │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  Projects │ Files │ AI Router │ Terminal │ iOS       │  │
│   │  ┌─────────────────────────────────────────────────┐ │  │
│   │  │ Sovern Logic Ladder (LangGraph)                 │ │  │
│   │  │  Awareness → Literalist → Congress → Judge      │ │  │
│   │  └───────────────────┬─────────────────────────────┘ │  │
│   │                      │                               │  │
│   │  ┌────────────┐  ┌───▼──────┐  ┌────────────────┐   │  │
│   │  │  ChromaDB  │  │  Ollama  │  │ Docker Manager │   │  │
│   │  │  (RAG/mem) │  │ (local)  │  │ (sandboxes)    │   │  │
│   │  └────────────┘  └──────────┘  └────────────────┘   │  │
│   │                                                       │  │
│   │  ┌──────────────────────────────────────────────┐    │  │
│   │  │  iOS Pipeline (macOS only)                   │    │  │
│   │  │  xcodebuild → notarytool → Transporter       │    │  │
│   │  └──────────────────────────────────────────────┘    │  │
│   └──────────────────────────────────────────────────────┘  │
│                         SQLite                              │
└─────────────────────────────────────────────────────────────┘
```

## Features (Phase 1 MVP)

| Feature | Status |
|---|---|
| Browser-based IDE (Monaco Editor) | ✅ |
| Project file tree (react-arborist) | ✅ |
| Integrated xterm.js terminal over WebSocket | ✅ |
| AI chat sidebar with Ollama | ✅ |
| Per-project Docker sandboxes | ✅ |
| Sovern Logic Ladder AI chain (LangGraph) | ✅ |
| RAG with ChromaDB for codebase context | ✅ |
| SQLite project persistence | ✅ |
| Git init / commit / branch | ✅ |
| SwiftUI / FastAPI / Node Express templates | ✅ |
| iOS build pipeline (macOS only) | ✅ |
| Persistent memory graph (embeddings) | ✅ |

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| macOS | 15+ | Required for iOS pipeline; Linux ok for non-iOS |
| Ollama | latest | `brew install ollama` |
| Docker Desktop | latest | For Python/Node/Rust/Go sandboxes |
| Xcode | 26+ | iOS 26 SDK + Command Line Tools |
| Python | 3.12+ | Backend runtime |
| Node.js | 22+ | Frontend runtime |
| RAM | 32GB+ | Apple Silicon preferred for Ollama models |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/fabledharbinger0993/Alkemist.git
cd Alkemist

# 2. Pull AI models
ollama pull deepseek-v3.2
ollama pull qwen3:235b-a22b-q4_K_M   # optional, large

# 3. Start backend
cd alkemist-server
pip install poetry
poetry install
poetry run uvicorn main:app --reload --port 8000

# 4. Start frontend (new terminal)
cd alkemist-client
npm install
npm run dev

# 5. Open http://localhost:3000
```

## Folder Structure

```
Alkemist/
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml          # ChromaDB + optional services
│
├── alkemist-client/            # Next.js 16 frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Main IDE layout
│   │   └── globals.css
│   ├── components/
│   │   ├── FileTree.tsx        # react-arborist file tree
│   │   ├── Editor.tsx          # Monaco Editor wrapper
│   │   ├── Terminal.tsx        # xterm.js + WebSocket
│   │   ├── AIChatSidebar.tsx   # AI chat + reasoning display
│   │   └── BuildPanel.tsx      # Build logs + iOS pipeline
│   └── lib/
│       ├── api.ts              # REST client
│       └── websocket.ts        # WebSocket manager
│
└── alkemist-server/            # FastAPI backend
    ├── pyproject.toml
    ├── main.py                 # App entrypoint + WebSocket
    ├── routers/
    │   ├── projects.py         # CRUD + Git ops
    │   ├── files.py            # File read/write/tree
    │   ├── ai.py               # AI endpoints
    │   └── terminal.py         # PTY WebSocket
    ├── ai/
    │   └── logic_ladder.py     # Sovern Logic Ladder (LangGraph)
    ├── execution/
    │   └── docker_manager.py   # Per-project Docker sandboxes
    ├── ios/
    │   └── pipeline.py         # xcodebuild/notarytool/transporter
    ├── models/
    │   ├── database.py         # SQLite + SQLAlchemy
    │   └── schemas.py          # Pydantic schemas
    └── tests/
        ├── test_logic_ladder.py
        └── test_pipeline.py
```

## Architecture Decisions

### Why Layered Monolith (not microservices)?

Single-user local app — microservices would add network overhead, complex orchestration, and operational burden with zero benefit at this scale. The layered monolith provides:
- **Low latency**: In-process calls between AI, execution, and file layers
- **Simple deployment**: `uvicorn main:app` starts everything
- **Easy debugging**: Single process, single log stream
- **Evolvable**: Layers can be extracted to services in Phase 3+ if needed

### Sovern Logic Ladder

Each AI request flows through a structured 4-stage chain:

1. **Awareness** — Capture user intent + embed full codebase snapshot into ChromaDB; retrieve relevant chunks
2. **Literalist Filter** — Strip metaphors, extract raw functional requirements only
3. **Congress** — Three agents in sequence:
   - *Advocate*: Proposes efficient implementation
   - *Skeptic*: Reviews against Apple HIG, App Store §2.5.2, deprecated APIs
   - *Synthesizer*: Merges advocate + skeptic feedback into final code
4. **Judge** — Outputs final code + structured commit message; logs step to memory graph

### Production Failure Modes & Hardening

| Risk | Mitigation |
|---|---|
| Docker port conflicts | Dynamic port allocation with conflict detection |
| Ollama OOM on large models | Model health check before request; graceful degradation to smaller model |
| App Store §2.5.2 violation (runtime executable download) | Skeptic agent explicitly checks this rule in every iOS code generation |
| Stale ChromaDB embeddings | Content hash-based invalidation on file save |
| xcodebuild process hang | Subprocess timeout (30 min default) + cancellation signal |

## Roadmap

| Phase | Features |
|---|---|
| **Phase 1** (MVP) | Monaco IDE, Docker execution, Ollama AI, iOS pipeline, SQLite |
| **Phase 2** | Multi-model routing, agent memory graph UI, collaborative sessions |
| **Phase 3** | Plugin marketplace, custom Docker manifests, CI integration |
| **Phase 4** | Mobile companion app, distributed team sessions |

## License

MIT — see [LICENSE](LICENSE)

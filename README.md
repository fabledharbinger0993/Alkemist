# Alkemist

Local AI-native IDE for building applications with language models.

**Features:**
- 🧠 Local LLM inference via **Ollama** (no cloud API costs)
- 🦞 **OpenClaw** orchestration with **Telegram bot** integration
- 📝 **Next.js** web UI + **Python FastAPI** backend
- 🤖 **Sovern Logic Ladder** reasoning engine (4-stage AI pipeline)
- 📞 Control via Telegram, web UI, or API
- 🔒 Local-only architecture (bound to localhost)

---

## Quick Start

### Prerequisites

- **Node.js 18+** (runtime)
- **Python 3.12+** (backend)
- **Ollama** (local LLM inference)
- **OpenClaw** (orchestration)
- **Docker** (optional, for project sandboxing)

### Launch (One Command)

**Linux/Ubuntu/macOS:**
```bash
cd /workspaces/Alkemist
chmod +x launch-alkemist-agent.sh
./launch-alkemist-agent.sh
```

**Windows:**
```bash
launch-alkemist-agent.bat
```

Both scripts handle:
1. ✅ Prerequisites check
2. 🧠 Ollama startup + model pull
3. 🦞 OpenClaw Gateway startup
4. 📱 Telegram bot verification
5. 🎯 Service health check

### Access Points

| Service | URL / Port | Interface |
|---------|-----------|-----------|
| **Frontend** | http://127.0.0.1:3000 | Web IDE |
| **Backend** | http://127.0.0.1:8000 | REST API |
| **Ollama** | http://127.0.0.1:11434 | LLM inference |
| **OpenClaw Gateway** | http://127.0.0.1:18789 | Telegram router |
| **Telegram** | @YourBotHandle | Command interface |

---

## Architecture

```
┌────────────────────────────────────────────────┐
│     Telegram Bot (User Interface)              │
│  Send: "test backed", "build project", etc.    │
└────────────│──────────────────────────────────┘
             │
        ┌────▼────────────────────────┐
        │ OpenClaw Gateway (18789)    │
        │ • Webhook handler           │
        │ • Command routing           │
        │ • Audit logging             │
        └────┬──────────────┬─────────┘
             │              │
      ┌──────▼─┐    ┌──────▼──────────────┐
      │ Ollama │    │ Alkemist Backend    │
      │ (11434)│    │ • FastAPI (8000)    │
      │        │    │ • Logic Ladder      │
      │ • Code │    │ • File management   │
      │   Gen  │    │ • Docker execution  │
      │ • Chat │    │ • SQLite + ChromaDB │
      │ • Embed│    │                     │
      └────────┘    └──────┬──────────────┘
                           │
                    ┌──────▼──────────┐
                    │ Next.js Frontend│
                    │ (3000)          │
                    │ • Monaco editor │
                    │ • File tree     │
                    │ • Terminal      │
                    │ • AI chat       │
                    └─────────────────┘
```

---

## Development Workflow

### Backend (Python)

```bash
cd alkemist-server
poetry install          # Install dependencies
poetry run pytest       # Run all tests (57 tests)
poetry run uvicorn main:app --reload --port 8000
```

### Frontend (TypeScript/React)

```bash
cd alkemist-client
npm install             # Install dependencies
npm run dev             # Dev server on port 3000
npm run type-check      # Type validation
npm run lint            # ESLint
npm run build           # Production build
```

### OpenClaw Router

New `routers/openclaw.py` handles Telegram webhook:
- **POST /openclaw/webhook** — Receive Telegram commands
- **GET /openclaw/status** — Health check
- **Commands:** status, test, build, health, logs, help, chat

Example workflow:
```
Telegram: "test alkemist backend"
  ↓
OpenClaw parses → "test" command
  ↓
Routes to /openclaw/webhook
  ↓
Executes pytest, returns result
  ↓
Telegram: "✅ 73 tests passing"
```

---

## Documentation

- **[OPENCLAW_OLLAMA_SETUP.md](OPENCLAW_OLLAMA_SETUP.md)** — Full setup guide, architecture, Telegram bot configuration
- **[docs/installer-matrix.md](docs/installer-matrix.md)** — Runtime packs & sandboxing
- **[docs/connect-models-mvp.md](docs/connect-models-mvp.md)** — Model provider flexibility
- **[docs/schemas/](docs/schemas/)** — Provider profile & audit log schemas
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** — Codebase overview (Bane agent)

---

## Agent Profiles

Custom agent configurations for this repo:

| Profile | Purpose |
|---------|---------|
| **Bane** | Full execution agent: backend, frontend, infra, debugging, releases |
| **Bane-Light** | Fast code reviewer: quick assessments, triage, min-viable fixes |

---

## Key Technologies

| Component | Stack |
|-----------|-------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy async, structlog |
| **Frontend** | Next.js 15, React 19, TypeScript, Tailwind CSS |
| **AI** | LangGraph, Ollama (local), ChromaDB (vector memory) |
| **Testing** | pytest, asyncio, unittest.mock |
| **Build** | Poetry (Python), npm (Node.js), Docker (optional) |

---

## Testing

### Run All Tests

```bash
cd alkemist-server
poetry run pytest -v
```

**Results:** ✅ 73 passing
- 16 tests for OpenClaw integration (new)
- 57 tests for core backend logic

### Frontend Validation

```bash
cd alkemist-client
npm run type-check      # TypeScript errors
npm run lint            # ESLint warnings/errors
npm run build           # Production build test
```

---

## Troubleshooting

### Ollama not responding
```bash
ollama serve            # Start manually
ollama list             # Check installed models
ollama pull mistral     # Install a model
```

### OpenClaw not initializing
```bash
npm install -g openclaw @latest
openclaw start          # Manual start
openclaw status         # Check configuration
```

### Port conflicts
```bash
# Find process using port
lsof -i :18789          # OpenClaw
lsof -i :11434          # Ollama
lsof -i :8000           # Alkemist backend
lsof -i :3000           # Frontend
```

### Telegram bot issues
```bash
openclaw status         # Check telegram config
openclaw onboard        # Re-authenticate
tail -f ~/.alkemist-logs/openclaw.log
```

---

## Telemetry & Logs

All activity is logged locally:
- **Logs location:** `~/.alkemist-logs/`
- **Backend logs:** `alkemist-server/ (console)`
- **OpenClaw logs:** `openclaw.log`
- **Ollama logs:** `ollama.log`

No data is sent to cloud. Everything runs on your machine.

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Run validation: `make validate` or:
   ```bash
   cd alkemist-server && poetry run pytest
   cd alkemist-client && npm run type-check && npm run lint
   ```
4. Commit with clear message
5. Push and open a Pull Request

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Status:** ✅ Production Ready (Ubuntu Branch)  
**Latest Commit:** OpenClaw + Ollama integration — full backend implementation  
**Tests:** 73/73 passing (backend + OpenClaw + integration tests)

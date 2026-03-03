# OpenClaw + Ollama Integration Guide

## Overview

This is the **Ubuntu integration** branch for Alkemist, adding **OpenClaw orchestration** and **Telegram bot access** on top of the existing Python backend + Next.js frontend.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Dev Machine                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           OpenClaw Gateway (18789)                   │  │
│  │  - Telegram bot handler                             │  │
│  │  - Request router & orchestrator                    │  │
│  │  - Audit logging                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────────┐      ┌──────────────────┐             │
│  │  Ollama LLM      │      │ Alkemist Backend │             │
│  │  (11434)         │      │   (8000)         │             │
│  │                  │      │  - FastAPI       │             │
│  │ • Code gen       │      │  - Logic Ladder  │             │
│  │ • Chat models    │      │  - File I/O      │             │
│  │ • Embeddings     │      │  - Terminal mgmt │             │
│  └──────────────────┘      └──────────────────┘             │
│                                    │                         │
│                                    ▼                         │
│                          ┌──────────────────┐               │
│                          │ Next.js Frontend │               │
│                          │     (3000)       │               │
│                          │  IDE UI (web)    │               │
│                          └──────────────────┘               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Telegram Bot (user interface)           │  │
│  │  - Remote access (from phone/desktop)               │  │
│  │  - Async command execution                          │  │
│  │  - Status/log streaming                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Linux/Ubuntu/macOS

```bash
chmod +x launch-alkemist-agent.sh
./launch-alkemist-agent.sh
```

### Windows

```cmd
launch-alkemist-agent.bat
```

Both scripts will:
1. ✅ Check for prerequisites (Node.js, Ollama, OpenClaw)
2. 🧠 Start Ollama LLM
3. 📥 Pull model if needed
4. 🚀 Start OpenClaw Gateway
5. 📱 Verify Telegram connectivity
6. 🎯 Display success message with next steps

All services run in the background. You can close the terminal/PowerShell.

## Prerequisites

### Required

- **Node.js 18+** — For OpenClaw execution
  ```bash
  # Install from https://nodejs.org
  node --version
  ```

- **Ollama** — Local LLM inference (CPU/GPU)
  ```bash
  # Install from https://ollama.com
  ollama --version
  ```

- **OpenClaw** — Orchestration gateway
  ```bash
  npm install -g openclaw
  openclaw --version
  ```

### Optional

- **Git** — For version control (already in repo)
- **Python Poetry** — For backend development (not needed for runtime)

### System Requirements

- **RAM:** 12–16 GB minimum (Ollama + services)
- **Disk:** 10–20 GB (Ollama models vary)
- **Network:** Localhost only (127.0.0.1) — not exposed online

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| Ollama LLM | 11434 | `http://127.0.0.1:11434` |
| OpenClaw Gateway | 18789 | `http://127.0.0.1:18789` |
| Alkemist Backend | 8000 | `http://127.0.0.1:8000` |
| Alkemist Frontend | 3000 | `http://127.0.0.1:3000` |
| ChromaDB (optional) | 8001 | `http://127.0.0.1:8001` |

## Telegram Bot Setup

### Connect Telegram

```bash
openclaw onboard
```

This will:
1. Walk you through bot creation on Telegram
2. Link your Telegram bot to OpenClaw
3. Authenticate your user ID (only you can send commands)

### Example Commands

From your Telegram bot, send:

```
/status
→ Shows running services and current project

Test Alkemist backend
→ Runs pytest on backend

Build Bool agent
→ Generates Bool code files

Check project health
→ Health check on all services

Run all tests
→ Full test suite

/logs
→ Tail recent logs
```

## Architecture Decisions

### Why OpenClaw?

- **Non-blocking UI** — Commands execute async in Telegram
- **Remote access** — Control Alkemist from phone/laptop anywhere
- **Audit trail** — Every command logged with user + timestamp
- **No new infrastructure** — Runs locally, bound to localhost

### Why Ollama?

- **Local inference** — No cloud API costs or latency
- **Privacy** — Data stays on your machine
- **Offline** — Works without internet
- **Flexible models** — Swap Mistral, Llama3, or fine-tuned variants

### Why keep Alkemist Backend + Frontend?

- **IDE experience** — Full-featured Next.js UI for complex editing
- **Dual access** — Code via web UI *or* Telegram bot, your choice
- **Separation of concerns** — OpenClaw handles routing, Alkemist handles logic

## Troubleshooting

### Ollama not responding

```bash
# Manual start (verbose output)
ollama serve

# Install models manually
ollama pull mistral
ollama list
```

### OpenClaw not starting

```bash
# Reinstall globally
npm uninstall -g openclaw
npm install -g openclaw

# Start in foreground for debugging
openclaw start
```

### Telegram bot not receiving messages

```bash
# Check configuration
openclaw status

# Re-authenticate
openclaw onboard

# Check logs
tail -f ~/.alkemist-logs/openclaw.log
```

### Port conflicts (already in use)

Close other services using the same port:

```bash
# Linux/macOS
lsof -i :11434   # Ollama
lsof -i :18789   # OpenClaw
lsof -i :8000    # Alkemist backend
lsof -i :3000    # Alkemist frontend
lsof -i :8001    # ChromaDB

# Windows
netstat -ano | find ":11434"
netstat -ano | find ":18789"
netstat -ano | find ":8000"
```

## Development

### Backend Changes

```bash
cd alkemist-server
poetry install
poetry run pytest
poetry run uvicorn main:app --reload
```

### Frontend Changes

```bash
cd alkemist-client
npm install
npm run dev
npm run type-check
npm run lint
```

### OpenClaw Integration Testing

```bash
# Test command routing
openclaw test --command "Demo"

# View request/response logs
tail -f ~/.alkemist-logs/openclaw.log
```

## Environment Variables

Optional customization (defaults work for local dev):

```bash
# Backend
export OLLAMA_BASE_URL="http://localhost:11434"
export CHROMA_HOST="localhost"
export CHROMA_PORT="8001"

# Frontend (in .env.local)
NEXT_PUBLIC_API_URL="http://localhost:8000"
NEXT_PUBLIC_WS_URL="ws://localhost:8000"

# OpenClaw
export OPENCLAW_GATEWAY_PORT="18789"
export OPENCLAW_LOG_LEVEL="info"
```

## Next Steps

1. **Run launcher** → All services start
2. **Set up Telegram** → `openclaw onboard`
3. **Send test command** → `Test Alkemist backend`
4. **Open web UI** → http://localhost:3000 (optional)
5. **Start coding** → Via Telegram or web UI

## Support

- **OpenClaw Docs:** https://docs.openclaw.ai
- **Ollama Guide:** https://github.com/ollama/ollama
- **Alkemist Issues:** Check `.github/ISSUE_TEMPLATE.md`

---

**Branch:** `feature/ubuntu-openclaw` / `ubuntu`  
**Status:** Build-Audit-Build ✅ (all tests passing)

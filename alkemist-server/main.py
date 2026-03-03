"""
Alkemist Server — FastAPI application entrypoint.

Architecture:
  - Layered monolith (single-process, multiple routers)
  - WebSocket for terminal PTY and live editor sync
  - SQLite for project/file metadata
  - ChromaDB for vector memory (RAG)
  - Ollama for local AI inference
"""

import asyncio
import json
import os
import pty
import select
import struct
import fcntl
import termios
from contextlib import asynccontextmanager
from typing import Any

import structlog
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from models.database import init_db
from routers import ai, files, projects, terminal, openclaw

logger = structlog.get_logger(__name__)

# ─── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Initialise resources on startup, clean up on shutdown."""
    logger.info("alkemist.startup")
    os.makedirs("projects", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    await init_db()
    yield
    logger.info("alkemist.shutdown")


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Alkemist",
    version="0.1.0",
    description="Local AI-native IDE backend",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(files.router, prefix="/projects", tags=["files"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(openclaw.router, prefix="", tags=["openclaw"])
app.include_router(terminal.router, prefix="", tags=["terminal"])


# ─── Health check ─────────────────────────────────────────────────────────────


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )

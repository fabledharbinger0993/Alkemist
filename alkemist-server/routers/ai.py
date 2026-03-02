"""
AI router — chat endpoint using the Sovern Logic Ladder.
"""

from typing import Annotated, Optional

import os
import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.logic_ladder import LogicLadder
from models.database import Project, get_db
from models.schemas import (
    ChatRequest,
    ChatResponse,
    ModelListResponse,
    ModelInstallRequest,
    ModelInstallResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter()

ALLOWED_INSTALL_MODELS = {
    "llama3.2:1b",
    "qwen2.5-coder:7b",
    "qwen2.5-coder:14b",
}

_logic_ladder = LogicLadder()


def _ollama_candidates() -> list[str]:
    configured = os.getenv("OLLAMA_BASE_URL", "").strip()
    candidates = [
        configured,
        "http://host.docker.internal:11434",
        "http://10.0.0.1:11434",
        "http://localhost:11434",
    ]
    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        if item and item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


async def _working_ollama_base_url() -> Optional[str]:
    for base_url in _ollama_candidates():
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{base_url}/api/tags")
                if response.status_code == 200:
                    return base_url
        except Exception:
            continue
    return None


async def _get_project_or_404(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/models", response_model=ModelListResponse)
async def list_models() -> ModelListResponse:
    """Return available local Ollama model tags for UI model selection."""
    base_url = await _working_ollama_base_url()
    if not base_url:
        logger.warning("ollama.models_unavailable", error="No reachable Ollama endpoint")
        return ModelListResponse(models=[])

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            payload = response.json()
        models = [
            item.get("name", "")
            for item in payload.get("models", [])
            if isinstance(item, dict) and item.get("name")
        ]
        return ModelListResponse(models=models)
    except Exception as exc:
        logger.warning("ollama.models_unavailable", error=str(exc))
        return ModelListResponse(models=[])


@router.post("/models/install", response_model=ModelInstallResponse)
async def install_model(payload: ModelInstallRequest) -> ModelInstallResponse:
    """Install a curated Ollama model via local Ollama server pull API."""
    model = payload.model.strip()
    if model not in ALLOWED_INSTALL_MODELS:
        raise HTTPException(status_code=400, detail="Model not allowed for one-click install")

    base_url = await _working_ollama_base_url()
    if not base_url:
        raise HTTPException(status_code=502, detail="No reachable Ollama endpoint")

    try:
        async with httpx.AsyncClient(timeout=1800.0) as client:
            response = await client.post(
                f"{base_url}/api/pull",
                json={"name": model, "stream": False},
            )
            response.raise_for_status()
        return ModelInstallResponse(
            success=True,
            message=f"Installed model: {model}",
            model=model,
        )
    except Exception as exc:
        logger.error("ollama.model_install_failed", model=model, error=str(exc))
        raise HTTPException(status_code=502, detail=f"Model install failed: {exc}")


@router.post("/{project_id}/chat", response_model=ChatResponse)
async def chat(
    project_id: str,
    payload: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatResponse:
    """
    Run user message through the Sovern Logic Ladder and return
    the structured response with reasoning steps.
    """
    project = await _get_project_or_404(project_id, db)

    result = await _logic_ladder.run(
        project_id=project_id,
        project_root=project.root_path,
        message=payload.message,
        model=payload.model,
        context_file=payload.context_file,
        context_content=payload.context_content,
        persona=payload.persona,
        app_idea=payload.app_idea,
        engineer_generate_readme=payload.engineer_generate_readme,
        engineer_generate_contractor_handoff=payload.engineer_generate_contractor_handoff,
        db=db,
    )

    return ChatResponse(
        content=result.final_output,
        reasoning_steps=[step.model_dump() for step in result.steps],
        model=payload.model,
    )

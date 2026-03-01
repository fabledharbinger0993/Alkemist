"""
AI router — chat endpoint using the Sovern Logic Ladder.
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai.logic_ladder import LogicLadder
from models.database import Project, get_db
from models.schemas import ChatRequest, ChatResponse

logger = structlog.get_logger(__name__)
router = APIRouter()

_logic_ladder = LogicLadder()


async def _get_project_or_404(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


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
        db=db,
    )

    return ChatResponse(
        content=result.final_output,
        reasoning_steps=[step.model_dump() for step in result.steps],
        model=payload.model,
    )

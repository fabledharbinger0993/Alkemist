"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ─── Projects ─────────────────────────────────────────────────────────────────


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    language: str = Field(default="python")


class ProjectResponse(BaseModel):
    id: str
    name: str
    language: str
    root_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Files ────────────────────────────────────────────────────────────────────


class FileNode(BaseModel):
    id: str
    name: str
    path: str
    isDirectory: bool
    children: Optional[list["FileNode"]] = None


class FileWrite(BaseModel):
    path: str
    content: str


class FileRead(BaseModel):
    path: str
    content: str


# ─── AI ───────────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model: str = Field(default="deepseek-v3.2")
    context_file: Optional[str] = None
    context_content: Optional[str] = None
    persona: Optional[Literal["visionary", "engineer", "contractor", "finisher"]] = None
    app_idea: Optional[str] = None
    engineer_generate_readme: bool = False
    engineer_generate_contractor_handoff: bool = False


class ReasoningStep(BaseModel):
    stage: str
    label: str
    summary: str


class ChatResponse(BaseModel):
    content: str
    reasoning_steps: list[ReasoningStep] = []
    model: str


class ModelListResponse(BaseModel):
    models: list[str] = []


class ModelInstallRequest(BaseModel):
    model: str


class ModelInstallResponse(BaseModel):
    success: bool
    message: str
    model: str


# ─── Build ────────────────────────────────────────────────────────────────────


class BuildAction(BaseModel):
    action: str  # run | build | ios_archive | ios_submit | stop


class BuildActionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    output: Optional[str] = None


# ─── Git ──────────────────────────────────────────────────────────────────────


class GitCommitRequest(BaseModel):
    message: str


class GitCommitResponse(BaseModel):
    message: str
    hash: str


class GitStatusResponse(BaseModel):
    branch: str
    status: list[str]

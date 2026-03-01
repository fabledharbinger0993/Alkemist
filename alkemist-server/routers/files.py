"""
Files router — read, write, and tree listing for project files.
"""

import hashlib
import os
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Project, get_db
from models.schemas import FileNode, FileRead, FileWrite

logger = structlog.get_logger(__name__)
router = APIRouter()

# Files larger than this are not read into memory
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

# Always-ignored directory names (never recurse into these)
IGNORED_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".venv",
    "venv",
    "DerivedData",
    ".build",
}

# Always-ignored file/dir names (OS noise)
IGNORED_NAMES = {".DS_Store", ".gitkeep", "Thumbs.db"}


# ─── Helpers ──────────────────────────────────────────────────────────────────


async def _get_project_or_404(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _build_tree(directory: Path, project_root: Path) -> list[FileNode]:
    """Recursively build a FileNode tree from a directory."""
    nodes: list[FileNode] = []
    try:
        entries = sorted(
            directory.iterdir(),
            key=lambda e: (not e.is_dir(), e.name.lower()),
        )
    except PermissionError:
        return nodes

    for entry in entries:
        if entry.name in IGNORED_DIRS or entry.name in IGNORED_NAMES:
            continue
        # Skip .git directory entries but allow other dotfiles (.env.example etc.)
        if entry.is_dir() and entry.name.startswith("."):
            continue

        rel_path = str(entry.relative_to(project_root))
        node_id = hashlib.md5(rel_path.encode()).hexdigest()[:12]

        if entry.is_dir():
            children = _build_tree(entry, project_root)
            nodes.append(
                FileNode(
                    id=node_id,
                    name=entry.name,
                    path=rel_path,
                    isDirectory=True,
                    children=children,
                )
            )
        else:
            nodes.append(
                FileNode(
                    id=node_id,
                    name=entry.name,
                    path=rel_path,
                    isDirectory=False,
                )
            )

    return nodes


# ─── Routes ───────────────────────────────────────────────────────────────────


@router.get("/{project_id}/files", response_model=list[FileNode])
async def get_file_tree(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[FileNode]:
    project = await _get_project_or_404(project_id, db)
    root = Path(project.root_path)
    if not root.exists():
        raise HTTPException(status_code=404, detail="Project directory not found")
    return _build_tree(root, root)


@router.get("/{project_id}/files/read", response_model=FileRead)
async def read_file(
    project_id: str,
    path: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> FileRead:
    project = await _get_project_or_404(project_id, db)
    root = Path(project.root_path)

    # Prevent path traversal
    target = (root / path).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if target.stat().st_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large to read")

    content = target.read_text(encoding="utf-8", errors="replace")
    return FileRead(path=path, content=content)


@router.put("/{project_id}/files/write", response_model=dict)
async def write_file(
    project_id: str,
    payload: FileWrite,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    project = await _get_project_or_404(project_id, db)
    root = Path(project.root_path)

    # Prevent path traversal
    target = (root / payload.path).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise HTTPException(status_code=400, detail="Path traversal not allowed")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload.content, encoding="utf-8")
    logger.info("file.written", project_id=project_id, path=payload.path)
    return {"status": "ok", "path": payload.path}

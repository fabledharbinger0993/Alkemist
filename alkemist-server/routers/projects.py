"""
Projects router — CRUD, Git operations, and build actions.
"""

import asyncio
import os
import shutil
import uuid
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from execution.docker_manager import DockerManager
from ios.pipeline import IOSPipeline
from models.database import Project, get_db
from models.schemas import (
    BuildAction,
    BuildActionResponse,
    GitCommitRequest,
    GitCommitResponse,
    GitStatusResponse,
    ProjectCreate,
    ProjectResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter()

PROJECTS_ROOT = Path(os.getenv("PROJECTS_ROOT", "./projects"))
docker_manager = DockerManager()
ios_pipeline = IOSPipeline()


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _project_path(project_id: str) -> Path:
    return PROJECTS_ROOT / project_id


async def _get_project_or_404(
    project_id: str, db: AsyncSession
) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _run_git(project_path: Path, *args: str) -> tuple[str, str, int]:
    """Run a git command in project_path, return (stdout, stderr, returncode)."""
    proc = await asyncio.create_subprocess_exec(
        "git",
        *args,
        cwd=str(project_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
    return stdout.decode(), stderr.decode(), proc.returncode or 0


# ─── Project CRUD ─────────────────────────────────────────────────────────────

TEMPLATES: dict[str, dict[str, str]] = {
    "python": {
        "main.py": 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/")\nasync def root():\n    return {"message": "Hello from Alkemist"}\n',
        "requirements.txt": "fastapi\nuvicorn[standard]\n",
        "README.md": "# My Python Project\n",
    },
    "typescript": {
        "index.ts": 'import express from "express";\n\nconst app = express();\nconst PORT = process.env.PORT ?? 3001;\n\napp.get("/", (_req, res) => res.json({ message: "Hello from Alkemist" }));\n\napp.listen(PORT, () => console.log(`Server running on port ${PORT}`));\n',
        "package.json": '{\n  "name": "my-node-project",\n  "version": "1.0.0",\n  "scripts": { "start": "ts-node index.ts", "dev": "ts-node-dev index.ts" },\n  "dependencies": { "express": "^4.21.0" },\n  "devDependencies": { "typescript": "^5.7.0", "ts-node": "^10.9.0", "@types/express": "^5.0.0" }\n}\n',
        "tsconfig.json": '{\n  "compilerOptions": {\n    "target": "ES2022",\n    "module": "commonjs",\n    "strict": true,\n    "outDir": "dist"\n  }\n}\n',
        "README.md": "# My TypeScript Project\n",
    },
    "swift": {
        "ContentView.swift": 'import SwiftUI\n\nstruct ContentView: View {\n    var body: some View {\n        VStack {\n            Image(systemName: "globe")\n                .imageScale(.large)\n                .foregroundStyle(.tint)\n            Text("Hello, Alkemist!")\n        }\n        .padding()\n    }\n}\n\n#Preview {\n    ContentView()\n}\n',
        "App.swift": 'import SwiftUI\n\n@main\nstruct AlkemistApp: App {\n    var body: some Scene {\n        WindowGroup {\n            ContentView()\n        }\n    }\n}\n',
        "README.md": "# My SwiftUI Project\n",
    },
    "rust": {
        "src/main.rs": 'fn main() {\n    println!("Hello from Alkemist!");\n}\n',
        "Cargo.toml": '[package]\nname = "my-rust-project"\nversion = "0.1.0"\nedition = "2021"\n\n[dependencies]\n',
        "README.md": "# My Rust Project\n",
    },
    "go": {
        "main.go": 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello from Alkemist!")\n}\n',
        "go.mod": 'module myproject\n\ngo 1.22\n',
        "README.md": "# My Go Project\n",
    },
}


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: Annotated[AsyncSession, Depends(get_db)]) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Project:
    project_id = str(uuid.uuid4())
    root_path = str(PROJECTS_ROOT / project_id)

    # Scaffold directory with template files
    project_dir = Path(root_path)
    project_dir.mkdir(parents=True, exist_ok=True)

    template = TEMPLATES.get(payload.language, TEMPLATES["python"])
    for rel_path, content in template.items():
        file_path = project_dir / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    # Initialize git if available; scaffolding should still succeed without it.
    git_initialized = False
    try:
        _, stderr, rc = await _run_git(project_dir, "init")
        if rc != 0:
            logger.warning("project.git_init_failed", project_id=project_id, stderr=stderr)
        else:
            _, stderr, rc = await _run_git(project_dir, "add", "-A")
            if rc != 0:
                logger.warning(
                    "project.git_add_failed", project_id=project_id, stderr=stderr
                )
            else:
                _, stderr, rc = await _run_git(
                    project_dir,
                    "-c",
                    "user.email=alkemist@local",
                    "-c",
                    "user.name=Alkemist",
                    "commit",
                    "-m",
                    "chore: initial scaffold",
                )
                if rc != 0:
                    logger.warning(
                        "project.git_commit_failed",
                        project_id=project_id,
                        stderr=stderr,
                    )
                else:
                    git_initialized = True
    except Exception as exc:
        logger.warning("project.git_init_exception", project_id=project_id, error=str(exc))

    project = Project(
        id=project_id,
        name=payload.name,
        language=payload.language,
        root_path=root_path,
        git_initialized=git_initialized,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    logger.info("project.created", id=project_id, name=payload.name)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    project = await _get_project_or_404(project_id, db)
    path = Path(project.root_path)
    if path.exists():
        shutil.rmtree(path)
    await db.delete(project)
    await db.commit()
    logger.info("project.deleted", id=project_id)


# ─── Build actions ────────────────────────────────────────────────────────────


@router.post("/{project_id}/build", response_model=BuildActionResponse)
async def build_action(
    project_id: str,
    payload: BuildAction,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BuildActionResponse:
    project = await _get_project_or_404(project_id, db)
    project_path = Path(project.root_path)

    if payload.action == "run":
        output = await docker_manager.run_project(
            project_id, project_path, project.language
        )
        return BuildActionResponse(success=True, output=output)

    if payload.action == "build":
        if project.language == "swift":
            result = await ios_pipeline.build(project_path)
            return BuildActionResponse(
                success=result.success, message=result.message, output=result.output
            )
        output = await docker_manager.build_project(
            project_id, project_path, project.language
        )
        return BuildActionResponse(success=True, output=output)

    if payload.action == "ios_archive":
        result = await ios_pipeline.archive(project_path)
        return BuildActionResponse(
            success=result.success, message=result.message, output=result.output
        )

    if payload.action == "ios_submit":
        result = await ios_pipeline.submit(project_path)
        return BuildActionResponse(
            success=result.success, message=result.message, output=result.output
        )

    if payload.action == "stop":
        await docker_manager.stop_container(project_id)
        return BuildActionResponse(success=True, message="Container stopped")

    raise HTTPException(status_code=400, detail=f"Unknown action: {payload.action}")


# ─── Git operations ───────────────────────────────────────────────────────────


@router.post("/{project_id}/git/init")
async def git_init(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    project = await _get_project_or_404(project_id, db)
    project_path = Path(project.root_path)
    stdout, stderr, code = await _run_git(project_path, "init")
    if code != 0:
        raise HTTPException(status_code=500, detail=stderr)
    project.git_initialized = True
    await db.commit()
    return {"message": stdout or "Git initialized"}


@router.post("/{project_id}/git/commit", response_model=GitCommitResponse)
async def git_commit(
    project_id: str,
    payload: GitCommitRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GitCommitResponse:
    project = await _get_project_or_404(project_id, db)
    project_path = Path(project.root_path)

    await _run_git(project_path, "add", "-A")
    stdout, stderr, code = await _run_git(
        project_path,
        "-c",
        "user.email=alkemist@local",
        "-c",
        "user.name=Alkemist",
        "commit",
        "-m",
        payload.message,
    )
    if code != 0 and "nothing to commit" not in stderr:
        raise HTTPException(status_code=500, detail=stderr)

    # Get commit hash
    hash_out, _, _ = await _run_git(project_path, "rev-parse", "HEAD")
    return GitCommitResponse(
        message=payload.message, hash=hash_out.strip()[:8]
    )


@router.get("/{project_id}/git/status", response_model=GitStatusResponse)
async def git_status(
    project_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GitStatusResponse:
    project = await _get_project_or_404(project_id, db)
    project_path = Path(project.root_path)

    branch_out, _, _ = await _run_git(
        project_path, "rev-parse", "--abbrev-ref", "HEAD"
    )
    status_out, _, _ = await _run_git(project_path, "status", "--short")
    status_lines = [l for l in status_out.splitlines() if l.strip()]

    return GitStatusResponse(
        branch=branch_out.strip() or "main",
        status=status_lines,
    )

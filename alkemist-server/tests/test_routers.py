"""
Integration tests for Alkemist HTTP API endpoints.

Uses an in-memory SQLite database and an httpx AsyncClient with ASGITransport
so the full request/response cycle is exercised without a live server.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app
from models.database import Base, get_db


# ─── In-memory DB fixtures ────────────────────────────────────────────────────


@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def client(db_engine):
    """Provide an AsyncClient wired to the FastAPI app with an in-memory DB."""
    Session = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _get_db():
        async with Session() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ─── Health ───────────────────────────────────────────────────────────────────


async def test_health_returns_ok(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


# ─── Projects — list ─────────────────────────────────────────────────────────


async def test_list_projects_empty(client: AsyncClient) -> None:
    resp = await client.get("/projects")
    assert resp.status_code == 200
    assert resp.json() == []


# ─── Projects — create / delete ──────────────────────────────────────────────


async def test_create_project_returns_201(
    client: AsyncClient, tmp_path: Path
) -> None:
    with patch("routers.projects.PROJECTS_ROOT", tmp_path):
        resp = await client.post(
            "/projects", json={"name": "My App", "language": "python"}
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My App"
    assert data["language"] == "python"
    assert "id" in data


async def test_create_project_appears_in_list(
    client: AsyncClient, tmp_path: Path
) -> None:
    with patch("routers.projects.PROJECTS_ROOT", tmp_path):
        await client.post(
            "/projects", json={"name": "Listed App", "language": "typescript"}
        )

    resp = await client.get("/projects")
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "Listed App"


async def test_delete_project_removes_record(
    client: AsyncClient, tmp_path: Path
) -> None:
    with patch("routers.projects.PROJECTS_ROOT", tmp_path):
        create_resp = await client.post(
            "/projects", json={"name": "Temp", "language": "python"}
        )
    project_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/projects/{project_id}")
    assert delete_resp.status_code == 204

    list_resp = await client.get("/projects")
    assert list_resp.json() == []


async def test_delete_nonexistent_project_returns_404(
    client: AsyncClient,
) -> None:
    resp = await client.delete("/projects/does-not-exist")
    assert resp.status_code == 404


# ─── Projects — validation ────────────────────────────────────────────────────


async def test_create_project_empty_name_rejected(
    client: AsyncClient,
) -> None:
    resp = await client.post("/projects", json={"name": "", "language": "python"})
    assert resp.status_code == 422  # Pydantic validation error


# ─── Files ────────────────────────────────────────────────────────────────────


@pytest.fixture
async def created_project(client: AsyncClient, tmp_path: Path) -> dict:
    """Helper: create a project and return the JSON response body."""
    with patch("routers.projects.PROJECTS_ROOT", tmp_path):
        resp = await client.post(
            "/projects", json={"name": "FileTest", "language": "python"}
        )
    assert resp.status_code == 201
    return resp.json()


async def test_get_file_tree_returns_list(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.get(f"/projects/{created_project['id']}/files")
    assert resp.status_code == 200
    nodes = resp.json()
    assert isinstance(nodes, list)
    # Python template creates main.py, requirements.txt, README.md
    names = [n["name"] for n in nodes]
    assert "main.py" in names


async def test_read_file_returns_content(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.get(
        f"/projects/{created_project['id']}/files/read",
        params={"path": "main.py"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert "path" in data
    assert "fastapi" in data["content"].lower()


async def test_write_then_read_file(
    client: AsyncClient, created_project: dict
) -> None:
    project_id = created_project["id"]

    write_resp = await client.put(
        f"/projects/{project_id}/files/write",
        json={"path": "hello.txt", "content": "hello world"},
    )
    assert write_resp.status_code == 200

    read_resp = await client.get(
        f"/projects/{project_id}/files/read",
        params={"path": "hello.txt"},
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["content"] == "hello world"


async def test_read_nonexistent_file_returns_404(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.get(
        f"/projects/{created_project['id']}/files/read",
        params={"path": "does_not_exist.py"},
    )
    assert resp.status_code == 404


async def test_read_file_path_traversal_rejected(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.get(
        f"/projects/{created_project['id']}/files/read",
        params={"path": "../../etc/passwd"},
    )
    assert resp.status_code == 400


async def test_write_file_path_traversal_rejected(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.put(
        f"/projects/{created_project['id']}/files/write",
        json={"path": "../../evil.txt", "content": "bad"},
    )
    assert resp.status_code == 400


async def test_get_file_tree_project_not_found(
    client: AsyncClient,
) -> None:
    resp = await client.get("/projects/nonexistent/files")
    assert resp.status_code == 404


# ─── Git endpoints ────────────────────────────────────────────────────────────


async def test_git_status_returns_branch(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.get(f"/projects/{created_project['id']}/git/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "branch" in data
    assert "status" in data


async def test_git_commit_succeeds(
    client: AsyncClient, created_project: dict
) -> None:
    # Write a file first so there's something to commit
    project_id = created_project["id"]
    await client.put(
        f"/projects/{project_id}/files/write",
        json={"path": "new_file.py", "content": "x = 1"},
    )

    resp = await client.post(
        f"/projects/{project_id}/git/commit",
        json={"message": "test: add new_file"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "test: add new_file"
    assert len(data["hash"]) == 8


# ─── Build action — unknown action rejected ──────────────────────────────────


async def test_build_action_unknown_returns_400(
    client: AsyncClient, created_project: dict
) -> None:
    resp = await client.post(
        f"/projects/{created_project['id']}/build",
        json={"action": "explode"},
    )
    assert resp.status_code == 400

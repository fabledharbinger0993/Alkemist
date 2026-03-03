"""
Tests for OpenClaw router (Telegram integration via webhook).
"""

import json
from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.database import Project, Base
from routers.openclaw import TelegramCommand, openclaw_webhook, openclaw_status
from fastapi.testclient import TestClient
from main import app

# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
async def test_db():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker_inst = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_sessionmaker_inst() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def sample_project(test_db: AsyncSession):
    """Create a sample project for testing."""
    project = Project(
        id="test-project-123",
        name="Test Project",
        root_path="/tmp/test-project",
    )
    test_db.add(project)
    await test_db.commit()
    return project


# ─── Test TelegramCommand Parser ───────────────────────────────────────────────


def test_telegram_command_slash_status():
    """Parse slash command."""
    cmd = TelegramCommand("/status")
    assert cmd.command == "status"
    assert cmd.raw == "/status"


def test_telegram_command_natural_language_test():
    """Parse natural language 'test' command."""
    cmd = TelegramCommand("test alkemist backend")
    assert cmd.command == "test"


def test_telegram_command_natural_language_health():
    """Parse natural language 'health' command."""
    cmd = TelegramCommand("check if everything is working")
    assert cmd.command == "health"


def test_telegram_command_natural_language_chat():
    """Parse natural language 'chat' command (default)."""
    cmd = TelegramCommand("what is the meaning of life?")
    assert cmd.command == "chat"


def test_telegram_command_with_project_id():
    """Extract project ID from command."""
    cmd = TelegramCommand("test --project abc-def-123")
    assert cmd.command == "test"
    assert cmd.args.get("project_id") == "abc-def-123"


def test_telegram_command_whitespace_handling():
    """Handle leading/trailing whitespace."""
    cmd = TelegramCommand("   /help   ")
    assert cmd.command == "help"


# ─── Test OpenClaw Webhook Handler ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_openclaw_webhook_missing_user_id(test_db: AsyncSession):
    """Reject webhook missing user_id."""
    client = TestClient(app)
    payload = {"message": "test", "project_id": "123"}

    with patch("routers.openclaw.get_db", return_value=test_db):
        response = client.post("/openclaw/webhook", json=payload)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_openclaw_webhook_missing_message(test_db: AsyncSession):
    """Reject webhook missing message."""
    client = TestClient(app)
    payload = {"user_id": "user123", "project_id": "123"}

    with patch("routers.openclaw.get_db", return_value=test_db):
        response = client.post("/openclaw/webhook", json=payload)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_openclaw_webhook_invalid_json(test_db: AsyncSession):
    """Reject invalid JSON."""
    client = TestClient(app)

    with patch("routers.openclaw.get_db", return_value=test_db):
        response = client.post("/openclaw/webhook", content="not-json", headers={})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_openclaw_webhook_missing_project(test_db: AsyncSession):
    """Return error when project not found."""
    client = TestClient(app)
    payload = {
        "user_id": "user123",
        "message": "/status",
        "project_id": "nonexistent",
    }

    with patch("routers.openclaw.get_db", return_value=test_db):
        response = client.post("/openclaw/webhook", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "Error" in data.get("response", "")


# ─── Test OpenClaw Status Endpoint ────────────────────────────────────────────


def test_openclaw_status():
    """Test status endpoint."""
    client = TestClient(app)
    response = client.get("/openclaw/status")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "openclaw"
    assert data["status"] == "active"
    assert "endpoints" in data
    assert "commands" in data
    assert isinstance(data["commands"], list)
    assert len(data["commands"]) == 7  # status, test, build, health, logs, help, chat


# ─── Test Command Parsing Edge Cases ───────────────────────────────────────────


def test_telegram_command_log_command():
    """Parse 'logs' command."""
    cmd = TelegramCommand("/logs")
    assert cmd.command == "logs"


def test_telegram_command_build_variant():
    """Parse build command variant."""
    cmd = TelegramCommand("generate files please")
    assert cmd.command == "build"


def test_telegram_command_empty_message():
    """Handle empty message (default to chat)."""
    cmd = TelegramCommand("")
    assert cmd.command == "chat"


def test_telegram_command_case_insensitive():
    """Commands should be case-insensitive."""
    cmd1 = TelegramCommand("/STATUS")
    cmd2 = TelegramCommand("/Status")
    assert cmd1.command == cmd2.command == "status"


# ─── Test Response Format ──────────────────────────────────────────────────────


def test_openclaw_response_has_timestamp():
    """All responses should include timestamp."""
    client = TestClient(app)
    response = client.get("/openclaw/status")
    data = response.json()
    assert "timestamp" in data
    # Verify ISO8601 format (with or without Z suffix)
    assert "T" in data["timestamp"]  # ISO8601 format includes T

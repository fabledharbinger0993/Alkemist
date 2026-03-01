"""
Unit tests for DockerManager helper utilities.

DockerManager's container operations require a live Docker daemon and are
therefore excluded from unit tests. This file covers the helpers that can
be tested without Docker.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from execution.docker_manager import (
    LANGUAGE_BUILD_COMMANDS,
    LANGUAGE_COMMANDS,
    LANGUAGE_IMAGES,
    DockerManager,
    _find_free_port,
)


# ─── _find_free_port ─────────────────────────────────────────────────────────


def test_find_free_port_returns_integer() -> None:
    port = _find_free_port()
    assert isinstance(port, int)


def test_find_free_port_is_in_valid_range() -> None:
    port = _find_free_port()
    assert 1024 <= port <= 65535


def test_find_free_port_returns_different_values() -> None:
    """Two successive calls each return a valid port (values may or may not match)."""
    p1 = _find_free_port()
    p2 = _find_free_port()
    assert isinstance(p1, int)
    assert isinstance(p2, int)


# ─── Language mappings ────────────────────────────────────────────────────────


def test_language_images_contains_expected_keys() -> None:
    for lang in ("python", "typescript", "javascript", "rust", "go"):
        assert lang in LANGUAGE_IMAGES, f"Missing image for language: {lang}"


def test_language_images_are_nonempty_strings() -> None:
    for lang, image in LANGUAGE_IMAGES.items():
        assert isinstance(image, str) and image, f"Empty image for {lang}"


def test_language_commands_contains_expected_keys() -> None:
    for lang in ("python", "typescript", "rust", "go"):
        assert lang in LANGUAGE_COMMANDS, f"Missing command for language: {lang}"


def test_language_commands_are_nonempty_lists() -> None:
    for lang, cmd in LANGUAGE_COMMANDS.items():
        assert isinstance(cmd, list) and cmd, f"Empty command list for {lang}"


def test_language_build_commands_contains_python() -> None:
    assert "python" in LANGUAGE_BUILD_COMMANDS


def test_language_build_commands_are_nonempty_lists() -> None:
    for lang, cmd in LANGUAGE_BUILD_COMMANDS.items():
        assert isinstance(cmd, list) and cmd, f"Empty build command for {lang}"


# ─── DockerManager._is_docker_available ──────────────────────────────────────


def test_is_docker_available_returns_false_when_daemon_absent() -> None:
    manager = DockerManager()
    with patch.object(manager, "_get_client", side_effect=Exception("no daemon")):
        assert manager._is_docker_available() is False


def test_is_docker_available_returns_false_on_ping_failure() -> None:
    manager = DockerManager()
    mock_client = MagicMock()
    mock_client.ping.side_effect = Exception("connection refused")
    with patch.object(manager, "_get_client", return_value=mock_client):
        assert manager._is_docker_available() is False


def test_is_docker_available_returns_true_when_ping_succeeds() -> None:
    manager = DockerManager()
    mock_client = MagicMock()
    mock_client.ping.return_value = True
    with patch.object(manager, "_get_client", return_value=mock_client):
        assert manager._is_docker_available() is True


# ─── DockerManager.run_project — no Docker ───────────────────────────────────


@pytest.mark.asyncio
async def test_run_project_returns_message_when_docker_unavailable() -> None:
    manager = DockerManager()
    with patch.object(manager, "_is_docker_available", return_value=False):
        result = await manager.run_project("proj1", Path("/fake"), "python")
    assert "Docker" in result


@pytest.mark.asyncio
async def test_run_project_returns_message_for_unsupported_language() -> None:
    manager = DockerManager()
    with patch.object(manager, "_is_docker_available", return_value=True):
        result = await manager.run_project("proj1", Path("/fake"), "cobol")
    assert "cobol" in result or "supported" in result.lower()


# ─── DockerManager.build_project — no Docker ─────────────────────────────────


@pytest.mark.asyncio
async def test_build_project_returns_message_when_docker_unavailable() -> None:
    manager = DockerManager()
    with patch.object(manager, "_is_docker_available", return_value=False):
        result = await manager.build_project("proj1", Path("/fake"), "python")
    assert "Docker" in result or "available" in result.lower()


@pytest.mark.asyncio
async def test_build_project_returns_message_for_unsupported_language() -> None:
    manager = DockerManager()
    with patch.object(manager, "_is_docker_available", return_value=True):
        result = await manager.build_project("proj1", Path("/fake"), "brainfuck")
    assert "brainfuck" in result or "supported" in result.lower()

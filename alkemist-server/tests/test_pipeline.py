"""
Unit tests for the iOS build pipeline.

Tests are isolated from real xcodebuild/notarytool using mocks.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ios.pipeline import IOSPipeline, PipelineResult, _find_xcodeproj, _find_scheme


# ─── Helpers ──────────────────────────────────────────────────────────────────


def make_pipeline() -> IOSPipeline:
    return IOSPipeline()


# ─── _find_xcodeproj ──────────────────────────────────────────────────────────


def test_find_xcodeproj_returns_none_when_missing(tmp_path: Path) -> None:
    assert _find_xcodeproj(tmp_path) is None


def test_find_xcodeproj_returns_path_when_present(tmp_path: Path) -> None:
    proj = tmp_path / "MyApp.xcodeproj"
    proj.mkdir()
    result = _find_xcodeproj(tmp_path)
    assert result == proj


def test_find_scheme_derives_from_name() -> None:
    p = Path("/some/path/MyApp.xcodeproj")
    assert _find_scheme(p) == "MyApp"


# ─── Build (non-macOS) ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_fails_on_linux() -> None:
    pipeline = make_pipeline()
    with patch("ios.pipeline._is_macos", return_value=False):
        result = await pipeline.build(Path("/fake"))
    assert not result.success
    assert "macOS" in result.message


# ─── Archive (non-macOS) ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_archive_fails_on_linux() -> None:
    pipeline = make_pipeline()
    with patch("ios.pipeline._is_macos", return_value=False):
        result = await pipeline.archive(Path("/fake"))
    assert not result.success
    assert "macOS" in result.message


# ─── Submit (non-macOS) ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_fails_on_linux() -> None:
    pipeline = make_pipeline()
    with patch("ios.pipeline._is_macos", return_value=False):
        result = await pipeline.submit(Path("/fake"))
    assert not result.success
    assert "macOS" in result.message


# ─── Build (macOS mocked) ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_fails_when_no_xcodeproj(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    with patch("ios.pipeline._is_macos", return_value=True):
        result = await pipeline.build(tmp_path)
    assert not result.success
    assert "xcodeproj" in result.message.lower()


@pytest.mark.asyncio
async def test_build_success(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    (tmp_path / "MyApp.xcodeproj").mkdir()

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch(
            "ios.pipeline._run_command",
            AsyncMock(return_value=("Build succeeded\n", "", 0)),
        ),
    ):
        result = await pipeline.build(tmp_path)

    assert result.success
    assert "succeeded" in result.message


@pytest.mark.asyncio
async def test_build_failure_propagates_output(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    (tmp_path / "MyApp.xcodeproj").mkdir()

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch(
            "ios.pipeline._run_command",
            AsyncMock(return_value=("", "error: Build failed\n", 1)),
        ),
    ):
        result = await pipeline.build(tmp_path)

    assert not result.success
    assert "failed" in result.message.lower()


# ─── Archive (macOS mocked) ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_archive_success(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    (tmp_path / "MyApp.xcodeproj").mkdir()
    (tmp_path / "build").mkdir(parents=True, exist_ok=True)

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch(
            "ios.pipeline._run_command",
            AsyncMock(return_value=("Archive succeeded\n", "", 0)),
        ),
    ):
        result = await pipeline.archive(tmp_path)

    assert result.success


@pytest.mark.asyncio
async def test_archive_export_fails_after_archive(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    (tmp_path / "MyApp.xcodeproj").mkdir()

    call_count = 0

    async def mock_run(*args: object, **kwargs: object) -> tuple[str, str, int]:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return ("Archive OK\n", "", 0)
        return ("", "Export failed\n", 1)

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch("ios.pipeline._run_command", mock_run),
    ):
        result = await pipeline.archive(tmp_path)

    assert not result.success
    assert "export failed" in result.message.lower()


# ─── Submit pipeline ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_returns_archive_failure_early(tmp_path: Path) -> None:
    pipeline = make_pipeline()

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch.object(
            pipeline,
            "archive",
            AsyncMock(return_value=PipelineResult(success=False, message="Archive failed")),
        ),
    ):
        result = await pipeline.submit(tmp_path)

    assert not result.success
    assert "Archive failed" in result.message


@pytest.mark.asyncio
async def test_submit_fails_when_no_ipa_found(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    (tmp_path / "build").mkdir()

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch.object(
            pipeline,
            "archive",
            AsyncMock(return_value=PipelineResult(success=True, message="ok")),
        ),
    ):
        result = await pipeline.submit(tmp_path)

    assert not result.success
    assert "No IPA" in result.message


@pytest.mark.asyncio
async def test_submit_full_success(tmp_path: Path) -> None:
    pipeline = make_pipeline()
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "MyApp.ipa").write_bytes(b"fake ipa")

    with (
        patch("ios.pipeline._is_macos", return_value=True),
        patch.object(
            pipeline,
            "archive",
            AsyncMock(return_value=PipelineResult(success=True, message="ok", output="archived")),
        ),
        patch.object(
            pipeline,
            "notarize",
            AsyncMock(return_value=PipelineResult(success=True, message="notarized", output="notarized")),
        ),
        patch(
            "ios.pipeline._run_command",
            AsyncMock(return_value=("Upload complete\n", "", 0)),
        ),
    ):
        result = await pipeline.submit(tmp_path)

    assert result.success
    assert "App Store" in result.message

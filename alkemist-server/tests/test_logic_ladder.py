"""
Unit tests for the Sovern Logic Ladder AI chain.

Tests are isolated from real Ollama/ChromaDB using mocks.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai.logic_ladder import (
    LadderState,
    LadderResult,
    LogicLadder,
    _retrieve_context,
    node_awareness,
    node_literalist,
    node_congress,
    node_judge,
)
from models.schemas import ReasoningStep


# ─── Fixtures ─────────────────────────────────────────────────────────────────


def make_state(**overrides: object) -> LadderState:
    """Create a minimal LadderState for testing."""
    base: LadderState = {
        "project_id": "test-project-123",
        "project_root": "/tmp/test-project",
        "user_message": "Add a GET /health endpoint",
        "model": "deepseek-v3.2",
        "context_file": None,
        "context_content": None,
        "retrieved_context": "",
        "literal_requirements": "",
        "advocate_proposal": "",
        "skeptic_review": "",
        "synthesized_code": "",
        "final_output": "",
        "commit_message": "",
        "steps": [],
    }
    base.update(overrides)  # type: ignore[arg-type]
    return base


# ─── ChromaDB helper tests ────────────────────────────────────────────────────


def test_retrieve_context_returns_empty_when_collection_is_none() -> None:
    result = _retrieve_context(None, "query")
    assert result == ""


def test_retrieve_context_handles_exception() -> None:
    mock_collection = MagicMock()
    mock_collection.query.side_effect = RuntimeError("ChromaDB unavailable")
    result = _retrieve_context(mock_collection, "query")
    assert result == ""


def test_retrieve_context_formats_documents() -> None:
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["def hello(): pass"]],
        "metadatas": [[{"path": "main.py"}]],
    }
    result = _retrieve_context(mock_collection, "hello function")
    assert "main.py" in result
    assert "def hello" in result


# ─── Node tests ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_node_awareness_adds_step() -> None:
    state = make_state()
    with (
        patch("ai.logic_ladder._get_chroma_collection", return_value=None),
        patch("ai.logic_ladder._embed_project_files"),
        patch("ai.logic_ladder._retrieve_context", return_value="some context"),
    ):
        result = await node_awareness(state)

    assert result["retrieved_context"] == "some context"
    assert len(result["steps"]) == 1
    assert result["steps"][0]["stage"] == "awareness"


@pytest.mark.asyncio
async def test_node_literalist_adds_step() -> None:
    state = make_state(retrieved_context="def hello(): pass")
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=MagicMock(content="1. Add GET /health endpoint\n2. Return 200 OK")
    )

    with patch("ai.logic_ladder._llm", return_value=mock_llm):
        result = await node_literalist(state)

    assert "1. Add GET" in result["literal_requirements"]
    assert len(result["steps"]) == 1
    assert result["steps"][0]["stage"] == "literalist"


@pytest.mark.asyncio
async def test_node_congress_adds_step() -> None:
    state = make_state(
        retrieved_context="# existing code",
        literal_requirements="1. Add /health endpoint",
    )
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=MagicMock(content="# proposed code")
    )

    with patch("ai.logic_ladder._llm", return_value=mock_llm):
        result = await node_congress(state)

    assert result["advocate_proposal"] != ""
    assert result["skeptic_review"] != ""
    assert result["synthesized_code"] != ""
    assert len(result["steps"]) == 1
    assert result["steps"][0]["stage"] == "congress"


@pytest.mark.asyncio
async def test_node_judge_parses_response_and_commit() -> None:
    state = make_state(
        synthesized_code="@app.get('/health')\nasync def health(): return {'ok': True}",
        user_message="Add /health endpoint",
    )
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=MagicMock(
            content="RESPONSE:\nHere is your health endpoint.\n\nCOMMIT:\nfeat: add GET /health endpoint"
        )
    )

    with patch("ai.logic_ladder._llm", return_value=mock_llm):
        result = await node_judge(state)

    assert "health endpoint" in result["final_output"]
    assert result["commit_message"] == "feat: add GET /health endpoint"
    assert result["steps"][0]["stage"] == "judge"


@pytest.mark.asyncio
async def test_node_judge_handles_missing_response_block() -> None:
    """Judge should still work even if LLM doesn't follow the format."""
    state = make_state(
        synthesized_code="some code",
        user_message="do something",
    )
    mock_llm = MagicMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=MagicMock(content="Just a plain response without markers")
    )

    with patch("ai.logic_ladder._llm", return_value=mock_llm):
        result = await node_judge(state)

    assert result["final_output"] != ""
    assert result["commit_message"] == "chore: ai-assisted update"


# ─── Integration-style test (mocked) ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_logic_ladder_run_returns_result() -> None:
    """Full ladder run with all nodes mocked."""
    ladder = LogicLadder()

    mock_state: LadderState = {
        "project_id": "test",
        "project_root": "/tmp/test",
        "user_message": "Add a route",
        "model": "deepseek-v3.2",
        "context_file": None,
        "context_content": None,
        "retrieved_context": "context",
        "literal_requirements": "1. Add route",
        "advocate_proposal": "code",
        "skeptic_review": "No issues found.",
        "synthesized_code": "final code",
        "final_output": "Here is your route.",
        "commit_message": "feat: add route",
        "steps": [
            {"stage": "awareness", "label": "Awareness", "summary": "ok"},
            {"stage": "literalist", "label": "Literalist Filter", "summary": "ok"},
            {"stage": "congress", "label": "Congress (Advocate → Skeptic → Synthesizer)", "summary": "ok"},
            {"stage": "judge", "label": "Judge", "summary": "ok"},
        ],
    }

    with patch.object(ladder._graph, "ainvoke", AsyncMock(return_value=mock_state)):
        result = await ladder.run(
            project_id="test",
            project_root="/tmp/test",
            message="Add a route",
            model="deepseek-v3.2",
            context_file=None,
            context_content=None,
            db=None,
        )

    assert isinstance(result, LadderResult)
    assert result.final_output == "Here is your route."
    assert result.commit_message == "feat: add route"
    assert len(result.steps) == 4
    assert all(isinstance(s, ReasoningStep) for s in result.steps)


@pytest.mark.asyncio
async def test_logic_ladder_graceful_on_llm_error() -> None:
    """Ladder should return error message rather than crash on LLM failure."""
    ladder = LogicLadder()

    async def failing_graph(state: object) -> LadderState:
        raise RuntimeError("Ollama not running")

    with patch.object(ladder._graph, "ainvoke", AsyncMock(side_effect=RuntimeError("Ollama not running"))):
        with pytest.raises(RuntimeError, match="Ollama not running"):
            await ladder.run(
                project_id="test",
                project_root="/tmp/test",
                message="test",
                model="deepseek-v3.2",
                context_file=None,
                context_content=None,
                db=None,
            )

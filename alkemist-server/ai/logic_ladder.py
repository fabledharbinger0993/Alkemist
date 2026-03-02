"""
Sovern Logic Ladder — structured AI reasoning chain implemented with LangGraph.

Stages:
  1. Awareness     — Capture user intent + embed/retrieve codebase context (RAG)
  2. Literalist    — Extract raw functional requirements (no metaphors)
  3. Congress      — Advocate → Skeptic → Synthesizer agents
  4. Judge         — Output final response + commit message + log to memory

Each stage is a LangGraph node. The graph is compiled once and reused.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, TypedDict

import structlog
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import MemoryLog
from models.schemas import ReasoningStep

logger = structlog.get_logger(__name__)

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))



def _ollama_base_url_candidates() -> list[str]:
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


def _resolve_ollama_base_url() -> str:
    for base_url in _ollama_base_url_candidates():
        try:
            with urllib.request.urlopen(f"{base_url}/api/tags", timeout=1.5):
                return base_url
        except Exception:
            continue
    return "http://localhost:11434"

PERSONA_PROFILES: dict[str, str] = {
    "visionary": (
        "Explain in plain language, focus on product direction, and provide quick phased milestones. "
        "Call out where the app is now and where it can go next."
    ),
    "engineer": (
        "Be technical and detail-oriented. Ask direct clarification questions when requirements are ambiguous. "
        "Prioritize correctness, architecture, and edge cases."
    ),
    "contractor": (
        "Execute fast and thoroughly. Focus on implementation steps, safety, testing loops, and backend/frontend checks."
    ),
    "finisher": (
        "Prioritize polish and visual quality. Recommend coherent UI style direction while preserving usability and consistency."
    ),
}


def _persona_guidance(state: LadderState) -> str:
    persona = (state.get("persona") or "engineer").lower()
    return PERSONA_PROFILES.get(persona, PERSONA_PROFILES["engineer"])


def _app_idea_text(state: LadderState) -> str:
    idea = (state.get("app_idea") or "").strip()
    return idea if idea else "No app idea provided yet."

# ─── State ────────────────────────────────────────────────────────────────────


class LadderState(TypedDict):
    # Inputs
    project_id: str
    project_root: str
    user_message: str
    model: str
    context_file: Optional[str]
    context_content: Optional[str]
    persona: Optional[str]
    app_idea: Optional[str]
    engineer_generate_readme: bool
    engineer_generate_contractor_handoff: bool

    # Intermediate
    retrieved_context: str
    literal_requirements: str
    advocate_proposal: str
    skeptic_review: str
    synthesized_code: str

    # Output
    final_output: str
    commit_message: str
    steps: list[dict[str, str]]


# ─── Result ───────────────────────────────────────────────────────────────────


@dataclass
class LadderResult:
    final_output: str
    commit_message: str
    steps: list[ReasoningStep] = field(default_factory=list)


# ─── ChromaDB helper ──────────────────────────────────────────────────────────


def _get_chroma_collection(project_id: str) -> Any:
    """Return (or create) a ChromaDB collection for the project."""
    try:
        import chromadb

        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        # Sanitise collection name (alphanumeric + underscores only)
        safe_id = "".join(c if c.isalnum() else "_" for c in project_id)
        return client.get_or_create_collection(f"project_{safe_id}")
    except Exception as exc:
        logger.warning("chroma.unavailable", error=str(exc))
        return None


def _embed_project_files(collection: Any, project_root: str) -> None:
    """Walk project files and upsert text chunks into ChromaDB."""
    if collection is None:
        return
    root = Path(project_root)
    ignored = {".git", "__pycache__", "node_modules", ".next", "dist", ".build"}
    for file_path in root.rglob("*"):
        if any(p in file_path.parts for p in ignored):
            continue
        if not file_path.is_file():
            continue
        # Only index text files < 500 KB
        if file_path.stat().st_size > 500_000:
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(file_path.relative_to(root))
        doc_id = hashlib.md5(rel.encode()).hexdigest()
        try:
            collection.upsert(
                ids=[doc_id],
                documents=[content[:8000]],  # Truncate for embedding
                metadatas=[{"path": rel}],
            )
        except Exception as exc:
            logger.debug("chroma.upsert_failed", path=rel, error=str(exc))


def _retrieve_context(collection: Any, query: str, n: int = 5) -> str:
    """Retrieve the most relevant code chunks for the query."""
    if collection is None:
        return ""
    try:
        results = collection.query(query_texts=[query], n_results=min(n, 10))
        docs: list[str] = results.get("documents", [[]])[0]
        metas: list[dict] = results.get("metadatas", [[]])[0]
        parts: list[str] = []
        for doc, meta in zip(docs, metas):
            parts.append(f"# {meta.get('path', 'unknown')}\n{doc}")
        return "\n\n---\n\n".join(parts)
    except Exception as exc:
        logger.warning("chroma.query_failed", error=str(exc))
        return ""


# ─── LLM helper ───────────────────────────────────────────────────────────────


def _llm(model: str, temperature: float = 0.2) -> ChatOllama:
    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=_resolve_ollama_base_url(),
    )


async def _invoke(llm: ChatOllama, system: str, human: str) -> str:
    """Invoke the LLM with system + human messages, return text."""
    try:
        response = await llm.ainvoke(
            [SystemMessage(content=system), HumanMessage(content=human)]
        )
        return str(response.content).strip()
    except Exception as exc:
        logger.error("llm.invoke_failed", error=str(exc))
        return f"[LLM Error: {exc}]"


# ─── Graph nodes ──────────────────────────────────────────────────────────────


async def node_awareness(state: LadderState) -> LadderState:
    """Stage 1: Embed codebase + retrieve relevant context."""
    logger.info("ladder.awareness", project_id=state["project_id"])

    collection = _get_chroma_collection(state["project_id"])
    _embed_project_files(collection, state["project_root"])
    query = state["user_message"]
    if state.get("context_content"):
        query += "\n" + (state["context_content"] or "")[:500]

    context = _retrieve_context(collection, query)

    state["retrieved_context"] = context
    state["steps"].append(
        {
            "stage": "awareness",
            "label": "Awareness",
            "summary": f"Retrieved {len(context.splitlines())} lines of context from codebase",
        }
    )
    return state


async def node_literalist(state: LadderState) -> LadderState:
    """Stage 2: Extract raw functional requirements only."""
    logger.info("ladder.literalist", project_id=state["project_id"])

    llm = _llm(state["model"])
    system = (
        "You are the Literalist Filter. Extract only concrete implementation requirements. "
        "If the request is vague, output direct clarification questions first, then provisional requirements. "
        "Always include a short section named Tooling that lists recommended languages/frameworks/tools based on the codebase context."
    )
    human = (
        f"Persona guidance: {_persona_guidance(state)}\n\n"
        f"App idea: {_app_idea_text(state)}\n\n"
        f"User request: {state['user_message']}\n\n"
        f"Context:\n{state['retrieved_context'][:3000]}"
    )
    requirements = await _invoke(llm, system, human)

    state["literal_requirements"] = requirements
    state["steps"].append(
        {
            "stage": "literalist",
            "label": "Literalist Filter",
            "summary": f"Extracted {len(requirements.splitlines())} requirements",
        }
    )
    return state


async def node_congress(state: LadderState) -> LadderState:
    """Stage 3: Advocate → Skeptic → Synthesizer."""
    logger.info("ladder.congress", project_id=state["project_id"])
    llm = _llm(state["model"])

    # ── Advocate ──────────────────────────────────────────────────────────────
    advocate_system = (
        "You are the Advocate. Propose the most efficient, clean implementation "
        "for the given requirements. Write production-quality code with docstrings. "
        "Consider the existing codebase context when proposing changes. "
        f"Persona behavior: {_persona_guidance(state)}"
    )
    advocate_human = (
        f"Requirements:\n{state['literal_requirements']}\n\n"
        f"Existing code context:\n{state['retrieved_context'][:2000]}"
    )
    advocate = await _invoke(llm, advocate_system, advocate_human)
    state["advocate_proposal"] = advocate

    # ── Skeptic ───────────────────────────────────────────────────────────────
    skeptic_system = (
        "You are the Skeptic. Review the proposed code critically. Check for:\n"
        "1. Apple Human Interface Guidelines violations (if SwiftUI/iOS code)\n"
        "2. App Store Review Guidelines §2.5.2 — NO runtime executable downloads\n"
        "3. Deprecated APIs (Swift, Python, Node.js)\n"
        "4. Security vulnerabilities (injection, path traversal, hardcoded secrets)\n"
        "5. Performance issues\n"
        "Output a numbered list of concerns. If none, output 'No issues found.'"
    )
    skeptic_human = f"Proposed code:\n{advocate}"
    skeptic = await _invoke(llm, skeptic_system, skeptic_human)
    state["skeptic_review"] = skeptic

    # ── Synthesizer ───────────────────────────────────────────────────────────
    synth_system = (
        "You are the Synthesizer. Merge the Advocate's proposal with the Skeptic's "
        "feedback to produce the final, improved code. "
        "Address all valid concerns. Keep the code clean and concise. "
        "Output only the final code (with any necessary explanation as comments)."
    )
    synth_human = (
        f"Advocate's proposal:\n{advocate}\n\n"
        f"Skeptic's concerns:\n{skeptic}"
    )
    synthesized = await _invoke(llm, synth_system, synth_human)
    state["synthesized_code"] = synthesized

    state["steps"].append(
        {
            "stage": "congress",
            "label": "Congress (Advocate → Skeptic → Synthesizer)",
            "summary": f"Reviewed {len(skeptic.splitlines())} concerns, synthesized final code",
        }
    )
    return state


async def node_judge(state: LadderState) -> LadderState:
    """Stage 4: Output final code + commit message."""
    logger.info("ladder.judge", project_id=state["project_id"])
    llm = _llm(state["model"], temperature=0.1)

    judge_system = (
        "You are the Judge. Produce a final response aligned with the selected persona. "
        "If app direction is still unclear, ask concise next-step questions in plain language before implementation details. "
        "Include: (1) current status, (2) next steps, (3) recommended tooling/profile fit. "
        "If engineer options are enabled, include a README Draft section and/or a Contractor Handoff section with actionable tasks. "
        "Also generate a concise conventional commit message. "
        "Format your response as:\n"
        "RESPONSE:\n<your response to the user>\n\nCOMMIT:\n<commit message>"
    )
    judge_human = (
        f"Persona guidance: {_persona_guidance(state)}\n\n"
        f"App idea: {_app_idea_text(state)}\n\n"
        f"Engineer generate README: {state.get('engineer_generate_readme', False)}\n"
        f"Engineer generate Contractor handoff: {state.get('engineer_generate_contractor_handoff', False)}\n\n"
        f"Original request: {state['user_message']}\n\n"
        f"Synthesized code:\n{state['synthesized_code']}"
    )
    judgment = await _invoke(llm, judge_system, judge_human)

    # Parse RESPONSE / COMMIT blocks
    final_output = judgment
    commit_message = "chore: ai-assisted update"
    if "COMMIT:" in judgment:
        parts = judgment.split("COMMIT:", 1)
        commit_message = parts[1].strip().splitlines()[0].strip()
        if "RESPONSE:" in parts[0]:
            final_output = parts[0].split("RESPONSE:", 1)[1].strip()
        else:
            final_output = parts[0].strip()

    state["final_output"] = final_output
    state["commit_message"] = commit_message
    state["steps"].append(
        {
            "stage": "judge",
            "label": "Judge",
            "summary": f"Final output generated. Commit: {commit_message[:60]}",
        }
    )
    return state


# ─── Graph construction ───────────────────────────────────────────────────────


def _build_graph() -> Any:
    """Compile the LangGraph state machine."""
    g = StateGraph(LadderState)
    g.add_node("awareness", node_awareness)
    g.add_node("literalist", node_literalist)
    g.add_node("congress", node_congress)
    g.add_node("judge", node_judge)

    g.set_entry_point("awareness")
    g.add_edge("awareness", "literalist")
    g.add_edge("literalist", "congress")
    g.add_edge("congress", "judge")
    g.add_edge("judge", END)

    return g.compile()


# ─── Public interface ─────────────────────────────────────────────────────────


class LogicLadder:
    """Singleton wrapper around the compiled LangGraph."""

    def __init__(self) -> None:
        self._graph = _build_graph()

    async def run(
        self,
        project_id: str,
        project_root: str,
        message: str,
        model: str,
        context_file: Optional[str],
        context_content: Optional[str],
        persona: Optional[str] = None,
        app_idea: Optional[str] = None,
        engineer_generate_readme: bool = False,
        engineer_generate_contractor_handoff: bool = False,
        db: Optional[AsyncSession] = None,
    ) -> LadderResult:
        """Run the full Logic Ladder and return structured result."""
        initial: LadderState = {
            "project_id": project_id,
            "project_root": project_root,
            "user_message": message,
            "model": model,
            "context_file": context_file,
            "context_content": context_content,
            "persona": persona or "engineer",
            "app_idea": app_idea,
            "engineer_generate_readme": engineer_generate_readme,
            "engineer_generate_contractor_handoff": engineer_generate_contractor_handoff,
            "retrieved_context": "",
            "literal_requirements": "",
            "advocate_proposal": "",
            "skeptic_review": "",
            "synthesized_code": "",
            "final_output": "",
            "commit_message": "",
            "steps": [],
        }

        final_state: LadderState = await self._graph.ainvoke(initial)

        # Persist memory log
        if db is not None:
            try:
                await self._persist_log(db, project_id, final_state)
            except Exception as exc:
                logger.warning("memory.persist_failed", error=str(exc))

        steps = [ReasoningStep(**s) for s in final_state["steps"]]
        return LadderResult(
            final_output=final_state["final_output"],
            commit_message=final_state["commit_message"],
            steps=steps,
        )

    async def _persist_log(
        self, db: AsyncSession, project_id: str, state: LadderState
    ) -> None:
        """Log the full ladder run to the memory_logs table."""
        log = MemoryLog(
            id=str(uuid.uuid4()),
            project_id=project_id,
            stage="full_run",
            content=json.dumps(
                {
                    "user_message": state["user_message"],
                    "commit_message": state["commit_message"],
                    "steps": state["steps"],
                },
                ensure_ascii=False,
            ),
        )
        db.add(log)
        await db.commit()

"""
Docker Manager — per-project container lifecycle for Python, TypeScript, Rust, Go.

Design principles:
- One container per project (isolation)
- Dynamic port allocation to avoid conflicts
- Graceful stop / cleanup
- Timeout-based execution guard
"""

from __future__ import annotations

import asyncio
import os
import socket
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)

# Language → Docker image mapping
LANGUAGE_IMAGES: dict[str, str] = {
    "python": "python:3.12-slim",
    "typescript": "node:22-slim",
    "javascript": "node:22-slim",
    "rust": "rust:1.82-slim",
    "go": "golang:1.22-alpine",
    "bash": "alpine:latest",
}

# Language → command to run the project
LANGUAGE_COMMANDS: dict[str, list[str]] = {
    "python": ["python", "main.py"],
    "typescript": ["sh", "-c", "npm install --silent && npx ts-node index.ts"],
    "javascript": ["sh", "-c", "npm install --silent && node index.js"],
    "rust": ["sh", "-c", "cargo run 2>&1"],
    "go": ["sh", "-c", "go run ."],
    "bash": ["sh", "run.sh"],
}

# Language → build command
LANGUAGE_BUILD_COMMANDS: dict[str, list[str]] = {
    "python": ["python", "-m", "py_compile", "main.py"],
    "typescript": ["sh", "-c", "npm install --silent && npx tsc --noEmit"],
    "rust": ["sh", "-c", "cargo build 2>&1"],
    "go": ["sh", "-c", "go build ./..."],
}

EXECUTION_TIMEOUT_SECONDS = int(os.getenv("EXECUTION_TIMEOUT", "60"))


def _find_free_port() -> int:
    """Find an available port on localhost (used for dynamic port mapping in Phase 2)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class DockerManager:
    """Manages per-project Docker containers."""

    def __init__(self) -> None:
        self._client: Optional[object] = None
        self._active_containers: dict[str, object] = {}

    def _get_client(self) -> object:
        """Lazily initialise docker client."""
        if self._client is None:
            import docker  # type: ignore

            self._client = docker.from_env()
        return self._client

    def _is_docker_available(self) -> bool:
        try:
            client = self._get_client()
            client.ping()  # type: ignore
            return True
        except Exception:
            return False

    async def run_project(
        self, project_id: str, project_path: Path, language: str
    ) -> str:
        """Run project in Docker container. Returns stdout output."""
        if not self._is_docker_available():
            return "Docker is not available. Please start Docker Desktop."

        image = LANGUAGE_IMAGES.get(language)
        command = LANGUAGE_COMMANDS.get(language)
        if not image or not command:
            return f"Language '{language}' is not supported for Docker execution."

        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_sync, project_id, project_path, language, image, command
        )

    def _run_sync(
        self,
        project_id: str,
        project_path: Path,
        language: str,
        image: str,
        command: list[str],
    ) -> str:
        """Synchronous Docker run (called in thread pool)."""
        import docker  # type: ignore

        client = self._get_client()

        # Stop any existing container for this project
        self._stop_sync(project_id)

        logger.info("docker.run", project_id=project_id, image=image)
        try:
            container = client.containers.run(  # type: ignore
                image=image,
                command=command,
                volumes={str(project_path.resolve()): {"bind": "/app", "mode": "rw"}},
                working_dir="/app",
                detach=True,
                remove=False,
                mem_limit="512m",
                cpu_period=100_000,
                cpu_quota=50_000,  # 50% of one CPU
                # network_mode="none" isolates the sandbox by default.
                # Set DOCKER_NETWORK_MODE=bridge in your environment if your
                # project needs network access (e.g., for npm install / pip install).
                network_mode=os.getenv("DOCKER_NETWORK_MODE", "none"),
                read_only=False,
                security_opt=["no-new-privileges:true"],
            )
            self._active_containers[project_id] = container

            # Wait for completion with timeout
            try:
                result = container.wait(timeout=EXECUTION_TIMEOUT_SECONDS)
                output = container.logs(stdout=True, stderr=True).decode(
                    "utf-8", errors="replace"
                )
                exit_code = result.get("StatusCode", 0)
                if exit_code != 0:
                    output = f"[Exit {exit_code}]\n{output}"
                return output
            except Exception as exc:
                container.kill()
                return f"Execution timed out after {EXECUTION_TIMEOUT_SECONDS}s\n{exc}"
            finally:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
                self._active_containers.pop(project_id, None)

        except Exception as exc:
            logger.error("docker.run_failed", error=str(exc))
            return f"Docker error: {exc}"

    async def build_project(
        self, project_id: str, project_path: Path, language: str
    ) -> str:
        """Build/type-check the project."""
        if not self._is_docker_available():
            return "Docker is not available."

        image = LANGUAGE_IMAGES.get(language)
        command = LANGUAGE_BUILD_COMMANDS.get(language)
        if not image or not command:
            return f"Build not supported for language: {language}"

        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_sync, project_id, project_path, language, image, command
        )

    async def stop_container(self, project_id: str) -> None:
        """Stop the running container for a project."""
        await asyncio.get_event_loop().run_in_executor(
            None, self._stop_sync, project_id
        )

    def _stop_sync(self, project_id: str) -> None:
        container = self._active_containers.pop(project_id, None)
        if container:
            try:
                container.kill()  # type: ignore
                container.remove(force=True)  # type: ignore
            except Exception as exc:
                logger.debug("docker.stop_failed", error=str(exc))

"""
Terminal router — WebSocket PTY bridge for per-project shells.

Each project gets a PTY subprocess running inside (or alongside) its
Docker container. Input/output is streamed over WebSocket as JSON frames.
"""

import asyncio
import fcntl
import json
import os
import pty
import struct
import termios
from typing import Any

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = structlog.get_logger(__name__)
router = APIRouter()

PROJECTS_ROOT = os.getenv("PROJECTS_ROOT", "./projects")


def _set_pty_size(fd: int, rows: int, cols: int) -> None:
    """Set PTY window size via ioctl."""
    try:
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
    except OSError:
        pass


@router.websocket("/ws/terminal/{project_id}")
async def terminal_ws(websocket: WebSocket, project_id: str) -> None:
    await websocket.accept()
    logger.info("terminal.connected", project_id=project_id)

    project_path = os.path.join(PROJECTS_ROOT, project_id)
    if not os.path.isdir(project_path):
        await websocket.send_text(
            json.dumps({"type": "output", "data": f"\r\nProject directory not found: {project_path}\r\n"})
        )
        await websocket.close()
        return

    # Fork a PTY with bash
    pid, master_fd = pty.fork()

    if pid == 0:
        # Child process — exec shell in project directory
        os.chdir(project_path)
        shell = os.environ.get("SHELL", "/bin/bash")
        os.execvpe(
            shell,
            [shell, "--login"],
            {
                **os.environ,
                "TERM": "xterm-256color",
                "COLORTERM": "truecolor",
                "PS1": r"\[\033[35m\]alkemist\[\033[0m\]:\[\033[34m\]\w\[\033[0m\]\$ ",
            },
        )
        # execvpe does not return; defensive exit
        os._exit(1)

    # Parent process — bridge PTY ↔ WebSocket
    loop = asyncio.get_event_loop()

    async def read_pty() -> None:
        """Read PTY output and forward to WebSocket."""
        while True:
            try:
                data = await loop.run_in_executor(None, os.read, master_fd, 4096)
                if not data:
                    break
                await websocket.send_text(
                    json.dumps({"type": "output", "data": data.decode("utf-8", errors="replace")})
                )
            except OSError:
                break

    pty_reader = asyncio.ensure_future(read_pty())

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "input":
                data = msg.get("data", "")
                if isinstance(data, str):
                    os.write(master_fd, data.encode("utf-8"))

            elif msg_type == "resize":
                cols = int(msg.get("cols", 80))
                rows = int(msg.get("rows", 24))
                _set_pty_size(master_fd, rows, cols)

    except WebSocketDisconnect:
        logger.info("terminal.disconnected", project_id=project_id)
    except Exception as exc:
        logger.error("terminal.error", error=str(exc))
    finally:
        pty_reader.cancel()
        try:
            os.close(master_fd)
        except OSError:
            pass
        try:
            os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            pass

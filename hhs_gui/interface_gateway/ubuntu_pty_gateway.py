"""Frontend-owned Ubuntu PTY transport adapter.

This adapter is intentionally outside canonical HHS backend/runtime authority.
It exposes the existing public `bin/hhs-guest` CLI to the thin web terminal
without importing HHS runtime implementation modules.

Security:
- bind loopback only in deployment;
- opt-in enable flag;
- bearer token required on the first WebSocket frame;
- guest SSH identity/known-hosts remain server-side inside hhs-guest;
- bounded commands, terminal dimensions, timeouts, and output;
- fail closed on malformed CLI output or nonzero adapter execution.
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import secrets
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

SCHEMA = "HHS_INTERFACE_UBUNTU_PTY_GATEWAY_V1"
ROOT = Path(__file__).resolve().parents[2]
GUEST_CLI = ROOT / "bin" / "hhs-guest"
MAX_COMMAND_CHARS = int(os.environ.get("HHS_INTERFACE_PTY_MAX_COMMAND_CHARS", "4096"))
MAX_OUTPUT_BYTES = int(os.environ.get("HHS_INTERFACE_PTY_MAX_OUTPUT_BYTES", "1048576"))
MAX_TIMEOUT = float(os.environ.get("HHS_INTERFACE_PTY_MAX_TIMEOUT", "120"))

app = FastAPI(title="HHS Interface Ubuntu PTY Gateway", version="1.0.0")


def enabled() -> bool:
    return os.environ.get("HHS_INTERFACE_PTY_ENABLED", "").strip() == "1"


def configured_token() -> str:
    return os.environ.get("HHS_INTERFACE_PTY_TOKEN", "")


def public_status() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "enabled": enabled(),
        "auth_required": True,
        "guest_cli": "bin/hhs-guest",
        "guest_credentials_exposed_to_client": False,
        "canonical_runtime_authority": False,
        "transport_only": True,
        "max_command_chars": MAX_COMMAND_CHARS,
        "max_output_bytes": MAX_OUTPUT_BYTES,
        "max_timeout_seconds": MAX_TIMEOUT,
    }


@app.get("/api/interface/ubuntu/pty/status")
async def status() -> dict[str, Any]:
    return public_status()


async def run_guest_cli(*args: str, timeout: float) -> dict[str, Any]:
    if not enabled():
        raise RuntimeError("HHS_INTERFACE_PTY_DISABLED")
    if not GUEST_CLI.is_file():
        raise RuntimeError("HHS_INTERFACE_GUEST_CLI_MISSING")

    process = await asyncio.create_subprocess_exec(
        "sh",
        str(GUEST_CLI),
        "--pretty",
        *args,
        cwd=str(ROOT),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout + 5)
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise RuntimeError("HHS_INTERFACE_GUEST_CLI_TIMEOUT")

    if len(stdout) > MAX_OUTPUT_BYTES or len(stderr) > MAX_OUTPUT_BYTES:
        raise RuntimeError("HHS_INTERFACE_PTY_OUTPUT_LIMIT")

    raw = stdout.decode("utf-8", errors="strict").strip()
    err = stderr.decode("utf-8", errors="replace").strip()
    try:
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise RuntimeError("HHS_INTERFACE_GUEST_CLI_NON_JSON") from exc

    if process.returncode != 0:
        raise RuntimeError(
            f"HHS_INTERFACE_GUEST_CLI_REJECTED:{process.returncode}:{payload or err}"
        )
    if not isinstance(payload, dict) or not payload.get("schema"):
        raise RuntimeError("HHS_INTERFACE_GUEST_CLI_CONTRACT_REJECTED")
    return payload


def bounded_exec_request(request: dict[str, Any]) -> tuple[str, int, int, float]:
    command = str(request.get("command") or "")
    if not command or len(command) > MAX_COMMAND_CHARS or "\x00" in command:
        raise RuntimeError("HHS_INTERFACE_PTY_COMMAND_INVALID")
    rows = int(request.get("rows", 24))
    cols = int(request.get("cols", 80))
    timeout = float(request.get("timeout", 60))
    if not 1 <= rows <= 4096 or not 1 <= cols <= 4096:
        raise RuntimeError("HHS_INTERFACE_PTY_SIZE_INVALID")
    if not 0 < timeout <= MAX_TIMEOUT:
        raise RuntimeError("HHS_INTERFACE_PTY_TIMEOUT_INVALID")
    return command, rows, cols, timeout


@app.websocket("/api/interface/ubuntu/pty/ws")
async def ubuntu_pty(websocket: WebSocket) -> None:
    await websocket.accept()
    token = configured_token()
    if not enabled() or not token:
        await websocket.send_json({
            "schema": SCHEMA,
            "ok": False,
            "classification": "HHS_INTERFACE_PTY_NOT_CONFIGURED",
        })
        await websocket.close(code=1011)
        return

    authenticated = False
    try:
        while True:
            request = await websocket.receive_json()
            if not isinstance(request, dict):
                raise RuntimeError("HHS_INTERFACE_PTY_FRAME_INVALID")

            action = str(request.get("action") or "")
            if not authenticated:
                if action != "auth":
                    raise RuntimeError("HHS_INTERFACE_PTY_AUTH_REQUIRED")
                supplied = str(request.get("token") or "")
                if not secrets.compare_digest(supplied, token):
                    raise RuntimeError("HHS_INTERFACE_PTY_AUTH_REJECTED")
                authenticated = True
                await websocket.send_json({
                    "schema": SCHEMA,
                    "ok": True,
                    "action": "auth",
                    "authenticated": True,
                    "runtime": public_status(),
                })
                continue

            if action == "status":
                result = await run_guest_cli("status", timeout=15)
            elif action == "exec":
                command, rows, cols, timeout = bounded_exec_request(request)
                result = await run_guest_cli(
                    "pty-exec",
                    "--rows", str(rows),
                    "--cols", str(cols),
                    "--timeout", str(timeout),
                    "--",
                    "bash", "-lc", command,
                    timeout=timeout,
                )
            else:
                raise RuntimeError("HHS_INTERFACE_PTY_ACTION_UNKNOWN")

            await websocket.send_json({
                "schema": SCHEMA,
                "ok": True,
                "action": action,
                "result": result,
            })
    except WebSocketDisconnect:
        return
    except Exception as exc:
        try:
            await websocket.send_json({
                "schema": SCHEMA,
                "ok": False,
                "classification": type(exc).__name__,
                "detail": str(exc),
            })
            await websocket.close(code=1008)
        except Exception:
            return

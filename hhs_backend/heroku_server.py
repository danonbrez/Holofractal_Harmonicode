"""Heroku-safe HHS deployment gateway.

The compiled HHS Runtime OS / visual IDE is the public root. The Pass 161
assistant shell and Pass 157 particle visualization remain available as
secondary tools. Canonical runtime and local LiteRT-LM startup are excluded
from web-dyno boot.
"""
from __future__ import annotations

import hashlib
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BOOT_ID = str(uuid.uuid4())
STARTED_AT = time.time()
ROOT_DIR = Path(__file__).resolve().parents[1]
RUNTIME_OS_ROOT = ROOT_DIR / "hhs_gui" / "dist"
PASS161_ROOT = ROOT_DIR / "applications" / "holofractal_harmonizer"
SWARM_DEMO_ROOT = ROOT_DIR / "apps" / "unified_gui"

app = FastAPI(
    title="HHS Heroku Deployment Gateway",
    version="1.2.0",
    description="Runtime OS gateway with bounded detached-runtime projections.",
)

_threads: dict[str, dict[str, Any]] = {}


def _message(role: str, content: str) -> dict[str, Any]:
    digest = hashlib.sha256(
        f"{role}\0{content}\0{time.time_ns()}".encode("utf-8")
    ).hexdigest()
    return {
        "message_id": f"message:{uuid.uuid4()}",
        "role": role,
        "content": content,
        "created_at": time.time(),
        "message_sha256": digest,
    }


def _thread_snapshot(thread: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(thread)
    snapshot["messages"] = [dict(message) for message in thread["messages"]]
    snapshot["message_count"] = len(snapshot["messages"])
    return snapshot


@app.get("/healthz")
@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "healthy",
        "mode": "HEROKU_RUNTIME_OS_GATEWAY",
        "boot_id": BOOT_ID,
        "uptime_seconds": time.time() - STARTED_AT,
        "default_interface": "HHS_RUNTIME_OS_VISUAL_IDE",
        "runtime_os_bundle_present": (RUNTIME_OS_ROOT / "index.html").is_file(),
        "assistant_interface_present": (PASS161_ROOT / "index.html").is_file(),
        "swarm_demo_present": (SWARM_DEMO_ROOT / "index.html").is_file(),
        "canonical_runtime_attached": False,
        "assistant_provider_online": False,
    }


@app.get("/api/system/status")
async def system_status() -> dict[str, Any]:
    return {
        "system": "HARMONICODE",
        "status": "online",
        "deployment_mode": "HEROKU_RUNTIME_OS_GATEWAY",
        "boot_id": BOOT_ID,
        "default_interface": "HHS_RUNTIME_OS_VISUAL_IDE",
        "assistant_interface": "/assistant-ui/",
        "swarm_diagnostic": "/swarm-demo/",
        "runtime_state": "DETACHED_PROJECTION_NO_CANONICAL_MUTATION",
    }


async def _hold_projection_socket(websocket: WebSocket) -> None:
    """Keep a projection channel open without fabricating runtime events."""
    await websocket.accept()
    try:
        while True:
            await websocket.receive()
    except WebSocketDisconnect:
        return


@app.websocket("/ws/runtime")
async def runtime_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.websocket("/ws/replay")
async def replay_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.websocket("/ws/graph")
async def graph_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.websocket("/ws/transport")
async def transport_socket(websocket: WebSocket) -> None:
    await _hold_projection_socket(websocket)


@app.get("/api/assistant/status")
async def assistant_status() -> dict[str, Any]:
    return {
        "ok": True,
        "online": False,
        "status": "DEGRADED",
        "model_id": "gemma4-12b",
        "request_model_id": "gemma4-12b",
        "execution_backend": "external-unavailable",
        "provider_id": "provider:hhs.litert_lm.gemma4",
        "direct_vm81_mutation_allowed": False,
    }


@app.get("/api/assistant/health")
async def assistant_health() -> dict[str, Any]:
    return {
        "ok": True,
        "online": False,
        "status": "ASSISTANT_DEGRADED",
        "reason": "LiteRT-LM is not hosted inside the Heroku web dyno.",
    }


@app.get("/api/assistant/tools")
async def assistant_tools() -> dict[str, Any]:
    return {
        "ok": True,
        "count": 0,
        "tools": [],
        "status": "EXTERNAL_RUNTIME_NOT_ATTACHED",
    }


@app.post("/api/assistant/threads")
async def create_thread(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = payload or {}
    thread_id = f"thread:{uuid.uuid4()}"
    thread = {
        "thread_id": thread_id,
        "project_id": str(data.get("project_id") or "project:holofractal-harmonizer"),
        "title": str(data.get("title") or "HHS Visual Development"),
        "metadata": dict(data.get("metadata") or {}),
        "created_at": time.time(),
        "messages": [
            _message(
                "assistant",
                "The HHS Runtime OS is online in detached projection mode. "
                "The canonical runtime and LiteRT-LM provider remain external.",
            )
        ],
    }
    _threads[thread_id] = thread
    return {"ok": True, "thread": _thread_snapshot(thread)}


@app.get("/api/assistant/threads/{thread_id:path}")
async def get_thread(thread_id: str) -> dict[str, Any]:
    thread = _threads.get(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Assistant thread not found")
    return {"ok": True, "thread": _thread_snapshot(thread)}


@app.post("/api/assistant/threads/{thread_id:path}/messages")
async def add_message(thread_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    thread = _threads.get(thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Assistant thread not found")

    content = str(payload.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message content is required")

    user_message = _message("user", content)
    assistant_message = _message(
        "assistant",
        "The request was received without runtime mutation. LiteRT-LM and the "
        "canonical HHS runtime must be attached before inference can execute.",
    )
    thread["messages"].extend([user_message, assistant_message])

    return {
        "ok": True,
        "status": "DEGRADED_PROVIDER_UNAVAILABLE",
        "thread": _thread_snapshot(thread),
        "user_message": user_message,
        "assistant_message": assistant_message,
        "hhs_api_tool_call_count": 0,
    }


if (PASS161_ROOT / "index.html").is_file():
    app.mount(
        "/assistant-ui",
        StaticFiles(directory=str(PASS161_ROOT), html=True),
        name="hhs-pass161-assistant-ui",
    )

if (SWARM_DEMO_ROOT / "index.html").is_file():
    app.mount(
        "/swarm-demo",
        StaticFiles(directory=str(SWARM_DEMO_ROOT), html=True),
        name="hhs-pass157-swarm-demo",
    )

if (RUNTIME_OS_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(RUNTIME_OS_ROOT), html=True),
        name="hhs-runtime-os-visual-ide",
    )
elif (PASS161_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(PASS161_ROOT), html=True),
        name="hhs-runtime-os-build-pending",
    )
else:
    @app.get("/", response_class=HTMLResponse)
    async def fallback_home() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><title>HHS Online</title></head>
        <body style='background:#050912;color:#e8eef8;font-family:system-ui;padding:2rem'>
        <h1>HHS deployment gateway is online</h1>
        <p>The Runtime OS frontend bundle has not been generated.</p>
        <p><a style='color:#8bd5ff' href='/healthz'>View deployment health</a></p>
        </body></html>"""

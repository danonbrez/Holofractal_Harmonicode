"""Heroku-safe HHS deployment gateway.

The advanced Pass 157 Unified GUI is the public root. The Pass 161 workflow and
assistant shell remains available at /assistant-ui. Canonical runtime and local
LiteRT-LM startup are intentionally excluded from web-dyno boot.
"""
from __future__ import annotations

import hashlib
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

BOOT_ID = str(uuid.uuid4())
STARTED_AT = time.time()
ROOT_DIR = Path(__file__).resolve().parents[1]
UNIFIED_GUI_ROOT = ROOT_DIR / "apps" / "unified_gui"
PASS161_ROOT = ROOT_DIR / "applications" / "holofractal_harmonizer"

app = FastAPI(
    title="HHS Heroku Deployment Gateway",
    version="1.1.0",
    description="Advanced GUI gateway with bounded degraded assistant endpoints.",
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
        "mode": "HEROKU_ADVANCED_GUI_GATEWAY",
        "boot_id": BOOT_ID,
        "uptime_seconds": time.time() - STARTED_AT,
        "default_interface": "HHS_PASS157_UNIFIED_GUI",
        "unified_gui_present": (UNIFIED_GUI_ROOT / "index.html").is_file(),
        "pass161_interface_present": (PASS161_ROOT / "index.html").is_file(),
        "canonical_runtime_attached": False,
        "assistant_provider_online": False,
    }


@app.get("/api/system/status")
async def system_status() -> dict[str, Any]:
    return {
        "system": "HARMONICODE",
        "status": "online",
        "deployment_mode": "HEROKU_ADVANCED_GUI_GATEWAY",
        "boot_id": BOOT_ID,
        "default_interface": "HHS-P157-UHAG-PSME",
        "assistant_interface": "/assistant-ui/",
        "runtime_state": "DEGRADED_EXTERNAL_RUNTIME_NOT_ATTACHED",
    }


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
                "The advanced HHS visual environment is online. The canonical runtime "
                "and LiteRT-LM provider remain external to this Heroku dyno.",
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

if (UNIFIED_GUI_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(UNIFIED_GUI_ROOT), html=True),
        name="hhs-unified-gui",
    )
elif (PASS161_ROOT / "index.html").is_file():
    app.mount(
        "/",
        StaticFiles(directory=str(PASS161_ROOT), html=True),
        name="hhs-pass161-fallback",
    )
else:
    @app.get("/", response_class=HTMLResponse)
    async def fallback_home() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><title>HHS Online</title></head>
        <body style='background:#050912;color:#e8eef8;font-family:system-ui;padding:2rem'>
        <h1>HHS deployment gateway is online</h1>
        <p>No visual application directory was included in this deployment.</p>
        <p><a style='color:#8bd5ff' href='/healthz'>View deployment health</a></p>
        </body></html>"""

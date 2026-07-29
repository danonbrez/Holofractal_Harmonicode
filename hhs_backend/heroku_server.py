"""Heroku-safe HHS visual gateway.

This module intentionally avoids importing the canonical runtime bootstrap during
web-dyno startup. It serves the Pass 161 visual environment immediately and
provides bounded degraded-mode assistant endpoints until external runtime and
LiteRT-LM services are attached.
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
VISUAL_ROOT = ROOT_DIR / "applications" / "holofractal_harmonizer"

app = FastAPI(
    title="HHS Heroku Visual Gateway",
    version="1.0.0",
    description="Bounded deployment gateway for the HHS visual environment.",
)

_threads: dict[str, dict[str, Any]] = {}


def _message(role: str, content: str) -> dict[str, Any]:
    digest = hashlib.sha256(f"{role}\0{content}\0{time.time_ns()}".encode("utf-8")).hexdigest()
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
        "mode": "HEROKU_DEPLOYMENT_GATEWAY",
        "boot_id": BOOT_ID,
        "uptime_seconds": time.time() - STARTED_AT,
        "visual_root_present": VISUAL_ROOT.is_dir(),
        "canonical_runtime_attached": False,
        "assistant_provider_online": False,
    }


@app.get("/api/system/status")
async def system_status() -> dict[str, Any]:
    return {
        "system": "HARMONICODE",
        "status": "online",
        "deployment_mode": "HEROKU_DEPLOYMENT_GATEWAY",
        "boot_id": BOOT_ID,
        "visual_environment": "HHS-P161-HHUMOCE",
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
                "The HHS visual environment is online in deployment-gateway mode. "
                "The canonical runtime and LiteRT-LM provider are not attached to this Heroku dyno.",
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
        "The request was received without runtime mutation. LiteRT-LM and the canonical "
        "HHS runtime must be attached as external services before inference can execute.",
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


if VISUAL_ROOT.is_dir() and (VISUAL_ROOT / "index.html").is_file():
    app.mount("/", StaticFiles(directory=str(VISUAL_ROOT), html=True), name="hhs-visual-home")
else:
    @app.get("/", response_class=HTMLResponse)
    async def fallback_home() -> str:
        return """<!doctype html><html><head><meta charset='utf-8'><title>HHS Online</title></head>
        <body style='background:#050912;color:#e8eef8;font-family:system-ui;padding:2rem'>
        <h1>HHS deployment gateway is online</h1>
        <p>The Pass 161 visual application directory was not included in this deployment.</p>
        <p><a style='color:#8bd5ff' href='/healthz'>View deployment health</a></p>
        </body></html>"""

"""Terminal Pass 175 WebSocket control and event stream."""
from __future__ import annotations

from base64 import b64decode
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from hhs_backend.api.pass175_terminal_routes import get_terminal_runtime
from hhs_runtime.pass175 import Pass175Error, TerminalInstructionRequest

router = APIRouter(tags=["pass175", "terminal", "websocket", "firmware"])


async def _send(websocket: WebSocket, payload: dict[str, Any]) -> None:
    await websocket.send_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    )


def _instruction(item: dict[str, Any]) -> TerminalInstructionRequest:
    try:
        exact = b64decode(str(item["exact_bytes_b64"]), validate=True)
    except Exception as exc:
        raise Pass175Error("HHS_P175_MALFORMED_EXACT_BYTES_BASE64") from exc
    return TerminalInstructionRequest(
        exact_bytes=exact,
        decoder_mode=str(item.get("decoder_mode", "LONG_64")),
        sequence=int(item.get("sequence", 0)),
        thread_id=int(item.get("thread_id", 0)),
        allow_privileged=bool(item.get("allow_privileged", False)),
        explicit_delta=tuple(
            (int(position), int(value))
            for position, value in dict(item.get("explicit_delta", {})).items()
        ),
        device=item.get("device"),
        device_operation=item.get("device_operation"),
        device_payload=dict(item.get("device_payload") or {}),
    )


@router.websocket("/api/v1/pass175/terminal/ws/events")
async def terminal_events(websocket: WebSocket) -> None:
    await websocket.accept()
    runtime = get_terminal_runtime()
    await _send(websocket, {
        "schema": "HHS_PASS_175_TERMINAL_WS_CONNECTED_V1",
        "classification": "HHS_PASS_175_TERMINAL_WS_READY",
        "runtime": runtime.status(),
    })
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                request = json.loads(raw)
                action = str(request.get("action", "status"))
                if action == "ping":
                    result = {
                        "classification": "HHS_PASS_175_TERMINAL_WS_PONG",
                        "parallel_state_authority": False,
                    }
                elif action == "status":
                    result = runtime.status(native_root=request.get("native_root"))
                elif action == "hydrate":
                    result = runtime.cold_hydrate_terminal(
                        seal=bool(request.get("seal", True))
                    )
                elif action == "boot":
                    if not runtime.secure_store.sealed:
                        runtime.cold_hydrate_terminal(seal=True)
                    result = runtime.boot_firmware()
                elif action == "execute":
                    instructions = [
                        _instruction(item) for item in request.get("instructions", [])
                    ]
                    result = runtime.execute_batch(
                        instructions,
                        max_workers=int(request.get("max_workers", 8)),
                    )
                elif action == "replay":
                    result = runtime.replay()
                elif action == "verify":
                    if not runtime.secure_store.sealed:
                        runtime.cold_hydrate_terminal(seal=True)
                    result = runtime.terminal_verification(
                        native_root=request.get("native_root"),
                        require_boot=bool(request.get("require_boot", True)),
                    )
                else:
                    raise Pass175Error("HHS_P175_TERMINAL_WS_ACTION_UNKNOWN", action)
                await _send(websocket, {"ok": True, "action": action, "result": result})
            except Exception as exc:
                await _send(websocket, {
                    "ok": False,
                    "schema": "HHS_PASS_175_TERMINAL_WS_REJECTION_V1",
                    "classification": getattr(exc, "classification", type(exc).__name__),
                    "detail": getattr(exc, "detail", str(exc)),
                })
    except WebSocketDisconnect:
        return

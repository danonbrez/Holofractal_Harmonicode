"""Pass 174 live WebSocket projection over the governed runtime."""
from __future__ import annotations

import asyncio
from dataclasses import asdict

from fastapi import WebSocket, WebSocketDisconnect

from .pass174_runtime_routes import get_runtime, router


@router.websocket("/ws/events")
async def pass174_events(websocket: WebSocket) -> None:
    await websocket.accept()
    runtime = get_runtime()
    receipt_cursor = 0
    try:
        while True:
            receipts = runtime.state.receipts[receipt_cursor:]
            receipt_cursor += len(receipts)
            await websocket.send_json({
                "schema": "HHS_P174_LIVE_EVENT_FRAME_V1",
                "classification": "HHS_PASS_174_LIVE_PROJECTION",
                "mutation_authority": False,
                "status": runtime.status(),
                "phase": asdict(runtime.phase),
                "receipts": receipts,
                "receipt_cursor": receipt_cursor,
            })
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            operation = str(message.get("operation") or "PING").upper()
            if operation == "PING":
                await websocket.send_json({
                    "schema": "HHS_P174_LIVE_CONTROL_RESPONSE_V1",
                    "classification": "PONG",
                    "logical_step": runtime.vmrc.epoch,
                    "mutation_authority": False,
                })
            elif operation == "STATUS":
                await websocket.send_json(runtime.status())
            else:
                await websocket.send_json({
                    "schema": "HHS_P174_LIVE_CONTROL_REJECTION_V1",
                    "classification": "HHS_P174_WEBSOCKET_MUTATION_REQUIRES_HTTP_AUTHORITY_ROUTE",
                    "requested_operation": operation,
                    "mutation_authority": False,
                })
    except WebSocketDisconnect:
        return

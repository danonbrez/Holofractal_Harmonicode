"""FastAPI routes for the production governed HHS assistant interface."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/assistant", tags=["assistant", "production", "hhs-tools"])
_SERVICE: Any = None


def _service() -> Any:
    global _SERVICE
    if _SERVICE is None:
        from hhs_backend.runtime.hhs_production_assistant_v1 import (
            DEFAULT_PRODUCTION_ASSISTANT_SERVICE,
        )
        _SERVICE = DEFAULT_PRODUCTION_ASSISTANT_SERVICE
    return _SERVICE


async def _async_service() -> Any:
    """Construct the production assistant without blocking the FastAPI event loop."""
    return await asyncio.to_thread(_service)


class CreateThreadRequest(BaseModel):
    project_id: str = "project:default"
    title: str = Field(default="HHS Assistant", min_length=1, max_length=160)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None


class ChatRequest(CreateThreadRequest, SendMessageRequest):
    thread_id: Optional[str] = None


class ExecuteToolRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)


@router.get("/status")
async def assistant_status() -> Dict[str, Any]:
    service = await _async_service()
    status = await asyncio.to_thread(service.status)
    if status.get("online") and status.get("ok"):
        return status

    # The repository-native provider has no external network liveness dependency:
    # its health path closes over the local installation contract and model registry.
    # Prime only that fallback here so the cheap UI status route cannot inherit the
    # configured Gemma/LiteRT provider timeout. The normal production status method
    # then recomputes provider selection and its Hash72 root from the cached result.
    await service._provider_health("native", service.native_service, force=False)
    return await asyncio.to_thread(service.status)


@router.get("/health")
async def assistant_health() -> Dict[str, Any]:
    service = await _async_service()
    return await service.health()


@router.get("/tools")
async def assistant_tools() -> Dict[str, Any]:
    from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
        assistant_api_tool_registry,
    )
    return assistant_api_tool_registry()


@router.post("/tools/{tool_name}")
async def assistant_execute_tool(
    tool_name: str,
    request: ExecuteToolRequest,
) -> Dict[str, Any]:
    from hhs_backend.runtime.hhs_assistant_api_tool_gateway_v1 import (
        execute_hhs_assistant_api_tool,
    )
    return await execute_hhs_assistant_api_tool(tool_name, request.arguments)


@router.get("/threads")
async def assistant_threads() -> Dict[str, Any]:
    threads = _service().threads.list()
    return {
        "schema": "HHS_AI_CONVERSATION_THREAD_LIST_V1",
        "ok": True,
        "count": len(threads),
        "threads": threads,
    }


@router.post("/threads")
async def assistant_create_thread(request: CreateThreadRequest) -> Dict[str, Any]:
    return {
        "schema": "HHS_AI_CONVERSATION_THREAD_CREATE_RESPONSE_V1",
        "ok": True,
        "thread": _service().create_thread(
            project_id=request.project_id,
            title=request.title,
            metadata=request.metadata,
        ),
    }


@router.get("/threads/{thread_id}")
async def assistant_get_thread(thread_id: str) -> Dict[str, Any]:
    thread = _service().threads.get(thread_id)
    if not thread:
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_AI_CONVERSATION_THREAD_NOT_FOUND_V1",
                "ok": False,
                "thread_id": thread_id,
            },
        )
    return {
        "schema": "HHS_AI_CONVERSATION_THREAD_RESPONSE_V1",
        "ok": True,
        "thread": thread,
    }


@router.post("/threads/{thread_id}/messages")
async def assistant_send_message(
    thread_id: str,
    request: SendMessageRequest,
) -> Dict[str, Any]:
    try:
        return await _service().send_message(
            thread_id,
            content=request.content,
            tools=request.tools,
            response_format=request.response_format,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_AI_CONVERSATION_THREAD_NOT_FOUND_V1",
                "ok": False,
                "thread_id": thread_id,
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_AI_CONVERSATION_MESSAGE_REJECTION_V1",
                "ok": False,
                "reason": str(exc),
            },
        ) from exc


@router.post("/chat")
async def assistant_chat(request: ChatRequest) -> Dict[str, Any]:
    thread_id = request.thread_id
    if not thread_id:
        thread = _service().create_thread(
            project_id=request.project_id,
            title=request.title,
            metadata=request.metadata,
        )
        thread_id = thread["thread_id"]
    try:
        return await _service().send_message(
            thread_id,
            content=request.content,
            tools=request.tools,
            response_format=request.response_format,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_AI_CONVERSATION_THREAD_NOT_FOUND_V1",
                "ok": False,
                "thread_id": thread_id,
            },
        ) from exc


@router.websocket("/ws/{thread_id}")
async def assistant_websocket(websocket: WebSocket, thread_id: str) -> None:
    await websocket.accept()
    service = _service()
    if not service.threads.get(thread_id):
        await websocket.send_json({
            "schema": "HHS_AI_CONVERSATION_THREAD_NOT_FOUND_V1",
            "ok": False,
            "thread_id": thread_id,
        })
        await websocket.close(code=4404)
        return
    try:
        while True:
            request = await websocket.receive_json()
            content = str(request.get("content") or "")
            if not content.strip():
                await websocket.send_json({
                    "schema": "HHS_AI_CONVERSATION_MESSAGE_REJECTION_V1",
                    "ok": False,
                    "reason": "message content must not be empty",
                })
                continue
            result = await service.send_message(
                thread_id,
                content=content,
                tools=request.get("tools"),
                response_format=request.get("response_format"),
            )
            await websocket.send_json(result)
    except WebSocketDisconnect:
        return

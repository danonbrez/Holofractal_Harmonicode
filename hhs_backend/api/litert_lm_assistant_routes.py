"""FastAPI routes for the production governed HHS assistant interface."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from hhs_backend.runtime.hhs_assistant_stage_timing_v1 import assistant_trace, timed_stage

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


class CreateThreadRequest(BaseModel):
    project_id: str = "project:default"
    title: str = Field(default="HHS Assistant", min_length=1, max_length=160)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1)
    tools: Optional[List[Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    custom_system_instruction: Optional[str] = Field(default=None, max_length=8192)
    assistant_mode: str = Field(default="BOTH", min_length=4, max_length=64)
    user_context: Optional[Dict[str, Any]] = None


class ChatRequest(CreateThreadRequest, SendMessageRequest):
    thread_id: Optional[str] = None


class ExecuteToolRequest(BaseModel):
    arguments: Dict[str, Any] = Field(default_factory=dict)


@router.get("/status")
async def assistant_status() -> Dict[str, Any]:
    return _service().status()


@router.get("/health")
async def assistant_health() -> Dict[str, Any]:
    return await _service().health()


@router.get("/deployment-health")
async def assistant_deployment_health() -> Dict[str, Any]:
    """Bounded production liveness without optional-provider diagnostic fan-out."""
    return await _service().deployment_health()


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
            custom_system_instruction=request.custom_system_instruction,
            assistant_mode=request.assistant_mode,
            user_context=request.user_context,
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


async def _execute_chat_request(
    request: ChatRequest,
    *,
    trace_label: str | None = None,
) -> Dict[str, Any]:
    with assistant_trace(trace_label):
        with timed_stage("route.assistant_chat.total"):
            thread_id = request.thread_id
            if not thread_id:
                with timed_stage("route.assistant_chat.create_thread"):
                    thread = _service().create_thread(
                        project_id=request.project_id,
                        title=request.title,
                        metadata=request.metadata,
                    )
                    thread_id = thread["thread_id"]
            try:
                with timed_stage("route.assistant_chat.service_send_message"):
                    return await _service().send_message(
                        thread_id,
                        content=request.content,
                        tools=request.tools,
                        response_format=request.response_format,
                        custom_system_instruction=request.custom_system_instruction,
                        assistant_mode=request.assistant_mode,
                        user_context=request.user_context,
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
    return await _execute_chat_request(request)


async def production_assistant_route_warmup(
    token: str = "HHS-PRODUCTION-CHATBOT-E2E-7249",
) -> Dict[str, Any]:
    """Exercise the identical two-turn production chat route before readiness."""
    started = time.perf_counter()
    first = await _execute_chat_request(
        ChatRequest(
            project_id="project:production-startup-prewarm",
            title="Production Startup Prewarm",
            content=f"Remember this exact token for my next message: {token}. Reply briefly.",
            assistant_mode="BOTH",
        ),
        trace_label="startup-prewarm-turn-1",
    )
    thread_id = str(first.get("thread_id") or "")
    if not thread_id:
        raise RuntimeError(f"production assistant warmup omitted thread_id: {first}")

    second = await _execute_chat_request(
        ChatRequest(
            thread_id=thread_id,
            project_id="project:production-startup-prewarm",
            title="Production Startup Prewarm",
            content=(
                "What exact token did I ask you to remember in my previous message? "
                "Reply with only the token."
            ),
            assistant_mode="BOTH",
        ),
        trace_label="startup-prewarm-turn-2",
    )
    recalled = str((second.get("assistant_message") or {}).get("content") or "").strip()
    if recalled != token:
        raise RuntimeError(
            f"production assistant warmup recall mismatch: expected={token!r} actual={recalled!r}"
        )
    if str(second.get("thread_id") or "") != thread_id:
        raise RuntimeError("production assistant warmup thread changed between turns")

    return {
        "schema": "HHS_PRODUCTION_ASSISTANT_ROUTE_WARMUP_V1",
        "ok": True,
        "thread_id": thread_id,
        "token": token,
        "two_turn_exact_memory_verified": True,
        "thread_continuity_verified": True,
        "elapsed_ms": int((time.perf_counter() - started) * 1000),
        "runtime_mutation_admitted": False,
    }


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
            try:
                result = await service.send_message(
                    thread_id,
                    content=content,
                    tools=request.get("tools"),
                    response_format=request.get("response_format"),
                    custom_system_instruction=request.get("custom_system_instruction"),
                    assistant_mode=request.get("assistant_mode", "BOTH"),
                    user_context=request.get("user_context"),
                )
            except ValueError as exc:
                await websocket.send_json({
                    "schema": "HHS_AI_CONVERSATION_MESSAGE_REJECTION_V1",
                    "ok": False,
                    "reason": str(exc),
                })
                continue
            await websocket.send_json(result)
    except WebSocketDisconnect:
        return

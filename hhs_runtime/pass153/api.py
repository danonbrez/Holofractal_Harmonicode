from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .environment import AgentEnvironment, Pass153Error, build_default_environment

router = APIRouter(prefix="/api/pass153", tags=["Pass 153 Open Model Agent"])
environment: AgentEnvironment = build_default_environment()
GUI_ROOT = Path(__file__).resolve().parents[2] / "hhs_gui" / "pass153"


class SessionCreate(BaseModel):
    model_id: str = "hhs-reference-open-model-v1"
    session_id: str | None = None


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=131072)
    max_tokens: int = Field(default=64, ge=1, le=512)


class ToolRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


def _raise(exc: Pass153Error) -> None:
    raise HTTPException(status_code=400, detail=exc.to_dict())


@router.get("/status")
def status() -> dict[str, Any]:
    return environment.status()


@router.get("/models")
def models() -> list[dict[str, Any]]:
    return environment.status()["models"]


@router.get("/tools")
def tools() -> list[dict[str, Any]]:
    return environment.status()["tools"]


@router.post("/sessions")
def create_session(request: SessionCreate) -> dict[str, Any]:
    try:
        return environment.create_session(request.model_id, session_id=request.session_id).to_dict()
    except Pass153Error as exc:
        _raise(exc)


@router.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    try:
        return environment.sessions[session_id].to_dict()
    except KeyError:
        _raise(Pass153Error("P153_SESSION_NOT_FOUND", "session does not exist"))


@router.post("/sessions/{session_id}/chat")
def chat(session_id: str, request: ChatRequest) -> dict[str, Any]:
    try:
        return environment.chat(session_id, request.prompt, max_tokens=request.max_tokens)
    except Pass153Error as exc:
        _raise(exc)


@router.post("/sessions/{session_id}/tools/{tool_name}")
def invoke_tool(session_id: str, tool_name: str, request: ToolRequest) -> dict[str, Any]:
    try:
        return environment.invoke_tool(session_id, tool_name, request.arguments)
    except Pass153Error as exc:
        _raise(exc)


@router.get("/sessions/{session_id}/replay")
def replay(session_id: str) -> dict[str, Any]:
    try:
        return environment.replay_session(session_id)
    except Pass153Error as exc:
        _raise(exc)


@router.get("/gui")
def gui() -> FileResponse:
    return FileResponse(GUI_ROOT / "index.html", media_type="text/html")


@router.get("/gui/app.js")
def gui_js() -> FileResponse:
    return FileResponse(GUI_ROOT / "app.js", media_type="application/javascript")


@router.get("/gui/styles.css")
def gui_css() -> FileResponse:
    return FileResponse(GUI_ROOT / "styles.css", media_type="text/css")

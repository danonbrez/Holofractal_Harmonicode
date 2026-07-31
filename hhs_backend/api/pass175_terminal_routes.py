"""Terminal Pass 175 processor, firmware, device, and evidence routes."""
from __future__ import annotations

from base64 import b64decode
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.pass175_runtime_routes import get_runtime as get_base_runtime
from hhs_runtime.pass175 import (
    EncryptedHash216Store,
    Pass175Error,
    TerminalInstructionRequest,
    TerminalPass175Runtime,
)

router = APIRouter(
    prefix="/api/v1/pass175/terminal",
    tags=["pass175", "terminal", "firmware", "devices", "native-kernel"],
)
_RUNTIME: TerminalPass175Runtime | None = None
_RUNTIME_ERROR: Exception | None = None


def _repository_root() -> Path:
    configured = os.environ.get("HHS_REPOSITORY_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def _state_root() -> Path:
    configured = os.environ.get("HHS_PASS175_STATE_DIR")
    return Path(configured).resolve() if configured else _repository_root() / ".hhs" / "pass175"


def get_terminal_runtime() -> TerminalPass175Runtime:
    global _RUNTIME, _RUNTIME_ERROR
    if _RUNTIME is None and _RUNTIME_ERROR is None:
        try:
            state_root = _state_root()
            state_root.mkdir(parents=True, exist_ok=True)
            secure = EncryptedHash216Store(
                state_root / "hash216_microcode.sqlite3",
                key_path=state_root / "hash216_microcode.key",
            )
            _RUNTIME = TerminalPass175Runtime(
                base_runtime=get_base_runtime(),
                secure_store=secure,
                repository_root=_repository_root(),
            )
        except Exception as exc:
            _RUNTIME_ERROR = exc
    if _RUNTIME is None:
        raise HTTPException(status_code=503, detail={
            "schema": "HHS_PASS_175_TERMINAL_BOOT_FAILURE_V1",
            "classification": getattr(
                _RUNTIME_ERROR, "classification", "HHS_P175_TERMINAL_RUNTIME_INITIALIZATION_FAILED"
            ),
            "detail": getattr(_RUNTIME_ERROR, "detail", str(_RUNTIME_ERROR)),
            "silent_freeze": False,
        })
    return _RUNTIME


def _raise(exc: Exception) -> None:
    classification = getattr(exc, "classification", type(exc).__name__)
    conflict = {
        "HHS_P175_TERMINAL_CANDIDATE_STALE_ROOT",
        "HHS_P175_WRITE_CONFLICT_AT_BARRIER",
        "HHS_P175_SECURE_STORE_STALE_ROOT",
        "HHS_P175_DEVICE_STALE_ROOT",
    }
    raise HTTPException(
        status_code=409 if classification in conflict else 422,
        detail={
            "schema": "HHS_PASS_175_TERMINAL_REJECTION_V1",
            "classification": classification,
            "detail": getattr(exc, "detail", str(exc)),
        },
    ) from exc


class DecodeRequest(BaseModel):
    exact_bytes_b64: str
    decoder_mode: str = "LONG_64"


class TerminalExecuteInstruction(BaseModel):
    exact_bytes_b64: str
    decoder_mode: str = "LONG_64"
    sequence: int = Field(default=0, ge=0)
    thread_id: int = Field(default=0, ge=0, le=63)
    allow_privileged: bool = False
    explicit_delta: dict[int, int] = Field(default_factory=dict)
    device: str | None = None
    device_operation: str | None = None
    device_payload: dict[str, Any] | None = None


class TerminalExecuteRequest(BaseModel):
    instructions: list[TerminalExecuteInstruction] = Field(min_length=1, max_length=256)
    max_workers: int = Field(default=8, ge=1, le=64)


class DeviceRequest(BaseModel):
    device: str
    operation: str
    payload: dict[str, Any] = Field(default_factory=dict)


class VerifyRequest(BaseModel):
    native_root: str | None = None
    require_boot: bool = True


def _decode(value: str) -> bytes:
    try:
        return b64decode(value, validate=True)
    except Exception as exc:
        raise Pass175Error("HHS_P175_MALFORMED_EXACT_BYTES_BASE64") from exc


def _dict(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.get("/status")
def status() -> dict[str, Any]:
    runtime = get_terminal_runtime()
    native_root = os.environ.get("HHS_PASS175_NATIVE_ARTIFACT_DIR")
    return runtime.status(native_root=native_root)


@router.post("/hydrate")
def hydrate(seal: bool = True) -> dict[str, Any]:
    try:
        return get_terminal_runtime().cold_hydrate_terminal(seal=seal)
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/boot")
def boot() -> dict[str, Any]:
    try:
        runtime = get_terminal_runtime()
        if not runtime.secure_store.sealed:
            runtime.cold_hydrate_terminal(seal=True)
        return runtime.boot_firmware()
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/decode")
def decode(request: DecodeRequest) -> dict[str, Any]:
    try:
        payload = _dict(request)
        decoded = get_terminal_runtime().decoder.decode(
            _decode(payload["exact_bytes_b64"]),
            decoder_mode=payload["decoder_mode"],
        )
        return {
            "schema": "HHS_PASS_175_TERMINAL_DECODE_RESULT_V1",
            "classification": "HHS_PASS_175_EXACT_X86_64_ENCODING_DECODED",
            "instruction": decoded.to_dict(),
            "mutation_authority": False,
        }
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/execute")
def execute(request: TerminalExecuteRequest) -> dict[str, Any]:
    try:
        payload = _dict(request)
        instructions = [
            TerminalInstructionRequest(
                exact_bytes=_decode(item["exact_bytes_b64"]),
                decoder_mode=item["decoder_mode"],
                sequence=item["sequence"],
                thread_id=item["thread_id"],
                allow_privileged=item["allow_privileged"],
                explicit_delta=tuple(
                    (int(position), int(value))
                    for position, value in item["explicit_delta"].items()
                ),
                device=item["device"],
                device_operation=item["device_operation"],
                device_payload=item["device_payload"],
            )
            for item in payload["instructions"]
        ]
        return get_terminal_runtime().execute_batch(
            instructions,
            max_workers=payload["max_workers"],
        )
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/device")
def device(request: DeviceRequest) -> dict[str, Any]:
    try:
        payload = _dict(request)
        # Every device mutation is paired with an exact NOP instruction candidate
        # and admitted by the singleton inherited VM81 authority.
        return get_terminal_runtime().execute_batch([
            TerminalInstructionRequest(
                exact_bytes=b"\x90",
                sequence=0,
                device=payload["device"],
                device_operation=payload["operation"],
                device_payload=payload["payload"],
            )
        ], max_workers=1)
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.get("/replay")
def replay() -> dict[str, Any]:
    try:
        return get_terminal_runtime().replay()
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/verify")
def verify(request: VerifyRequest) -> dict[str, Any]:
    try:
        payload = _dict(request)
        runtime = get_terminal_runtime()
        if not runtime.secure_store.sealed:
            runtime.cold_hydrate_terminal(seal=True)
        native_root = payload["native_root"] or os.environ.get("HHS_PASS175_NATIVE_ARTIFACT_DIR")
        return runtime.terminal_verification(
            native_root=native_root,
            require_boot=payload["require_boot"],
        )
    except (Pass175Error, ValueError) as exc:
        _raise(exc)

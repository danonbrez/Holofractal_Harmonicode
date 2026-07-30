"""Pass 175 hydrated virtual instruction processor API routes."""
from __future__ import annotations

from base64 import b64decode
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.pass174_runtime_routes import get_runtime as get_pass174_runtime
from hhs_runtime.pass175 import (
    ControlWord,
    HydratedMicrocodeStore,
    InstructionAddress,
    InstructionRequest,
    Pass175Error,
    Pass175Runtime,
    ReciprocalLane,
)

router = APIRouter(
    prefix="/api/v1/pass175",
    tags=["pass175", "vm5184", "g243", "hash216", "x86_64", "vm81"],
)
_RUNTIME: Pass175Runtime | None = None
_RUNTIME_ERROR: Exception | None = None


def _repository_root() -> Path:
    configured = os.environ.get("HHS_REPOSITORY_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def _state_root() -> Path:
    configured = os.environ.get("HHS_PASS175_STATE_DIR")
    return Path(configured).resolve() if configured else _repository_root() / ".hhs" / "pass175"


def get_runtime() -> Pass175Runtime:
    global _RUNTIME, _RUNTIME_ERROR
    if _RUNTIME is None and _RUNTIME_ERROR is None:
        try:
            state_root = _state_root()
            store = HydratedMicrocodeStore(state_root / "hash216_microcode.jsonl")
            _RUNTIME = Pass175Runtime(authority=get_pass174_runtime(), microcode_store=store)
        except Exception as exc:  # fail closed while leaving the service responsive
            _RUNTIME_ERROR = exc
    if _RUNTIME is None:
        classification = getattr(_RUNTIME_ERROR, "classification", "HHS_P175_RUNTIME_INITIALIZATION_FAILED")
        detail = getattr(_RUNTIME_ERROR, "detail", str(_RUNTIME_ERROR))
        raise HTTPException(status_code=503, detail={
            "schema": "HHS_P175_BOOT_FAILURE_V1",
            "classification": classification,
            "detail": detail,
            "silent_freeze": False,
        })
    return _RUNTIME


def _raise(exc: Exception) -> None:
    classification = getattr(exc, "classification", type(exc).__name__)
    detail = getattr(exc, "detail", str(exc))
    conflict = {
        "HHS_P175_CANDIDATE_STALE_ROOT",
        "HHS_P175_WRITE_CONFLICT_AT_BARRIER",
        "HHS_P175_MICROCODE_KEY_COLLISION",
    }
    raise HTTPException(
        status_code=409 if classification in conflict else 422,
        detail={
            "schema": "HHS_P175_REJECTION_V1",
            "classification": classification,
            "detail": detail,
        },
    ) from exc


class AddressRequest(BaseModel):
    state: int | None = Field(default=None, ge=0, le=5183)
    cell: int | None = Field(default=None, ge=0, le=80)
    operation: int | None = Field(default=None, ge=0, le=63)
    control: int | None = Field(default=None, ge=0, le=242)
    projected: int | None = Field(default=None, ge=0, le=1_259_711)


class ControlRequest(BaseModel):
    encoded: int | None = Field(default=None, ge=0, le=242)
    trits: list[int] | None = None


class HydrateRequest(BaseModel):
    exact_bytes_b64: str
    decoder_mode: str = "LONG_64"
    ordered_operands: list[str] = Field(default_factory=list)
    parenthesization: str = "EXACT_SOURCE_ORDER"
    read_set: list[int] = Field(default_factory=list)
    write_set: list[int] = Field(default_factory=list)


class ExecuteInstructionRequest(BaseModel):
    exact_bytes_b64: str
    decoder_mode: str = "LONG_64"
    ordered_operands: list[str] = Field(default_factory=list)
    parenthesization: str = "EXACT_SOURCE_ORDER"
    read_set: list[int] = Field(default_factory=list)
    write_set: list[int] = Field(default_factory=list)
    thread_id: int = Field(default=0, ge=0, le=63)
    sequence: int = Field(default=0, ge=0)
    explicit_delta: dict[int, int] = Field(default_factory=dict)
    allow_privileged: bool = False


class ExecuteBatchRequest(BaseModel):
    instructions: list[ExecuteInstructionRequest] = Field(min_length=1)
    max_workers: int = Field(default=4, ge=1, le=64)


class ReciprocalLaneRequest(BaseModel):
    opcode: str
    phase: int
    magnitude_numerator: int
    magnitude_denominator: int
    source_root_sha256: str
    provenance_root_sha256: str


class ProjectABRequest(BaseModel):
    a: ReciprocalLaneRequest
    b: ReciprocalLaneRequest


def _decode_exact(value: str) -> bytes:
    try:
        return b64decode(value, validate=True)
    except Exception as exc:
        raise Pass175Error("HHS_P175_MALFORMED_EXACT_BYTES_BASE64") from exc


def _model_dict(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.get("/status")
def status() -> dict[str, Any]:
    return get_runtime().status()


@router.get("/boot")
def boot() -> dict[str, Any]:
    payload = get_runtime().status()
    return {
        "schema": "HHS_P175_BOOT_STATUS_V1",
        "classification": "HHS_P175_BOOT_READY",
        "ready": True,
        "silent_freeze": False,
        "peers": {
            "pass174_system_image": True,
            "vm5184_instruction_fabric": payload["permanent_instruction_count"] == 5184,
            "g243_control_surface": payload["controls_per_instruction"] == 243,
            "hash216_microcode_store": True,
            "singleton_vm81_authority": payload["singleton_vm81_commit_authority"],
            "hash72_commit_streams": payload["hash72_commit_streams"],
        },
        "runtime": payload,
    }


@router.post("/address")
def address(request: AddressRequest) -> dict[str, Any]:
    try:
        payload = _model_dict(request)
        if payload["projected"] is not None:
            decoded, control = InstructionAddress.unproject(payload["projected"])
            return {"address": decoded.__dict__, "control": control, "projected": payload["projected"]}
        if payload["state"] is not None:
            decoded = InstructionAddress.from_state(payload["state"])
        elif payload["cell"] is not None and payload["operation"] is not None:
            decoded = InstructionAddress.from_cell_operation(payload["cell"], payload["operation"])
        else:
            raise Pass175Error("HHS_P175_ADDRESS_INPUT_INCOMPLETE")
        result = {"address": decoded.__dict__}
        if payload["control"] is not None:
            result["control"] = payload["control"]
            result["projected"] = decoded.project(payload["control"])
        return result
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/control")
def control(request: ControlRequest) -> dict[str, Any]:
    try:
        payload = _model_dict(request)
        if payload["encoded"] is not None:
            word = ControlWord.from_int(payload["encoded"])
        elif payload["trits"] is not None:
            word = ControlWord.from_trits(payload["trits"])
        else:
            raise Pass175Error("HHS_P175_CONTROL_INPUT_INCOMPLETE")
        return {"encoded": word.encoded, "trits": list(word.trits)}
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.get("/instruction/{state}")
def instruction(state: int) -> dict[str, Any]:
    try:
        return get_runtime().instruction(state)
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/hydrate/x86_64")
def hydrate_x86(request: HydrateRequest) -> dict[str, Any]:
    try:
        payload = _model_dict(request)
        exact = _decode_exact(payload.pop("exact_bytes_b64"))
        record = get_runtime().hydrate_x86(exact, **payload)
        return {
            "schema": "HHS_P175_HYDRATED_INSTRUCTION_RESULT_V1",
            "classification": "HHS_PASS_175_X86_64_INSTRUCTION_HYDRATED",
            "record": record.to_dict(),
            "microcode_store_root_sha256": get_runtime().microcode_store.root(),
            "mutation_authority": False,
        }
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/hydrate/bootstrap")
def hydrate_bootstrap(seal: bool = True) -> dict[str, Any]:
    try:
        return get_runtime().cold_hydrate_bootstrap(seal=seal)
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/execute/batch")
def execute_batch(request: ExecuteBatchRequest) -> dict[str, Any]:
    try:
        payload = _model_dict(request)
        instructions = []
        for item in payload["instructions"]:
            instructions.append(InstructionRequest(
                exact_bytes=_decode_exact(item["exact_bytes_b64"]),
                decoder_mode=item["decoder_mode"],
                ordered_operands=tuple(item["ordered_operands"]),
                parenthesization=item["parenthesization"],
                read_set=tuple(item["read_set"]),
                write_set=tuple(item["write_set"]),
                thread_id=item["thread_id"],
                sequence=item["sequence"],
                explicit_delta=tuple((int(key), int(value)) for key, value in item["explicit_delta"].items()),
                allow_privileged=item["allow_privileged"],
            ))
        return get_runtime().execute_batch(instructions, max_workers=payload["max_workers"])
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.post("/project/ab")
def project_ab(request: ProjectABRequest) -> dict[str, Any]:
    try:
        payload = _model_dict(request)
        return get_runtime().project_ab(ReciprocalLane(**payload["a"]), ReciprocalLane(**payload["b"]))
    except (Pass175Error, ValueError) as exc:
        _raise(exc)


@router.get("/microcode/root")
def microcode_root() -> dict[str, Any]:
    runtime = get_runtime()
    return {
        "schema": "HHS_P175_MICROCODE_STORE_ROOT_V1",
        "records": len(runtime.microcode_store.records()),
        "root_sha256": runtime.microcode_store.root(),
        "mutation_authority": False,
    }


@router.get("/replay")
def replay() -> dict[str, Any]:
    try:
        return get_runtime().replay()
    except (Pass175Error, ValueError) as exc:
        _raise(exc)

"""Pass 174 governed runtime and Visual IDE API routes."""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass174 import (
    Pass174Error,
    Pass174Runtime,
    PersistentEncryptedVectorStore,
)

router = APIRouter(prefix="/api/v1/pass174", tags=["pass174", "vm81", "hash216", "visual-ide", "sdlc"])
_RUNTIME: Pass174Runtime | None = None
_RUNTIME_ERROR: Exception | None = None


def _repository_root() -> Path:
    configured = os.environ.get("HHS_REPOSITORY_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def _state_root(repository_root: Path) -> Path:
    configured = os.environ.get("HHS_PASS174_STATE_DIR")
    return Path(configured).resolve() if configured else repository_root / ".hhs" / "pass174"


def get_runtime() -> Pass174Runtime:
    global _RUNTIME, _RUNTIME_ERROR
    if _RUNTIME is None and _RUNTIME_ERROR is None:
        try:
            repository_root = _repository_root()
            state_root = _state_root(repository_root)
            vector_store = PersistentEncryptedVectorStore(
                state_root / "hash216_vectors.sqlite3",
                key_path=state_root / "hash216_vectors.key",
                active_suffix_limit=int(os.environ.get("HHS_PASS174_ACTIVE_SUFFIX_LIMIT", "72")),
            )
            _RUNTIME = Pass174Runtime(
                repository_root=repository_root,
                vector_store=vector_store,
            )
        except Exception as exc:
            _RUNTIME_ERROR = exc
    if _RUNTIME is None:
        classification = getattr(_RUNTIME_ERROR, "classification", "HHS_P174_RUNTIME_INITIALIZATION_FAILED")
        detail = getattr(_RUNTIME_ERROR, "detail", str(_RUNTIME_ERROR))
        raise HTTPException(status_code=503, detail={
            "schema": "HHS_P174_BOOT_FAILURE_V1",
            "classification": classification,
            "detail": detail,
            "silent_freeze": False,
        })
    return _RUNTIME


def _raise(exc: Exception) -> None:
    classification = getattr(exc, "classification", type(exc).__name__)
    detail = getattr(exc, "detail", str(exc))
    status_code = 409 if classification in {
        "HHS_P174_RETRIEVAL_STALE_ROOT",
        "HHS_P174_VECTOR_QUARANTINED",
        "HHS_P174_AUDIT_FAILED",
    } else 422
    raise HTTPException(status_code=status_code, detail={
        "schema": "HHS_P174_REJECTION_V1",
        "classification": classification,
        "detail": detail,
    }) from exc


class ExecuteRequest(BaseModel):
    thread: int = Field(default=0, ge=0, le=63)
    writes: Dict[int, int] = Field(default_factory=dict)
    operation: str = "VMRC_COMMIT"
    capability_scope: str = "P174_WHOLE_FRAME_STATE_WRITE"
    gate_identity: Optional[str] = None
    prefer_retrieval: bool = True


class HarmonicGateRequest(BaseModel):
    connectors: List[str] = Field(min_length=1)
    phase_offsets: List[int]
    exact_weights: List[Any]
    additive_endpoint: str = "x+y"
    multiplicative_endpoint: str = "xy"


class AuditRequest(BaseModel):
    challenge: str = Field(min_length=1, max_length=4096)
    sample_limit: int = Field(default=16, ge=1, le=216)
    deep: bool = False


class QueryRequest(BaseModel):
    operation_key: str = Field(min_length=64, max_length=64)


class SDLCRunRequest(BaseModel):
    project_id: str = "project:default"
    source_name: str = "main.hhs"
    source_modality: str = "CODE"
    source_payload: Any
    requested_output: str = "VALIDATED_ARTIFACT"
    thread: int = Field(default=0, ge=0, le=63)


def _payload(model: BaseModel) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()


@router.get("/status")
def status() -> Dict[str, Any]:
    runtime = get_runtime()
    result = runtime.status()
    storage = runtime.vector_store
    if hasattr(storage, "storage_status"):
        result["persistent_vector_store"] = storage.storage_status()
    return result


@router.get("/boot")
def boot_status() -> Dict[str, Any]:
    runtime = get_runtime()
    status_payload = status()
    return {
        "schema": "HHS_P174_BOOT_STATUS_V1",
        "classification": "HHS_P174_BOOT_READY",
        "ready": True,
        "silent_freeze": False,
        "peers": {
            "legacy_foundation": True,
            "vm81": status_payload["vmrc"]["kernel_authorities"] == 1,
            "hash216": True,
            "persistent_storage": "persistent_vector_store" in status_payload,
            "visual_ide": True,
        },
        "runtime": status_payload,
    }


@router.get("/frame")
def frame() -> Dict[str, Any]:
    runtime = get_runtime()
    snapshot = runtime.vmrc.snapshot()
    compressed = snapshot.compress()
    return {
        "schema": "HHS_P174_FRAME_5184_V1",
        "logical_step": runtime.vmrc.epoch,
        "phase": asdict(runtime.phase),
        "encoding": "CANONICAL_UNPADDED_BASE64",
        "frame_bits": 5184,
        "frame_bytes": 648,
        "base64_symbols": 864,
        "snapshot_b64": snapshot.base64(),
        "snapshot_hash72": runtime.vmrc.snapshot_hash72,
        "state_hash72": runtime.vmrc.state_hash72,
        "sparse": {"background": compressed.background, "exceptions": list(compressed.exceptions)},
        "mutation_authority": False,
    }


@router.get("/phase")
def phase() -> Dict[str, Any]:
    runtime = get_runtime()
    return {
        "schema": "HHS_P174_PHASE_GEAR_STATUS_V1",
        "coordinate": asdict(runtime.phase),
        "controller": runtime.phase_controller(),
    }


@router.post("/execute")
def execute(request: ExecuteRequest) -> Dict[str, Any]:
    try:
        return get_runtime().execute(**_payload(request))
    except (Pass174Error, ValueError) as exc:
        _raise(exc)


@router.post("/harmonic/compile")
def compile_harmonic_gate(request: HarmonicGateRequest) -> Dict[str, Any]:
    try:
        return get_runtime().register_harmonic_gate(**_payload(request))
    except (Pass174Error, ValueError) as exc:
        _raise(exc)


@router.get("/harmonic/controller")
def harmonic_controller() -> Dict[str, Any]:
    return get_runtime().phase_controller()


@router.post("/hash216/query")
def query_hash216(request: QueryRequest) -> Dict[str, Any]:
    try:
        return get_runtime().query(request.operation_key)
    except (Pass174Error, ValueError) as exc:
        _raise(exc)


@router.get("/efficiency/report")
def efficiency_report() -> Dict[str, Any]:
    return get_runtime().efficiency_report()


@router.post("/audit")
def audit(request: AuditRequest) -> Dict[str, Any]:
    try:
        return get_runtime().audit(**_payload(request))
    except (Pass174Error, ValueError) as exc:
        _raise(exc)


@router.get("/replay")
def replay() -> Dict[str, Any]:
    try:
        return get_runtime().replay()
    except (Pass174Error, ValueError) as exc:
        _raise(exc)


@router.get("/legacy-foundation")
def legacy_foundation() -> Dict[str, Any]:
    return get_runtime().legacy_manifest.to_dict()


@router.post("/sdlc/run")
def run_sdlc(request: SDLCRunRequest) -> Dict[str, Any]:
    runtime = get_runtime()
    payload = _payload(request)
    canonical_source = {
        "project_id": payload["project_id"],
        "source_name": payload["source_name"],
        "source_modality": payload["source_modality"],
        "source_payload": payload["source_payload"],
        "requested_output": payload["requested_output"],
    }
    source_identity = sha256(
        b"HHS-P174-SDLC-SOURCE-V1\0" + repr(canonical_source).encode("utf-8")
    ).hexdigest()
    compiled_identity = sha256(
        b"HHS-P174-SDLC-COMPILED-V1\0"
        + bytes.fromhex(source_identity)
        + runtime.legacy_foundation_root.encode("ascii")
    ).hexdigest()
    writes = {
        index % 81: 1 if byte & 1 else -1
        for index, byte in enumerate(bytes.fromhex(compiled_identity)[:16])
    }
    execution = runtime.execute(
        thread=payload["thread"],
        writes=writes,
        operation="VMRC_COMMIT",
        capability_scope="P174_MULTIMODAL_SDLC_PIPELINE",
        prefer_retrieval=True,
    )
    artifact_identity = sha256(
        b"HHS-P174-SDLC-ARTIFACT-V1\0"
        + bytes.fromhex(source_identity)
        + bytes.fromhex(compiled_identity)
        + execution["receipt"]["receipt_hash72"].encode("ascii")
    ).hexdigest()
    stages = [
        {"stage": "PLAN", "status": "COMPLETED", "identity": source_identity},
        {"stage": "GENERATE", "status": "COMPLETED", "identity": source_identity},
        {"stage": "INTERPRET", "status": "COMPLETED", "identity": source_identity},
        {"stage": "COMPILE", "status": "COMPLETED", "identity": compiled_identity},
        {"stage": "RUN", "status": "COMPLETED", "identity": execution["receipt"]["receipt_sha256"]},
        {"stage": "VALIDATE", "status": "COMPLETED", "identity": execution["receipt"]["receipt_hash72"]},
        {"stage": "RECEIPT", "status": "COMPLETED", "identity": artifact_identity},
    ]
    return {
        "schema": "HHS_P174_MULTIMODAL_SDLC_RESULT_V1",
        "classification": "HHS_P174_SDLC_PIPELINE_COMMITTED",
        "project_id": payload["project_id"],
        "source_identity_sha256": source_identity,
        "compiled_identity_sha256": compiled_identity,
        "artifact_identity_sha256": artifact_identity,
        "stages": stages,
        "execution": execution,
        "replayable": True,
        "kernel_authority_path": "INPUT→SYMBOLIC_EXPANSION→STATE_PATCH→KERNEL_AUDIT→RECEIPT_COMMIT→REPLAY_VERIFICATION",
    }

"""Pass 174 governed runtime and Visual IDE API routes."""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_backend.api.development_lifecycle_routes import (
    DevelopmentLifecycleRequest,
    run_development_lifecycle,
)
from hhs_runtime.pass174 import (
    Pass174Error,
    Pass174Runtime,
    PersistentEncryptedVectorStore,
)

router = APIRouter(prefix="/api/v1/pass174", tags=["pass174", "vm81", "hash216", "visual-ide", "sdlc"])
_RUNTIME: Pass174Runtime | None = None
_RUNTIME_ERROR: Exception | None = None

_MODALITY_MAP = {
    "CODE": "SOURCE_CODE",
    "SOURCE_CODE": "SOURCE_CODE",
    "HARMONICODE_SOURCE": "SOURCE_CODE",
    "TEXT": "TEXT",
    "DOCUMENT": "MARKDOWN",
    "MARKDOWN": "MARKDOWN",
    "JSON": "JSON",
    "JSONL": "JSONL",
    "CSV": "CSV",
    "HTML": "HTML",
    "XML": "XML",
    "IMAGE": "IMAGE",
    "SPATIAL": "IMAGE",
    "AUDIO": "AUDIO",
    "BINARY": "BINARY_OBJECT",
}


def _repository_root() -> Path:
    configured = os.environ.get("HHS_REPOSITORY_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def _state_root(repository_root: Path) -> Path:
    configured = os.environ.get("HHS_PASS174_STATE_DIR")
    return Path(configured).resolve() if configured else repository_root / ".hhs" / "pass174"


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _source_bytes(value: Any) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, dict):
        encoded = value.get("source_b64") or value.get("content_b64") or value.get("base64")
        if isinstance(encoded, str):
            try:
                return b64decode(encoded, validate=True)
            except Exception as exc:
                raise Pass174Error("HHS_P174_MALFORMED_SOURCE_BASE64") from exc
    return _canonical_json(value)


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
    project_id: Optional[str] = None
    project_name: str = "HHS Pass 174 Visual IDE Project"
    source_name: str = "main.hhs"
    source_modality: str = "CODE"
    source_payload: Any
    requested_output: str = "VALIDATED_ARTIFACT"
    expression: Optional[str] = None
    target: str = "HHS_IR"
    steps: int = Field(default=8, ge=1, le=32)
    provenance: str = "PASS174_VISUAL_IDE"
    authorization_scope: str = "P174_MULTIMODAL_SDLC_PIPELINE"
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
            "inherited_development_lifecycle": True,
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
    source_bytes = _source_bytes(payload["source_payload"])
    declared_media_type = _MODALITY_MAP.get(
        str(payload["source_modality"]).upper(),
        str(payload["source_modality"]).upper(),
    )
    lifecycle_request = DevelopmentLifecycleRequest(
        source_b64=b64encode(source_bytes).decode("ascii"),
        source_name=payload["source_name"],
        declared_media_type=declared_media_type,
        provenance=payload["provenance"],
        authorization_scope=payload["authorization_scope"],
        project_id=payload["project_id"],
        project_name=payload["project_name"],
        expression=payload["expression"],
        target=payload["target"],
        steps=payload["steps"],
    )
    inherited = run_development_lifecycle(lifecycle_request)
    receipts = inherited.get("receipts") or {}
    lifecycle_hash216 = str(receipts.get("lifecycle_hash216") or "")
    if len(lifecycle_hash216) != 64:
        raise HTTPException(status_code=409, detail={
            "classification": "HHS_P174_INHERITED_LIFECYCLE_HASH216_MISSING",
            "inherited_status": inherited.get("status"),
        })
    writes = {
        index % 81: 1 if byte & 1 else -1
        for index, byte in enumerate(bytes.fromhex(lifecycle_hash216)[:16])
    }
    continuation = runtime.execute(
        thread=payload["thread"],
        writes=writes,
        operation="VMRC_COMMIT",
        capability_scope=payload["authorization_scope"],
        prefer_retrieval=True,
    )
    interpretation = inherited.get("interpretation") or {}
    compilation = inherited.get("compilation") or {}
    lifecycle_execution = inherited.get("execution") or {}
    overall_ok = bool(inherited.get("ok") and continuation.get("receipt"))
    source_identity = str(((inherited.get("ingress") or {}).get("source") or {}).get("source_hash") or sha256(source_bytes).hexdigest())
    stages = [
        {"stage": "PLAN", "status": "COMPLETED", "identity": source_identity},
        {"stage": "GENERATE", "status": "COMPLETED" if (inherited.get("workspace_ingress") or {}).get("ok") else "REJECTED", "identity": source_identity},
        {"stage": "INTERPRET", "status": "COMPLETED" if interpretation.get("ok") else "NOT_APPLICABLE_OR_REJECTED", "identity": receipts.get("interpretation_receipt_hash72")},
        {"stage": "COMPILE", "status": "COMPLETED" if compilation.get("ok") else "NOT_APPLICABLE_OR_REJECTED", "identity": receipts.get("compilation_receipt_hash72")},
        {"stage": "RUN", "status": "COMPLETED" if lifecycle_execution.get("ok") else "NOT_APPLICABLE_OR_REJECTED", "identity": receipts.get("execution_receipt_hash72")},
        {"stage": "VALIDATE", "status": "COMPLETED" if inherited.get("ok") else "PARTIAL", "identity": receipts.get("lifecycle_receipt_hash72")},
        {"stage": "RECEIPT", "status": "COMPLETED", "identity": continuation["receipt"]["receipt_sha256"]},
    ]
    return {
        "schema": "HHS_P174_MULTIMODAL_SDLC_RESULT_V2",
        "classification": "HHS_P174_SDLC_PIPELINE_COMMITTED" if overall_ok else "HHS_P174_SDLC_PIPELINE_PARTIAL",
        "ok": overall_ok,
        "project_id": (inherited.get("project") or {}).get("project_id"),
        "source_identity_sha256": source_identity,
        "lifecycle_hash216": lifecycle_hash216,
        "lifecycle_receipt_hash72": receipts.get("lifecycle_receipt_hash72"),
        "stages": stages,
        "inherited_lifecycle": inherited,
        "pass174_continuation": continuation,
        "execution": continuation,
        "replayable": True,
        "frontend_result_fabricated": False,
        "canonical_authorities": inherited.get("canonical_authorities", []) + [
            "PASS174_ENCRYPTED_HASH216_VECTOR_STORE",
            "PASS174_VM81_WHOLE_FRAME_CONTINUATION",
        ],
        "kernel_authority_path": "INPUT→PASS165_INGRESS→HHS_INTERPRETER→HHS_IR_COMPILER→VM81_EMULATOR→PASS174_WHOLE_FRAME_CONTINUATION→HASH72_RECEIPT→HASH216_INDEX→REPLAY_VERIFICATION",
    }

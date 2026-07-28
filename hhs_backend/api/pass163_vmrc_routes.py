"""Pass 163 VMRC governed runtime API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass163.vmrc import VMRCError, VMRCRuntime

router = APIRouter(
    prefix="/api/runtime/vmrc",
    tags=["runtime", "vm81", "pass163", "vmrc"],
)
VMRC = VMRCRuntime()


class ParameterRequest(BaseModel):
    type: str = Field(min_length=1, max_length=128)
    value: Any
    domain: str = Field(min_length=1, max_length=256)
    phase: int = Field(ge=0, le=71)
    operator: str = Field(min_length=1, max_length=128)
    constraints: List[str] = Field(default_factory=list)
    provenance: str = Field(min_length=1, max_length=1024)


class GearRequest(BaseModel):
    source: Tuple[int, int]
    target: Tuple[int, int]
    direction: int = Field(ge=-1, le=1)
    u72_offset: int = Field(default=0, ge=0, le=71)
    xyzw_weights: List[Any] = Field(default_factory=lambda: [1, 1, 1, 1])
    operator: str = "COPY"
    invariant_set: str = "DEFAULT"


class CandidateRequest(BaseModel):
    thread: int = Field(ge=0, le=63)
    writes: Dict[int, int]
    operation: str
    expected_input_hash72: str = Field(min_length=72, max_length=72)
    expected_output_hash72: Optional[str] = Field(
        default=None,
        min_length=72,
        max_length=72,
    )
    dependency_root: str = "0" * 64
    capability_scope: str = "VMRC_STATE_WRITE"
    source_architecture: str = "REFERENCE_CPU"
    target_architecture: str = "VM81"


class CandidateIdRequest(BaseModel):
    candidate_id: str = Field(min_length=64, max_length=64)


class MemristorRequest(BaseModel):
    source: str
    target: str
    conductance: Any
    polarity: int = Field(ge=-1, le=1)
    prior_identity: Optional[str] = None
    admit: bool = False


def _payload(model: BaseModel) -> dict[str, Any]:
    return (
        model.model_dump()
        if hasattr(model, "model_dump")
        else model.dict()
    )


def _raise(exc: VMRCError) -> None:
    status = 409 if exc.classification in {
        "VMRC_STALE_ROOT",
        "VMRC_STALE_EPOCH",
        "VMRC_EXPECTED_OUTPUT_ROOT_MISMATCH",
    } else 422
    raise HTTPException(
        status_code=status,
        detail={
            "schema": "HHS_P163_VMRC_REJECTION_V1",
            "classification": exc.classification,
            "detail": exc.detail,
        },
    ) from exc


@router.get("/status")
def status() -> Dict[str, Any]:
    return VMRC.status()


@router.get("/snapshot")
def snapshot() -> Dict[str, Any]:
    snap = VMRC.snapshot()
    compressed = snap.compress()
    return {
        "schema": "HHS_P163_VMRC_SNAPSHOT_V1",
        "version": 1,
        "encoding": "RAW_BASE64",
        "data": snap.base64(),
        "expanded_bytes": 648,
        "base64_symbols": 864,
        "snapshot_hash72": VMRC.snapshot_hash72,
        "state_hash72": VMRC.state_hash72,
        "sparse": {
            "background": compressed.background,
            "exceptions": list(compressed.exceptions),
        },
    }


@router.post("/parameters")
def register_parameter(request: ParameterRequest) -> Dict[str, Any]:
    try:
        return VMRC.register_parameter(**_payload(request))
    except VMRCError as exc:
        _raise(exc)


@router.post("/gears")
def register_gear(request: GearRequest) -> Dict[str, Any]:
    payload = _payload(request)
    try:
        return VMRC.register_gear(
            tuple(payload.pop("source")),
            tuple(payload.pop("target")),
            **payload,
        )
    except VMRCError as exc:
        _raise(exc)


@router.post("/candidates")
def submit_candidate(request: CandidateRequest) -> Dict[str, Any]:
    try:
        candidate = VMRC.submit_candidate(**_payload(request))
        return {
            "candidate": candidate.__dict__,
            "mutation_authority": False,
        }
    except VMRCError as exc:
        _raise(exc)


@router.post("/candidates/validate")
def validate_candidate(request: CandidateRequest) -> Dict[str, Any]:
    try:
        candidate = VMRC.submit_candidate(**_payload(request))
        return VMRC.validate(candidate)
    except VMRCError as exc:
        _raise(exc)


@router.post("/candidates/execute")
def execute_candidate(request: CandidateRequest) -> Dict[str, Any]:
    try:
        candidate = VMRC.submit_candidate(**_payload(request))
        return VMRC.execute(candidate)
    except VMRCError as exc:
        _raise(exc)


@router.post("/commit")
def commit_candidate(request: CandidateIdRequest) -> Dict[str, Any]:
    try:
        return VMRC.commit(request.candidate_id)
    except VMRCError as exc:
        _raise(exc)


@router.post("/memristors")
def memristor(request: MemristorRequest) -> Dict[str, Any]:
    payload = _payload(request)
    admit = bool(payload.pop("admit"))
    try:
        edge = VMRC.propose_memristor(**payload)
        if admit:
            return VMRC.admit_memristor(edge)
        return {
            "edge": edge.__dict__,
            "mutation_authority": False,
            "admission": "PENDING",
        }
    except VMRCError as exc:
        _raise(exc)


@router.get("/replay")
def replay() -> Dict[str, Any]:
    try:
        return VMRC.replay()
    except VMRCError as exc:
        _raise(exc)

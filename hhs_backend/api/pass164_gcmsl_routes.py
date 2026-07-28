"""Pass 164 governed GPU-cluster scaling API."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass163.vmrc import VMRCError
from hhs_runtime.pass164.gcmsl import (
    BackendDeclaration,
    GCMSError,
    GCMSLRuntime,
    coordinate_bijection_proof,
)

router = APIRouter(
    prefix="/api/runtime/gcmsl",
    tags=["runtime", "vm81", "pass164", "gpu-cluster", "scaling-law"],
)
GCMSL = GCMSLRuntime()


class ClusterRegisterRequest(BaseModel):
    cluster_id: str = Field(min_length=1, max_length=256)
    level: int = Field(default=1, ge=1, le=16)
    tile_index: int = Field(default=0, ge=0)
    required_participant: bool = True
    backend_id: str = "cpu-reference"
    architecture: str = "CPU_REFERENCE"
    subgroup_width: int = Field(default=1, ge=1, le=4096)
    max_workgroup_size: int = Field(default=1, ge=1, le=65536)
    memory_limit_bytes: int = Field(default=1 << 30, ge=1)
    deterministic: bool = True
    supported_operations: List[str] = Field(
        default_factory=lambda: ["GCMSL_OPERATION_SUBMIT", "GCMSL_CLUSTER_REDUCE"]
    )


class CapabilityRequest(BaseModel):
    capability_scope: str = Field(min_length=1, max_length=1024)


class EdgeRequest(BaseModel):
    level: int = Field(default=1, ge=1, le=16)
    source_cluster: str
    destination_cluster: str
    domain: str
    source: str
    destination: str
    exact_weight: str
    polarity: int = Field(ge=-1, le=1)
    u72_offset: int = Field(default=0, ge=0, le=71)
    xyzw_weights: List[str] = Field(default_factory=lambda: ["1", "1", "1", "1"])
    prior_edge_id: Optional[str] = None


class OperationRequest(BaseModel):
    cluster_id: str
    vm81_position: int = Field(ge=0, le=80)
    thread: int = Field(ge=0, le=63)
    phase: int = Field(ge=0, le=71)
    trit: int = Field(ge=-1, le=1)
    operation_class: str = "GCMSL_OPERATION_SUBMIT"
    incoming_hash72: Optional[str] = Field(default=None, min_length=72, max_length=72)
    read_set_root: str = "0" * 64
    write_set_root: str = "0" * 64
    dependency_root: str = "0" * 64
    parameter_root: Optional[str] = None
    expected_output_root: Optional[str] = None
    resource_bound: int = Field(default=1, ge=1, le=5184)
    reciprocal_pair_id: Optional[str] = None
    noncommutative_order: Optional[int] = Field(default=None, ge=0)


class ReduceRequest(BaseModel):
    operation_ids: List[str] = Field(min_length=1, max_length=5184)
    required_clusters: Optional[List[str]] = None


class CommitRequest(BaseModel):
    batch_id: str = Field(min_length=64, max_length=64)


class BenchmarkRequest(BaseModel):
    scale: int = Field(default=1, ge=1, le=4096)
    active_edges: Optional[int] = Field(default=None, ge=0)


def _payload(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_none=True)
    return model.dict(exclude_none=True)


def _run(callable_, *args, **kwargs):
    try:
        return callable_(*args, **kwargs)
    except (GCMSError, VMRCError) as exc:
        classification = getattr(exc, "classification", exc.__class__.__name__)
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_PASS_164_GCMSL_REJECTION_V1",
                "classification": classification,
                "reason": str(exc),
            },
        ) from exc


@router.get("/status")
def status() -> Dict[str, Any]:
    return GCMSL.status()


@router.get("/coordinate-bijection")
def coordinate_bijection() -> Dict[str, Any]:
    return _run(coordinate_bijection_proof)


@router.post("/clusters")
def register_cluster(request: ClusterRegisterRequest) -> Dict[str, Any]:
    data = _payload(request)
    backend = BackendDeclaration(
        backend_id=data.pop("backend_id"),
        architecture=data.pop("architecture"),
        subgroup_width=data.pop("subgroup_width"),
        max_workgroup_size=data.pop("max_workgroup_size"),
        memory_limit_bytes=data.pop("memory_limit_bytes"),
        deterministic=data.pop("deterministic"),
        supported_operations=tuple(data.pop("supported_operations")),
    )
    return _run(GCMSL.register_cluster, backend=backend, **data)


@router.post("/clusters/{cluster_id}/capabilities")
def grant_capability(cluster_id: str, request: CapabilityRequest) -> Dict[str, Any]:
    return _run(GCMSL.grant_capability, cluster_id, request.capability_scope)


@router.post("/edges")
def register_edge(request: EdgeRequest) -> Dict[str, Any]:
    return _run(GCMSL.register_edge, **_payload(request))


@router.post("/operations")
def submit_operation(request: OperationRequest) -> Dict[str, Any]:
    return _run(GCMSL.submit_operation, **_payload(request))


@router.post("/reduce")
def reduce(request: ReduceRequest) -> Dict[str, Any]:
    return _run(
        GCMSL.reduce,
        request.operation_ids,
        required_clusters=request.required_clusters,
    )


@router.post("/commit")
def commit(request: CommitRequest) -> Dict[str, Any]:
    return _run(GCMSL.commit, request.batch_id)


@router.get("/replay")
def replay() -> Dict[str, Any]:
    return _run(GCMSL.replay)


@router.post("/benchmark")
def benchmark(request: BenchmarkRequest) -> Dict[str, Any]:
    return _run(GCMSL.benchmark, **_payload(request))

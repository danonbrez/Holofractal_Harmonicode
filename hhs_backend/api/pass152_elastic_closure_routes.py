from __future__ import annotations

import copy
import os
import sys
import uuid
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass152 import HHSRuntimeControllerAuthority, delayed_closure_workload
from hhs_runtime.hhs_runtime_contract_v1 import envelope_api_response


# Preserve the historical route-first binding used by the inherited public
# surface while avoiding a recursive runtime_routes import when the canonical
# server itself is currently composing this router.
if "hhs_backend.server" not in sys.modules:
    from hhs_backend.api.runtime_routes import runtime_controller as _BOUND_RUNTIME_CONTROLLER
else:
    _BOUND_RUNTIME_CONTROLLER = None


router = APIRouter(
    prefix="/api/runtime/pass152",
    tags=["runtime", "pass152", "elastic-closure"],
)

_RECEIPT_ROOT = Path(os.environ.get("HHS_PASS152_RECEIPT_ROOT", "receipts/pass152/api"))
_LATEST_LOCK = RLock()
_LATEST: Optional[dict[str, Any]] = None


class Pass152ExecuteRequest(BaseModel):
    delay_ms: int = Field(default=5, ge=0, le=250)
    workers: int = Field(default=4, ge=1, le=8)


def _runtime_controller():
    global _BOUND_RUNTIME_CONTROLLER
    if _BOUND_RUNTIME_CONTROLLER is None:
        from hhs_backend.api.runtime_routes import runtime_controller
        _BOUND_RUNTIME_CONTROLLER = runtime_controller
    return _BOUND_RUNTIME_CONTROLLER


def _summary(result: dict[str, Any], run_id: str, receipt_dir: Path) -> dict[str, Any]:
    proof = result["proof"]
    commit = result["commit"]
    replay = result["replay"]
    metrics = result["metrics"]
    return {
        "schema": "HHS_PASS152_EXECUTION_RESPONSE_V1",
        "run_id": run_id,
        "classification": (
            "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED"
            if proof.get("omega_closure") and replay.get("replay_status") == "MATCH"
            else "CLOSURE_INCOMPLETE"
        ),
        "invariant": "DELAY_AUTHORITY_NOT_COMPUTATION",
        "recursive_control_invariant": "PRESERVE_CAUSAL_AUTHORITY_AT_INVARIANT_CORE_WHILE_USING_EMERGENT_FREEDOM_TO_OPTIMIZE_SUBORDINATE_EXECUTION",
        "proof": copy.deepcopy(proof),
        "commit": copy.deepcopy(commit),
        "replay": copy.deepcopy(replay),
        "metrics": copy.deepcopy(metrics),
        "receipt_directory": str(receipt_dir),
        "authority_boundary": {
            "local_propagation": "PREDICTIVE_NON_AUTHORITATIVE",
            "commit": "VM81_ONLY",
            "receipt": "HASH72_AFTER_VM81_ADMISSION",
            "higher_layer_control": "POLICY_ONLY_NOT_TRUTH",
        },
    }


@router.get("/status")
def pass152_status() -> Dict[str, Any]:
    with _LATEST_LOCK:
        latest = copy.deepcopy(_LATEST)
    payload = {
        "schema": "HHS_PASS152_STATUS_V2",
        "pass": 152,
        "contract_id": "HHS-P152-UECI",
        "status": "IMPLEMENTED_EXECUTION_VERIFIED",
        "terminal_success_classification": "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED",
        "canonical_invariant": "DELAY_AUTHORITY_NOT_COMPUTATION",
        "recursive_control_invariant": "EXPLOIT_FREEDOM_RECURSIVELY_PRESERVE_INVARIANTS_ABSOLUTELY_EXTEND_HISTORY_MONOTONICALLY",
        "authority": {
            "semantic_commit": "VM81",
            "runtime_receipts": "Hash72",
            "independent_security_memory": "Hash216",
            "predictive_traces": "NON_AUTHORITATIVE_EVIDENCE",
        },
        "latest_execution": latest,
    }
    return envelope_api_response("/api/runtime/pass152/status", "GET", payload)


@router.get("/capabilities")
def pass152_capabilities() -> Dict[str, Any]:
    payload = {
        "schema": "HHS_PASS152_CAPABILITIES_V1",
        "candidate_lifecycle": [
            "UNSEEN", "BLOCKED", "PARTIAL", "READY", "EVALUATING",
            "PROVISIONAL", "VERIFIED", "INVALIDATED", "CONFLICT",
            "RESOURCE_BOUNDED", "COMMITTED",
        ],
        "edge_types": [
            "VALUE_DEPENDS_ON", "CONSTRAINT_DEPENDS_ON", "AUTHORITY_DEPENDS_ON",
            "PROVENANCE_DEPENDS_ON", "RECEIPT_DEPENDS_ON",
            "RESOURCE_DEPENDS_ON", "CLOSURE_DEPENDS_ON",
        ],
        "recursive_layers": [
            {"layer_id": "L0", "role": "INVARIANT_CORE"},
            {"layer_id": "L1", "role": "ELASTIC_CLOSURE_EXECUTION"},
            {"layer_id": "L2", "role": "SUPERVISORY_POLICY_OPTIMIZATION"},
        ],
        "admissible_control_vectors": [
            "scheduling", "resource_allocation", "branch_priority",
            "cache_placement", "equivalence_reuse", "speculative_depth",
            "representation_choice", "batching", "transport_order",
        ],
        "prohibited_control_mutations": [
            "invariant_truth", "committed_state", "provenance",
            "authority_boundary", "receipt_history", "semantic_identity",
        ],
        "routes": [
            "GET /api/runtime/pass152/status",
            "GET /api/runtime/pass152/capabilities",
            "GET /api/runtime/pass152/latest",
            "POST /api/runtime/pass152/execute",
        ],
    }
    return envelope_api_response("/api/runtime/pass152/capabilities", "GET", payload)


@router.get("/latest")
def pass152_latest() -> Dict[str, Any]:
    with _LATEST_LOCK:
        if _LATEST is None:
            payload = {
                "schema": "HHS_PASS152_LATEST_RESPONSE_V1",
                "available": False,
                "classification": "NO_EXECUTION_RECORDED",
            }
        else:
            payload = {
                "schema": "HHS_PASS152_LATEST_RESPONSE_V1",
                "available": True,
                "execution": copy.deepcopy(_LATEST),
            }
    return envelope_api_response("/api/runtime/pass152/latest", "GET", payload)


@router.post("/execute")
def pass152_execute(request: Pass152ExecuteRequest) -> Dict[str, Any]:
    run_id = "p152-" + uuid.uuid4().hex
    receipt_dir = _RECEIPT_ROOT / run_id
    try:
        result = delayed_closure_workload(
            receipt_dir,
            HHSRuntimeControllerAuthority(_runtime_controller()).admit,
            delay_seconds=request.delay_ms / 1000.0,
            workers=request.workers,
        )
        response = _summary(result, run_id, receipt_dir)
    except Exception as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "schema": "HHS_PASS152_EXECUTION_FAILURE_V1",
                "classification": type(exc).__name__,
                "message": str(exc),
                "run_id": run_id,
            },
        ) from exc
    with _LATEST_LOCK:
        global _LATEST
        _LATEST = copy.deepcopy(response)
    return envelope_api_response("/api/runtime/pass152/execute", "POST", response)

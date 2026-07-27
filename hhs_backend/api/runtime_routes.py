from __future__ import annotations

from hhs_backend.runtime.hhs_deterministic_manifold_execution_v1 import run_deterministic_manifold_execution
from hhs_backend.runtime.hhs_global_reciprocal_contract_topology_v1 import run_global_reciprocal_contract_topology
from hhs_backend.runtime.hhs_federated_transaction_recovery_v1 import run_federated_transaction_recovery
from hhs_backend.runtime.hhs_bounded_rejection_authority_v1 import run_bounded_rejection_authority
# ============================================================================
# hhs_backend/api/runtime_routes.py
# HARMONICODE / HHS
# CANONICAL RUNTIME API ROUTES
#
# PURPOSE
# -------
# Network-accessible deterministic runtime execution layer.
#
# This module exposes:
#
#   - runtime execution
#   - receipt-chain control
#   - graph ingestion
#   - replay APIs
#   - vector prediction APIs
#   - websocket streaming
#   - sandbox orchestration
#
# ALL backend runtime access MUST flow through here.
#
# ============================================================================


import asyncio
import json
import time
import uuid

from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    HTTPException
)

from pydantic import BaseModel

from hhs_python.runtime.hhs_runtime_controller import (
    HHSRuntimeController
)

from hhs_python.runtime.hhs_runtime_emulator import (
    HHSCEmulator,
)

from hhs_runtime.hhs_service_registry_v1 import (
    HHSServiceRegistryError,
)

from hhs_runtime.hhs_io_gateway_v1 import (
    HHSIOGateway,
)

from hhs_runtime.hhs_runtime_contract_v1 import (
    envelope_api_response,
    make_runtime_packet,
)

from hhs_runtime.hhs_srcg_gate_v1 import (
    selfsolve_ab_gate,
)

from hhs_runtime.hhs_system_closure_harness_v1 import (
    system_closure_harness_self_test,
)

from hhs_runtime.hhs_runtime_constraint_enforcement_binding_v1 import (
    enforce_runtime_constraint_boundary,
)

from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import (
    guarded_surface_propagation,
    interpose_runtime_surface,
)

from hhs_runtime.hhs_kernel_invariant_registry_v1 import (
    get_invariant,
    list_invariants,
    validate_invariant_registry,
)
from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import (
    build_surface_map,
)
from hhs_runtime.hhs_kernel_conformance_decision_v1 import (
    evaluate_operation,
    evaluate_surface,
)


from hhs_backend.runtime.hhs_role_bound_agent_orchestrator_v1 import (
    run_role_bound_orchestration, build_role_contract, build_competency_record,
    build_task_assignment, build_handoff, validate_handoff, validate_derivation_equivalence,
    independently_revalidate, admit_response_candidate, build_authority_graph, validate_local_authority,
)


from hhs_backend.runtime.hhs_authority_enforced_dispatch_v1 import (
    run_authority_enforced_dispatch, issue_capability_lease, validate_dispatch,
    validate_execution_checkpoint, transition_lease, lease_with_state,
)

from hhs_backend.runtime.hhs_distributed_authority_federation_v1 import (
    run_distributed_authority_federation, build_federation_contract, build_remote_identity,
    issue_sublease, build_delegation_chain, validate_remote_dispatch,
    build_remote_checkpoint_chain, build_remote_receipt, federated_ingress, propagate_revocation,
)
from hhs_backend.runtime.hhs_partition_tolerant_federated_recovery_v1 import (
    run_partition_tolerant_federated_recovery, build_partition_evidence,
    build_revocation_vote, resolve_revocation_consensus, quarantine_stale_sublease,
    reconcile_partition, recover_federation,
)
from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import (
    run_canonical_federated_state_reconciliation, build_federated_state_snapshot,
    classify_state_conflicts, build_merge_policy, merge_federated_states,
    validate_canonical_merge,
)
from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import (
    run_canonical_federated_transaction_commit, build_transaction_contract,
    build_prepare_record, decide_commit, build_participant_receipt,
    build_compensation_record, decide_rollback, finalize_transaction,
)


from hhs_graph.hhs_multimodal_receipt_graph_v1 import (
    HHSMultimodalReceiptGraph
)

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="/api/runtime",
    tags=["runtime"]
)

# ============================================================================
# GLOBAL RUNTIME
# ============================================================================

runtime_controller = HHSRuntimeController()

runtime_emulator = HHSCEmulator(controller=runtime_controller)

runtime_graph = HHSMultimodalReceiptGraph()

io_gateway = HHSIOGateway(runtime_controller)


def _contract_response(route: str, method: str, payload: Dict[str, Any], *, io: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return envelope_api_response(route, method, payload, io=io or payload.get("io") or {})


def _contract_packet(direction: str, source: str, payload: Dict[str, Any], *, io_receipt: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return make_runtime_packet(direction, source, payload, io_receipt=io_receipt or {})

# ============================================================================
# WEBSOCKET CLIENTS
# ============================================================================

runtime_clients: List[WebSocket] = []

# ============================================================================
# REQUEST MODELS
# ============================================================================

class RuntimeStepRequest(BaseModel):

    steps: int = 1

# ----------------------------------------------------------------------------

class RuntimeServiceDispatchRequest(BaseModel):

    service: str

    payload: Optional[Dict[str, Any]] = None

# ----------------------------------------------------------------------------

class SRCGSelfSolveRequest(BaseModel):

    A: float = 1.0

    B: float = 1.0

    learning_rate: float = 0.125

    drift_threshold: float = 1.001

    max_steps: int = 1

    quartic_carrier: Optional[Any] = None

    proposition: Optional[str] = None

# ----------------------------------------------------------------------------

class ClosureHarnessRequest(BaseModel):

    proposition: Optional[str] = None

    cycles: int = 2

    A: float = 1.0005

    B: float = 1.0

    max_steps: int = 2

# ----------------------------------------------------------------------------

class RuntimeConstraintEnforcementRequest(BaseModel):

    surface: str = "api.runtime.admissibility.enforce"

    request_class: str = "canonical_full_witness_chain"

    candidate: Optional[Dict[str, Any]] = None

    brute_force_claim: bool = False

# ----------------------------------------------------------------------------

class RuntimeZeroBypassInterpositionRequest(BaseModel):

    surface: str = "service_registry.dispatch"

    request_class: str = "canonical_full_witness_chain"

    payload: Optional[Dict[str, Any]] = None

    brute_force_claim: bool = False

    attempted_operation: str = "guarded_runtime_surface_propagation"

# ----------------------------------------------------------------------------

class KernelConformanceEvaluationRequest(BaseModel):

    surface_id: str

    operation: Optional[str] = None

    contract_schema: Optional[str] = None

# ----------------------------------------------------------------------------

class SandboxCreateRequest(BaseModel):

    metadata: Optional[Dict] = None

# ============================================================================
# HELPERS
# ============================================================================

async def broadcast_runtime_state():

    if not runtime_clients:
        return

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    dead = []

    for ws in runtime_clients:

        try:

            await ws.send_text(
                json.dumps(_contract_packet("EGRESS", "api.runtime.broadcast", packet))
            )

        except Exception:

            dead.append(ws)

    for ws in dead:

        if ws in runtime_clients:
            runtime_clients.remove(ws)

# ============================================================================
# RUNTIME ROUTES
# ============================================================================

@router.get("/state")
async def get_runtime_state():

    ingress = io_gateway.ingress("api.runtime.state", {"method": "GET"})
    state = runtime_controller.latest_runtime_state()
    egress = io_gateway.egress("api.runtime.state", {"method": "GET", "step": state.get("step")})
    return _contract_response("/api/runtime/state", "GET", {"schema": "HHS_GUARDED_RUNTIME_STATE_RESPONSE_V1", "runtime": state, "io": {"ingress": ingress, "egress": egress}})

# ----------------------------------------------------------------------------

@router.post("/step")
async def runtime_step(
    request: RuntimeStepRequest
):

    ingress = io_gateway.ingress("api.runtime.step", {"steps": request.steps})

    result = runtime_emulator.run(
        steps=request.steps
    )

    packet = result.get("last_packet")

    if packet is not None:

        runtime_graph.ingest_runtime_state(packet)

    await broadcast_runtime_state()

    response = {

        "schema":
            "HHS_GUARDED_RUNTIME_STEP_RESPONSE_V1",

        "steps_executed":
            result["executed_steps"],

        "runtime":
            result["runtime"],

        "emulator":
            {
                "boot_id": result["boot_id"],
                "requested_steps": result["requested_steps"],
                "capped": result["capped"],
            },

        "guarded":
            True,
    }

    response["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress("api.runtime.step", {"steps_executed": response["steps_executed"], "step": response["runtime"].get("step")}),
    }

    return _contract_response("/api/runtime/step", "POST", response)

# ----------------------------------------------------------------------------

@router.post("/halt")
async def halt_runtime():

    ingress = io_gateway.ingress("api.runtime.halt", {"method": "POST"})
    result = runtime_controller.halt()

    await broadcast_runtime_state()

    egress = io_gateway.egress("api.runtime.halt", {"halted": True})
    return _contract_response("/api/runtime/halt", "POST", {"schema": "HHS_GUARDED_RUNTIME_HALT_RESPONSE_V1", "runtime": result, "io": {"ingress": ingress, "egress": egress}})

# ----------------------------------------------------------------------------

@router.post("/receipt/commit")
async def commit_receipt():

    ingress = io_gateway.ingress("api.runtime.receipt.commit", {"method": "POST"})
    receipt = runtime_controller.commit_receipt()
    egress = io_gateway.egress("api.runtime.receipt.commit", {"receipt_hash72": receipt.get("receipt_hash72", "")})

    return _contract_response("/api/runtime/receipt/commit", "POST", {"schema": "HHS_GUARDED_RECEIPT_COMMIT_RESPONSE_V1", "receipt": receipt, "io": {"ingress": ingress, "egress": egress}})


# ============================================================================
# GUARDED SERVICE ROUTES
# ============================================================================

@router.get("/services")
async def list_runtime_services():

    ingress = io_gateway.ingress("api.runtime.services", {"method": "GET"})
    response = {
        "schema": "HHS_RUNTIME_SERVICE_LIST_V1",
        "services": runtime_emulator.service_registry.services(),
    }
    response["io"] = {"ingress": ingress, "egress": io_gateway.egress("api.runtime.services", {"service_count": len(response["services"])})}
    return _contract_response("/api/runtime/services", "GET", response)

# ----------------------------------------------------------------------------

@router.get("/services/status")
async def runtime_services_status():

    ingress = io_gateway.ingress("api.runtime.services.status", {"method": "GET"})
    status = runtime_emulator.service_registry.status()
    egress = io_gateway.egress("api.runtime.services.status", {"service_count": status.get("service_count", 0)})
    return _contract_response("/api/runtime/services/status", "GET", {"schema": "HHS_GUARDED_SERVICE_STATUS_RESPONSE_V1", "status": status, "io": {"ingress": ingress, "egress": egress}})

# ----------------------------------------------------------------------------

@router.post("/services/dispatch")
async def dispatch_runtime_service(
    request: RuntimeServiceDispatchRequest
):

    ingress = io_gateway.ingress("api.runtime.services.dispatch", {"service": request.service, "payload": request.payload or {}})

    request_payload = dict(request.payload or {})
    interposition = interpose_runtime_surface(
        surface="service_registry.dispatch",
        request_class=str(request_payload.get("request_class") or "canonical_full_witness_chain"),
        payload={
            "schema": "HHS_API_SERVICE_DISPATCH_TO_NATIVE_INTERPOSITION_V1",
            "service": request.service,
            "payload": request_payload,
        },
        brute_force_claim=bool(request_payload.get("brute_force_claim", False)),
    )
    if not interposition.get("propagation_allowed"):
        raise HTTPException(
            status_code=403,
            detail={
                "schema": "HHS_ZERO_BYPASS_SERVICE_DISPATCH_REJECTION_V1",
                "reason": "service dispatch rejected by zero-bypass interposer",
                "interposition": interposition,
            },
        )
    request_payload["zero_bypass_interposition_token"] = interposition.get("interposition_token")

    try:

        result = runtime_emulator.dispatch_service(
            request.service,
            request_payload,
        )
        result["zero_bypass_interposition"] = {
            "status": interposition.get("status"),
            "token_digest72": (interposition.get("interposition_token") or {}).get("token_digest72"),
            "surface": interposition.get("surface"),
        }

    except HHSServiceRegistryError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)

    await broadcast_runtime_state()

    result["io"] = {
        "ingress": ingress,
        "egress": io_gateway.egress("api.runtime.services.dispatch", {"service": request.service, "record_schema": result.get("schema")}),
    }

    return _contract_response("/api/runtime/services/dispatch", "POST", result)

# ============================================================================
# KERNEL CONFORMANCE ROUTES
# ============================================================================

@router.get("/conformance/invariants")
async def list_kernel_conformance_invariants():

    ingress = io_gateway.ingress("api.runtime.conformance.invariants", {"method": "GET"})
    invariants = list_invariants()
    egress = io_gateway.egress("api.runtime.conformance.invariants", {"invariant_count": len(invariants)})
    return _contract_response(
        "/api/runtime/conformance/invariants",
        "GET",
        {"schema": "HHS_KERNEL_CONFORMANCE_INVARIANT_LIST_RESPONSE_V1", "invariants": invariants, "io": {"ingress": ingress, "egress": egress}},
    )

# ----------------------------------------------------------------------------

@router.get("/conformance/invariants/{invariant_id}")
async def get_kernel_conformance_invariant(invariant_id: str):

    ingress = io_gateway.ingress("api.runtime.conformance.invariant", {"method": "GET", "invariant_id": invariant_id})
    try:
        invariant = get_invariant(invariant_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"unknown invariant: {invariant_id}") from exc
    egress = io_gateway.egress("api.runtime.conformance.invariant", {"invariant_id": invariant_id})
    return _contract_response(
        f"/api/runtime/conformance/invariants/{invariant_id}",
        "GET",
        {"schema": "HHS_KERNEL_CONFORMANCE_INVARIANT_RESPONSE_V1", "invariant": invariant, "io": {"ingress": ingress, "egress": egress}},
    )

# ----------------------------------------------------------------------------

@router.get("/conformance/surfaces")
async def list_kernel_conformance_surfaces():

    ingress = io_gateway.ingress("api.runtime.conformance.surfaces", {"method": "GET"})
    surface_map = build_surface_map()
    surfaces = surface_map.get("surfaces", [])
    egress = io_gateway.egress("api.runtime.conformance.surfaces", {"surface_count": len(surfaces), "root": surface_map.get("conformance_root_hash72")})
    return _contract_response(
        "/api/runtime/conformance/surfaces",
        "GET",
        {"schema": "HHS_KERNEL_CONFORMANCE_SURFACE_LIST_RESPONSE_V1", "surfaces": surfaces, "conformance_root_hash72": surface_map.get("conformance_root_hash72"), "io": {"ingress": ingress, "egress": egress}},
    )

# ----------------------------------------------------------------------------

@router.get("/conformance/surfaces/{surface_id:path}")
async def get_kernel_conformance_surface(surface_id: str):

    ingress = io_gateway.ingress("api.runtime.conformance.surface", {"method": "GET", "surface_id": surface_id})
    surface_map = build_surface_map()
    candidates = [s for s in surface_map.get("surfaces", []) if s.get("surface_id") == surface_id]
    if not candidates:
        raise HTTPException(status_code=404, detail=f"unknown conformance surface: {surface_id}")
    egress = io_gateway.egress("api.runtime.conformance.surface", {"surface_id": surface_id})
    return _contract_response(
        f"/api/runtime/conformance/surfaces/{surface_id}",
        "GET",
        {"schema": "HHS_KERNEL_CONFORMANCE_SURFACE_RESPONSE_V1", "surface": candidates[0], "io": {"ingress": ingress, "egress": egress}},
    )

# ----------------------------------------------------------------------------

@router.post("/conformance/evaluate")
async def evaluate_kernel_conformance_surface(request: KernelConformanceEvaluationRequest):

    ingress = io_gateway.ingress("api.runtime.conformance.evaluate", {"method": "POST", "surface_id": request.surface_id, "operation": request.operation})
    surface_map = build_surface_map()
    candidates = [s for s in surface_map.get("surfaces", []) if s.get("surface_id") == request.surface_id]
    if not candidates:
        raise HTTPException(status_code=404, detail=f"unknown conformance surface: {request.surface_id}")
    surface = dict(candidates[0])
    if request.contract_schema:
        surface.setdefault("contract_schemas", []).append(request.contract_schema)
    decision = evaluate_operation(surface, request.operation or str(surface.get("symbol", "")))
    egress = io_gateway.egress("api.runtime.conformance.evaluate", {"surface_id": request.surface_id, "status": decision.get("status")})
    decision["io"] = {"ingress": ingress, "egress": egress}
    return _contract_response("/api/runtime/conformance/evaluate", "POST", decision)

# ----------------------------------------------------------------------------

@router.get("/conformance/status")
async def kernel_conformance_status():

    ingress = io_gateway.ingress("api.runtime.conformance.status", {"method": "GET"})
    invariant_status = validate_invariant_registry()
    surface_map = build_surface_map()
    response = {
        "schema": "HHS_KERNEL_CONFORMANCE_STATUS_RESPONSE_V1",
        "invariant_count": invariant_status.get("invariant_count"),
        "surface_count": surface_map.get("surface_count"),
        "conformance_edge_count": surface_map.get("conformance_edge_count"),
        "underived_surface_count": len(surface_map.get("underived_surfaces", [])),
        "conformance_root_hash72": surface_map.get("conformance_root_hash72"),
        "registry_root_hash72": invariant_status.get("registry_root_hash72"),
    }
    response["io"] = {"ingress": ingress, "egress": io_gateway.egress("api.runtime.conformance.status", {"underived_surface_count": response["underived_surface_count"]})}
    return _contract_response("/api/runtime/conformance/status", "GET", response)

# ============================================================================
# CONSTRAINT-STACK ENFORCEMENT ROUTES
# ============================================================================

@router.post("/admissibility/enforce")
async def enforce_runtime_admissibility(
    request: RuntimeConstraintEnforcementRequest
):

    ingress = io_gateway.ingress(
        "api.runtime.admissibility.enforce",
        {
            "surface": request.surface,
            "request_class": request.request_class,
            "brute_force_claim": request.brute_force_claim,
        },
    )

    decision = enforce_runtime_constraint_boundary(
        surface=request.surface,
        request_class=request.request_class,
        candidate=request.candidate,
        brute_force_claim=request.brute_force_claim,
    )

    egress = io_gateway.egress(
        "api.runtime.admissibility.enforce",
        {
            "status": decision.get("status"),
            "admitted": decision.get("admitted"),
            "enforcement_action": decision.get("enforcement_action"),
        },
    )

    decision["io"] = {
        "ingress": ingress,
        "egress": egress,
    }

    return _contract_response(
        "/api/runtime/admissibility/enforce",
        "POST",
        decision,
    )

# ----------------------------------------------------------------------------

@router.post("/admissibility/interpose")
async def interpose_runtime_admissibility(
    request: RuntimeZeroBypassInterpositionRequest
):

    ingress = io_gateway.ingress(
        "api.runtime.admissibility.interpose",
        {
            "surface": request.surface,
            "request_class": request.request_class,
            "brute_force_claim": request.brute_force_claim,
        },
    )

    interposition = interpose_runtime_surface(
        surface=request.surface,
        request_class=request.request_class,
        payload=request.payload,
        brute_force_claim=request.brute_force_claim,
    )

    guarded = guarded_surface_propagation(
        surface=request.surface,
        attempted_operation=request.attempted_operation,
        payload=request.payload,
        interposition_token=interposition.get("interposition_token"),
    ) if interposition.get("propagation_allowed") else None

    egress = io_gateway.egress(
        "api.runtime.admissibility.interpose",
        {
            "status": interposition.get("status"),
            "propagation_allowed": interposition.get("propagation_allowed"),
            "guarded_status": guarded.get("status") if guarded else "NOT_ATTEMPTED",
        },
    )

    response = {
        "schema": "HHS_ZERO_BYPASS_RUNTIME_INTERPOSITION_API_RESPONSE_V1",
        "interposition": interposition,
        "guarded_propagation": guarded,
        "io": {"ingress": ingress, "egress": egress},
    }

    return _contract_response(
        "/api/runtime/admissibility/interpose",
        "POST",
        response,
    )

# ----------------------------------------------------------------------------

# ============================================================================
# SRCG PRIMITIVE ROUTES
# ============================================================================

@router.post("/srcg/selfsolve")
async def srcg_selfsolve(
    request: SRCGSelfSolveRequest
):

    payload: Dict[str, Any] = {
        "A": request.A,
        "B": request.B,
        "learning_rate": request.learning_rate,
        "drift_threshold": request.drift_threshold,
        "max_steps": request.max_steps,
    }

    if request.quartic_carrier is not None:
        payload["quartic_carrier"] = request.quartic_carrier

    if request.proposition is not None:
        payload["proposition"] = request.proposition

    ingress = io_gateway.ingress(
        "api.runtime.srcg.selfsolve",
        {
            "primitive": "SelfSolve_AB_Gate",
            "A": request.A,
            "B": request.B,
            "max_steps": request.max_steps,
        },
    )

    result = selfsolve_ab_gate(payload)

    # Make the primitive visible to graph/replay state without bypassing the
    # canonical IO gateway or service/contract surfaces.
    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)

    await broadcast_runtime_state()

    egress = io_gateway.egress(
        "api.runtime.srcg.selfsolve",
        {
            "primitive": "SelfSolve_AB_Gate",
            "ok": result.get("ok"),
            "trace_count": len(result.get("trace", [])),
            "witness_id": (
                result.get("trace", [{}])[-1]
                .get("hash72_kernel_witness", {})
                .get("witness_id")
                if result.get("trace")
                else ""
            ),
        },
    )

    response = {
        "schema": "HHS_SRCG_SELFSOLVE_API_RESPONSE_V1",
        "primitive": "SelfSolve_AB_Gate",
        "result": result,
        "io": {
            "ingress": ingress,
            "egress": egress,
        },
    }

    return _contract_response(
        "/api/runtime/srcg/selfsolve",
        "POST",
        response,
    )

# ----------------------------------------------------------------------------

@router.post("/closure/harness")
async def system_closure_harness(
    request: ClosureHarnessRequest
):

    ingress = io_gateway.ingress(
        "api.runtime.closure.harness",
        {
            "cycles": request.cycles,
            "A": request.A,
            "B": request.B,
            "max_steps": request.max_steps,
            "proposition": request.proposition or "",
        },
    )

    result = system_closure_harness_self_test({
        "proposition": request.proposition or "Meaning is conserved through the Hash72/u^72 guarded SRCG execution chain.",
        "cycles": request.cycles,
        "A": request.A,
        "B": request.B,
        "max_steps": request.max_steps,
    })

    packet = runtime_controller.export_multimodal_packet()
    runtime_graph.ingest_runtime_state(packet)

    await broadcast_runtime_state()

    egress = io_gateway.egress(
        "api.runtime.closure.harness",
        {
            "ok": result.get("ok"),
            "converged": result.get("converged"),
            "stable_signature": result.get("stable_signature") or "",
        },
    )

    result["io"] = {
        "ingress": ingress,
        "egress": egress,
    }

    return _contract_response(
        "/api/runtime/closure/harness",
        "POST",
        result,
    )

# ----------------------------------------------------------------------------

# ============================================================================
# GRAPH ROUTES
# ============================================================================

@router.get("/graph/summary")
async def graph_summary():

    ingress = io_gateway.ingress("api.runtime.graph.summary", {"method": "GET"})
    summary = runtime_graph.export_graph_summary()
    egress = io_gateway.egress("api.runtime.graph.summary", {"node_count": summary.get("node_count", 0)})
    return _contract_response("/api/runtime/graph/summary", "GET", {"schema": "HHS_GUARDED_GRAPH_SUMMARY_RESPONSE_V1", "graph": summary, "io": {"ingress": ingress, "egress": egress}})

# ----------------------------------------------------------------------------

@router.get("/graph/hash/{hash72}")
async def graph_lookup_hash(
    hash72: str
):

    ingress = io_gateway.ingress("api.runtime.graph.hash", {"hash72": hash72})

    node = runtime_graph.get_by_hash72(hash72)

    if node is None:

        raise HTTPException(
            status_code=404,
            detail="Hash72 node not found"
        )

    egress = io_gateway.egress("api.runtime.graph.hash", {"found": True})
    return _contract_response(
        f"/api/runtime/graph/hash/{hash72}",
        "GET",
        {
            "schema": "HHS_GRAPH_NODE_RESPONSE_V1",
            "hash72": hash72,
            "node": node,
            "io": {"ingress": ingress, "egress": egress},
        },
    )

# ----------------------------------------------------------------------------

@router.get("/graph/replay/{node_id}")
async def graph_replay(
    node_id: str
):

    if node_id not in runtime_graph.nodes:

        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )

    ingress = io_gateway.ingress("api.runtime.graph.replay", {"node_id": node_id})

    replay = runtime_graph.replay_chain(
        node_id
    )

    egress = io_gateway.egress(
        "api.runtime.graph.replay",
        {"node_id": node_id, "replay_count": len(replay) if isinstance(replay, list) else 1},
    )
    return _contract_response(
        f"/api/runtime/graph/replay/{node_id}",
        "GET",
        {
            "schema": "HHS_GRAPH_REPLAY_RESPONSE_V1",
            "node_id": node_id,
            "replay": replay,
            "io": {"ingress": ingress, "egress": egress},
        },
    )

# ============================================================================
# PREDICTION ROUTES
# ============================================================================

@router.get("/predict/{node_id}")
async def predict_next_states(
    node_id: str,
    top_k: int = 5
):

    if node_id not in runtime_graph.nodes:

        raise HTTPException(
            status_code=404,
            detail="Node not found"
        )

    ingress = io_gateway.ingress("api.runtime.predict", {"node_id": node_id, "top_k": top_k})

    predictions = (
        runtime_graph.predict_next_states(
            node_id=node_id,
            top_k=top_k
        )
    )

    results = []

    for similarity, node in predictions:

        results.append({

            "similarity":
                similarity,

            "node_id":
                node.node_id,

            "state_hash72":
                node.state_hash72,

            "receipt_hash72":
                node.receipt_hash72,

            "step":
                node.step
        })

    egress = io_gateway.egress("api.runtime.predict", {"node_id": node_id, "prediction_count": len(results)})
    return _contract_response(
        f"/api/runtime/predict/{node_id}",
        "GET",
        {
            "schema": "HHS_PREDICT_STATES_RESPONSE_V1",
            "node_id": node_id,
            "top_k": top_k,
            "predictions": results,
            "io": {"ingress": ingress, "egress": egress},
        },
    )

# ============================================================================
# SANDBOX ROUTES
# ============================================================================

@router.post("/sandbox/create")
async def create_sandbox(
    request: SandboxCreateRequest
):

    sandbox = runtime_controller.create_sandbox(
        metadata=request.metadata
    )

    return _contract_response(
        "/api/runtime/sandbox/create",
        "POST",
        {
            "schema": "HHS_SANDBOX_CREATE_RESPONSE_V1",
            "sandbox_id": sandbox.sandbox_id,
            "created_at": sandbox.created_at,
        },
    )

# ----------------------------------------------------------------------------

@router.post("/sandbox/{sandbox_id}/step")
async def sandbox_step(
    sandbox_id: str
):

    if sandbox_id not in runtime_controller.sandboxes:

        raise HTTPException(
            status_code=404,
            detail="Sandbox not found"
        )

    result = runtime_controller.sandbox_step(
        sandbox_id
    )

    payload = {"schema": "HHS_SANDBOX_STEP_RESPONSE_V1", "sandbox_id": sandbox_id}
    payload.update(result)
    return _contract_response(
        f"/api/runtime/sandbox/{sandbox_id}/step",
        "POST",
        payload,
    )

# ============================================================================
# VECTOR ROUTES
# ============================================================================

@router.get("/vector/latest")
async def latest_vector_record():

    ingress = io_gateway.ingress("api.runtime.vector.latest", {"method": "GET"})
    record = runtime_controller.export_vector_record()
    egress = io_gateway.egress("api.runtime.vector.latest", {"record_hash72": record.get("hash72") or record.get("receipt_hash72") or ""})
    return _contract_response("/api/runtime/vector/latest", "GET", {"schema": "HHS_GUARDED_VECTOR_LATEST_RESPONSE_V1", "vector": record, "io": {"ingress": ingress, "egress": egress}})

# ============================================================================
# MULTIMODAL PACKET
# ============================================================================

@router.get("/packet/latest")
async def latest_multimodal_packet():

    ingress = io_gateway.ingress("api.runtime.packet.latest", {"method": "GET"})
    packet = runtime_controller.export_multimodal_packet()
    egress = io_gateway.egress("api.runtime.packet.latest", {"state_hash72": packet.get("state_hash72") or packet.get("runtime", {}).get("state_hash72") or ""})
    return _contract_response("/api/runtime/packet/latest", "GET", {"schema": "HHS_GUARDED_PACKET_LATEST_RESPONSE_V1", "packet": packet, "io": {"ingress": ingress, "egress": egress}})

# ============================================================================
# WEBSOCKET STREAM
# ============================================================================

@router.websocket("/ws/runtime")
async def websocket_runtime_stream(
    websocket: WebSocket
):

    await websocket.accept()

    runtime_clients.append(websocket)

    try:

        while True:

            packet = (
                runtime_controller
                .export_multimodal_packet()
            )

            await websocket.send_text(
                json.dumps(_contract_packet("EGRESS", "api.runtime.ws.runtime", packet))
            )

            await asyncio.sleep(0.05)

    except WebSocketDisconnect:

        if websocket in runtime_clients:
            runtime_clients.remove(websocket)


# ============================================================================
# PASS 054 — CANONICAL AUTHORITY GRAPH / ROLE-BOUND ORCHESTRATION
# ============================================================================

@router.get("/authority/status")
def authority_status():
    return _contract_response("/api/runtime/authority/status", "GET", run_role_bound_orchestration())

@router.get("/authority/graph")
def authority_graph():
    run = run_role_bound_orchestration()
    return _contract_response("/api/runtime/authority/graph", "GET", run["authority_graph"])

@router.get("/authority/roles")
def authority_roles():
    return _contract_response("/api/runtime/authority/roles", "GET", {"roles": [build_role_contract()]})

@router.get("/authority/components")
def authority_components():
    return _contract_response("/api/runtime/authority/components", "GET", {"components": [build_competency_record()]})

@router.get("/authority/tasks")
def authority_tasks():
    run = run_role_bound_orchestration()
    return _contract_response("/api/runtime/authority/tasks", "GET", {"tasks": [run["task_assignment"]]})

@router.post("/authority/task/assign")
def authority_task_assign(payload: Dict[str, Any]):
    role = build_role_contract(role_id=payload.get("role_id", "role:implementation-agent"), component_id=payload.get("component_id", "agent:development"))
    task = build_task_assignment(payload.get("source_root_hash72", ""), payload.get("specification_root_hash72", ""), role, task_id=payload.get("task_id", "task:runtime-assignment"), allowed=payload.get("allowed_transformations"))
    return _contract_response("/api/runtime/authority/task/assign", "POST", task)

@router.post("/authority/handoff")
def authority_handoff(payload: Dict[str, Any]):
    handoff = build_handoff(payload["task_assignment"], payload.get("return_evidence", {}), payload.get("semantic_fields_to_preserve"))
    return _contract_response("/api/runtime/authority/handoff", "POST", {"handoff": handoff, "validation": validate_handoff(handoff)})

@router.post("/authority/derivation/validate")
def authority_derivation_validate(payload: Dict[str, Any]):
    decision = validate_derivation_equivalence(payload.get("candidate_output"), payload.get("reference_output"), candidate_source_root=payload.get("candidate_source_root", ""), reference_source_root=payload.get("reference_source_root", ""), candidate_path=payload.get("candidate_path", []), reference_path=payload.get("reference_path", []), candidate_authority_path=payload.get("candidate_authority_path", []), reference_authority_path=payload.get("reference_authority_path", []))
    return _contract_response("/api/runtime/authority/derivation/validate", "POST", decision)

@router.post("/authority/revalidate")
def authority_revalidate(payload: Dict[str, Any]):
    decision = independently_revalidate(payload.get("role_decision", {}), payload.get("handoff_decision", {}), payload.get("derivation_decision", {}))
    return _contract_response("/api/runtime/authority/revalidate", "POST", decision)

@router.post("/authority/response/admit")
def authority_response_admit(payload: Dict[str, Any]):
    decision = admit_response_candidate(payload.get("candidate", {}), bool(payload.get("canonical_invariant_conflict")), bool(payload.get("presentation_mutates_meaning")))
    return _contract_response("/api/runtime/authority/response/admit", "POST", decision)



@router.get("/authority/leases/status")
def authority_lease_status():
    run = run_authority_enforced_dispatch()
    return _contract_response("/api/runtime/authority/leases/status", "GET", {"lease": run["active_lease"], "dispatch": run["dispatch_decision"], "receipt": run["execution_receipt"]})

@router.post("/authority/lease/issue")
def authority_lease_issue(payload: Dict[str, Any]):
    lease = issue_capability_lease(task=payload["task"], role_contract=payload["role_contract"], authority_graph_root_hash72=payload["authority_graph_root_hash72"], capability_ids=payload.get("capability_ids", []), source_scope=payload.get("source_scope", []), allowed_operations=payload.get("allowed_operations", []), valid_from_sequence=int(payload.get("valid_from_sequence", 0)), expires_at_sequence=int(payload.get("expires_at_sequence", 0)), delegable=bool(payload.get("delegable", False)))
    return _contract_response("/api/runtime/authority/lease/issue", "POST", lease)

@router.post("/authority/dispatch/validate")
def authority_dispatch_validate(payload: Dict[str, Any]):
    decision = validate_dispatch(role_decision=payload.get("role_decision", {}), task=payload.get("task", {}), lease=payload.get("lease"), capability_id=payload.get("capability_id", ""), operation=payload.get("operation", ""), source_object_id=payload.get("source_object_id", ""), sequence=int(payload.get("sequence", 0)), delegate_component_id=payload.get("delegate_component_id"))
    return _contract_response("/api/runtime/authority/dispatch/validate", "POST", decision)

@router.post("/authority/lease/checkpoint")
def authority_lease_checkpoint(payload: Dict[str, Any]):
    decision = validate_execution_checkpoint(lease=payload["lease"], task=payload["task"], sequence=int(payload.get("sequence", 0)), checkpoint_id=payload.get("checkpoint_id", "checkpoint:api"))
    return _contract_response("/api/runtime/authority/lease/checkpoint", "POST", decision)

@router.post("/authority/lease/revoke")
def authority_lease_revoke(payload: Dict[str, Any]):
    transition = transition_lease(payload["lease"], "REVOKED", int(payload.get("sequence", 0)), payload.get("reason", "EXPLICIT_REVOCATION"))
    return _contract_response("/api/runtime/authority/lease/revoke", "POST", {"transition": transition, "lease": lease_with_state(payload["lease"], transition)})


@router.get("/authority/federation/status")
def authority_federation_status():
    run = run_distributed_authority_federation()
    return _contract_response("/api/runtime/authority/federation/status", "GET", run)

@router.post("/authority/federation/contract")
def authority_federation_contract(payload: Dict[str, Any]):
    return _contract_response("/api/runtime/authority/federation/contract", "POST", build_federation_contract())

@router.post("/authority/federation/delegate")
def authority_federation_delegate(payload: Dict[str, Any]):
    sublease = issue_sublease(payload["parent_lease"], payload["federation_contract"], payload["remote_identity"], capabilities=payload.get("capability_ids", []), sources=payload.get("source_scope", []), operations=payload.get("allowed_operations", []), start=int(payload.get("valid_from_sequence", 0)), end=int(payload.get("expires_at_sequence", 0)), depth=int(payload.get("delegation_depth", 1)), parent_chain_ids=payload.get("parent_chain_ids", []))
    return _contract_response("/api/runtime/authority/federation/delegate", "POST", sublease)

@router.post("/authority/federation/dispatch")
def authority_federation_dispatch(payload: Dict[str, Any]):
    decision = validate_remote_dispatch(payload["parent_lease"], payload["sublease"], payload["delegation_chain"], sequence=int(payload.get("sequence", 0)))
    return _contract_response("/api/runtime/authority/federation/dispatch", "POST", decision)

@router.post("/authority/federation/ingress")
def authority_federation_ingress(payload: Dict[str, Any]):
    decision = federated_ingress(payload["remote_receipt"], payload["federation_contract"], bool(payload.get("local_revalidation_ok")))
    return _contract_response("/api/runtime/authority/federation/ingress", "POST", decision)

@router.post("/authority/federation/revoke")
def authority_federation_revoke(payload: Dict[str, Any]):
    decision = propagate_revocation(payload["parent_lease"], payload.get("subleases", []), int(payload.get("sequence", 0)))
    return _contract_response("/api/runtime/authority/federation/revoke", "POST", decision)


@router.get("/authority/federation/recovery/status")
def authority_federation_recovery_status():
    return _contract_response("/api/runtime/authority/federation/recovery/status", "GET", run_partition_tolerant_federated_recovery())

@router.post("/authority/federation/partition/evidence")
def authority_federation_partition_evidence(payload: Dict[str, Any]):
    decision = build_partition_evidence(payload["federation_run"], observed_sequence=int(payload["observed_sequence"]), last_ack_sequence=int(payload["last_acknowledged_sequence"]))
    return _contract_response("/api/runtime/authority/federation/partition/evidence", "POST", decision)

@router.post("/authority/federation/revocation/consensus")
def authority_federation_revocation_consensus(payload: Dict[str, Any]):
    decision = resolve_revocation_consensus(payload.get("votes", []), quorum=int(payload.get("quorum", 1)))
    return _contract_response("/api/runtime/authority/federation/revocation/consensus", "POST", decision)

@router.post("/authority/federation/stale/quarantine")
def authority_federation_stale_quarantine(payload: Dict[str, Any]):
    decision = quarantine_stale_sublease(payload["sublease"], payload["partition_evidence"], payload["revocation_consensus"])
    return _contract_response("/api/runtime/authority/federation/stale/quarantine", "POST", decision)

@router.post("/authority/federation/reconcile")
def authority_federation_reconcile(payload: Dict[str, Any]):
    decision = reconcile_partition(payload["federation_run"], payload["partition_evidence"], payload["revocation_consensus"], payload["quarantine"])
    return _contract_response("/api/runtime/authority/federation/reconcile", "POST", decision)

@router.post("/authority/federation/recover")
def authority_federation_recover(payload: Dict[str, Any]):
    decision = recover_federation(payload["reconciliation_receipt"], local_revalidation_ok=bool(payload.get("local_revalidation_ok")))
    return _contract_response("/api/runtime/authority/federation/recover", "POST", decision)

@router.get("/authority/federation/reconciliation/status")
def authority_federation_reconciliation_status():
    return _contract_response("/api/runtime/authority/federation/reconciliation/status", "GET", run_canonical_federated_state_reconciliation())

@router.post("/authority/federation/reconciliation/conflicts")
def authority_federation_reconciliation_conflicts(payload: Dict[str, Any]):
    decision = classify_state_conflicts(payload["local_snapshot"], payload["remote_snapshot"])
    return _contract_response("/api/runtime/authority/federation/reconciliation/conflicts", "POST", decision)

@router.post("/authority/federation/reconciliation/merge")
def authority_federation_reconciliation_merge(payload: Dict[str, Any]):
    decision = merge_federated_states(payload["local_snapshot"], payload["remote_snapshot"], payload["conflict_set"], payload["merge_policy"], payload.get("resolutions", {}))
    return _contract_response("/api/runtime/authority/federation/reconciliation/merge", "POST", decision)

@router.post("/authority/federation/reconciliation/validate")
def authority_federation_reconciliation_validate(payload: Dict[str, Any]):
    decision = validate_canonical_merge(payload["merge_candidate"], local_revalidation_ok=bool(payload.get("local_revalidation_ok")), explicit_conflict_acceptance=bool(payload.get("explicit_conflict_acceptance", False)))
    return _contract_response("/api/runtime/authority/federation/reconciliation/validate", "POST", decision)

@router.get("/authority/federation/transaction/status")
def authority_federation_transaction_status():
    return _contract_response("/api/runtime/authority/federation/transaction/status", "GET", run_canonical_federated_transaction_commit())

@router.post("/authority/federation/transaction/prepare")
def authority_federation_transaction_prepare(payload: Dict[str, Any]):
    decision = build_prepare_record(payload["transaction_contract"], payload["participant_id"], payload["authority_root_hash72"], payload["source_root_hash72"], payload.get("effect", {}), prepared=bool(payload.get("prepared", True)))
    return _contract_response("/api/runtime/authority/federation/transaction/prepare", "POST", decision)

@router.post("/authority/federation/transaction/commit")
def authority_federation_transaction_commit(payload: Dict[str, Any]):
    decision = decide_commit(payload["transaction_contract"], payload.get("prepare_records", []), commit_epoch=int(payload["commit_epoch"]), decision_witnessed=bool(payload.get("decision_witnessed", True)))
    return _contract_response("/api/runtime/authority/federation/transaction/commit", "POST", decision)

@router.post("/authority/federation/transaction/finalize")
def authority_federation_transaction_finalize(payload: Dict[str, Any]):
    decision = finalize_transaction(payload["commit_decision"], payload.get("participant_receipts", []), local_revalidation_ok=bool(payload.get("local_revalidation_ok")))
    return _contract_response("/api/runtime/authority/federation/transaction/finalize", "POST", decision)

@router.post("/authority/federation/transaction/rollback")
def authority_federation_transaction_rollback(payload: Dict[str, Any]):
    decision = decide_rollback(payload["transaction_contract"], payload.get("participant_receipts", []), payload.get("compensation_records", []), local_revalidation_ok=bool(payload.get("local_revalidation_ok")))
    return _contract_response("/api/runtime/authority/federation/transaction/rollback", "POST", decision)

# ============================================================================
# EVENT HOOKS
# ============================================================================

def _runtime_step_hook(payload):

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    runtime_graph.ingest_runtime_state(packet)

# ----------------------------------------------------------------------------

runtime_controller.add_listener(
    "runtime_step",
    _runtime_step_hook
)

# ============================================================================
# SELF TEST
# ============================================================================

def route_self_test():

    runtime_controller.run_steps(3)

    packet = (
        runtime_controller.export_multimodal_packet()
    )

    runtime_graph.ingest_runtime_state(packet)

    print()

    print("RUNTIME")

    print(runtime_controller.latest_runtime_state())

    print()

    print("GRAPH")

    print(runtime_graph.export_graph_summary())

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    route_self_test()

@router.get("/authority/federation/transaction/recovery/status")
def authority_federation_transaction_recovery_status():
    return _contract_response("/api/runtime/authority/federation/transaction/recovery/status", "GET", run_federated_transaction_recovery())

@router.post("/authority/federation/transaction/recovery/replay")
def authority_federation_transaction_recovery_replay():
    return _contract_response("/api/runtime/authority/federation/transaction/recovery/replay", "POST", run_federated_transaction_recovery())

@router.post("/authority/federation/transaction/recovery/admit")
def authority_federation_transaction_recovery_admit():
    return _contract_response("/api/runtime/authority/federation/transaction/recovery/admit", "POST", run_federated_transaction_recovery())


@router.get("/authority/rejection/status")
def authority_rejection_status():
    return _contract_response("/api/runtime/authority/rejection/status", "GET", run_bounded_rejection_authority())

@router.post("/authority/rejection/decide")
def authority_rejection_decide():
    return _contract_response("/api/runtime/authority/rejection/decide", "POST", run_bounded_rejection_authority())

@router.post("/authority/rejection/propagate")
def authority_rejection_propagate():
    return _contract_response("/api/runtime/authority/rejection/propagate", "POST", run_bounded_rejection_authority())

@router.post("/authority/rejection/revalidate")
def authority_rejection_revalidate():
    return _contract_response("/api/runtime/authority/rejection/revalidate", "POST", run_bounded_rejection_authority())

@router.post("/authority/rejection/release")
def authority_rejection_release():
    return _contract_response("/api/runtime/authority/rejection/release", "POST", run_bounded_rejection_authority())


@router.get("/authority/topology/reciprocal/status")
def authority_topology_reciprocal_status():
    return _contract_response("/api/runtime/authority/topology/reciprocal/status", "GET", run_global_reciprocal_contract_topology())

@router.post("/authority/topology/reciprocal/expand")
def authority_topology_reciprocal_expand():
    return _contract_response("/api/runtime/authority/topology/reciprocal/expand", "POST", run_global_reciprocal_contract_topology())

@router.post("/authority/topology/reciprocal/contract")
def authority_topology_reciprocal_contract():
    return _contract_response("/api/runtime/authority/topology/reciprocal/contract", "POST", run_global_reciprocal_contract_topology())

@router.post("/authority/topology/reciprocal/validate")
def authority_topology_reciprocal_validate():
    return _contract_response("/api/runtime/authority/topology/reciprocal/validate", "POST", run_global_reciprocal_contract_topology())


@router.get("/manifold/execution/status")
def manifold_execution_status():
    return _contract_response("/api/runtime/manifold/execution/status", "GET", run_deterministic_manifold_execution())

@router.post("/manifold/execution/propagate")
def manifold_execution_propagate():
    return _contract_response("/api/runtime/manifold/execution/propagate", "POST", run_deterministic_manifold_execution())

@router.post("/manifold/execution/cancel")
def manifold_execution_cancel():
    return _contract_response("/api/runtime/manifold/execution/cancel", "POST", run_deterministic_manifold_execution())

@router.post("/manifold/execution/close")
def manifold_execution_close():
    return _contract_response("/api/runtime/manifold/execution/close", "POST", run_deterministic_manifold_execution())

@router.post("/manifold/execution/revalidate")
def manifold_execution_revalidate():
    return _contract_response("/api/runtime/manifold/execution/revalidate", "POST", run_deterministic_manifold_execution())

from hhs_backend.runtime.hhs_alignment_agent_v1 import run_alignment_agent

@router.get("/alignment/status")
def alignment_status():
    return _contract_response("/api/runtime/alignment/status", "GET", run_alignment_agent())

@router.post("/alignment/admit")
def alignment_admit():
    return _contract_response("/api/runtime/alignment/admit", "POST", run_alignment_agent())


# Pass 065 — Local closed parallel branch-tree entanglement and A=B phase reintegration
from hhs_backend.runtime.hhs_local_parallel_branch_tree_v1 import run_local_parallel_branch_tree

@router.get("/branch-tree/status")
def runtime_branch_tree_status():
    return _contract_response("/api/runtime/branch-tree/status", "GET", run_local_parallel_branch_tree())

@router.post("/branch-tree/resolve")
def runtime_branch_tree_resolve():
    return _contract_response("/api/runtime/branch-tree/resolve", "POST", run_local_parallel_branch_tree())

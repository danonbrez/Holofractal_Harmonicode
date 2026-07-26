"""Guarded HTTP transport for the boot-reachable HHS cognition stack."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from hhs_backend.runtime.live_cognition_runtime_v1 import live_cognition_runtime
from hhs_runtime.hhs_runtime_contract_v1 import envelope_api_response

router = APIRouter(tags=["runtime", "cognition"])
_REGISTERED = False


class GoalCreateRequest(BaseModel):
    objective: str
    target_hash72: Optional[str] = None
    stability_bias: float = 1.0
    entropy_penalty: float = 0.5
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GoalAdaptRequest(BaseModel):
    horizon: int = Field(default=10, ge=1, le=256)


class CognitionTaskCreateRequest(BaseModel):
    objective: str
    goal_id: Optional[str] = None
    target_hash72: Optional[str] = None
    replay_context: str = "live_runtime"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SemanticIngestRequest(BaseModel):
    memory_type: str = "symbolic"
    semantic_text: str
    hash72: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PredictionRequest(BaseModel):
    horizon: int = Field(default=10, ge=1, le=256)


class ConsensusProposalRequest(BaseModel):
    proposal_type: str
    target_hash72: str
    quorum_required: int = Field(default=3, ge=1, le=64)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConsensusVoteRequest(BaseModel):
    proposal_id: str
    node_id: str
    approved: bool
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ToolchainExecuteRequest(BaseModel):
    originating_task: str
    graph_seed: str


class ResearchExecuteRequest(BaseModel):
    objective: str
    originating_goal: str = "api.runtime.research"
    exploration_horizon: int = Field(default=10, ge=1, le=256)


class MultinodeGoalRequest(BaseModel):
    originating_node: str
    objective: str
    target_hash72: str
    consensus_weight: float = Field(default=1.0, ge=0.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _io_gateway():
    from hhs_backend.api.runtime_routes import io_gateway
    return io_gateway


def _guarded(
    route: str,
    method: str,
    request_payload: Dict[str, Any],
    operation: Callable[[], Dict[str, Any]],
) -> Dict[str, Any]:
    gateway = _io_gateway()
    ingress = gateway.ingress(route, {"method": method, "payload": request_payload})
    try:
        payload = operation()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    egress = gateway.egress(route, payload)
    return envelope_api_response(
        route,
        method,
        payload,
        io={"ingress": ingress, "egress": egress},
    )


@router.get("/cognition/status")
def cognition_status() -> Dict[str, Any]:
    route = "/api/runtime/cognition/status"
    return _guarded(route, "GET", {}, live_cognition_runtime.status)


@router.post("/cognition/task")
def cognition_task_create(request: CognitionTaskCreateRequest) -> Dict[str, Any]:
    route = "/api/runtime/cognition/task"
    data = request.model_dump()
    return _guarded(route, "POST", data, lambda: live_cognition_runtime.create_task(**data))


@router.get("/cognition/task/{task_id}")
def cognition_task_status(task_id: str) -> Dict[str, Any]:
    route = f"/api/runtime/cognition/task/{task_id}"
    return _guarded(
        route,
        "GET",
        {"task_id": task_id},
        lambda: live_cognition_runtime.task_status(task_id),
    )


@router.post("/cognition/task/{task_id}/execute")
def cognition_task_execute(task_id: str) -> Dict[str, Any]:
    route = f"/api/runtime/cognition/task/{task_id}/execute"
    return _guarded(
        route,
        "POST",
        {"task_id": task_id},
        lambda: live_cognition_runtime.execute_task(task_id),
    )


@router.get("/goals")
def goals_list() -> Dict[str, Any]:
    route = "/api/runtime/goals"
    return _guarded(route, "GET", {}, live_cognition_runtime.goals)


@router.post("/goals")
def goals_create(request: GoalCreateRequest) -> Dict[str, Any]:
    route = "/api/runtime/goals"
    data = request.model_dump()
    return _guarded(route, "POST", data, lambda: live_cognition_runtime.create_goal(**data))


@router.get("/goals/metrics")
def goals_metrics() -> Dict[str, Any]:
    route = "/api/runtime/goals/metrics"
    return _guarded(route, "GET", {}, lambda: live_cognition_runtime.goals()["metrics"])


@router.get("/goals/{goal_id}")
def goal_status(goal_id: str) -> Dict[str, Any]:
    route = f"/api/runtime/goals/{goal_id}"
    return _guarded(
        route,
        "GET",
        {"goal_id": goal_id},
        lambda: live_cognition_runtime.goal_status(goal_id),
    )


@router.post("/goals/{goal_id}/adapt")
def goal_adapt(goal_id: str, request: GoalAdaptRequest) -> Dict[str, Any]:
    route = f"/api/runtime/goals/{goal_id}/adapt"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        {"goal_id": goal_id, **data},
        lambda: live_cognition_runtime.adapt_goal(goal_id, **data),
    )


@router.get("/semantic/search")
def semantic_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
) -> Dict[str, Any]:
    route = "/api/runtime/semantic/search"
    return _guarded(
        route,
        "GET",
        {"q": q, "limit": limit},
        lambda: live_cognition_runtime.semantic_search(q, limit),
    )


@router.post("/semantic/ingest")
def semantic_ingest(request: SemanticIngestRequest) -> Dict[str, Any]:
    route = "/api/runtime/semantic/ingest"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.semantic_ingest(**data),
    )


@router.get("/semantic/graph")
def semantic_graph() -> Dict[str, Any]:
    route = "/api/runtime/semantic/graph"
    return _guarded(route, "GET", {}, live_cognition_runtime.semantic_graph)


@router.get("/prediction/status")
def prediction_status() -> Dict[str, Any]:
    route = "/api/runtime/prediction/status"
    return _guarded(
        route,
        "GET",
        {},
        lambda: live_cognition_runtime.status()["layers"]["prediction"],
    )


@router.post("/prediction/generate")
def prediction_generate(request: PredictionRequest) -> Dict[str, Any]:
    route = "/api/runtime/prediction/generate"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.generate_prediction(**data),
    )


@router.get("/replay/status")
def replay_status() -> Dict[str, Any]:
    route = "/api/runtime/replay/status"
    return _guarded(
        route,
        "GET",
        {},
        lambda: live_cognition_runtime.status()["layers"]["replay"],
    )


@router.get("/consensus/status")
def consensus_status() -> Dict[str, Any]:
    route = "/api/runtime/consensus/status"
    return _guarded(route, "GET", {}, live_cognition_runtime.consensus_status)


@router.post("/consensus/propose")
def consensus_propose(request: ConsensusProposalRequest) -> Dict[str, Any]:
    route = "/api/runtime/consensus/propose"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.create_consensus_proposal(**data),
    )


@router.post("/consensus/vote")
def consensus_vote(request: ConsensusVoteRequest) -> Dict[str, Any]:
    route = "/api/runtime/consensus/vote"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.submit_consensus_vote(**data),
    )


@router.post("/consensus/collect/{proposal_id}")
def consensus_collect(proposal_id: str) -> Dict[str, Any]:
    route = f"/api/runtime/consensus/collect/{proposal_id}"
    return _guarded(
        route,
        "POST",
        {"proposal_id": proposal_id},
        lambda: live_cognition_runtime.collect_consensus(proposal_id),
    )


@router.get("/toolchain/status")
def toolchain_status() -> Dict[str, Any]:
    route = "/api/runtime/toolchain/status"
    return _guarded(route, "GET", {}, live_cognition_runtime.toolchain_status)


@router.get("/toolchain/{toolchain_id}")
def toolchain_get(toolchain_id: str) -> Dict[str, Any]:
    route = f"/api/runtime/toolchain/{toolchain_id}"
    return _guarded(
        route,
        "GET",
        {"toolchain_id": toolchain_id},
        lambda: live_cognition_runtime.toolchain_status(toolchain_id),
    )


@router.post("/toolchain/execute")
def toolchain_execute(request: ToolchainExecuteRequest) -> Dict[str, Any]:
    route = "/api/runtime/toolchain/execute"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.execute_toolchain(**data),
    )


@router.get("/research/status")
def research_status() -> Dict[str, Any]:
    route = "/api/runtime/research/status"
    return _guarded(route, "GET", {}, live_cognition_runtime.research_status)


@router.get("/research/{task_id}")
def research_get(task_id: str) -> Dict[str, Any]:
    route = f"/api/runtime/research/{task_id}"
    return _guarded(
        route,
        "GET",
        {"task_id": task_id},
        lambda: live_cognition_runtime.research_status(task_id),
    )


@router.post("/research/execute")
def research_execute(request: ResearchExecuteRequest) -> Dict[str, Any]:
    route = "/api/runtime/research/execute"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.execute_research(**data),
    )


@router.get("/multinode-goals/status")
def multinode_goals_status() -> Dict[str, Any]:
    route = "/api/runtime/multinode-goals/status"
    return _guarded(
        route,
        "GET",
        {},
        live_cognition_runtime.multinode_goal_status,
    )


@router.post("/multinode-goals")
def multinode_goals_register(request: MultinodeGoalRequest) -> Dict[str, Any]:
    route = "/api/runtime/multinode-goals"
    data = request.model_dump()
    return _guarded(
        route,
        "POST",
        data,
        lambda: live_cognition_runtime.register_multinode_goal(**data),
    )


@router.post("/multinode-goals/synchronize")
def multinode_goals_synchronize() -> Dict[str, Any]:
    route = "/api/runtime/multinode-goals/synchronize"
    return _guarded(
        route,
        "POST",
        {},
        live_cognition_runtime.synchronize_multinode_goals,
    )


def register_cognition_routes() -> bool:
    """Attach cognition routes to the canonical runtime router exactly once."""

    global _REGISTERED
    if _REGISTERED:
        return False
    from hhs_backend.api.runtime_routes import router as runtime_router

    existing = {getattr(route, "path", "") for route in runtime_router.routes}
    if "/api/runtime/cognition/status" not in existing:
        runtime_router.include_router(router)
    _REGISTERED = True
    return True

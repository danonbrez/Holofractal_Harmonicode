"""Status and evidence routes for the Pass 209 production LLM hierarchy."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/api/runtime/llm-orchestrator",
    tags=["runtime", "assistant", "kimi-k3", "gemma4", "native-agi", "pass209"],
)


def _service() -> Any:
    from hhs_backend.runtime.hhs_pass209_production_assistant_v1 import (
        DEFAULT_PASS209_PRODUCTION_ASSISTANT,
    )

    return DEFAULT_PASS209_PRODUCTION_ASSISTANT


@router.get("/status")
def llm_orchestrator_status() -> Dict[str, Any]:
    return _service().status()


@router.get("/health")
async def llm_orchestrator_health() -> Dict[str, Any]:
    return await _service().health()


@router.get("/optimizer/status")
def native_agi_optimizer_status() -> Dict[str, Any]:
    return _service().optimizer.status()


@router.get("/optimizer/observations")
def native_agi_optimizer_observations(
    limit: int = Query(default=100, ge=1, le=1000),
) -> Dict[str, Any]:
    observations = _service().optimizer.observations(limit=limit)
    return {
        "schema": "HHS_PASS_209_NATIVE_AGI_OBSERVATION_LIST_V1",
        "ok": True,
        "count": len(observations),
        "observations": observations,
        "native_agi_is_user_facing_provider": False,
        "runtime_mutation_admitted": False,
    }


@router.get("/optimizer/proposals")
def native_agi_optimizer_proposals(
    limit: int = Query(default=100, ge=1, le=1000),
) -> Dict[str, Any]:
    proposals = _service().optimizer.proposals(limit=limit)
    return {
        "schema": "HHS_PASS_209_NATIVE_AGI_OPTIMIZATION_PROPOSAL_LIST_V1",
        "ok": True,
        "count": len(proposals),
        "proposals": proposals,
        "proposals_are_canonical": False,
        "separate_admission_required": True,
        "runtime_mutation_admitted": False,
    }

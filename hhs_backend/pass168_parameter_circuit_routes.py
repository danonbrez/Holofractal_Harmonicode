from __future__ import annotations

import threading
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass168.public_service import (
    Pass168ParameterCircuitError,
    Pass168ParameterCircuitService,
)

_DEFAULT_SERVICE: Pass168ParameterCircuitService | None = None
_DEFAULT_LOCK = threading.Lock()


class CandidateBody(BaseModel):
    updates: dict[str, Any] = Field(min_length=1)


def _service() -> Pass168ParameterCircuitService:
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        with _DEFAULT_LOCK:
            if _DEFAULT_SERVICE is None:
                _DEFAULT_SERVICE = Pass168ParameterCircuitService()
    return _DEFAULT_SERVICE


def _call(function: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        return function(*args, **kwargs)
    except Pass168ParameterCircuitError as exc:
        status = 404 if exc.code.endswith("_NOT_FOUND") else 409
        raise HTTPException(status_code=status, detail=exc.as_dict()) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "ok": False,
                "error": "PASS168_REQUEST_INVALID",
                "message": f"{type(exc).__name__}:{exc}",
                "floating_point_canonical_authority": False,
            },
        ) from exc


def build_pass168_parameter_circuit_router() -> APIRouter:
    router = APIRouter(tags=["pass168-parameter-circuit"])

    @router.get("/v1/parameter-circuit")
    def status() -> dict[str, Any]:
        return _call(_service().status)

    @router.get("/v1/parameter-circuit/source")
    def source() -> dict[str, Any]:
        return _call(_service().source)

    @router.get("/v1/parameter-circuit/map")
    def cell_map() -> dict[str, Any]:
        return _call(_service().cell_map)

    @router.get("/v1/parameter-circuit/threads")
    def threads() -> dict[str, Any]:
        return _call(_service().threads)

    @router.get("/v1/parameter-circuit/parameters")
    def parameters() -> dict[str, Any]:
        return _call(_service().parameters)

    @router.get("/v1/parameter-circuit/parameters/{parameter_id}")
    def parameter(parameter_id: str) -> dict[str, Any]:
        return _call(_service().get_parameter, parameter_id)

    @router.post("/v1/parameter-circuit/candidates")
    def candidate(body: CandidateBody) -> dict[str, Any]:
        return _call(_service().create_candidate, body.updates)

    @router.get("/v1/parameter-circuit/candidates/{candidate_id}")
    def get_candidate(candidate_id: str) -> dict[str, Any]:
        return _call(_service().get_candidate, candidate_id)

    @router.post("/v1/parameter-circuit/candidates/{candidate_id}/validate")
    def validate_candidate(candidate_id: str) -> dict[str, Any]:
        return _call(_service().validate_candidate, candidate_id)

    @router.post("/v1/parameter-circuit/candidates/{candidate_id}/commit")
    def commit_candidate(candidate_id: str) -> dict[str, Any]:
        return _call(_service().commit_candidate, candidate_id)

    @router.get("/v1/parameter-circuit/dependencies/{parameter_id}")
    def dependencies(parameter_id: str) -> dict[str, Any]:
        return _call(_service().dependencies, parameter_id)

    @router.get("/v1/parameter-circuit/matrices/upper")
    def upper() -> dict[str, Any]:
        return _call(_service().matrix, "upper")

    @router.get("/v1/parameter-circuit/matrices/lower")
    def lower() -> dict[str, Any]:
        return _call(_service().matrix, "lower")

    @router.get("/v1/parameter-circuit/comparators/{comparator_id}")
    def comparator(comparator_id: str) -> dict[str, Any]:
        return _call(_service().compare, comparator_id)

    @router.get("/v1/parameter-circuit/transitions/{transition_id}")
    def transition(transition_id: str) -> dict[str, Any]:
        return _call(_service().get_transition, transition_id)

    @router.post("/v1/parameter-circuit/transitions/{transition_id}/replay")
    def replay(transition_id: str) -> dict[str, Any]:
        return _call(_service().replay, transition_id)

    @router.post("/v1/parameter-circuit/transitions/{transition_id}/rollback")
    def rollback(transition_id: str) -> dict[str, Any]:
        return _call(_service().rollback, transition_id)

    @router.get("/v1/parameter-circuit/transitions/{transition_id}/receipt")
    def receipt(transition_id: str) -> dict[str, Any]:
        return _call(_service().receipt, transition_id)

    return router


__all__ = ["build_pass168_parameter_circuit_router"]

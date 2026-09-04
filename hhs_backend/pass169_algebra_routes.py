"""Pass169 algebra router for the one canonical public FastAPI gateway.

This module intentionally does not instantiate FastAPI or VM81 authority.
"""
from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass169.public_service import Pass169AlgebraService, Pass169PublicSurfaceError

HTTP_EQUIVALENTS = (
    "GET /v1/algebra",
    "POST /v1/algebra/sources",
    "GET /v1/algebra/sources/{source_id}",
    "GET /v1/algebra/sources/{source_id}/tokens",
    "GET /v1/algebra/sources/{source_id}/ast",
    "GET /v1/algebra/sources/{source_id}/constraints",
    "POST /v1/algebra/sources/{source_id}/typecheck",
    "POST /v1/algebra/sources/{source_id}/normalize",
    "POST /v1/algebra/sources/{source_id}/candidates",
    "GET /v1/algebra/candidates/{candidate_id}",
    "POST /v1/algebra/candidates/{candidate_id}/validate",
    "POST /v1/algebra/candidates/{candidate_id}/commit",
    "GET /v1/algebra/proofs/{proof_id}",
    "GET /v1/algebra/transitions/{transition_id}",
    "GET /v1/algebra/transitions/{transition_id}/receipt",
    "POST /v1/algebra/transitions/{transition_id}/replay",
    "POST /v1/algebra/transitions/{transition_id}/reverse",
)


class SourceBody(BaseModel):
    source: str = Field(min_length=1, max_length=1048576)


def build_pass169_algebra_router(authority_provider: Callable[[], Any]) -> APIRouter:
    router = APIRouter(tags=["pass169-algebra"])
    service = Pass169AlgebraService(authority_provider=authority_provider)

    def call(operation: str, **params: Any) -> dict[str, Any]:
        try:
            return service.dispatch(operation, **params)
        except Pass169PublicSurfaceError as exc:
            raise HTTPException(status_code=exc.http_status, detail=exc.to_dict()) from exc

    @router.get("/v1/algebra")
    def algebra_status() -> dict[str, Any]:
        return call("status")

    @router.post("/v1/algebra/sources")
    def algebra_sources_create(body: SourceBody) -> dict[str, Any]:
        return call("register-source", source=body.source)

    @router.get("/v1/algebra/sources/{source_id}")
    def algebra_source(source_id: str) -> dict[str, Any]:
        return call("source", source_id=source_id)

    @router.get("/v1/algebra/sources/{source_id}/tokens")
    def algebra_tokens(source_id: str) -> dict[str, Any]:
        return call("tokens", source_id=source_id)

    @router.get("/v1/algebra/sources/{source_id}/ast")
    def algebra_ast(source_id: str) -> dict[str, Any]:
        return call("ast", source_id=source_id)

    @router.get("/v1/algebra/sources/{source_id}/constraints")
    def algebra_constraints(source_id: str) -> dict[str, Any]:
        return call("constraints", source_id=source_id)

    @router.post("/v1/algebra/sources/{source_id}/typecheck")
    def algebra_typecheck(source_id: str) -> dict[str, Any]:
        return call("typecheck", source_id=source_id)

    @router.post("/v1/algebra/sources/{source_id}/normalize")
    def algebra_normalize(source_id: str) -> dict[str, Any]:
        return call("normalize", source_id=source_id)

    @router.post("/v1/algebra/sources/{source_id}/candidates")
    def algebra_candidate_create(source_id: str) -> dict[str, Any]:
        return call("evaluate-candidate", source_id=source_id)

    @router.get("/v1/algebra/candidates/{candidate_id}")
    def algebra_candidate(candidate_id: str) -> dict[str, Any]:
        return call("inspect", node=f"candidate:{candidate_id}")

    @router.post("/v1/algebra/candidates/{candidate_id}/validate")
    def algebra_candidate_validate(candidate_id: str) -> dict[str, Any]:
        return call("admit", candidate_id=candidate_id)

    @router.post("/v1/algebra/candidates/{candidate_id}/commit")
    def algebra_candidate_commit(candidate_id: str) -> dict[str, Any]:
        return call("commit", candidate_id=candidate_id)

    @router.get("/v1/algebra/proofs/{proof_id}")
    def algebra_proof(proof_id: str) -> dict[str, Any]:
        return call("export-proof", transition_id=proof_id)

    @router.get("/v1/algebra/transitions/{transition_id}")
    def algebra_transition(transition_id: str) -> dict[str, Any]:
        return call("inspect", node=f"transition:{transition_id}")

    @router.get("/v1/algebra/transitions/{transition_id}/receipt")
    def algebra_receipt(transition_id: str) -> dict[str, Any]:
        return call("receipt", transition_id=transition_id)

    @router.post("/v1/algebra/transitions/{transition_id}/replay")
    def algebra_replay(transition_id: str) -> dict[str, Any]:
        return call("replay", transition_id=transition_id)

    @router.post("/v1/algebra/transitions/{transition_id}/reverse")
    def algebra_reverse(transition_id: str) -> dict[str, Any]:
        return call("reverse", transition_id=transition_id)

    return router


__all__ = ["HTTP_EQUIVALENTS", "build_pass169_algebra_router"]

"""Pass 177 backend authority reconciliation for browser project/workflow candidates."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from hhs_runtime.pass177.runtime import (
    PASS177_WORKFLOW_AUTHORITY,
    Pass177AuthorityError,
)

router = APIRouter(
    prefix="/api/runtime/pass177-workflows",
    tags=["pass177", "workflow", "vm81", "templates"],
)


def _reject(error: Exception) -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS_177_ROUTE_RESULT_V1",
        "ok": False,
        "status": "REJECT_PASS177_WORKFLOW_REQUEST",
        "reason": str(error),
    }


@router.get("/status")
def status() -> Dict[str, Any]:
    return PASS177_WORKFLOW_AUTHORITY.status()


@router.post("/project/admit")
def admit_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "record": PASS177_WORKFLOW_AUTHORITY.admit_project(payload),
        }
    except (Pass177AuthorityError, ValueError) as error:
        return _reject(error)


@router.post("/project/{project_id}/checkpoint/admit")
def admit_checkpoint(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return {
            "ok": True,
            "record": PASS177_WORKFLOW_AUTHORITY.admit_workflow_checkpoint(
                project_id=project_id,
                run=payload,
            ),
        }
    except (Pass177AuthorityError, ValueError) as error:
        return _reject(error)

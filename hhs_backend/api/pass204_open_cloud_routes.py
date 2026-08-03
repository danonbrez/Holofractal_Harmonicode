"""Pass 204 safe open cloud computer public API."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import hhs_backend.api.pass203_mainframe_routes as inherited_mainframe_routes
from hhs_backend.api.runtime_routes import _contract_response, runtime_controller
from hhs_backend.runtime.hhs_pass203_hydrated_mainframe_v1 import (
    InvocationRejectedError,
    UnknownFunctionError,
)
from hhs_backend.runtime.hhs_pass204_open_cloud_mainframe import (
    CLASSIFICATION,
    CONTRACT,
    KERNEL_CONSTRAINT_MANIFEST,
    OPEN_CLOUD_PREFIX,
    PASS204_MAINFRAME,
    SANDBOX_POLICY,
)

router = APIRouter(
    prefix=OPEN_CLOUD_PREFIX,
    tags=["runtime", "mainframe", "open-cloud", "sandbox", "snapshot", "pass204"],
)

PASS204_MAINFRAME.configure_authority(lambda source: runtime_controller.authorized_tick(source=source))

# Upgrade the inherited Pass 203 endpoints in place. Their request handlers
# resolve these module globals at call time, so catalog, invoke, plans, replay,
# jobs, and the existing visual studio all use Pass 204 without a forked API.
inherited_mainframe_routes.PASS203_MAINFRAME = PASS204_MAINFRAME
inherited_mainframe_routes.CONTRACT = CONTRACT
inherited_mainframe_routes.CLASSIFICATION = CLASSIFICATION


class RecallRequest(BaseModel):
    recall_token: str = Field(min_length=1, max_length=1024)


def _raise(exc: Exception) -> None:
    if isinstance(exc, UnknownFunctionError):
        raise HTTPException(
            status_code=404,
            detail={
                "schema": "HHS_PASS_204_RESOURCE_NOT_FOUND_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "ok": False,
                "reason": str(exc),
                "retryable": False,
                "remediation": "Use an identifier or recall token returned by a successful Pass 204 invocation.",
            },
        ) from exc
    if isinstance(exc, InvocationRejectedError):
        raise HTTPException(
            status_code=422,
            detail={
                "schema": "HHS_PASS_204_INVALID_CALL_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "ok": False,
                "reason": str(exc),
                "retryable": False,
                "remediation": "Submit arguments matching the function descriptor. Valid declared-function calls return HTTP success.",
            },
        ) from exc
    raise HTTPException(
        status_code=503,
        detail={
            "schema": "HHS_PASS_204_CONTROL_PLANE_UNAVAILABLE_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "ok": False,
            "reason": f"{exc.__class__.__name__}: {exc}",
            "retryable": True,
            "remediation": "Retry after the control plane is available; sandbox work never receives persistent capability or kernel access.",
        },
    ) from exc


@router.get("/status")
def open_cloud_status() -> Dict[str, Any]:
    return _contract_response(f"{OPEN_CLOUD_PREFIX}/status", "GET", PASS204_MAINFRAME.status())


@router.get("/policy")
def open_cloud_policy() -> Dict[str, Any]:
    result = {
        "schema": "HHS_PASS_204_OPEN_CLOUD_POLICY_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "ok": True,
        "policy": dict(SANDBOX_POLICY),
        "kernel_constraint_manifest": dict(KERNEL_CONSTRAINT_MANIFEST),
        "policy_is_read_only": True,
        "policy_mutation_endpoint": None,
        "capabilities_restored_on_recall": False,
    }
    return _contract_response(f"{OPEN_CLOUD_PREFIX}/policy", "GET", result)


@router.get("/closure")
def open_cloud_closure() -> Dict[str, Any]:
    status = PASS204_MAINFRAME.status()
    result = {
        "schema": "HHS_PASS_204_EXECUTABLE_DECLARATION_CLOSURE_V1",
        "contract": CONTRACT,
        "classification": CLASSIFICATION,
        "ok": True,
        "closed": status["closed"],
        "catalog_count": status["catalog_count"],
        "callable_count": status["callable_count"],
        "hydrated_count": status["hydrated_count"],
        "binding_gap_count": status["unbound_internal_count"],
        "all_declarations_executable": status["all_declarations_executable"],
        "valid_call_outcomes": ["COMPLETED", "ACCEPTED", "CONTINUATION_REQUIRED"],
        "valid_call_http_error": False,
        "capabilities_restored_on_recall": False,
    }
    return _contract_response(f"{OPEN_CLOUD_PREFIX}/closure", "GET", result)


@router.get("/sessions/{session_id:path}")
def open_cloud_session(session_id: str) -> Dict[str, Any]:
    try:
        result = PASS204_MAINFRAME.session(session_id)
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{OPEN_CLOUD_PREFIX}/sessions/{{session_id}}", "GET", result)


@router.post("/recall")
def open_cloud_recall(body: RecallRequest) -> Dict[str, Any]:
    try:
        result = PASS204_MAINFRAME.recall(body.recall_token)
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{OPEN_CLOUD_PREFIX}/recall", "POST", result)


@router.get("/jobs/{job_id:path}")
def open_cloud_job(job_id: str) -> Dict[str, Any]:
    try:
        result = PASS204_MAINFRAME.job(job_id)
    except Exception as exc:
        _raise(exc)
    return _contract_response(f"{OPEN_CLOUD_PREFIX}/jobs/{{job_id}}", "GET", result)

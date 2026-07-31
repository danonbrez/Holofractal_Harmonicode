"""HTTP projection for the HHS integrated application factory."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Response

from hhs_backend.runtime.hhs_application_factory_v1 import (
    APPLICATION_FACTORY,
    application_factory_self_test,
)

router = APIRouter(prefix="/api/runtime/application-factory", tags=["application-factory"])


@router.get("/status")
def application_factory_status() -> Dict[str, Any]:
    status = APPLICATION_FACTORY.status()
    status["self_test_projection"] = application_factory_self_test()
    return status


@router.get("/modules")
def application_factory_modules() -> Dict[str, Any]:
    return APPLICATION_FACTORY.module_library()


@router.get("/workflows")
def application_factory_workflows() -> Dict[str, Any]:
    return APPLICATION_FACTORY.workflow_library()


@router.post("/projects")
def application_factory_create_project(payload: Dict[str, Any]) -> Dict[str, Any]:
    return APPLICATION_FACTORY.create_project(
        name=str(payload.get("name") or "HHS Application"),
        workflow_id=str(payload.get("workflow_id") or "web_application"),
        extra_modules=payload.get("extra_modules") or [],
        initial_files=payload.get("initial_files") or {},
    )


@router.get("/projects/{project_id}")
def application_factory_get_project(project_id: str) -> Dict[str, Any]:
    project = APPLICATION_FACTORY.get_project(project_id)
    if project is None:
        return {
            "schema": "HHS_APPLICATION_FACTORY_PROJECT_ROUTE_RESULT_V1",
            "ok": False,
            "status": "REJECT_APPLICATION_PROJECT_UNKNOWN",
            "project_id": project_id,
        }
    return {
        "schema": "HHS_APPLICATION_FACTORY_PROJECT_ROUTE_RESULT_V1",
        "ok": True,
        "status": "APPLICATION_PROJECT_READY",
        "project": project,
    }


@router.put("/projects/{project_id}/files")
def application_factory_upsert_file(project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return APPLICATION_FACTORY.upsert_file(
        project_id,
        str(payload.get("path") or ""),
        payload.get("content", ""),
    )


@router.post("/projects/{project_id}/plan")
def application_factory_plan(
    project_id: str, payload: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    body = payload or {}
    return APPLICATION_FACTORY.plan_changes(project_id, body.get("changed_paths"))


@router.post("/projects/{project_id}/lifecycle")
def application_factory_lifecycle(
    project_id: str, payload: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    body = payload or {}
    return APPLICATION_FACTORY.run_lifecycle(
        project_id,
        body.get("changed_paths"),
        int(body.get("timeout_ms") or 30_000),
    )


@router.get("/jobs/{job_id}")
def application_factory_job(job_id: str) -> Dict[str, Any]:
    job = APPLICATION_FACTORY.jobs.get(job_id)
    if job is None:
        return {
            "schema": "HHS_APPLICATION_FACTORY_JOB_ROUTE_RESULT_V1",
            "ok": False,
            "status": "REJECT_APPLICATION_JOB_UNKNOWN",
            "job_id": job_id,
        }
    return {
        "schema": "HHS_APPLICATION_FACTORY_JOB_ROUTE_RESULT_V1",
        "ok": True,
        "status": f"APPLICATION_JOB_{job.get('state')}",
        "job": job,
    }


@router.post("/jobs/{job_id}/cancel")
def application_factory_cancel(job_id: str) -> Dict[str, Any]:
    return APPLICATION_FACTORY.cancel_job(job_id)


@router.post("/jobs/{job_id}/retry")
def application_factory_retry(job_id: str) -> Dict[str, Any]:
    return APPLICATION_FACTORY.retry_job(job_id)


@router.get("/projects/{project_id}/source.zip", response_model=None)
def application_factory_source_zip(project_id: str) -> Any:
    result = APPLICATION_FACTORY.export_source_zip(project_id)
    if not result.get("ok"):
        return result
    headers = {
        "Content-Disposition": f"attachment; filename={result['filename']}",
        "X-HHS-Source-Root-Hash72": str(result["manifest"]["source_root_hash72"]),
        "X-HHS-Export-Root-Hash72": str(result["manifest"]["export_root_hash72"]),
        "X-HHS-Transport-SHA256": str(result["sha256_transport_hint"]),
    }
    return Response(content=result["zip_bytes"], media_type="application/zip", headers=headers)


@router.get("/projects/{project_id}/replay")
def application_factory_replay(project_id: str) -> Dict[str, Any]:
    return APPLICATION_FACTORY.replay_project(project_id)

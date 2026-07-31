"""Pass 183 probability hydration HTTP and WebSocket projection."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import os
from typing import Any

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field

from hhs_runtime.pass183 import (
    ADAPTER_EQUATIONS,
    GLOBAL_MODULUS,
    Pass183Error,
    ProbabilityHydrationJobStore,
    ProbabilityHydrationRuntime,
)

router = APIRouter(prefix="/api/v1/probability", tags=["pass183-probability-hydration"])
_runtime: ProbabilityHydrationRuntime | None = None
_jobs: ProbabilityHydrationJobStore | None = None


def _runtime_instance() -> ProbabilityHydrationRuntime:
    global _runtime
    if _runtime is None:
        _runtime = ProbabilityHydrationRuntime()
    return _runtime


def _job_store() -> ProbabilityHydrationJobStore:
    global _jobs
    if _jobs is None:
        root = Path(os.environ.get("HHS_PASS183_JOB_DIR", "var/pass183_probability_jobs"))
        _jobs = ProbabilityHydrationJobStore(_runtime_instance(), root)
    return _jobs


def _error(exc: Pass183Error) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "classification": exc.classification,
            "detail": exc.detail,
            "guidance": "Correct the exact equation, probability domain, membrane structure, or seed manifest and retry.",
        },
    )


class ProbabilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adapter: str
    equation: str
    manifest: dict[str, Any] = Field(default_factory=dict)
    seed_class: str = "DETERMINISTIC_ENUMERATION"
    seed: str | None = None
    modulus: int = GLOBAL_MODULUS
    timeout_ms: int = Field(default=30_000, ge=1, le=300_000)


@router.get("/status")
async def probability_status() -> dict[str, Any]:
    status = _runtime_instance().status()
    return {
        **status,
        "api": "/api/v1/probability",
        "studio": "/probability-hydration/",
        "jobs_persistent": True,
        "websocket_events": True,
    }


@router.get("/adapters")
async def probability_adapters() -> dict[str, Any]:
    return {
        "classification": "P183_OK",
        "adapters": [
            {"adapter": adapter, "canonical_equation": equation}
            for adapter, equation in sorted(ADAPTER_EQUATIONS.items())
        ],
    }


@router.post("/parse")
async def probability_parse(request: ProbabilityRequest) -> dict[str, Any]:
    try:
        return _runtime_instance().inspect(adapter=request.adapter, equation=request.equation)
    except Pass183Error as exc:
        raise _error(exc) from exc


@router.post("/validate")
async def probability_validate(request: ProbabilityRequest) -> dict[str, Any]:
    try:
        evaluation = _runtime_instance().execute(
            adapter=request.adapter,
            equation=request.equation,
            manifest=request.manifest,
            seed_class=request.seed_class,
            seed=request.seed,
            modulus=request.modulus,
            commit=False,
        )
        return {
            "classification": "HHS_PASS_183_DOMAIN_AND_EQUATION_VALID",
            "probability_domain_valid": evaluation["probability_domain_valid"],
            "source_equation_true": evaluation["source_equation_true"],
            "membranes": evaluation["membranes"],
            "randomness_manifest": evaluation["randomness_manifest"],
        }
    except Pass183Error as exc:
        raise _error(exc) from exc


@router.post("/hydrate")
async def probability_hydrate(request: ProbabilityRequest) -> dict[str, Any]:
    try:
        evaluation = _runtime_instance().execute(
            adapter=request.adapter,
            equation=request.equation,
            manifest=request.manifest,
            seed_class=request.seed_class,
            seed=request.seed,
            modulus=request.modulus,
            commit=False,
        )
        return {
            "classification": "HHS_PASS_183_EXACT_HYDRATION_READY_FOR_VM81",
            "evaluation": evaluation,
            "mutation_authority": False,
        }
    except Pass183Error as exc:
        raise _error(exc) from exc


@router.post("/execute")
async def probability_execute(request: ProbabilityRequest) -> dict[str, Any]:
    store = _job_store()
    job = store.create(
        {
            "adapter": request.adapter,
            "equation": request.equation,
            "manifest": request.manifest,
            "seed_class": request.seed_class,
            "seed": request.seed,
            "modulus": request.modulus,
        },
        timeout_ms=request.timeout_ms,
    )
    return asdict(store.run(job.job_id))


@router.post("/replay")
async def probability_replay() -> dict[str, Any]:
    try:
        return _runtime_instance().replay()
    except Pass183Error as exc:
        raise _error(exc) from exc


@router.get("/jobs/{job_id}")
async def probability_job(job_id: str) -> dict[str, Any]:
    try:
        return asdict(_job_store().get(job_id))
    except Pass183Error as exc:
        raise HTTPException(status_code=404, detail={"classification": exc.classification, "detail": exc.detail}) from exc


@router.post("/jobs/{job_id}/cancel")
async def probability_cancel(job_id: str) -> dict[str, Any]:
    try:
        return asdict(_job_store().cancel(job_id))
    except Pass183Error as exc:
        raise _error(exc) from exc


@router.post("/jobs/{job_id}/retry")
async def probability_retry(job_id: str, timeout_ms: int = 30_000) -> dict[str, Any]:
    try:
        retried = _job_store().retry(job_id, timeout_ms=timeout_ms)
        return asdict(_job_store().run(retried.job_id))
    except Pass183Error as exc:
        raise _error(exc) from exc


@router.websocket("/jobs/{job_id}/events")
async def probability_events(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    try:
        job = _job_store().get(job_id)
        await websocket.send_json(
            {
                "classification": "HHS_PASS_183_JOB_EVENT_STREAM",
                "job_id": job_id,
                "state": job.state,
                "events": job.events,
                "terminal": job.state in ProbabilityHydrationJobStore.TERMINAL,
            }
        )
    except Pass183Error as exc:
        await websocket.send_json({"classification": exc.classification, "detail": exc.detail})
    except WebSocketDisconnect:
        return
    finally:
        try:
            await websocket.close()
        except RuntimeError:
            pass

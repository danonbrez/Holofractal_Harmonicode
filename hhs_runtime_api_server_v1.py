"""Retired legacy Runtime API v1 application constructor with preserved callables.

Pass219 I181 removes this module's independent FastAPI identity after I180 moved
its four HTTP operations into the governed Pass170 adapter and proved that its
four websocket paths already have canonical production-base replacements.  The
legacy calculation/agent/certification functions remain importable; requesting
``hhs_runtime_api_server_v1:app`` lazily resolves the exact canonical Pass170
application rather than constructing or exposing another public application.
"""
from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from hhs_backend_final_certification_v1 import HHSBackendFinalCertificationV1
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.harmonicode_interpreter_v1 import interpret
from hhs_runtime.harmonicode_constraint_solver_v1 import solve_interpreter_result
from hhs_runtime.hhs_interpreter_autocorrection_suggestions_v1 import (
    build_autocorrection_suggestions,
    suggestions_to_training_feedback,
)
from hhs_runtime.hhs_correction_simulation_overlay_v1 import (
    build_correction_simulation_overlay,
    overlay_to_training_feedback,
)
from hhs_runtime.hhs_correction_branch_competition_v1 import (
    compete_correction_branches,
    branch_frontier_to_training_feedback,
)
from hhs_runtime.hhs_convergence_packet_v1 import build_convergence_packet
from hhs_runtime.hhs_agent_patch_planner_v1 import plan_transformation_patch
from hhs_runtime.hhs_branch_to_equation_manifest_v1 import select_and_bind_equation_manifest
from hhs_runtime.hhs_ir_transpiler_v1 import transpile_manifest
from hhs_runtime.runtime_ws import (
    emit_graph_event,
    emit_replay_event,
    emit_runtime_event,
    emit_transport_event,
    graph_stream,
    replay_stream,
    runtime_stream,
    transport_stream,
)

APP_NAME = "HHS Runtime API Server v1"
ARTIFACT_ROOT = Path("demo_reports/runtime_api")
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

RETIREMENT_CLASSIFICATION = "PASS170_LEGACY_RUNTIME_API_V1_CONSTRUCTOR_RETIRED_I181"
CANONICAL_TARGET = "hhs_backend.public_api_server:app"
INDEPENDENT_FASTAPI_CONSTRUCTOR = False
PUBLIC_PORT_AUTHORITY = False
NEW_VM81_AUTHORITY = False
NEW_HASH72_MINT_AUTHORITY = False
HASH216_PERSISTENCE_AUTHORITY = False
CAPABILITY_TOKEN_AUTHORITY = False

legacy_router = APIRouter(tags=["legacy-runtime-api-v1-retired-i181"])


class CalculatorEvaluateRequest(BaseModel):
    expression: str


class AgentRunLoopRequest(BaseModel):
    expression: str
    auto_continue: bool = True
    max_passes: int = 3


def _calculator_evaluation_payload(expression: str) -> Dict[str, Any]:
    interpreted = interpret(expression)
    solved = solve_interpreter_result(interpreted)

    asyncio.create_task(
        emit_runtime_event(
            {
                "operation": "calculator_evaluate",
                "expression": expression,
                "receipt_hash72": interpreted.receipt.receipt_hash72,
                "source_hash72": interpreted.receipt.source_hash72,
            }
        )
    )

    autocorrections = build_autocorrection_suggestions(
        {"receipt": {"source_hash72": interpreted.receipt.source_hash72}},
        source_hash72=interpreted.receipt.source_hash72,
    )
    simulation_overlay = build_correction_simulation_overlay(
        autocorrections.to_dict(),
        source_hash72=interpreted.receipt.source_hash72,
    )
    branch_frontier = compete_correction_branches(simulation_overlay.to_dict())

    return {
        "interpreter": interpreted.to_dict(),
        "solver": solved.to_dict(),
        "autocorrections": autocorrections.to_dict(),
        "correctionSimulation": simulation_overlay.to_dict(),
        "correctionBranchFrontier": branch_frontier.to_dict(),
        "result_hash72": hash72_digest(
            ("calculator_evaluate_v1", interpreted.receipt.receipt_hash72),
            width=24,
        ),
    }


def _agent_run_loop_payload(
    expression: str,
    *,
    auto_continue: bool = True,
    max_passes: int = 3,
) -> Dict[str, Any]:
    pass_count = max(1, min(int(max_passes or 1), 12)) if auto_continue else 1
    current_expression = expression
    passes: List[Dict[str, Any]] = []

    for pass_index in range(pass_count):
        evaluation = _calculator_evaluation_payload(current_expression)
        asyncio.create_task(
            emit_replay_event(
                {
                    "operation": "agent_run_loop",
                    "pass_index": pass_index,
                    "expression": current_expression,
                    "evaluation_hash72": evaluation.get("result_hash72"),
                }
            )
        )

        feedback_records = [
            suggestions_to_training_feedback(evaluation.get("autocorrections", {})),
            overlay_to_training_feedback(evaluation.get("correctionSimulation", {})),
            branch_frontier_to_training_feedback(evaluation.get("correctionBranchFrontier", {})),
        ]
        convergence = build_convergence_packet(current_expression, [], [])
        patch_plan = plan_transformation_patch(convergence.to_dict())
        equation_manifest = select_and_bind_equation_manifest(
            current_expression,
            cycles=pass_index + 1,
            feedback_records=feedback_records,
            windows=72,
            target_layer="normalized",
        )
        transpile_receipt = transpile_manifest(
            equation_manifest,
            targets=["python", "c", "asm"],
        )
        pass_receipt_hash72 = hash72_digest(
            (
                "agent_run_loop_pass_v2",
                pass_index,
                current_expression,
                evaluation.get("result_hash72"),
                convergence.packet_hash72,
                patch_plan.get("patch_hash72"),
                equation_manifest.get("aggregate_hash72"),
                transpile_receipt.receipt_hash72,
            ),
            width=24,
        )
        passes.append(
            {
                "pass_index": pass_index,
                "expression": current_expression,
                "evaluation": evaluation,
                "convergence_packet": convergence.to_dict(),
                "patch_plan": patch_plan,
                "equation_manifest": equation_manifest,
                "transpile_receipt": transpile_receipt.to_dict(),
                "receipt_hash72": pass_receipt_hash72,
            }
        )
        if not auto_continue:
            break

    receipt_hash72 = hash72_digest(
        ("agent_run_loop_v2", expression, [item["receipt_hash72"] for item in passes]),
        width=24,
    )
    return {
        "status": "LOCKED",
        "expression": expression,
        "passes": passes,
        "receipt_hash72": receipt_hash72,
        "authority": "kernel_only_pipeline",
    }


@legacy_router.get("/api/status")
async def api_status() -> Dict[str, Any]:
    return {"status": "OK", "server": APP_NAME, "time_ns": time.time_ns()}


@legacy_router.post("/api/calculator/evaluate")
async def api_calculator_evaluate(req: CalculatorEvaluateRequest) -> Dict[str, Any]:
    return _calculator_evaluation_payload(req.expression)


@legacy_router.post("/api/agent/run-loop")
async def api_agent_run_loop(req: AgentRunLoopRequest) -> Dict[str, Any]:
    return _agent_run_loop_payload(
        req.expression,
        auto_continue=req.auto_continue,
        max_passes=req.max_passes,
    )


@legacy_router.get("/api/certification")
async def api_certification() -> Dict[str, Any] | JSONResponse:
    try:
        result = HHSBackendFinalCertificationV1().run_all()
        asyncio.create_task(
            emit_transport_event(
                {"operation": "certification", "status": result.get("status")}
            )
        )
        return result
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "CERTIFICATION_ERROR", "error": str(exc)},
        )


@legacy_router.websocket("/ws/runtime")
async def ws_runtime(websocket: WebSocket) -> None:
    await runtime_stream(websocket)


@legacy_router.websocket("/ws/replay")
async def ws_replay(websocket: WebSocket) -> None:
    await replay_stream(websocket)


@legacy_router.websocket("/ws/graph")
async def ws_graph(websocket: WebSocket) -> None:
    await graph_stream(websocket)


@legacy_router.websocket("/ws/transport")
async def ws_transport(websocket: WebSocket) -> None:
    await transport_stream(websocket)


def _canonical_app():
    """Resolve the canonical application only when legacy ``app`` is requested."""
    from hhs_backend.public_api_server import app as canonical_app

    return canonical_app


def __getattr__(name: str):
    if name == "app":
        return _canonical_app()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | {"app"})


def main() -> None:
    import uvicorn

    uvicorn.run(
        CANONICAL_TARGET,
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()


__all__ = [
    "APP_NAME",
    "ARTIFACT_ROOT",
    "AgentRunLoopRequest",
    "CANONICAL_TARGET",
    "CAPABILITY_TOKEN_AUTHORITY",
    "CalculatorEvaluateRequest",
    "HASH216_PERSISTENCE_AUTHORITY",
    "INDEPENDENT_FASTAPI_CONSTRUCTOR",
    "NEW_HASH72_MINT_AUTHORITY",
    "NEW_VM81_AUTHORITY",
    "PUBLIC_PORT_AUTHORITY",
    "RETIREMENT_CLASSIFICATION",
    "_agent_run_loop_payload",
    "_calculator_evaluation_payload",
    "api_agent_run_loop",
    "api_calculator_evaluate",
    "api_certification",
    "api_status",
    "app",
    "legacy_router",
    "main",
    "ws_graph",
    "ws_replay",
    "ws_runtime",
    "ws_transport",
]

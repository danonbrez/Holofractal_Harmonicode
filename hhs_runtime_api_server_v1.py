from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from hhs_backend_final_certification_v1 import HHSBackendFinalCertificationV1
from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts
from hhs_runtime.hhs_operator_selection_engine_v1 import OperatorSelectionGoal
from hhs_runtime.hhs_phase_coherent_operator_loop_v1 import run_phase_coherent_operator_loop
from hhs_runtime.hhs_realtime_multimodal_phase_integration_v1 import lock_live_multimodal_phase
from hhs_runtime.hhs_runtime_anomaly_detector_v1 import detect_runtime_anomalies
from hhs_runtime.hhs_phase_stabilization_feedback_loop_v1 import propose_corrective_operators, execute_approved_corrections
from hhs_runtime.hhs_loshu_phase_embedding_v1 import hash72_digest
from hhs_runtime.harmonicode_phase_projection_engine_v1 import interpret_transform_project
from hhs_runtime.harmonicode_root_execution_engine_v1 import stage_root_execution
from hhs_runtime.hhs_entangled_reciprocal_seesaw_temporal_shell_v1 import generate_temporal_shells
from hhs_runtime.hhs_branch_to_equation_manifest_v1 import select_and_bind_equation_manifest
from hhs_runtime.hhs_ir_transpiler_v1 import transpile_manifest
from hhs_runtime.hhs_interpreter_autocorrection_suggestions_v1 import build_autocorrection_suggestions, suggestions_to_training_feedback
from hhs_runtime.hhs_correction_simulation_overlay_v1 import build_correction_simulation_overlay, overlay_to_training_feedback
from hhs_runtime.hhs_correction_branch_competition_v1 import compete_correction_branches, branch_frontier_to_training_feedback
from hhs_runtime.harmonicode_interpreter_v1 import interpret
from hhs_runtime.harmonicode_constraint_solver_v1 import solve_interpreter_result
from hhs_runtime.hhs_convergence_packet_v1 import build_convergence_packet
from hhs_runtime.hhs_agent_patch_planner_v1 import plan_transformation_patch
from hhs_runtime.hhs_audio_phase_transport_encoder_v1 import encode_expression_to_wav_stems
from hhs_runtime.hhs_symbolic_linguistic_substitution_solver_v1 import solve_symbolic_linguistic_substitutions
from hhs_runtime.hhs_wordnet_relation_enforcer_v1 import default_wordnet_paths, load_wordnet_relations

APP_NAME = "HHS Runtime API Server v1"
ARTIFACT_ROOT = Path("demo_reports/runtime_api")
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STREAM_INTERVAL = 0.75
BATCH_SIZE = 3
LAST_CORRECTION_EXECUTION: Optional[Dict[str, Any]] = None
LAST_ROOT_CANDIDATE: Optional[Dict[str, Any]] = None
LAST_ROOT_COMMIT: Optional[Dict[str, Any]] = None
LAST_EQUATION_MANIFEST: Optional[Dict[str, Any]] = None
LAST_TRANSPILE_RECEIPT: Optional[Dict[str, Any]] = None
WORDNET_RELATION_DB: Optional[Dict[str, Any]] = None

class CalculatorEvaluateRequest(BaseModel):
    expression: str

class AgentRunLoopRequest(BaseModel):
    expression: str
    auto_continue: bool = True
    max_passes: int = 3


def _calculator_evaluation_payload(expression: str) -> Dict[str, Any]:
    interpreted = interpret(expression)
    solved = solve_interpreter_result(interpreted)
    symbolic_substitution = solve_symbolic_linguistic_substitutions(expression, WORDNET_RELATION_DB or {})
    autocorrections = build_autocorrection_suggestions({"receipt": {"source_hash72": interpreted.receipt.source_hash72}}, source_hash72=interpreted.receipt.source_hash72)
    simulation_overlay = build_correction_simulation_overlay(autocorrections.to_dict(), source_hash72=interpreted.receipt.source_hash72)
    branch_frontier = compete_correction_branches(simulation_overlay.to_dict())
    return {
        "interpreter": interpreted.to_dict(),
        "solver": solved.to_dict(),
        "symbolic_substitution": symbolic_substitution.to_dict(),
        "autocorrections": autocorrections.to_dict(),
        "correctionSimulation": simulation_overlay.to_dict(),
        "correctionBranchFrontier": branch_frontier.to_dict(),
        "result_hash72": hash72_digest(("calculator_evaluate_v1", interpreted.receipt.receipt_hash72), width=24),
    }


def _convergence_items_from_evaluation(evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
    interpreter = evaluation.get("interpreter", {})
    solver = evaluation.get("solver", {})
    substitution = evaluation.get("symbolic_substitution", {})
    items: List[Dict[str, Any]] = [
        {
            "id": "interpreter",
            "kind": "INTERPRETER_RECEIPT",
            "text": str(interpreter.get("receipt", {}).get("receipt_hash72", interpreter.get("receipt_hash72", ""))),
            "phaseIndex": 0,
            "payload": interpreter,
        },
        {
            "id": "solver",
            "kind": "CONSTRAINT_SOLVER_RECEIPT",
            "text": str(solver.get("receipt_hash72", solver.get("status", ""))),
            "phaseIndex": 0,
            "payload": solver,
        },
        {
            "id": "symbolic_substitution",
            "kind": "SYMBOLIC_SUBSTITUTION_RECEIPT",
            "text": str(substitution.get("receipt_hash72", substitution.get("status", ""))),
            "phaseIndex": 0,
            "payload": substitution,
        },
    ]
    return items


def _convergence_influences_from_evaluation(evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
    influences: List[Dict[str, Any]] = []
    for key, kind in [
        ("autocorrections", "AUTOCORRECTION"),
        ("correctionSimulation", "SIMULATION_OVERLAY"),
        ("correctionBranchFrontier", "BRANCH_FRONTIER"),
    ]:
        payload = evaluation.get(key, {})
        influences.append(
            {
                "id": key,
                "kind": kind,
                "text": str(payload.get("receipt_hash72", payload.get("frontier_hash72", payload.get("overlay_hash72", key)))),
                "phaseIndex": 0,
                "payload": payload,
            }
        )
    return influences


def _agent_run_loop_payload(expression: str, *, auto_continue: bool = True, max_passes: int = 3) -> Dict[str, Any]:
    pass_count = max(1, min(int(max_passes or 1), 12)) if auto_continue else 1
    current_expression = expression
    passes: List[Dict[str, Any]] = []

    for pass_index in range(pass_count):
        evaluation = _calculator_evaluation_payload(current_expression)
        items = _convergence_items_from_evaluation(evaluation)
        influences = _convergence_influences_from_evaluation(evaluation)
        convergence = build_convergence_packet(current_expression, items, influences)
        patch_plan = plan_transformation_patch(convergence.to_dict())
        feedback_records = [
            suggestions_to_training_feedback(evaluation.get("autocorrections", {})),
            overlay_to_training_feedback(evaluation.get("correctionSimulation", {})),
            branch_frontier_to_training_feedback(evaluation.get("correctionBranchFrontier", {})),
        ]
        equation_manifest = select_and_bind_equation_manifest(
            current_expression,
            cycles=pass_index + 1,
            feedback_records=feedback_records,
            windows=72,
            target_layer="normalized",
        )
        transpile_receipt = transpile_manifest(equation_manifest, targets=["python", "c", "asm"])
        pass_receipt_hash72 = hash72_digest(
            (
                "agent_run_loop_pass_v1",
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
        manifest_status = equation_manifest.get("manifest", {}).get("status")
        if manifest_status == "READY":
            break

    receipt_hash72 = hash72_digest(("agent_run_loop_v1", expression, [p["receipt_hash72"] for p in passes]), width=24)
    return {
        "status": "LOCKED",
        "expression": expression,
        "passes": passes,
        "receipt_hash72": receipt_hash72,
        "authority": "canonical_hhs_runtime_pipeline",
    }

@app.get("/api/status")
async def api_status() -> Dict[str, Any]:
    return {"status": "OK", "server": APP_NAME, "time_ns": time.time_ns()}

@app.post("/api/calculator/evaluate")
async def api_calculator_evaluate(req: CalculatorEvaluateRequest) -> Dict[str, Any]:
    return _calculator_evaluation_payload(req.expression)

@app.post("/api/agent/run-loop")
async def api_agent_run_loop(req: AgentRunLoopRequest) -> Dict[str, Any]:
    return _agent_run_loop_payload(req.expression, auto_continue=req.auto_continue, max_passes=req.max_passes)

@app.get("/api/certification")
async def api_certification() -> Dict[str, Any]:
    try:
        return HHSBackendFinalCertificationV1().run_all()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "CERTIFICATION_ERROR", "error": str(exc)})

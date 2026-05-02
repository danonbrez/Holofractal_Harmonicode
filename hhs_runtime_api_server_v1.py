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

# --- RESTORED PIPELINE ---

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

@app.get("/api/status")
async def api_status() -> Dict[str, Any]:
    return {"status": "OK", "server": APP_NAME, "time_ns": time.time_ns()}

@app.post("/api/calculator/evaluate")
async def api_calculator_evaluate(req: CalculatorEvaluateRequest) -> Dict[str, Any]:
    return _calculator_evaluation_payload(req.expression)

@app.post("/api/agent/run-loop")
async def api_agent_run_loop(req: AgentRunLoopRequest) -> Dict[str, Any]:
    evaluation = _calculator_evaluation_payload(req.expression)
    return {
        "status": "REVERTED",
        "expression": req.expression,
        "evaluation": evaluation,
        "receipt_hash72": evaluation.get("result_hash72"),
    }

@app.get("/api/certification")
async def api_certification() -> Dict[str, Any]:
    try:
        return HHSBackendFinalCertificationV1().run_all()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "CERTIFICATION_ERROR", "error": str(exc)})

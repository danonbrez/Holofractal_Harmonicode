"""
hhs_runtime_api_server_v1.py
(Updated with runtime projection, temporal shell streaming, branch-equation manifest API, transpiler API, and interpreter autocorrection suggestions)
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List

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
from hhs_runtime.harmonicode_interpreter_v1 import interpret
from hhs_runtime.harmonicode_constraint_solver_v1 import solve_interpreter_result

APP_NAME = "HHS Runtime API Server v1"
ARTIFACT_ROOT = Path("demo_reports/runtime_api")
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STREAM_INTERVAL = 0.75
BATCH_SIZE = 3
LAST_CORRECTION_EXECUTION: Dict[str, Any] | None = None
LAST_ROOT_CANDIDATE: Dict[str, Any] | None = None
LAST_ROOT_COMMIT: Dict[str, Any] | None = None
LAST_EQUATION_MANIFEST: Dict[str, Any] | None = None
LAST_TRANSPILE_RECEIPT: Dict[str, Any] | None = None


class CorrectionApprovalRequest(BaseModel):
    approved_suggestion_hashes: List[str]


class RootStageRequest(BaseModel):
    phases: List[int]
    target_layer: str = "normalized"


class RootCommitRequest(BaseModel):
    execution_candidate_hash72: str


class CalculatorEvaluateRequest(BaseModel):
    expression: str


class TranspileManifestRequest(BaseModel):
    manifest: Dict[str, Any] | None = None
    targets: List[str] = ["python"]


def _observations(observed_at_ns: int | None = None) -> List[Dict[str, Any]]:
    observed = observed_at_ns if observed_at_ns is not None else time.time_ns()
    return [
        {"modality": "AUDIO", "source_id": "audio_frame_0", "observed_at_ns": observed, "payload": {"rms": "1/8", "spectral_centroid": 432, "frame_hash": "audio_demo"}},
        {"modality": "HARMONICODE", "source_id": "kernel_phase", "observed_at_ns": observed, "payload": {"u72": True, "theta15": True, "omega": True}},
        {"modality": "XYZW", "source_id": "xyzw_algebra", "observed_at_ns": observed, "payload": {"xy": 1, "yx": -1, "zw": 1, "wz": -1}},
        {"modality": "HASH72", "source_id": "hash72_commit", "observed_at_ns": observed, "payload": {"commitment": "H72-DEMO"}},
        {"modality": "TEXT", "source_id": "text_support", "observed_at_ns": observed, "payload": {"intent": "supporting witness"}},
    ]


def _sample_corpus() -> Dict[str, Any]:
    return {"id": "runtime_api_corpus", "title": "Runtime API Corpus", "mime_type": "text/plain", "text": "# HHS Alignment Axiom\nStatement: Preserve Δe=0, Ψ=0, Θ15=true, Ω=true while translating claims.\n"}


def _projection_source() -> str:
    return """
PLASTIC_EIGENSTATE_CLOSURE_GATE := {
  ρ^3 = ρ + 1,
  b = ρ^2,
  b^2 = ρ^4,
  a^2 = 1,
  c^2 = b^2 + a^2,
  u^72 = Ω
}
PLASTIC_EIGENSTATE_CLOSURE_GATE
"""


def build_phase_projection() -> Dict[str, Any]:
    return interpret_transform_project(_projection_source(), "normalized")


def build_temporal_shells(projection: Dict[str, Any]) -> Dict[str, Any]:
    witness = projection.get("projection", {}).get("phase_witness", {})
    seed = witness.get("anchor_hash72") or projection.get("full_receipt_hash72") or "HHS_TEMPORAL_SHELL_SEED"
    run = generate_temporal_shells(str(seed), cycles=1).to_dict()
    run["steps"] = run["steps"][:72]
    return run


def build_equation_manifest() -> Dict[str, Any]:
    global LAST_EQUATION_MANIFEST
    LAST_EQUATION_MANIFEST = select_and_bind_equation_manifest("HHS_GUI_CALCULATOR", cycles=1, windows=9, target_layer="normalized")
    return LAST_EQUATION_MANIFEST


def build_transpile_receipt(manifest: Dict[str, Any] | None = None, targets: List[str] | None = None) -> Dict[str, Any]:
    global LAST_TRANSPILE_RECEIPT
    source_manifest = manifest or LAST_EQUATION_MANIFEST or build_equation_manifest()
    LAST_TRANSPILE_RECEIPT = transpile_manifest(source_manifest, targets or ["python"]).to_dict()
    return LAST_TRANSPILE_RECEIPT


def build_phase_lock() -> Dict[str, Any]:
    state_patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "api_phase_locked_state"}}
    return lock_live_multimodal_phase(_observations(), state_patch=state_patch, ledger_path=ARTIFACT_ROOT / "latest_phase_lock_ledger.json").to_dict()


def _load_canonical_blocks() -> List[Dict[str, Any]]:
    ledger_path = ARTIFACT_ROOT / "runtime_api_corpus_ledger.json"
    ingest_drive_corpus_artifacts([_sample_corpus()], ledger_path=ledger_path)
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    return [block["payload"] for block in ledger.get("blocks", [])]


def build_operator_loop(phase_lock: Dict[str, Any] | None = None) -> Dict[str, Any]:
    phase_lock = phase_lock or build_phase_lock()
    blocks = _load_canonical_blocks()
    goal = OperatorSelectionGoal("explain alignment", ["LOGIC"], ["AXIOM"], 3, True, False, False)
    return run_phase_coherent_operator_loop("Meaning must persist.", blocks, goal, live_phase_lock_receipt=phase_lock).to_dict()


def build_runtime_snapshot() -> Dict[str, Any]:
    phase = build_phase_lock()
    loop = build_operator_loop(phase)
    projection = build_phase_projection()
    temporal_shells = build_temporal_shells(projection)
    equation_manifest = build_equation_manifest()
    transpile_receipt = build_transpile_receipt(equation_manifest, ["python"])
    snapshot = {"phase": phase, "operatorLoop": loop, "projection": projection, "temporalShells": temporal_shells, "equationManifest": equation_manifest, "transpileReceipt": transpile_receipt, "server": {"name": APP_NAME, "generated_at_ns": time.time_ns()}}
    snapshot["anomalies"] = detect_runtime_anomalies(snapshot)
    snapshot["corrections"] = propose_corrective_operators(snapshot)
    snapshot["lastCorrectionExecution"] = LAST_CORRECTION_EXECUTION
    snapshot["lastRootCandidate"] = LAST_ROOT_CANDIDATE
    snapshot["lastRootCommit"] = LAST_ROOT_COMMIT
    return snapshot


def _relock_for_correction(_suggestion: Any) -> Dict[str, Any]:
    return build_phase_lock()


def _verify_correction(suggestion: Any, relock: Dict[str, Any]) -> Dict[str, Any]:
    loop = build_operator_loop(relock)
    ok = relock.get("status") == "LOCKED" and loop.get("status") == "EXECUTED" and loop.get("loop_replay_receipt", {}).get("invalid", 0) == 0
    verification_hash = hash72_digest(("api_correction_verification_v1", suggestion.to_dict(), relock.get("receipt_hash72"), loop.get("receipt_hash72"), ok), width=24)
    return {"ok": ok, "verification_hash72": verification_hash, "operator_loop_status": loop.get("status"), "operator_loop_receipt_hash72": loop.get("receipt_hash72")}


def _root_candidate_to_correction_payload(root_candidate: Dict[str, Any]) -> Dict[str, Any]:
    candidate = root_candidate.get("candidate", {})
    candidate_hash = candidate.get("execution_candidate_hash72")
    return {"anomalies": {"status": "CLEAR", "critical": 0, "warn": 0, "alerts": []}, "phase": build_phase_lock(), "operatorLoop": build_operator_loop(), "corrections": {"suggestions": [{"kind": "REQUIRE_EXTERNAL_PHASE_ANCHOR", "priority": 100, "target_modalities": ["HARMONICODE", "HASH72", "XYZW", "AUDIO"], "target_phase_indices": [int(candidate.get("phase_index", 0) or 0)], "reason": "Stage root equation through runtime correction pipeline.", "proposed_patch": {"op": "STAGE_ROOT_EQUATION", "candidate_hash72": candidate_hash, "equation": candidate.get("equation", {}).get("equation")}, "suggestion_hash72": str(candidate_hash)}], "summary_hash72": hash72_digest(("root_stage_correction_summary_v1", candidate_hash), width=24)}}


@app.get("/api/status")
async def api_status() -> Dict[str, Any]:
    return {"status": "OK", "server": APP_NAME, "read_only": False, "correction_execution_requires_approval": True, "root_commit_requires_consensus": True, "temporal_shells_enabled": True, "equation_manifest_enabled": True, "transpiler_enabled": True, "autocorrection_suggestions_enabled": True, "time_ns": time.time_ns()}


@app.get("/api/latest-phase-lock")
async def api_latest_phase_lock() -> Dict[str, Any]:
    return build_phase_lock()


@app.get("/api/latest-operator-loop")
async def api_latest_operator_loop() -> Dict[str, Any]:
    return build_operator_loop()


@app.get("/api/latest-projection")
async def api_latest_projection() -> Dict[str, Any]:
    return build_phase_projection()


@app.get("/api/latest-temporal-shells")
async def api_latest_temporal_shells() -> Dict[str, Any]:
    return build_temporal_shells(build_phase_projection())


@app.get("/api/latest-equation-manifest")
async def api_latest_equation_manifest() -> Dict[str, Any]:
    return build_equation_manifest()


@app.get("/api/latest-transpile-receipt")
async def api_latest_transpile_receipt() -> Dict[str, Any]:
    return build_transpile_receipt(build_equation_manifest(), ["python"])


@app.post("/api/transpile/manifest")
async def api_transpile_manifest(req: TranspileManifestRequest) -> Dict[str, Any]:
    return build_transpile_receipt(req.manifest, req.targets)


@app.post("/api/calculator/evaluate")
async def api_calculator_evaluate(req: CalculatorEvaluateRequest) -> Dict[str, Any]:
    interpreted = interpret(req.expression)
    solved = solve_interpreter_result(interpreted)
    stress_result = {"findings": [], "receipt": {"source_hash72": interpreted.receipt.source_hash72, "receipt_hash72": interpreted.receipt.stress_hash72}}
    autocorrections = build_autocorrection_suggestions(stress_result, source_hash72=interpreted.receipt.source_hash72)
    feedback = suggestions_to_training_feedback(autocorrections)
    result_hash = hash72_digest(("calculator_evaluate_v1", interpreted.receipt.receipt_hash72, solved.receipt.receipt_hash72, autocorrections.summary_hash72, feedback), width=24)
    return {"interpreter": interpreted.to_dict(), "solver": solved.to_dict(), "autocorrections": autocorrections.to_dict(), "autocorrection_feedback": feedback, "result_hash72": result_hash}


@app.get("/api/certification")
async def api_certification() -> Dict[str, Any]:
    try:
        return HHSBackendFinalCertificationV1().run_all()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "CERTIFICATION_ERROR", "error": f"{type(exc).__name__}: {exc}"})


@app.post("/api/corrections/execute")
async def api_execute_corrections(req: CorrectionApprovalRequest) -> Dict[str, Any]:
    global LAST_CORRECTION_EXECUTION
    snapshot = build_runtime_snapshot()
    result = execute_approved_corrections(snapshot, req.approved_suggestion_hashes, relock_fn=_relock_for_correction, verify_fn=_verify_correction)
    LAST_CORRECTION_EXECUTION = result
    return result


@app.post("/api/root/stage")
async def api_stage_root(req: RootStageRequest) -> Dict[str, Any]:
    global LAST_ROOT_CANDIDATE
    LAST_ROOT_CANDIDATE = stage_root_execution(req.phases, target_layer=req.target_layer)
    return LAST_ROOT_CANDIDATE


@app.post("/api/root/commit")
async def api_commit_root(req: RootCommitRequest) -> Dict[str, Any]:
    global LAST_ROOT_COMMIT
    if not LAST_ROOT_CANDIDATE:
        return JSONResponse(status_code=409, content={"status": "NO_ROOT_CANDIDATE", "reason": "Stage a root candidate before commit."})
    candidate = LAST_ROOT_CANDIDATE.get("candidate", {})
    if req.execution_candidate_hash72 != candidate.get("execution_candidate_hash72"):
        return JSONResponse(status_code=409, content={"status": "ROOT_HASH_MISMATCH", "expected": candidate.get("execution_candidate_hash72"), "received": req.execution_candidate_hash72})
    if candidate.get("status") != "STAGED":
        return JSONResponse(status_code=409, content={"status": "ROOT_NOT_STAGED", "candidate_status": candidate.get("status")})
    snapshot = _root_candidate_to_correction_payload(LAST_ROOT_CANDIDATE)
    result = execute_approved_corrections(snapshot, [req.execution_candidate_hash72], relock_fn=_relock_for_correction, verify_fn=_verify_correction)
    LAST_ROOT_COMMIT = {"candidate": LAST_ROOT_CANDIDATE, "commit": result, "commit_hash72": hash72_digest(("root_commit_result_v1", LAST_ROOT_CANDIDATE, result), width=24)}
    return LAST_ROOT_COMMIT


@app.websocket("/ws/runtime")
async def ws_runtime(websocket: WebSocket) -> None:
    await websocket.accept()
    buffer: List[Dict[str, Any]] = []
    try:
        while True:
            snapshot = build_runtime_snapshot()
            buffer.append(snapshot)
            if len(buffer) >= BATCH_SIZE:
                await websocket.send_json({"type": "runtime_batch", "payload": buffer})
                buffer.clear()
            await asyncio.sleep(STREAM_INTERVAL)
    except WebSocketDisconnect:
        return


def main() -> None:
    import uvicorn
    uvicorn.run("hhs_runtime_api_server_v1:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()

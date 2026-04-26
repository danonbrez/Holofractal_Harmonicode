"""
hhs_runtime_api_server_v1.py

FastAPI read-only runtime API + WebSocket stream for the HHS mobile runtime console.

Endpoints
---------
GET /api/status
GET /api/latest-phase-lock
GET /api/latest-operator-loop
GET /api/certification
WS  /ws/runtime

Run
---
    pip install fastapi uvicorn
    python hhs_runtime_api_server_v1.py

Then run GUI:
    cd gui/hhs-mobile-runtime-console
    npm run dev

Notes
-----
This server does not mutate kernel state directly. It builds certified/read-only
runtime snapshots from existing HHS modules and streams them to the GUI.
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

from hhs_backend_final_certification_v1 import HHSBackendFinalCertificationV1
from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts
from hhs_runtime.hhs_operator_selection_engine_v1 import OperatorSelectionGoal
from hhs_runtime.hhs_phase_coherent_operator_loop_v1 import run_phase_coherent_operator_loop
from hhs_runtime.hhs_realtime_multimodal_phase_integration_v1 import lock_live_multimodal_phase


APP_NAME = "HHS Runtime API Server v1"
ARTIFACT_ROOT = Path("demo_reports/runtime_api")
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {
        "id": "runtime_api_corpus",
        "title": "Runtime API Corpus",
        "mime_type": "text/plain",
        "text": """
# HHS Alignment Axiom
Statement: Preserve Δe=0, Ψ=0, Θ15=true, Ω=true while translating claims.

# Style Operator — Recursive Harmonic Prose
Write with recursive rhythm, controlled repetition, and semantic return. Apply the style without changing the claim.

# Writing Process — Draft Audit Compress Re-expand
Step 1: draft. Step 2: audit for semantic drift. Step 3: compress into an operator. Step 4: re-expand as clear prose.

# Operator Spec — Meaning Preservation
The operator must preserve meaning while transforming medium and style.
""",
    }


def build_phase_lock() -> Dict[str, Any]:
    state_patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "api_phase_locked_state"}}
    return lock_live_multimodal_phase(
        _observations(),
        state_patch=state_patch,
        ledger_path=ARTIFACT_ROOT / "latest_phase_lock_ledger.json",
    ).to_dict()


def _load_canonical_blocks() -> List[Dict[str, Any]]:
    ledger_path = ARTIFACT_ROOT / "runtime_api_corpus_ledger.json"
    ingest_drive_corpus_artifacts([_sample_corpus()], ledger_path=ledger_path)
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    return [block["payload"] for block in ledger.get("blocks", [])]


def build_operator_loop(phase_lock: Dict[str, Any] | None = None) -> Dict[str, Any]:
    phase_lock = phase_lock or build_phase_lock()
    blocks = _load_canonical_blocks()
    goal = OperatorSelectionGoal(
        intent="explain a technical alignment claim with harmonic recursive style and process audit",
        preferred_domains=["LOGIC", "STYLE", "PROCESS"],
        preferred_kinds=["AXIOM", "STYLE_OPERATOR", "WRITING_PROCESS"],
        max_chain_length=4,
        require_logic=True,
        require_style=True,
        require_process=True,
    )
    return run_phase_coherent_operator_loop(
        "The system must preserve meaning while changing form.",
        blocks,
        goal,
        live_phase_lock_receipt=phase_lock,
        feedback_ledger_path=ARTIFACT_ROOT / "operator_feedback_ledger.json",
        loop_ledger_path=ARTIFACT_ROOT / "operator_loop_ledger.json",
        execution_ledger_path=ARTIFACT_ROOT / "operator_execution_ledger.json",
    ).to_dict()


def build_runtime_snapshot() -> Dict[str, Any]:
    phase = build_phase_lock()
    loop = build_operator_loop(phase)
    return {
        "phase": phase,
        "operatorLoop": loop,
        "server": {
            "name": APP_NAME,
            "generated_at_ns": time.time_ns(),
            "read_only": True,
        },
    }


@app.get("/api/status")
async def api_status() -> Dict[str, Any]:
    return {"status": "OK", "server": APP_NAME, "read_only": True, "time_ns": time.time_ns()}


@app.get("/api/latest-phase-lock")
async def api_latest_phase_lock() -> Dict[str, Any]:
    return build_phase_lock()


@app.get("/api/latest-operator-loop")
async def api_latest_operator_loop() -> Dict[str, Any]:
    return build_operator_loop()


@app.get("/api/certification")
async def api_certification() -> Dict[str, Any]:
    try:
        return HHSBackendFinalCertificationV1().run_all()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "CERTIFICATION_ERROR", "error": f"{type(exc).__name__}: {exc}"})


@app.websocket("/ws/runtime")
async def ws_runtime(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            snapshot = build_runtime_snapshot()
            await websocket.send_json({"type": "runtime_snapshot", "payload": snapshot})
            await asyncio.sleep(0.75)
    except WebSocketDisconnect:
        return


def main() -> None:
    import uvicorn

    uvicorn.run("hhs_runtime_api_server_v1:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()

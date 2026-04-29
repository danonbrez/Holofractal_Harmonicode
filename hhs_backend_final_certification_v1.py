"""
hhs_backend_final_certification_v1.py

Final backend closure certification before GUI work.

Certifies the complete non-GUI execution path:

    curated corpus
    -> canonical blocks
    -> realtime multimodal phase lock
    -> phase-anchored operator loop
    -> execution receipt
    -> feedback ledger
    -> replay-valid reports

Run:
    python hhs_backend_final_certification_v1.py

Output:
    data/hhs_backend_final_certification_v1_report.json
    or $HHS_DATA_ROOT/hhs_backend_final_certification_v1_report.json
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List
import json
import os
import traceback

from hhs_realtime_phase_certification_v1 import RealtimePhaseCertificationV1
from hhs_runtime.hhs_drive_alignment_corpus_ingestor_v2 import ingest_drive_corpus_artifacts
from hhs_runtime.hhs_operator_selection_engine_v1 import OperatorSelectionGoal
from hhs_runtime.hhs_phase_coherent_operator_loop_v1 import PhaseLoopStatus, run_phase_coherent_operator_loop
from hhs_runtime.hhs_realtime_multimodal_phase_integration_v1 import LiveWitnessStatus, lock_live_multimodal_phase


DATA_ROOT = Path(os.environ.get("HHS_DATA_ROOT", "data")).resolve()
DATA_ROOT.mkdir(parents=True, exist_ok=True)
REPORT_PATH = DATA_ROOT / "hhs_backend_final_certification_v1_report.json"
LIVE_PHASE_PATH = DATA_ROOT / "hhs_backend_final_live_phase.json"
CORPUS_LEDGER_PATH = DATA_ROOT / "hhs_backend_final_corpus_ledger.json"
FEEDBACK_LEDGER_PATH = DATA_ROOT / "hhs_backend_final_feedback_ledger.json"
LOOP_LEDGER_PATH = DATA_ROOT / "hhs_backend_final_phase_loop_ledger.json"
EXECUTION_LEDGER_PATH = DATA_ROOT / "hhs_backend_final_execution_ledger.json"


@dataclass
class CertificationCase:
    name: str
    passed: bool
    detail: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSBackendFinalCertificationV1:
    def __init__(self) -> None:
        self.results: List[CertificationCase] = []

    def record(self, name: str, passed: bool, detail: str, payload: Dict[str, Any] | None = None) -> None:
        self.results.append(CertificationCase(name, passed, detail, payload or {}))

    def case(self, name: str, fn: Callable[[], None]) -> None:
        try:
            fn()
        except AssertionError as exc:
            self.record(name, False, str(exc), {"traceback": traceback.format_exc()})
        except Exception as exc:
            self.record(name, False, f"Unexpected exception: {type(exc).__name__}: {exc}", {"traceback": traceback.format_exc()})

    @staticmethod
    def observations(observed_at: int = 1_000_000_000) -> List[Dict[str, Any]]:
        return [
            {"modality": "AUDIO", "source_id": "audio_frame_0", "observed_at_ns": observed_at, "payload": {"rms": "1/8", "spectral_centroid": 432, "frame_hash": "audio_demo"}},
            {"modality": "HARMONICODE", "source_id": "kernel_phase", "observed_at_ns": observed_at, "payload": {"u72": True, "theta15": True, "omega": True}},
            {"modality": "XYZW", "source_id": "xyzw_algebra", "observed_at_ns": observed_at, "payload": {"xy": 1, "yx": -1, "zw": 1, "wz": -1}},
            {"modality": "HASH72", "source_id": "hash72_commit", "observed_at_ns": observed_at, "payload": {"commitment": "H72-DEMO"}},
            {"modality": "TEXT", "source_id": "text_support", "observed_at_ns": observed_at, "payload": {"intent": "supporting witness"}},
        ]

    @staticmethod
    def sample_corpus() -> Dict[str, Any]:
        return {
            "id": "backend_final_certification_corpus",
            "title": "Backend Final Certification Corpus",
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

    def test_realtime_phase_certification_runner(self) -> None:
        report = RealtimePhaseCertificationV1().run_all()
        assert report["all_ok"] is True, report
        self.record("realtime_phase_certification_runner", True, "Realtime phase certification runner passes.", report)

    def test_realtime_phase_bound_operator_loop(self) -> None:
        state_patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "phase_bound_operator_loop"}}
        live_phase = lock_live_multimodal_phase(
            self.observations(),
            state_patch=state_patch,
            ledger_path=str(LIVE_PHASE_PATH),
        ).to_dict()
        assert live_phase["status"] == LiveWitnessStatus.LOCKED.value, live_phase
        assert live_phase["replay_receipt"].get("invalid") == 0, live_phase

        ingest = ingest_drive_corpus_artifacts(
            [self.sample_corpus()],
            ledger_path=str(CORPUS_LEDGER_PATH),
        ).to_dict()
        assert ingest["accepted_blocks"] >= 3, ingest
        assert ingest["replay_receipt"].get("invalid") == 0, ingest

        corpus_ledger = json.loads(CORPUS_LEDGER_PATH.read_text(encoding="utf-8"))
        blocks = [block["payload"] for block in corpus_ledger["blocks"]]
        goal = OperatorSelectionGoal(
            intent="explain a technical alignment claim with harmonic recursive style and process audit",
            preferred_domains=["LOGIC", "STYLE", "PROCESS"],
            preferred_kinds=["AXIOM", "STYLE_OPERATOR", "WRITING_PROCESS"],
            max_chain_length=4,
            require_logic=True,
            require_style=True,
            require_process=True,
        )
        loop = run_phase_coherent_operator_loop(
            "The system must preserve meaning while changing form.",
            blocks,
            goal,
            live_phase_lock_receipt=live_phase,
            feedback_ledger_path=str(FEEDBACK_LEDGER_PATH),
            loop_ledger_path=str(LOOP_LEDGER_PATH),
            execution_ledger_path=str(EXECUTION_LEDGER_PATH),
        ).to_dict()
        assert loop["external_phase_anchor_used"] is True, loop
        assert loop["status"] == PhaseLoopStatus.EXECUTED.value, loop
        assert loop["execution_receipt"] is not None, loop
        assert loop["execution_receipt"]["replay_receipt"].get("invalid") == 0, loop
        assert loop["feedback_replay_receipt"].get("invalid") == 0, loop
        assert loop["loop_replay_receipt"].get("invalid") == 0, loop
        self.record("realtime_phase_bound_operator_loop", True, "Realtime phase anchor binds directly into operator loop and replays.", {"live_phase": live_phase, "ingest": ingest, "loop": loop})

    def run_all(self) -> Dict[str, Any]:
        for name, fn in [
            ("realtime_phase_certification_runner", self.test_realtime_phase_certification_runner),
            ("realtime_phase_bound_operator_loop", self.test_realtime_phase_bound_operator_loop),
        ]:
            self.case(name, fn)
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        report = {
            "certification": "HHS_BACKEND_FINAL_CERTIFICATION_V1",
            "all_ok": failed == 0,
            "status": "CERTIFIED_BACKEND_READY_FOR_GUI" if failed == 0 else "BACKEND_FINAL_CERTIFICATION_FAILED",
            "passed": passed,
            "failed": failed,
            "gui_readiness": {
                "backend_phase_lock": failed == 0,
                "operator_loop_bound_to_realtime_phase": failed == 0,
                "replay_ledgers_valid": failed == 0,
                "recommended_next_layer": "GUI_DESIGN",
            },
            "results": [r.to_dict() for r in self.results],
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return report


def main() -> None:
    report = HHSBackendFinalCertificationV1().run_all()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

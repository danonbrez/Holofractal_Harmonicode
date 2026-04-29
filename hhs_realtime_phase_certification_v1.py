"""
hhs_realtime_phase_certification_v1.py

End-to-end certification for live multimodal phase integration.

Certifies:
1. mandatory AUDIO/HARMONICODE/XYZW/HASH72 witnesses lock phase
2. missing mandatory witnesses fail closed
3. locked witness packets feed CrossModalShellGateV1 and commit state
4. shell and phase ledgers replay with invalid == 0

Run:
    python hhs_realtime_phase_certification_v1.py

Output:
    data/runtime/hhs_realtime_phase_certification_v1_report.json
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List
import json
import traceback

from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path
from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1
from hhs_runtime.hhs_cross_modal_shell_gate_v1 import CrossModalShellGateV1, ShellGateStatus
from hhs_runtime.hhs_realtime_multimodal_phase_integration_v1 import (
    LiveWitnessStatus,
    lock_live_multimodal_phase,
)


REPORT_PATH = runtime_artifact_path("hhs_realtime_phase_certification_v1_report.json")


@dataclass
class CertificationResult:
    name: str
    passed: bool
    detail: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RealtimePhaseCertificationV1:
    def __init__(self) -> None:
        self.results: List[CertificationResult] = []

    def record(self, name: str, passed: bool, detail: str, payload: Dict[str, Any] | None = None) -> None:
        self.results.append(CertificationResult(name, passed, detail, payload or {}))

    def case(self, name: str, fn: Callable[[], None]) -> None:
        try:
            fn()
        except AssertionError as exc:
            self.record(name, False, str(exc), {"traceback": traceback.format_exc()})
        except Exception as exc:
            self.record(name, False, f"Unexpected exception: {type(exc).__name__}: {exc}", {"traceback": traceback.format_exc()})

    @staticmethod
    def base_observations(observed_at: int = 1_000_000_000) -> List[Dict[str, Any]]:
        return [
            {"modality": "AUDIO", "source_id": "audio_frame_0", "observed_at_ns": observed_at, "payload": {"rms": "1/8", "spectral_centroid": 432, "frame_hash": "audio_demo"}},
            {"modality": "HARMONICODE", "source_id": "kernel_phase", "observed_at_ns": observed_at, "payload": {"u72": True, "theta15": True, "omega": True}},
            {"modality": "XYZW", "source_id": "xyzw_algebra", "observed_at_ns": observed_at, "payload": {"xy": 1, "yx": -1, "zw": 1, "wz": -1}},
            {"modality": "HASH72", "source_id": "hash72_commit", "observed_at_ns": observed_at, "payload": {"commitment": "H72-DEMO"}},
            {"modality": "TEXT", "source_id": "text_support", "observed_at_ns": observed_at, "payload": {"intent": "supporting witness"}},
        ]

    def test_phase_lock_with_mandatory_witnesses(self) -> None:
        patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "phase_locked_state"}}
        receipt = lock_live_multimodal_phase(
            self.base_observations(),
            state_patch=patch,
            ledger_path=str(runtime_artifact_path("hhs_realtime_phase_lock_cert_ok.json")),
        ).to_dict()
        assert receipt["status"] == LiveWitnessStatus.LOCKED.value, receipt
        assert receipt["mandatory_present"] is True, receipt
        assert receipt["temporal_ok"] is True, receipt
        assert receipt["phase_locked"] is True, receipt
        assert receipt["replay_receipt"].get("invalid") == 0, receipt
        assert len(receipt["shell_modality_patches"]) >= 4, receipt
        self.record("phase_lock_with_mandatory_witnesses", True, "Mandatory witnesses lock phase and replay.", receipt)

    def test_missing_mandatory_witness_fails_closed(self) -> None:
        patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "invalid_missing_audio"}}
        observations = [o for o in self.base_observations() if o["modality"] != "AUDIO"]
        receipt = lock_live_multimodal_phase(
            observations,
            state_patch=patch,
            ledger_path=str(runtime_artifact_path("hhs_realtime_phase_lock_cert_missing.json")),
        ).to_dict()
        assert receipt["status"] == LiveWitnessStatus.INCOMPLETE.value, receipt
        assert receipt["mandatory_present"] is False, receipt
        assert "AUDIO" in receipt["missing_mandatory"], receipt
        assert receipt["shell_modality_patches"] == [], receipt
        assert receipt["replay_receipt"].get("invalid") == 0, receipt
        self.record("missing_mandatory_witness_fails_closed", True, "Missing mandatory witness emits no shell patches.", receipt)

    def test_locked_witnesses_commit_through_shell(self) -> None:
        patch = {"op": "SET", "path": "runtime.intent", "value": {"next": "phase_locked_state"}}
        phase_receipt = lock_live_multimodal_phase(
            self.base_observations(),
            state_patch=patch,
            ledger_path=str(runtime_artifact_path("hhs_realtime_phase_shell_phase.json")),
        ).to_dict()
        assert phase_receipt["status"] == LiveWitnessStatus.LOCKED.value, phase_receipt
        state_layer = HHSStateLayerV1(initial_state={"runtime": {}})
        gate = CrossModalShellGateV1(state_layer=state_layer, ledger_path=str(runtime_artifact_path("hhs_realtime_phase_shell_commit.json")))
        shell = gate.propose_and_commit(phase_receipt["shell_modality_patches"]).to_dict()
        assert shell["status"] == ShellGateStatus.COMMITTED.value, shell
        assert shell["state_result"] and shell["state_result"].get("ok") is True, shell
        assert shell["replay_receipt"].get("invalid") == 0, shell
        assert state_layer.snapshot()["state"]["runtime"]["intent"]["next"] == "phase_locked_state"
        self.record("locked_witnesses_commit_through_shell", True, "Live phase witness packets commit through shell gate.", {"phase": phase_receipt, "shell": shell})

    def run_all(self) -> Dict[str, Any]:
        tests = [
            ("phase_lock_with_mandatory_witnesses", self.test_phase_lock_with_mandatory_witnesses),
            ("missing_mandatory_witness_fails_closed", self.test_missing_mandatory_witness_fails_closed),
            ("locked_witnesses_commit_through_shell", self.test_locked_witnesses_commit_through_shell),
        ]
        for name, fn in tests:
            self.case(name, fn)
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        report = {
            "certification": "HHS_REALTIME_MULTIMODAL_PHASE_INTEGRATION_V1",
            "all_ok": failed == 0,
            "status": "CERTIFIED_REALTIME_PHASE_LOCKED" if failed == 0 else "REALTIME_PHASE_CERTIFICATION_FAILED",
            "passed": passed,
            "failed": failed,
            "results": [r.to_dict() for r in self.results],
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return report


def main() -> None:
    report = RealtimePhaseCertificationV1().run_all()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

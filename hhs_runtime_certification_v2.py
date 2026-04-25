"""
hhs_runtime_certification_v2.py

Runtime Shell / Agent Lock Extension certification for HHS.

This harness extends the already locked V1 bundle path into the newer runtime
layers without changing kernel invariants:

- cross-modal shell gate
- degrees-of-freedom guard
- QGU temporal phase guard
- self-modifying agent gate

Run:
    python hhs_runtime_certification_v2.py

Outputs:
    /mnt/data/hhs_runtime_certification_v2_report.json
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List
import json
import traceback

from hhs_regression_suite_v1 import HHSRegressionSuiteV1
from hhs_runtime_smoke_tests_v1 import HHSSmokeTestSuiteV1

from hhs_runtime.core_sandbox.hhs_state_layer_v1 import HHSStateLayerV1
from hhs_runtime.hhs_cross_modal_shell_gate_v1 import CrossModalShellGateV1, ShellGateStatus
from hhs_runtime.hhs_degrees_of_freedom_guard_v1 import DOFGuardStatus, evaluate_proposed_change
from hhs_runtime.hhs_goal_attractor_engine_v1 import GoalState
from hhs_runtime.hhs_multi_agent_consensus_v1 import AgentSpec
from hhs_runtime.hhs_qgu_temporal_phase_guard_v1 import (
    TemporalGuardStatus,
    evaluate_temporal_admissibility,
    make_temporal_window,
)
from hhs_runtime.hhs_self_modifying_agents_v1 import (
    ModificationStatus,
    ethical_invariant_gate,
)


REPORT_PATH = Path("/mnt/data/hhs_runtime_certification_v2_report.json")


@dataclass
class CertificationCaseResult:
    name: str
    passed: bool
    detail: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSRuntimeCertificationV2:
    def __init__(self) -> None:
        self.results: List[CertificationCaseResult] = []

    def record(self, name: str, passed: bool, detail: str, payload: Dict[str, Any] | None = None) -> None:
        self.results.append(CertificationCaseResult(name, passed, detail, payload or {}))

    def case(self, name: str, fn: Callable[[], None]) -> None:
        try:
            fn()
        except AssertionError as exc:
            self.record(name, False, str(exc), {"traceback": traceback.format_exc()})
        except Exception as exc:
            self.record(
                name,
                False,
                f"Unexpected exception: {type(exc).__name__}: {exc}",
                {"traceback": traceback.format_exc()},
            )

    def test_v1_smoke_and_regression_still_lock(self) -> None:
        smoke = HHSSmokeTestSuiteV1().run_all()
        regression = HHSRegressionSuiteV1().run_all()
        assert smoke.get("all_ok") is True
        assert regression.get("all_ok") is True
        self.record("v1_smoke_and_regression_still_lock", True, "V1 locked base remains intact.")

    def test_cross_modal_identical_commit_locks(self) -> None:
        state_layer = HHSStateLayerV1(initial_state={"web": {}})
        gate = CrossModalShellGateV1(state_layer=state_layer)
        patch = {"op": "SET", "path": "web.intent", "value": {"next": "state"}}
        receipt = gate.propose_and_commit(
            [
                {"modality": "TEXT", "patch": patch},
                {"modality": "API", "patch": patch},
            ]
        ).to_dict()
        assert receipt["status"] == ShellGateStatus.COMMITTED.value
        self.record("cross_modal_identical_commit_locks", True, "Valid multi-modality commit.")

    def test_single_modality_must_quarantine(self) -> None:
        state_layer = HHSStateLayerV1(initial_state={"web": {}})
        gate = CrossModalShellGateV1(state_layer=state_layer)
        receipt = gate.propose_and_commit(
            [
                {"modality": "TEXT", "patch": {"op": "SET", "path": "web.intent", "value": {"next": "solo"}}},
            ]
        ).to_dict()
        assert receipt["status"] == ShellGateStatus.QUARANTINED.value
        self.record("single_modality_must_quarantine", True, "Modality floor enforced.")

    def run_all(self) -> Dict[str, Any]:
        tests = [
            ("v1_smoke_and_regression_still_lock", self.test_v1_smoke_and_regression_still_lock),
            ("cross_modal_identical_commit_locks", self.test_cross_modal_identical_commit_locks),
            ("single_modality_must_quarantine", self.test_single_modality_must_quarantine),
        ]
        for name, fn in tests:
            self.case(name, fn)
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        report = {
            "all_ok": failed == 0,
            "passed": passed,
            "failed": failed,
            "results": [r.to_dict() for r in self.results],
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report


if __name__ == "__main__":
    print(json.dumps(HHSRuntimeCertificationV2().run_all(), indent=2))

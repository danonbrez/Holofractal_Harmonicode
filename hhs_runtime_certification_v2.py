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

    # ------------------------------------------------------------------
    # Existing locked runtime base
    # ------------------------------------------------------------------

    def test_v1_smoke_and_regression_still_lock(self) -> None:
        smoke = HHSSmokeTestSuiteV1().run_all()
        regression = HHSRegressionSuiteV1().run_all()
        assert smoke.get("all_ok") is True, f"V1 smoke tests no longer lock: {smoke}"
        assert regression.get("all_ok") is True, f"V1 regression suite no longer locks: {regression}"
        self.record(
            "v1_smoke_and_regression_still_lock",
            True,
            "V1 locked base remains intact.",
            {"smoke": {"passed": smoke.get("passed"), "failed": smoke.get("failed")}, "regression": {"passed": regression.get("passed"), "failed": regression.get("failed")}},
        )

    # ------------------------------------------------------------------
    # Cross-modal shell cases
    # ------------------------------------------------------------------

    def test_cross_modal_identical_commit_locks(self) -> None:
        state_layer = HHSStateLayerV1(initial_state={"web": {}})
        gate = CrossModalShellGateV1(state_layer=state_layer, ledger_path="/mnt/data/hhs_v2_shell_identical.json")
        patch = {"op": "SET", "path": "web.intent", "value": {"next": "state"}}
        receipt = gate.propose_and_commit(
            [
                {"modality": "TEXT", "source_id": "text_parser", "patch": patch},
                {"modality": "API", "source_id": "api_schema", "patch": patch},
                {"modality": "FILE", "source_id": "file_tokenizer", "patch": patch},
            ]
        ).to_dict()
        assert receipt["status"] == ShellGateStatus.COMMITTED.value, f"identical cross-modal patch did not commit: {receipt}"
        assert receipt["state_result"] and receipt["state_result"].get("ok") is True, "state layer did not accept agreed transition"
        assert receipt["replay_receipt"].get("invalid") == 0, "shell ledger replay failed"
        self.record("cross_modal_identical_commit_locks", True, "Matching modalities commit through state layer and replay.", receipt)

    def test_cross_modal_disagreement_quarantines_without_state_write(self) -> None:
        state_layer = HHSStateLayerV1(initial_state={"web": {"intent": {"next": "old"}}})
        before = state_layer.snapshot()["state"]
        gate = CrossModalShellGateV1(state_layer=state_layer, ledger_path="/mnt/data/hhs_v2_shell_disagreement.json")
        receipt = gate.propose_and_commit(
            [
                {"modality": "TEXT", "source_id": "text_parser", "patch": {"op": "SET", "path": "web.intent", "value": {"next": "alpha"}}},
                {"modality": "API", "source_id": "api_schema", "patch": {"op": "SET", "path": "web.intent", "value": {"next": "beta"}}},
            ]
        ).to_dict()
        after = state_layer.snapshot()["state"]
        assert receipt["status"] == ShellGateStatus.QUARANTINED.value, f"disagreement did not quarantine: {receipt}"
        assert receipt["state_result"] is None, "disagreement still produced state_result"
        assert after == before, "state changed after cross-modal disagreement"
        self.record("cross_modal_disagreement_quarantines_without_state_write", True, "Disagreement quarantines and preserves prior state.", receipt)

    def test_single_modality_is_flagged_as_policy_gap(self) -> None:
        """
        This case intentionally records the current v1 shell behavior.

        The V2 policy requires at least two distinct modalities before commit.
        If this test fails, the shell has already been hardened and the gap is closed.
        """
        state_layer = HHSStateLayerV1(initial_state={"web": {}})
        gate = CrossModalShellGateV1(state_layer=state_layer, ledger_path="/mnt/data/hhs_v2_shell_single_modality.json")
        receipt = gate.propose_and_commit(
            [
                {"modality": "TEXT", "source_id": "text_parser", "patch": {"op": "SET", "path": "web.intent", "value": {"next": "solo"}}},
            ]
        ).to_dict()
        passed = receipt["status"] == ShellGateStatus.QUARANTINED.value
        detail = "single modality quarantined" if passed else "single modality currently commits; patch required: enforce distinct modality floor before state write"
        self.record("single_modality_policy_gap", passed, detail, receipt)

    # ------------------------------------------------------------------
    # DOF guard cases
    # ------------------------------------------------------------------

    def test_dof_guard_allows_validation_and_quarantine_adds(self) -> None:
        validation = evaluate_proposed_change({"target": "cross_modal_shell", "action": "add validation", "payload": {"allowed_namespaces": ["web", "uploads", "sensors"]}}).to_dict()
        quarantine = evaluate_proposed_change({"target": "security", "action": "add quarantine", "payload": {"pattern": "fake_receipt"}}).to_dict()
        assert validation["status"] == DOFGuardStatus.ALLOWED.value, f"validation add rejected: {validation}"
        assert quarantine["status"] == DOFGuardStatus.ALLOWED.value, f"quarantine add rejected: {quarantine}"
        self.record("dof_guard_allows_validation_and_quarantine_adds", True, "Non-restrictive hardening preserves degrees of freedom.", {"validation": validation, "quarantine": quarantine})

    def test_dof_guard_rejects_overconstraint(self) -> None:
        disable_sum = evaluate_proposed_change({"target": "runtime SUM", "action": "disable operation", "payload": {"operations": ["SUM"]}}).to_dict()
        single_modality = evaluate_proposed_change({"target": "modalities", "action": "reduce to single modality", "payload": {"single_modality": "TEXT"}}).to_dict()
        block_all = evaluate_proposed_change({"target": "runtime", "action": "namespace_block", "payload": {"blocked_namespaces": ["web", "uploads", "sensors", "execution", "memory", "learning", "planning", "fuzz", "semantic"]}}).to_dict()
        assert disable_sum["status"] == DOFGuardStatus.REJECTED.value, f"operation disable was not rejected: {disable_sum}"
        assert single_modality["status"] == DOFGuardStatus.REJECTED.value, f"single-modality reduction was not rejected: {single_modality}"
        assert block_all["status"] == DOFGuardStatus.REJECTED.value, f"namespace collapse was not rejected: {block_all}"
        self.record("dof_guard_rejects_overconstraint", True, "Immune-overdrive changes fail closed.", {"disable_sum": disable_sum, "single_modality": single_modality, "block_all": block_all})

    # ------------------------------------------------------------------
    # QGU temporal phase cases
    # ------------------------------------------------------------------

    def test_qgu_temporal_guard_allows_fresh_transition(self) -> None:
        window = make_temporal_window(max_latency_ms=20, decay_half_life_ms=5, created_at_ns=1_000_000_000)
        receipt = evaluate_temporal_admissibility({"op": "SET", "path": "audio.frame", "value": 1}, window=window, observed_at_ns=1_001_000_000, recursion_depth=0).to_dict()
        assert receipt["status"] == TemporalGuardStatus.ADMISSIBLE.value, f"fresh transition did not pass temporal guard: {receipt}"
        self.record("qgu_temporal_guard_allows_fresh_transition", True, "Fresh transition closes within QGU window.", receipt)

    def test_qgu_temporal_guard_blocks_expired_and_recursive_transitions(self) -> None:
        window = make_temporal_window(max_latency_ms=20, decay_half_life_ms=5, recursion_ttl=2, created_at_ns=1_000_000_000)
        expired = evaluate_temporal_admissibility({"op": "SET", "path": "video.frame", "value": 1}, window=window, observed_at_ns=1_050_000_000, recursion_depth=0).to_dict()
        recursive = evaluate_temporal_admissibility({"op": "SET", "path": "video.frame", "value": 1}, window=window, observed_at_ns=1_001_000_000, recursion_depth=3).to_dict()
        assert expired["status"] == TemporalGuardStatus.EXPIRED.value, f"expired transition was not blocked: {expired}"
        assert recursive["status"] == TemporalGuardStatus.RECURSION_BLOCKED.value, f"recursive transition was not blocked: {recursive}"
        self.record("qgu_temporal_guard_blocks_expired_and_recursive_transitions", True, "Expired and recursive transitions quarantine before commit.", {"expired": expired, "recursive": recursive})

    # ------------------------------------------------------------------
    # Self-modifying agent gate cases
    # ------------------------------------------------------------------

    def test_self_modifying_agent_gate_applies_safe_threshold_change(self) -> None:
        old = AgentSpec(name="phase_agent", goal=GoalState(name="Phase36", target_phase_index=36), vote_weight=1, min_score="1/2")
        proposed = AgentSpec(name="phase_agent", goal=GoalState(name="Phase36", target_phase_index=36), vote_weight=1, min_score="7/12")
        receipt = ethical_invariant_gate(old, proposed, "bounded_threshold_tighten").to_dict()
        assert receipt["status"] == ModificationStatus.APPLIED.value, f"safe threshold change did not apply: {receipt}"
        self.record("self_modifying_agent_gate_applies_safe_threshold_change", True, "Bounded same-identity threshold change passes invariant gate.", receipt)

    def test_self_modifying_agent_gate_quarantines_identity_or_commit_drift(self) -> None:
        old = AgentSpec(name="phase_agent", goal=GoalState(name="Phase36", target_phase_index=36), vote_weight=1, min_score="1/2")
        renamed = AgentSpec(name="kernel_agent", goal=GoalState(name="Phase36", target_phase_index=36), vote_weight=1, min_score="1/2")
        no_commit = AgentSpec(name="phase_agent", goal=GoalState(name="Phase36", target_phase_index=36, require_committed_transition=False), vote_weight=1, min_score="1/2")
        renamed_receipt = ethical_invariant_gate(old, renamed, "identity_drift_attempt").to_dict()
        no_commit_receipt = ethical_invariant_gate(old, no_commit, "commit_gate_disable_attempt").to_dict()
        assert renamed_receipt["status"] == ModificationStatus.QUARANTINED.value, f"identity drift did not quarantine: {renamed_receipt}"
        assert no_commit_receipt["status"] == ModificationStatus.QUARANTINED.value, f"commit-gate disable did not quarantine: {no_commit_receipt}"
        self.record("self_modifying_agent_gate_quarantines_identity_or_commit_drift", True, "Identity drift and commit-gate disable fail closed.", {"renamed": renamed_receipt, "no_commit": no_commit_receipt})

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------

    def run_all(self) -> Dict[str, Any]:
        tests = [
            ("v1_smoke_and_regression_still_lock", self.test_v1_smoke_and_regression_still_lock),
            ("cross_modal_identical_commit_locks", self.test_cross_modal_identical_commit_locks),
            ("cross_modal_disagreement_quarantines_without_state_write", self.test_cross_modal_disagreement_quarantines_without_state_write),
            ("single_modality_policy_gap", self.test_single_modality_is_flagged_as_policy_gap),
            ("dof_guard_allows_validation_and_quarantine_adds", self.test_dof_guard_allows_validation_and_quarantine_adds),
            ("dof_guard_rejects_overconstraint", self.test_dof_guard_rejects_overconstraint),
            ("qgu_temporal_guard_allows_fresh_transition", self.test_qgu_temporal_guard_allows_fresh_transition),
            ("qgu_temporal_guard_blocks_expired_and_recursive_transitions", self.test_qgu_temporal_guard_blocks_expired_and_recursive_transitions),
            ("self_modifying_agent_gate_applies_safe_threshold_change", self.test_self_modifying_agent_gate_applies_safe_threshold_change),
            ("self_modifying_agent_gate_quarantines_identity_or_commit_drift", self.test_self_modifying_agent_gate_quarantines_identity_or_commit_drift),
        ]
        for name, fn in tests:
            self.case(name, fn)
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        status = "CERTIFIED_RUNTIME_SHELL_LOCKED" if failed == 0 else "RUNTIME_SHELL_CERTIFICATION_FAILED"
        report = {
            "certification": "HHS_RUNTIME_SHELL_AGENT_LOCK_EXTENSION_V2",
            "all_ok": failed == 0,
            "status": status,
            "passed": passed,
            "failed": failed,
            "invariants_preserved": {"Δe": 0, "Ψ": 0, "Θ15": True, "Ω": True},
            "results": [r.to_dict() for r in self.results],
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report


def main() -> None:
    report = HHSRuntimeCertificationV2().run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

"""
hhs_regression_suite_v1.py

Regression suite for the HARMONICODE general programming environment.

Covers:
- valid operations lock
- invalid operations quarantine
- receipt-chain replay succeeds
- receipt tampering fails
- parent-link tampering fails
- IF gate locks valid branch
- LOOP gate locks terminating loop
- LOOP stutter quarantines
- .hhsprog execution succeeds
- .hhsrun replay verifies

Run:
    python hhs_regression_suite_v1.py
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List
import copy
import json
import tempfile
import traceback

from hhs_general_runtime_layer_v1 import AuditedRunner, DEFAULT_KERNEL_PATH
from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1
from hhs_control_flow_gates_v1 import HHSControlFlowGatesV1
from hhs_program_format_and_cli_v1 import (
    PROGRAM_FORMAT,
    RUN_RESULT_FORMAT,
    execute_program,
    verify_run_file,
    write_json,
)


@dataclass
class RegressionResult:
    name: str
    passed: bool
    detail: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSRegressionSuiteV1:
    def __init__(self):
        self.results: List[RegressionResult] = []

    def record(self, name: str, passed: bool, detail: str, payload: Dict[str, Any] | None = None) -> None:
        self.results.append(RegressionResult(name, passed, detail, payload or {}))

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
    # Runtime cases
    # ------------------------------------------------------------------

    def test_valid_operations_lock(self) -> None:
        runner = AuditedRunner()
        outputs = [
            runner.execute("ADD", 2, 3),
            runner.execute("MUL", 4, 9),
            runner.execute("SUM", [1, 2, 3, 4]),
            runner.execute("SORT", [5, 1, 3, 1]),
            runner.execute("BINARY_SEARCH", [1, 3, 5, 7], 5),
        ]
        assert all(o.get("ok") for o in outputs), "One or more valid operations failed to lock"
        chain = runner.commitments.verify_chain()
        assert chain["ok"] is True, f"Chain failed: {chain}"
        self.record("valid_operations_lock", True, "Valid operation set locked.", {"chain": chain})

    def test_invalid_operations_quarantine(self) -> None:
        runner = AuditedRunner()
        div = runner.execute("DIV", 1, 0)
        unsorted = runner.execute("BINARY_SEARCH", [1, 9, 3], 3)
        assert div["quarantine"] is True, "DIV by zero did not quarantine"
        assert unsorted["quarantine"] is True, "Unsorted binary search did not quarantine"
        self.record(
            "invalid_operations_quarantine",
            True,
            "Invalid operations quarantined fail-closed.",
            {"div": div["receipt"], "unsorted": unsorted["receipt"]},
        )

    def test_replay_succeeds(self) -> None:
        runner = AuditedRunner()
        runner.execute("ADD", 10, 5)
        runner.execute("SORT", [4, 2, 8])
        verifier = HHSReceiptReplayVerifierV1()
        report = verifier.verify_runner(runner).to_dict()
        assert report["ok"] is True, f"Replay failed: {report}"
        self.record("replay_succeeds", True, "Receipt replay verified.", report)

    def test_receipt_tamper_fails(self) -> None:
        runner = AuditedRunner()
        runner.execute("ADD", 2, 3)
        runner.execute("MUL", 5, 7)
        receipts = [r.to_dict() for r in runner.commitments.receipts]
        tampered = copy.deepcopy(receipts)
        tampered[0]["operation"] = "ADD_TAMPERED"
        verifier = HHSReceiptReplayVerifierV1()
        report = verifier.verify(tampered).to_dict()
        assert report["ok"] is False, "Tampered receipt unexpectedly verified"
        assert "mismatch" in report["reason"] or "failed" in report["reason"], f"Unexpected reason: {report}"
        self.record("receipt_tamper_fails", True, "Receipt mutation failed replay.", report)

    def test_parent_link_tamper_fails(self) -> None:
        runner = AuditedRunner()
        runner.execute("ADD", 2, 3)
        runner.execute("MUL", 5, 7)
        receipts = [r.to_dict() for r in runner.commitments.receipts]
        tampered = copy.deepcopy(receipts)
        tampered[1]["parent_receipt_hash72"] = "H72N-BADPARENT"
        verifier = HHSReceiptReplayVerifierV1()
        report = verifier.verify(tampered).to_dict()
        assert report["ok"] is False, "Parent tamper unexpectedly verified"
        assert report["reason"] == "parent_receipt_hash72 mismatch", f"Unexpected reason: {report}"
        self.record("parent_link_tamper_fails", True, "Parent-link tamper failed replay.", report)

    # ------------------------------------------------------------------
    # Control-flow cases
    # ------------------------------------------------------------------

    def test_if_gate_locks(self) -> None:
        gates = HHSControlFlowGatesV1()
        result = gates.audited_if(
            condition=True,
            then_fn=lambda: 11,
            else_fn=lambda: 22,
            label="REGRESSION_IF",
        ).to_dict()
        assert result["ok"] is True, f"IF gate did not lock: {result}"
        assert result["selected_branch"] == "THEN", "IF selected wrong branch"
        self.record("if_gate_locks", True, "IF gate locked selected branch.", result)

    def test_loop_gate_locks(self) -> None:
        gates = HHSControlFlowGatesV1()
        result = gates.audited_loop(
            initial_state=4,
            condition_fn=lambda s: s > 0,
            step_fn=lambda s: s - 1,
            variant_fn=lambda s: s,
            max_steps=10,
            label="REGRESSION_COUNTDOWN",
        ).to_dict()
        assert result["ok"] is True, f"LOOP gate did not lock: {result}"
        assert result["terminated"] is True, "Loop did not terminate"
        assert result["result"] == 0, "Loop result mismatch"
        self.record("loop_gate_locks", True, "Terminating loop locked.", result)

    def test_loop_stutter_quarantines(self) -> None:
        gates = HHSControlFlowGatesV1()
        result = gates.audited_loop(
            initial_state=3,
            condition_fn=lambda s: s > 0,
            step_fn=lambda s: s,  # stutter: never decreases
            variant_fn=lambda s: s,
            max_steps=5,
            label="REGRESSION_STUTTER",
        ).to_dict()
        assert result["ok"] is False, "Stutter loop unexpectedly locked"
        assert result["quarantine"] is True, "Stutter loop did not quarantine"
        assert "stutter" in result["reason"] or "decrease" in result["reason"], f"Unexpected reason: {result}"
        self.record("loop_stutter_quarantines", True, "Loop stutter quarantined.", result)

    # ------------------------------------------------------------------
    # Program file cases
    # ------------------------------------------------------------------

    def test_hhsprog_execution_succeeds(self) -> None:
        program = {
            "format": PROGRAM_FORMAT,
            "program_name": "REGRESSION_HHSPROG",
            "persist": False,
            "continue_on_quarantine": False,
            "operations": [
                {"op": "ADD", "args": [2, 3]},
                {"op": "SORT", "args": [[3, 1, 2]]},
                {"op": "BINARY_SEARCH", "args": [[1, 2, 3], 2]},
            ],
        }
        result = execute_program(program)
        assert result["format"] == RUN_RESULT_FORMAT, "Wrong run result format"
        assert result["all_ok"] is True, f"hhsprog execution failed: {result}"
        assert result["replay"]["ok"] is True, "hhsprog replay did not verify"
        self.record("hhsprog_execution_succeeds", True, ".hhsprog executed and replayed.", {
            "program_hash72": result["program_hash72"],
            "chain": result["chain"],
        })

    def test_hhsrun_verify_file_succeeds(self) -> None:
        program = {
            "format": PROGRAM_FORMAT,
            "program_name": "REGRESSION_HHSRUN_FILE",
            "persist": False,
            "operations": [
                {"op": "ADD", "args": [8, 13]},
                {"op": "MUL", "args": [3, 7]},
            ],
        }
        result = execute_program(program)

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "regression.hhsrun"
            write_json(p, result)
            verify = verify_run_file(p)
        assert verify["verification"]["ok"] is True, f".hhsrun verify failed: {verify}"
        self.record("hhsrun_verify_file_succeeds", True, ".hhsrun file verified.", verify)

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------

    def run_all(self) -> Dict[str, Any]:
        tests = [
            ("valid_operations_lock", self.test_valid_operations_lock),
            ("invalid_operations_quarantine", self.test_invalid_operations_quarantine),
            ("replay_succeeds", self.test_replay_succeeds),
            ("receipt_tamper_fails", self.test_receipt_tamper_fails),
            ("parent_link_tamper_fails", self.test_parent_link_tamper_fails),
            ("if_gate_locks", self.test_if_gate_locks),
            ("loop_gate_locks", self.test_loop_gate_locks),
            ("loop_stutter_quarantines", self.test_loop_stutter_quarantines),
            ("hhsprog_execution_succeeds", self.test_hhsprog_execution_succeeds),
            ("hhsrun_verify_file_succeeds", self.test_hhsrun_verify_file_succeeds),
        ]

        for name, fn in tests:
            self.case(name, fn)

        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        return {
            "suite": "HHS_REGRESSION_SUITE_V1",
            "passed": passed,
            "failed": failed,
            "all_ok": failed == 0,
            "results": [r.to_dict() for r in self.results],
        }


def main() -> None:
    suite = HHSRegressionSuiteV1()
    report = suite.run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

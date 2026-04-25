"""
hhs_runtime_smoke_tests_v1.py

Smoke tests for hhs_general_runtime_layer_v1.py.

Purpose
-------
Prove the general runtime wrapper can:
- load the locked kernel
- bind authoritative Hash72
- execute normal operations
- emit locked receipts for valid transitions
- quarantine invalid transitions
- maintain parent_receipt_hash72 continuity

Run:
    python hhs_runtime_smoke_tests_v1.py
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List
import json
import traceback

from hhs_general_runtime_layer_v1 import (
    AuditedRunner,
    DEFAULT_KERNEL_PATH,
)


@dataclass
class SmokeTestResult:
    name: str
    passed: bool
    detail: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSSmokeTestSuiteV1:
    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.kernel_path = Path(kernel_path)
        self.runner = AuditedRunner(self.kernel_path)
        self.results: List[SmokeTestResult] = []

    def record(self, name: str, passed: bool, detail: str, payload: Dict[str, Any] | None = None) -> None:
        self.results.append(
            SmokeTestResult(
                name=name,
                passed=passed,
                detail=detail,
                payload=payload or {},
            )
        )

    def run_case(self, name: str, fn: Callable[[], None]) -> None:
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
    # Tests
    # ------------------------------------------------------------------

    def test_kernel_authority_loaded(self) -> None:
        kernel = self.runner.kernel
        required = [
            "AUTHORITATIVE_TRUST_POLICY_V44",
            "security_hash72_v44",
            "NativeHash72Codec",
            "Manifold9",
            "Tensor",
        ]
        missing = [name for name in required if not hasattr(kernel, name)]
        assert not missing, f"Missing kernel symbols: {missing}"

        policy = getattr(kernel, "AUTHORITATIVE_TRUST_POLICY_V44")
        assert policy.get("authoritative_integrity") == "HASH72", "Kernel integrity policy is not HASH72"
        assert policy.get("forbid_legacy_sha_for_security_or_integrity") is True, (
            "Kernel does not forbid legacy SHA for security/integrity"
        )

        h = self.runner.authority.commit({"smoke": "authority"})
        assert isinstance(h, str) and h.startswith("H72N-"), f"Bad authority hash: {h}"

        self.record(
            "kernel_authority_loaded",
            True,
            "Kernel authority loaded and Hash72 commit returned H72N-*.",
            {"hash72": h, "policy": policy},
        )

    def test_add_locks(self) -> None:
        out = self.runner.execute("ADD", 2, 3)
        assert out["ok"] is True, f"ADD did not lock: {out}"
        assert out["receipt"]["locked"] is True, "ADD receipt not locked"
        assert out["receipt"]["receipt_hash72"].startswith("H72N-"), "Missing receipt hash"
        self.record("add_locks", True, "ADD locked and emitted receipt.", out)

    def test_div_zero_quarantines(self) -> None:
        out = self.runner.execute("DIV", 1, 0)
        assert out["ok"] is False, "DIV by zero unexpectedly passed"
        assert out["quarantine"] is True, "DIV by zero did not quarantine"
        assert out["receipt"]["gate_status"] == "QUARANTINED", "DIV receipt not quarantined"
        self.record("div_zero_quarantines", True, "DIV by zero quarantined fail-closed.", out)

    def test_sort_locks(self) -> None:
        data = [19, 3, 42, 11, 7, 7, 1]
        out = self.runner.execute("SORT", data)
        assert out["ok"] is True, f"SORT did not lock: {out}"
        result = out["result"]
        assert result["order_ok"] is True, "SORT order gate failed"
        assert result["multiset_ok"] is True, "SORT multiset gate failed"
        assert result["mass_ok"] is True, "SORT mass gate failed"
        assert result["shape_ok"] is True, "SORT shape gate failed"
        self.record("sort_locks", True, "SORT locked with order/mass/shape/multiset gates.", out)

    def test_binary_search_found_locks(self) -> None:
        data = [1, 3, 7, 11, 19, 42, 55]
        out = self.runner.execute("BINARY_SEARCH", data, 42)
        assert out["ok"] is True, f"BINARY_SEARCH found did not lock: {out}"
        assert out["result"]["found"] is True, "Target not found"
        assert out["result"]["status"] == "FOUND", "Search status not FOUND"
        assert len(out["result"]["path"]) >= 1, "Search path missing"
        self.record("binary_search_found_locks", True, "BINARY_SEARCH found target and locked.", out)

    def test_binary_search_missing_locks(self) -> None:
        data = [1, 3, 7, 11, 19, 42, 55]
        out = self.runner.execute("BINARY_SEARCH", data, 8)
        assert out["ok"] is True, f"BINARY_SEARCH missing did not lock: {out}"
        assert out["result"]["found"] is False, "Missing target reported found"
        assert out["result"]["status"] == "MISSING_EXCLUSION_COMPLETE", "Missing proof incomplete"
        self.record("binary_search_missing_locks", True, "BINARY_SEARCH missing proof locked.", out)

    def test_binary_search_unsorted_quarantines(self) -> None:
        data = [1, 9, 3, 7]
        out = self.runner.execute("BINARY_SEARCH", data, 7)
        assert out["ok"] is False, "Unsorted binary search unexpectedly passed"
        assert out["quarantine"] is True, "Unsorted binary search did not quarantine"
        assert out["receipt"]["gate_status"] == "QUARANTINED", "Unsorted search receipt not quarantined"
        self.record("binary_search_unsorted_quarantines", True, "Unsorted input quarantined.", out)

    def test_receipt_chain_continuity(self) -> None:
        chain = self.runner.commitments.verify_chain()
        assert chain["ok"] is True, f"Receipt chain failed: {chain}"
        assert chain["count"] == len(self.runner.commitments.receipts), "Receipt count mismatch"
        self.record("receipt_chain_continuity", True, "Parent receipt chain verified.", chain)

    # ------------------------------------------------------------------
    # Runner
    # ------------------------------------------------------------------

    def run_all(self) -> Dict[str, Any]:
        self.run_case("kernel_authority_loaded", self.test_kernel_authority_loaded)
        self.run_case("add_locks", self.test_add_locks)
        self.run_case("div_zero_quarantines", self.test_div_zero_quarantines)
        self.run_case("sort_locks", self.test_sort_locks)
        self.run_case("binary_search_found_locks", self.test_binary_search_found_locks)
        self.run_case("binary_search_missing_locks", self.test_binary_search_missing_locks)
        self.run_case("binary_search_unsorted_quarantines", self.test_binary_search_unsorted_quarantines)
        self.run_case("receipt_chain_continuity", self.test_receipt_chain_continuity)

        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        return {
            "suite": "HHS_RUNTIME_SMOKE_TESTS_V1",
            "kernel_path": str(self.kernel_path),
            "passed": passed,
            "failed": failed,
            "all_ok": failed == 0,
            "results": [r.to_dict() for r in self.results],
        }


def main() -> None:
    suite = HHSSmokeTestSuiteV1()
    report = suite.run_all()
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if not report["all_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

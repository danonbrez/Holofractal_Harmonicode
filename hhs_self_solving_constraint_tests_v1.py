"""
hhs_self_solving_constraint_tests_v1.py

Focused tests for the self-solving constraint modules.

Run:
    python hhs_self_solving_constraint_tests_v1.py
"""

from __future__ import annotations

import json

from hhs_self_solving_constraint_modules_v1 import HHSSelfSolvingConstraintModulesV1


def test_scaled_lock():
    solver = HHSSelfSolvingConstraintModulesV1()
    out = solver.enforce_bilateral_fixed_point(5, 5, 5).to_dict()
    assert out["ok"] is True, f"scaled lock failed: {out}"
    assert out["witness"]["scale"] == 5, "scale not preserved"


def test_unit_lock():
    solver = HHSSelfSolvingConstraintModulesV1()
    out = solver.enforce_bilateral_fixed_point(1, 1, 1).to_dict()
    assert out["ok"] is True, f"unit lock failed: {out}"
    assert out["witness"]["unit_lock"] is True, "unit flag not set"


def test_mismatch_quarantine():
    solver = HHSSelfSolvingConstraintModulesV1()
    out = solver.enforce_bilateral_fixed_point(5, 1, 5).to_dict()
    assert out["ok"] is False, "mismatch did not quarantine"
    assert out["quarantine"] is True, "quarantine flag not set"


def main() -> None:
    results = []
    for name, fn in [
        ("scaled_lock", test_scaled_lock),
        ("unit_lock", test_unit_lock),
        ("mismatch_quarantine", test_mismatch_quarantine),
    ]:
        try:
            fn()
            results.append({"name": name, "passed": True})
        except AssertionError as exc:
            results.append({"name": name, "passed": False, "error": str(exc)})
    report = {"suite": "HHS_SELF_SOLVING_CONSTRAINT_TESTS_V1", "results": results}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not all(r.get("passed") for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

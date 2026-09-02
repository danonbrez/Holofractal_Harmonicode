#!/usr/bin/env python3
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
import sys

from hhs_runtime.hhs_pass219_dynamic_paradox_phase_cycle_v1 import (
    canonical_random_guess_paradox,
    exact_work_model,
    h36_identity_witness,
)


CASES = (1, 64, 1024)


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "artifacts/pass219/i147-dynamic-paradox/benchmark.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    witness = canonical_random_guess_paradox()
    assert witness.object_has_fixed_point is False
    assert witness.trajectory == (
        Fraction(0, 1),
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(1, 4),
    )

    h36 = h36_identity_witness()
    assert h36["identity_equal"] is True
    assert h36["h36_value"] == 36

    cases = []
    baseline = 0
    optimized = 0
    saved = 0
    for count in CASES:
        work = dict(exact_work_model(evaluation_count=count))
        assert work["optimized_total_work"] < work["baseline_total_work"]
        baseline += int(work["baseline_total_work"])
        optimized += int(work["optimized_total_work"])
        saved += int(work["exact_work_saved"])
        cases.append(work)

    receipt = {
        "schema": "HHS_PASS219_I147_DYNAMIC_PARADOX_BENCHMARK_V1",
        "metric_class": "EXACT_LOGICAL_COMPARISON_WORK",
        "timing_is_canonical": False,
        "object_level": {
            "fixed_point_valid_option_count": 0,
            "trajectory": [str(v) for v in witness.trajectory],
            "preperiod": witness.preperiod,
            "period": witness.period,
        },
        "meta_level": {
            "empty_object_valid_set": witness.meta_empty_valid_set,
            "probability": str(witness.meta_probability),
            "promotes_object_option": False,
        },
        "h36": h36,
        "cases": cases,
        "aggregate": {
            "baseline_total_work": baseline,
            "optimized_total_work": optimized,
            "exact_work_saved": saved,
            "reduction_permille_floor": (saved * 1000) // baseline,
        },
        "authority": {
            "canonical_mutation_authority_changed": False,
            "hash72_authority_changed": False,
            "hash216_authority_changed": False,
        },
        "result": "PASS",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

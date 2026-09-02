#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    PCM64_NOISE_FLOOR,
    PCM64_SATURATION_CEILING,
    PCM64_ZERO_CROSSING,
    RAW_BITS,
    exact_serialization_work_model,
    pipeline,
)

CASES = (1, 64, 1024)


def pattern() -> str:
    return "".join("1" if ((i * 17 + 3) % 11) < 5 else "0" for i in range(RAW_BITS))


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "artifacts/pass219/i148-raw5184-audio/benchmark.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    hydration = pipeline(pattern())
    assert len(hydration.pcm64_bits) == 81
    assert len(hydration.quads) == 20
    for quad in hydration.quads:
        q = quad.stereo_ternary
        assert q.role_pcm64 == (
            PCM64_NOISE_FLOOR,
            PCM64_ZERO_CROSSING,
            PCM64_SATURATION_CEILING,
        )
        assert q.quotient_identity == (1, 1, 1)
        assert q.quotient_phase72 == (0, 0, 0)
        assert q.center_zero_over_zero_u0_mod_u72
        assert q.center_xy_sum_over_zw_sum_u0
        assert q.center_mono_xy_sum_colon_zw_sum
        assert not q.scalar_projection_runtime_authority

    cases = []
    baseline = fused = saved = 0
    for count in CASES:
        work = dict(exact_serialization_work_model(count))
        baseline += int(work["baseline_total_work"])
        fused += int(work["fused_total_work"])
        saved += int(work["exact_work_saved"])
        cases.append(work)

    receipt = {
        "schema": "HHS_PASS219_I148_RAW5184_AUDIO_BENCHMARK_V1",
        "metric_class": "EXACT_SERIALIZATION_LOGICAL_WORK",
        "timing_is_canonical": False,
        "raw_bits": 5184,
        "raw_bytes": 648,
        "pcm64_samples": 81,
        "phase_quads": 20,
        "mono_lanes": {
            "left": ["yx", "x+y", "xy"],
            "right": ["wz", "z+w", "zw"],
            "center_relation": "x+y:z+w",
        },
        "ternary_pcm64": {
            "roles": [-1, 0, 1],
            "amplitudes": [
                PCM64_NOISE_FLOOR,
                PCM64_ZERO_CROSSING,
                PCM64_SATURATION_CEILING,
            ],
            "semantics": [
                "binary_5184_digital_noise_floor",
                "zero_sum_crossing",
                "sample_saturation_ceiling",
            ],
        },
        "typed_u72_quotient": {
            "numerator": [-1, 0, 1],
            "denominator": [-1, 0, 1],
            "quotient": [1, 1, 1],
            "quotient_phase72": [0, 0, 0],
            "center": "0/0=u^0 mod(u^72)=1",
            "center_symbolic_relation": "(x+y)/(z+w)=u^0",
            "scalar_projection_runtime_authority": False,
            "scalar_division_attempted": False,
        },
        "cases": cases,
        "aggregate": {
            "baseline_total_work": baseline,
            "fused_total_work": fused,
            "exact_work_saved": saved,
            "reduction_permille_floor": (saved * 1000) // baseline,
        },
        "authority": {
            "canonical_mutation_authority_changed": False,
            "hash72_authority_changed": False,
            "hash216_authority_changed": False,
            "floating_point_authority": False,
        },
        "result": "PASS",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

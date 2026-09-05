#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_v1 import (
    PCM64_NOISE_FLOOR,
    PCM64_SATURATION_CEILING,
    PCM64_ZERO_CROSSING,
    SINE_Q62,
    SINE_Q62_SCALE,
    exact_serialization_work_model,
    pipeline,
)


CASES = (1, 64, 1024)


def fixture_bits() -> str:
    return "".join(
        "1" if ((i * 13 + 7) % 17) < 8 else "0"
        for i in range(5184)
    )


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "artifacts/pass219/i148-raw5184-audio/benchmark.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    hydration = pipeline(fixture_bits())
    assert len(hydration.pcm64_bits) == 81
    assert len(hydration.quads) == 20
    assert len(hydration.sine_pcm64) == 160
    assert SINE_Q62[0] == 0
    assert SINE_Q62[18] == SINE_Q62_SCALE
    assert SINE_Q62[36] == 0
    assert SINE_Q62[54] == -SINE_Q62_SCALE

    for quad in hydration.quads:
        t = quad.stereo_ternary
        assert t.numerator_roles == (-1, 0, 1)
        assert t.denominator_roles == (-1, 0, 1)
        assert t.quotient_identity == (1, 1, 1)
        assert t.role_pcm64 == (
            PCM64_NOISE_FLOOR,
            PCM64_ZERO_CROSSING,
            PCM64_SATURATION_CEILING,
        )
        assert t.center_zero_over_zero_u0_mod_u72 is True
        assert t.center_xy_sum_over_zw_sum_u0 is True
        assert t.scalar_projection_runtime_authority is False

    cases = []
    baseline = 0
    fused = 0
    saved = 0
    for count in CASES:
        work = dict(exact_serialization_work_model(count))
        assert work["fused_total_work"] < work["baseline_total_work"]
        baseline += int(work["baseline_total_work"])
        fused += int(work["fused_total_work"])
        saved += int(work["exact_work_saved"])
        cases.append(work)

    receipt = {
        "schema": "HHS_PASS219_I148_RAW5184_AUDIO_BENCHMARK_V1",
        "metric_class": "EXACT_LOGICAL_SERIALIZATION_WORK",
        "timing_is_canonical": False,
        "carrier": {
            "raw_bits": 5184,
            "bytes": 648,
            "pcm64_samples": 81,
            "bit_identity_required": True,
        },
        "mono_ternary": {
            "left": ["yx", "x+y", "xy"],
            "right": ["wz", "z+w", "zw"],
            "center_relation": "x+y:z+w",
            "roles": [-1, 0, 1],
            "role_pcm64": [
                PCM64_NOISE_FLOOR,
                PCM64_ZERO_CROSSING,
                PCM64_SATURATION_CEILING,
            ],
            "quotient": [1, 1, 1],
            "center_closure": "0/0=u^0 mod(u^72)=1",
            "scalar_projection_runtime_authority": False,
        },
        "sine_q62": {
            "phase_count": 72,
            "quarter": SINE_Q62_SCALE,
            "half": 0,
            "three_quarter": -SINE_Q62_SCALE,
            "runtime_float": False,
            "runtime_authority": False,
        },
        "cases": cases,
        "aggregate": {
            "baseline_total_work": baseline,
            "fused_total_work": fused,
            "exact_work_saved": saved,
            "reduction_permille_floor": (saved * 1000) // baseline,
        },
        "authority": {
            "vm81_mutation_changed": False,
            "hash72_changed": False,
            "hash216_changed": False,
            "scalar_projection_runtime_authority": False,
        },
        "result": "PASS",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

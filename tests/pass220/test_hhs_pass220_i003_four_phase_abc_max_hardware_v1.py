import json
import os
from pathlib import Path

import pytest

from benchmarks.pass220.hhs_pass220_i003_four_phase_abc_max_hardware_v1 import (
    PHASES,
    build_dataset,
    cyclic_hash216_distance,
    raw_rank,
)
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import HASH72_ALPHABET
from tools.pass220.hhs_pass220_i003_four_phase_abc_analyze_v1 import analyze


def test_dataset_is_deterministic_and_exact_candidate_is_present():
    left = build_dataset("xy", 0, 36, 16)
    right = build_dataset("xy", 0, 36, 16)
    assert left["dataset_digest"] == right["dataset_digest"]
    assert left["query"] == right["query"]
    assert left["candidates"] == right["candidates"]
    assert left["candidates"][0]["hash216"] == left["query"]["hash216"]


def test_raw_cyclic_distance_uses_hash72_ring_metric():
    base = HASH72_ALPHABET[0] * 216
    one = HASH72_ALPHABET[1] + HASH72_ALPHABET[0] * 215
    wrap = HASH72_ALPHABET[-1] + HASH72_ALPHABET[0] * 215
    assert cyclic_hash216_distance(base, base) == 0
    assert cyclic_hash216_distance(base, one) == 1
    assert cyclic_hash216_distance(base, wrap) == 1


def test_raw_rank_places_exact_hash216_match_first():
    dataset = build_dataset("zw", 18, 54, 32)
    ranked = raw_rank(dataset["query"]["hash216"], dataset["candidates"], 32)
    assert ranked["ranked"][0]["candidate_id"] == dataset["candidates"][0]["candidate_id"]
    assert ranked["ranked"][0]["distance"] == 0


def test_all_four_reciprocal_phase_geometries_are_frozen():
    assert PHASES == (("xy", 0, 36), ("yx", 36, 0), ("zw", 18, 54), ("wz", 54, 18))


def _synthetic_result():
    samples = []
    maxima = {}
    for phase, slot, inverse in PHASES:
        for rank, count in enumerate((8, 16), start=1):
            complete = True
            samples.append({
                "phase": phase,
                "phase_slot": slot,
                "inverse_phase_slot": inverse,
                "rank_index": rank,
                "candidate_count": count,
                "order": ("A", "B", "C") if rank == 1 else ("B", "C", "A"),
                "dataset_digest": f"{phase}:{count}",
                "same_dataset_verified": True,
                "all_arms_complete": complete,
                "arms": {
                    "A": {"elapsed_ns": 1000 * count, "completed": 2, "complete": True},
                    "B": {"elapsed_ns": 1200 * count, "completed": 2, "complete": True},
                    "C": {"elapsed_ns": 800 * count, "completed": 2, "complete": True},
                },
            })
        maxima[phase] = 16
    return {
        "schema": "HHS_PASS_220_I003_FOUR_PHASE_ABC_MAX_HARDWARE_QUERY_CALIBRATION_V1",
        "phases": [phase for phase, _, _ in PHASES],
        "samples": samples,
        "phase_max_hardware_closed_n": maxima,
        "global_max_hardware_closed_n": 16,
        "timing_observational_only": True,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "result": "PASS",
    }


def test_exact_analyzer_closes_four_phase_max_hardware_result():
    result = analyze(_synthetic_result())
    assert result["result"] == "PASS"
    assert result["four_phase_coverage"] is True
    assert result["global_max_hardware_closed_n"] == 16
    assert set(result["phase_summary"]) == {"xy", "yx", "zw", "wz"}
    assert result["global"]["ab_ratio"]["denominator"] > 0
    assert result["global"]["ac_ratio"]["denominator"] > 0
    assert result["global"]["bc_ratio"]["denominator"] > 0


def test_analyzer_fails_closed_on_phase_geometry_mismatch():
    payload = _synthetic_result()
    payload["samples"][0]["inverse_phase_slot"] = 18
    with pytest.raises(SystemExit):
        analyze(payload)


@pytest.mark.skipif(
    os.environ.get("HHS_PASS220_I003_INTEGRATION") != "1",
    reason="full Lane 5 CPU-reference integration runs in dedicated workflow",
)
def test_small_real_lane5_abc_integration():
    from benchmarks.pass220.hhs_pass220_i003_four_phase_abc_max_hardware_v1 import run

    result = run(
        leg_budget_ns=250_000_000,
        global_budget_ns=2_000_000_000,
        max_candidates=8,
        repeats=1,
    )
    assert result["result"] == "PASS"
    assert result["phase_max_hardware_closed_n"] == {"xy": 8, "yx": 8, "zw": 8, "wz": 8}
    assert result["global_max_hardware_closed_n"] == 8
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_authority"] is False
    assert result["canonical_hash216_authority"] is False

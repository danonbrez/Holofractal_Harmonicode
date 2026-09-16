from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V1.md"
TOOL = ROOT / "tools" / "hhs_time_bounded_math_supremacy_analyze_v1.py"
BENCH = ROOT / "benchmarks" / "pass219" / "hhs_lane5_time_bounded_math_supremacy_v1.c"


def _module():
    spec = importlib.util.spec_from_file_location("hhs_supremacy_v1", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_is_scoped_and_falsifiable() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    required = (
        "declared classical comparator class",
        "It is not, by itself, a claim that no possible classical algorithm",
        "Problem family A — exact affine modular orbit jump",
        "Problem family B — exact CRT reconstruction versus linear scan",
        "W_C_step(k) = k transition applications",
        "W_C_scan = M",
        "Empirical crossover",
        "Falsification rules",
        "Stage 2: add optimized conventional algorithms",
    )
    for needle in required:
        assert needle in text


def test_native_harness_uses_lane5_admission_and_zero_intermediates() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "hhs_exact_pass219_lane5_unbounded_workload_route_validate" in text
    assert "materialized_intermediate_states = 0U" in text
    assert "canonical_hash216_authority==0U" in text.replace(" ", "")
    assert "requires_signed_environmental_vm81_admission" in text
    assert "UINT64_C(1000000000000)" in text
    assert "101U,103U,107U,109U,113U,127U" in text


def test_analyzer_accepts_exact_synthetic_crossover() -> None:
    module = _module()
    native = {
        "result": "PASS",
        "scale_candidates": 1_000_000,
        "elapsed_ns": 4_000_000_000,
        "candidates_per_second_floor": 250_000,
        "stream_state_bytes": 568,
        "materialized_intermediate_states": 0,
    }
    meta = {"time_bound_ns": 50_000_000, "active_threads": 1}
    cases = [
        {
            "family": "affine", "size": 1000, "omega": 1000,
            "hhs_result": 7, "independent_result": 7,
            "linear_status": "solved", "linear_result": 7,
            "linear_steps": 1000, "linear_work_lower_bound": 1000,
            "hhs_compositions": 15, "hhs_total_ns": 100_000,
            "linear_elapsed_ns": 1_000_000, "exact": True,
            "lane5_admitted": True, "materialized_intermediate_states": 0,
        },
        {
            "family": "affine", "size": 10_000_000, "omega": 10_000_000,
            "hhs_result": 8, "independent_result": 8,
            "linear_status": "timeout", "linear_result": 0,
            "linear_steps": 500_000, "linear_work_lower_bound": 10_000_000,
            "hhs_compositions": 35, "hhs_total_ns": 150_000,
            "linear_elapsed_ns": 50_100_000, "exact": True,
            "lane5_admitted": True, "materialized_intermediate_states": 0,
        },
        {
            "family": "crt", "size": 2, "omega": 10_403,
            "hhs_result": 10_402, "independent_result": 10_402,
            "linear_status": "solved", "linear_result": 10_402,
            "linear_steps": 10_403, "linear_work_lower_bound": 10_403,
            "hhs_compositions": 1, "hhs_total_ns": 100_000,
            "linear_elapsed_ns": 2_000_000, "exact": True,
            "lane5_admitted": True, "materialized_intermediate_states": 0,
        },
        {
            "family": "crt", "size": 4, "omega": 121_330_189,
            "hhs_result": 121_330_188, "independent_result": 121_330_188,
            "linear_status": "timeout", "linear_result": 0,
            "linear_steps": 1_000_000, "linear_work_lower_bound": 121_330_189,
            "hhs_compositions": 3, "hhs_total_ns": 120_000,
            "linear_elapsed_ns": 50_100_000, "exact": True,
            "lane5_admitted": True, "materialized_intermediate_states": 0,
        },
    ]
    evidence = module.analyze(native, meta, cases)
    assert evidence["result"] == "PASS"
    assert evidence["claim_scope"]["universal_classical_supremacy_claim"] is False
    assert evidence["crossovers"]["affine"]["size"] == 10_000_000
    assert evidence["crossovers"]["crt"]["size"] == 4


def test_analyzer_rejects_missing_timeout_crossover() -> None:
    module = _module()
    native = {
        "result": "PASS", "scale_candidates": 1, "elapsed_ns": 1,
        "candidates_per_second_floor": 1, "stream_state_bytes": 568,
        "materialized_intermediate_states": 0,
    }
    meta = {"time_bound_ns": 50_000_000, "active_threads": 1}
    cases = [{
        "family": "affine", "size": 1000, "omega": 1000,
        "hhs_result": 1, "independent_result": 1,
        "linear_status": "solved", "linear_result": 1,
        "linear_steps": 1000, "linear_work_lower_bound": 1000,
        "hhs_compositions": 10, "hhs_total_ns": 1000,
        "linear_elapsed_ns": 2000, "exact": True,
        "lane5_admitted": True, "materialized_intermediate_states": 0,
    }]
    try:
        module.analyze(native, meta, cases)
    except ValueError as exc:
        assert "no bounded crossover" in str(exc)
    else:
        raise AssertionError("missing crossover should fail")

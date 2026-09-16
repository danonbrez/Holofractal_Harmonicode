from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from decimal import Decimal


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_120MS_RECIPROCAL_WAVE_XYZW_V3.md"
BENCH = ROOT / "benchmarks" / "pass219" / "hhs_lane5_120ms_reciprocal_wave_xyzw_v3.c"
ANALYZER = ROOT / "tools" / "hhs_120ms_reciprocal_wave_series_analyze_v3.py"


def _load_analyzer():
    spec = spec_from_file_location("wave_v3", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_uses_one_global_120ms_budget() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "T_global = 120,000,000 ns = 120 ms" in text
    assert "The 120 ms limit is global" in text
    assert "A / x" in text
    assert "B / y" in text
    assert "C / z" in text
    assert "D / w" in text


def test_contract_requires_same_state_per_gradient_sample() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "State(W_n)" in text
    assert "all four MUST equal `State(W_n)` exactly" in text
    assert "query_scale_(n+1) = 2 * query_scale_n" in text
    assert "greater mathematical difficulty" in text


def test_contract_defines_signed_wave_surface() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Psi_n = (x_n, y_n, z_n, w_n)" in text
    assert "D2 Psi_n + lambda * L_reciprocal(Psi_n) = eta_n" in text
    assert "Delta_xyzw = x*y - z*w" in text


def test_benchmark_enforces_global_budget_gradient_and_hhs_membrane() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "GLOBAL_BUDGET_NS = UINT64_C(120000000)" in text
    assert "remaining_ns / 4U" in text
    assert "query_scale *= 2U" in text
    assert "STREAM_SEED_W" in text
    assert "hhs_exact_pass219_lane5_unbounded_workload_route_validate" in text
    assert "route.materialized_intermediate_states = 0U" in text
    assert "route.candidate_only = 1U" in text
    assert "route.requires_signed_environmental_vm81_admission = 1U" in text


def test_signed_residual_is_negative_for_early_completion() -> None:
    m = _load_analyzer()
    ref = {"represented_transitions": "1000"}
    rec = {
        "dataset_complete": True,
        "completion_elapsed_ns": 5_000_000,
        "leg_budget_ns": 10_000_000,
        "represented_transitions": "1000",
    }
    assert m._signed_residual(rec, ref) == Decimal("-0.5")


def test_signed_residual_is_positive_for_incomplete_work() -> None:
    m = _load_analyzer()
    ref = {"represented_transitions": "1000"}
    rec = {
        "dataset_complete": False,
        "completion_elapsed_ns": 0,
        "leg_budget_ns": 10_000_000,
        "represented_transitions": "750",
    }
    assert m._signed_residual(rec, ref) == Decimal("0.25")


def test_reciprocal_graph_laplacian_conserves_sum() -> None:
    m = _load_analyzer()
    v = [Decimal("4"), Decimal("3"), Decimal("1"), Decimal("2")]
    lap = m._laplacian(v)
    assert sum(lap, Decimal(0)) == 0
    assert lap == [Decimal("3"), Decimal("1"), Decimal("-3"), Decimal("-1")]


def test_wave_fit_requires_three_gradient_samples_and_is_falsifiable() -> None:
    m = _load_analyzer()
    unavailable = m._wave_fit([[Decimal(1)] * 4, [Decimal(2)] * 4])
    assert unavailable["available"] is False

    vectors = [
        [Decimal("-0.9"), Decimal("-0.8"), Decimal("-0.75"), Decimal("-0.88")],
        [Decimal("-0.7"), Decimal("-0.6"), Decimal("-0.50"), Decimal("-0.68")],
        [Decimal("-0.4"), Decimal("-0.2"), Decimal("0.10"), Decimal("-0.35")],
    ]
    fit = m._wave_fit(vectors)
    assert fit["available"] is True
    assert "lambda" in fit
    assert "normalized_residual_rms" in fit

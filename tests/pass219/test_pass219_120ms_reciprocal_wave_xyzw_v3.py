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


def test_contract_fixes_all_four_legs_to_120ms() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Delta_t = 120,000,000 ns = 120 ms" in text
    assert "A / x" in text
    assert "B / y" in text
    assert "C / z" in text
    assert "D / w" in text
    assert "all four measurements have the identical wall-clock bound" in text


def test_contract_preserves_dataset_reciprocity() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "X: A -> C" in text
    assert "Y: B -> D" in text
    assert "C's completed prefix exactly matches A's prefix" in text
    assert "D's completed prefix exactly matches B's prefix" in text


def test_contract_defines_discrete_wave_surface() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Psi_n = (x_hat_n, y_hat_n, z_hat_n, w_hat_n)" in text
    assert "D2_t Psi_n" in text
    assert "Delta_xyzw = x_hat*y_hat - z_hat*w_hat" in text


def test_benchmark_uses_exact_common_window_and_hhs_membrane() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "DEFAULT_WINDOW_NS = UINT64_C(120000000)" in text
    assert "STREAM_SEED_X" in text and "STREAM_SEED_Y" in text
    assert "hhs_exact_pass219_lane5_unbounded_workload_route_validate" in text
    assert "materialized_intermediate_states = 0U" in text
    assert "candidate_only = 1U" in text
    assert "requires_signed_environmental_vm81_admission = 1U" in text


def test_signed_boundary_residual_is_negative_for_early_completion() -> None:
    m = _load_analyzer()
    producer = {"represented_transitions": "1000"}
    consumer = {
        "dataset_complete": True,
        "completion_elapsed_ns": 60_000_000,
        "represented_transitions": "1000",
    }
    assert m._boundary_residual(consumer, producer) == Decimal("-0.5")


def test_signed_boundary_residual_is_positive_for_incomplete_work() -> None:
    m = _load_analyzer()
    producer = {"represented_transitions": "1000"}
    consumer = {
        "dataset_complete": False,
        "completion_elapsed_ns": 0,
        "represented_transitions": "750",
    }
    assert m._boundary_residual(consumer, producer) == Decimal("0.25")


def test_reciprocal_graph_laplacian_conserves_sum() -> None:
    m = _load_analyzer()
    v = [Decimal("4"), Decimal("3"), Decimal("1"), Decimal("2")]
    lap = m._laplacian(v)
    assert sum(lap, Decimal(0)) == 0
    assert lap == [Decimal("3"), Decimal("1"), Decimal("-3"), Decimal("-1")]


def test_wave_fit_requires_three_samples_and_is_falsifiable() -> None:
    m = _load_analyzer()
    unavailable = m._wave_fit([[Decimal(1)] * 4, [Decimal(2)] * 4])
    assert unavailable["available"] is False

    vectors = [
        [Decimal("4"), Decimal("3"), Decimal("1"), Decimal("2")],
        [Decimal("3"), Decimal("2.5"), Decimal("2"), Decimal("2.2")],
        [Decimal("2"), Decimal("2"), Decimal("3"), Decimal("2.4")],
    ]
    fit = m._wave_fit(vectors)
    assert fit["available"] is True
    assert "lambda_s_inverse_2" in fit
    assert "normalized_residual_rms" in fit

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_TIME_BOUNDED_MATH_SUPREMACY_V2.md"
BENCH = ROOT / "benchmarks" / "pass219" / "hhs_lane5_time_bounded_math_supremacy_v2.c"
ANALYZER = ROOT / "tools" / "hhs_time_bounded_math_supremacy_analyze_v2.py"


def test_contract_defines_exact_bounded_supremacy_witness() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "same problem" in text
    assert "same exact target state" in text
    assert "same deadline" in text
    assert "HHS = complete" in text
    assert "legacy comparator = incomplete" in text
    assert "BOUNDED_SUPREMACY_WITNESS" in text


def test_contract_scopes_legacy_class_and_lower_bound() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "L_step" in text
    assert "W_L(k) = k dependent transition applications" in text
    assert "does not use the phrase `all classical computing`" in text
    assert "k_(n+1) = 10 * k_n" in text


def test_native_benchmark_uses_common_120ms_deadline_and_exact_verifier() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "DEFAULT_BOUND_NS = UINT64_C(120000000)" in text
    assert "legacy_linear" in text
    assert "apow" in text and "mpow" in text
    assert "result == independent" in text
    assert "k *= UINT64_C(10)" in text
    assert "BOUNDED_SUPREMACY_WITNESS" in text


def test_lane5_authority_membrane_is_preserved() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "route.materialized_intermediate_states = 0U" in text
    assert "route.candidate_only = 1U" in text
    assert "route.requires_signed_environmental_vm81_admission = 1U" in text
    assert "receipt.canonical_hash216_authority == 0U" in text


def test_analyzer_requires_calibration_and_first_incomplete_case() -> None:
    text = ANALYZER.read_text(encoding="utf-8")
    assert "missing calibration or bounded witness case" in text
    assert "gradient must scale k by exactly 10" in text
    assert "legacy completion at k_star" not in text.lower()  # wording comes from structured field below
    assert "legacy_completion_at_k_star_would_falsify" in text
    assert "Existence result against the explicitly defined linear state-materializing comparator class" in text

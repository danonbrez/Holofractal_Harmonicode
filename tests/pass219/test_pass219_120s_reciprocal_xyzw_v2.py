from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_120S_RECIPROCAL_XYZW_V2.md"
BENCH = ROOT / "benchmarks" / "pass219" / "hhs_lane5_120s_reciprocal_xyzw_v2.c"
TOOL = ROOT / "tools" / "hhs_120s_reciprocal_xyzw_analyze_v2.py"


def _module():
    spec = importlib.util.spec_from_file_location("hhs_reciprocal_v2", TOOL)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _synthetic():
    meta = {
        "schema": "HHS_120S_RECIPROCAL_XYZW_V2",
        "window_ns": 1_000_000_000,
        "stream_seed": 123,
        "modulus": 2_305_843_009_213_693_951,
        "k_min": 1_000_000,
        "k_span": 1_000_000_000,
        "active_threads_per_benchmark": 1,
        "benchmarks_sequential": True,
        "dataset_x_producer": "A",
        "dataset_y_producer": "B",
    }
    benches = {
        "A": {
            "id": "A", "axis": "x", "architecture": "hhs", "dataset": "X", "mode": "capacity_120s",
            "elapsed_ns": 1_000_100_000, "completed_queries": 100, "represented_transitions": "50000000000",
            "descriptor_bits": "9000", "affine_compositions": "4500", "matrix_multiplications": "4500",
            "lane5_admissions": 100, "endpoint_digest": 11, "descriptor_digest": 12,
            "materialized_intermediate_states": 0,
        },
        "B": {
            "id": "B", "axis": "y", "architecture": "conventional_matrix", "dataset": "Y", "mode": "capacity_120s",
            "elapsed_ns": 1_000_050_000, "completed_queries": 150, "represented_transitions": "75000000000",
            "descriptor_bits": "13500", "matrix_multiplications": "6750",
            "endpoint_digest": 21, "descriptor_digest": 22,
        },
        "C": {
            "id": "C", "axis": "z", "architecture": "conventional_matrix", "dataset": "X", "mode": "reciprocal_completion",
            "elapsed_ns": 700_000_000, "completed_queries": 100, "represented_transitions": "50000000000",
            "descriptor_bits": "9000", "matrix_multiplications": "4500",
            "endpoint_digest": 11, "descriptor_digest": 12,
        },
        "D": {
            "id": "D", "axis": "w", "architecture": "hhs", "dataset": "Y", "mode": "reciprocal_completion",
            "elapsed_ns": 1_500_000_000, "completed_queries": 150, "represented_transitions": "75000000000",
            "descriptor_bits": "13500", "affine_compositions": "6750", "matrix_multiplications": "6750",
            "lane5_admissions": 150, "endpoint_digest": 21, "descriptor_digest": 22,
            "materialized_intermediate_states": 0,
        },
    }
    verifications = {
        "X": {"dataset": "X", "producer": "A", "consumer": "C", "queries": 100, "endpoint_digest": 11, "descriptor_digest": 12, "exact": True},
        "Y": {"dataset": "Y", "producer": "B", "consumer": "D", "queries": 150, "endpoint_digest": 21, "descriptor_digest": 22, "exact": True},
    }
    return meta, benches, verifications


def test_contract_defines_four_pass_reciprocal_dataset_rule() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for needle in (
        "A / x",
        "B / y",
        "C / z",
        "D / w",
        "120,000,000,000 ns",
        "Dataset X is selected exactly once",
        "Dataset Y is selected exactly once",
        "optimized exact conventional architecture",
        "descriptor digest",
        "endpoint digest",
        "v1 literal-step result remains",
    ):
        assert needle in text


def test_native_benchmark_encodes_reciprocal_identity() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "DEFAULT_WINDOW_NS = UINT64_C(120000000000)" in text
    assert "run_hhs_window" in text
    assert "run_conventional_window" in text
    assert "run_conventional_count(a.completed_queries)" in text
    assert "run_hhs_count(b.completed_queries)" in text
    assert 'print_hhs("A", "x", "X"' in text
    assert 'print_conventional("B", "y", "Y"' in text
    assert 'print_conventional("C", "z", "X"' in text
    assert 'print_hhs("D", "w", "Y"' in text
    assert "c.descriptor_digest == a.descriptor_digest" in text
    assert "d.descriptor_digest == b.descriptor_digest" in text
    assert "c.endpoint_digest == a.endpoint_digest" in text
    assert "d.endpoint_digest == b.endpoint_digest" in text


def test_analyzer_accepts_exact_xyzw_result() -> None:
    mod = _module()
    evidence = mod.analyze(*_synthetic())
    assert evidence["result"] == "PASS"
    assert evidence["dataset_X"]["exact"] is True
    assert evidence["dataset_Y"]["exact"] is True
    assert evidence["xyzw"]["x_A_hhs_capacity_seconds"] == "1.0001"
    assert evidence["xyzw"]["y_B_conventional_capacity_seconds"] == "1.00005"
    assert evidence["xyzw"]["z_C_conventional_completes_X_seconds"] == "0.7"
    assert evidence["xyzw"]["w_D_hhs_completes_Y_seconds"] == "1.5"


def test_analyzer_rejects_any_cross_dataset_drift() -> None:
    mod = _module()
    meta, benches, verifications = _synthetic()
    benches["C"]["descriptor_digest"] = 999
    try:
        mod.analyze(meta, benches, verifications)
    except ValueError as exc:
        assert "dataset X differs" in str(exc)
    else:
        raise AssertionError("cross-dataset drift must fail")

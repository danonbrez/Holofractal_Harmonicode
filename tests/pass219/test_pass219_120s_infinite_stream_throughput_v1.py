from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_120S_INFINITE_STREAM_THROUGHPUT_V1.md"
BENCH = ROOT / "benchmarks" / "pass219" / "hhs_lane5_120s_infinite_stream_throughput_v1.c"
TOOL = ROOT / "tools" / "hhs_120s_infinite_stream_throughput_analyze_v1.py"


def _module():
    spec = importlib.util.spec_from_file_location("hhs_stream_v1", TOOL)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_contract_requires_same_stream_and_120_seconds() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for needle in (
        "same deterministic, non-terminating workload stream",
        "120,000,000,000 ns",
        "epochs run sequentially",
        "Endpoint state-space information rate",
        "Represented path-resolution rate",
        "full classical completed prefix replays",
        "does not claim universal classical-computing supremacy",
    ):
        assert needle in text


def test_native_benchmark_has_nonterminating_generator_and_lane5_membrane() -> None:
    text = BENCH.read_text(encoding="utf-8")
    assert "DEFAULT_WINDOW_NS = UINT64_C(120000000000)" in text
    assert "query_at(uint64_t index)" in text
    assert "hhs_exact_pass219_lane5_unbounded_workload_route_validate" in text
    assert "materialized_intermediate_states = 0U" in text
    assert "run_hhs(window_ns)" in text
    assert "run_classic(window_ns)" in text
    assert "replay_classical_prefix" in text


def test_analyzer_accepts_exact_synthetic_stream_result() -> None:
    mod = _module()
    meta = {
        "window_ns": 1_000_000_000,
        "stream_seed": 123,
        "modulus": 2_305_843_009_213_693_951,
        "k_min": 1_000_000,
        "k_span": 1_000_000_000,
        "active_threads_per_epoch": 1,
        "epochs_sequential": True,
    }
    hhs = {
        "elapsed_ns": 1_000_100_000,
        "completed_queries": 1000,
        "represented_transitions": "500000000000",
        "jump_descriptor_bits": "30000",
        "affine_compositions": "45000",
        "matrix_multiplications": "45000",
        "lane5_admissions": 1000,
        "endpoint_digest": 55,
        "materialized_intermediate_states": 0,
    }
    classical = {
        "elapsed_ns": 1_000_050_000,
        "completed_queries": 2,
        "represented_completed_transitions": "900000000",
        "executed_transition_steps": "1000000000",
        "jump_descriptor_bits": "59",
        "partial_steps": 100000000,
        "partial_query_k": 700000000,
        "endpoint_digest": 77,
    }
    verification = {
        "classical_prefix_queries": 2,
        "classical_prefix_digest": 77,
        "hhs_replay_digest": 77,
        "hhs_replay_compositions": "89",
        "exact": True,
    }
    evidence = mod.analyze(meta, hhs, classical, verification)
    assert evidence["result"] == "PASS"
    assert evidence["same_stream_exactness"]["exact"] is True
    assert evidence["hhs"]["completed_queries"] == 1000
    assert evidence["classical"]["completed_queries"] == 2
    assert evidence["claim_scope"]["universal_classical_supremacy_claim"] is False


def test_analyzer_rejects_prefix_digest_mismatch() -> None:
    mod = _module()
    meta = {
        "window_ns": 1_000_000_000,
        "stream_seed": 1,
        "modulus": 2_305_843_009_213_693_951,
        "k_min": 1_000_000,
        "k_span": 1_000_000_000,
        "active_threads_per_epoch": 1,
        "epochs_sequential": True,
    }
    hhs = {
        "elapsed_ns": 1_000_000_000,
        "completed_queries": 1,
        "represented_transitions": "1000000",
        "jump_descriptor_bits": "20",
        "affine_compositions": "20",
        "matrix_multiplications": "20",
        "lane5_admissions": 1,
        "endpoint_digest": 1,
        "materialized_intermediate_states": 0,
    }
    classical = {
        "elapsed_ns": 1_000_000_000,
        "completed_queries": 1,
        "represented_completed_transitions": "1000000",
        "executed_transition_steps": "1000000",
        "jump_descriptor_bits": "20",
        "partial_steps": 0,
        "partial_query_k": 0,
        "endpoint_digest": 2,
    }
    verification = {
        "classical_prefix_queries": 1,
        "classical_prefix_digest": 2,
        "hhs_replay_digest": 3,
        "hhs_replay_compositions": "20",
        "exact": True,
    }
    try:
        mod.analyze(meta, hhs, classical, verification)
    except ValueError as exc:
        assert "digest disagreement" in str(exc)
    else:
        raise AssertionError("digest mismatch must fail")

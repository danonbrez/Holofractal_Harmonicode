from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "contracts" / "pass219" / "PASS_219_120MS_RECIPROCAL_WAVE_XYZW_V3.md"
STRICT_BENCH = ROOT / "benchmarks" / "pass219" / "hhs_lane5_120ms_reciprocal_wave_xyzw_v3_strict.c"
STRICT_ANALYZER = ROOT / "tools" / "hhs_120ms_reciprocal_wave_series_analyze_v3_strict.py"


def _load_strict_analyzer():
    spec = spec_from_file_location("wave_v3_strict", STRICT_ANALYZER)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_uses_one_global_120ms_budget() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "T_global = 120,000,000 ns = 120 ms" in text
    assert "The 120 ms limit is global" in text
    assert "A / x" in text and "B / y" in text and "C / z" in text and "D / w" in text


def test_contract_requires_same_state_and_strict_positive_residual() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "all four MUST complete" in text
    assert "all four MUST equal `State(W_n)` exactly" in text
    assert "query_scale_(n+1) = 2 * query_scale_n" in text
    assert "greater problem difficulty" in text
    assert "zero or negative residual" in text
    assert "MUST NOT be clamped to zero" in text
    assert "There is no `subthreshold` admission path" in text


def test_contract_keeps_supremacy_theorem_separate() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Strict v3 does **not** create a bounded-supremacy witness" in text
    assert "executed witness at `n = 8`" in text
    assert "does not by itself prove universal classical-computing supremacy" in text


def test_strict_runner_reuses_exact_v3_primitives_and_rejects_clamping() -> None:
    text = STRICT_BENCH.read_text(encoding="utf-8")
    assert '#include "hhs_lane5_120ms_reciprocal_wave_xyzw_v3.c"' in text
    assert "remaining_ns / 4U" in text
    assert "query_scale *= 2U" in text
    assert "non_positive_leg_residual" in text
    assert "non_positive_global_residual" in text
    assert "non_positive_final_global_residual" in text
    assert "strict_positive_residual" in text
    assert '"clamping_permitted\\\":false' in text or "clamping_permitted" in text
    assert "boundary_sample_seen\\\":false" in text


def test_strict_analyzer_rejects_zero_global_residual() -> None:
    m = _load_strict_analyzer()
    meta = {
        "schema": m.STRICT_SCHEMA,
        "global_budget_ns": m.GLOBAL_BUDGET_NS,
        "strict_positive_residual": True,
        "clamping_permitted": False,
    }
    result = {
        "result": "PASS",
        "invalid_trial_seen": False,
        "stopped_before_unfair_trial": True,
        "batch_elapsed_ns": m.GLOBAL_BUDGET_NS,
        "remaining_budget_ns": 0,
        "sample_count": 3,
    }
    with pytest.raises(ValueError, match="strictly inside"):
        m._validate_strict(meta, [], {}, result)


def test_strict_analyzer_rejects_incomplete_or_zero_residual_leg() -> None:
    m = _load_strict_analyzer()
    meta = {
        "schema": m.STRICT_SCHEMA,
        "global_budget_ns": m.GLOBAL_BUDGET_NS,
        "strict_positive_residual": True,
        "clamping_permitted": False,
    }
    result = {
        "result": "PASS",
        "invalid_trial_seen": False,
        "stopped_before_unfair_trial": True,
        "batch_elapsed_ns": 60_000_000,
        "remaining_budget_ns": 60_000_000,
        "sample_count": 3,
    }
    refs = {
        i: {
            "sample": i,
            "query_scale": 2 ** (i + 1),
            "subthreshold": False,
            "completed_queries": 2 ** (i + 1),
            "represented_transitions": "10",
            "descriptor_bits": "20",
            "endpoint_digest": 30,
            "descriptor_digest": 40,
        }
        for i in range(3)
    }
    records = []
    for i in range(3):
        for ident in ("A", "B", "C", "D"):
            records.append({
                "sample": i,
                "id": ident,
                "leg_budget_ns": 10_000_000,
                "dataset_complete": True,
                "completion_elapsed_ns": 5_000_000,
                "completed_queries": 2 ** (i + 1),
                "represented_transitions": "10",
                "descriptor_bits": "20",
                "endpoint_digest": 30,
                "descriptor_digest": 40,
            })
    records[0]["dataset_complete"] = False
    with pytest.raises(ValueError, match="incomplete trial"):
        m._validate_strict(meta, records, refs, result)

    records[0]["dataset_complete"] = True
    records[0]["completion_elapsed_ns"] = 10_000_000
    with pytest.raises(ValueError, match="strictly positive"):
        m._validate_strict(meta, records, refs, result)


def test_strict_analyzer_accepts_four_way_exact_doubling_surface() -> None:
    m = _load_strict_analyzer()
    meta = {
        "schema": m.STRICT_SCHEMA,
        "global_budget_ns": m.GLOBAL_BUDGET_NS,
        "strict_positive_residual": True,
        "clamping_permitted": False,
    }
    result = {
        "result": "PASS",
        "invalid_trial_seen": False,
        "stopped_before_unfair_trial": True,
        "batch_elapsed_ns": 60_000_000,
        "remaining_budget_ns": 60_000_000,
        "sample_count": 3,
    }
    refs = {}
    records = []
    for i, scale in enumerate((2, 4, 8)):
        refs[i] = {
            "sample": i,
            "query_scale": scale,
            "subthreshold": False,
            "completed_queries": scale,
            "represented_transitions": "10",
            "descriptor_bits": "20",
            "endpoint_digest": 30,
            "descriptor_digest": 40,
        }
        for ident in ("A", "B", "C", "D"):
            records.append({
                "sample": i,
                "id": ident,
                "leg_budget_ns": 10_000_000,
                "dataset_complete": True,
                "completion_elapsed_ns": 5_000_000,
                "completed_queries": scale,
                "represented_transitions": "10",
                "descriptor_bits": "20",
                "endpoint_digest": 30,
                "descriptor_digest": 40,
            })
    m._validate_strict(meta, records, refs, result)


def test_no_invalid_trial_record_can_parse_as_evidence(tmp_path: Path) -> None:
    m = _load_strict_analyzer()
    path = tmp_path / "batch.ndjson"
    path.write_text(
        json.dumps({"type": "batch_meta", "schema": m.STRICT_SCHEMA}) + "\n"
        + json.dumps({"type": "invalid_trial", "reason": "non_positive_leg_residual"}) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid trial"):
        m._parse(path)

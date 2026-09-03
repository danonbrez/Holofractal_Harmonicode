from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "benchmarks" / "pass219" / "pass219_i151_benchmark_history.py"


def _load_tool():
    spec = importlib.util.spec_from_file_location("pass219_i151_benchmark_history", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixed_resolution_is_exact_bigint_and_not_tunable() -> None:
    tool = _load_tool()
    resolution = tool.fixed_resolution()
    assert resolution["base"] == 5184
    assert resolution["exponent"] == 21
    assert int(resolution["exact_cardinality_decimal"]) == 5184 ** 21
    assert 5184 ** 21 == 72 ** 42
    assert resolution["fixed"] is True
    assert resolution["exhaustive_enumeration_claim"] is False


def test_four_joint_integration_lanes_are_frozen() -> None:
    tool = _load_tool()
    assert tool.LANES == (
        "RAW5184_X86_64",
        "VM81_HASH72_HASH216",
        "OCTONION_DUAL_STEREO_TERNARY",
        "HARMONIC36_144X36",
    )


def test_inventory_discovers_current_pass219_benchmark_surfaces() -> None:
    tool = _load_tool()
    rows = tool.discover_inventory(ROOT)
    paths = {row["path"] for row in rows}
    assert "benchmarks/pass219/pass219_i148_raw5184_audio_benchmark.py" in paths
    assert "benchmarks/pass219/pass219_cross_modal_reversible_state_benchmark.py" in paths
    assert "benchmarks/pass219/harmonic36_stack_cache_capacity8_1_14_benchmark.cpp" in paths
    assert "benchmarks/pass219b/pass219b_phase_locality_benchmark.cpp" in paths
    assert "benchmarks/pass219b/PASS_219B_I2_MEASURED_RESULTS.json" in paths
    assert len(rows) >= 20
    assert len(tool.inventory_root(rows)) == 64


def test_history_is_append_only_chained_and_duplicate_run_keys_fail(tmp_path: Path) -> None:
    tool = _load_tool()
    receipt = ROOT / "benchmarks" / "pass219b" / "PASS_219B_I2_MEASURED_RESULTS.json"
    history = tmp_path / "history.jsonl"

    first = tool.build_entry(
        root=ROOT,
        repository_sha="a" * 40,
        run_id="100",
        observed_at="2026-09-03T00:00:00Z",
        receipt_paths=[receipt],
        previous_line_sha256=None,
    )
    tool.append_entry(history, first)
    first_bytes = history.read_bytes()

    previous = first_bytes.splitlines()[-1]
    second = tool.build_entry(
        root=ROOT,
        repository_sha="b" * 40,
        run_id="101",
        observed_at="2026-09-03T00:01:00Z",
        receipt_paths=[receipt],
        previous_line_sha256=hashlib.sha256(previous).hexdigest(),
    )
    tool.append_entry(history, second)

    after = history.read_bytes()
    assert after.startswith(first_bytes)
    parsed = [json.loads(line) for line in after.decode("utf-8").splitlines()]
    assert parsed[1]["previous_line_sha256"] == hashlib.sha256(previous).hexdigest()
    assert parsed[1]["resolution"]["exact_cardinality_decimal"] == str(5184 ** 21)
    assert parsed[1]["integrated_lanes"] == list(tool.LANES)
    assert len(parsed[1]["receipts"][0]["sha256"]) == 64

    with pytest.raises(ValueError, match="duplicate benchmark run key"):
        tool.append_entry(history, second)

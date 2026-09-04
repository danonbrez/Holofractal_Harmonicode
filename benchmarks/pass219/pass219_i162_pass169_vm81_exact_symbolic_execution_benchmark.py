from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time
from typing import Any

SCHEMA = "HHS_PASS219_I162_PASS169_VM81_EXACT_SYMBOLIC_BENCHMARK_V1"
PROBE_SCHEMA = "HHS_PASS219_I162_PASS169_VM81_EXACT_SYMBOLIC_PROBE_V1"


def _canonical(value: Any) -> bytes:
    def reject_float(node: Any) -> None:
        if isinstance(node, float):
            raise ValueError("FLOAT_CANONICAL_AUTHORITY_FORBIDDEN")
        if isinstance(node, dict):
            for child in node.values():
                reject_float(child)
        elif isinstance(node, (list, tuple)):
            for child in node:
                reject_float(child)

    reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _run_probe(binary: Path, source: Path) -> tuple[int, dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="pass219-i162-") as temp:
        out = Path(temp) / "probe.json"
        start = time.perf_counter_ns()
        subprocess.run(
            [str(binary), str(source), str(out)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        elapsed = time.perf_counter_ns() - start
        payload = json.loads(out.read_text(encoding="utf-8"))
    return elapsed, payload


def _validate_probe(row: dict[str, Any]) -> None:
    assert row["schema"] == PROBE_SCHEMA
    assert row["result"] == "PASS"
    assert row["edge_proved_mask"] == 1023
    assert row["typed_join_count"] == 10
    assert row["typed_join_proved"] == 10
    assert row["gate_true_mask"] == 31
    assert row["boolean_gate_count"] == 5
    assert row["boolean_gates_true"] == 5
    assert row["P"] == 30
    assert row["p"] == 29
    assert row["q"] == 31
    assert row["delta"] == 1
    assert row["typed_scalar_zero_verified"] is True
    assert row["typed_renewed_unit_verified"] is True
    assert row["ordinary_scalar_boundary_equality_claimed"] is False
    assert row["compatibility_ab_transport_only"] is True
    assert row["source_ab_definitionally_p2"] is False
    assert row["exact_vm81_admission_verified"] is True
    assert row["atomic_commit_verified"] is True
    assert row["hash72_receipt_verified"] is True
    assert row["hash216_proof_identity_verified"] is True
    assert row["deterministic_replay_verified"] is True
    assert row["source_reconstruction_verified"] is True
    assert row["pass169_authority_verified"] is True
    assert row["whole_equation_propagated"] is True
    assert row["floating_point_authority"] is False
    assert row["hash216_persistence_authority"] is False
    assert row["vm81_steps"] == 1
    assert row["replay_vm81_steps"] == 1
    assert row["receipt_hash72"] == row["replay_hash72"]
    assert row["proof_hash216"] != row["transition_hash216"]
    assert len(row["proof_hash216"]) == 216
    assert len(row["transition_hash216"]) == 216
    assert len(row["receipt_hash72"]) == 72
    assert len(row["canonical_global_symbol_environment_root"]) == 64


def benchmark(binary: Path, source: Path, repeats: int) -> dict[str, Any]:
    if repeats < 2:
        raise ValueError("REPEATS_MUST_BE_AT_LEAST_TWO")

    timings: list[int] = []
    probes: list[dict[str, Any]] = []
    for _ in range(repeats):
        elapsed, row = _run_probe(binary, source)
        _validate_probe(row)
        timings.append(elapsed)
        probes.append(row)

    stable_fields = (
        "edge_proved_mask",
        "gate_true_mask",
        "P",
        "p",
        "q",
        "delta",
        "vm5184_address",
        "vm81_steps",
        "replay_vm81_steps",
        "canonical_global_symbol_environment_root",
        "proof_hash216",
        "transition_hash216",
        "receipt_hash72",
        "replay_hash72",
    )
    reference = probes[0]
    deterministic = all(
        all(row[name] == reference[name] for name in stable_fields)
        for row in probes[1:]
    )
    if not deterministic:
        raise AssertionError("I162_DETERMINISTIC_RECEIPT_DRIFT")

    result = {
        "schema": SCHEMA,
        "result": "PASS",
        "repeats": repeats,
        "timing_clock": "perf_counter_ns",
        "timing_values_are_integer_nanoseconds": True,
        "min_ns": min(timings),
        "median_ns": int(statistics.median(timings)),
        "max_ns": max(timings),
        "deterministic_execution_receipt": deterministic,
        "typed_join_count": 10,
        "typed_join_proved": 10,
        "boolean_gate_count": 5,
        "boolean_gates_true": 5,
        "vm81_steps": reference["vm81_steps"],
        "replay_vm81_steps": reference["replay_vm81_steps"],
        "vm5184_address": reference["vm5184_address"],
        "canonical_global_symbol_environment_root": reference[
            "canonical_global_symbol_environment_root"
        ],
        "proof_hash216": reference["proof_hash216"],
        "transition_hash216": reference["transition_hash216"],
        "receipt_hash72": reference["receipt_hash72"],
        "replay_hash72": reference["replay_hash72"],
        "typed_scalar_zero_verified": True,
        "typed_renewed_unit_verified": True,
        "ordinary_scalar_boundary_equality_claimed": False,
        "compatibility_ab_transport_only": True,
        "source_ab_definitionally_p2": False,
        "legacy_full_symbolic_uqcel_v1_promoted": False,
        "exact_vm81_admission_verified": True,
        "atomic_commit_verified": True,
        "hash72_receipt_verified": True,
        "hash216_proof_identity_verified": True,
        "deterministic_replay_verified": True,
        "source_reconstruction_verified": True,
        "pass169_sealed_candidate_authority_verified": True,
        "pass169_terminal_contract_verified": False,
        "floating_point_authority": False,
        "hash216_persistence_authority": False,
        "fixed_resolution": "72^42=5184^21",
    }
    result["benchmark_receipt_sha256"] = _sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("probe_binary", type=Path)
    parser.add_argument("combined_source", type=Path)
    parser.add_argument("output_json", type=Path)
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    row = benchmark(
        args.probe_binary.resolve(),
        args.combined_source.resolve(),
        args.repeats,
    )
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(row, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(row, sort_keys=True))

    if args.enforce:
        assert row["result"] == "PASS"
        assert row["deterministic_execution_receipt"] is True
        assert row["typed_join_proved"] == 10
        assert row["boolean_gates_true"] == 5
        assert row["pass169_sealed_candidate_authority_verified"] is True
        assert row["pass169_terminal_contract_verified"] is False
        assert row["floating_point_authority"] is False
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Pass 219 Lane 5 1.56 — RNA self-ingestion bytecode experiment.

Experiment HHS-X5184-001.

This is a read-only finite-state experiment over the green HHS-T5184-004
constructor invariant. It asks what happens when the RNA layer ingests its own
ordered x/y/z/w words through two exact representations:

1. typed native operation64 byte:
      word -> kappa/operation64 -> one byte -> operation64 -> same word
2. external multiplicative spelling interpreted as an untyped BigInt number:
      "x*y*z" bytes -> integer -> mod64 -> operation64 -> decoded RNA word

The second path is deliberately marked NONCANONICAL. It exists to measure what
information is lost when type/provenance is discarded and a byte spelling is
treated as a bare number.

No bytes are executed as machine instructions. Native CI uses the existing
exact bytecode copy membrane only to prove ingress/egress byte identity.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

from hhs_runtime.harmonicode_lane5_t64_exhaustive_resolution_v1 import (
    DNA_ALPHABET,
    TERMINAL_ROOT,
    kappa_address,
    resolve_triplet,
)
from hhs_runtime.hhs_pass220_rna_operation64_c4_g41_radical_proof_v1 import (
    decode_operation64_rna_triplet,
)

SCHEMA = "HHS_PASS219_LANE5_RNA_SELF_INGESTION_BYTECODE_V1"
VERSION = "1.0.0"
EXPERIMENT_ID = "HHS-X5184-001"
PROJECTION_ID = "EXPERIMENTAL_NONCANONICAL_ASCII_BIGINT_MOD64"
BLOCK_MODULUS = 64


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _root(value: Any) -> str:
    raw = value if isinstance(value, str) else _stable_json(value)
    return sha256(raw.encode("utf-8")).hexdigest()


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = _root(record)
    return record


def all_triplets() -> Tuple[Tuple[str, str, str], ...]:
    return tuple(
        (q0, q1, q2)
        for q0 in DNA_ALPHABET
        for q1 in DNA_ALPHABET
        for q2 in DNA_ALPHABET
    )


def compact_word(triplet: Sequence[str]) -> str:
    values = tuple(triplet)
    if len(values) != 3 or any(symbol not in DNA_ALPHABET for symbol in values):
        raise ValueError("triplet must contain exactly three x/y/z/w symbols")
    return "".join(values)


def multiplicative_word(triplet: Sequence[str]) -> str:
    values = tuple(triplet)
    compact_word(values)
    return "*".join(values)


def bytes_to_bigint(raw: bytes) -> int:
    if not raw:
        raise ValueError("byte string must be nonempty")
    return int.from_bytes(raw, "big", signed=False)


def typed_native_code(triplet: Sequence[str]) -> Dict[str, Any]:
    address = kappa_address(triplet)
    operation64 = address["operation64"]
    raw = bytes((operation64,))
    decoded = decode_operation64_rna_triplet(raw[0])
    return {
        "triplet": tuple(triplet),
        "operation64": operation64,
        "byte_hex": raw.hex(),
        "byte_value": raw[0],
        "decoded_triplet": decoded,
        "fixed_point": decoded == tuple(triplet),
        "typed": True,
    }


def external_spelling_payload(triplet: Sequence[str]) -> Dict[str, Any]:
    compact = compact_word(triplet)
    explicit = multiplicative_word(triplet)
    compact_bytes = compact.encode("ascii")
    explicit_bytes = explicit.encode("ascii")
    compact_bigint = bytes_to_bigint(compact_bytes)
    explicit_bigint = bytes_to_bigint(explicit_bytes)
    return {
        "triplet": tuple(triplet),
        "compact_word": compact,
        "compact_bytes_hex": compact_bytes.hex(),
        "compact_bigint": compact_bigint,
        "explicit_word": explicit,
        "explicit_bytes_hex": explicit_bytes.hex(),
        "explicit_bigint": explicit_bigint,
        "last_symbol": compact[-1],
        "last_byte": compact_bytes[-1],
    }


def project_external_bigint_to_operation64(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("external bigint must be a nonnegative exact integer")
    return value % BLOCK_MODULUS


def projected_self_ingest(triplet: Sequence[str]) -> Dict[str, Any]:
    payload = external_spelling_payload(triplet)
    compact_op = project_external_bigint_to_operation64(
        payload["compact_bigint"]
    )
    explicit_op = project_external_bigint_to_operation64(
        payload["explicit_bigint"]
    )
    if compact_op != explicit_op:
        raise AssertionError("compact and explicit multiplicative spellings diverged mod64")
    decoded = decode_operation64_rna_triplet(compact_op)
    return {
        **payload,
        "projection_id": PROJECTION_ID,
        "projected_operation64": compact_op,
        "decoded_triplet": decoded,
        "decoded_word": compact_word(decoded),
        "typed": False,
        "canonical_authority": False,
    }


def iterate_projected_word(
    triplet: Sequence[str],
    *,
    maximum_steps: int = 64,
) -> Dict[str, Any]:
    current = tuple(triplet)
    seen: Dict[Tuple[str, str, str], int] = {}
    history = []
    for step in range(maximum_steps):
        if current in seen:
            cycle_start = seen[current]
            cycle = tuple(history[cycle_start:])
            return {
                "source": tuple(triplet),
                "history": tuple(history),
                "cycle": cycle,
                "cycle_length": len(cycle),
                "transient_length": cycle_start,
                "terminal": current,
            }
        seen[current] = len(history)
        history.append(current)
        current = tuple(projected_self_ingest(current)["decoded_triplet"])
    raise RuntimeError("self-ingestion orbit exceeded finite T64 bound")


def self_ingestion_witness() -> Dict[str, Any]:
    states = all_triplets()
    typed_records = tuple(typed_native_code(state) for state in states)
    projected_records = tuple(projected_self_ingest(state) for state in states)
    orbits = tuple(iterate_projected_word(state) for state in states)

    typed_image = {tuple(record["decoded_triplet"]) for record in typed_records}
    projected_image = {
        tuple(record["decoded_triplet"]) for record in projected_records
    }
    fixed = sorted(
        compact_word(state)
        for state in states
        if tuple(projected_self_ingest(state)["decoded_triplet"]) == state
    )
    basin_counts = Counter(
        compact_word(tuple(orbit["terminal"]))
        for orbit in orbits
    )

    projected_resolution = tuple(
        resolve_triplet(record["decoded_triplet"])
        for record in projected_records
    )

    # For any big-endian byte string, reduction mod64 depends only on the final
    # byte because 256 == 0 mod64. This is why the external spelling projection
    # discards the first two RNA symbols.
    last_byte_rule = all(
        record["projected_operation64"] == record["last_byte"] % 64
        for record in projected_records
    )

    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "experiment_id": EXPERIMENT_ID,
        "result": "PASS",
        "state_count": len(states),
        "typed_native": {
            "image_size": len(typed_image),
            "fixed_point_count": sum(
                1 for record in typed_records if record["fixed_point"]
            ),
            "all_64_identity": len(typed_image) == 64
                and all(record["fixed_point"] for record in typed_records),
        },
        "external_numeric_projection": {
            "projection_id": PROJECTION_ID,
            "canonical_authority": False,
            "image_size_after_one_step": len(projected_image),
            "fixed_points": tuple(fixed),
            "fixed_point_count": len(fixed),
            "basin_counts": dict(sorted(basin_counts.items())),
            "maximum_transient_length": max(
                orbit["transient_length"] for orbit in orbits
            ),
            "all_cycles_length_one": all(
                orbit["cycle_length"] == 1 for orbit in orbits
            ),
            "last_byte_mod64_rule": last_byte_rule,
            "compact_explicit_projection_agree": all(
                project_external_bigint_to_operation64(record["compact_bigint"])
                == project_external_bigint_to_operation64(record["explicit_bigint"])
                for record in projected_records
            ),
        },
        "post_projection_t004_resolution": {
            "resolved_count": sum(
                1
                for item in projected_resolution
                if tuple(item["resolved"]) == TERMINAL_ROOT
            ),
            "terminal_root": TERMINAL_ROOT,
            "unique_postprojection_operation64": len(
                {item["operation64"] for item in projected_resolution}
            ),
        },
        "typed_records_root_sha256": _root(typed_records),
        "projected_records_root_sha256": _root(projected_records),
        "orbits_root_sha256": _root(orbits),
        "bytes_executed_as_machine_instructions": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
    })


def validate_self_ingestion() -> Dict[str, Any]:
    witness = self_ingestion_witness()
    projected = witness["external_numeric_projection"]
    typed = witness["typed_native"]
    post = witness["post_projection_t004_resolution"]
    checks = {
        "t64_state_count_64": witness["state_count"] == 64,
        "typed_native_all_64_are_fixed_points": typed["all_64_identity"] is True
            and typed["fixed_point_count"] == 64
            and typed["image_size"] == 64,
        "external_projection_image_is_4": projected["image_size_after_one_step"] == 4,
        "external_projection_fixed_points_exact": projected["fixed_points"]
            == ("wyw", "wzx", "wzy", "wzz"),
        "external_projection_four_fixed_points": projected["fixed_point_count"] == 4,
        "external_projection_equal_16_state_basins": projected["basin_counts"]
            == {"wyw": 16, "wzx": 16, "wzy": 16, "wzz": 16},
        "external_projection_one_step_max_transient": projected["maximum_transient_length"] == 1,
        "external_projection_cycles_are_singletons": projected["all_cycles_length_one"] is True,
        "last_byte_mod64_explains_collapse": projected["last_byte_mod64_rule"] is True,
        "compact_and_explicit_multiplication_spellings_agree": projected[
            "compact_explicit_projection_agree"
        ] is True,
        "untyped_projection_has_no_canonical_authority": projected["canonical_authority"] is False,
        "postprojection_states_still_resolve_under_t004": post["resolved_count"] == 64
            and tuple(post["terminal_root"]) == TERMINAL_ROOT,
        "postprojection_provenance_collapses_to_four_addresses": post[
            "unique_postprojection_operation64"
        ] == 4,
        "bytecode_is_data_not_executed_code": witness[
            "bytes_executed_as_machine_instructions"
        ] is False,
        "no_canonical_authority_widened": (
            witness["canonical_vm81_mutation_authority"] is False
            and witness["canonical_hash72_authority"] is False
            and witness["canonical_hash216_authority"] is False
            and witness["canonical_persistence_authority"] is False
        ),
    }
    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "experiment_id": EXPERIMENT_ID,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "typed_native": typed,
        "external_numeric_projection": projected,
        "post_projection_t004_resolution": post,
    })


def main() -> int:
    report = validate_self_ingestion()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

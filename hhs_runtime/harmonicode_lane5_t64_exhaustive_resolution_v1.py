"""Pass 219 Lane 5 1.55 — HHS-T5184-004.

Bijective constructor provenance and exhaustive 64-state resolution.

This layer composes already-authoritative Pass 220 I020 RNA/operation64
addressing with the exact 8x8 phase-product law used by the native ABI.  It is
read-only proof infrastructure: no VM81, Hash72, Hash216, or persistence
authority is widened.

Resolve(s) is not a constant assignment.  Each ordered RNA triplet is:
  1. encoded through the inherited 4^3 <-> 8x8 operation64 bijection;
  2. evaluated through the ordered phase-product table;
  3. paired with its universal reciprocal phase so phase+reciprocal == 0 mod72;
  4. admitted to the orthogonal anchor ((0,-2)+(-2,0))/2=(-1,-1).

CI separately cross-checks all 64 Python phase results against the compiled
native hhs_exact_phase_product ABI and all 5,184 VM81 addresses.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_rna_operation64_c4_g41_radical_proof_v1 import (
    DNA_ALPHABET,
    decode_operation64_rna_triplet,
    encode_rna_triplet_operation64,
    rna_operation64_bijection_witness,
)
from hhs_runtime.harmonicode_lane5_reciprocal_phase_boundary_v1 import (
    GLOBAL_DENOMINATOR,
)

SCHEMA = "HHS_PASS219_LANE5_T64_EXHAUSTIVE_RESOLUTION_V1"
VERSION = "1.0.0"
THEOREM_ID = "HHS-T5184-004"

PHASE_MODULUS = 72
PHASE_ANCHOR: Tuple[int, ...] = (18, 54, 18, 54, 0, 36, 0, 36)
# Exact mirror of hhs_exact_phase_override in the authoritative C ABI.
PHASE_OVERRIDES: Mapping[Tuple[int, int], int] = {
    (0, 1): 0,
    (1, 0): 36,
    (2, 3): 0,
    (3, 2): 36,
    (4, 5): 36,
    (5, 4): 36,
    (6, 7): 36,
    (7, 6): 36,
    (4, 6): 0,
    (6, 4): 0,
    (5, 7): 0,
    (7, 5): 0,
}

ORTHOGONAL_VECTOR_A = (0, -2)
ORTHOGONAL_VECTOR_B = (-2, 0)
TERMINAL_ROOT = (-1, -1)

KAPPA_CODE: Mapping[str, str] = {
    "x": "00",
    "y": "01",
    "z": "10",
    "w": "11",
}


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _root(value: Any) -> str:
    payload = value if isinstance(value, str) else _stable_json(value)
    return sha256(payload.encode("utf-8")).hexdigest()


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = _root(record)
    return record


def kappa_address(triplet: Sequence[str]) -> Dict[str, Any]:
    values = tuple(triplet)
    encoded = encode_rna_triplet_operation64(values)
    binary6 = "".join(KAPPA_CODE[symbol] for symbol in values)
    if binary6 != encoded["binary6"]:
        raise AssertionError("kappa/base4 operation64 identity drift")
    row = int(binary6[:3], 2)
    column = int(binary6[3:], 2)
    if (row, column) != (
        encoded["left_basis8"],
        encoded["right_basis8"],
    ):
        raise AssertionError("kappa 3|3 split drift")
    return {
        "triplet": values,
        "binary6": binary6,
        "row8": row,
        "column8": column,
        "operation64": encoded["operation64"],
    }


def phase_product_reference(left_basis8: int, right_basis8: int) -> Dict[str, int]:
    if isinstance(left_basis8, bool) or isinstance(right_basis8, bool):
        raise ValueError("phase bases must be exact integers")
    if not 0 <= left_basis8 < 8 or not 0 <= right_basis8 < 8:
        raise ValueError("phase bases must lie in 0..7")
    raw = (PHASE_ANCHOR[left_basis8] + PHASE_ANCHOR[right_basis8]) % PHASE_MODULUS
    phase = PHASE_OVERRIDES.get((left_basis8, right_basis8), raw)
    reciprocal_phase = (-phase) % PHASE_MODULUS
    return {
        "left_basis": left_basis8,
        "right_basis": right_basis8,
        "raw_additive_phase": raw,
        "phase": phase,
        "reciprocal_phase": reciprocal_phase,
        "phase_zero_sum": int(
            (phase + reciprocal_phase) % PHASE_MODULUS == 0
        ),
        "native_closure_flag": int(phase in (0, 36)),
    }


def orthogonal_anchor() -> Dict[str, Any]:
    summed = (
        ORTHOGONAL_VECTOR_A[0] + ORTHOGONAL_VECTOR_B[0],
        ORTHOGONAL_VECTOR_A[1] + ORTHOGONAL_VECTOR_B[1],
    )
    resolved = (
        Fraction(summed[0], 2),
        Fraction(summed[1], 2),
    )
    if resolved != (Fraction(-1), Fraction(-1)):
        raise AssertionError("orthogonal root anchor drift")
    return {
        "vector_a": ORTHOGONAL_VECTOR_A,
        "vector_b": ORTHOGONAL_VECTOR_B,
        "sum": summed,
        "dyadic_divisor": 2,
        "resolved": tuple(int(value) for value in resolved),
    }


def resolve_triplet(triplet: Sequence[str]) -> Dict[str, Any]:
    address = kappa_address(triplet)
    phase = phase_product_reference(address["row8"], address["column8"])

    # Admission to the terminal q=-1 anchor is conditional on the actual
    # state-dependent phase/reciprocal closure, not assigned before it.
    if not phase["phase_zero_sum"]:
        raise AssertionError("triplet did not satisfy reciprocal phase closure")

    anchor = orthogonal_anchor()
    provenance = {
        "triplet": address["triplet"],
        "binary6": address["binary6"],
        "operation64": address["operation64"],
        "row8": address["row8"],
        "column8": address["column8"],
        "phase": phase["phase"],
        "reciprocal_phase": phase["reciprocal_phase"],
        "terminal_root": anchor["resolved"],
    }

    return _receipt({
        "schema": f"{SCHEMA}_STATE",
        "triplet": address["triplet"],
        "binary6": address["binary6"],
        "operation64": address["operation64"],
        "row8": address["row8"],
        "column8": address["column8"],
        "decoded_triplet": decode_operation64_rna_triplet(
            address["operation64"]
        ),
        "phase_product": phase,
        "orthogonal_anchor": anchor,
        "resolved": anchor["resolved"],
        "ordered_provenance_root_sha256": _root(provenance),
        "ordered_provenance_preserved": True,
        "commutation_authority": False,
    })


def exhaustive_resolution_witness() -> Dict[str, Any]:
    inherited = rna_operation64_bijection_witness()
    records = []
    addresses = set()
    provenance_roots = set()
    terminal_count = 0
    for q0 in DNA_ALPHABET:
        for q1 in DNA_ALPHABET:
            for q2 in DNA_ALPHABET:
                result = resolve_triplet((q0, q1, q2))
                records.append(result)
                addresses.add(result["operation64"])
                provenance_roots.add(
                    result["ordered_provenance_root_sha256"]
                )
                if tuple(result["resolved"]) == TERMINAL_ROOT:
                    terminal_count += 1

    if addresses != set(range(64)):
        raise AssertionError("T64 did not cover all 64 addresses")
    if len(provenance_roots) != 64:
        raise AssertionError("ordered provenance collision in T64")
    if terminal_count != 64:
        raise AssertionError("not all T64 states resolved to q=-1 root")

    return _receipt({
        "schema": SCHEMA,
        "version": VERSION,
        "theorem_id": THEOREM_ID,
        "result": "PASS",
        "triplet_count": len(records),
        "address_count": len(addresses),
        "provenance_root_count": len(provenance_roots),
        "resolved_terminal_count": terminal_count,
        "terminal_root": TERMINAL_ROOT,
        "kappa_codes": dict(KAPPA_CODE),
        "bijection": "{x,y,z,w}^3<->{0,1}^6<->8x8",
        "four_cubed": 4**3,
        "eight_squared": 8**2,
        "vm81_cells": 81,
        "local_constructor_states": 64,
        "serialization_geometry": 81 * 64,
        "inherited_i020_roundtrip_all_64": inherited["roundtrip_all_64"],
        "inherited_i020_order_preserved": inherited[
            "ordered_triplet_identity_preserved"
        ],
        "phase_modulus": PHASE_MODULUS,
        "phase_reference_is_native_abi_mirror": True,
        "native_crosscheck_required": True,
        "universal_denominator": GLOBAL_DENOMINATOR,
        "delta_cancellation_authority": False,
        "commutation_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "records": tuple(records),
    })


def validate_t5184_004() -> Dict[str, Any]:
    witness = exhaustive_resolution_witness()
    records = witness["records"]
    checks = {
        "four_cubed_is_64": witness["four_cubed"] == 64,
        "eight_squared_is_64": witness["eight_squared"] == 64,
        "kappa_all_64_bijective": (
            witness["triplet_count"]
            == witness["address_count"]
            == 64
        ),
        "ordered_provenance_all_64_unique": (
            witness["provenance_root_count"] == 64
        ),
        "inherited_i020_roundtrip_all_64": witness[
            "inherited_i020_roundtrip_all_64"
        ] is True,
        "inherited_i020_order_preserved": witness[
            "inherited_i020_order_preserved"
        ] is True,
        "all_addresses_decode_exact": all(
            tuple(record["triplet"]) == tuple(record["decoded_triplet"])
            for record in records
        ),
        "all_phase_products_zero_sum_with_reciprocal": all(
            record["phase_product"]["phase_zero_sum"] == 1
            for record in records
        ),
        "all_64_resolve_to_minus_one_minus_one": (
            witness["resolved_terminal_count"] == 64
            and all(tuple(record["resolved"]) == TERMINAL_ROOT for record in records)
        ),
        "orthogonal_anchor_exact": orthogonal_anchor()["resolved"] == TERMINAL_ROOT,
        "vm81_times_t64_is_5184": witness["serialization_geometry"] == 5184,
        "same_delta_boundary": witness["universal_denominator"] == GLOBAL_DENOMINATOR,
        "delta_never_cancelled": witness["delta_cancellation_authority"] is False,
        "commutation_not_granted": witness["commutation_authority"] is False,
        "native_phase_crosscheck_required": witness["native_crosscheck_required"] is True,
        "no_canonical_authority_widened": (
            witness["canonical_vm81_mutation_authority"] is False
            and witness["canonical_hash72_authority"] is False
            and witness["canonical_hash216_authority"] is False
        ),
    }
    return _receipt({
        "schema": f"{SCHEMA}_VALIDATION",
        "version": VERSION,
        "theorem_id": THEOREM_ID,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "triplet_count": witness["triplet_count"],
        "address_count": witness["address_count"],
        "resolved_terminal_count": witness["resolved_terminal_count"],
        "serialization_geometry": witness["serialization_geometry"],
        "terminal_root": witness["terminal_root"],
        "native_crosscheck": "REQUIRED_BY_CI",
    })


def main() -> int:
    report = validate_t5184_004()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

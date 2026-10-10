"""Pass 220 I085: x/u exact rational-exponent 5184 ADDRESS crosswalk.

Preserves original Pass186 (81 x86_64) <-> (36x144) and Pass220 I071
(72x72) arithmetic as lossless, position-bearing representations.
This is a coordinate/constructor admission surface, not an arbitrary
64-bit CELL VALUE compressor or an executed root-of-unity operator.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
    PHASE_BASIS, phase_gear_invariants,
)
from hhs_runtime.hhs_pass220_i084_x4_ordered_unit_quotient_v1 import formalize_i084

SCHEMA = "HHS_PASS_220_I085_X_OVER_U_RATIONAL_VM81_HASH72_CROSSWALK_V1"
SOURCE_RELATION = "(81*x86_64)=hash72=5184/72²=u⁷²"
REQUESTED_CONSTRUCTOR = "(x/u)^(s5184/72)"
Q72 = 72
Q81 = 81
Q64 = 64
N5184 = Q81 * Q64
Q144 = 144
LANES36 = 36
PHASE_BASIS_ORDERED = tuple(PHASE_BASIS)

# These properties are separate; syntactic u^(p/q) is NOT evaluated by
# standard host exponentiation or assumed to be a unique native operator.
NATIVE_OBLIGATIONS = (
    "original-x/u:ordered-division-inverse-admissibility",
    "u^72=1:typed-72-phase-primitive-root-and-parent-provenance",
    "u^(1/72):consistent-rational-root-branch-and-exponent-composition",
    "(x/u)^(s/72):native-power-operator-admissibility-for-the-canonical-branch",
    "different-exponents:distinct-native-cell-operators-not-only-text-labels",
    "all-VM81-cell-values:reversible-typed-amplitude-and-BigInt-content",
    "native-Hash72-72-glyph-ledger:not-confused-with-72x72-position-map",
    "original-Hash216:transition-witness-and-authoritative-state-lineage",
    "signed-VM81:only-original-environmental-mutation-authority",
)


class I085CrosswalkError(ValueError):
    pass


def _bounded_int(value: Any, *, name: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise I085CrosswalkError(f"{name} requires exact integer [{lower},{upper}]")
    return value


def _exponent_from_source(value: Mapping[str, Any]) -> Fraction:
    if not isinstance(value, Mapping):
        raise I085CrosswalkError("exact x/u exponent mapping required")
    n, d = value.get("numerator"), value.get("denominator")
    if isinstance(n, bool) or isinstance(d, bool) or not isinstance(n, int) or not isinstance(d, int):
        raise I085CrosswalkError("exact rational numerator/denominator required")
    if d <= 0:
        raise I085CrosswalkError("positive nonzero rational exponent denominator required")
    if d > Q72:
        raise I085CrosswalkError("canonical rational exponent denominator out of range")
    result = Fraction(n, d)
    if (result * Q72).denominator != 1:
        raise I085CrosswalkError("rational exponent does not address integer/72 position")
    return result


def _frac(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def encode_address(s5184: int) -> dict[str, Any]:
    """Canonical symbolic addressing of all 5184 *positions*, not payloads."""
    pos = _bounded_int(s5184, name="s5184", lower=0, upper=N5184-1)
    vm_cell, operation = divmod(pos, Q64)
    hash_row, hash_col = divmod(pos, Q72)
    lane36, q144 = divmod(pos, Q144)
    root_row, root_col = divmod(q144, 12)
    pair, ring_index = divmod(q144, Q72)
    phase = Fraction(pos, Q72)
    if not (Q81 * Q64 == Q72 * Q72 == LANES36 * Q144 == N5184):
        raise I085CrosswalkError("shared 5184-coordinate geometry changed")
    return {
        "schema": SCHEMA,
        "s5184": pos,
        "vm81": {"cell": vm_cell, "operation64": operation},
        # Lowercase "hash72" denotes a crosswalk geometry, NEVER a
        # canonical 72-character Hash72 receipt/cryptographic witness.
        "hash72_address_geometry": {"row": hash_row, "column": hash_col},
        "q144": {
            "opcode_lane36": lane36, "root_row12": root_row, "root_col12": root_col,
            "q144_index": q144, "u72_pair": pair, "u72_index": ring_index,
        },
        "operation": {
            "class8": operation // 8, "basis8": operation % 8,
            "ordered_symbol": PHASE_BASIS_ORDERED[operation % 8],
        },
        "typed_constructor": {
            "head": "HHS_ORDERED_RATIONAL_EXPONENT",
            "base": {
                "head": "HHS_ORDERED_QUOTIENT",
                "numerator": {"head": "PHASE_ADDRESS", "symbol": "x"},
                "denominator": {"head": "PHASE_ADDRESS", "symbol": "u"},
                "native_inverse_direction_proven": False,
            },
            "exponent": _frac(phase),
            "formal_symbol": "(x/u)^r",
            "native_operator_evaluation_proven": False,
            "rational_branch_proven": False,
        },
        "coordinate_bijection_verified": True,
        "native_phase_operator_uniqueness_proven": False,
        "original_vm81_cell_payload_encoded": False,
        "hash72_cryptographic_ledger_minted": False,
        "candidate_only": True,
    }


def decode_address(carrier: Mapping[str, Any]) -> int:
    """Lossless exact inverse only for complete untampered I085 coordinates."""
    if not isinstance(carrier, Mapping) or carrier.get("schema") != SCHEMA:
        raise I085CrosswalkError("typed I085 coordinate carrier required")
    constructor = carrier.get("typed_constructor")
    if not isinstance(constructor, Mapping):
        raise I085CrosswalkError("native x/u symbolic constructor required")
    power = _exponent_from_source(constructor.get("exponent"))
    s_frac = power * Q72
    if s_frac.denominator != 1:
        raise I085CrosswalkError("fractional address cannot map to VM81 integer")
    pos = _bounded_int(s_frac.numerator, name="decoded s5184", lower=0, upper=N5184-1)
    reconstructed = encode_address(pos)
    if dict(carrier) != reconstructed:
        raise I085CrosswalkError("I085 ordered address, type, phase or lineage changed")
    return pos


def enumerate_all_addresses() -> dict[str, Any]:
    """Enumerate 5184 exact addresses with full inverse and 81x64 coverage."""
    cells: set[tuple[int, int]] = set()
    hashes: set[tuple[int, int]] = set()
    phases: set[Fraction] = set()
    bases: set[str] = set()
    for pos in range(N5184):
        carrier = encode_address(pos)
        if decode_address(carrier) != pos:
            raise I085CrosswalkError("I085 exact address roundtrip failed")
        vm = carrier["vm81"]
        h = carrier["hash72_address_geometry"]
        cells.add((vm["cell"], vm["operation64"]))
        hashes.add((h["row"], h["column"]))
        phases.add(_exponent_from_source(carrier["typed_constructor"]["exponent"]))
        bases.add(carrier["operation"]["ordered_symbol"])
    if not (len(cells) == len(hashes) == len(phases) == N5184):
        raise I085CrosswalkError("position crosswalk not bijective")
    if bases != set(PHASE_BASIS_ORDERED):
        raise I085CrosswalkError("native operation order basis incomplete")
    return {
        "schema": f"{SCHEMA}_COVERAGE",
        "distinct_vm81_cell_operation_addresses": len(cells),
        "distinct_hash72_geometry_positions": len(hashes),
        "distinct_exact_rational_exponent_labels": len(phases),
        "ordered_basis8_count": len(bases),
        "all_81_vm81_cells_and_64_operation_slots_covered": True,
        "original_pass186_q144_crosswalk_preserved": True,
        "all_native_cell_values_encoded": False,
        "native_exponent_operator_uniqueness_proven": False,
        "no_hash72_mint": True,
        "no_vm81_mutation": True,
    }


def formalize_i085(*, enumerate_all: bool = False) -> dict[str, Any]:
    """Compose prior I084 source and inherited I071 phase geometry."""
    parent = formalize_i084()
    if (
        parent.get("original_source") != "x⁴=(t³-t)/(m²-m)=a²"
        or parent.get("projected_quotient_unit_closed") is not True
        or parent.get("native_chain_admitted") is not False
    ):
        raise I085CrosswalkError("I084 source/phase admission contract diverged")
    gear = phase_gear_invariants()
    if gear["coordinate_closure"] is not True or gear["qudit_phase_slots"] != Q72:
        raise I085CrosswalkError("inherited native I071 geometry diverged")
    coverage = enumerate_all_addresses() if enumerate_all else {
        "enumerated": False, "status": "REQUIRES_EXHAUSTIVE_EXECUTION"
    }
    body = {
        "schema": SCHEMA,
        "source_relation": SOURCE_RELATION,
        "requested_constructor": REQUESTED_CONSTRUCTOR,
        "inherited_i084_source_identity_sha256": parent["source_identity_sha256"],
        "inherited_i083_source_identity_sha256": parent["inherited_i083_source_identity_sha256"],
        "original_i082_c_root_relation": parent["inherited_i082_c_geometric_root"],
        "vm81_word_count": Q81,
        "x86_64_word_bits": Q64,
        "vm81_bit_positions": N5184,
        "hash72_geometry_rows": Q72,
        "hash72_geometry_cols": Q72,
        "hash72_geometry_positions": Q72*Q72,
        "fraction_5184_over_72_squared": _frac(Fraction(N5184,Q72*Q72)),
        "u72_torus_phase_condition": "u^72=1 (original typed phase rule)",
        "x_over_u_formal_rational_exponent": "(x/u)^(s5184/72)",
        "fractional_root_branch_condition": "native coherent branch required",
        "full_position_enumeration": coverage,
        "eight_ordered_operation_channels": list(PHASE_BASIS_ORDERED),
        "inherited_i071_phase_gear": gear,
        "native_operator_obligations": list(NATIVE_OBLIGATIONS),
        "full_5184_address_bijection": coverage.get(
            "all_81_vm81_cells_and_64_operation_slots_covered", False
        ),
        "native_universal_tensor_value_encoding_proven": False,
        "native_rational_exponent_phases_evaluated": False,
        "native_hash72_cryptographic_ledger_equivalence_proven": False,
        "native_hash216_lineage_witness_proven": False,
        "native_canonical_signed_admission_proven": False,
        "candidate_only": True,
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
    }
    body["source_identity_sha256"] = sha256(
        json.dumps({k:v for k,v in body.items() if k!="source_identity_sha256"},
                   sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(",",":")).encode()
    ).hexdigest()
    return body

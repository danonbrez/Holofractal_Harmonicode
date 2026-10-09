"""Pass 220 I084: x⁴=(t³-t)/(m²-m)=a² ordered Law-of-1 quotient.

This adds a SOURCE-PRESERVING quotient to the original SPI Law-of-1 and
I083 cubic chain. Native x, t, m, a² have different VM81/phase addresses;
equal projected unit values do not license commutation, scalarizing the
native quotient, or minting canonical Hash72/Hash216/VM81 authority.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_spi_law_of_one_projection_rule_v1 import member_witness
from hhs_runtime.hhs_pass220_i083_ordered_cubic_law_one_i082_bridge_v1 import (
    SOURCE_FRAGMENT as PARENT_I083_FRAGMENT,
    formalize_i083,
)

SCHEMA = "HHS_PASS_220_I084_X4_ORDERED_UNIT_QUOTIENT_V1"
SOURCE_RELATION = "x⁴=(t³-t)/(m²-m)=a²"
ORDERED_MEMBERS = ("x⁴", "t³-t", "m²-m", "a²")
EQUALITY_OPERANDS = ("x⁴", "(t³-t)/(m²-m)", "a²")
NATIVE_OPERATOR_OBLIGATIONS = (
    "x⁴:typed-x-phase-quartic-closure-witness",
    "t³-t:ordered-cubic-difference-and-parent-I083-history",
    "m²-m:typed-ordered-denominator-with-inverse-admissibility",
    "(t³-t)/(m²-m):native-directional-quotient-and-projector-compatibility",
    "a²:Lo-Shu-source-cell-7-identity",
    "x⁴==quotient==a²:ordered-native-equality-chain-proof",
    "original-I083-open-parenthesis:not-silently-closed",
)


class I084OrderedQuotientError(ValueError):
    pass


def _exact_member(member: str, record: Mapping[str, Any]) -> Fraction:
    if not isinstance(record, Mapping):
        raise I084OrderedQuotientError("original Law-of-1 receipt required")
    if (
        record.get("schema") != "HHS_SPI_LAW_OF_ONE_MEMBER_WITNESS_V1"
        or record.get("native_source_expression") != member
        or record.get("projection_relation") != f"pi({member})=1"
        or record.get("projection_only") is not True
        or record.get("native_identity_with_other_members") is not False
        or record.get("native_commutation_authorized") is not False
        or record.get("canonical_admission_authority") is not False
        or record.get("vm81_mutation_authority") is not False
        or record.get("canonical_hash72_authority") is not False
        or record.get("canonical_hash216_authority") is not False
    ):
        raise I084OrderedQuotientError("typed Law-of-1 member authority/source mismatch")
    v = record.get("projection_value")
    if not isinstance(v, Mapping) or v.get("type") != "EXACT_RATIONAL":
        raise I084OrderedQuotientError("typed exact rational projection required")
    p, q = v.get("numerator"), v.get("denominator")
    if (
        isinstance(p, bool) or isinstance(q, bool)
        or not isinstance(p, int) or not isinstance(q, int)
        or q == 0
    ):
        raise I084OrderedQuotientError("invalid or zero exact rational denominator")
    projected = Fraction(p, q)
    if projected != Fraction(1):
        raise I084OrderedQuotientError("original Law-of-1 unit changed")
    return projected


def formalize_i084(*, hydrate_existing_phase_gear: bool = False) -> dict[str, Any]:
    parent = formalize_i083(phase_gear_hydration=hydrate_existing_phase_gear)
    if (
        parent.get("source_fragment_exact") != PARENT_I083_FRAGMENT
        or parent.get("source_open_parenthesis_preserved") is not True
        or parent.get("native_chain_admitted") is not False
        or parent.get("i082_a2_cell_address") != 7
        or parent.get("scalar_projection_units_equal") is not True
    ):
        raise I084OrderedQuotientError("inherited I083 source or native hold diverged")

    # Authoritative registered SPI witnesses are obtained from the original
    # Law-of-1 runtime rather than synthesized from the newest source text.
    receipts = {member: member_witness(member) for member in ORDERED_MEMBERS}
    units = {member: _exact_member(member, receipts[member]) for member in ORDERED_MEMBERS}
    numerator = units["t³-t"]
    denominator = units["m²-m"]
    if denominator == 0:
        raise I084OrderedQuotientError("projected m²-m denominator cannot be zero")
    quotient = numerator / denominator
    if quotient != units["x⁴"] or quotient != units["a²"]:
        raise I084OrderedQuotientError("ordered quotient scalar unit failure")

    # The typed source is not canonicalized into a host-language algebra.
    # Each index and child list remains distinct in the source witness.
    ast = {
        "head": "HHS_ORDERED_EQUALITY_CHAIN",
        "source": SOURCE_RELATION,
        "operands": [
            {"head": "PHASE_POW", "symbol": "x", "exponent": 4},
            {
                "head": "NATIVE_ORDERED_DIVISION",
                "surface_symbol": "/",
                "numerator": {
                    "head": "NATIVE_ORDERED_SUBTRACTION",
                    "left": {"head": "PHASE_POW", "symbol": "t", "exponent": 3},
                    "right": {"head": "PHASE_ADDRESS", "symbol": "t"},
                },
                "denominator": {
                    "head": "NATIVE_ORDERED_SUBTRACTION",
                    "left": {"head": "PHASE_POW", "symbol": "m", "exponent": 2},
                    "right": {"head": "PHASE_ADDRESS", "symbol": "m"},
                },
                "native_inverse_direction_proven": False,
            },
            {"head": "ROOT_ADDRESS", "symbol": "a²"},
        ],
        "directed_edges": [[0, 1], [1, 2]],
        "native_equality_not_host_scalar_substitution": True,
    }
    sha = sha256(json.dumps(
        {"source": SOURCE_RELATION, "ast": ast,
         "i083_source_sha256": parent["source_identity_sha256"]},
        sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()

    def exact(value: Fraction) -> dict[str, int]:
        return {"numerator": value.numerator, "denominator": value.denominator}

    return {
        "schema": SCHEMA,
        "original_source": SOURCE_RELATION,
        "ordered_equality_operands": list(EQUALITY_OPERANDS),
        "typed_expression": ast,
        "source_identity_sha256": sha,
        "inherited_i083_source_identity_sha256": parent["source_identity_sha256"],
        "inherited_i083_open_group": True,
        "inherited_i082_a2_cell_address": 7,
        "inherited_i082_c_geometric_root": parent["i082_c_root_relation"],
        "law_of_one_member_order": list(ORDERED_MEMBERS),
        "inherited_law_of_one_receipts": receipts,
        "x4_member_evidence_kind": receipts["x⁴"]["evidence_kind"],
        "x4_registered_phase_quartic_axiom_is_not_native_execution": True,
        "exact_projected_numerator": exact(numerator),
        "exact_projected_denominator": exact(denominator),
        "exact_projected_quotient": exact(quotient),
        "exact_projected_x4": exact(units["x⁴"]),
        "exact_projected_a2": exact(units["a²"]),
        "denominator_nonzero_in_exact_projection": True,
        "projected_quotient_unit_closed": True,
        "projected_equality_chain_closed": True,
        "native_division_direction_verified": False,
        "native_quotient_projector_homomorphism_proven": False,
        "native_x4_equality_chain_proven": False,
        "native_x4_operator_executed": False,
        "native_source_address_phase_witness_proven": False,
        "native_operator_obligations": list(NATIVE_OPERATOR_OBLIGATIONS),
        "native_chain_admitted": False,
        "status": "HOLD_NATIVE_ORDERED_QUOTIENT_PROOF",
        "projection_only": True,
        "candidate_only": True,
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
    }

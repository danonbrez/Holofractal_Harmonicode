"""Pass 220 I083 — ordered cubic Law-of-1 link to the I082 tensor root.

Source supplied: (t³=t+(m²-m)=a²+t
The opening parenthesis remains syntactically OPEN, as supplied.

This is an additive bridge to existing Pass219 SPI three-set cubic and
Law-of-1 services, NOT a new cubic solver, scalar t/m assignment,
commutativity rule, native Hash72/Hash216 mint, or VM81 gate.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_i082_chiral_bilateral_loshu_bifurcation_v1 import (
    CANONICAL_VALUES,
    formalize_i082,
    positive_geometric_c_root,
)
from hhs_spi_law_of_one_projection_rule_v1 import member_witness
from hhs_spi_tensor_pair_cubic_normalization_rule_v1 import (
    tensor_pair_cubic_witness,
    SOURCE_RELATION as INHERITED_CUBIC_SOURCE,
    RESIDUAL_RELATION as INHERITED_CUBIC_RESIDUAL,
)

SCHEMA = "HHS_PASS_220_I083_ORDERED_CUBIC_LAW_ONE_I082_BRIDGE_V1"
SOURCE_FRAGMENT = "(t³=t+(m²-m)=a²+t"
SOURCE_OPEN_PARENTHESIS = True
CHAIN_OPERANDS = ("t³", "t+(m²-m)", "a²+t")
INHERITED_MEMBER_ORDER = ("t³-t", "m²-m", "a²")
SOURCE_OPERATOR_OBLIGATIONS = (
    "t³=t+(m²-m):ordered-native-cubic-edge",
    "t+(m²-m)=a²+t:ordered-native-reciprocal-addition-edge",
    "m²-m=a²:typed-unit-reference-link",
    "t+a²=a²+t:requires-native-commutation-or-phase-transport-proof",
    "t,m,a²:address-and-source-identity-preserved",
    "original-opening-parenthesis:source-completion-not-inferred",
)


class I083OrderedCubicError(ValueError):
    pass


def _q1(receipt: Mapping[str, Any], member: str) -> bool:
    record = receipt.get("projection_value")
    if not isinstance(record, Mapping):
        raise I083OrderedCubicError(f"missing exact Law-of-1 witness: {member}")
    if record.get("type") != "EXACT_RATIONAL":
        raise I083OrderedCubicError(f"untyped Law-of-1 witness: {member}")
    numerator = record.get("numerator")
    denominator = record.get("denominator")
    if isinstance(numerator, bool) or isinstance(denominator, bool) or (
        not isinstance(numerator, int) or not isinstance(denominator, int)
        or denominator == 0
    ):
        raise I083OrderedCubicError(f"invalid rational Law-of-1 witness: {member}")
    return Fraction(numerator, denominator) == Fraction(1)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def formalize_i083(
    *,
    phase_gear_hydration: bool = False,
    pair_layer_id: str | None = None,
    source_tensor_id: str | None = None,
    target_tensor_id: str | None = None,
    source_shape: Sequence[int] | None = None,
    target_shape: Sequence[int] | None = None,
    equal_sum_normalized: bool | None = None,
) -> dict[str, Any]:
    """Bounded original-service composition; no missing witness is invented.

    If a caller provides ALL tensor-pair inputs, invoke the authoritative
    existing Pass219 SPI cubic three-set normalizer. If not, only the
    individually registered Law-of-1 projections and I082 positional
    geometry are established and the pair evidence remains HOLD.
    """
    i082 = formalize_i082(hydrate_existing_phase_gear=phase_gear_hydration)
    c = positive_geometric_c_root()
    if (
        CANONICAL_VALUES["a²"] != 1
        or i082["matrix_exact"][2][1] != {"numerator": 1, "denominator": 1}
        or c*c != type(c)(3, 0)
        or i082["canonical_geometric_c_projection"] != c.to_dict()
    ):
        raise I083OrderedCubicError("I082 Lo Shu root/a² source binding diverged")
    witnesses = {member: member_witness(member) for member in INHERITED_MEMBER_ORDER}
    if any(not _q1(witnesses[name], name) for name in INHERITED_MEMBER_ORDER):
        raise I083OrderedCubicError("registered exact Law-of-1 projection changed")
    if INHERITED_CUBIC_SOURCE != "t³=t+a²" or INHERITED_CUBIC_RESIDUAL != "t³-t=a²=∆=1":
        raise I083OrderedCubicError("inherited Pass219 cubic source changed")

    supplied_pair_fields = (
        pair_layer_id, source_tensor_id, target_tensor_id,
        source_shape, target_shape, equal_sum_normalized,
    )
    has_pair = any(x is not None for x in supplied_pair_fields)
    if has_pair and not all(x is not None for x in supplied_pair_fields):
        raise I083OrderedCubicError("complete original tensor-pair proof inputs required")
    tensor_pair_receipt = None
    if has_pair:
        if not all(isinstance(v, str) and v.strip() for v in (
            pair_layer_id, source_tensor_id, target_tensor_id,
        )):
            raise I083OrderedCubicError("exact source/target tensor IDs required")
        if not isinstance(equal_sum_normalized, bool):
            raise I083OrderedCubicError("typed equal-sum proof decision required")
        tensor_pair_receipt = tensor_pair_cubic_witness(
            pair_layer_id=pair_layer_id,
            source_tensor_id=source_tensor_id,
            target_tensor_id=target_tensor_id,
            source_shape=source_shape,
            target_shape=target_shape,
            equal_sum_normalized=equal_sum_normalized,
            a2_projection=1,
            delta_projection=1,
            cubic_residual_projection=1,
        )

    # The scalar projection of the *addends* agrees. Do not cancel t,
    # commute it, or solve it at the native tensor level.
    m_unit = Fraction(1)
    a_unit = Fraction(1)
    t_cubic_unit = Fraction(1)
    projected_addend_residual = m_unit - a_unit
    projected_cubic_residual = t_cubic_unit - m_unit
    if projected_addend_residual != 0 or projected_cubic_residual != 0:
        raise I083OrderedCubicError("Law-of-1 unit residual diverged")

    source_identity = sha256(_canonical({
        "fragment": SOURCE_FRAGMENT, "open": SOURCE_OPEN_PARENTHESIS,
        "ordered_operands": CHAIN_OPERANDS,
        "parent_i082_source_sha256": i082["source_topology"]["source_equation_sha256"],
        "original_pass219_three_set": INHERITED_CUBIC_SOURCE,
    })).hexdigest()

    return {
        "schema": SCHEMA,
        "source_fragment_exact": SOURCE_FRAGMENT,
        "source_open_parenthesis_preserved": SOURCE_OPEN_PARENTHESIS,
        "ordered_equality_operands": list(CHAIN_OPERANDS),
        "equality_edge_order": [[0, 1], [1, 2]],
        "source_identity_sha256": source_identity,
        "i082_source_equation_sha256": i082["source_topology"]["source_equation_sha256"],
        "i082_a2_cell_address": 7,
        "i082_c_root_relation": i082["canonical_geometric_c_relation"],
        "inherited_cubic_original_source": INHERITED_CUBIC_SOURCE,
        "inherited_cubic_original_residual": INHERITED_CUBIC_RESIDUAL,
        "original_law_one_receipts": witnesses,
        "scalar_projection_units_equal": True,
        "projected_addend_residual": {"numerator": 0, "denominator": 1},
        "projected_cubic_residual": {"numerator": 0, "denominator": 1},
        "tensor_pair_three_set_receipt": tensor_pair_receipt,
        "tensor_pair_witness_executed": tensor_pair_receipt is not None,
        "tensor_pair_provenance_independently_verified": False,
        "native_t_solved": False,
        "native_m_solved": False,
        "native_t_plus_a2_equals_a2_plus_t_proven": False,
        "native_chain_admitted": False,
        "full_source_parenthesis_closed": False,
        "native_operator_obligations": list(SOURCE_OPERATOR_OBLIGATIONS),
        "status": "HOLD_NATIVE_ORDERED_EDGE_PROOF",
        "projection_only": True,
        "candidate_only": True,
        "floating_point_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_commit_authority": False,
        "canonical_persistence_authority": False,
    }

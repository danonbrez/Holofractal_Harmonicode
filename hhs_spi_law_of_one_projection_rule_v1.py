"""Pass 219 SPI — HARMONICODE Law-of-1 scalar projection invariant v1.

Operator-supplied additive rule:

    1=a²,x⁴,y⁴,z⁴,w⁴,∆,P²-pq,t³-t,m²-m,e^x²O,c²-b²,b²/2u⁷²

The rule is intentionally projection-scoped.  It does not identify the native
expressions with one another and it does not erase phase, source, ordering,
parenthesization, matrix/tensor, or equality-edge provenance.

Local law:
    every admitted Law-of-1 member projects to exact scalar 1 in a registered
    scalar-normalization layer.

Global law:
    every valid layer-to-layer normalization preserves the unit scalar:
        N[L_i -> L_j](1_Li) = 1_Lj.

Therefore any finite product of already-projected Law-of-1 values is also one.
This is a theorem about projection values only, never a license to commute or
multiply native HARMONICODE objects before projection.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

FORMAT = "HHS_SPI_LAW_OF_ONE_PROJECTION_RULE_V1"
VERSION = "1.0.0"
PROFILE = "HARMONICODE-LAW-OF-ONE-v1"
OPERATOR_SOURCE = "1=a²,x⁴,y⁴,z⁴,w⁴,∆,P²-pq,t³-t,m²-m,e^x²O,c²-b²,b²/2u⁷²"

LAW_OF_ONE_MEMBERS: Tuple[str, ...] = (
    "a²",
    "x⁴",
    "y⁴",
    "z⁴",
    "w⁴",
    "∆",
    "P²-pq",
    "t³-t",
    "m²-m",
    "e^x²O",
    "c²-b²",
    "b²/2u⁷²",
)

# xy is not inserted into the operator's source list above.  It is a conditional
# bridge into the same scalar unit class when the separately proven symmetric
# unit-product surface rule is active.
CONDITIONAL_UNIT_BRIDGES: Tuple[str, ...] = ("xy",)

EVIDENCE_KIND: Mapping[str, str] = {
    "a²": "REPOSITORY_PRIMITIVE_PROJECTION",
    "x⁴": "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM",
    "y⁴": "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM",
    "z⁴": "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM",
    "w⁴": "OPERATOR_SUPPLIED_PHASE_QUARTIC_PROJECTION_AXIOM",
    "∆": "PASS129_RATIONAL_RESIDUE_PROJECTION",
    "P²-pq": "PASS129_RATIONAL_RESIDUE_PROJECTION",
    "t³-t": "PASS129_RATIONAL_RESIDUE_PROJECTION",
    "m²-m": "PASS129_RATIONAL_RESIDUE_PROJECTION",
    "e^x²O": "OPERATOR_SUPPLIED_SOURCE_BOUND_PROJECTION_AXIOM",
    "c²-b²": "REPOSITORY_PRIMITIVE_DIFFERENCE_PROJECTION",
    "b²/2u⁷²": "OPERATOR_SUPPLIED_SOURCE_BOUND_PROJECTION_AXIOM",
    "xy": "SYMMETRIC_UNIT_PRODUCT_AND_PASS129_BRIDGE",
}

REPOSITORY_PREMISES: Mapping[str, Tuple[str, ...]] = {
    "a²": ("SPI-PROJ-0001: pi(a²)=1",),
    "∆": ("Pass129: ∆=t³-t=m²-m=xy=P²-pq, ∆!=0; rational projection gives ∆=1",),
    "P²-pq": ("SPI-T1: P²=pq+1", "Pass129 rational residue projection"),
    "t³-t": ("Pass129 common rational residue projection",),
    "m²-m": ("Pass129 common rational residue projection",),
    "c²-b²": ("SPI-PROJ-0002: pi(b²)=2", "SPI-PROJ-0003: pi(c²)=3"),
    "xy": ("SPI-O2-MATRIX: symmetric unit-product projection layer a²=xy=1", "Pass129 xy=1 unit closure"),
}


class SPILawOfOneError(ValueError):
    pass


def _exact_one() -> Fraction:
    return Fraction(1, 1)


def _exact_json(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"type": "EXACT_RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, tuple):
        return [_exact_json(v) for v in value]
    if isinstance(value, list):
        return [_exact_json(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _exact_json(value[k]) for k in sorted(value)}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise SPILawOfOneError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def member_witness(member: str, *, conditional_bridge: bool = False) -> Dict[str, Any]:
    allowed = CONDITIONAL_UNIT_BRIDGES if conditional_bridge else LAW_OF_ONE_MEMBERS
    if member not in allowed:
        kind = "conditional bridge" if conditional_bridge else "Law-of-1"
        raise SPILawOfOneError(f"{member!r} is not a registered {kind} member")
    witness: Dict[str, Any] = {
        "schema": "HHS_SPI_LAW_OF_ONE_MEMBER_WITNESS_V1",
        "profile": PROFILE,
        "operator_source": OPERATOR_SOURCE,
        "native_source_expression": member,
        "projection_value": _exact_one(),
        "projection_relation": f"pi({member})=1",
        "evidence_kind": EVIDENCE_KIND[member],
        "repository_premises": REPOSITORY_PREMISES.get(member, ()),
        "conditional_bridge": conditional_bridge,
        "projection_only": True,
        "native_identity_with_other_members": False,
        "native_commutation_authorized": False,
        "reverse_lift_status": "none",
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    witness["receipt_sha256"] = sha256(_stable_json(witness).encode("utf-8")).hexdigest()
    return _exact_json(witness)


def normalization_witness(member: str, source_layer: str, target_layer: str) -> Dict[str, Any]:
    if not source_layer or not target_layer:
        raise SPILawOfOneError("source_layer and target_layer are required")
    conditional = member in CONDITIONAL_UNIT_BRIDGES
    if member not in LAW_OF_ONE_MEMBERS and not conditional:
        raise SPILawOfOneError(f"unregistered unit member: {member!r}")
    witness = member_witness(member, conditional_bridge=conditional)
    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_LAW_OF_ONE_NORMALIZATION_WITNESS_V1",
        "profile": PROFILE,
        "member": member,
        "source_layer": source_layer,
        "target_layer": target_layer,
        "source_scalar": _exact_one(),
        "target_scalar": _exact_one(),
        "rule": "N[L_i->L_j](1_Li)=1_Lj",
        "member_receipt_sha256": witness["receipt_sha256"],
        "unit_preserved": True,
        "projection_only": True,
        "native_identity_across_layers": False,
        "canonical_admission_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)


def projected_product_witness(
    members: Sequence[str],
    *,
    layer_id: str,
    allow_conditional_bridges: bool = False,
) -> Dict[str, Any]:
    if not members:
        raise SPILawOfOneError("at least one projected member is required")
    if not layer_id:
        raise SPILawOfOneError("layer_id is required")
    member_receipts = []
    product = _exact_one()
    for member in members:
        if member in LAW_OF_ONE_MEMBERS:
            receipt = member_witness(member)
        elif allow_conditional_bridges and member in CONDITIONAL_UNIT_BRIDGES:
            receipt = member_witness(member, conditional_bridge=True)
        else:
            raise SPILawOfOneError(f"member is not admitted in this unit-product proof: {member!r}")
        member_receipts.append(receipt)
        # Multiply only already-projected exact scalar values.  Never multiply
        # or reorder native HARMONICODE expressions here.
        product *= _exact_one()
    result: Dict[str, Any] = {
        "schema": "HHS_SPI_LAW_OF_ONE_PRODUCT_WITNESS_V1",
        "profile": PROFILE,
        "layer_id": layer_id,
        "members_in_declared_order": tuple(members),
        "member_receipts": member_receipts,
        "projected_product": product,
        "unit_product": product == 1,
        "native_product_evaluated": False,
        "native_reordering_authorized": False,
        "projection_only": True,
        "canonical_admission_authority": False,
    }
    result["receipt_sha256"] = sha256(_stable_json(result).encode("utf-8")).hexdigest()
    return _exact_json(result)


def global_law_of_one_manifest(
    *,
    normalization_layers: Sequence[str] = ("LOCAL", "MATRIX_TENSOR", "RATIONAL", "MODULAR", "HYDRATION"),
) -> Dict[str, Any]:
    layers = tuple(str(layer) for layer in normalization_layers)
    if not layers or any(not layer for layer in layers):
        raise SPILawOfOneError("normalization_layers must be non-empty stable identifiers")

    members = [member_witness(member) for member in LAW_OF_ONE_MEMBERS]
    normalization_edges = []
    for i in range(len(layers) - 1):
        source_layer, target_layer = layers[i], layers[i + 1]
        # A single explicit unit edge is sufficient because member witnesses
        # establish that all admitted members enter normalization as exact 1.
        normalization_edges.append({
            "source_layer": source_layer,
            "target_layer": target_layer,
            "source_unit": _exact_one(),
            "target_unit": _exact_one(),
            "unit_preserved": True,
        })

    manifest: Dict[str, Any] = {
        "schema": "HHS_SPI_LAW_OF_ONE_GLOBAL_MANIFEST_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "operator_source": OPERATOR_SOURCE,
        "members": members,
        "member_count": len(members),
        "conditional_unit_bridges": [member_witness("xy", conditional_bridge=True)],
        "local_rule": "for every admitted member E in layer L: pi_L(E)=1_L",
        "global_rule": "for every valid normalization edge L_i->L_j: N(1_Li)=1_Lj",
        "finite_projected_product_rule": "product(pi_L(E_k))=1 for any finite admitted Law-of-1 member sequence",
        "normalization_layers": layers,
        "normalization_edges": normalization_edges,
        "symmetry_rule_link": "a complete symmetric matrix/tensor surface whose projected orbit products are unit may emit a²=xy=1",
        "projection_only": True,
        "native_member_collapse": False,
        "native_commutation_or_reassociation": False,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    manifest["manifest_sha256"] = sha256(_stable_json(manifest).encode("utf-8")).hexdigest()
    return _exact_json(manifest)

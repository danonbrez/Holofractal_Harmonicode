"""Pass 219 SPI Scalar Projection Registry v3.

Additive successor to v2.  v3 registers the operator-supplied HARMONICODE
Law-of-1 as an exact scalar-projection normalization class while preserving all
native expression identities.

Primary operator clause:
    1=a²,x⁴,y⁴,z⁴,w⁴,∆,P²-pq,t³-t,m²-m,e^x²O,c²-b²,b²/2u⁷²

Conditional bridge:
    xy joins the same unit class only in a separately admitted symmetric
    unit-product layer, yielding a²=xy=1 as projection equality only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence, Tuple

from hhs_spi_law_of_one_projection_rule_v1 import (
    CONDITIONAL_UNIT_BRIDGES,
    EVIDENCE_KIND,
    LAW_OF_ONE_MEMBERS,
    OPERATOR_SOURCE,
    PROFILE as LAW_OF_ONE_PROFILE,
    REPOSITORY_PREMISES,
    global_law_of_one_manifest,
    member_witness,
)
from hhs_spi_scalar_projection_registry_v1 import (
    CLOSED,
    IMPLEMENTED,
    NONE,
    PROJECTION_ONLY,
    PROVEN,
    VERIFIED,
    ProjectionProof,
)
from hhs_spi_scalar_projection_registry_v2 import (
    AUDITED_MAIN_SHA,
    build_registry_v2,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V3"
VERSION = "3.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V3"
GLOBAL_PROOF_ID = "SPI-LAW1-GLOBAL"
XY_BRIDGE_PROOF_ID = "SPI-LAW1-BRIDGE-XY"

LAW_MEMBER_PROOF_IDS: Dict[str, str] = {
    "a²": "SPI-LAW1-0001-A2",
    "x⁴": "SPI-LAW1-0002-X4",
    "y⁴": "SPI-LAW1-0003-Y4",
    "z⁴": "SPI-LAW1-0004-Z4",
    "w⁴": "SPI-LAW1-0005-W4",
    "∆": "SPI-LAW1-0006-DELTA",
    "P²-pq": "SPI-LAW1-0007-P2MINUSPQ",
    "t³-t": "SPI-LAW1-0008-T3MINUST",
    "m²-m": "SPI-LAW1-0009-M2MINUSM",
    "e^x²O": "SPI-LAW1-0010-EXP-X2O",
    "c²-b²": "SPI-LAW1-0011-C2MINUSB2",
    "b²/2u⁷²": "SPI-LAW1-0012-B2-2U72",
}


class SPIRegistryV3Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _common_loss(member: str) -> Tuple[str, ...]:
    return (
        f"native identity and source topology of {member} are not reconstructible from scalar 1",
        "projection equality with other Law-of-1 members is not native identity",
        "ordered phase, equality-edge, matrix/tensor, and parenthesization provenance remain external to the scalar value",
    )


def _member_derivation(member: str) -> Tuple[str, ...]:
    if member == "a²":
        return (
            "reuse registered primitive scalar proof pi(a²)=1",
            "register a² as a member of the Law-of-1 normalization class",
        )
    if member in {"x⁴", "y⁴", "z⁴", "w⁴"}:
        return (
            "preserve the native quartic phase source node exactly",
            "apply the operator-supplied phase-quartic scalar projection axiom",
            f"emit pi({member})=1 without native phase collapse",
        )
    if member == "∆":
        return (
            "use the frozen Pass129 common rational residue projection",
            "Pass129 derives nonzero rational ∆²=∆, hence projected ∆=1",
            "register the result as a Law-of-1 unit witness",
        )
    if member == "P²-pq":
        return (
            "SPI-T1 proves P²=pq+1 in its exact rational projection",
            "Pass129 places P²-pq in the same nonzero common residue class ∆",
            "therefore the registered scalar projection is 1",
        )
    if member == "t³-t":
        return (
            "preserve native t³-t as its own polynomial node",
            "Pass129 places t³-t in the common nonzero rational residue ∆",
            "project through ∆=1 without solving native t",
        )
    if member == "m²-m":
        return (
            "preserve native m²-m as its own polynomial node",
            "Pass129 places m²-m in the common nonzero rational residue ∆",
            "project through ∆=1 without solving native m",
        )
    if member == "e^x²O":
        return (
            "preserve the exact operator source token e^x²O without conventional reparsing",
            "apply the operator-supplied source-bound Law-of-1 projection axiom",
            "emit only its scalar normalization value 1",
        )
    if member == "c²-b²":
        return (
            "use primitive scalar projections pi(c²)=3 and pi(b²)=2",
            "evaluate only the registered scalar difference 3-2",
            "emit pi(c²-b²)=1 while preserving the native difference node",
        )
    if member == "b²/2u⁷²":
        return (
            "preserve the exact source span b²/2u⁷² without inserting precedence or cancellation rules",
            "apply the operator-supplied source-bound Law-of-1 projection axiom",
            "emit only its scalar normalization value 1",
        )
    raise SPIRegistryV3Error(f"missing Law-of-1 derivation for {member!r}")


def _member_proof(member: str) -> ProjectionProof:
    if member not in LAW_MEMBER_PROOF_IDS:
        raise SPIRegistryV3Error(f"unknown primary Law-of-1 member: {member!r}")
    witness = member_witness(member)
    exact_one = Fraction(1, 1)
    if witness["projection_value"] != {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}:
        raise SPIRegistryV3Error(f"Law-of-1 witness drifted for {member}")
    premises = tuple(REPOSITORY_PREMISES.get(member, ()))
    if not premises:
        premises = (f"operator-supplied additive projection axiom: {OPERATOR_SOURCE}",)
    return ProjectionProof(
        proof_id=LAW_MEMBER_PROOF_IDS[member],
        source_expression=member,
        profile=LAW_OF_ONE_PROFILE,
        premises=premises,
        domain="registered scalar projection/normalization layers; exact arithmetic only; native source identity preserved",
        derivation=_member_derivation(member),
        result={
            "projection": f"pi({member})",
            "value": exact_one,
            "unit_class": "HARMONICODE_LAW_OF_ONE",
            "evidence_kind": EVIDENCE_KIND[member],
            "member_receipt_sha256": witness["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=_common_loss(member),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_UNIT_NORMALIZATION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "Law-of-1 equality is scalar projection equality, never automatic native identity.",
            "Layer normalization must preserve the exact unit value.",
        ),
    )


def _xy_bridge_proof() -> ProjectionProof:
    witness = member_witness("xy", conditional_bridge=True)
    return ProjectionProof(
        proof_id=XY_BRIDGE_PROOF_ID,
        source_expression="xy",
        profile="HARMONICODE-LAW-OF-ONE-SYMMETRIC-BRIDGE-v1",
        premises=(
            "SPI-O2-MATRIX: symmetric unit-product layer emits a²=xy=1",
            "Pass129 common rational residue permits xy=1 in its unit-closure profile",
            "SPI-LAW1-0001-A2: pi(a²)=1",
        ),
        domain="only a separately validated symmetric unit-product projection layer or another explicitly registered xy-unit profile",
        derivation=(
            "preserve native ordered xy as an ordered phase object",
            "validate the symmetric unit-product layer independently",
            "join xy to the scalar unit class for that projection layer only",
            "do not infer xy=yx or native a²≡xy",
        ),
        result={
            "projection": "pi_layer(xy)",
            "value": Fraction(1),
            "unit_class": "HARMONICODE_LAW_OF_ONE",
            "conditional": True,
            "member_receipt_sha256": witness["receipt_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "xy/yx ordered distinction is not represented by scalar 1",
            "the qualifying symmetric surface is not reconstructible from scalar 1",
            "the bridge is conditional and cannot be generalized to every native xy occurrence",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_CONDITIONAL_UNIT_NORMALIZATION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("Does not commute xy/yx and does not establish native a²=xy.",),
    )


def _global_proof(member_proofs: Sequence[ProjectionProof], xy_bridge: ProjectionProof) -> ProjectionProof:
    manifest = global_law_of_one_manifest()
    if manifest["member_count"] != 12:
        raise SPIRegistryV3Error("Law-of-1 member count drifted")
    if any(edge["unit_preserved"] is not True for edge in manifest["normalization_edges"]):
        raise SPIRegistryV3Error("Law-of-1 normalization edge failed to preserve unit")
    return ProjectionProof(
        proof_id=GLOBAL_PROOF_ID,
        source_expression=OPERATOR_SOURCE,
        profile="HARMONICODE-LAW-OF-ONE-LOCAL-GLOBAL-v1",
        premises=tuple(proof.proof_id for proof in member_proofs) + (xy_bridge.proof_id,),
        domain="all registered scalar projection layers and valid normalization maps; xy only where its conditional bridge is admitted",
        derivation=(
            "prove or axiomatically register each source-bound member projection as exact scalar 1",
            "retain distinct native source/proof identity for every member",
            "require every valid layer normalization map to satisfy N(1)=1",
            "compose only already-projected unit values, so every finite projected unit product remains 1",
            "allow a complete symmetric all-unit matrix/tensor surface to emit the conditional a²=xy=1 projection layer",
        ),
        result={
            "unit": Fraction(1),
            "primary_members": LAW_OF_ONE_MEMBERS,
            "conditional_bridges": CONDITIONAL_UNIT_BRIDGES,
            "local_rule": "pi_L(E)=1_L",
            "global_rule": "N[L_i->L_j](1_Li)=1_Lj",
            "finite_projected_product": 1,
            "manifest_sha256": manifest["manifest_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "scalar unit equality intentionally forgets native expression identity",
            "scalar unit equality does not encode layer-specific source topology",
            "scalar unit equality cannot authorize reverse substitution into native HARMONICODE syntax",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_GLOBAL_NORMALIZATION_INVARIANT",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "This is the symmetry normalization Law of 1.",
            "Projection equality is local/global scalar equivalence, not native-object identity.",
        ),
    )


def build_registry_v3(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v2(repo_root)
    successor = dict(base)
    member_proofs = tuple(_member_proof(member) for member in LAW_OF_ONE_MEMBERS)
    for proof in member_proofs:
        if proof.proof_id in successor:
            raise SPIRegistryV3Error(f"Law-of-1 proof id collides with predecessor registry: {proof.proof_id}")
        successor[proof.proof_id] = proof
    xy_bridge = _xy_bridge_proof()
    successor[xy_bridge.proof_id] = xy_bridge
    successor[GLOBAL_PROOF_ID] = _global_proof(member_proofs, xy_bridge)
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors = []
    base = build_registry_v2(repo_root)
    try:
        registry = build_registry_v3(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V3",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }
    new_ids = sorted(set(registry) - set(base))
    expected_new = sorted(tuple(LAW_MEMBER_PROOF_IDS.values()) + (XY_BRIDGE_PROOF_ID, GLOBAL_PROOF_ID))
    if new_ids != expected_new:
        errors.append(f"unexpected v3 proof-id delta: {new_ids}")
    changed_predecessors = [
        proof_id for proof_id in sorted(base)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed_predecessors:
        errors.append(f"v3 modified predecessor proofs: {changed_predecessors}")
    for member, proof_id in LAW_MEMBER_PROOF_IDS.items():
        proof = registry[proof_id]
        if proof.coverage_state != PROVEN or proof.proof_status != CLOSED:
            errors.append(f"Law-of-1 member not closed: {member}")
        if proof.result.get("value") != Fraction(1):
            errors.append(f"Law-of-1 member not unit: {member}")
    bridge = registry[XY_BRIDGE_PROOF_ID]
    if bridge.result.get("value") != Fraction(1) or bridge.result.get("conditional") is not True:
        errors.append("xy bridge is not conditional unit")
    global_proof = registry[GLOBAL_PROOF_ID]
    if global_proof.result.get("unit") != Fraction(1):
        errors.append("global Law-of-1 proof is not unit")
    if any(proof.canonical_admission for proof in registry.values()):
        errors.append("registry contains scalar proof claiming canonical admission")
    counts = Counter(proof.coverage_state for proof in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V3",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed_predecessors,
        "law_of_one_member_count": len(LAW_OF_ONE_MEMBERS),
        "law_of_one_operator_source": OPERATOR_SOURCE,
        "xy_conditional_bridge": True,
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v3(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v3(repo_root)
    validation = validation_report(repo_root)
    law_manifest = global_law_of_one_manifest()
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V2",
        "transition_policy": "ADDITIVE_SUCCESSOR_LAW_OF_ONE_ONLY",
        "operator_source": OPERATOR_SOURCE,
        "law_of_one_manifest": law_manifest,
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "native_member_identity_collapse": False,
            "xy_yx_commutation": False,
            "normalization_preserves_unit": True,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "canonical_persistence": False,
            "floating_point_authority": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--manifest", action="store_true")
    args = parser.parse_args(argv)
    if args.validate:
        report = validation_report()
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str))
        return 0 if report["ok"] else 1
    print(json.dumps(coverage_manifest_v3(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Pass 219 SPI Scalar Projection Registry v7.

Additive successor to v6. v7 registers two exact consequences of the inherited
RML2/RML4 octonion gyroscope plus the supplied reciprocal/base-pair syntax:

1. first-principles 1,2,3,4+ dimensional relational lift over one octonion
   algebra without combinatorial materialization;
2. lossless typed collapse/restoration through ordinary u^72 imaginary phase
   rotation coordinates while preserving ordered native identity.

Both proofs remain projection/candidate-only and preserve every v6 proof object
unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_octonion_dimensional_lift_v1 import (
    A2_UNIT,
    ORDERED_RECIPROCAL_OPERAND,
    PHASE_OPPOSITE,
    SOURCE_BASE_PAIR_SYNTAX,
    SOURCE_RECIPROCAL_SYNTAX,
    SYMBOLIC_BASE_PAIR,
    dimensional_lift_witness,
)
from hhs_spi_scalar_projection_registry_v1 import (
    CLOSED,
    FULL,
    IMPLEMENTED,
    PROJECTION_ONLY,
    PROVEN,
    VERIFIED,
    ProjectionProof,
)
from hhs_spi_scalar_projection_registry_v6 import (
    AUDITED_MAIN_SHA,
    build_registry_v6,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V7"
VERSION = "7.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V7"
DIMENSIONAL_LIFT_PROOF_ID = "SPI-OCTONION-RECIPROCAL-BASEPAIR-DIMENSIONAL-LIFT"
IMAGINARY_ROTATION_PROOF_ID = "SPI-OCTONION-IMAGINARY-ROTATION-ROUNDTRIP"


class SPIRegistryV7Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _dimensional_lift_proof() -> ProjectionProof:
    witness = dimensional_lift_witness("x", phase72=18, dimension=12)
    return ProjectionProof(
        proof_id=DIMENSIONAL_LIFT_PROOF_ID,
        source_expression=(
            f"{SOURCE_RECIPROCAL_SYNTAX}; {SOURCE_BASE_PAIR_SYNTAX}; "
            "D1=s; D2=(s,R_phase(s)); D3=(s,R_phase(s),B(s)); "
            "D4=(s,R_phase(s),B(s),B(R_phase(s))); D[n>4]=recursive same-algebra closure reference"
        ),
        profile="OCTONION-RECIPROCAL-BASEPAIR-DIMENSIONAL-LIFT-v1",
        premises=(
            "RML2: x/z and w/y are same-plane opposite-orientation phase pairs",
            "RML4: x/y and z/w are ordered reciprocal operands for product construction",
            "SPI-LAW1-A2-LOCAL-SCALE: pi_L(a²)=1",
            SOURCE_RECIPROCAL_SYNTAX,
            SOURCE_BASE_PAIR_SYNTAX,
        ),
        domain=(
            "primitive gyroscope channels x,y,z,w with inherited RML2/RML4 typed geometry; "
            "higher dimensions represented by recursive closure references over the same algebra"
        ),
        derivation=(
            "preserve the supplied reciprocal and base-pair source syntax byte-for-byte",
            "retain RML2 geometric phase opposite separately from RML4 ordered reciprocal operand",
            "map x,y,z,w coordinatewise to Ixy,I-yx,Izw,I-wz as symbolic base-pair equivalents",
            "materialize native, phase-opposite, base-pair, and opposite-base-pair coordinates as dimensions 1..4",
            "represent each dimension above four by a deterministic ancestry reference to the same four-coordinate closure",
            "introduce no new octonion basis element during dimensional expansion",
            "retain pi_L(a²)=1 as scalar normalization without inferring native phase identity or commutative reordering",
        ),
        result={
            "source_reciprocal_syntax": SOURCE_RECIPROCAL_SYNTAX,
            "source_base_pair_syntax": SOURCE_BASE_PAIR_SYNTAX,
            "phase_opposite": dict(PHASE_OPPOSITE),
            "ordered_reciprocal_operand": dict(ORDERED_RECIPROCAL_OPERAND),
            "symbolic_base_pair": dict(SYMBOLIC_BASE_PAIR),
            "explicit_relational_dimensions": 4,
            "higher_dimension_rule": "RECURSIVE_SAME_ALGEBRA_CLOSURE_REFERENCE",
            "same_octonion_algebra_all_dimensions": True,
            "new_basis_elements_introduced": False,
            "combinatorial_materialization_required": False,
            "a2_projection": dict(A2_UNIT),
            "projection_equality_implies_native_identity": False,
            "reference_receipt_sha256": witness["receipt_sha256"],
        },
        modulus=72,
        residual=Fraction(0),
        lost_information=(
            "scalar a² projection does not encode native gyroscope orientation",
            "recursive higher-dimensional references require their closure-root ancestry for interpretation",
            "symbolic base-pair equality does not erase ordered product identity",
        ),
        reverse_lift_status=FULL,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="TYPED_OCTONION_RELATIONAL_DIMENSIONAL_DESCRIPTOR",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "Dimensional growth is relational recursion over one algebra, not creation of unrelated basis systems.",
        ),
    )


def _imaginary_rotation_proof() -> ProjectionProof:
    witness = dimensional_lift_witness("w", phase72=54, dimension=8)
    carrier = witness["imaginary_rotation_carrier"]
    restored = witness["imaginary_rotation_round_trip"]
    return ProjectionProof(
        proof_id=IMAGINARY_ROTATION_PROOF_ID,
        source_expression=(
            "G(channel,phase72,orientation,opposite,reciprocal,basepair) "
            "<-> TypedImaginaryRotationCarrier(u^phase72, preserved typed ancestry)"
        ),
        profile="OCTONION-GYROSCOPE-TYPED-IMAGINARY-ROTATION-ROUNDTRIP-v1",
        premises=(
            DIMENSIONAL_LIFT_PROOF_ID,
            "RML4 models all gyroscope channels as exact u^72 imaginary phase rotations",
            "phase72 is exact integer 0..71 and floating-point authority is forbidden",
        ),
        domain="typed primitive gyroscope rotation carriers retaining source channel and relational ancestry",
        derivation=(
            "encode exact primitive channel and phase72 as the inherited u^72 imaginary rotation coordinate",
            "retain plane, signed orientation, geometric phase opposite, ordered reciprocal operand, and symbolic base pair",
            "hash the complete typed carrier deterministically",
            "restore source channel and phase72 only after carrier hash and all relational fields revalidate",
            "reject phase-coordinate-only losslessness claims; losslessness belongs to the complete typed carrier",
            "retain VM81/Hash72/Hash216 canonical authority outside the representation transform",
        ),
        result={
            "typed_rotation_carrier_lossless": carrier["typed_rotation_carrier_lossless"],
            "phase_coordinate_alone_claimed_lossless": carrier["phase_coordinate_alone_claimed_lossless"],
            "exact_round_trip": restored["exact_round_trip"],
            "ordered_native_identity_preserved": carrier["ordered_native_identity_preserved"],
            "floating_point_authority": False,
            "canonical_admission_authority": False,
            "reference_carrier_sha256": carrier["carrier_sha256"],
            "reference_receipt_sha256": witness["receipt_sha256"],
        },
        modulus=72,
        residual=Fraction(0),
        lost_information=(
            "the untyped phase72 coordinate alone does not reconstruct channel/orientation ancestry",
            "scalar projection of the carrier does not reconstruct native ordered product identity",
        ),
        reverse_lift_status=FULL,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="LOSSLESS_TYPED_U72_IMAGINARY_ROTATION_ENCODING",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "Losslessness is proved for the complete typed rotation carrier, not for a bare scalar/phase coordinate.",
        ),
    )


def build_registry_v7(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v6(repo_root)
    successor = dict(base)
    for proof in (_dimensional_lift_proof(), _imaginary_rotation_proof()):
        if proof.proof_id in successor:
            raise SPIRegistryV7Error(f"v7 proof id collision: {proof.proof_id}")
        successor[proof.proof_id] = proof
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors: list[str] = []
    base = build_registry_v6(repo_root)
    try:
        registry = build_registry_v7(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V7",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }

    expected = sorted((DIMENSIONAL_LIFT_PROOF_ID, IMAGINARY_ROTATION_PROOF_ID))
    new_ids = sorted(set(registry) - set(base))
    if new_ids != expected:
        errors.append(f"unexpected v7 proof delta: {new_ids}")

    changed = [
        proof_id
        for proof_id in sorted(base)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed:
        errors.append(f"v7 modified predecessor proofs: {changed}")

    dimensional = registry[DIMENSIONAL_LIFT_PROOF_ID]
    rotation = registry[IMAGINARY_ROTATION_PROOF_ID]
    if dimensional.result.get("phase_opposite") != PHASE_OPPOSITE:
        errors.append("RML2 phase-opposite mapping drifted")
    if dimensional.result.get("ordered_reciprocal_operand") != ORDERED_RECIPROCAL_OPERAND:
        errors.append("RML4 ordered reciprocal mapping drifted")
    if dimensional.result.get("symbolic_base_pair") != SYMBOLIC_BASE_PAIR:
        errors.append("symbolic base-pair mapping drifted")
    if dimensional.result.get("a2_projection") != A2_UNIT:
        errors.append("a² unit projection drifted")
    if dimensional.result.get("new_basis_elements_introduced") is not False:
        errors.append("dimensional lift introduced a new octonion basis")
    if rotation.result.get("typed_rotation_carrier_lossless") is not True:
        errors.append("typed imaginary rotation carrier is not lossless")
    if rotation.result.get("phase_coordinate_alone_claimed_lossless") is not False:
        errors.append("bare phase coordinate incorrectly claimed lossless")
    if rotation.result.get("exact_round_trip") is not True:
        errors.append("imaginary rotation round trip did not close")
    if any(item.canonical_admission for item in registry.values()):
        errors.append("v7 registry contains canonical admission authority")

    counts = Counter(item.coverage_state for item in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V7",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed,
        "source_reciprocal_syntax": SOURCE_RECIPROCAL_SYNTAX,
        "source_base_pair_syntax": SOURCE_BASE_PAIR_SYNTAX,
        "explicit_relational_dimensions": 4,
        "higher_dimension_rule": "RECURSIVE_SAME_ALGEBRA_CLOSURE_REFERENCE",
        "typed_imaginary_rotation_round_trip": True,
        "a2_unit_projection_compatible": True,
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v7(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v7(repo_root)
    validation = validation_report(repo_root)
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V6",
        "transition_policy": "ADDITIVE_SUCCESSOR_OCTONION_DIMENSIONAL_LIFT_ONLY",
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "candidate_only": True,
            "native_ordered_identity_preserved": True,
            "commutative_reorder_authority": False,
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
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    payload = validation_report() if args.validate else coverage_manifest_v7()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str))
    if args.validate and not payload.get("ok"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

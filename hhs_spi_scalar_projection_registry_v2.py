"""Pass 219 SPI Scalar Projection Registry v2.

Additive successor to the frozen v1 registry.  The sole v1 proof-status
transition is O2.  O2 closes through two explicit HARMONICODE projection rules:

1. MATRIX/TENSOR-DEFINED SCALAR
   If an exact native equality edge defines a registered scalar S by a specific
   ordered matrix/tensor expression E and pi(S)=v is already registered, then
   this exact edge permits the downstream correspondence pi_edge(E)=v.

2. SYMMETRIC UNIT-PRODUCT LAYER
   If a complete symmetric matrix/tensor projection surface has exact unit
   product on every symmetry orbit, it may emit a new scalar layer a²=xy=1.

Neither rule promotes scalar equality to native identity, commutes xy/yx,
replaces NcalcMatrixPower, or acquires VM81/Hash72/Hash216 authority.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_ordered_matrix_projection_witness_v2 import (
    AUDITED_MAIN_SHA,
    ordered_matrix_projection_witness_v2,
)
from hhs_spi_scalar_projection_registry_v1 import (
    CLOSED,
    IMPLEMENTED,
    MISSING_PROJECTION,
    NONE,
    OPEN,
    PROJECTION_ONLY,
    PROVEN,
    SYMBOLIC,
    VERIFIED,
    ProjectionProof,
    build_registry as build_registry_v1,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V2"
VERSION = "2.2.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V2"
O2_PROFILE = "MATRIX-TENSOR-DEFINED-SCALAR+SYMMETRIC-UNIT-PRODUCT-v2"


class SPIRegistryV2Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parent


def _o2_closed_proof(repo_root: Path) -> ProjectionProof:
    witness = ordered_matrix_projection_witness_v2(repo_root)
    exact_one = {"type": "EXACT_RATIONAL", "numerator": 1, "denominator": 1}
    if witness["result"]["a²"] != exact_one or witness["result"]["xy"] != exact_one:
        raise SPIRegistryV2Error("O2 unit layer did not close at a²=xy=1")
    if witness["result"]["relation"] != "a²=xy=1":
        raise SPIRegistryV2Error("O2 unit-layer relation drifted")
    if witness["generic_matrix_tensor_scalarization_authorized"] is not False:
        raise SPIRegistryV2Error("O2 overclaimed generic matrix/tensor scalarization")
    if witness["native_a2_xy_identity_authorized"] is not False:
        raise SPIRegistryV2Error("O2 promoted projection equality to native identity")
    if witness["xy_yx_commutation_authorized"] is not False:
        raise SPIRegistryV2Error("O2 commuted xy/yx")
    if witness["canonical_admission_authority"] is not False:
        raise SPIRegistryV2Error("O2 claims canonical authority")

    matrix_definition = witness["matrix_defined_scalar_projection"]
    unit_surface = witness["symmetric_unit_product_surface"]["unit_layer_receipt"]
    return ProjectionProof(
        proof_id="SPI-O2-MATRIX",
        source_expression=matrix_definition["equality_edge_source"],
        profile=O2_PROFILE,
        premises=(
            "SPI-PROJ-0001: pi(a²)=1",
            "exact source-bound a² matrix/tensor definition edge",
            "MATRIX_TENSOR_DEFINED_SCALAR_PROJECTION-v1",
            "complete nine-cell O2 magnitude projection",
            "SYMMETRIC-UNIT-PRODUCT-LAYER-v1",
            "Pass129 rational membrane precedent: pi(xy)=1 under unit closure",
        ),
        domain=(
            "exact ordered O2 matrix/tensor definition edge plus complete symmetric unit-product projection surface; "
            "all component/orbit witnesses exact; no float; no generic matrix evaluation"
        ),
        derivation=(
            "preserve the exact ordered matrix/tensor node and its defining equality edge",
            "inherit pi(a²)=1 across that exact definition edge without host evaluation or substitution",
            "retain all eight ordered perimeter roles and the separately typed center closure",
            "derive the projected nine-cell all-ones magnitude surface",
            "verify complete transpose symmetry and unit product for every symmetry orbit",
            "apply the registered Pass129 xy-unit projection precedent",
            "emit the new projection layer a²=xy=1 with exact residual 0",
        ),
        result={
            "a²": exact_one,
            "xy": exact_one,
            "relation": "a²=xy=1",
            "relation_kind": "SCALAR_PROJECTION_LAYER_ONLY",
            "matrix_definition_profile": matrix_definition["profile"],
            "matrix_definition_receipt_sha256": matrix_definition["receipt_sha256"],
            "symmetric_unit_profile": unit_surface["profile"],
            "symmetric_unit_receipt_sha256": unit_surface["receipt_sha256"],
            "o2_witness_v2_sha256": witness["witness_sha256"],
            "generic_matrix_tensor_scalarization_authorized": False,
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "native NcalcMatrixPower/matrix/tensor object is not reconstructible from scalar 1",
            "ordered x/y/z/w/xy/yx/zw/wz topology is not encoded by the unit scalar layer",
            "native a² and native xy remain distinct typed objects",
            "xy/yx ordering and native equality-edge provenance must remain attached",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_PROJECTION_LAYER",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "A specific matrix/tensor definition may inherit its registered scalar target without evaluating the native matrix/tensor.",
            "A symmetric complete unit-product surface may emit the projection layer a²=xy=1.",
            "Neither rule implies native a²≡xy or xy=yx.",
        ),
    )


def build_registry_v2(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    root = _repo_root(repo_root)
    base = build_registry_v1()
    predecessor = base.get("SPI-O2-MATRIX")
    if predecessor is None:
        raise SPIRegistryV2Error("v1 O2 proof missing")
    if predecessor.proof_status != OPEN or predecessor.coverage_state != SYMBOLIC:
        raise SPIRegistryV2Error("v1 O2 predecessor is not frozen OPEN/SYMBOLIC")
    successor = dict(base)
    successor["SPI-O2-MATRIX"] = _o2_closed_proof(root)
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors = []
    base = build_registry_v1()
    try:
        registry = build_registry_v2(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V2",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }

    if set(registry) != set(base):
        errors.append("registry proof-id set changed")
    changed = [
        proof_id for proof_id in sorted(registry)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed != ["SPI-O2-MATRIX"]:
        errors.append(f"unexpected v1->v2 proof transitions: {changed}")
    o2 = registry["SPI-O2-MATRIX"]
    if not (
        o2.proof_status == CLOSED
        and o2.implementation_status == IMPLEMENTED
        and o2.receipt_status == VERIFIED
        and o2.coverage_state == PROVEN
        and o2.canonical_admission is False
        and o2.profile == O2_PROFILE
        and o2.result.get("relation") == "a²=xy=1"
    ):
        errors.append("O2 successor did not close exactly")
    o3 = registry["SPI-O3-PROVENANCE"]
    if o3.proof_status != OPEN or o3.coverage_state != MISSING_PROJECTION:
        errors.append("O3 changed before its proof pass")
    t3c = registry["SPI-T3C"]
    if t3c.proof_status != OPEN or t3c.coverage_state != SYMBOLIC:
        errors.append("T3C native MOD edge changed")
    if any(proof.canonical_admission for proof in registry.values()):
        errors.append("registry contains canonical admission authority")

    counts = Counter(proof.coverage_state for proof in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V2",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "changed_proof_ids": changed,
        "coverage": {
            "PROVEN": counts.get(PROVEN, 0),
            "SYMBOLIC": counts.get(SYMBOLIC, 0),
            "MISSING_PROJECTION": counts.get(MISSING_PROJECTION, 0),
        },
        "o2_profile": o2.profile,
        "o2_relation": o2.result.get("relation"),
        "o2_receipt_sha256": o2.receipt_sha256(),
        "generic_matrix_tensor_scalarization_authorized": False,
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v2(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v2(repo_root)
    validation = validation_report(repo_root)
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V1",
        "transition_policy": "ADDITIVE_SUCCESSOR_O2_ONLY",
        "projection_rules": [
            "MATRIX_TENSOR_DEFINED_SCALAR_PROJECTION-v1",
            "SYMMETRIC-UNIT-PRODUCT-LAYER-v1",
        ],
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "native_a2_xy_identity": False,
            "xy_yx_commutation": False,
            "generic_matrix_tensor_scalarization": False,
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
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if report["ok"] else 1
    print(json.dumps(coverage_manifest_v2(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

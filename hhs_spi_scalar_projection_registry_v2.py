"""Pass 219 SPI Scalar Projection Registry v2.

Additive successor to the frozen v1 registry.  The only proof-status transition
is O2: the canonical ordered matrix-power *scalar equality-chain projection*
closes through the exact O2 witness.  This does not make generic
NcalcMatrixPower calls scalar-valued and does not create canonical authority.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from hhs_spi_ordered_matrix_projection_witness_v1 import (
    AUDITED_MAIN_SHA,
    O2_EQUALITY_SOURCE,
    ordered_matrix_projection_witness,
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
VERSION = "2.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V2"
O2_PROFILE = "SPI-O2-ORDERED-MATRIX-EQUALITY-Q-v2"


class SPIRegistryV2Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _repo_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if root is not None else Path(__file__).resolve().parent


def _o2_closed_proof(repo_root: Path) -> ProjectionProof:
    witness = ordered_matrix_projection_witness(repo_root)
    if witness["scalar_value_complete_for_o2_profile"] is not True:
        raise SPIRegistryV2Error("O2 witness did not close its bounded scalar profile")
    if witness["ncalc_matrix_power_generic_family_complete"] is not False:
        raise SPIRegistryV2Error("O2 witness overclaimed the generic NcalcMatrixPower family")
    if witness["canonical_admission_authority"] is not False:
        raise SPIRegistryV2Error("O2 witness claims canonical authority")

    return ProjectionProof(
        proof_id="SPI-O2-MATRIX",
        source_expression=O2_EQUALITY_SOURCE,
        profile=O2_PROFILE,
        premises=(
            "SPI-PROJ-0001",
            "SPI-PROJ-0002",
            "SPI-PROJ-0004",
            "SPI-T6-SURD",
            "I121.8 exact ordered phase-projection witness",
            "Phase12 ordered symbolic relation-role lift",
            "inherited native center 0/0=u^0 mod(u^72)=1 closure",
        ),
        domain=(
            "canonical Pass219 O2 equality-chain projection; exact ordered matrix source; "
            "eight frozen u72 perimeter correspondences; separately typed native center closure; "
            "no host NcalcMatrixPower evaluation"
        ),
        derivation=(
            "preserve the exact 139-byte ordered NcalcMatrixPower source and its noncommutative role order",
            "witness all eight perimeter numerator/denominator phase differences as 0 mod 72 without commuting roles",
            "witness the center separately through the inherited native 0/0=u^0 mod(u^72)=1 constraint-intersection closure",
            "retain NcalcMatrixPower(...,4) as an EXACT_SYMBOLIC_MATRIX_POWER node; do not replace it by host matrix arithmetic",
            "project b⁴ from b²=2 as (b²)²=4 without choosing a sign for b",
            "use the intact equality chain to bind the matrix branch to the independently exact SPI-T6-SURD squared-radical a² projection",
            "SPI-T6-SURD gives a²->1 with exact residual 0; therefore the bounded O2 matrix branch scalar correspondence is 1 with residual 0",
        ),
        result={
            "matrix_branch_projection": witness["result"]["matrix_branch_projection"],
            "a_squared_projection": witness["result"]["a_squared_projection"],
            "ordered_outer_cell_count": witness["ordered_matrix_lift"]["outer_cell_count"],
            "all_nine_projection_cells_witnessed": witness["ordered_matrix_lift"]["all_nine_projection_cells_witnessed"],
            "ncalc_matrix_power_host_evaluated": False,
            "generic_ncalc_matrix_power_family_complete": False,
            "o2_witness_sha256": witness["witness_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "native NcalcMatrixPower runtime object is retained rather than reconstructed from scalar 1",
            "ordered x/y/z/w/xy/yx/zw/wz role identity is lost by the terminal scalar projection unless ancestry is retained",
            "native center 0/0 closure context cannot be reverse-lifted from scalar 1",
            "the equality-chain projection does not authorize generic NcalcMatrixPower evaluation or substitution",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_EQUALITY_CHAIN_PROJECTION",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=(
            "O2 scalar projection closure is narrower than the generic NcalcMatrixPower function family.",
            "Projection equality is not native identity.",
        ),
    )


def build_registry_v2(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    root = _repo_root(repo_root)
    base = build_registry_v1()
    predecessor = base.get("SPI-O2-MATRIX")
    if predecessor is None:
        raise SPIRegistryV2Error("v1 O2 proof missing")
    if predecessor.proof_status != OPEN or predecessor.coverage_state != SYMBOLIC:
        raise SPIRegistryV2Error("v1 O2 predecessor is not the frozen OPEN/SYMBOLIC proof")
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
        "o2_receipt_sha256": o2.receipt_sha256(),
        "o2_generic_ncalc_family_complete": False,
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
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "generic_ncalc_matrix_power_execution": False,
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

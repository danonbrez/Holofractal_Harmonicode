"""Pass 219 SPI Scalar Projection Registry v4.

Additive successor to v3.  v4 makes the Law-of-1 normalization hierarchy
explicit:

    universal scalar denominator: D_univ := pi(∆) = 1
    local scalar scale:            S_L    := pi_L(a²) = pi_L(∆) = 1

Thus ``∆=1`` is the system-wide denominator unit for scalar projection and
normalization, while ``a²=∆`` is the layer-local scaling bridge.  Both are
projection relations only; native ``a²`` and native ``∆`` remain distinct
source nodes with distinct proof ancestry.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_law_of_one_projection_rule_v1 import (
    LOCAL_GLOBAL_SCALE_BRIDGE,
    LOCAL_SCALE_SYMBOL,
    OPERATOR_SOURCE,
    PROFILE as LAW_OF_ONE_PROFILE,
    UNIVERSAL_DENOMINATOR_SYMBOL,
    global_law_of_one_manifest,
    local_scale_witness,
    scale_bridge_witness,
    universal_denominator_witness,
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
from hhs_spi_scalar_projection_registry_v3 import (
    AUDITED_MAIN_SHA,
    GLOBAL_PROOF_ID,
    LAW_MEMBER_PROOF_IDS,
    build_registry_v3,
)

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V4"
VERSION = "4.0.0"
SCHEMA = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_MANIFEST_V4"
DELTA_DENOMINATOR_PROOF_ID = "SPI-LAW1-DELTA-UNIVERSAL-DENOMINATOR"
A2_LOCAL_SCALE_PROOF_ID = "SPI-LAW1-A2-LOCAL-SCALE"
HIERARCHY_PROOF_ID = "SPI-LAW1-UNIT-HIERARCHY"


class SPIRegistryV4Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _delta_denominator_proof() -> ProjectionProof:
    witness = universal_denominator_witness(1, layer_id="SYSTEM-WIDE-SCALAR-NORMALIZATION")
    exact_one = Fraction(1)
    return ProjectionProof(
        proof_id=DELTA_DENOMINATOR_PROOF_ID,
        source_expression="∆",
        profile="HARMONICODE-DELTA-UNIVERSAL-DENOMINATOR-v1",
        premises=(
            f"{LAW_MEMBER_PROOF_IDS['∆']}: pi(∆)=1",
            "Pass129 nonzero rational residue projection gives ∆=1",
            f"{GLOBAL_PROOF_ID}: Law-of-1 unit preserved across scalar normalization layers",
        ),
        domain="all registered HARMONICODE scalar projection and normalization layers",
        derivation=(
            "retain native ∆ as its own typed source node",
            "use the registered exact scalar projection pi(∆)=1",
            "declare projected ∆ as the denominator identity for scalar normalization",
            "normalize any exact projected scalar v by v/pi(∆)=v/1=v",
            "do not execute or infer native division by ∆ from this scalar rule",
        ),
        result={
            "symbol": UNIVERSAL_DENOMINATOR_SYMBOL,
            "projection": exact_one,
            "role": "SYSTEM_WIDE_UNIVERSAL_DENOMINATOR_UNIT",
            "normalization_rule": "UniversalNormalize_L(v)=v/pi_L(∆)=v",
            "witness_receipt_sha256": witness["receipt_sha256"],
            "value_preserving": True,
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "native ∆ source identity is not represented by scalar 1",
            "the scalar denominator role does not encode every native syntactic position of ∆",
            "reverse substitution of scalar 1 into native ∆ is not authorized",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_UNIVERSAL_DENOMINATOR_UNIT",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("∆=1 is universal only for registered scalar projection/normalization semantics.",),
    )


def _a2_local_scale_proof() -> ProjectionProof:
    witness = local_scale_witness(1, layer_id="GENERIC-LOCAL-SCALAR-LAYER")
    bridge = scale_bridge_witness("GENERIC-LOCAL-SCALAR-LAYER")
    exact_one = Fraction(1)
    return ProjectionProof(
        proof_id=A2_LOCAL_SCALE_PROOF_ID,
        source_expression="a²=∆",
        profile="HARMONICODE-A2-LOCAL-SCALE-BRIDGE-v1",
        premises=(
            f"{LAW_MEMBER_PROOF_IDS['a²']}: pi(a²)=1",
            DELTA_DENOMINATOR_PROOF_ID,
            "Law-of-1 scalar bridge a²=∆=1",
        ),
        domain="each registered local scalar projection layer L where both a² and ∆ unit projections are admitted",
        derivation=(
            "retain native a² and native ∆ as distinct typed source nodes",
            "bind the local scale S_L to pi_L(a²)=1",
            "bind the universal denominator to pi_L(∆)=1",
            "register the scalar bridge pi_L(a²)=pi_L(∆)=1",
            "normalize local projected scalar v through v/pi_L(a²)=v before or while joining the universal ∆ denominator layer",
        ),
        result={
            "local_scale_symbol": LOCAL_SCALE_SYMBOL,
            "local_scale": exact_one,
            "universal_denominator_symbol": UNIVERSAL_DENOMINATOR_SYMBOL,
            "universal_denominator": exact_one,
            "bridge": LOCAL_GLOBAL_SCALE_BRIDGE,
            "local_normalization_rule": "LocalNormalize_L(v)=v/pi_L(a²)=v",
            "local_witness_receipt_sha256": witness["receipt_sha256"],
            "bridge_receipt_sha256": bridge["receipt_sha256"],
            "native_a2_delta_identity_authorized": False,
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "native distinction between a² and ∆ is intentionally preserved outside the scalar bridge",
            "local layer topology is not reconstructible from scale value 1",
            "scalar scale equality does not provide reverse native substitution",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_LOCAL_SCALE_UNIT",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("a²=∆ is a scalar scaling bridge, not native node identity.",),
    )


def _hierarchy_proof() -> ProjectionProof:
    manifest = global_law_of_one_manifest()
    exact_one = Fraction(1)
    if manifest["universal_denominator"]["symbol"] != "∆":
        raise SPIRegistryV4Error("global manifest lost universal ∆ denominator")
    if manifest["local_scale"]["symbol"] != "a²":
        raise SPIRegistryV4Error("global manifest lost local a² scale")
    if manifest["local_scale"]["bridge"] != "a²=∆=1":
        raise SPIRegistryV4Error("global manifest lost a²=∆=1 bridge")
    return ProjectionProof(
        proof_id=HIERARCHY_PROOF_ID,
        source_expression="∆=1; a²=∆",
        profile="HARMONICODE-LAW-OF-ONE-UNIT-HIERARCHY-v1",
        premises=(DELTA_DENOMINATOR_PROOF_ID, A2_LOCAL_SCALE_PROOF_ID, GLOBAL_PROOF_ID),
        domain="registered local/global scalar projection and normalization graph",
        derivation=(
            "establish ∆=1 as the universal scalar denominator identity",
            "establish a²=∆=1 as the local scale-to-universal-unit projection bridge",
            "normalize within each local layer by a²",
            "normalize and compose across layers through ∆",
            "because both projected units are exact one, local and global normalization preserve every already projected exact scalar value",
        ),
        result={
            "universal_denominator": {"symbol": "∆", "value": exact_one},
            "local_scale": {"symbol": "a²", "value": exact_one},
            "bridge": "a²=∆=1",
            "local_normalization": "v/a² -> v/1 -> v in scalar projection",
            "global_normalization": "v/∆ -> v/1 -> v in scalar projection",
            "composition_rule": "local-scale normalization composes into universal-denominator normalization without scalar drift",
            "manifest_sha256": manifest["manifest_sha256"],
        },
        modulus=None,
        residual=Fraction(0),
        lost_information=(
            "native a² and ∆ identities remain distinct",
            "native layer topology is not encoded by the scalar unit hierarchy",
            "the hierarchy does not authorize native cancellation or division rewrites",
        ),
        reverse_lift_status=NONE,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type="EXACT_RATIONAL_NORMALIZATION_HIERARCHY",
        authority=PROJECTION_ONLY,
        canonical_admission=False,
        notes=("Universal denominator and local scale are roles of the shared scalar unit, not native aliases.",),
    )


def build_registry_v4(repo_root: str | Path | None = None) -> Dict[str, ProjectionProof]:
    base = build_registry_v3(repo_root)
    successor = dict(base)
    for proof in (_delta_denominator_proof(), _a2_local_scale_proof(), _hierarchy_proof()):
        if proof.proof_id in successor:
            raise SPIRegistryV4Error(f"v4 proof id collision: {proof.proof_id}")
        successor[proof.proof_id] = proof
    return successor


def validation_report(repo_root: str | Path | None = None) -> Dict[str, Any]:
    errors = []
    base = build_registry_v3(repo_root)
    try:
        registry = build_registry_v4(repo_root)
    except Exception as exc:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V4",
            "ok": False,
            "errors": [f"{type(exc).__name__}: {exc}"],
            "canonical_admission_authority": False,
        }
    expected = sorted((DELTA_DENOMINATOR_PROOF_ID, A2_LOCAL_SCALE_PROOF_ID, HIERARCHY_PROOF_ID))
    new_ids = sorted(set(registry) - set(base))
    if new_ids != expected:
        errors.append(f"unexpected v4 proof delta: {new_ids}")
    changed_predecessors = [
        proof_id for proof_id in sorted(base)
        if registry[proof_id].to_dict() != base[proof_id].to_dict()
    ]
    if changed_predecessors:
        errors.append(f"v4 modified predecessor proofs: {changed_predecessors}")
    delta = registry[DELTA_DENOMINATOR_PROOF_ID]
    scale = registry[A2_LOCAL_SCALE_PROOF_ID]
    hierarchy = registry[HIERARCHY_PROOF_ID]
    if delta.result.get("projection") != Fraction(1):
        errors.append("∆ universal denominator is not exact unit")
    if scale.result.get("local_scale") != Fraction(1) or scale.result.get("universal_denominator") != Fraction(1):
        errors.append("a² local scale bridge is not unit/unit")
    if scale.result.get("bridge") != "a²=∆=1":
        errors.append("a²/∆ bridge drifted")
    if hierarchy.result.get("bridge") != "a²=∆=1":
        errors.append("unit hierarchy bridge drifted")
    if any(proof.canonical_admission for proof in registry.values()):
        errors.append("v4 registry contains canonical admission authority")
    counts = Counter(proof.coverage_state for proof in registry.values())
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_VALIDATION_V4",
        "ok": not errors,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "proof_count": len(registry),
        "new_proof_ids": new_ids,
        "changed_predecessor_proof_ids": changed_predecessors,
        "universal_denominator": "∆=1",
        "local_scale_bridge": "a²=∆=1",
        "coverage": dict(sorted(counts.items())),
        "canonical_admission_authority": False,
        "errors": errors,
    }


def coverage_manifest_v4(repo_root: str | Path | None = None) -> Dict[str, Any]:
    registry = build_registry_v4(repo_root)
    validation = validation_report(repo_root)
    law_manifest = global_law_of_one_manifest()
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "predecessor_format": "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V3",
        "transition_policy": "ADDITIVE_SUCCESSOR_DELTA_DENOMINATOR_A2_LOCAL_SCALE_ONLY",
        "operator_source": OPERATOR_SOURCE,
        "law_of_one_manifest": law_manifest,
        "normalization_hierarchy": {
            "universal_denominator": "∆=1",
            "local_scale_bridge": "a²=∆=1",
            "native_a2_delta_identity": False,
        },
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
        "validation": validation,
        "authority_boundary": {
            "projection_only": True,
            "native_a2_delta_identity": False,
            "native_member_identity_collapse": False,
            "native_division_rewrite": False,
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
    print(json.dumps(coverage_manifest_v4(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

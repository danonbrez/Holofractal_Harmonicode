"""
Pass 219 — SPI repository corpus projection reconciliation v1.

Consumes the conservative corpus census produced by
``hhs_spi_scalar_projection_corpus_v1`` and resolves every current
MISSING_PROJECTION expression family into either:

* a source-bound exact/parametric projection proof (PROVEN), or
* an explicitly registered symbolic/parser-limit profile (SYMBOLIC).

This is an overlay. It does not rewrite the raw census, native HARMONICODE
source, parser AST, VM81 state, or canonical Hash72/Hash216 lineage.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping

from hhs_spi_scalar_projection_registry_v1 import (
    AUDITED_MAIN_SHA,
    MISSING_PROJECTION,
    PROVEN,
    SYMBOLIC,
    UNSUPPORTED_DOMAIN,
)
from hhs_spi_scalar_projection_corpus_v1 import repository_coverage_manifest

FORMAT = "HHS_SPI_CORPUS_PROJECTION_RECONCILIATION_V1"
VERSION = "1.0.0"
EXPECTED_BASE_MANIFEST_SHA256 = "fc421b2f84d7186693ba02e40515d7dcf471efe4fd6ade3b3a3ab662e36ef5a7"

PROFILES: Dict[str, Dict[str, Any]] = {
    "(pq+u⁷²)^x": {
        "projection_id": "SPI-CORPUS-LEXICAL-PARTIAL-ROOT-EXP-v1",
        "coverage_state": SYMBOLIC,
        "result": None,
        "profile": "PARSER-LIMIT-WITNESS-v1",
        "premises": ("raw source span retained",),
        "derivation": (
            "scanner sees a prefix of √(pq+u⁷²)^x²",
            "do not infer the complete exponent from a partial lexical match",
        ),
        "lost_information": ("complete nested exponent AST unavailable in parser v1",),
        "notes": ("Parser limitation, not an algebraic scalar failure.",),
    },
    "I^2": {
        "projection_id": "SPI-CORPUS-I2-PHASE-v1",
        "coverage_state": SYMBOLIC,
        "result": {"phase_class": "I^2"},
        "profile": "FORMAL-QUARTIC-PHASE-v1",
        "premises": ("ordered formal I phase basis retained",),
        "derivation": ("retain I^2 as a formal phase-basis class",),
        "lost_information": ("no Q-valued scalar magnitude is asserted",),
        "notes": ("Does not identify formal I with host-language complex i.",),
    },
    "I^3": {
        "projection_id": "SPI-CORPUS-I3-PHASE-v1",
        "coverage_state": SYMBOLIC,
        "result": {"phase_class": "I^3"},
        "profile": "FORMAL-QUARTIC-PHASE-v1",
        "premises": ("ordered formal I phase basis retained",),
        "derivation": ("retain I^3 as a formal phase-basis class",),
        "lost_information": ("no Q-valued scalar magnitude is asserted",),
        "notes": ("Does not identify formal I with host-language complex i.",),
    },
    "I^4": {
        "projection_id": "SPI-CORPUS-I4-UNIT-v1",
        "coverage_state": PROVEN,
        "result": 1,
        "profile": "DYADIC-QUARTIC-PHASE-UNIT-v1",
        "premises": ("Pass 191 QUARTIC_CYCLE projection: I^4==1==16/16",),
        "derivation": ("I^4 -> 16/16", "16/16 -> 1"),
        "lost_information": ("formal phase orientation/class is collapsed to the unit scalar",),
        "notes": ("Projection equality is not native identity.",),
    },
    "P^2": {
        "projection_id": "SPI-CORPUS-P2-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(P)^2"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(P) when this projection is selected",),
        "derivation": ("Power(P,2) -> Power(pi(P),2)",),
        "lost_information": ("native P coordinate/type and lattice ancestry",),
        "notes": ("Parametric projection; no particular P value is assigned.",),
    },
    "P²": {
        "projection_id": "SPI-CORPUS-P2-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(P)^2"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(P) when this projection is selected",),
        "derivation": ("Power(P,2) -> Power(pi(P),2)",),
        "lost_information": ("native P coordinate/type and lattice ancestry",),
        "notes": ("Unicode source spelling preserves the same source-bound exponent 2.",),
    },
    "P^3": {
        "projection_id": "SPI-CORPUS-P3-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(P)^3"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(P) when this projection is selected",),
        "derivation": ("Power(P,3) -> Power(pi(P),3)",),
        "lost_information": ("native P coordinate/type and lattice ancestry",),
        "notes": ("Compatible with, but not a substitute for, SPI-T3B-I.",),
    },
    "P³": {
        "projection_id": "SPI-CORPUS-P3-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(P)^3"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(P) when this projection is selected",),
        "derivation": ("Power(P,3) -> Power(pi(P),3)",),
        "lost_information": ("native P coordinate/type and lattice ancestry",),
        "notes": ("Unicode source spelling preserves the same source-bound exponent 3.",),
    },
    "b^(2c^2)": {
        "projection_id": "SPI-CORPUS-B-2C2-v1",
        "coverage_state": PROVEN,
        "result": 8,
        "profile": "PRIMITIVE-EVEN-POWER-Q-v1",
        "premises": ("b² -> 2", "c² -> 3"),
        "derivation": (
            "2c² -> 2*3 -> 6",
            "b^(2c²) -> b^6",
            "b^6=(b²)^3 -> 2^3 -> 8",
        ),
        "lost_information": ("native power-node ancestry beyond retained source span",),
        "notes": ("No sign choice for b is required because the exponent is even.",),
    },
    "c^b": {
        "projection_id": "SPI-CORPUS-LEXICAL-PARTIAL-CHAIN-POWER-v1",
        "coverage_state": SYMBOLIC,
        "result": None,
        "profile": "PARSER-LIMIT-WITNESS-v1",
        "premises": ("raw source span retained",),
        "derivation": (
            "scanner prefix c^b occurs inside canonical c^b^4 source",
            "do not choose exponent associativity from the partial lexeme",
        ),
        "lost_information": ("complete chained-power AST unavailable in parser v1",),
        "notes": ("The enclosing 5184 proof remains independently registered.",),
    },
    "m^2": {
        "projection_id": "SPI-CORPUS-M2-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(m)^2"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(m) when this projection is selected",),
        "derivation": ("Power(m,2) -> Power(pi(m),2)",),
        "lost_information": ("native m is not solved as a rational/real/complex value",),
        "notes": ("Structural scalar correspondence only; compatible with SPI-T3A.",),
    },
    "t^3": {
        "projection_id": "SPI-CORPUS-T3-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(t)^3"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(t) when this projection is selected",),
        "derivation": ("Power(t,3) -> Power(pi(t),3)",),
        "lost_information": ("native t is not solved as a rational/real/complex value",),
        "notes": ("Structural scalar correspondence only; compatible with SPI-T3A.",),
    },
    "t³": {
        "projection_id": "SPI-CORPUS-T3-v1",
        "coverage_state": PROVEN,
        "result": {"parametric": "pi(t)^3"},
        "profile": "STRUCTURAL-INTEGER-POWER-Q-v1",
        "premises": ("registered scalar coordinate pi(t) when this projection is selected",),
        "derivation": ("Power(t,3) -> Power(pi(t),3)",),
        "lost_information": ("native t is not solved as a rational/real/complex value",),
        "notes": ("Unicode source spelling; structural correspondence only.",),
    },
    "u^360": {
        "projection_id": "SPI-CORPUS-U360-UNIT-v1",
        "coverage_state": PROVEN,
        "result": 1,
        "profile": "U72-MULTIPLE-PHASE-UNIT-v1",
        "premises": ("SPI-T6: pi(u^72)=1",),
        "derivation": ("360=5*72", "u^360=(u^72)^5", "1^5=1"),
        "lost_information": ("native u phase address/cycle index",),
        "notes": ("Projection closure only; source Mod envelopes remain separately typed.",),
    },
    "x^2": {
        "projection_id": "SPI-CORPUS-X2-PHASE-v1",
        "coverage_state": SYMBOLIC,
        "result": {"formal": "x^2"},
        "profile": "ORDERED-PHASE-SQUARE-v1",
        "premises": ("x remains a native ordered phase carrier",),
        "derivation": ("preserve squared phase coordinate without assigning scalar magnitude",),
        "lost_information": ("Q-valued magnitude is intentionally not supplied",),
        "notes": ("No scalar x value is inferred.",),
    },
    "x²": {
        "projection_id": "SPI-CORPUS-X2-PHASE-v1",
        "coverage_state": SYMBOLIC,
        "result": {"formal": "x^2"},
        "profile": "ORDERED-PHASE-SQUARE-v1",
        "premises": ("x remains a native ordered phase carrier",),
        "derivation": ("preserve squared phase coordinate without assigning scalar magnitude",),
        "lost_information": ("Q-valued magnitude is intentionally not supplied",),
        "notes": ("Unicode source spelling; no scalar x value is inferred.",),
    },
}


class SPIReconciliationError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def validate_profiles(profiles: Mapping[str, Mapping[str, Any]] = PROFILES) -> Dict[str, Any]:
    errors = []
    for expression, profile in profiles.items():
        if not expression:
            errors.append("empty expression profile")
        if profile.get("coverage_state") not in {PROVEN, SYMBOLIC, UNSUPPORTED_DOMAIN}:
            errors.append(f"{expression}: invalid resolved coverage state")
        if not profile.get("projection_id"):
            errors.append(f"{expression}: missing projection_id")
        if not profile.get("profile"):
            errors.append(f"{expression}: missing profile")
        if not profile.get("lost_information"):
            errors.append(f"{expression}: lost_information is mandatory")
        if profile.get("canonical_admission", False):
            errors.append(f"{expression}: reconciliation profile claims canonical admission")
    return {
        "schema": "HHS_SPI_CORPUS_RECONCILIATION_PROFILE_VALIDATION_V1",
        "ok": not errors,
        "errors": errors,
        "profile_count": len(profiles),
        "canonical_admission_authority": False,
    }


def reconciliation_manifest(repo_root: Path) -> Dict[str, Any]:
    base = repository_coverage_manifest(Path(repo_root))
    profile_validation = validate_profiles()
    if not profile_validation["ok"]:
        raise SPIReconciliationError(str(profile_validation["errors"]))
    if base["manifest_sha256"] != EXPECTED_BASE_MANIFEST_SHA256:
        raise SPIReconciliationError(
            "base corpus manifest changed; repair/re-audit reconciliation profiles before reuse"
        )

    missing_by_expression = {
        group["expression"]: group
        for group in base["missing_projection_groups"]
    }
    missing_expressions = set(missing_by_expression)
    profile_expressions = set(PROFILES)
    absent_profiles = sorted(missing_expressions - profile_expressions)
    stale_profiles = sorted(profile_expressions - missing_expressions)

    resolutions = []
    resolved_counts = Counter(base["candidate_counts"])
    for expression in sorted(missing_expressions & profile_expressions):
        group = missing_by_expression[expression]
        profile = dict(PROFILES[expression])
        count = int(group["count"])
        resolved_counts[MISSING_PROJECTION] -= count
        resolved_counts[profile["coverage_state"]] += count
        resolution = {
            "expression": expression,
            "occurrence_count": count,
            "paths": group["paths"],
            "spans": group["spans"],
            **profile,
            "canonical_admission": False,
        }
        resolution["resolution_receipt_sha256"] = _digest(resolution)
        resolutions.append(resolution)

    counts = {
        state: int(resolved_counts.get(state, 0))
        for state in (PROVEN, SYMBOLIC, UNSUPPORTED_DOMAIN, MISSING_PROJECTION)
    }
    manifest = {
        "schema": "HHS_SPI_REPOSITORY_CORPUS_RECONCILIATION_MANIFEST_V1",
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "base_corpus_manifest_sha256": base["manifest_sha256"],
        "base_candidate_counts": base["candidate_counts"],
        "profile_validation": profile_validation,
        "resolution_profile_count": len(PROFILES),
        "resolutions": resolutions,
        "absent_profiles": absent_profiles,
        "stale_profiles": stale_profiles,
        "resolved_candidate_counts": counts,
        "classification_complete": not absent_profiles and counts[MISSING_PROJECTION] == 0,
        "scalar_value_complete": (
            not absent_profiles
            and counts[MISSING_PROJECTION] == 0
            and counts[SYMBOLIC] == 0
            and counts[UNSUPPORTED_DOMAIN] == 0
        ),
        "open_symbolic_occurrence_count": counts[SYMBOLIC],
        "coverage_policy": {
            "raw_census_is_immutable_input": True,
            "reconciliation_is_overlay_only": True,
            "parser_limit_profiles_do_not_assert_algebra": True,
            "projection_equality_is_not_native_identity": True,
        },
        "authority_boundary": {
            "projection_only": True,
            "canonical_admission_authority": False,
            "native_source_rewriting": False,
            "ordered_product_commutation": False,
            "hash72_hash216_canonical_minting": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def validate_reconciliation(repo_root: Path) -> Dict[str, Any]:
    try:
        manifest = reconciliation_manifest(repo_root)
    except (OSError, SPIReconciliationError) as exc:
        return {
            "schema": "HHS_SPI_CORPUS_RECONCILIATION_VALIDATION_V1",
            "ok": False,
            "errors": [str(exc)],
            "canonical_admission_authority": False,
        }
    errors = []
    if manifest["absent_profiles"]:
        errors.append(f"unreconciled missing expressions: {manifest['absent_profiles']}")
    if manifest["stale_profiles"]:
        errors.append(f"stale reconciliation profiles: {manifest['stale_profiles']}")
    if manifest["resolved_candidate_counts"][MISSING_PROJECTION] != 0:
        errors.append("MISSING_PROJECTION remains after reconciliation")
    if not manifest["classification_complete"]:
        errors.append("classification coverage is not complete")
    return {
        "schema": "HHS_SPI_CORPUS_RECONCILIATION_VALIDATION_V1",
        "ok": not errors,
        "errors": errors,
        "base_corpus_manifest_sha256": manifest["base_corpus_manifest_sha256"],
        "resolved_candidate_counts": manifest["resolved_candidate_counts"],
        "classification_complete": manifest["classification_complete"],
        "scalar_value_complete": manifest["scalar_value_complete"],
        "open_symbolic_occurrence_count": manifest["open_symbolic_occurrence_count"],
        "manifest_sha256": manifest["manifest_sha256"],
        "canonical_admission_authority": False,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile SPI repository corpus scalar projection coverage")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument(
        "--require-scalar-values",
        action="store_true",
        help="fail unless every classified candidate has a scalar value rather than a symbolic profile",
    )
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    if args.manifest:
        print(json.dumps(reconciliation_manifest(root), indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    result = validate_reconciliation(root)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result["ok"]:
        return 1
    if args.require_scalar_values and not result["scalar_value_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

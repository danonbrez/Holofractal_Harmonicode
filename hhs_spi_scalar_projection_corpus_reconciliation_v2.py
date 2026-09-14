"""SPI corpus reconciliation v2 with nested-expression AST provenance.

This successor preserves the v1 scalar classification counts while replacing the
five parser-limit occurrence witnesses with exact source-spanned AST bindings.
It closes a syntax/provenance gap only. It does not invent scalar values,
select chained-power associativity, or acquire VM81 admission authority.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_scalar_projection_corpus_ast_binding_v2 import (
    EXPECTED_RECONCILIATION_V1_SHA256,
    TARGETS,
    binding_manifest,
)
from hhs_spi_scalar_projection_corpus_reconciliation_v1 import reconciliation_manifest

FORMAT = "HHS_SPI_CORPUS_PROJECTION_RECONCILIATION_V2"
VERSION = "2.0.0"
SCHEMA = "HHS_SPI_REPOSITORY_CORPUS_RECONCILIATION_MANIFEST_V2"


class SPIReconciliationV2Error(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def reconciliation_manifest_v2(repo_root: Path) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    predecessor = reconciliation_manifest(repo_root)
    if predecessor["manifest_sha256"] != EXPECTED_RECONCILIATION_V1_SHA256:
        raise SPIReconciliationV2Error("v1 reconciliation drifted")

    binding = binding_manifest(repo_root)
    if not binding["syntax_binding_complete"]:
        raise SPIReconciliationV2Error(str(binding["errors"]))

    bindings_by_expression: Dict[str, list[Dict[str, Any]]] = {}
    for item in binding["bindings"]:
        bindings_by_expression.setdefault(item["expression"], []).append(item)

    resolutions = []
    migrated_families = 0
    for old in predecessor["resolutions"]:
        expression = old["expression"]
        if expression not in TARGETS:
            resolutions.append(dict(old))
            continue
        migrated_families += 1
        target = TARGETS[expression]
        ast_bindings = sorted(
            bindings_by_expression.get(expression, []),
            key=lambda item: (item["path"], item["raw_candidate_span"]["start"]),
        )
        if len(ast_bindings) != int(old["occurrence_count"]):
            raise SPIReconciliationV2Error(f"{expression}: AST binding count mismatch")
        kinds = sorted({item["ast_node_kind"] for item in ast_bindings})
        source_forms = sorted({item["ast_source_text"] for item in ast_bindings})
        migrated: Dict[str, Any] = {
            "expression": expression,
            "occurrence_count": int(old["occurrence_count"]),
            "paths": list(old["paths"]),
            "spans": list(old["spans"]),
            "coverage_state": "SYMBOLIC",
            "projection_id": target["new_projection_id"],
            "profile": target["new_profile"],
            "result": {
                "syntax_node_kinds": kinds,
                "enclosing_source_forms": source_forms,
                "scalar_value": "UNRESOLVED",
            },
            "premises": [
                "raw v1 candidate span retained",
                "exact enclosing nested-expression AST v2 node bound by source containment",
            ],
            "derivation": [
                "locate the predecessor candidate span without rewriting source",
                "bind it to the shortest authorized enclosing AST node kind",
                "retain complete enclosing source and ordered operand identity",
                "leave scalar evaluation unresolved",
            ],
            "lost_information": [
                "scalar value/domain remains unassigned",
                "native runtime identity is not replaced by projection syntax",
            ],
            "notes": [
                "The predecessor parser-limit condition is closed.",
                "Syntax closure is not scalar-value closure and is not native identity.",
            ],
            "predecessor_projection_id": old["projection_id"],
            "predecessor_profile": old["profile"],
            "ast_parser_version": binding["nested_parser_version"],
            "ast_binding_receipts_sha256": [item["binding_receipt_sha256"] for item in ast_bindings],
            "ast_node_ids": [item["ast_node_id"] for item in ast_bindings],
            "parser_limit_closed": True,
            "algebraic_value_closed": False,
            "canonical_admission": False,
        }
        if expression == "c^b":
            migrated["lost_information"].append(
                "algebraic associativity of c^b^4 remains deliberately unselected"
            )
        migrated["resolution_receipt_sha256"] = _digest(migrated)
        resolutions.append(migrated)

    parser_limit_profiles = [
        item for item in resolutions if item.get("profile") == "PARSER-LIMIT-WITNESS-v1"
    ]
    counts = dict(predecessor["resolved_candidate_counts"])
    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": predecessor["audited_main_sha"],
        "predecessor_reconciliation_manifest_sha256": predecessor["manifest_sha256"],
        "nested_ast_binding_manifest_sha256": binding["manifest_sha256"],
        "raw_corpus_manifest_sha256": predecessor["base_corpus_manifest_sha256"],
        "resolved_candidate_counts": counts,
        "resolutions": resolutions,
        "migrated_resolution_family_count": migrated_families,
        "migrated_occurrence_count": binding["ast_bound_symbolic_occurrence_count"],
        "parser_limit_profile_family_count": len(parser_limit_profiles),
        "parser_limit_profile_occurrence_count": sum(
            int(item["occurrence_count"]) for item in parser_limit_profiles
        ),
        "classification_complete": bool(predecessor["classification_complete"]),
        "syntax_provenance_complete_for_migrated_profiles": (
            migrated_families == len(TARGETS)
            and binding["parser_limit_occurrence_count_after"] == 0
            and not parser_limit_profiles
        ),
        "scalar_value_complete": bool(predecessor["scalar_value_complete"]),
        "open_symbolic_occurrence_count": int(predecessor["open_symbolic_occurrence_count"]),
        "coverage_policy": {
            "v1_raw_census_frozen": True,
            "v1_reconciliation_frozen": True,
            "nested_ast_binding_additive": True,
            "projection_equality_is_not_native_identity": True,
            "syntax_binding_does_not_supply_scalar_value": True,
            "power_chain_associativity_not_selected": True,
        },
        "authority_boundary": {
            "canonical_admission_authority": False,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "native_source_rewriting": False,
            "ordered_product_commutation": False,
        },
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def validation_report(repo_root: Path) -> Dict[str, Any]:
    manifest = reconciliation_manifest_v2(repo_root)
    errors = []
    if manifest["resolved_candidate_counts"].get("MISSING_PROJECTION") != 0:
        errors.append("missing projection count reopened")
    if manifest["migrated_resolution_family_count"] != len(TARGETS):
        errors.append("not all parser-limit families migrated")
    if manifest["migrated_occurrence_count"] != 5:
        errors.append("unexpected migrated occurrence count")
    if manifest["parser_limit_profile_occurrence_count"] != 0:
        errors.append("parser-limit profiles remain after AST migration")
    if not manifest["syntax_provenance_complete_for_migrated_profiles"]:
        errors.append("syntax provenance migration incomplete")
    if manifest["scalar_value_complete"]:
        errors.append("scalar value completion was overclaimed")
    return {
        "schema": "HHS_SPI_CORPUS_RECONCILIATION_VALIDATION_V2",
        "ok": not errors,
        "manifest_sha256": manifest["manifest_sha256"],
        "resolved_candidate_counts": manifest["resolved_candidate_counts"],
        "migrated_resolution_family_count": manifest["migrated_resolution_family_count"],
        "migrated_occurrence_count": manifest["migrated_occurrence_count"],
        "parser_limit_profile_occurrence_count": manifest["parser_limit_profile_occurrence_count"],
        "syntax_provenance_complete_for_migrated_profiles": manifest[
            "syntax_provenance_complete_for_migrated_profiles"
        ],
        "scalar_value_complete": manifest["scalar_value_complete"],
        "canonical_admission_authority": False,
        "errors": errors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--manifest", action="store_true")
    group.add_argument("--require-scalar-values", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parent
    manifest = reconciliation_manifest_v2(repo_root)
    if args.validate:
        report = validation_report(repo_root)
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if report["ok"] else 1
    if args.require_scalar_values:
        print(json.dumps({
            "schema": "HHS_SPI_CORPUS_SCALAR_VALUE_COMPLETION_V2",
            "scalar_value_complete": manifest["scalar_value_complete"],
            "open_symbolic_occurrence_count": manifest["open_symbolic_occurrence_count"],
            "parser_limit_profile_occurrence_count": manifest["parser_limit_profile_occurrence_count"],
            "manifest_sha256": manifest["manifest_sha256"],
        }, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if manifest["scalar_value_complete"] else 2
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

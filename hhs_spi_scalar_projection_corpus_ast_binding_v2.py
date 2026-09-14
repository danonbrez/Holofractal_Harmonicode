"""Bind v1 parser-limit scalar candidates to exact nested-expression AST v2 nodes.

The raw corpus census and v1 reconciliation remain immutable evidence. This
successor layer migrates only the two parser-limit profile families onto the
additive nested-expression AST. It does not assign new scalar values.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from hhs_spi_scalar_projection_corpus_v1 import (
    EXPECTED_HARMONICODE_SOURCES,
    repository_coverage_manifest,
    validate_source_inventory,
)
from hhs_spi_scalar_projection_corpus_reconciliation_v1 import reconciliation_manifest
from native_projects.hhs_harmonicode_language.hhs_harmonicode_nested_expression_ast_v2 import (
    PARSER_VERSION as NESTED_PARSER_VERSION,
    find_enclosing_nodes,
    parse_source,
)

FORMAT = "HHS_SPI_CORPUS_NESTED_AST_BINDING_V2"
VERSION = "2.0.0"
SCHEMA = "HHS_SPI_CORPUS_NESTED_AST_BINDING_MANIFEST_V2"
EXPECTED_RAW_MANIFEST_SHA256 = "fc421b2f84d7186693ba02e40515d7dcf471efe4fd6ade3b3a3ab662e36ef5a7"
EXPECTED_RECONCILIATION_V1_SHA256 = "d726356e1651df8e43ad56a47885b2d4aacbb4b5c56a106476cf48519dc50b4f"

TARGETS: Dict[str, Dict[str, Any]] = {
    "(pq+u⁷²)^x": {
        "old_projection_id": "SPI-CORPUS-LEXICAL-PARTIAL-ROOT-EXP-v1",
        "old_profile": "PARSER-LIMIT-WITNESS-v1",
        "node_kind": "RadicalPowerSurface",
        "expected_enclosing_source": "√(pq+u⁷²)^x²",
        "new_projection_id": "SPI-CORPUS-RADICAL-EXPONENT-SYNTAX-v2",
        "new_profile": "NESTED-AST-SYNTAX-WITNESS-v2",
    },
    "c^b": {
        "old_projection_id": "SPI-CORPUS-LEXICAL-PARTIAL-CHAIN-POWER-v1",
        "old_profile": "PARSER-LIMIT-WITNESS-v1",
        "node_kind": "PowerChain",
        "expected_enclosing_source": "c^b^4",
        "new_projection_id": "SPI-CORPUS-CHAINED-POWER-SYNTAX-v2",
        "new_profile": "NESTED-AST-SYNTAX-WITNESS-v2",
    },
}


class SPIASTBindingError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def binding_manifest(repo_root: Path) -> Dict[str, Any]:
    repo_root = Path(repo_root)
    raw = repository_coverage_manifest(repo_root)
    if raw["manifest_sha256"] != EXPECTED_RAW_MANIFEST_SHA256:
        raise SPIASTBindingError("raw corpus manifest drifted; re-audit before AST binding")

    reconciliation_v1 = reconciliation_manifest(repo_root)
    if reconciliation_v1["manifest_sha256"] != EXPECTED_RECONCILIATION_V1_SHA256:
        raise SPIASTBindingError("v1 reconciliation manifest drifted; re-audit before AST binding")

    inventory = validate_source_inventory(repo_root)
    if not inventory["ok"]:
        raise SPIASTBindingError(str(inventory["errors"]))
    source_by_path = {record["path"]: record["source"] for record in inventory["records"]}

    old_resolution_by_expression = {
        item["expression"]: item
        for item in reconciliation_v1["resolutions"]
        if item["expression"] in TARGETS
    }
    if set(old_resolution_by_expression) != set(TARGETS):
        raise SPIASTBindingError("expected parser-limit v1 resolution families are not intact")

    ast_cache: Dict[str, Dict[str, Any]] = {}
    bindings = []
    errors = []
    for expression in sorted(TARGETS):
        target = TARGETS[expression]
        old = old_resolution_by_expression[expression]
        if old["projection_id"] != target["old_projection_id"] or old["profile"] != target["old_profile"]:
            errors.append(f"{expression}: predecessor parser-limit profile drift")
            continue
        for old_span in old["spans"]:
            path = old_span["path"]
            source = source_by_path.get(path)
            if source is None:
                errors.append(f"{expression}: missing source path {path}")
                continue
            ast = ast_cache.setdefault(path, parse_source(source))
            matches = find_enclosing_nodes(
                ast,
                int(old_span["start"]),
                int(old_span["end"]),
                kinds=(target["node_kind"],),
            )
            if not matches:
                errors.append(f"{expression}: no enclosing {target['node_kind']} at {path}:{old_span}")
                continue
            node = matches[0]
            if node["source_text"] != target["expected_enclosing_source"]:
                errors.append(f"{expression}: enclosing source drift at {path}: {node['source_text']!r}")
                continue
            binding = {
                "expression": expression,
                "path": path,
                "raw_candidate_span": {
                    "start": int(old_span["start"]),
                    "end": int(old_span["end"]),
                    "source_text": source[int(old_span["start"]):int(old_span["end"])],
                },
                "old_projection_id": target["old_projection_id"],
                "old_profile": target["old_profile"],
                "new_projection_id": target["new_projection_id"],
                "new_profile": target["new_profile"],
                "coverage_state": "SYMBOLIC",
                "ast_parser_version": NESTED_PARSER_VERSION,
                "ast_node_id": node["node_id"],
                "ast_node_root_hash72": node["node_root_hash72"],
                "ast_node_kind": node["kind"],
                "ast_source_text": node["source_text"],
                "ast_source_span": node["source_span"],
                "ast_associativity": node["associativity"],
                "scalar_value": None,
                "canonical_admission": False,
                "parser_limit_closed": True,
                "algebraic_value_closed": False,
            }
            binding["binding_receipt_sha256"] = _digest(binding)
            bindings.append(binding)

    expected_occurrences = sum(int(item["occurrence_count"]) for item in old_resolution_by_expression.values())
    if len(bindings) != expected_occurrences:
        errors.append(f"bound occurrence count {len(bindings)} != expected {expected_occurrences}")

    manifest: Dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "raw_corpus_manifest_sha256": raw["manifest_sha256"],
        "reconciliation_v1_manifest_sha256": reconciliation_v1["manifest_sha256"],
        "nested_parser_version": NESTED_PARSER_VERSION,
        "source_path_count": len(EXPECTED_HARMONICODE_SOURCES),
        "target_family_count": len(TARGETS),
        "parser_limit_occurrence_count_before": expected_occurrences,
        "parser_limit_occurrence_count_after": 0 if not errors else expected_occurrences - len(bindings),
        "ast_bound_symbolic_occurrence_count": len(bindings),
        "bindings": sorted(
            bindings,
            key=lambda item: (item["expression"], item["path"], item["raw_candidate_span"]["start"]),
        ),
        "syntax_binding_complete": not errors and len(bindings) == expected_occurrences,
        "scalar_value_complete": False,
        "authority_boundary": {
            "canonical_admission_authority": False,
            "vm81_mutation": False,
            "canonical_hash72_hash216_minting": False,
            "source_rewriting": False,
            "power_chain_associativity_selected": False,
        },
        "errors": errors,
    }
    manifest["manifest_sha256"] = _digest(manifest)
    return manifest


def validation_report(repo_root: Path) -> Dict[str, Any]:
    manifest = binding_manifest(repo_root)
    return {
        "schema": "HHS_SPI_CORPUS_NESTED_AST_BINDING_VALIDATION_V2",
        "ok": not manifest["errors"] and manifest["syntax_binding_complete"],
        "manifest_sha256": manifest["manifest_sha256"],
        "target_family_count": manifest["target_family_count"],
        "parser_limit_occurrence_count_before": manifest["parser_limit_occurrence_count_before"],
        "parser_limit_occurrence_count_after": manifest["parser_limit_occurrence_count_after"],
        "ast_bound_symbolic_occurrence_count": manifest["ast_bound_symbolic_occurrence_count"],
        "scalar_value_complete": manifest["scalar_value_complete"],
        "canonical_admission_authority": False,
        "errors": manifest["errors"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true")
    group.add_argument("--manifest", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parent
    if args.validate:
        report = validation_report(repo_root)
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        return 0 if report["ok"] else 1
    manifest = binding_manifest(repo_root)
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if manifest["syntax_binding_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

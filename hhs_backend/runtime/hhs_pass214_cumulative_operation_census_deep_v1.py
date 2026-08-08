"""Deep Pass 214 cumulative operation/capability census.

Extends the base repository-wide census with ABI declaration surfaces and the
remaining implementation/formal/build languages present in the repository.
The result keeps raw operation identities separate from canonical semantic
identity and never promotes or merges authority automatically.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    CLASSIFICATION as BASE_CLASSIFICATION,
    FROZEN_RUNTIME,
    FROZEN_RUNTIME_GIT_BLOB,
    MAX_DEFAULT_BYTES,
    OperationCensusError,
    _component,
    _digest,
    _normalize,
    _python_exposure,
    _reuse,
    build_cumulative_operation_census,
)
from hhs_backend.runtime.hhs_pass214_operation_language_extractors_v1 import (
    extract_supplemental_operations,
)

SCHEMA = "HHS_PASS_214_CUMULATIVE_OPERATION_CAPABILITY_CENSUS_DEEP_V1"
CLASSIFICATION = "HHS_PASS_214_DEEP_REPOSITORY_WIDE_REUSABLE_OPERATION_ACCOUNTING"


def _family(item: Mapping[str, Any]) -> str:
    kind = str(item["kind"])
    if kind == "C_ABI_DECLARATION":
        return "ABI_DECLARATION_SURFACE"
    if kind in {"YAML_DECLARATIVE_OPERATION", "TOML_DECLARATIVE_OPERATION"}:
        return "DECLARATIVE_CAPABILITY_REGISTRY"
    if kind in {"LEAN_FORMAL_DECLARATION", "ROCQ_FORMAL_DECLARATION"}:
        return "FORMAL_SPECIFICATION_SURFACE"
    if kind in {"BUILD_TASK", "CMAKE_CALLABLE"}:
        return "BUILD_AND_INTEGRATION_OPERATION"
    if kind == "ASSEMBLY_PUBLIC_SYMBOL":
        return "NATIVE_ASSEMBLY_OPERATION"
    return "SUPPLEMENTAL_CALLABLE_OPERATION"


def _supplemental_reuse(item: Mapping[str, Any], component_count: int) -> str:
    kind = str(item["kind"])
    if kind == "C_ABI_DECLARATION":
        return "ABI_DECLARATION_SURFACE"
    if kind in {"LEAN_FORMAL_DECLARATION", "ROCQ_FORMAL_DECLARATION"}:
        return "FORMAL_SPECIFICATION"
    if kind in {"BUILD_TASK", "CMAKE_CALLABLE"}:
        return "BUILD_AND_INTEGRATION_TASK"
    return _reuse(item, max(0, component_count - 1))


def _rebuild_summary(base: Mapping[str, Any], records: list[dict[str, Any]], language_manifest: Mapping[str, Any]) -> dict[str, Any]:
    families = Counter(str(x["family"]) for x in records)
    kinds = Counter(str(x["kind"]) for x in records)
    reuse = Counter(str(x["reuse_status"]) for x in records)
    python = Counter(str(x["python_exposure"]) for x in records)
    authorities = Counter(str(x["authority"]) for x in records)
    origins = Counter(
        "PRE_PASS_OR_UNNUMBERED" if x["pass_number"] is None else f"PASS_{int(x['pass_number']):03d}"
        for x in records
    )
    groups: dict[str, list[str]] = defaultdict(list)
    for item in records:
        groups[str(item["normalized_semantic_name"])].append(str(item["operation_key"]))
    multi = {key: values for key, values in groups.items() if len(values) > 1}
    isolated = [x for x in records if x["reuse_status"] == "ISOLATED_IMPLEMENTATION_CANDIDATE"]
    base_summary = dict(base["summary"])
    coverage = dict(base_summary["coverage"])
    coverage.update(
        raw_operation_identities=len(records),
        components_with_operations=len({x["component"] for x in records}),
        pre_pass_or_unnumbered_operations=origins["PRE_PASS_OR_UNNUMBERED"],
        numbered_pass_operations=len(records) - origins["PRE_PASS_OR_UNNUMBERED"],
    )
    return {
        **base_summary,
        "coverage": coverage,
        "family_counts": dict(sorted(families.items())),
        "kind_counts": dict(sorted(kinds.items())),
        "reuse_counts": dict(sorted(reuse.items())),
        "python_exposure_counts": dict(sorted(python.items())),
        "authority_counts": dict(sorted(authorities.items())),
        "origin_counts": dict(sorted(origins.items())),
        "semantic_accounting": {
            "normalized_semantic_name_groups": len(groups),
            "multi_identity_name_normalized_candidates": len(multi),
            "proven_exact_projection_records": sum(1 for x in records if x.get("semantic_equivalence") == "EXACT_PROJECTION_BY_NATIVE_REGISTRY"),
            "automatic_semantic_collapse_performed": False,
            "canonical_unique_semantic_operation_count": None,
            "canonical_count_status": "REQUIRES_PROVEN_EQUIVALENCE_RECONCILIATION",
        },
        "reuse_accounting": {
            "isolated_implementation_candidates": len(isolated),
            "reused_across_components": reuse["REUSED_ACROSS_COMPONENTS"],
            "shared_module_records": reuse["SHARED_MODULE"],
            "internal_primitives": reuse["INTERNAL_PRIMITIVE"],
            "abi_declaration_surfaces": reuse["ABI_DECLARATION_SURFACE"],
            "formal_specification_records": reuse["FORMAL_SPECIFICATION"],
            "build_and_integration_tasks": reuse["BUILD_AND_INTEGRATION_TASK"],
        },
        "language_coverage_manifest": dict(language_manifest),
    }


def build_deep_cumulative_operation_census(
    repository_root: Path,
    *,
    source_ref: str = "HEAD",
    max_source_bytes: int = MAX_DEFAULT_BYTES,
) -> dict[str, Any]:
    root = repository_root.resolve()
    base = build_cumulative_operation_census(
        root,
        source_ref=source_ref,
        max_source_bytes=max_source_bytes,
    )
    supplemental, language_manifest = extract_supplemental_operations(
        root,
        max_source_bytes=max_source_bytes,
    )
    ctypes_symbols = set(base["summary"].get("ctypes_bound_native_symbols", []))
    governed = {
        str(row["normalized_semantic_name"])
        for row in base["operations"]
        if row["kind"] == "PASS213_GOVERNED_NATIVE_DISPATCH"
    }

    records: dict[str, dict[str, Any]] = {str(row["operation_key"]): dict(row) for row in base["operations"]}
    for row in supplemental:
        item = dict(row)
        item["family"] = _family(item)
        records.setdefault(str(item["operation_key"]), item)

    values = list(records.values())
    components_by_name: dict[str, set[str]] = defaultdict(set)
    for item in values:
        item.setdefault("normalized_semantic_name", _normalize(str(item["raw_name"])))
        item.setdefault("component", _component(str(item["path"])))
        components_by_name[str(item["normalized_semantic_name"])].add(str(item["component"]))

    for item in values:
        if item["kind"] in {
            "C_ABI_DECLARATION", "RUST_FUNCTION", "JAVA_METHOD", "KOTLIN_FUNCTION",
            "SWIFT_FUNCTION", "LEAN_FORMAL_DECLARATION", "ROCQ_FORMAL_DECLARATION",
            "ASSEMBLY_PUBLIC_SYMBOL", "BUILD_TASK", "CMAKE_CALLABLE",
            "YAML_DECLARATIVE_OPERATION", "TOML_DECLARATIVE_OPERATION",
        }:
            component_count = len(components_by_name[str(item["normalized_semantic_name"])])
            item["semantic_name_component_count"] = component_count
            item.setdefault("cross_component_reference_count", max(0, component_count - 1))
            item.setdefault("cross_component_reference_examples", [])
            item.setdefault("reference_file_count", 0)
            item["reuse_status"] = _supplemental_reuse(item, component_count)
            item["python_exposure"] = _python_exposure(item, ctypes_symbols, governed)
            item.setdefault(
                "semantic_equivalence",
                "UNRESOLVED_NAME_NORMALIZED_CANDIDATE" if component_count > 1 else "DISTINCT_OR_UNRESOLVED",
            )

    values.sort(
        key=lambda x: (
            str(x["family"]), str(x["normalized_semantic_name"]), str(x["path"]),
            int(x["line"]), str(x["raw_name"]),
        )
    )
    summary = _rebuild_summary(base, values, language_manifest)
    if summary["frozen_runtime"]["git_blob"] != FROZEN_RUNTIME_GIT_BLOB:
        raise OperationCensusError("DEEP_CENSUS_FROZEN_RUNTIME_BLOB_MISMATCH")
    if not summary["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("DEEP_CENSUS_KNOWN_OPCODE_ANCHOR_FAILURE")

    groups: dict[str, list[str]] = defaultdict(list)
    for item in values:
        groups[str(item["normalized_semantic_name"])].append(str(item["operation_key"]))
    result = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "parent_census_schema": base["schema"],
        "parent_census_classification": BASE_CLASSIFICATION,
        "policy": {
            **base["policy"],
            "public_abi_declarations_counted_as_projection_surfaces": True,
            "formal_proof_declarations_separated_from_executable_operations": True,
            "build_tasks_separated_from_runtime_semantics": True,
            "multi_language_implementation_scan": True,
            "canonical_unique_semantic_operation_count_requires_proof": True,
        },
        "summary": summary,
        "parse_errors": base["parse_errors"],
        "skipped_large_or_binary_files": base["skipped_large_or_binary_files"],
        "semantic_name_candidates": [
            {"normalized_name": key, "operation_keys": operation_keys}
            for key, operation_keys in sorted(groups.items()) if len(operation_keys) > 1
        ],
        "isolated_implementation_candidates": [
            {
                "operation_key": row["operation_key"], "raw_name": row["raw_name"],
                "kind": row["kind"], "path": row["path"], "component": row["component"],
                "family": row["family"], "python_exposure": row["python_exposure"],
            }
            for row in values if row["reuse_status"] == "ISOLATED_IMPLEMENTATION_CANDIDATE"
        ],
        "operations": values,
    }
    result["census_sha256"] = _digest(result)
    return result


def write_deep_census(result: Mapping[str, Any], output: Path) -> None:
    import json
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_and_validate_deep_census(path: Path) -> dict[str, Any]:
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    supplied = data.pop("census_sha256", None)
    if supplied != _digest(data):
        raise OperationCensusError("DEEP_CENSUS_SHA256_VALIDATION_FAILURE")
    data["census_sha256"] = supplied
    if data.get("schema") != SCHEMA:
        raise OperationCensusError("DEEP_CENSUS_SCHEMA_MISMATCH")
    if not data["summary"]["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("DEEP_CENSUS_KNOWN_FAMILY_ANCHORS_FAILED")
    return data

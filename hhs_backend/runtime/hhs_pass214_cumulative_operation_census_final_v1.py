"""Final-quality Pass 214 cumulative operation/capability census.

Removes the broad legacy Python registry-string heuristic from the deep census
and replaces it with structural operation-registry keys. This preserves deep
coverage while preventing metadata strings from being counted as operations.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    MAX_DEFAULT_BYTES,
    OperationCensusError,
    _component,
    _digest,
    _normalize,
    _python_exposure,
    _reuse,
)
from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_deep_v1 import (
    CLASSIFICATION as DEEP_CLASSIFICATION,
    _rebuild_summary,
    build_deep_cumulative_operation_census,
)
from hhs_backend.runtime.hhs_pass214_python_operation_registry_v1 import (
    extract_python_operation_registry_keys,
)

SCHEMA = "HHS_PASS_214_CUMULATIVE_OPERATION_CAPABILITY_CENSUS_FINAL_V1"
CLASSIFICATION = "HHS_PASS_214_DEEP_OPERATION_REUSE_AND_EXPOSURE_ACCOUNTING_FINAL"


def build_final_cumulative_operation_census(
    repository_root: Path,
    *,
    source_ref: str = "HEAD",
    max_source_bytes: int = MAX_DEFAULT_BYTES,
) -> dict[str, Any]:
    root = repository_root.resolve()
    deep = build_deep_cumulative_operation_census(
        root, source_ref=source_ref, max_source_bytes=max_source_bytes
    )
    precise_registry, registry_manifest = extract_python_operation_registry_keys(
        root, max_source_bytes=max_source_bytes
    )

    # The base scanner's broad PYTHON_REGISTRY_ENTRY records are deliberately
    # removed here. They searched every string under loosely named variables and
    # could treat metadata/version/stop-word strings as operations.
    records: dict[str, dict[str, Any]] = {
        str(row["operation_key"]): dict(row)
        for row in deep["operations"]
        if row["kind"] != "PYTHON_REGISTRY_ENTRY"
    }
    for row in precise_registry:
        item = dict(row)
        item["family"] = "DECLARATIVE_CAPABILITY_REGISTRY"
        records.setdefault(str(item["operation_key"]), item)

    values = list(records.values())
    components_by_name: dict[str, set[str]] = defaultdict(set)
    for item in values:
        item.setdefault("normalized_semantic_name", _normalize(str(item["raw_name"])))
        item.setdefault("component", _component(str(item["path"])))
        components_by_name[str(item["normalized_semantic_name"])].add(str(item["component"]))

    ctypes_symbols = set(deep["summary"].get("ctypes_bound_native_symbols", []))
    governed = {
        str(row["normalized_semantic_name"])
        for row in values if row["kind"] == "PASS213_GOVERNED_NATIVE_DISPATCH"
    }
    for item in values:
        if item["kind"] != "PYTHON_OPERATION_REGISTRY_KEY":
            continue
        component_count = len(components_by_name[str(item["normalized_semantic_name"])])
        item["semantic_name_component_count"] = component_count
        item["cross_component_reference_count"] = max(0, component_count - 1)
        item["cross_component_reference_examples"] = []
        item["reference_file_count"] = 0
        item["reuse_status"] = _reuse(item, max(0, component_count - 1))
        item["python_exposure"] = _python_exposure(item, ctypes_symbols, governed)
        item["semantic_equivalence"] = (
            "UNRESOLVED_NAME_NORMALIZED_CANDIDATE"
            if component_count > 1 else "DISTINCT_OR_UNRESOLVED"
        )

    values.sort(
        key=lambda x: (
            str(x["family"]), str(x["normalized_semantic_name"]), str(x["path"]),
            int(x["line"]), str(x["raw_name"]),
        )
    )
    language_manifest = dict(deep["summary"]["language_coverage_manifest"])
    language_manifest["python_operation_registry"] = registry_manifest
    language_manifest["discarded_broad_python_registry_string_records"] = sum(
        1 for row in deep["operations"] if row["kind"] == "PYTHON_REGISTRY_ENTRY"
    )
    summary = _rebuild_summary(deep, values, language_manifest)
    summary["quality_controls"] = {
        "broad_python_registry_string_heuristic_removed": True,
        "structural_python_registry_keys_only": True,
        "discarded_broad_registry_string_records": language_manifest["discarded_broad_python_registry_string_records"],
        "replacement_python_operation_registry_keys": registry_manifest["python_operation_registry_keys"],
        "canonical_semantic_count_not_inferred_from_names": True,
    }
    if not summary["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("FINAL_CENSUS_KNOWN_OPCODE_ANCHOR_FAILURE")

    groups: dict[str, list[str]] = defaultdict(list)
    for item in values:
        groups[str(item["normalized_semantic_name"])].append(str(item["operation_key"]))
    result = {
        "schema": SCHEMA,
        "classification": CLASSIFICATION,
        "parent_census_schema": deep["schema"],
        "parent_census_classification": DEEP_CLASSIFICATION,
        "policy": {
            **deep["policy"],
            "broad_python_registry_string_heuristic_discarded": True,
            "python_operation_registries_are_structural_keys_only": True,
            "metadata_strings_are_not_operations_by_default": True,
        },
        "summary": summary,
        "parse_errors": deep["parse_errors"],
        "skipped_large_or_binary_files": deep["skipped_large_or_binary_files"],
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


def write_final_census(result: Mapping[str, Any], output: Path) -> None:
    import json
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_and_validate_final_census(path: Path) -> dict[str, Any]:
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    supplied = data.pop("census_sha256", None)
    if supplied != _digest(data):
        raise OperationCensusError("FINAL_CENSUS_SHA256_VALIDATION_FAILURE")
    data["census_sha256"] = supplied
    if data.get("schema") != SCHEMA:
        raise OperationCensusError("FINAL_CENSUS_SCHEMA_MISMATCH")
    if not data["summary"]["known_opcode_family_anchors"]["all_satisfied"]:
        raise OperationCensusError("FINAL_CENSUS_KNOWN_FAMILY_ANCHORS_FAILED")
    if not data["summary"]["quality_controls"]["broad_python_registry_string_heuristic_removed"]:
        raise OperationCensusError("FINAL_CENSUS_REGISTRY_QUALITY_GATE_FAILED")
    return data

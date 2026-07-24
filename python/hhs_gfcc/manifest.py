from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping
import hashlib
import json
import zipfile

from .core import CONTRACT_ID, PASS_NUMBER, digest256, stable, write_json

INHERITED_TERMINAL = "HHS_PASS_152_UNIVERSAL_ELASTIC_CLOSURE_INVARIANT_VERIFIED"

INHERITED_EVIDENCE_PATHS = (
    "reports/pass152/PASS_152_FULL_VALIDATION_REPORT.json",
    "PASS_152_RELEASE_MANIFEST.json",
    "receipts/pass152/final/P152_FINAL_EXECUTION_SUMMARY.json",
    "HHS_PASS_152_IMPLEMENTATION_REPORT.md",
    "HHS_PASS_152_FINAL_CONTRACT.md",
    "tests/test_hhs_pass152_universal_elastic_closure_v1.py",
)

GFCC_SOURCE_ROOTS = (
    "python/hhs_gfcc",
    "native_projects/hhs_gfcc_pass152/include",
    "native_projects/hhs_gfcc_pass152/src",
    "native_projects/hhs_gfcc_pass152/tests",
    "native_projects/hhs_gfcc_pass152/specs",
    "native_projects/hhs_gfcc_pass152/contracts",
)

REQUIRED_RECEIPTS = (
    "GFCC_SOURCE_SPEC_RECEIPT.json",
    "GFCC_DEPENDENCY_GRAPH_RECEIPT.json",
    "GFCC_SHELL_CLOSURE_RECEIPT.json",
    "GFCC_DELTA369_RECEIPT.json",
    "GFCC_NONARY_QUDIT_RECEIPT.json",
    "GFCC_VM81_CONSTRUCTION_RECEIPT.json",
    "GFCC_HASH72_PROJECTION_RECEIPT.json",
    "GFCC_HASH216_INDEX_RECEIPT.json",
    "GFCC_C_CODEGEN_RECEIPT.json",
    "GFCC_NATIVE_BUILD_RECEIPT.json",
    "GFCC_SHADER_CODEGEN_RECEIPT.json",
    "GFCC_SHADER_BUILD_RECEIPT.json",
    "GFCC_GEOMETRY_CONSTRUCTION_RECEIPT.json",
    "GFCC_COLLISION_CONSTRUCTION_RECEIPT.json",
    "GFCC_COLLISION_ENFORCEMENT_RECEIPT.json",
    "GFCC_NEGATIVE_TEST_RECEIPT.json",
    "GFCC_REPLAY_RECEIPT.json",
    "GFCC_FINAL_VALIDATION_RECEIPT.json",
)

REQUIRED_GENERATED_ARTIFACTS = (
    "generated/hhs_gfcc_spec.json",
    "generated/hhs_gfcc_parameters.json",
    "generated/hhs_gfcc_dependency_graph.json",
    "generated/hhs_gfcc_delta369.json",
    "generated/maps/hhs_gfcc_vm81_map.bin",
    "generated/maps/hhs_gfcc_hash72_projection_map.bin",
    "generated/maps/hhs_gfcc_hash216_index_map.bin",
    "generated/maps/hhs_gfcc_collision_constraint_table.bin",
    "generated/c/hhs_gfcc_parameters.h",
    "generated/c/hhs_gfcc_parameters.c",
    "generated/c/hhs_gfcc_tables.h",
    "generated/c/hhs_gfcc_tables.c",
    "generated/c/hhs_gfcc_vm81_map.h",
    "generated/c/hhs_gfcc_vm81_map.c",
    "generated/c/hhs_gfcc_hash72_map.h",
    "generated/c/hhs_gfcc_hash72_map.c",
    "generated/c/hhs_gfcc_hash216_map.h",
    "generated/c/hhs_gfcc_hash216_map.c",
    "generated/c/hhs_gfcc_collision_table.h",
    "generated/c/hhs_gfcc_collision_table.c",
    "generated/shaders/hhs_gfcc_fragment.glsl",
    "generated/shaders/hhs_gfcc_collision_field.glsl",
    "dist/hhs_gfcc_shader.spv",
    "dist/hhs_gfcc_collision_field.spv",
    "dist/libhhs_gfcc.a",
    "dist/libhhs_gfcc.so",
    "dist/hhs-gfcc",
    "dist/test_hhs_gfcc",
    "receipts/hhs_gfcc_receipts.jsonl",
    "reports/HHS_PASS_152_VALIDATION_REPORT.md",
    "reports/HHS_PASS_152_VALIDATION_REPORT.json",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_record(path: Path, root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": _sha256_bytes(data),
    }


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON evidence must be an object: {path}")
    return stable(value)


def validate_inherited_pass152(repo: Path) -> dict[str, Any]:
    records = []
    missing = []
    for relative in INHERITED_EVIDENCE_PATHS:
        path = repo / relative
        if not path.is_file():
            missing.append(relative)
        else:
            records.append(file_record(path, repo))
    conditions: dict[str, bool] = {
        "all_evidence_files_present": not missing,
        "terminal_classification_matches": False,
        "release_scope_complete_inherited_nucleus": False,
        "complete_parent_files_preserved": False,
        "no_unauthorized_inherited_modifications": False,
        "positive_matrix_30_of_30": False,
        "negative_matrix_30_of_30": False,
        "api_integration_5_passed": False,
        "native_c_passed": False,
        "vm81_commit_present": False,
        "hash72_receipt_present": False,
        "recursive_history_valid": False,
        "deterministic_replay_match": False,
        "final_execution_summary_matches": False,
    }
    details: dict[str, Any] = {"missing": missing, "records": records}
    if not missing:
        report = _read_json(repo / INHERITED_EVIDENCE_PATHS[0])
        release = _read_json(repo / INHERITED_EVIDENCE_PATHS[1])
        final = _read_json(repo / INHERITED_EVIDENCE_PATHS[2])
        parent = report.get("parent", {})
        pass152 = report.get("pass152", {})
        conditions.update(
            {
                "terminal_classification_matches": report.get("classification") == INHERITED_TERMINAL
                and report.get("terminal_status") == INHERITED_TERMINAL
                and release.get("terminal_status") == INHERITED_TERMINAL,
                "release_scope_complete_inherited_nucleus": release.get("release_scope")
                == "FULL_INHERITED_HHS_PASS_HISTORY_NUCLEUS",
                "complete_parent_files_preserved": release.get("complete_parent_files_preserved") is True
                and parent.get("legacy_paths_preserved") is True
                and parent.get("missing_inherited_files") == [],
                "no_unauthorized_inherited_modifications": parent.get("unauthorized_inherited_modifications")
                == [],
                "positive_matrix_30_of_30": pass152.get("positive_cases") == 30
                and pass152.get("failed") == 0,
                "negative_matrix_30_of_30": pass152.get("negative_cases") == 30
                and pass152.get("failed") == 0,
                "api_integration_5_passed": pass152.get("api_integration_pytest") == "5_PASSED",
                "native_c_passed": pass152.get("native_c") == "PASSED"
                and release.get("native_c11_validation") is True,
                "vm81_commit_present": pass152.get("vm81_commit") is True
                and release.get("vm81_commit_validation") is True,
                "hash72_receipt_present": pass152.get("hash72_receipt_present") is True
                and release.get("hash72_receipt_validation") is True,
                "recursive_history_valid": pass152.get("recursive_history_valid") is True,
                "deterministic_replay_match": pass152.get("replay") == "MATCH"
                and release.get("deterministic_replay_validation") is True,
                "final_execution_summary_matches": final.get("classification") == INHERITED_TERMINAL
                and final.get("replay", {}).get("replay_status") == "MATCH"
                and final.get("commit", {}).get("vm81_admitted") is True
                and final.get("commit", {}).get("hash72_receipt", {}).get("authority_audit", {}).get("ok")
                is True,
            }
        )
        details.update(
            {
                "validation_report_classification": report.get("classification"),
                "release_terminal_status": release.get("terminal_status"),
                "final_summary_classification": final.get("classification"),
                "parent_byte_identical_files": parent.get("byte_identical_inherited_files"),
                "parent_manifest_entries": parent.get("parent_manifest_entries"),
            }
        )
    valid = all(conditions.values())
    result = {
        "schema": "HHS_GFCC_INHERITED_PASS152_EVIDENCE_V1",
        "contract_id": CONTRACT_ID,
        "pass_number": PASS_NUMBER,
        "required_inherited_terminal": INHERITED_TERMINAL,
        "conditions": conditions,
        "details": details,
        "valid": valid,
        "classification": "IMPLEMENTED_AND_EXECUTION_VERIFIED"
        if valid
        else "IMPLEMENTED_VALIDATION_FAILED",
    }
    result["evidence_digest"] = digest256(result)
    return stable(result)


def build_source_manifest(repo: Path) -> dict[str, Any]:
    paths: set[Path] = set()
    for relative in GFCC_SOURCE_ROOTS:
        root = repo / relative
        if root.is_dir():
            paths.update(path for path in root.rglob("*") if path.is_file())
    for relative in (
        "tests/test_hhs_gfcc_pass152.py",
        "tests/test_hhs_gfcc_cross_lane.py",
        ".github/workflows/pass152-gfcc-constructor.yml",
        "GNUmakefile",
        "native_projects/hhs_gfcc_pass152/Makefile",
        "native_projects/hhs_gfcc_pass152/CMakeLists.txt",
        "native_projects/hhs_gfcc_pass152/pyproject.toml",
        "native_projects/hhs_gfcc_pass152/README.md",
        "native_projects/hhs_gfcc_pass152/VERSION",
        "native_projects/hhs_gfcc_pass152/CHANGELOG.md",
    ):
        path = repo / relative
        if path.is_file():
            paths.add(path)
    records = [file_record(path, repo) for path in sorted(paths, key=lambda item: item.as_posix())]
    result = {
        "schema": "HHS_GFCC_SOURCE_MANIFEST_V1",
        "contract_id": CONTRACT_ID,
        "file_count": len(records),
        "expanded_bytes": sum(record["size"] for record in records),
        "records": records,
    }
    result["manifest_digest"] = digest256(result)
    return stable(result)


def validate_source_manifest(repo: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    mismatches = []
    for record in manifest.get("records", []):
        path = repo / str(record["path"])
        if not path.is_file():
            mismatches.append({"path": record["path"], "error": "MISSING"})
            continue
        observed = file_record(path, repo)
        if observed["size"] != record["size"] or observed["sha256"] != record["sha256"]:
            mismatches.append(
                {
                    "path": record["path"],
                    "error": "DIGEST_OR_SIZE_MISMATCH",
                    "expected": {"size": record["size"], "sha256": record["sha256"]},
                    "observed": {"size": observed["size"], "sha256": observed["sha256"]},
                }
            )
    valid = not mismatches and manifest.get("file_count") == len(manifest.get("records", []))
    return {
        "valid": valid,
        "matched": len(manifest.get("records", [])) - len(mismatches),
        "total": len(manifest.get("records", [])),
        "mismatches": mismatches,
    }


def build_repository_manifest(repo: Path) -> dict[str, Any]:
    excluded_parts = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
    records = []
    for path in sorted(repo.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or any(part in excluded_parts for part in path.relative_to(repo).parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        records.append(file_record(path, repo))
    result = {
        "schema": "HHS_GFCC_REPOSITORY_MANIFEST_V1",
        "contract_id": CONTRACT_ID,
        "repository_classification": "COMPLETE_INHERITED_PASS_HISTORY_NUCLEUS",
        "file_count": len(records),
        "expanded_bytes": sum(record["size"] for record in records),
        "records_digest": digest256(records),
        "inherited_evidence": validate_inherited_pass152(repo),
    }
    result["manifest_digest"] = digest256(result)
    return stable(result)


def audit_receipt_set(receipts_dir: Path) -> dict[str, Any]:
    records = []
    errors = []
    previous_digest = "0" * 64
    previous_sequence = 0
    for filename in REQUIRED_RECEIPTS:
        path = receipts_dir / filename
        if not path.is_file():
            errors.append({"file": filename, "error": "MISSING"})
            continue
        try:
            receipt = _read_json(path)
        except ValueError as exc:
            errors.append({"file": filename, "error": "INVALID_JSON", "details": str(exc)})
            continue
        supplied_digest = receipt.get("receipt_digest")
        observed_digest = digest256({key: value for key, value in receipt.items() if key != "receipt_digest"})
        if receipt.get("contract_id") != CONTRACT_ID or str(receipt.get("pass_number")) != PASS_NUMBER:
            errors.append({"file": filename, "error": "CONTRACT_IDENTITY_MISMATCH"})
        if supplied_digest != observed_digest:
            errors.append({"file": filename, "error": "RECEIPT_DIGEST_MISMATCH"})
        sequence = int(receipt.get("deterministic_sequence", 0))
        if sequence != previous_sequence + 1:
            errors.append(
                {
                    "file": filename,
                    "error": "SEQUENCE_DISCONTINUITY",
                    "expected": previous_sequence + 1,
                    "observed": sequence,
                }
            )
        if receipt.get("predecessor_receipt_digest") != previous_digest:
            errors.append(
                {
                    "file": filename,
                    "error": "PREDECESSOR_DISCONTINUITY",
                    "expected": previous_digest,
                    "observed": receipt.get("predecessor_receipt_digest"),
                }
            )
        previous_sequence = sequence
        previous_digest = str(supplied_digest or "")
        records.append(
            {
                "file": filename,
                "operation_id": receipt.get("operation_id"),
                "sequence": sequence,
                "receipt_digest": supplied_digest,
                "authority_level": receipt.get("authority_level"),
                "classification": receipt.get("result_classification"),
            }
        )
    valid = not errors and len(records) == len(REQUIRED_RECEIPTS)
    return {
        "schema": "HHS_GFCC_RECEIPT_SET_AUDIT_V1",
        "required_count": len(REQUIRED_RECEIPTS),
        "observed_count": len(records),
        "valid": valid,
        "terminal_receipt_digest": previous_digest if valid else None,
        "records": records,
        "errors": errors,
    }


def build_artifact_manifest(subsystem: Path) -> dict[str, Any]:
    records = []
    missing = []
    for relative in REQUIRED_GENERATED_ARTIFACTS:
        path = subsystem / relative
        if not path.is_file():
            missing.append(relative)
        else:
            records.append(file_record(path, subsystem))
    receipt_audit = audit_receipt_set(subsystem / "receipts")
    result = {
        "schema": "HHS_PASS_152_GFCC_ARTIFACT_MANIFEST_V1",
        "contract_id": CONTRACT_ID,
        "required_artifact_count": len(REQUIRED_GENERATED_ARTIFACTS),
        "observed_artifact_count": len(records),
        "missing_artifacts": missing,
        "records": records,
        "receipt_audit": receipt_audit,
        "valid": not missing and receipt_audit["valid"],
    }
    result["manifest_digest"] = digest256(result)
    return stable(result)


def validate_archive(
    archive_path: Path,
    *,
    required_paths: Iterable[str],
    expected_repository_file_minimum: int,
) -> dict[str, Any]:
    if not archive_path.is_file():
        return {"valid": False, "error": "ARCHIVE_MISSING", "path": archive_path.as_posix()}
    errors = []
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        name_set = set(names)
        duplicate_names = sorted({name for name in names if names.count(name) > 1})
        if duplicate_names:
            errors.append({"error": "DUPLICATE_ARCHIVE_PATHS", "paths": duplicate_names})
        for required in required_paths:
            if required not in name_set:
                errors.append({"error": "REQUIRED_PATH_MISSING", "path": required})
        unsafe = [
            name
            for name in names
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name
        ]
        if unsafe:
            errors.append({"error": "UNSAFE_ARCHIVE_PATH", "paths": unsafe})
        bad_crc = archive.testzip()
        if bad_crc:
            errors.append({"error": "CRC_FAILURE", "path": bad_crc})
        total_bytes = sum(info.file_size for info in archive.infolist())
        if len(names) < expected_repository_file_minimum:
            errors.append(
                {
                    "error": "INHERITED_NUCLEUS_FILE_COUNT_TOO_SMALL",
                    "minimum": expected_repository_file_minimum,
                    "observed": len(names),
                }
            )
    return {
        "valid": not errors,
        "filename": archive_path.name,
        "byte_size": archive_path.stat().st_size,
        "sha256": _sha256_bytes(archive_path.read_bytes()),
        "expanded_file_count": len(names),
        "expanded_byte_size": total_bytes,
        "errors": errors,
    }


def write_manifests(repo: Path) -> dict[str, Any]:
    subsystem = repo / "native_projects" / "hhs_gfcc_pass152"
    manifest_dir = subsystem / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    inheritance = validate_inherited_pass152(repo)
    source = build_source_manifest(repo)
    source_validation = validate_source_manifest(repo, source)
    repository = build_repository_manifest(repo)
    artifact = build_artifact_manifest(subsystem)
    write_json(manifest_dir / "inherited_pass152_evidence.json", inheritance)
    write_json(manifest_dir / "source_manifest.json", source)
    write_json(manifest_dir / "source_manifest_validation.json", source_validation)
    write_json(manifest_dir / "repository_manifest.json", repository)
    write_json(manifest_dir / "artifact_manifest.json", artifact)
    return {
        "inheritance": inheritance,
        "source_manifest": source,
        "source_manifest_validation": source_validation,
        "repository_manifest": repository,
        "artifact_manifest": artifact,
    }


__all__ = [
    "INHERITED_TERMINAL",
    "REQUIRED_RECEIPTS",
    "REQUIRED_GENERATED_ARTIFACTS",
    "audit_receipt_set",
    "build_artifact_manifest",
    "build_repository_manifest",
    "build_source_manifest",
    "validate_archive",
    "validate_inherited_pass152",
    "validate_source_manifest",
    "write_manifests",
]

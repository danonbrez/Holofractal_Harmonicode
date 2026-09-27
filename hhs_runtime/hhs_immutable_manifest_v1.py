"""Immutable Pass 078 freeze validation with explicit successor lineage.

Pass 078 remains a historical byte-exact freeze. Later authorized repairs may
replace a whole-file identity only when a repository-visible successor proof
binds the current file. This validator therefore checks both temporal layers:
the original four-file freeze at its historical anchor and the exact current
successor identities.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Dict

from hhs_runtime.hhs_repo_paths_v1 import repo_root

MANIFEST_NAME = "PASS_078_KERNEL_FREEZE_MANIFEST.json"
EXPECTED_SCHEMA = "HHS_KERNEL_FREEZE_MANIFEST_PASS_078_V1"
PASS078_HISTORICAL_REF = "66c614ae1de0c1b1651451e2c406307a8dee83ed"
PASS206_LINEAGE_PATH = Path("artifacts/pass206/CORE_SUCCESSOR_REPAIR_LINEAGE.json")
PASS078_SUCCESSOR_PATH = Path("evidence/pass220/PASS_078_SUCCESSOR_LINEAGE_V1.json")
I028_PROOF_PATH = Path("evidence/pass220/i028_g3_ouroboros_wolfram_20260922_v1.output.json")

VM81_PATH = "hhs_runtime/HARMONICODE_VM_RUNTIME.c"
RUNTIME_ABI_PATH = "hhs_runtime/c/hhs_runtime_abi.c"
APPROVED_RUNTIME_ABI_BLOB = "6a3ed4a10c5d83fa77bb4d118819fc230d32248a"
APPROVED_VM81_BLOB = "92afd8d0e26119b6db6420740c05db25a37d389a"
I028_VALIDATED_HEAD = "8a750bb56d14fc9847166736bbbf2ca0660bff7f"
I028_MERGE_COMMIT = "86a66d32ba3c17430887cb4ff9fa0da7dbb4bf6f"
I028_VALIDATION_RUN = 35723417642

LEGACY_OPCODE_PREFIX = (
    "OP_NOP", "OP_ADD", "OP_SUB", "OP_ROT", "OP_XOR", "OP_AND", "OP_OR",
    "OP_LOAD", "OP_STORE", "OP_BRANCH", "OP_BZ", "OP_BNZ", "OP_MULXY",
    "OP_MULYX", "OP_QGU", "OP_GATE_APB", "OP_GATE_CLOSURE",
    "OP_GATE_IDENTITY", "OP_QBRANCH", "OP_CONSTRAIN", "OP_RELAX",
    "OP_SWEEP81", "OP_CLOSE81", "OP_HALT",
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(base: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=base,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError("GIT_EVIDENCE_UNAVAILABLE:" + detail)
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _git_blob(base: Path, ref: str, path: str) -> str:
    return str(_git(base, "rev-parse", f"{ref}:{path}"))


def _git_bytes(base: Path, ref: str, path: str) -> bytes:
    value = _git(base, "show", f"{ref}:{path}", binary=True)
    assert isinstance(value, bytes)
    return value


def _is_ancestor(base: Path, ancestor: str, descendant: str = "HEAD") -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=base,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def _load_object(base: Path, path: Path) -> Dict[str, Any]:
    value = json.loads((base / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("OBJECT_REQUIRED:" + str(path))
    return value


def _opcode_names(source: str) -> tuple[str, ...]:
    marker = source.index("// OPCODES")
    start = source.index("typedef enum {", marker)
    end = source.index("} Opcode;", start)
    names = []
    for line in source[start:end].splitlines():
        token = line.strip().split("=", 1)[0].strip().rstrip(",")
        if token.startswith("OP_"):
            names.append(token)
    return tuple(names)


def validate_manifest(root: Path | None = None) -> Dict[str, Any]:
    base = Path(root) if root is not None else repo_root()
    manifest_path = base / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"ok": False, "status": "MANIFEST_MISSING", "manifest": str(manifest_path)}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "MANIFEST_UNREADABLE", "error": str(exc)}

    errors: list[dict[str, Any]] = []
    historical: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    if manifest.get("schema") != EXPECTED_SCHEMA:
        errors.append({"kind": "SCHEMA_MISMATCH", "actual": manifest.get("schema")})
    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        errors.append({"kind": "EMPTY_FREEZE_MANIFEST"})
        records = []

    by_path = {
        str(record.get("path")): record
        for record in records
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }

    try:
        if not _is_ancestor(base, PASS078_HISTORICAL_REF):
            errors.append({
                "kind": "PASS078_HISTORICAL_REF_NOT_ANCESTRAL",
                "ref": PASS078_HISTORICAL_REF,
            })

        for record in records:
            if not isinstance(record, dict):
                errors.append({"kind": "INVALID_FREEZE_RECORD"})
                continue
            relative = record.get("path")
            if not isinstance(relative, str):
                errors.append({"kind": "INVALID_FREEZE_PATH", "path": relative})
                continue
            frozen = _git_bytes(base, PASS078_HISTORICAL_REF, relative)
            actual_size = len(frozen)
            actual_sha256 = _sha256_bytes(frozen)
            match = (
                actual_size == record.get("size")
                and actual_sha256 == record.get("sha256")
            )
            historical.append({
                "path": relative,
                "ref": PASS078_HISTORICAL_REF,
                "size": actual_size,
                "sha256": actual_sha256,
                "ok": match,
            })
            if not match:
                errors.append({
                    "kind": "HISTORICAL_FROZEN_FILE_MISMATCH",
                    "path": relative,
                    "expected_size": record.get("size"),
                    "actual_size": actual_size,
                    "expected_sha256": record.get("sha256"),
                    "actual_sha256": actual_sha256,
                })
    except Exception as exc:
        errors.append({"kind": "HISTORICAL_FREEZE_EVIDENCE_ERROR", "error": str(exc)})

    try:
        pass206 = _load_object(base, PASS206_LINEAGE_PATH)
        successor = _load_object(base, PASS078_SUCCESSOR_PATH)
        i028 = _load_object(base, I028_PROOF_PATH)

        if successor.get("schema") != "HHS_PASS_078_SUCCESSOR_LINEAGE_V1":
            errors.append({"kind": "SUCCESSOR_SCHEMA_MISMATCH"})
        if successor.get("historical_ref") != PASS078_HISTORICAL_REF:
            errors.append({"kind": "SUCCESSOR_HISTORICAL_REF_MISMATCH"})

        approved = {
            row.get("repository_path"): row
            for row in pass206.get("approved_successors", [])
            if isinstance(row, dict)
        }
        abi_successor = approved.get(RUNTIME_ABI_PATH)
        if not isinstance(abi_successor, dict):
            errors.append({"kind": "PASS206_RUNTIME_ABI_SUCCESSOR_MISSING"})

        for relative, record in by_path.items():
            path = base / relative
            if not path.is_file():
                errors.append({"kind": "CURRENT_FILE_MISSING", "path": relative})
                continue
            current_size = path.stat().st_size
            current_sha256 = _sha256(path)
            historical_match = (
                current_size == record.get("size")
                and current_sha256 == record.get("sha256")
            )
            disposition = "HISTORICAL_BYTES_UNCHANGED"
            ok = historical_match

            if relative == RUNTIME_ABI_PATH and not historical_match:
                blob = _git_blob(base, "HEAD", relative)
                ok = bool(
                    abi_successor
                    and blob == APPROVED_RUNTIME_ABI_BLOB
                    and blob == abi_successor.get("approved_current_git_blob")
                    and abi_successor.get("baseline_file_sha256") == record.get("sha256")
                    and abi_successor.get("canonical_authority_change") is False
                    and abi_successor.get("abi_signature_drift") is False
                    and _is_ancestor(base, str(abi_successor.get("repair_merge_commit")))
                )
                disposition = "PASS206_APPROVED_ADDITIVE_ABI_SUCCESSOR"

            elif relative == VM81_PATH and not historical_match:
                blob = _git_blob(base, "HEAD", relative)
                source = path.read_text(encoding="utf-8")
                names = _opcode_names(source)
                successor_vm = successor.get("vm81_successor") or {}
                ok = bool(
                    blob == APPROVED_VM81_BLOB
                    and blob == successor_vm.get("approved_current_git_blob")
                    and successor_vm.get("validated_head") == I028_VALIDATED_HEAD
                    and successor_vm.get("merge_commit") == I028_MERGE_COMMIT
                    and successor_vm.get("validation_run") == I028_VALIDATION_RUN
                    and successor_vm.get("validation_conclusion") == "success"
                    and _is_ancestor(base, I028_VALIDATED_HEAD)
                    and _is_ancestor(base, I028_MERGE_COMMIT)
                    and i028.get("status") == "PASS"
                    and i028.get("check_count") == 12
                    and i028.get("pass_count") == 12
                    and i028.get("failed") == []
                    and i028.get("opcode_values") == list(range(24, 35))
                    and names[:24] == LEGACY_OPCODE_PREFIX
                    and "_Static_assert(OP_HALT == 23" in source
                    and "_Static_assert(OP_G3_IEEE_INGRESS == 24" in source
                    and "_Static_assert(OP_G3_OUROBOROS == 34" in source
                    and "_Static_assert(OP__COUNT == 35" in source
                )
                disposition = "PASS220_I028_APPEND_ONLY_VM81_SUCCESSOR"

            current.append({
                "path": relative,
                "size": current_size,
                "sha256": current_sha256,
                "historical_match": historical_match,
                "disposition": disposition,
                "ok": ok,
            })
            if not ok:
                errors.append({
                    "kind": "CURRENT_SUCCESSOR_NOT_AUTHORIZED",
                    "path": relative,
                    "disposition": disposition,
                    "sha256": current_sha256,
                })
    except Exception as exc:
        errors.append({"kind": "CURRENT_SUCCESSOR_EVIDENCE_ERROR", "error": str(exc)})

    return {
        "ok": not errors,
        "status": "VERIFIED" if not errors else "REJECTED",
        "schema": EXPECTED_SCHEMA,
        "manifest": MANIFEST_NAME,
        "manifest_root_hash72": manifest.get("pass078_kernel_freeze_manifest_root_hash72"),
        "historical_ref": PASS078_HISTORICAL_REF,
        "historical_checked_file_count": len(historical),
        "historical_files": historical,
        "current_checked_file_count": len(current),
        "current_files": current,
        "temporal_validation": "HISTORICAL_FREEZE_PLUS_EXPLICIT_SUCCESSOR_LINEAGE",
        "errors": errors,
    }


if __name__ == "__main__":
    print(json.dumps(validate_manifest(), indent=2, sort_keys=True))

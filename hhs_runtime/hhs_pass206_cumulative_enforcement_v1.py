"""Pass 206 cumulative contract/core-preservation enforcement.

This module is a read/validate-only membrane. It authenticates the historical
Pass 206 grounding freeze, the one accepted post-baseline ABI repair, and the
current cumulative successor boundary without creating a second VM81, Hash72
clock, persistence path, or mutation primitive.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from typing import Any, Mapping, Sequence

PASS = 206
BASELINE = "918121aeb6d1c55aa8fbd5d60b15f03c4eb22423"
SEALED_PREDECESSOR = "2fe770d68f6e1da172d2c7992a90e31d69577b90"
APPROVED_REPAIR_MERGE = "284bf652d9635cc0c940f79dfe6aff6f8b787c3c"
APPROVED_REPAIR_VALIDATED_HEAD = "3235f9066219bf2e665503d9f94aa11701d4c20e"
APPROVED_REPAIR_RUN = 31941882432
APPROVED_REPAIR_JOB = 95152163266
APPROVED_RUNTIME_ABI_BLOB = "6a3ed4a10c5d83fa77bb4d118819fc230d32248a"

REQUIRED_ARTIFACTS = (
    "ACCUMULATED_CONTRACT_INDEX.json",
    "ACCUMULATED_CONSTRAINT_INDEX.json",
    "CORE_FUNCTION_FREEZE_MANIFEST.json",
    "ABI_OPCODE_SCHEMA_FREEZE_MANIFEST.json",
    "CONTRACT_CONFLICT_REPORT.json",
    "PLUGIN_COMPATIBILITY_REPORT.json",
    "INTERFACE_CAPABILITY_PARITY_REPORT.json",
    "VALIDATION_MATRIX.json",
    "CORE_SUCCESSOR_REPAIR_LINEAGE.json",
)

REQUIRED_RECEIPT_ORDER = (
    "candidate_proposal",
    "cumulative_python_and_native_validation",
    "singleton_vm81_kernel_admission",
    "valid_transformation",
    "prev_state_receipt_hash72_block",
    "exact_ordered_216_character_concatenation",
    "character_addressed_sha256_array",
    "hash216_vector_index_and_durable_storage",
    "optional_buffer_cache_reuse",
)

REQUIRED_HASH72_BLOCK = ("prev_hash72", "state_hash72", "receipt_hash72")
REQUIRED_BASIS = ("x", "y", "z", "w", "xy", "yx", "zw", "wz")
REQUIRED_LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))


class Pass206EnforcementRejected(RuntimeError):
    pass


def _root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def _git(root: pathlib.Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.check_output(["git", *args], cwd=root)
    return result if binary else result.decode("utf-8").strip()


def _load(path: pathlib.Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Pass206EnforcementRejected(f"expected JSON object: {path}")
    return value


def _canonical_artifact_hash(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("artifact_sha256", None)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _artifact_integrity(value: Mapping[str, Any]) -> bool:
    stored = value.get("artifact_sha256")
    return isinstance(stored, str) and len(stored) == 64 and stored == _canonical_artifact_hash(value)


def _baseline_bytes(root: pathlib.Path, repository_path: str) -> bytes:
    return _git(root, "show", f"{BASELINE}:{repository_path}", binary=True)  # type: ignore[return-value]


def _blob(root: pathlib.Path, ref: str, repository_path: str) -> str:
    return str(_git(root, "rev-parse", f"{ref}:{repository_path}"))


def _is_ancestor(root: pathlib.Path, ancestor: str, descendant: str = "HEAD") -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def _changed_paths(root: pathlib.Path, base: str, paths: Sequence[str]) -> tuple[str, ...]:
    text = str(_git(root, "diff", "--name-only", f"{base}..HEAD", "--", *paths))
    return tuple(line for line in text.splitlines() if line)


def _static_contract_reasons(contract: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    authority = contract.get("authority", {})
    core = contract.get("core_function_policy", {})
    hydration = contract.get("hydration", {})
    security = contract.get("security_boundary", {})
    plugin = contract.get("plugin_compatibility", {})

    expected = {
        "pass": PASS,
        "grounding_baseline": BASELINE,
        "classification": "CONTRACT_AUTHORIZED_FULL_IMPLEMENTATION_REQUIRED",
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            reasons.append(f"CONTRACT_{key.upper()}_MISMATCH")
    if authority.get("canonical_mutation_authority_count") != 1:
        reasons.append("CANONICAL_MUTATION_AUTHORITY_COUNT_MISMATCH")
    if authority.get("canonical_mutation_authority") != "VM81_KERNEL":
        reasons.append("CANONICAL_MUTATION_AUTHORITY_MISMATCH")
    if authority.get("canonical_hash72_commit_stream_count") != 1:
        reasons.append("HASH72_COMMIT_STREAM_COUNT_MISMATCH")
    if authority.get("parallel_canonical_authorities_allowed") is not False:
        reasons.append("PARALLEL_CANONICAL_AUTHORITY_FORBIDDEN")
    if core.get("mode") != "FREEZE_AND_ENFORCE" or core.get("alter_core_functions") is not False:
        reasons.append("CORE_FREEZE_POLICY_MISMATCH")
    if core.get("fallback_authority_allowed") is not False:
        reasons.append("FALLBACK_AUTHORITY_FORBIDDEN")
    if core.get("separate_repair_contract_required_for_core_change") is not True:
        reasons.append("REPAIR_CONTRACT_REQUIREMENT_MISSING")
    if contract.get("ordered_basis") != list(REQUIRED_BASIS):
        reasons.append("ORDERED_BASIS_MISMATCH")
    if tuple(tuple(row) for row in contract.get("lo_shu", ())) != REQUIRED_LO_SHU:
        reasons.append("LO_SHU_MISMATCH")
    if hydration.get("vm81_cells") != 81 or hydration.get("bits_per_cell") != 64:
        reasons.append("VM81_DIMENSION_MISMATCH")
    if hydration.get("permanent_addresses") != 5184 or hydration.get("control_states") != 243:
        reasons.append("HYDRATION_CARDINALITY_MISMATCH")
    if hydration.get("projected_addresses") != 1259712:
        reasons.append("PROJECTED_ADDRESS_CARDINALITY_MISMATCH")
    if hydration.get("permanent_address_formula") != "s=64c+o":
        reasons.append("PERMANENT_ADDRESS_FORMULA_MISMATCH")
    if hydration.get("projected_address_formula") != "q=243s+g":
        reasons.append("PROJECTED_ADDRESS_FORMULA_MISMATCH")
    if tuple(contract.get("receipt_archival_order", ())) != REQUIRED_RECEIPT_ORDER:
        reasons.append("RECEIPT_ARCHIVAL_ORDER_MISMATCH")
    if tuple(contract.get("hash72_block", ())) != REQUIRED_HASH72_BLOCK:
        reasons.append("HASH72_BLOCK_ORDER_MISMATCH")
    if contract.get("hash216_authorizes_original_transformation") is not False:
        reasons.append("HASH216_MUTATION_AUTHORITY_FORBIDDEN")
    if contract.get("cache_bypasses_admission") is not False:
        reasons.append("CACHE_ADMISSION_BYPASS_FORBIDDEN")
    if security.get("public_stage_selection_allowed") is not False:
        reasons.append("PUBLIC_STAGE_SELECTION_FORBIDDEN")
    if security.get("public_stage_reordering_allowed") is not False:
        reasons.append("PUBLIC_STAGE_REORDERING_FORBIDDEN")
    if security.get("public_stage_bypass_allowed") is not False:
        reasons.append("PUBLIC_STAGE_BYPASS_FORBIDDEN")
    if plugin.get("full_backward_compatibility_required") is not True:
        reasons.append("BACKWARD_COMPATIBILITY_REQUIRED")
    if plugin.get("core_modification_allowed") is not False:
        reasons.append("PLUGIN_CORE_MODIFICATION_FORBIDDEN")
    if plugin.get("alternate_authority_allowed") is not False:
        reasons.append("PLUGIN_ALTERNATE_AUTHORITY_FORBIDDEN")
    return reasons


def _core_identity_reasons(
    freeze: Mapping[str, Any],
    lineage: Mapping[str, Any],
    baseline_blobs: Mapping[str, str],
    current_blobs: Mapping[str, str],
    baseline_hashes: Mapping[str, str],
    *,
    repair_ancestral: bool,
    pass206_changed_paths: Sequence[str],
) -> list[str]:
    reasons: list[str] = []
    entries = freeze.get("entries", [])
    if freeze.get("grounding_baseline") != BASELINE or freeze.get("entry_count") != 10:
        reasons.append("CORE_FREEZE_MANIFEST_IDENTITY_MISMATCH")
        return reasons
    approved = {
        row["repository_path"]: row
        for row in lineage.get("approved_successors", [])
        if isinstance(row, dict) and "repository_path" in row
    }
    if lineage.get("approved_successor_count") != 1 or lineage.get("unchanged_core_count") != 9:
        reasons.append("APPROVED_SUCCESSOR_CARDINALITY_MISMATCH")
    if not repair_ancestral:
        reasons.append("APPROVED_REPAIR_NOT_ANCESTRAL")
    if pass206_changed_paths:
        reasons.append("PASS206_REPAIR_TOUCHED_FROZEN_CORE")

    for entry in entries:
        if not isinstance(entry, dict):
            reasons.append("INVALID_CORE_FREEZE_ENTRY")
            continue
        path = str(entry.get("repository_path"))
        if entry.get("baseline_commit") != BASELINE:
            reasons.append(f"BASELINE_COMMIT_MISMATCH:{path}")
        if baseline_blobs.get(path) != entry.get("git_blob"):
            reasons.append(f"BASELINE_GIT_BLOB_MISMATCH:{path}")
        if baseline_hashes.get(path) != entry.get("file_sha256"):
            reasons.append(f"BASELINE_SHA256_MISMATCH:{path}")
        successor = approved.get(path)
        if successor is None:
            if current_blobs.get(path) != entry.get("git_blob"):
                reasons.append(f"UNAPPROVED_CORE_DRIFT:{path}")
        else:
            if successor.get("repair_merge_commit") != APPROVED_REPAIR_MERGE:
                reasons.append(f"REPAIR_MERGE_IDENTITY_MISMATCH:{path}")
            if successor.get("validated_implementation_head") != APPROVED_REPAIR_VALIDATED_HEAD:
                reasons.append(f"REPAIR_VALIDATED_HEAD_MISMATCH:{path}")
            if successor.get("validation_run") != APPROVED_REPAIR_RUN or successor.get("validation_job") != APPROVED_REPAIR_JOB:
                reasons.append(f"REPAIR_VALIDATION_EVIDENCE_MISMATCH:{path}")
            if successor.get("approved_current_git_blob") != APPROVED_RUNTIME_ABI_BLOB:
                reasons.append(f"APPROVED_SUCCESSOR_BLOB_RECORD_MISMATCH:{path}")
            if current_blobs.get(path) != successor.get("approved_current_git_blob"):
                reasons.append(f"APPROVED_SUCCESSOR_CURRENT_BLOB_MISMATCH:{path}")
            if successor.get("canonical_authority_change") is not False or successor.get("abi_signature_drift") is not False:
                reasons.append(f"APPROVED_SUCCESSOR_BOUNDARY_MISMATCH:{path}")
    return reasons


def _successor_reasons(pass207: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if pass207.get("pass") != 207 or pass207.get("parent") != "Complete cumulative HHS runtime through Pass 206":
        reasons.append("PASS207_PARENT_BINDING_MISMATCH")
    authority = pass207.get("authority", {})
    core = pass207.get("core_preservation", {})
    determinism = pass207.get("determinism", {})
    if authority.get("canonical_mutation_authority") != "VM81_KERNEL" or authority.get("canonical_mutation_authority_count") != 1:
        reasons.append("PASS207_VM81_AUTHORITY_MISMATCH")
    if authority.get("canonical_hash72_commit_stream_count") != 1:
        reasons.append("PASS207_HASH72_AUTHORITY_MISMATCH")
    if authority.get("gpu_may_commit_hash72") is not False or authority.get("gpu_may_bypass_vm81_admission") is not False:
        reasons.append("PASS207_GPU_AUTHORITY_BOUNDARY_MISMATCH")
    if core.get("modifies_pass205_core_abi") is not False or core.get("modifies_pass206_frozen_core") is not False:
        reasons.append("PASS207_CORE_PRESERVATION_MISMATCH")
    if core.get("new_additive_files_only") is not True or core.get("uses_existing_vm81_single_authority_boundary") is not True:
        reasons.append("PASS207_ADDITIVE_BOUNDARY_MISMATCH")
    if determinism.get("integer_only_canonical_fields") is not True or determinism.get("canonical_float_fields") != 0:
        reasons.append("PASS207_EXACT_CANONICAL_FIELD_MISMATCH")
    return reasons


def validate_pass206_enforcement(repository_root: pathlib.Path | None = None) -> dict[str, Any]:
    root = repository_root or _root()
    artifact_root = root / "artifacts" / "pass206"
    contract = _load(root / "contracts" / "pass206" / "PASS_206_CONTRACT.json")
    pass207 = _load(root / "contracts" / "pass207" / "PASS_207_CONTRACT.json")
    artifacts = {name: _load(artifact_root / name) for name in REQUIRED_ARTIFACTS}

    checks: list[dict[str, Any]] = []
    reasons: list[str] = []

    def record(name: str, failures: Sequence[str]) -> None:
        failures = tuple(failures)
        checks.append({"name": name, "ok": not failures, "reasons": list(failures)})
        reasons.extend(failures)

    bad_artifacts = [name for name, value in artifacts.items() if not _artifact_integrity(value)]
    record("artifact_integrity", [f"ARTIFACT_HASH_MISMATCH:{name}" for name in bad_artifacts])
    record("static_contract", _static_contract_reasons(contract))

    freeze = artifacts["CORE_FUNCTION_FREEZE_MANIFEST.json"]
    lineage = artifacts["CORE_SUCCESSOR_REPAIR_LINEAGE.json"]
    entries = tuple(row for row in freeze.get("entries", []) if isinstance(row, dict))
    paths = tuple(str(row["repository_path"]) for row in entries)
    baseline_blobs = {path: _blob(root, BASELINE, path) for path in paths}
    current_blobs = {path: _blob(root, "HEAD", path) for path in paths}
    baseline_hashes = {path: hashlib.sha256(_baseline_bytes(root, path)).hexdigest() for path in paths}
    changed = _changed_paths(root, SEALED_PREDECESSOR, paths)
    core_reasons = _core_identity_reasons(
        freeze,
        lineage,
        baseline_blobs,
        current_blobs,
        baseline_hashes,
        repair_ancestral=_is_ancestor(root, APPROVED_REPAIR_MERGE),
        pass206_changed_paths=changed,
    )
    record("core_identity_and_repair_lineage", core_reasons)

    conflicts = artifacts["CONTRACT_CONFLICT_REPORT.json"]
    conflict_failures: list[str] = []
    if conflicts.get("unresolved_conflicts") != []:
        conflict_failures.append("UNRESOLVED_CONTRACT_CONFLICT")
    if not all(bool(value) for value in conflicts.get("checks", {}).values()):
        conflict_failures.append("CONTRACT_CONFLICT_CHECK_FAILED")
    record("contract_conflict_report", conflict_failures)

    plugin = artifacts["PLUGIN_COMPATIBILITY_REPORT.json"]
    plugin_failures: list[str] = []
    if plugin.get("full_backward_compatibility_required") is not True:
        plugin_failures.append("PLUGIN_BACKWARD_COMPATIBILITY_POLICY_MISMATCH")
    if plugin.get("core_modification_allowed") is not False or plugin.get("alternate_authority_allowed") is not False:
        plugin_failures.append("PLUGIN_AUTHORITY_POLICY_MISMATCH")
    record("plugin_compatibility_policy", plugin_failures)

    record("pass207_successor_preservation", _successor_reasons(pass207))

    return {
        "schema": "HHS_PASS_206_CUMULATIVE_ENFORCEMENT_DECISION_V1",
        "pass": PASS,
        "ok": not reasons,
        "status": "ADMIT_PASS206_CUMULATIVE_ENFORCEMENT" if not reasons else "REJECT_PASS206_CUMULATIVE_ENFORCEMENT",
        "grounding_baseline": BASELINE,
        "sealed_predecessor": SEALED_PREDECESSOR,
        "approved_repair_merge": APPROVED_REPAIR_MERGE,
        "frozen_core_count": len(paths),
        "approved_successor_count": lineage.get("approved_successor_count"),
        "pass206_changed_frozen_core_paths": list(changed),
        "canonical_mutation_authority": "VM81_KERNEL",
        "canonical_mutation_authority_count": 1,
        "canonical_hash72_commit_stream_count": 1,
        "pass206_new_mutation_authority": False,
        "pass206_new_persistence_authority": False,
        "pass206_new_hash72_clock": False,
        "checks": checks,
        "reasons": reasons,
    }


def enforce_pass206(repository_root: pathlib.Path | None = None) -> dict[str, Any]:
    decision = validate_pass206_enforcement(repository_root)
    if not decision["ok"]:
        raise Pass206EnforcementRejected(";".join(decision["reasons"]))
    return decision


if __name__ == "__main__":
    print(json.dumps(enforce_pass206(), indent=2, sort_keys=True))

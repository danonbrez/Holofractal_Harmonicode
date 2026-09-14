"""Pass219 I174 / Pass170 bounded legacy launcher retirement verifier.

This verifier is read-only. It freezes the exact-main I173 operation-record
proof, scans the six known uvicorn self-launch surfaces, verifies three new
canonical redirects plus the inherited WebSocket redirect, and leaves the
canonical base launcher and audio-language compatibility launcher explicitly
nonterminal.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)
from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172 import (
    _scan_uvicorn_launchers,
)

SCHEMA = "HHS_PASS219_I174_PASS170_LAUNCHER_RETIREMENT_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I174"
BASE_MAIN = "cb39509ec5e16dc884d9556ed65cfc1a40d8c5d8"
REGISTRY = "HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I174.json"
OPERATION_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX.json"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
CLASSIFICATION = "PASS170_LEGACY_LAUNCHER_RETIREMENT_TRANCHE_A_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_CANONICAL_BASE_LAUNCHER_AND_AUDIO_ROUTE_MIGRATION"
EXPECTED_PENDING = (
    "hhs_backend/server.py",
    "hhs_runtime_api_server_plus_v1.py",
)
EXPECTED_REDIRECTED = (
    "hhs_backend/runtime/runtime_server.py",
    "hhs_runtime/main.py",
    "hhs_runtime_api_server_v1.py",
)
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_AUDIO_LANGUAGE_ROUTE_MIGRATION_PENDING",
    "PASS170_CANONICAL_BASE_SELF_LAUNCH_PENDING_REDIRECT",
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN",
    "PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING",
    "PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING",
)


class Pass170I174VerificationError(RuntimeError):
    """Raised when bounded I174 launcher evidence fails closed."""


def _json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I174VerificationError(
            f"PASS170_I174_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I174VerificationError(f"PASS170_I174_JSON_ROOT_INVALID:{path}")
    return payload


def verify_i174_launcher_retirement(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    registry = _json(root / REGISTRY)
    operation_index = _json(root / OPERATION_INDEX)
    inventory = build_i169_pass170_public_authority_inventory(root)
    observed = _scan_uvicorn_launchers(root)

    if registry.get("schema") != "HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I174_V1":
        blockers.append("PASS170_I174_REGISTRY_SCHEMA_INVALID")
    if registry.get("contract") != CONTRACT_ID or registry.get("iteration") != ITERATION:
        blockers.append("PASS170_I174_REGISTRY_METADATA_INVALID")
    if registry.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I174_BASE_MAIN_MISMATCH")
    if registry.get("canonical_gateway") != CANONICAL_GATEWAY:
        blockers.append("PASS170_I174_CANONICAL_GATEWAY_MISMATCH")

    if registry.get("parent_i173_exact_main_run") != 34030977410:
        blockers.append("PASS170_I174_PARENT_I173_RUN_MISMATCH")
    if registry.get("parent_i173_exact_main_artifact") != 9988603949:
        blockers.append("PASS170_I174_PARENT_I173_ARTIFACT_MISMATCH")
    if registry.get("parent_i173_exact_main_artifact_digest") != (
        "sha256:a96c116ae5c32679f4b2372bf589618417c972a2eb7f58f3cee53e79d39721cb"
    ):
        blockers.append("PASS170_I174_PARENT_I173_DIGEST_MISMATCH")

    if operation_index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_V1":
        blockers.append("PASS170_I174_I173_OPERATION_INDEX_SCHEMA_INVALID")
    if operation_index.get("iteration") != "PASS219-I173":
        blockers.append("PASS170_I174_I173_OPERATION_INDEX_METADATA_INVALID")
    if operation_index.get("aggregate_record_count") != 47:
        blockers.append("PASS170_I174_I173_OPERATION_RECORD_COUNT_MISMATCH")

    records = registry.get("launcher_records")
    if not isinstance(records, list):
        records = []
        blockers.append("PASS170_I174_LAUNCHER_RECORDS_INVALID")

    observed_by_path = {item.get("path"): item for item in observed if isinstance(item, dict)}
    registered_by_path = {
        item.get("path"): item
        for item in records
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if len(observed) != 6 or len(observed_by_path) != 6:
        blockers.append("PASS170_I174_OBSERVED_LAUNCHER_COUNT_MISMATCH")
    if len(records) != 6 or len(registered_by_path) != 6:
        blockers.append("PASS170_I174_REGISTERED_LAUNCHER_COUNT_MISMATCH")
    if set(observed_by_path) != set(registered_by_path):
        blockers.append("PASS170_I174_LAUNCHER_CENSUS_MISMATCH")

    verified_paths: list[str] = []
    pending_paths: list[str] = []
    for path, record in sorted(registered_by_path.items()):
        observed_record = observed_by_path.get(path)
        if not isinstance(observed_record, dict):
            continue
        if observed_record.get("target") != record.get("expected_target"):
            blockers.append(f"PASS170_I174_LAUNCHER_TARGET_MISMATCH:{path}")
        status = str(record.get("status", ""))
        if status.startswith("VERIFIED_CANONICAL_GATEWAY_REDIRECT"):
            verified_paths.append(path)
            if observed_record.get("target") != CANONICAL_GATEWAY:
                blockers.append(f"PASS170_I174_VERIFIED_LAUNCHER_NOT_CANONICAL:{path}")
        elif status.startswith("PENDING_"):
            pending_paths.append(path)
        else:
            blockers.append(f"PASS170_I174_LAUNCHER_STATUS_INVALID:{path}")

    if sorted(registry.get("newly_redirected_paths", [])) != sorted(EXPECTED_REDIRECTED):
        blockers.append("PASS170_I174_REDIRECTED_PATH_SET_INVALID")
    if sorted(pending_paths) != sorted(EXPECTED_PENDING):
        blockers.append("PASS170_I174_PENDING_PATH_SET_INVALID")
    if len(verified_paths) != 4:
        blockers.append("PASS170_I174_CANONICAL_REDIRECT_COUNT_MISMATCH")
    if len(pending_paths) != 2:
        blockers.append("PASS170_I174_PENDING_LAUNCHER_COUNT_MISMATCH")

    for path in EXPECTED_REDIRECTED:
        observed_record = observed_by_path.get(path, {})
        if observed_record.get("target") != CANONICAL_GATEWAY:
            blockers.append(f"PASS170_I174_REQUIRED_REDIRECT_ABSENT:{path}")

    invariants = registry.get("invariants", {}) if isinstance(registry, dict) else {}
    if invariants.get("launcher_count_expected") != 6:
        blockers.append("PASS170_I174_LAUNCHER_COUNT_INVARIANT_INVALID")
    if invariants.get("canonical_redirect_count_expected") != 4:
        blockers.append("PASS170_I174_REDIRECT_COUNT_INVARIANT_INVALID")
    if invariants.get("pending_launcher_count_expected") != 2:
        blockers.append("PASS170_I174_PENDING_COUNT_INVARIANT_INVALID")
    if invariants.get("legacy_callable_exports_preserved") is not True:
        blockers.append("PASS170_I174_CALLABLE_EXPORT_PRESERVATION_INVALID")
    if invariants.get("operation_record_layer_mutated") is not False:
        blockers.append("PASS170_I174_OPERATION_RECORD_MUTATION_FLAG_INVALID")
    for key in (
        "canonical_state_mutated_by_verification",
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if invariants.get(key) is not False:
            blockers.append(f"PASS170_I174_FORBIDDEN_AUTHORITY_FLAG:{key}")

    constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if constructor_count != 10:
        blockers.append("PASS170_I174_FASTAPI_CONSTRUCTOR_COUNT_DRIFT")

    target_blockers = list(EXPECTED_TARGET_BLOCKERS)
    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I174_EVIDENCE_FAILED",
        "parent_i173_exact_main_verified": True,
        "i173_operation_record_count_preserved": operation_index.get("aggregate_record_count"),
        "observed_launcher_count": len(observed),
        "canonical_redirect_count": len(verified_paths),
        "pending_launcher_count": len(pending_paths),
        "verified_launcher_paths": sorted(verified_paths),
        "pending_launcher_paths": sorted(pending_paths),
        "newly_redirected_paths": list(EXPECTED_REDIRECTED),
        "fastapi_constructor_count_preserved": constructor_count,
        "evidence_verified": evidence_verified,
        "evidence_blockers": evidence_blockers,
        "target_blockers": target_blockers,
        "pass170_terminal_contract_verified": False,
        "canonical_state_mutated": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I174VerificationError(
            "PASS170_I174_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_PENDING",
    "EXPECTED_REDIRECTED",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I174VerificationError",
    "verify_i174_launcher_retirement",
]

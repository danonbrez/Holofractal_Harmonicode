"""Pass219 I176 / Pass170 canonical-base launcher and capability reconciliation.

I176 freezes exact-main I175 evidence, verifies that all six known uvicorn
launchers now target the single canonical Pass170 gateway, and reconciles the
new audio-language public operation against the inherited Pass190 capability
model. No new capability scope is invented: public admission fails closed until
an authoritative scope is explicitly registered in a later boundary.
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

SCHEMA = "HHS_PASS219_I176_PASS170_CANONICAL_BASE_CAPABILITY_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I176"
BASE_MAIN = "8d9ab8a0ec453b2e3f527c8420542929e29cb9d0"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
LAUNCHER_REGISTRY = "HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I176.json"
CAPABILITY_RECONCILIATION = "HHS_PUBLIC_CAPABILITY_MODEL_RECONCILIATION_I176.json"
ADMISSION_OVERLAY = "HHS_PUBLIC_OPERATION_ADMISSION_OVERLAY_I176.json"
AUDIO_RECORD = "contracts/pass219/pass170_operation_records_i175/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_V1.json"
CLASSIFICATION = "PASS170_ALL_PUBLIC_LAUNCHERS_CANONICAL_CAPABILITY_UNRESOLVED_FAIL_CLOSED"
NEXT_BOUNDARY = "PASS170_PUBLIC_CAPABILITY_MODEL_EXTENSION_AND_CONSTRUCTOR_RETIREMENT"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_PUBLIC_AUDIO_CAPABILITY_BINDING_PENDING",
    "PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING",
    "PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING",
)


class Pass170I176VerificationError(RuntimeError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I176VerificationError(
            f"PASS170_I176_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I176VerificationError(f"PASS170_I176_JSON_ROOT_INVALID:{path}")
    return payload


def _text(root: Path, path: str, blockers: list[str], code: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(code)
        return ""


def verify_i176_canonical_base_capability(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    launcher_registry = _json(root / LAUNCHER_REGISTRY)
    capability = _json(root / CAPABILITY_RECONCILIATION)
    overlay = _json(root / ADMISSION_OVERLAY)
    audio_shard = _json(root / AUDIO_RECORD)
    inventory = build_i169_pass170_public_authority_inventory(root)
    observed_launchers = _scan_uvicorn_launchers(root)

    if launcher_registry.get("schema") != "HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I176_V1":
        blockers.append("PASS170_I176_LAUNCHER_REGISTRY_SCHEMA_INVALID")
    if launcher_registry.get("contract") != CONTRACT_ID or launcher_registry.get("iteration") != ITERATION:
        blockers.append("PASS170_I176_LAUNCHER_REGISTRY_METADATA_INVALID")
    if launcher_registry.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I176_BASE_MAIN_MISMATCH")
    if launcher_registry.get("parent_i175_exact_main_run") != 34062282668:
        blockers.append("PASS170_I176_PARENT_I175_RUN_MISMATCH")
    if launcher_registry.get("parent_i175_exact_main_artifact") != 9997852836:
        blockers.append("PASS170_I176_PARENT_I175_ARTIFACT_MISMATCH")
    if launcher_registry.get("parent_i175_exact_main_artifact_digest") != (
        "sha256:6af6f3cf900f2502f8e531ed2b5cd35fad866dc349c65814b0287195db890476"
    ):
        blockers.append("PASS170_I176_PARENT_I175_DIGEST_MISMATCH")

    records = launcher_registry.get("launcher_records")
    if not isinstance(records, list):
        records = []
        blockers.append("PASS170_I176_LAUNCHER_RECORDS_INVALID")
    observed_by_path = {
        item.get("path"): item for item in observed_launchers if isinstance(item, dict)
    }
    registered_by_path = {
        item.get("path"): item
        for item in records
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if len(observed_launchers) != 6 or len(observed_by_path) != 6:
        blockers.append("PASS170_I176_OBSERVED_LAUNCHER_COUNT_MISMATCH")
    if len(records) != 6 or set(observed_by_path) != set(registered_by_path):
        blockers.append("PASS170_I176_LAUNCHER_CENSUS_MISMATCH")

    canonical_paths: list[str] = []
    for path, registered in sorted(registered_by_path.items()):
        observed = observed_by_path.get(path, {})
        if registered.get("expected_target") != CANONICAL_GATEWAY:
            blockers.append(f"PASS170_I176_REGISTERED_TARGET_NOT_CANONICAL:{path}")
        if observed.get("target") != CANONICAL_GATEWAY:
            blockers.append(f"PASS170_I176_OBSERVED_TARGET_NOT_CANONICAL:{path}")
        if not str(registered.get("status", "")).startswith("VERIFIED_CANONICAL_GATEWAY_REDIRECT"):
            blockers.append(f"PASS170_I176_LAUNCHER_STATUS_INVALID:{path}")
        else:
            canonical_paths.append(path)
    if len(canonical_paths) != 6:
        blockers.append("PASS170_I176_CANONICAL_REDIRECT_COUNT_MISMATCH")
    if launcher_registry.get("pending_paths") != []:
        blockers.append("PASS170_I176_PENDING_LAUNCHERS_REMAIN")

    launcher_invariants = launcher_registry.get("invariants") if isinstance(launcher_registry.get("invariants"), dict) else {}
    if launcher_invariants.get("launcher_count_expected") != 6:
        blockers.append("PASS170_I176_LAUNCHER_COUNT_INVARIANT_INVALID")
    if launcher_invariants.get("canonical_redirect_count_expected") != 6:
        blockers.append("PASS170_I176_CANONICAL_COUNT_INVARIANT_INVALID")
    if launcher_invariants.get("pending_launcher_count_expected") != 0:
        blockers.append("PASS170_I176_PENDING_COUNT_INVARIANT_INVALID")
    if launcher_invariants.get("canonical_base_constructor_preserved") is not True:
        blockers.append("PASS170_I176_BASE_CONSTRUCTOR_PRESERVATION_INVALID")

    if capability.get("schema") != "HHS_PUBLIC_CAPABILITY_MODEL_RECONCILIATION_I176_V1":
        blockers.append("PASS170_I176_CAPABILITY_RECONCILIATION_SCHEMA_INVALID")
    inherited = capability.get("inherited_capability_model") if isinstance(capability.get("inherited_capability_model"), dict) else {}
    audio = capability.get("audio_operation") if isinstance(capability.get("audio_operation"), dict) else {}
    invariants = capability.get("invariants") if isinstance(capability.get("invariants"), dict) else {}
    if inherited.get("verifier") != "verify_capability":
        blockers.append("PASS170_I176_CAPABILITY_VERIFIER_MISMATCH")
    if inherited.get("public_or_none_scope_requires_token") is not False:
        blockers.append("PASS170_I176_PUBLIC_SCOPE_MODEL_MISMATCH")
    if inherited.get("non_public_scope_requires_capability_secret") is not True:
        blockers.append("PASS170_I176_NONPUBLIC_SECRET_MODEL_MISMATCH")
    if inherited.get("non_public_scope_requires_signed_token") is not True:
        blockers.append("PASS170_I176_NONPUBLIC_TOKEN_MODEL_MISMATCH")
    if audio.get("reconciliation_status") != "UNRESOLVED_NO_AUTHORITATIVE_INHERITED_AUDIO_SCOPE":
        blockers.append("PASS170_I176_AUDIO_SCOPE_RECONCILIATION_INVALID")
    if audio.get("invent_new_scope_in_i176") is not False:
        blockers.append("PASS170_I176_AUDIO_SCOPE_INVENTED")
    if audio.get("admit_without_resolved_policy") is not False:
        blockers.append("PASS170_I176_AUDIO_PENDING_POLICY_NOT_FAIL_CLOSED")
    if invariants.get("fail_closed_until_capability_model_resolved") is not True:
        blockers.append("PASS170_I176_FAIL_CLOSED_CAPABILITY_INVARIANT_INVALID")
    for key in (
        "pass190_registry_mutated",
        "new_capability_authority_created",
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if invariants.get(key) is not False:
            blockers.append(f"PASS170_I176_FORBIDDEN_CAPABILITY_FLAG:{key}")

    if overlay.get("schema") != "HHS_PUBLIC_OPERATION_ADMISSION_OVERLAY_I176_V1":
        blockers.append("PASS170_I176_ADMISSION_OVERLAY_SCHEMA_INVALID")
    if overlay.get("operation_id") != "public.audio_language.feedback.run":
        blockers.append("PASS170_I176_ADMISSION_OPERATION_MISMATCH")
    if overlay.get("admission_policy") != "FAIL_CLOSED_UNTIL_AUTHORITATIVE_SCOPE_BOUND":
        blockers.append("PASS170_I176_ADMISSION_POLICY_INVALID")
    refusal = overlay.get("typed_refusal") if isinstance(overlay.get("typed_refusal"), dict) else {}
    if refusal != {
        "http_status": 503,
        "detail": "HHS_PASS170_AUDIO_CAPABILITY_MODEL_UNRESOLVED",
    }:
        blockers.append("PASS170_I176_TYPED_REFUSAL_INVALID")

    audio_records = audio_shard.get("records") if isinstance(audio_shard.get("records"), list) else []
    if len(audio_records) != 1 or not isinstance(audio_records[0], dict):
        blockers.append("PASS170_I176_AUDIO_PARENT_RECORD_INVALID")
        audio_record: dict[str, Any] = {}
    else:
        audio_record = audio_records[0]
    if audio_record.get("authorization_scope") != "PENDING_PASS170_CAPABILITY_BINDING":
        blockers.append("PASS170_I176_AUDIO_PARENT_SCOPE_NOT_PENDING")
    if audio_record.get("admission_policy") != "PENDING_PASS170_CAPABILITY_BINDING":
        blockers.append("PASS170_I176_AUDIO_PARENT_ADMISSION_NOT_PENDING")

    completion_source = _text(root, "hhs_runtime/pass190/completion.py", blockers, "PASS170_I176_PASS190_COMPLETION_UNREADABLE")
    audio_source = _text(root, "hhs_backend/pass170_audio_language_routes.py", blockers, "PASS170_I176_AUDIO_ROUTE_SOURCE_UNREADABLE")
    server_source = _text(root, "hhs_backend/server.py", blockers, "PASS170_I176_SERVER_SOURCE_UNREADABLE")
    for token in (
        'if required_scope in {"public", "none"}:',
        "HHS_P190_FULL_RUNTIME_CAPABILITY_SECRET_REQUIRED",
        "HHS_P190_CAPABILITY_REQUIRED",
        "required_scope=required_scope",
    ):
        if token not in completion_source:
            blockers.append(f"PASS170_I176_PASS190_CAPABILITY_SOURCE_TOKEN_MISSING:{token}")
    for token in (
        "def enforce_audio_public_admission",
        "HHS_PASS170_AUDIO_CAPABILITY_MODEL_UNRESOLVED",
        "raise HTTPException(status_code=503",
        "enforce_audio_public_admission()",
    ):
        if token not in audio_source:
            blockers.append(f"PASS170_I176_AUDIO_FAIL_CLOSED_SOURCE_TOKEN_MISSING:{token}")
    if '"hhs_backend.public_api_server:app"' not in server_source:
        blockers.append("PASS170_I176_CANONICAL_BASE_SOURCE_REDIRECT_ABSENT")
    if '"hhs_backend.server:app"' in server_source:
        blockers.append("PASS170_I176_LEGACY_BASE_SELF_LAUNCH_TARGET_REMAINS")

    constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if constructor_count != 10:
        blockers.append("PASS170_I176_FASTAPI_CONSTRUCTOR_COUNT_DRIFT")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I176_EVIDENCE_FAILED",
        "parent_i175_exact_main_verified": True,
        "observed_launcher_count": len(observed_launchers),
        "canonical_redirect_count": len(canonical_paths),
        "pending_launcher_count": 0 if not launcher_registry.get("pending_paths") else len(launcher_registry.get("pending_paths", [])),
        "all_public_launchers_canonical": len(canonical_paths) == 6 and not any(item.startswith("PASS170_I176_OBSERVED_TARGET") for item in evidence_blockers),
        "audio_capability_scope_resolved": False,
        "audio_public_admission_fail_closed": not any("AUDIO_FAIL_CLOSED" in item or "ADMISSION_POLICY" in item or "TYPED_REFUSAL" in item for item in evidence_blockers),
        "new_capability_scope_created": False,
        "fastapi_constructor_count_preserved": constructor_count,
        "evidence_verified": evidence_verified,
        "evidence_blockers": evidence_blockers,
        "target_blockers": list(EXPECTED_TARGET_BLOCKERS),
        "pass170_terminal_contract_verified": False,
        "canonical_state_mutated": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I176VerificationError(
            "PASS170_I176_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I176VerificationError",
    "verify_i176_canonical_base_capability",
]

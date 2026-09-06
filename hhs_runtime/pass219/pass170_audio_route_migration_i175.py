"""Pass219 I175 / Pass170 audio-language migration and audio-security role verifier.

I175 migrates the legacy plus-v1 audio-language route into canonical Pass170
composition, extends the frozen I173 operation record set from 47 to 48, and
records the inherited harmonic-time/audio error-correction role in the internal
post-quantum-oriented security boundary.  The verifier is read-only and does
not grant audio an independent cryptographic, VM81, Hash72, or Hash216 authority.
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

SCHEMA = "HHS_PASS219_I175_PASS170_AUDIO_ROUTE_MIGRATION_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I175"
BASE_MAIN = "95c17e6430ce9c182c6a94ce41848805e2be96ae"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
PARENT_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX.json"
INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX_I175.json"
EXTENSION = "contracts/pass219/pass170_operation_records_i175/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_V1.json"
LAUNCHER_REGISTRY = "HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I175.json"
SECURITY_PROFILE = "HHS_AUDIO_ERROR_CORRECTION_PQ_SECURITY_PROFILE_I175.json"
OPERATION_ID = "public.audio_language.feedback.run"
CLASSIFICATION = "PASS170_AUDIO_ROUTE_MIGRATION_ECC_PQ_ROLE_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_CANONICAL_BASE_LAUNCHER_REDIRECT_AND_PUBLIC_CAPABILITY_PARITY"
EXPECTED_PENDING = ("hhs_backend/server.py",)
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_CANONICAL_BASE_SELF_LAUNCH_PENDING_REDIRECT",
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN",
    "PASS170_PUBLIC_AUDIO_CAPABILITY_BINDING_PENDING",
    "PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING",
    "PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING",
)


class Pass170I175VerificationError(RuntimeError):
    """Raised when I175 evidence fails closed."""


def _json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I175VerificationError(
            f"PASS170_I175_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I175VerificationError(f"PASS170_I175_JSON_ROOT_INVALID:{path}")
    return payload


def _text(root: Path, path: str, blockers: list[str], code: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(code)
        return ""


def verify_i175_audio_route_migration(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    parent_index = _json(root / PARENT_INDEX)
    index = _json(root / INDEX)
    extension = _json(root / EXTENSION)
    launcher_registry = _json(root / LAUNCHER_REGISTRY)
    security_profile = _json(root / SECURITY_PROFILE)
    inventory = build_i169_pass170_public_authority_inventory(root)
    observed_launchers = _scan_uvicorn_launchers(root)

    if parent_index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_V1":
        blockers.append("PASS170_I175_PARENT_INDEX_SCHEMA_INVALID")
    if parent_index.get("iteration") != "PASS219-I173" or parent_index.get("aggregate_record_count") != 47:
        blockers.append("PASS170_I175_PARENT_INDEX_NOT_FROZEN_47")

    if index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_I175_V1":
        blockers.append("PASS170_I175_INDEX_SCHEMA_INVALID")
    if index.get("contract") != CONTRACT_ID or index.get("iteration") != ITERATION:
        blockers.append("PASS170_I175_INDEX_METADATA_INVALID")
    if index.get("frozen_parent_record_count") != 47 or index.get("aggregate_record_count") != 48:
        blockers.append("PASS170_I175_INDEX_COUNT_INVALID")
    if index.get("new_operation_ids") != [OPERATION_ID]:
        blockers.append("PASS170_I175_NEW_OPERATION_ID_INVALID")
    if index.get("security_role_profile") != SECURITY_PROFILE:
        blockers.append("PASS170_I175_SECURITY_PROFILE_LINK_INVALID")

    if extension.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_SHARD_V1":
        blockers.append("PASS170_I175_EXTENSION_SCHEMA_INVALID")
    if extension.get("iteration") != ITERATION or extension.get("record_count") != 1:
        blockers.append("PASS170_I175_EXTENSION_METADATA_INVALID")
    records = extension.get("records") if isinstance(extension.get("records"), list) else []
    if len(records) != 1 or not isinstance(records[0], dict):
        blockers.append("PASS170_I175_EXTENSION_RECORD_INVALID")
        record: dict[str, Any] = {}
    else:
        record = records[0]
    if record.get("operation_id") != OPERATION_ID:
        blockers.append("PASS170_I175_OPERATION_ID_MISMATCH")
    if record.get("HTTP_method") != "POST" or record.get("HTTP_path") != "/v1/audio-language/run":
        blockers.append("PASS170_I175_CANONICAL_ROUTE_RECORD_INVALID")
    aliases = record.get("deprecated_aliases") if isinstance(record.get("deprecated_aliases"), list) else []
    if {"HTTP_method": "POST", "HTTP_path": "/api/audio-language/run"} not in aliases:
        blockers.append("PASS170_I175_LEGACY_ALIAS_RECORD_ABSENT")
    if record.get("VM81_commit_required") is not False or record.get("canonical_vm81_mutation") is not False:
        blockers.append("PASS170_I175_AUDIO_ROUTE_VM81_AUTHORITY_INVALID")
    if record.get("new_hash72_mint_authority") is not False or record.get("new_hash216_persistence_authority") is not False:
        blockers.append("PASS170_I175_AUDIO_ROUTE_HASH_AUTHORITY_INVALID")
    roles = record.get("cross_cutting_roles") if isinstance(record.get("cross_cutting_roles"), list) else []
    for required_role in (
        "LOCAL_AUDIO_LANGUAGE_APPLICATION",
        "HARMONIC_TIME_AUDIO_ERROR_CORRECTION_WITNESS_SOURCE",
        "INTERNAL_POST_QUANTUM_ORIENTED_SECURITY_ENFORCEMENT_SIGNAL",
    ):
        if required_role not in roles:
            blockers.append(f"PASS170_I175_AUDIO_ROLE_ABSENT:{required_role}")
    pq_binding = record.get("post_quantum_security_binding") if isinstance(record.get("post_quantum_security_binding"), dict) else {}
    if pq_binding.get("scope") != "INTERNAL_CONSTRAINT_ENFORCEMENT_ONLY":
        blockers.append("PASS170_I175_PQ_SCOPE_INVALID")
    for key in ("public_crypto_primitive", "standardized_pq_crypto_claim", "independent_key_or_kem_authority"):
        if pq_binding.get(key) is not False:
            blockers.append(f"PASS170_I175_PUBLIC_CRYPTO_AUTHORITY_INVALID:{key}")

    route_source = _text(root, "hhs_backend/pass170_audio_language_routes.py", blockers, "PASS170_I175_ROUTE_SOURCE_UNREADABLE")
    public_source = _text(root, "hhs_backend/public_api_server.py", blockers, "PASS170_I175_PUBLIC_GATEWAY_SOURCE_UNREADABLE")
    plus_source = _text(root, "hhs_runtime_api_server_plus_v1.py", blockers, "PASS170_I175_PLUS_V1_SOURCE_UNREADABLE")
    for token in (
        "def execute_audio_language_feedback_request",
        "@router.post(LEGACY_ALIAS_PATH, deprecated=True)",
        "@router.post(CANONICAL_PATH)",
        "run_audio_language_feedback_cycle",
    ):
        if token not in route_source:
            blockers.append(f"PASS170_I175_ROUTE_SOURCE_TOKEN_MISSING:{token}")
    if "build_pass170_audio_language_router" not in public_source or "router.include_router(build_pass170_audio_language_router())" not in public_source:
        blockers.append("PASS170_I175_CANONICAL_AUDIO_ROUTER_NOT_COMPOSED")
    if "from hhs_backend.public_api_server import app" not in plus_source:
        blockers.append("PASS170_I175_PLUS_V1_NOT_CANONICAL_APP_SHIM")
    if '"hhs_backend.public_api_server:app"' not in plus_source:
        blockers.append("PASS170_I175_PLUS_V1_LAUNCHER_NOT_REDIRECTED")
    if "@app.post" in plus_source or "@app.get" in plus_source or "@app.websocket" in plus_source:
        blockers.append("PASS170_I175_PLUS_V1_INDEPENDENT_ROUTE_REMAINS")

    if launcher_registry.get("schema") != "HHS_PUBLIC_LAUNCHER_RETIREMENT_REGISTRY_I175_V1":
        blockers.append("PASS170_I175_LAUNCHER_REGISTRY_SCHEMA_INVALID")
    if launcher_registry.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I175_LAUNCHER_BASE_MAIN_MISMATCH")
    if launcher_registry.get("parent_i174_exact_main_run") != 34045997663:
        blockers.append("PASS170_I175_PARENT_I174_RUN_MISMATCH")
    if launcher_registry.get("parent_i174_exact_main_artifact") != 9993120344:
        blockers.append("PASS170_I175_PARENT_I174_ARTIFACT_MISMATCH")
    if launcher_registry.get("parent_i174_exact_main_artifact_digest") != "sha256:92922ab3f30b4823b33e68a82fd19c801373cfc3aef3c624fff66ef0b856a64a":
        blockers.append("PASS170_I175_PARENT_I174_DIGEST_MISMATCH")

    launcher_records = launcher_registry.get("launcher_records") if isinstance(launcher_registry.get("launcher_records"), list) else []
    observed_by_path = {item.get("path"): item for item in observed_launchers if isinstance(item, dict)}
    registered_by_path = {item.get("path"): item for item in launcher_records if isinstance(item, dict) and isinstance(item.get("path"), str)}
    if len(observed_launchers) != 6 or len(observed_by_path) != 6:
        blockers.append("PASS170_I175_OBSERVED_LAUNCHER_COUNT_MISMATCH")
    if len(launcher_records) != 6 or set(observed_by_path) != set(registered_by_path):
        blockers.append("PASS170_I175_LAUNCHER_CENSUS_MISMATCH")
    canonical_paths: list[str] = []
    pending_paths: list[str] = []
    for path, registered in sorted(registered_by_path.items()):
        observed = observed_by_path.get(path, {})
        if observed.get("target") != registered.get("expected_target"):
            blockers.append(f"PASS170_I175_LAUNCHER_TARGET_MISMATCH:{path}")
        status = str(registered.get("status", ""))
        if status.startswith("VERIFIED_CANONICAL_GATEWAY_REDIRECT"):
            canonical_paths.append(path)
            if observed.get("target") != CANONICAL_GATEWAY:
                blockers.append(f"PASS170_I175_VERIFIED_LAUNCHER_NOT_CANONICAL:{path}")
        elif status.startswith("PENDING_"):
            pending_paths.append(path)
        else:
            blockers.append(f"PASS170_I175_LAUNCHER_STATUS_INVALID:{path}")
    if len(canonical_paths) != 5:
        blockers.append("PASS170_I175_CANONICAL_LAUNCHER_COUNT_MISMATCH")
    if tuple(sorted(pending_paths)) != tuple(sorted(EXPECTED_PENDING)):
        blockers.append("PASS170_I175_PENDING_LAUNCHER_SET_INVALID")

    if security_profile.get("schema") != "HHS_AUDIO_ERROR_CORRECTION_PQ_SECURITY_PROFILE_I175_V1":
        blockers.append("PASS170_I175_AUDIO_SECURITY_PROFILE_SCHEMA_INVALID")
    if security_profile.get("local_application_operation_id") != OPERATION_ID:
        blockers.append("PASS170_I175_AUDIO_SECURITY_OPERATION_LINK_INVALID")
    ecc = security_profile.get("error_correction") if isinstance(security_profile.get("error_correction"), dict) else {}
    pq = security_profile.get("post_quantum_security") if isinstance(security_profile.get("post_quantum_security"), dict) else {}
    if ecc.get("required_when_temporal") is not True or ecc.get("invalid_witness_must_fail_closed") is not True:
        blockers.append("PASS170_I175_AUDIO_ECC_FAIL_CLOSED_INVARIANT_INVALID")
    if pq.get("boundary") != "INTERNAL_KERNEL_AND_INTEGRATED_RUNTIME_ONLY":
        blockers.append("PASS170_I175_PQ_INTERNAL_BOUNDARY_INVALID")
    for key in ("public_independent_crypto_operation", "public_key_or_kem_authority", "standardized_post_quantum_security_claim", "audio_witness_can_bypass_other_security_layers"):
        if pq.get(key) is not False:
            blockers.append(f"PASS170_I175_PQ_PUBLIC_BOUNDARY_INVALID:{key}")
    if pq.get("audio_witness_is_redundant_constraint_input") is not True:
        blockers.append("PASS170_I175_AUDIO_REDUNDANCY_ROLE_INVALID")

    reality_source = _text(root, "hhs_runtime/hhs_reality_to_manifold_translation_v1.py", blockers, "PASS170_I175_REALITY_SOURCE_UNREADABLE")
    harness_source = _text(root, "hhs_runtime/hhs_constraint_stack_security_harness_v1.py", blockers, "PASS170_I175_SECURITY_HARNESS_SOURCE_UNREADABLE")
    architecture_source = _text(root, "ARCHITECTURE.md", blockers, "PASS170_I175_ARCHITECTURE_SOURCE_UNREADABLE")
    for token in (
        "def make_harmonic_time_audio_witness",
        "HHS_HARMONIC_TIME_AUDIO_PHASE_ECC_WITNESS_V1",
        "harmonic_time_audio_coherence_when_temporal",
    ):
        if token not in reality_source:
            blockers.append(f"PASS170_I175_AUDIO_ECC_SOURCE_TOKEN_MISSING:{token}")
    for token in ("invalid_harmonic_time_audio_ecc", "REJECTED_TEMPORAL_COHERENCE_DRIFT"):
        if token not in harness_source:
            blockers.append(f"PASS170_I175_AUDIO_SECURITY_HARNESS_TOKEN_MISSING:{token}")
    architecture_token = pq.get("required_architecture_token")
    if not isinstance(architecture_token, str) or architecture_token not in architecture_source:
        blockers.append("PASS170_I175_INTERNAL_PQ_ARCHITECTURE_TOKEN_MISSING")

    authority_invariants = security_profile.get("authority_invariants") if isinstance(security_profile.get("authority_invariants"), dict) else {}
    for key in (
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
        "audio_local_application_can_commit_canonical_state",
        "audio_security_role_can_mint_public_crypto_authority",
    ):
        if authority_invariants.get(key) is not False:
            blockers.append(f"PASS170_I175_FORBIDDEN_AUDIO_AUTHORITY_FLAG:{key}")

    constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if constructor_count != 10:
        blockers.append("PASS170_I175_FASTAPI_CONSTRUCTOR_COUNT_DRIFT")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I175_EVIDENCE_FAILED",
        "parent_i174_exact_main_verified": True,
        "frozen_parent_operation_record_count": parent_index.get("aggregate_record_count"),
        "successor_operation_record_count": index.get("aggregate_record_count"),
        "audio_operation_id": record.get("operation_id"),
        "audio_canonical_route": record.get("HTTP_path"),
        "audio_ecc_role_verified": not any(item.startswith("PASS170_I175_AUDIO_ECC") for item in evidence_blockers),
        "audio_internal_pq_security_role_verified": not any("PQ_" in item or "PUBLIC_CRYPTO" in item for item in evidence_blockers),
        "public_crypto_authority_created": False,
        "observed_launcher_count": len(observed_launchers),
        "canonical_redirect_count": len(canonical_paths),
        "pending_launcher_count": len(pending_paths),
        "pending_launcher_paths": sorted(pending_paths),
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
        raise Pass170I175VerificationError(
            "PASS170_I175_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_PENDING",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I175VerificationError",
    "verify_i175_audio_route_migration",
]

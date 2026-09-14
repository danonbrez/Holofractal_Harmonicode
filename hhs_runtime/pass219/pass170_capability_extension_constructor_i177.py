"""Pass219 I177 / Pass170 capability extension and constructor retirement gate.

I177 inherits exact-main I176 evidence, registers one Pass170-owned audio
application capability scope on the existing Pass190 signed-token verifier,
and retires the legacy Heroku FastAPI constructor to the canonical gateway.
It does not expose the audio ECC/PQ security witness as a public capability and
creates no new token, VM81, Hash72, or Hash216 authority.
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

SCHEMA = "HHS_PASS219_I177_PASS170_CAPABILITY_EXTENSION_CONSTRUCTOR_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I177"
BASE_MAIN = "0707cedbbe41cae8478b498f60db56117da5c462"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
AUDIO_SCOPE = "pass170.audio_language.feedback"
CAPABILITY_REGISTRY = "HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I177.json"
CONSTRUCTOR_REGISTRY = "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I177.json"
OPERATION_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX_I177.json"
AUDIO_RECORD = "contracts/pass219/pass170_operation_records_i177/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_CAPABILITY_V1.json"
CONTRACT_FILE = "contracts/pass219/PASS_219_I177_PASS170_CAPABILITY_EXTENSION_CONSTRUCTOR_1_0.json"
CLASSIFICATION = "PASS170_AUDIO_CAPABILITY_BOUND_HEROKU_CONSTRUCTOR_RETIRED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_CONSTRUCTOR_RETIREMENT_TRANCHE_B_AND_PUBLIC_TRANSPORT_PARITY"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING",
    "PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING",
)


class Pass170I177VerificationError(RuntimeError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I177VerificationError(
            f"PASS170_I177_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I177VerificationError(f"PASS170_I177_JSON_ROOT_INVALID:{path}")
    return payload


def _text(root: Path, path: str, blockers: list[str], code: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(code)
        return ""


def verify_i177_capability_extension_constructor(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    capability = _json(root / CAPABILITY_REGISTRY)
    constructors = _json(root / CONSTRUCTOR_REGISTRY)
    operation_index = _json(root / OPERATION_INDEX)
    audio_shard = _json(root / AUDIO_RECORD)
    contract = _json(root / CONTRACT_FILE)
    inventory = build_i169_pass170_public_authority_inventory(root)
    observed_launchers = _scan_uvicorn_launchers(root)

    # Exact-main parent evidence is immutable input, not replayed against I177.
    parent = contract.get("parent_exact_main_evidence") if isinstance(contract.get("parent_exact_main_evidence"), dict) else {}
    if parent.get("main_sha") != BASE_MAIN:
        blockers.append("PASS170_I177_PARENT_MAIN_SHA_MISMATCH")
    if parent.get("workflow_run") != 34065089119:
        blockers.append("PASS170_I177_PARENT_I176_RUN_MISMATCH")
    if parent.get("artifact_id") != 9998685624:
        blockers.append("PASS170_I177_PARENT_I176_ARTIFACT_MISMATCH")
    if parent.get("artifact_digest") != "sha256:01ac05b0614a2ac68f0d8506bc1439a7f6aaf5a54f61ad007e30a1b3ecd78e1e":
        blockers.append("PASS170_I177_PARENT_I176_DIGEST_MISMATCH")

    if capability.get("schema") != "HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I177_V1":
        blockers.append("PASS170_I177_CAPABILITY_REGISTRY_SCHEMA_INVALID")
    if capability.get("contract") != CONTRACT_ID or capability.get("iteration") != ITERATION:
        blockers.append("PASS170_I177_CAPABILITY_REGISTRY_METADATA_INVALID")
    if capability.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I177_CAPABILITY_BASE_MAIN_MISMATCH")
    token_authority = capability.get("inherited_token_authority") if isinstance(capability.get("inherited_token_authority"), dict) else {}
    if token_authority.get("token_schema") != "HHS_PASS_190_CAPABILITY_V1":
        blockers.append("PASS170_I177_TOKEN_SCHEMA_MISMATCH")
    if token_authority.get("authorization_scheme") != "HHS-Capability":
        blockers.append("PASS170_I177_AUTHORIZATION_SCHEME_MISMATCH")
    if token_authority.get("verifier") != "hhs_runtime.pass190.completion.verify_capability_token":
        blockers.append("PASS170_I177_INHERITED_VERIFIER_MISMATCH")
    for key in ("pass190_registry_mutated", "new_token_issuer_created", "new_signature_algorithm_created"):
        if token_authority.get(key) is not False:
            blockers.append(f"PASS170_I177_TOKEN_AUTHORITY_MUTATION:{key}")

    scopes = capability.get("scope_records") if isinstance(capability.get("scope_records"), list) else []
    if capability.get("scope_count") != 1 or len(scopes) != 1 or not isinstance(scopes[0], dict):
        blockers.append("PASS170_I177_SCOPE_RECORD_COUNT_INVALID")
        scope: dict[str, Any] = {}
    else:
        scope = scopes[0]
    if scope.get("scope_id") != AUDIO_SCOPE:
        blockers.append("PASS170_I177_AUDIO_SCOPE_ID_INVALID")
    if scope.get("operation_ids") != ["public.audio_language.feedback.run"]:
        blockers.append("PASS170_I177_AUDIO_SCOPE_OPERATION_BINDING_INVALID")
    if scope.get("required_on_public_http") is not True or scope.get("anonymous_admission") is not False:
        blockers.append("PASS170_I177_AUDIO_SCOPE_ADMISSION_INVALID")
    excluded = set(scope.get("explicitly_excluded_authority", []))
    required_exclusions = {
        "CANONICAL_VM81_COMMIT",
        "HASH72_MINT",
        "HASH216_CANONICAL_PERSISTENCE",
        "CAPABILITY_TOKEN_ISSUANCE",
        "KEY_OR_KEM_AUTHORITY",
        "PUBLIC_CRYPTO_PRIMITIVE",
        "INTERNAL_HARMONIC_TIME_AUDIO_ECC_SECURITY_AUTHORITY",
    }
    if not required_exclusions.issubset(excluded):
        blockers.append("PASS170_I177_AUDIO_SCOPE_AUTHORITY_EXCLUSIONS_INCOMPLETE")
    security = capability.get("audio_security_boundary") if isinstance(capability.get("audio_security_boundary"), dict) else {}
    for key in (
        "harmonic_time_audio_ecc_remains_internal",
        "post_quantum_oriented_security_signal_remains_internal",
        "public_scope_does_not_expose_internal_security_witness",
    ):
        if security.get(key) is not True:
            blockers.append(f"PASS170_I177_AUDIO_SECURITY_BOUNDARY_INVALID:{key}")
    if security.get("standardized_post_quantum_crypto_claim") is not False:
        blockers.append("PASS170_I177_STANDARDIZED_PQ_CLAIM_FORBIDDEN")

    if operation_index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_I177_V1":
        blockers.append("PASS170_I177_OPERATION_INDEX_SCHEMA_INVALID")
    if operation_index.get("aggregate_record_count") != 48:
        blockers.append("PASS170_I177_OPERATION_COUNT_DRIFT")
    if operation_index.get("new_operation_ids") != []:
        blockers.append("PASS170_I177_UNEXPECTED_NEW_OPERATION_ID")
    if operation_index.get("capability_scope_registry") != CAPABILITY_REGISTRY:
        blockers.append("PASS170_I177_OPERATION_INDEX_CAPABILITY_LINK_INVALID")

    records = audio_shard.get("records") if isinstance(audio_shard.get("records"), list) else []
    if audio_shard.get("replacement_count") != 1 or len(records) != 1 or not isinstance(records[0], dict):
        blockers.append("PASS170_I177_AUDIO_REPLACEMENT_RECORD_INVALID")
        record: dict[str, Any] = {}
    else:
        record = records[0]
    if record.get("operation_id") != "public.audio_language.feedback.run":
        blockers.append("PASS170_I177_AUDIO_OPERATION_ID_INVALID")
    if record.get("capability_scope") != AUDIO_SCOPE or record.get("authorization_scope") != AUDIO_SCOPE:
        blockers.append("PASS170_I177_AUDIO_RECORD_SCOPE_MISMATCH")
    if record.get("admission_policy") != "SIGNED_HHS_CAPABILITY_REQUIRED_FAIL_CLOSED":
        blockers.append("PASS170_I177_AUDIO_RECORD_ADMISSION_POLICY_INVALID")
    if record.get("capability_binding_status") != "VERIFIED_PASS170_SCOPE_BOUND_I177":
        blockers.append("PASS170_I177_AUDIO_RECORD_BINDING_STATUS_INVALID")
    if record.get("new_capability_token_authority") is not False:
        blockers.append("PASS170_I177_AUDIO_RECORD_TOKEN_AUTHORITY_FORBIDDEN")
    pq = record.get("post_quantum_security_binding") if isinstance(record.get("post_quantum_security_binding"), dict) else {}
    if pq.get("scope") != "INTERNAL_CONSTRAINT_ENFORCEMENT_ONLY" or pq.get("exposed_by_public_capability_scope") is not False:
        blockers.append("PASS170_I177_AUDIO_PQ_PUBLIC_SCOPE_LEAK")

    if constructors.get("schema") != "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I177_V1":
        blockers.append("PASS170_I177_CONSTRUCTOR_REGISTRY_SCHEMA_INVALID")
    if constructors.get("parent_constructor_count") != 10:
        blockers.append("PASS170_I177_PARENT_CONSTRUCTOR_COUNT_INVALID")
    if constructors.get("active_constructor_count") != 9 or constructors.get("retired_constructor_count") != 1:
        blockers.append("PASS170_I177_CONSTRUCTOR_SUCCESSOR_COUNTS_INVALID")
    retired = constructors.get("retired_constructor_records") if isinstance(constructors.get("retired_constructor_records"), list) else []
    if len(retired) != 1 or retired[0].get("path") != "hhs_backend/heroku_server.py":
        blockers.append("PASS170_I177_RETIRED_CONSTRUCTOR_IDENTITY_INVALID")
    elif retired[0].get("compatibility_target") != CANONICAL_GATEWAY or retired[0].get("independent_fastapi_constructor") is not False:
        blockers.append("PASS170_I177_RETIRED_CONSTRUCTOR_TARGET_INVALID")

    constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if constructor_count != 9:
        blockers.append("PASS170_I177_FASTAPI_CONSTRUCTOR_COUNT_NOT_REDUCED")

    launcher_by_path = {
        item.get("path"): item for item in observed_launchers if isinstance(item, dict)
    }
    if len(observed_launchers) != 6 or len(launcher_by_path) != 6:
        blockers.append("PASS170_I177_LAUNCHER_COUNT_DRIFT")
    if any(item.get("target") != CANONICAL_GATEWAY for item in launcher_by_path.values()):
        blockers.append("PASS170_I177_CANONICAL_LAUNCHER_PARITY_REGRESSED")

    audio_source = _text(root, "hhs_backend/pass170_audio_language_routes.py", blockers, "PASS170_I177_AUDIO_SOURCE_UNREADABLE")
    heroku_source = _text(root, "hhs_backend/heroku_server.py", blockers, "PASS170_I177_HEROKU_SOURCE_UNREADABLE")
    for token in (
        'AUDIO_CAPABILITY_SCOPE = "pass170.audio_language.feedback"',
        "verify_capability_token(",
        "required_scope=AUDIO_CAPABILITY_SCOPE",
        "admission = enforce_audio_public_admission(authorization)",
        "payload = await execute_audio_language_feedback_request(req)",
    ):
        if token not in audio_source:
            blockers.append(f"PASS170_I177_AUDIO_CAPABILITY_SOURCE_TOKEN_MISSING:{token}")
    if "HHS_PASS170_AUDIO_CAPABILITY_MODEL_UNRESOLVED" in audio_source:
        blockers.append("PASS170_I177_I176_PENDING_REFUSAL_REMAINS")
    if "FastAPI(" in heroku_source or "from fastapi import FastAPI" in heroku_source:
        blockers.append("PASS170_I177_HEROKU_FASTAPI_CONSTRUCTOR_REMAINS")
    if "from hhs_backend.public_api_server import app" not in heroku_source:
        blockers.append("PASS170_I177_HEROKU_CANONICAL_ALIAS_ABSENT")

    cap_invariants = capability.get("invariants") if isinstance(capability.get("invariants"), dict) else {}
    if cap_invariants.get("new_capability_scope_registered") is not True:
        blockers.append("PASS170_I177_SCOPE_REGISTRATION_FLAG_INVALID")
    for key in (
        "new_capability_authority_created",
        "pass190_operation_registry_mutated",
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if cap_invariants.get(key) is not False:
            blockers.append(f"PASS170_I177_FORBIDDEN_AUTHORITY_FLAG:{key}")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I177_EVIDENCE_FAILED",
        "parent_i176_exact_main_verified": not any(item.startswith("PASS170_I177_PARENT_") for item in evidence_blockers),
        "audio_capability_scope": AUDIO_SCOPE,
        "audio_capability_binding_verified": not any("AUDIO_SCOPE" in item or "AUDIO_RECORD_SCOPE" in item or "AUDIO_RECORD_BINDING" in item for item in evidence_blockers),
        "audio_public_signed_admission_verified": not any("AUDIO_CAPABILITY_SOURCE" in item or "AUDIO_RECORD_ADMISSION" in item for item in evidence_blockers),
        "audio_internal_ecc_pq_boundary_preserved": not any("AUDIO_SECURITY" in item or "AUDIO_PQ" in item or "PQ_CLAIM" in item for item in evidence_blockers),
        "pass190_token_verifier_reused": token_authority.get("verifier") == "hhs_runtime.pass190.completion.verify_capability_token",
        "new_capability_scope_registered": True,
        "new_capability_token_authority": False,
        "parent_fastapi_constructor_count": 10,
        "fastapi_constructor_count": constructor_count,
        "retired_constructor_count": 1,
        "retired_constructor_path": "hhs_backend/heroku_server.py",
        "observed_launcher_count": len(observed_launchers),
        "canonical_redirect_count": sum(1 for item in observed_launchers if item.get("target") == CANONICAL_GATEWAY),
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
        raise Pass170I177VerificationError(
            "PASS170_I177_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "AUDIO_SCOPE",
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I177VerificationError",
    "verify_i177_capability_extension_constructor",
]

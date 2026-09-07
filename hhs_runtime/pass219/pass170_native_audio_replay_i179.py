"""Pass219 I179 / Pass170 native audio ABI and receipt replay verifier.

I179 freezes exact-main I178 evidence, verifies the additive exact C audio
security membrane, proves the audio operation replacement record now has
HTTP/CLI/Python/native binding plus non-reexecuting replay, and keeps unsafe
constructor retirement fail-closed. It never treats the audio ECC/PQ-oriented
signal as a public cryptographic authority.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172 import (
    _scan_uvicorn_launchers,
)
from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)

SCHEMA = "HHS_PASS219_I179_PASS170_NATIVE_AUDIO_REPLAY_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I179"
BASE_MAIN = "9f74da54706e252e64a081e68598197a01c5c9c0"
PARENT_I178_RUN = 34066947332
PARENT_I178_ARTIFACT = 9999243782
PARENT_I178_DIGEST = "sha256:0c00e896cac4832a366091c295f1fb973f8a41d783c0794bb8987baac9ab7344"
CONSTRUCTOR_REGISTRY = "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I179.json"
OPERATION_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX_I179.json"
AUDIO_RECORD = "contracts/pass219/pass170_operation_records_i179/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_NATIVE_REPLAY_V1.json"
NATIVE_HEADER = "hhs_runtime/include/hhs_pass219_audio_security_transport_1_0.h"
NATIVE_SOURCE = "hhs_runtime/c/hhs_pass219_audio_security_transport_1_0.inc"
AGGREGATE_HEADER = "hhs_runtime/include/hhs_runtime_exact_abi.h"
AGGREGATE_SOURCE = "hhs_runtime/c/hhs_runtime_exact_abi.c"
AUDIO_ROUTE = "hhs_backend/pass170_audio_language_routes.py"
AUDIO_TRANSPORT = "hhs_runtime/pass219/pass170_audio_transport_i178.py"
AUDIO_NATIVE_BINDING = "hhs_runtime/pass219/pass170_audio_native_abi_i179.py"
AUDIO_ORCHESTRATOR = "hhs_runtime/hhs_audio_language_feedback_orchestrator_v1.py"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
NATIVE_SYMBOL = "hhs_exact_pass219_audio_security_transport_admit"
CLASSIFICATION = "PASS170_AUDIO_NATIVE_ABI_AND_NON_REEXECUTING_REPLAY_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_LEGACY_ROUTE_MIGRATION_AND_REMAINING_PUBLIC_OPERATION_PARITY"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_PENDING",
    "PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING",
)


class Pass170I179VerificationError(RuntimeError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I179VerificationError(
            f"PASS170_I179_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I179VerificationError(f"PASS170_I179_JSON_ROOT_INVALID:{path}")
    return payload


def _text(root: Path, path: str, blockers: list[str]) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(f"PASS170_I179_SOURCE_UNREADABLE:{path}")
        return ""


def verify_i179_native_audio_replay(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    constructors = _json(root / CONSTRUCTOR_REGISTRY)
    index = _json(root / OPERATION_INDEX)
    shard = _json(root / AUDIO_RECORD)
    inventory = build_i169_pass170_public_authority_inventory(root)
    launchers = _scan_uvicorn_launchers(root)

    if constructors.get("schema") != "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I179_V1":
        blockers.append("PASS170_I179_CONSTRUCTOR_REGISTRY_SCHEMA_INVALID")
    if constructors.get("contract") != CONTRACT_ID or constructors.get("iteration") != ITERATION:
        blockers.append("PASS170_I179_CONSTRUCTOR_REGISTRY_METADATA_INVALID")
    if constructors.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I179_CONSTRUCTOR_BASE_MAIN_MISMATCH")
    if constructors.get("parent_active_constructor_count") != 8:
        blockers.append("PASS170_I179_PARENT_CONSTRUCTOR_COUNT_MISMATCH")
    if constructors.get("active_constructor_count") != 8:
        blockers.append("PASS170_I179_CONSTRUCTOR_COUNT_MANIFEST_INVALID")
    if constructors.get("newly_retired_constructor_count") != 0:
        blockers.append("PASS170_I179_UNSAFE_CONSTRUCTOR_RETIREMENT_RECORDED")
    decision = constructors.get("tranche_c_decision") if isinstance(constructors.get("tranche_c_decision"), dict) else {}
    if decision.get("classification") != "NO_SAFE_CONSTRUCTOR_RETIREMENT_WITHOUT_ROUTE_MIGRATION":
        blockers.append("PASS170_I179_TRANCHE_C_DECISION_INVALID")
    if decision.get("unsafe_forced_retirement_performed") is not False:
        blockers.append("PASS170_I179_UNSAFE_FORCED_RETIREMENT")

    observed_constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if observed_constructor_count != 8:
        blockers.append("PASS170_I179_FASTAPI_CONSTRUCTOR_COUNT_DRIFT")
    active_records = constructors.get("active_constructor_records")
    if not isinstance(active_records, list) or len(active_records) != 8:
        blockers.append("PASS170_I179_ACTIVE_CONSTRUCTOR_RECORD_COUNT_INVALID")
    active_paths = {
        item.get("path")
        for item in active_records or []
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    for required in (
        "hhs_backend/runtime/runtime_server.py",
        "hhs_runtime_api_server_v1.py",
        "hhs_backend/runtime_os_source_only_server.py",
    ):
        if required not in active_paths:
            blockers.append(f"PASS170_I179_REQUIRED_UNMIGRATED_CONSTRUCTOR_MISSING:{required}")

    if len(launchers) != 6:
        blockers.append("PASS170_I179_LAUNCHER_COUNT_DRIFT")
    canonical_launchers = [item for item in launchers if item.get("target") == CANONICAL_GATEWAY]
    if len(canonical_launchers) != 6:
        blockers.append("PASS170_I179_CANONICAL_LAUNCHER_PARITY_FAILED")

    if index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_I179_V1":
        blockers.append("PASS170_I179_OPERATION_INDEX_SCHEMA_INVALID")
    if index.get("contract") != CONTRACT_ID or index.get("iteration") != ITERATION:
        blockers.append("PASS170_I179_OPERATION_INDEX_METADATA_INVALID")
    if index.get("frozen_parent_record_count") != 48 or index.get("aggregate_record_count") != 48:
        blockers.append("PASS170_I179_OPERATION_COUNT_INVALID")
    if index.get("new_operation_ids") != []:
        blockers.append("PASS170_I179_UNEXPECTED_NEW_OPERATION_ID")
    transport_state = index.get("transport_state") if isinstance(index.get("transport_state"), dict) else {}
    expected_transport = {
        "http": "EXECUTABLE_VERIFIED_TARGET",
        "cli": "EXECUTABLE_VERIFIED_TARGET",
        "python": "EXECUTABLE_VERIFIED_TARGET",
        "native_abi": "EXECUTABLE_VERIFIED_TARGET",
        "receipt_replay": "NON_REEXECUTING_EXECUTABLE_VERIFIED_TARGET",
    }
    if transport_state != expected_transport:
        blockers.append("PASS170_I179_TRANSPORT_STATE_INVALID")

    records = shard.get("records") if isinstance(shard.get("records"), list) else []
    if len(records) != 1 or not isinstance(records[0], dict):
        blockers.append("PASS170_I179_AUDIO_RECORD_INVALID")
        record: dict[str, Any] = {}
    else:
        record = records[0]
    if record.get("operation_id") != "public.audio_language.feedback.run":
        blockers.append("PASS170_I179_AUDIO_OPERATION_ID_DRIFT")
    if record.get("semantic_version") != "1.3.0":
        blockers.append("PASS170_I179_AUDIO_SEMANTIC_VERSION_INVALID")
    if record.get("native_ABI_symbol") != NATIVE_SYMBOL:
        blockers.append("PASS170_I179_NATIVE_ABI_SYMBOL_INVALID")
    if record.get("replay_supported") is not True or record.get("replay_reexecutes_operation") is not False:
        blockers.append("PASS170_I179_REPLAY_CONTRACT_INVALID")
    if record.get("replay_HTTP_path") != "/v1/audio-language/replay/{receipt_hash72}":
        blockers.append("PASS170_I179_REPLAY_HTTP_PATH_INVALID")
    if record.get("transport_parity_status") != "HTTP_CLI_PYTHON_NATIVE_ABI_EXECUTABLE_VERIFIED_I179":
        blockers.append("PASS170_I179_AUDIO_TRANSPORT_STATUS_INVALID")
    if record.get("receipt_replay_status") != "VERIFIED_NON_REEXECUTING_AUXILIARY_RECEIPT_REPLAY_I179":
        blockers.append("PASS170_I179_AUDIO_REPLAY_STATUS_INVALID")
    if record.get("VM81_commit_required") is not False or record.get("auxiliary_persistence") is not True:
        blockers.append("PASS170_I179_AUDIO_MUTATION_CLASS_INVALID")
    native_invariants = record.get("native_abi_invariants") if isinstance(record.get("native_abi_invariants"), dict) else {}
    for key in (
        "pass190_remains_signed_token_authority",
        "raw5184_audio_hydration_surface_must_exist",
        "harmonic_time_audio_ecc_required",
        "internal_pq_oriented_signal_required",
        "receipt_replay_binding_required",
    ):
        if native_invariants.get(key) is not True:
            blockers.append(f"PASS170_I179_NATIVE_INVARIANT_MISSING:{key}")
    for key in (
        "native_audio_engine_created",
        "native_token_verifier_created",
        "public_crypto_primitive_created",
        "standardized_pq_crypto_claim",
        "independent_key_or_kem_authority",
    ):
        if native_invariants.get(key) is not False:
            blockers.append(f"PASS170_I179_FORBIDDEN_NATIVE_FLAG:{key}")
    replay_invariants = record.get("replay_invariants") if isinstance(record.get("replay_invariants"), dict) else {}
    for key in (
        "same_auxiliary_semantic_sqlite_store",
        "read_only_replay_connection",
        "receipt_hash_recomputed",
        "stored_states_verified",
        "transition_trace_verified",
        "cross_modality_links_verified",
    ):
        if replay_invariants.get(key) is not True:
            blockers.append(f"PASS170_I179_REPLAY_INVARIANT_MISSING:{key}")
    for key in (
        "training_reexecuted",
        "auxiliary_persistence_mutated_during_replay",
        "vm81_replay_claimed",
        "parallel_receipt_ledger_created",
    ):
        if replay_invariants.get(key) is not False:
            blockers.append(f"PASS170_I179_FORBIDDEN_REPLAY_FLAG:{key}")
    security = record.get("security_boundary") if isinstance(record.get("security_boundary"), dict) else {}
    for key in (
        "public_crypto_primitive",
        "standardized_pq_crypto_claim",
        "independent_key_or_kem_authority",
        "canonical_vm81_mutation_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if security.get(key) is not False:
            blockers.append(f"PASS170_I179_FORBIDDEN_SECURITY_FLAG:{key}")

    header = _text(root, NATIVE_HEADER, blockers)
    native_source = _text(root, NATIVE_SOURCE, blockers)
    aggregate_h = _text(root, AGGREGATE_HEADER, blockers)
    aggregate_c = _text(root, AGGREGATE_SOURCE, blockers)
    route_source = _text(root, AUDIO_ROUTE, blockers)
    transport_source = _text(root, AUDIO_TRANSPORT, blockers)
    binding_source = _text(root, AUDIO_NATIVE_BINDING, blockers)
    orchestrator_source = _text(root, AUDIO_ORCHESTRATOR, blockers)

    for token in (
        "HHSExactPass219AudioSecurityTransportWitnessV1",
        NATIVE_SYMBOL,
        "harmonic_time_audio_ecc_valid",
        "internal_pq_oriented_signal_valid",
        "receipt_replay_binding_required",
    ):
        if token not in header:
            blockers.append(f"PASS170_I179_NATIVE_HEADER_TOKEN_MISSING:{token}")
    for token in (
        "signed_capability_verified != 1U",
        "harmonic_time_audio_ecc_valid != 1U",
        "public_crypto_primitive != 0U",
        "canonical_vm81_mutation_authority != 0U",
        "new_hash72_mint_authority != 0U",
        "hash216_persistence_authority != 0U",
    ):
        if token not in native_source:
            blockers.append(f"PASS170_I179_NATIVE_FAIL_CLOSED_TOKEN_MISSING:{token}")
    if 'hhs_pass219_audio_security_transport_1_0.h' not in aggregate_h:
        blockers.append("PASS170_I179_NATIVE_HEADER_NOT_AGGREGATED")
    if 'hhs_pass219_audio_security_transport_1_0.inc' not in aggregate_c:
        blockers.append("PASS170_I179_NATIVE_SOURCE_NOT_AGGREGATED")
    for token in (
        "admit_audio_native_transport",
        "execute_audio_language_public_request",
        "replay_audio_language_feedback_receipt",
        "admit_audio_native_replay",
        "@router.get(REPLAY_PATH)",
    ):
        if token not in route_source:
            blockers.append(f"PASS170_I179_ROUTE_TOKEN_MISSING:{token}")
    for token in (
        "execute_audio_language_public_request",
        "execute_audio_language_public_replay",
        "native_abi_invoked",
        'sub.add_parser("replay")',
    ):
        if token not in transport_source:
            blockers.append(f"PASS170_I179_TRANSPORT_TOKEN_MISSING:{token}")
    for token in (
        "make_harmonic_time_audio_witness",
        "make_non_silent_security_policy",
        "make_hash72_kernel_witness",
        "hhs_exact_pass219_audio5184_hydrate",
        NATIVE_SYMBOL,
    ):
        if token not in binding_source:
            blockers.append(f"PASS170_I179_NATIVE_BINDING_TOKEN_MISSING:{token}")
    for token in (
        "audio_language_feedback_receipts_i179",
        "mode=ro",
        "replay_audio_language_feedback_receipt",
        '"reexecuted": False',
        '"training_reexecuted": False',
        '"auxiliary_persistence_mutated": False',
    ):
        if token not in orchestrator_source:
            blockers.append(f"PASS170_I179_REPLAY_SOURCE_TOKEN_MISSING:{token}")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I179_EVIDENCE_FAILED",
        "parent_i178_exact_main_verified": True,
        "parent_i178_exact_main_run": PARENT_I178_RUN,
        "parent_i178_exact_main_artifact": PARENT_I178_ARTIFACT,
        "parent_i178_exact_main_artifact_digest": PARENT_I178_DIGEST,
        "fastapi_constructor_count": observed_constructor_count,
        "newly_retired_constructor_count": 0,
        "unsafe_constructor_retirement_performed": False,
        "observed_launcher_count": len(launchers),
        "canonical_redirect_count": len(canonical_launchers),
        "aggregate_operation_count": index.get("aggregate_record_count"),
        "audio_native_abi_verified": evidence_verified and record.get("native_ABI_symbol") == NATIVE_SYMBOL,
        "audio_receipt_replay_verified": evidence_verified and record.get("replay_supported") is True,
        "audio_replay_reexecutes_operation": False,
        "audio_internal_ecc_pq_boundary_preserved": evidence_verified,
        "new_capability_token_authority": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "public_crypto_primitive_created": False,
        "standardized_pq_crypto_claim": False,
        "evidence_verified": evidence_verified,
        "evidence_blockers": evidence_blockers,
        "target_blockers": list(EXPECTED_TARGET_BLOCKERS),
        "pass170_terminal_contract_verified": False,
        "canonical_state_mutated_by_verifier": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I179VerificationError(
            "PASS170_I179_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


if __name__ == "__main__":
    print(json.dumps(verify_i179_native_audio_replay(), indent=2, sort_keys=True))


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I179VerificationError",
    "verify_i179_native_audio_replay",
]

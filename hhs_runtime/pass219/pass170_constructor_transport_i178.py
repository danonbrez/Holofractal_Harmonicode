"""Pass219 I178 / Pass170 constructor tranche B + public transport parity.

I178 freezes exact-main I177 evidence, retires the independent
``hhs_runtime.main`` FastAPI constructor while preserving its canonical direct
launcher, and proves that the audio-language operation executes through HTTP,
CLI, and Python surfaces using one signed admission gate and one internal
adapter. Native ABI and public receipt replay remain explicitly nonterminal.
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

SCHEMA = "HHS_PASS219_I178_PASS170_CONSTRUCTOR_TRANSPORT_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I178"
BASE_MAIN = "a01a63eaa05f88bdb3cfda1963bd733a0f542113"
CANONICAL_GATEWAY = "hhs_backend.public_api_server:app"
CONSTRUCTOR_REGISTRY = "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I178.json"
OPERATION_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX_I178.json"
AUDIO_RECORD = "contracts/pass219/pass170_operation_records_i178/HHS_PUBLIC_OPERATION_RECORDS_AUDIO_LANGUAGE_TRANSPORT_V1.json"
CONTRACT_FILE = "contracts/pass219/PASS_219_I178_PASS170_CONSTRUCTOR_TRANSPORT_1_0.json"
AUDIO_TRANSPORT = "hhs_runtime/pass219/pass170_audio_transport_i178.py"
CLASSIFICATION = "PASS170_RUNTIME_MAIN_CONSTRUCTOR_RETIRED_HTTP_CLI_PYTHON_AUDIO_PARITY_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_CONSTRUCTOR_RETIREMENT_TRANCHE_C_NATIVE_AUDIO_ABI_AND_RECEIPT_REPLAY"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_PUBLIC_NATIVE_ABI_PARITY_PENDING",
    "PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING",
)


class Pass170I178VerificationError(RuntimeError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I178VerificationError(
            f"PASS170_I178_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I178VerificationError(f"PASS170_I178_JSON_ROOT_INVALID:{path}")
    return payload


def _text(root: Path, path: str, blockers: list[str], code: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(code)
        return ""


def verify_i178_constructor_transport(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    constructors = _json(root / CONSTRUCTOR_REGISTRY)
    operation_index = _json(root / OPERATION_INDEX)
    audio_shard = _json(root / AUDIO_RECORD)
    contract = _json(root / CONTRACT_FILE)
    inventory = build_i169_pass170_public_authority_inventory(root)
    observed_launchers = _scan_uvicorn_launchers(root)

    parent = contract.get("parent_exact_main_evidence") if isinstance(contract.get("parent_exact_main_evidence"), dict) else {}
    if parent.get("main_sha") != BASE_MAIN:
        blockers.append("PASS170_I178_PARENT_MAIN_SHA_MISMATCH")
    if parent.get("workflow_run") != 34065675606:
        blockers.append("PASS170_I178_PARENT_I177_RUN_MISMATCH")
    if parent.get("artifact_id") != 9998859961:
        blockers.append("PASS170_I178_PARENT_I177_ARTIFACT_MISMATCH")
    if parent.get("artifact_digest") != "sha256:9b4d91010dcc3cd791d75979e798b391f248374eec721c8fbf73c42ef2edaeea":
        blockers.append("PASS170_I178_PARENT_I177_DIGEST_MISMATCH")

    if constructors.get("schema") != "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I178_V1":
        blockers.append("PASS170_I178_CONSTRUCTOR_REGISTRY_SCHEMA_INVALID")
    if constructors.get("contract") != CONTRACT_ID or constructors.get("iteration") != ITERATION:
        blockers.append("PASS170_I178_CONSTRUCTOR_REGISTRY_METADATA_INVALID")
    if constructors.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I178_CONSTRUCTOR_BASE_MAIN_MISMATCH")
    if constructors.get("parent_active_constructor_count") != 9:
        blockers.append("PASS170_I178_PARENT_CONSTRUCTOR_COUNT_INVALID")
    if constructors.get("active_constructor_count") != 8:
        blockers.append("PASS170_I178_SUCCESSOR_CONSTRUCTOR_COUNT_INVALID")
    if constructors.get("cumulative_retired_constructor_count") != 2:
        blockers.append("PASS170_I178_CUMULATIVE_RETIRED_COUNT_INVALID")
    newly_retired = constructors.get("newly_retired_constructor_records") if isinstance(constructors.get("newly_retired_constructor_records"), list) else []
    if len(newly_retired) != 1 or not isinstance(newly_retired[0], dict):
        blockers.append("PASS170_I178_NEW_RETIRED_CONSTRUCTOR_RECORD_INVALID")
        retired: dict[str, Any] = {}
    else:
        retired = newly_retired[0]
    if retired.get("path") != "hhs_runtime/main.py":
        blockers.append("PASS170_I178_RETIRED_CONSTRUCTOR_IDENTITY_INVALID")
    if retired.get("compatibility_target") != CANONICAL_GATEWAY or retired.get("independent_fastapi_constructor") is not False:
        blockers.append("PASS170_I178_RETIRED_CONSTRUCTOR_TARGET_INVALID")

    constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if constructor_count != 8:
        blockers.append("PASS170_I178_FASTAPI_CONSTRUCTOR_COUNT_NOT_REDUCED")

    launcher_by_path = {
        item.get("path"): item for item in observed_launchers if isinstance(item, dict)
    }
    if len(observed_launchers) != 6 or len(launcher_by_path) != 6:
        blockers.append("PASS170_I178_LAUNCHER_COUNT_DRIFT")
    if any(item.get("target") != CANONICAL_GATEWAY for item in launcher_by_path.values()):
        blockers.append("PASS170_I178_CANONICAL_LAUNCHER_PARITY_REGRESSED")
    if launcher_by_path.get("hhs_runtime/main.py", {}).get("target") != CANONICAL_GATEWAY:
        blockers.append("PASS170_I178_RUNTIME_MAIN_DIRECT_LAUNCH_NOT_CANONICAL")

    if operation_index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_I178_V1":
        blockers.append("PASS170_I178_OPERATION_INDEX_SCHEMA_INVALID")
    if operation_index.get("aggregate_record_count") != 48:
        blockers.append("PASS170_I178_OPERATION_COUNT_DRIFT")
    if operation_index.get("new_operation_ids") != []:
        blockers.append("PASS170_I178_UNEXPECTED_NEW_OPERATION_ID")
    transport_state = operation_index.get("transport_state") if isinstance(operation_index.get("transport_state"), dict) else {}
    for surface in ("http", "cli", "python"):
        if transport_state.get(surface) != "EXECUTABLE_VERIFIED_TARGET":
            blockers.append(f"PASS170_I178_TRANSPORT_INDEX_INVALID:{surface}")
    if transport_state.get("native_abi") != "PENDING":
        blockers.append("PASS170_I178_NATIVE_ABI_PREMATURELY_CLAIMED")

    records = audio_shard.get("records") if isinstance(audio_shard.get("records"), list) else []
    if audio_shard.get("replacement_count") != 1 or len(records) != 1 or not isinstance(records[0], dict):
        blockers.append("PASS170_I178_AUDIO_REPLACEMENT_RECORD_INVALID")
        record: dict[str, Any] = {}
    else:
        record = records[0]
    if record.get("operation_id") != "public.audio_language.feedback.run":
        blockers.append("PASS170_I178_AUDIO_OPERATION_ID_INVALID")
    if record.get("CLI_command") != "python -m hhs_runtime.pass219.pass170_audio_transport_i178 invoke":
        blockers.append("PASS170_I178_AUDIO_CLI_BINDING_INVALID")
    if record.get("language_binding_symbol") != "hhs_runtime.pass219.pass170_audio_transport_i178.invoke_audio_language_python":
        blockers.append("PASS170_I178_AUDIO_PYTHON_BINDING_INVALID")
    if record.get("native_ABI_symbol") is not None:
        blockers.append("PASS170_I178_AUDIO_NATIVE_ABI_PREMATURELY_BOUND")
    if record.get("transport_parity_status") != "HTTP_CLI_PYTHON_EXECUTABLE_NATIVE_ABI_PENDING":
        blockers.append("PASS170_I178_AUDIO_TRANSPORT_STATUS_INVALID")
    transport_invariants = record.get("transport_invariants") if isinstance(record.get("transport_invariants"), dict) else {}
    for key in (
        "http_cli_python_share_admission_gate",
        "http_cli_python_share_internal_adapter",
        "cli_executes_real_operation",
        "python_binding_executes_real_operation",
    ):
        if transport_invariants.get(key) is not True:
            blockers.append(f"PASS170_I178_TRANSPORT_INVARIANT_INVALID:{key}")
    for key in ("native_abi_claimed", "parallel_operation_engine_created"):
        if transport_invariants.get(key) is not False:
            blockers.append(f"PASS170_I178_TRANSPORT_AUTHORITY_FLAG:{key}")
    security = record.get("security_boundary") if isinstance(record.get("security_boundary"), dict) else {}
    for key in (
        "internal_audio_ecc_exposed_by_public_transport",
        "internal_pq_oriented_signal_exposed_by_public_transport",
        "public_crypto_primitive",
        "standardized_pq_crypto_claim",
        "independent_key_or_kem_authority",
    ):
        if security.get(key) is not False:
            blockers.append(f"PASS170_I178_AUDIO_SECURITY_PUBLIC_LEAK:{key}")

    runtime_main_source = _text(root, "hhs_runtime/main.py", blockers, "PASS170_I178_RUNTIME_MAIN_SOURCE_UNREADABLE")
    transport_source = _text(root, AUDIO_TRANSPORT, blockers, "PASS170_I178_AUDIO_TRANSPORT_SOURCE_UNREADABLE")
    audio_source = _text(root, "hhs_backend/pass170_audio_language_routes.py", blockers, "PASS170_I178_AUDIO_ROUTE_SOURCE_UNREADABLE")
    if "FastAPI(" in runtime_main_source or "from fastapi import FastAPI" in runtime_main_source:
        blockers.append("PASS170_I178_RUNTIME_MAIN_FASTAPI_CONSTRUCTOR_REMAINS")
    if "from hhs_backend.public_api_server import app" not in runtime_main_source:
        blockers.append("PASS170_I178_RUNTIME_MAIN_CANONICAL_ALIAS_ABSENT")
    if 'uvicorn.run(\n        "hhs_backend.public_api_server:app"' not in runtime_main_source:
        blockers.append("PASS170_I178_RUNTIME_MAIN_CANONICAL_LAUNCH_SOURCE_ABSENT")
    for token in (
        "def invoke_audio_language_python(",
        "enforce_audio_public_admission(",
        "execute_audio_language_feedback_request(",
        "def main(argv:",
        "HHS_PASS170_AUDIO_AUTHORIZATION",
        "native_abi_invoked\": False",
    ):
        if token not in transport_source:
            blockers.append(f"PASS170_I178_TRANSPORT_SOURCE_TOKEN_MISSING:{token}")
    for token in (
        'AUDIO_CAPABILITY_SCOPE = "pass170.audio_language.feedback"',
        "required_scope=AUDIO_CAPABILITY_SCOPE",
    ):
        if token not in audio_source:
            blockers.append(f"PASS170_I178_I177_CAPABILITY_BINDING_REGRESSED:{token}")

    constructor_invariants = constructors.get("invariants") if isinstance(constructors.get("invariants"), dict) else {}
    if constructor_invariants.get("retired_runtime_main_has_no_independent_fastapi_call") is not True:
        blockers.append("PASS170_I178_RETIREMENT_INVARIANT_INVALID")
    if constructor_invariants.get("route_bearing_legacy_constructors_not_retired_without_route_migration") is not True:
        blockers.append("PASS170_I178_ROUTE_MIGRATION_SAFETY_INVARIANT_INVALID")
    for key in (
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
    ):
        if constructor_invariants.get(key) is not False:
            blockers.append(f"PASS170_I178_FORBIDDEN_AUTHORITY_FLAG:{key}")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I178_EVIDENCE_FAILED",
        "parent_i177_exact_main_verified": not any(item.startswith("PASS170_I178_PARENT_") for item in evidence_blockers),
        "parent_fastapi_constructor_count": 9,
        "fastapi_constructor_count": constructor_count,
        "newly_retired_constructor_count": 1,
        "cumulative_retired_constructor_count": 2,
        "retired_constructor_path": "hhs_runtime/main.py",
        "observed_launcher_count": len(observed_launchers),
        "canonical_redirect_count": sum(1 for item in observed_launchers if item.get("target") == CANONICAL_GATEWAY),
        "audio_http_transport_verified": True,
        "audio_cli_transport_verified": not any("CLI_BINDING" in item for item in evidence_blockers),
        "audio_python_transport_verified": not any("PYTHON_BINDING" in item for item in evidence_blockers),
        "audio_native_abi_verified": False,
        "shared_signed_admission_preserved": not any("I177_CAPABILITY_BINDING_REGRESSED" in item for item in evidence_blockers),
        "audio_internal_ecc_pq_boundary_preserved": not any("AUDIO_SECURITY_PUBLIC_LEAK" in item for item in evidence_blockers),
        "new_capability_token_authority": False,
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
        raise Pass170I178VerificationError(
            "PASS170_I178_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I178VerificationError",
    "verify_i178_constructor_transport",
]

"""Pass219 I182 / Pass170 transport parity + degraded-shell verifier."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_legacy_constructor_retirement_i181 import (
    verify_i181_legacy_constructor_retirement,
)
from hhs_runtime.pass219.pass170_public_transport_i182 import (
    AUDIO_NATIVE_SYMBOL,
    AUDIO_OPERATION_ID,
    CANONICAL_GATEWAY,
    CLI_BINDING,
    EXPECTED_AGGREGATE_RECORDS,
    EXPECTED_HTTP_RECORDS,
    EXPECTED_STREAMING_RECORDS,
    PYTHON_BINDING,
    operation_records,
)

SCHEMA = "HHS_PASS219_I182_PASS170_TRANSPORT_DEGRADED_RECONCILIATION_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I182"
BASE_MAIN = "c7f079ad3c0ed67d39bb0be840d47b8d52b24c05"
TRANSPORT_MANIFEST = "HHS_PUBLIC_TRANSPORT_PARITY_I182.json"
DEGRADED_MANIFEST = "HHS_SOURCE_ONLY_DEGRADED_GATEWAY_RECONCILIATION_I182.json"
SOURCE_ONLY_SERVER = "hhs_backend/runtime_os_source_only_server.py"
DISPATCHER = "hhs_backend/runtime_os_application_server.py"
CLASSIFICATION = "PASS170_PUBLIC_TRANSPORT_PARITY_AND_DEGRADED_SAFETY_SHELL_RECONCILED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF"
EXPECTED_TARGET_BLOCKERS = ("PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING",)


class Pass170I182VerificationError(RuntimeError):
    pass


def _json(root: Path, path: str) -> dict[str, Any]:
    try:
        value = json.loads((root / path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I182VerificationError(
            f"PASS170_I182_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(value, dict):
        raise Pass170I182VerificationError(f"PASS170_I182_JSON_ROOT_INVALID:{path}")
    return value


def _text(root: Path, path: str, blockers: list[str]) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(f"PASS170_I182_SOURCE_UNREADABLE:{path}")
        return ""


def _canonical_route_signatures() -> tuple[set[tuple[str, str]], bool]:
    from hhs_backend import public_api_server
    from hhs_backend import runtime_os_application_server

    if runtime_os_application_server.SOURCE_ONLY_DEGRADED_MODE:
        return set(), False
    identity = (
        runtime_os_application_server.PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED is True
        and runtime_os_application_server.app is public_api_server.app
    )
    signatures = public_api_server._http_route_signatures(  # type: ignore[attr-defined]
        runtime_os_application_server.app.routes
    )
    return signatures, identity


def verify_i182_transport_degraded_reconciliation(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
    inspect_live_app: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    try:
        parent = verify_i181_legacy_constructor_retirement(root)
    except Exception as exc:
        parent = {"evidence_verified": False, "error": f"{type(exc).__name__}:{exc}"}
        blockers.append("PASS170_I182_INHERITED_I181_INVALID")
    if parent.get("evidence_verified") is not True:
        blockers.append("PASS170_I182_INHERITED_I181_NOT_VERIFIED")

    transport_manifest = _json(root, TRANSPORT_MANIFEST)
    degraded_manifest = _json(root, DEGRADED_MANIFEST)
    try:
        records = operation_records(root)
    except Exception as exc:
        records = {}
        blockers.append(f"PASS170_I182_OPERATION_CHAIN_INVALID:{type(exc).__name__}:{exc}")

    if transport_manifest.get("schema") != "HHS_PUBLIC_TRANSPORT_PARITY_I182_V1":
        blockers.append("PASS170_I182_TRANSPORT_MANIFEST_SCHEMA_INVALID")
    if transport_manifest.get("contract") != CONTRACT_ID or transport_manifest.get("iteration") != ITERATION:
        blockers.append("PASS170_I182_TRANSPORT_MANIFEST_METADATA_INVALID")
    if transport_manifest.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I182_TRANSPORT_BASE_MAIN_INVALID")
    if transport_manifest.get("frozen_parent_record_count") != EXPECTED_AGGREGATE_RECORDS:
        blockers.append("PASS170_I182_PARENT_RECORD_COUNT_INVALID")
    if transport_manifest.get("canonical_gateway") != CANONICAL_GATEWAY:
        blockers.append("PASS170_I182_CANONICAL_GATEWAY_INVALID")
    if transport_manifest.get("python_binding") != PYTHON_BINDING:
        blockers.append("PASS170_I182_PYTHON_BINDING_INVALID")
    if transport_manifest.get("cli_binding") != CLI_BINDING:
        blockers.append("PASS170_I182_CLI_BINDING_INVALID")

    http_records = [
        record for record in records.values()
        if isinstance(record.get("HTTP_method"), str) and isinstance(record.get("HTTP_path"), str)
    ]
    streaming_only = [
        record for record in records.values()
        if not record.get("HTTP_method") and isinstance(record.get("WebSocket_channel"), str)
    ]
    native_records = [
        record for record in records.values()
        if isinstance(record.get("native_ABI_symbol"), str) and record.get("native_ABI_symbol")
    ]
    if len(records) != EXPECTED_AGGREGATE_RECORDS:
        blockers.append("PASS170_I182_AGGREGATE_OPERATION_COUNT_INVALID")
    if len(http_records) != EXPECTED_HTTP_RECORDS:
        blockers.append("PASS170_I182_HTTP_OPERATION_COUNT_INVALID")
    if len(streaming_only) != EXPECTED_STREAMING_RECORDS:
        blockers.append("PASS170_I182_STREAMING_OPERATION_COUNT_INVALID")
    if len(native_records) != 1:
        blockers.append("PASS170_I182_NATIVE_DECLARATION_COUNT_INVALID")
    elif (
        native_records[0].get("operation_id") != AUDIO_OPERATION_ID
        or native_records[0].get("native_ABI_symbol") != AUDIO_NATIVE_SYMBOL
        or native_records[0].get("transport_parity_status")
        != "HTTP_CLI_PYTHON_NATIVE_ABI_EXECUTABLE_VERIFIED_I179"
    ):
        blockers.append("PASS170_I182_INHERITED_AUDIO_NATIVE_PARITY_INVALID")

    route_signatures: set[tuple[str, str]] = set()
    app_identity = False
    if inspect_live_app:
        try:
            route_signatures, app_identity = _canonical_route_signatures()
        except Exception as exc:
            blockers.append(f"PASS170_I182_CANONICAL_APP_IMPORT_FAILED:{type(exc).__name__}:{exc}")
        if not app_identity:
            blockers.append("PASS170_I182_CANONICAL_APP_IDENTITY_INVALID")
        missing_routes = sorted(
            (str(record["HTTP_method"]).upper(), str(record["HTTP_path"]))
            for record in http_records
            if (str(record["HTTP_method"]).upper(), str(record["HTTP_path"])) not in route_signatures
        )
        if missing_routes:
            blockers.append("PASS170_I182_CANONICAL_HTTP_ROUTE_PARITY_MISMATCH")
    else:
        missing_routes = []

    transport_invariants = transport_manifest.get("invariants", {})
    for key in (
        "all_http_records_bound_to_same_canonical_asgi_app",
        "cli_and_python_share_same_transport_function",
        "http_method_and_path_come_from_frozen_operation_record",
        "path_parameters_must_match_exactly",
        "floating_payloads_rejected_by_transport",
        "authorization_forwarded_without_token_rewriting",
        "streaming_operation_not_scalarized",
        "native_abi_not_invented_for_operations_without_declared_symbol",
        "i179_audio_native_and_replay_evidence_inherited",
    ):
        if transport_invariants.get(key) is not True:
            blockers.append(f"PASS170_I182_TRANSPORT_INVARIANT_FALSE:{key}")
    for key in (
        "generic_transport_reimplements_operation_semantics",
        "new_capability_token_authority",
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "floating_point_canonical_authority",
        "canonical_state_mutated_by_transport_registry",
    ):
        if transport_invariants.get(key) is not False:
            blockers.append(f"PASS170_I182_TRANSPORT_AUTHORITY_FLAG_INVALID:{key}")

    if degraded_manifest.get("schema") != "HHS_SOURCE_ONLY_DEGRADED_GATEWAY_RECONCILIATION_I182_V1":
        blockers.append("PASS170_I182_DEGRADED_MANIFEST_SCHEMA_INVALID")
    selection = degraded_manifest.get("selection", {})
    authority = degraded_manifest.get("degraded_authority", {})
    reconciliation = degraded_manifest.get("reconciliation", {})
    if selection.get("explicit_degraded_request_required") is not True:
        blockers.append("PASS170_I182_DEGRADED_EXPLICIT_SELECTION_NOT_REQUIRED")
    if selection.get("compiled_runtime_must_be_unavailable") is not True:
        blockers.append("PASS170_I182_DEGRADED_RUNTIME_ABSENCE_NOT_REQUIRED")
    if selection.get("normal_production_selects_canonical_pass170_gateway") is not True:
        blockers.append("PASS170_I182_NORMAL_PRODUCTION_GATEWAY_INVALID")
    for key in (
        "canonical_runtime_authority_active",
        "canonical_mutation_permitted",
        "python_replacement_authority",
        "browser_replacement_authority",
        "frontend_is_authority",
        "assistant_runtime_mutation_admitted",
    ):
        if authority.get(key) is not False:
            blockers.append(f"PASS170_I182_DEGRADED_AUTHORITY_FLAG_INVALID:{key}")
    if authority.get("unmatched_api_requests_fail_with_503") is not True:
        blockers.append("PASS170_I182_DEGRADED_UNMATCHED_API_NOT_FAIL_CLOSED")
    if reconciliation.get("explicit_source_only_degraded_gateway_blocker_cleared_by_governed_classification") is not True:
        blockers.append("PASS170_I182_DEGRADED_RECONCILIATION_NOT_DECLARED")
    if reconciliation.get("degraded_safety_behavior_removed") is not False:
        blockers.append("PASS170_I182_DEGRADED_SAFETY_BEHAVIOR_REMOVED")
    if reconciliation.get("degraded_behavior_promoted_to_canonical_authority") is not False:
        blockers.append("PASS170_I182_DEGRADED_PROMOTED_TO_AUTHORITY")

    source_only = _text(root, SOURCE_ONLY_SERVER, blockers)
    dispatcher = _text(root, DISPATCHER, blockers)
    for token in (
        "canonical_runtime_authority_active\": False",
        "canonical_mutation_permitted\": False",
        "python_replacement_authority\": False",
        "frontend_is_authority\": False",
        "status_code=503",
        "project_runtime_os(app, mount_name=PUBLIC_MOUNT_NAME)",
    ):
        if token not in source_only:
            blockers.append(f"PASS170_I182_DEGRADED_SOURCE_TOKEN_MISSING:{token}")
    for token in (
        "_EXPLICIT_DEGRADED_REQUEST",
        "and not _RUNTIME_LIBRARY_PATH.is_file()",
        "from hhs_backend.runtime_os_source_only_server import",
        "PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED = False",
        "if app is not _pass170_public_gateway.app",
        "PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED = True",
    ):
        if token not in dispatcher:
            blockers.append(f"PASS170_I182_DISPATCHER_TOKEN_MISSING:{token}")

    blockers = sorted(set(blockers))
    verified = not blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if verified else "PASS170_I182_EVIDENCE_FAILED",
        "inherited_i181_verified": parent.get("evidence_verified") is True,
        "aggregate_operation_count": len(records),
        "http_operation_count": len(http_records),
        "streaming_only_operation_count": len(streaming_only),
        "native_declared_operation_count": len(native_records),
        "canonical_http_routes_verified": len(http_records) - len(missing_routes) if inspect_live_app else None,
        "canonical_application_identity_verified": app_identity if inspect_live_app else None,
        "generic_cli_transport_bound": True,
        "generic_python_transport_bound": True,
        "semantic_engine_reimplemented": False,
        "streaming_operation_preserved": len(streaming_only) == EXPECTED_STREAMING_RECORDS,
        "audio_native_replay_inherited": not any("AUDIO_NATIVE" in item for item in blockers),
        "source_only_degraded_shell_reconciled": not any("DEGRADED" in item for item in blockers),
        "source_only_degraded_shell_retained_fail_closed": True,
        "new_capability_token_authority": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "canonical_state_mutated_by_verifier": False,
        "evidence_verified": verified,
        "evidence_blockers": blockers,
        "target_blockers": list(EXPECTED_TARGET_BLOCKERS),
        "pass170_terminal_contract_verified": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if blockers and fail_closed:
        raise Pass170I182VerificationError(
            "PASS170_I182_VERIFICATION_FAILED:" + "|".join(blockers)
        )
    return report


if __name__ == "__main__":
    print(json.dumps(verify_i182_transport_degraded_reconciliation(), indent=2, sort_keys=True))


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I182VerificationError",
    "verify_i182_transport_degraded_reconciliation",
]

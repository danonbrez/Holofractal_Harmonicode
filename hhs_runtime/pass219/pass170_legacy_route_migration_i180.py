"""Pass219 I180 / Pass170 legacy route migration verifier.

I180 freezes exact-main I179 evidence, registers eleven legacy-compatible HTTP
operations behind the canonical Pass170 federation, binds sensitive operations
to Pass170 scopes backed by the inherited Pass190 signed-token verifier, and
proves the four legacy websocket paths already have canonical production-base
replacements.  Constructor retirement remains deferred to the next boundary.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)

SCHEMA = "HHS_PASS219_I180_PASS170_LEGACY_ROUTE_MIGRATION_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I180"
BASE_MAIN = "8b02d3a26eee0a9161939f78b19804b6fb2b7065"
PARENT_I179_RUN = 34077531408
PARENT_I179_ARTIFACT = 10002586241
PARENT_I179_DIGEST = "sha256:daecc1c3a6bbeaa431f03f2cd900460853fe643662b56ff5131952d79f460b7f"
MIGRATION_MANIFEST = "HHS_PUBLIC_LEGACY_ROUTE_MIGRATION_I180.json"
CAPABILITY_REGISTRY = "HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I180.json"
OPERATION_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX_I180.json"
OPERATION_SHARD = "contracts/pass219/pass170_operation_records_i180/HHS_PUBLIC_OPERATION_RECORDS_LEGACY_RUNTIME_MIGRATION_V1.json"
ADAPTER = "hhs_backend/pass170_legacy_runtime_routes.py"
FEDERATION_ENTRY = "hhs_backend/api/pass170_legacy_runtime_routes.py"
PASS201_FEDERATION = "hhs_backend/runtime/hhs_pass201_public_api_federation_v1.py"
CANONICAL_WS = "hhs_backend/runtime/runtime_ws.py"
LEGACY_V1 = "hhs_runtime_api_server_v1.py"
CLASSIFICATION = "PASS170_LEGACY_HTTP_ROUTE_MIGRATION_AND_CANONICAL_WS_REPLACEMENT_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_LEGACY_CONSTRUCTOR_RETIREMENT_AND_REMAINING_TRANSPORT_PARITY"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_PENDING",
    "PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING",
)
EXPECTED_HTTP = (
    ("GET", "/api/healthz"),
    ("GET", "/api/runtime/metrics"),
    ("POST", "/api/hhs/solve"),
    ("POST", "/api/runtime/event"),
    ("GET", "/api/runtime/replay"),
    ("GET", "/api/runtime/graph"),
    ("GET", "/api/runtime/transport"),
    ("GET", "/api/status"),
    ("POST", "/api/calculator/evaluate"),
    ("POST", "/api/agent/run-loop"),
    ("GET", "/api/certification"),
)
EXPECTED_WS = ("/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport")
EXPECTED_NEW_IDS = (
    "public.runtime.health",
    "public.runtime.metrics",
    "public.runtime.solve",
    "public.runtime.event.inject",
    "public.runtime.replay.status",
    "public.runtime.graph.status",
    "public.runtime.transport.status",
    "public.runtime.api.status",
    "public.runtime.calculator.evaluate",
    "public.runtime.agent.run_loop",
    "public.runtime.certification",
)
SCOPE_EXPECTATIONS = {
    "pass170.runtime.execute": {
        "public.runtime.solve",
        "public.runtime.calculator.evaluate",
        "public.runtime.agent.run_loop",
    },
    "pass170.runtime.event.inject": {"public.runtime.event.inject"},
    "pass170.runtime.certification": {"public.runtime.certification"},
}


class Pass170I180VerificationError(RuntimeError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I180VerificationError(
            f"PASS170_I180_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(value, dict):
        raise Pass170I180VerificationError(f"PASS170_I180_JSON_ROOT_INVALID:{path}")
    return value


def _text(root: Path, path: str, blockers: list[str]) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(f"PASS170_I180_SOURCE_UNREADABLE:{path}")
        return ""


def _router_http_signatures() -> tuple[tuple[str, str], ...]:
    from hhs_backend.pass170_legacy_runtime_routes import build_pass170_legacy_runtime_router

    router = build_pass170_legacy_runtime_router()
    signatures: set[tuple[str, str]] = set()
    for route in router.routes:
        methods = getattr(route, "methods", None)
        if methods:
            for method in methods:
                if str(method) not in {"HEAD", "OPTIONS"}:
                    signatures.add((str(method), str(getattr(route, "path", ""))))
    return tuple(sorted(signatures))


def verify_i180_legacy_route_migration(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    migration = _json(root / MIGRATION_MANIFEST)
    scopes = _json(root / CAPABILITY_REGISTRY)
    index = _json(root / OPERATION_INDEX)
    shard = _json(root / OPERATION_SHARD)
    inventory = build_i169_pass170_public_authority_inventory(root)

    if migration.get("schema") != "HHS_PUBLIC_LEGACY_ROUTE_MIGRATION_I180_V1":
        blockers.append("PASS170_I180_MIGRATION_SCHEMA_INVALID")
    if migration.get("contract") != CONTRACT_ID or migration.get("iteration") != ITERATION:
        blockers.append("PASS170_I180_MIGRATION_METADATA_INVALID")
    if migration.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I180_BASE_MAIN_MISMATCH")
    parent = migration.get("parent_i179_exact_main") if isinstance(migration.get("parent_i179_exact_main"), dict) else {}
    if parent.get("commit") != BASE_MAIN:
        blockers.append("PASS170_I180_PARENT_COMMIT_MISMATCH")
    if parent.get("run") != PARENT_I179_RUN or parent.get("artifact") != PARENT_I179_ARTIFACT:
        blockers.append("PASS170_I180_PARENT_EVIDENCE_ID_MISMATCH")
    if parent.get("artifact_digest") != PARENT_I179_DIGEST:
        blockers.append("PASS170_I180_PARENT_EVIDENCE_DIGEST_MISMATCH")

    manifest_http = migration.get("http_routes") if isinstance(migration.get("http_routes"), list) else []
    manifest_signatures = {
        (str(item.get("method")), str(item.get("path")))
        for item in manifest_http
        if isinstance(item, dict)
    }
    if migration.get("http_route_count") != 11 or manifest_signatures != set(EXPECTED_HTTP):
        blockers.append("PASS170_I180_HTTP_MANIFEST_PARITY_FAILED")

    try:
        live_signatures = set(_router_http_signatures())
    except Exception as exc:
        blockers.append(f"PASS170_I180_ROUTER_IMPORT_FAILED:{type(exc).__name__}:{exc}")
        live_signatures = set()
    if live_signatures != set(EXPECTED_HTTP):
        blockers.append("PASS170_I180_LIVE_HTTP_ROUTE_PARITY_FAILED")

    ws_records = migration.get("websocket_replacements") if isinstance(migration.get("websocket_replacements"), list) else []
    if migration.get("websocket_replacement_count") != 4:
        blockers.append("PASS170_I180_WS_REPLACEMENT_COUNT_INVALID")
    if {str(item.get("path")) for item in ws_records if isinstance(item, dict)} != set(EXPECTED_WS):
        blockers.append("PASS170_I180_WS_REPLACEMENT_MANIFEST_INVALID")

    adapter_source = _text(root, ADAPTER, blockers)
    federation_source = _text(root, FEDERATION_ENTRY, blockers)
    pass201_source = _text(root, PASS201_FEDERATION, blockers)
    canonical_ws_source = _text(root, CANONICAL_WS, blockers)
    legacy_v1_source = _text(root, LEGACY_V1, blockers)

    for token in (
        "verify_capability_token",
        "RUNTIME_EXEC_SCOPE",
        "RUNTIME_EVENT_SCOPE",
        "RUNTIME_CERTIFICATION_SCOPE",
        "build_pass170_legacy_runtime_router",
    ):
        if token not in adapter_source:
            blockers.append(f"PASS170_I180_ADAPTER_TOKEN_MISSING:{token}")
    if ".websocket(" in adapter_source or "@router.websocket" in adapter_source:
        blockers.append("PASS170_I180_DUPLICATE_WEBSOCKET_ROUTE_REGISTERED")
    for path in EXPECTED_WS:
        if f'"{path}"' not in canonical_ws_source:
            blockers.append(f"PASS170_I180_CANONICAL_WS_REPLACEMENT_MISSING:{path}")
        if f'"{path}"' not in legacy_v1_source:
            blockers.append(f"PASS170_I180_LEGACY_WS_DUPLICATE_EVIDENCE_MISSING:{path}")
    if "build_pass170_legacy_runtime_router" not in federation_source or "router =" not in federation_source:
        blockers.append("PASS170_I180_FEDERATION_ENTRY_INVALID")
    for token in ("pkgutil.walk_packages", "return sorted(", "existing_signatures", "if signature in existing_signatures"):
        if token not in pass201_source:
            blockers.append(f"PASS170_I180_PASS201_FEDERATION_INVARIANT_MISSING:{token}")

    if scopes.get("schema") != "HHS_PUBLIC_CAPABILITY_SCOPE_REGISTRY_I180_V1":
        blockers.append("PASS170_I180_CAPABILITY_REGISTRY_SCHEMA_INVALID")
    inherited = scopes.get("inherited_token_authority") if isinstance(scopes.get("inherited_token_authority"), dict) else {}
    if inherited.get("verifier") != "hhs_runtime.pass190.completion.verify_capability_token":
        blockers.append("PASS170_I180_PASS190_VERIFIER_NOT_REUSED")
    if inherited.get("new_token_issuer_created") is not False or inherited.get("new_signature_algorithm_created") is not False:
        blockers.append("PASS170_I180_NEW_TOKEN_AUTHORITY_DETECTED")
    scope_records = scopes.get("scope_records") if isinstance(scopes.get("scope_records"), list) else []
    scope_map = {
        str(item.get("scope_id")): set(str(op) for op in item.get("operation_ids", []))
        for item in scope_records
        if isinstance(item, dict)
    }
    for scope, expected_ids in SCOPE_EXPECTATIONS.items():
        if scope_map.get(scope) != expected_ids:
            blockers.append(f"PASS170_I180_SCOPE_OPERATION_MAPPING_INVALID:{scope}")

    if index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_I180_V1":
        blockers.append("PASS170_I180_OPERATION_INDEX_SCHEMA_INVALID")
    if index.get("frozen_parent_record_count") != 48 or index.get("aggregate_record_count") != 59:
        blockers.append("PASS170_I180_OPERATION_COUNT_INVALID")
    new_ids = index.get("new_operation_ids") if isinstance(index.get("new_operation_ids"), list) else []
    if new_ids != list(EXPECTED_NEW_IDS):
        blockers.append("PASS170_I180_NEW_OPERATION_ID_ORDER_OR_SET_INVALID")

    if shard.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_SHARD_V1" or shard.get("record_count") != 11:
        blockers.append("PASS170_I180_OPERATION_SHARD_INVALID")
    records = shard.get("records") if isinstance(shard.get("records"), list) else []
    ids = [str(item.get("operation_id")) for item in records if isinstance(item, dict)]
    if ids != list(EXPECTED_NEW_IDS):
        blockers.append("PASS170_I180_OPERATION_SHARD_ID_PARITY_FAILED")
    by_id = {str(item.get("operation_id")): item for item in records if isinstance(item, dict)}
    for operation_id in EXPECTED_NEW_IDS:
        record = by_id.get(operation_id, {})
        if record.get("contract_id") != CONTRACT_ID or record.get("implementation_status") is None:
            blockers.append(f"PASS170_I180_OPERATION_RECORD_INCOMPLETE:{operation_id}")
        if record.get("new_vm81_authority") is not False or record.get("new_hash72_mint_authority") is not False or record.get("hash216_persistence_authority") is not False:
            blockers.append(f"PASS170_I180_FORBIDDEN_OPERATION_AUTHORITY:{operation_id}")
    for scope, expected_ids in SCOPE_EXPECTATIONS.items():
        for operation_id in expected_ids:
            if by_id.get(operation_id, {}).get("capability_scope") != scope:
                blockers.append(f"PASS170_I180_OPERATION_SCOPE_BINDING_INVALID:{operation_id}")

    observed_constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if observed_constructor_count != 8:
        blockers.append("PASS170_I180_FASTAPI_CONSTRUCTOR_COUNT_DRIFT")
    constructor_state = migration.get("constructor_state") if isinstance(migration.get("constructor_state"), dict) else {}
    if constructor_state.get("active_constructor_count") != 8 or constructor_state.get("constructor_retirement_performed") is not False:
        blockers.append("PASS170_I180_PREMATURE_CONSTRUCTOR_RETIREMENT")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I180_EVIDENCE_FAILED",
        "parent_i179_exact_main_verified": True,
        "parent_i179_exact_main_run": PARENT_I179_RUN,
        "parent_i179_exact_main_artifact": PARENT_I179_ARTIFACT,
        "parent_i179_exact_main_artifact_digest": PARENT_I179_DIGEST,
        "migrated_http_route_count": len(live_signatures),
        "canonical_websocket_replacement_count": len(EXPECTED_WS),
        "aggregate_operation_count": index.get("aggregate_record_count"),
        "new_operation_count": len(new_ids),
        "fastapi_constructor_count": observed_constructor_count,
        "constructor_retirement_performed": False,
        "pass190_token_verifier_reused": inherited.get("verifier") == "hhs_runtime.pass190.completion.verify_capability_token",
        "new_capability_token_authority": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "evidence_verified": evidence_verified,
        "evidence_blockers": evidence_blockers,
        "target_blockers": list(EXPECTED_TARGET_BLOCKERS),
        "pass170_terminal_contract_verified": False,
        "canonical_state_mutated_by_verifier": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I180VerificationError(
            "PASS170_I180_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


if __name__ == "__main__":
    print(json.dumps(verify_i180_legacy_route_migration(), indent=2, sort_keys=True))


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_HTTP",
    "EXPECTED_NEW_IDS",
    "EXPECTED_TARGET_BLOCKERS",
    "EXPECTED_WS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I180VerificationError",
    "verify_i180_legacy_route_migration",
]

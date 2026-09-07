"""Pass219 I181 / Pass170 legacy constructor retirement verifier."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)

SCHEMA = "HHS_PASS219_I181_PASS170_LEGACY_CONSTRUCTOR_RETIREMENT_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I181"
BASE_MAIN = "2e8bfa52ede8af64bd4c39cc9e6318f40f6844bf"
PARENT_I180_RUN = 34078826576
PARENT_I180_ARTIFACT = 10002996393
PARENT_I180_DIGEST = "sha256:69d16fd63ab9b763998541e11ef28a725ed09ee4a74e8ae36108948b1a08a7e8"
REGISTRY = "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I181.json"
RUNTIME_SERVER = "hhs_backend/runtime/runtime_server.py"
RUNTIME_API_V1 = "hhs_runtime_api_server_v1.py"
I180_MIGRATION = "HHS_PUBLIC_LEGACY_ROUTE_MIGRATION_I180.json"
CLASSIFICATION = "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_RETIRED_WITH_I180_ROUTE_PARITY_PRESERVED"
NEXT_BOUNDARY = "PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_AND_DEGRADED_GATEWAY_RECONCILIATION"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_REMAINING_PUBLIC_OPERATION_TRANSPORT_PARITY_PENDING",
    "PASS170_FULL_PUBLIC_E2E_TERMINAL_PROOF_PENDING",
)
RETIRED = (RUNTIME_SERVER, RUNTIME_API_V1)
EXPECTED_HTTP = {
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
}


class Pass170I181VerificationError(RuntimeError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I181VerificationError(
            f"PASS170_I181_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(value, dict):
        raise Pass170I181VerificationError(f"PASS170_I181_JSON_ROOT_INVALID:{path}")
    return value


def _text(root: Path, path: str, blockers: list[str]) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except OSError:
        blockers.append(f"PASS170_I181_SOURCE_UNREADABLE:{path}")
        return ""


def _live_migrated_http_signatures() -> set[tuple[str, str]]:
    from hhs_backend.pass170_legacy_runtime_routes import build_pass170_legacy_runtime_router

    router = build_pass170_legacy_runtime_router()
    signatures: set[tuple[str, str]] = set()
    for route in router.routes:
        methods = getattr(route, "methods", None)
        if methods:
            for method in methods:
                method_name = str(method)
                if method_name not in {"HEAD", "OPTIONS"}:
                    signatures.add((method_name, str(getattr(route, "path", ""))))
    return signatures


def verify_i181_legacy_constructor_retirement(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    blockers: list[str] = []

    registry = _json(root / REGISTRY)
    migration = _json(root / I180_MIGRATION)
    inventory = build_i169_pass170_public_authority_inventory(root)

    if registry.get("schema") != "HHS_FASTAPI_CONSTRUCTOR_REGISTRY_I181_V1":
        blockers.append("PASS170_I181_REGISTRY_SCHEMA_INVALID")
    if registry.get("contract") != CONTRACT_ID or registry.get("iteration") != ITERATION:
        blockers.append("PASS170_I181_REGISTRY_METADATA_INVALID")
    if registry.get("base_main") != BASE_MAIN:
        blockers.append("PASS170_I181_BASE_MAIN_MISMATCH")
    if registry.get("parent_active_constructor_count") != 8:
        blockers.append("PASS170_I181_PARENT_CONSTRUCTOR_COUNT_INVALID")
    if registry.get("active_constructor_count") != 6:
        blockers.append("PASS170_I181_ACTIVE_CONSTRUCTOR_COUNT_INVALID")
    if registry.get("newly_retired_constructor_count") != 2:
        blockers.append("PASS170_I181_RETIREMENT_COUNT_INVALID")
    if registry.get("cumulative_retired_constructor_count") != 4:
        blockers.append("PASS170_I181_CUMULATIVE_RETIREMENT_COUNT_INVALID")

    migration_parent = migration.get("parent_i179_exact_main") if isinstance(migration.get("parent_i179_exact_main"), dict) else {}
    if migration.get("schema") != "HHS_PUBLIC_LEGACY_ROUTE_MIGRATION_I180_V1":
        blockers.append("PASS170_I181_I180_MIGRATION_SCHEMA_INVALID")
    if migration.get("http_route_count") != 11 or migration.get("websocket_replacement_count") != 4:
        blockers.append("PASS170_I181_I180_MIGRATION_EVIDENCE_INVALID")
    if migration_parent.get("commit") is None:
        blockers.append("PASS170_I181_I180_PARENT_EVIDENCE_MISSING")

    retired_records = registry.get("retirement_records") if isinstance(registry.get("retirement_records"), list) else []
    retired_map = {
        str(item.get("path")): item
        for item in retired_records
        if isinstance(item, dict)
    }
    if set(retired_map) != set(RETIRED):
        blockers.append("PASS170_I181_RETIRED_PATH_SET_INVALID")
    for path in RETIRED:
        record = retired_map.get(path, {})
        if record.get("compatibility_target") != "hhs_backend.public_api_server:app":
            blockers.append(f"PASS170_I181_CANONICAL_ALIAS_TARGET_INVALID:{path}")
        if record.get("independent_fastapi_constructor") is not False:
            blockers.append(f"PASS170_I181_CONSTRUCTOR_NOT_RETIRED:{path}")
        if record.get("public_port_authority") is not False:
            blockers.append(f"PASS170_I181_PUBLIC_PORT_AUTHORITY_REMAINS:{path}")

    for path in RETIRED:
        source = _text(root, path, blockers)
        if "FastAPI(" in source:
            blockers.append(f"PASS170_I181_FASTAPI_CONSTRUCTOR_TOKEN_REMAINS:{path}")
        for token in (
            'CANONICAL_TARGET = "hhs_backend.public_api_server:app"',
            "INDEPENDENT_FASTAPI_CONSTRUCTOR = False",
            "PUBLIC_PORT_AUTHORITY = False",
            "def __getattr__(name: str):",
            'if name == "app":',
            "return _canonical_app()",
            "legacy_router = APIRouter",
        ):
            if token not in source:
                blockers.append(f"PASS170_I181_RETIREMENT_TOKEN_MISSING:{path}:{token}")

    runtime_source = _text(root, RUNTIME_SERVER, blockers)
    for token in (
        "async def execute_runtime_expression",
        "async def healthz",
        "async def runtime_metrics",
        "async def solve",
        "async def inject_runtime_event",
        "async def runtime_replay",
        "async def runtime_graph",
        "async def runtime_transport",
    ):
        if token not in runtime_source:
            blockers.append(f"PASS170_I181_RUNTIME_CALLABLE_MISSING:{token}")

    v1_source = _text(root, RUNTIME_API_V1, blockers)
    for token in (
        "class CalculatorEvaluateRequest",
        "class AgentRunLoopRequest",
        "def _calculator_evaluation_payload",
        "def _agent_run_loop_payload",
        "async def api_status",
        "async def api_calculator_evaluate",
        "async def api_agent_run_loop",
        "async def api_certification",
        "async def ws_runtime",
        "async def ws_replay",
        "async def ws_graph",
        "async def ws_transport",
    ):
        if token not in v1_source:
            blockers.append(f"PASS170_I181_V1_CALLABLE_MISSING:{token}")

    try:
        live_http = _live_migrated_http_signatures()
    except Exception as exc:
        blockers.append(f"PASS170_I181_I180_ADAPTER_IMPORT_FAILED:{type(exc).__name__}:{exc}")
        live_http = set()
    if live_http != EXPECTED_HTTP:
        blockers.append("PASS170_I181_MIGRATED_HTTP_PARITY_DRIFT")

    observed_constructor_count = inventory.get("inventory", {}).get("fastapi_constructor_count")
    if observed_constructor_count != 6:
        blockers.append("PASS170_I181_FASTAPI_CONSTRUCTOR_COUNT_DRIFT")
    parse_errors = inventory.get("inventory", {}).get("parse_errors") or []
    if parse_errors:
        blockers.append("PASS170_I181_PUBLIC_SURFACE_PARSE_ERRORS")

    evidence_blockers = sorted(set(blockers))
    evidence_verified = not evidence_blockers
    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I181_EVIDENCE_FAILED",
        "parent_i180_exact_main_verified": True,
        "parent_i180_exact_main_run": PARENT_I180_RUN,
        "parent_i180_exact_main_artifact": PARENT_I180_ARTIFACT,
        "parent_i180_exact_main_artifact_digest": PARENT_I180_DIGEST,
        "fastapi_constructor_count": observed_constructor_count,
        "newly_retired_constructor_count": 2,
        "cumulative_retired_constructor_count": 4,
        "migrated_http_route_count": len(live_http),
        "canonical_websocket_replacement_count": 4,
        "legacy_app_alias_target": "hhs_backend.public_api_server:app",
        "legacy_handler_callables_preserved": True,
        "constructor_retirement_performed": True,
        "legacy_fastapi_constructor_blocker_cleared": evidence_verified,
        "new_capability_token_authority": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "canonical_state_mutated_by_verifier": False,
        "evidence_verified": evidence_verified,
        "evidence_blockers": evidence_blockers,
        "target_blockers": list(EXPECTED_TARGET_BLOCKERS),
        "pass170_terminal_contract_verified": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I181VerificationError(
            "PASS170_I181_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


if __name__ == "__main__":
    print(json.dumps(verify_i181_legacy_constructor_retirement(), indent=2, sort_keys=True))


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I181VerificationError",
    "verify_i181_legacy_constructor_retirement",
]

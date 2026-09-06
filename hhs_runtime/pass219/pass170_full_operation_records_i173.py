"""Pass219 I173 / Pass170 full public operation-record verification.

The I171 route-identity registry remains frozen so inherited evidence can be
revalidated byte-for-byte. I173 extends it with a root operation-record index
and explicit JSON shards. This verifier requires one complete Section-9 record
for every one of the 47 I171 route identities and binds every record to the
actual decorated FastAPI handler in executable source.

I173 is deliberately nonterminal. It clears only the full-operation-record
construction blocker; legacy launcher/constructor retirement plus CLI/native/
language-binding parity and public end-to-end receipt/replay proof remain
explicit later Pass170 boundaries.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172_gate import (
    verify_i172_legacy_constructor_router_manifest,
)

SCHEMA = "HHS_PASS219_I173_PASS170_FULL_OPERATION_RECORDS_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I173"
BASE_MAIN = "0a199e422e1bf10318b4dbfe0530afc3ba36fdef"
PARENT_REGISTRY = "HHS_PUBLIC_OPERATION_REGISTRY.json"
RECORD_INDEX = "HHS_PUBLIC_OPERATION_RECORD_INDEX.json"
CLASSIFICATION = "PASS170_FULL_OPERATION_RECORDS_EXECUTABLE_SOURCE_BOUND_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_LEGACY_LAUNCHER_RETIREMENT_AND_PUBLIC_PARITY_COMPLETION"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_EXPLICIT_SOURCE_ONLY_DEGRADED_GATEWAY_REMAINS",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
    "PASS170_LEGACY_SELF_LAUNCH_BYPASSES_REMAIN",
    "PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING",
    "PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING",
)
_ROUTE_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace", "websocket"}


class Pass170I173VerificationError(RuntimeError):
    """Raised when the I173 record package does not match executable source."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I173VerificationError(
            f"PASS170_I173_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I173VerificationError(f"PASS170_I173_JSON_ROOT_INVALID:{path}")
    return payload


def _constant_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _module_path(root: Path, module: str) -> Path:
    return root / (module.replace(".", "/") + ".py")


def _route_handlers(path: Path) -> dict[tuple[str, str], str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise Pass170I173VerificationError(
            f"PASS170_I173_ROUTE_SOURCE_PARSE_FAILED:{path}:{type(exc).__name__}"
        ) from exc
    routes: dict[tuple[str, str], str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.lower()
            if method not in _ROUTE_METHODS or not decorator.args:
                continue
            route = _constant_string(decorator.args[0])
            if route is None:
                continue
            signature = (method.upper(), route)
            if signature in routes and routes[signature] != node.name:
                raise Pass170I173VerificationError(
                    f"PASS170_I173_EXECUTABLE_ROUTE_DUPLICATE:{path}:{signature[0]}:{signature[1]}"
                )
            routes[signature] = node.name
    return routes


def _expected_routes(parent: dict[str, Any]) -> dict[str, dict[str, str]]:
    expected: dict[str, dict[str, str]] = {}
    direct = parent.get("direct_gateway_routes")
    if not isinstance(direct, list):
        raise Pass170I173VerificationError("PASS170_I173_PARENT_DIRECT_ROUTES_INVALID")
    for record in direct:
        if not isinstance(record, dict):
            raise Pass170I173VerificationError("PASS170_I173_PARENT_DIRECT_RECORD_INVALID")
        operation_id = record.get("operation_id")
        method = record.get("method")
        path = record.get("path")
        if not all(isinstance(value, str) and value for value in (operation_id, method, path)):
            raise Pass170I173VerificationError("PASS170_I173_PARENT_DIRECT_RECORD_INVALID")
        expected[operation_id] = {
            "method": method.upper(),
            "path": path,
            "module": "hhs_backend.public_api_server",
        }

    delegates = parent.get("router_delegates")
    if not isinstance(delegates, list):
        raise Pass170I173VerificationError("PASS170_I173_PARENT_DELEGATES_INVALID")
    for delegate in delegates:
        if not isinstance(delegate, dict) or not isinstance(delegate.get("module"), str):
            raise Pass170I173VerificationError("PASS170_I173_PARENT_DELEGATE_INVALID")
        module = delegate["module"]
        routes = delegate.get("routes")
        if not isinstance(routes, list):
            raise Pass170I173VerificationError("PASS170_I173_PARENT_DELEGATE_ROUTES_INVALID")
        for record in routes:
            if not isinstance(record, dict):
                raise Pass170I173VerificationError("PASS170_I173_PARENT_DELEGATE_ROUTE_INVALID")
            operation_id = record.get("route_operation_id")
            method = record.get("method")
            path = record.get("path")
            if not all(isinstance(value, str) and value for value in (operation_id, method, path)):
                raise Pass170I173VerificationError("PASS170_I173_PARENT_DELEGATE_ROUTE_INVALID")
            if operation_id in expected:
                raise Pass170I173VerificationError(f"PASS170_I173_PARENT_OPERATION_ID_DUPLICATE:{operation_id}")
            expected[operation_id] = {"method": method.upper(), "path": path, "module": module}
    return expected


def verify_i173_full_operation_records(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    evidence_blockers: list[str] = []

    try:
        inherited_i172 = verify_i172_legacy_constructor_router_manifest(root)
    except Exception as exc:
        inherited_i172 = {"evidence_verified": False, "target_blockers": [], "error": f"{type(exc).__name__}:{exc}"}
        evidence_blockers.append("PASS170_I173_INHERITED_I172_INVALID")

    try:
        parent = _load_json(root / PARENT_REGISTRY)
        index = _load_json(root / RECORD_INDEX)
    except Pass170I173VerificationError:
        if fail_closed:
            raise
        parent = {}
        index = {}
        evidence_blockers.append("PASS170_I173_REQUIRED_REGISTRY_UNREADABLE")

    if inherited_i172.get("evidence_verified") is not True:
        evidence_blockers.append("PASS170_I173_INHERITED_I172_NOT_VERIFIED")
    if parent.get("contract") != CONTRACT_ID or parent.get("iteration") != "PASS219-I171":
        evidence_blockers.append("PASS170_I173_FROZEN_PARENT_REGISTRY_METADATA_INVALID")
    if index.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_INDEX_V1":
        evidence_blockers.append("PASS170_I173_INDEX_SCHEMA_INVALID")
    if index.get("contract") != CONTRACT_ID or index.get("iteration") != ITERATION:
        evidence_blockers.append("PASS170_I173_INDEX_METADATA_INVALID")
    if index.get("parent_registry") != PARENT_REGISTRY:
        evidence_blockers.append("PASS170_I173_INDEX_PARENT_MISMATCH")

    required_fields = index.get("required_fields")
    if not isinstance(required_fields, list) or not required_fields or any(not isinstance(item, str) for item in required_fields):
        required_fields = []
        evidence_blockers.append("PASS170_I173_REQUIRED_FIELD_SET_INVALID")
    required_set = set(required_fields)

    try:
        expected = _expected_routes(parent)
    except Pass170I173VerificationError as exc:
        expected = {}
        evidence_blockers.append(str(exc))
    if len(expected) != 47:
        evidence_blockers.append("PASS170_I173_EXPECTED_ROUTE_COUNT_MISMATCH")

    shards = index.get("shards")
    if not isinstance(shards, list) or not shards:
        shards = []
        evidence_blockers.append("PASS170_I173_SHARD_INDEX_INVALID")

    records: list[dict[str, Any]] = []
    shard_reports: list[dict[str, Any]] = []
    for shard_ref in shards:
        if not isinstance(shard_ref, dict):
            evidence_blockers.append("PASS170_I173_SHARD_REFERENCE_INVALID")
            continue
        path_text = shard_ref.get("path")
        shard_id = shard_ref.get("shard_id")
        declared_count = shard_ref.get("record_count")
        if not isinstance(path_text, str) or not isinstance(shard_id, str) or not isinstance(declared_count, int):
            evidence_blockers.append("PASS170_I173_SHARD_REFERENCE_INVALID")
            continue
        try:
            shard = _load_json(root / path_text)
        except Pass170I173VerificationError as exc:
            evidence_blockers.append(str(exc))
            continue
        shard_records = shard.get("records")
        if shard.get("schema") != "HHS_PUBLIC_OPERATION_RECORD_SHARD_V1":
            evidence_blockers.append("PASS170_I173_SHARD_SCHEMA_INVALID")
        if shard.get("contract") != CONTRACT_ID or shard.get("iteration") != ITERATION:
            evidence_blockers.append("PASS170_I173_SHARD_METADATA_INVALID")
        if shard.get("shard_id") != shard_id:
            evidence_blockers.append("PASS170_I173_SHARD_ID_MISMATCH")
        if shard.get("required_fields") != required_fields:
            evidence_blockers.append("PASS170_I173_SHARD_REQUIRED_FIELDS_MISMATCH")
        if not isinstance(shard_records, list):
            shard_records = []
            evidence_blockers.append("PASS170_I173_SHARD_RECORDS_INVALID")
        if shard.get("record_count") != len(shard_records) or declared_count != len(shard_records):
            evidence_blockers.append("PASS170_I173_SHARD_COUNT_MISMATCH")
        records.extend(item for item in shard_records if isinstance(item, dict))
        shard_reports.append({"shard_id": shard_id, "path": path_text, "record_count": len(shard_records)})

    if index.get("aggregate_record_count") != 47 or len(records) != 47:
        evidence_blockers.append("PASS170_I173_AGGREGATE_RECORD_COUNT_MISMATCH")

    operation_ids: list[str] = []
    signatures: list[tuple[str, str]] = []
    source_cache: dict[str, dict[tuple[str, str], str]] = {}
    source_bound_count = 0
    transport_pending_count = 0
    receipt_pending_count = 0

    for record in records:
        missing = sorted(required_set - set(record))
        if missing:
            evidence_blockers.append("PASS170_I173_OPERATION_REQUIRED_FIELDS_MISSING")
        operation_id = record.get("operation_id")
        if not isinstance(operation_id, str) or not operation_id:
            evidence_blockers.append("PASS170_I173_OPERATION_ID_INVALID")
            continue
        operation_ids.append(operation_id)
        expected_record = expected.get(operation_id)
        if expected_record is None:
            evidence_blockers.append("PASS170_I173_OPERATION_ID_NOT_IN_PARENT_REGISTRY")
            continue

        ws = record.get("WebSocket_channel")
        if isinstance(ws, str) and ws:
            signature = ("WEBSOCKET", ws)
        else:
            method = record.get("HTTP_method")
            path = record.get("HTTP_path")
            if not isinstance(method, str) or not isinstance(path, str):
                evidence_blockers.append("PASS170_I173_OPERATION_ROUTE_INVALID")
                continue
            signature = (method.upper(), path)
        signatures.append(signature)
        if signature != (expected_record["method"], expected_record["path"]):
            evidence_blockers.append("PASS170_I173_OPERATION_ROUTE_PARENT_MISMATCH")

        binding = record.get("source_binding")
        if not isinstance(binding, dict):
            evidence_blockers.append("PASS170_I173_SOURCE_BINDING_INVALID")
            continue
        module = binding.get("module")
        factory = binding.get("factory")
        handler = binding.get("handler")
        if module != expected_record["module"] or not isinstance(factory, str) or not isinstance(handler, str):
            evidence_blockers.append("PASS170_I173_SOURCE_BINDING_PARENT_MISMATCH")
            continue
        if module not in source_cache:
            try:
                source_cache[module] = _route_handlers(_module_path(root, module))
            except Pass170I173VerificationError as exc:
                source_cache[module] = {}
                evidence_blockers.append(str(exc))
        observed_handler = source_cache[module].get(signature)
        if observed_handler != handler:
            evidence_blockers.append("PASS170_I173_EXECUTABLE_HANDLER_MISMATCH")
        else:
            source_bound_count += 1
        try:
            source_text = _module_path(root, module).read_text(encoding="utf-8")
        except OSError:
            source_text = ""
        if f"def {factory}(" not in source_text:
            evidence_blockers.append("PASS170_I173_FACTORY_SOURCE_BINDING_MISSING")
        if record.get("implementation_status") != "EXECUTABLE_SOURCE_BOUND":
            evidence_blockers.append("PASS170_I173_IMPLEMENTATION_STATUS_INVALID")
        if str(record.get("transport_parity_status", "")).startswith("PENDING_"):
            transport_pending_count += 1
        if str(record.get("receipt_replay_status", "")).startswith("PENDING_"):
            receipt_pending_count += 1

    if len(operation_ids) != len(set(operation_ids)):
        evidence_blockers.append("PASS170_I173_OPERATION_ID_DUPLICATE")
    if len(signatures) != len(set(signatures)):
        evidence_blockers.append("PASS170_I173_ROUTE_SIGNATURE_DUPLICATE")
    if set(operation_ids) != set(expected):
        evidence_blockers.append("PASS170_I173_OPERATION_ID_PARITY_MISMATCH")
    if source_bound_count != 47:
        evidence_blockers.append("PASS170_I173_EXECUTABLE_SOURCE_BOUND_COUNT_MISMATCH")

    invariants = index.get("invariants", {}) if isinstance(index, dict) else {}
    for key in (
        "one_record_per_registered_route", "record_operation_identity_unique",
        "route_signature_unique", "executable_source_binding_required",
        "documentation_only_records_forbidden",
    ):
        if invariants.get(key) is not True:
            evidence_blockers.append(f"PASS170_I173_REQUIRED_INVARIANT_FALSE:{key}")
    for key in (
        "new_vm81_authority", "new_hash72_mint_authority",
        "hash216_persistence_authority", "floating_point_canonical_authority",
        "canonical_state_mutated_by_index_load",
    ):
        if invariants.get(key) is not False:
            evidence_blockers.append(f"PASS170_I173_FORBIDDEN_AUTHORITY_FLAG:{key}")

    evidence_blockers = sorted(set(evidence_blockers))
    evidence_verified = not evidence_blockers

    inherited_targets = set(inherited_i172.get("target_blockers", []))
    inherited_targets.discard("PASS170_FULL_OPERATION_RECORDS_PENDING")
    target_blockers = set(inherited_targets)
    if transport_pending_count:
        target_blockers.add("PASS170_PUBLIC_CLI_NATIVE_LANGUAGE_PARITY_PENDING")
    if receipt_pending_count:
        target_blockers.add("PASS170_PUBLIC_E2E_RECEIPT_REPLAY_PENDING")
    target_blockers = sorted(target_blockers)

    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "repository_root": str(root),
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I173_EVIDENCE_FAILED",
        "inherited_i172_verified": inherited_i172.get("evidence_verified") is True,
        "frozen_i171_route_identity_registry_retained": parent.get("iteration") == "PASS219-I171",
        "operation_record_index_verified": evidence_verified,
        "shard_count": len(shard_reports),
        "shards": shard_reports,
        "expected_route_count": len(expected),
        "operation_record_count": len(records),
        "unique_operation_id_count": len(set(operation_ids)),
        "unique_route_signature_count": len(set(signatures)),
        "executable_source_bound_count": source_bound_count,
        "transport_parity_pending_count": transport_pending_count,
        "receipt_replay_pending_count": receipt_pending_count,
        "full_operation_records_verified": evidence_verified and len(records) == 47 and source_bound_count == 47,
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
        raise Pass170I173VerificationError(
            "PASS170_I173_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


__all__ = [
    "BASE_MAIN", "CLASSIFICATION", "CONTRACT_ID", "EXPECTED_TARGET_BLOCKERS",
    "ITERATION", "NEXT_BOUNDARY", "RECORD_INDEX", "SCHEMA",
    "Pass170I173VerificationError", "verify_i173_full_operation_records",
]

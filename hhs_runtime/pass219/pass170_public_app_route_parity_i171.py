"""Pass219 I171 / Pass170 production-app identity and delegated-route parity gate.

This verifier is read-only.  It proves that the Pass170 gateway is composed onto
the inherited production FastAPI object, that the normal RuntimeOS dispatcher
exports that exact object, and that every Pass168/Pass169 delegated HTTP route
matches the machine-readable public operation registry exactly.

I171 is deliberately nonterminal.  Raw legacy FastAPI constructors, the full
ordered router manifest, and complete Pass170 operation records remain explicit
repair boundaries rather than being hidden or reclassified.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)
from hhs_runtime.pass219.pass170_public_registry_i170 import verify_public_registries

SCHEMA = "HHS_PASS219_I171_PASS170_PUBLIC_APP_ROUTE_PARITY_V1"
CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I171"
BASE_MAIN = "44b9852cd86e6a7584f81f1b214d5faa469880e7"
OPERATION_REGISTRY = "HHS_PUBLIC_OPERATION_REGISTRY.json"
PUBLIC_GATEWAY = "hhs_backend/public_api_server.py"
PRODUCTION_DISPATCHER = "hhs_backend/runtime_os_application_server.py"
CANONICAL_GATEWAY_ENTRYPOINT = "hhs_backend.public_api_server:app"
PRODUCTION_BASE_ENTRYPOINT = "hhs_backend.server:app"
PRODUCTION_DISPATCH_ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"
CLASSIFICATION = "PASS170_PRODUCTION_APPLICATION_IDENTITY_AND_DELEGATE_ROUTE_PARITY_VERIFIED_NONTERMINAL"
NEXT_BOUNDARY = "PASS170_LEGACY_FASTAPI_CONSTRUCTOR_RETIREMENT_AND_FULL_ROUTER_MANIFEST"
EXPECTED_TARGET_BLOCKERS = (
    "PASS170_FULL_OPERATION_RECORDS_PENDING",
    "PASS170_FULL_ROUTER_MANIFEST_PENDING",
    "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN",
)
_ROUTE_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace", "websocket"}


class Pass170I171VerificationError(RuntimeError):
    """Raised when I171 evidence fails closed."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170I171VerificationError(
            f"PASS170_I171_JSON_UNREADABLE:{path}:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise Pass170I171VerificationError(f"PASS170_I171_JSON_ROOT_INVALID:{path}")
    return payload


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _constant_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _route_signatures(path: Path) -> set[tuple[str, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise Pass170I171VerificationError(
            f"PASS170_I171_ROUTE_SOURCE_PARSE_FAILED:{path}:{type(exc).__name__}"
        ) from exc
    routes: set[tuple[str, str]] = set()
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
            if route is not None:
                routes.add((method.upper(), route))
    return routes


def _module_path(root: Path, module: str) -> Path:
    return root / (module.replace(".", "/") + ".py")


def _production_identity_evidence(root: Path) -> tuple[bool, list[str], dict[str, Any]]:
    blockers: list[str] = []
    gateway_path = root / PUBLIC_GATEWAY
    dispatcher_path = root / PRODUCTION_DISPATCHER
    try:
        gateway = gateway_path.read_text(encoding="utf-8")
        dispatcher = dispatcher_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, ["PASS170_I171_PRODUCTION_IDENTITY_SOURCE_UNREADABLE"], {
            "error": f"{type(exc).__name__}:{exc}"
        }

    gateway_checks = {
        "imports_production_base": "from hhs_backend import server as production_base" in gateway,
        "normal_factory_uses_production_base_app": "target = production_base.app" in gateway,
        "isolated_factory_is_explicit": "isolated_ephemeral = bool(config.get(\"isolated_ephemeral\", False))" in gateway,
        "compatibility_factory_requests_ephemeral": "configuration={\"isolated_ephemeral\": True}" in gateway,
        "module_app_uses_public_factory": "app = create_public_api_app()" in gateway,
        "router_builder_present": "def build_pass170_router(" in gateway,
        "compose_once_guard_present": "hhs_pass170_routes_composed" in gateway,
    }
    if not all(gateway_checks.values()):
        blockers.append("PASS170_I171_PUBLIC_GATEWAY_PRODUCTION_IDENTITY_INVALID")

    gateway_import = "from hhs_backend import public_api_server as _pass170_public_gateway"
    full_import = "from hhs_backend.runtime_os_application_server_full import *"
    identity_assertion = "if app is not _pass170_public_gateway.app:"
    dispatcher_checks = {
        "imports_pass170_gateway": gateway_import in dispatcher,
        "imports_full_composition": full_import in dispatcher,
        "pass170_import_precedes_full_composition": (
            gateway_import in dispatcher
            and full_import in dispatcher
            and dispatcher.index(gateway_import) < dispatcher.index(full_import)
        ),
        "identity_assertion_present": identity_assertion in dispatcher,
        "identity_verification_flag_present": "PASS170_PUBLIC_GATEWAY_IDENTITY_VERIFIED = True" in dispatcher,
    }
    if not all(dispatcher_checks.values()):
        blockers.append("PASS170_I171_PRODUCTION_DISPATCH_IDENTITY_INVALID")

    return not blockers, blockers, {
        "gateway_checks": gateway_checks,
        "dispatcher_checks": dispatcher_checks,
        "canonical_gateway_entrypoint": CANONICAL_GATEWAY_ENTRYPOINT,
        "production_base_entrypoint": PRODUCTION_BASE_ENTRYPOINT,
        "production_dispatch_entrypoint": PRODUCTION_DISPATCH_ENTRYPOINT,
    }


def verify_i171_public_app_route_parity(
    repository_root: str | Path = ".",
    *,
    fail_closed: bool = True,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    evidence_blockers: list[str] = []

    try:
        inherited_registry = verify_public_registries(root)
    except Exception as exc:
        inherited_registry = {
            "registry_evidence_verified": False,
            "blockers": [f"{type(exc).__name__}:{exc}"],
        }
        evidence_blockers.append("PASS170_I171_INHERITED_I170_REGISTRY_INVALID")

    try:
        operation = _load_json(root / OPERATION_REGISTRY)
    except Pass170I171VerificationError as exc:
        if fail_closed:
            raise
        operation = {}
        evidence_blockers.append(str(exc))

    if operation.get("contract") != CONTRACT_ID or operation.get("iteration") != ITERATION:
        evidence_blockers.append("PASS170_I171_OPERATION_REGISTRY_METADATA_INVALID")
    if operation.get("canonical_gateway") != CANONICAL_GATEWAY_ENTRYPOINT:
        evidence_blockers.append("PASS170_I171_CANONICAL_GATEWAY_MISMATCH")
    if operation.get("production_base_application") != PRODUCTION_BASE_ENTRYPOINT:
        evidence_blockers.append("PASS170_I171_PRODUCTION_BASE_MISMATCH")
    if operation.get("production_dispatch_entrypoint") != PRODUCTION_DISPATCH_ENTRYPOINT:
        evidence_blockers.append("PASS170_I171_PRODUCTION_DISPATCH_ENTRYPOINT_MISMATCH")

    identity_ok, identity_blockers, identity = _production_identity_evidence(root)
    evidence_blockers.extend(identity_blockers)

    delegates = operation.get("router_delegates")
    if not isinstance(delegates, list) or not delegates:
        delegates = []
        evidence_blockers.append("PASS170_I171_ROUTER_DELEGATES_EMPTY")

    delegate_reports: list[dict[str, Any]] = []
    aggregate_route_signatures: list[tuple[str, str]] = []
    route_operation_ids: list[str] = []
    for delegate in delegates:
        if not isinstance(delegate, dict):
            evidence_blockers.append("PASS170_I171_ROUTER_DELEGATE_INVALID")
            continue
        module = delegate.get("module")
        prefix = delegate.get("route_prefix")
        expected_count = delegate.get("route_count")
        records = delegate.get("routes")
        if not isinstance(module, str) or not isinstance(prefix, str) or not isinstance(records, list):
            evidence_blockers.append("PASS170_I171_ROUTER_DELEGATE_RECORD_INVALID")
            continue

        registered: list[tuple[str, str]] = []
        local_ids: list[str] = []
        for record in records:
            if not isinstance(record, dict):
                evidence_blockers.append("PASS170_I171_DELEGATE_ROUTE_RECORD_INVALID")
                continue
            method = record.get("method")
            path = record.get("path")
            operation_id = record.get("route_operation_id")
            if not all(isinstance(value, str) and value for value in (method, path, operation_id)):
                evidence_blockers.append("PASS170_I171_DELEGATE_ROUTE_RECORD_INVALID")
                continue
            signature = (method.upper(), path)
            registered.append(signature)
            aggregate_route_signatures.append(signature)
            local_ids.append(operation_id)
            route_operation_ids.append(operation_id)
            if not path.startswith(prefix):
                evidence_blockers.append("PASS170_I171_DELEGATE_ROUTE_PREFIX_MISMATCH")

        try:
            observed = _route_signatures(_module_path(root, module))
        except Pass170I171VerificationError as exc:
            observed = set()
            evidence_blockers.append(str(exc))
        registered_set = set(registered)
        parity = observed == registered_set
        if not parity:
            evidence_blockers.append("PASS170_I171_DELEGATE_ROUTE_PARITY_MISMATCH")
        if expected_count != len(records) or expected_count != len(observed):
            evidence_blockers.append("PASS170_I171_DELEGATE_ROUTE_COUNT_MISMATCH")
        if len(registered) != len(registered_set):
            evidence_blockers.append("PASS170_I171_DELEGATE_ROUTE_SIGNATURE_DUPLICATE")
        if len(local_ids) != len(set(local_ids)):
            evidence_blockers.append("PASS170_I171_DELEGATE_OPERATION_ID_DUPLICATE")
        if delegate.get("route_parity_status") != "VERIFIED_PASS219_I171":
            evidence_blockers.append("PASS170_I171_DELEGATE_PARITY_STATUS_INVALID")
        if delegate.get("registry_record_status") != "ROUTE_IDENTITY_ONLY_PENDING_FULL_PASS170_OPERATION_RECORDS":
            evidence_blockers.append("PASS170_I171_DELEGATE_RECORD_STATUS_INVALID")

        delegate_reports.append({
            "operation_id": delegate.get("operation_id"),
            "module": module,
            "route_prefix": prefix,
            "registered_route_count": len(registered_set),
            "observed_route_count": len(observed),
            "route_operation_id_count": len(set(local_ids)),
            "parity_verified": parity,
            "registered_routes": sorted([list(item) for item in registered_set]),
            "observed_routes": sorted([list(item) for item in observed]),
        })

    direct_records = operation.get("direct_gateway_routes")
    direct_signatures: list[tuple[str, str]] = []
    direct_operation_ids: list[str] = []
    if isinstance(direct_records, list):
        for record in direct_records:
            if not isinstance(record, dict):
                continue
            method = record.get("method")
            path = record.get("path")
            operation_id = record.get("operation_id")
            if isinstance(method, str) and isinstance(path, str):
                direct_signatures.append((method.upper(), path))
            if isinstance(operation_id, str):
                direct_operation_ids.append(operation_id)
    else:
        evidence_blockers.append("PASS170_I171_DIRECT_ROUTE_REGISTRY_INVALID")

    all_signatures = direct_signatures + aggregate_route_signatures
    if len(all_signatures) != len(set(all_signatures)):
        evidence_blockers.append("PASS170_I171_PUBLIC_ROUTE_SIGNATURE_DUPLICATE")
    if len(route_operation_ids) != len(set(route_operation_ids)):
        evidence_blockers.append("PASS170_I171_ROUTE_OPERATION_ID_DUPLICATE")
    if set(direct_operation_ids) & set(route_operation_ids):
        evidence_blockers.append("PASS170_I171_DIRECT_DELEGATE_OPERATION_ID_COLLISION")

    inherited_inventory = build_i169_pass170_public_authority_inventory(root)
    raw_constructor_count = int(inherited_inventory.get("inventory", {}).get("fastapi_constructor_count", 0))
    raw_multiple_constructor_blocker = "PASS170_MULTIPLE_FASTAPI_CONSTRUCTORS_PRESENT" in inherited_inventory.get("blockers", [])
    target_blockers: list[str] = []
    if raw_constructor_count > 1 and raw_multiple_constructor_blocker:
        target_blockers.append("PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN")
    elif raw_constructor_count > 1 or raw_multiple_constructor_blocker:
        evidence_blockers.append("PASS170_I171_INHERITED_CONSTRUCTOR_INVENTORY_INCONSISTENT")

    # I171 deliberately records route identity only. Full Pass170 operation
    # records and the ordered cumulative router manifest are future proof gates.
    if any(
        isinstance(delegate, dict)
        and delegate.get("registry_record_status") == "ROUTE_IDENTITY_ONLY_PENDING_FULL_PASS170_OPERATION_RECORDS"
        for delegate in delegates
    ):
        target_blockers.append("PASS170_FULL_OPERATION_RECORDS_PENDING")
    target_blockers.append("PASS170_FULL_ROUTER_MANIFEST_PENDING")

    if raw_constructor_count <= 1:
        # If future work has already retired legacy constructors, do not retain a
        # stale target blocker. I171 evidence remains valid and the next pass can
        # skip directly to manifest/operation closure.
        target_blockers = [
            item for item in target_blockers
            if item != "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN"
        ]

    invariants = operation.get("invariants", {}) if isinstance(operation, dict) else {}
    required_true = (
        "exact_symbolic_transport",
        "production_application_identity_unified",
        "isolated_factory_is_test_ephemeral_only",
        "delegate_route_signature_uniqueness_required",
    )
    for key in required_true:
        if invariants.get(key) is not True:
            evidence_blockers.append(f"PASS170_I171_REQUIRED_INVARIANT_FALSE:{key}")
    for key in (
        "floating_point_canonical_authority",
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "canonical_state_mutated_by_registry_load",
    ):
        if invariants.get(key) is not False:
            evidence_blockers.append(f"PASS170_I171_FORBIDDEN_AUTHORITY_FLAG:{key}")

    evidence_blockers = sorted(set(evidence_blockers))
    target_blockers = sorted(set(target_blockers))
    evidence_verified = (
        not evidence_blockers
        and inherited_registry.get("registry_evidence_verified") is True
        and identity_ok
    )

    report = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "iteration": ITERATION,
        "base_main": BASE_MAIN,
        "repository_root": str(root),
        "classification": CLASSIFICATION if evidence_verified else "PASS170_I171_EVIDENCE_FAILED",
        "inherited_i170_registry_verified": inherited_registry.get("registry_evidence_verified") is True,
        "production_application_identity_verified": identity_ok,
        "production_identity": identity,
        "delegate_count": len(delegate_reports),
        "delegate_route_count": sum(item["observed_route_count"] for item in delegate_reports),
        "delegate_route_operation_id_count": len(set(route_operation_ids)),
        "delegate_reports": delegate_reports,
        "direct_gateway_route_count": len(set(direct_signatures)),
        "combined_registered_route_count": len(set(all_signatures)),
        "raw_fastapi_constructor_count": raw_constructor_count,
        "raw_fastapi_constructors": inherited_inventory.get("inventory", {}).get("fastapi_constructors", []),
        "inherited_i169_blockers": inherited_inventory.get("blockers", []),
        "evidence_blockers": evidence_blockers,
        "target_blockers": target_blockers,
        "i171_evidence_verified": evidence_verified,
        "canonical_state_mutated": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "pass170_terminal_contract_verified": False,
        "next_boundary": NEXT_BOUNDARY,
    }
    if evidence_blockers and fail_closed:
        raise Pass170I171VerificationError(
            "PASS170_I171_VERIFICATION_FAILED:" + "|".join(evidence_blockers)
        )
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_root", nargs="?", default=".")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = verify_i171_public_app_route_parity(args.repository_root)
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BASE_MAIN",
    "CLASSIFICATION",
    "CONTRACT_ID",
    "EXPECTED_TARGET_BLOCKERS",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170I171VerificationError",
    "verify_i171_public_app_route_parity",
]

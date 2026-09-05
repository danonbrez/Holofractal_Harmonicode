"""Pass 219 I170 / Pass170 canonical public-registry verification.

The verifier is read-only.  It proves that the canonical public gateway is
bound to machine-readable operation and network registries while preserving
the inherited Pass190/VM81/Hash72/Hash216 authority boundary.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

CONTRACT_ID = "HHS-P170-PAPAE-HLFDCR"
ITERATION = "PASS219-I170"
OPERATION_REGISTRY = "HHS_PUBLIC_OPERATION_REGISTRY.json"
NETWORK_REGISTRY = "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json"
CANONICAL_GATEWAY_FILE = "hhs_backend/public_api_server.py"
CANONICAL_GATEWAY_ENTRYPOINT = "hhs_backend.public_api_server:app"
CANONICAL_FACTORY = "hhs_backend.public_api_server:create_public_api_app"
NEXT_BOUNDARY = "PASS170_FASTAPI_CONSTRUCTOR_CONSOLIDATION_AND_ROUTE_PARITY"
_ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "websocket"}


class Pass170PublicRegistryError(RuntimeError):
    """Raised when the Pass170 public registries fail closed."""


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Pass170PublicRegistryError(f"PASS170_REGISTRY_UNREADABLE:{path}:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise Pass170PublicRegistryError(f"PASS170_REGISTRY_ROOT_INVALID:{path}")
    return value


def _direct_route_signatures(path: Path) -> set[tuple[str, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        raise Pass170PublicRegistryError(f"PASS170_GATEWAY_PARSE_FAILED:{path}:{type(exc).__name__}") from exc
    result: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.lower()
            if method not in _ROUTE_METHODS or not decorator.args:
                continue
            arg = decorator.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                result.add((method.upper(), arg.value))
    return result


def _module_path(root: Path, module: str) -> Path:
    return root / (module.replace(".", "/") + ".py")


def _module_defines(path: Path, function_name: str) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return False
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
        for node in tree.body
    )


def verify_public_registries(root: Path | None = None, *, fail_closed: bool = True) -> dict[str, Any]:
    root = Path(root or repository_root()).resolve()
    blockers: list[str] = []

    try:
        operation = _load_json(root / OPERATION_REGISTRY)
        network = _load_json(root / NETWORK_REGISTRY)
    except Pass170PublicRegistryError as exc:
        if fail_closed:
            raise
        return {
            "schema": "HHS_PASS219_I170_PUBLIC_REGISTRY_VERIFICATION_V1",
            "iteration": ITERATION,
            "contract": CONTRACT_ID,
            "registry_evidence_verified": False,
            "blockers": [str(exc)],
            "pass170_terminal_contract_verified": False,
            "next_boundary": NEXT_BOUNDARY,
        }

    if operation.get("schema") != "HHS_PUBLIC_OPERATION_REGISTRY_V1":
        blockers.append("PASS170_PUBLIC_OPERATION_REGISTRY_SCHEMA_INVALID")
    if operation.get("contract") != CONTRACT_ID:
        blockers.append("PASS170_PUBLIC_OPERATION_REGISTRY_CONTRACT_MISMATCH")
    if operation.get("canonical_gateway") != CANONICAL_GATEWAY_ENTRYPOINT:
        blockers.append("PASS170_PUBLIC_OPERATION_GATEWAY_MISMATCH")
    if operation.get("canonical_factory") != CANONICAL_FACTORY:
        blockers.append("PASS170_PUBLIC_OPERATION_FACTORY_MISMATCH")

    if network.get("schema") != "HHS_PUBLIC_NETWORK_PORT_REGISTRY_V1":
        blockers.append("PASS170_PUBLIC_NETWORK_REGISTRY_SCHEMA_INVALID")
    if network.get("contract") != CONTRACT_ID:
        blockers.append("PASS170_PUBLIC_NETWORK_REGISTRY_CONTRACT_MISMATCH")
    if network.get("canonical_gateway") != CANONICAL_GATEWAY_ENTRYPOINT:
        blockers.append("PASS170_PUBLIC_NETWORK_GATEWAY_MISMATCH")

    direct_records = operation.get("direct_gateway_routes")
    if not isinstance(direct_records, list) or not direct_records:
        blockers.append("PASS170_DIRECT_GATEWAY_ROUTE_REGISTRY_EMPTY")
        direct_records = []
    expected_routes: list[tuple[str, str]] = []
    public_ids: list[str] = []
    for record in direct_records:
        if not isinstance(record, dict):
            blockers.append("PASS170_DIRECT_GATEWAY_ROUTE_RECORD_INVALID")
            continue
        method = record.get("method")
        path = record.get("path")
        operation_id = record.get("operation_id")
        if not all(isinstance(value, str) and value for value in (method, path, operation_id)):
            blockers.append("PASS170_DIRECT_GATEWAY_ROUTE_RECORD_INVALID")
            continue
        expected_routes.append((method.upper(), path))
        public_ids.append(operation_id)
    if len(expected_routes) != len(set(expected_routes)):
        blockers.append("PASS170_DIRECT_GATEWAY_ROUTE_SIGNATURE_DUPLICATE")

    delegates = operation.get("router_delegates")
    if not isinstance(delegates, list) or not delegates:
        blockers.append("PASS170_ROUTER_DELEGATES_EMPTY")
        delegates = []
    for delegate in delegates:
        if not isinstance(delegate, dict):
            blockers.append("PASS170_ROUTER_DELEGATE_INVALID")
            continue
        operation_id = delegate.get("operation_id")
        module = delegate.get("module")
        factory = delegate.get("factory")
        if isinstance(operation_id, str):
            public_ids.append(operation_id)
        if not isinstance(module, str) or not isinstance(factory, str) or not _module_defines(_module_path(root, module), factory):
            blockers.append("PASS170_ROUTER_DELEGATE_UNRESOLVED")
    if len(public_ids) != len(set(public_ids)):
        blockers.append("PASS170_PUBLIC_OPERATION_ID_DUPLICATE")

    try:
        observed_routes = _direct_route_signatures(root / CANONICAL_GATEWAY_FILE)
    except Pass170PublicRegistryError as exc:
        blockers.append(str(exc))
        observed_routes = set()
    expected_route_set = set(expected_routes)
    if observed_routes != expected_route_set:
        blockers.append("PASS170_DIRECT_GATEWAY_ROUTE_PARITY_MISMATCH")

    source = operation.get("dispatch_source_registry")
    source_payload: dict[str, Any] = {}
    source_path = ""
    if not isinstance(source, dict):
        blockers.append("PASS170_DISPATCH_SOURCE_REGISTRY_INVALID")
    else:
        source_path = str(source.get("path", ""))
        try:
            source_payload = _load_json(root / source_path)
        except Pass170PublicRegistryError:
            blockers.append("PASS170_DISPATCH_SOURCE_REGISTRY_UNREADABLE")
        if source_payload:
            if source_payload.get("schema") != source.get("schema") or source_payload.get("schema") != "HHS_OPERATION_REGISTRY_V1":
                blockers.append("PASS170_DISPATCH_SOURCE_REGISTRY_SCHEMA_MISMATCH")
            registry_hash216 = source_payload.get("registry_hash216")
            expected_length = source.get("registry_hash216_required_length")
            if not isinstance(registry_hash216, str) or len(registry_hash216) != expected_length:
                blockers.append("PASS170_DISPATCH_SOURCE_HASH216_INVALID")
            source_operations = source_payload.get("operations")
            if not isinstance(source_operations, list) or not source_operations:
                blockers.append("PASS170_DISPATCH_SOURCE_OPERATIONS_EMPTY")
            else:
                source_ids = [item.get("operation_id") for item in source_operations if isinstance(item, dict)]
                if len(source_ids) != len(source_operations) or any(not isinstance(item, str) or not item for item in source_ids):
                    blockers.append("PASS170_DISPATCH_SOURCE_OPERATION_ID_INVALID")
                elif len(source_ids) != len(set(source_ids)):
                    blockers.append("PASS170_DISPATCH_SOURCE_OPERATION_ID_DUPLICATE")

    ports = network.get("ports")
    if not isinstance(ports, list):
        blockers.append("PASS170_NETWORK_PORTS_INVALID")
        ports = []
    public_ports = [item for item in ports if isinstance(item, dict) and item.get("public_or_private") == "PUBLIC_GOVERNED_GATEWAY"]
    if len(public_ports) != 1:
        blockers.append("PASS170_PUBLIC_GATEWAY_PORT_CARDINALITY_INVALID")
    else:
        port = public_ports[0]
        transports = set(port.get("transport", [])) if isinstance(port.get("transport"), list) else set()
        if not {"HTTP_REST", "WEBSOCKET"}.issubset(transports):
            blockers.append("PASS170_PUBLIC_GATEWAY_TRANSPORT_INVALID")
        if port.get("application_entrypoint") != CANONICAL_GATEWAY_ENTRYPOINT:
            blockers.append("PASS170_PUBLIC_GATEWAY_ENTRYPOINT_INVALID")
        if port.get("health_endpoint") != "/v1/system/status":
            blockers.append("PASS170_PUBLIC_GATEWAY_HEALTH_ENDPOINT_INVALID")
        default_port = port.get("default_port")
        if not isinstance(default_port, int) or isinstance(default_port, bool) or not 1 <= default_port <= 65535:
            blockers.append("PASS170_PUBLIC_GATEWAY_DEFAULT_PORT_INVALID")
        override = port.get("environment_override")
        if override != {"host": "HHS_PUBLIC_API_HOST", "port": "HHS_PUBLIC_API_PORT"}:
            blockers.append("PASS170_PUBLIC_GATEWAY_ENVIRONMENT_OVERRIDE_INVALID")

    operation_invariants = operation.get("invariants", {})
    for key in (
        "floating_point_canonical_authority",
        "new_vm81_authority",
        "new_hash72_mint_authority",
        "hash216_persistence_authority",
        "canonical_state_mutated_by_registry_load",
    ):
        if operation_invariants.get(key) is not False:
            blockers.append(f"PASS170_FORBIDDEN_AUTHORITY_FLAG:{key}")
    if network.get("invariants", {}).get("canonical_state_mutated_by_registry_load") is not False:
        blockers.append("PASS170_NETWORK_REGISTRY_MUTATION_FLAG_INVALID")

    blockers = sorted(set(blockers))
    report = {
        "schema": "HHS_PASS219_I170_PUBLIC_REGISTRY_VERIFICATION_V1",
        "iteration": ITERATION,
        "contract": CONTRACT_ID,
        "repository_root": str(root),
        "canonical_gateway": CANONICAL_GATEWAY_ENTRYPOINT,
        "canonical_factory": CANONICAL_FACTORY,
        "direct_gateway_route_count": len(observed_routes),
        "registered_direct_gateway_route_count": len(expected_route_set),
        "router_delegate_count": len(delegates),
        "dispatch_source_registry": source_path,
        "dispatch_source_operation_count": len(source_payload.get("operations", [])) if isinstance(source_payload.get("operations"), list) else 0,
        "dispatch_source_registry_hash216": source_payload.get("registry_hash216", ""),
        "public_gateway_port_count": len(public_ports),
        "registry_evidence_verified": not blockers,
        "canonical_state_mutated": False,
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "pass170_terminal_contract_verified": False,
        "blockers": blockers,
        "next_boundary": NEXT_BOUNDARY,
    }
    if blockers and fail_closed:
        raise Pass170PublicRegistryError("PASS170_PUBLIC_REGISTRY_VERIFICATION_FAILED:" + "|".join(blockers))
    return report


__all__ = [
    "CONTRACT_ID",
    "ITERATION",
    "NEXT_BOUNDARY",
    "Pass170PublicRegistryError",
    "repository_root",
    "verify_public_registries",
]

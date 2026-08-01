#!/usr/bin/env python3
"""Pass 190 canonical operation and hydration fabric foundation.

This module intentionally uses only the Python standard library. It provides a
single authority context, a machine-readable operation registry, safe
HARMONICODE constructor parsing, Bash-like shell lowering, Python-identity
compatibility, deterministic Hash72/Hash216 receipts, capability-gated
mutation, OpenAPI projection, and replay.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import shlex
import sys
import threading
from dataclasses import dataclass
from math import gcd
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

CONTRACT_ID = "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_190_EXECUTABLE_OPERATION_FABRIC_FOUNDATION_VERIFIED"
REGISTRY_SCHEMA = "HHS_OPERATION_REGISTRY_V1"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "registry" / "HHS_OPERATION_REGISTRY_V1.json"


class HHSOperationError(Exception):
    """Base typed operation error."""


class RegistryValidationError(HHSOperationError):
    pass


class UnknownOperationError(HHSOperationError):
    pass


class ArgumentValidationError(HHSOperationError):
    pass


class CapabilityDeniedError(HHSOperationError):
    pass


class StateConflictError(HHSOperationError):
    pass


class ReplayMismatchError(HHSOperationError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash72(domain: str, payload: Any) -> str:
    encoded = canonical_json({"domain": domain, "payload": payload}).encode("utf-8")
    first = hashlib.sha256(encoded).hexdigest()
    second = hashlib.sha256(b"HHS72\x00" + encoded).hexdigest()
    return first + second[:8]


def hash216(domain: str, payload: Any) -> str:
    return "".join(hash72(f"{domain}:{lane}", payload) for lane in ("minus", "center", "plus"))


def _type_matches(value: Any, type_name: str) -> bool:
    if type_name == "any":
        return True
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "number":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "boolean":
        return isinstance(value, bool)
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "object":
        return isinstance(value, dict)
    if type_name == "null":
        return value is None
    return False


def _validate_schema(value: Any, schema: Mapping[str, Any], path: str = "argument") -> None:
    type_name = str(schema.get("type", "any"))
    if not _type_matches(value, type_name):
        raise ArgumentValidationError(f"{path} must be {type_name}")
    if type_name == "integer":
        if "minimum" in schema and value < schema["minimum"]:
            raise ArgumentValidationError(f"{path} is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ArgumentValidationError(f"{path} is above maximum")
    if type_name == "string" and "maxLength" in schema and len(value) > schema["maxLength"]:
        raise ArgumentValidationError(f"{path} exceeds maxLength")
    if type_name == "array":
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            raise ArgumentValidationError(f"{path} exceeds maxItems")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                _validate_schema(item, item_schema, f"{path}[{index}]")
    if type_name == "object":
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        missing = required - value.keys()
        if missing:
            raise ArgumentValidationError(f"{path} missing required fields: {sorted(missing)}")
        if schema.get("additionalProperties") is False:
            extra = value.keys() - properties.keys()
            if extra:
                raise ArgumentValidationError(f"{path} has unknown fields: {sorted(extra)}")
        for name, item_schema in properties.items():
            if name in value:
                _validate_schema(value[name], item_schema, f"{path}.{name}")


@dataclass(frozen=True)
class OperationRecord:
    raw: Mapping[str, Any]

    @property
    def operation_id(self) -> str:
        return str(self.raw["operation_id"])

    @property
    def constructor(self) -> str:
        return str(self.raw["harmonicode_constructor"])

    @property
    def capability(self) -> str:
        return str(self.raw["capability_scope"])

    @property
    def effect_class(self) -> str:
        return str(self.raw["effect_class"])

    @property
    def argument_schema(self) -> Mapping[str, Any]:
        return self.raw["argument_schema"]

    @property
    def python_identities(self) -> Sequence[str]:
        return tuple(self.raw.get("Python_identities", []))

    @property
    def shell_forms(self) -> Sequence[str]:
        return tuple(self.raw.get("shell_forms", []))


class OperationRegistry:
    REQUIRED_FIELDS = {
        "operation_id", "canonical_name", "harmonicode_constructor", "constructor_version",
        "namespace", "aliases", "introduced_by_pass", "semantic_version", "operation_class",
        "effect_class", "mutation_class", "argument_schema", "result_schema", "streaming_schema",
        "error_schema", "exception_mappings", "capability_scope", "authorization_scope",
        "admission_policy", "resource_bounds", "timeout_policy", "idempotency_policy",
        "determinism_class", "replay_supported", "reverse_supported", "VM81_binding",
        "native_ABI_symbols", "HTTP_method", "HTTP_path", "WebSocket_channel", "CLI_command",
        "shell_forms", "Python_identities", "SDK_symbols", "GUI_action_ids", "hydration_adapters",
        "Hash216_identity", "receipt_class", "test_vectors", "deprecated_aliases",
        "implementation_status",
    }

    def __init__(self, registry_path: Path = DEFAULT_REGISTRY):
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
        if payload.get("schema") != REGISTRY_SCHEMA:
            raise RegistryValidationError("unexpected registry schema")
        records = [OperationRecord(record) for record in payload.get("operations", [])]
        if not records:
            raise RegistryValidationError("operation registry is empty")
        self.payload = payload
        self.records = tuple(records)
        self.by_id: dict[str, OperationRecord] = {}
        self.by_constructor: dict[str, OperationRecord] = {}
        self.by_python: dict[str, OperationRecord] = {}
        self.by_shell: dict[str, OperationRecord] = {}
        self._validate_and_index()

    def _validate_and_index(self) -> None:
        for record in self.records:
            missing = self.REQUIRED_FIELDS - record.raw.keys()
            if missing:
                raise RegistryValidationError(f"{record.operation_id} missing fields: {sorted(missing)}")
            if record.operation_id in self.by_id:
                raise RegistryValidationError(f"duplicate operation_id: {record.operation_id}")
            if record.constructor in self.by_constructor:
                raise RegistryValidationError(f"duplicate constructor: {record.constructor}")
            identity_payload = dict(record.raw)
            supplied = identity_payload.pop("Hash216_identity")
            expected = hash216("pass190.operation", identity_payload)
            if supplied != expected:
                raise RegistryValidationError(f"Hash216 mismatch for {record.operation_id}")
            self.by_id[record.operation_id] = record
            self.by_constructor[record.constructor] = record
            for identity in record.python_identities:
                if identity in self.by_python:
                    raise RegistryValidationError(f"duplicate Python identity: {identity}")
                self.by_python[identity] = record
            for shell_form in record.shell_forms:
                command = shell_form.split()[0]
                if command in self.by_shell and self.by_shell[command] != record:
                    raise RegistryValidationError(f"duplicate shell command: {command}")
                self.by_shell[command] = record

    def resolve(self, operation_id: str) -> OperationRecord:
        try:
            return self.by_id[operation_id]
        except KeyError as exc:
            raise UnknownOperationError(operation_id) from exc


@dataclass(frozen=True)
class InvocationResult:
    operation_id: str
    result: Any
    receipt: Mapping[str, Any]
    requested_surface: str
    replay_verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "result": self.result,
            "receipt": dict(self.receipt),
            "requested_surface": self.requested_surface,
            "replay_verified": self.replay_verified,
        }


class HHSAuthorityContext:
    """Exactly one injectable operation authority for the process."""

    def __init__(self, registry_path: Path = DEFAULT_REGISTRY):
        self.registry = OperationRegistry(registry_path)
        self._lock = threading.RLock()
        self._receipt_index = 0
        self._last_hash72 = "0" * 72
        self._receipts: dict[str, dict[str, Any]] = {}
        self._idempotency: dict[str, InvocationResult] = {}
        self._state: dict[str, Any] = {"counter": 0}
        self._state_root = hash72("pass190.state", self._state)
        self._implementations: dict[str, Callable[[dict[str, Any]], Any]] = {
            "system.status": self._op_status,
            "python.len": self._op_len,
            "python.abs": self._op_abs,
            "python.sorted": self._op_sorted,
            "list.with_appended": self._op_with_appended,
            "dict.get": self._op_dict_get,
            "text.join": self._op_join,
            "math.gcd": self._op_gcd,
            "pass189.context.decode": self._op_pass189_decode,
            "state.counter.advance": self._op_counter_advance,
        }
        if set(self._implementations) != set(self.registry.by_id):
            missing = set(self.registry.by_id) - set(self._implementations)
            extra = set(self._implementations) - set(self.registry.by_id)
            raise RegistryValidationError(f"registry/implementation mismatch missing={sorted(missing)} extra={sorted(extra)}")

    @property
    def state_root(self) -> str:
        return self._state_root

    def reset_for_tests(self) -> None:
        with self._lock:
            self._receipt_index = 0
            self._last_hash72 = "0" * 72
            self._receipts.clear()
            self._idempotency.clear()
            self._state = {"counter": 0}
            self._state_root = hash72("pass190.state", self._state)

    def invoke(
        self,
        operation_id: str,
        arguments: Mapping[str, Any] | None = None,
        *,
        surface: str = "canonical",
        capabilities: Iterable[str] = (),
        idempotency_key: str | None = None,
        expected_state: str | None = None,
    ) -> InvocationResult:
        args = copy.deepcopy(dict(arguments or {}))
        record = self.registry.resolve(operation_id)
        _validate_schema(args, record.argument_schema)
        capability_set = frozenset(capabilities)
        if record.capability not in {"public", "none"} and record.capability not in capability_set:
            raise CapabilityDeniedError(f"missing capability: {record.capability}")
        request_identity = hash72("pass190.request", {"operation_id": operation_id, "arguments": args})
        if idempotency_key:
            prior = self._idempotency.get(idempotency_key)
            if prior:
                if prior.receipt["request_identity"] != request_identity:
                    raise ArgumentValidationError("idempotency key reused with different request")
                return InvocationResult(prior.operation_id, copy.deepcopy(prior.result), prior.receipt, surface, prior.replay_verified)
        with self._lock:
            if record.effect_class == "mutation" and expected_state is not None and expected_state != self._state_root:
                raise StateConflictError("expected state root does not match current state")
            state_before = self._state_root
            result = self._implementations[operation_id](args)
            state_after = self._state_root
            self._receipt_index += 1
            receipt_payload = {
                "schema": "HHS_PASS_190_RECEIPT_V1",
                "contract": CONTRACT_ID,
                "receipt_index": self._receipt_index,
                "operation_id": operation_id,
                "operation_hash216": record.raw["Hash216_identity"],
                "canonical_constructor": record.constructor,
                "arguments": args,
                "result": result,
                "request_identity": request_identity,
                "effect_class": record.effect_class,
                "state_before": state_before,
                "state_after": state_after,
                "predecessor_hash72": self._last_hash72,
                "determinism_class": record.raw["determinism_class"],
                "closure": {"delta_e": 0, "psi": 0, "omega": True},
            }
            receipt_hash = hash72("pass190.receipt", receipt_payload)
            receipt = {**receipt_payload, "hash72": receipt_hash, "hash216": hash216("pass190.receipt.topology", receipt_payload)}
            self._last_hash72 = receipt_hash
            self._receipts[receipt_hash] = receipt
            invocation = InvocationResult(operation_id, copy.deepcopy(result), receipt, surface)
            if idempotency_key:
                self._idempotency[idempotency_key] = invocation
            return invocation

    def replay(self, receipt_hash72: str) -> InvocationResult:
        receipt = self._receipts.get(receipt_hash72)
        if receipt is None:
            raise ReplayMismatchError("unknown receipt")
        operation_id = receipt["operation_id"]
        args = copy.deepcopy(receipt["arguments"])
        expected = copy.deepcopy(receipt["result"])
        if operation_id == "state.counter.advance":
            delta = args["delta"]
            before = expected["before"]
            recomputed = {"before": before, "after": before + delta, "state_root": expected["state_root"]}
        else:
            recomputed = self._implementations[operation_id](args)
        if recomputed != expected:
            raise ReplayMismatchError("semantic replay mismatch")
        payload = {key: value for key, value in receipt.items() if key not in {"hash72", "hash216"}}
        if hash72("pass190.receipt", payload) != receipt["hash72"]:
            raise ReplayMismatchError("Hash72 replay mismatch")
        if hash216("pass190.receipt.topology", payload) != receipt["hash216"]:
            raise ReplayMismatchError("Hash216 replay mismatch")
        return InvocationResult(operation_id, expected, receipt, "replay", True)

    def invoke_constructor(self, expression: str, **kwargs: Any) -> InvocationResult:
        operation_id, args = parse_constructor(expression, self.registry)
        return self.invoke(operation_id, args, surface="harmonicode", **kwargs)

    def invoke_python(self, identity: str, arguments: Mapping[str, Any], **kwargs: Any) -> InvocationResult:
        try:
            record = self.registry.by_python[identity]
        except KeyError as exc:
            raise UnknownOperationError(identity) from exc
        return self.invoke(record.operation_id, arguments, surface="python", **kwargs)

    def invoke_shell(self, command_line: str, **kwargs: Any) -> InvocationResult:
        tokens = shlex.split(command_line)
        if not tokens:
            raise ArgumentValidationError("empty command")
        if tokens[0] != "hhs":
            return self.invoke_constructor(command_line, **kwargs)
        if len(tokens) < 2:
            raise ArgumentValidationError("missing hhs command")
        command = tokens[1]
        if command == "status":
            return self.invoke("system.status", {}, surface="shell", **kwargs)
        if command == "eval":
            if len(tokens) != 3:
                raise ArgumentValidationError("usage: hhs eval 'Constructor(...)'")
            operation_id, args = parse_constructor(tokens[2], self.registry)
            return self.invoke(operation_id, args, surface="shell", **kwargs)
        if command == "invoke":
            if len(tokens) != 4:
                raise ArgumentValidationError("usage: hhs invoke OPERATION_ID JSON_OBJECT")
            args = json.loads(tokens[3])
            if not isinstance(args, dict):
                raise ArgumentValidationError("invoke arguments must be a JSON object")
            return self.invoke(tokens[2], args, surface="shell", **kwargs)
        record = self.registry.by_shell.get(command)
        if record is None:
            suggestions = sorted(name for name in self.registry.by_shell if name.startswith(command[:1]))[:5]
            suffix = f"; suggestions: {suggestions}" if suggestions else ""
            raise UnknownOperationError(f"{command}{suffix}")
        if len(tokens) != 3:
            raise ArgumentValidationError(f"usage: hhs {command} JSON_OBJECT")
        args = json.loads(tokens[2])
        return self.invoke(record.operation_id, args, surface="shell", **kwargs)

    def openapi_document(self) -> dict[str, Any]:
        paths: dict[str, Any] = {}
        for record in self.registry.records:
            path = record.raw["HTTP_path"]
            method = record.raw["HTTP_method"].lower()
            paths.setdefault(path, {})[method] = {
                "operationId": record.operation_id,
                "summary": record.raw["canonical_name"],
                "x-hhs-constructor": record.constructor,
                "x-hhs-hash216": record.raw["Hash216_identity"],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": record.argument_schema}},
                },
                "responses": {
                    "200": {"description": "Admitted operation result"},
                    "400": {"description": "Typed validation or operation error"},
                    "403": {"description": "Capability denied"},
                    "409": {"description": "State conflict"},
                },
            }
        return {
            "openapi": "3.1.0",
            "info": {"title": "HHS Pass 190 Unified Operation Fabric", "version": "1.0.0"},
            "paths": paths,
            "x-hhs-contract": CONTRACT_ID,
            "x-hhs-registry-hash216": self.registry.payload["registry_hash216"],
        }

    def _op_status(self, _args: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "ok",
            "classification": CLASSIFICATION,
            "contract": CONTRACT_ID,
            "operations": len(self.registry.records),
            "state_root": self._state_root,
            "receipt_index": self._receipt_index,
        }

    @staticmethod
    def _op_len(args: dict[str, Any]) -> int:
        return len(args["value"])

    @staticmethod
    def _op_abs(args: dict[str, Any]) -> int:
        return abs(args["value"])

    @staticmethod
    def _op_sorted(args: dict[str, Any]) -> list[Any]:
        return sorted(args["values"], reverse=args.get("reverse", False))

    @staticmethod
    def _op_with_appended(args: dict[str, Any]) -> list[Any]:
        return [*args["source"], copy.deepcopy(args["value"])]

    @staticmethod
    def _op_dict_get(args: dict[str, Any]) -> Any:
        return copy.deepcopy(args["mapping"].get(args["key"], args.get("default")))

    @staticmethod
    def _op_join(args: dict[str, Any]) -> str:
        return args["separator"].join(args["values"])

    @staticmethod
    def _op_gcd(args: dict[str, Any]) -> int:
        return gcd(args["a"], args["b"])

    @staticmethod
    def _op_pass189_decode(args: dict[str, Any]) -> dict[str, int]:
        address = args["address"]
        if not 0 <= address < 51_648_192:
            raise ArgumentValidationError("address outside Pass 189 contextual fabric")
        kappa = address % 41
        projected = address // 41
        gear243 = projected % 243
        permanent = projected // 243
        cell81 = permanent // 64
        operation64 = permanent % 64
        return {
            "address": address,
            "projected": projected,
            "cell81": cell81,
            "operation64": operation64,
            "gear243": gear243,
            "kappa41": kappa,
            "local_k": kappa - 20,
        }

    def _op_counter_advance(self, args: dict[str, Any]) -> dict[str, Any]:
        before = self._state["counter"]
        after = before + args["delta"]
        self._state = {**self._state, "counter": after}
        self._state_root = hash72("pass190.state", self._state)
        return {"before": before, "after": after, "state_root": self._state_root}


_CONTEXT: HHSAuthorityContext | None = None
_CONTEXT_LOCK = threading.Lock()


def get_context() -> HHSAuthorityContext:
    global _CONTEXT
    if _CONTEXT is None:
        with _CONTEXT_LOCK:
            if _CONTEXT is None:
                _CONTEXT = HHSAuthorityContext()
    return _CONTEXT


def _literal(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (str, int, bool)) or node.value is None:
            return node.value
        raise ArgumentValidationError("unsupported literal")
    if isinstance(node, ast.List):
        return [_literal(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return [_literal(item) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {_literal(key): _literal(value) for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        value = _literal(node.operand)
        if isinstance(value, int) and not isinstance(value, bool):
            return -value
    raise ArgumentValidationError("constructor arguments must be exact literals")


def parse_constructor(expression: str, registry: OperationRegistry) -> tuple[str, dict[str, Any]]:
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ArgumentValidationError("invalid constructor syntax") from exc
    call = parsed.body
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
        raise ArgumentValidationError("expected one constructor call")
    try:
        record = registry.by_constructor[call.func.id]
    except KeyError as exc:
        raise UnknownOperationError(call.func.id) from exc
    schema = record.argument_schema
    required_order = list(schema.get("required", []))
    property_order = required_order + [name for name in schema.get("properties", {}) if name not in required_order]
    if len(call.args) > len(property_order):
        raise ArgumentValidationError("too many positional arguments")
    arguments: dict[str, Any] = {}
    for name, node in zip(property_order, call.args):
        arguments[name] = _literal(node)
    for keyword in call.keywords:
        if keyword.arg is None:
            raise ArgumentValidationError("dictionary expansion is forbidden")
        if keyword.arg in arguments:
            raise ArgumentValidationError(f"duplicate argument: {keyword.arg}")
        arguments[keyword.arg] = _literal(keyword.value)
    _validate_schema(arguments, schema)
    return record.operation_id, arguments


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hhs", description="Pass 190 HARMONICODE operation shell")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if not args.command:
        parser.error("supply a shell command or constructor")
    command_line = " ".join(args.command)
    try:
        result = get_context().invoke_shell(command_line)
    except HHSOperationError as exc:
        payload = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
        print(canonical_json(payload) if args.as_json else f"ERROR {payload['error']}: {payload['message']}", file=sys.stderr)
        return 2
    payload = result.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.as_json else canonical_json(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

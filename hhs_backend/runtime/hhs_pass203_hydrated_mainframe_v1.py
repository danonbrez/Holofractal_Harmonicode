"""Pass 203 universal hydrated-function mainframe authority.

This module extends Pass 201 route federation and the inherited Pass 190
operation fabric into one machine-readable, receipt-bearing execution surface.
It indexes registered governed operations, Python callables, and native ABI
symbols. Only registered operations, explicit adapters, and bounded exact
Python functions are executable; raw host-language eval and unrestricted
subprocess execution remain forbidden.
"""
from __future__ import annotations

import ast
import base64
import dataclasses
import hashlib
import importlib
import inspect
import json
import os
import re
import subprocess
import sys
import threading
import time
from collections import Counter
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

CONTRACT = "HHS-P203-UNIVERSAL-HYDRATED-FUNCTION-MAINFRAME-VM81-H72-H216"
CLASSIFICATION = "HHS_PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME_VERIFIED"
VERSION = "PASS_203_UNIVERSAL_HYDRATED_FUNCTION_MAINFRAME_V1"
PUBLIC_PREFIX = "/api/runtime/mainframe"

MAX_ARGUMENT_BYTES = 2 * 1024 * 1024
MAX_RESULT_BYTES = 16 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 900

_REPO_EXCLUDED_PARTS = {
    ".git", ".github", "__pycache__", ".pytest_cache", ".mypy_cache",
    "node_modules", "dist", "build", "artifacts", "evidence",
    "release_artifacts", "rejections", "tests", "test", "docs",
}
_PYTHON_ROOTS = (
    "hhs_backend",
    "hhs_runtime",
    "hhs_python",
    "python",
    "native_projects/hhs_harmonicode_interpreter",
    "native_projects/hhs_compiler_artifact_pipeline",
    "native_projects/hhs_ide_workspace",
    "native_projects/hhs_pass190_operation_fabric/python",
)
_C_HEADER_ROOTS = (
    "hhs_runtime/include",
    "native_projects",
)
_SAFE_MODULE_PREFIXES = (
    "hhs_backend.runtime.",
    "hhs_runtime.",
    "hhs_python.runtime.",
    "python.hhs_gfcc.",
    "native_projects.hhs_harmonicode_interpreter.",
    "native_projects.hhs_compiler_artifact_pipeline.",
    "native_projects.hhs_ide_workspace.",
)
_SAFE_FUNCTION_PREFIXES = (
    "build_", "compile_", "contextual_", "decode_", "encode_", "get_",
    "hash", "inspect_", "interpret_", "list_", "parse_", "plan_",
    "read_", "reciprocal_", "render_", "resolve_", "status", "validate_",
    "verify_", "live_", "interpreting_",
)
_DENIED_NAME_FRAGMENTS = (
    "delete", "drop", "erase", "exec", "eval", "fork", "kill", "open_shell",
    "remove", "rmtree", "spawn", "system", "unlink", "write_file",
)
_NATIVE_PROTOTYPE = re.compile(
    r"(?P<return>[A-Za-z_][A-Za-z0-9_\s\*]*?)\s+"
    r"(?P<name>hhs_[A-Za-z0-9_]+)\s*\((?P<params>[^;{}]*)\)\s*;",
    re.MULTILINE,
)


class MainframeError(RuntimeError):
    """Base Pass 203 mainframe error."""


class UnknownFunctionError(MainframeError):
    """Raised when a function identity is absent."""


class InvocationRejectedError(MainframeError):
    """Raised when an invocation violates its execution policy."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _json_safe(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _json_safe(dataclasses.asdict(value))
    if isinstance(value, Enum):
        return _json_safe(value.value)
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, bytes):
        return {"encoding": "base64", "data": base64.b64encode(value).decode("ascii")}
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, bool, float)):
        return value
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _json_safe(value.to_dict())
    return str(value)


def _source_module(repo_root: Path, path: Path) -> Optional[str]:
    try:
        relative = path.relative_to(repo_root).with_suffix("")
    except ValueError:
        return None
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts or any(not part.isidentifier() for part in parts):
        return None
    return ".".join(parts)


def _annotation_text(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _literal_default(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        try:
            return ast.unparse(node)
        except Exception:
            return None


def _effect_class(name: str, module_name: str) -> str:
    lowered = f"{module_name}.{name}".lower()
    if any(fragment in lowered for fragment in _DENIED_NAME_FRAGMENTS):
        return "forbidden"
    if name.startswith(("get_", "list_", "read_", "inspect_", "status", "verify_", "validate_", "hash")):
        return "pure"
    if name.startswith(("build_", "compile_", "interpret_", "parse_", "plan_", "resolve_", "render_", "encode_", "decode_", "contextual_", "reciprocal_")):
        return "bounded"
    if name.endswith("_self_test") or name.startswith(("live_", "interpreting_")):
        return "bounded"
    return "mutation"


def _family(module_name: str, function_name: str) -> str:
    value = f"{module_name}.{function_name}".lower()
    for family in (
        "interpreter", "compiler", "workspace", "artifact", "job", "scheduler",
        "graphics", "storybook", "game", "audio", "video", "document",
        "database", "vector", "hash", "vm81", "abi", "runtime",
    ):
        if family in value:
            return family
    return "general"


def _callable_policy(module_name: str, function_name: str, effect_class: str) -> Tuple[bool, str]:
    if effect_class == "forbidden":
        return False, "FORBIDDEN"
    if not module_name.startswith(_SAFE_MODULE_PREFIXES):
        return False, "ADAPTER_REQUIRED"
    if function_name.startswith("_"):
        return False, "PRIVATE"
    if not function_name.startswith(_SAFE_FUNCTION_PREFIXES) and not function_name.endswith("_self_test"):
        return False, "ADAPTER_REQUIRED"
    if effect_class == "mutation":
        return False, "WORKSPACE_JOB_ADAPTER_REQUIRED"
    return True, "ISOLATED_PYTHON"


def _function_parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Dict[str, Any]]:
    args = [*node.args.posonlyargs, *node.args.args]
    defaults: List[Optional[ast.AST]] = [None] * (len(args) - len(node.args.defaults)) + list(node.args.defaults)
    records: List[Dict[str, Any]] = []
    for argument, default in zip(args, defaults):
        records.append({
            "name": argument.arg,
            "kind": "POSITIONAL_OR_KEYWORD",
            "annotation": _annotation_text(argument.annotation),
            "required": default is None,
            "default": None if default is None else _literal_default(default),
        })
    if node.args.vararg is not None:
        records.append({
            "name": node.args.vararg.arg,
            "kind": "VAR_POSITIONAL",
            "annotation": _annotation_text(node.args.vararg.annotation),
            "required": False,
            "default": None,
        })
    for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        records.append({
            "name": argument.arg,
            "kind": "KEYWORD_ONLY",
            "annotation": _annotation_text(argument.annotation),
            "required": default is None,
            "default": None if default is None else _literal_default(default),
        })
    if node.args.kwarg is not None:
        records.append({
            "name": node.args.kwarg.arg,
            "kind": "VAR_KEYWORD",
            "annotation": _annotation_text(node.args.kwarg.annotation),
            "required": False,
            "default": None,
        })
    return records


class HydratedMainframe:
    """Unified catalog and execution authority for hydrated HHS functions."""

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[2])
        configured = os.environ.get("HHS_PASS203_STATE_ROOT")
        self.state_root = Path(configured or self.repo_root / "var" / "pass203")
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.pass190_database = self.state_root / "pass190-mainframe.sqlite3"
        self._lock = threading.RLock()
        self._catalog: Optional[List[Dict[str, Any]]] = None
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._pass190_context: Any = None
        self._authority_provider: Optional[Callable[[str], Mapping[str, Any]]] = None
        self._last_refresh_ns = 0

    def configure_authority(self, provider: Callable[[str], Mapping[str, Any]]) -> None:
        self._authority_provider = provider

    def _authority_tick(self, source: str) -> Dict[str, Any]:
        if self._authority_provider is None:
            return {"source": source, "available": False, "receipt_hash72": None, "runtime_step": None}
        value = dict(self._authority_provider(source))
        return {
            "source": source,
            "available": True,
            "receipt_hash72": (value.get("receipt") or {}).get("receipt_hash72"),
            "runtime_step": (value.get("runtime") or {}).get("step"),
        }

    def _iter_python_files(self) -> Iterable[Path]:
        seen: set[Path] = set()
        for root_name in _PYTHON_ROOTS:
            root = self.repo_root / root_name
            if not root.is_dir():
                continue
            for path in root.rglob("*.py"):
                if path in seen or any(part in _REPO_EXCLUDED_PARTS for part in path.relative_to(self.repo_root).parts):
                    continue
                seen.add(path)
                yield path

    def _scan_python(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for path in sorted(self._iter_python_files()):
            module_name = _source_module(self.repo_root, path)
            if not module_name:
                continue
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
            except (OSError, UnicodeError, SyntaxError):
                continue
            module_doc = ast.get_docstring(tree) or ""
            for node in tree.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name.startswith("_"):
                    continue
                effect = _effect_class(node.name, module_name)
                callable_now, execution_mode = _callable_policy(module_name, node.name, effect)
                identity = {
                    "kind": "PYTHON_FUNCTION",
                    "module": module_name,
                    "qualname": node.name,
                    "source": str(path.relative_to(self.repo_root)),
                }
                function_id = f"py:{_sha256(identity)}"
                record = {
                    "function_id": function_id,
                    **identity,
                    "name": node.name,
                    "family": _family(module_name, node.name),
                    "summary": (ast.get_docstring(node) or module_doc or node.name).strip().splitlines()[0][:240],
                    "parameters": _function_parameters(node),
                    "return_annotation": _annotation_text(node.returns),
                    "async": isinstance(node, ast.AsyncFunctionDef),
                    "effect_class": effect,
                    "execution_mode": execution_mode,
                    "hydrated": callable_now,
                    "callable": callable_now,
                    "requires_workspace": effect == "mutation",
                    "requires_vm81_authority": effect != "pure",
                    "invocation_path": f"{PUBLIC_PREFIX}/invoke",
                }
                record["descriptor_sha256"] = _sha256(record)
                records.append(record)
        return records

    def _iter_headers(self) -> Iterable[Path]:
        seen: set[Path] = set()
        for root_name in _C_HEADER_ROOTS:
            root = self.repo_root / root_name
            if not root.exists():
                continue
            paths = root.rglob("*.h") if root.is_dir() else [root]
            for path in paths:
                if path in seen or any(part in _REPO_EXCLUDED_PARTS for part in path.relative_to(self.repo_root).parts):
                    continue
                seen.add(path)
                yield path

    def _scan_abi(self, operations: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        operation_text = [(str(item.get("operation_id")), _canonical_json(item)) for item in operations]
        records: List[Dict[str, Any]] = []
        for path in sorted(self._iter_headers()):
            try:
                source = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            relative = str(path.relative_to(self.repo_root))
            for match in _NATIVE_PROTOTYPE.finditer(source):
                symbol = match.group("name")
                bound = next((operation_id for operation_id, raw in operation_text if symbol in raw), None)
                identity = {"kind": "NATIVE_ABI", "symbol": symbol, "header": relative}
                function_id = f"abi:{_sha256(identity)}"
                record = {
                    "function_id": function_id,
                    **identity,
                    "name": symbol,
                    "family": _family(relative, symbol),
                    "summary": f"Native ABI symbol {symbol}",
                    "return_type": " ".join(match.group("return").split()),
                    "parameters_c": " ".join(match.group("params").split()),
                    "effect_class": "native",
                    "execution_mode": "PASS190_GOVERNED" if bound else "ABI_BINDING_REQUIRED",
                    "hydrated": bool(bound),
                    "callable": bool(bound),
                    "bound_operation_id": bound,
                    "requires_workspace": True,
                    "requires_vm81_authority": True,
                    "invocation_path": f"{PUBLIC_PREFIX}/invoke",
                }
                record["descriptor_sha256"] = _sha256(record)
                records.append(record)
        return records

    def _load_pass190_registry(self) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        python_root = self.repo_root / "native_projects" / "hhs_pass190_operation_fabric" / "python"
        if not python_root.is_dir():
            return [], "Pass 190 Python root is absent"
        if str(python_root) not in sys.path:
            sys.path.insert(0, str(python_root))
        try:
            module = importlib.import_module("hhs_pass190_iteration7_registry")
            registry = module.Iteration7OperationRegistry()
        except Exception as exc:
            return [], f"{exc.__class__.__name__}: {exc}"
        records: List[Dict[str, Any]] = []
        for operation in registry.records:
            raw = _json_safe(operation.raw)
            operation_id = str(raw.get("operation_id"))
            record = {
                "function_id": f"op:{operation_id}",
                "kind": "GOVERNED_OPERATION",
                "operation_id": operation_id,
                "name": operation_id,
                "family": str(raw.get("operation_class") or _family(operation_id, operation_id)),
                "summary": str(raw.get("summary") or raw.get("description") or operation_id),
                "parameters_schema": raw.get("input_schema") or raw.get("arguments_schema") or {},
                "result_schema": raw.get("output_schema") or {},
                "effect_class": str(raw.get("effect_class") or "unknown"),
                "capability_scope": raw.get("capability_scope"),
                "execution_mode": "PASS190_GOVERNED",
                "hydrated": True,
                "callable": True,
                "requires_workspace": operation_id.startswith(("workspace.", "artifact.", "job.")),
                "requires_vm81_authority": True,
                "raw_operation": raw,
                "invocation_path": f"{PUBLIC_PREFIX}/operations/invoke",
            }
            record["descriptor_sha256"] = _sha256(record)
            records.append(record)
        return records, None

    @staticmethod
    def _adapter_records() -> List[Dict[str, Any]]:
        adapters = (
            (
                "adapter:interpreter.exact", "interpreter.exact", "interpreter",
                "Interpret exact integer/rational Harmonicode expressions with witnessed rejection.",
                {"type": "object", "additionalProperties": False, "properties": {
                    "project_id": {"type": "string"}, "source_object_id": {"type": "string"},
                    "expression": {"type": "string", "minLength": 1, "maxLength": 16384},
                    "input_state_ids": {"type": "array", "items": {"type": "string"}},
                }, "required": ["expression"]},
            ),
            (
                "adapter:compiler.hhs_ir", "compiler.hhs_ir", "compiler",
                "Compile HHS source into a proof-carrying compiler artifact without automatic execution admission.",
                {"type": "object", "additionalProperties": False, "properties": {
                    "project_id": {"type": "string"}, "source_object_id": {"type": "string"},
                    "source_text": {"type": "string", "minLength": 1, "maxLength": 1048576},
                    "target": {"type": "string"},
                }, "required": ["source_text"]},
            ),
            (
                "adapter:interpreter.self_test", "interpreter.self_test", "interpreter",
                "Run the bounded live interpreter positive and host-eval rejection test.",
                {"type": "object", "additionalProperties": False, "properties": {}},
            ),
            (
                "adapter:compiler.self_test", "compiler.self_test", "compiler",
                "Run the interpreting compiler artifact and unsupported-target rejection test.",
                {"type": "object", "additionalProperties": False, "properties": {}},
            ),
            (
                "adapter:mainframe.refresh", "mainframe.refresh", "runtime",
                "Refresh the complete hydrated function, operation, and ABI catalog.",
                {"type": "object", "additionalProperties": False, "properties": {}},
            ),
        )
        records: List[Dict[str, Any]] = []
        for function_id, name, family, summary, schema in adapters:
            record = {
                "function_id": function_id,
                "kind": "MAINFRAME_ADAPTER",
                "name": name,
                "family": family,
                "summary": summary,
                "parameters_schema": schema,
                "result_schema": {"type": "object"},
                "effect_class": "bounded",
                "execution_mode": "GOVERNED_ADAPTER",
                "hydrated": True,
                "callable": True,
                "requires_workspace": name.startswith(("interpreter.", "compiler.")),
                "requires_vm81_authority": True,
                "invocation_path": f"{PUBLIC_PREFIX}/invoke",
            }
            record["descriptor_sha256"] = _sha256(record)
            records.append(record)
        return records

    def refresh(self) -> Dict[str, Any]:
        with self._lock:
            operations, operation_error = self._load_pass190_registry()
            python_records = self._scan_python()
            abi_records = self._scan_abi(operations)
            records = [*self._adapter_records(), *operations, *python_records, *abi_records]
            records.sort(key=lambda item: (str(item.get("family")), str(item.get("kind")), str(item.get("name"))))
            by_id: Dict[str, Dict[str, Any]] = {}
            duplicates: List[str] = []
            for record in records:
                function_id = str(record["function_id"])
                if function_id in by_id:
                    duplicates.append(function_id)
                by_id[function_id] = record
            self._catalog = records
            self._by_id = by_id
            self._last_refresh_ns = time.time_ns()
            counts = Counter(str(item.get("kind")) for item in records)
            callable_count = sum(1 for item in records if item.get("callable"))
            hydrated_count = sum(1 for item in records if item.get("hydrated"))
            report = {
                "schema": "HHS_PASS_203_MAINFRAME_REFRESH_V1",
                "contract": CONTRACT,
                "classification": CLASSIFICATION,
                "closed": not duplicates and operation_error is None,
                "catalog_count": len(records),
                "hydrated_count": hydrated_count,
                "callable_count": callable_count,
                "unbound_count": len(records) - hydrated_count,
                "kind_counts": dict(sorted(counts.items())),
                "pass190_registry_error": operation_error,
                "duplicate_function_ids": duplicates,
                "refreshed_at_ns": self._last_refresh_ns,
            }
            report["catalog_sha256"] = _sha256(records)
            report["refresh_hash72"] = hash72("HHS_PASS_203_MAINFRAME_REFRESH_V1", report)
            return report

    def catalog(self) -> List[Dict[str, Any]]:
        if self._catalog is None:
            self.refresh()
        return list(self._catalog or [])

    def status(self) -> Dict[str, Any]:
        records = self.catalog()
        counts = Counter(str(item.get("kind")) for item in records)
        modes = Counter(str(item.get("execution_mode")) for item in records)
        families = Counter(str(item.get("family")) for item in records)
        payload = {
            "schema": "HHS_PASS_203_MAINFRAME_STATUS_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "version": VERSION,
            "ok": True,
            "closed": not any(item.get("function_id") is None for item in records),
            "catalog_count": len(records),
            "hydrated_count": sum(1 for item in records if item.get("hydrated")),
            "callable_count": sum(1 for item in records if item.get("callable")),
            "unbound_internal_count": sum(1 for item in records if not item.get("hydrated")),
            "kind_counts": dict(sorted(counts.items())),
            "execution_mode_counts": dict(sorted(modes.items())),
            "family_counts": dict(sorted(families.items())),
            "last_refresh_ns": self._last_refresh_ns,
            "pass_inheritance": "PASS_203_INHERITS_ALL_PRIOR_PASSES_AS_ONE_INTEGRATED_SYSTEM",
            "arbitrary_host_eval_available": False,
            "unrestricted_subprocess_available": False,
            "native_authority_preserved": True,
            "public_function_endpoint": f"{PUBLIC_PREFIX}/functions",
            "public_invoke_endpoint": f"{PUBLIC_PREFIX}/invoke",
            "public_operation_endpoint": f"{PUBLIC_PREFIX}/operations/invoke",
            "public_replay_endpoint": f"{PUBLIC_PREFIX}/replay/{{receipt_hash72}}",
        }
        payload["catalog_sha256"] = _sha256(records)
        payload["status_hash72"] = hash72("HHS_PASS_203_MAINFRAME_STATUS_V1", payload)
        return payload

    def list_functions(self, *, query: str = "", family: str = "", kind: str = "",
                       callable_only: bool = False, hydrated_only: bool = False,
                       offset: int = 0, limit: int = 200) -> Dict[str, Any]:
        query_value = query.strip().lower()
        family_value = family.strip().lower()
        kind_value = kind.strip().upper()
        records = []
        for item in self.catalog():
            if callable_only and not item.get("callable"):
                continue
            if hydrated_only and not item.get("hydrated"):
                continue
            if family_value and str(item.get("family", "")).lower() != family_value:
                continue
            if kind_value and str(item.get("kind", "")).upper() != kind_value:
                continue
            if query_value:
                haystack = " ".join(str(item.get(key, "")) for key in
                                    ("function_id", "name", "module", "symbol", "summary", "family")).lower()
                if query_value not in haystack:
                    continue
            records.append(item)
        total = len(records)
        bounded_offset = max(0, int(offset))
        bounded_limit = max(1, min(1000, int(limit)))
        return {
            "schema": "HHS_PASS_203_FUNCTION_CATALOG_V1",
            "contract": CONTRACT,
            "classification": CLASSIFICATION,
            "total": total,
            "offset": bounded_offset,
            "limit": bounded_limit,
            "functions": records[bounded_offset: bounded_offset + bounded_limit],
            "catalog_sha256": _sha256(self.catalog()),
        }

    def detail(self, function_id: str) -> Dict[str, Any]:
        if self._catalog is None:
            self.refresh()
        record = self._by_id.get(function_id)
        if record is None:
            raise UnknownFunctionError(function_id)
        return {"schema": "HHS_PASS_203_FUNCTION_DETAIL_V1", "contract": CONTRACT,
                "classification": CLASSIFICATION, "function": record}

    def _pass190(self) -> Any:
        if self._pass190_context is not None:
            return self._pass190_context
        python_root = self.repo_root / "native_projects" / "hhs_pass190_operation_fabric" / "python"
        if str(python_root) not in sys.path:
            sys.path.insert(0, str(python_root))
        module = importlib.import_module("hhs_pass190_iteration7")
        self._pass190_context = module.DurableExecutionContext(self.pass190_database)
        return self._pass190_context

    def _invoke_pass190(self, operation_id: str, arguments: Mapping[str, Any], *,
                        capabilities: Sequence[str], idempotency_key: Optional[str],
                        expected_state: Optional[str]) -> Dict[str, Any]:
        result = self._pass190().invoke(operation_id, dict(arguments), surface="pass203-public-api",
                                        capabilities=list(capabilities), idempotency_key=idempotency_key,
                                        expected_state=expected_state)
        return _json_safe(result)

    def _invoke_adapter(self, function_id: str, arguments: Mapping[str, Any]) -> Any:
        if function_id == "adapter:interpreter.exact":
            from hhs_backend.runtime.hhs_live_interpreter_v1 import build_interpreter_request, interpret_expression
            expression = str(arguments.get("expression") or "")
            if not expression:
                raise InvocationRejectedError("expression is required")
            request = build_interpreter_request(
                project_id=str(arguments.get("project_id") or "project:mainframe"),
                source_object_id=str(arguments.get("source_object_id") or "object:expression"),
                expression=expression,
                input_state_ids=list(arguments.get("input_state_ids") or []),
            )
            return interpret_expression(request, expression)
        if function_id == "adapter:compiler.hhs_ir":
            from hhs_backend.runtime.hhs_interpreting_compiler_v1 import build_compiler_request, compile_hhs_source
            source_text = str(arguments.get("source_text") or "")
            if not source_text:
                raise InvocationRejectedError("source_text is required")
            request = build_compiler_request(
                str(arguments.get("project_id") or "project:mainframe"),
                str(arguments.get("source_object_id") or "object:source"),
                source_text,
                str(arguments.get("target") or "HHS_IR"),
            )
            return compile_hhs_source(request, source_text)
        if function_id == "adapter:interpreter.self_test":
            from hhs_backend.runtime.hhs_live_interpreter_v1 import live_interpreter_self_test
            return live_interpreter_self_test()
        if function_id == "adapter:compiler.self_test":
            from hhs_backend.runtime.hhs_interpreting_compiler_v1 import interpreting_compiler_self_test
            return interpreting_compiler_self_test()
        if function_id == "adapter:mainframe.refresh":
            return self.refresh()
        raise UnknownFunctionError(function_id)

    def _invoke_python(self, record: Mapping[str, Any], arguments: Mapping[str, Any], timeout_seconds: int) -> Any:
        if record.get("execution_mode") != "ISOLATED_PYTHON" or not record.get("callable"):
            raise InvocationRejectedError(
                f"Python function requires governed adapter: {record.get('module')}.{record.get('qualname')}"
            )
        request = {
            "module": record["module"], "qualname": record["qualname"],
            "arguments": dict(arguments), "allowed_module_prefixes": list(_SAFE_MODULE_PREFIXES),
            "maximum_result_bytes": MAX_RESULT_BYTES,
        }
        environment = {
            "PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(self.repo_root),
            "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "HHS_PASS203_WORKER": "1",
        }
        completed = subprocess.run(
            [sys.executable, "-m", "hhs_backend.runtime.hhs_pass203_function_worker_v1"],
            cwd=str(self.repo_root), env=environment, input=_canonical_json(request), text=True,
            capture_output=True, timeout=timeout_seconds, check=False,
        )
        if completed.returncode != 0:
            raise InvocationRejectedError(completed.stderr.strip() or completed.stdout.strip() or "isolated function failed")
        try:
            response = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise InvocationRejectedError("isolated function returned invalid JSON") from exc
        if not response.get("ok"):
            raise InvocationRejectedError(str(response.get("error") or "isolated function rejected"))
        return response.get("result")

    def replay(self, receipt_hash72: str) -> Dict[str, Any]:
        return _json_safe(self._pass190().replay(receipt_hash72))

    def invoke(self, function_id: str, arguments: Mapping[str, Any], *,
               workspace_id: Optional[str] = None, project_id: Optional[str] = None,
               capabilities: Sequence[str] = (), idempotency_key: Optional[str] = None,
               expected_state: Optional[str] = None,
               timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Dict[str, Any]:
        encoded_arguments = _canonical_json(arguments).encode("utf-8")
        if len(encoded_arguments) > MAX_ARGUMENT_BYTES:
            raise InvocationRejectedError(f"arguments exceed {MAX_ARGUMENT_BYTES} bytes")
        timeout = max(1, min(MAX_TIMEOUT_SECONDS, int(timeout_seconds)))
        detail = self.detail(function_id)["function"]
        if not detail.get("callable"):
            raise InvocationRejectedError(
                f"function is cataloged but not hydrated for execution; execution_mode={detail.get('execution_mode')}"
            )
        admission = self._authority_tick(f"api.runtime.mainframe.invoke:{function_id}")
        started_ns = time.time_ns()
        if function_id.startswith("op:"):
            result = self._invoke_pass190(function_id[3:], arguments, capabilities=capabilities,
                                          idempotency_key=idempotency_key, expected_state=expected_state)
        elif function_id.startswith("adapter:"):
            result = self._invoke_adapter(function_id, arguments)
        elif function_id.startswith("py:"):
            result = self._invoke_python(detail, arguments, timeout)
        elif function_id.startswith("abi:") and detail.get("bound_operation_id"):
            result = self._invoke_pass190(str(detail["bound_operation_id"]), arguments,
                                          capabilities=capabilities, idempotency_key=idempotency_key,
                                          expected_state=expected_state)
        else:
            raise InvocationRejectedError(f"unsupported execution binding for {function_id}")
        completed_ns = time.time_ns()
        safe_result = _json_safe(result)
        result_bytes = _canonical_json(safe_result).encode("utf-8")
        if len(result_bytes) > MAX_RESULT_BYTES:
            raise InvocationRejectedError(f"result exceeds {MAX_RESULT_BYTES} bytes")
        receipt = {
            "schema": "HHS_PASS_203_FUNCTION_INVOCATION_RECEIPT_V1", "contract": CONTRACT,
            "classification": CLASSIFICATION, "function_id": function_id,
            "descriptor_sha256": detail.get("descriptor_sha256"),
            "arguments_sha256": hashlib.sha256(encoded_arguments).hexdigest(),
            "result_sha256": hashlib.sha256(result_bytes).hexdigest(),
            "workspace_id": workspace_id, "project_id": project_id,
            "started_ns": started_ns, "completed_ns": completed_ns,
            "elapsed_ns": completed_ns - started_ns, "vm81_authorized_tick": admission,
            "execution_mode": detail.get("execution_mode"), "effect_class": detail.get("effect_class"),
        }
        receipt["receipt_hash72"] = hash72("HHS_PASS_203_FUNCTION_INVOCATION_RECEIPT_V1", receipt)
        return {"schema": "HHS_PASS_203_FUNCTION_INVOCATION_V1", "contract": CONTRACT,
                "classification": CLASSIFICATION, "ok": True, "function": detail,
                "arguments": dict(arguments), "result": safe_result, "receipt": receipt}


PASS203_MAINFRAME = HydratedMainframe()

__all__ = [
    "CLASSIFICATION", "CONTRACT", "HydratedMainframe", "InvocationRejectedError",
    "MainframeError", "PASS203_MAINFRAME", "PUBLIC_PREFIX", "UnknownFunctionError", "VERSION",
]

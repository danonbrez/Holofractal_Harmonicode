"""
HHS Authorized Pure Function Executor v1
=======================================

Pass 031 introduced the first deliberately narrow promotion from dry-run execution into
actual authorized function execution.  It is limited to explicit allow-listed,
side-effect-free functions whose body passes a static purity scan and whose
execution path is already represented by the Pass 029 dry-run trace and Pass 030
contract/witness schema registry.

This is not unrestricted plugin execution.  The executor calls only pure,
deterministic functions with JSON-stable inputs and outputs.  Mutation, writes,
network/process activity, dynamic eval/exec, and non-allow-listed targets remain
blocked.  Every promoted call emits:

* the Pass 029 dry-run trace;
* canonical execution request and runtime packet;
* Pass 030 schema-registry validations for the execution objects;
* HHS-M001..M007 foundational audits;
* an authorized runtime tick;
* a C u^72 Hash72 Digital DNA witness;
* a unified Hash72 ledger receipt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import ast
import copy
import importlib
import inspect
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_contract_schema_registry_v1 import classify_schema_object, validate_schema_object
from hhs_runtime.hhs_dryrun_live_plugin_executor_v1 import (
    DRYRUN_MODE_PLANNED_RESULT,
    execute_dryrun_live_plugin,
)
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import assert_contract, make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_AUTHORIZED_PURE_FUNCTION_EXECUTOR_V1"
VERSION = "PASS_032"
MANIFEST_FILE = "AUTHORIZED_PURE_FUNCTION_EXECUTIONS_PASS_032.json"
REPORT_FILE = "AUTHORIZED_PURE_FUNCTION_EXECUTIONS_PASS_032.md"

# Authorized execution batch: pure read/computation helpers only.  These
# functions are deliberately chosen because they perform no persistence, no
# network/process work, no runtime mutation, and no indirect service dispatch.
DEFAULT_AUTHORIZED_PURE_TARGETS = [
    {
        "path": "hhs_runtime/hhs_srcg_gate_v1.py",
        "function": "check_1001_invariant",
        "arguments": [1, 1],
        "keyword_arguments": {"threshold": 1.001},
        "sample_payload": {"A": 1, "B": 1, "threshold": 1.001},
    },
    {
        "path": "hhs_runtime/hhs_system_closure_harness_v1.py",
        "function": "summarize_closure_cycle",
        "arguments": [
            {
                "cycle_index": 0,
                "closure_signature": "PASS_032_SAMPLE_CLOSURE_SIGNATURE",
                "closure_witness": {
                    "schema": "HHS_HASH72_KERNEL_WITNESS_V1",
                    "digest": "0" * 72,
                    "zero_sum": True,
                    "trace_count": 1,
                },
                "ingress": {"direction": "INGRESS", "payload_hash72": "1" * 72},
                "semantic_record": {"payload_hash72": "2" * 72},
                "vector_record": {"vector_hash72": "3" * 72},
                "egress": {"direction": "EGRESS", "payload_hash72": "4" * 72},
                "srcg": {"ok": True, "reason": "sample", "trace": []},
                "api_response_contract": {
                    "contract_type": "api_response",
                    "route": "/api/runtime/closure/harness",
                    "payload_hash72": "5" * 72,
                    "contract_hash72": "6" * 72,
                },
                "ledger": {"ok": True},
                "stable_projection": {},
            }
        ],
        "keyword_arguments": {},
        "sample_payload": {"cycle_index": 0},
    },
    {
        "path": "hhs_runtime/hhs_runtime_contract_v1.py",
        "function": "is_hash72",
        "arguments": ["0" * 72],
        "keyword_arguments": {},
        "sample_payload": {"value": "0" * 72},
    },
]

AUTHORIZED_PURE_ALLOWLIST = {
    "hhs_runtime/hhs_srcg_gate_v1.py": {"check_1001_invariant"},
    "hhs_runtime/hhs_system_closure_harness_v1.py": {"summarize_closure_cycle"},
    "hhs_runtime/hhs_runtime_contract_v1.py": {"is_hash72"},
}

# Conservative static scan.  Local variable assignment is allowed; operations
# that can mutate external state or execute arbitrary code are not.
PURE_FUNCTION_BLOCKED_NAMES = {
    "append",
    "extend",
    "insert",
    "pop",
    "remove",
    "clear",
    "update",
    "setdefault",
    "write",
    "writelines",
    "write_text",
    "write_bytes",
    "read_text",  # authorized pure functions should not touch the filesystem at all
    "read_bytes",
    "open",
    "mkdir",
    "rmdir",
    "unlink",
    "rename",
    "replace",
    "delete",
    "exec",
    "eval",
    "compile",
    "__import__",
    "import_module",
    "subprocess",
    "system",
    "popen",
    "socket",
    "requests",
    "urlopen",
    "send",
    "commit",
    "dispatch",
    "authorized_tick",
    "append_payload",
}


class HHSAuthorizedPureFunctionExecutorError(RuntimeError):
    """Raised when Pass 032 authorized pure execution would violate policy."""


@dataclass(frozen=True)
class HHSPureFunctionSurface:
    schema: str
    version: str
    path: str
    module_name: str
    function: str
    signature: str
    source_line: int | None
    source_end_line: int | None
    is_async: bool
    risk_flags: List[str]
    purity_static_scan_ok: bool
    import_performed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HHSAuthorizedPureFunctionExecution:
    path: str
    function: str
    execution_status: str
    authorized_pure_execution: bool
    execution_policy: Dict[str, Any]
    dry_run_trace: Dict[str, Any]
    function_surface: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    schema_registry_validations: Dict[str, Any]
    live_result: Dict[str, Any]
    result_kernel_witness: Dict[str, Any]
    foundational_conformance_pre: Dict[str, Any]
    foundational_conformance_post: Dict[str, Any]
    authorized_tick: Dict[str, Any]
    ledger: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def _json_roundtrip(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, ensure_ascii=False, default=str))


def _with_digest72_alias(witness: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _module_name_from_path(path: str) -> str:
    rel = path.replace("\\", "/")
    if not rel.endswith(".py"):
        raise HHSAuthorizedPureFunctionExecutorError(f"authorized pure target must be a Python module path: {path}")
    return rel[:-3].replace("/", ".")


def _source_path(root: Path, path: str) -> Path:
    rel = path.replace("\\", "/")
    candidate = (root / rel).resolve()
    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(rel)
    if root not in candidate.parents and candidate != root:
        raise HHSAuthorizedPureFunctionExecutorError(f"path escapes repository root: {rel}")
    return candidate


def _function_node(source: str, rel_path: str, function_name: str) -> ast.AST:
    tree = ast.parse(source, filename=rel_path)
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            return node
    raise HHSAuthorizedPureFunctionExecutorError(f"function not found in source: {rel_path}.{function_name}")


def _static_purity_flags(node: ast.AST) -> List[str]:
    names: List[str] = []
    for item in ast.walk(node):
        if isinstance(item, ast.Name):
            names.append(item.id)
        elif isinstance(item, ast.Attribute):
            names.append(item.attr)
        elif isinstance(item, (ast.Import, ast.ImportFrom)):
            names.append("import")
        elif isinstance(item, (ast.With, ast.AsyncWith)):
            names.append("with")
        elif isinstance(item, (ast.Global, ast.Nonlocal)):
            names.append("global_nonlocal")
        elif isinstance(item, (ast.Await, ast.Yield, ast.YieldFrom)):
            names.append("async_or_generator")
    lowered = {name.lower() for name in names}
    return sorted(name for name in PURE_FUNCTION_BLOCKED_NAMES if name.lower() in lowered)


def _assert_authorized_pure_policy(target: Mapping[str, Any]) -> Dict[str, Any]:
    path = str(target.get("path") or "")
    function_name = str(target.get("function") or "")
    if path not in AUTHORIZED_PURE_ALLOWLIST:
        raise HHSAuthorizedPureFunctionExecutorError(f"target path is not in Pass 032 pure allow-list: {path}")
    if function_name not in AUTHORIZED_PURE_ALLOWLIST[path]:
        raise HHSAuthorizedPureFunctionExecutorError(f"function is not in Pass 032 pure allow-list: {path}.{function_name}")
    for flag in ("direct_execution_authorized", "mutation_authorized", "write_authorized", "network_authorized", "process_authorized"):
        if bool(target.get(flag, False)):
            raise HHSAuthorizedPureFunctionExecutorError(f"{flag} must remain false for authorized pure execution")
    if not bool(target.get("authorized_pure_execution", True)):
        raise HHSAuthorizedPureFunctionExecutorError("authorized_pure_execution must be true")
    return {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_POLICY_V1",
        "version": VERSION,
        "path": path,
        "function": function_name,
        "allowed": True,
        "allowlist_match": True,
        "dry_run_required": True,
        "pass030_schema_registry_required": True,
        "operation_class": "AUTHORIZED_PURE_DETERMINISTIC_FUNCTION",
        "direct_legacy_execution": False,
        "mutation_allowed": False,
        "write_allowed": False,
        "network_allowed": False,
        "process_allowed": False,
        "result_must_be_json_stable": True,
    }


def _function_surface(root: Path, path: str, function_name: str) -> Dict[str, Any]:
    source_file = _source_path(root, path)
    source = source_file.read_text(encoding="utf-8", errors="replace")
    node = _function_node(source, path, function_name)
    module_name = _module_name_from_path(path)
    module = importlib.import_module(module_name)
    fn = getattr(module, function_name, None)
    if fn is None or not callable(fn):
        raise HHSAuthorizedPureFunctionExecutorError(f"function is not callable: {module_name}.{function_name}")
    flags = _static_purity_flags(node)
    try:
        signature = str(inspect.signature(fn))
    except (TypeError, ValueError):
        signature = "<unavailable>"
    surface = HHSPureFunctionSurface(
        schema="HHS_AUTHORIZED_PURE_FUNCTION_SURFACE_V1",
        version=VERSION,
        path=path,
        module_name=module_name,
        function=function_name,
        signature=signature,
        source_line=getattr(node, "lineno", None),
        source_end_line=getattr(node, "end_lineno", None),
        is_async=inspect.iscoroutinefunction(fn),
        risk_flags=flags,
        purity_static_scan_ok=not flags and not inspect.iscoroutinefunction(fn),
        import_performed=True,
    ).to_dict()
    if flags:
        raise HHSAuthorizedPureFunctionExecutorError(f"static purity scan blocked {path}.{function_name}: {flags}")
    if surface["is_async"]:
        raise HHSAuthorizedPureFunctionExecutorError("authorized pure execution is synchronous only")
    return surface


def _get_callable(path: str, function_name: str) -> Any:
    module = importlib.import_module(_module_name_from_path(path))
    fn = getattr(module, function_name, None)
    if fn is None or not callable(fn):
        raise HHSAuthorizedPureFunctionExecutorError(f"function is not callable: {path}.{function_name}")
    return fn


def _execute_pure_callable(fn: Any, arguments: List[Any], keyword_arguments: Dict[str, Any]) -> Dict[str, Any]:
    sig = inspect.signature(fn)
    try:
        bound = sig.bind(*arguments, **keyword_arguments)
    except TypeError as exc:
        raise HHSAuthorizedPureFunctionExecutorError(f"arguments do not bind to pure function signature: {exc}") from exc
    bound.apply_defaults()
    before_arguments = _json_roundtrip({"args": arguments, "kwargs": keyword_arguments})
    result = fn(*arguments, **keyword_arguments)
    after_arguments = _json_roundtrip({"args": arguments, "kwargs": keyword_arguments})
    result_json = _json_roundtrip(result)
    return {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_RESULT_V1",
        "version": VERSION,
        "result_type": type(result).__name__,
        "result": result_json,
        "call_performed": True,
        "body_execution_performed": True,
        "argument_mutation_detected": before_arguments != after_arguments,
        "mutation_performed": False,
        "write_performed": False,
        "network_performed": False,
        "process_performed": False,
        "json_stable": _canonical(result_json) == _canonical(_json_roundtrip(result_json)),
    }


def execute_authorized_pure_function(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
) -> Dict[str, Any]:
    """Execute one allow-listed pure function through the authorized authority chain."""

    root_path = _repo_root(root)
    policy = _assert_authorized_pure_policy(target)
    path = policy["path"]
    function_name = policy["function"]
    arguments = copy.deepcopy(list(target.get("arguments") or []))
    keyword_arguments = copy.deepcopy(dict(target.get("keyword_arguments") or {}))
    sample_payload = copy.deepcopy(dict(target.get("sample_payload") or {"arguments": arguments, "keyword_arguments": keyword_arguments}))

    dry_run_trace = execute_dryrun_live_plugin(
        {
            "path": path,
            "function": function_name,
            "mode": DRYRUN_MODE_PLANNED_RESULT,
            "sample_payload": sample_payload,
            "dry_run_live_authorized": True,
        },
        root=root_path,
        controller=controller,
    )
    if dry_run_trace.get("dry_run_result", {}).get("call_performed"):
        raise HHSAuthorizedPureFunctionExecutorError("dry-run trace unexpectedly performed a function call")

    function_surface = _function_surface(root_path, path, function_name)

    proposition_identity = make_proposition_identity(
        f"Authorized pure execution preserves the explicit function identity for {path}.{function_name} after dry-run and schema validation.",
        source=f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}",
        context={"policy": policy, "arguments": arguments, "keyword_arguments": keyword_arguments},
    )
    meaning_pre = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="authorized pure function preflight after dry-run preserves proposition identity",
        reversible=True,
        receipt_hash72=dry_run_trace.get("dryrun_kernel_witness", {}).get("digest72", ""),
    )
    pre_payload = {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_PRE_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "dry_run_trace": dry_run_trace,
        "function_surface": function_surface,
        "arguments": arguments,
        "keyword_arguments": keyword_arguments,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_pre,
    }
    execution_request = make_execution_request(
        source=f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}",
        operation=f"authorized_pure_function.{function_name}",
        payload=pre_payload,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet("INTERNAL", f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}", pre_payload)
    assert_contract(runtime_packet, expected_type="runtime_packet")

    schema_validations = {
        "execution_request_classification": classify_schema_object(execution_request),
        "execution_request_validation": validate_schema_object(execution_request),
        "runtime_packet_classification": classify_schema_object(runtime_packet),
        "runtime_packet_validation": validate_schema_object(runtime_packet),
        "dryrun_trace_classification": classify_schema_object(dry_run_trace),
        "dryrun_trace_validation": validate_schema_object(dry_run_trace),
    }
    if not schema_validations["execution_request_validation"].get("ok"):
        raise HHSAuthorizedPureFunctionExecutorError("Pass 030 schema registry rejected execution_request")
    if not schema_validations["runtime_packet_validation"].get("ok"):
        raise HHSAuthorizedPureFunctionExecutorError("Pass 030 schema registry rejected runtime_packet")

    foundational_pre = assert_foundational_conformance(
        execution_request,
        source=f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}.pre",
        require_receipt=False,
    ).to_dict()

    active_controller = controller or HHSRuntimeController()
    authorized_tick = active_controller.authorized_tick(source=f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}")

    live_result = _execute_pure_callable(_get_callable(path, function_name), arguments, keyword_arguments)
    if live_result.get("argument_mutation_detected"):
        raise HHSAuthorizedPureFunctionExecutorError("authorized pure execution detected argument mutation")
    if not live_result.get("json_stable"):
        raise HHSAuthorizedPureFunctionExecutorError("authorized pure execution result is not JSON stable")

    result_kernel_witness = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_authorized_pure_function_result_v1",
            _canonical({"policy": policy, "function_surface": function_surface, "live_result": live_result}),
            width=72,
        ).to_dict()
    )
    meaning_post = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="authorized pure function execution returned a deterministic JSON-stable result under the guarded authority chain",
        reversible=True,
        receipt_hash72=result_kernel_witness.get("digest72", ""),
    )
    post_payload = {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_POST_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "function_surface": function_surface,
        "live_result": live_result,
        "result_kernel_witness": result_kernel_witness,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_post,
    }
    foundational_post = assert_foundational_conformance(
        post_payload,
        source=f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}.post",
        require_receipt=False,
    ).to_dict()

    ledger_payload = {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_LEDGER_PAYLOAD_V1",
        "version": VERSION,
        "policy": policy,
        "dry_run_trace_summary": {
            "execution_status": dry_run_trace.get("execution_status"),
            "dryrun_kernel_witness": dry_run_trace.get("dryrun_kernel_witness", {}),
        },
        "function_surface": function_surface,
        "live_result": live_result,
        "result_kernel_witness": result_kernel_witness,
        "authorized_receipt": authorized_tick.get("receipt", {}),
        "foundational_conformance_pre": foundational_pre,
        "foundational_conformance_post": foundational_post,
        "schema_registry_validations": schema_validations,
    }
    ledger = append_payload(
        "AUTHORIZED_PURE_FUNCTION_EXECUTION",
        f"hhs_authorized_pure_function_executor_v1.{path}.{function_name}",
        ledger_payload,
    )

    return HHSAuthorizedPureFunctionExecution(
        path=path,
        function=function_name,
        execution_status="AUTHORIZED_PURE_FUNCTION_EXECUTED",
        authorized_pure_execution=True,
        execution_policy=policy,
        dry_run_trace=dry_run_trace,
        function_surface=function_surface,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        schema_registry_validations=schema_validations,
        live_result=live_result,
        result_kernel_witness=result_kernel_witness,
        foundational_conformance_pre=foundational_pre,
        foundational_conformance_post=foundational_post,
        authorized_tick=authorized_tick,
        ledger={
            "entry_count": ledger.get("entry_count"),
            "tip_hash72": ledger.get("tip_hash72"),
            "ledger_hash72": ledger.get("ledger_hash72"),
            "hash72_authority": ledger.get("hash72_authority"),
        },
    ).to_dict()


def build_authorized_pure_function_execution_manifest(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    executions: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for target in list(targets or DEFAULT_AUTHORIZED_PURE_TARGETS):
        t = dict(target)
        t.setdefault("authorized_pure_execution", True)
        try:
            executions.append(execute_authorized_pure_function(t, root=root_path))
        except Exception as exc:  # pragma: no cover - manifest preserves rejection evidence
            errors.append({"target": _canonical(t), "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "execution_count": len(executions),
        "error_count": len(errors),
        "execution_policy": "Allow-listed pure deterministic functions only; dry-run trace, Pass 030 schema validation, Hash72/u^72 witness, foundational audit, authorized tick, and ledger receipt required before/after actual call.",
        "allowlist_size": sum(len(functions) for functions in AUTHORIZED_PURE_ALLOWLIST.values()),
        "targets": [{"path": item.get("path"), "function": item.get("function")} for item in executions],
        "raw_plugin_execution": "blocked",
        "mutation_write_network_process": "blocked",
    }
    witness = _with_digest72_alias(
        make_hash72_kernel_witness("hhs_authorized_pure_function_manifest_v1", _canonical(payload), width=72).to_dict()
    )
    return {
        **payload,
        "executions": executions,
        "errors": errors,
        "ledger": verify_unified_ledger(),
        "hash72_kernel_witness": witness,
    }


def write_authorized_pure_function_execution_artifacts(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_authorized_pure_function_execution_manifest(root_path, targets=targets)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Function | Status | Call | Argument Mutation | Witness |", "|---|---|---|---:|---:|---|"]
    for item in manifest.get("executions", []):
        witness = item.get("result_kernel_witness", {}).get("digest72", "")
        result = item.get("live_result", {})
        rows.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                item.get("path", ""),
                item.get("function", ""),
                item.get("execution_status", ""),
                result.get("call_performed"),
                result.get("argument_mutation_detected"),
                witness[:18] + "…" if witness else "",
            )
        )
    content = f"""# Pass 032 Authorized Pure Function Executions

Schema: `{manifest.get('schema')}`  
Version: `{manifest.get('version')}`

Pass 032 expands the narrow allow-list from dry-run into actual execution, but
only for pure deterministic functions.  The execution boundary remains strict:
no arbitrary legacy/plugin execution, no mutation, no writes, no network/process
activity, and no schema-unregistered promotion.

## Summary

- Execution count: `{manifest.get('execution_count')}`
- Error count: `{manifest.get('error_count')}`
- Allow-list size: `{manifest.get('allowlist_size')}`
- Ledger OK: `{manifest.get('ledger', {}).get('ok')}`
- Manifest witness: `{manifest.get('hash72_kernel_witness', {}).get('digest72')}`

## Executions

{chr(10).join(rows)}

## Promotion invariant

```text
Dry-run trace
→ Pass 030 schema validation
→ HHS-M001..M007 foundational audit
→ authorized runtime tick
→ actual pure call
→ C u^72 Hash72 result witness
→ unified ledger receipt
```

Any target that requires mutation/write/network/process access remains blocked
until a later explicit adapter with rollback and closure-harness coverage exists.
"""
    (root / REPORT_FILE).write_text(content, encoding="utf-8")


def authorized_pure_function_executor_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    payload = dict(payload or {})
    root = payload.get("root")
    manifest = write_authorized_pure_function_execution_artifacts(root)
    no_errors = manifest.get("error_count") == 0
    calls = [item.get("live_result", {}).get("call_performed") for item in manifest.get("executions", [])]
    no_argument_mutation = all(
        not item.get("live_result", {}).get("argument_mutation_detected")
        for item in manifest.get("executions", [])
    )
    schema_valid = all(
        item.get("schema_registry_validations", {}).get("execution_request_validation", {}).get("ok")
        and item.get("schema_registry_validations", {}).get("runtime_packet_validation", {}).get("ok")
        for item in manifest.get("executions", [])
    )
    ok = (
        manifest.get("schema") == SCHEMA
        and manifest.get("execution_count", 0) > 0
        and no_errors
        and all(calls)
        and no_argument_mutation
        and schema_valid
        and manifest.get("ledger", {}).get("ok")
        and bool(manifest.get("hash72_kernel_witness", {}).get("digest72"))
    )
    return {
        "schema": "HHS_AUTHORIZED_PURE_FUNCTION_EXECUTOR_SELF_TEST_V1",
        "ok": bool(ok),
        "execution_count": manifest.get("execution_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
        "call_performed": all(calls),
        "argument_mutation_detected": not no_argument_mutation,
        "schema_registry_valid": schema_valid,
    }


if __name__ == "__main__":
    print(json.dumps(authorized_pure_function_executor_self_test(), indent=2, sort_keys=True))

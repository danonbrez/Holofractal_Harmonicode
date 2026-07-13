"""
HHS Dry-Run Live Plugin Executor v1
===================================

Pass 029 adds the dry-run execution layer after Pass 028 read-only live
introspection. The executor imports explicit allow-listed modules, validates a
named function surface, builds a canonical dry-run invocation envelope, and
emits the same authority evidence required by live execution:

* canonical execution request;
* canonical runtime packet;
* HHS-M001..M007 foundational audits;
* authorized runtime tick;
* C u^72 Hash72 Digital DNA witnesses;
* unified Hash72 ledger append.

The boundary is intentionally strict: target function bodies are not executed.
Dry-run execution means "produce the contract-bound invocation trace and planned
result shape". It is the last staging point before a future pass can promote a
specific adapter from dry-run to live mutation-safe execution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import ast
import importlib
import inspect
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import assert_contract, make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_DRYRUN_LIVE_PLUGIN_EXECUTOR_V1"
VERSION = "PASS_029"
MANIFEST_FILE = "DRYRUN_LIVE_PLUGIN_EXECUTIONS_PASS_029.json"
REPORT_FILE = "DRYRUN_LIVE_PLUGIN_EXECUTIONS_PASS_029.md"

DRYRUN_MODE_CONTRACT_TRACE = "CONTRACT_TRACE"
DRYRUN_MODE_PLANNED_RESULT = "PLANNED_RESULT"

DEFAULT_DRYRUN_LIVE_TARGETS = [
    {
        "path": "hhs_backend/runtime/runtime_semantic_memory_engine.py",
        "function": "semantic_memory_self_test",
        "mode": DRYRUN_MODE_CONTRACT_TRACE,
        "sample_payload": {},
    },
    {
        "path": "hhs_backend/runtime/runtime_multimodal_embedding_router.py",
        "function": "multimodal_router_self_test",
        "mode": DRYRUN_MODE_CONTRACT_TRACE,
        "sample_payload": {},
    },
    {
        "path": "hhs_backend/runtime/runtime_prediction_engine.py",
        "function": "prediction_engine_self_test",
        "mode": DRYRUN_MODE_CONTRACT_TRACE,
        "sample_payload": {},
    },
    {
        "path": "hhs_runtime/hhs_srcg_gate_v1.py",
        "function": "check_1001_invariant",
        "mode": DRYRUN_MODE_PLANNED_RESULT,
        "sample_payload": {"A": 1, "B": 1, "threshold": 1.001},
    },
]

DRYRUN_LIVE_ALLOWLIST = {
    "hhs_backend/runtime/runtime_semantic_memory_engine.py": {"semantic_memory_self_test"},
    "hhs_backend/runtime/runtime_multimodal_embedding_router.py": {"multimodal_router_self_test"},
    "hhs_backend/runtime/runtime_prediction_engine.py": {"prediction_engine_self_test"},
    "hhs_backend/runtime/runtime_agentic_cognition_layer.py": {"agentic_cognition_self_test"},
    "hhs_runtime/hhs_system_closure_harness_v1.py": {"summarize_closure_cycle", "system_closure_harness_self_test"},
    "hhs_runtime/hhs_srcg_gate_v1.py": {"check_1001_invariant", "selfsolve_ab_gate", "srcg_primitive_self_test"},
    "hhs_runtime/hhs_hash72_kernel_authority_v1.py": {"hash72_kernel_authority_self_test"},
    "hhs_runtime/hhs_runtime_contract_v1.py": {"is_hash72"},
}

MUTATION_RISK_NAMES = {
    "write",
    "write_text",
    "write_bytes",
    "append",
    "delete",
    "remove",
    "unlink",
    "rmdir",
    "mkdir",
    "rename",
    "replace",
    "open",
    "exec",
    "eval",
    "subprocess",
    "system",
    "socket",
    "requests",
}


class HHSDryRunLivePluginExecutorError(RuntimeError):
    """Raised when a dry-run live adapter request violates policy."""


@dataclass(frozen=True)
class HHSDryRunLivePluginExecution:
    path: str
    function: str
    mode: str
    execution_status: str
    dry_run_authorized: bool
    execution_policy: Dict[str, Any]
    function_surface: Dict[str, Any]
    dry_run_result: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    dryrun_kernel_witness: Dict[str, Any]
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


def _with_digest72_alias(witness: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _module_name_from_path(path: str) -> str:
    rel = path.replace("\\", "/")
    if not rel.endswith(".py"):
        raise HHSDryRunLivePluginExecutorError(f"dry-run target must be a Python module path: {path}")
    return rel[:-3].replace("/", ".")


def _source_path(root: Path, path: str) -> Path:
    rel = path.replace("\\", "/")
    candidate = (root / rel).resolve()
    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(rel)
    if root not in candidate.parents and candidate != root:
        raise HHSDryRunLivePluginExecutorError(f"path escapes repository root: {rel}")
    return candidate


def _find_function_node(source: str, rel_path: str, function_name: str) -> ast.AST:
    tree = ast.parse(source, filename=rel_path)
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            return node
    raise HHSDryRunLivePluginExecutorError(f"function not found in source: {rel_path}.{function_name}")


def _function_risk_flags(node: ast.AST) -> List[str]:
    names: List[str] = []
    for item in ast.walk(node):
        if isinstance(item, ast.Name):
            names.append(item.id)
        elif isinstance(item, ast.Attribute):
            names.append(item.attr)
    lowered = {name.lower() for name in names}
    return sorted(name for name in MUTATION_RISK_NAMES if name.lower() in lowered)


def _assert_dryrun_policy(target: Mapping[str, Any]) -> Dict[str, Any]:
    path = str(target.get("path") or "")
    function_name = str(target.get("function") or "")
    mode = str(target.get("mode") or DRYRUN_MODE_CONTRACT_TRACE)
    if path not in DRYRUN_LIVE_ALLOWLIST:
        raise HHSDryRunLivePluginExecutorError(f"target is not in dry-run live allow-list: {path}")
    if function_name not in DRYRUN_LIVE_ALLOWLIST[path]:
        raise HHSDryRunLivePluginExecutorError(f"function is not in dry-run live allow-list: {path}.{function_name}")
    if mode not in {DRYRUN_MODE_CONTRACT_TRACE, DRYRUN_MODE_PLANNED_RESULT}:
        raise HHSDryRunLivePluginExecutorError(f"unsupported dry-run mode: {mode}")
    if bool(target.get("direct_execution_authorized", False)):
        raise HHSDryRunLivePluginExecutorError("direct legacy execution is not accepted by Pass 029")
    if bool(target.get("mutation_authorized", False)):
        raise HHSDryRunLivePluginExecutorError("mutation_authorized must remain false for dry-run adapters")
    if bool(target.get("network_authorized", False)):
        raise HHSDryRunLivePluginExecutorError("network_authorized must remain false for dry-run adapters")
    if bool(target.get("write_authorized", False)):
        raise HHSDryRunLivePluginExecutorError("write_authorized must remain false for dry-run adapters")
    if not bool(target.get("dry_run_live_authorized", True)):
        raise HHSDryRunLivePluginExecutorError("dry_run_live_authorized must be true")
    return {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_POLICY_V1",
        "version": VERSION,
        "path": path,
        "function": function_name,
        "mode": mode,
        "allowed": True,
        "allowlist_match": True,
        "direct_legacy_execution": False,
        "function_body_execution": False,
        "dry_run_execution": True,
        "mutation_allowed": False,
        "write_allowed": False,
        "network_allowed": False,
        "process_allowed": False,
        "operation_class": "DRY_RUN_CONTRACT_TRACE",
    }


def _summarize_function_surface(root: Path, path: str, function_name: str) -> Dict[str, Any]:
    source_file = _source_path(root, path)
    source = source_file.read_text(encoding="utf-8", errors="replace")
    node = _find_function_node(source, path, function_name)
    module_name = _module_name_from_path(path)
    module = importlib.import_module(module_name)
    fn = getattr(module, function_name, None)
    if not callable(fn):
        raise HHSDryRunLivePluginExecutorError(f"imported function is not callable: {module_name}.{function_name}")
    try:
        signature = str(inspect.signature(fn))
    except (TypeError, ValueError):
        signature = "<unavailable>"
    return {
        "schema": "HHS_DRYRUN_FUNCTION_SURFACE_V1",
        "version": VERSION,
        "module_name": module_name,
        "module_file": str(getattr(module, "__file__", "")),
        "function": function_name,
        "signature": signature,
        "is_async": inspect.iscoroutinefunction(fn),
        "doc": (inspect.getdoc(fn) or "").splitlines()[:6],
        "source_line": getattr(node, "lineno", None),
        "source_end_line": getattr(node, "end_lineno", None),
        "risk_flags": _function_risk_flags(node),
        "import_performed": True,
        "body_execution_performed": False,
        "mutation_performed": False,
    }


def execute_dryrun_live_plugin(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
) -> Dict[str, Any]:
    """Build and commit a dry-run invocation trace for an allow-listed function."""

    root_path = _repo_root(root)
    policy = _assert_dryrun_policy(target)
    path = policy["path"]
    function_name = policy["function"]
    sample_payload = dict(target.get("sample_payload") or {})
    function_surface = _summarize_function_surface(root_path, path, function_name)

    proposition_identity = make_proposition_identity(
        f"Dry-run live plugin executor preserves function identity for {path}.{function_name} without direct body execution.",
        source=f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}",
        context={"policy": policy, "sample_payload": sample_payload},
    )
    meaning_witness_pre = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="dry-run live plugin preflight preserves function identity before planned invocation",
        reversible=True,
        receipt_hash72="",
    )
    pre_payload = {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_PRE_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "sample_payload": sample_payload,
        "function_surface": function_surface,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness_pre,
        "transformation_rule": "contract-bound dry-run trace only",
    }
    execution_request = make_execution_request(
        source=f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}",
        operation=f"dryrun_live_plugin.{function_name}",
        payload=pre_payload,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet("INTERNAL", f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}", pre_payload)
    assert_contract(runtime_packet, expected_type="runtime_packet")
    foundational_pre = assert_foundational_conformance(
        execution_request,
        source=f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}.pre",
        require_receipt=False,
    ).to_dict()

    active_controller = controller or HHSRuntimeController()
    authorized_tick = active_controller.authorized_tick(source=f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}")

    dry_run_result = {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_RESULT_V1",
        "version": VERSION,
        "status": "DRY_RUN_TRACE_GENERATED",
        "path": path,
        "function": function_name,
        "mode": policy["mode"],
        "sample_payload": sample_payload,
        "planned_result_shape": {
            "ok": "bool",
            "schema": "string",
            "artifacts": "list[string]",
            "ledger": "hash72-ledger-summary",
        },
        "call_performed": False,
        "body_execution_performed": False,
        "mutation_performed": False,
        "network_performed": False,
        "write_performed": False,
    }
    dryrun_kernel_witness = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_dryrun_live_plugin_result_v1",
            _canonical({"policy": policy, "function_surface": function_surface, "dry_run_result": dry_run_result}),
            width=72,
        ).to_dict()
    )
    meaning_witness_post = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="dry-run live plugin executor generated planned result trace without function body execution",
        reversible=True,
        receipt_hash72=dryrun_kernel_witness.get("digest72", ""),
    )
    post_payload = {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_POST_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "function_surface": function_surface,
        "dry_run_result": dry_run_result,
        "dryrun_kernel_witness": dryrun_kernel_witness,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness_post,
    }
    foundational_post = assert_foundational_conformance(
        post_payload,
        source=f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}.post",
        require_receipt=False,
    ).to_dict()

    ledger_payload = {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_LEDGER_PAYLOAD_V1",
        "version": VERSION,
        "policy": policy,
        "function_surface": function_surface,
        "dry_run_result": dry_run_result,
        "authorized_receipt": authorized_tick.get("receipt", {}),
        "dryrun_kernel_witness": dryrun_kernel_witness,
        "foundational_conformance_pre": foundational_pre,
        "foundational_conformance_post": foundational_post,
    }
    ledger = append_payload("DRYRUN_LIVE_PLUGIN_EXECUTION", f"hhs_dryrun_live_plugin_executor_v1.{path}.{function_name}", ledger_payload)

    return HHSDryRunLivePluginExecution(
        path=path,
        function=function_name,
        mode=policy["mode"],
        execution_status="DRYRUN_LIVE_PLUGIN_TRACE_GENERATED",
        dry_run_authorized=True,
        execution_policy=policy,
        function_surface=function_surface,
        dry_run_result=dry_run_result,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        dryrun_kernel_witness=dryrun_kernel_witness,
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


def build_dryrun_live_plugin_execution_manifest(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    executions: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    prepared_targets: List[Mapping[str, Any]] = []
    for target in list(targets or DEFAULT_DRYRUN_LIVE_TARGETS):
        t = dict(target)
        t.setdefault("dry_run_live_authorized", True)
        t.setdefault("mode", DRYRUN_MODE_CONTRACT_TRACE)
        prepared_targets.append(t)
    for target in prepared_targets:
        try:
            executions.append(execute_dryrun_live_plugin(target, root=root_path))
        except Exception as exc:  # pragma: no cover - manifest keeps audit trail
            errors.append({"target": _canonical(target), "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "execution_count": len(executions),
        "error_count": len(errors),
        "execution_policy": "Dry-run contract-bound planned invocation traces only; no function body execution, mutation, write, network, or process activity.",
        "allowlist_size": sum(len(functions) for functions in DRYRUN_LIVE_ALLOWLIST.values()),
        "targets": [{"path": item.get("path"), "function": item.get("function"), "mode": item.get("mode")} for item in executions],
    }
    return {
        **payload,
        "executions": executions,
        "errors": errors,
        "ledger": verify_unified_ledger(),
        "hash72_kernel_witness": _with_digest72_alias(
            make_hash72_kernel_witness("hhs_dryrun_live_plugin_manifest_v1", _canonical(payload), width=72).to_dict()
        ),
    }


def write_dryrun_live_plugin_execution_artifacts(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_dryrun_live_plugin_execution_manifest(root_path, targets=targets)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Function | Mode | Status | Call Performed | Witness |", "|---|---|---|---|---:|---|"]
    for item in manifest.get("executions", []):
        witness = item.get("dryrun_kernel_witness", {}).get("digest72", "")
        rows.append(
            "| `{}` | `{}` | `{}` | {} | {} | `{}` |".format(
                item.get("path"),
                item.get("function"),
                item.get("mode"),
                item.get("execution_status"),
                item.get("dry_run_result", {}).get("call_performed"),
                f"{witness[:18]}…" if witness else "—",
            )
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | — | See manifest. |")
    report = f"""# Dry-Run Live Plugin Executor — Pass 029

## Purpose

Pass 029 promotes the plugin adapter path from read-only module introspection to dry-run invocation traces. A target function can now be imported, signature-validated, wrapped in a canonical execution request, and assigned a planned result shape without executing the target function body.

## Non-Bypass Policy

```text
explicit dry-run allow-list
→ import/signature validation
→ no target function body execution
→ canonical execution request/runtime packet
→ HHS-M001..M007 foundational audits
→ authorized runtime tick
→ C u^72 Hash72 Digital DNA witness
→ unified Hash72 ledger append
```

## Summary

```json
{json.dumps({k: manifest.get(k) for k in ['schema', 'version', 'execution_count', 'error_count', 'execution_policy', 'allowlist_size']}, indent=2, sort_keys=True)}
```

## Executions

{chr(10).join(rows)}

## Manifest Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def dryrun_live_plugin_executor_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    targets = payload.get("targets") if payload else None
    manifest = write_dryrun_live_plugin_execution_artifacts(root, targets=targets)
    no_calls = all(not item.get("dry_run_result", {}).get("call_performed", True) for item in manifest.get("executions", []))
    ok = (
        manifest.get("schema") == SCHEMA
        and manifest.get("execution_count", 0) > 0
        and manifest.get("error_count") == 0
        and manifest.get("ledger", {}).get("ok")
        and no_calls
    )
    return {
        "schema": "HHS_DRYRUN_LIVE_PLUGIN_EXECUTOR_SELF_TEST_V1",
        "ok": bool(ok),
        "execution_count": manifest.get("execution_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
        "call_performed": not no_calls,
    }


if __name__ == "__main__":
    print(json.dumps(dryrun_live_plugin_executor_self_test(), indent=2, sort_keys=True))

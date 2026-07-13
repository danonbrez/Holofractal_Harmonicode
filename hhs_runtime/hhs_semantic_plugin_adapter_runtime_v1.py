"""
HHS Semantic Plugin Adapter Runtime v1
======================================

Pass 026 is the first live guarded semantic-adapter layer for PLUGIN_READY
modules.

Pass 023 created static adapter reachability.
Pass 024 created safe invocation plans.
Pass 025 made those plans authority-reachable but intentionally did not execute
legacy/plugin module code.

Pass 026 executes the semantic adapter itself, not the legacy module. The
adapter reads source, parses AST, preserves the requested function identity,
emits canonical contracts and C u^72 Hash72 witnesses, runs HHS-M001..M007
audits, records the event in the unified Hash72 ledger, and returns a
closure-harness-ready semantic result.

This advances plugin integration without opening a bypass path: no candidate
module is imported, no top-level legacy code runs, and no function body from a
candidate module is executed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import ast
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_plugin_capability_planner_v1 import (
    DEFAULT_CAPABILITY_PLAN_PATHS,
    build_plugin_capability_plan_manifest,
)
from hhs_runtime.hhs_guarded_plugin_invocation_executor_v1 import (
    DEFAULT_INVOCATION_TARGETS,
    execute_planned_plugin_invocation,
)
from hhs_runtime.hhs_runtime_contract_v1 import (
    assert_contract,
    make_execution_request,
    make_runtime_packet,
)
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_SEMANTIC_PLUGIN_ADAPTER_RUNTIME_V1"
VERSION = "PASS_026"
MANIFEST_FILE = "SEMANTIC_PLUGIN_ADAPTER_EXECUTIONS_PASS_026.json"
REPORT_FILE = "SEMANTIC_PLUGIN_ADAPTER_EXECUTIONS_PASS_026.md"

DEFAULT_SEMANTIC_ADAPTER_TARGETS = DEFAULT_INVOCATION_TARGETS[:6]


class HHSSemanticPluginAdapterError(RuntimeError):
    """Raised when a semantic adapter execution violates the non-bypass policy."""


@dataclass(frozen=True)
class HHSSemanticAdapterExecution:
    path: str
    function: str
    adapter_type: str
    execution_status: str
    direct_legacy_import: bool
    executed_legacy_code: bool
    source_summary: Dict[str, Any]
    semantic_adapter_result: Dict[str, Any]
    invocation_record: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    adapter_kernel_witness: Dict[str, Any]
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


def _plans_by_path(root: Path, paths: Optional[Iterable[str]] = None) -> Dict[str, Dict[str, Any]]:
    manifest = build_plugin_capability_plan_manifest(root, paths=paths or DEFAULT_CAPABILITY_PLAN_PATHS)
    return {str(plan.get("path")): plan for plan in manifest.get("plans", [])}


def _public_defs(tree: ast.AST) -> tuple[List[ast.AST], List[str]]:
    functions: List[ast.AST] = []
    classes: List[str] = []
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            functions.append(node)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            classes.append(node.name)
    return functions, sorted(classes)


def _imports(tree: ast.AST) -> List[str]:
    found: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.append(node.module or "")
    return sorted(set(x for x in found if x))


def _call_count(node: ast.AST) -> int:
    return sum(1 for child in ast.walk(node) if isinstance(child, ast.Call))


def _function_node(functions: Iterable[ast.AST], name: str) -> ast.AST:
    for node in functions:
        if getattr(node, "name", None) == name:
            return node
    raise HHSSemanticPluginAdapterError(f"function {name!r} is not present in source")


def _safe_docstring(node: ast.AST) -> str:
    doc = ast.get_docstring(node) or ""
    return doc.strip().splitlines()[0][:240] if doc else ""


def _source_summary(root: Path, rel_path: str, function_name: str) -> Dict[str, Any]:
    rel = rel_path.replace("\\", "/")
    path = (root / rel).resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(rel)
    if root not in path.parents and path != root:
        raise ValueError(f"path escapes repository root: {rel}")

    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=rel)
    functions, classes = _public_defs(tree)
    fn = _function_node(functions, function_name)
    arg_names = [arg.arg for arg in getattr(fn.args, "args", [])]
    source_contract = {
        "schema": "HHS_SEMANTIC_PLUGIN_SOURCE_SUMMARY_V1",
        "version": VERSION,
        "path": rel,
        "function": function_name,
        "function_args": arg_names,
        "function_arg_count": len(arg_names),
        "function_is_async": isinstance(fn, ast.AsyncFunctionDef),
        "function_docstring_head": _safe_docstring(fn),
        "function_ast_call_count": _call_count(fn),
        "public_function_count": len(functions),
        "public_class_count": len(classes),
        "imports": _imports(tree),
        "line_count": len(source.splitlines()),
        "execution_policy": "SEMANTIC_ADAPTER_EXECUTION_ONLY_NO_LEGACY_IMPORT",
    }
    source_contract["source_kernel_witness"] = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_semantic_plugin_adapter_source_summary_v1",
            _canonical(source_contract),
            width=72,
        ).to_dict()
    )
    return source_contract


def execute_semantic_plugin_adapter(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Execute the guarded semantic adapter for a planned plugin function.

    The adapter itself is live code. The target plugin is not imported or
    executed. The returned result is therefore safe to route through API/GUI as
    an adapter execution while preserving the no-bypass rule.
    """

    root_path = _repo_root(root)
    path = str(target.get("path") or "")
    function_name = str(target.get("function") or "")
    if not path or not function_name:
        raise HHSSemanticPluginAdapterError("target requires non-empty path and function")

    if bool(target.get("direct_execution_authorized", False)):
        raise HHSSemanticPluginAdapterError("direct legacy execution is not authorized by the semantic adapter runtime")

    plans = _plans_by_path(root_path, paths=plan_paths)
    plan = plans.get(path)
    if not plan:
        raise HHSSemanticPluginAdapterError(f"no capability plan found for {path}")
    fn_plan = None
    for fn in plan.get("public_functions", []):
        if fn.get("name") == function_name:
            fn_plan = dict(fn)
            break
    if fn_plan is None:
        raise HHSSemanticPluginAdapterError(f"no function plan found for {path}:{function_name}")

    invocation_record = execute_planned_plugin_invocation(
        {"path": path, "function": function_name, "payload": dict(target.get("payload") or {})},
        root=root_path,
        controller=controller,
        plan_paths=plan_paths,
    )
    source_summary = _source_summary(root_path, path, function_name)

    proposition_identity = make_proposition_identity(
        f"Semantic adapter execution preserves planned function identity for {path}:{function_name} without importing or executing legacy code.",
        source=f"hhs_semantic_plugin_adapter_runtime_v1.{path}.{function_name}",
        context={
            "path": path,
            "function": function_name,
            "adapter_type": fn_plan.get("required_adapter", "guarded_semantic_adapter"),
            "execution_policy": "SEMANTIC_ADAPTER_EXECUTION_ONLY_NO_LEGACY_IMPORT",
        },
    )

    semantic_adapter_result = {
        "schema": "HHS_SEMANTIC_PLUGIN_ADAPTER_RESULT_V1",
        "version": VERSION,
        "status": "SEMANTIC_ADAPTER_EXECUTED_NO_LEGACY_IMPORT",
        "path": path,
        "function": function_name,
        "adapter_type": fn_plan.get("required_adapter", "guarded_semantic_adapter"),
        "capabilities": list(plan.get("capabilities", [])),
        "risk_flags": list(plan.get("risk_flags", [])),
        "declared_inputs": dict(fn_plan.get("contract_inputs", {})),
        "source_summary": source_summary,
        "execution_boundary": {
            "direct_legacy_import": False,
            "executed_legacy_code": False,
            "adapter_live_execution": True,
            "closure_harness_required_before_direct_import": True,
        },
    }
    adapter_witness = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_semantic_plugin_adapter_execution_v1",
            _canonical(semantic_adapter_result),
            width=72,
        ).to_dict()
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="planned invocation to live semantic adapter result; legacy module remains non-imported and non-executed",
        reversible=True,
        receipt_hash72=adapter_witness.get("digest72") or adapter_witness.get("dna") or "",
    )

    contract_payload = {
        "schema": "HHS_SEMANTIC_PLUGIN_ADAPTER_EXECUTION_PAYLOAD_V1",
        "version": VERSION,
        "target": {"path": path, "function": function_name},
        "plan": plan,
        "function_plan": fn_plan,
        "source_summary": source_summary,
        "semantic_adapter_result": semantic_adapter_result,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness,
        "adapter_kernel_witness": adapter_witness,
    }
    execution_request = make_execution_request(
        source=f"hhs_semantic_plugin_adapter_runtime_v1.{path}",
        operation=f"semantic_plugin_adapter.execute::{function_name}",
        payload=contract_payload,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_semantic_plugin_adapter_runtime_v1.{path}.{function_name}",
        contract_payload,
    )
    assert_contract(runtime_packet, expected_type="runtime_packet")

    foundational_pre = assert_foundational_conformance(
        execution_request,
        source=f"hhs_semantic_plugin_adapter_runtime_v1.{path}.{function_name}.pre",
        require_receipt=False,
    ).to_dict()
    active_controller = controller or HHSRuntimeController()
    authorized_tick = active_controller.authorized_tick(
        source=f"hhs_semantic_plugin_adapter_runtime_v1.{path}.{function_name}"
    )
    foundational_post = assert_foundational_conformance(
        {
            "schema": "HHS_SEMANTIC_PLUGIN_ADAPTER_RESULT_AUDIT_V1",
            "payload": contract_payload,
            "result": semantic_adapter_result,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
        },
        source=f"hhs_semantic_plugin_adapter_runtime_v1.{path}.{function_name}.post",
        require_receipt=False,
    ).to_dict()

    ledger_payload = {
        "schema": "HHS_SEMANTIC_PLUGIN_ADAPTER_LEDGER_PAYLOAD_V1",
        "version": VERSION,
        "path": path,
        "function": function_name,
        "semantic_adapter_result": semantic_adapter_result,
        "adapter_kernel_witness": adapter_witness,
        "invocation_kernel_witness": invocation_record.get("invocation_kernel_witness", {}),
        "authorized_receipt": authorized_tick.get("receipt", {}),
        "foundational_conformance_pre": foundational_pre,
        "foundational_conformance_post": foundational_post,
    }
    ledger = append_payload(
        "SEMANTIC_PLUGIN_ADAPTER_EXECUTION",
        f"hhs_semantic_plugin_adapter_runtime_v1.{path}.{function_name}",
        ledger_payload,
    )

    return HHSSemanticAdapterExecution(
        path=path,
        function=function_name,
        adapter_type=str(fn_plan.get("required_adapter", "guarded_semantic_adapter")),
        execution_status="SEMANTIC_ADAPTER_EXECUTED_NO_LEGACY_IMPORT",
        direct_legacy_import=False,
        executed_legacy_code=False,
        source_summary=source_summary,
        semantic_adapter_result=semantic_adapter_result,
        invocation_record=invocation_record,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        adapter_kernel_witness=adapter_witness,
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


def build_semantic_plugin_adapter_execution_manifest(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    executions: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for target in list(targets or DEFAULT_SEMANTIC_ADAPTER_TARGETS):
        try:
            executions.append(execute_semantic_plugin_adapter(target, root=root_path, plan_paths=plan_paths))
        except Exception as exc:  # pragma: no cover - retained for auditability
            errors.append({"target": _canonical(target), "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "execution_count": len(executions),
        "error_count": len(errors),
        "execution_policy": "Live semantic adapter execution only; legacy/plugin imports and function bodies remain blocked.",
        "targets": [{"path": item.get("path"), "function": item.get("function")} for item in executions],
    }
    return {
        **payload,
        "executions": executions,
        "errors": errors,
        "ledger": verify_unified_ledger(),
        "hash72_kernel_witness": _with_digest72_alias(
            make_hash72_kernel_witness(
                "hhs_semantic_plugin_adapter_manifest_v1",
                _canonical(payload),
                width=72,
            ).to_dict()
        ),
    }


def write_semantic_plugin_adapter_execution_artifacts(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_semantic_plugin_adapter_execution_manifest(root_path, targets=targets, plan_paths=plan_paths)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Function | Adapter | Status | Witness |", "|---|---|---|---|---|"]
    for item in manifest.get("executions", []):
        witness = item.get("adapter_kernel_witness", {}).get("digest72", "")
        rows.append(
            "| `{}` | `{}` | `{}` | {} | `{}` |".format(
                item.get("path"),
                item.get("function"),
                item.get("adapter_type"),
                item.get("execution_status"),
                f"{witness[:18]}…" if witness else "—",
            )
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | See manifest. |")
    report = f"""# Semantic Plugin Adapter Runtime — Pass 026

## Purpose

Pass 026 is the first live semantic-adapter execution layer. It executes adapter logic around planned plugin functions while continuing to block direct legacy/plugin imports and function-body execution.

## Non-Bypass Policy

Every adapter execution passes through:

```text
capability plan validation
→ Pass 025 guarded invocation record
→ static source/function identity summary
→ canonical execution request
→ canonical runtime packet
→ HHS-M001..M007 foundational audits
→ authorized runtime tick
→ C u^72 Hash72 Digital DNA witness
→ unified Hash72 ledger append
```

The adapter returns `SEMANTIC_ADAPTER_EXECUTED_NO_LEGACY_IMPORT`. Candidate plugin code is still not imported or executed.

## Summary

```json
{json.dumps({k: manifest.get(k) for k in ['schema', 'version', 'execution_count', 'error_count', 'execution_policy']}, indent=2, sort_keys=True)}
```

## Executed Semantic Adapters

{chr(10).join(rows)}

## Manifest Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def semantic_plugin_adapter_runtime_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    targets = payload.get("targets") if payload else None
    plan_paths = payload.get("plan_paths") if payload else None
    manifest = write_semantic_plugin_adapter_execution_artifacts(root, targets=targets, plan_paths=plan_paths)
    ok = (
        manifest.get("schema") == SCHEMA
        and manifest.get("execution_count", 0) > 0
        and manifest.get("error_count") == 0
        and manifest.get("ledger", {}).get("ok")
    )
    return {
        "schema": "HHS_SEMANTIC_PLUGIN_ADAPTER_RUNTIME_SELF_TEST_V1",
        "ok": bool(ok),
        "execution_count": manifest.get("execution_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(semantic_plugin_adapter_runtime_self_test(), indent=2, sort_keys=True))

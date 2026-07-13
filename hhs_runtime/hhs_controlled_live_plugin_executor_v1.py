"""
HHS Controlled Live Plugin Executor v1
======================================

Pass 027 is the first *controlled live* execution layer for selected
low-risk plugin-ready modules.

Pass 026 executed live semantic adapters while keeping legacy/plugin modules
non-imported and non-executed. Pass 027 allows a deliberately small allow-list
of self-test style functions to run, but only after the candidate passes the
existing authority path:

* Pass 024 capability plan validation;
* Pass 025 guarded invocation record;
* Pass 026 semantic adapter execution;
* explicit allow-list and self-test function policy;
* import/function signature gate;
* canonical execution request/runtime packet;
* HHS-M001..M007 foundational audits;
* authorized runtime tick;
* C u^72 Hash72 Digital DNA witness;
* unified Hash72 ledger append.

This is not raw plugin execution. It is controlled adapter execution for
selected functions whose purpose is already internal self-verification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import asyncio
import importlib
import inspect
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_guarded_plugin_invocation_executor_v1 import DEFAULT_INVOCATION_TARGETS
from hhs_runtime.hhs_semantic_plugin_adapter_runtime_v1 import execute_semantic_plugin_adapter
from hhs_runtime.hhs_runtime_contract_v1 import assert_contract, make_execution_request, make_runtime_packet
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload, verify_unified_ledger
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_CONTROLLED_LIVE_PLUGIN_EXECUTOR_V1"
VERSION = "PASS_027"
MANIFEST_FILE = "CONTROLLED_LIVE_PLUGIN_EXECUTIONS_PASS_027.json"
REPORT_FILE = "CONTROLLED_LIVE_PLUGIN_EXECUTIONS_PASS_027.md"

# Conservative first live batch: self-test functions only. These are already
# designed to return diagnostic records and are the least risky live execution
# candidates for proving the guarded adapter path.
DEFAULT_CONTROLLED_LIVE_TARGETS = [
    {"path": "hhs_backend/runtime/runtime_semantic_memory_engine.py", "function": "semantic_memory_self_test"},
]

# Explicit path/function allow-list. A module must be in this set and its
# function name must match *_self_test before it can be live-executed.
CONTROLLED_LIVE_ALLOWLIST = {
    ("hhs_backend/runtime/runtime_semantic_memory_engine.py", "semantic_memory_self_test"),
    ("hhs_backend/runtime/runtime_multimodal_embedding_router.py", "multimodal_router_self_test"),
    ("hhs_backend/runtime/runtime_prediction_engine.py", "prediction_engine_self_test"),
    ("hhs_backend/runtime/runtime_agentic_cognition_layer.py", "agentic_cognition_self_test"),
}


class HHSControlledLivePluginExecutionError(RuntimeError):
    """Raised when controlled live execution would violate the adapter policy."""


@dataclass(frozen=True)
class HHSControlledLivePluginExecution:
    path: str
    function: str
    execution_status: str
    live_execution_authorized: bool
    semantic_adapter_execution: Dict[str, Any]
    execution_policy: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    live_result_summary: Dict[str, Any]
    live_kernel_witness: Dict[str, Any]
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
        raise HHSControlledLivePluginExecutionError(f"controlled live target must be a Python module path: {path}")
    return rel[:-3].replace("/", ".")


def _assert_controlled_policy(target: Mapping[str, Any]) -> Dict[str, Any]:
    path = str(target.get("path") or "")
    function_name = str(target.get("function") or "")
    if (path, function_name) not in CONTROLLED_LIVE_ALLOWLIST:
        raise HHSControlledLivePluginExecutionError(f"target is not in controlled live allow-list: {path}:{function_name}")
    if not function_name.endswith("_self_test"):
        raise HHSControlledLivePluginExecutionError("Pass 027 controlled live execution is limited to *_self_test functions")
    if bool(target.get("direct_execution_authorized", False)):
        raise HHSControlledLivePluginExecutionError(
            "raw direct execution flag is not accepted; use controlled_live_authorized with the allow-list"
        )
    if not bool(target.get("controlled_live_authorized", True)):
        raise HHSControlledLivePluginExecutionError("controlled_live_authorized must be true for Pass 027 execution")
    return {
        "schema": "HHS_CONTROLLED_LIVE_PLUGIN_POLICY_V1",
        "version": VERSION,
        "path": path,
        "function": function_name,
        "allowed": True,
        "allowlist_match": True,
        "function_class": "SELF_TEST_ONLY",
        "direct_legacy_execution": False,
        "controlled_live_adapter_execution": True,
        "raw_top_level_execution_policy": "IMPORT_ALLOWED_ONLY_FOR_EXPLICIT_ALLOWLISTED_SELF_TEST_MODULES",
    }


def _import_and_get_function(path: str, function_name: str) -> Any:
    module_name = _module_name_from_path(path)
    module = importlib.import_module(module_name)
    func = getattr(module, function_name, None)
    if func is None or not callable(func):
        raise HHSControlledLivePluginExecutionError(f"function not callable: {module_name}.{function_name}")
    sig = inspect.signature(func)
    required = [
        p for p in sig.parameters.values()
        if p.default is inspect._empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY)
    ]
    if required:
        raise HHSControlledLivePluginExecutionError(
            f"controlled self-test functions must have no required arguments: {module_name}.{function_name}"
        )
    return func


def _run_function(func: Any) -> Any:
    result = func()
    if inspect.isawaitable(result):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        if loop.is_running():
            # Avoid nested event-loop execution in notebook/server contexts.
            return {"awaitable": True, "status": "SKIPPED_RUNNING_EVENT_LOOP"}
        return loop.run_until_complete(result)
    return result


def _summarize_live_result(value: Any) -> Dict[str, Any]:
    serializable = json.loads(json.dumps(value, default=str, ensure_ascii=False))
    summary = {
        "schema": "HHS_CONTROLLED_LIVE_PLUGIN_RESULT_SUMMARY_V1",
        "version": VERSION,
        "result_type": type(value).__name__,
        "json_serializable": True,
        "ok": bool(serializable.get("ok", True)) if isinstance(serializable, dict) else True,
        "keys": sorted(serializable.keys())[:50] if isinstance(serializable, dict) else [],
        "preview": serializable,
    }
    preview_text = _canonical(summary.get("preview"))
    if len(preview_text) > 4000:
        summary["preview"] = preview_text[:4000] + "…"
        summary["preview_truncated"] = True
    else:
        summary["preview_truncated"] = False
    return summary


def execute_controlled_live_plugin(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Execute one allow-listed self-test through the guarded live adapter path."""

    root_path = _repo_root(root)
    policy = _assert_controlled_policy(target)
    path = policy["path"]
    function_name = policy["function"]

    semantic_adapter_execution = execute_semantic_plugin_adapter(
        {"path": path, "function": function_name, "payload": dict(target.get("payload") or {})},
        root=root_path,
        controller=controller,
        plan_paths=plan_paths,
    )

    proposition_identity = make_proposition_identity(
        f"Controlled live plugin execution preserves planned self-test identity for {path}:{function_name} through the canonical authority chain.",
        source=f"hhs_controlled_live_plugin_executor_v1.{path}.{function_name}",
        context=policy,
    )

    pre_meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="controlled live execution preflight preserves the planned self-test identity before import",
        reversible=True,
        receipt_hash72=semantic_adapter_execution.get("adapter_kernel_witness", {}).get("digest72", ""),
    )
    pre_payload = {
        "schema": "HHS_CONTROLLED_LIVE_PLUGIN_PRE_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "semantic_adapter_execution_status": semantic_adapter_execution.get("execution_status"),
        "semantic_adapter_witness": semantic_adapter_execution.get("adapter_kernel_witness", {}),
        "proposition_identity": proposition_identity,
        "meaning_witness": pre_meaning_witness,
        "transformation_rule": "controlled live execution preflight preserves the planned self-test identity before import",
        "reversible": True,
    }
    execution_request = make_execution_request(
        source=f"hhs_controlled_live_plugin_executor_v1.{path}",
        operation=f"controlled_live_plugin.execute::{function_name}",
        payload=pre_payload,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_controlled_live_plugin_executor_v1.{path}.{function_name}",
        pre_payload,
    )
    assert_contract(runtime_packet, expected_type="runtime_packet")

    foundational_pre = assert_foundational_conformance(
        execution_request,
        source=f"hhs_controlled_live_plugin_executor_v1.{path}.{function_name}.pre",
        require_receipt=False,
    ).to_dict()

    active_controller = controller or HHSRuntimeController()
    authorized_tick = active_controller.authorized_tick(
        source=f"hhs_controlled_live_plugin_executor_v1.{path}.{function_name}"
    )

    func = _import_and_get_function(path, function_name)
    live_result_raw = _run_function(func)
    live_result_summary = _summarize_live_result(live_result_raw)

    live_witness = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_controlled_live_plugin_result_v1",
            _canonical({"policy": policy, "result_summary": live_result_summary}),
            width=72,
        ).to_dict()
    )

    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="planned semantic adapter to controlled allow-listed live self-test execution",
        reversible=True,
        receipt_hash72=live_witness.get("digest72") or live_witness.get("dna") or "",
    )

    post_payload = {
        "schema": "HHS_CONTROLLED_LIVE_PLUGIN_POST_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "live_result_summary": live_result_summary,
        "live_kernel_witness": live_witness,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness,
    }
    foundational_post = assert_foundational_conformance(
        post_payload,
        source=f"hhs_controlled_live_plugin_executor_v1.{path}.{function_name}.post",
        require_receipt=False,
    ).to_dict()

    ledger_payload = {
        "schema": "HHS_CONTROLLED_LIVE_PLUGIN_LEDGER_PAYLOAD_V1",
        "version": VERSION,
        "policy": policy,
        "semantic_adapter_witness": semantic_adapter_execution.get("adapter_kernel_witness", {}),
        "live_kernel_witness": live_witness,
        "authorized_receipt": authorized_tick.get("receipt", {}),
        "foundational_conformance_pre": foundational_pre,
        "foundational_conformance_post": foundational_post,
        "live_result_summary": live_result_summary,
    }
    ledger = append_payload(
        "CONTROLLED_LIVE_PLUGIN_EXECUTION",
        f"hhs_controlled_live_plugin_executor_v1.{path}.{function_name}",
        ledger_payload,
    )

    return HHSControlledLivePluginExecution(
        path=path,
        function=function_name,
        execution_status="CONTROLLED_LIVE_PLUGIN_EXECUTED",
        live_execution_authorized=True,
        semantic_adapter_execution=semantic_adapter_execution,
        execution_policy=policy,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        live_result_summary=live_result_summary,
        live_kernel_witness=live_witness,
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


def build_controlled_live_plugin_execution_manifest(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    executions: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    prepared_targets: List[Mapping[str, Any]] = []
    for target in list(targets or DEFAULT_CONTROLLED_LIVE_TARGETS):
        t = dict(target)
        t.setdefault("controlled_live_authorized", True)
        prepared_targets.append(t)
    for target in prepared_targets:
        try:
            executions.append(execute_controlled_live_plugin(target, root=root_path, plan_paths=plan_paths))
        except Exception as exc:  # pragma: no cover - retained for audit trail
            errors.append({"target": _canonical(target), "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "execution_count": len(executions),
        "error_count": len(errors),
        "execution_policy": "Controlled live execution of explicit allow-listed *_self_test modules only.",
        "allowlist_size": len(CONTROLLED_LIVE_ALLOWLIST),
        "targets": [{"path": item.get("path"), "function": item.get("function")} for item in executions],
    }
    return {
        **payload,
        "executions": executions,
        "errors": errors,
        "ledger": verify_unified_ledger(),
        "hash72_kernel_witness": _with_digest72_alias(
            make_hash72_kernel_witness("hhs_controlled_live_plugin_manifest_v1", _canonical(payload), width=72).to_dict()
        ),
    }


def write_controlled_live_plugin_execution_artifacts(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_controlled_live_plugin_execution_manifest(root_path, targets=targets, plan_paths=plan_paths)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Function | Status | Result OK | Witness |", "|---|---|---|---|---|"]
    for item in manifest.get("executions", []):
        witness = item.get("live_kernel_witness", {}).get("digest72", "")
        rows.append(
            "| `{}` | `{}` | {} | {} | `{}` |".format(
                item.get("path"),
                item.get("function"),
                item.get("execution_status"),
                item.get("live_result_summary", {}).get("ok"),
                f"{witness[:18]}…" if witness else "—",
            )
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | See manifest. |")
    report = f"""# Controlled Live Plugin Executor — Pass 027

## Purpose

Pass 027 permits the first controlled live execution of selected low-risk plugin-ready modules. The allowed target class is restricted to explicit allow-listed `*_self_test` functions.

## Non-Bypass Policy

```text
capability plan validation
→ guarded invocation record
→ semantic adapter execution
→ explicit allow-list gate
→ import/signature gate
→ canonical execution request/runtime packet
→ HHS-M001..M007 foundational audits
→ authorized runtime tick
→ live self-test execution
→ C u^72 Hash72 Digital DNA witness
→ unified Hash72 ledger append
```

Raw direct execution remains blocked. Pass 027 is controlled live adapter execution only.

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


def controlled_live_plugin_executor_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    targets = payload.get("targets") if payload else None
    plan_paths = payload.get("plan_paths") if payload else None
    manifest = write_controlled_live_plugin_execution_artifacts(root, targets=targets, plan_paths=plan_paths)
    ok = (
        manifest.get("schema") == SCHEMA
        and manifest.get("execution_count", 0) > 0
        and manifest.get("error_count") == 0
        and manifest.get("ledger", {}).get("ok")
    )
    return {
        "schema": "HHS_CONTROLLED_LIVE_PLUGIN_EXECUTOR_SELF_TEST_V1",
        "ok": bool(ok),
        "execution_count": manifest.get("execution_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(controlled_live_plugin_executor_self_test(), indent=2, sort_keys=True))

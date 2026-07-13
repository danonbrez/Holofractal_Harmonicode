"""
HHS Read-Only Live Plugin Adapter v1
====================================

Pass 028 extends the controlled live plugin pathway from self-test-only
execution into read-only live adapter surfaces.

The adapter may import explicitly allow-listed modules and summarize their
runtime-visible surfaces, but it must not call arbitrary legacy/plugin
functions, mutate runtime state, write files outside pass artifacts, or bypass
canonical authority. Each read-only execution still emits:

* a canonical execution request;
* a canonical runtime packet;
* HHS-M001..M007 foundational audits;
* an authorized runtime tick;
* a C u^72 Hash72 Digital DNA kernel witness;
* a unified Hash72 ledger entry.

This pass is intentionally conservative: the default operation is module
introspection only. Function body execution remains limited to the Pass 027
controlled self-test executor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
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

SCHEMA = "HHS_READONLY_LIVE_PLUGIN_ADAPTER_V1"
VERSION = "PASS_028"
MANIFEST_FILE = "READONLY_LIVE_PLUGIN_ADAPTERS_PASS_028.json"
REPORT_FILE = "READONLY_LIVE_PLUGIN_ADAPTERS_PASS_028.md"

READONLY_MODE_MODULE_INTROSPECTION = "MODULE_INTROSPECTION"
READONLY_MODE_SELF_TEST_DELEGATE = "SELF_TEST_DELEGATE"

DEFAULT_READONLY_LIVE_TARGETS = [
    {"path": "hhs_backend/runtime/runtime_semantic_memory_engine.py", "mode": READONLY_MODE_MODULE_INTROSPECTION},
    {"path": "hhs_backend/runtime/runtime_multimodal_embedding_router.py", "mode": READONLY_MODE_MODULE_INTROSPECTION},
    {"path": "hhs_backend/runtime/runtime_prediction_engine.py", "mode": READONLY_MODE_MODULE_INTROSPECTION},
]

READONLY_LIVE_ALLOWLIST = {
    "hhs_backend/runtime/runtime_semantic_memory_engine.py",
    "hhs_backend/runtime/runtime_multimodal_embedding_router.py",
    "hhs_backend/runtime/runtime_prediction_engine.py",
    "hhs_backend/runtime/runtime_agentic_cognition_layer.py",
    "hhs_runtime/hhs_system_closure_harness_v1.py",
    "hhs_runtime/hhs_srcg_gate_v1.py",
    "hhs_runtime/hhs_hash72_kernel_authority_v1.py",
}


class HHSReadOnlyLivePluginAdapterError(RuntimeError):
    """Raised when a read-only live adapter request violates policy."""


@dataclass(frozen=True)
class HHSReadOnlyLiveAdapterExecution:
    path: str
    mode: str
    execution_status: str
    read_only_authorized: bool
    execution_policy: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    module_summary: Dict[str, Any]
    kernel_witness: Dict[str, Any]
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
        raise HHSReadOnlyLivePluginAdapterError(f"read-only live target must be a Python module path: {path}")
    return rel[:-3].replace("/", ".")


def _assert_readonly_policy(target: Mapping[str, Any]) -> Dict[str, Any]:
    path = str(target.get("path") or "")
    mode = str(target.get("mode") or READONLY_MODE_MODULE_INTROSPECTION)
    if path not in READONLY_LIVE_ALLOWLIST:
        raise HHSReadOnlyLivePluginAdapterError(f"target is not in read-only live allow-list: {path}")
    if mode not in {READONLY_MODE_MODULE_INTROSPECTION, READONLY_MODE_SELF_TEST_DELEGATE}:
        raise HHSReadOnlyLivePluginAdapterError(f"unsupported read-only adapter mode: {mode}")
    if bool(target.get("direct_execution_authorized", False)):
        raise HHSReadOnlyLivePluginAdapterError("direct legacy execution is not accepted by Pass 028")
    if bool(target.get("mutation_authorized", False)):
        raise HHSReadOnlyLivePluginAdapterError("mutation_authorized must remain false for read-only adapters")
    if not bool(target.get("read_only_live_authorized", True)):
        raise HHSReadOnlyLivePluginAdapterError("read_only_live_authorized must be true")
    return {
        "schema": "HHS_READONLY_LIVE_PLUGIN_POLICY_V1",
        "version": VERSION,
        "path": path,
        "mode": mode,
        "allowed": True,
        "allowlist_match": True,
        "direct_legacy_execution": False,
        "function_body_execution": mode == READONLY_MODE_SELF_TEST_DELEGATE,
        "mutation_allowed": False,
        "write_allowed": False,
        "network_allowed": False,
        "operation_class": "READ_ONLY_MODULE_SURFACE" if mode == READONLY_MODE_MODULE_INTROSPECTION else "DELEGATED_SELF_TEST_ONLY",
    }


def _summarize_module(path: str) -> Dict[str, Any]:
    module_name = _module_name_from_path(path)
    module = importlib.import_module(module_name)
    public_functions: List[Dict[str, Any]] = []
    public_classes: List[str] = []
    public_constants: List[str] = []
    for name, value in sorted(vars(module).items()):
        if name.startswith("_"):
            continue
        if inspect.isfunction(value) and getattr(value, "__module__", None) == module.__name__:
            try:
                signature = str(inspect.signature(value))
            except (TypeError, ValueError):
                signature = "<unavailable>"
            public_functions.append({
                "name": name,
                "signature": signature,
                "is_async": inspect.iscoroutinefunction(value),
                "doc": (inspect.getdoc(value) or "").splitlines()[:3],
            })
        elif inspect.isclass(value) and getattr(value, "__module__", None) == module.__name__:
            public_classes.append(name)
        elif name.isupper() and isinstance(value, (str, int, float, bool, tuple, list, dict, set, type(None))):
            public_constants.append(name)
    return {
        "schema": "HHS_READONLY_LIVE_MODULE_SUMMARY_V1",
        "version": VERSION,
        "module_name": module_name,
        "module_file": str(getattr(module, "__file__", "")),
        "doc": (inspect.getdoc(module) or "").splitlines()[:8],
        "public_function_count": len(public_functions),
        "public_class_count": len(public_classes),
        "public_constant_count": len(public_constants),
        "public_functions": public_functions[:80],
        "public_classes": public_classes[:80],
        "public_constants": public_constants[:80],
        "body_execution_performed": False,
        "mutation_performed": False,
    }


def execute_readonly_live_adapter(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
) -> Dict[str, Any]:
    """Execute a read-only live adapter against an explicit allow-listed module."""

    _repo_root(root)  # resolves root for parity with other pass adapters
    policy = _assert_readonly_policy(target)
    path = policy["path"]
    mode = policy["mode"]

    proposition_identity = make_proposition_identity(
        f"Read-only live plugin adapter preserves module identity for {path} without direct mutation or arbitrary function execution.",
        source=f"hhs_readonly_live_plugin_adapter_v1.{path}",
        context=policy,
    )
    meaning_witness_pre = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="read-only live adapter preflight preserves module surface identity before import/introspection",
        reversible=True,
        receipt_hash72="",
    )
    pre_payload = {
        "schema": "HHS_READONLY_LIVE_PLUGIN_PRE_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness_pre,
        "transformation_rule": "read-only module surface introspection only",
    }
    execution_request = make_execution_request(
        source=f"hhs_readonly_live_plugin_adapter_v1.{path}",
        operation=f"readonly_live_plugin.{mode.lower()}",
        payload=pre_payload,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet("INTERNAL", f"hhs_readonly_live_plugin_adapter_v1.{path}", pre_payload)
    assert_contract(runtime_packet, expected_type="runtime_packet")
    foundational_pre = assert_foundational_conformance(
        execution_request,
        source=f"hhs_readonly_live_plugin_adapter_v1.{path}.pre",
        require_receipt=False,
    ).to_dict()

    active_controller = controller or HHSRuntimeController()
    authorized_tick = active_controller.authorized_tick(source=f"hhs_readonly_live_plugin_adapter_v1.{path}")

    if mode == READONLY_MODE_SELF_TEST_DELEGATE:
        raise HHSReadOnlyLivePluginAdapterError(
            "SELF_TEST_DELEGATE is reserved for Pass 027 controlled_live_plugin_executor; Pass 028 defaults to module introspection."
        )
    module_summary = _summarize_module(path)

    kernel_witness = _with_digest72_alias(
        make_hash72_kernel_witness(
            "hhs_readonly_live_plugin_adapter_result_v1",
            _canonical({"policy": policy, "module_summary": module_summary}),
            width=72,
        ).to_dict()
    )
    meaning_witness_post = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="read-only live adapter imported the allow-listed module and inspected metadata without mutation",
        reversible=True,
        receipt_hash72=kernel_witness.get("digest72", ""),
    )
    post_payload = {
        "schema": "HHS_READONLY_LIVE_PLUGIN_POST_EXECUTION_V1",
        "version": VERSION,
        "policy": policy,
        "module_summary": module_summary,
        "kernel_witness": kernel_witness,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness_post,
    }
    foundational_post = assert_foundational_conformance(
        post_payload,
        source=f"hhs_readonly_live_plugin_adapter_v1.{path}.post",
        require_receipt=False,
    ).to_dict()

    ledger_payload = {
        "schema": "HHS_READONLY_LIVE_PLUGIN_LEDGER_PAYLOAD_V1",
        "version": VERSION,
        "policy": policy,
        "authorized_receipt": authorized_tick.get("receipt", {}),
        "kernel_witness": kernel_witness,
        "module_summary": module_summary,
        "foundational_conformance_pre": foundational_pre,
        "foundational_conformance_post": foundational_post,
    }
    ledger = append_payload("READONLY_LIVE_PLUGIN_ADAPTER", f"hhs_readonly_live_plugin_adapter_v1.{path}", ledger_payload)

    return HHSReadOnlyLiveAdapterExecution(
        path=path,
        mode=mode,
        execution_status="READONLY_LIVE_PLUGIN_ADAPTER_EXECUTED",
        read_only_authorized=True,
        execution_policy=policy,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        module_summary=module_summary,
        kernel_witness=kernel_witness,
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


def build_readonly_live_adapter_manifest(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    executions: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    prepared_targets: List[Mapping[str, Any]] = []
    for target in list(targets or DEFAULT_READONLY_LIVE_TARGETS):
        t = dict(target)
        t.setdefault("read_only_live_authorized", True)
        t.setdefault("mode", READONLY_MODE_MODULE_INTROSPECTION)
        prepared_targets.append(t)
    for target in prepared_targets:
        try:
            executions.append(execute_readonly_live_adapter(target, root=root_path))
        except Exception as exc:  # pragma: no cover - manifest keeps audit trail
            errors.append({"target": _canonical(target), "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "execution_count": len(executions),
        "error_count": len(errors),
        "execution_policy": "Read-only live import/introspection for explicit allow-listed modules only; no arbitrary function execution.",
        "allowlist_size": len(READONLY_LIVE_ALLOWLIST),
        "targets": [{"path": item.get("path"), "mode": item.get("mode")} for item in executions],
    }
    return {
        **payload,
        "executions": executions,
        "errors": errors,
        "ledger": verify_unified_ledger(),
        "hash72_kernel_witness": _with_digest72_alias(
            make_hash72_kernel_witness("hhs_readonly_live_plugin_manifest_v1", _canonical(payload), width=72).to_dict()
        ),
    }


def write_readonly_live_adapter_artifacts(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_readonly_live_adapter_manifest(root_path, targets=targets)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Mode | Status | Functions | Classes | Witness |", "|---|---|---|---:|---:|---|"]
    for item in manifest.get("executions", []):
        witness = item.get("kernel_witness", {}).get("digest72", "")
        summary = item.get("module_summary", {})
        rows.append(
            "| `{}` | `{}` | {} | {} | {} | `{}` |".format(
                item.get("path"),
                item.get("mode"),
                item.get("execution_status"),
                summary.get("public_function_count"),
                summary.get("public_class_count"),
                f"{witness[:18]}…" if witness else "—",
            )
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | — | See manifest. |")
    report = f"""# Read-Only Live Plugin Adapter — Pass 028

## Purpose

Pass 028 extends the plugin integration path from controlled self-test execution into read-only live adapter surfaces. It allows explicit allow-listed modules to be imported and introspected while still blocking arbitrary legacy function execution and mutation.

## Non-Bypass Policy

```text
explicit read-only allow-list
→ import/introspection only
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


def readonly_live_plugin_adapter_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    targets = payload.get("targets") if payload else None
    manifest = write_readonly_live_adapter_artifacts(root, targets=targets)
    ok = (
        manifest.get("schema") == SCHEMA
        and manifest.get("execution_count", 0) > 0
        and manifest.get("error_count") == 0
        and manifest.get("ledger", {}).get("ok")
    )
    return {
        "schema": "HHS_READONLY_LIVE_PLUGIN_ADAPTER_SELF_TEST_V1",
        "ok": bool(ok),
        "execution_count": manifest.get("execution_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(readonly_live_plugin_adapter_self_test(), indent=2, sort_keys=True))

"""
HHS Guarded Plugin Invocation Executor v1
=========================================

Pass 025 promotes Pass 024 safe invocation plans into guarded invocation
records without authorizing direct legacy/plugin execution yet.

This is a deliberate intermediate runtime layer:

* the executor validates a planned module/function against the capability plan;
* it creates canonical execution/runtime packets;
* it emits C u^72 Hash72 Digital DNA witnesses;
* it runs HHS-M001..HHS-M007 foundational audits;
* it records the invocation intent in the unified Hash72 ledger;
* it returns an explicit adapter result stating that no legacy code executed.

Live plugin execution remains blocked until a future semantic adapter declares
I/O schemas, closure behavior, rollback behavior, and closure-harness coverage.
This keeps the non-bypass rule intact while making planned capabilities
reachable through the validated runtime graph.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_plugin_capability_planner_v1 import (
    DEFAULT_CAPABILITY_PLAN_PATHS,
    build_plugin_capability_plan_manifest,
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

SCHEMA = "HHS_GUARDED_PLUGIN_INVOCATION_EXECUTOR_V1"
VERSION = "PASS_025"
MANIFEST_FILE = "GUARDED_PLUGIN_INVOCATIONS_PASS_025.json"
REPORT_FILE = "GUARDED_PLUGIN_INVOCATIONS_PASS_025.md"

DEFAULT_INVOCATION_TARGETS = [
    {"path": "hhs_backend/runtime/runtime_orchestrator.py", "function": "orchestrator_self_test"},
    {"path": "hhs_backend/runtime/runtime_semantic_memory_engine.py", "function": "semantic_memory_self_test"},
    {"path": "hhs_backend/runtime/runtime_multimodal_embedding_router.py", "function": "multimodal_router_self_test"},
    {"path": "hhs_backend/runtime/runtime_prediction_engine.py", "function": "prediction_engine_self_test"},
    {"path": "hhs_backend/runtime/runtime_agentic_cognition_layer.py", "function": "agentic_cognition_self_test"},
    {"path": "hhs_backend/runtime/runtime_autonomous_research_layer.py", "function": "autonomous_research_self_test"},
]


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


@dataclass(frozen=True)
class GuardedPluginInvocation:
    path: str
    function: str
    invocation_status: str
    execution_policy: str
    required_adapter: str
    direct_execution_authorized: bool
    payload_contract: Dict[str, Any]
    execution_request: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    authorized_tick: Dict[str, Any]
    invocation_kernel_witness: Dict[str, Any]
    foundational_conformance_pre: Dict[str, Any]
    foundational_conformance_post: Dict[str, Any]
    ledger: Dict[str, Any]
    adapter_result: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSGuardedPluginInvocationError(RuntimeError):
    """Raised when a plugin invocation attempt violates guarded planning."""


def _plans_by_path(root: Path, paths: Optional[Iterable[str]] = None) -> Dict[str, Dict[str, Any]]:
    manifest = build_plugin_capability_plan_manifest(root, paths=paths or DEFAULT_CAPABILITY_PLAN_PATHS)
    return {str(plan.get("path")): plan for plan in manifest.get("plans", [])}


def _function_plan(plan: Mapping[str, Any], function_name: str) -> Dict[str, Any]:
    for fn in plan.get("public_functions", []):
        if fn.get("name") == function_name:
            return dict(fn)
    available = [fn.get("name") for fn in plan.get("public_functions", [])]
    raise HHSGuardedPluginInvocationError(
        f"function {function_name!r} is not present in capability plan for {plan.get('path')}; available={available}"
    )


def execute_planned_plugin_invocation(
    target: Mapping[str, Any],
    *,
    root: Optional[str | Path] = None,
    controller: Optional[HHSRuntimeController] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """Create a guarded invocation record for one planned function.

    This function intentionally does not import or execute the target module.
    It executes the *invocation authority path*: plan validation, contract
    emission, u^72 witness, foundational audit, authorized tick, and ledger
    append. A future semantic adapter can replace the adapter_result body while
    preserving this authority envelope.
    """

    root_path = _repo_root(root)
    path = str(target.get("path") or "")
    function_name = str(target.get("function") or "")
    if not path or not function_name:
        raise HHSGuardedPluginInvocationError("target requires non-empty path and function")

    plan = _plans_by_path(root_path, paths=plan_paths).get(path)
    if not plan:
        raise HHSGuardedPluginInvocationError(f"no capability plan found for {path}")
    fn_plan = _function_plan(plan, function_name)

    direct_authorized = bool(target.get("direct_execution_authorized", False))
    if direct_authorized:
        raise HHSGuardedPluginInvocationError(
            "direct plugin execution is not authorized in Pass 025; declare a dedicated semantic adapter first"
        )

    invocation_payload = {
        "schema": "HHS_GUARDED_PLUGIN_INVOCATION_PAYLOAD_V1",
        "version": VERSION,
        "path": path,
        "function": function_name,
        "payload": dict(target.get("payload") or {}),
        "capabilities": list(plan.get("capabilities", [])),
        "risk_flags": list(plan.get("risk_flags", [])),
        "function_plan": fn_plan,
        "source_plan_witness": plan.get("plan_kernel_witness", {}),
        "direct_execution_authorized": False,
        "execution_policy": "GUARDED_PLAN_EXECUTION_ONLY_NO_LEGACY_IMPORT",
    }
    invocation_witness = _with_digest72_alias(make_hash72_kernel_witness(
        "hhs_guarded_plugin_invocation_v1",
        _canonical(invocation_payload),
        width=72,
    ).to_dict())

    proposition_identity = make_proposition_identity(
        f"Guarded invocation preserves planned function identity for {path}:{function_name} without executing legacy code.",
        source=f"hhs_guarded_plugin_invocation_executor_v1.{path}.{function_name}",
        context={"path": path, "function": function_name, "execution_policy": invocation_payload["execution_policy"]},
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="capability plan to guarded invocation receipt; no direct legacy import or execution",
        reversible=True,
        receipt_hash72=invocation_witness.get("digest72") or invocation_witness.get("dna") or "",
    )

    payload_contract = {
        **invocation_payload,
        "proposition_identity": proposition_identity,
        "meaning_witness": meaning_witness,
        "invocation_kernel_witness": invocation_witness,
    }
    execution_request = make_execution_request(
        source=f"hhs_guarded_plugin_invocation_executor_v1.{path}",
        operation=f"plugin.invoke_plan::{function_name}",
        payload=payload_contract,
        requires_authority=True,
    )
    assert_contract(execution_request, expected_type="execution_request")
    runtime_packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_guarded_plugin_invocation_executor_v1.{path}.{function_name}",
        payload_contract,
    )
    assert_contract(runtime_packet, expected_type="runtime_packet")

    foundational_pre = assert_foundational_conformance(
        execution_request,
        source=f"hhs_guarded_plugin_invocation_executor_v1.{path}.{function_name}.pre",
        require_receipt=False,
    ).to_dict()

    active_controller = controller or HHSRuntimeController()
    authorized_tick = active_controller.authorized_tick(
        source=f"hhs_guarded_plugin_invocation_executor_v1.{path}.{function_name}"
    )

    adapter_result = {
        "schema": "HHS_GUARDED_PLUGIN_ADAPTER_RESULT_V1",
        "status": "GUARDED_INVOCATION_ACCEPTED_PLAN_ONLY",
        "executed_legacy_code": False,
        "path": path,
        "function": function_name,
        "required_adapter": fn_plan.get("required_adapter", "guarded_semantic_adapter"),
        "next_action": "bind dedicated semantic adapter before live module execution",
        "closure_harness_required": True,
        "hash72_kernel_witness": invocation_witness,
    }
    foundational_post = assert_foundational_conformance(
        {
            "schema": "HHS_GUARDED_PLUGIN_INVOCATION_RESULT_AUDIT_V1",
            "payload_contract": payload_contract,
            "adapter_result": adapter_result,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
        },
        source=f"hhs_guarded_plugin_invocation_executor_v1.{path}.{function_name}.post",
        require_receipt=False,
    ).to_dict()

    ledger_payload = {
        "schema": "HHS_GUARDED_PLUGIN_INVOCATION_LEDGER_PAYLOAD_V1",
        "version": VERSION,
        "payload_contract": payload_contract,
        "execution_request": execution_request,
        "runtime_packet": runtime_packet,
        "authorized_tick": authorized_tick,
        "adapter_result": adapter_result,
        "foundational_conformance_pre": foundational_pre,
        "foundational_conformance_post": foundational_post,
    }
    ledger = append_payload(
        "PLUGIN_INVOCATION_PLAN",
        f"hhs_guarded_plugin_invocation_executor_v1.{path}.{function_name}",
        ledger_payload,
    )

    return GuardedPluginInvocation(
        path=path,
        function=function_name,
        invocation_status="WIRED_GUARDED_INVOCATION_PLAN",
        execution_policy="guarded plan execution only; no legacy import/execution until semantic adapter is declared",
        required_adapter=str(fn_plan.get("required_adapter", "guarded_semantic_adapter")),
        direct_execution_authorized=False,
        payload_contract=payload_contract,
        execution_request=execution_request,
        runtime_packet=runtime_packet,
        authorized_tick=authorized_tick,
        invocation_kernel_witness=invocation_witness,
        foundational_conformance_pre=foundational_pre,
        foundational_conformance_post=foundational_post,
        ledger=ledger,
        adapter_result=adapter_result,
    ).to_dict()


def build_guarded_plugin_invocation_manifest(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    invocations: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for target in list(targets or DEFAULT_INVOCATION_TARGETS):
        try:
            invocations.append(execute_planned_plugin_invocation(target, root=root_path, plan_paths=plan_paths))
        except Exception as exc:  # pragma: no cover - retained in manifest for auditability
            errors.append({"target": _canonical(target), "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "invocation_count": len(invocations),
        "error_count": len(errors),
        "execution_policy": "Guarded invocation executes authority path only; legacy/plugin code remains blocked pending semantic adapters.",
        "targets": [{"path": item.get("path"), "function": item.get("function")} for item in invocations],
    }
    return {
        **payload,
        "invocations": invocations,
        "errors": errors,
        "ledger": verify_unified_ledger(),
        "hash72_kernel_witness": _with_digest72_alias(make_hash72_kernel_witness(
            "hhs_guarded_plugin_invocation_manifest_v1",
            _canonical(payload),
            width=72,
        ).to_dict()),
    }


def write_guarded_plugin_invocation_artifacts(
    root: Optional[str | Path] = None,
    targets: Optional[Iterable[Mapping[str, Any]]] = None,
    plan_paths: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_guarded_plugin_invocation_manifest(root_path, targets=targets, plan_paths=plan_paths)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Function | Adapter | Status | Witness |", "|---|---|---|---|---|"]
    for item in manifest.get("invocations", []):
        witness = item.get("invocation_kernel_witness", {}).get("digest72", "")
        rows.append(
            "| `{}` | `{}` | `{}` | {} | `{}` |".format(
                item.get("path"),
                item.get("function"),
                item.get("required_adapter"),
                item.get("adapter_result", {}).get("status"),
                f"{witness[:18]}…" if witness else "—",
            )
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | See manifest. |")
    report = f"""# Guarded Plugin Invocation Executor — Pass 025

## Purpose

Pass 025 converts Pass 024 safe invocation plans into guarded invocation records. It makes selected planned functions reachable through the validated authority graph while still blocking direct legacy/plugin execution.

## Non-Bypass Policy

Every invocation record passes through:

```text
capability plan validation
→ canonical execution request
→ canonical runtime packet
→ HHS-M001..M007 foundational audit
→ authorized runtime tick
→ C u^72 Hash72 Digital DNA witness
→ unified Hash72 ledger append
```

No plugin module is imported or executed in this pass. The adapter result is intentionally `GUARDED_INVOCATION_ACCEPTED_PLAN_ONLY`.

## Summary

```json
{json.dumps({k: manifest.get(k) for k in ['schema', 'version', 'invocation_count', 'error_count', 'execution_policy']}, indent=2, sort_keys=True)}
```

## Guarded Invocation Targets

{chr(10).join(rows)}

## Manifest Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def guarded_plugin_invocation_executor_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    targets = payload.get("targets") if payload else None
    plan_paths = payload.get("plan_paths") if payload else None
    manifest = write_guarded_plugin_invocation_artifacts(root, targets=targets, plan_paths=plan_paths)
    ok = manifest.get("schema") == SCHEMA and manifest.get("invocation_count", 0) > 0 and manifest.get("error_count") == 0 and manifest.get("ledger", {}).get("ok")
    return {
        "schema": "HHS_GUARDED_PLUGIN_INVOCATION_EXECUTOR_SELF_TEST_V1",
        "ok": bool(ok),
        "invocation_count": manifest.get("invocation_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "ledger": manifest.get("ledger"),
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(guarded_plugin_invocation_executor_self_test(), indent=2, sort_keys=True))

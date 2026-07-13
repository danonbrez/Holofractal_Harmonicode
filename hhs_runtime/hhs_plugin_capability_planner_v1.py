
"""
HHS Plugin Capability Planner v1
================================

Pass 024 turns guarded static adapters into actionable integration plans without
executing legacy/plugin-ready code. The planner statically inspects selected
modules, declares their capability metadata, generates safe invocation plans,
and emits C u^72 Hash72 kernel witnesses for every plan.

This is deliberately a planning surface, not a live adapter. It preserves the
non-bypass rule: candidate functions are not imported, called, or allowed to
read/write runtime state until a future semantic adapter explicitly binds them
to the canonical runtime contract, Hash72/u^72 authority, foundational audits,
and closure harness coverage.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import ast
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import make_runtime_packet, assert_contract
from hhs_foundation.hhs_foundational_standards_v1 import (
    assert_foundational_conformance,
    make_meaning_witness,
    make_proposition_identity,
)

SCHEMA = "HHS_PLUGIN_CAPABILITY_PLANNER_V1"
VERSION = "PASS_024"
MANIFEST_FILE = "PLUGIN_CAPABILITY_PLANS_PASS_024.json"
REPORT_FILE = "PLUGIN_CAPABILITY_PLANS_PASS_024.md"

# Second guarded batch: runtime/AI/database/API modules where invocation planning
# gives the highest release leverage while still avoiding direct execution.
DEFAULT_CAPABILITY_PLAN_PATHS = [
    "hhs_backend/runtime/runtime_orchestrator.py",
    "hhs_backend/runtime/runtime_semantic_memory_engine.py",
    "hhs_backend/runtime/runtime_multimodal_embedding_router.py",
    "hhs_backend/runtime/runtime_prediction_engine.py",
    "hhs_backend/runtime/runtime_agentic_cognition_layer.py",
    "hhs_backend/runtime/runtime_autonomous_research_layer.py",
    "hhs_backend/runtime/runtime_adaptive_goal_engine.py",
    "hhs_backend/runtime/runtime_graph_projection.py",
    "hhs_backend/runtime/runtime_receipt_chain.py",
    "hhs_backend/runtime/runtime_transport_protocol.py",
    "hhs_backend/runtime/runtime_replay_engine.py",
    "hhs_backend/runtime/runtime_snapshot_codec.py",
    "hhs_backend/runtime/runtime_rehydration_engine.py",
    "hhs_backend/runtime/runtime_recursive_toolchain_layer.py",
    "hhs_backend/runtime/runtime_self_modification_governor.py",
    "hhs_backend/runtime/runtime_multinode_goal_consensus.py",
    "hhs_backend/runtime/runtime_server.py",
    "hhs_backend/runtime/runtime_ws.py",
    "hhs_backend/runtime/distributed_runtime_node_v1.py",
    "hhs_backend/runtime/distributed_consensus_runtime.py",
    "hhs_backend/websocket/runtime_stream_manager.py",
    "hhs_backend/api/runtime_routes.py",
    "hhs_runtime/hhs_cross_modal_action_planner_v1.py",
    "hhs_runtime/hhs_multimodal_file_tokenizer_db_v1.py",
]

CAPABILITY_KEYWORDS = {
    "semantic_memory": ("semantic", "memory", "embedding", "vector", "wordnet"),
    "runtime_orchestration": ("orchestrator", "transport", "server", "ws", "websocket", "event"),
    "prediction_ai": ("prediction", "agentic", "autonomous", "goal", "planning", "consensus"),
    "replay_persistence": ("receipt", "replay", "snapshot", "rehydration", "chain"),
    "graph_projection": ("graph", "projection", "topology"),
    "security_governance": ("governor", "self_modification", "authority", "guard", "consensus"),
    "multimodal_ingestion": ("multimodal", "file", "tokenizer", "audio", "modal"),
    "api_surface": ("api", "route", "endpoint", "server"),
}

RISK_KEYWORDS = {
    "filesystem": ("open", "Path", "read_text", "write_text", "json.dump", "json.load"),
    "network": ("requests", "socket", "websocket", "FastAPI", "APIRouter"),
    "process": ("subprocess", "os.system", "exec", "eval"),
    "state_mutation": ("append", "write", "save", "delete", "remove", "update"),
    "model_inference": ("predict", "infer", "embedding", "model", "agent"),
}


@dataclass(frozen=True)
class FunctionPlan:
    name: str
    args: List[str]
    arg_count: int
    is_async: bool
    invocation_policy: str
    required_adapter: str
    contract_inputs: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapabilityPlan:
    path: str
    adapter_status: str
    capabilities: List[str]
    risk_flags: List[str]
    public_functions: List[FunctionPlan]
    public_classes: List[str]
    import_count: int
    line_count: int
    execution_policy: str
    safe_invocation_plan: Dict[str, Any]
    source_kernel_witness: Dict[str, Any]
    plan_kernel_witness: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    foundational_audit: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["public_functions"] = [item.to_dict() if hasattr(item, "to_dict") else item for item in self.public_functions]
        return data


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _with_digest72_alias(witness: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


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


def _node_names(tree: ast.AST) -> List[str]:
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
    return names


def _infer_capabilities(path: str, imports: Iterable[str], public_names: Iterable[str], source_names: Iterable[str]) -> List[str]:
    haystack = " ".join([path, *imports, *public_names, *source_names]).lower()
    capabilities = [cap for cap, keys in CAPABILITY_KEYWORDS.items() if any(key.lower() in haystack for key in keys)]
    return sorted(set(capabilities or ["runtime_plugin_candidate"]))


def _infer_risks(imports: Iterable[str], source_names: Iterable[str]) -> List[str]:
    haystack = " ".join([*imports, *source_names]).lower()
    risks = [risk for risk, keys in RISK_KEYWORDS.items() if any(key.lower() in haystack for key in keys)]
    return sorted(set(risks))


def _function_plan(node: ast.AST) -> FunctionPlan:
    assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    args = [arg.arg for arg in getattr(node.args, "args", [])]
    # Default to plan-only. The function is not directly callable until a
    # semantic adapter declares payload schema, authority, and closure behavior.
    required_adapter = "guarded_semantic_adapter"
    if node.name.endswith("self_test") or node.name.endswith("_self_test"):
        required_adapter = "guarded_self_test_adapter"
    elif "route" in node.name or "api" in node.name:
        required_adapter = "canonical_api_adapter"
    elif node.name.startswith(("predict", "infer", "embed", "search", "query")):
        required_adapter = "semantic_memory_vector_adapter"
    elif node.name.startswith(("save", "load", "write", "read", "export")):
        required_adapter = "persistence_guard_adapter"
    return FunctionPlan(
        name=node.name,
        args=args,
        arg_count=len(args),
        is_async=isinstance(node, ast.AsyncFunctionDef),
        invocation_policy="PLAN_ONLY_NO_DIRECT_EXECUTION",
        required_adapter=required_adapter,
        contract_inputs={arg: "declared-by-future-semantic-adapter" for arg in args},
    )


def inspect_capability_plan(root: Optional[str | Path], rel_path: str) -> CapabilityPlan:
    root_path = _repo_root(root)
    rel = rel_path.replace("\\", "/")
    path = (root_path / rel).resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(rel)
    if root_path not in path.parents and path != root_path:
        raise ValueError(f"path escapes repository root: {rel}")

    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=rel)
    functions, public_classes = _public_defs(tree)
    imports = _imports(tree)
    source_names = _node_names(tree)
    function_plans = [_function_plan(fn) for fn in functions]
    public_function_names = [fn.name for fn in function_plans]
    capabilities = _infer_capabilities(rel, imports, public_function_names, source_names)
    risks = _infer_risks(imports, source_names)

    source_contract = {
        "schema": "HHS_PLUGIN_CAPABILITY_SOURCE_CONTRACT_V1",
        "version": VERSION,
        "path": rel,
        "line_count": len(source.splitlines()),
        "public_functions": public_function_names,
        "public_classes": public_classes,
        "imports": imports,
        "execution_policy": "PLAN_ONLY_NO_DIRECT_EXECUTION",
    }
    source_witness = _with_digest72_alias(make_hash72_kernel_witness(
        "hhs_plugin_capability_source_v1",
        json.dumps(source_contract, sort_keys=True, ensure_ascii=False),
        width=72,
    ).to_dict())
    safe_invocation_plan = {
        "schema": "HHS_SAFE_INVOCATION_PLAN_V1",
        "path": rel,
        "direct_execution_authorized": False,
        "required_runtime_path": [
            "canonical_runtime_contract",
            "HHS_FOUNDATIONAL_STANDARDS",
            "Hash72_u72_kernel_witness",
            "guarded_service_registry",
            "closure_harness_coverage",
        ],
        "candidate_function_count": len(function_plans),
        "risk_flags": risks,
        "capabilities": capabilities,
        "next_action": "declare semantic adapter before live execution",
    }
    plan_witness = _with_digest72_alias(make_hash72_kernel_witness(
        "hhs_plugin_capability_plan_v1",
        json.dumps(safe_invocation_plan, sort_keys=True, ensure_ascii=False),
        width=72,
    ).to_dict())
    packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_plugin_capability_planner_v1.{rel}",
        {
            "source_contract": source_contract,
            "safe_invocation_plan": safe_invocation_plan,
            "source_kernel_witness": source_witness,
            "plan_kernel_witness": plan_witness,
        },
    )
    assert_contract(packet, expected_type="runtime_packet")
    proposition_identity = make_proposition_identity(
        f"Capability plan preserves source identity for {rel} and forbids direct plugin execution.",
        source=f"hhs_plugin_capability_planner_v1.{rel}",
        context={"path": rel, "capabilities": capabilities, "risk_flags": risks},
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="static AST capability planning to guarded invocation plan; no live plugin execution",
        reversible=True,
        receipt_hash72=plan_witness.get("digest72") or plan_witness.get("dna") or "",
    )
    audit = assert_foundational_conformance(
        {
            "schema": "HHS_PLUGIN_CAPABILITY_FOUNDATIONAL_AUDIT_V1",
            "path": rel,
            "source_contract": source_contract,
            "safe_invocation_plan": safe_invocation_plan,
            "source_kernel_witness": source_witness,
            "plan_kernel_witness": plan_witness,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
            "reversible": True,
            "transformation_rule": "static AST capability planning to guarded invocation plan; no live plugin execution",
        },
        source=f"hhs_plugin_capability_planner_v1.{rel}",
        require_receipt=False,
    ).to_dict()
    return CapabilityPlan(
        path=rel,
        adapter_status="WIRED_CAPABILITY_PLAN_ONLY",
        capabilities=capabilities,
        risk_flags=risks,
        public_functions=function_plans,
        public_classes=public_classes,
        import_count=len(imports),
        line_count=len(source.splitlines()),
        execution_policy="plan/introspection only; direct execution blocked until dedicated semantic adapter exists",
        safe_invocation_plan=safe_invocation_plan,
        source_kernel_witness=source_witness,
        plan_kernel_witness=plan_witness,
        runtime_packet=packet,
        foundational_audit=audit,
    )


def build_plugin_capability_plan_manifest(root: Optional[str | Path] = None, paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    plan_paths = list(paths or DEFAULT_CAPABILITY_PLAN_PATHS)
    plans: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for rel in plan_paths:
        try:
            plans.append(inspect_capability_plan(root_path, rel).to_dict())
        except Exception as exc:  # pragma: no cover - report instead of hiding failures
            errors.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
    capability_counts: Dict[str, int] = {}
    risk_counts: Dict[str, int] = {}
    for plan in plans:
        for capability in plan.get("capabilities", []):
            capability_counts[capability] = capability_counts.get(capability, 0) + 1
        for risk in plan.get("risk_flags", []):
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "plan_count": len(plans),
        "error_count": len(errors),
        "capability_counts": dict(sorted(capability_counts.items())),
        "risk_counts": dict(sorted(risk_counts.items())),
        "execution_policy": "Capability plans are guarded metadata only; no plugin code is imported or executed.",
    }
    return {
        **payload,
        "plans": plans,
        "errors": errors,
        "hash72_kernel_witness": _with_digest72_alias(make_hash72_kernel_witness(
            "hhs_plugin_capability_plans_manifest_v1",
            json.dumps(payload, sort_keys=True, ensure_ascii=False),
            width=72,
        ).to_dict()),
    }


def write_plugin_capability_plan_artifacts(root: Optional[str | Path] = None, paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_plugin_capability_plan_manifest(root_path, paths=paths)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Capabilities | Risks | Functions | Classes | Plan Witness |", "|---|---|---|---:|---:|---|"]
    for plan in manifest.get("plans", []):
        witness = plan.get("plan_kernel_witness", {}).get("digest72", "")
        rows.append(
            "| `{}` | {} | {} | {} | {} | `{}` |".format(
                plan.get("path"),
                ", ".join(plan.get("capabilities", [])) or "—",
                ", ".join(plan.get("risk_flags", [])) or "—",
                len(plan.get("public_functions", [])),
                len(plan.get("public_classes", [])),
                f"{witness[:18]}…" if witness else "—",
            )
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | — | See manifest. |")
    report = f"""# Plugin Capability Plans — Pass 024

## Purpose

Pass 024 upgrades guarded plugin reachability from static source cataloging to safe invocation planning. The planner still never imports or executes plugin-ready modules. It records module capabilities, risk flags, candidate function adapters, C `u^72` Hash72 witnesses, runtime packets, and foundational audits.

## Policy

Every planned module remains blocked from live execution until a dedicated semantic adapter declares input/output contracts, authority requirements, closure behavior, and closure-harness coverage.

## Summary

```json
{json.dumps({k: manifest.get(k) for k in ['schema', 'version', 'plan_count', 'error_count', 'capability_counts', 'risk_counts', 'execution_policy']}, indent=2, sort_keys=True)}
```

## Planned Modules

{chr(10).join(rows)}

## Kernel Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def plugin_capability_planner_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    paths = payload.get("paths") if payload else None
    manifest = write_plugin_capability_plan_artifacts(root, paths=paths)
    ok = manifest.get("schema") == SCHEMA and manifest.get("plan_count", 0) > 0 and manifest.get("error_count") == 0
    return {
        "schema": "HHS_PLUGIN_CAPABILITY_PLANNER_SELF_TEST_V1",
        "ok": ok,
        "plan_count": manifest.get("plan_count"),
        "error_count": manifest.get("error_count"),
        "capability_counts": manifest.get("capability_counts"),
        "risk_counts": manifest.get("risk_counts"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(plugin_capability_planner_self_test(), indent=2, sort_keys=True))

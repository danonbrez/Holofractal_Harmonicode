"""
HHS Guarded Plugin Adapters v1
==============================

Pass 023 begins reducing the PLUGIN_READY frontier by creating guarded,
non-executing adapters for high-value legacy/runtime modules. The adapter layer
is intentionally conservative: it does not import candidate modules and does not
execute their top-level code. It statically inspects source with AST, emits a
C u^72 Hash72 kernel witness for the source contract, and makes the module
reachable through the guarded service registry.

This turns selected legacy sources from silent plugin-ready files into explicit,
receipt-backed runtime catalog services while preserving the no-bypass rule:
modules still require a dedicated semantic adapter before their functions may be
executed as live runtime instructions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import ast
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_contract_v1 import make_runtime_packet, assert_contract
from hhs_foundation.hhs_foundational_standards_v1 import assert_foundational_conformance, make_proposition_identity, make_meaning_witness

SCHEMA = "HHS_GUARDED_PLUGIN_ADAPTERS_V1"
VERSION = "PASS_023"
MANIFEST_FILE = "GUARDED_PLUGIN_ADAPTERS_PASS_023.json"
REPORT_FILE = "GUARDED_PLUGIN_ADAPTERS_PASS_023.md"

# First guarded adapter batch: high-value legacy/AI/database/symbolic modules.
DEFAULT_ADAPTER_PATHS = [
    "harmonicode_verbatim_semantic_database_v1.py",
    "harmonicode_modality_verbatim_ingestion_v1-1.py",
    "hhs_database_integration_layer_v1.py",
    "hhs_self_solving_constraint_modules_v1.py",
    "hhs_self_solving_constraint_pipeline_v1.py",
    "hhs_runtime/hhs_symbolic_reasoning_engine_v1.py",
    "hhs_runtime/hhs_symbolic_quantum_algebra_v1.py",
    "hhs_runtime/hhs_text_semantic_reconstruction_v1.py",
    "hhs_runtime/hhs_wordnet_relation_enforcer_v1.py",
    "hhs_runtime/hhs_receipt_vector_index_v1.py",
    "hhs_runtime/hhs_recursive_symbol_kernel_v1.py",
    "hhs_runtime/hhs_recursive_global_constraint_bundle_v1.py",
]


@dataclass(frozen=True)
class GuardedPluginAdapter:
    path: str
    adapter_status: str
    execution_policy: str
    public_functions: List[str]
    public_classes: List[str]
    imports: List[str]
    line_count: int
    source_kernel_witness: Dict[str, Any]
    runtime_packet: Dict[str, Any]
    foundational_audit: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[str | Path] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _with_digest72_alias(witness: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(witness)
    data.setdefault("digest72", data.get("digest") or data.get("dna") or "")
    data.setdefault("authority", "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1")
    return data


def _name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _imports(tree: ast.AST) -> List[str]:
    found: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            found.append(mod)
    return sorted(set(x for x in found if x))


def _public_defs(tree: ast.AST) -> tuple[List[str], List[str]]:
    functions: List[str] = []
    classes: List[str] = []
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            classes.append(node.name)
    return sorted(functions), sorted(classes)


def inspect_plugin_source(root: Optional[str | Path], rel_path: str) -> GuardedPluginAdapter:
    root_path = _repo_root(root)
    rel = rel_path.replace("\\", "/")
    path = (root_path / rel).resolve()
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(rel)
    if root_path not in path.parents and path != root_path:
        raise ValueError(f"path escapes repository root: {rel}")

    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=rel)
    public_functions, public_classes = _public_defs(tree)
    import_names = _imports(tree)
    source_contract = {
        "schema": "HHS_GUARDED_PLUGIN_SOURCE_CONTRACT_V1",
        "version": VERSION,
        "path": rel,
        "public_functions": public_functions,
        "public_classes": public_classes,
        "imports": import_names,
        "line_count": len(source.splitlines()),
        "execution_policy": "STATIC_ADAPTER_ONLY_NO_DIRECT_EXECUTION",
    }
    witness = _with_digest72_alias(make_hash72_kernel_witness(
        "hhs_guarded_plugin_adapter_source_v1",
        json.dumps(source_contract, sort_keys=True, ensure_ascii=False),
        width=72,
    ).to_dict())
    packet = make_runtime_packet(
        "INTERNAL",
        f"hhs_guarded_plugin_adapters_v1.{rel}",
        {"source_contract": source_contract, "hash72_kernel_witness": witness},
    )
    assert_contract(packet, expected_type="runtime_packet")
    proposition_identity = make_proposition_identity(
        f"Guarded static adapter preserves source identity for {rel} without executing legacy module code.",
        source=f"hhs_guarded_plugin_adapters_v1.{rel}",
        context={"path": rel, "execution_policy": source_contract["execution_policy"]},
    )
    meaning_witness = make_meaning_witness(
        proposition_identity,
        proposition_identity,
        transformation_rule="static AST source inspection to guarded adapter contract; no live legacy execution",
        reversible=True,
        receipt_hash72=witness.get("digest72") or witness.get("dna") or "",
    )
    audit = assert_foundational_conformance(
        {
            "schema": "HHS_GUARDED_PLUGIN_ADAPTER_FOUNDATIONAL_AUDIT_V1",
            "path": rel,
            "source_contract": source_contract,
            "hash72_kernel_witness": witness,
            "proposition_identity": proposition_identity,
            "meaning_witness": meaning_witness,
            "transformation_rule": "static AST source inspection to guarded adapter contract; no live legacy execution",
            "reversible": True,
        },
        source=f"hhs_guarded_plugin_adapters_v1.{rel}",
        require_receipt=False,
    ).to_dict()
    return GuardedPluginAdapter(
        path=rel,
        adapter_status="WIRED_STATIC_GUARDED_ADAPTER",
        execution_policy="catalog/introspection only; live function execution requires a dedicated guarded semantic adapter",
        public_functions=public_functions,
        public_classes=public_classes,
        imports=import_names,
        line_count=len(source.splitlines()),
        source_kernel_witness=witness,
        runtime_packet=packet,
        foundational_audit=audit,
    )


def build_guarded_plugin_adapter_manifest(root: Optional[str | Path] = None, paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    adapter_paths = list(paths or DEFAULT_ADAPTER_PATHS)
    adapters: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []
    for rel in adapter_paths:
        try:
            adapters.append(inspect_plugin_source(root_path, rel).to_dict())
        except Exception as exc:  # pragma: no cover - included in manifest instead of hiding failures
            errors.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "adapter_count": len(adapters),
        "error_count": len(errors),
        "execution_policy": "No adapted module may execute directly. This pass creates guarded static reachability only.",
    }
    return {
        **payload,
        "adapters": adapters,
        "errors": errors,
        "hash72_kernel_witness": _with_digest72_alias(make_hash72_kernel_witness(
            "hhs_guarded_plugin_adapters_manifest_v1",
            json.dumps(payload, sort_keys=True),
            width=72,
        ).to_dict()),
    }


def write_guarded_plugin_adapter_artifacts(root: Optional[str | Path] = None, paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_guarded_plugin_adapter_manifest(root_path, paths)
    (root_path / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    rows = ["| Path | Public Functions | Public Classes | Lines | Witness |", "|---|---:|---:|---:|---|"]
    for adapter in manifest.get("adapters", []):
        witness = adapter.get("source_kernel_witness", {}).get("digest72", "")
        rows.append(
            f"| `{adapter.get('path')}` | {len(adapter.get('public_functions', []))} | {len(adapter.get('public_classes', []))} | {adapter.get('line_count')} | `{witness[:18]}…` |"
        )
    if manifest.get("errors"):
        rows.append("| Errors | — | — | — | See manifest. |")
    report = f"""# Guarded Plugin Adapters — Pass 023

## Purpose

Pass 023 starts converting `PLUGIN_READY` files into explicit guarded adapter surfaces. The adapter is static and non-executing: it parses source, records public functions/classes/imports, emits C `u^72` Hash72 kernel witnesses, validates the adapter packet against the runtime contract, and runs a foundational audit.

## Policy

No plugin-ready module is directly executed by this adapter. Live execution requires a future dedicated semantic adapter that declares inputs, outputs, authority requirements, and closure behavior.

## Summary

```json
{json.dumps({k: manifest.get(k) for k in ['schema', 'version', 'adapter_count', 'error_count', 'execution_policy']}, indent=2, sort_keys=True)}
```

## Adapted Modules

{chr(10).join(rows)}

## Kernel Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def guarded_plugin_adapters_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    paths = payload.get("paths") if payload else None
    manifest = write_guarded_plugin_adapter_artifacts(root, paths=paths)
    ok = manifest.get("schema") == SCHEMA and manifest.get("adapter_count", 0) > 0 and manifest.get("error_count") == 0
    return {
        "schema": "HHS_GUARDED_PLUGIN_ADAPTERS_SELF_TEST_V1",
        "ok": ok,
        "adapter_count": manifest.get("adapter_count"),
        "error_count": manifest.get("error_count"),
        "artifacts": [MANIFEST_FILE, REPORT_FILE],
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(guarded_plugin_adapters_self_test(), indent=2, sort_keys=True))

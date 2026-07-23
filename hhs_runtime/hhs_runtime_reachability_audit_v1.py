"""
HHS Runtime Reachability Audit v1
=================================

Repository-wide static reachability map for release integration.

Pass 025 purpose:
    no orphan functions, no shadow pathways, no hidden subsystems.

This auditor is intentionally conservative and non-executing. It parses source
files and known canonical entry surfaces to classify files/modules by how they
enter the validated HHS runtime graph:

    BOOT_REACHABLE      - imported from backend/runtime boot roots
    SERVICE_REACHABLE   - registered in the guarded service registry
    API_REACHABLE       - reachable from canonical FastAPI runtime routes
    GUI_REACHABLE       - reachable from the GUI runtime bridge/sockets
    PLUGIN_READY        - safe-looking extension candidate, not yet wired
    DOCUMENTED_ONLY     - docs/specs/reports/reference assets
    DEPRECATED          - intentionally retained inactive/archive/deprecated
    ORPHAN              - source-like module with no current validated path

This does not import arbitrary modules, because importing orphan candidates can
execute side effects. The manifest is therefore a deterministic static audit and
roadmap generator, not a dynamic runtime loader.
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from hhs_runtime.hhs_hash72_kernel_authority_v1 import hash72_kernel_digest, make_hash72_kernel_witness
from hhs_runtime.hhs_runtime_integration_decisions_v1 import build_integration_decisions, write_integration_decision_artifacts
from hhs_runtime.hhs_native_project_ownership_v1 import ownership_for, validate_ownership

SCHEMA = "HHS_RUNTIME_REACHABILITY_MANIFEST_V1"
AUDITOR_VERSION = "PASS_032"

SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".c", ".h"}
DOCUMENT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".toml"}
GENERATED_DIR_NAMES = {"__pycache__", ".pytest_cache", "builds", "node_modules", "dist", ".git"}
DEPRECATED_MARKERS = {"deprecated", "archive", "legacy_disabled", "retired"}

BOOT_ROOT_MODULES = {
    "hhs_backend.server",
    "hhs_backend.api.runtime_routes",
    "hhs_runtime.main",
    "hhs_runtime.hhs_service_registry_v1",
    "hhs_runtime.hhs_io_gateway_v1",
    "hhs_runtime.hhs_runtime_contract_v1",
    "hhs_runtime.hhs_unified_hash72_ledger_v1",
    "hhs_runtime.hhs_system_closure_harness_v1",
    "hhs_runtime.hhs_srcg_gate_v1",
    "hhs_python.runtime.hhs_runtime_controller",
    "hhs_python.runtime.hhs_runtime_emulator",
    "hhs_python.runtime.hhs_ctypes_bridge",
}

CANONICAL_ROUTE_FILE = "hhs_backend/api/runtime_routes.py"
CANONICAL_BACKEND_FILE = "hhs_backend/server.py"
CANONICAL_SERVICE_REGISTRY_FILE = "hhs_runtime/hhs_service_registry_v1.py"
GUI_ROOTS = {
    "hhs_gui/src/runtime/RuntimeKernelBridge.ts",
    "hhs_gui/src/runtime/RuntimeSocketManager.ts",
    "hhs_gui/src/types/RuntimeContractEnvelope.ts",
    "hhs_gui/src/App.tsx",
    "hhs_gui/main.tsx",
}


@dataclass(frozen=True)
class ModuleRecord:
    path: str
    module: str
    kind: str
    status: str
    reasons: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    api_routes: List[str] = field(default_factory=list)
    gui_refs: List[str] = field(default_factory=list)
    contract_required: bool = True
    hash72_kernel_witness: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReachabilityManifest:
    schema: str
    version: str
    root: str
    module_count: int
    status_counts: Dict[str, int]
    service_count: int
    api_route_count: int
    gui_surface_count: int
    orphan_count: int
    plugin_ready_count: int
    integration_decision_count: int
    integration_decision_counts: Dict[str, int]
    records: List[Dict[str, Any]]
    unresolved_imports: List[str]
    hash72_kernel_witness: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repo_root(root: Optional[Path | str] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _skip_path(path: Path) -> bool:
    return any(part in GENERATED_DIR_NAMES for part in path.parts)


def _module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel.endswith("/__init__.py"):
        rel = rel[: -len("/__init__.py")]
    elif path.suffix == ".py":
        rel = rel[:-3]
    else:
        rel = rel.replace("/", ".")
        if path.suffix:
            rel = rel[: -len(path.suffix)]
    return rel.replace("/", ".")


def _kind_for(path: Path) -> str:
    if path.suffix == ".py":
        return "python"
    if path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return "frontend"
    if path.suffix in {".c", ".h"}:
        return "c_runtime"
    if path.suffix in DOCUMENT_SUFFIXES:
        return "document"
    return "asset"


def _all_relevant_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or _skip_path(path):
            continue
        if path.suffix in SOURCE_SUFFIXES or path.suffix in DOCUMENT_SUFFIXES:
            files.append(path)
    return sorted(files)


def _parse_python_imports(root: Path, path: Path) -> Set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    imports: Set[str] = set()
    package = _module_name(root, path).split(".")[:-1]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                base = package[: max(0, len(package) - node.level + 1)]
                if module:
                    imports.add(".".join(base + module.split(".")))
                else:
                    imports.add(".".join(base))
            elif module:
                imports.add(module)
    return imports


def _parse_frontend_imports(path: Path) -> Set[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    refs: Set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if "from " in stripped and ("import" in stripped):
            refs.add(stripped)
        elif stripped.startswith("import"):
            refs.add(stripped)
    return refs


def _extract_service_specs(root: Path) -> Dict[str, Dict[str, Any]]:
    path = root / CANONICAL_SERVICE_REGISTRY_FILE
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    specs: Dict[str, Dict[str, Any]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "register_function":
            kwargs: Dict[str, Any] = {}
            for kw in node.keywords:
                if kw.arg is None:
                    continue
                try:
                    kwargs[kw.arg] = ast.literal_eval(kw.value)
                except Exception:
                    if isinstance(kw.value, ast.Constant):
                        kwargs[kw.arg] = kw.value.value
                    else:
                        kwargs[kw.arg] = "<dynamic>"
            name = str(kwargs.get("name", ""))
            if name:
                specs[name] = kwargs
    return specs


def _extract_api_routes(root: Path) -> Dict[str, Dict[str, Any]]:
    path = root / CANONICAL_ROUTE_FILE
    if not path.exists():
        return {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return {}
    routes: Dict[str, Dict[str, Any]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if isinstance(dec.func.value, ast.Name) and dec.func.value.id == "router":
                    method = dec.func.attr.upper()
                    if method in {"GET", "POST", "PUT", "PATCH", "DELETE", "WEBSOCKET"}:
                        route = ""
                        if dec.args and isinstance(dec.args[0], ast.Constant):
                            route = str(dec.args[0].value)
                        full = f"{method} /api/runtime{route}"
                        routes[full] = {"function": node.name, "method": method, "path": f"/api/runtime{route}"}
    return routes


def _transitive_import_closure(import_graph: Mapping[str, Set[str]], roots: Iterable[str]) -> Set[str]:
    known_modules = set(import_graph)
    reached: Set[str] = set()
    queue = list(roots)
    while queue:
        current = queue.pop(0)
        if current in reached:
            continue
        if current not in known_modules:
            # Allow package roots to match exact known children, but do not explode stdlib imports.
            matches = [m for m in known_modules if m == current or m.startswith(current + ".")]
            if not matches:
                continue
            for match in matches:
                if match not in reached:
                    queue.append(match)
            continue
        reached.add(current)
        for imp in sorted(import_graph.get(current, set())):
            for candidate in known_modules:
                if candidate == imp or candidate.startswith(imp + "."):
                    if candidate not in reached:
                        queue.append(candidate)
    return reached


def _reverse_imports(import_graph: Mapping[str, Set[str]], modules: Set[str]) -> Dict[str, List[str]]:
    reverse: Dict[str, Set[str]] = {m: set() for m in modules}
    for src, imports in import_graph.items():
        for imp in imports:
            for candidate in modules:
                if candidate == imp or candidate.startswith(imp + "."):
                    reverse.setdefault(candidate, set()).add(src)
    return {k: sorted(v) for k, v in reverse.items()}


def _looks_plugin_ready(path: Path, module: str, text: str) -> bool:
    if "self_test" in text or "SelfTest" in text:
        return True
    if "register_function" in text or "HHSServiceSpec" in text:
        return True
    if module.startswith("hhs_runtime.hhs_") and any(token in module for token in ["adapter", "engine", "router", "validator", "solver", "guard", "ledger", "bridge", "operator"]):
        return True
    return False


def _status_for(
    *,
    rel: str,
    path: Path,
    module: str,
    kind: str,
    text: str,
    boot_reached: Set[str],
    api_reached_modules: Set[str],
    service_modules: Dict[str, List[str]],
    gui_refs_by_file: Dict[str, List[str]],
) -> Tuple[str, List[str]]:
    lower_rel = rel.lower()
    reasons: List[str] = []
    if any(marker in lower_rel for marker in DEPRECATED_MARKERS):
        return "DEPRECATED", ["path contains deprecated/archive marker"]
    if kind == "document":
        stem = Path(rel).stem
        generated_root_artifact = "/" not in rel and stem == stem.upper() and rel.endswith((".json", ".md", ".txt"))
        if rel.startswith("docs/") or rel.endswith(".md") or rel in {"PROJECT_STATE.json", "SCHEMA_REQUIREMENTS.md"} or generated_root_artifact:
            return "DOCUMENTED_ONLY", ["documentation/state/specification/generated pass artifact"]
    if kind == "frontend":
        if rel in GUI_ROOTS or rel in gui_refs_by_file:
            reasons.append("frontend runtime/contract surface")
            return "GUI_REACHABLE", reasons
        if rel.startswith("hhs_gui/src/") or rel.startswith("hhs_gui/"):
            return "PLUGIN_READY", ["frontend source not yet explicitly mapped to runtime bridge"]
    if kind == "c_runtime":
        if rel.startswith("hhs_runtime/c/") or rel.startswith("hhs_runtime/include/") or rel.startswith("hhs_runtime/src/") or rel.startswith("hhs_runtime/HARMONICODE_VM_RUNTIME"):
            return "BOOT_REACHABLE", ["C runtime build target / ABI surface"]
    if module in service_modules:
        return "SERVICE_REACHABLE", ["registered guarded service: " + ", ".join(sorted(service_modules[module]))]
    if module in api_reached_modules or rel == CANONICAL_ROUTE_FILE or rel == CANONICAL_BACKEND_FILE:
        return "API_REACHABLE", ["reachable through canonical backend/API route graph"]
    if module in boot_reached or module in BOOT_ROOT_MODULES:
        return "BOOT_REACHABLE", ["reachable from backend/runtime boot import graph"]
    if kind == "python" and _looks_plugin_ready(path, module, text):
        return "PLUGIN_READY", ["source has integration shape but no current guarded route/service"]
    if kind == "asset":
        return "DOCUMENTED_ONLY", ["non-source artifact"]
    return "ORPHAN", ["no boot/service/API/GUI/static documentation reachability found"]


def build_reachability_manifest(root: Optional[Path | str] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    files = _all_relevant_files(root_path)

    py_modules_by_path: Dict[str, str] = {}
    import_graph: Dict[str, Set[str]] = {}
    frontend_refs: Dict[str, Set[str]] = {}

    for path in files:
        rel = path.relative_to(root_path).as_posix()
        if path.suffix == ".py":
            module = _module_name(root_path, path)
            py_modules_by_path[rel] = module
            import_graph[module] = _parse_python_imports(root_path, path)
        elif path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            frontend_refs[rel] = _parse_frontend_imports(path)

    known_modules = set(import_graph)
    service_specs = _extract_service_specs(root_path)
    service_modules: Dict[str, List[str]] = {}
    for service_name, spec in service_specs.items():
        module = str(spec.get("module", ""))
        if module:
            service_modules.setdefault(module, []).append(service_name)

    api_routes = _extract_api_routes(root_path)
    api_import_roots = {"hhs_backend.api.runtime_routes", "hhs_backend.server"}
    # Runtime routes import concrete modules; treat their direct HHS imports as API reachable.
    api_reached_modules = _transitive_import_closure(import_graph, api_import_roots)
    boot_reached = _transitive_import_closure(import_graph, BOOT_ROOT_MODULES)

    reverse = _reverse_imports(import_graph, known_modules)

    gui_refs_by_file = {rel: sorted(refs) for rel, refs in frontend_refs.items() if rel in GUI_ROOTS or "RuntimeKernelBridge" in "\n".join(refs) or "RuntimeContractEnvelope" in "\n".join(refs)}

    records: List[ModuleRecord] = []
    unresolved_imports: Set[str] = set()
    for module, imports in import_graph.items():
        for imp in imports:
            if imp.startswith(("hhs_", "hhs_runtime", "hhs_python", "hhs_backend", "hhs_graph", "hhs_foundation")):
                if not any(candidate == imp or candidate.startswith(imp + ".") for candidate in known_modules):
                    unresolved_imports.add(imp)

    # Pass 025 explicit integration decisions convert previously silent orphan
    # candidates into auditable plugin/documentation/deprecation decisions.
    # Decisions do not override canonical wired states; they only resolve ORPHAN
    # records after the ordinary boot/service/API/GUI classification runs.
    decision_manifest_preview = build_integration_decisions(root_path)
    integration_decisions = {
        str(item.get("path")): item
        for item in decision_manifest_preview.get("decisions", [])
    }

    for path in files:
        rel = path.relative_to(root_path).as_posix()
        kind = _kind_for(path)
        module = py_modules_by_path.get(rel, _module_name(root_path, path))
        text = path.read_text(encoding="utf-8", errors="replace") if path.suffix in SOURCE_SUFFIXES else ""
        status, reasons = _status_for(
            rel=rel,
            path=path,
            module=module,
            kind=kind,
            text=text,
            boot_reached=boot_reached,
            api_reached_modules=api_reached_modules,
            service_modules=service_modules,
            gui_refs_by_file=gui_refs_by_file,
        )
        owner = ownership_for(rel) if status == "ORPHAN" else None
        if owner is not None:
            validate_ownership(root_path, rel, owner)
            status = str(owner["status"])
            reasons = [f"Pass 105.3 native ownership: {owner['owner_module']} via {owner['owner_test']}"]
        decision = integration_decisions.get(rel)
        if status == "ORPHAN" and decision and decision.get("decision") in {"PLUGIN_READY", "DOCUMENTED_ONLY", "DEPRECATED", "WIRED"}:
            status = "SERVICE_REACHABLE" if decision.get("decision") == "WIRED" else str(decision.get("decision"))
            reasons = [f"Pass 025 integration decision: {decision.get('reason')}"]
        services = sorted(service_modules.get(module, []))
        api_route_refs = []
        if rel == CANONICAL_ROUTE_FILE:
            api_route_refs = sorted(api_routes)
        elif module in api_reached_modules:
            api_route_refs = ["imported_by_runtime_routes"]
        gui_refs = sorted(frontend_refs.get(rel, [])) if kind == "frontend" else []
        witness_payload = {
            "schema": "HHS_MODULE_REACHABILITY_RECORD_WITNESS_V1",
            "path": rel,
            "module": module,
            "status": status,
            "services": services,
            "api_routes": api_route_refs,
        }
        records.append(
            ModuleRecord(
                path=rel,
                module=module,
                kind=kind,
                status=status,
                reasons=reasons,
                imports=sorted(import_graph.get(module, set())),
                imported_by=reverse.get(module, []),
                services=services,
                api_routes=api_route_refs,
                gui_refs=gui_refs,
                contract_required=kind in {"python", "frontend", "c_runtime"} and status not in {"DOCUMENTED_ONLY", "DEPRECATED"},
                hash72_kernel_witness=make_hash72_kernel_witness("hhs_runtime_reachability_record_v1", json.dumps(witness_payload, sort_keys=True), width=72).to_dict(),
            )
        )

    status_counts: Dict[str, int] = {}
    for record in records:
        status_counts[record.status] = status_counts.get(record.status, 0) + 1

    manifest_payload = {
        "schema": SCHEMA,
        "version": AUDITOR_VERSION,
        "status_counts": status_counts,
        "record_count": len(records),
        "service_count": len(service_specs),
        "api_route_count": len(api_routes),
        "orphan_count": status_counts.get("ORPHAN", 0),
    }
    manifest = ReachabilityManifest(
        schema=SCHEMA,
        version=AUDITOR_VERSION,
        root=str(root_path),
        module_count=len(records),
        status_counts=dict(sorted(status_counts.items())),
        service_count=len(service_specs),
        api_route_count=len(api_routes),
        gui_surface_count=len(gui_refs_by_file),
        orphan_count=status_counts.get("ORPHAN", 0),
        plugin_ready_count=status_counts.get("PLUGIN_READY", 0),
        integration_decision_count=decision_manifest_preview.get("decision_count", 0),
        integration_decision_counts=decision_manifest_preview.get("decision_counts", {}),
        records=[r.to_dict() for r in sorted(records, key=lambda item: item.path)],
        unresolved_imports=sorted(unresolved_imports),
        hash72_kernel_witness=make_hash72_kernel_witness("hhs_runtime_reachability_manifest_v1", json.dumps(manifest_payload, sort_keys=True), width=72).to_dict(),
    )
    return manifest.to_dict()


def write_reachability_artifacts(root: Optional[Path | str] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_reachability_manifest(root_path)
    write_integration_decision_artifacts(root_path, records=manifest.get("records", []))
    (root_path / "RUNTIME_REACHABILITY_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    _write_reports(root_path, manifest)
    return manifest


def _records_by_status(manifest: Mapping[str, Any], status: str) -> List[Mapping[str, Any]]:
    return [r for r in manifest.get("records", []) if r.get("status") == status]


def _write_reports(root: Path, manifest: Mapping[str, Any]) -> None:
    counts = manifest.get("status_counts", {})
    orphan_records = _records_by_status(manifest, "ORPHAN")
    plugin_records = _records_by_status(manifest, "PLUGIN_READY")
    service_records = _records_by_status(manifest, "SERVICE_REACHABLE")
    api_records = _records_by_status(manifest, "API_REACHABLE")
    boot_records = _records_by_status(manifest, "BOOT_REACHABLE")
    gui_records = _records_by_status(manifest, "GUI_REACHABLE")

    def table(records: Sequence[Mapping[str, Any]], limit: int = 80) -> str:
        if not records:
            return "| Path | Module | Reason |\n|---|---|---|\n| — | — | — |\n"
        rows = ["| Path | Module | Reason |", "|---|---|---|"]
        for record in records[:limit]:
            reason = "; ".join(record.get("reasons", []))
            rows.append(f"| `{record.get('path')}` | `{record.get('module')}` | {reason} |")
        if len(records) > limit:
            rows.append(f"| … | … | {len(records) - limit} additional records omitted from this summary; see JSON manifest. |")
        return "\n".join(rows) + "\n"

    report = f"""# Module Reachability Report — Pass 025

## Purpose

Pass 025 maintains the repository-wide runtime truth map. Every source-like module is classified by how it enters the HHS validated execution graph, or by why it is intentionally not executable.

## Status Counts

```json
{json.dumps(counts, indent=2, sort_keys=True)}
```

## Canonical Surfaces

- Services discovered: **{manifest.get('service_count')}**
- API routes discovered: **{manifest.get('api_route_count')}**
- GUI runtime surfaces discovered: **{manifest.get('gui_surface_count')}**
- Orphan records: **{manifest.get('orphan_count')}**
- Plugin-ready candidates: **{manifest.get('plugin_ready_count')}**
- Pass 025 integration decisions: **{manifest.get('integration_decision_count')}**

## BOOT_REACHABLE

{table(boot_records, 40)}

## SERVICE_REACHABLE

{table(service_records, 60)}

## API_REACHABLE

{table(api_records, 60)}

## GUI_REACHABLE

{table(gui_records, 60)}

## PLUGIN_READY Candidates

These are not failures. They are likely integration candidates that have service/engine/adapter/validator shape but are not currently part of the canonical dispatch graph.

{table(plugin_records, 100)}

## ORPHAN Candidates

These require explicit integration, deprecation, or documentation-only classification in subsequent passes.

{table(orphan_records, 120)}

## Kernel Witness

The manifest itself is sealed with a C `u^72` Digital DNA Hash72 kernel witness.

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / "MODULE_REACHABILITY_REPORT_PASS_032.md").write_text(report, encoding="utf-8")

    orphan_report = f"""# Orphan Modules — Pass 025

This report lists modules/files that are not currently reachable from boot, guarded services, API routes, GUI runtime surfaces, or documentation classification.

A record here is not automatically wrong. It means the file requires one of four decisions:

1. wire into the guarded runtime graph,
2. expose as a service/API/GUI/plugin,
3. mark as documented-only/reference,
4. deprecate/archive explicitly.

## Count

**{len(orphan_records)}** orphan candidates.

{table(orphan_records, 250)}
"""
    (root / "ORPHAN_MODULES_PASS_032.md").write_text(orphan_report, encoding="utf-8")

    graph = {
        "schema": "HHS_EXECUTION_GRAPH_PASS_032_V1",
        "boot_roots": sorted(BOOT_ROOT_MODULES),
        "service_modules": sorted({r.get("module") for r in service_records}),
        "api_modules": sorted({r.get("module") for r in api_records}),
        "gui_surfaces": sorted({r.get("path") for r in gui_records}),
        "plugin_ready": sorted({r.get("module") for r in plugin_records}),
        "orphans": sorted({r.get("module") for r in orphan_records}),
        "policy": "No executable source should remain ORPHAN across release-candidate stabilization.",
        "hash72": hash72_kernel_digest("hhs_execution_graph_pass_022_v1", json.dumps(counts, sort_keys=True), width=72),
    }
    (root / "EXECUTION_GRAPH_PASS_032.json").write_text(json.dumps(graph, indent=2, sort_keys=True), encoding="utf-8")


def reachability_audit_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    manifest = write_reachability_artifacts(root)
    ok = manifest.get("schema") == SCHEMA and manifest.get("module_count", 0) > 0 and manifest.get("service_count", 0) >= 1
    return {
        "schema": "HHS_RUNTIME_REACHABILITY_AUDIT_SELF_TEST_V1",
        "ok": ok,
        "manifest_schema": manifest.get("schema"),
        "module_count": manifest.get("module_count"),
        "status_counts": manifest.get("status_counts"),
        "service_count": manifest.get("service_count"),
        "api_route_count": manifest.get("api_route_count"),
        "orphan_count": manifest.get("orphan_count"),
        "artifacts": [
            "RUNTIME_REACHABILITY_MANIFEST.json",
            "MODULE_REACHABILITY_REPORT_PASS_032.md",
            "ORPHAN_MODULES_PASS_032.md",
            "EXECUTION_GRAPH_PASS_032.json",
        ],
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(reachability_audit_self_test(), indent=2, sort_keys=True))

"""
HHS Runtime Integration Decisions v1
====================================

Pass 023 decision layer for the reachability/orphan frontier.

Pass 021 exposed every file that did not have a validated boot/service/API/GUI
path. Pass 022 adds explicit, repository-native decisions for silent candidates
without deleting source or changing legacy semantics. The goal is to make the
remaining frontier deterministic:

    ORPHAN -> PLUGIN_READY / DOCUMENTED_ONLY / DEPRECATED / WIRED

The decision layer is intentionally static and conservative. It does not import
legacy modules, because import side effects would create exactly the kind of
shadow execution path the runtime is designed to avoid. Instead it records which
files are eligible for future guarded integration and which files are reference,
state, build, or compatibility artifacts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness, hash72_kernel_digest

SCHEMA = "HHS_RUNTIME_INTEGRATION_DECISIONS_V1"
VERSION = "PASS_024"
DECISION_FILE = "RUNTIME_INTEGRATION_DECISIONS.json"
REPORT_FILE = "RUNTIME_INTEGRATION_DECISIONS_PASS_024.md"

VALID_DECISIONS = {"PLUGIN_READY", "DOCUMENTED_ONLY", "DEPRECATED", "WIRED"}

WIRED_STATIC_ADAPTER_PATHS = {
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
    "hhs_runtime/hhs_guarded_plugin_adapters_v1.py",
    "hhs_runtime/hhs_plugin_capability_planner_v1.py",
}


@dataclass(frozen=True)
class IntegrationDecision:
    path: str
    decision: str
    reason: str
    pass_id: str = VERSION
    requires_guarded_entrypoint: bool = True
    hash72_kernel_witness: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data["hash72_kernel_witness"] is None:
            payload = {k: v for k, v in data.items() if k != "hash72_kernel_witness"}
            data["hash72_kernel_witness"] = make_hash72_kernel_witness(
                "hhs_runtime_integration_decision_v1",
                json.dumps(payload, sort_keys=True),
                width=72,
            ).to_dict()
        return data


def _repo_root(root: Optional[Path | str] = None) -> Path:
    if root is not None:
        return Path(root).resolve()
    return Path(__file__).resolve().parents[1]


def _is_generated_runtime_state(rel: str) -> bool:
    return rel.startswith("data/runtime/") and rel.endswith((".json", ".txt", ".jsonl"))


def _is_repo_state_artifact(rel: str) -> bool:
    base = Path(rel).name
    return (
        base.startswith(("RUNTIME_REACHABILITY_MANIFEST", "EXECUTION_GRAPH_PASS_", "MODULE_REACHABILITY_REPORT_PASS_", "ORPHAN_MODULES_PASS_", "GUARDED_PLUGIN_ADAPTERS_PASS_", "PLUGIN_CAPABILITY_PLANS_PASS_"))
        or base.startswith(("CHANGELOG_PASS_", "INTEGRATION_REPORT_PASS_", "KNOWN_ISSUES_PASS_", "NEXT_PASS_", "TEST_REPORT_PASS_"))
        or base in {
            "PROJECT_STATE.json",
            "SCHEMA_REQUIREMENTS.md",
            "DEVELOPMENT_OUTLINE.md",
            "HHS_FOUNDATIONAL_STANDARDS.md",
            "WordnetThesaurus.csv",
            "RUNTIME_INTEGRATION_DECISIONS.json",
            "GUARDED_PLUGIN_ADAPTERS_PASS_023.json",
            "PLUGIN_CAPABILITY_PLANS_PASS_024.json",
        }
    )


def _is_dictionary_or_reference_artifact(rel: str) -> bool:
    base = Path(rel).name.lower()
    return rel.startswith("hhs_runtime/") and base.endswith((".csv", ".txt")) and ("wordnet" in base or "grammar" in base or "word" in base)


def _is_config_or_build_artifact(rel: str) -> bool:
    base = Path(rel).name
    return (
        rel.startswith(".github/workflows/")
        or base in {"package.json", "tsconfig.json", "tsconfig.node.json", "vite.config.ts", "pytest.ini", "requirements.txt", "Makefile"}
        or base.endswith((".yml", ".yaml", ".toml"))
    )


def _is_foundation_shim(rel: str) -> bool:
    return rel.startswith("hhs_foundation/") and rel.endswith(".py") and Path(rel).stem in {
        "HHS-M001", "HHS-M002", "HHS-M003", "HHS-M004", "HHS-M005", "HHS-M006", "HHS-M007",
        "HHS_M001", "HHS_M002", "HHS_M003", "HHS_M004", "HHS_M005", "HHS_M006", "HHS_M007",
        "constitutional_validator", "meaning_conservation", "__init__",
    }


def _is_legacy_or_experimental_source(rel: str) -> bool:
    if not rel.endswith((".py", ".ts", ".tsx", ".js", ".jsx")):
        return False
    if rel.startswith("hhs_python/runtime/"):
        return True
    if rel.startswith("hhs_backend/runtime/"):
        return True
    if rel.startswith("gui/hhs-mobile-runtime-console/"):
        return True
    if rel.startswith("examples/"):
        return True
    if rel.startswith("hhs_gui/"):
        return True
    stem = Path(rel).stem.lower()
    return stem.startswith((
        "hhs_",
        "harmonicode_",
        "runtime_",
        "terminal_hhsprog",
        "hhs_v1_bundle_runner",
        "harmonicode_agent",
        "harmonicode_verbatim",
        "harmonicode_modality",
    )) or "harmonicode_kernel" in stem


def decide_path(rel: str) -> Optional[IntegrationDecision]:
    """Return the Pass 024 explicit decision for a path, if one applies."""

    if rel in WIRED_STATIC_ADAPTER_PATHS:
        return IntegrationDecision(
            path=rel,
            decision="WIRED",
            reason="wired through Pass 023 guarded static plugin adapter; direct execution remains unauthorized until a semantic adapter is declared",
            requires_guarded_entrypoint=True,
        )

    if _is_generated_runtime_state(rel):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="generated runtime state/data artifact; not an executable entrypoint",
            requires_guarded_entrypoint=False,
        )
    if _is_repo_state_artifact(rel):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="repository state/report/spec artifact; canonical context but not an executable entrypoint",
            requires_guarded_entrypoint=False,
        )
    if _is_config_or_build_artifact(rel):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="build/configuration/CI artifact; governed by release process rather than runtime dispatch",
            requires_guarded_entrypoint=False,
        )
    if _is_dictionary_or_reference_artifact(rel):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="dictionary/reference corpus used by semantic layers; not an executable entrypoint",
            requires_guarded_entrypoint=False,
        )
    if rel.startswith("schemas/") and rel.endswith(".json"):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="schema artifact; validates contract shape but is not an executable pathway",
            requires_guarded_entrypoint=False,
        )
    if rel.startswith("tests/") and rel.endswith(".py"):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="test harness artifact; executed only by explicit verification targets",
            requires_guarded_entrypoint=False,
        )
    if rel.startswith("tools/") and rel.endswith(".py"):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="developer tooling candidate; requires guarded operator/CLI integration before runtime use",
            requires_guarded_entrypoint=True,
        )
    if _is_foundation_shim(rel):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="constitutional compatibility shim; callable only through canonical foundational standards module",
            requires_guarded_entrypoint=True,
        )
    if rel.endswith("/__init__.py"):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="package marker; not a standalone executable entrypoint",
            requires_guarded_entrypoint=False,
        )
    if rel.startswith("hhs_runtime/test_") and rel.endswith(".py"):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="runtime validation test artifact; executed only by explicit verification targets",
            requires_guarded_entrypoint=False,
        )
    if rel.startswith("hhs_runtime/") and rel.endswith((".c", ".h")):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="C runtime/bridge source candidate; must be reached through Makefile/ABI build or explicit kernel adapter",
            requires_guarded_entrypoint=True,
        )
    if rel == "hhs_runtime/kernel_resolution.py":
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="runtime kernel-resolution candidate retained for guarded adapter integration",
            requires_guarded_entrypoint=True,
        )
    if rel.startswith("hhs_runtime/plugins/"):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="plugin candidate; requires canonical plugin SDK/contract wrapping",
            requires_guarded_entrypoint=True,
        )
    if rel.startswith("hhs_runtime/testing/"):
        return IntegrationDecision(
            path=rel,
            decision="DOCUMENTED_ONLY",
            reason="runtime testing support artifact; executed only by explicit verification targets",
            requires_guarded_entrypoint=False,
        )
    if rel.startswith("hhs_runtime/core_sandbox/"):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="sandbox/experimental kernel candidate retained for guarded adapter review; direct execution unauthorized",
            requires_guarded_entrypoint=True,
        )
    if rel.startswith(("hhs_runtime/core/", "hhs_runtime/acceleration/", "hhs_runtime/api/", "hhs_runtime/data/")):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="runtime subpackage candidate retained for guarded contract integration",
            requires_guarded_entrypoint=True,
        )
    if _is_legacy_or_experimental_source(rel):
        return IntegrationDecision(
            path=rel,
            decision="PLUGIN_READY",
            reason="legacy/high-value source retained for guarded adapter integration; no direct execution authorized",
            requires_guarded_entrypoint=True,
        )
    return None


def build_integration_decisions(root: Optional[Path | str] = None, records: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    decision_records: List[Dict[str, Any]] = []
    paths: Iterable[str]
    if records is not None:
        paths = [str(record.get("path", "")) for record in records]
    else:
        paths = [p.relative_to(root_path).as_posix() for p in root_path.rglob("*") if p.is_file()]

    for rel in sorted(set(paths)):
        decision = decide_path(rel)
        if decision is not None:
            decision_records.append(decision.to_dict())

    counts: Dict[str, int] = {}
    for record in decision_records:
        counts[record["decision"]] = counts.get(record["decision"], 0) + 1
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "decision_count": len(decision_records),
        "decision_counts": dict(sorted(counts.items())),
    }
    return {
        **payload,
        "policy": "Every noncanonical source must be explicitly wired, plugin-ready, documented-only, or deprecated before release candidate stabilization.",
        "decisions": decision_records,
        "hash72_kernel_witness": make_hash72_kernel_witness(
            "hhs_runtime_integration_decisions_v1",
            json.dumps(payload, sort_keys=True),
            width=72,
        ).to_dict(),
    }


def write_integration_decision_artifacts(root: Optional[Path | str] = None, records: Optional[Iterable[Mapping[str, Any]]] = None) -> Dict[str, Any]:
    root_path = _repo_root(root)
    manifest = build_integration_decisions(root_path, records=records)
    (root_path / DECISION_FILE).write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    _write_report(root_path, manifest)
    return manifest


def _write_report(root: Path, manifest: Mapping[str, Any]) -> None:
    counts = manifest.get("decision_counts", {})
    decisions = list(manifest.get("decisions", []))

    def table(decision: str, limit: int = 80) -> str:
        rows = ["| Path | Reason | Guarded Entry Required |", "|---|---|---|"]
        subset = [d for d in decisions if d.get("decision") == decision]
        if not subset:
            rows.append("| — | — | — |")
            return "\n".join(rows) + "\n"
        for item in subset[:limit]:
            rows.append(f"| `{item.get('path')}` | {item.get('reason')} | `{item.get('requires_guarded_entrypoint')}` |")
        if len(subset) > limit:
            rows.append(f"| … | {len(subset) - limit} additional records omitted; see `{DECISION_FILE}`. | … |")
        return "\n".join(rows) + "\n"

    report = f"""# Runtime Integration Decisions — Pass 023

## Purpose

Pass 023 updates integration decisions after the first guarded static adapter batch converts selected plugin-ready files into explicit release decisions. This is not deletion and not semantic rewriting. It is the first controlled reduction of the orphan frontier created in Pass 021.

## Decision Counts

```json
{json.dumps(counts, indent=2, sort_keys=True)}
```

## Policy

No source-like file may remain silently outside the validated runtime graph. Each candidate must become one of:

- `WIRED`
- `PLUGIN_READY`
- `DOCUMENTED_ONLY`
- `DEPRECATED`

## PLUGIN_READY

These files are retained as high-value integration candidates. They are not authorized for direct execution until wrapped by the service registry, API contract, GUI bridge, or plugin SDK.

{table('PLUGIN_READY', 160)}

## DOCUMENTED_ONLY

These files carry state, reports, specifications, configuration, generated runtime evidence, or release context. They are not executable runtime pathways.

{table('DOCUMENTED_ONLY', 120)}

## Kernel Witness

```json
{json.dumps(manifest.get('hash72_kernel_witness', {}), indent=2, sort_keys=True)}
```
"""
    (root / REPORT_FILE).write_text(report, encoding="utf-8")


def integration_decisions_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root(payload.get("root") if payload else None)
    manifest = write_integration_decision_artifacts(root)
    ok = manifest.get("schema") == SCHEMA and manifest.get("decision_count", 0) > 0
    return {
        "schema": "HHS_RUNTIME_INTEGRATION_DECISIONS_SELF_TEST_V1",
        "ok": ok,
        "decision_count": manifest.get("decision_count"),
        "decision_counts": manifest.get("decision_counts"),
        "artifacts": [DECISION_FILE, REPORT_FILE],
        "hash72_kernel_witness": manifest.get("hash72_kernel_witness"),
    }


if __name__ == "__main__":
    print(json.dumps(integration_decisions_self_test(), indent=2, sort_keys=True))

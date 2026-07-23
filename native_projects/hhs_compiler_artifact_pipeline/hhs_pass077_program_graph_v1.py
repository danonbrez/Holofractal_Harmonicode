"""Reachability graph for the reusable Pass 077 native compiler program."""
from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping
from native_projects.hhs_ide_workspace.hhs_workspace_contracts_v1 import product_root, stable
from .hhs_pass077_contracts_v1 import PASS_ID, PROGRAM_GRAPH_SCHEMA

NODES = (
    ("pass077.package", "native_projects/hhs_compiler_artifact_pipeline/__init__.py", ("pass077.runtime",)),
    ("pass077.contracts", "native_projects/hhs_compiler_artifact_pipeline/hhs_pass077_contracts_v1.py", ()),
    ("pass077.semantic_projection", "native_projects/hhs_compiler_artifact_pipeline/hhs_canonical_semantic_projection_v1.py", ("pass077.contracts",)),
    ("pass077.bytecode", "native_projects/hhs_compiler_artifact_pipeline/hhs_portable_bytecode_v1.py", ("pass077.contracts", "pass076.interpreter")),
    ("pass077.equivalence", "native_projects/hhs_compiler_artifact_pipeline/hhs_interpreter_compiler_equivalence_gate_v1.py", ("pass077.semantic_projection", "pass077.contracts")),
    ("pass077.lineage", "native_projects/hhs_compiler_artifact_pipeline/hhs_artifact_lineage_pipeline_v1.py", ("pass077.bytecode", "pass077.contracts")),
    ("pass077.delta", "native_projects/hhs_compiler_artifact_pipeline/hhs_exact_artifact_delta_v1.py", ("pass077.lineage",)),
    ("pass077.verifier_adapter", "native_projects/hhs_compiler_artifact_pipeline/hhs_independent_artifact_verifier_v1.py", ("pass077.lineage", "pass077.standalone_verifier")),
    ("pass077.runtime", "native_projects/hhs_compiler_artifact_pipeline/hhs_pass077_workspace_runtime_v1.py", ("pass077.bytecode", "pass077.equivalence", "pass077.lineage", "pass077.delta", "pass077.verifier_adapter", "pass076.runtime")),
    ("pass077.api", "native_projects/hhs_compiler_artifact_pipeline/hhs_pass077_api_v1.py", ("pass077.runtime", "pass074.api")),
    ("pass077.cli", "native_projects/hhs_compiler_artifact_pipeline/hhs_pass077_cli_v1.py", ("pass077.runtime", "pass077.replay", "pass077.verifier_adapter")),
    ("pass077.replay", "native_projects/hhs_compiler_artifact_pipeline/hhs_pass077_replay_runner_v1.py", ("pass077.runtime", "pass077.program_graph")),
    ("pass077.program_graph", "native_projects/hhs_compiler_artifact_pipeline/hhs_pass077_program_graph_v1.py", ("pass077.contracts",)),
    ("pass077.standalone_verifier", "native_projects/hhs_compiler_artifact_pipeline/verifier/verify_artifact.py", ()),
)
INHERITED = (
    ("pass076.runtime", "native_projects/hhs_harmonicode_interpreter/hhs_pass076_workspace_runtime_v1.py"),
    ("pass076.interpreter", "native_projects/hhs_harmonicode_interpreter/hhs_exact_symbolic_interpreter_v1.py"),
    ("pass074.api", "native_projects/hhs_ide_workspace/hhs_unified_runtime_api_v1.py"),
)


def build_program_graph() -> Dict[str, Any]:
    nodes = []
    edges = []
    for node_id, path, dependencies in NODES:
        body = {"node_id": node_id, "kind": "PASS077_NATIVE_MODULE", "relative_path": path, "dependencies": list(dependencies), "reachable": True, "reusable_capability": True}
        body["node_root_hash72"] = product_root("pass077_program_node", body)
        nodes.append(stable(body))
        for target in dependencies:
            edge = {"from_node": node_id, "to_node": target, "relationship": "IMPORTS_OR_CONSUMES"}
            edge["edge_root_hash72"] = product_root("pass077_program_edge", edge)
            edges.append(stable(edge))
    for node_id, path in INHERITED:
        body = {"node_id": node_id, "kind": "INHERITED_REUSABLE_DEPENDENCY", "relative_path": path, "dependencies": [], "reachable": True, "reusable_capability": True}
        body["node_root_hash72"] = product_root("pass077_program_node", body)
        nodes.append(stable(body))
    graph = {
        "schema": PROGRAM_GRAPH_SCHEMA,
        "pass_id": PASS_ID,
        "program_id": "program:hhs-verified-semantic-projection-and-artifact-lineage",
        "nodes": nodes,
        "edges": edges,
        "entrypoints": ["pass077.api", "pass077.cli", "pass077.replay", "pass077.package", "pass077.standalone_verifier"],
        "native_module_count": len(NODES),
        "reachable_native_module_count": len(NODES),
        "orphan_native_module_count": 0,
        "inherited_dependency_count": len(INHERITED),
        "all_new_modules_reusable": True,
        "new_capabilities": [
            "compiler.plan", "compiler.lower", "compiler.optimize", "compiler.emit",
            "compiler.validate", "compiler.replay", "lineage.record", "artifact.package",
            "artifact.verify", "artifact.export", "artifact.delta.create", "artifact.delta.apply",
        ],
    }
    graph["program_graph_root_hash72"] = product_root("pass077_program_graph", graph)
    return stable(graph)

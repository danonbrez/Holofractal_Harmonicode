"""Workspace graph projection surface for Pass 049."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

GRAPH_PROJECTION_SCHEMA = "HHS_RUNTIME_GRAPH_PROJECTION_V1"

NODE_TYPES = ["INVARIANT", "SURFACE", "SERVICE", "API_ROUTE", "COMMAND", "CONTRACT", "WITNESS", "VALIDATOR", "GUARD", "EXECUTOR", "STATE", "OBJECT", "ARTIFACT", "RECEIPT", "LEDGER_ENTRY", "SEMANTIC_MEMORY", "MODALITY_PROJECTION", "EMULATOR_SESSION", "HUMAN_REQUEST", "AI_PROPOSAL"]
EDGE_TYPES = ["DERIVES", "REQUESTS", "AUTHORIZES", "REJECTS", "TRANSFORMS", "WITNESSES", "VALIDATES", "PERSISTS", "PROJECTS", "COMPILES_TO", "INTERPRETS_AS", "EMULATES", "REPLAYS", "RECONSTRUCTS", "REFERENCES", "CONSERVES", "BRANCHES_FROM"]


def build_workspace_graph_projection(nodes: Iterable[Mapping[str, Any]], edges: Iterable[Mapping[str, Any]], *, project_id: str = "project:default") -> Dict[str, Any]:
    node_list = [dict(n) for n in nodes]
    edge_list = [dict(e) for e in edges]
    projection = {
        "schema": GRAPH_PROJECTION_SCHEMA,
        "version": VERSION,
        "projection_id": f"graph:{uuid.uuid4().hex}",
        "project_id": project_id,
        "nodes": node_list,
        "edges": edge_list,
        "layout_is_authoritative": False,
        "collapsed_nodes_hide_authority_failures": False,
        "manual_annotations_executable": False,
        "authority": AUTHORITY,
    }
    projection["projection_root_hash72"] = hash72(GRAPH_PROJECTION_SCHEMA, projection)
    return projection


def workspace_graph_projection_self_test() -> Dict[str, Any]:
    projection = build_workspace_graph_projection(
        [{"id": "object:1", "type": "OBJECT"}, {"id": "receipt:1", "type": "RECEIPT"}],
        [{"from": "object:1", "to": "receipt:1", "type": "WITNESSES"}],
        project_id="project:pass049",
    )
    ok = bool(projection.get("projection_root_hash72") and not projection.get("layout_is_authoritative"))
    return {
        "schema": "HHS_WORKSPACE_GRAPH_PROJECTION_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "projection": projection,
        "node_types": NODE_TYPES,
        "edge_types": EDGE_TYPES,
        "constraint": "CANVAS_LAYOUT_IS_NOT_GRAPH_TRUTH",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(workspace_graph_projection_self_test(), indent=2, sort_keys=True, default=str))

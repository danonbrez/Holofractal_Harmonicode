"""Workspace semantic memory/search projection for Pass 049."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

QUERY_SCHEMA = "HHS_SEMANTIC_RUNTIME_QUERY_V1"


def build_workspace_semantic_query(query_text: str, *, project_id: str = "project:default", object_ids: Iterable[str] = ()) -> Dict[str, Any]:
    query = {
        "schema": QUERY_SCHEMA,
        "version": VERSION,
        "query_id": f"query:{uuid.uuid4().hex}",
        "project_id": project_id,
        "query_text": query_text,
        "query_object_ids": list(object_ids),
        "modalities": [],
        "relation_types": [],
        "bounded_result_count": 50,
        "requires_witnessed_results": True,
        "retrieval_mutates_project_state": False,
    }
    query["query_root_hash72"] = hash72(QUERY_SCHEMA, query)
    return query


def execute_workspace_semantic_query(query: Mapping[str, Any], objects: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    text = str(query.get("query_text") or "").lower()
    results = []
    for obj in objects:
        hay = f"{obj.get('name')} {obj.get('object_type')} {obj.get('modality')}".lower()
        if text in hay or not text:
            results.append({
                "object_id": obj.get("object_id"),
                "object_type": obj.get("object_type"),
                "root_hash72": obj.get("current_root_hash72"),
                "result_is_authority": False,
                "resolves_to_canonical_object": True,
            })
    bounded = results[: int(query.get("bounded_result_count") or 50)]
    response = {
        "schema": "HHS_WORKSPACE_SEMANTIC_MEMORY_QUERY_RESULT_V1",
        "version": VERSION,
        "ok": True,
        "query_id": query.get("query_id"),
        "results": bounded,
        "ranking_is_truth_authority": False,
        "embeddings_are_identity": False,
        "authority": AUTHORITY,
    }
    response["result_root_hash72"] = hash72("HHS_WORKSPACE_SEMANTIC_MEMORY_QUERY_RESULT_V1", response)
    return response


def workspace_semantic_memory_self_test() -> Dict[str, Any]:
    query = build_workspace_semantic_query("source", project_id="project:pass049")
    objects = [{"object_id": "object:source", "object_type": "SYMBOLIC_SOURCE_DOCUMENT", "modality": "HARMONICODE_SOURCE", "name": "main.hhs", "current_root_hash72": "root"}]
    result = execute_workspace_semantic_query(query, objects)
    return {
        "schema": "HHS_WORKSPACE_SEMANTIC_MEMORY_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(result.get("ok") and result.get("results") and not result.get("ranking_is_truth_authority")),
        "query": query,
        "result": result,
        "constraint": "RETRIEVAL_DOES_NOT_MUTATE_CANONICAL_PROJECT_STATE",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(workspace_semantic_memory_self_test(), indent=2, sort_keys=True, default=str))

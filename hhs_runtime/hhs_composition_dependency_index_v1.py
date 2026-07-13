"""Pass 044 semantic dependency index for incremental pipeline rebuild."""
from __future__ import annotations
from typing import Any, Dict, List, Mapping
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness

VERSION = "PASS_044_SEMANTIC_COMPOSITION_CACHE_V1"
INDEX_SCHEMA = "HHS_SEMANTIC_DEPENDENCY_INDEX_V1"


def _hash72(label: str, payload: Any) -> str:
    return make_hash72_kernel_witness(label, payload, width=72).digest


def _add(index: Dict[str, Dict[str, List[str]]], family: str, key: str, surface_id: str) -> None:
    index.setdefault(family, {}).setdefault(str(key), [])
    if surface_id not in index[family][str(key)]:
        index[family][str(key)].append(surface_id)


def build_dependency_index(surface_map: Mapping[str, Any]) -> Dict[str, Any]:
    idx: Dict[str, Dict[str, List[str]]] = {
        "invariant_to_surfaces": {},
        "surface_to_contracts": {},
        "contract_to_surfaces": {},
        "validator_to_surfaces": {},
        "witness_to_surfaces": {},
        "guard_to_surfaces": {},
        "rejection_code_to_surfaces": {},
        "surface_to_operations": {},
    }
    for surface in surface_map.get("surfaces", []) or []:
        sid = str(surface.get("surface_id"))
        for iid in surface.get("invariant_ids", []) or []:
            _add(idx, "invariant_to_surfaces", iid, sid)
        for contract in surface.get("contract_schemas", []) or []:
            _add(idx, "contract_to_surfaces", contract, sid)
            _add(idx, "surface_to_contracts", sid, contract)
        for validator in surface.get("validators", []) or []:
            _add(idx, "validator_to_surfaces", validator, sid)
        for witness in surface.get("witness_schemas", []) or []:
            _add(idx, "witness_to_surfaces", witness, sid)
        for guard in surface.get("guards", []) or []:
            _add(idx, "guard_to_surfaces", guard, sid)
        for code in surface.get("rejection_codes", []) or []:
            _add(idx, "rejection_code_to_surfaces", code, sid)
        for op in surface.get("declared_operations", []) or []:
            _add(idx, "surface_to_operations", sid, op)
    index = {
        "schema": INDEX_SCHEMA,
        "version": VERSION,
        "conformance_graph_root": surface_map.get("conformance_root_hash72"),
        "surface_count": surface_map.get("surface_count"),
        "dependency_families": idx,
        "semantic_index_authority": "DEPENDENCY_LOOKUP_ONLY_KERNEL_CONFORMANCE_REMAINS_AUTHORITY",
    }
    index["semantic_dependency_index_hash72"] = _hash72(INDEX_SCHEMA, index)
    return index


def affected_surfaces(index: Mapping[str, Any], *, dependency_family: str, dependency_id: str) -> List[str]:
    families = index.get("dependency_families", {})
    return sorted(families.get(dependency_family, {}).get(str(dependency_id), []) or [])


def dependency_query(index: Mapping[str, Any], query: str) -> Dict[str, Any]:
    hits = {}
    for family, mapping in (index.get("dependency_families") or {}).items():
        if query in mapping:
            hits[family] = sorted(mapping[query])
    return {
        "schema": "HHS_SEMANTIC_DEPENDENCY_QUERY_RESULT_V1",
        "version": VERSION,
        "query": query,
        "hit_families": sorted(hits.keys()),
        "hits": hits,
    }


def composition_dependency_index_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map
    surface_map = build_surface_map()
    index = build_dependency_index(surface_map)
    first_surface = surface_map["surfaces"][0]
    iid = first_surface["invariant_ids"][0]
    hits = affected_surfaces(index, dependency_family="invariant_to_surfaces", dependency_id=iid)
    query = dependency_query(index, iid)
    return {"schema": "HHS_COMPOSITION_DEPENDENCY_INDEX_SELF_TEST_V1", "version": VERSION, "ok": first_surface["surface_id"] in hits and bool(query["hit_families"]), "index": index, "hits": hits[:8], "query": query}

if __name__ == "__main__":
    print(composition_dependency_index_self_test())

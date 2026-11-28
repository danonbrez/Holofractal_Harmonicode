#!/usr/bin/env python3
"""Deterministic read-only Pass914 G2 dependency evaluator.

The preserved 21 edges are a seed, not proof that the live graph is complete.
No git mutation, merge, candidate commit or authority receipt is produced.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import heapq
import json
from pathlib import Path
import re

CONTRACT = Path("contracts/architecture/HHS_PR914_G2_DEPENDENCY_CONFLICT_AND_CANDIDATE_COMPOSITION_CONTRACT_V1.json")
INVENTORY = Path("contracts/architecture/HHS_PR914_OPEN_BRANCH_INVENTORY_20261123.json")
SHA = re.compile(r"^[0-9a-f]{40}$")


def _id(pr: int) -> str:
    return f"PR:{pr:06d}"


def _strong_components(nodes, outgoing):
    """Tarjan with sorted traversal; canonical SCC and self-cycle witnesses."""
    index = 0
    indices, lowlink, stack, onstack, components = {}, {}, [], set(), []

    def visit(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)
        for w in sorted(outgoing[v]):
            if w not in indices:
                visit(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], indices[w])
        if lowlink[v] == indices[v]:
            component = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                component.append(w)
                if w == v:
                    break
            components.append(sorted(component))

    for v in sorted(nodes):
        if v not in indices:
            visit(v)
    return sorted(
        [c for c in components if len(c) > 1 or c[0] in outgoing[c[0]]],
        key=lambda x: tuple(x),
    )


def evaluate(contract: dict, inventory: dict, refresh: dict | None = None) -> dict:
    seed = contract["known_dependency_edge_seed"]
    if seed["orientation"] != "DEPENDENT_PR_REQUIRES_PARENT_PR":
        raise ValueError("G2_EDGE_ORIENTATION_MISMATCH")
    edges = seed["edges"]
    if len(edges) != 21:
        raise ValueError("G2_PRESERVED_EDGE_COUNT_MISMATCH")
    original = inventory.get("entries", [])
    ids = {_id(int(x["number"])) for x in original}
    if len(ids) != len(original):
        raise ValueError("G2_DUPLICATE_PR_INVENTORY_ENTRY")
    outgoing, parents = defaultdict(set), defaultdict(set)
    edge_evidence = []
    for edge in edges:
        p, d = _id(int(edge["required_parent_pr"])), _id(int(edge["dependent_pr"]))
        ids.update((p, d))
        outgoing[p].add(d)
        parents[d].add(p)
        edge_evidence.append({
            "required_parent_node_id": p, "dependent_node_id": d,
            "direction": "PARENT_BEFORE_DEPENDENT",
            "source": "G2_KNOWN_DEPENDENCY_EDGE_SEED",
            "source_evidence_requires_live_confirmation": True,
        })
    seed_set = {_id(int(x["number"])) for x in original}
    external = sorted(ids - seed_set)
    cycles = _strong_components(ids, outgoing)
    degree = {n: len(parents[n]) for n in ids}
    ready = [n for n in ids if degree[n] == 0]
    heapq.heapify(ready)
    ordered = []
    while ready:
        n = heapq.heappop(ready)
        ordered.append(n)
        for child in sorted(outgoing[n]):
            degree[child] -= 1
            if degree[child] == 0:
                heapq.heappush(ready, child)

    # Reachable parent closure is explicit, including unresolved external refs.
    def ancestors(n, seen=None):
        seen = set() if seen is None else seen
        for p in sorted(parents[n]):
            if p not in seen:
                seen.add(p)
                ancestors(p, seen)
        return seen

    blocked = [
        {"node_id": n, "unresolved_parent_nodes": sorted(ancestors(n) & set(external))}
        for n in sorted(ids)
        if ancestors(n) & set(external)
    ]
    reasons = []
    if cycles:
        reasons.append("G2_BLOCKED_DEPENDENCY_CYCLE")
    if external:
        reasons.append("G2_BLOCKED_INCOMPLETE_GRAPH")
    if refresh is None:
        reasons.append("G2_BLOCKED_STALE_REFS")
    else:
        base = refresh.get("main_sha")
        exact = isinstance(base, str) and SHA.fullmatch(base) is not None
        entries = refresh.get("entries", [])
        complete = refresh.get("pagination_complete") is True and refresh.get("g1_complete") is True
        known = {_id(int(x["number"])) for x in entries if x.get("kind") == "OPEN_PR" and isinstance(x.get("number"), int)}
        complete = complete and ids <= known and not external
        exact = exact and all(
            isinstance(x.get("head_sha"), str) and SHA.fullmatch(x["head_sha"])
            and isinstance(x.get("base_sha"), str) and SHA.fullmatch(x["base_sha"])
            and isinstance(x.get("merge_base_sha"), str) and SHA.fullmatch(x["merge_base_sha"])
            for x in entries
        )
        if not exact:
            reasons.append("G2_BLOCKED_STALE_REFS")
        if not complete:
            reasons.append("G2_BLOCKED_INCOMPLETE_GRAPH")
    if len(ordered) != len(ids):
        reasons.append("G2_BLOCKED_DEPENDENCY_CYCLE")
    # This evaluator cannot attest conflict resolution, provenance or native tests.
    reasons.extend([
        "G2_BLOCKED_UNRESOLVED_SEMANTIC_CONFLICT",
        "G2_BLOCKED_CAPABILITY_COVERAGE_GAP",
    ])
    return {
        "schema": "HHS_PR914_G2_DEPENDENCY_GRAPH_EVALUATION_V1",
        "input_mode": "HISTORICAL_SEED_ONLY" if refresh is None else "REFRESH_SUPPLIED_UNVERIFIED",
        "dependency_orientation": "PARENT_BEFORE_DEPENDENT",
        "tie_break": "LEXICOGRAPHIC_NODE_ID_FOR_INDEPENDENT_NODES_ONLY",
        "preserved_edge_count": len(edges),
        "preserved_edge_evidence": edge_evidence,
        "observed_pr_nodes": len(original),
        "all_seed_nodes": len(ids),
        "unresolved_external_parent_or_dependent_nodes": external,
        "cycle_components": cycles,
        "topological_order": ordered if not cycles else None,
        "blocked_by_dependency": blocked,
        "source_inventory_sha256": sha256(
            json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "candidate_composed": False,
        "g1_complete": False,
        "g2_complete": False,
        "main_merge_authorized": False,
        "production_deploy_authorized": False,
        "blocking_reasons": sorted(set(reasons)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=CONTRACT)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    parser.add_argument("--refresh", type=Path)
    parser.add_argument("--output", type=Path)
    a = parser.parse_args()
    contract = json.loads(a.contract.read_text(encoding="utf-8"))
    inventory = json.loads(a.inventory.read_text(encoding="utf-8"))
    refresh = json.loads(a.refresh.read_text(encoding="utf-8")) if a.refresh else None
    result = evaluate(contract, inventory, refresh)
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if a.output:
        a.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Inherited HHS proof-index traversal; candidate-only, no new mathematical rules.

Inputs are complete *provided* index collections, not a claim of exhaustive
repository coverage. Preserve original status and exact declared dependencies.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA = "HHS_PASS220_CUMULATIVE_LEMMA_FRONTIER_V1"


class CorpusFrontierError(ValueError):
    pass


def _digest(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, allow_nan=False,
        separators=(",", ":"),
    ).encode()).hexdigest()


def _record(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise CorpusFrontierError("INVALID_" + label)
    return value


def construct_frontier(
    *,
    lemma_corpora: Iterable[Mapping[str, Any]] = (),
    course_indexes: Iterable[Mapping[str, Any]] = (),
    targets: Iterable[str] = (),
) -> dict[str, Any]:
    """Traverse all supplied records, irrespective of selected attention targets.

    The original proof status is never promoted. Course index entries remain
    *source pointers*, not proof certificates. No inferred semantic edges.
    """
    nodes: dict[str, dict[str, Any]] = {}
    parents: dict[str, tuple[str, ...]] = {}

    for corpus in lemma_corpora:
        corpus = _record(corpus, "LEMMA_CORPUS")
        items = corpus.get("lemmas", ())
        if not isinstance(items, list):
            raise CorpusFrontierError("INVALID_LEMMA_LIST")
        for item in items:
            item = _record(item, "LEMMA")
            key = item.get("id")
            if not isinstance(key, str) or not key or key in nodes:
                raise CorpusFrontierError("DUPLICATE_OR_INVALID_LEMMA_ID")
            deps = item.get("dependencies", ())
            if not isinstance(deps, list) or any(not isinstance(d, str) for d in deps):
                raise CorpusFrontierError("INVALID_LEMMA_DEPENDENCIES")
            nodes[key] = {
                "id": key, "kind": "INHERITED_LEMMA",
                "source_schema": corpus.get("schema"),
                "name": item.get("name"), "statement": item.get("statement"),
                "assumptions": item.get("assumptions"),
                "status": item.get("status"),
                "source_record_sha256": _digest(item),
            }
            parents[key] = tuple(deps)

    for index in course_indexes:
        index = _record(index, "COURSE_INDEX")
        source = _record(index.get("source"), "COURSE_SOURCE")
        items = index.get("modules", ())
        if not isinstance(items, list):
            raise CorpusFrontierError("INVALID_COURSE_MODULE_LIST")
        for item in items:
            item = _record(item, "COURSE_MODULE")
            key = item.get("id")
            if not isinstance(key, str) or not key or key in nodes:
                raise CorpusFrontierError("DUPLICATE_OR_INVALID_MODULE_ID")
            nodes[key] = {
                "id": key, "kind": "INDEXED_COURSE_SOURCE",
                "source_path": source.get("path"),
                "source_git_blob_sha": source.get("git_blob_sha"),
                "source_heading": item.get("source_heading"),
                "title": item.get("title"),
                "proof_admitted": item.get("proof_admitted"),
                "canonical_runtime_admitted": item.get("canonical_runtime_admitted"),
                "source_record_sha256": _digest(item),
            }
            # Source positions are not equivalent to formal inference edges.
            parents[key] = ()

    for key, deps in parents.items():
        missing = [dep for dep in deps if dep not in nodes]
        if missing:
            raise CorpusFrontierError(
                "MISSING_INHERITED_LEMMA_DEPENDENCY:" + key + ":" + ",".join(missing)
            )
        if key in deps:
            raise CorpusFrontierError("SELF_DEPENDENCY:" + key)

    targets = tuple(targets)
    if any(key not in nodes for key in targets):
        raise CorpusFrontierError("UNKNOWN_TARGET")

    visiting: set[str] = set()
    done: set[str] = set()
    order: list[str] = []

    def visit(key: str) -> None:
        if key in visiting:
            raise CorpusFrontierError("CYCLIC_PROOF_DEPENDENCIES:" + key)
        if key in done:
            return
        visiting.add(key)
        for dep in parents[key]:
            visit(dep)
        visiting.remove(key)
        done.add(key)
        order.append(key)

    # Targets prioritize traversal, but never filter out any other proof source.
    for key in (*targets, *sorted(nodes)):
        visit(key)

    edges = sorted({(dep, key) for key, deps in parents.items() for dep in deps})
    result = {
        "schema": SCHEMA,
        "candidate_only": True,
        "canonical_vm81_admission": False,
        "proofs_newly_admitted": 0,
        "indexed_coverage_only": True,
        "selected_targets": list(targets),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": [nodes[key] for key in sorted(nodes)],
        "dependency_edges": [
            {"premise": a, "conclusion": b} for a, b in edges
        ],
        "complete_input_frontier_order": order,
        "source_proof_status_preserved": True,
        "source_course_admission_not_inferred": True,
        "rule_application_authority": "INHERITED_NATIVE_SYMBOLIC_PROOF_RULES_ONLY",
    }
    result["frontier_sha256"] = _digest(result)
    return result


def construct_from_repository(repo: Path) -> dict[str, Any]:
    """Run on two registered indexes; does not claim whole-repository coverage."""
    lemma_path = repo / "formal/lemmas/pass_144/LEMMA_CORPUS.json"
    course_path = repo / "contracts/pass220/HARMONICODE_COURSE_EXPANSION_INDEX_V1.json"
    return construct_frontier(
        lemma_corpora=(json.loads(lemma_path.read_text()),),
        course_indexes=(json.loads(course_path.read_text()),),
    )

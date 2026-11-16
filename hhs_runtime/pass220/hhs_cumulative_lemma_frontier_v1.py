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
    repository_dependency_graph: Mapping[str, Any] | None = None,
    targets: Iterable[str] = (),
) -> dict[str, Any]:
    """Traverse all supplied records, irrespective of selected attention targets.

    The original proof status is never promoted. Course index entries remain
    *source pointers*, not proof certificates. No inferred semantic edges.
    """
    nodes: dict[str, dict[str, Any]] = {}
    parents: dict[str, tuple[str, ...]] = {}
    source_edges: list[dict[str, Any]] = []
    source_graph_root: str | None = None

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

    if repository_dependency_graph is not None:
        graph = _record(repository_dependency_graph, "DEPENDENCY_GRAPH")
        roots = _record(graph.get("roots"), "DEPENDENCY_GRAPH_ROOTS")
        source_graph_root = roots.get("graph_root_hash216")
        if not isinstance(source_graph_root, str) or len(source_graph_root) != 216:
            raise CorpusFrontierError("INVALID_SOURCE_GRAPH_ROOT")
        files = graph.get("files")
        edges = graph.get("dependency_edges")
        if not isinstance(files, list) or not isinstance(edges, list):
            raise CorpusFrontierError("INVALID_SOURCE_GRAPH_ARRAYS")
        paths: set[str] = set()
        for file in files:
            file = _record(file, "INDEXED_FILE")
            source_path = file.get("path")
            identity = file.get("hash216")
            if (not isinstance(source_path, str) or not source_path
                    or source_path in paths or not isinstance(identity, str)
                    or len(identity) != 216):
                raise CorpusFrontierError("INVALID_OR_DUPLICATE_SOURCE_FILE")
            paths.add(source_path)
            key = "repo-file:" + source_path
            if key in nodes:
                raise CorpusFrontierError("DUPLICATE_GRAPH_NODE")
            nodes[key] = {
                "id": key, "kind": "INDEXED_REPOSITORY_FILE",
                "source_path": source_path, "source_hash216": identity,
                "source_git_blob": file.get("git_blob"),
                "source_record_sha256": _digest(file),
            }
            parents[key] = ()  # files have dependencies, NOT mathematical proof premises
        for edge in edges:
            edge = _record(edge, "SOURCE_DEPENDENCY_EDGE")
            origin, dest = edge.get("from"), edge.get("to")
            if origin not in paths or dest not in paths:
                raise CorpusFrontierError("MISSING_SOURCE_DEPENDENCY_ENDPOINT")
            source_edges.append({
                "from": origin, "to": dest, "type": edge.get("type"),
                "line": edge.get("line"), "hash216": edge.get("hash216"),
            })
        source_edges.sort(key=lambda e: (
            e["from"], e["to"], str(e["type"]),
            str(e["line"]), str(e["hash216"]),
        ))
        counts = graph.get("counts", {})
        if isinstance(counts, Mapping):
            expected_files = counts.get("content_bound_files")
            if expected_files is not None and expected_files != len(files):
                raise CorpusFrontierError("SOURCE_FILE_COUNT_MISMATCH")

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
        "source_dependency_edge_count": len(source_edges),
        "source_graph_root_hash216": source_graph_root,
        "source_dependency_edges": source_edges,
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
    """Bind existing complete indexed file graph and two mathematical indexes.

    An index is not automatically a proof census: other formal/corpus sources
    must still be bound through their existing registered paths.
    """
    lemma_path = repo / "formal/lemmas/pass_144/LEMMA_CORPUS.json"
    course_path = repo / "contracts/pass220/HARMONICODE_COURSE_EXPANSION_INDEX_V1.json"
    dependency_path = repo / "artifacts/repository_index/REPOSITORY_HASH216_DEPENDENCY_GRAPH.json"
    return construct_frontier(
        lemma_corpora=(json.loads(lemma_path.read_text()),),
        course_indexes=(json.loads(course_path.read_text()),),
        repository_dependency_graph=json.loads(dependency_path.read_text()),
    )

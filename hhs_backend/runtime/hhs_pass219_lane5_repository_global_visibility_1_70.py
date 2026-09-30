"""Pass 219 Lane 5 repository-global visibility hydration 1.70.

This successor makes repository visibility exhaustive for the bound source tree without
turning discovery metadata into execution or canonical authority.  Every tracked
repository object is visible to Lane 5, every statically discoverable top-level
callable is represented as a candidate, inherited 1.69 capability/constructor
nodes retain their evidence, and external branch/PR provenance can be hydrated as
typed unresolved state.

Visibility, composition, validation, admission, and mutation are deliberately
separate dimensions.
"""
from __future__ import annotations

import ast
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
from typing import Any, Mapping, Sequence

from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import (
    build_repository_hydration_knowledge_graph,
)
from hhs_runtime.pass191.repository_hydration import _hash216

SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_GLOBAL_VISIBILITY_1_70"
DB_SCHEMA = "HHS_PASS_219_LANE5_REPOSITORY_GLOBAL_VISIBILITY_DATABASE_1_70"
LANE5_GLOBAL_VISIBILITY_OPERATIONS = (
    "lane5.repository_global_visibility.status",
    "lane5.repository_global_visibility.search",
    "lane5.repository_global_visibility.neighbors",
)

SOURCE_SUFFIXES = {
    ".py": "python", ".pyi": "python",
    ".c": "c_cpp", ".h": "c_cpp", ".cc": "c_cpp", ".cpp": "c_cpp",
    ".cxx": "c_cpp", ".hpp": "c_cpp", ".hh": "c_cpp",
    ".js": "js_ts", ".mjs": "js_ts", ".cjs": "js_ts",
    ".jsx": "js_ts", ".ts": "js_ts", ".tsx": "js_ts",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
}
C_CPP_FUNCTION = re.compile(
    r"(?m)^[ \t]*(?!if\b|for\b|while\b|switch\b)"
    r"(?:[A-Za-z_][A-Za-z0-9_:<>,*& \t]+\s+)"
    r"([A-Za-z_][A-Za-z0-9_:]*)\s*\([^;{}]*\)\s*\{"
)
JS_TS_FUNCTION = re.compile(
    r"(?m)^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?"
    r"(?:function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\(|"
    r"class\s+([A-Za-z_$][A-Za-z0-9_$]*)\b)"
)
SHELL_FUNCTION = re.compile(
    r"(?m)^\s*(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\s*\))?\s*\{"
)


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point visibility metadata forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canon(value: Any) -> str:
    _reject_float(value)
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _h216(domain: str, payload: Any) -> str:
    identity = _hash216(domain, payload)
    if not isinstance(identity, str) or len(identity) != 216:
        raise ValueError(f"{domain} did not produce a 216-character Hash216 identity")
    return identity


def _files(dependency_graph: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = dependency_graph.get("files")
    if not isinstance(rows, list):
        raise ValueError("dependency graph files missing")
    out: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("file row must be a mapping")
        path = str(row.get("path", ""))
        identity = str(row.get("hash216", ""))
        if not path or len(identity) != 216 or path in out:
            raise ValueError("invalid or duplicate repository file identity")
        out[path] = row
    return out


def _safe_text(root: Path, path: str, size: object) -> str | None:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix not in SOURCE_SUFFIXES:
        return None
    try:
        if size is not None and int(size) > 8 * 1024 * 1024:
            return None
    except (TypeError, ValueError):
        pass
    target = (root / path).resolve()
    try:
        target.relative_to(root)
        raw = target.read_bytes()
    except (OSError, ValueError):
        return None
    if b"\0" in raw:
        return None
    return raw.decode("utf-8", "surrogateescape")


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _visibility_fields(
    *, composition_state: str, validation_state: str, closure_state: str
) -> dict[str, Any]:
    return {
        "visible_to_lane5": True,
        "visibility_state": "VISIBLE",
        "composition_state": composition_state,
        "validation_state": validation_state,
        "closure_state": closure_state,
        "admission_state": "NOT_CANONICALLY_ADMITTED",
        "canonical_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "classification_is_visibility_filter": False,
        "configuration_state": "NOT_INFERRED",
        "adapter_state": "NOT_INFERRED",
        "candidate_only": True,
    }


def _repository_object(path: str, row: Mapping[str, Any]) -> dict[str, Any]:
    suffix = PurePosixPath(path).suffix.lower()
    body = {
        "node_id": f"repository-object:{path}",
        "node_kind": "REPOSITORY_OBJECT",
        "name": PurePosixPath(path).name,
        "source_path": path,
        "source_file_hash216": str(row["hash216"]),
        "git_blob": str(row.get("git_blob", "")),
        "language": str(row.get("language", "")),
        "disposition": str(row.get("disposition", "")),
        "origin": str(row.get("origin", "")),
        "capability_candidate": suffix in SOURCE_SUFFIXES,
        **_visibility_fields(
            composition_state="UNRESOLVED",
            validation_state="OBSERVED_IN_BOUND_REPOSITORY_TREE",
            closure_state="UNRESOLVED",
        ),
    }
    body["hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-REPOSITORY-OBJECT-1.70", body
    )
    return body


def _callable_node(
    *, path: str, name: str, line: int, language: str,
    callable_kind: str, evidence: Sequence[str]
) -> dict[str, Any]:
    body = {
        "node_id": f"callable:{language}:{path}#{name}:{int(line)}",
        "node_kind": "DISCOVERED_CALLABLE",
        "name": name,
        "symbol": name,
        "source_path": path,
        "line": int(line),
        "language": language,
        "callable_kind": callable_kind,
        "discovery_evidence": sorted(set(str(item) for item in evidence)),
        **_visibility_fields(
            composition_state="UNRESOLVED",
            validation_state="STATICALLY_DISCOVERED",
            closure_state="UNRESOLVED",
        ),
    }
    body["hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-CALLABLE-1.70", body
    )
    return body


def discover_repository_callable_candidates(
    repo_root: str | Path,
    dependency_graph: Mapping[str, Any],
) -> list[dict[str, Any]]:
    root = Path(repo_root).resolve()
    files = _files(dependency_graph)
    found: dict[str, dict[str, Any]] = {}
    for path, row in sorted(files.items()):
        suffix = PurePosixPath(path).suffix.lower()
        language = SOURCE_SUFFIXES.get(suffix)
        text = _safe_text(root, path, row.get("size_bytes"))
        if not language or text is None:
            continue

        nodes: list[dict[str, Any]] = []
        if language == "python":
            try:
                tree = ast.parse(text, filename=path)
            except (SyntaxError, ValueError):
                tree = None
            if tree is not None:
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        nodes.append(_callable_node(
                            path=path, name=node.name, line=node.lineno,
                            language=language, callable_kind="PYTHON_CLASS",
                            evidence=("AST_TOP_LEVEL_CLASS",),
                        ))
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        nodes.append(_callable_node(
                            path=path, name=node.name, line=node.lineno,
                            language=language, callable_kind="PYTHON_FUNCTION",
                            evidence=("AST_TOP_LEVEL_FUNCTION",),
                        ))
        elif language == "c_cpp":
            for match in C_CPP_FUNCTION.finditer(text):
                nodes.append(_callable_node(
                    path=path, name=match.group(1), line=_line(text, match.start()),
                    language=language, callable_kind="C_CPP_FUNCTION_DEFINITION",
                    evidence=("STATIC_FUNCTION_DEFINITION",),
                ))
        elif language == "js_ts":
            for match in JS_TS_FUNCTION.finditer(text):
                name = match.group(1) or match.group(2)
                nodes.append(_callable_node(
                    path=path, name=name, line=_line(text, match.start()),
                    language=language,
                    callable_kind="JS_TS_FUNCTION" if match.group(1) else "JS_TS_CLASS",
                    evidence=("STATIC_TOP_LEVEL_DECLARATION",),
                ))
        elif language == "shell":
            for match in SHELL_FUNCTION.finditer(text):
                nodes.append(_callable_node(
                    path=path, name=match.group(1), line=_line(text, match.start()),
                    language=language, callable_kind="SHELL_FUNCTION",
                    evidence=("STATIC_SHELL_FUNCTION",),
                ))

        for node in nodes:
            node_id = str(node["node_id"])
            if node_id in found and found[node_id] != node:
                raise ValueError(f"callable identity collision: {node_id}")
            found[node_id] = node
    return [found[key] for key in sorted(found)]


def _inherit_1_69_node(raw: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(raw)
    source_hash216 = str(source.pop("hash216"))
    node_kind = str(source.get("node_kind", ""))
    if node_kind not in {"CAPABILITY", "CONSTRUCTOR"}:
        raise ValueError("unsupported inherited 1.69 node kind")
    body = {
        **source,
        "source_1_69_hash216": source_hash216,
        **_visibility_fields(
            composition_state="TYPED_CANDIDATE",
            validation_state="INHERITED_1_69_DISCOVERY_EVIDENCE",
            closure_state="UNRESOLVED",
        ),
    }
    body["hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-INHERITED-1.70", body
    )
    return body


def _provenance_class(raw: Mapping[str, Any]) -> str:
    explicit = str(raw.get("provenance_class", "")).strip().upper()
    if explicit:
        return explicit
    kind = str(raw.get("ref_kind", "")).strip().upper()
    state = str(raw.get("state", "")).strip().upper()
    merged = bool(raw.get("merged"))
    green = bool(raw.get("checks_green"))
    if merged and green:
        return "MERGED_GREEN"
    if merged:
        return "MERGED"
    if kind in {"PULL_REQUEST", "PR"} and state == "OPEN" and green:
        return "OPEN_GREEN_PR"
    if kind in {"PULL_REQUEST", "PR"} and state == "OPEN":
        return "OPEN_UNTESTED_PR"
    if kind == "BRANCH":
        return "BRANCH_REF"
    return "SOURCE_ONLY"


def _provenance_states(provenance_class: str) -> tuple[str, str, str]:
    if provenance_class == "MERGED_GREEN":
        return "ELIGIBLE", "INHERITED_GREEN", "INHERITED_CLOSED"
    if provenance_class == "OPEN_GREEN_PR":
        return "ELIGIBLE_CANDIDATE", "GREEN_CANDIDATE", "UNRESOLVED"
    if provenance_class == "MERGED":
        return "UNRESOLVED", "MERGED_UNVERIFIED", "UNRESOLVED"
    return "UNRESOLVED", "UNRESOLVED", "UNRESOLVED"


def _provenance_node(raw: Mapping[str, Any]) -> dict[str, Any]:
    provenance_class = _provenance_class(raw)
    composition, validation, closure = _provenance_states(provenance_class)
    ref_kind = str(raw.get("ref_kind", "UNKNOWN")).strip().upper() or "UNKNOWN"
    ref_name = str(raw.get("ref_name", "")).strip()
    head_sha = str(raw.get("head_sha", "")).strip()
    if not ref_name and not head_sha:
        raise ValueError("provenance record requires ref_name or head_sha")
    declared_metadata = dict(raw.get("declared_metadata") or {})
    _reject_float(declared_metadata)
    explicit_non_exec = bool(raw.get("explicit_non_executable_evidence"))
    if explicit_non_exec:
        composition = "DECLARED_NON_EXECUTABLE"
    body = {
        "node_id": f"provenance:{ref_kind.lower()}:{ref_name or head_sha}",
        "node_kind": "REPOSITORY_PROVENANCE",
        "name": ref_name or head_sha,
        "ref_kind": ref_kind,
        "ref_name": ref_name,
        "head_sha": head_sha,
        "base_sha": str(raw.get("base_sha", "")),
        "merge_commit_sha": str(raw.get("merge_commit_sha", "")),
        "pr_number": int(raw.get("pr_number") or 0),
        "state": str(raw.get("state", "")),
        "provenance_class": provenance_class,
        "declared_metadata": declared_metadata,
        "explicit_non_executable_evidence": explicit_non_exec,
        "dependency_touch_invalidates_inherited_green": True,
        **_visibility_fields(
            composition_state=composition,
            validation_state=validation,
            closure_state=closure,
        ),
    }
    if explicit_non_exec:
        body["composition_state"] = "DECLARED_NON_EXECUTABLE"
    body["hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-PROVENANCE-1.70", body
    )
    return body


def _edge(
    source: Mapping[str, Any],
    relation_type: str,
    *, target: Mapping[str, Any] | None = None,
    target_file_path: str | None = None,
    evidence: Sequence[str] = (),
) -> dict[str, Any]:
    body = {
        "source_node_id": str(source["node_id"]),
        "source_hash216": str(source["hash216"]),
        "relation_type": relation_type,
        "visible_to_lane5": True,
        "candidate_only": True,
        "canonical_mutation_authority": False,
        "evidence": sorted(set(str(item) for item in evidence)),
    }
    if target is not None:
        body["target_node_id"] = str(target["node_id"])
        body["target_hash216"] = str(target["hash216"])
    if target_file_path is not None:
        body["target_file_path"] = target_file_path
    if target is None and target_file_path is None:
        raise ValueError("visibility edge requires target node or file")
    body["hash216"] = _h216(
        "HHS-P219-LANE5-GLOBAL-VISIBILITY-EDGE-1.70", body
    )
    return body


def build_repository_global_visibility_graph(
    repo_root: str | Path,
    dependency_graph: Mapping[str, Any],
    *,
    lane5_snapshot: Mapping[str, Any] | None = None,
    provenance_records: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    files = _files(dependency_graph)
    base = build_repository_hydration_knowledge_graph(
        repo_root, dependency_graph, lane5_snapshot=lane5_snapshot
    )

    repository_objects = [
        _repository_object(path, row) for path, row in sorted(files.items())
    ]
    inherited_capabilities = [_inherit_1_69_node(node) for node in base["capabilities"]]
    inherited_constructors = [_inherit_1_69_node(node) for node in base["constructors"]]
    callables = discover_repository_callable_candidates(repo_root, dependency_graph)
    raw_provenance = list(provenance_records or ())
    provenance = [_provenance_node(record) for record in sorted(
        raw_provenance,
        key=lambda item: (
            str(item.get("ref_kind", "")),
            str(item.get("ref_name", "")),
            str(item.get("head_sha", "")),
        ),
    )]

    nodes = repository_objects + inherited_capabilities + inherited_constructors + callables + provenance
    node_ids = [str(node["node_id"]) for node in nodes]
    node_hashes = [str(node["hash216"]) for node in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("global visibility node-id collision")
    if len(node_hashes) != len(set(node_hashes)):
        raise ValueError("global visibility Hash216 collision")

    objects_by_path = {str(node["source_path"]): node for node in repository_objects}
    typed_by_path_name: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for node in inherited_capabilities + inherited_constructors:
        path = node.get("source_path")
        if isinstance(path, str) and path:
            typed_by_path_name.setdefault((path, str(node.get("name", ""))), []).append(node)

    edges: list[dict[str, Any]] = []
    for node in inherited_capabilities + inherited_constructors + callables:
        path = node.get("source_path")
        if isinstance(path, str) and path in objects_by_path:
            edges.append(_edge(
                node, "DECLARED_IN_REPOSITORY_OBJECT",
                target=objects_by_path[path],
                evidence=("SOURCE_PATH_BINDING",),
            ))
    for callable_node in callables:
        key = (str(callable_node.get("source_path", "")), str(callable_node.get("name", "")))
        for typed in typed_by_path_name.get(key, []):
            edges.append(_edge(
                callable_node, "STATIC_DISCOVERY_ALIGNS_WITH_TYPED_NODE",
                target=typed,
                evidence=("SAME_SOURCE_PATH", "SAME_SYMBOL_NAME"),
            ))
    provenance_by_identity = {
        (str(node["ref_kind"]), str(node["ref_name"]), str(node["head_sha"])): node
        for node in provenance
    }
    for record in raw_provenance:
        node = provenance_by_identity[
            (
                str(record.get("ref_kind", "UNKNOWN")).strip().upper() or "UNKNOWN",
                str(record.get("ref_name", "")).strip(),
                str(record.get("head_sha", "")).strip(),
            )
        ]
        for path in sorted(set(str(p) for p in (record.get("source_paths") or ()))):
            if path in objects_by_path:
                edges.append(_edge(
                    node, "PROVENANCE_TOUCHES_REPOSITORY_OBJECT",
                    target=objects_by_path[path],
                    evidence=("EXPLICIT_PROVENANCE_SOURCE_PATH",),
                ))

    edges.sort(key=lambda edge: (
        str(edge["source_node_id"]),
        str(edge["relation_type"]),
        str(edge.get("target_node_id", edge.get("target_file_path", ""))),
    ))
    if len({str(edge["hash216"]) for edge in edges}) != len(edges):
        raise ValueError("global visibility edge Hash216 collision")

    roots = {
        "repository_object_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-REPOSITORY-ROOT-1.70",
            [node["hash216"] for node in repository_objects],
        ),
        "typed_node_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-TYPED-ROOT-1.70",
            [node["hash216"] for node in inherited_capabilities + inherited_constructors],
        ),
        "callable_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-CALLABLE-ROOT-1.70",
            [node["hash216"] for node in callables],
        ),
        "provenance_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-PROVENANCE-ROOT-1.70",
            [node["hash216"] for node in provenance],
        ),
        "edge_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-EDGE-ROOT-1.70",
            [edge["hash216"] for edge in edges],
        ),
    }
    counts = {
        "repository_objects": len(repository_objects),
        "typed_capabilities": len(inherited_capabilities),
        "typed_constructors": len(inherited_constructors),
        "discovered_callables": len(callables),
        "provenance_nodes": len(provenance),
        "visibility_nodes": len(nodes),
        "visibility_edges": len(edges),
    }
    core = {
        "schema": SCHEMA,
        "version": 1,
        "source_commit": str(dependency_graph.get("source_commit", "")),
        "source_tree": str(dependency_graph.get("source_tree", "")),
        "source_1_69_projection_root_hash216": str(base["roots"]["projection_root_hash216"]),
        "counts": counts,
        "scope": {
            "bound_repository_tracked_file_visibility_complete": len(repository_objects) == len(files),
            "bound_repository_static_top_level_callable_scan_complete": True,
            "external_ref_provenance_supplied": bool(provenance),
            "external_ref_content_scan_complete": False,
            "repository_total_historical_capability_complete": False,
        },
        "authority": {
            "lane5_is_pass219_composition_manifold": True,
            "visibility_filtering_allowed": False,
            "classification_metadata_can_hide_nodes": False,
            "unresolved_state_remains_visible": True,
            "configuration_or_adapter_requirement_requires_evidence": True,
            "visibility_implies_composition": False,
            "composition_implies_validation": False,
            "validation_implies_admission": False,
            "admission_implies_mutation_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
            "signed_environmental_vm81_admission_required_for_mutation": True,
        },
        "roots": roots,
        "repository_objects": repository_objects,
        "capabilities": inherited_capabilities,
        "constructors": inherited_constructors,
        "callables": callables,
        "provenance": provenance,
        "edges": edges,
    }
    roots["projection_root_hash216"] = _h216(
        "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-ROOT-1.70",
        {
            "source_commit": core["source_commit"],
            "source_tree": core["source_tree"],
            "source_1_69_projection_root_hash216": core["source_1_69_projection_root_hash216"],
            "counts": counts,
            "scope": core["scope"],
            "authority": core["authority"],
            "roots": dict(roots),
        },
    )
    return core


def _verify_projection(projection: Mapping[str, Any]) -> None:
    if projection.get("schema") != SCHEMA:
        raise ValueError("global visibility schema mismatch")
    authority = projection.get("authority")
    if not isinstance(authority, Mapping):
        raise ValueError("global visibility authority missing")
    if authority.get("visibility_filtering_allowed") is not False:
        raise ValueError("visibility filtering must remain forbidden")
    for key in (
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "canonical_persistence_authority",
    ):
        if authority.get(key) is not False:
            raise ValueError(f"authority escalation: {key}")

    collections = (
        projection.get("repository_objects"),
        projection.get("capabilities"),
        projection.get("constructors"),
        projection.get("callables"),
        projection.get("provenance"),
        projection.get("edges"),
    )
    if not all(isinstance(value, list) for value in collections):
        raise ValueError("global visibility collections missing")

    node_domains = {
        "REPOSITORY_OBJECT": "HHS-P219-LANE5-GLOBAL-VISIBILITY-REPOSITORY-OBJECT-1.70",
        "CAPABILITY": "HHS-P219-LANE5-GLOBAL-VISIBILITY-INHERITED-1.70",
        "CONSTRUCTOR": "HHS-P219-LANE5-GLOBAL-VISIBILITY-INHERITED-1.70",
        "DISCOVERED_CALLABLE": "HHS-P219-LANE5-GLOBAL-VISIBILITY-CALLABLE-1.70",
        "REPOSITORY_PROVENANCE": "HHS-P219-LANE5-GLOBAL-VISIBILITY-PROVENANCE-1.70",
    }
    nodes = (
        list(projection["repository_objects"])
        + list(projection["capabilities"])
        + list(projection["constructors"])
        + list(projection["callables"])
        + list(projection["provenance"])
    )
    for node in nodes:
        if node.get("visible_to_lane5") is not True:
            raise ValueError("invisible node in global visibility projection")
        body = dict(node)
        claimed = str(body.pop("hash216", ""))
        domain = node_domains.get(str(node.get("node_kind", "")))
        if not domain or claimed != _h216(domain, body):
            raise ValueError(f"global visibility node Hash216 mismatch: {node.get('node_id')}")
    for edge in projection["edges"]:
        body = dict(edge)
        claimed = str(body.pop("hash216", ""))
        if claimed != _h216("HHS-P219-LANE5-GLOBAL-VISIBILITY-EDGE-1.70", body):
            raise ValueError("global visibility edge Hash216 mismatch")

    roots = projection.get("roots")
    if not isinstance(roots, Mapping):
        raise ValueError("global visibility roots missing")
    expected = {
        "repository_object_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-REPOSITORY-ROOT-1.70",
            [node["hash216"] for node in projection["repository_objects"]],
        ),
        "typed_node_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-TYPED-ROOT-1.70",
            [node["hash216"] for node in projection["capabilities"] + projection["constructors"]],
        ),
        "callable_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-CALLABLE-ROOT-1.70",
            [node["hash216"] for node in projection["callables"]],
        ),
        "provenance_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-PROVENANCE-ROOT-1.70",
            [node["hash216"] for node in projection["provenance"]],
        ),
        "edge_root_hash216": _h216(
            "HHS-P219-LANE5-GLOBAL-VISIBILITY-EDGE-ROOT-1.70",
            [edge["hash216"] for edge in projection["edges"]],
        ),
    }
    for key, value in expected.items():
        if roots.get(key) != value:
            raise ValueError(f"global visibility aggregate root mismatch: {key}")
    projection_root = _h216(
        "HHS-P219-LANE5-REPOSITORY-GLOBAL-VISIBILITY-ROOT-1.70",
        {
            "source_commit": projection.get("source_commit"),
            "source_tree": projection.get("source_tree"),
            "source_1_69_projection_root_hash216": projection.get("source_1_69_projection_root_hash216"),
            "counts": projection.get("counts"),
            "scope": projection.get("scope"),
            "authority": projection.get("authority"),
            "roots": expected,
        },
    )
    if roots.get("projection_root_hash216") != projection_root:
        raise ValueError("global visibility projection root Hash216 mismatch")


class Lane5RepositoryGlobalVisibilityDatabase:
    """Restartable Hash216-positioned vector index for 1.70 visibility state."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.database_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS visibility_nodes(
            node_id TEXT PRIMARY KEY,node_hash216 TEXT NOT NULL UNIQUE,
            node_kind TEXT NOT NULL,name TEXT NOT NULL,source_path TEXT,
            visibility_state TEXT NOT NULL,composition_state TEXT NOT NULL,
            validation_state TEXT NOT NULL,closure_state TEXT NOT NULL,
            payload_json TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS visibility_kind_name ON visibility_nodes(node_kind,name);
        CREATE INDEX IF NOT EXISTS visibility_source ON visibility_nodes(source_path,node_kind);
        CREATE TABLE IF NOT EXISTS visibility_edges(
            edge_hash216 TEXT PRIMARY KEY,
            source_node_id TEXT NOT NULL REFERENCES visibility_nodes(node_id),
            target_node_id TEXT,target_file_path TEXT,relation_type TEXT NOT NULL,
            payload_json TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS visibility_edge_source ON visibility_edges(source_node_id,relation_type);
        CREATE TABLE IF NOT EXISTS hash216_positions(
            owner_hash216 TEXT NOT NULL,owner_kind TEXT NOT NULL,
            ordinal INTEGER NOT NULL,lane INTEGER NOT NULL,lane_offset INTEGER NOT NULL,
            symbol TEXT NOT NULL,symbol_sha256 TEXT NOT NULL,
            PRIMARY KEY(owner_hash216,ordinal));
        CREATE TABLE IF NOT EXISTS hydration_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        """)
        self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self.db.close()

    @staticmethod
    def _positions(identity: str, kind: str):
        if len(identity) != 216:
            raise ValueError("Hash216 position index requires 216 characters")
        return [
            (identity,kind,ordinal,ordinal//72,ordinal%72,symbol,sha256(symbol.encode("utf-8")).hexdigest())
            for ordinal,symbol in enumerate(identity)
        ]

    def hydrate(self, visibility_projection: Mapping[str, Any]) -> dict[str, Any]:
        _verify_projection(visibility_projection)
        nodes = (
            list(visibility_projection["repository_objects"])
            + list(visibility_projection["capabilities"])
            + list(visibility_projection["constructors"])
            + list(visibility_projection["callables"])
            + list(visibility_projection["provenance"])
        )
        edges = list(visibility_projection["edges"])
        with self.db:
            for table in ("hash216_positions","visibility_edges","visibility_nodes","hydration_metadata"):
                self.db.execute(f"DELETE FROM {table}")
            self.db.executemany(
                "INSERT INTO visibility_nodes VALUES(?,?,?,?,?,?,?,?,?,?)",
                [
                    (
                        str(node["node_id"]),str(node["hash216"]),str(node["node_kind"]),
                        str(node.get("name",node["node_id"])),node.get("source_path"),
                        str(node["visibility_state"]),str(node["composition_state"]),
                        str(node["validation_state"]),str(node["closure_state"]),_canon(node),
                    )
                    for node in nodes
                ],
            )
            self.db.executemany(
                "INSERT INTO visibility_edges VALUES(?,?,?,?,?,?)",
                [
                    (
                        str(edge["hash216"]),str(edge["source_node_id"]),
                        edge.get("target_node_id"),edge.get("target_file_path"),
                        str(edge["relation_type"]),_canon(edge),
                    )
                    for edge in edges
                ],
            )
            for node in nodes:
                self.db.executemany(
                    "INSERT INTO hash216_positions VALUES(?,?,?,?,?,?,?)",
                    self._positions(str(node["hash216"]),str(node["node_kind"])),
                )
            for edge in edges:
                self.db.executemany(
                    "INSERT INTO hash216_positions VALUES(?,?,?,?,?,?,?)",
                    self._positions(str(edge["hash216"]),"VISIBILITY_EDGE"),
                )
            metadata = {
                "schema": DB_SCHEMA,
                "source_commit": str(visibility_projection.get("source_commit","")),
                "projection_root_hash216": str(visibility_projection["roots"]["projection_root_hash216"]),
                "restart_rehydratable": "true",
                "visibility_filtering_allowed": "false",
                "canonical_mutation_authority": "false",
            }
            self.db.executemany("INSERT INTO hydration_metadata VALUES(?,?)", sorted(metadata.items()))
        return self.status()

    def status(self) -> dict[str, Any]:
        synchronous = int(self.db.execute("PRAGMA synchronous").fetchone()[0])
        return {
            "schema": DB_SCHEMA,
            "database_path": str(self.database_path),
            "visibility_nodes": int(self.db.execute("SELECT COUNT(*) FROM visibility_nodes").fetchone()[0]),
            "visibility_edges": int(self.db.execute("SELECT COUNT(*) FROM visibility_edges").fetchone()[0]),
            "hash216_positions": int(self.db.execute("SELECT COUNT(*) FROM hash216_positions").fetchone()[0]),
            "journal_mode": str(self.db.execute("PRAGMA journal_mode").fetchone()[0]),
            "synchronous_full": synchronous == 2,
            "restart_rehydratable": True,
            "visibility_filtering_allowed": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
            "canonical_persistence_authority": False,
        }

    def search(
        self, text: str, *, kinds: Sequence[str] | None = None, limit: int = 128
    ) -> list[dict[str, Any]]:
        query = text.strip()
        if not query or limit <= 0 or limit > 1024:
            raise ValueError("invalid bounded visibility search")
        like = f"%{query}%"
        args: list[Any] = [like,like,like]
        kind_sql = ""
        if kinds:
            canonical = tuple(sorted(set(str(kind) for kind in kinds)))
            if not canonical:
                raise ValueError("invalid kind filter")
            kind_sql = " AND node_kind IN (" + ",".join("?" for _ in canonical) + ")"
            args.extend(canonical)
        args.append(int(limit))
        rows = self.db.execute(
            "SELECT * FROM visibility_nodes "
            "WHERE (name LIKE ? OR node_id LIKE ? OR COALESCE(source_path,'') LIKE ?)"
            + kind_sql + " ORDER BY node_kind,name,node_id LIMIT ?",
            tuple(args),
        ).fetchall()
        return [
            {
                "node_id":str(row["node_id"]),"hash216":str(row["node_hash216"]),
                "node_kind":str(row["node_kind"]),"name":str(row["name"]),
                "source_path":row["source_path"],
                "visibility_state":str(row["visibility_state"]),
                "composition_state":str(row["composition_state"]),
                "validation_state":str(row["validation_state"]),
                "closure_state":str(row["closure_state"]),
                "payload":json.loads(str(row["payload_json"])),
            }
            for row in rows
        ]

    def neighbors(self, node_id: str, *, limit: int = 512) -> list[dict[str, Any]]:
        if limit <= 0 or limit > 4096:
            raise ValueError("invalid neighbor limit")
        rows = self.db.execute(
            "SELECT * FROM visibility_edges WHERE source_node_id=? OR target_node_id=? "
            "ORDER BY relation_type,edge_hash216 LIMIT ?",
            (node_id,node_id,int(limit)),
        ).fetchall()
        return [
            {
                "hash216":str(row["edge_hash216"]),
                "source_node_id":str(row["source_node_id"]),
                "target_node_id":row["target_node_id"],
                "target_file_path":row["target_file_path"],
                "relation_type":str(row["relation_type"]),
                "payload":json.loads(str(row["payload_json"])),
            }
            for row in rows
        ]


def discover_local_ref_provenance(repo_root: str | Path) -> list[dict[str, Any]]:
    """Observe already-fetched local Git refs without checking out or executing them."""
    root = Path(repo_root).resolve()
    command = [
        "git","-C",str(root),"for-each-ref",
        "--format=%(refname)%09%(objectname)",
        "refs/remotes/origin","refs/remotes/pull",
    ]
    try:
        output = subprocess.check_output(command,text=True,stderr=subprocess.DEVNULL)
    except (OSError,subprocess.CalledProcessError):
        return []
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        if "\t" not in line:
            continue
        ref_name,head_sha = line.split("\t",1)
        if ref_name.endswith("/HEAD"):
            continue
        if ref_name.startswith("refs/remotes/pull/"):
            kind,state = "PULL_REQUEST","UNKNOWN"
        else:
            kind,state = "BRANCH","OBSERVED"
        records.append({
            "ref_kind":kind,
            "ref_name":ref_name,
            "head_sha":head_sha,
            "state":state,
            "declared_metadata":{
                "source":"LOCAL_FETCHED_GIT_REF",
                "content_executed":False,
            },
        })
    return sorted(records,key=lambda item:(item["ref_kind"],item["ref_name"]))


__all__ = [
    "DB_SCHEMA",
    "LANE5_GLOBAL_VISIBILITY_OPERATIONS",
    "Lane5RepositoryGlobalVisibilityDatabase",
    "SCHEMA",
    "build_repository_global_visibility_graph",
    "discover_local_ref_provenance",
    "discover_repository_callable_candidates",
]

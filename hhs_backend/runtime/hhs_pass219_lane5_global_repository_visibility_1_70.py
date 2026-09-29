"""Pass 219 Lane 5 global repository visibility successor 1.70.

This module implements the inherited Pass 219 global-visibility law as a
read-only Hash216 projection. Discovery precedes classification: repository
files, inherited capability records, and static branch/PR ref deltas remain
visible to Lane 5 regardless of demo/example/reference/candidate/ready/enabled
metadata. Visibility does not grant execution, validation, admission, mutation,
receipt-minting, or persistence authority.

Non-main Git refs are inspected only through Git object metadata/diffs. Their
Python, native, workflow, or other source is never imported or executed.
"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
from typing import Any, Mapping, Sequence

from hhs_runtime.pass191.repository_hydration import _hash216

SCHEMA = "HHS_PASS_219_LANE5_GLOBAL_REPOSITORY_VISIBILITY_1_70"
VERSION = 1
MAX_REFS = 4096
MAX_REF_DELTA_NODES = 200000

_CLASSIFICATION_KEYS = {
    "demo",
    "example",
    "reference",
    "candidate_only",
    "enabled",
    "ready",
    "disabled",
    "deprecated",
    "needs_adapter",
    "adapter_required",
    "needs_configuration",
    "configuration_required",
    "execution_authority",
    "hash216_composition_eligible",
    "superedge_promotion_eligible",
}


def _reject_float(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise ValueError(f"floating-point visibility metadata forbidden at {path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _h216(domain: str, payload: Any) -> str:
    _reject_float(payload)
    identity = _hash216(domain, payload)
    if not isinstance(identity, str) or len(identity) != 216:
        raise ValueError(f"{domain} did not produce a 216-character Hash216 identity")
    return identity


def _git(root: Path, *args: str, text: bool = True) -> str | bytes:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=text,
        stderr=subprocess.DEVNULL,
    )


def _git_text(root: Path, *args: str) -> str:
    return str(_git(root, *args, text=True)).strip()


def _declared_classification(raw: Mapping[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in raw.items():
        normalized = str(key).casefold()
        if normalized in _CLASSIFICATION_KEYS:
            if isinstance(value, (str, int, bool)) or value is None:
                out[str(key)] = value
    return dict(sorted(out.items()))


def _authority() -> dict[str, bool]:
    return {
        "candidate_projection_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "pqc_key_authority": False,
        "receipt_clock_authority": False,
        "automatic_hash216_composition_promotion": False,
        "automatic_superedge_promotion": False,
    }


def _base_fields(
    *,
    node_id: str,
    node_kind: str,
    source_state: str,
    source_ref: str,
    source_commit: str,
    source_path: str | None,
    closure_state: str,
    validation_state: str,
    executability_state: str = "UNRESOLVED",
    declared_classification: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_kind": node_kind,
        "source_state": source_state,
        "source_ref": source_ref,
        "source_commit": source_commit,
        "source_path": source_path,
        "lane5_visible": True,
        "visibility_filter_allowed": False,
        "closure_state": closure_state,
        "validation_state": validation_state,
        "executability_state": executability_state,
        "configuration_requirement_state": "UNRESOLVED",
        "adapter_requirement_state": "UNRESOLVED",
        "declared_classification": dict(declared_classification or {}),
        "non_executable_evidence": [],
        "configuration_requirement_evidence": [],
        "adapter_requirement_evidence": [],
        "lane5_selection_authority": "INHERITED_PASS219_OPTIMIZER",
        "runtime_validation_required_for_execution": True,
        **_authority(),
    }


def _seal(node: dict[str, Any], domain: str) -> dict[str, Any]:
    body = dict(node)
    body["hash216"] = _h216(domain, body)
    return body


def _main_file_nodes(
    dependency_graph: Mapping[str, Any],
    *,
    source_commit: str,
) -> list[dict[str, Any]]:
    rows = dependency_graph.get("files")
    if not isinstance(rows, list):
        raise ValueError("dependency graph files missing")
    nodes: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("dependency graph file row must be a mapping")
        path = str(row.get("path") or "")
        subject_hash216 = str(row.get("hash216") or "")
        if not path or len(subject_hash216) != 216:
            raise ValueError("invalid repository file visibility source")
        node = _base_fields(
            node_id=f"visibility:main-file:{path}",
            node_kind="REPOSITORY_FILE_SURFACE",
            source_state="BOUND_MAIN_REPOSITORY",
            source_ref="HEAD",
            source_commit=source_commit,
            source_path=path,
            closure_state="SOURCE_TREE_BOUND",
            validation_state="SOURCE_OBSERVED",
        )
        node.update(
            {
                "subject_hash216": subject_hash216,
                "git_blob": str(row.get("git_blob") or ""),
                "language": str(row.get("language") or ""),
                "disposition": str(row.get("disposition") or ""),
                "origin": str(row.get("origin") or ""),
            }
        )
        nodes.append(
            _seal(
                node,
                "HHS-P219-LANE5-GLOBAL-VISIBILITY-MAIN-FILE-1.70",
            )
        )
    return nodes


def _capability_nodes(
    lane5_snapshot: Mapping[str, Any],
    *,
    source_commit: str,
) -> list[dict[str, Any]]:
    rows = lane5_snapshot.get("nodes")
    if not isinstance(rows, list):
        raise ValueError("Lane 5 capability snapshot nodes missing")
    nodes: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("Lane 5 capability visibility row must be a mapping")
        raw_id = str(raw.get("node_id") or "")
        if not raw_id:
            raise ValueError("Lane 5 capability visibility row missing node_id")
        path_value = raw.get("path") or raw.get("declaring_header")
        source_path = str(path_value) if path_value else None
        node = _base_fields(
            node_id=f"visibility:capability:{raw_id}",
            node_kind="CAPABILITY_SURFACE",
            source_state="INHERITED_PASS219_REVERSE_DISCOVERY",
            source_ref="HEAD",
            source_commit=source_commit,
            source_path=source_path,
            closure_state="REVERSE_DISCOVERY_OBSERVED",
            validation_state="INHERITED_EVIDENCE_PRESENT",
            declared_classification=_declared_classification(raw),
        )
        node.update(
            {
                "repository_capability_node_id": raw_id,
                "source_kind": str(raw.get("source_kind") or ""),
                "authority_class": int(raw.get("authority_class") or 0),
                "entry_signature64": int(raw.get("entry_signature64") or 0),
                "operation_key": str(raw.get("operation_key") or ""),
                "export_name": str(raw.get("export_name") or ""),
                "capability_id": str(raw.get("capability_id") or ""),
                "raw_name": str(raw.get("raw_name") or ""),
            }
        )
        nodes.append(
            _seal(
                node,
                "HHS-P219-LANE5-GLOBAL-VISIBILITY-CAPABILITY-1.70",
            )
        )
    return nodes


def discover_repository_refs(repo_root: str | Path) -> list[tuple[str, str]]:
    root = Path(repo_root).resolve()
    output = _git_text(
        root,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)",
        "refs/heads",
        "refs/remotes/origin",
        "refs/remotes/pull",
    )
    rows: list[tuple[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        ref, commit = line.split("\t", 1)
        if ref.endswith("/HEAD"):
            continue
        rows.append((ref, commit))
    rows.sort()
    if len(rows) > MAX_REFS:
        raise RuntimeError(
            f"repository ref visibility exceeds complete-scan bound: {len(rows)} > {MAX_REFS}"
        )
    return rows


def _resolve_refs(
    root: Path,
    ref_names: Sequence[str] | None,
) -> list[tuple[str, str]]:
    if ref_names is None:
        return discover_repository_refs(root)
    rows: list[tuple[str, str]] = []
    for ref in sorted(dict.fromkeys(str(value) for value in ref_names)):
        commit = _git_text(root, "rev-parse", f"{ref}^{{commit}}")
        rows.append((ref, commit))
    if len(rows) > MAX_REFS:
        raise RuntimeError(
            f"repository ref visibility exceeds complete-scan bound: {len(rows)} > {MAX_REFS}"
        )
    return rows


def _provenance_state(ref: str) -> str:
    if ref.startswith("refs/remotes/pull/"):
        return "PULL_REQUEST_REF"
    if ref.startswith("refs/remotes/origin/"):
        return "REMOTE_BRANCH_REF"
    if ref.startswith("refs/heads/"):
        return "LOCAL_BRANCH_REF"
    return "GIT_REF"


def _diff_rows(root: Path, base: str, ref: str) -> list[tuple[str, str, str | None]]:
    raw = bytes(
        _git(
            root,
            "diff",
            "--name-status",
            "-z",
            "-M",
            base,
            ref,
            "--",
            text=False,
        )
    )
    parts = raw.decode("utf-8", "surrogateescape").split("\0")
    if parts and parts[-1] == "":
        parts.pop()
    rows: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(parts):
        status = parts[index]
        index += 1
        if not status:
            continue
        if status.startswith(("R", "C")):
            if index + 1 >= len(parts):
                raise RuntimeError("malformed git rename/copy visibility diff")
            old_path, new_path = parts[index], parts[index + 1]
            index += 2
            rows.append((status, new_path, old_path))
        else:
            if index >= len(parts):
                raise RuntimeError("malformed git visibility diff")
            path = parts[index]
            index += 1
            rows.append((status, path, None))
    return rows


def _blob_at_ref(root: Path, ref: str, path: str, status: str) -> str:
    if status.startswith("D"):
        return ""
    try:
        return _git_text(root, "rev-parse", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return ""


def _ref_delta_nodes(
    root: Path,
    *,
    source_commit: str,
    refs: Sequence[tuple[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    ref_records: list[dict[str, Any]] = []
    for ref, commit in refs:
        if commit == source_commit:
            ref_records.append(
                {
                    "source_ref": ref,
                    "source_commit": commit,
                    "provenance_state": _provenance_state(ref),
                    "merge_base": source_commit,
                    "delta_nodes": 0,
                    "coverage_state": "COMPLETE_NO_DELTA",
                }
            )
            continue
        try:
            merge_base = _git_text(root, "merge-base", source_commit, commit)
            rows = _diff_rows(root, merge_base, commit)
            coverage_state = "COMPLETE_FROM_MERGE_BASE"
        except subprocess.CalledProcessError:
            merge_base = ""
            listing = _git_text(root, "ls-tree", "-r", "--name-only", commit)
            rows = [("A", path, None) for path in listing.splitlines() if path]
            coverage_state = "COMPLETE_UNRELATED_HISTORY_TREE"
        if len(nodes) + len(rows) > MAX_REF_DELTA_NODES:
            raise RuntimeError(
                "repository ref delta visibility exceeds complete-scan bound: "
                f"{len(nodes) + len(rows)} > {MAX_REF_DELTA_NODES}"
            )
        for status, path, previous_path in rows:
            node = _base_fields(
                node_id=f"visibility:ref-delta:{ref}:{path}",
                node_kind="REPOSITORY_REF_DELTA_SURFACE",
                source_state=_provenance_state(ref),
                source_ref=ref,
                source_commit=commit,
                source_path=path,
                closure_state="UNRESOLVED",
                validation_state="UNRESOLVED",
            )
            node.update(
                {
                    "merge_base_commit": merge_base,
                    "change_status": status,
                    "previous_path": previous_path,
                    "git_blob": _blob_at_ref(root, ref, path, status),
                    "static_discovery_only": True,
                    "source_executed_during_discovery": False,
                }
            )
            nodes.append(
                _seal(
                    node,
                    "HHS-P219-LANE5-GLOBAL-VISIBILITY-REF-DELTA-1.70",
                )
            )
        ref_records.append(
            {
                "source_ref": ref,
                "source_commit": commit,
                "provenance_state": _provenance_state(ref),
                "merge_base": merge_base,
                "delta_nodes": len(rows),
                "coverage_state": coverage_state,
            }
        )
    return nodes, ref_records


def verify_global_repository_visibility(projection: Mapping[str, Any]) -> None:
    if projection.get("schema") != SCHEMA:
        raise ValueError("global repository visibility schema mismatch")
    nodes = projection.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("global repository visibility nodes missing")
    node_ids: set[str] = set()
    identities: set[str] = set()
    domains = {
        "REPOSITORY_FILE_SURFACE": "HHS-P219-LANE5-GLOBAL-VISIBILITY-MAIN-FILE-1.70",
        "CAPABILITY_SURFACE": "HHS-P219-LANE5-GLOBAL-VISIBILITY-CAPABILITY-1.70",
        "REPOSITORY_REF_DELTA_SURFACE": "HHS-P219-LANE5-GLOBAL-VISIBILITY-REF-DELTA-1.70",
    }
    for node in nodes:
        if not isinstance(node, Mapping):
            raise ValueError("global visibility node must be a mapping")
        node_id = str(node.get("node_id") or "")
        claimed = str(node.get("hash216") or "")
        if not node_id or node_id in node_ids:
            raise ValueError(f"duplicate/empty global visibility node id: {node_id}")
        if len(claimed) != 216 or claimed in identities:
            raise ValueError(f"duplicate/invalid global visibility Hash216: {node_id}")
        if node.get("lane5_visible") is not True:
            raise ValueError(f"Lane 5 visibility was removed: {node_id}")
        if node.get("visibility_filter_allowed") is not False:
            raise ValueError(f"visibility filtering was admitted: {node_id}")
        if node.get("executability_state") == "NON_EXECUTABLE" and not node.get(
            "non_executable_evidence"
        ):
            raise ValueError(f"unsupported non-executable classification: {node_id}")
        if node.get("configuration_requirement_state") == "REQUIRED" and not node.get(
            "configuration_requirement_evidence"
        ):
            raise ValueError(f"unsupported configuration requirement: {node_id}")
        if node.get("adapter_requirement_state") == "REQUIRED" and not node.get(
            "adapter_requirement_evidence"
        ):
            raise ValueError(f"unsupported adapter requirement: {node_id}")
        for key in (
            "canonical_vm81_mutation_authority",
            "canonical_hash72_authority",
            "canonical_hash216_authority",
            "canonical_persistence_authority",
            "pqc_key_authority",
            "receipt_clock_authority",
            "automatic_hash216_composition_promotion",
            "automatic_superedge_promotion",
        ):
            if node.get(key) is not False:
                raise ValueError(f"authority escalation in {node_id}: {key}")
        body = dict(node)
        body.pop("hash216", None)
        domain = domains.get(str(node.get("node_kind") or ""))
        if domain is None or claimed != _h216(domain, body):
            raise ValueError(f"global visibility Hash216 mismatch: {node_id}")
        node_ids.add(node_id)
        identities.add(claimed)
    roots = projection.get("roots")
    if not isinstance(roots, Mapping):
        raise ValueError("global visibility roots missing")
    expected = _h216(
        "HHS-P219-LANE5-GLOBAL-REPOSITORY-VISIBILITY-ROOT-1.70",
        [str(node["hash216"]) for node in nodes],
    )
    if roots.get("visibility_root_hash216") != expected:
        raise ValueError("global visibility aggregate Hash216 mismatch")
    coverage = projection.get("coverage")
    if not isinstance(coverage, Mapping) or coverage.get("complete_within_discovered_refs") is not True:
        raise ValueError("global visibility coverage is not complete")


def build_global_repository_visibility(
    repo_root: str | Path,
    dependency_graph: Mapping[str, Any],
    *,
    lane5_snapshot: Mapping[str, Any] | None = None,
    ref_names: Sequence[str] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    source_commit = str(dependency_graph.get("source_commit") or "")
    source_tree = str(dependency_graph.get("source_tree") or "")
    if len(source_commit) != 40 or len(source_tree) != 40:
        raise ValueError("dependency graph source commit/tree missing")
    if lane5_snapshot is None:
        from hhs_backend.runtime.hhs_pass219_lane5_repository_capability_reverse_discovery_1_44 import (
            build_repository_capability_reverse_discovery,
        )
        lane5_snapshot = build_repository_capability_reverse_discovery(root)

    main_nodes = _main_file_nodes(dependency_graph, source_commit=source_commit)
    capability_nodes = _capability_nodes(lane5_snapshot, source_commit=source_commit)
    refs = _resolve_refs(root, ref_names)
    ref_nodes, ref_records = _ref_delta_nodes(
        root,
        source_commit=source_commit,
        refs=refs,
    )
    nodes = sorted(
        [*main_nodes, *capability_nodes, *ref_nodes],
        key=lambda item: str(item["node_id"]),
    )
    visibility_root = _h216(
        "HHS-P219-LANE5-GLOBAL-REPOSITORY-VISIBILITY-ROOT-1.70",
        [str(node["hash216"]) for node in nodes],
    )
    projection = {
        "schema": SCHEMA,
        "version": VERSION,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_dependency_graph_root_hash216": str(
            dependency_graph.get("roots", {}).get("graph_root_hash216") or ""
        ),
        "source_lane5_model_root_sha256": str(
            lane5_snapshot.get("model_root_sha256") or ""
        ),
        "counts": {
            "main_repository_file_surfaces": len(main_nodes),
            "inherited_capability_surfaces": len(capability_nodes),
            "repository_ref_delta_surfaces": len(ref_nodes),
            "discovered_refs": len(refs),
            "total_visibility_nodes": len(nodes),
        },
        "coverage": {
            "discovery_precedes_classification": True,
            "main_repository_files_complete": True,
            "inherited_reverse_discovery_nodes_complete": True,
            "discovered_git_refs_complete": True,
            "complete_within_discovered_refs": True,
            "silent_truncation_allowed": False,
            "ref_bound": MAX_REFS,
            "ref_delta_node_bound": MAX_REF_DELTA_NODES,
        },
        "semantic_separation": {
            "visible_implies_executable": False,
            "visible_implies_validated": False,
            "visible_implies_admitted": False,
            "visible_implies_mutable": False,
            "candidate_only_implies_non_executable": False,
            "security_restriction_implies_demo": False,
            "unknown_state_is_preserved_as_unresolved": True,
            "declared_demo_example_reference_flags_are_visibility_filters": False,
            "configuration_or_adapter_requirements_require_explicit_evidence": True,
        },
        "authority": _authority(),
        "ref_records": ref_records,
        "roots": {"visibility_root_hash216": visibility_root},
        "nodes": nodes,
    }
    verify_global_repository_visibility(projection)
    return projection


__all__ = [
    "SCHEMA",
    "VERSION",
    "MAX_REFS",
    "MAX_REF_DELTA_NODES",
    "build_global_repository_visibility",
    "discover_repository_refs",
    "verify_global_repository_visibility",
]

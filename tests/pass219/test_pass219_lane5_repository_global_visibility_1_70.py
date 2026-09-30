from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_repository_global_visibility_1_70 import (
    LANE5_GLOBAL_VISIBILITY_OPERATIONS,
    Lane5RepositoryGlobalVisibilityDatabase,
    build_repository_global_visibility_graph,
)
from hhs_runtime.pass191.repository_hydration import _hash216


def _file(path: str, language: str) -> dict[str, object]:
    body = {
        "path": path,
        "mode": "100644",
        "git_blob": ("a" if path.endswith(".py") else "b") * 40,
        "size_bytes": 256,
        "language": language,
        "disposition": "TRACKED",
        "origin": "REPOSITORY",
    }
    return {**body, "hash216": _hash216("HHS-REPOSITORY-INDEX-FILE-V1", body)}


def _edge(source: str, target: str) -> dict[str, object]:
    body = {
        "from": source,
        "to": target,
        "type": "REPOSITORY_PATH_REFERENCE",
        "line": 1,
        "reference": target,
    }
    return {
        **body,
        "hash216": _hash216("HHS-REPOSITORY-DEPENDENCY-EDGE-V1", body),
    }


@pytest.fixture()
def case(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "pkg/core.py").write_text(
        "class Widget:\n"
        "    def __init__(self, value): self.value = value\n"
        "    @classmethod\n"
        "    def from_record(cls, record): return cls(record['value'])\n\n"
        "def build_widget(value): return Widget(value)\n\n"
        "def helper(value): return value\n",
        encoding="utf-8",
    )
    (tmp_path / "docs/WIDGET_CONSTRUCTOR.md").write_text(
        "# Widget constructor\n", encoding="utf-8"
    )
    core = _file("pkg/core.py", "python")
    formal = _file("docs/WIDGET_CONSTRUCTOR.md", "documentation")
    graph = {
        "schema": "HHS_REPOSITORY_HASH216_FILE_DEPENDENCY_INDEX_V1",
        "source_commit": "c" * 40,
        "source_tree": "d" * 40,
        "counts": {"tracked_files": 2, "file_dependency_edges": 1},
        "roots": {
            "graph_root_hash216": _hash216("fixture-graph-1.70", {"fixture": True})
        },
        "files": [core, formal],
        "dependency_edges": [_edge("docs/WIDGET_CONSTRUCTOR.md", "pkg/core.py")],
    }
    lane5 = {
        "schema": "TEST_LANE5_1_70",
        "model_root_sha256": "e" * 64,
        "counts": {"canonical_boundaries": 1, "total": 1},
        "native_receipt": {"accepted": True, "candidate_only": True},
        "nodes": [
            {
                "node_id": "python-registry:widget.build",
                "source_kind": "PYTHON_OPERATION_REGISTRY",
                "authority_class": 0,
                "operation_key": "widget.build",
                "raw_name": "widget.build",
                "normalized_semantic_name": "widget build",
                "path": "pkg/core.py",
                "line": 6,
                "entry_signature64": 123456789,
            }
        ],
    }
    provenance = [
        {
            "ref_kind": "PULL_REQUEST",
            "ref_name": "refs/pull/100/head",
            "head_sha": "1" * 40,
            "base_sha": "0" * 40,
            "merge_commit_sha": "2" * 40,
            "pr_number": 100,
            "state": "MERGED",
            "merged": True,
            "checks_green": True,
            "source_paths": ["pkg/core.py"],
            "declared_metadata": {"label": "demo"},
        },
        {
            "ref_kind": "BRANCH",
            "ref_name": "refs/remotes/origin/old-capability",
            "head_sha": "3" * 40,
            "state": "OBSERVED",
            "source_paths": ["pkg/core.py"],
            "declared_metadata": {"label": "reference"},
        },
        {
            "ref_kind": "PULL_REQUEST",
            "ref_name": "refs/pull/101/head",
            "head_sha": "4" * 40,
            "pr_number": 101,
            "state": "OPEN",
            "checks_green": True,
            "source_paths": ["pkg/core.py"],
            "declared_metadata": {"enabled": False},
        },
    ]
    return tmp_path, graph, lane5, provenance


def _build(case):
    root, graph, lane5, provenance = case
    return build_repository_global_visibility_graph(
        root,
        graph,
        lane5_snapshot=lane5,
        provenance_records=provenance,
    )


def test_declares_global_visibility_operations():
    assert LANE5_GLOBAL_VISIBILITY_OPERATIONS == (
        "lane5.repository_global_visibility.status",
        "lane5.repository_global_visibility.search",
        "lane5.repository_global_visibility.neighbors",
    )


def test_every_bound_repository_object_and_callable_remains_visible(case):
    projection = _build(case)
    assert projection["counts"]["repository_objects"] == 2
    assert projection["scope"]["bound_repository_tracked_file_visibility_complete"] is True
    assert projection["authority"]["lane5_is_pass219_composition_manifold"] is True
    assert projection["authority"]["visibility_filtering_allowed"] is False
    assert projection["authority"]["classification_metadata_can_hide_nodes"] is False

    repository_paths = {node["source_path"] for node in projection["repository_objects"]}
    assert repository_paths == {"pkg/core.py", "docs/WIDGET_CONSTRUCTOR.md"}

    callables = {node["name"]: node for node in projection["callables"]}
    assert {"Widget", "build_widget", "helper"} <= set(callables)
    for node in projection["repository_objects"] + projection["callables"]:
        assert node["visible_to_lane5"] is True
        assert node["configuration_state"] == "NOT_INFERRED"
        assert node["adapter_state"] == "NOT_INFERRED"
        assert node["canonical_mutation_authority"] is False
        assert len(node["hash216"]) == 216


def test_demo_reference_disabled_and_unresolved_metadata_never_hide_nodes(case):
    projection = _build(case)
    by_class = {node["provenance_class"]: node for node in projection["provenance"]}
    assert {"MERGED_GREEN", "ORPHAN_BRANCH", "OPEN_GREEN_PR"} <= set(by_class)
    for node in projection["provenance"]:
        assert node["visible_to_lane5"] is True
        assert node["classification_is_visibility_filter"] is False
        assert node["configuration_state"] == "NOT_INFERRED"
        assert node["adapter_state"] == "NOT_INFERRED"

    assert by_class["MERGED_GREEN"]["declared_metadata"]["label"] == "demo"
    assert by_class["ORPHAN_BRANCH"]["declared_metadata"]["label"] == "reference"
    assert by_class["OPEN_GREEN_PR"]["declared_metadata"]["enabled"] is False


def test_provenance_preserves_green_merge_inheritance_without_widening_authority(case):
    projection = _build(case)
    by_class = {node["provenance_class"]: node for node in projection["provenance"]}

    merged = by_class["MERGED_GREEN"]
    assert merged["composition_state"] == "ELIGIBLE"
    assert merged["validation_state"] == "INHERITED_GREEN"
    assert merged["closure_state"] == "INHERITED_CLOSED"
    assert merged["dependency_touch_invalidates_inherited_green"] is True

    open_green = by_class["OPEN_GREEN_PR"]
    assert open_green["composition_state"] == "ELIGIBLE_CANDIDATE"
    assert open_green["validation_state"] == "GREEN_CANDIDATE"
    assert open_green["closure_state"] == "UNRESOLVED"

    orphan = by_class["ORPHAN_BRANCH"]
    assert orphan["composition_state"] == "UNRESOLVED"
    assert orphan["closure_state"] == "UNRESOLVED"

    for node in (merged, open_green, orphan):
        assert node["canonical_mutation_authority"] is False
        assert node["canonical_hash72_authority"] is False
        assert node["canonical_hash216_authority"] is False
        assert node["canonical_persistence_authority"] is False


def test_only_explicit_non_executable_evidence_can_mark_non_executable(case):
    root, graph, lane5, provenance = case
    ordinary = build_repository_global_visibility_graph(
        root, graph, lane5_snapshot=lane5, provenance_records=provenance
    )
    assert all(
        node["composition_state"] != "DECLARED_NON_EXECUTABLE"
        for node in ordinary["provenance"]
    )

    explicit = deepcopy(provenance)
    explicit[1]["explicit_non_executable_evidence"] = True
    projected = build_repository_global_visibility_graph(
        root, graph, lane5_snapshot=lane5, provenance_records=explicit
    )
    branch = next(
        node for node in projected["provenance"]
        if node["provenance_class"] == "ORPHAN_BRANCH"
    )
    assert branch["visible_to_lane5"] is True
    assert branch["composition_state"] == "DECLARED_NON_EXECUTABLE"


def test_database_is_restartable_searchable_and_hash216_positioned(case, tmp_path: Path):
    projection = _build(case)
    path = tmp_path / "global-visibility.sqlite3"
    with Lane5RepositoryGlobalVisibilityDatabase(path) as database:
        status = database.hydrate(projection)
        assert status["visibility_nodes"] == projection["counts"]["visibility_nodes"]
        assert status["visibility_edges"] == projection["counts"]["visibility_edges"]
        assert status["hash216_positions"] == (
            projection["counts"]["visibility_nodes"]
            + projection["counts"]["visibility_edges"]
        ) * 216
        assert status["journal_mode"].lower() == "wal"
        assert status["synchronous_full"] is True
        assert status["visibility_filtering_allowed"] is False
        rows = database.search("widget")
        assert rows
        assert all(row["visibility_state"] == "VISIBLE" for row in rows)

    with Lane5RepositoryGlobalVisibilityDatabase(path) as reopened:
        status = reopened.status()
        assert status["restart_rehydratable"] is True
        assert status["visibility_nodes"] == projection["counts"]["visibility_nodes"]


def test_projection_tamper_fails_closed(case, tmp_path: Path):
    projection = _build(case)
    tampered = deepcopy(projection)
    tampered["callables"][0]["name"] = "tampered"
    with Lane5RepositoryGlobalVisibilityDatabase(tmp_path / "tampered.sqlite3") as database:
        with pytest.raises(ValueError, match="Hash216 mismatch"):
            database.hydrate(tampered)

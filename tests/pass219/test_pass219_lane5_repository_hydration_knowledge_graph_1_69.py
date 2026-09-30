from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import (
    LANE5_REPOSITORY_KNOWLEDGE_OPERATIONS,
    Lane5RepositoryHydrationKnowledgeDatabase,
    build_repository_hydration_knowledge_graph,
)
from hhs_runtime.pass191.repository_hydration import _hash216


def _file(path: str, language: str) -> dict[str, object]:
    body = {
        "path": path, "mode": "100644",
        "git_blob": ("a" if path.endswith(".py") else "b") * 40,
        "size_bytes": 128, "language": language,
        "disposition": "TRACKED", "origin": "REPOSITORY",
    }
    return {**body, "hash216": _hash216("HHS-REPOSITORY-INDEX-FILE-V1", body)}


def _edge(source: str, target: str) -> dict[str, object]:
    body = {"from": source, "to": target, "type": "REPOSITORY_PATH_REFERENCE", "line": 1, "reference": target}
    return {**body, "hash216": _hash216("HHS-REPOSITORY-DEPENDENCY-EDGE-V1", body)}


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
    (tmp_path / "docs/WIDGET_CONSTRUCTOR.md").write_text("# Widget constructor\n", encoding="utf-8")
    core, formal = _file("pkg/core.py", "python"), _file("docs/WIDGET_CONSTRUCTOR.md", "documentation")
    graph = {
        "schema": "HHS_REPOSITORY_HASH216_FILE_DEPENDENCY_INDEX_V1",
        "source_commit": "c" * 40, "source_tree": "d" * 40,
        "counts": {"tracked_files": 2, "file_dependency_edges": 1},
        "roots": {"graph_root_hash216": _hash216("fixture-graph", {"fixture": True})},
        "files": [core, formal],
        "dependency_edges": [_edge("docs/WIDGET_CONSTRUCTOR.md", "pkg/core.py")],
    }
    lane5 = {
        "schema": "TEST_LANE5",
        "model_root_sha256": "e" * 64,
        "counts": {"canonical_boundaries": 1, "total": 1},
        "native_receipt": {"accepted": True, "candidate_only": True},
        "nodes": [{
            "node_id": "python-registry:widget.build",
            "source_kind": "PYTHON_OPERATION_REGISTRY",
            "authority_class": 0,
            "operation_key": "widget.build",
            "raw_name": "widget.build",
            "normalized_semantic_name": "widget build",
            "path": "pkg/core.py", "line": 6,
            "entry_signature64": 123456789,
        }],
    }
    return tmp_path, graph, lane5


def test_declares_first_class_lane5_operation_registry():
    assert LANE5_REPOSITORY_KNOWLEDGE_OPERATIONS == (
        "lane5.repository_hydration_knowledge.status",
        "lane5.repository_hydration_knowledge.search",
        "lane5.repository_hydration_knowledge.neighbors",
    )


def test_projection_lifts_capabilities_constructors_and_bindings(case):
    root, graph, lane5 = case
    projection = build_repository_hydration_knowledge_graph(root, graph, lane5_snapshot=lane5)
    assert projection["counts"]["capabilities"] == 5
    assert projection["counts"]["inherited_lane5_capabilities"] == 1
    assert projection["counts"]["repository_static_callables"] == 4
    assert projection["counts"]["constructors"] == 3
    assert projection["counts"]["knowledge_nodes"] == 4
    assert len(projection["roots"]["projection_root_hash216"]) == 216
    assert projection["authority"]["candidate_only"] is True
    assert projection["authority"]["canonical_hash216_authority"] is False
    assert projection["visibility_policy"]["classification_flags_filter_visibility"] is False
    assert projection["visibility_policy"]["unresolved_state_filters_visibility"] is False
    helper = next(item for item in projection["capabilities"] if item["name"] == "helper")
    assert helper["visible_to_lane5"] is True
    assert helper["execution_eligibility"] == "DISCOVERED_NOT_PRECLUDED"
    assert helper["demo_or_reference_status"] == "NOT_INFERRED"
    assert helper["configuration_requirement"] == "NOT_INFERRED"
    assert helper["adapter_requirement"] == "NOT_INFERRED"
    assert helper["execution_authority"] is False
    kinds = {item["constructor_kind"] for item in projection["constructors"]}
    assert {"PYTHON_CLASS","PYTHON_FACTORY_FUNCTION","FORMAL_CONSTRUCTOR_ARTIFACT"} <= kinds
    relations = {item["relation_type"] for item in projection["edges"]}
    assert {"DECLARED_IN_FILE","SEMANTICALLY_ALIGNED_WITH_CAPABILITY"} <= relations
    for item in projection["capabilities"] + projection["constructors"] + projection["edges"]:
        assert len(item["hash216"]) == 216


def test_database_is_restartable_queryable_and_position_indexed(case, tmp_path: Path):
    root, graph, lane5 = case
    projection = build_repository_hydration_knowledge_graph(root, graph, lane5_snapshot=lane5)
    path = tmp_path / "knowledge.sqlite3"
    with Lane5RepositoryHydrationKnowledgeDatabase(path) as db:
        status = db.hydrate(dependency_graph=graph, knowledge_projection=projection)
        assert status["repository_files"] == 2
        assert status["file_dependencies"] == 1
        assert status["capabilities"] == projection["counts"]["capabilities"]
        assert status["constructors"] == 3
        assert status["hash216_positions"] == (projection["counts"]["knowledge_nodes"] + projection["counts"]["knowledge_edges"]) * 216
        assert status["journal_mode"].lower() == "wal"
        assert status["synchronous_full"] is True
        rows = db.search("widget")
        assert {row["node_kind"] for row in rows} == {"CAPABILITY","CONSTRUCTOR"}
        cap = next(row["node_id"] for row in rows if row["node_kind"] == "CAPABILITY")
        assert any(row["relation_type"] == "SEMANTICALLY_ALIGNED_WITH_CAPABILITY" for row in db.neighbors(cap))
    with Lane5RepositoryHydrationKnowledgeDatabase(path) as reopened:
        assert reopened.status()["restart_rehydratable"] is True
        assert reopened.status()["constructors"] == 3


def test_branch_ref_callable_is_visible_without_executing_branch_source(case):
    root, graph, lane5 = case

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout.strip()

    git("init", "-b", "main")
    git("config", "user.name", "HHS Test")
    git("config", "user.email", "hhs-test@example.invalid")
    git("add", ".")
    git("commit", "-m", "fixture main")
    git("checkout", "-b", "feature/ref-visible")
    branch_file = root / "pkg" / "branch_only.py"
    branch_file.write_text(
        "def branch_only_capability(value):\n"
        "    return value\n",
        encoding="utf-8",
    )
    git("add", "pkg/branch_only.py")
    git("commit", "-m", "branch capability")
    feature_commit = git("rev-parse", "HEAD")
    git("update-ref", "refs/remotes/origin/feature/ref-visible", feature_commit)
    git("checkout", "main")

    projection = build_repository_hydration_knowledge_graph(
        root, graph, lane5_snapshot=lane5
    )
    ref_caps = [
        item for item in projection["capabilities"]
        if item.get("source_ref") == "refs/remotes/origin/feature/ref-visible"
    ]
    assert len(ref_caps) == 1
    cap = ref_caps[0]
    assert cap["name"] == "branch_only_capability"
    assert cap["visible_to_lane5"] is True
    assert cap["closure_state"] == "UNRESOLVED"
    assert cap["integration_evidence"] == "STATIC_GIT_OBJECT_DISCOVERY_ONLY"
    assert cap["ref_source_executed"] is False
    assert cap["execution_authority"] is False
    assert projection["counts"]["repository_ref_heads"] == 1
    assert projection["counts"]["repository_ref_static_callables"] == 1
    assert len(projection["roots"]["repository_ref_snapshot_root_hash216"]) == 216
    assert projection["repository_ref_snapshot"] == [{
        "source_ref": "refs/remotes/origin/feature/ref-visible",
        "source_commit": feature_commit,
        "source_state": "BRANCH_HEAD",
    }]
    assert not any(
        edge.get("source_node_id") == cap["node_id"]
        and edge.get("relation_type") == "DECLARED_IN_FILE"
        for edge in projection["edges"]
    )


def test_tamper_fails_closed(case, tmp_path: Path):
    root, graph, lane5 = case
    projection = build_repository_hydration_knowledge_graph(root, graph, lane5_snapshot=lane5)
    tampered = deepcopy(projection)
    tampered["constructors"][0]["name"] = "tampered"
    with Lane5RepositoryHydrationKnowledgeDatabase(tmp_path / "bad.sqlite3") as db:
        with pytest.raises(ValueError, match="Hash216 mismatch"):
            db.hydrate(dependency_graph=graph, knowledge_projection=tampered)

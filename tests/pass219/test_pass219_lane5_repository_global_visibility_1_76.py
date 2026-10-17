from __future__ import annotations

from pathlib import Path

import pytest

from hhs_backend.runtime.hhs_pass219_lane5_repository_global_visibility_1_76 import (
    Lane5RepositoryGlobalVisibilityDatabase,
    build_repository_global_capability_visibility,
)
from hhs_runtime.pass191.repository_hydration import _hash216


def _file(path: str, *, language: str = "python") -> dict[str, object]:
    body = {
        "path": path,
        "mode": "100644",
        "git_blob": ("a" if path.endswith(".py") else "b") * 40,
        "size_bytes": 128,
        "language": language,
        "disposition": "TRACKED",
        "origin": "REPOSITORY",
    }
    return {**body, "hash216": _hash216("HHS-REPOSITORY-INDEX-FILE-V1", body)}


@pytest.fixture()
def case(tmp_path: Path):
    (tmp_path / "hhs_runtime").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "hhs_runtime/capability.py").write_text(
        "candidate_only = True\n"
        "enabled = False\n"
        "needs_adapter = True\n"
        "def run(value): return value\n",
        encoding="utf-8",
    )
    (tmp_path / "docs/example.md").write_text(
        "# Example reference\nThis remains visible knowledge evidence.\n",
        encoding="utf-8",
    )
    source = _file("hhs_runtime/capability.py")
    doc = _file("docs/example.md", language="documentation")
    graph = {
        "schema": "HHS_REPOSITORY_HASH216_FILE_DEPENDENCY_INDEX_V1",
        "source_commit": "c" * 40,
        "source_tree": "d" * 40,
        "counts": {"tracked_files": 2, "file_dependency_edges": 0},
        "roots": {"graph_root_hash216": _hash216("fixture-global-visibility", {"ok": True})},
        "files": [source, doc],
        "dependency_edges": [],
    }
    lane5 = {
        "schema": "TEST_LANE5",
        "model_root_sha256": "e" * 64,
        "counts": {"canonical_boundaries": 1, "total": 1},
        "native_receipt": {"accepted": True, "candidate_only": True},
        "nodes": [
            {
                "node_id": "python-registry:capability.run",
                "source_kind": "PYTHON_OPERATION_REGISTRY",
                "authority_class": 1,
                "path": "hhs_runtime/capability.py",
            }
        ],
    }
    refs = [
        {
            "kind": "OPEN_PR_HEAD",
            "name": "pull/999",
            "sha": "f" * 40,
            "pull_request_number": 999,
            "draft": False,
            "validation_state": "UNRESOLVED",
            "merge_state": "OPEN",
            "changed_paths": ["hhs_runtime/capability.py"],
        },
        {
            "kind": "BRANCH_HEAD",
            "name": "feature/example",
            "sha": "1" * 40,
            "validation_state": "UNRESOLVED",
            "merge_state": "UNRESOLVED",
        },
    ]
    return tmp_path, graph, lane5, refs


def test_overinclusive_visibility_preserves_flags_as_metadata(case):
    root, graph, lane5, refs = case
    projection = build_repository_global_capability_visibility(
        root,
        graph,
        lane5_snapshot=lane5,
        reference_inventory=refs,
    )
    assert projection["counts"]["repository_objects_visible"] == 2
    assert projection["counts"]["reference_objects_visible"] == 2
    assert projection["counts"]["visibility_filtered_objects"] == 0
    source = next(
        item for item in projection["repository_visibility"]
        if item["path"] == "hhs_runtime/capability.py"
    )
    assert source["lane5_visible"] is True
    assert source["visibility_filtered"] is False
    assert source["execution_eligibility"] == (
        "LANE5_COMPOSITION_CANDIDATE_REQUIRES_RUNTIME_VALIDATION"
    )
    assert {"CANDIDATE_ONLY", "DISABLED_HINT", "ADAPTER_HINT"} <= set(
        source["classification_markers"]
    )
    assert source["direct_linux_kernel_bypass_authority"] is False
    assert source["direct_service_bypass_authority"] is False


def test_open_pr_and_branch_are_visible_without_executing_their_code(case):
    root, graph, lane5, refs = case
    projection = build_repository_global_capability_visibility(
        root,
        graph,
        lane5_snapshot=lane5,
        reference_inventory=refs,
    )
    assert {item["reference_kind"] for item in projection["reference_visibility"]} == {
        "OPEN_PR_HEAD",
        "BRANCH_HEAD",
    }
    for item in projection["reference_visibility"]:
        assert item["lane5_visible"] is True
        assert item["branch_or_pr_code_executed_during_discovery"] is False
        assert item["canonical_vm81_mutation_authority"] is False


def test_restartable_hash216_vector_projection(case, tmp_path: Path):
    root, graph, lane5, refs = case
    projection = build_repository_global_capability_visibility(
        root,
        graph,
        lane5_snapshot=lane5,
        reference_inventory=refs,
    )
    db_path = tmp_path / "global-visibility.sqlite3"
    with Lane5RepositoryGlobalVisibilityDatabase(db_path) as db:
        status = db.hydrate(projection)
        expected_records = (
            projection["counts"]["repository_objects_visible"]
            + projection["counts"]["reference_objects_visible"]
            + projection["counts"]["inherited_capability_bindings"]
        )
        assert status["visibility_records"] == expected_records
        assert status["hash216_positions"] == expected_records * 216
        hits = db.search("capability.py")
        assert hits
        assert all(len(row["hash216"]) == 216 for row in hits)
    with Lane5RepositoryGlobalVisibilityDatabase(db_path) as reopened:
        assert reopened.status()["restart_rehydratable"] is True


def test_invalid_reference_identity_fails_closed(case):
    root, graph, lane5, _ = case
    with pytest.raises(ValueError, match="40-hex SHA"):
        build_repository_global_capability_visibility(
            root,
            graph,
            lane5_snapshot=lane5,
            reference_inventory=[
                {"kind": "OPEN_PR_HEAD", "name": "pull/1", "sha": "not-a-sha"}
            ],
        )

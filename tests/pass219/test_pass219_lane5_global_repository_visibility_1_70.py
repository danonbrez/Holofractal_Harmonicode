from __future__ import annotations

from pathlib import Path
import subprocess

from hhs_backend.runtime.hhs_pass219_lane5_global_repository_visibility_1_70 import (
    build_global_repository_visibility,
    verify_global_repository_visibility,
)
from hhs_backend.runtime.hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69 import (
    Lane5RepositoryHydrationKnowledgeDatabase,
)
from hhs_runtime.pass191.repository_hydration import _hash216


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
    ).strip()


def _file(path: str, blob: str = "a" * 40) -> dict[str, object]:
    body = {
        "path": path,
        "mode": "100644",
        "git_blob": blob,
        "size_bytes": 128,
        "language": "python",
        "disposition": "TRACKED",
        "origin": "REPOSITORY",
    }
    return {
        **body,
        "hash216": _hash216("HHS-REPOSITORY-INDEX-FILE-V1", body),
    }


def _case(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "hhs-test@example.invalid")
    _git(root, "config", "user.name", "HHS Test")

    (root / "core.py").write_text(
        "def execute(value):\n    return value\n",
        encoding="utf-8",
    )
    (root / "flagged.py").write_text(
        "DEMO = True\n"
        "candidate_only = True\n"
        "enabled = False\n"
        "def fully_wired(value):\n    return value\n",
        encoding="utf-8",
    )
    _git(root, "add", ".")
    _git(root, "commit", "-m", "main integrated capability")
    source_commit = _git(root, "rev-parse", "HEAD")
    source_tree = _git(root, "rev-parse", "HEAD^{tree}")

    graph = {
        "schema": "HHS_REPOSITORY_HASH216_FILE_DEPENDENCY_INDEX_V1",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "counts": {"tracked_files": 2, "file_dependency_edges": 0},
        "roots": {
            "graph_root_hash216": _hash216(
                "fixture-global-visibility-graph",
                {"source_commit": source_commit},
            )
        },
        "files": [_file("core.py"), _file("flagged.py", "b" * 40)],
        "dependency_edges": [],
    }
    lane5 = {
        "schema": "TEST_LANE5",
        "model_root_sha256": "e" * 64,
        "counts": {"canonical_boundaries": 1, "total": 1},
        "native_receipt": {"accepted": True, "candidate_only": True},
        "nodes": [
            {
                "node_id": "python-registry:fully.wired",
                "source_kind": "PYTHON_OPERATION_REGISTRY",
                "authority_class": 0,
                "operation_key": "fully.wired",
                "raw_name": "fully.wired",
                "normalized_semantic_name": "fully wired",
                "path": "flagged.py",
                "line": 4,
                "entry_signature64": 123456789,
                "candidate_only": True,
                "enabled": False,
                "demo": True,
                "needs_configuration": True,
                "adapter_required": True,
                "execution_authority": "DISCOVERY_ONLY_UNCLASSIFIED",
            }
        ],
    }

    _git(root, "checkout", "-b", "feature/runtime-capability")
    (root / "new_capability.py").write_text(
        "raise RuntimeError('BRANCH SOURCE MUST NEVER EXECUTE DURING DISCOVERY')\n"
        "DEMO = True\n"
        "enabled = False\n"
        "def run():\n    return 'wired'\n",
        encoding="utf-8",
    )
    _git(root, "add", "new_capability.py")
    _git(root, "commit", "-m", "add branch capability")
    feature_commit = _git(root, "rev-parse", "HEAD")
    _git(root, "checkout", "main")

    return root, graph, lane5, feature_commit


def test_global_visibility_keeps_flags_as_metadata_not_filters(tmp_path: Path):
    root, graph, lane5, feature_commit = _case(tmp_path)
    projection = build_global_repository_visibility(
        root,
        graph,
        lane5_snapshot=lane5,
        ref_names=["refs/heads/feature/runtime-capability"],
    )
    verify_global_repository_visibility(projection)

    assert projection["coverage"]["discovery_precedes_classification"] is True
    assert projection["coverage"]["silent_truncation_allowed"] is False
    assert projection["semantic_separation"]["candidate_only_implies_non_executable"] is False
    assert projection["semantic_separation"]["security_restriction_implies_demo"] is False
    assert projection["counts"]["main_repository_file_surfaces"] == 2
    assert projection["counts"]["inherited_capability_surfaces"] == 1
    assert projection["counts"]["repository_ref_delta_surfaces"] == 1

    nodes = projection["nodes"]
    assert all(node["lane5_visible"] is True for node in nodes)
    assert all(node["visibility_filter_allowed"] is False for node in nodes)
    assert all(node["canonical_vm81_mutation_authority"] is False for node in nodes)
    assert all(node["canonical_hash72_authority"] is False for node in nodes)
    assert all(node["canonical_hash216_authority"] is False for node in nodes)
    assert all(len(node["hash216"]) == 216 for node in nodes)

    capability = next(
        node for node in nodes
        if node["node_kind"] == "CAPABILITY_SURFACE"
    )
    assert capability["declared_classification"]["candidate_only"] is True
    assert capability["declared_classification"]["enabled"] is False
    assert capability["declared_classification"]["demo"] is True
    assert capability["declared_classification"]["needs_configuration"] is True
    assert capability["declared_classification"]["adapter_required"] is True
    assert capability["executability_state"] == "UNRESOLVED"
    assert capability["configuration_requirement_state"] == "UNRESOLVED"
    assert capability["adapter_requirement_state"] == "UNRESOLVED"

    branch = next(
        node for node in nodes
        if node["node_kind"] == "REPOSITORY_REF_DELTA_SURFACE"
    )
    assert branch["source_commit"] == feature_commit
    assert branch["source_path"] == "new_capability.py"
    assert branch["closure_state"] == "UNRESOLVED"
    assert branch["validation_state"] == "UNRESOLVED"
    assert branch["executability_state"] == "UNRESOLVED"
    assert branch["source_executed_during_discovery"] is False


def test_global_visibility_hydrates_same_hash216_vector_store(tmp_path: Path):
    root, graph, lane5, _ = _case(tmp_path)
    projection = build_global_repository_visibility(
        root,
        graph,
        lane5_snapshot=lane5,
        ref_names=["refs/heads/feature/runtime-capability"],
    )
    database_path = tmp_path / "lane5.sqlite3"
    with Lane5RepositoryHydrationKnowledgeDatabase(database_path) as db:
        before = db.status()
        assert before["global_visibility_nodes"] == 0
        status = db.hydrate_global_visibility(projection)
        assert status["global_visibility_nodes"] == projection["counts"]["total_visibility_nodes"]
        assert status["hash216_positions"] == projection["counts"]["total_visibility_nodes"] * 216
        rows = db.search_visibility("new_capability.py")
        assert len(rows) == 1
        assert rows[0]["source_state"] == "LOCAL_BRANCH_REF"
        assert rows[0]["payload"]["lane5_visible"] is True
        assert rows[0]["payload"]["source_executed_during_discovery"] is False


def test_unresolved_is_information_not_visibility_failure(tmp_path: Path):
    root, graph, lane5, _ = _case(tmp_path)
    projection = build_global_repository_visibility(
        root,
        graph,
        lane5_snapshot=lane5,
        ref_names=["refs/heads/feature/runtime-capability"],
    )
    unresolved = [
        node for node in projection["nodes"]
        if node["closure_state"] == "UNRESOLVED"
    ]
    assert unresolved
    assert all(node["lane5_visible"] is True for node in unresolved)
    assert all(node["runtime_validation_required_for_execution"] is True for node in unresolved)

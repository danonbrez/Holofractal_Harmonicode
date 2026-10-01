from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import subprocess

from hhs_backend.runtime.hhs_pass219_lane5_global_capability_visibility_1_76 import (
    HASH216_CHARS,
    build_global_capability_visibility,
    hydrate_hash216_vector_database,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _init_repo(root: Path) -> None:
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "pass219@example.invalid")
    _git(root, "config", "user.name", "Pass219 Test")


def test_classification_flags_are_metadata_not_visibility_filters(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    source = tmp_path / "demo_reference_disabled.py"
    source.write_text(
        "CANDIDATE_ONLY = True\n"
        "DISABLED = True\n"
        "NEEDS_CONFIGURATION = True\n"
        "def usable_capability(value):\n"
        "    return value\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "add fully visible capability")

    snapshot = build_global_capability_visibility(tmp_path, include_refs=False)
    matching = [
        node
        for node in snapshot["nodes"]
        if node["source_path"] == "demo_reference_disabled.py"
    ]
    assert matching
    assert all(node["visible_to_lane5"] is True for node in matching)
    assert all(node["classification_is_visibility_filter"] is False for node in matching)
    labels = {label for node in matching for label in node["classification_labels"]}
    assert {"DEMO", "REFERENCE", "DISABLED", "CANDIDATE_ONLY", "NEEDS_CONFIGURATION"} <= labels
    assert any(node["symbol"] == "usable_capability" for node in matching)


def test_branch_code_is_discovered_statically_without_import_or_execution(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "base.py").write_text("def base():\n    return 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "base")
    _git(tmp_path, "checkout", "-b", "feature/runtime-capability")
    (tmp_path / "branch_tool.py").write_text(
        "raise RuntimeError('THIS MODULE MUST NEVER BE IMPORTED BY DISCOVERY')\n"
        "def branch_capability():\n"
        "    return 'visible'\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "add branch capability")
    _git(tmp_path, "checkout", "main")

    snapshot = build_global_capability_visibility(tmp_path, include_refs=True)
    matching = [
        node
        for node in snapshot["nodes"]
        if node["source_path"] == "branch_tool.py"
    ]
    assert matching
    assert any(node["symbol"] == "branch_capability" for node in matching)
    assert all(node["source_state"] == "LOCAL_BRANCH_HEAD" for node in matching)
    assert all(node["visible_to_lane5"] is True for node in matching)
    assert snapshot["invariants"]["discovery_imports_or_executes_discovered_code"] is False


def test_unresolved_discovery_never_grants_execution_or_mutation_authority(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    (tmp_path / "capability.py").write_text(
        "def capability():\n    return 42\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "capability")

    snapshot = build_global_capability_visibility(tmp_path, include_refs=False)
    assert snapshot["nodes"]
    for node in snapshot["nodes"]:
        assert node["closure_state"] == "DISCOVERED_UNCLASSIFIED"
        assert node["execution_state"] == "UNRESOLVED_BY_VISIBILITY_LAYER"
        assert node["validation_state"] == "UNRESOLVED_BY_VISIBILITY_LAYER"
        assert node["admission_state"] == "NOT_GRANTED_BY_VISIBILITY_LAYER"
        assert node["candidate_only"] is True
        assert node["direct_linux_or_service_bypass_authority"] is False
        assert node["canonical_vm81_mutation_authority"] is False
        assert node["canonical_hash72_mint_authority"] is False
        assert node["canonical_hash216_mint_authority"] is False
        assert node["canonical_persistence_authority"] is False
        assert len(node["hash216"]) == HASH216_CHARS


def test_hash216_vector_database_hydrates_every_visible_node_position(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    (repo / "capability.py").write_text(
        "class Capability:\n"
        "    def execute(self):\n"
        "        return 1\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "capability")

    snapshot = build_global_capability_visibility(repo, include_refs=False)
    db = tmp_path / "state" / "lane5.sqlite3"
    receipt = hydrate_hash216_vector_database(snapshot, db)

    assert receipt["node_count"] == len(snapshot["nodes"])
    assert receipt["hash216_vector_positions"] == len(snapshot["nodes"]) * HASH216_CHARS
    assert receipt["canonical_persistence_authority"] is False
    assert receipt["restart_rehydratable"] is True

    connection = sqlite3.connect(db)
    try:
        visible = connection.execute(
            "SELECT payload_json FROM capability_nodes ORDER BY node_id"
        ).fetchall()
        vectors = connection.execute(
            "SELECT COUNT(*) FROM hash216_vectors"
        ).fetchone()[0]
    finally:
        connection.close()
    assert len(visible) == len(snapshot["nodes"])
    assert vectors == len(snapshot["nodes"]) * HASH216_CHARS

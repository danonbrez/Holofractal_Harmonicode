from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from hhs_backend.runtime_os_pass220_lane5_capability_hydration import (
    Pass219Lane5CapabilityVisibilityLifecycle,
)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _repo(root: Path) -> None:
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "pass219@example.invalid")
    _git(root, "config", "user.name", "Pass219 Test")
    (root / "service.py").write_text(
        "DISABLED = True\n"
        "def fully_functioning_capability(value):\n"
        "    return value\n",
        encoding="utf-8",
    )
    _git(root, "add", ".")
    _git(root, "commit", "-m", "capability")


def test_pass220_hosts_pass219_visibility_without_selection_or_mutation_authority(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _repo(repo)
    state = tmp_path / "state"
    lifecycle = Pass219Lane5CapabilityVisibilityLifecycle(
        repository_root=repo,
        state_root=state,
        include_refs=False,
    )
    before = lifecycle.status()
    assert before["state"] == "NOT_STARTED"
    assert before["available_to_lane5"] is False

    after = lifecycle.startup()
    assert after["state"] == "READY"
    assert after["available_to_lane5"] is True
    assert after["node_count"] > 0
    assert after["hash216_vector_positions"] == after["node_count"] * 216
    assert after["pass220_host_only"] is True
    assert after["lane5_selection_authority"] is False
    assert after["runtime_validation_authority"] is False
    assert after["canonical_mutation_authority"] is False

    result = lifecycle.search("fully_functioning_capability")
    assert result["result_count"] >= 1
    assert any(
        item["symbol"] == "fully_functioning_capability"
        for item in result["results"]
    )
    assert all(item["visible_to_lane5"] is True for item in result["results"])
    assert all(
        item["classification_is_visibility_filter"] is False
        for item in result["results"]
    )
    assert lifecycle.receipt_path.is_file()
    receipt = json.loads(lifecycle.receipt_path.read_text(encoding="utf-8"))
    assert receipt["pass220_host_only"] is True
    assert receipt["lane5_selection_authority"] is False
    assert receipt["canonical_mutation_authority"] is False


def test_host_failure_does_not_create_alternate_execution_path(tmp_path: Path) -> None:
    lifecycle = Pass219Lane5CapabilityVisibilityLifecycle(
        repository_root=tmp_path / "missing",
        state_root=tmp_path / "state",
        include_refs=False,
    )
    status = lifecycle.startup()
    assert status["state"] == "UNAVAILABLE"
    assert status["available_to_lane5"] is False
    assert status["lane5_selection_authority"] is False
    assert status["runtime_validation_authority"] is False
    assert status["canonical_mutation_authority"] is False
    with pytest.raises(RuntimeError, match="NOT_READY"):
        lifecycle.summary()

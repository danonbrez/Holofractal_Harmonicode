from __future__ import annotations

import json
from pathlib import Path
import subprocess

from hhs_runtime.pass174.storage import PersistentEncryptedVectorStore
from hhs_runtime.pass191.main_history_hash216_hydration import (
    GENESIS_IDENTITY,
    LEGACY_FOUNDATION_ROOT,
    decode_frame,
    hydrate_main_history,
)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def _write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    _git(root, "add", ".")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def test_main_history_hydration_is_exact_reversible_and_idempotent(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    _git(repository, "init", "-b", "main")
    _git(repository, "config", "user.email", "hhs-test@example.invalid")
    _git(repository, "config", "user.name", "HHS Test")

    _write(repository, "README.md", "bootstrap\n")
    _commit(repository, "Initial repository state")

    _write(
        repository,
        "src/gate.py",
        "INVARIANT = 'single authority'\n"
        "def enforce_contract(value):\n"
        "    if not value:\n"
        "        raise ValueError('fail-closed contract')\n"
        "    return value\n",
    )
    source_commit = _commit(repository, "Implement invariant gate (#1)")
    source_parent = _git(repository, "rev-parse", f"{source_commit}^")
    source_patch = subprocess.check_output(
        [
            "git", "diff", "--no-color", "--no-ext-diff", "--unified=3",
            "--find-renames", source_parent, source_commit, "--", "src/gate.py",
        ],
        cwd=repository,
    )

    _write(repository, "README.md", "bootstrap\nordinary prose only\n")
    _commit(repository, "Documentation only (#2)")

    _write(
        repository,
        "contracts/runtime.json",
        '{"contract":"VM81_SINGLE_AUTHORITY","enforced":true}\n',
    )
    contract_commit = _commit(repository, "Add runtime contract (#3)")
    contract_parent = _git(repository, "rev-parse", f"{contract_commit}^")
    contract_patch = subprocess.check_output(
        [
            "git", "diff", "--no-color", "--no-ext-diff", "--unified=3",
            "--find-renames", contract_parent, contract_commit, "--",
            "contracts/runtime.json",
        ],
        cwd=repository,
    )

    state_root = tmp_path / "state"
    database = tmp_path / "vectors.sqlite3"
    key = tmp_path / "vectors.key"

    first = hydrate_main_history(
        repository_root=repository,
        ref="main",
        state_root=state_root,
        vector_database=database,
        vector_key=key,
    )
    assert first["classification"] == "HHS_MAIN_HISTORY_GREEN_PR_HASH216_HYDRATED"
    assert first["artifact_count"] == 2
    assert first["new_frames"] == first["frame_count"]
    assert first["reused_frames"] == 0
    assert first["verification"]["artifacts_reconstructed"] == 2

    manifest = json.loads((state_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["resolved_commit"] == contract_commit
    assert manifest["pr_commit_count"] == 3
    assert manifest["historical_ci_status_requeried"] is False
    assert manifest["canonical_mutation_authority"] is False
    assert manifest["vector_store_role"] == "READ_ONLY_HYDRATED_LOGIC_INDEX"

    by_path = {row["path"]: row for row in manifest["artifacts"]}
    assert set(by_path) == {"src/gate.py", "contracts/runtime.json"}
    assert by_path["src/gate.py"]["artifact_sha256"]
    assert by_path["contracts/runtime.json"]["selection_reason"] == "POLICY_SURFACE_PATH"

    store = PersistentEncryptedVectorStore(database, key_path=key)
    try:
        reconstructed = {}
        for path, artifact in by_path.items():
            payload = bytearray()
            for operation_key in artifact["operation_keys"]:
                obj, frame = store.retrieve(
                    operation_key,
                    legacy_foundation_root=LEGACY_FOUNDATION_ROOT,
                    genesis_identity=GENESIS_IDENTITY,
                )
                obj.hash216.verify()
                assert len(obj.hash216.character_indexes_sha256) == 216
                payload.extend(decode_frame(frame))
            reconstructed[path] = bytes(payload)
    finally:
        store.close()

    assert reconstructed["src/gate.py"] == source_patch
    assert reconstructed["contracts/runtime.json"] == contract_patch

    root_before = first["store_root_sha256"]
    second = hydrate_main_history(
        repository_root=repository,
        ref="main",
        state_root=state_root,
        vector_database=database,
        vector_key=key,
    )
    assert second["new_frames"] == 0
    assert second["reused_frames"] == second["frame_count"]
    assert second["store_root_sha256"] == root_before
    assert second["manifest_sha256"] == first["manifest_sha256"]


def test_non_pr_first_parent_commit_is_not_hydrated(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    _git(repository, "init", "-b", "main")
    _git(repository, "config", "user.email", "hhs-test@example.invalid")
    _git(repository, "config", "user.name", "HHS Test")
    _write(repository, "contracts/direct.json", '{"invariant":true}\n')
    _commit(repository, "Direct main maintenance commit")

    report = hydrate_main_history(
        repository_root=repository,
        ref="main",
        state_root=tmp_path / "state",
        vector_database=tmp_path / "vectors.sqlite3",
        vector_key=tmp_path / "vectors.key",
    )
    assert report["artifact_count"] == 0
    assert report["frame_count"] == 0
    assert report["verification"]["artifacts_reconstructed"] == 0

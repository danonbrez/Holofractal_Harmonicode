from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest

from hhs_runtime.checkpoint_ancestry import (
    MANIFEST_NAME,
    AncestryViolationError,
    ParentRejectedError,
    PatchApplicationError,
    apply_unified_patch,
    build_full_child_checkpoint,
    build_manifest,
    classify_archive,
    deterministic_zip,
    locate_first_corruption,
    parent_path_comparison,
    parse_unified_patch,
    sha256_file,
    validate_manifest_tree,
    write_json,
)


def make_root(root: Path, pass_id: str = "PASS_001") -> None:
    for directory in ["hhs_runtime", "hhs_backend", "hhs_python", "hhs_gui", "hhs_foundation", "tests", "contracts", "schemas", "tools"]:
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / "hhs_runtime" / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "hhs_backend" / "server.py").write_text("SERVER = True\n", encoding="utf-8")
    (root / "hhs_python" / "bridge.py").write_text("ABI = True\n", encoding="utf-8")
    (root / "hhs_gui" / "main.tsx").write_text("export const x = 1;\n", encoding="utf-8")
    (root / "hhs_foundation" / "invariants.py").write_text("O_NE_PI = True\n", encoding="utf-8")
    (root / "tests" / "test_core.py").write_text("def test_x(): assert True\n", encoding="utf-8")
    (root / "contracts" / "root.md").write_text("root\n", encoding="utf-8")
    (root / "schemas" / "root.json").write_text("{}\n", encoding="utf-8")
    (root / "tools" / "run.py").write_text("print('x')\n", encoding="utf-8")
    for index in range(32):
        (root / "hhs_runtime" / f"m{index}.py").write_text(f"X={index}\n", encoding="utf-8")
    cache = root / "hhs_runtime" / "__pycache__"; cache.mkdir()
    (cache / "core.pyc").write_bytes(b"cache")
    write_json(root / MANIFEST_NAME, build_manifest(root, pass_id=pass_id, parent_pass=None, parent_tree_root=None))


def make_full_zip(tmp_path: Path, name: str = "parent.zip") -> Path:
    root = tmp_path / f"{name}.root"; root.mkdir()
    make_root(root)
    archive = tmp_path / name
    deterministic_zip(root, archive)
    return archive


def test_evidence_only_archive_is_rejected(tmp_path: Path):
    archive = tmp_path / "evidence.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for i in range(10):
            zf.writestr(f"PASS_132_REPORT_{i}.json", "{}")
    assert classify_archive(archive).archive_class == "EVIDENCE_BUNDLE"
    delta = tmp_path / "delta"; delta.mkdir()
    with pytest.raises(ParentRejectedError):
        build_full_child_checkpoint(archive, delta, tmp_path / "out.zip", pass_id="PASS_2", parent_pass="PASS_1")


def test_full_child_preserves_parent_and_excludes_cache(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    delta = tmp_path / "delta"; (delta / "hhs_runtime").mkdir(parents=True)
    (delta / "hhs_runtime" / "new.py").write_text("NEW=True\n", encoding="utf-8")
    out = tmp_path / "child.zip"
    receipt = build_full_child_checkpoint(parent, delta, out, pass_id="PASS_002", parent_pass="PASS_001")
    assert receipt["status"] == "FULL_ANCESTOR_COPY_VERIFIED"
    assert classify_archive(out).archive_class == "FULL_SYSTEM_CHECKPOINT"
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
    assert "hhs_runtime/core.py" in names
    assert "hhs_runtime/new.py" in names
    assert not any("__pycache__" in name for name in names)


def test_changed_parent_path_is_preserved_as_same_identity(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    delta = tmp_path / "delta"; (delta / "hhs_runtime").mkdir(parents=True)
    (delta / "hhs_runtime" / "core.py").write_text("VALUE = 2\n", encoding="utf-8")
    out = tmp_path / "child.zip"
    receipt = build_full_child_checkpoint(parent, delta, out, pass_id="PASS_002", parent_pass="PASS_001")
    assert receipt["path_comparison"]["missing_parent_paths"] == 0
    assert receipt["path_comparison"]["changed_paths"] >= 1


def test_delete_control_is_rejected(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    delta = tmp_path / "delta"; delta.mkdir()
    (delta / "HHS_DELETE_PATHS.json").write_text('["hhs_runtime/core.py"]', encoding="utf-8")
    with pytest.raises(AncestryViolationError):
        build_full_child_checkpoint(parent, delta, tmp_path / "out.zip", pass_id="PASS_002", parent_pass="PASS_001")


def test_manifest_tamper_is_detected(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    extracted = tmp_path / "tree"
    with zipfile.ZipFile(parent) as zf:
        zf.extractall(extracted)
    (extracted / "hhs_runtime" / "core.py").write_text("tampered\n", encoding="utf-8")
    assert validate_manifest_tree(extracted)["ok"] is False


def test_unified_patch_applies_modify_and_create(tmp_path: Path):
    root = tmp_path / "root"; root.mkdir()
    (root / "a.txt").write_text("one\ntwo\n", encoding="utf-8")
    patch = tmp_path / "change.patch"
    patch.write_text(
        "--- a/a.txt\n+++ b/a.txt\n@@ -1,2 +1,2 @@\n one\n-two\n+three\n"
        "--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1,1 @@\n+new\n",
        encoding="utf-8",
    )
    receipt = apply_unified_patch(root, patch)
    assert (root / "a.txt").read_text() == "one\nthree\n"
    assert (root / "new.txt").read_text() == "new\n"
    assert receipt["deleted_paths"] == []


def test_unified_patch_deletion_is_rejected(tmp_path: Path):
    text = "--- a/a.txt\n+++ /dev/null\n@@ -1,1 +0,0 @@\n-x\n"
    with pytest.raises(AncestryViolationError):
        parse_unified_patch(text)


def test_deterministic_rebuild_bytes(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    delta = tmp_path / "delta"; (delta / "hhs_runtime").mkdir(parents=True)
    (delta / "hhs_runtime" / "new.py").write_text("NEW=True\n", encoding="utf-8")
    a = tmp_path / "a.zip"; b = tmp_path / "b.zip"
    build_full_child_checkpoint(parent, delta, a, pass_id="PASS_002", parent_pass="PASS_001")
    build_full_child_checkpoint(parent, delta, b, pass_id="PASS_002", parent_pass="PASS_001")
    assert sha256_file(a) == sha256_file(b)


def test_corruption_localization_finds_first_invalid_checkpoint(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    delta = tmp_path / "delta"; (delta / "hhs_runtime").mkdir(parents=True)
    (delta / "hhs_runtime" / "new.py").write_text("NEW=True\n", encoding="utf-8")
    child = tmp_path / "child.zip"
    build_full_child_checkpoint(parent, delta, child, pass_id="PASS_002", parent_pass="PASS_001")
    broken_root = tmp_path / "broken"
    with zipfile.ZipFile(child) as zf:
        zf.extractall(broken_root)
    (broken_root / "hhs_runtime" / "core.py").unlink()
    broken = tmp_path / "broken.zip"; deterministic_zip(broken_root, broken)
    report = locate_first_corruption([parent, child, broken])
    assert report["first_corrupt_index"] == 2
    assert report["chain_valid"] is False


def test_wrong_parent_sha_fails(tmp_path: Path):
    parent = make_full_zip(tmp_path)
    delta = tmp_path / "delta"; delta.mkdir()
    with pytest.raises(ParentRejectedError):
        build_full_child_checkpoint(
            parent, delta, tmp_path / "out.zip", pass_id="PASS_002", parent_pass="PASS_001",
            expected_parent_sha256="0" * 64,
        )


def test_executable_mode_survives_deterministic_zip_and_validation(tmp_path: Path):
    root = tmp_path / "mode-root"; root.mkdir()
    make_root(root)
    tool = root / "tools" / "run.py"
    tool.chmod(0o755)
    write_json(root / MANIFEST_NAME, build_manifest(root, pass_id="PASS_MODE", parent_pass=None, parent_tree_root=None))
    archive = tmp_path / "mode.zip"
    deterministic_zip(root, archive)
    classification = classify_archive(archive)
    assert classification.archive_class == "FULL_SYSTEM_CHECKPOINT"
    assert classification.manifest_valid is True

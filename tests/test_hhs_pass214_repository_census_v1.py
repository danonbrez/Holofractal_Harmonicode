from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from hhs_backend.runtime.hhs_pass214_repository_census_v1 import (
    Pass214CensusError,
    build_repository_census,
    load_and_validate_outputs,
    write_census_outputs,
)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


@pytest.fixture()
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init")
    git(root, "config", "user.name", "pass214-test")
    git(root, "config", "user.email", "pass214-test@example.invalid")
    write(root, "hhs_runtime/cache.py", "def reuse_vector(value):\n    return value\n\nclass Cache:\n    def lookup(self, key):\n        return key\n")
    write(root, "hhs_backend/runtime/hhs_pass165_learning_v1.py", "async def train_multimodal_weight(delta):\n    return delta\n")
    write(root, "native/pass213/dispatch.c", "int hhs_dispatch(unsigned long x) { return (int)x; }\n")
    write(root, "docs/pass214/CONTRACT.md", "# Contract\n")
    write(root, "tests/test_runtime.py", "def test_runtime():\n    assert True\n")
    write(root, "experimental/prototype.ts", "export const batchGpu = (x: number) => x;\n")
    write(root, "vendor/library.js", "function externalThing() { return 1; }\n")
    write(root, "broken.py", "def broken(:\n")
    write(root, "duplicate-a.json", '{"x":1}\n')
    write(root, "duplicate-b.json", '{"x":1}\n')
    git(root, "add", "-A")
    git(root, "commit", "-m", "fixture")
    return root


def test_complete_tree_classification_and_symbol_registry(repository: Path) -> None:
    result = build_repository_census(repository)
    summary = result["summary"]
    assert summary["coverage"]["classification_complete"] is True
    assert summary["coverage"]["tracked_tree_entries"] == len(result["path_census"])
    assert summary["coverage"]["candidate_symbols"] >= 5
    assert summary["coverage"]["pre_pass_or_unnumbered_entries"] > 0
    assert summary["coverage"]["numbered_pass_maximum"] == 214
    symbols = {(item["path"], item["entrypoint"]) for item in result["optimization_registry"]}
    assert ("hhs_runtime/cache.py", "reuse_vector") in symbols
    assert ("hhs_runtime/cache.py", "Cache.lookup") in symbols
    assert ("hhs_backend/runtime/hhs_pass165_learning_v1.py", "train_multimodal_weight") in symbols
    assert any(path == "native/pass213/dispatch.c" and name == "hhs_dispatch" for path, name in symbols)


def test_dispositions_and_duplicates(repository: Path) -> None:
    result = build_repository_census(repository)
    records = {item["path"]: item for item in result["path_census"]}
    assert records["docs/pass214/CONTRACT.md"]["disposition"] == "SCANNED_CONTRACT_ONLY"
    assert records["tests/test_runtime.py"]["disposition"] == "SCANNED_TEST_OR_EVIDENCE"
    assert records["experimental/prototype.ts"]["disposition"] == "SCANNED_EXPERIMENTAL"
    assert records["vendor/library.js"]["disposition"] == "SCANNED_NOT_APPLICABLE"
    assert records["broken.py"]["disposition"] == "SCANNED_BROKEN"
    duplicate_records = [records["duplicate-a.json"], records["duplicate-b.json"]]
    assert sorted(item["disposition"] for item in duplicate_records) == ["SCANNED_DATA_AUTHORITY", "SCANNED_DUPLICATE"]
    assert result["summary"]["coverage"]["exact_duplicate_groups"] >= 1


def test_multimodal_ml_and_pass213_families(repository: Path) -> None:
    result = build_repository_census(repository)
    counts = result["summary"]["optimization_family_counts"]
    assert counts["multimodal_machine_learning"] >= 1
    assert counts["cache_retrieval_reuse"] >= 1
    assert counts["compiled_rom_native_dispatch"] >= 1
    records = {item["path"]: item for item in result["path_census"]}
    assert records["hhs_backend/runtime/hhs_pass165_learning_v1.py"]["origin"]["pass_number"] == 165
    assert records["native/pass213/dispatch.c"]["origin"]["pass_number"] == 213


def test_outputs_are_root_bound_and_tamper_evident(repository: Path, tmp_path: Path) -> None:
    result = build_repository_census(repository)
    output = tmp_path / "evidence"
    write_census_outputs(result, output)
    loaded = load_and_validate_outputs(output)
    assert loaded["iteration1_summary"]["roots"] == result["summary"]["roots"]
    path = output / "optimization_registry.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[0]["entrypoint"] = "tampered"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(Pass214CensusError, match="optimization_registry_root_hash216"):
        load_and_validate_outputs(output)


def test_repeated_scan_is_semantically_deterministic(repository: Path) -> None:
    first = build_repository_census(repository)
    second = build_repository_census(repository)
    assert first["summary"]["roots"] == second["summary"]["roots"]
    assert first["summary"]["receipt_hash72"] == second["summary"]["receipt_hash72"]
    assert first["path_census"] == second["path_census"]
    assert first["optimization_registry"] == second["optimization_registry"]


def test_requires_git_metadata(tmp_path: Path) -> None:
    with pytest.raises(Pass214CensusError, match="GIT_METADATA_REQUIRED"):
        build_repository_census(tmp_path)

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys


def _write_json(path: pathlib.Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _build_package(root: pathlib.Path) -> pathlib.Path:
    root.mkdir(parents=True)
    _write_json(
        root / "schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["schema_ref", "value"],
            "properties": {
                "schema_ref": {"const": "schema.json"},
                "role": {"type": "string"},
                "value": {"type": "integer"},
            },
            "additionalProperties": True,
        },
    )
    examples = []
    for index in range(4):
        name = f"example_{index + 1}.json"
        examples.append(name)
        _write_json(
            root / name,
            {
                "schema_ref": "schema.json",
                "role": "example",
                "value": index,
            },
        )
    _write_json(
        root / "conformance_vectors.json",
        {
            "schema": "HHS_CONFORMANCE_VECTORS_V1",
            "conformance": True,
            "vector": [0, 1, 2, 3],
        },
    )
    _write_json(
        root / "domains.json",
        {
            "domains": [
                "canonical constants and minimum registry unit",
                "vm81 vm5184 logical control address",
                "hash216 snapshot identity",
                "fixed width noncommutative nested constraint bytecode",
                "novel transition inverse delta records",
                "cpu directed gpu dispatch manifest",
                "global serialization vector cache entries",
                "emergent object closure",
                "validation commit receipt",
                "deep learning candidate transition",
                "5184 phase error syndrome",
                "runtime state machine rule",
                "default implementation profile",
                "example checksum conformance vector",
            ]
        },
    )
    for index in range(15):
        _write_json(
            root / f"component_{index + 1:02d}.json",
            {
                "schema": "HHS_COMPONENT_V1",
                "component": index + 1,
            },
        )
    files = sorted(path.name for path in root.glob("*.json"))
    files.append("manifest.json")
    assert len(files) == 23
    entries = []
    for name in sorted(files):
        entry = {"path": name}
        path = root / name
        if path.exists():
            entry["sha256"] = _sha256(path)
        entries.append(entry)
    _write_json(
        root / "manifest.json",
        {
            "schema": "HHS_RUNTIME_JSON_SPECIFICATION_PACKAGE_MANIFEST_V1",
            "files": entries,
            "examples": examples,
            "expected_file_count": 23,
        },
    )
    return root


def test_pass208_json_spec_package_validator(tmp_path: pathlib.Path) -> None:
    root = _build_package(tmp_path / "package")
    repository = pathlib.Path(__file__).resolve().parents[1]
    validator = repository / "deployment/digitalocean/gpu/validate-json-spec-package.py"
    receipt = tmp_path / "receipt.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--root",
            str(root),
            "--expected-files",
            "23",
            "--expected-examples",
            "4",
            "--receipt",
            str(receipt),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    value = json.loads(receipt.read_text(encoding="utf-8"))
    assert value["ok"] is True
    assert value["json_file_count"] == 23
    assert value["schema_linked_instances_validated"] == 4
    assert value["declared_example_count"] >= 4
    assert all(value["domain_results"].values())


def test_pass208_json_spec_package_rejects_checksum_drift(tmp_path: pathlib.Path) -> None:
    root = _build_package(tmp_path / "package")
    repository = pathlib.Path(__file__).resolve().parents[1]
    validator = repository / "deployment/digitalocean/gpu/validate-json-spec-package.py"
    (root / "component_01.json").write_text('{"mutated":true}\n', encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(validator), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "checksum mismatch" in (completed.stdout + completed.stderr)


def test_pass208_digitalocean_scripts_are_fail_closed() -> None:
    repository = pathlib.Path(__file__).resolve().parents[1]
    scripts = [
        repository / "deployment/digitalocean/gpu/install.sh",
        repository / "deployment/digitalocean/gpu/hhs-gpu-preflight.sh",
        repository / "deployment/digitalocean/gpu/post-merge.sh",
    ]
    subprocess.run(["bash", "-n", *map(str, scripts)], check=True)
    installer = scripts[0].read_text(encoding="utf-8")
    preflight = scripts[1].read_text(encoding="utf-8")
    assert "HHS_PASS207_REQUIRE_PHYSICAL_GPU 1" in installer
    assert "HHS_PASS207_GPU_BACKEND OPENCL" in installer
    assert "HHS_JSON_SPEC_EXPECTED_FILES" in installer
    assert "ExecStartPre=" in installer
    assert "physical GPU fail-closed mode is required" in preflight
    assert "PHYSICAL_GPU_NOT_ACTIVE" in preflight
    assert "OPENCL_GPU_BACKEND_NOT_ACTIVE" in preflight

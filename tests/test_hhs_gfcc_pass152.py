from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from hhs_gfcc.codegen_c import generate_all as generate_c
from hhs_gfcc.codegen_shader import generate_all as generate_shaders
from hhs_gfcc.compiler import compile_native, compile_shaders
from hhs_gfcc.core import (
    ExactRational,
    build_delta369,
    build_dependency_graph,
    build_qudit9,
    build_vm81,
    canonical_spec,
    evaluate_dependency_graph,
    replay_workload,
    run_representative_workload,
    validate_spec,
    vm81_index,
    vm81_inverse,
)
from hhs_gfcc.validator import negative_matrix, positive_matrix, validate_core

SUBSYSTEM = ROOT / "native_projects" / "hhs_gfcc_pass152"


def test_gfcc_core_positive_symbol_shell_delta_vm81_hash_collision():
    results = positive_matrix()
    failed = [item for item in results if not item["passed"]]
    assert not failed, failed
    workload = run_representative_workload()
    assert workload["shell"]["values"]["e2"] == {"numerator": 8, "denominator": 1}
    assert workload["shell"]["values"]["b4"] == {"numerator": 4, "denominator": 1}
    assert workload["shell"]["terminal_residual"] == {"numerator": 0, "denominator": 1}
    assert workload["stage_ratio"] == {"numerator": 34, "denominator": 21}
    assert workload["delta369"]["ring_modulus"] == 9
    assert workload["delta369"]["coordinate_dimensions"] == 4
    assert workload["vm81"]["cell_count"] == 81
    assert len(workload["hash72"]["value"]) == 72
    assert len(workload["hash216"]["value"]) == 216
    assert workload["enforcement"]["invariants_preserved"] is True


def test_gfcc_dependency_ancestry_and_shell_first_order():
    spec = canonical_spec()
    graph = build_dependency_graph(spec)
    closure = evaluate_dependency_graph(spec, graph)
    assert closure["closed_shells"] == ["denominator", "numerator"]
    assert closure["ancestry"]["e2"] == ["d2", "c2"]
    assert closure["ancestry"]["b4"] == ["a2", "a2", "c2_minus_a2"]
    order = [entry["node"] for entry in closure["trace"]]
    assert order.index("e2") < order.index("outer_quotient")
    assert order.index("b4") < order.index("outer_quotient")


def test_gfcc_vm81_forward_inverse_exhaustive():
    observed = set()
    for row in range(9):
        for column in range(9):
            index = vm81_index(row, column)
            assert vm81_inverse(index) == (row, column)
            observed.add(index)
    assert observed == set(range(81))


def test_gfcc_codegen_is_byte_deterministic(tmp_path: Path):
    workload = run_representative_workload()
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_c = generate_c(workload, first_root)
    second_c = generate_c(workload, second_root)
    first_shader = generate_shaders(workload, first_root)
    second_shader = generate_shaders(workload, second_root)
    assert first_c["manifest_digest"] == second_c["manifest_digest"]
    assert first_shader["manifest_digest"] == second_shader["manifest_digest"]
    first_files = sorted((first_root / "generated").rglob("*"))
    for first in first_files:
        if first.is_file():
            relative = first.relative_to(first_root)
            assert first.read_bytes() == (second_root / relative).read_bytes()


def test_gfcc_native_reachability_compiles_and_executes():
    if shutil.which("cc") is None or shutil.which("ar") is None:
        pytest.skip("native compiler unavailable")
    workload = run_representative_workload()
    generate_c(workload, SUBSYSTEM)
    manifest = compile_native(ROOT)
    assert manifest["native_test_reached"] is True
    assert "GOLDEN_FRACTAL_CORRESPONDENCE_NATIVE_CORE_PASSED" in manifest["native_test_stdout"]
    assert any(item["path"].endswith("libhhs_gfcc.a") for item in manifest["artifacts"])
    assert any(item["path"].endswith("libhhs_gfcc.so") for item in manifest["artifacts"])
    assert any(item["path"].endswith("hhs-gfcc") for item in manifest["artifacts"])


def test_gfcc_shader_reachability_compiles_real_spirv():
    if shutil.which("glslangValidator") is None:
        pytest.skip("glslangValidator unavailable")
    workload = run_representative_workload()
    generate_shaders(workload, SUBSYSTEM)
    manifest = compile_shaders(ROOT)
    assert len(manifest["records"]) == 2
    for record in manifest["records"]:
        artifact = ROOT / record["artifact"]
        assert artifact.read_bytes()[:4] == bytes.fromhex("03022307")
        assert record["artifact_size"] >= 20


def test_gfcc_cli_machine_readable_reachability():
    command = [
        sys.executable,
        "-m",
        "hhs_gfcc.cli",
        "build-parameters",
        "--repo",
        str(ROOT),
        "--output",
        "json",
    ]
    environment = dict(__import__("os").environ)
    environment["PYTHONPATH"] = str(PYTHON_ROOT)
    completed = subprocess.run(command, cwd=ROOT, env=environment, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["result"]["receipt_count"] >= 11


def test_gfcc_negative_matrix():
    results = negative_matrix()
    failed = [item for item in results if not item["passed"]]
    assert not failed, failed
    report = validate_core()
    assert report["negative_passed"] == report["negative_total"]


def test_gfcc_replay_byte_identical_canonical_result():
    first = run_representative_workload("AUTHORITY_ROOT_A")
    second = run_representative_workload("AUTHORITY_ROOT_A")
    assert first == second
    replay = replay_workload(first)
    assert replay["match"] is True
    different = run_representative_workload("AUTHORITY_ROOT_B")
    assert different["canonical_result_digest"] != first["canonical_result_digest"]


def test_gfcc_required_python_modules_and_native_api_are_concrete():
    required_modules = {
        "__init__.py", "schema.py", "exact.py", "symbols.py", "dependencies.py",
        "delta369.py", "nonary.py", "vm81.py", "hash72.py", "hash216.py",
        "geometry.py", "shader.py", "collision.py", "codegen_c.py",
        "codegen_shader.py", "compiler.py", "validator.py", "receipts.py",
        "replay.py", "package.py", "cli.py",
    }
    package_files = {path.name for path in (PYTHON_ROOT / "hhs_gfcc").glob("*.py")}
    assert required_modules <= package_files
    native_source = (SUBSYSTEM / "src" / "hhs_gfcc.c").read_text(encoding="utf-8")
    for symbol in (
        "hhs_gfcc_context_init", "hhs_gfcc_load_parameters", "hhs_gfcc_build_parameters",
        "hhs_gfcc_close_shells", "hhs_gfcc_construct_vm81", "hhs_gfcc_project_hash72",
        "hhs_gfcc_index_hash216", "hhs_gfcc_build_transform",
        "hhs_gfcc_build_collision_constraint", "hhs_gfcc_enforce_collision",
        "hhs_gfcc_step", "hhs_gfcc_validate", "hhs_gfcc_replay",
    ):
        assert f"{symbol}(" in native_source
    prohibited = ("TODO", "NOT_IMPLEMENTED", "return HHS_GFCC_OK; /* stub")
    assert not any(token in native_source for token in prohibited)

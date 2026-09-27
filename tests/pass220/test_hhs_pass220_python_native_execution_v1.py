from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

import pytest

from hhs_runtime.hhs_pass220_python_native_execution_v1 import (
    HHSPythonNativeBoundError,
    HHSPythonNativeExecutor,
    python1_contract,
    python1_self_test,
)

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "native_projects" / "hhs_pass220_python_native_execution"
SOURCE = NATIVE / "src" / "hhs_pass220_python_native_execution_v1.c"
C_TEST = NATIVE / "tests" / "hhs_pass220_python_native_execution_v1_test.c"


@pytest.fixture()
def native_library(tmp_path: Path) -> Path:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    shared = tmp_path / "libhhs_python_native_execution_v1.so"
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-fPIC",
            "-shared",
            f"-I{NATIVE / 'include'}",
            str(SOURCE),
            "-o",
            str(shared),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return shared


def test_python1_native_c11_harness(tmp_path: Path) -> None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    exe = tmp_path / "python-native-execution-test"
    subprocess.run(
        [
            cc,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            f"-I{NATIVE / 'include'}",
            str(SOURCE),
            str(C_TEST),
            "-o",
            str(exe),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    completed = subprocess.run(
        [str(exe)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert completed.stdout.strip() == "PASS hhs_pass220_python_native_execution_v1"


def _cpython_result(source: str) -> int:
    namespace: dict[str, object] = {}
    exec(source, {"__builtins__": {}}, namespace)
    value = namespace["result"]
    assert isinstance(value, int) and not isinstance(value, bool)
    return value


@pytest.mark.parametrize(
    "source",
    [
        "result = 1 + 2 * 3",
        "result = (1 + 2) * 3",
        "result = -5 * 3 + 2",
        "a = 7\nb = a * 11\nresult = b - 2",
        "a = 1234567890123456789012345678901234567890\n"
        "b = 987654321098765432109876543210987654321\n"
        "result = a * b + a - b",
        "a = -999999999999999999999999999999999999999\n"
        "b = -888888888888888888888888888888888888888\n"
        "result = a * b - a + b",
        "result = ---5 + ++2 * -3",
    ],
)
def test_python1_native_execution_matches_cpython_for_supported_subset(
    native_library: Path,
    source: str,
) -> None:
    native = HHSPythonNativeExecutor(native_library).execute(source)
    assert native.projected_python_int == _cpython_result(source)
    assert native.result_decimal == str(_cpython_result(source))
    assert native.host_python_evaluator_used is False
    assert native.execution_authority == "HHS_C11_NATIVE_BIGINT_EXECUTION"


def test_python1_statement_count_and_source_identity_are_deterministic(
    native_library: Path,
) -> None:
    executor = HHSPythonNativeExecutor(native_library)
    source = "a=2\nb=3\nresult=(a+b)*4"
    first = executor.execute(source)
    second = executor.execute(source)
    assert first.statement_count == 3
    assert first.source_sha256 == second.source_sha256
    assert first.result_decimal == second.result_decimal == "20"


def test_python1_name_error_matches_python_exception_class(
    native_library: Path,
) -> None:
    executor = HHSPythonNativeExecutor(native_library)
    with pytest.raises(NameError):
        executor.execute("result = missing + 1")


@pytest.mark.parametrize(
    "source",
    [
        "result = __import__('os')",
        "result = open('x')",
        "result = eval('1+1')",
        "result = 2**8",
        "result = 1/2",
        "result = 1.25",
        "import os",
        "def f():\n    return 1",
        "result = [1,2,3]",
    ],
)
def test_python1_unadmitted_python_syntax_fails_closed(
    native_library: Path,
    source: str,
) -> None:
    executor = HHSPythonNativeExecutor(native_library)
    with pytest.raises((SyntaxError, NameError)):
        executor.execute(source)


def test_python1_5184_digit_bound_is_enforced(
    native_library: Path,
) -> None:
    executor = HHSPythonNativeExecutor(native_library)
    too_large = "9" * 5185
    with pytest.raises(HHSPythonNativeBoundError):
        executor.execute(f"result={too_large}")


def test_python1_self_test_closes(native_library: Path) -> None:
    result = python1_self_test(native_library)
    assert result["status"] == "PASS"
    assert result["host_escape_rejected"] is True
    assert result["host_python_evaluator_used"] is False
    assert len(result["receipt_sha256"]) == 64


def test_python1_contract_inherits_pass190_and_points_float_work_to_numpy1() -> None:
    contract = python1_contract()
    assert contract["python_external_contract_target"] == "CPython 3.12"
    assert contract["pass190_compatibility_schema"] == (
        "HHS_PYTHON_COMPATIBILITY_OPERATION_REGISTRY_V1"
    )
    assert contract["native_execution_language"] == "C11"
    assert contract["native_bigint_decimal_digits"] == 5184
    assert contract["host_ast_execution_required"] is False
    assert contract["host_eval_required"] is False
    assert contract["host_exec_required"] is False
    assert contract["host_compile_required"] is False
    assert contract["host_python_arithmetic_authority"] is False
    assert contract["numpy1_bridge_next"] is True


def test_python1_runtime_membrane_has_no_host_parser_or_evaluator_calls() -> None:
    source = (
        ROOT / "hhs_runtime" / "hhs_pass220_python_native_execution_v1.py"
    ).read_text(encoding="utf-8")
    assert "import ast" not in source
    for forbidden in ("eval", "exec", "compile"):
        assert re.search(rf"\b{forbidden}\s*\(", source) is None


def test_python1_c_kernel_has_no_host_python_dependency() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    lowered = source.lower()
    assert "python.h" not in lowered
    assert "pyeval" not in lowered
    assert "pyobject" not in lowered
    assert "malloc(" not in lowered
    assert "calloc(" not in lowered
    assert "realloc(" not in lowered

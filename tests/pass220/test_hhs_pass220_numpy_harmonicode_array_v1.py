from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from hhs_runtime.hhs_pass220_numpy_harmonicode_array_v1 import (
    HHSNumPyCompatibilityError,
    HHSNumPyEngine,
    HHSNumPyScalar,
    numpy1_contract,
)

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "native_projects" / "hhs_pass220_numpy_native_array_kernel"
SOURCE = NATIVE / "src" / "hhs_pass220_numpy_native_array_kernel_v1.c"
C_TEST = NATIVE / "tests" / "hhs_pass220_numpy_native_array_kernel_v1_test.c"


@pytest.fixture()
def native_library(tmp_path: Path) -> Path:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    shared = tmp_path / "libhhs_numpy_native_array_kernel_v1.so"
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


def test_numpy1_native_c11_array_kernel_harness(tmp_path: Path) -> None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    exe = tmp_path / "numpy-native-array-test"
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
    result = subprocess.run(
        [str(exe)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    assert result.stdout.strip() == "PASS hhs_pass220_numpy_native_array_kernel_v1"


def _numpy_float64_bits(value) -> tuple[int, ...]:
    array = np.asarray(value, dtype=np.float64)
    return tuple(int(item) for item in array.view(np.uint64).reshape(-1))


def test_numpy1_float64_ingress_egress_preserves_ieee_bits_and_bigint_carrier(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    values = [0.1, -2.5, -0.0, 1.0 / 3.0]
    array = engine.array(values, dtype="float64")

    assert array.shape == (4,)
    assert array.dtype == "float64"
    assert array.ieee_bits() == _numpy_float64_bits(values)
    assert _numpy_float64_bits(array.tolist()) == _numpy_float64_bits(values)

    for scalar, expected_bits, serialized in zip(
        array._data,
        array.ieee_bits(),
        array.bigint_5184(),
    ):
        assert len(serialized) == 5184
        assert scalar.recover_ingress_identity() == expected_bits


def test_numpy1_exact_decimal_ingress_matches_numpy_float64_rounding(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    hhs = engine.array(
        ["0.1", "1.2345678901234567", "-9007199254740993"],
        dtype="float64",
    )
    numpy = np.asarray(
        ["0.1", "1.2345678901234567", "-9007199254740993"],
        dtype=np.float64,
    )
    assert hhs.ieee_bits() == _numpy_float64_bits(numpy)


def test_numpy1_native_broadcast_add_is_numpy_bit_equivalent(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    left_values = [[0.1], [2.0]]
    right_values = [[3.0, -4.5, 0.25]]
    left = engine.array(left_values, dtype="float64")
    right = engine.array(right_values, dtype="float64")

    result = engine.add(left, right)
    expected = np.add(
        np.asarray(left_values, dtype=np.float64),
        np.asarray(right_values, dtype=np.float64),
    )

    assert result.shape == expected.shape
    assert result.dtype == "float64"
    assert result.ieee_bits() == _numpy_float64_bits(expected)


def test_numpy1_native_broadcast_multiply_is_numpy_bit_equivalent(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    left_values = [[1.5], [-2.0]]
    right_values = [[0.5, 4.0, -3.25]]
    result = engine.multiply(
        engine.array(left_values, dtype="float64"),
        engine.array(right_values, dtype="float64"),
    )
    expected = np.multiply(
        np.asarray(left_values, dtype=np.float64),
        np.asarray(right_values, dtype=np.float64),
    )
    assert result.shape == expected.shape
    assert result.ieee_bits() == _numpy_float64_bits(expected)


@pytest.mark.parametrize(
    ("left", "right", "operation"),
    [
        (-0.0, -0.0, "add"),
        (-0.0, 0.0, "subtract"),
        (-0.0, 3.0, "multiply"),
    ],
)
def test_numpy1_signed_zero_boundaries_match_numpy(
    native_library: Path,
    left: float,
    right: float,
    operation: str,
) -> None:
    engine = HHSNumPyEngine(native_library)
    lhs = engine.array(left, dtype="float64")
    rhs = engine.array(right, dtype="float64")
    if operation == "add":
        result = engine.add(lhs, rhs)
        expected = np.add(np.float64(left), np.float64(right))
    elif operation == "subtract":
        result = engine.subtract(lhs, rhs)
        expected = np.subtract(np.float64(left), np.float64(right))
    else:
        result = engine.multiply(lhs, rhs)
        expected = np.multiply(np.float64(left), np.float64(right))
    assert result.ieee_bits() == _numpy_float64_bits(expected)


def test_numpy1_int64_arithmetic_wrap_matches_numpy(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    lhs = engine.array([2**63 - 1, -(2**63)], dtype="int64")
    rhs = engine.array([1, -1], dtype="int64")

    with np.errstate(over="ignore"):
        expected_add = np.add(
            np.asarray([2**63 - 1, -(2**63)], dtype=np.int64),
            np.asarray([1, -1], dtype=np.int64),
        )
        expected_mul = np.multiply(
            np.asarray([2**63 - 1, -(2**63)], dtype=np.int64),
            np.asarray([1, -1], dtype=np.int64),
        )

    assert engine.add(lhs, rhs).tolist() == expected_add.tolist()
    assert engine.multiply(lhs, rhs).tolist() == expected_mul.tolist()


def test_numpy1_int64_to_float64_promotion_rounds_before_operation(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    lhs = engine.array([2**60 + 1], dtype="int64")
    rhs = engine.array([1.0], dtype="float64")
    result = engine.add(lhs, rhs)
    expected = np.add(
        np.asarray([2**60 + 1], dtype=np.int64),
        np.asarray([1.0], dtype=np.float64),
    )
    assert result.dtype == "float64"
    assert result.ieee_bits() == _numpy_float64_bits(expected)


def test_numpy1_float64_palindromic_symbolic_bigint_witness_is_value_bound(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    scalar = engine.array([0.1], dtype="float64")._data[0]
    witness = scalar.palindromic_symbolic_witness()

    assert witness["schema"] == "HHS_PASS_220_NUMPY1_FLOAT64_PALINDROMIC_WITNESS_V1"
    assert witness["recovered_ieee_bits"] == witness["ieee_bits"]
    assert len(witness["bigint_5184"]) == 5184
    assert witness["host_float_arithmetic_used"] is False
    assert witness["constructor"]["representation_views"]["bigint_5184"] == witness["bigint_5184"]
    assert witness["validation"]["valid"] is True


def test_numpy1_rejects_out_of_range_int64_ingress(
    native_library: Path,
) -> None:
    engine = HHSNumPyEngine(native_library)
    with pytest.raises(HHSNumPyCompatibilityError, match="INT64_INGRESS_OUT_OF_RANGE"):
        engine.array([2**63], dtype="int64")


def test_numpy1_contract_keeps_numpy_as_external_membrane(
    native_library: Path,
) -> None:
    contract = numpy1_contract(HHSNumPyEngine(native_library))
    assert contract["numpy_external_contract_target"] is True
    assert contract["numpy_internal_dependency_required"] is False
    assert contract["native_broadcast_kernel"] is True
    assert contract["float64_internal_pre_round_symbolic_exact"] is True
    assert contract["float64_rounding"] == "INTEGER_ONLY_NEAREST_EVEN_BINARY64"
    assert contract["bigint_serialization_characters_per_scalar"] == 5184
    assert contract["bigint_serialization_is_value_bound"] is True
    assert contract["host_float_arithmetic_canonical_authority"] is False


def test_numpy1_runtime_module_does_not_import_numpy() -> None:
    source = (
        ROOT / "hhs_runtime" / "hhs_pass220_numpy_harmonicode_array_v1.py"
    ).read_text(encoding="utf-8")
    lowered = source.lower()
    assert "import numpy" not in lowered
    assert "from numpy" not in lowered

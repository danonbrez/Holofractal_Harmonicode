from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from hhs_backend.runtime.hhs_pass220_native_litert_execution_graph_v1 import (
    LiteRT2OperationSpec,
    LiteRT2TensorSpec,
    NativeLiteRTExecutionGraph,
    NativeLiteRTGraphError,
    litert2_contract,
)

ROOT = Path(__file__).resolve().parents[2]
GRAPH_NATIVE = ROOT / "native_projects" / "hhs_pass220_litert_native_execution_graph"
GRAPH_SOURCE = GRAPH_NATIVE / "src" / "hhs_pass220_litert_native_execution_graph_v1.c"
NUMPY_NATIVE = ROOT / "native_projects" / "hhs_pass220_numpy_native_array_kernel"
NUMPY_SOURCE = NUMPY_NATIVE / "src" / "hhs_pass220_numpy_native_array_kernel_v1.c"
MODEL_HASH = "M" * 216


@pytest.fixture()
def native_libraries(tmp_path: Path) -> tuple[Path, Path]:
    cc = shutil.which("cc") or shutil.which("gcc")
    if not cc:
        pytest.skip("C compiler unavailable")
    graph = tmp_path / "libhhs_litert_native_execution_graph_v1.so"
    numpy1 = tmp_path / "libhhs_numpy_native_array_kernel_v1.so"
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
            f"-I{GRAPH_NATIVE / 'include'}",
            str(GRAPH_SOURCE),
            "-o",
            str(graph),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
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
            f"-I{NUMPY_NATIVE / 'include'}",
            str(NUMPY_SOURCE),
            "-o",
            str(numpy1),
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return graph, numpy1


def _bits(value) -> tuple[int, ...]:
    arr = np.asarray(value, dtype=np.float64)
    return tuple(int(item) for item in arr.view(np.uint64).reshape(-1))


def test_litert2_float64_broadcast_add_matches_numpy_bits(
    native_libraries: tuple[Path, Path],
) -> None:
    graph_lib, numpy_lib = native_libraries
    graph = NativeLiteRTExecutionGraph(
        graph_library=graph_lib,
        numpy1_library=numpy_lib,
        model_identity_hash216=MODEL_HASH,
        graph_name="broadcast-add",
        tensors=(
            LiteRT2TensorSpec("left", "float64", (2, 1), input=True),
            LiteRT2TensorSpec("right", "float64", (1, 3), input=True),
            LiteRT2TensorSpec("out", "float64", (2, 3), output=True),
        ),
        operations=(
            LiteRT2OperationSpec("add", "add", "left", "right", "out"),
        ),
    )
    left = [[0.1], [2.0]]
    right = [[3.0, -4.5, 0.25]]
    result = graph.execute({"left": left, "right": right})
    expected = np.add(
        np.asarray(left, dtype=np.float64),
        np.asarray(right, dtype=np.float64),
    )
    assert result.outputs["out"].shape == expected.shape
    assert result.outputs["out"].ieee_bits() == _bits(expected)
    assert result.witness["numeric_authority"] == "NUMPY1_HARMONICODE"
    assert result.witness["host_float_canonical_authority"] is False
    assert len(result.witness["witness_hash216"]) == 216
    assert len(result.witness["operations"][0]["bigint_5184_sha256"]) == 6


def test_litert2_multi_operation_ordering_uses_prior_native_output(
    native_libraries: tuple[Path, Path],
) -> None:
    graph_lib, numpy_lib = native_libraries
    graph = NativeLiteRTExecutionGraph(
        graph_library=graph_lib,
        numpy1_library=numpy_lib,
        model_identity_hash216=MODEL_HASH,
        graph_name="add-then-multiply",
        tensors=(
            LiteRT2TensorSpec("a", "float64", (2,), input=True),
            LiteRT2TensorSpec("b", "float64", (2,), input=True),
            LiteRT2TensorSpec("scale", "float64", (1,), constant=True),
            LiteRT2TensorSpec("sum", "float64", (2,)),
            LiteRT2TensorSpec("out", "float64", (2,), output=True),
        ),
        operations=(
            LiteRT2OperationSpec("sum-op", "add", "a", "b", "sum"),
            LiteRT2OperationSpec(
                "scale-op", "multiply", "sum", "scale", "out"
            ),
        ),
        constants={"scale": [0.5]},
    )
    result = graph.execute({"a": [0.1, -0.0], "b": [0.2, 4.0]})
    expected = (
        np.asarray([0.1, -0.0], dtype=np.float64)
        + np.asarray([0.2, 4.0], dtype=np.float64)
    ) * np.asarray([0.5], dtype=np.float64)
    assert result.outputs["out"].ieee_bits() == _bits(expected)
    assert [item["operation"] for item in result.witness["operations"]] == [
        "sum-op",
        "scale-op",
    ]


def test_litert2_int64_overflow_matches_numpy1_numpy_contract(
    native_libraries: tuple[Path, Path],
) -> None:
    graph_lib, numpy_lib = native_libraries
    graph = NativeLiteRTExecutionGraph(
        graph_library=graph_lib,
        numpy1_library=numpy_lib,
        model_identity_hash216=MODEL_HASH,
        graph_name="int64-wrap",
        tensors=(
            LiteRT2TensorSpec("a", "int64", (2,), input=True),
            LiteRT2TensorSpec("b", "int64", (2,), input=True),
            LiteRT2TensorSpec("out", "int64", (2,), output=True),
        ),
        operations=(
            LiteRT2OperationSpec("mul", "multiply", "a", "b", "out"),
        ),
    )
    a = [2**63 - 1, -(2**63)]
    b = [2, -1]
    result = graph.execute({"a": a, "b": b})
    with np.errstate(over="ignore"):
        expected = np.multiply(
            np.asarray(a, dtype=np.int64),
            np.asarray(b, dtype=np.int64),
        )
    assert result.outputs["out"].tolist() == expected.tolist()


def test_litert2_graph_identity_and_execution_are_deterministic(
    native_libraries: tuple[Path, Path],
) -> None:
    graph_lib, numpy_lib = native_libraries

    def build():
        return NativeLiteRTExecutionGraph(
            graph_library=graph_lib,
            numpy1_library=numpy_lib,
            model_identity_hash216=MODEL_HASH,
            graph_name="replay",
            tensors=(
                LiteRT2TensorSpec("x", "int64", (3,), input=True),
                LiteRT2TensorSpec("y", "int64", (3,), input=True),
                LiteRT2TensorSpec("out", "int64", (3,), output=True),
            ),
            operations=(
                LiteRT2OperationSpec(
                    "subtract", "subtract", "x", "y", "out"
                ),
            ),
        )

    first = build()
    second = build()
    assert first.graph_identity_hash216 == second.graph_identity_hash216
    assert first.graph_fingerprint64 == second.graph_fingerprint64
    first_result = first.execute({"x": [5, 6, 7], "y": [1, 2, 3]})
    second_result = second.execute({"x": [5, 6, 7], "y": [1, 2, 3]})
    assert (
        first_result.witness["witness_hash216"]
        == second_result.witness["witness_hash216"]
    )
    assert first_result.outputs["out"].tolist() == [4, 4, 4]


def test_litert2_rejects_unadmitted_float32_execution(
    native_libraries: tuple[Path, Path],
) -> None:
    graph_lib, numpy_lib = native_libraries
    with pytest.raises(
        NativeLiteRTGraphError,
        match="EXECUTION_DTYPE_NOT_ADMITTED",
    ):
        NativeLiteRTExecutionGraph(
            graph_library=graph_lib,
            numpy1_library=numpy_lib,
            model_identity_hash216=MODEL_HASH,
            graph_name="float32-not-yet",
            tensors=(
                LiteRT2TensorSpec("x", "float32", (1,), input=True),
                LiteRT2TensorSpec("y", "float32", (1,), input=True),
                LiteRT2TensorSpec("out", "float32", (1,), output=True),
            ),
            operations=(
                LiteRT2OperationSpec("add", "add", "x", "y", "out"),
            ),
        )


def test_litert2_rejects_declared_broadcast_output_mismatch(
    native_libraries: tuple[Path, Path],
) -> None:
    graph_lib, numpy_lib = native_libraries
    with pytest.raises(
        NativeLiteRTGraphError,
        match="GRAPH_REGISTRATION_REJECTED:7",
    ):
        NativeLiteRTExecutionGraph(
            graph_library=graph_lib,
            numpy1_library=numpy_lib,
            model_identity_hash216=MODEL_HASH,
            graph_name="bad-broadcast",
            tensors=(
                LiteRT2TensorSpec("x", "float64", (2, 1), input=True),
                LiteRT2TensorSpec("y", "float64", (1, 3), input=True),
                LiteRT2TensorSpec("out", "float64", (2, 4), output=True),
            ),
            operations=(
                LiteRT2OperationSpec("add", "add", "x", "y", "out"),
            ),
        )


def test_litert2_contract_keeps_float32_and_quantized_execution_fail_closed() -> None:
    contract = litert2_contract()
    assert contract["native_graph_topology_authority"] is True
    assert contract["native_graph_numeric_authority"] is False
    assert contract["numpy1_numeric_authority"] is True
    assert contract["admitted_execution_dtypes"] == ("int64", "float64")
    assert contract["admitted_operations"] == (
        "add",
        "subtract",
        "multiply",
    )
    assert contract["float32_litert_metadata_registrable"] is True
    assert contract["float32_canonical_execution_admitted"] is False
    assert contract["quantized_litert_metadata_registrable"] is True
    assert contract["quantized_canonical_execution_admitted"] is False


def test_litert2_runtime_does_not_import_numpy_or_external_litert() -> None:
    source = (
        ROOT
        / "hhs_backend"
        / "runtime"
        / "hhs_pass220_native_litert_execution_graph_v1.py"
    ).read_text(encoding="utf-8").lower()
    assert "import numpy" not in source
    assert "from numpy" not in source
    assert "import litert_lm" not in source
    assert "ai_edge_litert" not in source

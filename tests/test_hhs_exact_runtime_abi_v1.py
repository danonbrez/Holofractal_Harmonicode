from __future__ import annotations

import ctypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from hhs_python.runtime import hhs_exact_ctypes_bridge as exact_mod
from hhs_python.runtime.hhs_exact_ctypes_bridge import HHSExactRuntimeBridge
from hhs_runtime.pass175.x86_64 import ExactX86Decoder


ROOT = Path(__file__).resolve().parents[1]


def test_exact_abi_self_validation_and_descriptor() -> None:
    assert HHSExactRuntimeBridge.validate()
    descriptor = HHSExactRuntimeBridge.descriptor()
    assert descriptor["hash72_len"] == 72
    assert descriptor["hash72_coords"] == 5184
    assert descriptor["vm81_cells"] == 81
    assert descriptor["vm81_word_bits"] == 64
    assert descriptor["vm81_frame_bits"] == 5184
    assert descriptor["vm81_frame_bytes"] == 648
    assert descriptor["phase_basis_count"] == 8
    assert descriptor["phase_pair_count"] == 64
    assert descriptor["x86_max_instruction_bytes"] == 15
    assert descriptor["legacy_v1_layout_preserved"] == 1


def test_hash72_5184_positional_plane_roundtrips_exhaustively() -> None:
    for coord in range(5184):
        position, symbol = HHSExactRuntimeBridge.hash72_decode(coord)
        assert HHSExactRuntimeBridge.hash72_coord(position, symbol) == coord


def test_vm81_5184_ordered_phase_addresses_roundtrip_exhaustively() -> None:
    for address in range(5184):
        cell, left, right = HHSExactRuntimeBridge.vm5184_decode(address)
        assert HHSExactRuntimeBridge.vm5184_address(cell, left, right) == address


def test_ordered_phase_products_preserve_noncommutative_identity() -> None:
    xy = HHSExactRuntimeBridge.phase_product(0, 1)
    yx = HHSExactRuntimeBridge.phase_product(1, 0)
    zw = HHSExactRuntimeBridge.phase_product(2, 3)
    wz = HHSExactRuntimeBridge.phase_product(3, 2)
    assert xy["phase"] == 0
    assert yx["phase"] == 36
    assert zw["phase"] == 0
    assert wz["phase"] == 36
    assert xy["ordered_tag"] == 0x5859
    assert yx["ordered_tag"] == 0x5958
    assert zw["ordered_tag"] == 0x5A57
    assert wz["ordered_tag"] == 0x575A
    assert xy["ordered_tag"] != yx["ordered_tag"]
    assert zw["ordered_tag"] != wz["ordered_tag"]


def test_vm81_raw_x86_64_frame_is_exact_648_byte_roundtrip() -> None:
    raw = bytes((index * 37 + 11) & 0xFF for index in range(648))
    assert HHSExactRuntimeBridge.frame_roundtrip(raw) == raw


def test_x86_64_instruction_and_stream_ingress_egress_are_byte_exact() -> None:
    samples = [
        bytes.fromhex("90"),
        bytes.fromhex("f34801d8"),
        bytes.fromhex("4889d8"),
        bytes.fromhex("0f05"),
        bytes.fromhex("c5f877"),
        bytes.fromhex("e978563412"),
        bytes.fromhex("67488b042578563412"),
    ]
    decoder = ExactX86Decoder()
    for raw in samples:
        assert HHSExactRuntimeBridge.x86_instruction_roundtrip(raw) == raw
        assert decoder.decode(raw).reencode() == raw

    stream = b"".join(samples)
    assert HHSExactRuntimeBridge.x86_bytecode_roundtrip(stream) == stream


def test_legacy_v1_binary_layout_remains_frozen() -> None:
    lib = exact_mod._RUNTIME_LIB
    lib.hhs_sizeof_runtime_state.argtypes = []
    lib.hhs_sizeof_runtime_state.restype = ctypes.c_size_t
    lib.hhs_sizeof_receipt.argtypes = []
    lib.hhs_sizeof_receipt.restype = ctypes.c_size_t
    lib.hhs_sizeof_tensor_state.argtypes = []
    lib.hhs_sizeof_tensor_state.restype = ctypes.c_size_t
    lib.hhs_sizeof_graph_node.argtypes = []
    lib.hhs_sizeof_graph_node.restype = ctypes.c_size_t
    lib.hhs_sizeof_graph_edge.argtypes = []
    lib.hhs_sizeof_graph_edge.restype = ctypes.c_size_t

    assert lib.hhs_sizeof_runtime_state() == 992
    assert lib.hhs_sizeof_receipt() == 192
    assert lib.hhs_sizeof_tensor_state() == 40
    assert lib.hhs_sizeof_graph_node() == 112
    assert lib.hhs_sizeof_graph_edge() == 24


def test_exact_authority_sources_have_no_approximate_numeric_types() -> None:
    for relative in (
        "hhs_runtime/include/hhs_runtime_exact_abi.h",
        "hhs_runtime/c/hhs_runtime_exact_abi.c",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for forbidden in (
            "double",
            "float",
            "<math.h>",
            "sqrt(",
            "sin(",
            "cos(",
            "pow(",
            "log(",
            "exp(",
        ):
            assert forbidden not in text


def test_pass219_i119_pass205_binding_and_membrane_conformance() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with tempfile.TemporaryDirectory(prefix="hhs-i119-") as temp_dir:
        temp = Path(temp_dir)
        exact_obj = temp / "exact.o"
        c_bin = temp / "pass205-c"
        cpp_bin = temp / "pass205-cpp"
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
                "-o", str(exact_obj),
            ],
            cwd=ROOT,
            check=True,
            env=env,
        )
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass205_1_19.c",
                str(exact_obj), "-o", str(c_bin),
            ],
            cwd=ROOT,
            check=True,
            env=env,
        )
        subprocess.run([str(c_bin)], cwd=ROOT, check=True, env=env)
        subprocess.run(
            [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass205_1_19.cpp",
                str(exact_obj), "-o", str(cpp_bin),
            ],
            cwd=ROOT,
            check=True,
            env=env,
        )
        subprocess.run([str(cpp_bin)], cwd=ROOT, check=True, env=env)
    subprocess.run(
        [sys.executable, "tests/pass219/test_pass219_cumulative_pass205_membrane_i119.py"],
        cwd=ROOT,
        check=True,
        env=env,
    )


def test_pass219_i120_pass204_binding_and_membrane_conformance() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with tempfile.TemporaryDirectory(prefix="hhs-i120-") as temp_dir:
        temp = Path(temp_dir)
        exact_obj = temp / "exact.o"
        c_bin = temp / "pass204-c"
        cpp_bin = temp / "pass204-cpp"
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
                "-o", str(exact_obj),
            ],
            cwd=ROOT,
            check=True,
            env=env,
        )
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass204_1_20.c",
                str(exact_obj), "-o", str(c_bin),
            ],
            cwd=ROOT,
            check=True,
            env=env,
        )
        subprocess.run([str(c_bin)], cwd=ROOT, check=True, env=env)
        subprocess.run(
            [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass204_1_20.cpp",
                str(exact_obj), "-o", str(cpp_bin),
            ],
            cwd=ROOT,
            check=True,
            env=env,
        )
        subprocess.run([str(cpp_bin)], cwd=ROOT, check=True, env=env)
    subprocess.run(
        [sys.executable, "tests/pass219/test_pass219_cumulative_pass204_membrane_i120.py"],
        cwd=ROOT,
        check=True,
        env=env,
    )


def test_pass219_i121_pass203_binding_and_membrane_conformance() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with tempfile.TemporaryDirectory(prefix="hhs-i121-") as temp_dir:
        temp = Path(temp_dir)
        exact_obj = temp / "exact.o"
        c_bin = temp / "pass203-c"
        cpp_bin = temp / "pass203-cpp"
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
                "-o", str(exact_obj),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass203_1_21.c",
                str(exact_obj), "-o", str(c_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(c_bin)], cwd=ROOT, check=True, env=env)
        subprocess.run(
            [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass203_1_21.cpp",
                str(exact_obj), "-o", str(cpp_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(cpp_bin)], cwd=ROOT, check=True, env=env)
    subprocess.run(
        [sys.executable, "tests/pass219/test_pass219_cumulative_pass203_membrane_i121.py"],
        cwd=ROOT, check=True, env=env,
    )


def test_pass219_i122_pass202_binding_and_membrane_conformance() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with tempfile.TemporaryDirectory(prefix="hhs-i122-") as temp_dir:
        temp = Path(temp_dir)
        exact_obj = temp / "exact.o"
        c_bin = temp / "pass202-c"
        cpp_bin = temp / "pass202-cpp"
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
                "-o", str(exact_obj),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass202_1_22.c",
                str(exact_obj), "-o", str(c_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(c_bin)], cwd=ROOT, check=True, env=env)
        subprocess.run(
            [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass202_1_22.cpp",
                str(exact_obj), "-o", str(cpp_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(cpp_bin)], cwd=ROOT, check=True, env=env)
    subprocess.run(
        [sys.executable, "tests/pass219/test_pass219_cumulative_pass202_membrane_i122.py"],
        cwd=ROOT, check=True, env=env,
    )


def test_pass219_i123_pass201_binding_and_membrane_conformance() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with tempfile.TemporaryDirectory(prefix="hhs-i123-") as temp_dir:
        temp = Path(temp_dir)
        exact_obj = temp / "exact.o"
        c_bin = temp / "pass201-c"
        cpp_bin = temp / "pass201-cpp"
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
                "-o", str(exact_obj),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass201_1_23.c",
                str(exact_obj), "-o", str(c_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(c_bin)], cwd=ROOT, check=True, env=env)
        subprocess.run(
            [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass201_1_23.cpp",
                str(exact_obj), "-o", str(cpp_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(cpp_bin)], cwd=ROOT, check=True, env=env)
    subprocess.run(
        [sys.executable, "tests/pass219/test_pass219_cumulative_pass201_membrane_i123.py"],
        cwd=ROOT, check=True, env=env,
    )


def test_pass219_i124_pass200c_binding_and_membrane_conformance() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with tempfile.TemporaryDirectory(prefix="hhs-i124-") as temp_dir:
        temp = Path(temp_dir)
        exact_obj = temp / "exact.o"
        c_bin = temp / "pass200c-c"
        cpp_bin = temp / "pass200c-cpp"
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "-c", "hhs_runtime/c/hhs_runtime_exact_abi.c",
                "-o", str(exact_obj),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run(
            [
                "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass200c_1_24.c",
                str(exact_obj), "-o", str(c_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(c_bin)], cwd=ROOT, check=True, env=env)
        subprocess.run(
            [
                "g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
                "-Ihhs_runtime/include", "tests/pass219/test_pass219_inherited_pass200c_1_24.cpp",
                str(exact_obj), "-o", str(cpp_bin),
            ], cwd=ROOT, check=True, env=env,
        )
        subprocess.run([str(cpp_bin)], cwd=ROOT, check=True, env=env)
    subprocess.run(
        [sys.executable, "tests/pass219/test_pass219_cumulative_pass200c_membrane_i124.py"],
        cwd=ROOT, check=True, env=env,
    )

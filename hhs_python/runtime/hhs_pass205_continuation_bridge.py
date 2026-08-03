"""Native bridge for the Pass 205 deterministic VM5184 × G243 continuation ABI."""
from __future__ import annotations

import ctypes
import os
import pathlib
import platform
import subprocess
from ctypes import POINTER, Structure, c_char, c_size_t, c_uint8, c_uint16, c_uint32, c_uint64
from typing import Iterable, Mapping, Sequence

CELL_COUNT = 81
BITS_PER_CELL = 64
STATE_BITS = CELL_COUNT * BITS_PER_CELL
CONTROL_COUNT = 243
Q_COUNT = STATE_BITS * CONTROL_COUNT
PROJECTION_CHANNELS = 32
HASH72_LEN = 72
HASH216_LEN = 216
UINT64_MASK = (1 << 64) - 1


class HHSHash72(Structure):
    _fields_ = [("value", c_char * (HASH72_LEN + 1))]


class HHSHash216(Structure):
    _fields_ = [("value", c_char * (HASH216_LEN + 1))]


class HHSPass205State(Structure):
    _fields_ = [("cells", c_uint64 * CELL_COUNT)]


class HHSPass205Delta(Structure):
    _fields_ = [
        ("count", c_uint16),
        ("cell_index", c_uint8 * CELL_COUNT),
        ("control_g", c_uint8 * CELL_COUNT),
        ("xor_mask", c_uint64 * CELL_COUNT),
    ]


class HHSPass205Frontier(Structure):
    _fields_ = [("cell", c_uint8 * CELL_COUNT)]


class HHSPass205Projection(Structure):
    _fields_ = [("channel", (c_uint32 * CELL_COUNT) * PROJECTION_CHANNELS)]


class HHSPass205Token(Structure):
    _fields_ = [
        ("parent_root", HHSHash216),
        ("content_root", HHSHash216),
        ("delta_root", HHSHash216),
        ("hydration_root", HHSHash216),
        ("dependency_root", HHSHash216),
        ("projection_root", HHSHash216),
        ("learning_root", HHSHash216),
        ("continuation_root", HHSHash216),
        ("parent_receipt", HHSHash72),
        ("receipt", HHSHash72),
        ("generation", c_uint64),
    ]


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _library_path() -> pathlib.Path:
    root = _repo_root()
    build_dir = root / "hhs_runtime" / "builds"
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_pass205_continuation.dll"
    elif system == "darwin":
        name = "libhhs_pass205_continuation.dylib"
    else:
        name = "libhhs_pass205_continuation.so"
    return build_dir / name


def build_native_library(*, force: bool = False) -> pathlib.Path:
    """Build the additive Pass 205 ABI without changing the inherited C ABI target."""
    root = _repo_root()
    output = _library_path()
    source = root / "hhs_runtime" / "c" / "hhs_pass205_continuation.c"
    hash_source = root / "hhs_runtime" / "src" / "hhs_hash216.c"
    if output.exists() and not force:
        newest_input = max(source.stat().st_mtime, hash_source.stat().st_mtime)
        if output.stat().st_mtime >= newest_input:
            return output
    output.parent.mkdir(parents=True, exist_ok=True)
    cc = os.environ.get("CC", "cc")
    system = platform.system().lower()
    command = [
        cc,
        "-std=c11",
        "-O3",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-pedantic",
        f"-I{root / 'hhs_runtime' / 'include'}",
        f"-I{root / 'hhs_runtime' / 'c'}",
    ]
    if system == "windows":
        command.extend(["-shared"])
    elif system == "darwin":
        command.extend(["-fPIC", "-dynamiclib"])
    else:
        command.extend(["-fPIC", "-shared"])
    command.extend([str(source), str(hash_source), "-o", str(output)])
    completed = subprocess.run(
        command,
        cwd=str(root),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Pass 205 native ABI build failed:\n"
            + " ".join(command)
            + "\n"
            + completed.stdout
            + completed.stderr
        )
    return output


def _load_library() -> ctypes.CDLL:
    output = _library_path()
    disable = os.environ.get("HHS_DISABLE_PASS205_C_AUTOBUILD", "").lower() in {
        "1", "true", "yes", "on"
    }
    if not output.exists() and disable:
        raise FileNotFoundError(f"Pass 205 native library missing: {output}")
    if not output.exists():
        build_native_library()
    return ctypes.CDLL(str(output))


_LIB = _load_library()

_LIB.hhs_pass205_q_address.argtypes = [c_uint16, c_uint8, POINTER(c_uint8)]
_LIB.hhs_pass205_q_address.restype = c_uint32
_LIB.hhs_pass205_q_decode.argtypes = [c_uint32, POINTER(c_uint16), POINTER(c_uint8)]
_LIB.hhs_pass205_q_decode.restype = c_uint8
_LIB.hhs_pass205_state_clear.argtypes = [POINTER(HHSPass205State)]
_LIB.hhs_pass205_state_clear.restype = None
_LIB.hhs_pass205_validate_delta.argtypes = [POINTER(HHSPass205Delta)]
_LIB.hhs_pass205_validate_delta.restype = c_uint8
_LIB.hhs_pass205_apply_delta.argtypes = [
    POINTER(HHSPass205State), POINTER(HHSPass205Delta), POINTER(HHSPass205State)
]
_LIB.hhs_pass205_apply_delta.restype = c_uint8
_LIB.hhs_pass205_build_required_frontier.argtypes = [
    POINTER(HHSPass205Delta), POINTER(HHSPass205Frontier)
]
_LIB.hhs_pass205_build_required_frontier.restype = c_uint8
_LIB.hhs_pass205_validate_frontier.argtypes = [
    POINTER(HHSPass205Delta), POINTER(HHSPass205Frontier)
]
_LIB.hhs_pass205_validate_frontier.restype = c_uint8
_LIB.hhs_pass205_project_full.argtypes = [
    POINTER(HHSPass205State), POINTER(HHSPass205Projection)
]
_LIB.hhs_pass205_project_full.restype = None
_LIB.hhs_pass205_project_sparse.argtypes = [
    POINTER(HHSPass205State),
    POINTER(HHSPass205Projection),
    POINTER(HHSPass205Frontier),
    POINTER(HHSPass205Projection),
]
_LIB.hhs_pass205_project_sparse.restype = c_uint8
_LIB.hhs_pass205_projection_equal.argtypes = [
    POINTER(HHSPass205Projection), POINTER(HHSPass205Projection)
]
_LIB.hhs_pass205_projection_equal.restype = c_uint8
_LIB.hhs_pass205_state_hash216.argtypes = [POINTER(HHSPass205State), POINTER(HHSHash216)]
_LIB.hhs_pass205_state_hash216.restype = None
_LIB.hhs_pass205_delta_hash216.argtypes = [POINTER(HHSPass205Delta), POINTER(HHSHash216)]
_LIB.hhs_pass205_delta_hash216.restype = None
_LIB.hhs_pass205_hydration_hash216.argtypes = [POINTER(HHSPass205Delta), POINTER(HHSHash216)]
_LIB.hhs_pass205_hydration_hash216.restype = None
_LIB.hhs_pass205_frontier_hash216.argtypes = [POINTER(HHSPass205Frontier), POINTER(HHSHash216)]
_LIB.hhs_pass205_frontier_hash216.restype = None
_LIB.hhs_pass205_projection_hash216.argtypes = [
    POINTER(HHSPass205Projection), POINTER(HHSHash216)
]
_LIB.hhs_pass205_projection_hash216.restype = None
_LIB.hhs_pass205_hash216_bytes.argtypes = [POINTER(c_uint8), c_size_t, POINTER(HHSHash216)]
_LIB.hhs_pass205_hash216_bytes.restype = None
_LIB.hhs_pass205_build_token.argtypes = [
    POINTER(HHSHash216), POINTER(HHSHash216), POINTER(HHSHash216),
    POINTER(HHSHash216), POINTER(HHSHash216), POINTER(HHSHash216),
    POINTER(HHSHash216), POINTER(HHSHash72), c_uint64, POINTER(HHSPass205Token),
]
_LIB.hhs_pass205_build_token.restype = c_uint8


def _decode_hash(value: object) -> str:
    raw = bytes(getattr(value, "value"))
    return raw.decode("ascii").rstrip("\x00")


def _hash216(value: str) -> HHSHash216:
    encoded = value.encode("ascii")
    if len(encoded) != HASH216_LEN:
        raise ValueError(f"Hash216 must contain exactly {HASH216_LEN} ASCII symbols")
    result = HHSHash216()
    result.value = encoded
    return result


def _hash72(value: str) -> HHSHash72:
    encoded = value.encode("ascii")
    if len(encoded) != HASH72_LEN:
        raise ValueError(f"Hash72 must contain exactly {HASH72_LEN} ASCII symbols")
    result = HHSHash72()
    result.value = encoded
    return result


def state_from_words(words: Sequence[int]) -> HHSPass205State:
    if len(words) != CELL_COUNT:
        raise ValueError(f"state requires exactly {CELL_COUNT} uint64 words")
    state = HHSPass205State()
    for index, value in enumerate(words):
        integer = int(value)
        if integer < 0 or integer > UINT64_MASK:
            raise ValueError(f"state word {index} is outside uint64")
        state.cells[index] = integer
    return state


def state_to_words(state: HHSPass205State) -> list[int]:
    return [int(value) for value in state.cells]


def delta_from_events(events: Sequence[Mapping[str, int]]) -> HHSPass205Delta:
    if len(events) > CELL_COUNT:
        raise ValueError(f"delta supports at most {CELL_COUNT} cell events")
    delta = HHSPass205Delta()
    delta.count = len(events)
    for index, event in enumerate(events):
        cell = int(event["cell"])
        control_g = int(event["control_g"])
        xor_mask = int(event["xor_mask"])
        if cell < 0 or cell >= CELL_COUNT:
            raise ValueError(f"invalid cell index: {cell}")
        if control_g < 0 or control_g >= CONTROL_COUNT:
            raise ValueError(f"invalid control_g: {control_g}")
        if xor_mask <= 0 or xor_mask > UINT64_MASK:
            raise ValueError(f"invalid xor_mask: {xor_mask}")
        delta.cell_index[index] = cell
        delta.control_g[index] = control_g
        delta.xor_mask[index] = xor_mask
    if not _LIB.hhs_pass205_validate_delta(ctypes.byref(delta)):
        raise ValueError("delta rejected by native Pass 205 ABI")
    return delta


def projection_to_lists(projection: HHSPass205Projection) -> list[list[int]]:
    return [[int(value) for value in row] for row in projection.channel]


def projection_from_lists(channels: Sequence[Sequence[int]]) -> HHSPass205Projection:
    if len(channels) != PROJECTION_CHANNELS:
        raise ValueError(f"projection requires {PROJECTION_CHANNELS} channels")
    projection = HHSPass205Projection()
    for channel, row in enumerate(channels):
        if len(row) != CELL_COUNT:
            raise ValueError(f"projection channel {channel} requires {CELL_COUNT} cells")
        for cell, value in enumerate(row):
            integer = int(value)
            if integer < 0 or integer > 0xFFFFFFFF:
                raise ValueError("projection value outside uint32")
            projection.channel[channel][cell] = integer
    return projection


class Pass205NativeBridge:
    """Exact fixed-width native execution surface for Pass 205."""

    @staticmethod
    def q_address(s: int, g: int) -> int:
        ok = c_uint8(0)
        q = int(_LIB.hhs_pass205_q_address(int(s), int(g), ctypes.byref(ok)))
        if not ok.value:
            raise ValueError(f"invalid hydration coordinate s={s}, g={g}")
        return q

    @staticmethod
    def q_decode(q: int) -> tuple[int, int]:
        s = c_uint16(0)
        g = c_uint8(0)
        if not _LIB.hhs_pass205_q_decode(int(q), ctypes.byref(s), ctypes.byref(g)):
            raise ValueError(f"invalid hydration address q={q}")
        return int(s.value), int(g.value)

    @staticmethod
    def apply_delta(
        parent_words: Sequence[int], events: Sequence[Mapping[str, int]]
    ) -> tuple[list[int], list[int], HHSPass205Delta, HHSPass205Frontier]:
        parent = state_from_words(parent_words)
        delta = delta_from_events(events)
        child = HHSPass205State()
        frontier = HHSPass205Frontier()
        if not _LIB.hhs_pass205_apply_delta(
            ctypes.byref(parent), ctypes.byref(delta), ctypes.byref(child)
        ):
            raise ValueError("native Pass 205 delta application failed")
        if not _LIB.hhs_pass205_build_required_frontier(
            ctypes.byref(delta), ctypes.byref(frontier)
        ):
            raise ValueError("native Pass 205 frontier construction failed")
        return state_to_words(child), [int(value) for value in frontier.cell], delta, frontier

    @staticmethod
    def validate_frontier(
        events: Sequence[Mapping[str, int]], frontier_cells: Iterable[int]
    ) -> bool:
        delta = delta_from_events(events)
        frontier = HHSPass205Frontier()
        for cell in frontier_cells:
            index = int(cell)
            if index < 0 or index >= CELL_COUNT:
                return False
            frontier.cell[index] = 1
        return bool(_LIB.hhs_pass205_validate_frontier(ctypes.byref(delta), ctypes.byref(frontier)))

    @staticmethod
    def project_full(words: Sequence[int]) -> list[list[int]]:
        state = state_from_words(words)
        projection = HHSPass205Projection()
        _LIB.hhs_pass205_project_full(ctypes.byref(state), ctypes.byref(projection))
        return projection_to_lists(projection)

    @staticmethod
    def project_sparse(
        child_words: Sequence[int],
        parent_projection: Sequence[Sequence[int]],
        frontier_cells: Iterable[int],
    ) -> list[list[int]]:
        state = state_from_words(child_words)
        parent = projection_from_lists(parent_projection)
        frontier = HHSPass205Frontier()
        for cell in frontier_cells:
            index = int(cell)
            if index < 0 or index >= CELL_COUNT:
                raise ValueError(f"invalid frontier cell: {index}")
            frontier.cell[index] = 1
        child = HHSPass205Projection()
        if not _LIB.hhs_pass205_project_sparse(
            ctypes.byref(state), ctypes.byref(parent), ctypes.byref(frontier), ctypes.byref(child)
        ):
            raise ValueError("native Pass 205 sparse projection failed")
        return projection_to_lists(child)

    @staticmethod
    def state_root(words: Sequence[int]) -> str:
        state = state_from_words(words)
        result = HHSHash216()
        _LIB.hhs_pass205_state_hash216(ctypes.byref(state), ctypes.byref(result))
        return _decode_hash(result)

    @staticmethod
    def delta_root(events: Sequence[Mapping[str, int]]) -> str:
        delta = delta_from_events(events)
        result = HHSHash216()
        _LIB.hhs_pass205_delta_hash216(ctypes.byref(delta), ctypes.byref(result))
        return _decode_hash(result)

    @staticmethod
    def hydration_root(events: Sequence[Mapping[str, int]]) -> str:
        delta = delta_from_events(events)
        result = HHSHash216()
        _LIB.hhs_pass205_hydration_hash216(ctypes.byref(delta), ctypes.byref(result))
        return _decode_hash(result)

    @staticmethod
    def frontier_root(frontier_cells: Iterable[int]) -> str:
        frontier = HHSPass205Frontier()
        for cell in frontier_cells:
            index = int(cell)
            if index < 0 or index >= CELL_COUNT:
                raise ValueError(f"invalid frontier cell: {index}")
            frontier.cell[index] = 1
        result = HHSHash216()
        _LIB.hhs_pass205_frontier_hash216(ctypes.byref(frontier), ctypes.byref(result))
        return _decode_hash(result)

    @staticmethod
    def projection_root(channels: Sequence[Sequence[int]]) -> str:
        projection = projection_from_lists(channels)
        result = HHSHash216()
        _LIB.hhs_pass205_projection_hash216(ctypes.byref(projection), ctypes.byref(result))
        return _decode_hash(result)

    @staticmethod
    def hash216_bytes(payload: bytes) -> str:
        result = HHSHash216()
        if payload:
            buffer = (c_uint8 * len(payload)).from_buffer_copy(payload)
            _LIB.hhs_pass205_hash216_bytes(buffer, len(payload), ctypes.byref(result))
        else:
            _LIB.hhs_pass205_hash216_bytes(None, 0, ctypes.byref(result))
        return _decode_hash(result)

    @staticmethod
    def build_token(
        *,
        parent_root: str,
        content_root: str,
        delta_root: str,
        hydration_root: str,
        dependency_root: str,
        projection_root: str,
        learning_root: str,
        parent_receipt: str,
        generation: int,
    ) -> dict[str, object]:
        token = HHSPass205Token()
        roots = [
            _hash216(parent_root), _hash216(content_root), _hash216(delta_root),
            _hash216(hydration_root), _hash216(dependency_root),
            _hash216(projection_root), _hash216(learning_root),
        ]
        receipt = _hash72(parent_receipt)
        ok = _LIB.hhs_pass205_build_token(
            *(ctypes.byref(root) for root in roots),
            ctypes.byref(receipt),
            int(generation),
            ctypes.byref(token),
        )
        if not ok:
            raise RuntimeError("native Pass 205 token construction failed")
        return {
            "parent_root216": _decode_hash(token.parent_root),
            "content_root216": _decode_hash(token.content_root),
            "delta_root216": _decode_hash(token.delta_root),
            "hydration_root216": _decode_hash(token.hydration_root),
            "dependency_root216": _decode_hash(token.dependency_root),
            "projection_root216": _decode_hash(token.projection_root),
            "learning_root216": _decode_hash(token.learning_root),
            "continuation_root216": _decode_hash(token.continuation_root),
            "parent_receipt_hash72": _decode_hash(token.parent_receipt),
            "receipt_hash72": _decode_hash(token.receipt),
            "generation": int(token.generation),
        }

    @staticmethod
    def abi_status() -> dict[str, object]:
        return {
            "schema": "HHS_PASS_205_NATIVE_ABI_STATUS_V1",
            "state_bits": STATE_BITS,
            "cell_count": CELL_COUNT,
            "bits_per_cell": BITS_PER_CELL,
            "control_count": CONTROL_COUNT,
            "q_count": Q_COUNT,
            "projection_channels": PROJECTION_CHANNELS,
            "state_bytes": ctypes.sizeof(HHSPass205State),
            "delta_bytes": ctypes.sizeof(HHSPass205Delta),
            "frontier_bytes": ctypes.sizeof(HHSPass205Frontier),
            "projection_bytes": ctypes.sizeof(HHSPass205Projection),
            "token_bytes": ctypes.sizeof(HHSPass205Token),
            "canonical_float_fields": 0,
            "native_library": str(_library_path()),
        }

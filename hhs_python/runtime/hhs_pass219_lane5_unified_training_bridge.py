"""ctypes adapter for the Pass 219 Lane 5 unified VM5184/Hash216 training API 1.74.

This module is a client of the native C++ training class.  It does not own
training authority or canonical VM81/Hash72/Hash216 mutation.
"""
from __future__ import annotations

import ctypes
import os
import pathlib
import platform
import subprocess
from ctypes import (
    POINTER,
    Structure,
    c_char,
    c_int8,
    c_size_t,
    c_uint8,
    c_uint32,
    c_uint64,
)
from typing import Mapping

VERSION = 0x0001004A
METHOD_COUNT = 19
METHOD_ID_BYTES = 48
HASH216_BYTES = 217
HASH72_BYTES = 73
VM5184_BYTES = 648
FEEDBACK_NONE = 255
PROFILE_INTEGER_SYMMETRIC_V1 = 1
STATUS_OK = 0


class HHSExactPass219Lane5TrainingMethodV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("mode", c_uint32),
        ("temporal", c_uint32),
        ("primary_target", c_uint32),
        ("target_mask", c_uint32),
        ("method_id", c_char * METHOD_ID_BYTES),
        ("requires_oracle", c_uint8),
        ("requires_negative_controls", c_uint8),
        ("requires_replay", c_uint8),
        ("preserves_ingress_egress", c_uint8),
        ("routes_through_vm5184", c_uint8),
        ("emits_candidate_hash216", c_uint8),
        ("candidate_only", c_uint8),
        ("natural_language_native", c_uint8),
        ("ethical_text_supervisor", c_uint8),
        ("reserved0", c_uint8 * 7),
    ]


class HHSExactPass219Lane5TrainingSpecimenV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("mode", c_uint32),
        ("temporal", c_uint32),
        ("target", c_uint32),
        ("reserved0", c_uint32),
        ("source_identity216", c_char * HASH216_BYTES),
        ("oracle_identity216", c_char * HASH216_BYTES),
        ("ethical_text_supervisor_identity216", c_char * HASH216_BYTES),
        ("adapter_signature64", c_uint64),
        ("executor_signature64", c_uint64),
        ("validator_signature64", c_uint64),
        ("negative_control_signature64", c_uint64),
        ("replay_signature64", c_uint64),
        ("ethical_text_supervisor_signature64", c_uint64),
        ("oracle_verified", c_uint8),
        ("negative_controls_verified", c_uint8),
        ("replay_verified", c_uint8),
        ("ingress_egress_preserved", c_uint8),
        ("candidate_only_acknowledged", c_uint8),
        ("natural_language_training", c_uint8),
        ("ethical_text_supervision_verified", c_uint8),
        ("reserved1", c_uint8),
    ]


class HHSExactPass219Lane5TrainingReceiptV1(Structure):
    _fields_ = [
        ("struct_size", c_uint32),
        ("version", c_uint32),
        ("namespace_id", c_uint32),
        ("mode", c_uint32),
        ("temporal", c_uint32),
        ("target", c_uint32),
        ("method_index", c_uint32),
        ("selected_lane", c_uint32),
        ("graph_signature64", c_uint64),
        ("tensor_signature64", c_uint64),
        ("decision_signature64", c_uint64),
        ("source_identity216", c_char * HASH216_BYTES),
        ("oracle_identity216", c_char * HASH216_BYTES),
        ("ethical_text_supervisor_identity216", c_char * HASH216_BYTES),
        ("training_candidate_hash216", c_char * HASH216_BYTES),
        ("accepted", c_uint8),
        ("registry_verified", c_uint8),
        ("specimen_identity_verified", c_uint8),
        ("oracle_verified", c_uint8),
        ("negative_controls_verified", c_uint8),
        ("replay_verified", c_uint8),
        ("ingress_egress_preserved", c_uint8),
        ("natural_language_training", c_uint8),
        ("ethical_text_supervision_required", c_uint8),
        ("ethical_text_supervision_verified", c_uint8),
        ("vm5184_routed", c_uint8),
        ("hash216_candidate_derived", c_uint8),
        ("candidate_only", c_uint8),
        ("canonical_vm81_mutation_authority", c_uint8),
        ("canonical_hash72_authority", c_uint8),
        ("canonical_hash216_authority", c_uint8),
        ("canonical_persistence_authority", c_uint8),
        ("floating_point_canonical_authority", c_uint8),
        ("reserved0", c_uint8 * 6),
    ]


def _repo_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _runtime_path() -> pathlib.Path:
    system = platform.system().lower()
    if system == "windows":
        name = "hhs_runtime.dll"
    elif system == "darwin":
        name = "libhhs_runtime.dylib"
    else:
        name = "libhhs_runtime.so"
    return _repo_root() / "hhs_runtime" / "builds" / name


def _load_runtime() -> ctypes.CDLL:
    root = _repo_root()
    path = _runtime_path()
    disabled = os.environ.get("HHS_DISABLE_C_AUTOBUILD", "").lower() in {
        "1", "true", "yes", "on"
    }
    if not path.exists() and not disabled:
        subprocess.run(
            ["make", "-f", "GNUmakefile", "c-abi"],
            cwd=str(root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    if not path.exists():
        raise FileNotFoundError(f"HHS runtime shared library not found: {path}")
    return ctypes.CDLL(str(path))


def _text(value: bytes | bytearray | memoryview | str, size: int, name: str) -> bytes:
    raw = value.encode("ascii") if isinstance(value, str) else bytes(value)
    if len(raw) >= size:
        raise ValueError(f"{name} must contain at most {size - 1} bytes")
    if b"\x00" in raw:
        raise ValueError(f"{name} may not contain NUL")
    return raw


def _decode(value: bytes | ctypes.Array[c_char]) -> str:
    return bytes(value).split(b"\x00", 1)[0].decode("ascii")


class Pass219Lane5UnifiedTrainingBridge:
    def __init__(self) -> None:
        self.lib = _load_runtime()
        self.lib.hhs_exact_pass219_lane5_training_c_abi_version.argtypes = []
        self.lib.hhs_exact_pass219_lane5_training_c_abi_version.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_training_method_count.argtypes = []
        self.lib.hhs_exact_pass219_lane5_training_method_count.restype = c_uint32
        self.lib.hhs_exact_pass219_lane5_training_method.argtypes = [
            c_uint32,
            POINTER(HHSExactPass219Lane5TrainingMethodV1),
        ]
        self.lib.hhs_exact_pass219_lane5_training_method.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_training_genesis_identity216.argtypes = [
            POINTER(c_char)
        ]
        self.lib.hhs_exact_pass219_lane5_training_genesis_identity216.restype = ctypes.c_int
        self.lib.hhs_exact_pass219_lane5_training_evaluate_raw.argtypes = [
            POINTER(HHSExactPass219Lane5TrainingSpecimenV1),
            c_uint32,
            POINTER(c_uint8),
            c_size_t,
            POINTER(c_uint8),
            c_size_t,
            POINTER(c_char),
            POINTER(c_char),
            POINTER(c_char),
            c_uint8,
            c_uint8,
            c_int8,
            POINTER(HHSExactPass219Lane5TrainingReceiptV1),
        ]
        self.lib.hhs_exact_pass219_lane5_training_evaluate_raw.restype = ctypes.c_int

    def version(self) -> int:
        return int(self.lib.hhs_exact_pass219_lane5_training_c_abi_version())

    def methods(self) -> list[dict[str, object]]:
        count = int(self.lib.hhs_exact_pass219_lane5_training_method_count())
        result: list[dict[str, object]] = []
        for index in range(count):
            value = HHSExactPass219Lane5TrainingMethodV1()
            status = self.lib.hhs_exact_pass219_lane5_training_method(
                index, ctypes.byref(value)
            )
            if status != STATUS_OK:
                raise RuntimeError(f"training method lookup {index} failed: {status}")
            result.append(
                {
                    "index": index,
                    "mode": int(value.mode),
                    "temporal": int(value.temporal),
                    "primary_target": int(value.primary_target),
                    "target_mask": int(value.target_mask),
                    "method_id": _decode(value.method_id),
                    "requires_oracle": bool(value.requires_oracle),
                    "requires_negative_controls": bool(value.requires_negative_controls),
                    "requires_replay": bool(value.requires_replay),
                    "preserves_ingress_egress": bool(value.preserves_ingress_egress),
                    "routes_through_vm5184": bool(value.routes_through_vm5184),
                    "emits_candidate_hash216": bool(value.emits_candidate_hash216),
                    "candidate_only": bool(value.candidate_only),
                    "natural_language_native": bool(value.natural_language_native),
                    "ethical_text_supervisor": bool(value.ethical_text_supervisor),
                }
            )
        return result

    def genesis_identity216(self) -> str:
        output = (c_char * HASH216_BYTES)()
        status = self.lib.hhs_exact_pass219_lane5_training_genesis_identity216(output)
        if status != STATUS_OK:
            raise RuntimeError(f"training genesis identity failed: {status}")
        return _decode(output)

    def evaluate_raw(
        self,
        specimen: Mapping[str, object],
        raw_frame: bytes,
        *,
        delta_be: bytes = b"\x01",
        uqcel_profile: int = PROFILE_INTEGER_SYMMETRIC_V1,
        previous_hash72: str | None = None,
        change_hash72: str | None = None,
        receipt_hash72: str | None = None,
        feedback_lane: int = FEEDBACK_NONE,
        feedback_trinary: int = 0,
    ) -> dict[str, object]:
        if len(raw_frame) != VM5184_BYTES:
            raise ValueError("raw VM5184 frame must be exactly 648 bytes")
        if not delta_be:
            raise ValueError("delta_be must be nonempty")

        native = HHSExactPass219Lane5TrainingSpecimenV1()
        native.struct_size = ctypes.sizeof(native)
        native.version = VERSION
        for key in ("mode", "temporal", "target"):
            setattr(native, key, int(specimen[key]))
        native.source_identity216 = _text(
            specimen["source_identity216"], HASH216_BYTES, "source_identity216"
        )
        native.oracle_identity216 = _text(
            specimen["oracle_identity216"], HASH216_BYTES, "oracle_identity216"
        )
        supervisor_identity = specimen.get("ethical_text_supervisor_identity216", "")
        native.ethical_text_supervisor_identity216 = _text(
            supervisor_identity, HASH216_BYTES, "ethical_text_supervisor_identity216"
        )
        for key in (
            "adapter_signature64",
            "executor_signature64",
            "validator_signature64",
            "negative_control_signature64",
            "replay_signature64",
            "ethical_text_supervisor_signature64",
        ):
            setattr(native, key, int(specimen.get(key, 0)))
        for key in (
            "oracle_verified",
            "negative_controls_verified",
            "replay_verified",
            "ingress_egress_preserved",
            "candidate_only_acknowledged",
            "natural_language_training",
            "ethical_text_supervision_verified",
        ):
            setattr(native, key, int(bool(specimen.get(key, False))))

        delta = (c_uint8 * len(delta_be)).from_buffer_copy(delta_be)
        frame = (c_uint8 * len(raw_frame)).from_buffer_copy(raw_frame)

        explicit = any(
            value is not None
            for value in (previous_hash72, change_hash72, receipt_hash72)
        )
        if explicit and not all(
            value is not None
            for value in (previous_hash72, change_hash72, receipt_hash72)
        ):
            raise ValueError(
                "previous_hash72, change_hash72 and receipt_hash72 must be supplied together"
            )

        previous_buf = change_buf = receipt_buf = None
        use_genesis = 0 if explicit else 1
        if explicit:
            previous_buf = ctypes.create_string_buffer(
                _text(previous_hash72 or "", HASH72_BYTES, "previous_hash72"),
                HASH72_BYTES,
            )
            change_buf = ctypes.create_string_buffer(
                _text(change_hash72 or "", HASH72_BYTES, "change_hash72"),
                HASH72_BYTES,
            )
            receipt_buf = ctypes.create_string_buffer(
                _text(receipt_hash72 or "", HASH72_BYTES, "receipt_hash72"),
                HASH72_BYTES,
            )

        output = HHSExactPass219Lane5TrainingReceiptV1()
        status = self.lib.hhs_exact_pass219_lane5_training_evaluate_raw(
            ctypes.byref(native),
            int(uqcel_profile),
            delta,
            len(delta_be),
            frame,
            len(raw_frame),
            previous_buf,
            change_buf,
            receipt_buf,
            use_genesis,
            int(feedback_lane),
            int(feedback_trinary),
            ctypes.byref(output),
        )
        if status != STATUS_OK:
            raise ValueError(f"Lane 5 unified training rejected: status={status}")

        return {
            "version": int(output.version),
            "namespace_id": int(output.namespace_id),
            "mode": int(output.mode),
            "temporal": int(output.temporal),
            "target": int(output.target),
            "method_index": int(output.method_index),
            "selected_lane": int(output.selected_lane),
            "graph_signature64": int(output.graph_signature64),
            "tensor_signature64": int(output.tensor_signature64),
            "decision_signature64": int(output.decision_signature64),
            "source_identity216": _decode(output.source_identity216),
            "oracle_identity216": _decode(output.oracle_identity216),
            "ethical_text_supervisor_identity216": _decode(
                output.ethical_text_supervisor_identity216
            ),
            "training_candidate_hash216": _decode(
                output.training_candidate_hash216
            ),
            "accepted": bool(output.accepted),
            "registry_verified": bool(output.registry_verified),
            "specimen_identity_verified": bool(output.specimen_identity_verified),
            "oracle_verified": bool(output.oracle_verified),
            "negative_controls_verified": bool(output.negative_controls_verified),
            "replay_verified": bool(output.replay_verified),
            "ingress_egress_preserved": bool(output.ingress_egress_preserved),
            "natural_language_training": bool(output.natural_language_training),
            "ethical_text_supervision_required": bool(
                output.ethical_text_supervision_required
            ),
            "ethical_text_supervision_verified": bool(
                output.ethical_text_supervision_verified
            ),
            "vm5184_routed": bool(output.vm5184_routed),
            "hash216_candidate_derived": bool(output.hash216_candidate_derived),
            "candidate_only": bool(output.candidate_only),
            "canonical_vm81_mutation_authority": bool(
                output.canonical_vm81_mutation_authority
            ),
            "canonical_hash72_authority": bool(output.canonical_hash72_authority),
            "canonical_hash216_authority": bool(output.canonical_hash216_authority),
            "canonical_persistence_authority": bool(
                output.canonical_persistence_authority
            ),
            "floating_point_canonical_authority": bool(
                output.floating_point_canonical_authority
            ),
        }


__all__ = [
    "METHOD_COUNT",
    "VERSION",
    "Pass219Lane5UnifiedTrainingBridge",
    "HHSExactPass219Lane5TrainingMethodV1",
    "HHSExactPass219Lane5TrainingReceiptV1",
    "HHSExactPass219Lane5TrainingSpecimenV1",
]

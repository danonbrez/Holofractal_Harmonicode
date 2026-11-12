"""Pass 220 native C11 packet egress for an admitted ordered decay observation.

Reuses the canonical Pass 179 C ABI and the Pass 163 API-owned VMRC instance;
never compiles native code on a web request, instantiates another VM81, or
permits a browser-supplied receipt/identity. Deployment must install the
existing C11 shared library in the trusted repository build path first.
"""
from __future__ import annotations

from base64 import b64encode
import ctypes as C
from pathlib import Path
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_gfx4_decay_matrix_observation_v1 import (
    admit_decay_matrix_observation,
)

SCHEMA = "HHS_PASS_220_NATIVE_OBSERVATION_EGRESS_V1"
C11_LIBRARY = (
    Path(__file__).resolve().parents[1]
    / "native_projects/hhs_pass220_gfx1_native_render_commands"
    / "build/libhhs_pass179_render_command_v1.so"
)
MAX_MATRIX_BYTES = 4 * 1024 * 1024
MAX_COMMANDS = 4096


class NativeObservationExportError(ValueError):
    pass


class Init(C.Structure):
    _fields_ = [
        ("struct_size", C.c_uint32),
        ("flags", C.c_uint32),
        ("projection_profile", C.c_uint32),
        ("target_width", C.c_uint32),
        ("target_height", C.c_uint32),
        ("target_format", C.c_uint32),
        ("frame_index", C.c_uint64),
        ("exact_time_num", C.c_int64),
        ("exact_time_den", C.c_uint64),
        ("scene_snapshot_hash216", C.c_uint8 * 216),
        ("frame_hash216", C.c_uint8 * 216),
        ("prior_frame_hash216", C.c_uint8 * 216),
        ("resource_manifest_hash216", C.c_uint8 * 216),
        ("camera_hash72", C.c_uint8 * 72),
        ("software_digest_sha256", C.c_uint8 * 32),
        ("backend_evidence_sha256", C.c_uint8 * 32),
    ]


class Command(C.Structure):
    _fields_ = [
        ("opcode", C.c_uint16),
        ("flags", C.c_uint16),
        ("byte_length", C.c_uint32),
        ("resource_id", C.c_uint64),
        ("arg0", C.c_uint64),
        ("arg1", C.c_uint64),
    ]


def _exact_int(value: Any, name: str, *, upper: int = (1 << 64) - 1) -> int:
    if type(value) is not int or value < 0 or value > upper:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_EXACT_" + name)
    return value


def _native_packet(identity: Mapping[str, Any], *, frame_index: int, time_num: int,
                   time_den: int, width: int, height: int,
                   commands: list[Mapping[str, Any]]) -> bytes:
    if not C11_LIBRARY.is_file():
        raise NativeObservationExportError("P220_NATIVE_EGRESS_C11_LIBRARY_UNAVAILABLE")
    from hhs_runtime.hhs_pass220_gfx4_vm81_graphics_packet_identity_v1 import packet_identity_bytes
    lanes = packet_identity_bytes(identity)
    lib = C.CDLL(str(C11_LIBRARY))
    ptr = C.POINTER(C.c_uint8)
    lib.hhs179_render_packet_required_bytes.argtypes = [C.c_uint32]
    lib.hhs179_render_packet_required_bytes.restype = C.c_size_t
    lib.hhs179_render_packet_init.argtypes = [ptr, C.c_size_t, C.POINTER(Init), C.c_uint32]
    lib.hhs179_render_packet_init.restype = C.c_int
    lib.hhs179_render_packet_write_command.argtypes = [ptr, C.c_size_t, C.c_uint32, C.POINTER(Command)]
    lib.hhs179_render_packet_write_command.restype = C.c_int
    lib.hhs179_render_packet_seal.argtypes = [ptr, C.c_size_t]
    lib.hhs179_render_packet_seal.restype = C.c_int
    lib.hhs179_render_packet_validate.argtypes = [ptr, C.c_size_t]
    lib.hhs179_render_packet_validate.restype = C.c_int
    if len(commands) < 2 or len(commands) > MAX_COMMANDS:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_COMMAND_COUNT")
    if commands[0].get("opcode") != 1 or commands[-1].get("opcode") != 24:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_COMMAND_SEQUENCE")
    init = Init()
    init.struct_size = C.sizeof(Init)
    init.flags = 2  # SEALED is set by the C11 seal operation. Projection only.
    init.projection_profile = 1
    init.target_width = width
    init.target_height = height
    init.target_format = 1
    init.frame_index = frame_index
    init.exact_time_num = time_num
    init.exact_time_den = time_den
    for name in ("scene", "frame", "prior", "resources", "camera"):
        field = {"scene":"scene_snapshot_hash216","frame":"frame_hash216",
                 "prior":"prior_frame_hash216","resources":"resource_manifest_hash216",
                 "camera":"camera_hash72"}[name]
        setattr(init, field, type(getattr(init, field))(*lanes[name]))
    size = lib.hhs179_render_packet_required_bytes(len(commands))
    if size <= 1088 or size > 1088 + MAX_COMMANDS * 32:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_PACKET_BOUNDS")
    buffer = (C.c_uint8 * size)()
    if lib.hhs179_render_packet_init(buffer, size, C.byref(init), len(commands)) != 0:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_C11_INIT_REJECTED")
    for index, raw in enumerate(commands):
        opcode = _exact_int(raw.get("opcode"), "OPCODE", upper=24)
        flags = _exact_int(raw.get("flags", 0), "FLAGS", upper=65535)
        rid = _exact_int(raw.get("resource_id", 0), "RESOURCE")
        arg0 = _exact_int(raw.get("arg0", 0), "ARG0")
        arg1 = _exact_int(raw.get("arg1", 0), "ARG1")
        command = Command(opcode, flags, 32, rid, arg0, arg1)
        if lib.hhs179_render_packet_write_command(buffer, size, index, C.byref(command)) != 0:
            raise NativeObservationExportError("P220_NATIVE_EGRESS_C11_COMMAND_REJECTED")
    if lib.hhs179_render_packet_seal(buffer, size) != 0 or lib.hhs179_render_packet_validate(buffer, size) != 0:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_C11_SEAL_REJECTED")
    return bytes(buffer)


def native_observation_export(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Guarded registry service; uses the existing Pass 163 API VMRC singleton."""
    if not isinstance(payload, Mapping):
        raise NativeObservationExportError("P220_NATIVE_EGRESS_PAYLOAD_REQUIRED")
    forbidden = {"identity", "vm81_admission", "nativeAdmission", "packet", "verification",
                 "receipt_hash72", "zero_bypass_interposition_token"}
    # Dispatch strips its interposition token before passing the payload.
    if any(name in payload for name in forbidden):
        raise NativeObservationExportError("P220_NATIVE_EGRESS_CLIENT_AUTHORITY_CLAIM")
    encoded = payload.get("matrix_hex")
    if not isinstance(encoded, str) or len(encoded) == 0 or len(encoded) % 2 or len(encoded) > MAX_MATRIX_BYTES * 2:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_MATRIX_ENCODING")
    try:
        matrix = bytes.fromhex(encoded)
    except ValueError as exc:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_MATRIX_ENCODING") from exc
    if matrix.hex() != encoded:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_MATRIX_NONCANONICAL")
    size = _exact_int(payload.get("matrix_byte_length"), "MATRIX_LENGTH", upper=MAX_MATRIX_BYTES)
    if len(matrix) != size:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_MATRIX_SIZE_MISMATCH")
    version = _exact_int(payload.get("matrix_version"), "VERSION")
    index = _exact_int(payload.get("frame_index"), "FRAME_INDEX")
    num = payload.get("exact_time_num")
    if type(num) is not int or num < -(1 << 63) or num > (1 << 63) - 1:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_TIME_NUM")
    den = _exact_int(payload.get("exact_time_den"), "TIME_DEN")
    if den == 0:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_ZERO_DEN")
    width = _exact_int(payload.get("target_width"), "WIDTH", upper=16384)
    height = _exact_int(payload.get("target_height"), "HEIGHT", upper=16384)
    if width == 0 or height == 0:
        raise NativeObservationExportError("P220_NATIVE_EGRESS_ZERO_TARGET")
    commands = payload.get("commands")
    if not isinstance(commands, list) or not all(isinstance(item, Mapping) for item in commands):
        raise NativeObservationExportError("P220_NATIVE_EGRESS_COMMANDS_REQUIRED")
    # Fail before canonical mutation if the runtime-native packet builder is
    # absent, rather than minting an admitted identity with no packet egress.
    if not C11_LIBRARY.is_file():
        raise NativeObservationExportError("P220_NATIVE_EGRESS_C11_LIBRARY_UNAVAILABLE")
    from hhs_backend.api.pass163_vmrc_routes import VMRC
    record = admit_decay_matrix_observation(
        vm81=VMRC,
        matrix_bytes=matrix,
        matrix_byte_length=size,
        matrix_version=version,
        scene_snapshot=payload.get("scene_snapshot"),
        frame_state=payload.get("frame_state"),
        resource_manifest=payload.get("resource_manifest"),
        camera_state=payload.get("camera_state"),
        frame_index=index,
        exact_time_num=num,
        exact_time_den=den,
        prior_frame_hash216=payload.get("prior_frame_hash216"),
    )
    raw_packet = _native_packet(
        record["identity"], frame_index=index, time_num=num, time_den=den,
        width=width, height=height, commands=commands,
    )
    return {
        "schema": SCHEMA,
        "native_receipt_verified": record["witness"]["verified_live_vm81_commit"],
        "native_decay_binding_verified": record["verification"]["verified_decay_matrix_binding"],
        "packet_identity_verified": True,
        "observation": {
            "frameHash216": record["frameHash216"],
            "decayHash216": record["decayHash216"],
            "matrixVersion": record["matrixVersion"],
            "identity": record["identity"],
            "verification": record["verification"],
            "packet_base64": b64encode(raw_packet).decode("ascii"),
        },
        "canonical_mutation_authority": False,
    }

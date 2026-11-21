"""Reversible geometry inspection of actual source-bound VM81 candidate egress.

Files are emitted by the inherited native candidate feedback test, not
manufactured as scalar witnesses. The HNAN and redundant Lo Shu views must
both reconstruct each exact VM81 output byte-for-byte. This is a codec
boundary witness, NOT a global proof or a Delta tensor scalarization.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys

from hhs_runtime.pass219.production_phase_geometry_binding import build_raw5184_phase_source
from hhs_runtime.pass219.dynamic_octonion_gyroscope import CHANNELS, PRODUCT_RELATIONS, PHASE_MODULUS
from hhs_runtime.hhs_pass220_base64_balanced_trit_v1 import (
    BALANCED_TRITS, BASE64_SEXTETS, FRAME_BITS,
    encode_frame, decode_frame,
)
from test_binary_trinary_egress_memory_lift import (
    _bits, _lift_bit, _pack, _recover_bit,
)


def inspect(path: Path) -> dict:
    frame = path.read_bytes()
    if len(frame) != 648:
        raise ValueError("NATIVE_VM81_FRAME_648_REQUIRED")
    bits = _bits(frame, "MSB0")
    if len(bits) != FRAME_BITS:
        raise AssertionError("NATIVE_BITS")
    trit_blocks = tuple(_lift_bit(bit) for bit in bits)
    recovered = tuple(_recover_bit(block) for block in trit_blocks)
    if len(trit_blocks) * 9 != 46656 or _pack(recovered, "MSB0") != frame:
        raise AssertionError("LO_SHU_EGRESS_GEOMETRY")
    carrier = encode_frame("".join(str(bit) for bit in bits))
    if len(carrier.trits) != BALANCED_TRITS or len(carrier.alphabet64) != BASE64_SEXTETS:
        raise AssertionError("HNAN_GEOMETRY")
    decoded = decode_frame(carrier)
    if decoded != "".join(str(bit) for bit in bits):
        raise AssertionError("HNAN_REPLAY")
    if _pack(tuple(int(bit) for bit in decoded), "MSB0") != frame:
        raise AssertionError("CROSS_VIEW_EGRESS")
    native_phase = build_raw5184_phase_source(frame)
    if native_phase["raw5184_sha256"] != sha256(frame).hexdigest():
        raise AssertionError("RML3_NATIVE_PHASE_SOURCE_IDENTITY")
    if native_phase["raw_bytes"] != 648 or native_phase["phase_quad_count"] != 20:
        raise AssertionError("RML3_NATIVE_PHASE_TOPOLOGY")
    if tuple(native_phase["phase_channel_order"]) != CHANNELS:
        raise AssertionError("RML3_NATIVE_ORDERED_CHANNELS")
    if native_phase["phase_ring"] != PHASE_MODULUS:
        raise AssertionError("RML3_NATIVE_PHASE_MODULUS")
    if native_phase["scalar_projection_runtime_authority"] is not False:
        raise AssertionError("RML3_SCALAR_AUTHORITY")
    if native_phase["canonical_vm81_mutation_authority"] is not False:
        raise AssertionError("RML3_VM81_AUTHORITY")
    if len(native_phase["channel_ledger"]) != 20:
        raise AssertionError("RML3_QUAD_LEDGER")
    for quad in native_phase["channel_ledger"]:
        phases = quad["ordered_channel_phase72"]
        if tuple(phases) != CHANNELS:
            raise AssertionError("RML3_QUAD_CHANNEL_ORDER")
        if any(type(v) is not int or not 0 <= v < PHASE_MODULUS
               for v in phases.values()):
            raise AssertionError("RML3_QUAD_PHASE_RANGE")
        for product, relation in PRODUCT_RELATIONS.items():
            generator = relation["generator"]
            reciprocal = relation["reciprocal"]
            expected = (phases[generator] + phases[reciprocal]
                        + (36 if product in ("yx", "wz") else 0)) % PHASE_MODULUS
            if phases[product] != expected:
                raise AssertionError("RML3_QUAD_RECIPROCAL_IDENTITY")
    return {"bytes": len(frame), "sha256": sha256(frame).hexdigest(),
            "rml3_phase_quads": len(native_phase["channel_ledger"]),
            "rml3_phase_root_sha256": native_phase["phase_circuit_root_sha256"],
            "rml3_source_receipt_sha256": native_phase["source_receipt_sha256"],
            "lo_shu_trit_positions": len(trit_blocks) * 9,
            "hnan_trits": len(carrier.trits),
            "base64_sextets": len(carrier.alphabet64),
            "roundtrip": True}


def main(args: list[str]) -> None:
    if len(args) != 2:
        raise SystemExit("usage: ... native-first.bin native-second.bin")
    first = inspect(Path(args[0]))
    second = inspect(Path(args[1]))
    print("PASS220_NATIVE_OUTPUT_FRAME_HNAN_LO_SHU_REINGESTION_PASS")
    print("source_bound_vm81_candidate_frames=2")
    print("native_delta_geometry_proof=false")
    print(f"first_sha256={first['sha256']}")
    print(f"second_sha256={second['sha256']}")


if __name__ == "__main__":
    main(sys.argv[1:])

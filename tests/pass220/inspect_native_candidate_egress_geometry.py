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
    return {"bytes": len(frame), "sha256": sha256(frame).hexdigest(),
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

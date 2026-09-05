from __future__ import annotations

import json
import sys
from pathlib import Path

from hhs_python.runtime.hhs_uqcel_ctypes_bridge import HHSUQCELRuntimeBridge

ENV_ROOT = bytes.fromhex(
    "da28e8224838999759d071a36fb25f924af10a9fffe2acd79b4b2c0c7840851b"
)


def build_frame() -> bytes:
    words = [0] * 81
    words[0] = 0x4832313949313632
    words[1] = 30
    words[2] = 29
    words[3] = 31
    words[4] = 1
    words[5] = 900
    words[6] = 810000
    words[7] = 26970
    words[8] = 71022
    words[9] = 1023
    words[10] = 31
    words[11] = 18 | (54 << 8) | (18 << 16) | (54 << 24)
    for chunk in range(4):
        words[12 + chunk] = int.from_bytes(ENV_ROOT[chunk * 8 : (chunk + 1) * 8], "little")
    return b"".join(word.to_bytes(8, "little") for word in words)


def canonical_record() -> dict[str, object]:
    result = HHSUQCELRuntimeBridge.admit_vm81(
        build_frame(),
        P=30,
        p=29,
        q=31,
        delta=1,
        A=900,
        B=900,
        cell81=0,
        left_basis8=0,
        right_basis8=1,
        previous_hash72="0" * 72,
    )
    admission = result["admission"]
    assert result["status"] == 0
    assert result["admitted"] is True
    assert result["committed_frame"] == build_frame()
    assert isinstance(admission, dict)
    return {
        "schema": "HHS_PASS219_I163_CROSSARCH_EXACT_RECORD_V1",
        "status": 0,
        "decision": admission["decision"],
        "frame_committed": 1 if admission["frame_committed"] else 0,
        "vm5184_address": admission["vm5184_address"],
        "frame_bytes": len(result["committed_frame"]),
        "change_hash72": admission["change_hash72"],
        "receipt_hash72": admission["receipt_hash72"],
        "hash216_triplet": admission["hash216_triplet"],
        "hash216_identity": admission["hash216_identity"],
    }


def main() -> int:
    record = canonical_record()
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import sys
from pathlib import Path

from hhs_python.runtime import hhs_uqcel_ctypes_bridge as uq

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


def boundary_record() -> dict[str, object]:
    result = uq.HHSUQCELRuntimeBridge.admit_vm81(
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
    hidden_composed_mutator_exported = (
        getattr(uq._LIB, "hhs_exact_pass219_admit_composed", None) is not None
    )
    public_environment_signed_exported = (
        getattr(uq._LIB, "hhs_exact_pass219_vm81_environment_admit_signed", None) is not None
    )

    # Pass 219 1.31/1.32 closes dynamic mutation through the historical
    # composed/UQCEL compatibility surface. A valid candidate may still be
    # validated, but canonical mutation must fail closed and the successor
    # environmental signed authority must remain exported.
    assert result["status"] == 5
    assert result["admitted"] is False
    assert result["committed_frame"] == bytes(uq.HHS_EXACT_VM81_FRAME_BYTES)
    assert isinstance(admission, dict)
    assert admission["decision"] == uq.HHS_EXACT_UQCEL_DECISION_ADMIT
    assert admission["frame_committed"] is False
    assert hidden_composed_mutator_exported is False
    assert public_environment_signed_exported is True

    return {
        "schema": "HHS_PASS219_I163_PYTHON_AUTHORITY_BOUNDARY_V1",
        "status": int(result["status"]),
        "validation_decision": int(admission["decision"]),
        "admitted": bool(result["admitted"]),
        "frame_committed": 1 if admission["frame_committed"] else 0,
        "committed_frame_zero": result["committed_frame"] == bytes(uq.HHS_EXACT_VM81_FRAME_BYTES),
        "frame_bytes": len(result["committed_frame"]),
        "hidden_composed_mutator_exported": hidden_composed_mutator_exported,
        "public_environment_signed_exported": public_environment_signed_exported,
    }


def main() -> int:
    record = boundary_record()
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"))
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

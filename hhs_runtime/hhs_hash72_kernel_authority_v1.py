"""
HHS Hash72 Kernel Authority v1
==============================

Kernel-backed Hash72 authority adapter for the u^72 Digital DNA ring.

This module deliberately separates the legacy deterministic receipt shell from
Hash72's kernel-native state identity. A receipt digest is now derived by
rotating the C runtime's 72-position Digital DNA ring with a canonical payload
trace, then exporting the resulting validated DNA/rotation profile witness.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List
import json

from hhs_python.runtime.hhs_ctypes_bridge import HHSHash72RingBridge


HASH72_LEN = 72


def canonical_payload(value: Any) -> str:
    """Stable semantic projection before ring transport.

    This is not the Hash72 identity itself. It is the deterministic transport
    trace used to rotate the u^72 ring.
    """

    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class HHSHash72KernelWitness:
    schema: str
    label: str
    canonical_payload: str
    dna: str
    digest: str
    zero_sum: bool
    trace_count: int
    rotation_profile: List[int]
    positions: List[int]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _transport_bytes(label: str, payload: str) -> bytes:
    return f"{label}\u241f{payload}".encode("utf-8")


def make_hash72_kernel_witness(label: str, value: Any, *, width: int = 24) -> HHSHash72KernelWitness:
    """Derive a Hash72 witness by rotating the C u^72 ring.

    For each canonical byte, the byte value is interpreted as a toroidal
    rotation delta at a deterministic ring coordinate. The C kernel applies the
    compensatory adjacent rotation, preserving the zero-sum closure invariant.
    """

    payload = canonical_payload(value)
    ring = HHSHash72RingBridge()

    for offset, byte in enumerate(_transport_bytes(label, payload)):
        # Position is primary. The label/payload stream supplies offsets from
        # the u^72 closure state, not a direct symbol substitution.
        index = offset % HASH72_LEN
        delta = ((byte + offset) % HASH72_LEN) or HASH72_LEN
        ok = ring.rotate(index, delta)
        if not ok:
            raise RuntimeError("Hash72 u^72 ring transport failed zero-sum validation")

    export = ring.export()
    dna = export["dna"]
    width = max(1, min(HASH72_LEN, int(width)))
    digest = dna[:width]
    return HHSHash72KernelWitness(
        schema="HHS_HASH72_KERNEL_WITNESS_V1",
        label=label,
        canonical_payload=payload,
        dna=dna,
        digest=digest,
        zero_sum=bool(export["zero_sum"]),
        trace_count=int(export["trace_count"]),
        rotation_profile=[int(x) for x in export["rotation_profile"]],
        positions=[int(x) for x in export["positions"]],
    )


def hash72_kernel_digest(label: str, value: Any, *, width: int = 24) -> str:
    return make_hash72_kernel_witness(label, value, width=width).digest


def hash72_kernel_authority_self_test() -> Dict[str, Any]:
    payload = {"message": "Hash72 kernel-backed receipt authority", "n": 179971}
    witness_a = make_hash72_kernel_witness("self_test", payload)
    witness_b = make_hash72_kernel_witness("self_test", dict(reversed(list(payload.items()))))
    ring = HHSHash72RingBridge()
    before = ring.export()
    ring.rotate(5, 12)
    rotated = ring.export()
    reversed_ring = ring.reverse_state().export()
    ok = (
        witness_a.digest == witness_b.digest
        and witness_a.zero_sum
        and rotated["zero_sum"]
        and before["positions"] == reversed_ring["positions"]
    )
    return {
        "schema": "HHS_HASH72_KERNEL_AUTHORITY_SELF_TEST_V1",
        "ok": ok,
        "deterministic_digest": witness_a.digest,
        "witness": witness_a.to_dict(),
        "ring_before": before,
        "ring_rotated": rotated,
        "ring_reversed": reversed_ring,
    }


if __name__ == "__main__":
    print(hash72_kernel_authority_self_test())

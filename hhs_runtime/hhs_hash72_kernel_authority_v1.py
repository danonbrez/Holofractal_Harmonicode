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


def _apply_aggregated_transport(ring: HHSHash72RingBridge, transport: bytes) -> None:
    """Apply the exact bytewise ring trace with at most 72 ctypes crossings.

    ``hhs_hash72_ring_rotate`` is additive: each call adds ``delta`` to the
    selected ring position/profile and subtracts the same ``delta`` from the
    adjacent toroidal position/profile. The final ring state therefore depends
    on the sum of primary deltas for each of the 72 coordinates, while the
    canonical witness also records the total trace count and final operation.

    The legacy adapter crossed Python -> C once per transport byte. Large API
    payloads consequently performed millions of ctypes calls even though the
    native transition itself is only a pair of integer additions plus the
    invariant refresh. Aggregating deltas by primary coordinate preserves the
    exact final positions, DNA, rotation profile, zero-sum closure, trace count,
    last index, and last delta while reducing the boundary crossings to <= 72.
    """

    trace_count = len(transport)
    if trace_count == 0:
        return

    primary_deltas = [0] * HASH72_LEN
    last_delta = 0

    for offset, byte in enumerate(transport):
        index = offset % HASH72_LEN
        # offset == index (mod 72), so this is bit-for-bit equivalent to the
        # historical ((byte + offset) % 72) expression.
        delta = ((byte + index) % HASH72_LEN) or HASH72_LEN
        primary_deltas[index] += delta
        last_delta = delta

    for index, delta in enumerate(primary_deltas):
        if delta and not ring.rotate(index, delta):
            raise RuntimeError("Hash72 u^72 ring transport failed zero-sum validation")

    # Aggregated native rotations intentionally compress only call overhead,
    # not witness semantics. Restore the exact metadata produced by the full
    # bytewise trace after the equivalent final ring state has been reached.
    ring.ring.trace_count = trace_count
    ring.ring.last_index = (trace_count - 1) % HASH72_LEN
    ring.ring.last_delta = last_delta


def make_hash72_kernel_witness(label: str, value: Any, *, width: int = 24) -> HHSHash72KernelWitness:
    """Derive a Hash72 witness by rotating the C u^72 ring.

    For each canonical byte, the byte value is interpreted as a toroidal
    rotation delta at a deterministic ring coordinate. The C kernel applies the
    compensatory adjacent rotation, preserving the zero-sum closure invariant.
    The adapter aggregates equivalent rotations before crossing the Python/C ABI
    so authoritative semantics stay unchanged while large payloads remain
    practical for runtime use.
    """

    payload = canonical_payload(value)
    ring = HHSHash72RingBridge()
    _apply_aggregated_transport(ring, _transport_bytes(label, payload))

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

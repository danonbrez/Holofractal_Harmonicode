"""Generate byte-exact recovered binary payload for the native VM81 bridge test.

The binary source is 648 bytes; no canonical mutation or Delta arithmetic is
performed by this fixture emitter. Source provenance is a deterministic pattern
used only for dependency-scoped conformance.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("output", type=Path)
    args = p.parse_args()
    spec = importlib.util.spec_from_file_location(
        "egress_lift_test",
        Path(__file__).with_name("test_binary_trinary_egress_memory_lift.py"),
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("memory lift test source unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = bytes((i * 73 + 19) % 256 for i in range(648))
    bits = module._bits(source, "LSB0")
    trinary = tuple(module._lift_bit(bit) for bit in bits)
    recovered = module._pack(
        tuple(module._recover_bit(block) for block in trinary), "LSB0"
    )
    if recovered != source or len(trinary) * 9 != 46656:
        raise AssertionError("binary -> trinary -> binary exact witness mismatch")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(recovered)
    print(json.dumps({
        "schema": "PASS220_BINARY_TRINARY_NATIVE_FRAME_BRIDGE_V1",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "recovered_sha256": hashlib.sha256(recovered).hexdigest(),
        "bit_order": "LSB0",
        "source_bytes": len(source),
        "source_bits": len(bits),
        "trinary_positions": len(trinary) * 9,
        "roundtrip_identity": True,
        "native_delta_executed": False,
    }, sort_keys=True))

if __name__ == "__main__":
    main()

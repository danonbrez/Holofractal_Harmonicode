"""Emit a byte-offset manifest for the existing native Pass159 probe.

The manifest is a source witness, not a derived instruction program or
canonical proof. All offsets address the complete UTF-8 List(...) circuit.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
from hhs_runtime.hhs_pass220_nucleus5_matrixtimes_abp_source_v1 import Nucleus5Source
from hhs_runtime.hhs_pass220_nucleus5_source_topology_v1 import source_topology


def encode_manifest(configuration: str) -> bytes:
    circuit = Nucleus5Source().native_compilation_source_bytes(configuration)
    topology = source_topology(configuration)
    rows = [f"NUCLEUS5_V1 {len(circuit)} {sha256(circuit).hexdigest()}"]
    count = 0
    for matrix in topology["matrices"]:
        for cell in matrix["cells"]:
            # List( is a fixed five-byte source prefix.
            start, end = cell["start"] + 5, cell["end"] + 5
            payload = circuit[start:end]
            if payload != cell["source"].encode("utf-8"):
                raise ValueError("NUCLEUS5_CELL_SOURCE_MISMATCH")
            rows.append(
                f"C {matrix['index']} {cell['row']} {cell['column']} "
                f"{start} {end} {sha256(payload).hexdigest()}"
            )
            count += 1
    if count != 48:
        raise ValueError("NUCLEUS5_CELL_COUNT")
    for gate in topology["equality_occurrences"]:
        start, end = gate["start"], gate["end"]
        if circuit[start:end] != b"==":
            raise ValueError("NUCLEUS5_EQUALITY_SOURCE_MISMATCH")
        rows.append(f"E {gate['index']} {start} {end}")
    rows.append(f"END {count} {len(topology['equality_occurrences'])}")
    return ("\n".join(rows) + "\n").encode("ascii")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("configuration", choices=("ONE_INPUT", "SUCCESSOR_INPUT"))
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    args.output.write_bytes(encode_manifest(args.configuration))


if __name__ == "__main__":
    main()

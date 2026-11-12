"""Observe the inherited Pass219 signed admission native probe without changing authority.

The native helper owns exit status and committed output. This diagnostic only
surfaces stderr/stdout and exact committed-frame evidence that subprocess.run
(check=True) otherwise hides in the existing pytest traceback.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile

from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    VM81_FRAME_BYTES,
    build_execution_cases,
)

MODES = ("commit", "constraint", "bad-parent", "missing-input", "bad-pass")


def inspect_probe(executable: str, mode: str = "constraint") -> dict:
    if mode not in MODES:
        raise ValueError("UNKNOWN_PROBE_MODE")
    path = Path(executable)
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = build_execution_cases()[0]["raw_bytes"]
    if len(raw) != VM81_FRAME_BYTES:
        raise ValueError("RAW_VM81_FRAME_LENGTH")
    with tempfile.TemporaryDirectory(prefix="hhs-p219-admission-diagnostic-") as root:
        source = Path(root) / "candidate.bin"
        committed = Path(root) / "committed.bin"
        source.write_bytes(raw)
        # Do not use check=True: a negative native return IS the evidence.
        process = subprocess.run(
            [str(path), mode, str(source), str(committed)],
            check=False, capture_output=True, text=True,
        )
        result = committed.read_bytes() if committed.is_file() else None
    return {
        "mode": mode,
        "native_exit_code": process.returncode,
        "native_stdout": process.stdout,
        "native_stderr": process.stderr,
        "source_sha256": sha256(raw).hexdigest(),
        "committed_present": result is not None,
        "committed_length": len(result) if result is not None else None,
        "committed_sha256": sha256(result).hexdigest() if result is not None else None,
        "committed_all_zero": (
            result == bytes(VM81_FRAME_BYTES) if result is not None else None
        ),
        "committed_equals_input": result == raw if result is not None else None,
        "diagnostic_only": True,
        "new_canonical_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("native_probe", help="Existing compiled Pass219 native probe")
    parser.add_argument("--mode", choices=MODES, default="constraint")
    args = parser.parse_args()
    evidence = inspect_probe(args.native_probe, args.mode)
    print(json.dumps(evidence, sort_keys=True, indent=2))
    # A nonzero probe exit is preserved rather than mistaken for closure.
    return 0 if evidence["native_exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare observed Pass159 identities for independent nucleus-5 ABP source circuits.

This is a diagnostic classifier, not a symbolic proof or a replacement
Hash216 authority. It must not label fixed/program-independent VMIR as
genuine source-dependent computation.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

FIELDS = (
    "SOURCE_HASH216",
    "AST_HASH216",
    "CONSTRAINT_HASH216",
    "VMIR_HASH216",
    "HELD_RECEIPT_HASH216",
)
ALPHABET = re.compile(r"^[!-~]{216}$")


def parse(log: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in log.splitlines():
        if "=" not in line:
            continue
        field, value = line.split("=", 1)
        if field not in FIELDS:
            continue
        if field in rows or not ALPHABET.fullmatch(value):
            raise ValueError("PASS159_IDENTITY_MALFORMED:" + field)
        rows[field] = value
    if tuple(sorted(rows)) != tuple(sorted(FIELDS)):
        raise ValueError("PASS159_IDENTITY_INCOMPLETE")
    if "NUCLEUS5_PASS159_FRONTEND_HELD_INTERPRET_REPLAY_PASS" not in log:
        raise ValueError("PASS159_NATIVE_PROBE_NOT_PASSED")
    return rows


def compare(left: str, right: str) -> dict[str, bool]:
    a, b = parse(left), parse(right)
    return {field: a[field] != b[field] for field in FIELDS}


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: compare_nucleus5_pass159_identities.py ONE_INPUT.log EQUATION_INPUT.log")
    result = compare(Path(sys.argv[1]).read_text(), Path(sys.argv[2]).read_text())
    for field, different in result.items():
        print(f"{field}_DIFFERS={int(different)}")
    if not result["SOURCE_HASH216"]:
        print("SOURCE_IDENTITY_NOT_BOUND_TO_INPUT", file=sys.stderr)
        return 1
    # No false source-dependent VM81 authority from frontend identities.
    if not result["VMIR_HASH216"]:
        print("VMIR_NOT_SOURCE_DISCRIMINATING: native semantic lowering still open")
    else:
        print("VMIR_IDENTITY_DISTINCT: instruction semantics and native execution still require proof")
    if not result["HELD_RECEIPT_HASH216"]:
        print("HELD_RECEIPT_NOT_SOURCE_DISCRIMINATING: no source-dependent execution proof")
    else:
        print("HELD_RECEIPT_IDENTITY_DISTINCT: does not itself establish native semantic closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

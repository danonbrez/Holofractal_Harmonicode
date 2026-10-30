#!/usr/bin/env python3
"""Initial additive Frozen-Layer Preservation CI gate.

Policy scope is deliberately explicit: absence from the protected registry does
NOT imply a service is mutable or that the broader contract is enforced.
"""
import argparse
import subprocess
import sys

# Existing, repository-inspected native paths. Expand only with closure evidence.
PROTECTED_EXACT_PATHS = frozenset({
    "hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py",
    "hhs_runtime/hhs_hash72_signing_layer_v1.py",
})

def changed_paths(base: str, head: str) -> set[str]:
    if not base or not head:
        raise ValueError("both base and head commits are required")
    output = subprocess.check_output(
        ["git", "diff", "--no-renames", "--name-only", "-z", "--diff-filter=ACDMRTUXB",
         f"{base}...{head}"]
    )
    return {p.decode("utf-8", "surrogateescape") for p in output.split(b"\0") if p}

def violations(paths: set[str]) -> list[str]:
    return sorted(paths & PROTECTED_EXACT_PATHS)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()
    try:
        paths = changed_paths(args.base, args.head)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"FROZEN_LAYER_GATE_ERROR: {exc}", file=sys.stderr)
        return 2
    blocked = violations(paths)
    if blocked:
        print("FROZEN_LAYER_UNAUTHORIZED_MUTATION: protected native files changed")
        for path in blocked:
            print(f"  {path}")
        print("Use a separately authorized lower-layer repair process; do not bundle into a feature extension.")
        return 1
    print(f"FROZEN_LAYER_SCOPED_GATE_PASS: {len(paths)} changed path(s), "
          f"{len(PROTECTED_EXACT_PATHS)} exact frozen paths protected.")
    print("This is a scoped source-diff check, NOT Lane 5/VM81/Hash72/Hash216 admission proof.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

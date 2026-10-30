#!/usr/bin/env python3
"""Fail-closed supplemental registry check; no claim of total runtime enforcement."""
import json
from pathlib import Path
import subprocess
import sys

REGISTRY = "contracts/frozen_layer_registry.v1.json"
BASELINE = frozenset({
    "hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py",
    "hhs_runtime/hhs_hash72_signing_layer_v1.py",
})

def load_paths(filename=REGISTRY):
    data = json.loads(Path(filename).read_text(encoding="utf-8"))
    if data.get("schema") != "hhs.frozen-layer-registry.v1":
        raise ValueError("unrecognized registry schema")
    records = data.get("protected")
    if not isinstance(records, list) or not records:
        raise ValueError("missing registry entries")
    names = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ValueError("invalid registry entry")
        path = record["path"]
        if path.startswith("/") or "\\" in path or any(
            x in ("", ".", "..") for x in path.split("/")
        ):
            raise ValueError("unsafe protected path")
        names.append(path)
    if len(names) != len(set(names)) or not BASELINE.issubset(names):
        raise ValueError("duplicate entry or baseline protection missing")
    return frozenset(names)

def evaluate(paths, protected):
    return sorted(set(paths) & protected)

def main(args):
    if len(args) != 2 or not all(args):
        print("REGISTRY_GATE_ERROR: base and head required", file=sys.stderr)
        return 2
    try:
        protected = load_paths()
        changed = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-only", "-z", "--diff-filter=ACDMRTUXB",
             args[0] + "..." + args[1]]
        )
        paths = [p.decode("utf-8", "surrogateescape") for p in changed.split(b"\0") if p]
        blocked = evaluate(paths, protected)
    except (ValueError, TypeError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print("REGISTRY_GATE_ERROR:", error, file=sys.stderr)
        return 2
    if blocked:
        for path in blocked:
            print("FROZEN_LAYER_MUTATION:", path)
        return 1
    print("FROZEN_LAYER_REGISTRY_SCOPED_PASS", len(protected))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

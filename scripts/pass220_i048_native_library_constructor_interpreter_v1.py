#!/usr/bin/env python3
"""Materialize Pass 220 I048 constructor registry from I047 records."""
from __future__ import annotations

import argparse
import json

from hhs_runtime.hhs_pass220_i048_native_library_constructor_interpreter_v1 import (
    materialize_constructor_registry,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True, help="I047 records.jsonl")
    parser.add_argument("--output", required=True, help="I048 registry JSON")
    args = parser.parse_args()
    result = materialize_constructor_registry(args.records, args.output)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

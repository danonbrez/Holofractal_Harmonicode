#!/usr/bin/env python3
"""Materialize Pass 220 I047 native-library training dataset artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hhs_runtime.hhs_pass220_i047_native_library_training_dataset_v1 import (
    load_input_spec,
    materialize_dataset,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="I047 path-based dataset input JSON")
    parser.add_argument("--output", required=True, help="noncanonical dataset output directory")
    args = parser.parse_args()

    examples = load_input_spec(Path(args.spec))
    manifest = materialize_dataset(examples, Path(args.output))
    print(json.dumps(manifest, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build and validate a Pass 214 Iteration 3 admitted oracle-model bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from hhs_backend.runtime.hhs_pass214_oracle_adjudication_v1 import (
    build_oracle_adjudication_bundle,
    canonical_json,
    validate_oracle_adjudication_bundle,
    write_oracle_adjudication_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteration2-directory", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = build_oracle_adjudication_bundle(args.iteration2_directory, manifest)
    validate_oracle_adjudication_bundle(result)
    write_oracle_adjudication_outputs(result, args.output_directory)
    print(canonical_json(result["iteration3_summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

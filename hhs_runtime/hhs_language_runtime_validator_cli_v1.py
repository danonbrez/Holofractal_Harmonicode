"""
HHS Language Runtime Validator CLI v1
====================================

Command-line interface for:
- CSV auto-discovery
- runtime language gate validation
- repo readiness reporting

Usage:
    python hhs_language_runtime_validator_cli_v1.py
    python hhs_language_runtime_validator_cli_v1.py --require-grammar
    python hhs_language_runtime_validator_cli_v1.py --min-wordnet-known-ratio 0.5
"""

from __future__ import annotations

import argparse
import json

from hhs_runtime.hhs_linguistic_validation_pipeline_v1 import validate_repo_language_runtime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-grammar", action="store_true")
    parser.add_argument("--require-wordnet", action="store_true", default=True)
    parser.add_argument("--min-wordnet-known-ratio", type=float, default=0.0)

    args = parser.parse_args()

    result = validate_repo_language_runtime(
        require_grammar=args.require_grammar,
        require_wordnet=args.require_wordnet,
        min_wordnet_known_ratio=args.min_wordnet_known_ratio,
    )

    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Issue bounded signed Pass 190 capability credentials for administrators."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from hhs_pass190_capability import CapabilityTokenError, issue_capability_token  # noqa: E402


def read_secret(env_file: Path | None) -> str:
    direct = os.environ.get("HHS_PASS190_CAPABILITY_SECRET")
    if direct:
        return direct
    if env_file is not None and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("HHS_PASS190_CAPABILITY_SECRET="):
                return line.split("=", 1)[1].strip()
    raise CapabilityTokenError("HHS_PASS190_CAPABILITY_SECRET is unavailable")


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue one signed Pass 190 capability token")
    parser.add_argument("--principal", required=True)
    parser.add_argument("--scope", action="append", required=True, dest="scopes")
    parser.add_argument("--ttl", type=int, default=900, dest="ttl_seconds")
    parser.add_argument("--env-file", type=Path, default=Path("/etc/hhs/pass190.env"))
    args = parser.parse_args()
    try:
        token = issue_capability_token(
            read_secret(args.env_file),
            principal=args.principal,
            scopes=args.scopes,
            ttl_seconds=args.ttl_seconds,
        )
    except CapabilityTokenError as exc:
        print(f"ERROR CapabilityTokenError: {exc}", file=sys.stderr)
        return 2
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Portable Pass 172 bootstrap.

The bootstrap imports the repository implementation and delegates all planning,
mutation, validation, and receipts to ``hhs_installer``. It is not an
independent installer authority.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_installer.cli import main


if __name__ == "__main__":
    raise SystemExit(main())

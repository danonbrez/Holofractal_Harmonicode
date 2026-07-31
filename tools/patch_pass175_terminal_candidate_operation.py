#!/usr/bin/env python3
"""Bind terminal candidate admission to the inherited VMRC_COMMIT operation class."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "hhs_runtime" / "pass175" / "terminal.py"
text = path.read_text(encoding="utf-8")
old = 'operation="P175_TERMINAL_ORDERED_CANDIDATE_COMMIT",'
new = 'operation="VMRC_COMMIT",'
if text.count(old) != 1:
    raise SystemExit(f"expected one ordered-candidate operation binding, found {text.count(old)}")
path.write_text(text.replace(old, new), encoding="utf-8")
Path(__file__).unlink()

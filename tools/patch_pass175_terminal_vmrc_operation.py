#!/usr/bin/env python3
"""Bind terminal hydration sealing to the inherited VMRC_COMMIT operation class."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "hhs_runtime" / "pass175" / "terminal.py"
text = path.read_text(encoding="utf-8")
old = 'operation="P175_TERMINAL_HASH216_HYDRATION_SEAL",'
new = 'operation="VMRC_COMMIT",'
if text.count(old) != 1:
    raise SystemExit(f"expected one hydration-seal operation binding, found {text.count(old)}")
path.write_text(text.replace(old, new), encoding="utf-8")
Path(__file__).unlink()

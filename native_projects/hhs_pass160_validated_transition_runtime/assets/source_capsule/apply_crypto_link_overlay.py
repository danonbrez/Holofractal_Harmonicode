#!/usr/bin/env python3
"""Apply a link-only crypto repair to a verified, generated Pass160 Makefile.

The source-capsule reference Makefile is checksum-pinned and MUST NOT change.
This utility modifies only Makefile.materialized after upstream transport and
reference-source verification and does not modify an original source blob.
"""
from __future__ import annotations

from pathlib import Path
import sys

REPAIRS = (
    ("$(CC) -shared $^ -o $@", "$(CC) -shared $^ -o $@ $(CRYPTO_LIBS)"),
    ("$(DIST)/libhhs_pass160.a -o $@", "$(DIST)/libhhs_pass160.a -o $@ $(CRYPTO_LIBS)"),
    ("tests/test_pass160_sanitizer.c -o $(DIST)/hhs-pass160-sanitize",
     "tests/test_pass160_sanitizer.c -o $(DIST)/hhs-pass160-sanitize $(CRYPTO_LIBS)"),
)
LIBRARY_VARIABLE = "CRYPTO_LIBS ?= -lcrypto\n"


def apply_overlay(source: str) -> str:
    if LIBRARY_VARIABLE in source:
        # A generated file may be reprocessed, but only if the complete overlay is present.
        if all(new in source for _, new in REPAIRS):
            return source
        raise ValueError("PASS160_PARTIAL_CRYPTO_OVERLAY")
    anchor = "CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic\n"
    if source.count(anchor) != 1:
        raise ValueError("PASS160_GENERATED_MAKEFILE_BASELINE_MISMATCH")
    result = source.replace(anchor, anchor + LIBRARY_VARIABLE)
    for old, new in REPAIRS:
        if old not in result:
            raise ValueError("PASS160_GENERATED_LINK_COMMAND_MISSING")
        result = result.replace(old, new)
    if result.count("$(CRYPTO_LIBS)") != 5:
        raise ValueError("PASS160_LINK_OVERLAY_INCOMPLETE")
    return result


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_crypto_link_overlay.py <generated-Makefile.materialized>")
    path = Path(sys.argv[1])
    if path.name != "Makefile.materialized" or not path.is_file() or path.is_symlink():
        raise SystemExit("PASS160_EXPECTED_GENERATED_MAKEFILE_REQUIRED")
    original = path.read_text(encoding="utf-8")
    patched = apply_overlay(original)
    if patched != original:
        path.write_text(patched, encoding="utf-8")
    print("PASS160_GENERATED_CRYPTO_LINK_OVERLAY=VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

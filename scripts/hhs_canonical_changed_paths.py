"""Canonical byte-preserving Git change-path constructor for frozen-layer admission.

Candidate-only evidence: this module never grants canonical VM81 authority.
"""
from __future__ import annotations

import subprocess


class ChangedPathEvidenceError(ValueError):
    """Git path evidence is absent, malformed, or unverifiable."""


def decode_nul_paths(data: bytes) -> frozenset[str]:
    if not isinstance(data, bytes) or not data or not data.endswith(b"\0"):
        raise ChangedPathEvidenceError("GIT_PATH_EVIDENCE_NOT_NUL_TERMINATED")
    entries = data[:-1].split(b"\0")
    if any(not item for item in entries):
        raise ChangedPathEvidenceError("GIT_PATH_EVIDENCE_EMPTY_ENTRY")
    return frozenset(item.decode("utf-8", "surrogateescape") for item in entries)


def changed_paths(base: str, head: str) -> frozenset[str]:
    if not base or not head:
        raise ChangedPathEvidenceError("BASE_AND_HEAD_REQUIRED")
    output = subprocess.check_output([
        "git", "diff", "--no-renames", "--name-only", "-z",
        "--diff-filter=ACDMRTUXB", f"{base}...{head}",
    ])
    if not output:
        return frozenset()
    return decode_nul_paths(output)

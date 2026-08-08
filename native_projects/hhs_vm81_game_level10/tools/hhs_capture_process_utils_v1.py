"""Shared process/video-rate utilities for VM81 modality capture tooling.

These helpers were proven structurally identical by the Pass 214 semantic
reconciliation gate before extraction. They are presentation/tooling helpers
only and hold no VM81 mutation, Hash72, Hash216, receipt, or ledger authority.
"""
from __future__ import annotations

from fractions import Fraction
import subprocess

SCHEMA = "HHS_VM81_CAPTURE_PROCESS_UTILS_V1"
CLASSIFICATION = "VM81_SHARED_PRESENTATION_TOOLING_NON_CANONICAL"


def parse_rate(value: str) -> Fraction:
    """Parse ffprobe rational rates, mapping its unknown 0/0 sentinel to zero."""
    if not value or value == "0/0":
        return Fraction(0, 1)
    return Fraction(value)


def run_checked(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a text subprocess and return captured stdout/stderr or raise."""
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

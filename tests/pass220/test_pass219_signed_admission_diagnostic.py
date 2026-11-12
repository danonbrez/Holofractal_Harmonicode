"""Diagnostic-only regression: expose native rejection; never authorize it."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.diagnostics.pass219_signed_admission_diagnostic import inspect_probe


def _fake_native(tmp_path: Path, exit_code: int) -> str:
    script = tmp_path / "native-probe"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import pathlib, sys\n"
        "pathlib.Path(sys.argv[3]).write_bytes(bytes(648))\n"
        "print('CONSTRAINT_REJECTION_DIAGNOSTIC status=3', file=sys.stderr)\n"
        "print('CASE_INSPECTED=1')\n"
        f"sys.exit({exit_code})\n"
    )
    script.chmod(0o755)
    return str(script)


def test_rejected_native_case_retains_diagnostic_and_zero_frame(tmp_path: Path) -> None:
    result = inspect_probe(_fake_native(tmp_path, 1), "constraint")
    assert result["native_exit_code"] == 1
    assert "CONSTRAINT_REJECTION_DIAGNOSTIC" in result["native_stderr"]
    assert "CASE_INSPECTED=1" in result["native_stdout"]
    assert result["committed_length"] == 648
    assert result["committed_all_zero"] is True
    assert result["committed_equals_input"] is False
    assert result["new_canonical_authority"] is False


def test_zero_exit_does_not_claim_canonical_admission(tmp_path: Path) -> None:
    result = inspect_probe(_fake_native(tmp_path, 0), "commit")
    assert result["native_exit_code"] == 0
    assert result["diagnostic_only"] is True
    assert result["new_canonical_authority"] is False
    assert result["committed_equals_input"] is False


def test_unknown_mode_rejected_before_process(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="UNKNOWN_PROBE_MODE"):
        inspect_probe(_fake_native(tmp_path, 0), "bypass")

from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = ROOT / "python"
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from hhs_gfcc.core import HASH72_ALPHABET, inherited_hash72, inherited_hash216, run_representative_workload

SUBSYSTEM = ROOT / "native_projects" / "hhs_gfcc_pass152"


def test_inherited_hash_alphabet_is_exactly_72_unique_symbols():
    assert len(HASH72_ALPHABET) == 72
    assert len(set(HASH72_ALPHABET)) == 72
    assert HASH72_ALPHABET == "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"


def test_python_and_native_gfcc_projections_are_identical():
    workload = run_representative_workload("HHS_PASS_152_AUTHORITY_ROOT")
    cli_binary = SUBSYSTEM / "dist" / "hhs-gfcc"
    assert cli_binary.is_file()
    completed = subprocess.run([str(cli_binary)], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    native = json.loads(completed.stdout)
    assert native["stage_ratio"] == workload["stage_ratio"]
    assert native["numerator_shell"] == workload["shell"]["values"]["e2"]["numerator"]
    assert native["denominator_shell"] == workload["shell"]["values"]["b4"]["numerator"]
    assert native["terminal_residual"] == workload["shell"]["terminal_residual"]["numerator"]
    assert native["vm81_cells"] == workload["vm81"]["cell_count"] == 81
    assert native["hash72"] == workload["hash72"]["value"]
    assert native["hash216"] == workload["hash216"]["value"]


def test_python_inherited_hashes_are_deterministic_and_width_exact():
    payload = b"HHS-P152-GFCC-cross-lane-test"
    first72 = inherited_hash72(payload)
    first216 = inherited_hash216(payload)
    assert first72 == inherited_hash72(payload)
    assert first216 == inherited_hash216(payload)
    assert len(first72) == 72
    assert len(first216) == 216
    assert set(first72 + first216) <= set(HASH72_ALPHABET)

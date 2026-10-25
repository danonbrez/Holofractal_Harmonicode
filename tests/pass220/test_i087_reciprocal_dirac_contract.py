"""I087: two reciprocal Dirac constraint slots per *existing* HNAN group.

Structural interface gate only: not a quantum or hydrogen validation.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/operations/restart/PASS_220_I087_RECIPROCAL_DIRAC_HNAN_CHECKPOINT_20261025.md"


def test_reciprocal_dirac_pair_is_not_eight_new_oscillators():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "D_g^+(psi_g)" in text
    assert "D_g^-(bar_psi_g)" in text
    assert "overleftarrow{D}_mu" in text
    assert "already defined" in text
    assert "no particles, geometry, clock, or VM81 mutation" in text
    assert "exact gamma conventions" in text.lower()
    assert "no native C++ or GUI changes" in text


def test_preserves_existing_orbit_partition_fixture():
    cycles = [{(group + 16 * k) % 72 for k in range(9)} for group in range(8)]
    assert all(len(cycle) == 9 for cycle in cycles)
    assert len(set.union(*cycles)) == 72

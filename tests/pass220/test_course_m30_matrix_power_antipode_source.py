"""Module 30: independent exact arithmetic projection, not native HNAN admission."""
from pathlib import Path
import re

SOURCE = Path(__file__).resolve().parents[2] / "evidence/pass220/course_m30_matrix_power_antipode_hnan_source_20261021.md"


def test_module30_source_and_projection_are_distinct():
    source = SOURCE.read_text(encoding="utf-8")
    assert "MODULE 30" in source
    assert "Λ = (x+y−z−w) + (xy−zw) + (x²+z²−y²−w²)" in source
    assert "M^C = expm(C·logm(M))" in source
    assert "Independent exact projection audit" in source
    assert "{2i, 0, 0}" in source  # preserved source assertion, not verified eigenvalues
    assert "{0,1+i,-1+i}" in source


def test_antipode_ledger_and_exact_matrix_characteristic():
    # Gaussian integers represented by Python's exact integer real/imag
    x, y, z, w = 1j, -1j, 1j, -1j
    linear = x+y-z-w
    product = x*y-z*w
    quadratic = x*x+z*z-y*y-w*w
    assert (linear, product, quadratic) == (0j, 0j, 0j)
    matrix = ((x,x*x,y),(y*y,linear+product+quadratic,x**4),(w,z**4,z))
    assert matrix[2] == tuple(-t for t in matrix[0])
    assert sum(matrix[i][i] for i in range(3)) == 2j
    # Sum of 2x2 principal minors = -2; characteristic is
    # lambda*(lambda-(1+i))*(lambda-(-1+i)).
    principal = sum(matrix[i][i]*matrix[j][j]-matrix[i][j]*matrix[j][i]
                    for i,j in ((0,1),(0,2),(1,2)))
    assert principal == -2
    assert (1+1j)*(-1+1j) == -2
    assert (1+1j)+(-1+1j) == 2j


def test_centered_lo_shu_zero_mode_and_rank():
    lo_shu = ((4,9,2),(3,5,7),(8,1,6))
    centered = tuple(tuple(v-5 for v in row) for row in lo_shu)
    assert all(sum(row)==0 for row in centered)
    assert all(sum(centered[i][j] for i in range(3))==0 for j in range(3))
    assert centered[0][0]*centered[1][1]-centered[0][1]*centered[1][0] != 0
    principal = sum(centered[i][i]*centered[j][j]-centered[i][j]*centered[j][i]
                    for i,j in ((0,1),(0,2),(1,2)))
    assert principal == 24  # eigenvalues 0, +/-2sqrt(6)*i

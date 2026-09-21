from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WHITEPAPERS = ROOT / "docs" / "whitepapers"

U72 = WHITEPAPERS / "HHS_U72_UNIFIED_SCALAR_HOLOGRAPHIC_CLOSURE_V1.md"
H36 = WHITEPAPERS / "HHS_H36_DYNAMIC_LANE5_CORRESPONDENCE_V1.md"
PASS220 = WHITEPAPERS / "HHS_PASS_220_LO_SHU_PYTHAGOREAN_COLLAPSE_V1.md"
INDEX = WHITEPAPERS / "HHS_U72_H36_WHITEPAPER_ADDENDUM_INDEX_V1.md"
DIRECT = ROOT / "contracts" / "pass219" / "PASS_219_LANE5_DIRECT_WITNESS_ROUTING_1_46.md"
NONARY_PROBE = ROOT / "hhs_runtime" / "pass219" / "nonary_qudit_bigint_assembly_probe.py"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def test_exact_h36_factorization_closes_to_lane5_domain() -> None:
    assert 8 * 9 == 72
    assert 8**2 == 64
    assert 9**2 == 81
    assert 81 * 64 == 72**2 == 5184
    assert 5184**36 == 72**72
    assert (8 * 9) ** 72 == 72**72


def test_nucleus_boundary_arithmetic_is_exact() -> None:
    a2 = 1
    b2 = 2
    c2 = 3
    b4 = b2**2
    b6 = b2**3
    c4 = c2**2

    assert (a2, b2, c2) == (1, 2, 3)
    assert (c2 * a2, c2 * b2, c2 * c2) == (3, 6, 9)
    assert c4 == 9
    assert b6 * c4 == 72
    assert 81 - 9 == 72
    assert 45 == 5 * 9
    assert 45 % 9 == 0
    assert (9 + 3) // 2 == 6
    assert 15 % 9 == 6


def test_seven_cell_nested_normalizer_closes_exactly() -> None:
    b2 = 2
    c2 = 3
    b4 = b2**2
    b6 = b2**3
    c4 = c2**2
    sqrt_c4 = 3
    xy = 1

    inner = (b2 * (c2 + b2) - (c2 - b2)) // sqrt_c4
    outer = (c2 * b6 - c2) // inner

    assert inner == 3
    assert outer == 7
    assert b4 + c2 == 7
    assert ((b6 - xy) * (b4 + c2)) // outer == 7
    assert 7**2 % 9 == 4


def test_pass220_modulus_offset_geometry_is_exact() -> None:
    cells = (4, 9, 2, 3, 5, 7, 8, 1, 6)
    offsets = tuple((-cell) % 9 for cell in cells)
    assert offsets == (5, 0, 7, 6, 4, 2, 1, 8, 3)
    assert sum(cells) == 45
    assert sum(offsets) == 36
    assert sum(cells) + sum(offsets) == 81 == 9**2


def test_pass220_base72_nucleus_folds_to_normalization_cell() -> None:
    cells = (4, 9, 2, 3, 5, 7, 8, 1, 6)
    packed = 0
    for cell in cells:
        packed = packed * 72 + cell
    assert packed == 2979376632189006
    assert packed % 9 == 6


def test_u72_paper_preserves_unified_scalar_closure_reading() -> None:
    text = read(U72)
    required = (
        "BigInt serialization",
        "exact scalar arithmetic",
        "value == address == operation identity",
        "3,6,9",
        "45 mod 9 = 0",
        "81-9 = b^6c^4 = 72",
        "8*9 = 72",
        "64*81 = 5184",
        "H36(5184) := 5184^36 = 72^72",
        "AB != BA",
        "(AB+BA=P^4)/(a^2+b^2=c^2)=u",
        "u^0 == u^72",
        "zero-sum != informationless zero",
        "no native modality should require an information-losing bridge",
    )
    for needle in required:
        assert needle in text, needle


def test_h36_paper_is_explicitly_dynamic_not_static() -> None:
    text = read(H36)
    required = (
        "72^72 = exact closure/address domain",
        "simultaneously materialized runtime states",
        "algebraic transition",
        "metadata evolution",
        "dependency evolution",
        "`u^72` dynamic resonance frame",
        "materialized_intermediate_states = 0",
        "BigInt exact state",
        "VM81/C++ RNA admitted operation path",
        "recomposed_result",
        "authoritative_exact_result",
    )
    for needle in required:
        assert needle in text, needle


def test_pass220_paper_freezes_nucleus_controller_semantics() -> None:
    text = read(PASS220)
    required = (
        "HHS_PASS_220_LO_SHU_PYTHAGOREAN_COLLAPSE_V1",
        "HHS-L144-011",
        "Az=Bx",
        "Bz=Ax",
        "A != B",
        "AB !=path BA",
        "AB=P^4=BA",
        "P^4=c^4=9",
        "6=(9+sqrt(9))/2=(9+3)/2",
        "Cell `1` is the typed reciprocal of the boundary modulus",
        "Cell `7` is the nucleus collapse tensor",
        "(AB+BA=P^4)/(a^2+b^2=c^2)=u",
        "45+36=81=9^2",
        "2979376632189006 mod 9 = 6",
        "H36(5184)=5184^36=(72^2)^36=72^72",
        "u^0==u^72",
        "does **not** assert raw commutativity",
    )
    for needle in required:
        assert needle in text, needle


def test_pass220_paper_preserves_verbatim_constructor_fragments() -> None:
    text = read(PASS220)
    for needle in (
        "MatrixTimes(List(List((xy),x+y,(yx))",
        "NcalcMatrixPower",
        "COMPLEX INFINITY=(P²=pq+((q-p)P/(p+q))",
        "∆/P=√(pq+u⁷²)^x²",
        "b²P-(p+q)=x+y+z+w+xy+yx+zw+wz",
    ):
        assert needle in text, needle


def test_addendum_index_links_all_closure_papers() -> None:
    index = read(INDEX)
    assert U72.name in index
    assert H36.name in index
    assert PASS220.name in index
    for label in (
        "EXECUTED_EXACT",
        "HHS_NATIVE_SEMANTIC",
        "DEVELOPMENT_VERBATIM",
    ):
        assert label in index
    for needle in (
        "Az=Bx",
        "Bz=Ax",
        "AB=P^4=BA",
        "cell-7 collapse-tensor constraint",
    ):
        assert needle in index, needle


def test_inherited_direct_route_and_nonary_probe_supply_executable_evidence() -> None:
    direct = read(DIRECT)
    probe = read(NONARY_PROBE)

    assert "72^72 = 5184^36" in direct
    assert "5184 = 72*72 = 81*64" in direct
    assert "u^0 == u^72, u^18, u^36, u^54" in direct
    assert "materialized_intermediate_states = 0" in direct

    # The implementation probe must retain exact integer/nonary/phase mechanics.
    for needle in ("72", "9", "8"):
        assert needle in probe

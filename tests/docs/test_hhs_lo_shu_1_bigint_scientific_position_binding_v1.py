from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WHITEPAPER = ROOT / "docs" / "whitepapers" / "HHS_LO_SHU_1_BIGINT_SCIENTIFIC_POSITION_BINDING_V1.md"
CONTRACT_MD = ROOT / "contracts" / "pass219" / "PASS_219_LO_SHU_1_BIGINT_SCIENTIFIC_POSITION_BINDING_V1.md"
CONTRACT_JSON = ROOT / "contracts" / "pass219" / "pass_219_lo_shu_1_bigint_scientific_position_binding_v1.json"
SERIALIZER = ROOT / "hhs_runtime" / "hhs_reality_to_manifold_translation_v1.py"
INDEX = ROOT / "docs" / "whitepapers" / "HHS_U72_H36_WHITEPAPER_ADDENDUM_INDEX_V1.md"


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def test_lo_shu_one_cell_is_exactly_row3_column2() -> None:
    grid = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
    coords = [(r + 1, c + 1) for r, row in enumerate(grid) for c, value in enumerate(row) if value == 1]
    assert coords == [(3, 2)]


def test_machine_contract_freezes_typed_terminal_binding_without_invented_index() -> None:
    data = json.loads(read(CONTRACT_JSON))
    assert data["schema"] == "HHS_PASS_219_LO_SHU_1_BIGINT_SCIENTIFIC_POSITION_BINDING_V1"

    terminal = data["terminal_binding"]
    assert terminal["symbol"] == "1"
    assert terminal["semantics"] == "addressed_closure_admission_predicate"
    assert terminal["generic_scalar_unity_complete_interpretation"] is False
    assert terminal["lo_shu"]["layout"] == [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    assert terminal["lo_shu"]["value"] == 1
    assert terminal["lo_shu"]["row_1_based"] == 3
    assert terminal["lo_shu"]["column_1_based"] == 2

    binding = data["bigint_scientific_binding"]
    assert binding["carrier_schema"] == "HHS_HASH72_BIGINT_FLOATING_STRING_SERIALIZATION_V1"
    assert binding["position_binding"] == "bigint_string_position"
    assert binding["position_source"] == "authoritative_serialized_bigint_state"
    assert binding["numeric_index"] is None
    assert binding["numeric_index_policy"] == "must_not_be_invented_or_hard_coded"
    assert binding["scientific_matrix_shape"] == [10, 10]
    assert binding["floating_point_position_authority"] is False
    assert binding["round_trip_provenance_required"] is True


def test_whitepaper_preserves_verbatim_constructor_and_typed_annotation() -> None:
    text = read(WHITEPAPER)
    required = (
        "G³=((P²-pq)×(xA(1.112)+(123.321)×1,000",
        "−1.001)×((c²-b²),(c²-a²),(a²+b²))",
        "Mod(2^81^(-81),72^72)",
        "(m^2-m)/(y-x)-u^72==1",
        "1_LS(3,2)->BI_10x10",
        "BigInt string position",
        "10*10 scientific-notation matrix",
        "addressed closure/admission predicate",
    )
    for needle in required:
        assert needle in text, needle


def test_prose_and_machine_contract_agree_on_non_scalar_semantics() -> None:
    prose = read(CONTRACT_MD)
    machine = json.loads(read(CONTRACT_JSON))
    assert "generic scalar unity" in prose
    assert "one-based coordinate `(row=3,column=2)`" in read(WHITEPAPER)
    assert machine["terminal_binding"]["generic_scalar_unity_complete_interpretation"] is False
    assert machine["typed_annotation"]["text"] in prose
    assert machine["typed_annotation"]["authoritative_source_replacement"] is False


def test_inherited_exact_serializer_remains_anchor() -> None:
    text = read(SERIALIZER)
    assert 'schema: str = "HHS_HASH72_BIGINT_FLOATING_STRING_SERIALIZATION_V1"' in text
    assert "mantissa = str(bigint)" in text
    assert 'scientific = f"{mantissa[0]}.{mantissa[1:]}e+{len(mantissa)-1}"' in text
    assert "lossless_decode=lossless" in text


def test_contract_adds_no_authority() -> None:
    data = json.loads(read(CONTRACT_JSON))
    assert not any(data["authority"].values())


def test_addendum_index_exposes_lo_shu_one_binding() -> None:
    text = read(INDEX)
    assert WHITEPAPER.name in text
    assert "typed Lo Shu 1 at one-based (3,2)" in text
    assert "BigInt string-position provenance" in text
    assert "10*10 scientific-notation matrix binding" in text
    assert "no invented hard-coded BigInt position" in text

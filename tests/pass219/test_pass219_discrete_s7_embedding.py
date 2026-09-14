from __future__ import annotations

import pytest

from hhs_runtime.pass219.discrete_s7_embedding import (
    CHART_PARAMETER_ORDER,
    DiscreteS7EmbeddingError,
    audit_rml5_generator_family_on_s7,
    build_discrete_s7_embedding,
    build_reversible_chart,
    decode_reversible_chart,
    verify_chiral_pair_flip_on_s7,
    verify_coupled_generator_transition_on_s7,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    CHANNELS,
    PRODUCTS,
    build_gyroscope_state,
    expected_product_phase,
)


def _signs(xy: int = 1, zw: int = 1) -> dict[str, int]:
    return {"xy": xy, "yx": -xy, "zw": zw, "wz": -zw}


def _state(
    *,
    x: int = 0,
    y: int = 12,
    z: int = 24,
    w: int = 36,
    xy_sign: int = 1,
    zw_sign: int = 1,
    state_id: str = "rml6:test",
) -> dict[str, object]:
    signs = _signs(xy_sign, zw_sign)
    primitives = {"x": x, "y": y, "z": z, "w": w}
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": expected_product_phase(x, signs["xy"]),
        "yx": expected_product_phase(y, signs["yx"]),
        "zw": expected_product_phase(z, signs["zw"]),
        "wz": expected_product_phase(w, signs["wz"]),
    }
    return build_gyroscope_state(phases, signs, state_id=state_id)


def test_reversible_chart_preserves_full_balanced_gyroscope_identity() -> None:
    state = _state()
    chart = build_reversible_chart(state)
    assert tuple(chart["parameters"].keys()) == CHART_PARAMETER_ORDER
    assert chart["chart_dimension"] == 7
    assert chart["parameters"]["xy_generator_track_code"] == 0 * 72 + 12
    assert chart["parameters"]["zw_generator_track_code"] == 24 * 72 + 36
    decoded = decode_reversible_chart(chart)
    assert decoded["phases"] == state["phases"]
    assert decoded["quarter_turn_signs"] == state["quarter_turn_signs"]
    assert decoded["chart_roundtrip_exact"] is True


def test_exact_inverse_stereographic_point_is_on_s7_without_floats() -> None:
    embedding = build_discrete_s7_embedding(_state())
    point = embedding["s7_point"]
    assert len(point["coordinate_numerators"]) == 8
    assert point["sphere_norm_numerator"] == point["sphere_norm_denominator"]
    assert point["exact_unit_s7_identity_verified"] is True
    assert point["inverse_stereographic_chart_recovered_exactly"] is True
    assert point["common_denominator"] + point["coordinate_numerators"][0] == 2
    assert point["floating_point_coordinates_used"] is False
    assert embedding["discrete_embedding_injective"] is True


def test_all_four_balanced_chirality_sectors_have_distinct_exact_s7_points() -> None:
    hashes = set()
    sectors = set()
    for xy_sign in (-1, 1):
        for zw_sign in (-1, 1):
            embedding = build_discrete_s7_embedding(
                _state(xy_sign=xy_sign, zw_sign=zw_sign, state_id=f"sector:{xy_sign}:{zw_sign}")
            )
            hashes.add(embedding["s7_point"]["s7_point_sha256"])
            sectors.add(embedding["chart"]["parameters"]["chirality_sector"])
    assert len(hashes) == 4
    assert sectors == {0, 1, 2, 3}


def test_distinct_phase_states_do_not_collapse_in_reversible_chart_fixture() -> None:
    first = build_discrete_s7_embedding(_state(x=0, y=0, z=0, w=0, state_id="a"))
    second = build_discrete_s7_embedding(_state(x=1, y=0, z=0, w=0, state_id="b"))
    third = build_discrete_s7_embedding(_state(x=0, y=1, z=0, w=0, state_id="c"))
    points = {
        first["s7_point"]["s7_point_sha256"],
        second["s7_point"]["s7_point_sha256"],
        third["s7_point"]["s7_point_sha256"],
    }
    assert len(points) == 3
    assert len({
        first["chart"]["chart_sha256"],
        second["chart"]["chart_sha256"],
        third["chart"]["chart_sha256"],
    }) == 3


def test_coupled_generator_transition_preserves_exact_s7_and_inverse() -> None:
    state = _state(x=71, y=12, z=24, w=36)
    witness = verify_coupled_generator_transition_on_s7(
        state,
        generator="x",
        signed_steps=1,
        transition_id="wrap-x",
    )
    assert witness["source_exact_unit_s7"] is True
    assert witness["target_exact_unit_s7"] is True
    assert witness["reciprocal_phase_transition_bijective"] is True
    assert witness["inverse_restores_exact_s7_point"] is True
    assert witness["transition_generator_closed_on_discrete_s7_embedding"] is True
    assert witness["source_s7_point_sha256"] != witness["target_s7_point_sha256"]
    assert witness["source_s7_point_sha256"] == witness["restored_s7_point_sha256"]


@pytest.mark.parametrize("generator", ["x", "y", "z", "w"])
@pytest.mark.parametrize("delta", [-37, -18, -1, 0, 1, 18, 36, 71])
def test_all_coupled_generator_types_stay_on_s7(generator: str, delta: int) -> None:
    witness = verify_coupled_generator_transition_on_s7(
        _state(),
        generator=generator,
        signed_steps=delta,
        transition_id=f"{generator}:{delta}",
    )
    assert witness["transition_generator_closed_on_discrete_s7_embedding"] is True
    assert witness["inverse_restores_exact_s7_point"] is True


@pytest.mark.parametrize("pair_index", [0, 1])
def test_u36_chiral_pair_flip_is_self_inverse_on_s7(pair_index: int) -> None:
    witness = verify_chiral_pair_flip_on_s7(
        _state(),
        pair_index=pair_index,
        transition_id=f"pair:{pair_index}",
    )
    assert witness["u36_flip_closed_on_discrete_s7_embedding"] is True
    assert witness["u36_flip_self_inverse_on_s7"] is True
    assert witness["source_s7_point_sha256"] != witness["target_s7_point_sha256"]
    assert witness["source_s7_point_sha256"] == witness["restored_s7_point_sha256"]


def test_complete_rml5_generating_family_closes_on_discrete_s7() -> None:
    audit = audit_rml5_generator_family_on_s7(_state(x=71, y=0, z=35, w=71))
    assert audit["coupled_z72_generator_cases"] == 288
    assert audit["u36_pair_flip_cases"] == 2
    assert audit["total_generator_cases"] == 290
    assert audit["all_rml5_generators_closed_on_exact_discrete_s7"] is True
    assert audit["ambient_72_pow_8_exhaustively_enumerated"] is False


def test_rml6_rejects_product_disequilibrium() -> None:
    state = _state()
    phases = dict(state["phases"])
    phases["xy"] = (phases["xy"] + 1) % 72
    broken = build_gyroscope_state(phases, state["quarter_turn_signs"], state_id="broken-product")
    assert broken["admissible_product_geometry"] is False
    with pytest.raises(DiscreteS7EmbeddingError, match="PRODUCT_GEOMETRY_NOT_ADMISSIBLE"):
        build_discrete_s7_embedding(broken)


def test_rml6_rejects_unbalanced_chirality_even_when_products_are_geometric() -> None:
    signs = {"xy": 1, "yx": 1, "zw": 1, "wz": -1}
    primitives = {"x": 0, "y": 12, "z": 24, "w": 36}
    phases = {
        **primitives,
        "xy": expected_product_phase(primitives["x"], signs["xy"]),
        "yx": expected_product_phase(primitives["y"], signs["yx"]),
        "zw": expected_product_phase(primitives["z"], signs["zw"]),
        "wz": expected_product_phase(primitives["w"], signs["wz"]),
    }
    state = build_gyroscope_state(phases, signs, state_id="unbalanced")
    assert state["admissible_product_geometry"] is True
    with pytest.raises(DiscreteS7EmbeddingError, match="BALANCED_CHIRALITY_REQUIRED"):
        build_discrete_s7_embedding(state)


def test_rml6_rejects_float_topology_input_and_claims_no_hopf_or_bott_authority() -> None:
    state = _state()
    bad = dict(state)
    bad["phases"] = dict(state["phases"])
    bad["phases"]["x"] = 1.0
    with pytest.raises(DiscreteS7EmbeddingError, match="FLOAT_TOPOLOGY_AUTHORITY_FORBIDDEN"):
        build_discrete_s7_embedding(bad)

    embedding = build_discrete_s7_embedding(state)
    assert embedding["isometry_claimed"] is False
    assert embedding["geodesic_preservation_claimed"] is False
    assert embedding["hopf_fibration_preservation_claimed"] is False
    assert embedding["bott_periodicity_correspondence_claimed"] is False
    assert embedding["canonical_vm81_mutation_authority"] is False
    assert embedding["canonical_hash72_mint_authority"] is False
    assert embedding["canonical_hash216_persistence_authority"] is False

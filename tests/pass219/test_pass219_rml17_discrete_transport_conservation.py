from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime.pass219.discrete_transport_conservation import (
    ADDRESS_COUNT,
    CELL_COUNT,
    DIRECTIONS,
    INVERSE_DIRECTION,
    LANE_COUNT,
    OPERATIONS_PER_CELL,
    PHASE_COUNT,
    DiscreteTransportConservationError,
    audit_composed_transport_conservation,
    audit_rml16_route_conservation,
    audit_transport_address,
    audit_transport_address_manifold,
    decode_transport_address,
    discrete_divergence,
    encode_transport_address,
    signed_address_flux,
    transport_neighbor,
)
from hhs_runtime.pass219.dynamic_octonion_gyroscope import (
    build_gyroscope_state,
    expected_product_phase,
)
from hhs_runtime.pass219.reciprocal_route_cache import clear_reciprocal_route_cache

SIGNS = {"xy": 1, "yx": -1, "zw": 1, "wz": -1}


def _state(
    state_id: str,
    *,
    x: int = 7,
    y: int = 19,
    z: int = 31,
    w: int = 43,
) -> dict[str, object]:
    phases = {
        "x": x,
        "y": y,
        "z": z,
        "w": w,
        "xy": expected_product_phase(x, SIGNS["xy"]),
        "yx": expected_product_phase(y, SIGNS["yx"]),
        "zw": expected_product_phase(z, SIGNS["zw"]),
        "wz": expected_product_phase(w, SIGNS["wz"]),
    }
    return build_gyroscope_state(phases, SIGNS, state_id=state_id)


def test_address_cardinality_is_exact_four_by_64_by_72_by_81() -> None:
    assert LANE_COUNT == 4
    assert OPERATIONS_PER_CELL == 64
    assert PHASE_COUNT == 72
    assert CELL_COUNT == 81
    assert ADDRESS_COUNT == 1_492_992


@pytest.mark.parametrize(
    "coordinates",
    [
        (0, 0, 0, 0),
        (0, 63, 71, 80),
        (1, 7, 19, 31),
        (2, 31, 36, 40),
        (3, 63, 71, 80),
    ],
)
def test_address_encode_decode_is_exact_bijection(
    coordinates: tuple[int, int, int, int],
) -> None:
    address = encode_transport_address(*coordinates)
    assert decode_transport_address(address) == coordinates


def test_local_discrete_divergence_and_reciprocal_edge_balance() -> None:
    address = encode_transport_address(2, 31, 36, 40)
    audit = audit_transport_address(address)
    assert audit["zero_discrete_divergence"] is True
    assert audit["reciprocal_neighbor_edges"] is True
    assert audit["reciprocal_edge_flux_balance"] is True
    assert audit["address_neighborhood_has_canonical_transition_authority"] is False
    assert discrete_divergence(address) == 0

    for direction in DIRECTIONS:
        target = transport_neighbor(address, direction)
        inverse = INVERSE_DIRECTION[direction]
        assert transport_neighbor(target, inverse) == address
        assert signed_address_flux(address, direction) == -signed_address_flux(
            target, inverse
        )


def test_transport_address_range_is_fail_closed() -> None:
    with pytest.raises(
        DiscreteTransportConservationError,
        match="TRANSPORT_ADDRESS_OUT_OF_RANGE",
    ):
        decode_transport_address(ADDRESS_COUNT)


def test_exhaustive_1492992_address_manifold_conservation() -> None:
    receipt = audit_transport_address_manifold()
    assert receipt["result"] == "PASS"
    assert receipt["visited_address_count"] == 1_492_992
    assert receipt["cardinality_exact"] is True
    assert receipt["bijection_failures"] == 0
    assert receipt["discrete_divergence_failures"] == 0
    assert receipt["reciprocal_neighbor_failures"] == 0
    assert receipt["reciprocal_flux_failures"] == 0
    assert receipt["all_addresses_zero_discrete_divergence"] is True
    assert receipt["all_address_edges_reciprocal"] is True
    assert receipt["all_address_edge_fluxes_balanced"] is True
    assert receipt["exhaustive_scan"] is True
    assert receipt["optimized_runtime_path"] is False


def test_rml16_route_satisfies_zero_viscosity_operator_contract() -> None:
    clear_reciprocal_route_cache()
    source = _state("rml17:route:source")
    target = _state("rml17:route:target", x=10, z=35)
    audit = audit_rml16_route_conservation(
        source,
        target,
        route_id="rml17:route",
    )
    assert audit["result"] == "PASS"
    assert audit["zero_discrete_route_divergence"] is True
    assert audit["reciprocal_edge_balance"] is True
    assert audit["admission_preserved"] is True
    assert audit["route_edge_chain_identity_preserved"] is True
    assert audit["nu_h"] == 0
    assert audit["l_h_equivalent_zero"] is True
    assert audit["canonical_diffusion_operator_present"] is False
    assert audit["composed_reverse_identity_for_route"] is True
    assert audit["delta_loss"] == 0
    assert audit["structural_information_loss_zero"] is True
    assert audit["latency_participates_in_viscosity_definition"] is False
    assert audit["rml16_cache_changes_operator_semantics"] is False


def test_rml17_rejects_float_bearing_transport_state() -> None:
    source = _state("rml17:float:source")
    target = _state("rml17:float:target", y=20)
    corrupt = deepcopy(source)
    corrupt["rml17_illegal_float"] = 0.5
    with pytest.raises(
        DiscreteTransportConservationError,
        match="FLOAT_TRANSPORT_AUTHORITY_FORBIDDEN",
    ):
        audit_rml16_route_conservation(
            corrupt,
            target,
            route_id="rml17:float",
        )


def test_admitted_composition_preserves_zero_loss_reverse_closure() -> None:
    clear_reciprocal_route_cache()
    states = [
        _state("rml17:composition:s0"),
        _state("rml17:composition:s1", x=8),
        _state("rml17:composition:s2", x=8, y=23),
        _state("rml17:composition:s3", x=12, y=23, z=36),
    ]
    audit = audit_composed_transport_conservation(
        states,
        composition_id="rml17:composition",
    )
    assert audit["result"] == "PASS"
    assert audit["state_count"] == 4
    assert audit["segment_count"] == 3
    assert audit["all_prefix_states_admission_preserved"] is True
    assert audit["route_segments_chain_exactly"] is True
    assert audit["all_segments_zero_discrete_divergence"] is True
    assert audit["all_segments_reciprocal_edge_balanced"] is True
    assert audit["nu_h"] == 0
    assert audit["l_h_equivalent_zero_under_composition"] is True
    assert audit["reverse_composition_restores_origin_exactly"] is True
    assert audit["delta_loss"] == 0
    assert audit["structural_information_loss_zero_under_composition"] is True
    assert audit["canonical_transition_authority_expanded"] is False


def test_distinguishable_predecessors_retain_distinguishable_reverse_ancestry() -> None:
    clear_reciprocal_route_cache()
    source_a = _state("rml17:injective:a", x=7)
    source_b = _state("rml17:injective:b", x=8)
    target = _state("rml17:injective:target", x=12)

    audit_a = audit_rml16_route_conservation(
        source_a,
        target,
        route_id="rml17:injective:a",
    )
    audit_b = audit_rml16_route_conservation(
        source_b,
        target,
        route_id="rml17:injective:b",
    )

    assert source_a["state_sha256"] != source_b["state_sha256"]
    assert audit_a["structural_information_loss_zero"] is True
    assert audit_b["structural_information_loss_zero"] is True
    assert audit_a["selected_route_sha256"] != audit_b["selected_route_sha256"]
    assert audit_a["audit_sha256"] != audit_b["audit_sha256"]

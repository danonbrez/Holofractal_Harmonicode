from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.discrete_transport_conservation import (
    ADDRESS_COUNT,
    DIRECTION_COUNT,
    INDEX_DIRECTION,
    decode_transport_address,
    discrete_divergence,
    signed_address_flux,
    transport_neighbor,
)
from hhs_runtime.pass219.rml20_rna_vm5184_cell_wall_bridge import (
    RML20NativeBridgeError,
    route_rml17_candidate_through_rna_vm5184,
)

ROOT = Path(__file__).resolve().parents[2]
LIBRARY = ROOT / "hhs_runtime" / "builds" / "libhhs_runtime.so"


def _raw_frame() -> bytes:
    return bytes(((index * 131 + 17) & 0xFF) for index in range(648))


@pytest.mark.parametrize(
    "address",
    [0, 1, 2, 3, 80, 373247, 746496, ADDRESS_COUNT - 1],
)
def test_rml20_native_bridge_matches_current_rml17(address: int) -> None:
    assert LIBRARY.is_file(), f"native runtime required: {LIBRARY}"
    raw = _raw_frame()
    coordinates = decode_transport_address(address)
    direction = INDEX_DIRECTION[coordinates[3]]

    result = route_rml17_candidate_through_rna_vm5184(
        raw,
        address,
        direction,
        library_path=LIBRARY,
    )

    assert result["result"] == "PASS"
    assert result["source_coordinates"] == list(coordinates)
    assert result["target_address"] == transport_neighbor(address)
    assert result["forward_flux"] == signed_address_flux(address)
    assert result["discrete_divergence"] == discrete_divergence(address) == 0
    assert result["native_lane_count"] == DIRECTION_COUNT
    assert result["current_rml17_direction_count"] == DIRECTION_COUNT
    assert len(result["transition_identity216"]) == 216
    assert result["selected_lane"] in range(DIRECTION_COUNT)
    assert all(result["parity"].values())
    assert result["authority"] == {
        "candidate_only": True,
        "exact_integer_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_persistence_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }


def test_rml20_native_bridge_rejects_non_5184_carrier() -> None:
    with pytest.raises(RML20NativeBridgeError, match="EXACT_648_BYTES_REQUIRED"):
        route_rml17_candidate_through_rna_vm5184(
            bytes(647), 0, "x", library_path=LIBRARY
        )


def test_rml20_native_bridge_rejects_bad_address_and_direction() -> None:
    raw = _raw_frame()
    with pytest.raises(RML20NativeBridgeError, match="SOURCE_ADDRESS_OUT_OF_RANGE"):
        route_rml17_candidate_through_rna_vm5184(
            raw, ADDRESS_COUNT, "x", library_path=LIBRARY
        )
    with pytest.raises(RML20NativeBridgeError, match="DIRECTION_UNSUPPORTED"):
        route_rml17_candidate_through_rna_vm5184(
            raw, 0, "lane_forward", library_path=LIBRARY
        )


def test_rml20_native_bridge_rejects_direction_not_embedded_in_address() -> None:
    raw = _raw_frame()
    with pytest.raises(
        RML20NativeBridgeError,
        match="DIRECTION_MUST_MATCH_EMBEDDED_RML17_ADDRESS",
    ):
        route_rml17_candidate_through_rna_vm5184(
            raw, 0, "y", library_path=LIBRARY
        )

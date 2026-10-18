import pytest
from hhs_runtime.pass220_phasegear_vm81_bigint_binding_v1 import (
    bind_candidate, source_locked, PhaseGearBindingError,
)

COORDS = tuple(range(64))

def test_inherited_exact_vm81_bigint_and_source_locked():
    result = bind_candidate(source_locked(), 179971, COORDS)
    assert result["frame_length"] == 648
    assert result["bigint_decimal"] == "179971"
    assert len(result["four_ordered_component_sha256"]) == 4
    assert len(result["linear5184_positions"]) == 64
    assert result["candidate_only"]
    assert not result["native_cell_wall_executed"]
    assert not result["signed_vm81_admitted"]
    assert not result["canonical_hash216_minted"]

@pytest.mark.parametrize("bigint", [-1, True, 72**72, 1.5])
def test_invalid_bigints_fail_closed(bigint):
    with pytest.raises(PhaseGearBindingError):
        bind_candidate(source_locked(), bigint, COORDS)

@pytest.mark.parametrize("coordinates", [
    tuple(range(63)), tuple(range(63)) + (62,),
    tuple(range(63)) + (5184,), tuple(range(63)) + (True,)
])
def test_invalid_coordinates_fail_closed(coordinates):
    with pytest.raises(PhaseGearBindingError):
        bind_candidate(source_locked(), 10, coordinates)

def test_source_mismatch_fails_closed():
    with pytest.raises(PhaseGearBindingError):
        bind_candidate(source_locked().replace("-180", "180", 1), 3, COORDS)

def test_invalid_lane_fails_closed():
    with pytest.raises(PhaseGearBindingError):
        bind_candidate(source_locked(), 3, COORDS, lane_index=12)

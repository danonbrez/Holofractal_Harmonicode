"""I086 Conway logic and inherited native-frame integration regression."""
import pytest

from hhs_runtime.hhs_pass220_i086_conway_life_projection_v1 import (
    MASK, conway_step, compose_conway_frame,
)


def test_toroidal_b3_s23_still_life_and_oscillator():
    assert conway_step(0) == 0
    block = sum(1 << (r * 9 + c) for r in (3, 4) for c in (3, 4))
    assert conway_step(block) == block
    horizontal = sum(1 << (4 * 9 + c) for c in (3, 4, 5))
    vertical = sum(1 << (r * 9 + 4) for r in (3, 4, 5))
    assert conway_step(horizontal) == vertical
    assert conway_step(vertical) == horizontal
    wrap = sum(1 << (r * 9 + 8) for r in (3, 4, 5))
    assert conway_step(wrap) == sum(1 << (4 * 9 + c) for c in (7, 8, 0))


@pytest.mark.parametrize("invalid", [-1, MASK + 1, True, 1.0, "0"])
def test_conway_rejects_untyped_or_out_of_domain_states(invalid):
    with pytest.raises(ValueError):
        conway_step(invalid)


def test_conway_81_native_cell_projection_preserves_inherited_hash216_array():
    occupancy = sum(1 << (4 * 9 + c) for c in (3, 4, 5))
    result = compose_conway_frame(occupancy=occupancy, frame_id=0)
    assert result["occupancy_after"] == str(conway_step(occupancy))
    assert len(result["cell_addresses"]) == 81
    assert [x["native_address"]["vm81_cell"] for x in result["cell_addresses"]] == list(range(81))
    assert [x["native_address"]["position5184"] for x in result["cell_addresses"]] == [64*i for i in range(81)]
    assert result["inherited_two_sweep_hash216_array"]
    assert len(result["inherited_hash216_index_root_sha256"]) == 64
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["native_tensor_redefined"] is False
    assert result == compose_conway_frame(occupancy=occupancy, frame_id=0)

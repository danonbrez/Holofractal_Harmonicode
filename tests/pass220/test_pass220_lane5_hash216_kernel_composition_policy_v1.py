"""Hash state identity is intrinsic; only native kernel evaluates composition."""
import inspect
import pytest

from hhs_backend.runtime.hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37 import (
    Hash216CompositionCandidate,
    Pass219Lane5Hash216GPUPhaseInterlaceOptimizer,
    split_hash216,
)
from hhs_backend.runtime.hhs_pass220_holographic_hash216_lane5_bridge_v1 import (
    Pass220HolographicLane5QueryBridge,
)
from hhs_backend.runtime.hhs_pass207_vm81_gpu_runtime_v1 import HASH72_ALPHABET


def _hash216(seed: int) -> str:
    return "".join(HASH72_ALPHABET[(seed+i)%72] for i in range(216))


@pytest.mark.parametrize("start",[0,1,19,35,71])
def test_hash72_and_hash216_well_formed_states_intrinsically_valid(start):
    value=_hash216(start)
    lanes=split_hash216(value)
    assert len(lanes)==3
    assert all(len(lane)==72 for lane in lanes)
    assert "".join(lanes)==value
    assert len(set(HASH72_ALPHABET))==72


def test_legacy_boolean_is_not_state_validity():
    value=_hash216(7)
    a=Hash216CompositionCandidate(candidate_id="a",hash216=value,validated=False)
    b=Hash216CompositionCandidate(candidate_id="b",hash216=value,validated=True)
    assert split_hash216(a.hash216)==split_hash216(b.hash216)
    # This flag has no independent authority; the existing ABI is the evaluator.
    source=inspect.getsource(Pass219Lane5Hash216GPUPhaseInterlaceOptimizer.search_hash216)
    assert "if not candidate.validated" not in source
    assert "self.phase.prime_route(" in source
    assert "self.gpu.rank_hash72_vectors(" in source


def test_holographic_bridge_does_not_forge_json_validation():
    source=inspect.getsource(Pass220HolographicLane5QueryBridge.search)
    assert "validated=True" not in source
    assert "validated=False" in source


@pytest.mark.parametrize("bad",[
    "", "x"*215, "x"*217, "~"*216,
])
def test_invalid_serialization_rejected_as_type_boundary_not_state_invalidity(bad):
    with pytest.raises(ValueError):
        split_hash216(bad)

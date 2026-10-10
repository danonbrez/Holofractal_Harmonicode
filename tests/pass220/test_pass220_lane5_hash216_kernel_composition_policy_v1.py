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

def test_native_kernel_receipt_corruption_never_counts_as_valid_composition(monkeypatch):
    """A true JSON boolean cannot override a failed native receipt."""
    native_state = _hash216(31)
    # Construct the instance without native loading. The call path itself
    # must still consume native receipt evidence and reject forged/partial
    # outputs, even if legacy metadata says "validated=True".
    optimizer = object.__new__(Pass219Lane5Hash216GPUPhaseInterlaceOptimizer)
    class Phase:
        def prime_route(self, *_args):
            return {
                "prime_cells_validated": False,
                "upper_triangular": True,
                "invertible_mod_cycle": True,
                "candidate_only": True,
                "canonical_mutation_authority": False,
                "canonical_hash72_authority": False,
                "canonical_hash216_authority": False,
                "requires_exact_cpu_vm81_replay": True,
            }
        def phase_address(self, *_args):
            return {"phases":[0,0,0,0]}
    optimizer.phase = Phase()
    with pytest.raises(RuntimeError,match="native Lane5 phase receipt"):
        optimizer.search_hash216(
            query_hash216=native_state,
            candidates=[Hash216CompositionCandidate("a",native_state,validated=True)],
            tick=0, cycle_index=0,
        )


def test_native_vector_receipt_requires_complete_ordered_sources():
    native_state = _hash216(41)
    optimizer = object.__new__(Pass219Lane5Hash216GPUPhaseInterlaceOptimizer)
    class Phase:
        def prime_route(self,*_args):
            return {
                "prime_cells_validated": True,
                "upper_triangular": True,
                "invertible_mod_cycle": True,
                "candidate_only": True,
                "canonical_mutation_authority": False,
                "canonical_hash72_authority": False,
                "canonical_hash216_authority": False,
                "requires_exact_cpu_vm81_replay": True,
                "routed_slot": [0,1,2,3],
            }
        def phase_address(self,*_args):
            return {"phases":[0,0,0,0]}
    class CorruptGPU:
        def rank_hash72_vectors(self,**kwargs):
            return {
                "candidate_count":len(kwargs["candidate_hash72"]),
                "ranked":[{
                    "candidate_id":kwargs["candidate_ids"][0],
                    "candidate_hash72":kwargs["candidate_hash72"][0],
                    "source_ordinal":0,
                    "distance":0,
                }],  # incomplete when two separate candidate references
            }
    optimizer.phase = Phase()
    optimizer.gpu = CorruptGPU()
    with pytest.raises(RuntimeError,match="native Hash72 vector ranking incomplete"):
        optimizer.search_hash216(
            query_hash216=native_state,
            candidates=[
                Hash216CompositionCandidate("a",native_state,validated=True),
                Hash216CompositionCandidate("b",native_state,validated=False),
            ],
            tick=0,cycle_index=0,
        )

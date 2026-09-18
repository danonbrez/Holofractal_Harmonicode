import pytest

from hhs_backend.runtime.hhs_pass220_genesis_zero_sum_lane5_gate_v1 import (
    Pass220GenesisZeroSumLane5Gate,
)
from hhs_runtime.hhs_pass220_genesis_zero_sum_halt_v1 import (
    HALT_REASON,
    LO_SHU_ONE_LOCAL_INDEX,
    LO_SHU_SEVEN_LOCAL_INDEX,
    Pass220GenesisHaltError,
    closed_nucleus_witnesses,
    genesis_zero_sum_halt_decision,
)


ZERO81 = (0,) * 81


def _decision(
    *,
    current=ZERO81,
    nxt=ZERO81,
    witnesses=None,
    modalities_closed=True,
    raw_state_change_zero=True,
):
    return genesis_zero_sum_halt_decision(
        current_offsets=current,
        next_offsets=nxt,
        nucleus_witnesses=closed_nucleus_witnesses() if witnesses is None else witnesses,
        global_modality_zero_closed=modalities_closed,
        raw_5184_bit_state_change_zero=raw_state_change_zero,
    )


def test_global_zero_sum_closure_halts_exactly():
    result = _decision()
    assert result["halt"] is True
    assert result["reason"] == HALT_REASON
    assert result["global_zero_sum_closed"] is True
    assert result["global_modality_zero_closed"] is True
    assert result["all_local_nuclei_closed"] is True
    assert result["normalized_state_change_zero"] is True
    assert result["raw_5184_bit_state_change_zero"] is True
    assert result["global_state_change_zero"] is True
    assert result["candidate_expansion_blocked"] is True
    assert result["new_canonical_transition_blocked"] is True
    assert result["halt_extends_hash72_ledger"] is False
    assert result["halt_mints_hash216_transition"] is False
    assert LO_SHU_ONE_LOCAL_INDEX == 7
    assert LO_SHU_SEVEN_LOCAL_INDEX == 5
    assert len(result["nuclei"]) == 9


def test_each_local_one_and_seven_anchor_resolves_to_expected_global_position():
    result = _decision()
    for index, nucleus in enumerate(result["nuclei"]):
        assert nucleus["lo_shu_one_global_index"] == index * 9 + 7
        assert nucleus["lo_shu_seven_global_index"] == index * 9 + 5
        assert nucleus["one_cell_zero_normalized"] is True
        assert nucleus["seven_cell_zero_normalized"] is True


def test_any_typed_equation_witness_open_keeps_scaling_open():
    witnesses = list(closed_nucleus_witnesses())
    witnesses[4] = {**witnesses[4], "one_ninth_invariant_closed": False}
    result = _decision(witnesses=witnesses)
    assert result["halt"] is False
    assert result["all_local_nuclei_closed"] is False
    assert result["nuclei"][4]["nucleus_closed"] is False


def test_any_nonzero_normalization_offset_keeps_scaling_open():
    current = list(ZERO81)
    current[7] = 1
    result = _decision(current=current, nxt=current)
    assert result["halt"] is False
    assert result["global_zero_sum_closed"] is False
    assert result["nuclei"][0]["one_cell_zero_normalized"] is False


def test_new_normalized_state_change_keeps_scaling_open():
    nxt = list(ZERO81)
    nxt[0] = 1
    result = _decision(nxt=nxt)
    assert result["halt"] is False
    assert result["global_zero_sum_closed"] is True
    assert result["normalized_state_change_zero"] is False
    assert result["global_state_change_zero"] is False


def test_global_modality_zero_must_close_at_the_same_center():
    result = _decision(modalities_closed=False)
    assert result["halt"] is False
    assert result["global_zero_sum_closed"] is True
    assert result["global_modality_zero_closed"] is False


def test_raw_5184_bit_state_must_have_no_change():
    result = _decision(raw_state_change_zero=False)
    assert result["halt"] is False
    assert result["normalized_state_change_zero"] is True
    assert result["raw_5184_bit_state_change_zero"] is False
    assert result["global_state_change_zero"] is False


def test_witness_shape_is_fail_closed():
    with pytest.raises(Pass220GenesisHaltError):
        genesis_zero_sum_halt_decision(
            current_offsets=ZERO81,
            next_offsets=ZERO81,
            nucleus_witnesses=closed_nucleus_witnesses()[:-1],
            global_modality_zero_closed=True,
            raw_5184_bit_state_change_zero=True,
        )

    duplicate = list(closed_nucleus_witnesses())
    duplicate[-1] = {**duplicate[-1], "nucleus_index": 0}
    with pytest.raises(Pass220GenesisHaltError):
        genesis_zero_sum_halt_decision(
            current_offsets=ZERO81,
            next_offsets=ZERO81,
            nucleus_witnesses=duplicate,
            global_modality_zero_closed=True,
            raw_5184_bit_state_change_zero=True,
        )

    non_boolean = list(closed_nucleus_witnesses())
    non_boolean[0] = {**non_boolean[0], "ab_p4_closed": 1}
    with pytest.raises(Pass220GenesisHaltError):
        genesis_zero_sum_halt_decision(
            current_offsets=ZERO81,
            next_offsets=ZERO81,
            nucleus_witnesses=non_boolean,
            global_modality_zero_closed=True,
            raw_5184_bit_state_change_zero=True,
        )

    with pytest.raises(Pass220GenesisHaltError):
        genesis_zero_sum_halt_decision(
            current_offsets=ZERO81,
            next_offsets=ZERO81,
            nucleus_witnesses=closed_nucleus_witnesses(),
            global_modality_zero_closed=1,
            raw_5184_bit_state_change_zero=True,
        )


class _FailIfInvokedBridge:
    def search(self, **_kwargs):
        raise AssertionError("Lane 5 must not be invoked after global Genesis closure")

    def close(self):
        pass


class _RecordingBridge:
    def __init__(self):
        self.calls = []

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "baseline_ranked_ids": ("a",),
            "holographic_ranked_ids": ("a",),
            "candidate_only": True,
        }

    def close(self):
        pass


def test_lane5_gate_returns_before_ranking_on_global_closure():
    gate = Pass220GenesisZeroSumLane5Gate(bridge=_FailIfInvokedBridge())
    result = gate.search_or_halt(
        current_offsets=ZERO81,
        next_offsets=ZERO81,
        nucleus_witnesses=closed_nucleus_witnesses(),
        global_modality_zero_closed=True,
        raw_5184_bit_state_change_zero=True,
        phase="xy",
        query={},
        candidates=({"candidate_id": "unused"},),
        tick=0,
        cycle_index=0,
    )
    assert result["halt"] is True
    assert result["lane5_invoked"] is False
    assert result["candidate_count_input"] == 1
    assert result["candidate_count_ranked"] == 0
    assert result["new_canonical_transition_blocked"] is True


def test_lane5_gate_delegates_only_while_closure_is_unresolved():
    bridge = _RecordingBridge()
    gate = Pass220GenesisZeroSumLane5Gate(bridge=bridge)
    current = list(ZERO81)
    current[0] = 1
    result = gate.search_or_halt(
        current_offsets=current,
        next_offsets=current,
        nucleus_witnesses=closed_nucleus_witnesses(),
        global_modality_zero_closed=True,
        raw_5184_bit_state_change_zero=True,
        phase="xy",
        query={"hash216": "unused-by-recording-bridge"},
        candidates=({"candidate_id": "a"},),
        tick=0,
        cycle_index=0,
    )
    assert result["halt"] is False
    assert result["lane5_invoked"] is True
    assert result["candidate_count_ranked"] == 1
    assert len(bridge.calls) == 1

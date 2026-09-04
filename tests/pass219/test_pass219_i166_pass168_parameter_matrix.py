from __future__ import annotations

import ctypes

from hhs_python.runtime.hhs_pass168_ctypes_bridge import (
    HHSPass168RuntimeBridge,
    state_dict,
)


VALUES = (-2, -1, 0, 1, 2, 3)


def _candidate(index: int, value: int):
    baseline = HHSPass168RuntimeBridge.initialize()
    candidate = HHSPass168RuntimeBridge.begin(baseline)
    HHSPass168RuntimeBridge.set(candidate, index, value, 1)
    return baseline, candidate


def test_every_raw_parameter_has_deterministic_six_value_validation_matrix() -> None:
    rows = []
    for index in range(40):
        for value in VALUES:
            baseline, candidate = _candidate(index, value)
            first = HHSPass168RuntimeBridge.validate(baseline, candidate)
            second = HHSPass168RuntimeBridge.validate(baseline, candidate)
            assert first == second
            assert candidate.update_mask == (1 << index)
            assert candidate.affected_thread_bitmap & (1 << index)
            if first["valid"]:
                evaluated_a = HHSPass168RuntimeBridge.evaluate(baseline, candidate)
                evaluated_b = HHSPass168RuntimeBridge.evaluate(baseline, candidate)
                assert state_dict(evaluated_a) == state_dict(evaluated_b)
            else:
                assert first["status"] != 0
                assert first["reject_reason"] != 0
            rows.append((index, value, first["status"], first["reject_reason"]))
    assert len(rows) == 240
    assert {index for index, *_ in rows} == set(range(40))
    assert {value for _, value, *_ in rows} == set(VALUES)


def test_grouped_gauge_comparator_and_global_mutations_are_exact() -> None:
    baseline = HHSPass168RuntimeBridge.initialize()

    matched = HHSPass168RuntimeBridge.begin(baseline)
    HHSPass168RuntimeBridge.set(matched, 12, 2, 1)  # P13
    HHSPass168RuntimeBridge.set(matched, 18, 2, 1)  # P19
    assert HHSPass168RuntimeBridge.validate(baseline, matched)["valid"] is True
    matched_state = state_dict(HHSPass168RuntimeBridge.evaluate(baseline, matched))
    assert matched_state["derived"][2] == {"numerator": 1, "denominator": 1}

    mismatch = HHSPass168RuntimeBridge.begin(baseline)
    HHSPass168RuntimeBridge.set(mismatch, 12, 2, 1)
    HHSPass168RuntimeBridge.set(mismatch, 18, 3, 1)
    assert HHSPass168RuntimeBridge.validate(baseline, mismatch)["valid"] is True
    mismatch_state = state_dict(HHSPass168RuntimeBridge.evaluate(baseline, mismatch))
    assert mismatch_state["derived"][2] == {"numerator": 3, "denominator": 2}

    cancellation = HHSPass168RuntimeBridge.begin(baseline)
    HHSPass168RuntimeBridge.set(cancellation, 32, 360, 1)  # E5
    HHSPass168RuntimeBridge.set(cancellation, 33, 361, 1)  # E6
    assert HHSPass168RuntimeBridge.validate(baseline, cancellation)["valid"] is True
    cancelled_state = state_dict(HHSPass168RuntimeBridge.evaluate(baseline, cancellation))
    assert all(cell["numerator"] == 0 for row in cancelled_state["successor"] for cell in row)

    global_gain = HHSPass168RuntimeBridge.begin(baseline)
    HHSPass168RuntimeBridge.set(global_gain, 0, 2, 1)  # P1
    assert HHSPass168RuntimeBridge.validate(baseline, global_gain)["valid"] is True
    assert global_gain.affected_thread_bitmap & 1
    assert global_gain.affected_thread_bitmap != 1


def test_deterministic_fixed_seed_candidate_fuzz() -> None:
    seed = 0x16805184
    records = []
    for _ in range(256):
        seed = (seed * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        index = (seed >> 16) % 40
        value = int((seed >> 40) % 7) - 3
        baseline, candidate = _candidate(index, value)
        one = HHSPass168RuntimeBridge.validate(baseline, candidate)
        two = HHSPass168RuntimeBridge.validate(baseline, candidate)
        assert one == two
        record = (index, value, one["status"], one["reject_reason"], int(candidate.affected_thread_bitmap))
        if one["valid"]:
            a = state_dict(HHSPass168RuntimeBridge.evaluate(baseline, candidate))["state_hash216"]
            b = state_dict(HHSPass168RuntimeBridge.evaluate(baseline, candidate))["state_hash216"]
            assert a == b
            record += (a,)
        records.append(record)
    assert len(records) == 256
    assert len({row[0] for row in records}) == 40

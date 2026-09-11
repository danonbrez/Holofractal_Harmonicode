"""Focused tests for the Pass 219 SPI computational determinism invariant."""
from __future__ import annotations

import copy
import json

from hhs_spi_computational_determinism_invariant_v1 import (
    CLOSING_CONDITION_KIND,
    DETERMINISM_INVARIANT_ID,
    OUTCOMES,
    SPIComputationalDeterminismError,
    build_task_envelope,
    build_transition_candidate,
)
from hhs_spi_computational_determinism_invariant_v2 import (
    SELECTION_RULE_V2,
    execute_deterministic_step,
    reference_determinism_witness,
    replay_deterministic_step,
)


def _task(max_steps: int = 4):
    return build_task_envelope(
        instruction_id="TEST-INSTRUCTION",
        instruction="advance inside TEST scope until done=true",
        authorized_scope=("TEST",),
        closing_condition={"kind": CLOSING_CONDITION_KIND, "field": "done", "value": True},
        max_steps=max_steps,
        invariant_ids=("TEST_INVARIANT",),
    )


def _candidate(task, *, cid="A", ordinal=1, scope="TEST", status="ADMISSIBLE", closed=True, label=None):
    return build_transition_candidate(
        task,
        candidate_id=cid,
        scope_tag=scope,
        transition_ordinal=ordinal,
        next_state={"done": True, "value": ordinal},
        status=status,
        invariant_closed=closed,
        semantic_label=label,
    )


def test_task_envelope_requires_explicit_instruction_scope_closure_and_bound():
    task = _task()
    assert task["instruction"] == "advance inside TEST scope until done=true"
    assert task["authorized_scope"] == ["TEST"]
    assert task["closing_condition"] == {
        "kind": CLOSING_CONDITION_KIND,
        "field": "done",
        "value": True,
    }
    assert task["max_steps"] == 4
    assert DETERMINISM_INVARIANT_ID in task["invariant_ids"]
    assert task["outcome_domain"] == ["ADVANCE", "HALT"]
    assert tuple(task["outcome_domain"]) == OUTCOMES
    assert task["discretionary_refusal_state_exists"] is False


def test_missing_instruction_scope_or_closing_condition_fails_before_execution():
    cases = [
        dict(
            instruction_id="I",
            instruction="",
            authorized_scope=("TEST",),
            closing_condition={"kind": CLOSING_CONDITION_KIND, "field": "done", "value": True},
            max_steps=1,
        ),
        dict(
            instruction_id="I",
            instruction="x",
            authorized_scope=(),
            closing_condition={"kind": CLOSING_CONDITION_KIND, "field": "done", "value": True},
            max_steps=1,
        ),
        dict(
            instruction_id="I",
            instruction="x",
            authorized_scope=("TEST",),
            closing_condition={"kind": "UNBOUNDED", "field": "done", "value": True},
            max_steps=1,
        ),
        dict(
            instruction_id="I",
            instruction="x",
            authorized_scope=("TEST",),
            closing_condition={"kind": CLOSING_CONDITION_KIND, "field": "done", "value": True},
            max_steps=0,
        ),
    ]
    for kwargs in cases:
        try:
            build_task_envelope(**kwargs)
        except SPIComputationalDeterminismError:
            pass
        else:
            raise AssertionError(f"invalid task unexpectedly accepted: {kwargs}")


def test_same_canonical_inputs_produce_identical_advance_and_receipt():
    task = _task()
    state = {"done": False, "value": 0}
    candidates = (_candidate(task, cid="B", ordinal=2), _candidate(task, cid="A", ordinal=1))
    first = execute_deterministic_step(task, state, step_index=0, candidates=candidates)
    second = execute_deterministic_step(task, state, step_index=0, candidates=candidates)
    assert first == second
    assert first["outcome"] == "ADVANCE"
    assert first["selected_candidate_id"] == "A"
    assert first["selection_rule"] == list(SELECTION_RULE_V2)
    assert first["candidate_receipt_used_for_selection"] is False


def test_candidate_enumeration_order_has_no_authority():
    task = _task()
    state = {"done": False, "value": 0}
    a = _candidate(task, cid="A", ordinal=1)
    b = _candidate(task, cid="B", ordinal=2)
    left = execute_deterministic_step(task, state, step_index=0, candidates=(a, b))
    right = execute_deterministic_step(task, state, step_index=0, candidates=(b, a))
    assert left == right


def test_semantic_label_cannot_change_selected_transition():
    task = _task()
    state = {"done": False, "value": 0}
    later = _candidate(task, cid="LATER", ordinal=2, label="very persuasive language")
    first_a = _candidate(task, cid="FIRST", ordinal=1, label="plain")
    first_b = _candidate(task, cid="FIRST", ordinal=1, label="completely different prose")
    a = execute_deterministic_step(task, state, step_index=0, candidates=(later, first_a))
    b = execute_deterministic_step(task, state, step_index=0, candidates=(later, first_b))
    assert a["selected_candidate_id"] == b["selected_candidate_id"] == "FIRST"
    assert a["next_state"] == b["next_state"]
    assert a["semantic_label_used_for_selection"] is False
    assert b["semantic_label_used_for_selection"] is False
    assert a["candidate_receipt_used_for_selection"] is False
    assert b["candidate_receipt_used_for_selection"] is False


def test_duplicate_candidate_identity_halts_instead_of_receipt_tiebreak():
    task = _task()
    state = {"done": False}
    a = _candidate(task, cid="DUP", ordinal=1, label="one")
    b = _candidate(task, cid="DUP", ordinal=2, label="two")
    decision = execute_deterministic_step(task, state, step_index=0, candidates=(a, b))
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "QUARANTINED"
    assert decision["evidence"]["duplicate_candidate_ids"] == ["DUP"]
    assert decision["evidence"]["candidate_receipt_tie_break_forbidden"] is True


def test_closed_state_halts_with_closed_reason():
    task = _task()
    decision = execute_deterministic_step(task, {"done": True}, step_index=0, candidates=())
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "CLOSED"
    assert decision["discretionary_refusal"] is False


def test_finite_step_bound_halts_resource_bounded():
    task = _task(max_steps=2)
    decision = execute_deterministic_step(task, {"done": False}, step_index=2, candidates=())
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "RESOURCE_BOUNDED"
    assert decision["evidence"]["max_steps"] == 2


def test_empty_candidate_set_halts_null_branch():
    task = _task()
    decision = execute_deterministic_step(task, {"done": False}, step_index=0, candidates=())
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "NULL_BRANCH"


def test_out_of_scope_or_invariant_open_candidates_cannot_advance():
    task = _task()
    state = {"done": False}
    out_scope = _candidate(task, cid="OUT", ordinal=1, scope="OTHER")
    decision = execute_deterministic_step(task, state, step_index=0, candidates=(out_scope,))
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "REJECTED"
    assert decision["evidence"]["out_of_scope_candidate_ids"] == ["OUT"]

    open_invariant = _candidate(task, cid="OPEN", ordinal=1, closed=False)
    decision = execute_deterministic_step(task, state, step_index=0, candidates=(open_invariant,))
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "REJECTED"
    assert decision["evidence"]["invariant_open_candidate_ids"] == ["OPEN"]


def test_unresolved_and_quarantined_are_halt_reason_classes_not_actions():
    task = _task()
    state = {"done": False}
    unresolved = _candidate(task, cid="U", ordinal=1, status="UNRESOLVED", closed=False)
    decision = execute_deterministic_step(task, state, step_index=0, candidates=(unresolved,))
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "STABLE_UNRESOLVED"

    quarantined = _candidate(task, cid="Q", ordinal=1, status="QUARANTINED", closed=False)
    decision = execute_deterministic_step(task, state, step_index=0, candidates=(quarantined,))
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "QUARANTINED"


def test_tampered_candidate_is_receipt_bearing_quarantined_halt():
    task = _task()
    candidate = _candidate(task)
    tampered = copy.deepcopy(candidate)
    tampered["next_state"]["value"] = 999
    decision = execute_deterministic_step(
        task,
        {"done": False},
        step_index=0,
        candidates=(tampered,),
    )
    assert decision["outcome"] == "HALT"
    assert decision["halt_reason"] == "QUARANTINED"
    assert decision["evidence"]["candidate_errors"]


def test_float_transition_state_fails_before_candidate_admission():
    task = _task()
    try:
        build_transition_candidate(
            task,
            candidate_id="FLOAT",
            scope_tag="TEST",
            transition_ordinal=1,
            next_state={"done": False, "value": 1.5},
        )
    except SPIComputationalDeterminismError as exc:
        assert "FLOAT_AUTHORITY_FORBIDDEN" in str(exc)
    else:
        raise AssertionError("float candidate unexpectedly admitted")


def test_deterministic_replay_detects_decision_tampering():
    task = _task()
    state = {"done": False, "value": 0}
    candidate = _candidate(task)
    decision = execute_deterministic_step(task, state, step_index=0, candidates=(candidate,))
    replay = replay_deterministic_step(
        task,
        state,
        step_index=0,
        candidates=(candidate,),
        expected_decision=decision,
    )
    assert replay["replay_equal"] is True

    tampered = copy.deepcopy(decision)
    tampered["selected_candidate_id"] = "OTHER"
    try:
        replay_deterministic_step(
            task,
            state,
            step_index=0,
            candidates=(candidate,),
            expected_decision=tampered,
        )
    except SPIComputationalDeterminismError as exc:
        assert "DETERMINISTIC_REPLAY_MISMATCH" in str(exc)
    else:
        raise AssertionError("tampered deterministic decision unexpectedly replayed")


def test_reference_witness_closes_every_declared_determinism_invariant():
    witness = reference_determinism_witness()
    assert all(witness["invariants"].values()), witness["invariants"]
    assert witness["selection_rule"] == list(SELECTION_RULE_V2)
    assert witness["authority"] == {
        "projection_only": True,
        "candidate_only": True,
        "vm81_mutation": False,
        "canonical_hash72_minting": False,
        "canonical_hash216_minting": False,
        "canonical_persistence": False,
        "semantic_override": False,
        "floating_point_authority": False,
    }


def main() -> None:
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_") and callable(value)]
    results = []
    for test in tests:
        try:
            test()
            results.append({"name": test.__name__, "passed": True})
        except Exception as exc:
            results.append({"name": test.__name__, "passed": False, "error": f"{type(exc).__name__}: {exc}"})
    report = {
        "schema": "HHS_SPI_COMPUTATIONAL_DETERMINISM_TEST_REPORT_V2",
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "results": results,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if report["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

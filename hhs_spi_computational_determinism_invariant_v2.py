"""Repair-forward hardening for the Pass 219 SPI determinism invariant.

v2 keeps the v1 task/candidate schemas but strengthens selection identity:

    MIN_TRANSITION_ORDINAL -> STABLE_CANDIDATE_ID

Candidate receipts remain mandatory integrity witnesses, but never participate
in transition choice. Duplicate candidate IDs are therefore quarantined rather
than resolved by receipt bytes that may contain descriptive metadata.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from hhs_spi_computational_determinism_invariant_v1 import (
    CLOSING_CONDITION_KIND,
    DETERMINISM_INVARIANT_ID,
    FORMAT,
    OUTCOMES,
    SCHEMA,
    SPIComputationalDeterminismError,
    VERSION,
    _halt_decision,
    _sha256,
    build_task_envelope,
    build_transition_candidate,
    execute_deterministic_step as _execute_v1,
    verify_task_envelope,
    verify_transition_candidate,
)

SELECTION_RULE_V2 = (
    "MIN_TRANSITION_ORDINAL",
    "STABLE_CANDIDATE_ID",
)


def execute_deterministic_step(
    envelope: Mapping[str, Any],
    current_state: Mapping[str, Any],
    *,
    step_index: int,
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    task = verify_task_envelope(envelope)

    verified: list[dict[str, Any]] = []
    for candidate in candidates:
        try:
            verified.append(
                verify_transition_candidate(
                    candidate,
                    expected_task_receipt_sha256=task["task_receipt_sha256"],
                )
            )
        except SPIComputationalDeterminismError:
            # Let v1 produce the canonical receipt-bearing QUARANTINED halt.
            return _execute_v1(
                envelope,
                current_state,
                step_index=step_index,
                candidates=candidates,
            )

    ids = [item["candidate_id"] for item in verified]
    duplicates = sorted({candidate_id for candidate_id in ids if ids.count(candidate_id) > 1})
    if duplicates:
        candidate_set_sha256 = _sha256(
            {
                "verified_candidate_receipts": sorted(
                    item["candidate_receipt_sha256"] for item in verified
                ),
                "duplicate_candidate_ids": duplicates,
            }
        )
        return _halt_decision(
            task=task,
            current_state=current_state,
            step_index=step_index,
            reason="QUARANTINED",
            candidate_set_sha256=candidate_set_sha256,
            evidence={
                "duplicate_candidate_ids": duplicates,
                "selection_identity_ambiguous": True,
                "candidate_receipt_tie_break_forbidden": True,
            },
        )

    decision = _execute_v1(
        envelope,
        current_state,
        step_index=step_index,
        candidates=candidates,
    )
    if decision["outcome"] == "ADVANCE":
        decision = dict(decision)
        decision["selection_rule"] = list(SELECTION_RULE_V2)
        decision["candidate_receipt_used_for_selection"] = False
        decision.pop("decision_receipt_sha256", None)
        decision["decision_receipt_sha256"] = _sha256(decision)
    return decision


def replay_deterministic_step(
    envelope: Mapping[str, Any],
    current_state: Mapping[str, Any],
    *,
    step_index: int,
    candidates: Sequence[Mapping[str, Any]],
    expected_decision: Mapping[str, Any],
) -> dict[str, Any]:
    actual = execute_deterministic_step(
        envelope,
        current_state,
        step_index=step_index,
        candidates=candidates,
    )
    if _sha256(actual) != _sha256(expected_decision):
        raise SPIComputationalDeterminismError("DETERMINISTIC_REPLAY_MISMATCH")
    return {
        "schema": "HHS_SPI_DETERMINISTIC_REPLAY_RECEIPT_V2",
        "decision_receipt_sha256": actual["decision_receipt_sha256"],
        "replay_equal": True,
        "outcome": actual["outcome"],
    }


def reference_determinism_witness() -> dict[str, Any]:
    task = build_task_envelope(
        instruction_id="SPI-V8-DETERMINISM-INVARIANT",
        instruction="advance only inside the explicit scope until done=true, otherwise halt with receipt",
        authorized_scope=("SPI_REFERENCE",),
        closing_condition={
            "kind": CLOSING_CONDITION_KIND,
            "field": "done",
            "value": True,
        },
        max_steps=4,
        invariant_ids=("SPI_V7_OCTONION_REDUNDANCY_CLOSED",),
        v7_anchor_channel="x",
        v7_anchor_phase72=18,
    )
    state0 = {"counter": 0, "done": False}
    later = build_transition_candidate(
        task,
        candidate_id="LATER",
        scope_tag="SPI_REFERENCE",
        transition_ordinal=2,
        next_state={"counter": 2, "done": True},
        semantic_label="semantically attractive wording",
    )
    first = build_transition_candidate(
        task,
        candidate_id="FIRST",
        scope_tag="SPI_REFERENCE",
        transition_ordinal=1,
        next_state={"counter": 1, "done": True},
        semantic_label="neutral wording",
    )

    advance = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(later, first),
    )
    reordered = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(first, later),
    )

    first_relabelled = build_transition_candidate(
        task,
        candidate_id="FIRST",
        scope_tag="SPI_REFERENCE",
        transition_ordinal=1,
        next_state={"counter": 1, "done": True},
        semantic_label="completely different descriptive prose",
    )
    relabelled = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(later, first_relabelled),
    )

    replay = replay_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(later, first),
        expected_decision=advance,
    )
    closed = execute_deterministic_step(
        task,
        advance["next_state"],
        step_index=1,
        candidates=(),
    )
    null_branch = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(),
    )

    duplicate_first = build_transition_candidate(
        task,
        candidate_id="FIRST",
        scope_tag="SPI_REFERENCE",
        transition_ordinal=3,
        next_state={"counter": 3, "done": False},
        semantic_label="duplicate identity must not be receipt-tiebroken",
    )
    duplicate_halt = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(first, duplicate_first),
    )

    witness = {
        "schema": "HHS_SPI_COMPUTATIONAL_DETERMINISM_WITNESS_V2",
        "format": FORMAT,
        "version": VERSION,
        "task": task,
        "advance": advance,
        "reordered_candidate_advance": reordered,
        "relabelled_selected_candidate_advance": relabelled,
        "replay": replay,
        "closed_halt": closed,
        "null_branch_halt": null_branch,
        "duplicate_identity_halt": duplicate_halt,
        "selection_rule": list(SELECTION_RULE_V2),
        "invariants": {
            "computational_determinism_is_explicit_invariant": (
                DETERMINISM_INVARIANT_ID in task["invariant_ids"]
            ),
            "only_advance_or_halt_outcomes_exist": tuple(task["outcome_domain"]) == OUTCOMES,
            "candidate_enumeration_order_has_no_authority": (
                advance["decision_receipt_sha256"] == reordered["decision_receipt_sha256"]
            ),
            "semantic_label_has_no_selection_authority": (
                advance["selected_candidate_id"] == relabelled["selected_candidate_id"] == "FIRST"
                and advance["next_state"] == relabelled["next_state"]
                and advance["semantic_label_used_for_selection"] is False
                and advance["candidate_receipt_used_for_selection"] is False
            ),
            "duplicate_candidate_identity_halts_instead_of_receipt_tiebreak": (
                duplicate_halt["outcome"] == "HALT"
                and duplicate_halt["halt_reason"] == "QUARANTINED"
            ),
            "deterministic_replay_closes": replay["replay_equal"] is True,
            "advance_reaches_closing_condition": advance["closing_condition_after_outcome"] is True,
            "closed_state_halts": (
                closed["outcome"] == "HALT" and closed["halt_reason"] == "CLOSED"
            ),
            "empty_branch_halts": (
                null_branch["outcome"] == "HALT" and null_branch["halt_reason"] == "NULL_BRANCH"
            ),
            "discretionary_refusal_absent": all(
                item["discretionary_refusal"] is False
                for item in (advance, closed, null_branch, duplicate_halt)
            ),
            "v7_redundancy_anchor_closed": all(
                task["v7_redundancy_anchor"][key] is True
                for key in (
                    "typed_rotation_round_trip_lossless",
                    "same_octonion_algebra_all_dimensions",
                    "a2_unit_projection_preserved",
                )
            ),
        },
        "authority": {
            "projection_only": True,
            "candidate_only": True,
            "vm81_mutation": False,
            "canonical_hash72_minting": False,
            "canonical_hash216_minting": False,
            "canonical_persistence": False,
            "semantic_override": False,
            "floating_point_authority": False,
        },
    }
    witness["witness_receipt_sha256"] = _sha256(witness)
    return witness

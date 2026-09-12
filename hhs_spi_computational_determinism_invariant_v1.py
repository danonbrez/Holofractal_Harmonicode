"""Pass 219 SPI — computational determinism invariant v1.

This additive layer makes computational determinism itself an executable
constraint over a bounded explicit instruction envelope.

Within the verified execution domain, the runtime exposes exactly two action
outcomes:

    ADVANCE
    HALT

Existing repository closure classifications (CLOSED, REJECTED, QUARANTINED,
NULL_BRANCH, RESOURCE_BOUNDED, STABLE_UNRESOLVED) are reason classes beneath
HALT.  They are not discretionary third actions.

A task is executable only when it carries:

1. an explicit instruction;
2. an explicit authorized scope;
3. a specific typed closing condition;
4. a finite exact-integer step bound;
5. the computational-determinism invariant in its invariant bundle.

The same canonical task/state/candidate bytes deterministically produce the
same outcome and receipt. Candidate enumeration order and semantic labels have
no selection authority. A transition may advance only through a candidate
that is task-bound, inside authorized scope, and invariant-closed.

The v7 reciprocal/base-pair octonion dimensional-lift receipt is retained as a
redundancy/provenance anchor. It is not promoted into an alternate transition
authority.

This SPI layer remains projection/candidate-only. It cannot mutate VM81, mint
canonical Hash72/Hash216, or persist canonical state.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from hhs_spi_octonion_dimensional_lift_v1 import dimensional_lift_witness

FORMAT = "HHS_SPI_COMPUTATIONAL_DETERMINISM_INVARIANT_V1"
VERSION = "1.0.0"
SCHEMA = "HHS_SPI_COMPUTATIONAL_DETERMINISM_RECEIPT_V1"

DETERMINISM_INVARIANT_ID = "I_DET_COMPUTATIONAL_DETERMINISM"
OUTCOMES = ("ADVANCE", "HALT")
HALT_REASONS = (
    "CLOSED",
    "REJECTED",
    "QUARANTINED",
    "NULL_BRANCH",
    "RESOURCE_BOUNDED",
    "STABLE_UNRESOLVED",
)
CANDIDATE_STATUSES = ("ADMISSIBLE", "REJECTED", "QUARANTINED", "UNRESOLVED")
SELECTION_RULE = (
    "MIN_TRANSITION_ORDINAL",
    "STABLE_CANDIDATE_ID",
    "CANDIDATE_RECEIPT_SHA256",
)
CLOSING_CONDITION_KIND = "STATE_FIELD_EQUALS"


class SPIComputationalDeterminismError(ValueError):
    pass


def _validate_exact_json(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise SPIComputationalDeterminismError(f"FLOAT_AUTHORITY_FORBIDDEN:{path}")
    if value is None or isinstance(value, (str, int, bool)):
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise SPIComputationalDeterminismError(f"STRING_OBJECT_KEY_REQUIRED:{path}")
            _validate_exact_json(child, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _validate_exact_json(child, f"{path}[{index}]")
        return
    raise SPIComputationalDeterminismError(f"UNSUPPORTED_CANONICAL_TYPE:{path}:{type(value).__name__}")


def _stable_json(value: Any) -> str:
    _validate_exact_json(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256(value: Any) -> str:
    return sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SPIComputationalDeterminismError(f"{label}_NONEMPTY_STRING_REQUIRED")
    return value


def _exact_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SPIComputationalDeterminismError(f"{label}_EXACT_INTEGER_REQUIRED")
    return value


def _normalize_scope(scope: Sequence[str]) -> tuple[str, ...]:
    if isinstance(scope, (str, bytes)) or not isinstance(scope, Sequence):
        raise SPIComputationalDeterminismError("AUTHORIZED_SCOPE_SEQUENCE_REQUIRED")
    result = tuple(_nonempty_string(item, "SCOPE_TAG") for item in scope)
    if not result:
        raise SPIComputationalDeterminismError("AUTHORIZED_SCOPE_MUST_NOT_BE_EMPTY")
    if len(set(result)) != len(result):
        raise SPIComputationalDeterminismError("AUTHORIZED_SCOPE_DUPLICATE_TAG")
    return result


def _normalize_invariant_ids(invariant_ids: Sequence[str]) -> tuple[str, ...]:
    if isinstance(invariant_ids, (str, bytes)) or not isinstance(invariant_ids, Sequence):
        raise SPIComputationalDeterminismError("INVARIANT_ID_SEQUENCE_REQUIRED")
    supplied = tuple(_nonempty_string(item, "INVARIANT_ID") for item in invariant_ids)
    combined = (DETERMINISM_INVARIANT_ID,) + tuple(
        item for item in supplied if item != DETERMINISM_INVARIANT_ID
    )
    if len(set(combined)) != len(combined):
        raise SPIComputationalDeterminismError("INVARIANT_ID_DUPLICATE")
    return combined


def _normalize_closing_condition(condition: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(condition, Mapping):
        raise SPIComputationalDeterminismError("CLOSING_CONDITION_MAPPING_REQUIRED")
    _validate_exact_json(condition)
    if condition.get("kind") != CLOSING_CONDITION_KIND:
        raise SPIComputationalDeterminismError("UNSUPPORTED_CLOSING_CONDITION_KIND")
    field = _nonempty_string(condition.get("field"), "CLOSING_CONDITION_FIELD")
    if "value" not in condition:
        raise SPIComputationalDeterminismError("CLOSING_CONDITION_VALUE_REQUIRED")
    value = condition["value"]
    _validate_exact_json(value, "$.closing_condition.value")
    return {"kind": CLOSING_CONDITION_KIND, "field": field, "value": value}


def build_task_envelope(
    *,
    instruction_id: str,
    instruction: str,
    authorized_scope: Sequence[str],
    closing_condition: Mapping[str, Any],
    max_steps: int,
    invariant_ids: Sequence[str] = (),
    v7_anchor_channel: str = "x",
    v7_anchor_phase72: int = 18,
) -> dict[str, Any]:
    """Build a receipt-bound explicit instruction/scope/closure envelope."""
    iid = _nonempty_string(instruction_id, "INSTRUCTION_ID")
    text = _nonempty_string(instruction, "INSTRUCTION")
    scope = _normalize_scope(authorized_scope)
    close = _normalize_closing_condition(closing_condition)
    bound = _exact_int(max_steps, "MAX_STEPS")
    if bound < 1:
        raise SPIComputationalDeterminismError("MAX_STEPS_MUST_BE_POSITIVE")
    invariants = _normalize_invariant_ids(invariant_ids)

    v7 = dimensional_lift_witness(v7_anchor_channel, phase72=v7_anchor_phase72, dimension=8)
    if not all(v7["invariants"].values()):
        raise SPIComputationalDeterminismError("V7_REDUNDANCY_ANCHOR_NOT_CLOSED")

    envelope = {
        "schema": "HHS_SPI_BOUNDED_INSTRUCTION_ENVELOPE_V1",
        "instruction_id": iid,
        "instruction": text,
        "authorized_scope": list(scope),
        "closing_condition": close,
        "max_steps": bound,
        "invariant_ids": list(invariants),
        "v7_redundancy_anchor": {
            "source_channel": v7["source_channel"],
            "receipt_sha256": v7["receipt_sha256"],
            "typed_rotation_round_trip_lossless": v7["invariants"][
                "typed_imaginary_rotation_round_trip_lossless"
            ],
            "same_octonion_algebra_all_dimensions": v7["invariants"][
                "same_octonion_algebra_all_dimensions"
            ],
            "a2_unit_projection_preserved": v7["invariants"]["a2_unit_projection_preserved"],
        },
        "outcome_domain": list(OUTCOMES),
        "discretionary_refusal_state_exists": False,
        "semantic_override_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
    }
    envelope["task_receipt_sha256"] = _sha256(envelope)
    return envelope


def verify_task_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise SPIComputationalDeterminismError("TASK_ENVELOPE_MAPPING_REQUIRED")
    body = dict(envelope)
    supplied = body.pop("task_receipt_sha256", None)
    if not isinstance(supplied, str) or supplied != _sha256(body):
        raise SPIComputationalDeterminismError("TASK_ENVELOPE_RECEIPT_MISMATCH")
    if body.get("schema") != "HHS_SPI_BOUNDED_INSTRUCTION_ENVELOPE_V1":
        raise SPIComputationalDeterminismError("TASK_ENVELOPE_SCHEMA_MISMATCH")
    _nonempty_string(body.get("instruction_id"), "INSTRUCTION_ID")
    _nonempty_string(body.get("instruction"), "INSTRUCTION")
    _normalize_scope(body.get("authorized_scope"))
    _normalize_closing_condition(body.get("closing_condition"))
    bound = _exact_int(body.get("max_steps"), "MAX_STEPS")
    if bound < 1:
        raise SPIComputationalDeterminismError("MAX_STEPS_MUST_BE_POSITIVE")
    invariants = body.get("invariant_ids")
    if not isinstance(invariants, list) or DETERMINISM_INVARIANT_ID not in invariants:
        raise SPIComputationalDeterminismError("COMPUTATIONAL_DETERMINISM_INVARIANT_REQUIRED")
    if body.get("outcome_domain") != list(OUTCOMES):
        raise SPIComputationalDeterminismError("OUTCOME_DOMAIN_DRIFT")
    if body.get("discretionary_refusal_state_exists") is not False:
        raise SPIComputationalDeterminismError("DISCRETIONARY_REFUSAL_STATE_FORBIDDEN")
    body["task_receipt_sha256"] = supplied
    return body


def build_transition_candidate(
    envelope: Mapping[str, Any],
    *,
    candidate_id: str,
    scope_tag: str,
    transition_ordinal: int,
    next_state: Mapping[str, Any],
    status: str = "ADMISSIBLE",
    invariant_closed: bool = True,
    semantic_label: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    task = verify_task_envelope(envelope)
    cid = _nonempty_string(candidate_id, "CANDIDATE_ID")
    scope = _nonempty_string(scope_tag, "CANDIDATE_SCOPE_TAG")
    ordinal = _exact_int(transition_ordinal, "TRANSITION_ORDINAL")
    if ordinal < 0:
        raise SPIComputationalDeterminismError("TRANSITION_ORDINAL_MUST_BE_NONNEGATIVE")
    if not isinstance(next_state, Mapping):
        raise SPIComputationalDeterminismError("NEXT_STATE_MAPPING_REQUIRED")
    _validate_exact_json(next_state)
    if status not in CANDIDATE_STATUSES:
        raise SPIComputationalDeterminismError("UNKNOWN_CANDIDATE_STATUS")
    if not isinstance(invariant_closed, bool):
        raise SPIComputationalDeterminismError("INVARIANT_CLOSED_BOOLEAN_REQUIRED")
    if semantic_label is not None:
        _nonempty_string(semantic_label, "SEMANTIC_LABEL")
    if reason is not None:
        _nonempty_string(reason, "CANDIDATE_REASON")

    candidate = {
        "schema": "HHS_SPI_DETERMINISTIC_TRANSITION_CANDIDATE_V1",
        "task_receipt_sha256": task["task_receipt_sha256"],
        "candidate_id": cid,
        "scope_tag": scope,
        "transition_ordinal": ordinal,
        "status": status,
        "invariant_closed": invariant_closed,
        "next_state": dict(next_state),
        "next_state_sha256": _sha256(next_state),
        "semantic_label": semantic_label,
        "reason": reason,
    }
    candidate["candidate_receipt_sha256"] = _sha256(candidate)
    return candidate


def verify_transition_candidate(
    candidate: Mapping[str, Any], *, expected_task_receipt_sha256: str
) -> dict[str, Any]:
    if not isinstance(candidate, Mapping):
        raise SPIComputationalDeterminismError("TRANSITION_CANDIDATE_MAPPING_REQUIRED")
    body = dict(candidate)
    supplied = body.pop("candidate_receipt_sha256", None)
    if not isinstance(supplied, str) or supplied != _sha256(body):
        raise SPIComputationalDeterminismError("TRANSITION_CANDIDATE_RECEIPT_MISMATCH")
    if body.get("schema") != "HHS_SPI_DETERMINISTIC_TRANSITION_CANDIDATE_V1":
        raise SPIComputationalDeterminismError("TRANSITION_CANDIDATE_SCHEMA_MISMATCH")
    if body.get("task_receipt_sha256") != expected_task_receipt_sha256:
        raise SPIComputationalDeterminismError("TRANSITION_CANDIDATE_TASK_BINDING_MISMATCH")
    _nonempty_string(body.get("candidate_id"), "CANDIDATE_ID")
    _nonempty_string(body.get("scope_tag"), "CANDIDATE_SCOPE_TAG")
    ordinal = _exact_int(body.get("transition_ordinal"), "TRANSITION_ORDINAL")
    if ordinal < 0:
        raise SPIComputationalDeterminismError("TRANSITION_ORDINAL_MUST_BE_NONNEGATIVE")
    if body.get("status") not in CANDIDATE_STATUSES:
        raise SPIComputationalDeterminismError("UNKNOWN_CANDIDATE_STATUS")
    if not isinstance(body.get("invariant_closed"), bool):
        raise SPIComputationalDeterminismError("INVARIANT_CLOSED_BOOLEAN_REQUIRED")
    if not isinstance(body.get("next_state"), Mapping):
        raise SPIComputationalDeterminismError("NEXT_STATE_MAPPING_REQUIRED")
    if body.get("next_state_sha256") != _sha256(body["next_state"]):
        raise SPIComputationalDeterminismError("NEXT_STATE_RECEIPT_MISMATCH")
    body["candidate_receipt_sha256"] = supplied
    return body


def closing_condition_satisfied(envelope: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
    task = verify_task_envelope(envelope)
    if not isinstance(state, Mapping):
        raise SPIComputationalDeterminismError("STATE_MAPPING_REQUIRED")
    _validate_exact_json(state)
    condition = task["closing_condition"]
    return state.get(condition["field"]) == condition["value"]


def _halt_decision(
    *,
    task: Mapping[str, Any],
    current_state: Mapping[str, Any],
    step_index: int,
    reason: str,
    candidate_set_sha256: str,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    if reason not in HALT_REASONS:
        raise SPIComputationalDeterminismError("UNKNOWN_HALT_REASON")
    decision = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "task_receipt_sha256": task["task_receipt_sha256"],
        "current_state_sha256": _sha256(current_state),
        "step_index": step_index,
        "candidate_set_sha256": candidate_set_sha256,
        "outcome": "HALT",
        "halt_reason": reason,
        "selected_candidate_id": None,
        "selected_candidate_receipt_sha256": None,
        "next_state": None,
        "next_state_sha256": None,
        "closing_condition_after_outcome": closing_condition_satisfied(task, current_state),
        "evidence": dict(evidence),
        "discretionary_refusal": False,
        "semantic_override_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
    }
    decision["decision_receipt_sha256"] = _sha256(decision)
    return decision


def execute_deterministic_step(
    envelope: Mapping[str, Any],
    current_state: Mapping[str, Any],
    *,
    step_index: int,
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return exactly ADVANCE or receipt-bearing HALT for a verified task."""
    task = verify_task_envelope(envelope)
    if not isinstance(current_state, Mapping):
        raise SPIComputationalDeterminismError("STATE_MAPPING_REQUIRED")
    _validate_exact_json(current_state)
    step = _exact_int(step_index, "STEP_INDEX")
    if step < 0:
        raise SPIComputationalDeterminismError("STEP_INDEX_MUST_BE_NONNEGATIVE")
    if isinstance(candidates, (str, bytes)) or not isinstance(candidates, Sequence):
        raise SPIComputationalDeterminismError("CANDIDATE_SEQUENCE_REQUIRED")

    verified: list[dict[str, Any]] = []
    candidate_errors: list[str] = []
    for index, candidate in enumerate(candidates):
        try:
            verified.append(
                verify_transition_candidate(
                    candidate,
                    expected_task_receipt_sha256=task["task_receipt_sha256"],
                )
            )
        except SPIComputationalDeterminismError as exc:
            candidate_errors.append(f"candidate[{index}]:{exc}")

    canonical_candidate_receipts = sorted(
        item["candidate_receipt_sha256"] for item in verified
    )
    candidate_set_sha256 = _sha256(
        {
            "verified_candidate_receipts": canonical_candidate_receipts,
            "candidate_errors": sorted(candidate_errors),
        }
    )

    if candidate_errors:
        return _halt_decision(
            task=task,
            current_state=current_state,
            step_index=step,
            reason="QUARANTINED",
            candidate_set_sha256=candidate_set_sha256,
            evidence={
                "candidate_errors": sorted(candidate_errors),
                "verified_candidate_count": len(verified),
            },
        )

    if closing_condition_satisfied(task, current_state):
        return _halt_decision(
            task=task,
            current_state=current_state,
            step_index=step,
            reason="CLOSED",
            candidate_set_sha256=candidate_set_sha256,
            evidence={"closing_condition_satisfied": True},
        )

    if step >= task["max_steps"]:
        return _halt_decision(
            task=task,
            current_state=current_state,
            step_index=step,
            reason="RESOURCE_BOUNDED",
            candidate_set_sha256=candidate_set_sha256,
            evidence={"max_steps": task["max_steps"]},
        )

    scope = set(task["authorized_scope"])
    eligible = [
        item
        for item in verified
        if item["status"] == "ADMISSIBLE"
        and item["invariant_closed"] is True
        and item["scope_tag"] in scope
    ]

    if not eligible:
        if not verified:
            reason = "NULL_BRANCH"
        elif any(item["status"] == "QUARANTINED" for item in verified):
            reason = "QUARANTINED"
        elif any(item["status"] == "UNRESOLVED" for item in verified):
            reason = "STABLE_UNRESOLVED"
        else:
            reason = "REJECTED"
        return _halt_decision(
            task=task,
            current_state=current_state,
            step_index=step,
            reason=reason,
            candidate_set_sha256=candidate_set_sha256,
            evidence={
                "verified_candidate_count": len(verified),
                "eligible_candidate_count": 0,
                "authorized_scope": list(task["authorized_scope"]),
                "candidate_statuses": sorted(item["status"] for item in verified),
                "out_of_scope_candidate_ids": sorted(
                    item["candidate_id"] for item in verified if item["scope_tag"] not in scope
                ),
                "invariant_open_candidate_ids": sorted(
                    item["candidate_id"] for item in verified if item["invariant_closed"] is not True
                ),
            },
        )

    selected = min(
        eligible,
        key=lambda item: (
            item["transition_ordinal"],
            item["candidate_id"],
            item["candidate_receipt_sha256"],
        ),
    )
    next_state = selected["next_state"]
    decision = {
        "schema": SCHEMA,
        "format": FORMAT,
        "version": VERSION,
        "task_receipt_sha256": task["task_receipt_sha256"],
        "current_state_sha256": _sha256(current_state),
        "step_index": step,
        "candidate_set_sha256": candidate_set_sha256,
        "outcome": "ADVANCE",
        "halt_reason": None,
        "selection_rule": list(SELECTION_RULE),
        "selected_candidate_id": selected["candidate_id"],
        "selected_candidate_receipt_sha256": selected["candidate_receipt_sha256"],
        "selected_transition_ordinal": selected["transition_ordinal"],
        "semantic_label_used_for_selection": False,
        "next_state": dict(next_state),
        "next_state_sha256": selected["next_state_sha256"],
        "closing_condition_after_outcome": closing_condition_satisfied(task, next_state),
        "discretionary_refusal": False,
        "semantic_override_used": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
        "canonical_persistence_authority": False,
    }
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
    if not isinstance(expected_decision, Mapping):
        raise SPIComputationalDeterminismError("EXPECTED_DECISION_MAPPING_REQUIRED")
    actual = execute_deterministic_step(
        envelope,
        current_state,
        step_index=step_index,
        candidates=candidates,
    )
    if _stable_json(actual) != _stable_json(expected_decision):
        raise SPIComputationalDeterminismError("DETERMINISTIC_REPLAY_MISMATCH")
    return {
        "schema": "HHS_SPI_DETERMINISTIC_REPLAY_RECEIPT_V1",
        "decision_receipt_sha256": actual["decision_receipt_sha256"],
        "replay_equal": True,
        "outcome": actual["outcome"],
    }


def reference_determinism_witness() -> dict[str, Any]:
    task = build_task_envelope(
        instruction_id="SPI-V8-REFERENCE-INSTRUCTION",
        instruction="advance the bounded reference state until done=true",
        authorized_scope=("SPI_REFERENCE",),
        closing_condition={"kind": CLOSING_CONDITION_KIND, "field": "done", "value": True},
        max_steps=4,
        invariant_ids=("SPI_V7_OCTONION_REDUNDANCY_CLOSED",),
        v7_anchor_channel="x",
        v7_anchor_phase72=18,
    )
    state0 = {"counter": 0, "done": False}
    candidate_a = build_transition_candidate(
        task,
        candidate_id="SEMANTICALLY_ATTRACTIVE_BUT_LATER",
        scope_tag="SPI_REFERENCE",
        transition_ordinal=2,
        next_state={"counter": 2, "done": True},
        semantic_label="preferred by prose only",
    )
    candidate_b = build_transition_candidate(
        task,
        candidate_id="EXACT_FIRST",
        scope_tag="SPI_REFERENCE",
        transition_ordinal=1,
        next_state={"counter": 1, "done": True},
        semantic_label="neutral",
    )

    forward = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(candidate_a, candidate_b),
    )
    reordered = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(candidate_b, candidate_a),
    )
    replay = replay_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(candidate_a, candidate_b),
        expected_decision=forward,
    )
    closed = execute_deterministic_step(
        task,
        forward["next_state"],
        step_index=1,
        candidates=(),
    )
    no_branch = execute_deterministic_step(
        task,
        state0,
        step_index=0,
        candidates=(),
    )

    witness = {
        "schema": "HHS_SPI_COMPUTATIONAL_DETERMINISM_WITNESS_V1",
        "format": FORMAT,
        "version": VERSION,
        "task": task,
        "advance": forward,
        "reordered_candidate_advance": reordered,
        "replay": replay,
        "closed_halt": closed,
        "null_branch_halt": no_branch,
        "invariants": {
            "computational_determinism_is_explicit_invariant": (
                DETERMINISM_INVARIANT_ID in task["invariant_ids"]
            ),
            "only_advance_or_halt_outcomes_exist": tuple(task["outcome_domain"]) == OUTCOMES,
            "candidate_enumeration_order_has_no_authority": (
                forward["decision_receipt_sha256"] == reordered["decision_receipt_sha256"]
            ),
            "semantic_label_has_no_selection_authority": (
                forward["semantic_label_used_for_selection"] is False
            ),
            "deterministic_replay_closes": replay["replay_equal"] is True,
            "advance_reaches_closing_condition": forward["closing_condition_after_outcome"] is True,
            "closed_state_halts": (
                closed["outcome"] == "HALT" and closed["halt_reason"] == "CLOSED"
            ),
            "empty_branch_halts": (
                no_branch["outcome"] == "HALT" and no_branch["halt_reason"] == "NULL_BRANCH"
            ),
            "discretionary_refusal_absent": (
                forward["discretionary_refusal"] is False
                and closed["discretionary_refusal"] is False
                and no_branch["discretionary_refusal"] is False
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

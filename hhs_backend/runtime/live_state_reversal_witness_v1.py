"""
HHS Live State Reversal Witness v1
=================================

A live mutation is admissible only if it records pre-state identity,
transformation identity, post-state identity, and a bounded reversal recipe.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

from hhs_backend.runtime.live_authorized_mutation_contract_v1 import (
    AUTHORITY,
    REJECT_MUTATION_WITHOUT_POST_STATE,
    REJECT_MUTATION_WITHOUT_PRE_STATE,
    REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS,
    REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY,
    VERSION,
    hash72,
)

WITNESS_SCHEMA = "HHS_LIVE_STATE_REVERSAL_WITNESS_V1"


def build_state_identity(label: str, state: Mapping[str, Any]) -> Dict[str, Any]:
    identity = {
        "schema": "HHS_LIVE_STATE_IDENTITY_V1",
        "version": VERSION,
        "label": label,
        "state": dict(state),
    }
    identity["state_hash72"] = hash72("HHS_LIVE_STATE_IDENTITY_V1", identity)
    return identity


def build_transformation_identity(operation: str, command: Mapping[str, Any], pre_state: Mapping[str, Any]) -> Dict[str, Any]:
    identity = {
        "schema": "HHS_LIVE_TRANSFORMATION_IDENTITY_V1",
        "version": VERSION,
        "operation": operation,
        "command_id": command.get("command_id"),
        "mutation_id": command.get("mutation_id"),
        "target_surface": command.get("target_surface"),
        "pre_state_hash72": pre_state.get("state_hash72"),
    }
    identity["transformation_hash72"] = hash72("HHS_LIVE_TRANSFORMATION_IDENTITY_V1", identity)
    return identity


def build_live_state_reversal_witness(
    *,
    command: Mapping[str, Any],
    pre_state: Mapping[str, Any],
    transformation: Mapping[str, Any],
    post_state: Mapping[str, Any],
) -> Dict[str, Any]:
    witness = {
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "authority": AUTHORITY,
        "command_id": command.get("command_id"),
        "mutation_id": command.get("mutation_id"),
        "operation": command.get("requested_operation"),
        "pre_state_hash72": pre_state.get("state_hash72"),
        "transformation_hash72": transformation.get("transformation_hash72"),
        "post_state_hash72": post_state.get("state_hash72"),
        "reversible": True,
        "reversal_mode": "BOUNDED_RESTORE_TO_PRE_STATE_IDENTITY",
        "reversal_recipe": {
            "restore_pre_state_hash72": pre_state.get("state_hash72"),
            "invalidate_post_state_hash72": post_state.get("state_hash72"),
            "replay_required": False,
            "external_state_mutation": False,
        },
        "hard_invariant": "EVERY_MUTATION_REQUIRES_PRE_TRANSFORM_POST_AND_RECEIPT_IDENTITY",
    }
    witness["reversal_witness_hash72"] = hash72(WITNESS_SCHEMA, witness)
    return witness


def validate_live_state_reversal_witness(witness: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    if not witness.get("pre_state_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_PRE_STATE)
    if not witness.get("transformation_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY)
    if not witness.get("post_state_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_POST_STATE)
    if not witness.get("reversal_witness_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS)
    return {
        "schema": "HHS_LIVE_STATE_REVERSAL_WITNESS_VALIDATION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_LIVE_STATE_REVERSAL_WITNESS" if not reasons else "REJECT_LIVE_STATE_REVERSAL_WITNESS",
        "reasons": reasons,
        "reversal_witness_hash72": witness.get("reversal_witness_hash72"),
    }


def live_state_reversal_witness_self_test() -> Dict[str, Any]:
    command = {"command_id": "gui-command:self-test", "mutation_id": "mutation:self-test", "requested_operation": "runtime.tick", "target_surface": "api_route:POST /api/runtime/live/tick"}
    pre = build_state_identity("pre", {"tick": 1})
    transform = build_transformation_identity("runtime.tick", command, pre)
    post = build_state_identity("post", {"tick": 2})
    witness = build_live_state_reversal_witness(command=command, pre_state=pre, transformation=transform, post_state=post)
    validation = validate_live_state_reversal_witness(witness)
    rejected = validate_live_state_reversal_witness({})
    return {
        "schema": "HHS_LIVE_STATE_REVERSAL_WITNESS_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validation.get("ok") and not rejected.get("ok")),
        "witness": witness,
        "validation": validation,
        "rejected": rejected,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(live_state_reversal_witness_self_test(), indent=2, sort_keys=True, default=str))

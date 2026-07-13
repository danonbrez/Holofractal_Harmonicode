"""
HHS Live Mutation Receipt Chain v1
=================================

Pass 048 receipt construction for authorized live mutations.  A mutation receipt
binds command identity, pre-state, transformation identity, post-state, reversal
witness, conformance root, and WebSocket projection obligations.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

from hhs_backend.runtime.live_authorized_mutation_contract_v1 import (
    AUTHORITY,
    GUI_COMMAND_MUTATION_PROJECTED_TO_WEBSOCKET,
    GUI_COMMAND_MUTATION_RECEIPT_EMITTED,
    MUTATION_RECEIPT_SCHEMA,
    REJECT_MUTATION_WITHOUT_POST_STATE,
    REJECT_MUTATION_WITHOUT_PRE_STATE,
    REJECT_MUTATION_WITHOUT_RECEIPT,
    REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS,
    REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY,
    VERSION,
    hash72,
)

CHANNELS = ["/ws/runtime", "/ws/replay", "/ws/graph", "/ws/transport"]


def build_live_mutation_receipt(
    *,
    command: Mapping[str, Any],
    pre_state: Mapping[str, Any],
    transformation: Mapping[str, Any],
    post_state: Mapping[str, Any],
    reversal_witness: Mapping[str, Any],
    execution_record: Mapping[str, Any],
    projected_to_channels: Sequence[str] = CHANNELS,
) -> Dict[str, Any]:
    receipt = {
        "schema": MUTATION_RECEIPT_SCHEMA,
        "version": VERSION,
        "authority": AUTHORITY,
        "command_id": command.get("command_id"),
        "mutation_id": command.get("mutation_id"),
        "operation": command.get("requested_operation"),
        "target_surface": command.get("target_surface"),
        "pre_state_hash72": pre_state.get("state_hash72"),
        "transformation_hash72": transformation.get("transformation_hash72"),
        "post_state_hash72": post_state.get("state_hash72"),
        "kernel_authority": "HHS_HASH72_KERNEL_U72_DIGITAL_DNA_V1",
        "conformance_root": execution_record.get("conformance_root") or hash72("HHS_LIVE_MUTATION_CONFORMANCE_ROOT_V1", command),
        "zero_bypass_status": execution_record.get("zero_bypass_status") or "ADMITTED",
        "reversal_witness": reversal_witness.get("reversal_witness_hash72"),
        "reversal_witness_record": dict(reversal_witness),
        "execution_record": dict(execution_record),
        "projected_to_channels": list(projected_to_channels),
        "statuses": [
            GUI_COMMAND_MUTATION_RECEIPT_EMITTED,
            GUI_COMMAND_MUTATION_PROJECTED_TO_WEBSOCKET,
        ],
        "gui_mutated_runtime_truth": False,
    }
    receipt["receipt_hash72"] = hash72(MUTATION_RECEIPT_SCHEMA, receipt)
    return receipt


def validate_live_mutation_receipt(receipt: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    if receipt.get("schema") != MUTATION_RECEIPT_SCHEMA:
        reasons.append(REJECT_MUTATION_WITHOUT_RECEIPT)
    if not receipt.get("pre_state_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_PRE_STATE)
    if not receipt.get("transformation_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_TRANSFORMATION_IDENTITY)
    if not receipt.get("post_state_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_POST_STATE)
    if not receipt.get("reversal_witness"):
        reasons.append(REJECT_MUTATION_WITHOUT_REVERSAL_WITNESS)
    if not receipt.get("receipt_hash72"):
        reasons.append(REJECT_MUTATION_WITHOUT_RECEIPT)
    return {
        "schema": "HHS_LIVE_MUTATION_RECEIPT_VALIDATION_V1",
        "version": VERSION,
        "ok": not reasons,
        "status": "ADMIT_LIVE_MUTATION_RECEIPT" if not reasons else "REJECT_LIVE_MUTATION_RECEIPT",
        "reasons": reasons,
        "receipt_hash72": receipt.get("receipt_hash72"),
    }


def live_mutation_receipt_chain_self_test() -> Dict[str, Any]:
    command = {"command_id": "gui-command:self-test", "mutation_id": "mutation:self-test", "requested_operation": "runtime.tick", "target_surface": "api_route:POST /api/runtime/live/tick"}
    pre = {"state_hash72": "p" * 72}
    transformation = {"transformation_hash72": "t" * 72}
    post = {"state_hash72": "q" * 72}
    reversal = {"reversal_witness_hash72": "r" * 72}
    receipt = build_live_mutation_receipt(command=command, pre_state=pre, transformation=transformation, post_state=post, reversal_witness=reversal, execution_record={"zero_bypass_status": "ADMITTED"})
    validation = validate_live_mutation_receipt(receipt)
    rejected = validate_live_mutation_receipt({})
    return {
        "schema": "HHS_LIVE_MUTATION_RECEIPT_CHAIN_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validation.get("ok") and not rejected.get("ok")),
        "receipt": receipt,
        "validation": validation,
        "rejected": rejected,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(live_mutation_receipt_chain_self_test(), indent=2, sort_keys=True, default=str))

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from hhs_runtime.core_sandbox.hhs_general_runtime_layer_v1 import canonicalize_for_hash72, security_hash72_v44
from hhs_runtime.core_sandbox.hhs_qgu_agreement_audit_v1 import qgu_agreement_audit
from hhs_runtime.hhs_memory_ledger_replay_v1 import MemoryLedger, replay_ledger


QGU_LEARNING_TRACE_TYPE = "qgu_modality_agreement_learning_trace_v1"


def record_qgu_learning_trace(
    payload: Dict[str, Any],
    *,
    ledger_path: str | Path = "demo_reports/hhs_qgu_learning_trace_ledger_v1.json",
) -> Dict[str, Any]:
    """
    Run QGU modality agreement audit and record the resulting trace.

    This bridge does not mutate kernel code. It writes disagreement/agreement
    evidence into the append-only memory ledger so adaptive layers can consume it
    as correction material after replay validation.
    """
    audit = qgu_agreement_audit(payload)
    trace = {
        "trace_type": QGU_LEARNING_TRACE_TYPE,
        "status": audit.get("status"),
        "locked": audit.get("locked"),
        "reason": audit.get("reason", ""),
        "learning_trace": audit.get("learning_trace"),
        "trace_hash72": audit.get("trace_hash72"),
        "primitive_witness_hash72": audit.get("primitive", {}).get("witness_hash72") if isinstance(audit.get("primitive"), dict) else None,
        "propagation_rule": "locked traces may reinforce; quarantined traces may only penalize or request correction",
    }
    trace["record_hash72"] = security_hash72_v44(trace, domain="HHS_QGU_LEARNING_TRACE_RECORD")

    ledger = MemoryLedger(ledger_path)
    commit = ledger.append_payloads(QGU_LEARNING_TRACE_TYPE, [canonicalize_for_hash72(trace)])
    replay = replay_ledger(ledger_path)
    return {
        "ok": audit.get("locked") is True and replay.invalid == 0,
        "status": "RECORDED" if replay.invalid == 0 else "REPLAY_INVALID",
        "audit": canonicalize_for_hash72(audit),
        "trace": canonicalize_for_hash72(trace),
        "ledger_commit_receipt": commit.to_dict(),
        "replay_receipt": replay.to_dict(),
        "receipt_hash72": security_hash72_v44(
            {"trace": trace, "commit": commit.to_dict(), "replay": replay.to_dict()},
            domain="HHS_QGU_LEARNING_TRACE_BRIDGE_RECEIPT",
        ),
    }


def qgu_trace_to_adaptive_learning_record(recorded_trace: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a recorded QGU trace into an adaptive-learning-compatible record.

    The adaptive layer can consume this as a deterministic feedback cycle.
    Quarantine does not mutate core state; it becomes a penalized pattern.
    """
    trace = recorded_trace.get("trace", {})
    locked = bool(trace.get("locked"))
    action_status = "COMMITTED" if locked else "QUARANTINED"
    return {
        "receipt_hash72": recorded_trace.get("receipt_hash72"),
        "cycles": [
            {
                "cycle_index": 0,
                "receipt_hash72": trace.get("record_hash72"),
                "status": action_status,
                "actions": [
                    {
                        "status": action_status,
                        "receipt_hash72": trace.get("trace_hash72"),
                        "action": {
                            "kind": "QGU_MODALITY_AGREEMENT",
                            "operation": "AUDIT_AND_RECORD",
                            "state_value": {
                                "predicate": "qgu_modality_agreement_locked" if locked else "qgu_modality_disagreement_quarantined",
                                "locked": locked,
                                "reason": trace.get("reason", ""),
                            },
                        },
                    }
                ],
            }
        ],
    }

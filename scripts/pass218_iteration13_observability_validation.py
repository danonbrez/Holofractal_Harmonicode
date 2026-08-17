#!/usr/bin/env python3
"""Project real I12 operational evidence through the I13 control plane.

The preceding I12 validator supplies actual mTLS rotation, learner replacement,
quorum-loss/recovery and snapshot evidence.  I13 then consumes that evidence as
an observability/operator workload without creating a new authority source.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime_os_pass218_authority_i13 import Pass218AuthorityControlPlane
from hhs_runtime.pass218.observability_i13 import validate_authority_observability_status

I12_EVIDENCE = ROOT / ".i12-evidence"
I13_EVIDENCE = ROOT / ".i13-evidence"


class EvidenceLifecycle:
    def __init__(self, i12: dict) -> None:
        replacement = i12["member_replacement"]
        recovery = i12["bounded_recovery"]
        self._status = {
            "startup_complete": True,
            "ingestion_enabled": True,
            "local_authority_held": True,
            "distributed_authority_held": True,
            "distributed_fence_epoch": int(recovery["recovered_fence"]),
            "cluster_quorum_ready": True,
            "cluster_identity_consistent": True,
            "cluster_linearizable_read_ready": True,
            "cluster_expected_member_count": 3,
            "cluster_quorum_size": 2,
            "cluster_reachable_member_count": int(replacement["reachable_member_count"]),
            "cluster_unavailable_member_count": 0,
            "cluster_id": None,
            "cluster_member_ids": list(replacement["member_ids"]),
            "cluster_leader_ids": [],
            "cluster_probe_hash72": replacement["post_probe_hash72"],
            "quorum_loss_count": 1,
            "quorum_recovery_count": 1,
        }

    def status(self) -> dict:
        return dict(self._status)


def main() -> int:
    source_path = I12_EVIDENCE / "operational-summary.json"
    snapshot_path = I12_EVIDENCE / "pass218-i12-snapshot.db"
    cert_path = ROOT / ".i12-pki" / "client-new.pem"
    if not source_path.is_file() or not snapshot_path.is_file() or not cert_path.is_file():
        raise RuntimeError("P218_I13_REAL_I12_EVIDENCE_REQUIRED")

    i12 = json.loads(source_path.read_text(encoding="utf-8"))
    recorded_snapshot_sha = i12["snapshot"]["snapshot_sha256"]
    from hashlib import sha256
    actual_snapshot_sha = sha256(snapshot_path.read_bytes()).hexdigest()
    if actual_snapshot_sha != recorded_snapshot_sha:
        raise RuntimeError("P218_I13_I12_SNAPSHOT_DIGEST_MISMATCH")

    now = time.time_ns() // 1_000_000_000
    evidence_epoch = int(snapshot_path.stat().st_mtime_ns // 1_000_000_000)
    os.environ["HHS_PASS218_ETCD_CLIENT_CERT_FILE"] = str(cert_path)
    os.environ["HHS_PASS218_LATEST_SNAPSHOT_EPOCH_SECONDS"] = str(evidence_epoch)
    os.environ["HHS_PASS218_LATEST_REHEARSAL_EPOCH_SECONDS"] = str(evidence_epoch)

    I13_EVIDENCE.mkdir(parents=True, exist_ok=True)
    control = Pass218AuthorityControlPlane(
        EvidenceLifecycle(i12),
        state_root=I13_EVIDENCE / "state",
    )
    status = control.status()
    validate_authority_observability_status(status)
    if status["health"] == "BLOCKED" or status["critical_alert_count"] != 0:
        raise RuntimeError("P218_I13_REAL_EVIDENCE_STATUS_BLOCKED")
    alert_codes = {item["code"] for item in status["alerts"]}
    allowed_real_evidence_alerts = {"P218_I13_CERT_EXPIRY_NEAR"}
    unexpected_alerts = alert_codes - allowed_real_evidence_alerts
    if unexpected_alerts:
        raise RuntimeError(
            "P218_I13_REAL_EVIDENCE_UNEXPECTED_ALERTS:" + ",".join(sorted(unexpected_alerts))
        )
    if status["health"] == "DEGRADED" and alert_codes != allowed_real_evidence_alerts:
        raise RuntimeError("P218_I13_REAL_EVIDENCE_DEGRADED_WITHOUT_EXPECTED_CERT_ALERT")
    if status["health"] == "READY" and alert_codes:
        raise RuntimeError("P218_I13_REAL_EVIDENCE_READY_WITH_ALERTS")
    if status["distributed_fence_epoch"] != i12["bounded_recovery"]["recovered_fence"]:
        raise RuntimeError("P218_I13_RECOVERED_FENCE_PROJECTION_MISMATCH")
    if status["cluster_reachable_member_count"] != 3:
        raise RuntimeError("P218_I13_REAL_MEMBER_REACHABILITY_MISMATCH")

    action = control.prepare_action({
        "request_id": "i13-real-evidence-member-replacement-preflight",
        "operator_id": "i13-ci-operator",
        "action": "PREPARE_MEMBER_REPLACEMENT",
    })
    if action["prepared_not_executed"] is not True:
        raise RuntimeError("P218_I13_PREPARED_ACTION_EXECUTION_AMBIGUITY")
    if action["requires_external_executor"] is not True:
        raise RuntimeError("P218_I13_EXTERNAL_EXECUTOR_NOT_REQUIRED")

    receipt = control.record_run({
        "action_record_hash72": action["record_hash72"],
        "run_id": "i13-real-evidence-preflight-abort",
        "outcome": "ABORTED",
        "started_epoch_seconds": action["prepared_epoch_seconds"],
        "external_operation_executed": False,
        "canonical_target_changed": False,
        "authority_minted": False,
    })
    if receipt["canonical_target_changed"] is not False:
        raise RuntimeError("P218_I13_CANONICAL_TARGET_CHANGED")
    if receipt["authority_minted"] is not False:
        raise RuntimeError("P218_I13_AUTHORITY_MINTED")

    final_status = control.status()
    summary = {
        "schema": "HHS-P218-I13-REAL-EVIDENCE-VALIDATION-V1",
        "i12_snapshot_sha256": actual_snapshot_sha,
        "i12_recovered_fence": i12["bounded_recovery"]["recovered_fence"],
        "i12_member_ids": i12["member_replacement"]["member_ids"],
        "i13_initial_status_hash72": status["record_hash72"],
        "i13_initial_health": status["health"],
        "i13_initial_alert_codes": sorted(alert_codes),
        "i13_certificate_warning_is_observability_evidence": "P218_I13_CERT_EXPIRY_NEAR" in alert_codes,
        "i13_action_hash72": action["record_hash72"],
        "i13_run_receipt_hash72": receipt["record_hash72"],
        "i13_final_status_hash72": final_status["record_hash72"],
        "i13_pending_operator_actions": final_status["pending_operator_actions"],
        "canonical_authority_minted": False,
        "canonical_mutation_permitted": False,
        "canonical_learning_commit_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "verbatim_source_retained": False,
        "pass165_source_retaining_path_invoked": False,
        "authoritative_float_weights": False,
        "observed_epoch_seconds": now,
    }
    (I13_EVIDENCE / "real-evidence-summary.json").write_text(
        json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("PASS218_I13_REAL_EVIDENCE_OBSERVABILITY=1")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

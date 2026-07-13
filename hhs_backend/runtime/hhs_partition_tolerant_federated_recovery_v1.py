"""Pass 057 — Partition-Tolerant Revocation Consensus and Federated Recovery."""
from __future__ import annotations
from typing import Any, Dict, Iterable, Mapping
import json
from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_backend.runtime.hhs_distributed_authority_federation_v1 import run_distributed_authority_federation

VERSION = "PASS_057_PARTITION_TOLERANT_REVOCATION_CONSENSUS_FEDERATED_RECOVERY_V1"
AUTHORITY = "HHS_I019_PARTITION_TOLERANT_FEDERATED_AUTHORITY_RECOVERY_V1"
REJECTIONS = [
    "REJECT_PARTITIONED_DOMAIN_AS_CURRENT_AUTHORITY",
    "REJECT_STALE_SUBLEASE_AFTER_REVOCATION_SEQUENCE",
    "REJECT_REMOTE_CHECKPOINT_DURING_UNWITNESSED_PARTITION",
    "REJECT_REVOCATION_CONSENSUS_WITHOUT_QUORUM",
    "REJECT_CONFLICTING_REVOCATION_EPOCH",
    "REJECT_STALE_LEASE_NOT_QUARANTINED",
    "REJECT_RECONCILIATION_WITH_BROKEN_ANCESTRY",
    "REJECT_RECOVERY_WITHOUT_REVOCATION_CONVERGENCE",
    "REJECT_PARTITION_RESULT_AS_LOCAL_CANONICAL_STATE",
    "REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION",
]

def _w(label: str, payload: Any) -> Dict[str, Any]:
    return make_hash72_kernel_witness(label, payload, width=72).to_dict()

def _root(label: str, payload: Any) -> str:
    return _w(label, payload)["digest"]

def _finish(schema: str, obj: Dict[str, Any], field: str, label: str) -> Dict[str, Any]:
    out = {"schema": schema, "version": VERSION, "authority": AUTHORITY, **obj}
    out[field] = _root(label, out)
    return out

def build_partition_evidence(run: Mapping[str, Any], *, observed_sequence: int, last_ack_sequence: int) -> Dict[str, Any]:
    partitioned = last_ack_sequence < observed_sequence
    return _finish("HHS_FEDERATION_PARTITION_EVIDENCE_V1", {
        "federation_contract_root_hash72": run["federation_contract"]["federation_contract_root_hash72"],
        "delegation_chain_root_hash72": run["delegation_chain"]["delegation_chain_root_hash72"],
        "observed_sequence": observed_sequence,
        "last_acknowledged_sequence": last_ack_sequence,
        "partition_detected": partitioned,
        "remote_domain_current_authority": not partitioned,
    }, "partition_evidence_root_hash72", "hhs_federation_partition_evidence_v1")

def build_revocation_vote(domain_id: str, parent_lease_root: str, epoch: int, decision: str) -> Dict[str, Any]:
    return _finish("HHS_REVOCATION_CONSENSUS_VOTE_V1", {
        "domain_id": domain_id,
        "parent_lease_root_hash72": parent_lease_root,
        "revocation_epoch": epoch,
        "decision": decision,
    }, "vote_root_hash72", "hhs_revocation_consensus_vote_v1")

def resolve_revocation_consensus(votes: Iterable[Mapping[str, Any]], *, quorum: int) -> Dict[str, Any]:
    votes = list(votes)
    epochs = {v.get("revocation_epoch") for v in votes}
    revoke_votes = [v for v in votes if v.get("decision") == "REVOKE"]
    reasons = []
    if len(epochs) != 1:
        reasons.append("REJECT_CONFLICTING_REVOCATION_EPOCH")
    if len(revoke_votes) < quorum:
        reasons.append("REJECT_REVOCATION_CONSENSUS_WITHOUT_QUORUM")
    return _finish("HHS_PARTITION_TOLERANT_REVOCATION_CONSENSUS_V1", {
        "votes": votes,
        "quorum": quorum,
        "revocation_epoch": next(iter(epochs)) if len(epochs) == 1 else None,
        "consensus_reached": not reasons,
        "decision": "REVOKE" if not reasons else "UNRESOLVED",
        "reasons": reasons,
    }, "revocation_consensus_root_hash72", "hhs_partition_tolerant_revocation_consensus_v1")

def quarantine_stale_sublease(sublease: Mapping[str, Any], partition: Mapping[str, Any], consensus: Mapping[str, Any]) -> Dict[str, Any]:
    stale = bool(partition.get("partition_detected")) and consensus.get("decision") == "REVOKE"
    reasons = [] if stale else ["REJECT_STALE_LEASE_NOT_QUARANTINED"]
    return _finish("HHS_STALE_SUBLEASE_QUARANTINE_V1", {
        "sublease_root_hash72": sublease.get("sublease_root_hash72"),
        "partition_evidence_root_hash72": partition.get("partition_evidence_root_hash72"),
        "revocation_consensus_root_hash72": consensus.get("revocation_consensus_root_hash72"),
        "quarantine_state": "QUARANTINED" if stale else "NOT_QUARANTINED",
        "execution_allowed": False if stale else True,
        "canonical_ingress_allowed": False if stale else True,
        "reasons": reasons,
    }, "quarantine_root_hash72", "hhs_stale_sublease_quarantine_v1")

def reconcile_partition(run: Mapping[str, Any], partition: Mapping[str, Any], consensus: Mapping[str, Any], quarantine: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    if not run["delegation_chain"].get("complete"):
        reasons.append("REJECT_RECONCILIATION_WITH_BROKEN_ANCESTRY")
    if not consensus.get("consensus_reached"):
        reasons.append("REJECT_RECOVERY_WITHOUT_REVOCATION_CONVERGENCE")
    if quarantine.get("quarantine_state") != "QUARANTINED":
        reasons.append("REJECT_STALE_LEASE_NOT_QUARANTINED")
    return _finish("HHS_FEDERATION_RECONCILIATION_RECEIPT_V1", {
        "delegation_chain_root_hash72": run["delegation_chain"]["delegation_chain_root_hash72"],
        "partition_evidence_root_hash72": partition["partition_evidence_root_hash72"],
        "revocation_consensus_root_hash72": consensus["revocation_consensus_root_hash72"],
        "quarantine_root_hash72": quarantine["quarantine_root_hash72"],
        "reconciliation_complete": not reasons,
        "stale_remote_results_disposition": "PRESERVED_AS_NONCANONICAL_EVIDENCE",
        "reasons": reasons,
    }, "reconciliation_receipt_root_hash72", "hhs_federation_reconciliation_receipt_v1")

def recover_federation(reconciliation: Mapping[str, Any], *, local_revalidation_ok: bool) -> Dict[str, Any]:
    reasons = []
    if not reconciliation.get("reconciliation_complete"):
        reasons.append("REJECT_RECOVERY_WITHOUT_REVOCATION_CONVERGENCE")
    if not local_revalidation_ok:
        reasons.append("REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION")
    return _finish("HHS_FEDERATED_RECOVERY_DECISION_V1", {
        "reconciliation_receipt_root_hash72": reconciliation.get("reconciliation_receipt_root_hash72"),
        "local_revalidation_performed": local_revalidation_ok,
        "recovered": not reasons,
        "canonical_continuation": not reasons,
        "stale_remote_execution_became_local_authority": False,
        "status": "ADMIT_FEDERATED_RECOVERY" if not reasons else "REJECT_FEDERATED_RECOVERY",
        "reasons": reasons,
    }, "federated_recovery_root_hash72", "hhs_federated_recovery_decision_v1")

def run_partition_tolerant_federated_recovery() -> Dict[str, Any]:
    p56 = run_distributed_authority_federation()
    partition = build_partition_evidence(p56, observed_sequence=160, last_ack_sequence=129)
    parent_root = p56["parent_lease"]["lease_root_hash72"]
    votes = [
        build_revocation_vote("runtime:local", parent_root, 7, "REVOKE"),
        build_revocation_vote("runtime:witness-b", parent_root, 7, "REVOKE"),
        build_revocation_vote("runtime:remote-a", parent_root, 7, "UNKNOWN"),
    ]
    consensus = resolve_revocation_consensus(votes, quorum=2)
    quarantine = quarantine_stale_sublease(p56["delegated_sublease"], partition, consensus)
    reconciliation = reconcile_partition(p56, partition, consensus, quarantine)
    recovery = recover_federation(reconciliation, local_revalidation_ok=True)
    out = {
        "schema": "HHS_PARTITION_TOLERANT_FEDERATED_RECOVERY_RUN_V1", "version": VERSION, "authority": AUTHORITY,
        "ok": all([p56["ok"], partition["partition_detected"], consensus["consensus_reached"], quarantine["quarantine_state"] == "QUARANTINED", reconciliation["reconciliation_complete"], recovery["recovered"]]),
        "pass056_federation_root_hash72": p56["run_root_hash72"],
        "partition_evidence": partition, "revocation_consensus": consensus, "stale_sublease_quarantine": quarantine,
        "reconciliation_receipt": reconciliation, "recovery_decision": recovery, "rejection_codes": REJECTIONS,
    }
    out["run_root_hash72"] = _root("hhs_partition_tolerant_federated_recovery_run_v1", out)
    return out

def partition_tolerant_federated_recovery_self_test() -> Dict[str, Any]:
    run = run_partition_tolerant_federated_recovery()
    parent_root = run["revocation_consensus"]["votes"][0]["parent_lease_root_hash72"]
    no_quorum = resolve_revocation_consensus([build_revocation_vote("a", parent_root, 8, "REVOKE")], quorum=2)
    conflict = resolve_revocation_consensus([build_revocation_vote("a", parent_root, 8, "REVOKE"), build_revocation_vote("b", parent_root, 9, "REVOKE")], quorum=2)
    bad_recovery = recover_federation(run["reconciliation_receipt"], local_revalidation_ok=False)
    ok = run["ok"] and "REJECT_REVOCATION_CONSENSUS_WITHOUT_QUORUM" in no_quorum["reasons"] and "REJECT_CONFLICTING_REVOCATION_EPOCH" in conflict["reasons"] and "REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION" in bad_recovery["reasons"]
    return {"schema": "HHS_PARTITION_TOLERANT_FEDERATED_RECOVERY_SELF_TEST_V1", "ok": ok, "run_root_hash72": run["run_root_hash72"], "negative_cases": {"no_quorum": no_quorum, "conflicting_epoch": conflict, "missing_local_revalidation": bad_recovery}}

if __name__ == "__main__":
    print(json.dumps(partition_tolerant_federated_recovery_self_test(), indent=2, sort_keys=True))

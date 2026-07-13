from hhs_backend.runtime.hhs_partition_tolerant_federated_recovery_v1 import run_partition_tolerant_federated_recovery, partition_tolerant_federated_recovery_self_test

def test_positive_partition_recovery_chain():
    r = run_partition_tolerant_federated_recovery()
    assert r["ok"]
    assert r["partition_evidence"]["partition_detected"] is True
    assert r["revocation_consensus"]["consensus_reached"] is True
    assert r["stale_sublease_quarantine"]["execution_allowed"] is False
    assert r["recovery_decision"]["canonical_continuation"] is True
    assert r["recovery_decision"]["stale_remote_execution_became_local_authority"] is False

def test_negative_consensus_and_revalidation_cases():
    r = partition_tolerant_federated_recovery_self_test()
    assert r["ok"]
    assert "REJECT_REVOCATION_CONSENSUS_WITHOUT_QUORUM" in r["negative_cases"]["no_quorum"]["reasons"]
    assert "REJECT_CONFLICTING_REVOCATION_EPOCH" in r["negative_cases"]["conflicting_epoch"]["reasons"]
    assert "REJECT_RECOVERY_WITHOUT_LOCAL_REVALIDATION" in r["negative_cases"]["missing_local_revalidation"]["reasons"]

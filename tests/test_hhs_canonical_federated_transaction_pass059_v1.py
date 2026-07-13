from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import canonical_federated_transaction_commit_self_test, run_canonical_federated_transaction_commit

def test_pass059_transaction_self_test():
    assert canonical_federated_transaction_commit_self_test()["ok"]

def test_pass059_canonical_commit():
    run=run_canonical_federated_transaction_commit()
    assert run["ok"]
    assert run["transaction_decision"]["canonical_continuation"]
    assert not run["transaction_decision"]["successful_participant_confers_global_authority"]

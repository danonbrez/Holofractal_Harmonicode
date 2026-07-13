from hhs_backend.runtime.hhs_distributed_authority_federation_v1 import run_distributed_authority_federation,distributed_authority_federation_self_test

def test_pass056_positive_federation_chain():
    r=run_distributed_authority_federation(); assert r["ok"]; assert r["delegated_sublease"]["authority_amplified"] is False; assert r["remote_execution_receipt"]["remote_result_is_local_authority"] is False; assert r["federated_ingress"]["canonical_continuation"] is True

def test_pass056_negative_cases_and_revocation():
    r=distributed_authority_federation_self_test(); assert r["ok"]; assert r["revocation_propagation"]["propagation_complete"] is True

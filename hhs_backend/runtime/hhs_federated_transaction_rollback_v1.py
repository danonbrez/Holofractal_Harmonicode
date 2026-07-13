"""Pass 059 service surface: hhs_federated_transaction_rollback_v1."""
from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import decide_rollback

def federated_transaction_rollback_v1_self_test():
    from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import canonical_federated_transaction_commit_self_test
    return canonical_federated_transaction_commit_self_test()

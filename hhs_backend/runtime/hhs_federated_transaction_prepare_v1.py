"""Pass 059 service surface: hhs_federated_transaction_prepare_v1."""
from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import build_prepare_record

def federated_transaction_prepare_v1_self_test():
    from hhs_backend.runtime.hhs_canonical_federated_transaction_commit_v1 import canonical_federated_transaction_commit_self_test
    return canonical_federated_transaction_commit_self_test()

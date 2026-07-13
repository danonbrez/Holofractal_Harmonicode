"""Pass 058 service surface: hhs_conflict_preserving_merge_policy_v1."""
from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import build_merge_policy

def conflict_preserving_merge_policy_v1_self_test():
    from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import canonical_federated_state_reconciliation_self_test
    return canonical_federated_state_reconciliation_self_test()

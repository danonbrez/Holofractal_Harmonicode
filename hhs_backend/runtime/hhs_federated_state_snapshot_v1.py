"""Pass 058 service surface: hhs_federated_state_snapshot_v1."""
from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import build_federated_state_snapshot

def federated_state_snapshot_v1_self_test():
    from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import canonical_federated_state_reconciliation_self_test
    return canonical_federated_state_reconciliation_self_test()

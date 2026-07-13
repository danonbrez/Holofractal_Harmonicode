"""Pass 060 specialized recovery surface."""
from hhs_backend.runtime.hhs_federated_transaction_recovery_v1 import *

def self_test():
    return federated_transaction_recovery_self_test()

SERVICE_NAME = "transaction_replay_receipt.self_test"
if __name__ == "__main__":
    import json; print(json.dumps(self_test(), indent=2, sort_keys=True))

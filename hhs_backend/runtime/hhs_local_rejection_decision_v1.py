"""Pass 061 specialized bounded rejection surface."""
from hhs_backend.runtime.hhs_bounded_rejection_authority_v1 import *
def self_test(): return bounded_rejection_authority_self_test()
SERVICE_NAME = "local_rejection_decision_v1.self_test"
if __name__ == "__main__":
 import json; print(json.dumps(self_test(), indent=2, sort_keys=True))

"""Pass 055 specialized Runtime surface."""
from hhs_backend.runtime.hhs_authority_enforced_dispatch_v1 import authority_enforced_dispatch_self_test
def capability_lease_registry_self_test():
    base=authority_enforced_dispatch_self_test(); return {"schema":"HHS_CAPABILITY_LEASE_REGISTRY_SELF_TEST_V1","ok":base["ok"],"run_root_hash72":base["run_root_hash72"]}
if __name__=="__main__":
 import json; print(json.dumps(capability_lease_registry_self_test(),indent=2,sort_keys=True))

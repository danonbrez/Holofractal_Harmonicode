from hhs_backend.runtime.hhs_authority_enforced_dispatch_v1 import run_authority_enforced_dispatch
def test_lease_is_task_bound_and_non_delegable():
 l=run_authority_enforced_dispatch()["lease"]; assert l["revocable"] is True; assert l["delegable"] is False; assert l["mutation_authority"]=="EXPLICIT_ONLY"
def test_lease_lifecycle_consumes_authority():
 r=run_authority_enforced_dispatch(); assert r["active_lease"]["lease_state"]=="ACTIVE"; assert r["consumed_lease"]["lease_state"]=="CONSUMED"

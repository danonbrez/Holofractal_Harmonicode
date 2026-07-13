from hhs_backend.runtime.hhs_bounded_rejection_authority_v1 import bounded_rejection_authority_self_test, run_bounded_rejection_authority

def test_pass061_self_test(): assert bounded_rejection_authority_self_test()["ok"]
def test_pass061_local_proportionate_release():
 r=run_bounded_rejection_authority(); assert r["ok"]; assert not r["rejection_decision"]["global_effect"]; assert r["propagation"]["propagation_minimal"]; assert r["release_decision"]["rejection_released"]

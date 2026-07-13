from hhs_backend.runtime.hhs_federated_transaction_recovery_v1 import federated_transaction_recovery_self_test, run_federated_transaction_recovery

def test_pass060_recovery_self_test(): assert federated_transaction_recovery_self_test()["ok"]
def test_pass060_exactly_once_admission():
 r=run_federated_transaction_recovery(); assert r["ok"]; assert r["canonical_admission"]["exactly_once_admitted"]; assert all(x["duplicate_effect_suppressed"] for x in r["replay_decisions"])

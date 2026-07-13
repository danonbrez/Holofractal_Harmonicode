from hhs_backend.runtime.hhs_partition_tolerant_federated_recovery_v1 import partition_tolerant_federated_recovery_self_test

def federation_partition_evidence_v1_self_test():
    base = partition_tolerant_federated_recovery_self_test()
    return {"schema": "HHS_FEDERATION_PARTITION_EVIDENCE_V1_SELF_TEST_V1", "ok": base["ok"], "run_root_hash72": base["run_root_hash72"]}

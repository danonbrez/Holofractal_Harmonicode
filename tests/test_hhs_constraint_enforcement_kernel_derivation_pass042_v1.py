from hhs_runtime.hhs_runtime_constraint_enforcement_binding_v1 import enforce_runtime_constraint_boundary


def test_constraint_enforcement_rejects_underived_operation():
    decision = enforce_runtime_constraint_boundary(surface="external.underived", request_class="canonical_full_witness_chain")
    assert decision["status"] == "REJECT_OPERATION_NOT_DERIVED_FROM_KERNEL_INVARIANT"
    assert decision["propagation_allowed"] is False


def test_constraint_enforcement_admits_derived_runtime_surface():
    decision = enforce_runtime_constraint_boundary(surface="service_registry.dispatch", request_class="canonical_full_witness_chain")
    assert decision["admitted"] is True
    assert decision["propagation_allowed"] is True

import pytest
from hhs_runtime.hhs_pass106_hash72_capability_truth_v1 import (
    CapabilityAdmissionError,
    CapabilityClaim,
    Hash72CapabilityLedger,
    execute_production_workload,
    pass106_self_test,
)


@pytest.fixture(scope="module")
def pass106_result():
    return pass106_self_test()


def test_pass106_real_native_and_derived_admissions(pass106_result):
    result = pass106_result
    assert result["status"] == "PASS"
    assert result["native_verified_count"] == 2
    assert result["derived_verified_count"] == 1
    assert result["placeholder_capabilities_admitted"] == 0
    assert result["mock_evidence_admitted"] == 0
    assert result["parallel_test_computation_used"] is False


def test_pass106_uses_real_pass105_6_production_workload(pass106_result):
    admission = pass106_result["native_capability_admissions"][0]
    assert admission["implementation_class"] == "NATIVE_VERIFIED"
    assert admission["positive_workload_receipt_roots"]
    # The admission is created only after the real Pass 105.6 compile-and-run workload succeeds.
    assert admission["status"] == "CANONICAL_EXECUTABLE"


def test_pass106_missing_implementation_rejected():
    ledger = Hash72CapabilityLedger()
    claim = CapabilityClaim("missing", "NATIVE_VERIFIED", module="does.not.exist", function="x")
    with pytest.raises(CapabilityAdmissionError) as exc:
        ledger.admit_native(claim, positive_evidence={}, negative_evidence_roots=[], reachability_root_hash72="r", conformance_root_hash72="c")
    assert exc.value.code == "REJECT_CLAIM_WITHOUT_IMPLEMENTATION"


def test_pass106_rejected_probes_are_observed_from_real_admission_logic(pass106_result):
    observed = {x["probe"]: x["observed"] for x in pass106_result["rejected_probes"]}
    assert observed == {
        "missing_implementation": "REJECT_CLAIM_WITHOUT_IMPLEMENTATION",
        "open_repair_obligation": "REJECT_OPEN_REPAIR_OBLIGATION",
        "mock_evidence": "REJECT_MOCK_KERNEL_AS_PRODUCTION_EVIDENCE",
    }


def test_pass106_invocation_roots_bind_current_implementation(pass106_result):
    receipts = pass106_result["invocation_receipts"]
    assert len(receipts) == 3
    assert all(x["status"] == "ADMITTED_FOR_PRODUCTION_INVOCATION" for x in receipts)
    assert len({x["capability_admission_root_hash72"] for x in receipts}) == 3


def test_pass106_ledger_is_append_only_and_rooted(pass106_result):
    ledger = pass106_result["capability_ledger"]
    assert ledger["event_count"] == 3
    assert ledger["ledger_root_hash72"]
    previous = None
    for event in ledger["events"]:
        assert event["previous_event_root_hash72"] == previous
        previous = event["event_root_hash72"]


def test_pass106_service_registered_and_conformance_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.capability_truth_admission.pass106")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "zero_bypass_runtime_interposer" in service["guards"]

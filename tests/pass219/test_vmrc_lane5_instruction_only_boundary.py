from __future__ import annotations

import pytest

from hhs_runtime.pass163.vmrc import CandidateTransition, VMRCError, VMRCRuntime
from hhs_runtime.pass219.lane5_instruction import (
    TARGET_VM81,
    bind_rna_cell_wall,
    bind_signed_pqc_admission,
    lower_object_to_lane5_instruction,
)
from hhs_runtime.pass219.lane5_interceptor_sandbox_cache import (
    reset_default_sandbox_for_tests,
)


@pytest.fixture(autouse=True)
def _reset_sandbox() -> None:
    reset_default_sandbox_for_tests()


def _candidate(runtime: VMRCRuntime) -> CandidateTransition:
    return runtime.submit_candidate(
        thread=0,
        writes={0: 1},
        operation="VMRC_COMMIT",
        expected_input_hash72=runtime.state_hash72,
        dependency_root="lane5-test-root",
        capability_scope="LANE5_TEST_VMRC_COMMIT",
    )


def test_raw_vmrc_candidate_is_blocked_and_redirected_to_lane5_queue() -> None:
    runtime = VMRCRuntime()
    candidate = _candidate(runtime)

    with pytest.raises(VMRCError) as captured:
        runtime.execute(candidate)

    assert captured.value.classification == "VMRC_LANE5_REDIRECT_REQUIRED"
    assert captured.value.detail
    assert runtime.epoch == 0


def test_raw_vmrc_validation_is_also_redirected() -> None:
    runtime = VMRCRuntime()
    candidate = _candidate(runtime)

    with pytest.raises(VMRCError) as captured:
        runtime.validate(candidate)

    assert captured.value.classification == "VMRC_LANE5_REDIRECT_REQUIRED"
    assert runtime.epoch == 0


def test_raw_commit_identifier_cannot_cross_vm81_gateway() -> None:
    runtime = VMRCRuntime()
    candidate = _candidate(runtime)

    with pytest.raises(VMRCError) as captured:
        runtime.commit(candidate.candidate_id)

    assert captured.value.classification == "VMRC_LANE5_PQC_INSTRUCTION_REQUIRED"
    assert runtime.epoch == 0


def test_vmrc_executes_only_pqc_admitted_lane5_instruction() -> None:
    runtime = VMRCRuntime()
    candidate = _candidate(runtime)

    instruction = lower_object_to_lane5_instruction(
        candidate,
        target=TARGET_VM81,
        traffic_class="vmrc.compatibility",
        operation=candidate.operation,
        dependency_root=candidate.dependency_root,
        metadata={
            "candidate_id": candidate.candidate_id,
            "expected_input_hash72": candidate.expected_input_hash72,
        },
    )

    # Unit-test receipts model the already-validated downstream evidence.
    # Production must bind receipts from the native C++ RNA/PQC path.
    instruction = bind_rna_cell_wall(
        instruction,
        rna_receipt={
            "rna_cpp_cell_wall_routed": True,
            "candidate_only": True,
        },
    )
    instruction = bind_signed_pqc_admission(
        instruction,
        pqc_receipt={
            "signed_environmental_admission": True,
            "pqc_authenticated": True,
            "decision": "ADMIT",
            "singleton_vm81_authority": True,
        },
    )

    result = runtime.execute(instruction)
    assert runtime.epoch == 1
    assert result["validation"]["validated"]["vm81_admission"] == (
        "LANE5_VALIDATED_PENDING_PQC_COMMIT"
    )
    assert result["commit"]["classification"] == "HHS_PASS_163_COMMIT_ADMITTED"

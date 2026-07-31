from __future__ import annotations

from typing import Any

import pytest

from hhs_runtime.pass174 import (
    PASS175_AUTHORITY_OPERATIONS,
    Pass174Error,
    Pass174Runtime,
    Pass175AuthorityAdapter,
)
from hhs_runtime.pass175 import InstructionRequest, Pass175Error, Pass175Runtime


def _exercise_genuine_authority() -> dict[str, Any]:
    runtime = Pass175Runtime()
    assert isinstance(runtime.authority, Pass175AuthorityAdapter)

    hydration = runtime.cold_hydrate_bootstrap(seal=True)
    hydration_authority = hydration["authority_result"]
    assert hydration_authority["classification"] == "HHS_PASS_174_PASS175_OPERATION_COMMITTED"
    assert hydration_authority["pass175_operation"] == "P175_COLD_HYDRATION_SEAL"
    assert hydration_authority["vmrc_operation_class"] == "VMRC_COMMIT"
    assert hydration_authority["receipt"]["schema"] == "P174_PASS175_AUTHORITY_ADAPTER_RECEIPT"
    assert hydration_authority["receipt"]["pass175_operation"] == "P175_COLD_HYDRATION_SEAL"

    execution = runtime.execute_batch(
        [
            InstructionRequest(
                exact_bytes=b"\x90",
                sequence=0,
                thread_id=1,
                explicit_delta=((1, 1),),
            ),
            InstructionRequest(
                exact_bytes=b"\x31\xC0",
                sequence=1,
                thread_id=2,
                explicit_delta=((2, -1),),
            ),
            InstructionRequest(
                exact_bytes=b"\x0F\xA2",
                sequence=2,
                thread_id=3,
                explicit_delta=((3, 1),),
            ),
        ],
        max_workers=3,
    )
    authority_result = execution["waves"][0]["authority_result"]
    assert authority_result["classification"] == "HHS_PASS_174_PASS175_OPERATION_COMMITTED"
    assert authority_result["pass175_operation"] == "P175_PARALLEL_CANDIDATE_BATCH_COMMIT"
    assert authority_result["vmrc_operation_class"] == "VMRC_COMMIT"
    assert authority_result["receipt"]["pass175_operation"] == "P175_PARALLEL_CANDIDATE_BATCH_COMMIT"
    assert runtime.authority.vmrc.epoch == 2

    replay = runtime.replay()
    assert replay["authority_replay"]["classification"] == "HHS_PASS_174_REPLAY_CLOSED"
    assert replay["authority_replay"]["inherited_vmrc_replay"]["deterministic_replay"] is True
    assert replay["authority_replay"]["receipt_chain_valid"] is True

    return {
        "hydration_store_root": hydration["microcode_store_root_sha256"],
        "hydration_receipt": hydration_authority["receipt"]["receipt_sha256"],
        "candidate_root": execution["waves"][0]["candidate_root_sha256"],
        "execution_receipt": authority_result["receipt"]["receipt_sha256"],
        "commit_chain_root": replay["commit_chain_root_sha256"],
        "authority_receipt_root": replay["authority_replay"]["final_receipt_sha256"],
        "authority_state_hash72": runtime.authority.vmrc.state_hash72,
    }


def test_genuine_pass174_authority_hydration_execution_and_replay() -> None:
    result = _exercise_genuine_authority()
    assert all(result.values())


def test_genuine_authority_is_cross_instance_deterministic() -> None:
    assert _exercise_genuine_authority() == _exercise_genuine_authority()


def test_adapter_surface_is_explicit_and_unknown_pass175_operations_fail_closed() -> None:
    assert set(PASS175_AUTHORITY_OPERATIONS) == {
        "P175_COLD_HYDRATION_SEAL",
        "P175_WARM_HYDRATION_SEAL",
        "P175_PARALLEL_CANDIDATE_BATCH_COMMIT",
        "P175_X86_64_INGRESS_COMMIT",
        "P175_PRIVILEGED_TRAP_RECEIPT",
        "P175_DEVICE_EVENT_RECEIPT",
        "P175_DETERMINISTIC_REPLAY_RECEIPT",
    }
    authority = Pass174Runtime()
    before = (
        authority.vmrc.epoch,
        authority.vmrc.state_hash72,
        len(authority.state.receipts),
    )
    with pytest.raises(Pass174Error) as captured:
        authority.execute(
            thread=0,
            writes={},
            operation="P175_UNKNOWN_OPERATION",
            capability_scope="P175_UNKNOWN_SCOPE",
        )
    assert captured.value.classification == "HHS_P174_UNSUPPORTED_PASS175_OPERATION"
    assert before == (
        authority.vmrc.epoch,
        authority.vmrc.state_hash72,
        len(authority.state.receipts),
    )


def test_privileged_trap_has_zero_authority_mutation() -> None:
    runtime = Pass175Runtime()
    authority = runtime.authority
    before = (
        authority.vmrc.epoch,
        authority.vmrc.state_hash72,
        len(authority.state.receipts),
    )
    with pytest.raises(Pass175Error) as captured:
        runtime.execute_batch([InstructionRequest(exact_bytes=b"\xF4")])
    assert captured.value.classification == "HHS_P175_PRIVILEGED_INSTRUCTION_TRAPPED"
    assert before == (
        authority.vmrc.epoch,
        authority.vmrc.state_hash72,
        len(authority.state.receipts),
    )

    witness = authority.execute(
        thread=0,
        writes={},
        operation="P175_PRIVILEGED_TRAP_RECEIPT",
        capability_scope="P175_PRIVILEGED_TRAP",
    )
    assert witness["mutation_authority"] is False
    assert witness["admitted"] is False
    assert witness["receipt"]["receipt_chain_mutated"] is False
    assert before == (
        authority.vmrc.epoch,
        authority.vmrc.state_hash72,
        len(authority.state.receipts),
    )


def test_pass175_capability_scope_is_fail_closed() -> None:
    authority = Pass174Runtime()
    with pytest.raises(Pass174Error) as captured:
        authority.execute(
            thread=0,
            writes={},
            operation="P175_COLD_HYDRATION_SEAL",
            capability_scope="P175_WRONG_SCOPE",
        )
    assert captured.value.classification == "HHS_P174_PASS175_CAPABILITY_SCOPE_MISMATCH"

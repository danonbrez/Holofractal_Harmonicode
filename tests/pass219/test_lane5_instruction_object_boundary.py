from __future__ import annotations

from dataclasses import dataclass

import pytest

from hhs_runtime.pass219.lane5_instruction import (
    Lane5InstructionError,
    STATE_OBSERVATION_ADMITTED,
    STATE_PQC_ADMITTED,
    STATE_QUEUED_OPTIMIZED,
    TARGET_LINUX,
    TARGET_VM81,
    bind_rna_cell_wall,
    bind_signed_pqc_admission,
    execute_linux_instruction,
    execute_vm81_instruction,
    lower_object_to_lane5_instruction,
    require_lane5_instruction,
)
from hhs_runtime.pass219.lane5_interceptor_sandbox_cache import (
    reset_default_sandbox_for_tests,
)


@dataclass(frozen=True)
class DemoObject:
    name: str
    value: int


@pytest.fixture(autouse=True)
def _reset_sandbox() -> None:
    reset_default_sandbox_for_tests()


def test_arbitrary_object_lowers_to_lane5_instruction() -> None:
    source = DemoObject("alpha", 7)
    instruction = lower_object_to_lane5_instruction(
        source,
        target=TARGET_VM81,
        traffic_class="runtime.abi",
        operation="demo_commit",
        dependency_root="demo-root",
    )
    assert instruction.source_object_payload is source
    assert instruction.source_object_type == "DemoObject"
    assert instruction.state_affecting is True
    assert instruction.lane5_state == STATE_QUEUED_OPTIMIZED
    assert instruction.sandbox_queue_optimized is True
    assert instruction.mandatory_optimization_dispatch is True
    assert instruction.canonical_mutation_authority is False
    assert instruction.direct_fallback_allowed is False


def test_vm81_gateway_rejects_raw_object() -> None:
    with pytest.raises(Lane5InstructionError, match="LANE5_INSTRUCTION_REQUIRED"):
        require_lane5_instruction(
            DemoObject("raw", 1),
            expected_target=TARGET_VM81,
        )


def test_vm81_instruction_requires_rna_and_signed_pqc() -> None:
    source = DemoObject("vm81", 2)
    instruction = lower_object_to_lane5_instruction(
        source,
        target=TARGET_VM81,
        traffic_class="vmrc.compatibility",
        operation="canonical_commit",
    )
    with pytest.raises(
        Lane5InstructionError,
        match="LANE5_PQC_ADMITTED_INSTRUCTION_REQUIRED",
    ):
        execute_vm81_instruction(instruction, lambda obj: obj)

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
    assert instruction.lane5_state == STATE_PQC_ADMITTED
    assert execute_vm81_instruction(instruction, lambda obj: obj) is source


def test_linux_gateway_accepts_only_lane5_instruction() -> None:
    with pytest.raises(Lane5InstructionError, match="LANE5_INSTRUCTION_REQUIRED"):
        execute_linux_instruction(
            DemoObject("raw-linux", 3),  # type: ignore[arg-type]
            lambda obj: obj,
        )


def test_linux_read_only_instruction_needs_no_mutation_authority() -> None:
    source = {"path": "/proc/self/status"}
    instruction = lower_object_to_lane5_instruction(
        source,
        target=TARGET_LINUX,
        traffic_class="linux.file.io",
        operation="read",
        read_only=True,
    )
    assert instruction.lane5_state == STATE_OBSERVATION_ADMITTED
    assert instruction.canonical_mutation_authority is False
    assert instruction.pqc_authenticated is False
    result = execute_linux_instruction(instruction, lambda obj: dict(obj))
    assert result == source


def test_state_affecting_linux_instruction_requires_signed_pqc() -> None:
    source = {"argv": ["worker", "--run"]}
    instruction = lower_object_to_lane5_instruction(
        source,
        target=TARGET_LINUX,
        traffic_class="native.subprocess",
        operation="spawn",
    )
    with pytest.raises(
        Lane5InstructionError,
        match="LANE5_PQC_ADMITTED_INSTRUCTION_REQUIRED",
    ):
        execute_linux_instruction(instruction, lambda obj: obj)

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
            "singleton_vm81_authority": False,
        },
    )
    assert execute_linux_instruction(instruction, lambda obj: obj) == source


def test_target_mismatch_fails_closed() -> None:
    instruction = lower_object_to_lane5_instruction(
        DemoObject("mismatch", 9),
        target=TARGET_LINUX,
        traffic_class="linux.kernel.abi",
        operation="noop",
        read_only=True,
    )
    with pytest.raises(Lane5InstructionError, match="TARGET_MISMATCH"):
        require_lane5_instruction(
            instruction,
            expected_target=TARGET_VM81,
        )

from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.pass219.lane5_instruction import (
    TARGET_LINUX,
    bind_rna_cell_wall,
    bind_signed_pqc_admission,
    lower_object_to_lane5_instruction,
)
from hhs_runtime.pass219.lane5_interceptor_sandbox_cache import (
    reset_default_sandbox_for_tests,
)
from hhs_runtime.pass219.lane5_linux_host_gateway import (
    Lane5LinuxHostGatewayError,
    LinuxFileReadRequest,
    LinuxFileWriteRequest,
    LinuxSubprocessRequest,
    read_file,
    run_subprocess,
    write_file,
)


@pytest.fixture(autouse=True)
def _reset_sandbox() -> None:
    reset_default_sandbox_for_tests()


def _admit_state_affecting(instruction):
    instruction = bind_rna_cell_wall(
        instruction,
        rna_receipt={
            "rna_cpp_cell_wall_routed": True,
            "candidate_only": True,
        },
    )
    return bind_signed_pqc_admission(
        instruction,
        pqc_receipt={
            "signed_environmental_admission": True,
            "pqc_authenticated": True,
            "decision": "ADMIT",
            "singleton_vm81_authority": False,
        },
    )


def test_linux_gateway_rejects_raw_request() -> None:
    with pytest.raises(Lane5LinuxHostGatewayError, match="LANE5_INSTRUCTION_REQUIRED"):
        read_file(LinuxFileReadRequest("/tmp/x"))  # type: ignore[arg-type]


def test_read_only_file_request_executes_only_after_lane5_lowering(
    tmp_path: Path,
) -> None:
    target = tmp_path / "input.txt"
    target.write_text("lane5", encoding="utf-8")
    request = LinuxFileReadRequest(str(target), max_bytes=32)
    instruction = lower_object_to_lane5_instruction(
        request,
        target=TARGET_LINUX,
        traffic_class="linux.file.io",
        operation="read",
        read_only=True,
    )
    assert read_file(instruction) == b"lane5"


def test_state_affecting_file_write_requires_pqc_admitted_instruction(
    tmp_path: Path,
) -> None:
    target = tmp_path / "output.bin"
    request = LinuxFileWriteRequest(str(target), b"abc")
    instruction = lower_object_to_lane5_instruction(
        request,
        target=TARGET_LINUX,
        traffic_class="linux.file.io",
        operation="write",
        read_only=False,
    )
    with pytest.raises(
        Lane5LinuxHostGatewayError,
        match="LANE5_PQC_ADMITTED_INSTRUCTION_REQUIRED",
    ):
        write_file(instruction)

    admitted = _admit_state_affecting(instruction)
    result = write_file(admitted)
    assert result["bytes_written"] == 3
    assert target.read_bytes() == b"abc"


def test_subprocess_gateway_never_uses_shell() -> None:
    request = LinuxSubprocessRequest(
        argv=("/bin/sh", "-c", "printf lane5"),
        capture_output=True,
    )
    instruction = lower_object_to_lane5_instruction(
        request,
        target=TARGET_LINUX,
        traffic_class="native.subprocess",
        operation="spawn",
        read_only=False,
    )
    result = run_subprocess(_admit_state_affecting(instruction))
    assert result["returncode"] == 0
    assert result["stdout"] == b"lane5"
    assert result["canonical_hhs_mutation_authority"] is False

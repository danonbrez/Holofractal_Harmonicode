"""HHS-controlled Linux host execution gateway.

The gateway accepts only Lane5Instruction objects.  It is the repository-side
host/kernel adapter boundary; unrelated host processes remain out of scope.

No shell execution is provided.  State-affecting operations require a fully
PQC-admitted Lane5Instruction before any host call is made.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
import socket
import subprocess
from typing import Any, Mapping, Sequence

from hhs_runtime.pass219.lane5_instruction import (
    Lane5Instruction,
    Lane5InstructionError,
    TARGET_LINUX,
    execute_linux_instruction,
    require_lane5_instruction,
)


class Lane5LinuxHostGatewayError(RuntimeError):
    pass


@dataclass(frozen=True)
class LinuxSubprocessRequest:
    argv: tuple[str, ...]
    cwd: str | None = None
    env: Mapping[str, str] | None = None
    timeout_seconds: int | None = None
    capture_output: bool = True


@dataclass(frozen=True)
class LinuxFileReadRequest:
    path: str
    max_bytes: int = 1 << 20


@dataclass(frozen=True)
class LinuxFileWriteRequest:
    path: str
    data: bytes
    create_parents: bool = False


@dataclass(frozen=True)
class LinuxSocketConnectRequest:
    host: str
    port: int
    timeout_seconds: int = 5


@dataclass(frozen=True)
class LinuxNativeLibraryRequest:
    path: str


def _require_instruction(
    instruction: Lane5Instruction,
) -> Lane5Instruction:
    try:
        return require_lane5_instruction(
            instruction,
            expected_target=TARGET_LINUX,
            require_executable=True,
        )
    except Lane5InstructionError as exc:
        raise Lane5LinuxHostGatewayError(str(exc)) from exc


def run_subprocess(instruction: Lane5Instruction) -> dict[str, Any]:
    admitted = _require_instruction(instruction)
    request = admitted.source_object_payload
    if not isinstance(request, LinuxSubprocessRequest):
        raise Lane5LinuxHostGatewayError(
            "LANE5_LINUX_SUBPROCESS_REQUEST_REQUIRED"
        )
    if not request.argv or any(
        not isinstance(item, str) or not item for item in request.argv
    ):
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_ARGV_INVALID")
    if request.timeout_seconds is not None and request.timeout_seconds <= 0:
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_TIMEOUT_INVALID")

    completed = subprocess.run(
        list(request.argv),
        cwd=request.cwd,
        env=None if request.env is None else dict(request.env),
        timeout=request.timeout_seconds,
        capture_output=request.capture_output,
        check=False,
        shell=False,
    )
    return {
        "classification": "HHS_PASS219_LANE5_LINUX_SUBPROCESS_EXECUTED",
        "returncode": completed.returncode,
        "stdout": completed.stdout if request.capture_output else None,
        "stderr": completed.stderr if request.capture_output else None,
        "lane5_instruction_sha256": admitted.instruction_sha256,
        "canonical_hhs_mutation_authority": False,
    }


def read_file(instruction: Lane5Instruction) -> bytes:
    admitted = _require_instruction(instruction)
    request = admitted.source_object_payload
    if not isinstance(request, LinuxFileReadRequest):
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_FILE_READ_REQUEST_REQUIRED")
    if request.max_bytes <= 0:
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_FILE_READ_BOUND_INVALID")
    path = Path(request.path)
    data = path.read_bytes()
    if len(data) > request.max_bytes:
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_FILE_READ_BOUND_EXCEEDED")
    return data


def write_file(instruction: Lane5Instruction) -> dict[str, Any]:
    admitted = _require_instruction(instruction)
    request = admitted.source_object_payload
    if not isinstance(request, LinuxFileWriteRequest):
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_FILE_WRITE_REQUEST_REQUIRED")
    path = Path(request.path)
    if request.create_parents:
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(request.data))
    return {
        "classification": "HHS_PASS219_LANE5_LINUX_FILE_WRITE_EXECUTED",
        "path": str(path),
        "bytes_written": len(request.data),
        "lane5_instruction_sha256": admitted.instruction_sha256,
        "canonical_hhs_mutation_authority": False,
    }


def connect_socket(instruction: Lane5Instruction) -> socket.socket:
    admitted = _require_instruction(instruction)
    request = admitted.source_object_payload
    if not isinstance(request, LinuxSocketConnectRequest):
        raise Lane5LinuxHostGatewayError(
            "LANE5_LINUX_SOCKET_CONNECT_REQUEST_REQUIRED"
        )
    if not (1 <= request.port <= 65535):
        raise Lane5LinuxHostGatewayError("LANE5_LINUX_SOCKET_PORT_INVALID")
    sock = socket.create_connection(
        (request.host, request.port),
        timeout=request.timeout_seconds,
    )
    return sock


def load_native_library(instruction: Lane5Instruction) -> ctypes.CDLL:
    admitted = _require_instruction(instruction)
    request = admitted.source_object_payload
    if not isinstance(request, LinuxNativeLibraryRequest):
        raise Lane5LinuxHostGatewayError(
            "LANE5_LINUX_NATIVE_LIBRARY_REQUEST_REQUIRED"
        )
    path = Path(request.path).expanduser().resolve()
    if not path.is_file():
        raise Lane5LinuxHostGatewayError(
            f"LANE5_LINUX_NATIVE_LIBRARY_NOT_FOUND:{path}"
        )
    return ctypes.CDLL(str(path))


__all__ = [
    "Lane5LinuxHostGatewayError",
    "LinuxFileReadRequest",
    "LinuxFileWriteRequest",
    "LinuxNativeLibraryRequest",
    "LinuxSocketConnectRequest",
    "LinuxSubprocessRequest",
    "connect_socket",
    "load_native_library",
    "read_file",
    "run_subprocess",
    "write_file",
]

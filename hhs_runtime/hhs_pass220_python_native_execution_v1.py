"""Pass 220 Python1 native Python integer execution compatibility membrane.

The C11 kernel parses and executes the supported source subset. This Python
module is transport/egress only: it does not parse or evaluate source and does
not call ast, eval, exec, or compile.
"""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from hhs_runtime.pass190.python_compat import (
    PYTHON_COMPAT_SCHEMA,
    PYTHON_COMPAT_VERSION,
)

SCHEMA = "HHS_PASS_220_PYTHON1_NATIVE_BIGINT_EXECUTION_V1"
MAX_DIGITS = 5184
MAX_SOURCE_BYTES = 65536

STATUS_OK = 0
STATUS_ARGUMENT = 1
STATUS_SOURCE_TOO_LARGE = 2
STATUS_SYNTAX = 3
STATUS_NAME = 4
STATUS_BIGINT_OVERFLOW = 5
STATUS_VARIABLE_CAPACITY = 6
STATUS_RESULT_CAPACITY = 7
STATUS_UNSUPPORTED = 8


class HHSPythonNativeExecutionError(RuntimeError):
    pass


class HHSPythonNativeBoundError(OverflowError):
    pass


@dataclass(frozen=True)
class HHSPythonNativeResult:
    schema: str
    source_sha256: str
    result_decimal: str
    projected_python_int: int
    statement_count: int
    execution_authority: str
    host_python_evaluator_used: bool
    pass190_compatibility_schema: str
    pass190_python_version: str

    def as_record(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "source_sha256": self.source_sha256,
            "result_decimal": self.result_decimal,
            "projected_python_int": self.projected_python_int,
            "statement_count": self.statement_count,
            "execution_authority": self.execution_authority,
            "host_python_evaluator_used": self.host_python_evaluator_used,
            "pass190_compatibility_schema": self.pass190_compatibility_schema,
            "pass190_python_version": self.pass190_python_version,
        }


class HHSPythonNativeExecutor:
    def __init__(self, library_path: str | Path):
        self.library_path = str(Path(library_path))
        self._lib = ctypes.CDLL(self.library_path)
        self._lib.hhs_python_native_execution_version.restype = ctypes.c_uint32
        self._lib.hhs_python_native_execute.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self._lib.hhs_python_native_execute.restype = ctypes.c_int
        if int(self._lib.hhs_python_native_execution_version()) != 1:
            raise HHSPythonNativeExecutionError(
                "HHS_PYTHON1_NATIVE_EXECUTION_VERSION_MISMATCH"
            )

    def execute(self, source: str) -> HHSPythonNativeResult:
        if not isinstance(source, str):
            raise TypeError("source must be str")
        encoded = source.encode("utf-8")
        if len(encoded) > MAX_SOURCE_BYTES:
            raise HHSPythonNativeBoundError(
                "source exceeds native Python1 source bound"
            )

        result = ctypes.create_string_buffer(MAX_DIGITS + 2)
        error = ctypes.create_string_buffer(512)
        result_length = ctypes.c_size_t()
        statement_count = ctypes.c_uint32()

        status = int(
            self._lib.hhs_python_native_execute(
                encoded,
                result,
                len(result),
                ctypes.byref(result_length),
                error,
                len(error),
                ctypes.byref(statement_count),
            )
        )
        message = error.value.decode("utf-8", errors="replace")

        if status == STATUS_SYNTAX or status == STATUS_UNSUPPORTED:
            raise SyntaxError(message or "unsupported native Python1 syntax")
        if status == STATUS_NAME:
            raise NameError(message or "name is not defined")
        if status in {
            STATUS_SOURCE_TOO_LARGE,
            STATUS_BIGINT_OVERFLOW,
            STATUS_VARIABLE_CAPACITY,
            STATUS_RESULT_CAPACITY,
        }:
            raise HHSPythonNativeBoundError(
                message or "native Python1 bounded execution limit exceeded"
            )
        if status != STATUS_OK:
            raise HHSPythonNativeExecutionError(
                message or f"HHS_PYTHON1_NATIVE_EXECUTION_FAILED:{status}"
            )

        decimal_text = result.value.decode("ascii")
        if len(decimal_text.lstrip("-")) > MAX_DIGITS:
            raise HHSPythonNativeBoundError(
                "native Python1 returned an oversized BigInt"
            )

        # int(...) is egress materialization only. All parsing, binding,
        # precedence and arithmetic occurred inside the C11 kernel.
        projected = int(decimal_text)
        return HHSPythonNativeResult(
            schema=SCHEMA,
            source_sha256=sha256(encoded).hexdigest(),
            result_decimal=decimal_text,
            projected_python_int=projected,
            statement_count=int(statement_count.value),
            execution_authority="HHS_C11_NATIVE_BIGINT_EXECUTION",
            host_python_evaluator_used=False,
            pass190_compatibility_schema=PYTHON_COMPAT_SCHEMA,
            pass190_python_version=PYTHON_COMPAT_VERSION,
        )


def python1_contract() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "python_external_contract_target": "CPython 3.12",
        "pass190_compatibility_schema": PYTHON_COMPAT_SCHEMA,
        "pass190_python_version": PYTHON_COMPAT_VERSION,
        "native_execution_language": "C11",
        "native_bigint_decimal_digits": MAX_DIGITS,
        "supported_statements": (
            "expression_statement",
            "simple_name_assignment",
        ),
        "supported_expressions": (
            "integer_literal",
            "name_load",
            "parentheses",
            "unary_plus",
            "unary_minus",
            "addition",
            "subtraction",
            "multiplication",
        ),
        "operator_precedence": "PYTHON_COMPATIBLE_FOR_SUPPORTED_SUBSET",
        "host_ast_execution_required": False,
        "host_eval_required": False,
        "host_exec_required": False,
        "host_compile_required": False,
        "host_python_arithmetic_authority": False,
        "cpython_differential_test_only": True,
        "numpy1_bridge_next": True,
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }


def python1_self_test(library_path: str | Path) -> dict[str, Any]:
    executor = HHSPythonNativeExecutor(library_path)
    result = executor.execute(
        "a=999999999999999999999999999999\n"
        "b=888888888888888888888888888888\n"
        "a*b"
    )
    expected = (
        "888888888888888888888888888887"
        "111111111111111111111111111112"
    )
    if result.result_decimal != expected:
        raise HHSPythonNativeExecutionError(
            "HHS_PYTHON1_SELF_TEST_BIGINT_MISMATCH"
        )
    rejected = False
    try:
        executor.execute("__import__('os')")
    except (SyntaxError, NameError):
        rejected = True
    if not rejected:
        raise HHSPythonNativeExecutionError(
            "HHS_PYTHON1_SELF_TEST_HOST_ESCAPE_NOT_REJECTED"
        )
    record = {
        "schema": "HHS_PASS_220_PYTHON1_NATIVE_BIGINT_EXECUTION_SELF_TEST_V1",
        "status": "PASS",
        "result_decimal": result.result_decimal,
        "statement_count": result.statement_count,
        "host_escape_rejected": True,
        "host_python_evaluator_used": False,
    }
    record["receipt_sha256"] = sha256(
        json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return record


__all__ = [
    "HHSPythonNativeBoundError",
    "HHSPythonNativeExecutionError",
    "HHSPythonNativeExecutor",
    "HHSPythonNativeResult",
    "python1_contract",
    "python1_self_test",
]

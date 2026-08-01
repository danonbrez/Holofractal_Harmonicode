#!/usr/bin/env python3
"""Pass 190 iteration 3 registry-backed compiler and native C ABI bridge."""
from __future__ import annotations

import copy
import ctypes
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from hhs_pass190 import (
    DEFAULT_REGISTRY,
    HHSAuthorityContext,
    OperationRegistry,
    canonical_json,
    hash72,
    hash216,
    parse_constructor,
)

ITERATION3_CLASSIFICATION = "HHS_PASS_190_ITERATION_3_NATIVE_ABI_COMPILER_PARITY_FOUNDATION_VERIFIED"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NATIVE_MANIFEST = ROOT / "native" / "generated" / "HHS_NATIVE_ABI_MANIFEST_V1.json"
DEFAULT_NATIVE_LIBRARY = ROOT / "build" / "libhhs_pass190_abi.so"


class NativeABIError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompiledInstruction:
    source_line: int
    source: str
    operation_id: str
    arguments: Mapping[str, Any]
    cst: Mapping[str, Any]
    ast: Mapping[str, Any]
    hir: Mapping[str, Any]
    vmir: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_line": self.source_line,
            "source": self.source,
            "operation_id": self.operation_id,
            "arguments": copy.deepcopy(dict(self.arguments)),
            "cst": copy.deepcopy(dict(self.cst)),
            "ast": copy.deepcopy(dict(self.ast)),
            "hir": copy.deepcopy(dict(self.hir)),
            "vmir": copy.deepcopy(dict(self.vmir)),
        }


class NativeManifest:
    def __init__(self, registry: OperationRegistry, path: Path = DEFAULT_NATIVE_MANIFEST):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "HHS_NATIVE_ABI_MANIFEST_V1":
            raise NativeABIError("unexpected native ABI manifest schema")
        operations = payload.get("operations", [])
        if payload.get("operation_count") != len(operations):
            raise NativeABIError("native ABI manifest count mismatch")
        self.payload = payload
        self.by_id = {item["operation_id"]: item for item in operations}
        if list(self.by_id) != list(registry.by_id):
            raise NativeABIError("native ABI operation order differs from canonical registry")
        for operation_id, item in self.by_id.items():
            record = registry.resolve(operation_id)
            if item["vm81_binding"] != record.raw["VM81_binding"]:
                raise NativeABIError(f"native VM81 binding mismatch for {operation_id}")
            if item["slot"] < 0 or item["slot"] >= len(operations):
                raise NativeABIError(f"invalid native slot for {operation_id}")


class HarmonicodeOperationCompiler:
    """Lowers exact constructor statements through CST, AST, HIR, and VMIR."""

    def __init__(
        self,
        registry_path: Path = DEFAULT_REGISTRY,
        manifest_path: Path = DEFAULT_NATIVE_MANIFEST,
    ):
        self.registry = OperationRegistry(registry_path)
        self.native = NativeManifest(self.registry, manifest_path)

    def compile_instruction(self, source: str, source_line: int = 1) -> CompiledInstruction:
        operation_id, arguments = parse_constructor(source, self.registry)
        record = self.registry.resolve(operation_id)
        native = self.native.by_id[operation_id]
        cst = {
            "schema": "HHS_P190_CST_V1",
            "source_line": source_line,
            "lexical_source": source,
            "preserve_exact": True,
        }
        ast_node = {
            "schema": "HHS_P190_AST_V1",
            "node": "OperationConstructor",
            "constructor": record.constructor,
            "arguments": copy.deepcopy(arguments),
        }
        hir = {
            "schema": "HHS_P190_HIR_V1",
            "operation_id": operation_id,
            "operation_hash216": record.raw["Hash216_identity"],
            "effect_class": record.raw["effect_class"],
            "capability_scope": record.raw["capability_scope"],
            "determinism_class": record.raw["determinism_class"],
        }
        vmir = {
            "schema": "HHS_P190_VMIR_V1",
            "vm81_binding": record.raw["VM81_binding"],
            "native_abi_symbol": native["native_symbol"],
            "native_profile": native["native_profile"],
            "operation_slot": native["slot"],
            "mutation_lane": bool(native["mutates_state"]),
        }
        return CompiledInstruction(source_line, source, operation_id, arguments, cst, ast_node, hir, vmir)

    def compile_program(self, source: str) -> dict[str, Any]:
        instructions = []
        for line_number, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            instructions.append(self.compile_instruction(stripped, line_number))
        if not instructions:
            raise ValueError("program contains no constructor instructions")
        instruction_payload = [item.to_dict() for item in instructions]
        identity_payload = {
            "schema": "HHS_P190_COMPILED_PROGRAM_V1",
            "contract": "HHS-P190-OVRA-HOSS-PCA-FHF-VM81-H72-H216",
            "iteration": 3,
            "instructions": instruction_payload,
        }
        return {
            **identity_payload,
            "program_hash72": hash72("pass190.iteration3.program", identity_payload),
            "program_hash216": hash216("pass190.iteration3.program.topology", identity_payload),
        }

    def execute(
        self,
        program: Mapping[str, Any],
        context: HHSAuthorityContext,
        *,
        capabilities: Iterable[str] = (),
    ) -> list[dict[str, Any]]:
        outputs = []
        for instruction in program["instructions"]:
            result = context.invoke(
                instruction["operation_id"],
                instruction["arguments"],
                surface="compiler-vmir",
                capabilities=capabilities,
            )
            outputs.append(result.to_dict())
        return outputs


class _Context(ctypes.Structure):
    _fields_ = [("counter", ctypes.c_int64), ("receipt_index", ctypes.c_uint64)]


class _Status(ctypes.Structure):
    _fields_ = [
        ("abi_major", ctypes.c_uint32),
        ("abi_minor", ctypes.c_uint32),
        ("abi_patch", ctypes.c_uint32),
        ("operation_count", ctypes.c_uint32),
        ("counter", ctypes.c_int64),
        ("receipt_index", ctypes.c_uint64),
    ]


class _Pass189Address(ctypes.Structure):
    _fields_ = [
        ("address", ctypes.c_uint64),
        ("projected", ctypes.c_uint64),
        ("cell81", ctypes.c_uint32),
        ("operation64", ctypes.c_uint32),
        ("gear243", ctypes.c_uint32),
        ("kappa41", ctypes.c_uint32),
        ("local_k", ctypes.c_int32),
    ]


class _KVJSON(ctypes.Structure):
    _fields_ = [("key", ctypes.c_char_p), ("json_value", ctypes.c_char_p)]


class NativeABI:
    def __init__(self, library_path: Path = DEFAULT_NATIVE_LIBRARY):
        self.library_path = Path(library_path)
        self.lib = ctypes.CDLL(str(self.library_path))
        self.context = _Context()
        self._configure()
        self.reset()

    def _configure(self) -> None:
        self.lib.hhs_p190_context_init.argtypes = [ctypes.POINTER(_Context)]
        self.lib.hhs_p190_context_init.restype = ctypes.c_int
        self.lib.hhs_p190_system_status.argtypes = [ctypes.POINTER(_Context), ctypes.POINTER(_Status)]
        self.lib.hhs_p190_system_status.restype = ctypes.c_int
        self.lib.hhs_p190_python_len.argtypes = [ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self.lib.hhs_p190_python_len.restype = ctypes.c_int
        self.lib.hhs_p190_python_abs.argtypes = [ctypes.c_int64, ctypes.POINTER(ctypes.c_int64)]
        self.lib.hhs_p190_python_abs.restype = ctypes.c_int
        self.lib.hhs_p190_python_sorted_i64.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t, ctypes.c_int, ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t]
        self.lib.hhs_p190_python_sorted_i64.restype = ctypes.c_int
        self.lib.hhs_p190_list_with_appended_i64.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t, ctypes.c_int64, ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self.lib.hhs_p190_list_with_appended_i64.restype = ctypes.c_int
        self.lib.hhs_p190_dict_get_json.argtypes = [ctypes.POINTER(_KVJSON), ctypes.c_size_t, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        self.lib.hhs_p190_dict_get_json.restype = ctypes.c_int
        self.lib.hhs_p190_text_join.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t, ctypes.POINTER(ctypes.c_char), ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self.lib.hhs_p190_text_join.restype = ctypes.c_int
        self.lib.hhs_p190_math_gcd.argtypes = [ctypes.c_int64, ctypes.c_int64, ctypes.POINTER(ctypes.c_int64)]
        self.lib.hhs_p190_math_gcd.restype = ctypes.c_int
        self.lib.hhs_p190_pass189_context_decode.argtypes = [ctypes.c_uint64, ctypes.POINTER(_Pass189Address)]
        self.lib.hhs_p190_pass189_context_decode.restype = ctypes.c_int
        self.lib.hhs_p190_state_counter_advance.argtypes = [ctypes.POINTER(_Context), ctypes.c_int64, ctypes.c_int, ctypes.c_int64, ctypes.POINTER(ctypes.c_int64), ctypes.POINTER(ctypes.c_int64)]
        self.lib.hhs_p190_state_counter_advance.restype = ctypes.c_int

    @staticmethod
    def _check(code: int, operation: str) -> None:
        if code != 0:
            raise NativeABIError(f"{operation} failed with native result {code}")

    @staticmethod
    def _int64(value: Any, name: str) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or not -(2**63) <= value < 2**63:
            raise NativeABIError(f"{name} must fit signed int64")
        return value

    def reset(self) -> None:
        self._check(self.lib.hhs_p190_context_init(ctypes.byref(self.context)), "context_init")

    def invoke(self, operation_id: str, arguments: Mapping[str, Any]) -> Any:
        args = dict(arguments)
        if operation_id == "system.status":
            status = _Status()
            self._check(self.lib.hhs_p190_system_status(ctypes.byref(self.context), ctypes.byref(status)), operation_id)
            return {
                "abi_version": f"{status.abi_major}.{status.abi_minor}.{status.abi_patch}",
                "operations": status.operation_count,
                "counter": status.counter,
                "receipt_index": status.receipt_index,
            }
        if operation_id == "python.len":
            value = args["value"]
            length = len(value)
            output = ctypes.c_size_t()
            self._check(self.lib.hhs_p190_python_len(length, ctypes.byref(output)), operation_id)
            return output.value
        if operation_id == "python.abs":
            output = ctypes.c_int64()
            self._check(self.lib.hhs_p190_python_abs(self._int64(args["value"], "value"), ctypes.byref(output)), operation_id)
            return output.value
        if operation_id == "python.sorted":
            values = [self._int64(item, "values item") for item in args["values"]]
            array_type = ctypes.c_int64 * max(1, len(values))
            input_array = array_type(*values) if values else array_type()
            output_array = array_type()
            self._check(self.lib.hhs_p190_python_sorted_i64(input_array, len(values), int(bool(args.get("reverse", False))), output_array, len(values)), operation_id)
            return list(output_array)[:len(values)]
        if operation_id == "list.with_appended":
            values = [self._int64(item, "source item") for item in args["source"]]
            value = self._int64(args["value"], "value")
            input_type = ctypes.c_int64 * max(1, len(values))
            output_type = ctypes.c_int64 * (len(values) + 1)
            input_array = input_type(*values) if values else input_type()
            output_array = output_type()
            output_count = ctypes.c_size_t()
            self._check(self.lib.hhs_p190_list_with_appended_i64(input_array, len(values), value, output_array, len(values) + 1, ctypes.byref(output_count)), operation_id)
            return list(output_array)[:output_count.value]
        if operation_id == "dict.get":
            mapping = args["mapping"]
            if not all(isinstance(key, str) for key in mapping):
                raise NativeABIError("native dict.get requires string keys")
            encoded = [(key.encode(), canonical_json(value).encode()) for key, value in mapping.items()]
            array_type = _KVJSON * max(1, len(encoded))
            items = array_type(*[_KVJSON(key, value) for key, value in encoded]) if encoded else array_type()
            default = canonical_json(args.get("default")).encode()
            output = ctypes.c_char_p()
            self._check(self.lib.hhs_p190_dict_get_json(items, len(encoded), args["key"].encode(), default, ctypes.byref(output)), operation_id)
            return json.loads(output.value.decode())
        if operation_id == "text.join":
            encoded = [item.encode() for item in args["values"]]
            values_type = ctypes.c_char_p * max(1, len(encoded))
            values = values_type(*encoded) if encoded else values_type()
            required = sum(len(item) for item in encoded) + max(0, len(encoded) - 1) * len(args["separator"].encode())
            output = ctypes.create_string_buffer(required + 1)
            output_length = ctypes.c_size_t()
            self._check(self.lib.hhs_p190_text_join(args["separator"].encode(), values, len(encoded), output, len(output), ctypes.byref(output_length)), operation_id)
            return output.value.decode()
        if operation_id == "math.gcd":
            output = ctypes.c_int64()
            self._check(self.lib.hhs_p190_math_gcd(self._int64(args["a"], "a"), self._int64(args["b"], "b"), ctypes.byref(output)), operation_id)
            return output.value
        if operation_id == "pass189.context.decode":
            output = _Pass189Address()
            self._check(self.lib.hhs_p190_pass189_context_decode(args["address"], ctypes.byref(output)), operation_id)
            return {name: getattr(output, name) for name, _field in output._fields_}
        if operation_id == "state.counter.advance":
            before = ctypes.c_int64()
            after = ctypes.c_int64()
            self._check(self.lib.hhs_p190_state_counter_advance(ctypes.byref(self.context), self._int64(args["delta"], "delta"), 0, 0, ctypes.byref(before), ctypes.byref(after)), operation_id)
            return {"before": before.value, "after": after.value}
        raise NativeABIError(f"operation is not bound to native ABI: {operation_id}")


def semantic_parity(operation_id: str, python_result: Any, native_result: Any) -> bool:
    if operation_id == "system.status":
        return python_result["operations"] == native_result["operations"]
    if operation_id == "state.counter.advance":
        return python_result["before"] == native_result["before"] and python_result["after"] == native_result["after"]
    return python_result == native_result


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Pass 190 iteration 3 compiler and native ABI bridge")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source")
    source_group.add_argument("--file", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--capability", action="append", default=[])
    args = parser.parse_args(argv)
    source = args.source if args.source is not None else args.file.read_text(encoding="utf-8")
    compiler = HarmonicodeOperationCompiler()
    program = compiler.compile_program(source)
    payload: dict[str, Any] = {"program": program}
    if args.execute:
        payload["authority_results"] = compiler.execute(
            program,
            HHSAuthorityContext(),
            capabilities=args.capability,
        )
    if args.native:
        native = NativeABI()
        payload["native_results"] = [
            {
                "operation_id": instruction["operation_id"],
                "result": native.invoke(instruction["operation_id"], instruction["arguments"]),
            }
            for instruction in program["instructions"]
        ]
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

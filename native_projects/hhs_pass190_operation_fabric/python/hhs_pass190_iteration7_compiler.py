#!/usr/bin/env python3
"""Iteration 7 compiler for native operations and exact durable-execution fallbacks."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from hhs_pass190 import DEFAULT_REGISTRY, OperationRegistry, hash72, hash216, parse_constructor
from hhs_pass190_iteration3 import DEFAULT_NATIVE_MANIFEST, CompiledInstruction, NativeManifest
from hhs_pass190_iteration7_registry import ITERATION7_CONTRACT, Iteration7OperationRegistry


class DurableExecutionCompiler:
    """Compile all governed operations without extending the validated ten-operation C ABI."""

    def __init__(
        self,
        registry_path: Path = DEFAULT_REGISTRY,
        manifest_path: Path = DEFAULT_NATIVE_MANIFEST,
    ):
        self.registry = Iteration7OperationRegistry(registry_path)
        self.native = NativeManifest(OperationRegistry(registry_path), manifest_path)

    def compile_instruction(self, source: str, source_line: int = 1) -> CompiledInstruction:
        operation_id, arguments = parse_constructor(source, self.registry)
        record = self.registry.resolve(operation_id)
        native = self.native.by_id.get(operation_id)
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
            "operation_class": record.raw["operation_class"],
        }
        if native is None:
            vmir: dict[str, Any] = {
                "schema": "HHS_P190_VMIR_V1",
                "vm81_binding": record.raw["VM81_binding"],
                "native_available": False,
                "native_abi_symbol": None,
                "native_profile": "vm81-exact-authority-fallback-v1",
                "operation_slot": None,
                "mutation_lane": record.raw["effect_class"] == "mutation",
                "fallback_authority": "HHSAuthorityContext.invoke",
            }
        else:
            vmir = {
                "schema": "HHS_P190_VMIR_V1",
                "vm81_binding": record.raw["VM81_binding"],
                "native_available": True,
                "native_abi_symbol": native["native_symbol"],
                "native_profile": native["native_profile"],
                "operation_slot": native["slot"],
                "mutation_lane": bool(native["mutates_state"]),
                "fallback_authority": None,
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
        instruction_payload = [instruction.to_dict() for instruction in instructions]
        identity = {
            "schema": "HHS_P190_COMPILED_PROGRAM_V1",
            "contract": ITERATION7_CONTRACT,
            "iteration": 7,
            "registry_hash216": self.registry.payload["registry_hash216"],
            "native_operation_count": len(self.native.by_id),
            "governed_operation_count": len(self.registry.records),
            "execution_operation_count": int(self.registry.payload["execution_operation_count"]),
            "instructions": instruction_payload,
        }
        return {
            **identity,
            "program_hash72": hash72("pass190.iteration7.program", identity),
            "program_hash216": hash216("pass190.iteration7.program.topology", identity),
        }

    def execute(self, program: dict[str, Any], context: Any, *, capabilities: tuple[str, ...] = ()) -> list[dict[str, Any]]:
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

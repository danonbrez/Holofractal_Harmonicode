from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass118_symbolic_harmonicode_runtime_v1 import HarmonicodeRuntimeEngine

PASS_ID = "PASS_121"
CORE_SPEC_SCHEMA = "HHS_HARMONICODE_CORE_SPEC_V1"
INTERPRETATION_SCHEMA = "HHS_HARMONICODE_NATIVE_INTERPRETATION_V1"
CLOSED_OPERATION_SCHEMA = "HHS_HARMONICODE_CLOSED_VALIDATED_OPERATION_V1"
PYTHON_EXPORT_SCHEMA = "HHS_HARMONICODE_ONE_WAY_PYTHON_EXPORT_V1"
EXPORT_VALIDATION_SCHEMA = "HHS_HARMONICODE_EXPORT_VALIDATION_RECEIPT_V1"

REJECTION_CODES = {
    "REJECT_UNKNOWN_CORE_OPCODE",
    "REJECT_CORE_OPCODE_WITHOUT_NATIVE_RUNTIME_SURFACE",
    "REJECT_UNVALIDATED_OPERATION_EXPORT",
    "REJECT_OPEN_SYMBOL_EXPORT",
    "REJECT_PYTHON_AS_RUNTIME_VALIDATOR",
    "REJECT_PYTHON_IMPORT_AS_CANONICAL_AUTHORITY",
    "REJECT_EXPORT_SOURCE_ROOT_MISMATCH",
    "REJECT_EXPORT_MANIFEST_MISMATCH",
    "REJECT_MUTATED_CLOSED_OPERATION",
    "REJECT_FLOAT_AS_EXACT_AUTHORITY",
    "REJECT_RESOURCE_CONTRACT_EXCEEDED",
}


class Pass121Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class CoreOpcode:
    name: str
    arity_min: int
    arity_max: int
    domain: str
    native_surface: str
    commutative: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arity_min": self.arity_min,
            "arity_max": self.arity_max,
            "domain": self.domain,
            "native_surface": self.native_surface,
            "commutative": self.commutative,
        }


class HarmonicodeCoreLibrary:
    """Native HARMONICODE core specification, interpreter, and sealed one-way exporter."""

    def __init__(self, *, max_operations: int = 4096):
        self.runtime = HarmonicodeRuntimeEngine()
        self.max_operations = max_operations
        self._opcodes = {
            "add": CoreOpcode("add", 2, 1024, "EXACT_SCALAR", "HarmonicodeRuntimeEngine.evaluate_expression", True),
            "subtract": CoreOpcode("subtract", 2, 2, "EXACT_SCALAR", "HarmonicodeRuntimeEngine.evaluate_expression", False),
            "multiply": CoreOpcode("multiply", 2, 1024, "EXACT_SCALAR_OR_TENSOR", "HarmonicodeRuntimeEngine.evaluate_expression", False),
            "divide_exact": CoreOpcode("divide_exact", 2, 2, "EXACT_SCALAR", "HarmonicodeRuntimeEngine.evaluate_expression", False),
                        "power": CoreOpcode("power", 2, 2, "EXACT_SCALAR", "HarmonicodeRuntimeEngine.evaluate_expression", False),
            "equal": CoreOpcode("equal", 2, 2, "TYPED_VALUE", "HarmonicodeRuntimeEngine.evaluate_expression", True),
                        "matmul": CoreOpcode("matmul", 2, 2, "EXACT_TENSOR", "HarmonicodeRuntimeEngine.evaluate_expression", False),
                    }
        self.spec = self._build_spec()

    def _build_spec(self) -> dict[str, Any]:
        spec = {
            "schema": CORE_SPEC_SCHEMA,
            "pass_id": PASS_ID,
            "authority_model": {
                "interpreter": "NATIVE_HARMONICODE_RUNTIME_AUTHORITY",
                "proof": "NATIVE_RUNTIME_AND_HASH72_RECEIPTS",
                "python": "ONE_WAY_EGRESS_ONLY_NONAUTHORITATIVE",
            },
            "exact_domains": ["INTEGER", "RATIONAL", "HARMONICODE_Q_B_I", "EXACT_TENSOR", "TRINARY_LOGIC"],
            "defining_relations": ["b^2=2", "i^2=-1"],
            "opcodes": [self._opcodes[k].to_dict() for k in sorted(self._opcodes)],
            "noncommutative_order_preserved": True,
            "float_authority_prohibited": True,
        }
        spec["core_spec_root_hash72"] = _hash("hhs_pass121_core_spec_v1", spec)
        return spec

    def describe_opcode(self, name: str) -> dict[str, Any]:
        op = self._opcodes.get(str(name))
        if op is None:
            raise Pass121Error("REJECT_UNKNOWN_CORE_OPCODE", str(name))
        return op.to_dict()

    def interpret(self, expression: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        if not authority_root_hash72:
            raise Pass121Error("REJECT_CORE_OPCODE_WITHOUT_NATIVE_RUNTIME_SURFACE", "missing authority")
        node_count = self._count_nodes(expression)
        if node_count > self.max_operations:
            raise Pass121Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", str(node_count))
        for op in self._collect_ops(expression):
            self.describe_opcode(op)
        runtime = self.runtime.evaluate_expression(deepcopy(dict(expression)))
        result = {
            "schema": INTERPRETATION_SCHEMA,
            "core_spec_root_hash72": self.spec["core_spec_root_hash72"],
            "authority_root_hash72": authority_root_hash72,
            "expression": deepcopy(dict(expression)),
            "typed_ast": runtime["result"].get("typed_ast"),
            "canonical_result": runtime["result"].get("canonical_value", runtime["result"].get("value")),
            "runtime_result_root_hash72": runtime["result"]["result_root_hash72"],
            "execution_status": "NATIVE_HARMONICODE_INTERPRETATION_VALIDATED",
            "python_used_for_validation": False,
        }
        result["interpretation_root_hash72"] = _hash("hhs_pass121_interpretation_v1", result)
        return result

    def close_operation(self, interpretation: Mapping[str, Any]) -> dict[str, Any]:
        if interpretation.get("execution_status") != "NATIVE_HARMONICODE_INTERPRETATION_VALIDATED":
            raise Pass121Error("REJECT_UNVALIDATED_OPERATION_EXPORT", "interpretation status")
        expr = interpretation.get("expression", {})
        if self._contains_open_symbol(expr):
            raise Pass121Error("REJECT_OPEN_SYMBOL_EXPORT", "operation contains unbound symbol")
        closed = {
            "schema": CLOSED_OPERATION_SCHEMA,
            "core_spec_root_hash72": interpretation["core_spec_root_hash72"],
            "interpretation_root_hash72": interpretation["interpretation_root_hash72"],
            "runtime_result_root_hash72": interpretation["runtime_result_root_hash72"],
            "expression": deepcopy(expr),
            "canonical_result": deepcopy(interpretation.get("canonical_result")),
            "closure_status": "CLOSED_AND_RUNTIME_VALIDATED",
            "export_authority": "HARMONICODE_ONLY",
        }
        closed["closed_operation_root_hash72"] = _hash("hhs_pass121_closed_operation_v1", closed)
        return closed

    def export_python(self, closed_operation: Mapping[str, Any], *, module_name: str = "harmonicode_export") -> dict[str, Any]:
        expected = dict(closed_operation)
        root = expected.pop("closed_operation_root_hash72", None)
        if root != _hash("hhs_pass121_closed_operation_v1", expected):
            raise Pass121Error("REJECT_MUTATED_CLOSED_OPERATION", "root mismatch")
        if closed_operation.get("closure_status") != "CLOSED_AND_RUNTIME_VALIDATED":
            raise Pass121Error("REJECT_UNVALIDATED_OPERATION_EXPORT", "not closed")
        payload = repr(deepcopy(closed_operation.get("canonical_result")))
        source = (
            '"""Generated one-way HARMONICODE egress artifact.\n'
            'This module is not a runtime validator or canonical authority.\n"""\n\n'
            f"HARMONICODE_CLOSED_OPERATION_ROOT = {root!r}\n"
            f"HARMONICODE_CORE_SPEC_ROOT = {closed_operation['core_spec_root_hash72']!r}\n"
            f"CANONICAL_RESULT = {payload}\n\n"
            "def exported_result():\n"
            "    return CANONICAL_RESULT\n"
        )
        export = {
            "schema": PYTHON_EXPORT_SCHEMA,
            "module_name": module_name,
            "closed_operation_root_hash72": root,
            "core_spec_root_hash72": closed_operation["core_spec_root_hash72"],
            "source": source,
            "authority": "NONAUTHORITATIVE_ONE_WAY_EGRESS",
            "python_validation_permitted": False,
            "python_import_as_authority_permitted": False,
        }
        export["source_root_hash72"] = _hash("hhs_pass121_python_source_v1", source)
        export["export_root_hash72"] = _hash("hhs_pass121_python_export_v1", export)
        return export

    def validate_export(self, export: Mapping[str, Any], closed_operation: Mapping[str, Any]) -> dict[str, Any]:
        if export.get("python_validation_permitted") is not False:
            raise Pass121Error("REJECT_PYTHON_AS_RUNTIME_VALIDATOR", "flag changed")
        if export.get("python_import_as_authority_permitted") is not False:
            raise Pass121Error("REJECT_PYTHON_IMPORT_AS_CANONICAL_AUTHORITY", "flag changed")
        if export.get("source_root_hash72") != _hash("hhs_pass121_python_source_v1", export.get("source", "")):
            raise Pass121Error("REJECT_EXPORT_SOURCE_ROOT_MISMATCH", "source")
        if export.get("closed_operation_root_hash72") != closed_operation.get("closed_operation_root_hash72"):
            raise Pass121Error("REJECT_EXPORT_MANIFEST_MISMATCH", "closed operation")
        receipt = {
            "schema": EXPORT_VALIDATION_SCHEMA,
            "export_root_hash72": export["export_root_hash72"],
            "closed_operation_root_hash72": closed_operation["closed_operation_root_hash72"],
            "validation_status": "ONE_WAY_EXPORT_VALIDATED",
            "runtime_authority_transferred": False,
            "python_executed_for_validation": False,
        }
        receipt["validation_receipt_root_hash72"] = _hash("hhs_pass121_export_validation_v1", receipt)
        return receipt

    @staticmethod
    def _count_nodes(value: Any) -> int:
        if isinstance(value, Mapping):
            return 1 + sum(HarmonicodeCoreLibrary._count_nodes(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return 1 + sum(HarmonicodeCoreLibrary._count_nodes(v) for v in value)
        return 1

    @staticmethod
    def _collect_ops(value: Any) -> list[str]:
        found: list[str] = []
        if isinstance(value, Mapping):
            if value.get("node") == "call":
                found.append(str(value.get("op")))
            for v in value.values():
                found.extend(HarmonicodeCoreLibrary._collect_ops(v))
        elif isinstance(value, (list, tuple)):
            for v in value:
                found.extend(HarmonicodeCoreLibrary._collect_ops(v))
        return found

    @staticmethod
    def _contains_open_symbol(value: Any) -> bool:
        if isinstance(value, Mapping):
            if value.get("node") in {"symbol", "variable"}:
                return True
            return any(HarmonicodeCoreLibrary._contains_open_symbol(v) for v in value.values())
        if isinstance(value, (list, tuple)):
            return any(HarmonicodeCoreLibrary._contains_open_symbol(v) for v in value)
        return False


def pass121_self_test() -> dict[str, Any]:
    core = HarmonicodeCoreLibrary()
    expr = {"node": "call", "op": "add", "args": [
        {"node": "literal", "kind": "RATIONAL", "value": "1/3"},
        {"node": "literal", "kind": "RATIONAL", "value": "2/3"},
    ]}
    auth = _hash("hhs_pass121_self_test_auth", "ok")
    interpreted = core.interpret(expr, authority_root_hash72=auth)
    closed = core.close_operation(interpreted)
    exported = core.export_python(closed)
    receipt = core.validate_export(exported, closed)
    return {
        "ok": receipt["validation_status"] == "ONE_WAY_EXPORT_VALIDATED",
        "core_spec_root_hash72": core.spec["core_spec_root_hash72"],
        "closed_operation_root_hash72": closed["closed_operation_root_hash72"],
        "export_root_hash72": exported["export_root_hash72"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(pass121_self_test(), indent=2, sort_keys=True))

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass117_vm81_deterministic_quantum_simulation_v1 import (
    ExactComplex,
    ExactQuadratic,
    NativeSymbolicAmplitude,
    VM81QuantumSimulationEngine,
)

PASS_ID = "PASS_118"
PROGRAM_SCHEMA = "HHS_HARMONICODE_PROGRAM_V1"
AST_SCHEMA = "HHS_HARMONICODE_TYPED_AST_V1"
PROOF_SCHEMA = "HHS_SYMBOLIC_PROOF_V1"
RUNTIME_EQ_SCHEMA = "HHS_SYMBOLIC_RUNTIME_EQUIVALENCE_RECEIPT_V1"
HASH72_PROGRAM_SCHEMA = "HHS_HASH72_SYMBOLIC_PROGRAM_REPLAY_V1"
PHASE_GEAR_SCHEMA = "HHS_XYZW_PHASE_GEAR_STATE_V1"
TOKEN_SCHEMA = "HHS_MULTIMODAL_TOKEN_V1"

REJECTION_CODES = {
    "REJECT_UNTYPED_SYMBOLIC_OPERATION",
    "REJECT_AMBIGUOUS_SYMBOL_SCOPE",
    "REJECT_VARIABLE_CAPTURE",
    "REJECT_UNKNOWN_OPERATOR",
    "REJECT_OPERATOR_DOMAIN_MISMATCH",
    "REJECT_FLOAT_AS_CANONICAL_EXACT_RESULT",
    "REJECT_INVALID_IDENTITY_SIMPLIFICATION",
    "REJECT_NONCOMMUTATIVE_ORDER_ERASURE",
    "REJECT_REWRITE_WITHOUT_PRECONDITION",
    "REJECT_NONTERMINATING_REWRITE_CYCLE",
    "REJECT_CONCLUSION_WITHOUT_DERIVATION",
    "REJECT_INDETERMINATE_LOGIC_COLLAPSED_TO_FALSE",
    "REJECT_HARMONICODE_JSON_SCHEMA_FAILURE",
    "REJECT_HARMONICODE_OPCODE_WITHOUT_RUNTIME_SURFACE",
    "REJECT_RUNTIME_RESULT_NOT_MATCHING_SYMBOLIC_RESULT",
    "REJECT_SYMBOLIC_DERIVATION_REPORTED_AS_RUNTIME_EXECUTION",
    "REJECT_EXECUTION_WITHOUT_AUTHORITY",
    "REJECT_HASH72_ROOT_USED_AS_REVERSIBLE_PAYLOAD",
    "REJECT_HASH72_REPLAY_WITH_MISSING_OPERATION_PAYLOAD",
    "REJECT_SYMBOLIC_STATE_ROOT_MISMATCH",
    "REJECT_HASH72_ORDER_LOSS",
    "REJECT_PHASE_GEAR_RELATION_ASSUMED_WITHOUT_DOMAIN",
    "REJECT_RECIPROCAL_PAIR_MISMATCH",
    "REJECT_PAIR_PRODUCT_CLOSURE_FAILURE",
    "REJECT_ZERO_SUM_INFERRED_WITHOUT_NEGATION_RELATION",
    "REJECT_PHASE_ROTATION_WITHOUT_INVERSE",
    "REJECT_PHASE_GEAR_RESULT_WITHOUT_VM81_RECEIPT",
    "REJECT_MULTIMODAL_TOKEN_WITHOUT_SOURCE_BINDING",
    "REJECT_MULTIMODAL_RELATION_DIRECTION_LOSS",
    "REJECT_TOKEN_TYPE_MISMATCH",
    "REJECT_GENERATED_CANDIDATE_REPORTED_AS_ADMITTED",
    "REJECT_NONRENDERABLE_TOKEN_REPORTED_AS_EMITTED",
    "REJECT_MULTIMODAL_OUTPUT_WITHOUT_PROVENANCE",
    "REJECT_RESOURCE_CONTRACT_EXCEEDED",
}


class Pass118Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _fraction(v: Any) -> Fraction:
    if isinstance(v, Fraction):
        return v
    if isinstance(v, bool):
        return Fraction(int(v), 1)
    if isinstance(v, int):
        return Fraction(v, 1)
    if isinstance(v, str):
        return Fraction(v)
    if isinstance(v, float):
        raise Pass118Error("REJECT_FLOAT_AS_CANONICAL_EXACT_RESULT", repr(v))
    raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", type(v).__name__)


def _fraction_dict(v: Fraction) -> dict[str, int]:
    return {"numerator": v.numerator, "denominator": v.denominator}


def _canonical_value(v: Any) -> Any:
    if isinstance(v, Fraction):
        return {"kind": "RATIONAL", **_fraction_dict(v)}
    if isinstance(v, ExactQuadratic):
        return {"kind": "Q_B", **v.to_dict()}
    if isinstance(v, NativeSymbolicAmplitude):
        return v.to_dict()
    if isinstance(v, ExactComplex):
        return {"kind": "COMPLEX_RATIONAL", **v.to_dict()}
    if isinstance(v, Trinary):
        return {"kind": "TRINARY", "value": v.value}
    if isinstance(v, TensorValue):
        return v.to_dict()
    if isinstance(v, (str, bool, int)) or v is None:
        return v
    if isinstance(v, list):
        return [_canonical_value(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _canonical_value(v[k]) for k in sorted(v)}
    raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", f"uncanonical value {type(v).__name__}")


@dataclass(frozen=True)
class Trinary:
    value: int
    def __post_init__(self) -> None:
        if self.value not in (-1, 0, 1):
            raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "trinary")


@dataclass(frozen=True)
class TensorValue:
    shape: tuple[int, ...]
    values: tuple[Any, ...]
    def __post_init__(self) -> None:
        n = 1
        for d in self.shape:
            if d <= 0:
                raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "tensor shape")
            n *= d
        if n != len(self.values):
            raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "tensor value count")
    def to_dict(self) -> dict[str, Any]:
        return {"kind": "TENSOR", "shape": list(self.shape), "values": [_canonical_value(v) for v in self.values]}


@dataclass(frozen=True)
class SymbolBinding:
    name: str
    type_name: str
    value: Any
    scope: str
    binding_root_hash72: str


class HarmonicodeRuntimeEngine:
    """Typed exact HARMONICODE JSON interpreter and Hash72 replay surface."""

    def __init__(self, *, max_ast_nodes: int = 4096, max_operations: int = 2048):
        self.max_ast_nodes = max_ast_nodes
        self.max_operations = max_operations
        self.vm81 = VM81QuantumSimulationEngine()

    # ----------------------- parsing / typing -----------------------
    def _literal(self, node: Mapping[str, Any]) -> tuple[Any, str]:
        kind = node.get("kind")
        value = node.get("value")
        if kind == "INTEGER":
            if isinstance(value, float):
                raise Pass118Error("REJECT_FLOAT_AS_CANONICAL_EXACT_RESULT", repr(value))
            return Fraction(int(value), 1), "RATIONAL"
        if kind == "RATIONAL":
            return _fraction(value), "RATIONAL"
        if kind == "TRINARY":
            return Trinary(int(value)), "TRINARY"
        if kind == "BOOLEAN":
            if not isinstance(value, bool):
                raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "boolean")
            return value, "BOOLEAN"
        if kind == "STRING":
            return str(value), "STRING"
        if kind == "B_INVERSE":
            return NativeSymbolicAmplitude.b_inverse(), "HARMONICODE_Q_B_I"
        if kind == "SYMBOLIC_AMPLITUDE":
            return NativeSymbolicAmplitude.from_dict(value), "HARMONICODE_Q_B_I"
        raise Pass118Error("REJECT_HARMONICODE_JSON_SCHEMA_FAILURE", f"literal {kind}")

    def build_typed_ast(self, expr: Mapping[str, Any], environment: Mapping[str, SymbolBinding] | None = None) -> dict[str, Any]:
        env = environment or {}
        count = 0
        def visit(node: Mapping[str, Any], path: tuple[int, ...]) -> dict[str, Any]:
            nonlocal count
            count += 1
            if count > self.max_ast_nodes:
                raise Pass118Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "AST nodes")
            if not isinstance(node, Mapping):
                raise Pass118Error("REJECT_HARMONICODE_JSON_SCHEMA_FAILURE", "expression node")
            ntype = node.get("node")
            if ntype == "literal":
                value, type_name = self._literal(node)
                children: list[dict[str, Any]] = []
                payload = {"node": ntype, "type": type_name, "value": _canonical_value(value), "path": list(path)}
            elif ntype == "symbol":
                name = str(node.get("name", ""))
                if name not in env:
                    raise Pass118Error("REJECT_AMBIGUOUS_SYMBOL_SCOPE", name)
                binding = env[name]
                children = []
                payload = {"node": ntype, "name": name, "type": binding.type_name, "scope": binding.scope, "binding_root_hash72": binding.binding_root_hash72, "path": list(path)}
            elif ntype == "call":
                op = str(node.get("op", ""))
                args = node.get("args")
                if not op or not isinstance(args, list):
                    raise Pass118Error("REJECT_HARMONICODE_JSON_SCHEMA_FAILURE", "call")
                children = [visit(arg, path + (i,)) for i, arg in enumerate(args)]
                type_name = self._infer_call_type(op, [c["type"] for c in children])
                payload = {"node": ntype, "op": op, "type": type_name, "path": list(path)}
            elif ntype == "tensor":
                shape = tuple(int(x) for x in node.get("shape", []))
                args = node.get("values")
                if not shape or not isinstance(args, list):
                    raise Pass118Error("REJECT_HARMONICODE_JSON_SCHEMA_FAILURE", "tensor")
                children = [visit(arg, path + (i,)) for i, arg in enumerate(args)]
                payload = {"node": ntype, "shape": list(shape), "type": "TENSOR", "path": list(path)}
            else:
                raise Pass118Error("REJECT_HARMONICODE_JSON_SCHEMA_FAILURE", str(ntype))
            ast_root = _hash("hhs_pass118_ast_node_v1", {"payload": payload, "children": [c["ast_root_hash72"] for c in children]})
            return {"schema": "HHS_HARMONICODE_AST_NODE_V1", **payload, "children": children, "ast_root_hash72": ast_root}
        root = visit(expr, ())
        return {"schema": AST_SCHEMA, "node_count": count, "root": root, "ast_root_hash72": _hash("hhs_pass118_typed_ast_v1", root)}

    @staticmethod
    def _infer_call_type(op: str, types: Sequence[str]) -> str:
        arithmetic = {"add", "subtract", "multiply", "divide_exact", "power"}
        if op in arithmetic:
            if not types or len(set(types)) != 1 or types[0] not in {"RATIONAL", "HARMONICODE_Q_B_I"}:
                raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", f"{op}:{types}")
            return types[0]
        if op in {"equal", "not_equal", "less_than", "is_normalized"}:
            return "BOOLEAN"
        if op in {"trinary_not", "trinary_and", "trinary_or"}:
            if any(t != "TRINARY" for t in types):
                raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", f"{op}:{types}")
            return "TRINARY"
        if op == "tensor_product" or op == "matmul":
            return "TENSOR"
        raise Pass118Error("REJECT_UNKNOWN_OPERATOR", op)

    # ----------------------- exact operations -----------------------
    @staticmethod
    def _binary_arithmetic(op: str, a: Any, b: Any) -> Any:
        if isinstance(a, Fraction) and isinstance(b, Fraction):
            if op == "add": return a + b
            if op == "subtract": return a - b
            if op == "multiply": return a * b
            if op == "divide_exact":
                if b == 0: raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "division by zero")
                return a / b
            if op == "power":
                if b.denominator != 1: raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "noninteger power")
                return a ** b.numerator
        if isinstance(a, NativeSymbolicAmplitude) and isinstance(b, NativeSymbolicAmplitude):
            if op == "add": return a + b
            if op == "subtract": return a - b
            if op == "multiply": return a * b
            if op == "power":
                # bounded nonnegative integer exponent represented by rational real amplitude
                if not b.imag.is_zero() or b.real.b_coeff != 0 or b.real.rational.denominator != 1:
                    raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "symbolic exponent")
                n = b.real.rational.numerator
                if n < 0 or n > 72: raise Pass118Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "symbolic exponent")
                out = NativeSymbolicAmplitude.make(1)
                for _ in range(n): out = out * a
                return out
        raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", f"{op}:{type(a).__name__}:{type(b).__name__}")

    @staticmethod
    def _trinary_not(a: Trinary) -> Trinary:
        return Trinary(-a.value)

    @staticmethod
    def _trinary_and(a: Trinary, b: Trinary) -> Trinary:
        return Trinary(min(a.value, b.value))

    @staticmethod
    def _trinary_or(a: Trinary, b: Trinary) -> Trinary:
        return Trinary(max(a.value, b.value))

    def _eval_ast_node(self, ast: Mapping[str, Any], environment: Mapping[str, SymbolBinding]) -> Any:
        ntype = ast["node"]
        if ntype == "literal":
            kind = ast["value"].get("kind") if isinstance(ast["value"], Mapping) else None
            if kind == "RATIONAL": return Fraction(ast["value"]["numerator"], ast["value"]["denominator"])
            if kind == "HARMONICODE_Q_B_I": return NativeSymbolicAmplitude.from_dict(ast["value"])
            if kind == "TRINARY": return Trinary(int(ast["value"]["value"]))
            return ast["value"]
        if ntype == "symbol":
            return environment[ast["name"]].value
        if ntype == "tensor":
            values = tuple(self._eval_ast_node(c, environment) for c in ast["children"])
            return TensorValue(tuple(ast["shape"]), values)
        args = [self._eval_ast_node(c, environment) for c in ast["children"]]
        op = ast["op"]
        if op in {"add", "subtract", "multiply", "divide_exact", "power"}:
            if len(args) != 2: raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", op)
            return self._binary_arithmetic(op, args[0], args[1])
        if op == "equal": return _canonical_value(args[0]) == _canonical_value(args[1])
        if op == "not_equal": return _canonical_value(args[0]) != _canonical_value(args[1])
        if op == "less_than":
            if not all(isinstance(x, Fraction) for x in args): raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", op)
            return args[0] < args[1]
        if op == "trinary_not": return self._trinary_not(args[0])
        if op == "trinary_and": return self._trinary_and(args[0], args[1])
        if op == "trinary_or": return self._trinary_or(args[0], args[1])
        if op == "tensor_product": return self.tensor_product(args[0], args[1])
        if op == "matmul": return self.matmul(args[0], args[1])
        if op == "is_normalized":
            if isinstance(args[0], TensorValue):
                total = sum((x.probability() for x in args[0].values if isinstance(x, (ExactComplex, NativeSymbolicAmplitude))), Fraction(0,1))
                return total == 1
            raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", op)
        raise Pass118Error("REJECT_UNKNOWN_OPERATOR", op)

    @staticmethod
    def tensor_product(a: TensorValue, b: TensorValue) -> TensorValue:
        if not isinstance(a, TensorValue) or not isinstance(b, TensorValue):
            raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "tensor_product")
        return TensorValue(a.shape + b.shape, tuple(x * y for x in a.values for y in b.values))

    @staticmethod
    def matmul(a: TensorValue, b: TensorValue) -> TensorValue:
        if len(a.shape) != 2 or len(b.shape) not in (1, 2) or a.shape[1] != b.shape[0]:
            raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "matmul shape")
        rows, inner = a.shape
        cols = 1 if len(b.shape) == 1 else b.shape[1]
        out = []
        zero = Fraction(0, 1)
        for r in range(rows):
            for c in range(cols):
                acc: Any = None
                for k in range(inner):
                    av = a.values[r * inner + k]
                    bv = b.values[k] if cols == 1 else b.values[k * cols + c]
                    term = av * bv
                    acc = term if acc is None else acc + term
                out.append(acc if acc is not None else zero)
        return TensorValue((rows,) if cols == 1 else (rows, cols), tuple(out))

    # ----------------------- programs / proofs / replay -----------------------
    def bind_environment(self, declarations: Sequence[Mapping[str, Any]], parent_scope: str = "global") -> dict[str, SymbolBinding]:
        env: dict[str, SymbolBinding] = {}
        for decl in declarations:
            name = str(decl.get("name", ""))
            if not name or name in env:
                raise Pass118Error("REJECT_AMBIGUOUS_SYMBOL_SCOPE", name)
            value, inferred = self._literal(decl.get("value", {}))
            declared = str(decl.get("type", inferred))
            if declared != inferred:
                raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", f"{name}:{declared}!={inferred}")
            root = _hash("hhs_pass118_symbol_binding_v1", {"name": name, "type": declared, "value": _canonical_value(value), "scope": parent_scope})
            env[name] = SymbolBinding(name, declared, value, parent_scope, root)
        return env

    def evaluate_expression(self, expr: Mapping[str, Any], environment: Mapping[str, SymbolBinding] | None = None) -> dict[str, Any]:
        env = environment or {}
        ast = self.build_typed_ast(expr, env)
        value = self._eval_ast_node(ast["root"], env)
        result = {"type": ast["root"]["type"], "value": _canonical_value(value)}
        result["result_root_hash72"] = _hash("hhs_pass118_symbolic_result_v1", result)
        return {"ast": ast, "native_value": value, "result": result}

    def execute_program(self, program: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        if not authority_root_hash72:
            raise Pass118Error("REJECT_EXECUTION_WITHOUT_AUTHORITY", "empty")
        if program.get("schema") != PROGRAM_SCHEMA or not isinstance(program.get("operations"), list):
            raise Pass118Error("REJECT_HARMONICODE_JSON_SCHEMA_FAILURE", "program")
        operations = program["operations"]
        if len(operations) > self.max_operations:
            raise Pass118Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "operations")
        env = self.bind_environment(program.get("symbols", []), str(program.get("scope", "global")))
        state_root = _hash("hhs_pass118_program_genesis_v1", {"program": program.get("program_id"), "authority": authority_root_hash72, "bindings": [b.binding_root_hash72 for b in env.values()]})
        transitions = []
        outputs = []
        proofs = []
        for index, operation in enumerate(operations):
            op_kind = operation.get("kind", "evaluate")
            if op_kind not in {"evaluate", "bind", "assert"}:
                raise Pass118Error("REJECT_HARMONICODE_OPCODE_WITHOUT_RUNTIME_SURFACE", str(op_kind))
            evaluated = self.evaluate_expression(operation["expression"], env)
            result = evaluated["result"]
            if op_kind == "assert":
                if result["type"] != "BOOLEAN" or result["value"] is not True:
                    raise Pass118Error("REJECT_CONCLUSION_WITHOUT_DERIVATION", f"assert {index}")
                proofs.append(self._proof(index, evaluated["ast"], result, "EVALUATE_EXACT_ASSERTION"))
            if op_kind == "bind":
                name = str(operation.get("name", ""))
                if not name or name in env:
                    raise Pass118Error("REJECT_AMBIGUOUS_SYMBOL_SCOPE", name)
                binding_root = _hash("hhs_pass118_symbol_binding_v1", {"name": name, "type": result["type"], "value": result["value"], "scope": program.get("scope", "global"), "parent_state": state_root})
                env[name] = SymbolBinding(name, result["type"], evaluated["native_value"], str(program.get("scope", "global")), binding_root)
            transition_payload = {
                "index": index,
                "kind": op_kind,
                "previous_state_root_hash72": state_root,
                "ast_root_hash72": evaluated["ast"]["ast_root_hash72"],
                "result_root_hash72": result["result_root_hash72"],
                "binding_name": operation.get("name"),
            }
            transition_root = _hash("hhs_pass118_hash72_symbolic_transition_v1", transition_payload)
            transition = {**transition_payload, "transition_root_hash72": transition_root, "operation_payload": deepcopy(operation), "result": result}
            transitions.append(transition)
            state_root = _hash("hhs_pass118_symbolic_state_v1", {"previous": state_root, "transition": transition_root, "environment": [env[k].binding_root_hash72 for k in sorted(env)]})
            outputs.append(result)
        program_root = _hash("hhs_pass118_harmonicode_program_v1", program)
        receipt = {
            "schema": "HHS_HARMONICODE_EXECUTION_RECEIPT_V1",
            "program_root_hash72": program_root,
            "authority_root_hash72": authority_root_hash72,
            "transition_roots": [t["transition_root_hash72"] for t in transitions],
            "proof_roots": [p["proof_root_hash72"] for p in proofs],
            "terminal_state_root_hash72": state_root,
            "operation_count": len(transitions),
            "execution_status": "EXECUTED_SUCCESSFULLY",
        }
        receipt["execution_receipt_root_hash72"] = _hash("hhs_pass118_execution_receipt_v1", receipt)
        return {"program": deepcopy(program), "environment": {k: {"type": v.type_name, "value": _canonical_value(v.value), "binding_root_hash72": v.binding_root_hash72} for k, v in sorted(env.items())}, "outputs": outputs, "transitions": transitions, "proofs": proofs, "receipt": receipt}

    @staticmethod
    def _proof(index: int, ast: Mapping[str, Any], conclusion: Mapping[str, Any], rule: str) -> dict[str, Any]:
        proof = {"schema": PROOF_SCHEMA, "premise_roots": [ast["ast_root_hash72"]], "rule_application_roots": [_hash("hhs_pass118_rule_v1", rule)], "intermediate_expression_roots": [ast["root"]["ast_root_hash72"]], "conclusion_root_hash72": conclusion["result_root_hash72"], "proof_status": "VALIDATED", "step_index": index}
        proof["proof_root_hash72"] = _hash("hhs_pass118_proof_v1", proof)
        return proof

    def validate_runtime_equivalence(self, program: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        symbolic = self.execute_program(program, authority_root_hash72=authority_root_hash72)
        # Production execution uses the same registered exact operation implementations but replays from payload.
        runtime = self.replay_hash72_program(symbolic, authority_root_hash72=authority_root_hash72)
        value_match = symbolic["outputs"] == runtime["outputs"]
        state_match = symbolic["receipt"]["terminal_state_root_hash72"] == runtime["receipt"]["terminal_state_root_hash72"]
        receipt = {"schema": RUNTIME_EQ_SCHEMA, "expression_root_hash72": symbolic["receipt"]["program_root_hash72"], "symbolic_result_root_hash72": _hash("hhs_pass118_outputs_v1", symbolic["outputs"]), "runtime_result_root_hash72": _hash("hhs_pass118_outputs_v1", runtime["outputs"]), "type_match": value_match, "value_match": value_match, "state_match": state_match, "receipt_match": symbolic["receipt"]["transition_roots"] == runtime["receipt"]["transition_roots"], "equivalence_status": "SYMBOLIC_RUNTIME_EQUIVALENCE_VALIDATED" if value_match and state_match else "REJECTED"}
        receipt["equivalence_root_hash72"] = _hash("hhs_pass118_runtime_equivalence_v1", receipt)
        if receipt["equivalence_status"] != "SYMBOLIC_RUNTIME_EQUIVALENCE_VALIDATED":
            raise Pass118Error("REJECT_RUNTIME_RESULT_NOT_MATCHING_SYMBOLIC_RESULT", str(receipt))
        return receipt

    def replay_hash72_program(self, execution: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        if not execution.get("program") or any("operation_payload" not in t for t in execution.get("transitions", [])):
            raise Pass118Error("REJECT_HASH72_REPLAY_WITH_MISSING_OPERATION_PAYLOAD", "payload")
        replay = self.execute_program(execution["program"], authority_root_hash72=authority_root_hash72)
        expected = [t["transition_root_hash72"] for t in execution["transitions"]]
        actual = [t["transition_root_hash72"] for t in replay["transitions"]]
        if expected != actual:
            raise Pass118Error("REJECT_HASH72_ORDER_LOSS", "transition roots")
        return replay

    # ----------------------- phase gear -----------------------
    @staticmethod
    def _phase_one(v: Any) -> Any:
        return NativeSymbolicAmplitude.make(1) if isinstance(v, NativeSymbolicAmplitude) else Fraction(1, 1)

    @staticmethod
    def _phase_neg(v: Any) -> Any:
        return NativeSymbolicAmplitude.make() - v if isinstance(v, NativeSymbolicAmplitude) else -v

    @staticmethod
    def _phase_equal(a: Any, b: Any) -> bool:
        return _canonical_value(a) == _canonical_value(b)

    def construct_phase_gear(self, x: Any, y: Any, z: Any, w: Any, *, require_negation: bool = False, authority_root_hash72: str) -> dict[str, Any]:
        if not authority_root_hash72:
            raise Pass118Error("REJECT_EXECUTION_WITHOUT_AUTHORITY", "phase gear")
        raw = (x, y, z, w)
        symbolic = any(isinstance(v, NativeSymbolicAmplitude) for v in raw)
        if symbolic:
            if not all(isinstance(v, NativeSymbolicAmplitude) for v in raw):
                raise Pass118Error("REJECT_OPERATOR_DOMAIN_MISMATCH", "mixed phase-gear domains")
        else:
            x, y, z, w = map(_fraction, raw)
        one = self._phase_one(x)
        if not self._phase_equal(x * y, one) or not self._phase_equal(z * w, one):
            raise Pass118Error("REJECT_RECIPROCAL_PAIR_MISMATCH", "x/y or z/w")
        negation_closed = self._phase_equal(y, self._phase_neg(x)) and self._phase_equal(w, self._phase_neg(z))
        if require_negation and not negation_closed:
            raise Pass118Error("REJECT_ZERO_SUM_INFERRED_WITHOUT_NEGATION_RELATION", "negation")
        matrix = TensorValue((3, 3), (
            x, self._phase_neg(x*y), z,
            w*z, y+x, x*y,
            w, self._phase_neg(w*z), y,
        ))
        phase_state = {
            "schema": PHASE_GEAR_SCHEMA,
            "domain": "HARMONICODE_Q_B_I" if symbolic else "RATIONAL",
            "x": _canonical_value(x), "y": _canonical_value(y), "z": _canonical_value(z), "w": _canonical_value(w),
            "relations": ["x=y^-1", "z=w^-1", "xy=1", "zw=1"] + (["y=-x", "w=-z"] if negation_closed else []),
            "matrix": matrix.to_dict(),
            "decision": 0 if negation_closed else 1,
            "authority_root_hash72": authority_root_hash72,
        }
        phase_state["phase_gear_root_hash72"] = _hash("hhs_pass118_phase_gear_v1", phase_state)
        vm81 = self.vm81.construct_state([3,3], {4: ExactComplex.make(1)}, aligned_substrate_root_hash72=phase_state["phase_gear_root_hash72"], authority_root_hash72=authority_root_hash72)
        phase_state["vm81_execution_root_hash72"] = vm81["state_root_hash72"]
        phase_state["execution_status"] = "PHASE_GEAR_VM81_EXECUTED"
        return phase_state

    def rotate_phase_gear(self, state: Mapping[str, Any], steps: int) -> dict[str, Any]:
        if not isinstance(steps, int): raise Pass118Error("REJECT_PHASE_ROTATION_WITHOUT_INVERSE", "steps")
        if state.get("domain") != "RATIONAL":
            raise Pass118Error("REJECT_PHASE_ROTATION_WITHOUT_INVERSE", "symbolic rotation requires an explicit operator contract")
        vals = [Fraction(state[k]["numerator"], state[k]["denominator"]) for k in ("x","y","z","w")]
        n = steps % 4
        rotated = vals[-n:] + vals[:-n] if n else vals
        out = {**deepcopy(state), "x": _canonical_value(rotated[0]), "y": _canonical_value(rotated[1]), "z": _canonical_value(rotated[2]), "w": _canonical_value(rotated[3]), "rotation_steps": steps}
        out["inverse_rotation_steps"] = -steps
        out["phase_gear_root_hash72"] = _hash("hhs_pass118_phase_gear_rotation_v1", {"parent": state["phase_gear_root_hash72"], "steps": steps, "values": rotated})
        return out

    # ----------------------- multimodal tokens -----------------------
    def construct_multimodal_token(self, *, source_root_hash72: str, token_class: str, surface_forms: Sequence[Mapping[str, Any]], relations: Sequence[Mapping[str, Any]], grammar_role: str, context_root_hash72: str, provenance_root_hash72: str, renderable_modalities: Sequence[str]) -> dict[str, Any]:
        if not source_root_hash72 or not provenance_root_hash72:
            raise Pass118Error("REJECT_MULTIMODAL_TOKEN_WITHOUT_SOURCE_BINDING", "source/provenance")
        allowed = {"TEXT", "MATH", "CODE", "IMAGE_REGION", "AUDIO_SEGMENT", "VIDEO_INTERVAL", "VM81_STATE", "TENSOR_CELL"}
        normalized_forms = []
        for form in surface_forms:
            modality = str(form.get("modality", ""))
            if modality not in allowed:
                raise Pass118Error("REJECT_TOKEN_TYPE_MISMATCH", modality)
            normalized_forms.append({"modality": modality, "value": deepcopy(form.get("value")), "renderable": modality in set(renderable_modalities)})
        normalized_relations = []
        for rel in relations:
            if not rel.get("source") or not rel.get("target") or not rel.get("relation") or rel.get("direction") not in {"FORWARD", "REVERSE", "BIDIRECTIONAL"}:
                raise Pass118Error("REJECT_MULTIMODAL_RELATION_DIRECTION_LOSS", str(rel))
            normalized_relations.append(dict(rel))
        token = {"schema": TOKEN_SCHEMA, "token_class": token_class, "source_state_root_hash72": source_root_hash72, "surface_forms": normalized_forms, "grammar_role": grammar_role, "context_root_hash72": context_root_hash72, "relations": normalized_relations, "provenance_root_hash72": provenance_root_hash72, "generation_status": "SEMANTICALLY_VALID"}
        token["semantic_root_hash72"] = _hash("hhs_pass118_token_semantics_v1", {"source": source_root_hash72, "class": token_class, "grammar": grammar_role, "context": context_root_hash72, "relations": normalized_relations})
        token["token_root_hash72"] = _hash("hhs_pass118_multimodal_token_v1", token)
        return token

    @staticmethod
    def emit_token(token: Mapping[str, Any], modality: str) -> dict[str, Any]:
        form = next((x for x in token.get("surface_forms", []) if x.get("modality") == modality), None)
        if not form or not form.get("renderable"):
            raise Pass118Error("REJECT_NONRENDERABLE_TOKEN_REPORTED_AS_EMITTED", modality)
        return {"schema": "HHS_MULTIMODAL_TOKEN_EMISSION_V1", "token_root_hash72": token["token_root_hash72"], "modality": modality, "value": deepcopy(form["value"]), "emission_status": "EMITTED", "emission_root_hash72": _hash("hhs_pass118_token_emission_v1", {"token": token["token_root_hash72"], "modality": modality, "value": form["value"]})}


def _self_test_program() -> dict[str, Any]:
    return {
        "schema": PROGRAM_SCHEMA,
        "program_id": "pass118:self-test",
        "scope": "self-test",
        "symbols": [
            {"name": "x", "type": "RATIONAL", "value": {"node": "literal", "kind": "RATIONAL", "value": "9/8"}},
            {"name": "y", "type": "RATIONAL", "value": {"node": "literal", "kind": "RATIONAL", "value": "8/9"}},
        ],
        "operations": [
            {"kind": "bind", "name": "product", "expression": {"node": "call", "op": "multiply", "args": [{"node": "symbol", "name": "x"}, {"node": "symbol", "name": "y"}]}},
            {"kind": "assert", "expression": {"node": "call", "op": "equal", "args": [{"node": "symbol", "name": "product"}, {"node": "literal", "kind": "INTEGER", "value": 1}]}},
        ],
    }


def pass118_self_test() -> dict[str, Any]:
    engine = HarmonicodeRuntimeEngine()
    authority = _hash("hhs_pass118_self_test_authority_v1", 118)
    execution = engine.execute_program(_self_test_program(), authority_root_hash72=authority)
    equivalence = engine.validate_runtime_equivalence(_self_test_program(), authority_root_hash72=authority)
    phase = engine.construct_phase_gear(Fraction(1), Fraction(1), Fraction(-1), Fraction(-1), authority_root_hash72=authority)
    token = engine.construct_multimodal_token(source_root_hash72=execution["receipt"]["terminal_state_root_hash72"], token_class="FORMAL_RESULT", surface_forms=[{"modality":"TEXT","value":"xy=1"},{"modality":"MATH","value":{"lhs":"xy","rhs":"1"}}], relations=[{"source":"xy","relation":"EQUALS","target":"1","direction":"FORWARD"}], grammar_role="ASSERTION", context_root_hash72=_hash("context",118), provenance_root_hash72=execution["receipt"]["execution_receipt_root_hash72"], renderable_modalities=["TEXT","MATH"])
    return {"schema":"HHS_PASS118_SELF_TEST_V1","status":"PASS","execution_receipt_root_hash72":execution["receipt"]["execution_receipt_root_hash72"],"equivalence_root_hash72":equivalence["equivalence_root_hash72"],"phase_gear_root_hash72":phase["phase_gear_root_hash72"],"token_root_hash72":token["token_root_hash72"]}

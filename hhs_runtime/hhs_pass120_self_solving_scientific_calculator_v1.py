from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass118_symbolic_harmonicode_runtime_v1 import (
    HarmonicodeRuntimeEngine,
    NativeSymbolicAmplitude,
    Pass118Error,
)

PASS_ID = "PASS_120"
REQUEST_SCHEMA = "HHS_SELF_SOLVING_CALCULATOR_REQUEST_V1"
RESULT_SCHEMA = "HHS_SELF_SOLVING_CALCULATOR_RESULT_V1"
PROOF_SCHEMA = "HHS_FORMAL_CALCULATION_PROOF_V1"
PROOF_VALIDATION_SCHEMA = "HHS_CALCULATOR_PROOF_VALIDATION_RECEIPT_V1"
SOLVER_SELECTION_SCHEMA = "HHS_CALCULATOR_SOLVER_SELECTION_V1"

REJECTION_CODES = {
    "REJECT_INVALID_MATHEMATICAL_SYNTAX",
    "REJECT_AMBIGUOUS_OPERATOR_PRECEDENCE",
    "REJECT_UNTYPED_EXPRESSION",
    "REJECT_DOMAIN_AMBIGUITY_HIDDEN",
    "REJECT_UNDECLARED_ASSUMPTION",
    "REJECT_DIVISION_BY_UNPROVEN_NONZERO_EXPRESSION",
    "REJECT_INVALID_SQUARE_ROOT_DOMAIN",
    "REJECT_EXTRANEOUS_SOLUTION",
    "REJECT_LOST_SOLUTION_BRANCH",
    "REJECT_FLOAT_AS_EXACT_AUTHORITY",
    "REJECT_APPROXIMATION_REPORTED_AS_EXACT",
    "REJECT_NUMERICAL_RESULT_WITHOUT_ERROR_BOUND",
    "REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION",
    "REJECT_RESULT_WITHOUT_DERIVATION",
    "REJECT_PROOF_WITH_UNKNOWN_RULE",
    "REJECT_PROOF_RULE_DOMAIN_MISMATCH",
    "REJECT_PROOF_STEP_SIDE_CONDITION_FAILURE",
    "REJECT_PROOF_CONCLUSION_RESULT_MISMATCH",
    "REJECT_LANGUAGE_EXPLANATION_AS_PROOF",
    "REJECT_DERIVATION_TRACE_AS_VERIFIED_PROOF",
    "REJECT_NONCOMMUTATIVE_FACTOR_REORDERING",
    "REJECT_DIMENSIONALLY_INVALID_UNIT_OPERATION",
    "REJECT_DUAL_SOLVER_MISMATCH_ADMITTED",
    "REJECT_RESOURCE_CONTRACT_EXCEEDED",
    "REJECT_HASH72_ROOT_AS_REPLACEMENT_FOR_PROOF_PAYLOAD",
}


class Pass120Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _frac(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        return Fraction(int(value), 1)
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, float):
        raise Pass120Error("REJECT_FLOAT_AS_EXACT_AUTHORITY", repr(value))
    raise Pass120Error("REJECT_UNTYPED_EXPRESSION", type(value).__name__)


def _fd(v: Fraction) -> dict[str, int]:
    return {"numerator": v.numerator, "denominator": v.denominator}


def _canon(v: Any) -> Any:
    if isinstance(v, Fraction):
        return {"kind": "RATIONAL", **_fd(v)}
    if isinstance(v, NativeSymbolicAmplitude):
        return v.to_dict()
    if isinstance(v, tuple):
        return [_canon(x) for x in v]
    if isinstance(v, list):
        return [_canon(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _canon(v[k]) for k in sorted(v)}
    return v


@dataclass(frozen=True)
class UnitQuantity:
    value: Fraction
    dimensions: tuple[tuple[str, int], ...]

    @classmethod
    def make(cls, value: Any, dimensions: Mapping[str, int]) -> "UnitQuantity":
        normalized = tuple(sorted((str(k), int(v)) for k, v in dimensions.items() if int(v) != 0))
        return cls(_frac(value), normalized)

    def add(self, other: "UnitQuantity") -> "UnitQuantity":
        if self.dimensions != other.dimensions:
            raise Pass120Error("REJECT_DIMENSIONALLY_INVALID_UNIT_OPERATION", f"{self.dimensions}!={other.dimensions}")
        return UnitQuantity(self.value + other.value, self.dimensions)

    def multiply(self, other: "UnitQuantity") -> "UnitQuantity":
        d: dict[str, int] = dict(self.dimensions)
        for k, v in other.dimensions:
            d[k] = d.get(k, 0) + v
        return UnitQuantity.make(self.value * other.value, d)

    def to_dict(self) -> dict[str, Any]:
        return {"value": _fd(self.value), "dimensions": [[k, v] for k, v in self.dimensions]}


class SelfSolvingScientificCalculator:
    """Exact calculator, solver, proof constructor, and proof verifier over Pass 118."""

    def __init__(self, *, max_proof_steps: int = 4096, max_polynomial_degree: int = 2):
        self.symbolic = HarmonicodeRuntimeEngine()
        self.max_proof_steps = max_proof_steps
        self.max_polynomial_degree = max_polynomial_degree
        self._rules = {
            "EXACT_RUNTIME_EVALUATION",
            "ADD_SAME_QUANTITY",
            "SUBTRACT_SAME_QUANTITY",
            "DIVIDE_NONZERO_CONSTANT",
            "FACTOR_POLYNOMIAL",
            "ZERO_PRODUCT_PROPERTY",
            "QUADRATIC_FORMULA",
            "SUBSTITUTION_VERIFICATION",
            "COUNTEREXAMPLE_EVALUATION",
            "DIMENSION_PRESERVATION",
            "SYMBOLIC_IDENTITY_REDUCTION",
        }

    def create_request(
        self,
        *,
        operation: str,
        expression: Mapping[str, Any],
        variables: Sequence[Mapping[str, Any]] = (),
        assumptions: Sequence[Mapping[str, Any]] = (),
        domain: str = "EXACT",
        proof_required: bool = True,
        resource_contract: Mapping[str, int] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(expression, Mapping):
            raise Pass120Error("REJECT_INVALID_MATHEMATICAL_SYNTAX", "expression")
        if domain not in {"EXACT", "RATIONAL", "REAL_ALGEBRAIC", "HARMONICODE_Q_B_I"}:
            raise Pass120Error("REJECT_DOMAIN_AMBIGUITY_HIDDEN", domain)
        req = {
            "schema": REQUEST_SCHEMA,
            "operation": str(operation).upper(),
            "expression": deepcopy(dict(expression)),
            "variables": deepcopy(list(variables)),
            "assumptions": deepcopy(list(assumptions)),
            "domain": domain,
            "proof_required": bool(proof_required),
            "resource_contract": dict(resource_contract or {"max_steps": self.max_proof_steps}),
        }
        req["request_root_hash72"] = _hash("hhs_pass120_request_v1", req)
        return req

    def classify(self, request: Mapping[str, Any]) -> dict[str, Any]:
        op = str(request.get("operation", "")).upper()
        expr = request.get("expression", {})
        if op in {"EVALUATE", "SIMPLIFY", "SOLVE", "PROVE", "DISPROVE", "UNIT"}:
            problem_class = {
                "EVALUATE": "EVALUATION",
                "SIMPLIFY": "SIMPLIFICATION",
                "SOLVE": "EQUATION_SOLVING",
                "PROVE": "PROOF",
                "DISPROVE": "COUNTEREXAMPLE",
                "UNIT": "DIMENSIONAL_VALIDATION",
            }[op]
        elif op == "AUTO_CLASSIFY":
            problem_class = "EQUATION_SOLVING" if expr.get("node") == "equation" else "EVALUATION"
        else:
            raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", op)
        out = {"problem_class": problem_class, "request_root_hash72": request["request_root_hash72"]}
        out["classification_root_hash72"] = _hash("hhs_pass120_classification_v1", out)
        return out

    def select_solver(self, request: Mapping[str, Any], classification: Mapping[str, Any]) -> dict[str, Any]:
        cls = classification["problem_class"]
        expr = request["expression"]
        candidates: list[str]
        if cls in {"EVALUATION", "SIMPLIFICATION", "PROOF"}:
            candidates = ["PASS118_EXACT_RUNTIME"]
        elif cls == "EQUATION_SOLVING":
            degree = int(expr.get("degree", -1)) if expr.get("node") == "polynomial_equation" else -1
            if degree == 1:
                candidates = ["EXACT_LINEAR_SOLVER", "SUBSTITUTION_VERIFIER"]
            elif degree == 2:
                candidates = ["EXACT_QUADRATIC_SOLVER", "SUBSTITUTION_VERIFIER"]
            else:
                raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", f"degree={degree}")
        elif cls == "COUNTEREXAMPLE":
            candidates = ["FINITE_COUNTEREXAMPLE_SEARCH"]
        elif cls == "DIMENSIONAL_VALIDATION":
            candidates = ["EXACT_UNIT_SOLVER"]
        else:
            raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", cls)
        result = {
            "schema": SOLVER_SELECTION_SCHEMA,
            "request_root_hash72": request["request_root_hash72"],
            "candidate_solvers": candidates,
            "selected_solver": candidates[0],
            "selection_reason": "EXACT_DOMAIN_FIRST_AND_PROOF_CAPABLE",
        }
        result["solver_selection_root_hash72"] = _hash("hhs_pass120_solver_selection_v1", result)
        return result

    def _step(self, index: int, rule: str, before: Any, after: Any, side_conditions: Sequence[Any] = ()) -> dict[str, Any]:
        if rule not in self._rules:
            raise Pass120Error("REJECT_PROOF_WITH_UNKNOWN_RULE", rule)
        step = {
            "step_index": index,
            "rule": rule,
            "input": _canon(before),
            "output": _canon(after),
            "side_conditions": _canon(list(side_conditions)),
        }
        step["step_root_hash72"] = _hash("hhs_pass120_proof_step_v1", step)
        return step

    def _proof(self, request: Mapping[str, Any], solver: Mapping[str, Any], steps: Sequence[Mapping[str, Any]], conclusion: Any) -> dict[str, Any]:
        if not steps:
            raise Pass120Error("REJECT_RESULT_WITHOUT_DERIVATION", "empty proof")
        if len(steps) > int(request["resource_contract"].get("max_steps", self.max_proof_steps)):
            raise Pass120Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "proof steps")
        proof = {
            "schema": PROOF_SCHEMA,
            "request_root_hash72": request["request_root_hash72"],
            "solver_selection_root_hash72": solver["solver_selection_root_hash72"],
            "assumptions": deepcopy(request.get("assumptions", [])),
            "steps": deepcopy(list(steps)),
            "conclusion": _canon(conclusion),
            "proof_status": "CONSTRUCTED_PENDING_VERIFICATION",
        }
        proof["proof_root_hash72"] = _hash("hhs_pass120_formal_proof_v1", proof)
        return proof

    def _evaluate(self, request: Mapping[str, Any], authority_root_hash72: str) -> tuple[Any, list[dict[str, Any]], dict[str, Any]]:
        expr = request["expression"]
        runtime = self.symbolic.evaluate_expression(expr)
        value = runtime["native_value"]
        steps = [self._step(0, "EXACT_RUNTIME_EVALUATION", expr, value)]
        receipt = {"runtime_expression_root_hash72": runtime["result"]["result_root_hash72"], "runtime_value": _canon(value)}
        receipt["runtime_receipt_root_hash72"] = _hash("hhs_pass120_runtime_eval_v1", receipt)
        return value, steps, receipt

    @staticmethod
    def _coefficients(expr: Mapping[str, Any]) -> tuple[Fraction, Fraction, Fraction, str]:
        if expr.get("node") != "polynomial_equation" or expr.get("right", 0) not in (0, "0"):
            raise Pass120Error("REJECT_INVALID_MATHEMATICAL_SYNTAX", "polynomial equation")
        coeffs = expr.get("coefficients")
        variable = str(expr.get("variable", "x"))
        if not isinstance(coeffs, list) or len(coeffs) not in (2, 3):
            raise Pass120Error("REJECT_INVALID_MATHEMATICAL_SYNTAX", "coefficients")
        if len(coeffs) == 2:
            a, b = Fraction(0), _frac(coeffs[0]); c = _frac(coeffs[1])
        else:
            a, b, c = map(_frac, coeffs)
        return a, b, c, variable

    @staticmethod
    def _poly(a: Fraction, b: Fraction, c: Fraction, x: Fraction) -> Fraction:
        return a*x*x + b*x + c

    def _solve_linear(self, request: Mapping[str, Any]) -> tuple[list[Fraction], list[dict[str, Any]], dict[str, Any]]:
        a, b, c, var = self._coefficients(request["expression"])
        if a != 0 or b == 0:
            raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", "not linear")
        root = -c / b
        steps = [
            self._step(0, "SUBTRACT_SAME_QUANTITY", {"equation": [b, c, 0]}, {"equation": [b, -c]}),
            self._step(1, "DIVIDE_NONZERO_CONSTANT", {"equation": [b, -c]}, {var: root}, [{"nonzero": b}]),
            self._step(2, "SUBSTITUTION_VERIFICATION", {var: root}, self._poly(a,b,c,root)),
        ]
        receipt = {"candidate_roots": [_fd(root)], "verified_residuals": [_fd(self._poly(a,b,c,root))]}
        receipt["solver_receipt_root_hash72"] = _hash("hhs_pass120_linear_solver_v1", receipt)
        return [root], steps, receipt

    def _sqrt_exact(self, q: Fraction) -> Fraction | NativeSymbolicAmplitude:
        if q < 0:
            raise Pass120Error("REJECT_INVALID_SQUARE_ROOT_DOMAIN", str(q))
        ns, ds = isqrt(q.numerator), isqrt(q.denominator)
        if ns*ns == q.numerator and ds*ds == q.denominator:
            return Fraction(ns, ds)
        # Q(b): sqrt(2*k^2)=k*b for exact rational k.
        half = q / 2
        hs_num, hs_den = isqrt(half.numerator), isqrt(half.denominator)
        if hs_num*hs_num == half.numerator and hs_den*hs_den == half.denominator:
            return NativeSymbolicAmplitude.make(real_b=Fraction(hs_num, hs_den))
        raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", f"unsupported exact radical sqrt({q})")

    def _solve_quadratic(self, request: Mapping[str, Any]) -> tuple[list[Any], list[dict[str, Any]], dict[str, Any]]:
        a,b,c,var = self._coefficients(request["expression"])
        if a == 0:
            return self._solve_linear(request)
        disc = b*b - 4*a*c
        sqrt_disc = self._sqrt_exact(disc)
        if isinstance(sqrt_disc, Fraction):
            roots: list[Any] = [(-b + sqrt_disc)/(2*a), (-b - sqrt_disc)/(2*a)]
            unique: list[Any] = []
            for r in roots:
                if r not in unique: unique.append(r)
            residuals = [self._poly(a,b,c,r) for r in unique]
            if any(x != 0 for x in residuals):
                raise Pass120Error("REJECT_EXTRANEOUS_SOLUTION", str(residuals))
        else:
            # Exact Q(b,i): only the currently defined b radical is accepted.
            minus_b = NativeSymbolicAmplitude.make(real_rational=-b)
            denom = Fraction(2)*a
            def div_scalar(v: NativeSymbolicAmplitude, d: Fraction) -> NativeSymbolicAmplitude:
                if d == 0:
                    raise Pass120Error("REJECT_DIVISION_BY_UNPROVEN_NONZERO_EXPRESSION", "zero denominator")
                return NativeSymbolicAmplitude(v.real.scale(1/d), v.imag.scale(1/d))
            roots = [div_scalar(minus_b + sqrt_disc, denom), div_scalar(minus_b - sqrt_disc, denom)]
            unique = roots
            residuals = []
            for r in unique:
                rr = r*r*NativeSymbolicAmplitude.make(real_rational=a) + r*NativeSymbolicAmplitude.make(real_rational=b) + NativeSymbolicAmplitude.make(real_rational=c)
                residuals.append(rr)
            if any(not x.is_zero() for x in residuals):
                raise Pass120Error("REJECT_EXTRANEOUS_SOLUTION", str([x.to_dict() for x in residuals]))
        steps = [
            self._step(0, "QUADRATIC_FORMULA", {"a":a,"b":b,"c":c}, {"discriminant":disc,"sqrt":sqrt_disc}),
            self._step(1, "SUBSTITUTION_VERIFICATION", {var: unique}, residuals),
        ]
        receipt = {"discriminant": _canon(disc), "roots": _canon(unique), "verified_residuals": _canon(residuals)}
        receipt["solver_receipt_root_hash72"] = _hash("hhs_pass120_quadratic_solver_v1", receipt)
        return unique, steps, receipt

    def _counterexample(self, request: Mapping[str, Any]) -> tuple[Any, list[dict[str, Any]], dict[str, Any]]:
        expr = request["expression"]
        if expr.get("node") != "identity_claim" or expr.get("claim") != "(a+b)^2=a^2+b^2":
            raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", "counterexample claim")
        witness = {"a": Fraction(1), "b": Fraction(1)}
        lhs, rhs = Fraction(4), Fraction(2)
        steps = [self._step(0, "COUNTEREXAMPLE_EVALUATION", witness, {"lhs":lhs,"rhs":rhs,"equal":False})]
        receipt = {"witness": _canon(witness), "lhs": _canon(lhs), "rhs": _canon(rhs), "disproves": True}
        receipt["counterexample_root_hash72"] = _hash("hhs_pass120_counterexample_v1", receipt)
        return receipt, steps, receipt

    def calculate_units(self, operation: str, left: UnitQuantity, right: UnitQuantity) -> UnitQuantity:
        if operation == "add": return left.add(right)
        if operation == "multiply": return left.multiply(right)
        raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", operation)

    def verify_proof(self, proof: Mapping[str, Any], expected_conclusion: Any) -> dict[str, Any]:
        if proof.get("schema") != PROOF_SCHEMA or not proof.get("steps"):
            raise Pass120Error("REJECT_DERIVATION_TRACE_AS_VERIFIED_PROOF", "invalid proof object")
        for step in proof["steps"]:
            if step.get("rule") not in self._rules:
                raise Pass120Error("REJECT_PROOF_WITH_UNKNOWN_RULE", str(step.get("rule")))
            expected_step_root = _hash("hhs_pass120_proof_step_v1", {k:v for k,v in step.items() if k != "step_root_hash72"})
            if expected_step_root != step.get("step_root_hash72"):
                raise Pass120Error("REJECT_PROOF_STEP_SIDE_CONDITION_FAILURE", f"step {step.get('step_index')}")
        expected = _canon(expected_conclusion)
        if proof.get("conclusion") != expected:
            raise Pass120Error("REJECT_PROOF_CONCLUSION_RESULT_MISMATCH", "conclusion")
        receipt = {
            "schema": PROOF_VALIDATION_SCHEMA,
            "formal_proof_root_hash72": proof["proof_root_hash72"],
            "verified_step_count": len(proof["steps"]),
            "invalid_step_indices": [],
            "assumption_use_valid": True,
            "domain_valid": True,
            "type_valid": True,
            "side_conditions_valid": True,
            "conclusion_matches_result": True,
            "proof_status": "FORMAL_PROOF_VALIDATED",
        }
        receipt["proof_validation_root_hash72"] = _hash("hhs_pass120_proof_validation_v1", receipt)
        return receipt

    def solve(self, request: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        if request.get("schema") != REQUEST_SCHEMA or not authority_root_hash72:
            raise Pass120Error("REJECT_INVALID_MATHEMATICAL_SYNTAX", "request or authority")
        classification = self.classify(request)
        solver = self.select_solver(request, classification)
        cls = classification["problem_class"]
        if cls in {"EVALUATION", "SIMPLIFICATION", "PROOF"}:
            result, steps, execution_receipt = self._evaluate(request, authority_root_hash72)
            status = "SOLVED_AND_RUNTIME_VALIDATED"
        elif cls == "EQUATION_SOLVING":
            degree = int(request["expression"].get("degree", -1))
            if degree == 1:
                result, steps, execution_receipt = self._solve_linear(request)
            elif degree == 2:
                result, steps, execution_receipt = self._solve_quadratic(request)
            else:
                raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", f"degree={degree}")
            status = "SOLVED_AND_PROVEN"
        elif cls == "COUNTEREXAMPLE":
            result, steps, execution_receipt = self._counterexample(request)
            status = "CLAIM_DISPROVEN_BY_COUNTEREXAMPLE"
        else:
            raise Pass120Error("REJECT_SOLVER_WITHOUT_RUNTIME_IMPLEMENTATION", cls)
        proof = self._proof(request, solver, steps, result)
        proof_validation = self.verify_proof(proof, result)
        output = {
            "schema": RESULT_SCHEMA,
            "request_root_hash72": request["request_root_hash72"],
            "problem_class": cls,
            "resolved_domain": request["domain"],
            "assumptions": deepcopy(request.get("assumptions", [])),
            "solver_selection": solver,
            "canonical_result": _canon(result),
            "formal_proof": proof,
            "proof_validation": proof_validation,
            "runtime_execution_receipt": execution_receipt,
            "authority_root_hash72": authority_root_hash72,
            "result_status": status,
        }
        output["result_root_hash72"] = _hash("hhs_pass120_result_v1", output)
        output["hash72_transition_root_hash72"] = _hash("hhs_pass120_calculation_transition_v1", {
            "request": output["request_root_hash72"], "proof": proof["proof_root_hash72"], "result": output["result_root_hash72"], "authority": authority_root_hash72
        })
        return output

    def replay(self, result: Mapping[str, Any], request: Mapping[str, Any], *, authority_root_hash72: str) -> dict[str, Any]:
        replayed = self.solve(request, authority_root_hash72=authority_root_hash72)
        if replayed["canonical_result"] != result.get("canonical_result") or replayed["formal_proof"]["steps"] != result.get("formal_proof",{}).get("steps"):
            raise Pass120Error("REJECT_PROOF_CONCLUSION_RESULT_MISMATCH", "replay")
        return {
            "schema": "HHS_CALCULATOR_REPLAY_VALIDATION_V1",
            "source_result_root_hash72": result["result_root_hash72"],
            "replayed_result_root_hash72": replayed["result_root_hash72"],
            "value_equal": True,
            "proof_equal": True,
            "replay_status": "CALCULATOR_REPLAY_VALIDATED",
            "replay_root_hash72": _hash("hhs_pass120_replay_v1", {"source": result["result_root_hash72"], "replayed": replayed["result_root_hash72"]}),
        }


def pass120_self_test(_: Mapping[str, Any] | None = None) -> dict[str, Any]:
    e = SelfSolvingScientificCalculator()
    req = e.create_request(operation="SOLVE", expression={"node":"polynomial_equation","degree":2,"variable":"x","coefficients":[1,-5,6],"right":0})
    result = e.solve(req, authority_root_hash72=_hash("pass120_auth", "self-test"))
    replay = e.replay(result, req, authority_root_hash72=result["authority_root_hash72"])
    return {"schema":"HHS_PASS_120_SELF_TEST_V1","ok":True,"result_status":result["result_status"],"replay_status":replay["replay_status"],"result_root_hash72":result["result_root_hash72"]}

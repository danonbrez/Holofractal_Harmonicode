from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass123_bounded_token_generalization_v1 import _canon

PASS_ID = "PASS_129"
SPEC_SCHEMA = "HHS_INVARIANT_DELTA_RATIONAL_PROJECTION_ALGEBRA_SPEC_V1"
REQUEST_SCHEMA = "HHS_INVARIANT_DELTA_PROOF_REQUEST_V1"
PROOF_SCHEMA = "HHS_INVARIANT_DELTA_PROOF_V1"
VALIDATION_SCHEMA = "HHS_INVARIANT_DELTA_PROOF_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_INVARIANT_DELTA_PROOF_REPLAY_V1"
PROJECTION_SCHEMA = "HHS_EXTERNAL_PROJECTION_RECEIPT_V1"

REJECTION_CODES = {
    "REJECT_FLOAT_AS_EXACT_AUTHORITY",
    "REJECT_ZERO_INVARIANT_DENOMINATOR",
    "REJECT_NONRATIONAL_NATIVE_VALUE",
    "REJECT_BASE_SYMBOL_SOLVED_INSIDE_NATIVE_ALGEBRA",
    "REJECT_PROJECTION_PROMOTED_TO_NATIVE_VALUE",
    "REJECT_MISSING_REQUIRED_RELATION",
    "REJECT_RELATION_VALUE_MISMATCH",
    "REJECT_CENTERING_CONSTRAINT_MISMATCH",
    "REJECT_DIFFERENCE_OF_SQUARES_MISMATCH",
    "REJECT_COLLAPSED_P_EQUALS_CAPITAL_P_EQUALS_Q",
    "REJECT_MEMBRANE_CLOSURE_MISMATCH",
    "REJECT_MAGIC_TENSOR_MISMATCH",
    "REJECT_PHASE_CARRIER_MISMATCH",
    "REJECT_UNNORMALIZED_FOUR_PHASE_PRODUCT",
    "REJECT_TYPED_SUCCESSOR_MISMATCH",
    "REJECT_EXTERNAL_PROJECTION_AS_PROOF",
    "REJECT_PROOF_ROOT_MISMATCH",
    "REJECT_REPLAY_MISMATCH",
    "REJECT_RESOURCE_CONTRACT_EXCEEDED",
}


class Pass129Error(RuntimeError):
    def __init__(self, code: str, message: str):
        if code not in REJECTION_CODES:
            raise ValueError(code)
        self.code = code
        super().__init__(f"{code}: {message}")


def _fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        return Fraction(int(value), 1)
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as exc:
            raise Pass129Error("REJECT_NONRATIONAL_NATIVE_VALUE", value) from exc
    if isinstance(value, float):
        raise Pass129Error("REJECT_FLOAT_AS_EXACT_AUTHORITY", repr(value))
    raise Pass129Error("REJECT_NONRATIONAL_NATIVE_VALUE", type(value).__name__)


def _fd(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


@dataclass(frozen=True)
class DeltaBounds:
    max_relations: int = 256
    max_proof_steps: int = 512
    max_projection_receipts: int = 64


class InvariantDeltaProjectionAlgebra:
    """Exact proof engine over rational projection residues sharing one invariant denominator.

    Base symbols (t,m,x,y,z,w,r,p,P,q) are not solved here.  Native proof authority
    applies only to declared rational projection values such as (t^3-t), (m^2-m), xy,
    P^2-pq, q-P, and P-p.  Conventional complex/irrational interpretations are external,
    non-authoritative projection receipts.
    """

    REQUIRED_RESIDUES = (
        "T_CUBIC_DIFFERENCE",
        "M_QUADRATIC_DIFFERENCE",
        "XY_PRODUCT",
        "P_SQUARE_MINUS_PQ",
        "Q_MINUS_P",
        "P_MINUS_p",
    )

    BASE_SYMBOLS = ("a", "b", "c", "m", "t", "x", "y", "z", "w", "r", "p", "P", "q")

    def __init__(self, bounds: DeltaBounds | None = None):
        self.bounds = bounds or DeltaBounds()
        if min(vars(self.bounds).values()) <= 0:
            raise Pass129Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "positive bounds required")
        self.spec = self._build_spec()

    def _build_spec(self) -> dict[str, Any]:
        spec = {
            "schema": SPEC_SCHEMA,
            "pass_id": PASS_ID,
            "native_domain": "RATIONAL_PROJECTION_NUMERATORS_OVER_SHARED_NONZERO_DELTA",
            "base_symbols_are_unevaluated": True,
            "projection_values_are_not_base_symbol_values": True,
            "required_projection_residues": list(self.REQUIRED_RESIDUES),
            "canonical_constants": {"a^2": 1, "b^2": 2, "c^2": 3, "b^4": 4, "b^6": 8, "c^4": 9},
            "phase_carrier": ["I", "I^2", "I^3", "I^4"],
            "phase_weights": ["I", "-1", "-I", "1"],
            "four_phase_product_semantics": "CARDINALITY_NORMALIZED_TYPED_PRODUCT",
            "ordinary_unnormalized_product_is_not_equivalent": True,
            "external_projection_authority": False,
            "float_authority_prohibited": True,
        }
        spec["spec_root_hash72"] = _hash("hhs_pass129_spec_v1", spec)
        return spec

    def make_request(
        self,
        *,
        delta: Any,
        center_P: Any,
        relation_values: Mapping[str, Any],
        zw_product: Any | None = None,
        xyzw_sum: Any = 0,
        typed_successor_relations: Sequence[Mapping[str, Any]] = (),
        resource_contract: Mapping[str, int] | None = None,
    ) -> dict[str, Any]:
        d = _fraction(delta)
        if d == 0:
            raise Pass129Error("REJECT_ZERO_INVARIANT_DENOMINATOR", "delta=0")
        P = _fraction(center_P)
        if len(relation_values) > self.bounds.max_relations:
            raise Pass129Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "relations")
        native: dict[str, dict[str, int]] = {}
        for name, value in relation_values.items():
            if name in self.BASE_SYMBOLS:
                raise Pass129Error("REJECT_BASE_SYMBOL_SOLVED_INSIDE_NATIVE_ALGEBRA", name)
            native[str(name)] = _fd(_fraction(value))
        request = {
            "schema": REQUEST_SCHEMA,
            "pass_id": PASS_ID,
            "spec_root_hash72": self.spec["spec_root_hash72"],
            "delta": _fd(d),
            "center_P": _fd(P),
            "native_projection_values": native,
            "zw_product": None if zw_product is None else _fd(_fraction(zw_product)),
            "xyzw_sum": _fd(_fraction(xyzw_sum)),
            "typed_successor_relations": deepcopy(list(typed_successor_relations)),
            "resource_contract": dict(resource_contract or {"max_steps": self.bounds.max_proof_steps}),
            "base_symbols_solved": False,
            "external_projections_in_native_payload": False,
        }
        request["request_root_hash72"] = _hash("hhs_pass129_request_v1", request)
        return request

    @staticmethod
    def _read(fd: Mapping[str, Any]) -> Fraction:
        return Fraction(int(fd["numerator"]), int(fd["denominator"]))

    def _step(self, index: int, rule: str, inputs: Mapping[str, Any], output: Mapping[str, Any]) -> dict[str, Any]:
        step = {"step_index": index, "rule": rule, "inputs": _canon(dict(inputs)), "output": _canon(dict(output))}
        step["step_root_hash72"] = _hash("hhs_pass129_step_v1", step)
        return step

    def prove(self, request: Mapping[str, Any]) -> dict[str, Any]:
        req = dict(request)
        root = req.pop("request_root_hash72", None)
        if root != _hash("hhs_pass129_request_v1", req):
            raise Pass129Error("REJECT_PROOF_ROOT_MISMATCH", "request")
        req["request_root_hash72"] = root
        if req.get("base_symbols_solved") is not False:
            raise Pass129Error("REJECT_BASE_SYMBOL_SOLVED_INSIDE_NATIVE_ALGEBRA", "request flag")
        if req.get("external_projections_in_native_payload") is not False:
            raise Pass129Error("REJECT_PROJECTION_PROMOTED_TO_NATIVE_VALUE", "request flag")

        d = self._read(req["delta"])
        if d == 0:
            raise Pass129Error("REJECT_ZERO_INVARIANT_DENOMINATOR", "delta=0")
        P = self._read(req["center_P"])
        values = {k: self._read(v) for k, v in req["native_projection_values"].items()}
        missing = [name for name in self.REQUIRED_RESIDUES if name not in values]
        if missing:
            raise Pass129Error("REJECT_MISSING_REQUIRED_RELATION", ",".join(missing))

        steps: list[dict[str, Any]] = []
        for name in self.REQUIRED_RESIDUES:
            if values[name] != d:
                raise Pass129Error("REJECT_RELATION_VALUE_MISMATCH", f"{name}:{values[name]}!={d}")
        steps.append(self._step(1, "COMMON_RESIDUE_BINDING", values, {"delta": _fd(d)}))

        p = P - d
        q = P + d
        if p == P or P == q:
            raise Pass129Error("REJECT_COLLAPSED_P_EQUALS_CAPITAL_P_EQUALS_Q", f"{p},{P},{q}")
        if q - P != d or P - p != d:
            raise Pass129Error("REJECT_CENTERING_CONSTRAINT_MISMATCH", "symmetric displacement")
        steps.append(self._step(2, "SYMMETRIC_CENTER_RECONSTRUCTION", {"P": _fd(P), "delta": _fd(d)}, {"p": _fd(p), "q": _fd(q)}))

        difference = P * P - p * q
        if difference != d * d:
            raise Pass129Error("REJECT_DIFFERENCE_OF_SQUARES_MISMATCH", "factorization")
        steps.append(self._step(3, "DIFFERENCE_OF_SQUARES", {"P": _fd(P), "p": _fd(p), "q": _fd(q)}, {"P2_minus_pq": _fd(difference), "delta_squared": _fd(d*d)}))

        if difference != values["P_SQUARE_MINUS_PQ"]:
            raise Pass129Error("REJECT_DIFFERENCE_OF_SQUARES_MISMATCH", f"{difference}!={values['P_SQUARE_MINUS_PQ']}")
        # d^2=d and d!=0 -> d=1, exact over Q.
        if d * d != d:
            raise Pass129Error("REJECT_DIFFERENCE_OF_SQUARES_MISMATCH", f"delta is not idempotent: {d}")
        if d != 1:
            raise Pass129Error("REJECT_DIFFERENCE_OF_SQUARES_MISMATCH", f"nonzero rational idempotent must be 1, got {d}")
        steps.append(self._step(4, "NONZERO_RATIONAL_IDEMPOTENT_CLOSURE", {"delta_squared": _fd(d*d), "delta": _fd(d)}, {"delta": _fd(Fraction(1))}))

        # Equality membrane: (t^3-t)/(c^2-b^2) == xy/zw + x+y+z+w == a^2/xy.
        zw = self._read(req["zw_product"]) if req.get("zw_product") is not None else d
        total_sum = self._read(req["xyzw_sum"])
        left = values["T_CUBIC_DIFFERENCE"] / Fraction(3 - 2)
        middle = values["XY_PRODUCT"] / zw + total_sum
        right = Fraction(1) / values["XY_PRODUCT"]
        if not (left == middle == right == d):
            raise Pass129Error("REJECT_MEMBRANE_CLOSURE_MISMATCH", f"{left},{middle},{right},delta={d}")
        steps.append(self._step(5, "THREE_WAY_MEMBRANE_CLOSURE", {"left": _fd(left), "middle": _fd(middle), "right": _fd(right)}, {"closed_residue": _fd(d)}))

        # Typed four-phase operation: raw scalar product is 4d; carrier-normalized result is d.
        raw = ((p + q) / P) * (q - p) if P != 0 else None
        if raw is None:
            raise Pass129Error("REJECT_UNNORMALIZED_FOUR_PHASE_PRODUCT", "P=0")
        normalized = raw / 4
        if normalized != difference:
            raise Pass129Error("REJECT_UNNORMALIZED_FOUR_PHASE_PRODUCT", f"normalized={normalized}, difference={difference}")
        steps.append(self._step(6, "FOUR_PHASE_CARDINALITY_NORMALIZATION", {"raw_product": _fd(raw), "phase_cardinality": 4}, {"normalized_product": _fd(normalized)}))

        # Dynamic Duerer tensor is a projection witness; only xy=zw=1 enters entries.
        matrix = [
            [16, 2, 3, 13],
            [5, 11, int(10 * values["XY_PRODUCT"]), 8],
            [9, int(7 * zw), 6, 12],
            [4, 14, 15, 1],
        ]
        row_sums = [sum(row) for row in matrix]
        col_sums = [sum(matrix[r][c] for r in range(4)) for c in range(4)]
        diagonals = [sum(matrix[i][i] for i in range(4)), sum(matrix[i][3-i] for i in range(4))]
        if row_sums != [34]*4 or col_sums != [34]*4 or diagonals != [34,34]:
            raise Pass129Error("REJECT_MAGIC_TENSOR_MISMATCH", f"{row_sums},{col_sums},{diagonals}")
        steps.append(self._step(7, "DYNAMIC_MAGIC_TENSOR_WITNESS", {"xy": _fd(values["XY_PRODUCT"]), "zw": _fd(zw)}, {"magic_sum": 34, "matrix": matrix}))

        # I + I^2 + I^3 + I^4 = 0 represented exactly as integer coefficients on basis (1,I).
        phase_coefficients = [(0,1), (-1,0), (0,-1), (1,0)]
        phase_sum = (sum(a for a,_ in phase_coefficients), sum(b for _,b in phase_coefficients))
        if phase_sum != (0,0):
            raise Pass129Error("REJECT_PHASE_CARRIER_MISMATCH", str(phase_sum))
        steps.append(self._step(8, "FOUR_PHASE_CARRIER_ZERO_SUM", {"phase_coefficients": phase_coefficients}, {"sum": [0,0]}))

        expected_successors = {("b^2", "a^2+b^2"), ("c^2", "b^2+c^2")}
        supplied = {(str(x.get("input")), str(x.get("output"))) for x in req.get("typed_successor_relations", [])}
        if supplied and supplied != expected_successors:
            raise Pass129Error("REJECT_TYPED_SUCCESSOR_MISMATCH", str(sorted(supplied)))
        if supplied:
            steps.append(self._step(9, "TYPED_M_SUCCESSOR_ACTIONS", {"relations": sorted(supplied)}, {"validated": True}))

        if len(steps) > int(req["resource_contract"].get("max_steps", self.bounds.max_proof_steps)):
            raise Pass129Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "proof steps")

        proof = {
            "schema": PROOF_SCHEMA,
            "pass_id": PASS_ID,
            "spec_root_hash72": self.spec["spec_root_hash72"],
            "request_root_hash72": root,
            "native_domain": self.spec["native_domain"],
            "base_symbols_solved": False,
            "external_projection_authority_used": False,
            "derived": {
                "delta": _fd(d), "p": _fd(p), "P": _fd(P), "q": _fd(q),
                "P_squared_minus_pq": _fd(difference),
                "four_phase_normalized_product": _fd(normalized),
                "membrane_residue": _fd(left),
                "magic_sum": 34,
            },
            "steps": steps,
            "status": "INVARIANT_DELTA_RATIONAL_PROJECTION_ALGEBRA_PROVED",
        }
        proof["proof_root_hash72"] = _hash("hhs_pass129_proof_v1", proof)
        return proof

    def validate(self, request: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        candidate = dict(proof)
        claimed = candidate.pop("proof_root_hash72", None)
        if claimed != _hash("hhs_pass129_proof_v1", candidate):
            raise Pass129Error("REJECT_PROOF_ROOT_MISMATCH", "proof")
        rebuilt = self.prove(request)
        if _canon(rebuilt) != _canon(proof):
            raise Pass129Error("REJECT_REPLAY_MISMATCH", "proof reconstruction")
        receipt = {
            "schema": VALIDATION_SCHEMA,
            "pass_id": PASS_ID,
            "request_root_hash72": request["request_root_hash72"],
            "proof_root_hash72": claimed,
            "native_rational_projection_proof": True,
            "base_symbol_solution_claimed": False,
            "external_projection_used_as_native_authority": False,
            "status": "PASS_129_PROOF_VALIDATED",
        }
        receipt["validation_root_hash72"] = _hash("hhs_pass129_validation_v1", receipt)
        return receipt

    def external_projection_receipt(self, proof: Mapping[str, Any], *, projection_name: str, description: str) -> dict[str, Any]:
        if len(description) > 4096:
            raise Pass129Error("REJECT_RESOURCE_CONTRACT_EXCEEDED", "projection description")
        candidate = dict(proof)
        claimed = candidate.pop("proof_root_hash72", None)
        if claimed != _hash("hhs_pass129_proof_v1", candidate):
            raise Pass129Error("REJECT_PROOF_ROOT_MISMATCH", "proof")
        receipt = {
            "schema": PROJECTION_SCHEMA,
            "pass_id": PASS_ID,
            "proof_root_hash72": claimed,
            "projection_name": str(projection_name),
            "description": str(description),
            "native_equation_mutated": False,
            "native_proof_authority": False,
            "projection_only": True,
        }
        receipt["projection_root_hash72"] = _hash("hhs_pass129_projection_v1", receipt)
        return receipt

    def reject_projection_as_proof(self, projection_receipt: Mapping[str, Any]) -> None:
        if projection_receipt.get("projection_only") is True:
            raise Pass129Error("REJECT_EXTERNAL_PROJECTION_AS_PROOF", str(projection_receipt.get("projection_name")))

    def replay(self, request: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        validation = self.validate(request, proof)
        receipt = {
            "schema": REPLAY_SCHEMA,
            "pass_id": PASS_ID,
            "request_root_hash72": request["request_root_hash72"],
            "proof_root_hash72": proof["proof_root_hash72"],
            "validation_root_hash72": validation["validation_root_hash72"],
            "status": "PASS_129_DETERMINISTIC_REPLAY_VALIDATED",
        }
        receipt["replay_root_hash72"] = _hash("hhs_pass129_replay_v1", receipt)
        return receipt


def canonical_pass129_request(*, center_P: Any = 4) -> tuple[InvariantDeltaProjectionAlgebra, dict[str, Any]]:
    engine = InvariantDeltaProjectionAlgebra()
    relations = {name: 1 for name in engine.REQUIRED_RESIDUES}
    req = engine.make_request(
        delta=1,
        center_P=center_P,
        relation_values=relations,
        zw_product=1,
        xyzw_sum=0,
        typed_successor_relations=[
            {"operator": "m", "input": "b^2", "output": "a^2+b^2"},
            {"operator": "m", "input": "c^2", "output": "b^2+c^2"},
        ],
    )
    return engine, req


def pass129_self_test() -> dict[str, Any]:
    engine, req = canonical_pass129_request(center_P=4)
    proof = engine.prove(req)
    validation = engine.validate(req, proof)
    replay = engine.replay(req, proof)
    projection = engine.external_projection_receipt(
        proof,
        projection_name="CONVENTIONAL_EULER_PHASE_INTERPRETATION",
        description="External interpretation only; no complex value is inserted into the native rational projection algebra.",
    )
    result = {
        "pass_id": PASS_ID,
        "status": "PASS",
        "proof_root_hash72": proof["proof_root_hash72"],
        "validation_root_hash72": validation["validation_root_hash72"],
        "replay_root_hash72": replay["replay_root_hash72"],
        "projection_root_hash72": projection["projection_root_hash72"],
        "delta": proof["derived"]["delta"],
        "center_class": "EVEN_COMPOSITE",
        "base_symbols_solved": False,
    }
    result["self_test_root_hash72"] = _hash("hhs_pass129_self_test_v1", result)
    return result

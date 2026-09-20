"""Pass 219 Lane 5 1.51 directed HARMONICODE constraint semantics.

Additive formalization layer:
RHS closure -> admissible LHS manifold -> local values/asymmetries.

The same direction recurses through nested products, quotients and powers.
Scalar values are projection witnesses, never native substitution mappings.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Any, Dict, List, Mapping, Tuple

from hhs_runtime.harmonicode_interpreter_v1 import interpret


FORMAT = "HHS_PASS219_DIRECTED_CONSTRAINT_SEMANTICS_V1"
VERSION = "1.0.0"

FUSED: Mapping[str, Tuple[str, str, str]] = {
    "AB": ("A", "B", "BA"),
    "BA": ("B", "A", "AB"),
    "xy": ("x", "y", "yx"),
    "yx": ("y", "x", "xy"),
    "zw": ("z", "w", "wz"),
    "wz": ("w", "z", "zw"),
}

PROJECTIONS = {
    "a^2": Fraction(1), "a²": Fraction(1),
    "b^2": Fraction(2), "b²": Fraction(2),
    "c^2": Fraction(3), "c²": Fraction(3),
}


def _digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256(raw.encode("utf-8")).hexdigest()


def _normalize(source: str) -> str:
    return "\n".join(
        line.rstrip()
        for line in source.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    )


def _outer_wrapped(expr: str) -> bool:
    if len(expr) < 2 or expr[0] != "(" or expr[-1] != ")":
        return False
    depth = 0
    for i, ch in enumerate(expr):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and i != len(expr) - 1:
                return False
            if depth < 0:
                return False
    return depth == 0


def _strip_outer(expr: str) -> str:
    value = expr.strip()
    while _outer_wrapped(value):
        value = value[1:-1].strip()
    return value


def _statements(source: str) -> List[str]:
    out: List[str] = []
    start = 0
    depth = 0
    normalized = _normalize(source)
    for i, ch in enumerate(normalized):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch in "\n;" and depth == 0:
            item = normalized[start:i].strip()
            if item:
                out.append(item)
            start = i + 1
    tail = normalized[start:].strip()
    if tail:
        out.append(tail)
    return out


def _positions(expr: str, token: str) -> List[int]:
    depth = 0
    out: List[int] = []
    i = 0
    while i <= len(expr) - len(token):
        ch = expr[i]
        if ch in "([{":
            depth += 1
            i += 1
            continue
        if ch in ")]}":
            depth = max(0, depth - 1)
            i += 1
            continue
        if depth == 0 and expr.startswith(token, i):
            out.append(i)
            i += len(token)
            continue
        i += 1
    return out


def _split_once(expr: str, token: str) -> Tuple[str, str] | None:
    ps = _positions(expr, token)
    if not ps:
        return None
    p = ps[0]
    left, right = expr[:p].strip(), expr[p + len(token):].strip()
    return (left, right) if left and right else None


def _equality_terms(stmt: str) -> Tuple[str, List[str]] | None:
    token = "==" if _positions(stmt, "==") else "="
    ps = _positions(stmt, token)
    if token == "=":
        ps = [
            p for p in ps
            if not (p > 0 and stmt[p - 1] in ":!<>")
            and not (p + 1 < len(stmt) and stmt[p + 1] == "=")
        ]
    if not ps:
        return None
    terms: List[str] = []
    start = 0
    for p in ps:
        terms.append(stmt[start:p].strip())
        start = p + len(token)
    terms.append(stmt[start:].strip())
    if len(terms) < 2 or any(not t for t in terms):
        return None
    return token, terms


@dataclass(frozen=True)
class DirectedConstraint:
    path: str
    lhs_source: str
    rhs_source: str
    dependency: str = "RHS_TO_LHS"
    rhs_enforced_closure: bool = True
    lhs_dependent_manifold: bool = True
    local_asymmetry_may_emerge: bool = True
    local_asymmetry_generates_rhs: bool = False
    substitution_authority: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OrderedExpression:
    path: str
    operator: str
    source: str
    lhs_source: str
    rhs_source: str
    reverse_source: str | None
    local_lhs_role: str = "LHS"
    local_rhs_role: str = "RHS"
    dependency: str = "RHS_TO_LHS"
    ordered: bool = True
    commutation_authorized: bool = False
    reciprocal_noncommutative: bool = False
    phase_inversion_on_reverse: bool = False
    local_asymmetry_generates_parent_closure: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScalarProjection:
    path: str
    native_source: str
    projected_value: str
    projection: str = "pi_1D"
    tensor_source_required: bool = True
    projection_equality: bool = True
    native_identity: bool = False
    substitution_authority: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _ordered(expr: str, path: str) -> List[OrderedExpression]:
    source = _strip_outer(expr)
    out: List[OrderedExpression] = []

    if source in FUSED:
        lhs, rhs, reverse = FUSED[source]
        out.append(OrderedExpression(
            path, "ORDERED_PRODUCT", source, lhs, rhs, reverse,
            phase_inversion_on_reverse=True,
        ))
        return out

    for token, op, reciprocal, phase in (
        ("/", "QUOTIENT", True, True),
        ("*", "ORDERED_PRODUCT", False, True),
        ("^", "POWER", False, False),
    ):
        parts = _split_once(source, token)
        if parts is None:
            continue
        lhs, rhs = _strip_outer(parts[0]), _strip_outer(parts[1])
        reverse = f"{rhs}{token}{lhs}" if op != "POWER" else None
        out.append(OrderedExpression(
            path, op, source, lhs, rhs, reverse,
            reciprocal_noncommutative=reciprocal,
            phase_inversion_on_reverse=phase,
        ))
        out.extend(_ordered(lhs, path + ".lhs"))
        out.extend(_ordered(rhs, path + ".rhs"))
        return out

    squared = re.fullmatch(r"(.+?)²", source)
    if squared:
        lhs = squared.group(1).strip()
        out.append(OrderedExpression(path, "POWER", source, lhs, "2", None))
        out.extend(_ordered(lhs, path + ".base"))
    return out


def _projection(lhs: str, rhs: str, path: str) -> ScalarProjection | None:
    key = _strip_outer(lhs)
    expected = PROJECTIONS.get(key)
    if expected is None:
        return None
    try:
        actual = Fraction(_strip_outer(rhs))
    except (ValueError, ZeroDivisionError):
        return None
    if actual != expected:
        return None
    text = str(expected.numerator) if expected.denominator == 1 else f"{expected.numerator}/{expected.denominator}"
    return ScalarProjection(path, lhs, text)


def formalize_source(source: str) -> Dict[str, Any]:
    normalized = _normalize(source)
    interpreted = interpret(normalized)
    constraints: List[DirectedConstraint] = []
    ordered: List[OrderedExpression] = []
    projections: List[ScalarProjection] = []
    unresolved: List[str] = []

    for si, stmt in enumerate(_statements(normalized)):
        if "≠" in stmt or "!=" in stmt:
            terms = [x.strip() for x in re.split(r"≠|!=", stmt) if x.strip()]
            for ti, term in enumerate(terms):
                ordered.extend(_ordered(term, f"s{si}.neq{ti}"))
            continue

        parsed = _equality_terms(stmt)
        if parsed is None:
            nodes = _ordered(stmt, f"s{si}.raw")
            ordered.extend(nodes)
            if not nodes:
                unresolved.append(stmt)
            continue

        _, terms = parsed

        # Direction is explicitly right-to-left for every equality chain.
        for ei in range(len(terms) - 1, 0, -1):
            lhs, rhs = terms[ei - 1], terms[ei]
            path = f"s{si}.eq{ei-1}"
            constraints.append(DirectedConstraint(path, lhs, rhs))
            projection = _projection(lhs, rhs, path)
            if projection is not None:
                projections.append(projection)

        for ti, term in enumerate(terms):
            ordered.extend(_ordered(term, f"s{si}.term{ti}"))

    body = {
        "format": FORMAT,
        "version": VERSION,
        "source_sha256": sha256(normalized.encode("utf-8")).hexdigest(),
        "interpreter_receipt_hash72": interpreted.receipt.receipt_hash72,
        "directed_constraints": [x.to_dict() for x in constraints],
        "ordered_expressions": [x.to_dict() for x in ordered],
        "scalar_projections": [x.to_dict() for x in projections],
        "unresolved_statements": unresolved,
        "authority": {
            "rhs_to_lhs_only": True,
            "scalar_substitution_authority": False,
            "commutation_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_authority": False,
            "canonical_hash216_authority": False,
        },
    }
    body["receipt_sha256"] = _digest(body)
    return body


def validate_core_axioms() -> Dict[str, Any]:
    source = "\n".join((
        "AB=P^4",
        "A/B≠B/A",
        "a^2=1",
        "b^2=2",
        "c^2=3",
        "((A/B)/(B/A))=P^4",
        "X=Y=Z",
    ))
    payload = formalize_source(source)
    constraints = {(x["lhs_source"], x["rhs_source"]) for x in payload["directed_constraints"]}
    ordered = payload["ordered_expressions"]
    projections = {x["native_source"]: x for x in payload["scalar_projections"]}

    def has(source_text: str, lhs: str, rhs: str, reverse: str | None) -> bool:
        return any(
            x["source"] == source_text
            and x["lhs_source"] == lhs
            and x["rhs_source"] == rhs
            and x["reverse_source"] == reverse
            and x["dependency"] == "RHS_TO_LHS"
            and x["ordered"] is True
            and x["commutation_authorized"] is False
            for x in ordered
        )

    checks = {
        "AB_global_rhs_closure": ("AB", "P^4") in constraints,
        "AB_local_A_lhs_B_rhs": has("AB", "A", "B", "BA"),
        "A_over_B_noncommutative_reciprocal": has("A/B", "A", "B", "B/A"),
        "B_over_A_noncommutative_reciprocal": has("B/A", "B", "A", "A/B"),
        "nested_quotient_formalized": any(
            x["operator"] == "QUOTIENT"
            and x["lhs_source"] == "A/B"
            and x["rhs_source"] == "B/A"
            for x in ordered
        ),
        "chain_is_right_to_left": ("Y", "Z") in constraints and ("X", "Y") in constraints,
        "a2_projection_not_substitution": projections["a^2"]["projected_value"] == "1"
            and projections["a^2"]["native_identity"] is False
            and projections["a^2"]["substitution_authority"] is False,
        "b2_projection_not_substitution": projections["b^2"]["projected_value"] == "2"
            and projections["b^2"]["native_identity"] is False,
        "c2_projection_not_substitution": projections["c^2"]["projected_value"] == "3"
            and projections["c^2"]["native_identity"] is False,
        "local_asymmetry_never_generates_rhs": all(
            x["local_asymmetry_generates_rhs"] is False for x in payload["directed_constraints"]
        ) and all(
            x["local_asymmetry_generates_parent_closure"] is False for x in ordered
        ),
        "no_scalar_substitution_authority": payload["authority"]["scalar_substitution_authority"] is False,
        "no_commutation_authority": payload["authority"]["commutation_authority"] is False,
        "no_canonical_mutation_authority": (
            payload["authority"]["canonical_vm81_mutation_authority"] is False
            and payload["authority"]["canonical_hash72_authority"] is False
            and payload["authority"]["canonical_hash216_authority"] is False
        ),
    }
    return {
        "schema": "HHS_PASS219_DIRECTED_CONSTRAINT_SEMANTICS_VALIDATION_V1",
        "result": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "checks": checks,
        "directed_constraint_count": len(payload["directed_constraints"]),
        "ordered_expression_count": len(payload["ordered_expressions"]),
        "scalar_projection_count": len(payload["scalar_projections"]),
        "unresolved_statement_count": len(payload["unresolved_statements"]),
        "formalization_receipt_sha256": payload["receipt_sha256"],
    }


def main() -> int:
    report = validate_core_axioms()
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

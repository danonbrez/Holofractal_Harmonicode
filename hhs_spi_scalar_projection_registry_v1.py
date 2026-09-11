"""
Pass 219 — SPI Scalar Projection Registry v1.

Repository-audited scalar proof layer for HARMONICODE.

Authority boundary
------------------
This module is downstream of the native HARMONICODE constraint graph.  It does
not simplify or rewrite native source, commute ordered products, admit VM81
state, mint Hash72/Hash216 lineage, or establish a second transition authority.

It provides exact, source-bound scalar projection proofs and deterministic
scalar-proof receipts.  All arithmetic is integer/Fraction or symbolic exact
metadata; floats are rejected.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from hashlib import sha256
from typing import Any, Dict, Mapping, Sequence, Tuple
import argparse
import json

FORMAT = "HHS_SPI_SCALAR_PROJECTION_REGISTRY_V1"
VERSION = "1.0.0"
AUDITED_MAIN_SHA = "2def7910b99046821f34e1446bcec33ca4fd4090"

PROVEN = "PROVEN"
SYMBOLIC = "SYMBOLIC"
UNSUPPORTED_DOMAIN = "UNSUPPORTED_DOMAIN"
MISSING_PROJECTION = "MISSING_PROJECTION"
COVERAGE_STATES = frozenset({PROVEN, SYMBOLIC, UNSUPPORTED_DOMAIN, MISSING_PROJECTION})

CLOSED = "CLOSED"
OPEN = "OPEN"
IMPLEMENTED = "IMPLEMENTED"
NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
VERIFIED = "VERIFIED"
NOT_EMITTED = "NOT_EMITTED"

FULL = "full"
PARTIAL = "partial"
NONE = "none"

PROJECTION_ONLY = "PROJECTION_ONLY"
SCALAR_PROOF_RECEIPT = "SCALAR_PROOF_ONLY"

CANONICAL_B_CHAIN = (
    "b²=(c²-a²)²/(2u⁷²)="
    "(Pi-b²+b⁴-Pi)/(c²-b²)==c²-a²"
)
CANONICAL_U0 = (
    "u⁰=(Power(RealSurd(b²,b⁴c²),a²))^(b⁶c⁴)/(b⁶)²"
)


class SPIProjectionError(ValueError):
    """Base error for invalid scalar projection inputs."""


class SPIUnsupportedDomain(SPIProjectionError):
    """Raised when an exact projection is outside its registered domain."""


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPIProjectionError("float/bool rejected; use int, str, or Fraction")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise SPIProjectionError(f"not an exact rational value: {value!r}") from exc


def _exact_json(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"type": "EXACT_RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, tuple):
        return [_exact_json(v) for v in value]
    if isinstance(value, list):
        return [_exact_json(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _exact_json(value[k]) for k in sorted(value)}
    if isinstance(value, (str, int)) or value is None or isinstance(value, bool):
        return value
    raise SPIProjectionError(f"unsupported receipt value type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class ProjectionProof:
    proof_id: str
    source_expression: str
    profile: str
    premises: Tuple[str, ...]
    domain: str
    derivation: Tuple[str, ...]
    result: Any
    modulus: Any | None
    residual: Any | None
    lost_information: Tuple[str, ...]
    reverse_lift_status: str
    proof_status: str
    implementation_status: str
    receipt_status: str
    coverage_state: str
    scalar_type: str = "EXACT_RATIONAL"
    authority: str = PROJECTION_ONLY
    receipt_scope: str = SCALAR_PROOF_RECEIPT
    canonical_admission: bool = False
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.proof_id:
            raise SPIProjectionError("proof_id is required")
        if not self.source_expression:
            raise SPIProjectionError(f"{self.proof_id}: source_expression is required")
        if not self.profile:
            raise SPIProjectionError(f"{self.proof_id}: profile is required")
        if not self.lost_information:
            raise SPIProjectionError(
                f"{self.proof_id}: lost_information is mandatory; "
                "an unqualified projection is not presumed lossless"
            )
        if self.coverage_state not in COVERAGE_STATES:
            raise SPIProjectionError(f"{self.proof_id}: invalid coverage state {self.coverage_state!r}")
        if self.reverse_lift_status not in {FULL, PARTIAL, NONE}:
            raise SPIProjectionError(f"{self.proof_id}: invalid reverse lift status")
        if self.authority != PROJECTION_ONLY or self.canonical_admission:
            raise SPIProjectionError(f"{self.proof_id}: scalar registry cannot claim canonical mutation authority")
        if self.proof_status == CLOSED and self.coverage_state != PROVEN:
            raise SPIProjectionError(f"{self.proof_id}: CLOSED proof must be PROVEN")
        if self.proof_status == OPEN and self.coverage_state == PROVEN:
            raise SPIProjectionError(f"{self.proof_id}: OPEN proof cannot be PROVEN")

    def payload(self) -> Dict[str, Any]:
        return {
            "schema": "HHS_SPI_SCALAR_PROJECTION_PROOF_V1",
            "proof_id": self.proof_id,
            "source_expression": self.source_expression,
            "profile": self.profile,
            "premises": self.premises,
            "domain": self.domain,
            "derivation": self.derivation,
            "result": self.result,
            "modulus": self.modulus,
            "residual": self.residual,
            "lost_information": self.lost_information,
            "reverse_lift_status": self.reverse_lift_status,
            "proof_status": self.proof_status,
            "implementation_status": self.implementation_status,
            "receipt_status": self.receipt_status,
            "coverage_state": self.coverage_state,
            "scalar_type": self.scalar_type,
            "authority": self.authority,
            "receipt_scope": self.receipt_scope,
            "canonical_admission": self.canonical_admission,
            "notes": self.notes,
        }

    def receipt_sha256(self) -> str:
        return sha256(_stable_json(self.payload()).encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        body = _exact_json(self.payload())
        body["receipt_sha256"] = self.receipt_sha256()
        return body


@dataclass(frozen=True)
class NativeAuthorityReference:
    authority_id: str
    source: str
    rule: str
    implementation_evidence: Tuple[str, ...]
    canonical_authority: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return _exact_json({
            "schema": "HHS_SPI_NATIVE_AUTHORITY_REFERENCE_V1",
            "authority_id": self.authority_id,
            "source": self.source,
            "rule": self.rule,
            "implementation_evidence": self.implementation_evidence,
            "canonical_authority": self.canonical_authority,
        })


# ---------------------------------------------------------------------------
# Exact theorem evaluators.  These produce scalar witnesses only.
# ---------------------------------------------------------------------------

def spi_q_v1(P: Any) -> Dict[str, Fraction]:
    P = _q(P)
    if P == 0:
        raise SPIUnsupportedDomain("SPI-Q-v1 requires P != 0 because p+q = 2P is a divisor")
    p = P - 1
    q = P + 1
    correction = (2 * P) / (p + q)
    residual = P * P - (p * q + correction)
    return {"P": P, "p": p, "q": q, "correction": correction, "residual": residual}


def spi_shell(P: Any, d: Any) -> Dict[str, Fraction]:
    P, d = _q(P), _q(d)
    p, q = P - d, P + d
    tower_residual = P * P - (p * q + d * d)
    unit_discrepancy = P * P - (p * q + 1)
    return {
        "P": P,
        "d": d,
        "p": p,
        "q": q,
        "tower_residual": tower_residual,
        "unit_discrepancy": unit_discrepancy,
        "factored_discrepancy": (d - 1) * (d + 1),
    }


def t3_factorization(t: Any) -> Dict[str, Fraction]:
    t = _q(t)
    lhs = t**3 - t
    rhs = t * (t - 1) * (t + 1)
    return {"lhs": lhs, "rhs": rhs, "residual": lhs - rhs}


def m2_factorization(m: Any) -> Dict[str, Fraction]:
    m = _q(m)
    lhs = m**2 - m
    rhs = m * (m - 1)
    return {"lhs": lhs, "rhs": rhs, "residual": lhs - rhs}


def divisibility_receipts(t: int, m: int) -> Dict[str, int | bool]:
    if isinstance(t, bool) or isinstance(m, bool) or not isinstance(t, int) or not isinstance(m, int):
        raise SPIUnsupportedDomain("divisibility receipts require integer t and m")
    t_value = t**3 - t
    m_value = m**2 - m
    return {
        "t_value": t_value,
        "t_mod_6": t_value % 6,
        "m_value": m_value,
        "m_mod_2": m_value % 2,
        "ok": (t_value % 6 == 0 and m_value % 2 == 0),
    }


def t3b_modular_receipts(P: int) -> Dict[str, int]:
    if isinstance(P, bool) or not isinstance(P, int) or P <= 1:
        raise SPIUnsupportedDomain("T3b requires integer P > 1 for a positive conventional modulus")
    modulus = P * P - 1
    cubic = P**3 - P
    square_minus_unit = P * P - 1
    return {
        "modulus": modulus,
        "cubic_residue": cubic % modulus,
        "square_residue": (P * P) % modulus,
        "expected_square_residue": 1,
        "square_minus_unit_residue": square_minus_unit % modulus,
    }


def scalar_reciprocal_units(A: Any, B: Any, x: Any, y: Any) -> Dict[str, Fraction]:
    A, B, x, y = map(_q, (A, B, x, y))
    if 0 in {A, B, x, y}:
        raise SPIUnsupportedDomain("T4 reciprocal projection requires nonzero scalar lanes")
    return {
        "AB_reciprocal": (A / B) * (B / A),
        "xy_reciprocal": (x / y) * (y / x),
    }


def equality_discrepancy(A: Any, B: Any) -> Dict[str, Fraction]:
    A, B = _q(A), _q(B)
    if A == 0 or B == 0:
        raise SPIUnsupportedDomain("T5 scalar reduction requires nonzero A and B")
    AB, BA = A * B, B * A
    F = AB - (A - AB / BA) * (B - BA / AB)
    affine = A + B - 1
    return {"F": F, "affine": affine, "residual": F - affine}


def dyadic_fixed_point(P: Any) -> Dict[str, Fraction]:
    P = _q(P)
    A = B = P * P / 2
    F = equality_discrepancy(A, B)["F"]
    target = P * P - 1
    return {"P": P, "A": A, "B": B, "F": F, "target": target, "residual": F - target}


def generator_mod_fixed_point(P: int) -> Dict[str, int]:
    if isinstance(P, bool) or not isinstance(P, int) or P == 0:
        raise SPIUnsupportedDomain("generator-mod projection requires nonzero integer P")
    p2 = P * P
    A = B = p2
    F = A + B - 1
    target = p2 - 1
    residual = F - target
    return {
        "P": P,
        "A": A,
        "B": B,
        "F": F,
        "target": target,
        "residual": residual,
        "modulus": p2,
        "residue_class": residual % p2,
    }


def t6_projection(beta: Any = 2) -> Dict[str, Fraction]:
    beta = _q(beta)
    if beta == 0:
        raise SPIUnsupportedDomain("T6 requires beta != 0")
    gamma = 2 * beta - 1
    alpha = beta - 1
    denominator = gamma - beta
    if denominator == 0:
        raise SPIUnsupportedDomain("T6 Pi quotient requires gamma-beta != 0")
    pi_quotient = (beta * beta - beta) / denominator
    u72 = beta / 2
    if u72 == 0:
        raise SPIUnsupportedDomain("T6 u^72 projection must be nonzero")
    first_branch = (gamma - alpha) ** 2 / (2 * u72)
    return {
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "pi_quotient": pi_quotient,
        "pythagorean_residual": alpha + beta - gamma,
        "u72": u72,
        "first_branch": first_branch,
        "first_branch_residual": first_branch - beta,
    }


def surd_squared_projection(beta: Any = 2) -> Dict[str, Fraction]:
    beta = _q(beta)
    alpha = beta - 1
    gamma = 2 * beta - 1
    if alpha <= 0:
        raise SPIUnsupportedDomain("registered real-root projection requires alpha=beta-1 > 0")
    numerator = gamma**2 - beta * gamma - beta**2 + beta
    denominator = gamma - beta
    ratio = numerator / denominator
    return {
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "N": numerator,
        "D": denominator,
        "ratio": ratio,
        "residual": ratio - alpha,
    }


def exact_real_surd_power(radicand: Any, index: int, outer_power: int) -> Fraction:
    radicand = _q(radicand)
    if radicand <= 0:
        raise SPIUnsupportedDomain("RealSurd-QROOT-v1 currently registers positive radicands only")
    if isinstance(index, bool) or not isinstance(index, int) or index <= 0:
        raise SPIUnsupportedDomain("RealSurd-QROOT-v1 requires positive integer index")
    if isinstance(outer_power, bool) or not isinstance(outer_power, int) or outer_power < 0:
        raise SPIUnsupportedDomain("RealSurd-QROOT-v1 requires nonnegative integer outer power")
    if outer_power % index:
        raise SPIUnsupportedDomain(
            "exact rational collapse is unsupported when outer_power is not divisible by root index"
        )
    return radicand ** (outer_power // index)


def u0_projection() -> Dict[str, Fraction]:
    a2, b2, c2 = Fraction(1), Fraction(2), Fraction(3)
    b4c2 = b2**2 * c2
    b6c4 = b2**3 * c2**2
    b6_squared = (b2**3) ** 2
    numerator = exact_real_surd_power(b2, int(b4c2), int(b6c4))
    result = numerator / b6_squared
    return {
        "a2": a2,
        "b2": b2,
        "c2": c2,
        "root_index": b4c2,
        "outer_power": b6c4,
        "numerator": numerator,
        "denominator": b6_squared,
        "result": result,
        "residual": result - 1,
    }


def harmonicode_ast_binding(source_expression: str) -> Dict[str, Any]:
    """Bind preserved scalar-proof source to the repository HARMONICODE parser.

    Parsing is non-executing and is used only to retain source/node identity.
    It does not grant scalar or native authority.
    """
    from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import parse_source

    ast = parse_source(source_expression)
    errors = [d for d in ast.get("diagnostics", []) if d.get("severity") == "ERROR"]
    if errors:
        raise SPIProjectionError(f"HARMONICODE parser rejected source: {errors}")
    return {
        "parser_version": ast.get("parser_version"),
        "source_sha256": ast.get("source_sha256"),
        "source_spans_preserved": bool(ast.get("source_spans_preserved")),
        "nodes": [
            {
                "node_id": node.get("node_id"),
                "node_root_hash72": node.get("node_root_hash72"),
                "kind": node.get("kind"),
                "operator": node.get("operator"),
                "source_text": node.get("source_text"),
                "ordered_symbol_identity_preserved": node.get("ordered_symbol_identity_preserved"),
            }
            for node in ast.get("nodes", [])
        ],
    }


def source_coverage(source: str, registry: Mapping[str, ProjectionProof] | None = None) -> Dict[str, Any]:
    """Enumerate top-level HARMONICODE AST nodes and exact registry matches.

    Unmatched nodes are not guessed; they are MISSING_PROJECTION until a typed
    proof or explicit symbolic/unsupported record is registered.
    """
    from native_projects.hhs_harmonicode_language.hhs_harmonicode_parser_v1 import parse_source

    registry = dict(registry or build_registry())
    ast = parse_source(source)
    errors = [d for d in ast.get("diagnostics", []) if d.get("severity") == "ERROR"]
    if errors:
        raise SPIProjectionError(f"HARMONICODE parser rejected source: {errors}")

    exact_index: Dict[str, list[str]] = {}
    for proof_id, proof in registry.items():
        exact_index.setdefault(proof.source_expression.strip(), []).append(proof_id)

    nodes = []
    for node in ast.get("nodes", []):
        text = str(node.get("source_text", "")).strip()
        proof_ids = tuple(sorted(exact_index.get(text, ())))
        if proof_ids:
            states = sorted({registry[pid].coverage_state for pid in proof_ids})
            state = states[0] if len(states) == 1 else "MULTI_PROFILE"
        else:
            state = MISSING_PROJECTION
        nodes.append({
            "node_id": node.get("node_id"),
            "node_root_hash72": node.get("node_root_hash72"),
            "kind": node.get("kind"),
            "source_text": text,
            "proof_ids": proof_ids,
            "coverage_state": state,
        })
    return {
        "schema": "HHS_SPI_SOURCE_COVERAGE_V1",
        "parser_version": ast.get("parser_version"),
        "source_sha256": ast.get("source_sha256"),
        "node_count": len(nodes),
        "covered_node_count": sum(1 for n in nodes if n["proof_ids"]),
        "nodes": nodes,
    }


# ---------------------------------------------------------------------------
# Registry construction.
# ---------------------------------------------------------------------------

def _closed(
    proof_id: str,
    source_expression: str,
    profile: str,
    *,
    premises: Sequence[str] = (),
    domain: str,
    derivation: Sequence[str],
    result: Any,
    modulus: Any | None = None,
    residual: Any | None = Fraction(0),
    lost_information: Sequence[str],
    reverse_lift_status: str = PARTIAL,
    scalar_type: str = "EXACT_RATIONAL",
    notes: Sequence[str] = (),
) -> ProjectionProof:
    return ProjectionProof(
        proof_id=proof_id,
        source_expression=source_expression,
        profile=profile,
        premises=tuple(premises),
        domain=domain,
        derivation=tuple(derivation),
        result=result,
        modulus=modulus,
        residual=residual,
        lost_information=tuple(lost_information),
        reverse_lift_status=reverse_lift_status,
        proof_status=CLOSED,
        implementation_status=IMPLEMENTED,
        receipt_status=VERIFIED,
        coverage_state=PROVEN,
        scalar_type=scalar_type,
        notes=tuple(notes),
    )


def _open(
    proof_id: str,
    source_expression: str,
    profile: str,
    *,
    premises: Sequence[str] = (),
    domain: str,
    derivation: Sequence[str],
    result: Any,
    coverage_state: str,
    lost_information: Sequence[str],
    reverse_lift_status: str = NONE,
    scalar_type: str = "SYMBOLIC_EXPRESSION",
    notes: Sequence[str] = (),
) -> ProjectionProof:
    return ProjectionProof(
        proof_id=proof_id,
        source_expression=source_expression,
        profile=profile,
        premises=tuple(premises),
        domain=domain,
        derivation=tuple(derivation),
        result=result,
        modulus=None,
        residual=None,
        lost_information=tuple(lost_information),
        reverse_lift_status=reverse_lift_status,
        proof_status=OPEN,
        implementation_status=NOT_IMPLEMENTED,
        receipt_status=NOT_EMITTED,
        coverage_state=coverage_state,
        scalar_type=scalar_type,
        notes=tuple(notes),
    )


def build_registry() -> Dict[str, ProjectionProof]:
    common_loss = ("native type/tag context", "phase/lattice address unless separately retained")
    proofs = [
        _closed("SPI-PROJ-0001", "a²", "PRIMITIVE-NUMERAL-v1", domain="registered primitive scalar projection", derivation=("primitive projection axiom a² -> 1",), result=Fraction(1), lost_information=common_loss),
        _closed("SPI-PROJ-0002", "b²", "PRIMITIVE-NUMERAL-v1", domain="registered primitive scalar projection", derivation=("primitive projection axiom b² -> 2",), result=Fraction(2), lost_information=common_loss),
        _closed("SPI-PROJ-0003", "c²", "PRIMITIVE-NUMERAL-v1", domain="registered primitive scalar projection", derivation=("primitive projection axiom c² -> 3",), result=Fraction(3), lost_information=common_loss),
        _closed("SPI-PROJ-0004", "b⁴", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0002",), domain="b² scalar projection available", derivation=("b⁴=(b²)²", "2²=4"), result=Fraction(4), lost_information=common_loss),
        _closed("SPI-PROJ-0005", "c⁴", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0003",), domain="c² scalar projection available", derivation=("c⁴=(c²)²", "3²=9"), result=Fraction(9), lost_information=common_loss),
        _closed("SPI-PROJ-0006", "b⁶", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0002",), domain="b² scalar projection available", derivation=("b⁶=(b²)³", "2³=8"), result=Fraction(8), lost_information=common_loss),
        _closed("SPI-PROJ-0007", "b²c²", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0002", "SPI-PROJ-0003"), domain="b²,c² scalar projections available", derivation=("b²c² -> 2*3", "2*3=6"), result=Fraction(6), lost_information=("ordered/native multiplication semantics", *common_loss)),
        _closed("SPI-PROJ-0008", "b²c²-a²", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0001", "SPI-PROJ-0002", "SPI-PROJ-0003"), domain="primitive scalar projections available", derivation=("b²c²-a² -> 2*3-1", "6-1=5"), result=Fraction(5), lost_information=("source expression identity beyond retained ancestry", *common_loss)),
        _closed("SPI-PROJ-0009", "b⁴+c²", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0003", "SPI-PROJ-0004"), domain="b⁴,c² scalar projections available", derivation=("b⁴+c² -> 4+3", "4+3=7"), result=Fraction(7), lost_information=common_loss),
        _closed("SPI-PROJ-0010", "b⁶c⁴", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0005", "SPI-PROJ-0006"), domain="b⁶,c⁴ scalar projections available", derivation=("b⁶c⁴ -> 8*9", "8*9=72"), result=Fraction(72), lost_information=("phase-address meaning of 72", *common_loss)),
        _closed("SPI-PROJ-0011", "(b^(2c²)c^(b⁴))²", "POLYNOMIAL-Q-v1", premises=("SPI-PROJ-0002", "SPI-PROJ-0003", "SPI-PROJ-0004", "SPI-PROJ-0010"), domain="positive even-power scalar projection", derivation=("2c² -> 6; b⁴ -> 4", "(b^6 c^4)^2 = b^12 c^8", "b^12=(b²)^6=2^6; c^8=(c²)^4=3^4", "2^6*3^4=5184"), result=Fraction(5184), lost_information=("native power-node grouping retained only as ancestry", *common_loss)),
        _closed("SPI-T1", "P²=pq+2P/(p+q)", "SPI-Q-v1", domain="P in Q, P != 0; p=P-1; q=P+1", derivation=("p+q=2P", "2P/(p+q)=1", "pq=P²-1", "residual=0"), result={"identity": "P²=pq+1", "correction": 1}, lost_information=("ordered native p/q state orientation beyond explicit pair tag",), scalar_type="PARAMETRIC_EXACT_RATIONAL_THEOREM"),
        _closed("SPI-T2", "P²-[(P-d)(P+d)+1]=(d-1)(d+1)", "SPI-SHELL-Q-v1", premises=("SPI-T1",), domain="P,d in Q; unit closure d=±1", derivation=("pq=P²-d²", "unit discrepancy=d²-1", "d²-1=(d-1)(d+1)"), result={"unit_shell": "|d|=1", "canonical_orientation": "d=+1", "reverse_orientation": "d=-1"}, lost_information=("native orientation is retained as a tag but scalar unordered shell equivalence loses lane identity",), scalar_type="PARAMETRIC_EXACT_RATIONAL_THEOREM"),
        _closed("SPI-T3A", "t³-t=t(t-1)(t+1); m²-m=m(m-1)", "INTEGER-POLYNOMIAL-v1", domain="factorization over Q; divisibility receipt requires integral t,m", derivation=("t³-t=t(t²-1)=t(t-1)(t+1)", "m²-m=m(m-1)", "three/two consecutive integer factors give divisibility 6/2"), result={"t_divisor": 6, "m_divisor": 2}, lost_information=("native t,m types are not solved as rational values",), scalar_type="PARAMETRIC_INTEGER_THEOREM"),
        _closed("SPI-T3B-I", "P³-P ≡ 0 (mod pq)", "SPI-MOD-v1", premises=("SPI-T1",), domain="integer P>1; pq=P²-1", derivation=("P³-P=P(P²-1)", "pq=P²-1", "residue=0"), result={"residue": 0}, modulus="pq=P²-1", residual=0, lost_information=("native P²(MOD)(pq) edge typing", "quotient information"), scalar_type="PARAMETRIC_MODULAR_THEOREM"),
        _closed("SPI-T3B-II", "P² ≡ 1 (mod pq)", "SPI-MOD-v1", premises=("SPI-T1",), domain="integer P>1; pq=P²-1", derivation=("P²=(P²-1)+1", "pq=P²-1", "residue=1"), result={"residue": 1}, modulus="pq=P²-1", residual=0, lost_information=("native P²(MOD)(pq) edge typing", "quotient information"), scalar_type="PARAMETRIC_MODULAR_THEOREM"),
        _open("SPI-T3C", "P²(MOD)(pq)", "NATIVE-MOD-EDGE-v1", premises=("SPI-T3B-I", "SPI-T3B-II"), domain="native edge typing controls; scalar receipts do not identify this edge", derivation=("preserve source edge without scalar collapse",), result={"status": "SEPARATELY_TYPED_NATIVE_EDGE"}, coverage_state=SYMBOLIC, lost_information=("no native MOD-edge semantics are projected by this placeholder",), notes=("T3b receipts must not be substituted for T3c native semantics.",)),
        _closed("SPI-T4", "(A/B)(B/A)=1; (x/y)(y/x)=1", "COMMUTATIVE-RECIPROCAL-Q-v1", domain="A,B,x,y in Q and all nonzero", derivation=("apply registered commutative scalar projection", "reciprocal factors cancel exactly"), result={"AB_lane_unit": 1, "xy_lane_unit": 1}, lost_information=("native lane orientation", "noncommutative product identity"), notes=("Does not imply native A/B=B/A or xy=yx.",)),
        _closed("SPI-T5-DYADIC", "F(A,B)=P²-1 with A=B", "SPI-DYADIC-Q-v1", premises=("SPI-T4",), domain="nonzero scalar lanes; A=B", derivation=("F=AB-(A-1)(B-1)=A+B-1", "A=B", "2A=P²", "A=B=P²/2"), result={"A": "P²/2", "B": "P²/2"}, lost_information=("native A=P=B authority relation", "native lane identity"), scalar_type="PARAMETRIC_EXACT_RATIONAL_THEOREM"),
        _closed("SPI-T5-GENERATOR-MOD", "F(P²,P²) ≡ P²-1 (mod P²)", "SPI-GENERATOR-MOD-v1", premises=("SPI-T4",), domain="nonzero integer P", derivation=("F(P²,P²)=2P²-1", "target=P²-1", "difference=P²", "difference≡0 mod P²"), result={"residue_class": 0}, modulus="P²", residual="P²", lost_information=("native A=P=B authority relation", "integer quotient by P²"), scalar_type="PARAMETRIC_MODULAR_THEOREM"),
        _closed("SPI-T6", CANONICAL_B_CHAIN, "SPI-T6-Q-v1", premises=("SPI-PROJ-0001", "SPI-PROJ-0002", "SPI-PROJ-0003"), domain="beta!=0; gamma-beta!=0; projected u^72 !=0; Pi cancels only with itself", derivation=("beta=(beta²-beta)/(gamma-beta) -> gamma=2beta-1", "(beta²-beta)/(gamma-beta)=gamma-alpha -> alpha=beta-1", "alpha+beta=gamma", "beta=(gamma-alpha)²/(2*pi(u^72)) -> pi(u^72)=beta/2", "beta=2 -> alpha=1,gamma=3,pi(u^72)=1"), result={"a²": 1, "b²": 2, "c²": 3, "u⁷²": 1}, lost_information=("Pi phase-label identity", "native equality-edge identity", "u^72 phase address")),
        _closed("SPI-T6-SURD", "[sqrt(c⁴-b²c²-b⁴+b²)/sqrt(c²-b²)]² -> a²", "SPI-SURD-SQUARED-Q-v1", premises=("SPI-T6",), domain="alpha=beta-1>0 (real-root projection); beta>1", derivation=("N=gamma²-beta*gamma-beta²+beta=(beta-1)²=alpha²", "D=gamma-beta=alpha", "N/D=alpha"), result={"projection": "a²", "primitive_value": 1}, lost_information=("root branch orientation is removed by outer square", "native radical node identity"), scalar_type="EXACT_ALGEBRAIC_PROJECTION"),
        _closed("SPI-QROOT-0001", "RealSurd(r,n)^k", "RealSurd-QROOT-v1", domain="r>0; n positive integer; k nonnegative integer; exact rational collapse currently requires n|k", derivation=("RealSurd(r,n) is the registered positive real nth root", "when n|k, (r^(1/n))^k=r^(k/n) exactly"), result={"rule": "r^(k/n) when n divides k"}, lost_information=("root-node source identity unless ancestry retained", "branch data outside registered positive-real profile"), reverse_lift_status=PARTIAL, scalar_type="EXACT_ALGEBRAIC_PROJECTION_RULE"),
        _closed("SPI-O4-U0", CANONICAL_U0, "SPI-U0-QROOT-v1", premises=("SPI-PROJ-0001", "SPI-PROJ-0002", "SPI-PROJ-0003", "SPI-PROJ-0010", "SPI-QROOT-0001"), domain="primitive projections; positive RealSurd profile; exact exponent divisibility", derivation=("b⁴c²=12", "RealSurd(2,12)^72=2^(72/12)=2^6=64", "(b⁶)²=(2³)²=64", "64/64=1"), result=Fraction(1), residual=Fraction(0), lost_information=("u native phase/state meaning", "RealSurd branch/type context beyond registered profile")),
        _open("SPI-O2-MATRIX", "a²=MatrixPower(M/J,4)^(b⁴)", "SPI-MATRIX-WITNESS-v1", domain="requires exact ordered matrix, inverse/lift, fourth power, root witness", derivation=("source preserved; concrete exact witness not yet registered",), result={"required_witness": ["x", "y", "z", "w", "ordered_matrix", "exact_inverse_or_lift", "fourth_power", "root_witness", "residual=0"]}, coverage_state=SYMBOLIC, lost_information=("no scalar matrix witness exists yet",), notes=("Open obligation O2.",)),
        _closed("SPI-O3-LITERAL", "179971.179971", "BOUNDARY-RATIONAL-v1", domain="exact fixed decimal boundary literal", derivation=("179971.179971 -> 179971179971/1000000",), result=Fraction(179971179971, 1000000), lost_information=("original decimal spelling unless source span retained",), reverse_lift_status=FULL),
        _open("SPI-O3-PROVENANCE", "residual provenance from f==t/m", "SPI-RESIDUAL-PROVENANCE-v1", premises=("SPI-O3-LITERAL",), domain="requires source-bound derivation from f==t/m state change", derivation=("exact literal is known; provenance derivation is not yet witnessed",), result={"status": "OPEN"}, coverage_state=MISSING_PROJECTION, lost_information=("state-change provenance not established",), notes=("Do not infer provenance from repeated literal use.",)),
    ]
    return {proof.proof_id: proof for proof in proofs}


NATIVE_AUTHORITY_REFERENCES = (
    NativeAuthorityReference(
        authority_id="SPI-AUTH-NATIVE-FIXED-POINT",
        source="hhs_self_solving_constraint_modules_v1.py",
        rule="A=P=B; scaled equality states allowed; unit state A=P=B=1 is a special case",
        implementation_evidence=("enforce_bilateral_fixed_point", "test_scaled_lock", "test_unit_lock", "test_mismatch_quarantine"),
    ),
)


def validate_registry(registry: Mapping[str, ProjectionProof] | None = None) -> Dict[str, Any]:
    registry = dict(registry or build_registry())
    errors = []
    if len(registry) != len(set(registry)):
        errors.append("duplicate proof IDs")
    for proof_id, proof in registry.items():
        if proof_id != proof.proof_id:
            errors.append(f"{proof_id}: key/id mismatch")
        for dependency in proof.premises:
            if dependency not in registry:
                errors.append(f"{proof_id}: missing premise {dependency}")
        if proof.proof_status == CLOSED:
            if proof.implementation_status != IMPLEMENTED:
                errors.append(f"{proof_id}: closed proof not implemented")
            if proof.receipt_status != VERIFIED:
                errors.append(f"{proof_id}: closed proof receipt not verified")
            if proof.coverage_state != PROVEN:
                errors.append(f"{proof_id}: closed proof is not PROVEN")
        if proof.proof_status == OPEN and proof.receipt_status != NOT_EMITTED:
            errors.append(f"{proof_id}: open proof unexpectedly emits verified receipt")
        if proof.canonical_admission:
            errors.append(f"{proof_id}: scalar proof claims canonical admission")
        if not proof.lost_information:
            errors.append(f"{proof_id}: missing mandatory lost_information")
        if len(proof.receipt_sha256()) != 64:
            errors.append(f"{proof_id}: invalid scalar proof receipt digest")

    states = {state: 0 for state in sorted(COVERAGE_STATES)}
    for proof in registry.values():
        states[proof.coverage_state] += 1

    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_VALIDATION_V1",
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "ok": not errors,
        "proof_count": len(registry),
        "coverage": states,
        "errors": errors,
        "canonical_admission_authority": False,
    }


def coverage_manifest(registry: Mapping[str, ProjectionProof] | None = None) -> Dict[str, Any]:
    registry = dict(registry or build_registry())
    validation = validate_registry(registry)
    if not validation["ok"]:
        raise SPIProjectionError(f"registry invalid: {validation['errors']}")
    return {
        "schema": "HHS_SPI_SCALAR_PROJECTION_COVERAGE_MANIFEST_V1",
        "format": FORMAT,
        "version": VERSION,
        "audited_main_sha": AUDITED_MAIN_SHA,
        "architectural_rule": "scalar calculus is downstream of the native constraint graph; projection equality is not native identity",
        "coverage_states": sorted(COVERAGE_STATES),
        "validation": validation,
        "native_authority_references": [ref.to_dict() for ref in NATIVE_AUTHORITY_REFERENCES],
        "proofs": [registry[key].to_dict() for key in sorted(registry)],
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Validate or emit the HHS SPI scalar projection registry")
    parser.add_argument("--manifest", action="store_true", help="emit the complete JSON coverage manifest")
    parser.add_argument("--validate", action="store_true", help="emit validation summary")
    args = parser.parse_args()
    if args.manifest:
        print(json.dumps(coverage_manifest(), indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    result = validate_registry()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(_main())

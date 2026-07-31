"""Pass 183 exact probability-equation hydration membrane runtime.

The runtime preserves lexical identity, builds non-destructive nested membrane
witnesses, evaluates probability adapters with exact rational arithmetic,
constructs the canonical Factorial(72) reciprocal lanes, routes valid zero
results through typed zero-bypass, closes through u^72, applies the outer
modulus only after exact closure, commits one bounded witness through the
inherited singleton VM81 authority, and emits deterministic Hash72/Hash216
receipts and replay evidence.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from fractions import Fraction
from hashlib import sha256
from math import comb, factorial, gcd, lcm
from pathlib import Path
import json
import os
import time
from typing import Any, Iterable, Mapping, MutableMapping, Protocol, Sequence

try:
    from hhs_runtime.core.hash72_digest_v1 import hash72_digest as _repository_hash72_digest
except ImportError:  # Local isolated validation only; repository CI uses the canonical digest.
    _repository_hash72_digest = None

try:
    from hhs_runtime.pass174 import Pass174Runtime
except ImportError:  # Local isolated validation can inject a deterministic authority.
    Pass174Runtime = None  # type: ignore[assignment,misc]

CONTRACT_ID = "HHS-P183-PEHMR-M1259713-F72-VM81-H72-H216"
RUNTIME_VERSION = "HHS-P183-PROBABILITY-HYDRATION-1.0.0"
AUTHORITY_ID = "HHS_VM81_SINGLETON_PROBABILITY_HYDRATION_AUTHORITY_V1"
GLOBAL_MODULUS = 1_259_713
FACTORIAL_72 = factorial(72)
ZERO_SHA256 = "0" * 64
MAX_SOURCE_BYTES = 16_384
MAX_MEMBRANE_DEPTH = 256
MAX_SUPPORT = 4_096
MAX_MARKOV_DIMENSION = 128
MAX_STOCHASTIC_DRAWS = 1_000_000

CANONICAL_FORMULA = (
    "(List(x*Factorial(72),(y*(1/Factorial(72))))*z)*"
    "(w*List((y*(1/Factorial(72))),x*Factorial(72)))/u^72"
    "==(x*y)/(x*y)==u^72"
)
FORWARD_LANE_TOKEN = "List(x*Factorial(72),(y*(1/Factorial(72))))"
RECIPROCAL_LANE_TOKEN = "List((y*(1/Factorial(72))),x*Factorial(72))"

ALLOWED_SEED_CLASSES = {
    "DETERMINISTIC_ENUMERATION",
    "CONTENT_ADDRESSED_SEED",
    "EXPLICIT_USER_SEED",
    "HASH72_CLOCK_SEED",
    "EXTERNAL_ENTROPY_EVIDENCE",
}

ADAPTER_EQUATIONS: dict[str, str] = {
    "bayes": "P(A|B)*P(B)=P(B|A)*P(A)",
    "conditional_probability": "P(A|B)=P(A∩B)/P(B)",
    "independent_intersection": "P(A∩B)=P(A)*P(B)",
    "general_intersection": "P(A∩B)=P(A|B)*P(B)",
    "union_inclusion_exclusion": "P(A∪B)=P(A)+P(B)-P(A∩B)",
    "total_probability": "P(E)=P(H)*P(E|H)+(1-P(H))*P(E|not H)",
    "expectation": "E[X]=sum_x(x*P(X=x))",
    "variance": "Var(X)=sum_x((x-E[X])^2*P(X=x))",
    "finite_discrete_distribution": "sum_i(p_i)=1",
    "binomial": "sum_(k=0..n)(C(n,k)*p^k*(1-p)^(n-k))=1",
    "multinomial": "sum_(k_1+...+k_m=n)(n!/(k_1!...k_m!))*prod_i(p_i^k_i)=1",
    "markov_chain": "for_every_i(sum_j(T_ij)=1)",
    "weighted_choice": "sum_i(w_i)=1",
    "monte_carlo_control": "estimate=successes/draws",
}


class Pass183Error(ValueError):
    """Typed Pass 183 rejection or bounded execution status."""

    def __init__(self, classification: str, detail: str | None = None) -> None:
        super().__init__(classification if detail is None else f"{classification}:{detail}")
        self.classification = classification
        self.detail = detail


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _hash72(payload: Any, exact: bytes = b"") -> str:
    if _repository_hash72_digest is not None:
        return str(_repository_hash72_digest(payload, exact))
    seed = sha256(b"P183-LOCAL-HASH72\0" + _canonical(payload) + exact).hexdigest()
    return (seed + sha256(seed.encode("ascii")).hexdigest())[:72]


def _hash216(payload: Any, exact: bytes = b"") -> dict[str, Any]:
    lanes = tuple(
        _hash72({"payload": payload, "lane": lane}, exact)
        for lane in ("PREDECESSOR", "CURRENT", "SUCCESSOR")
    )
    combined = "".join(lanes)
    indexes: list[str] = []
    prior = ZERO_SHA256
    logical = sha256(b"P183-HASH216\0" + combined.encode("ascii") + _canonical(payload) + exact).hexdigest()
    for position, character in enumerate(combined):
        prior = sha256(
            b"P183-HASH216-INDEX\0"
            + _canonical(
                {
                    "logical": logical,
                    "position": position,
                    "character": character,
                    "prior": prior,
                }
            )
        ).hexdigest()
        indexes.append(prior)
    root = sha256(b"P183-HASH216-ROOT\0" + b"".join(bytes.fromhex(item) for item in indexes)).hexdigest()
    return {
        "predecessor": lanes[0],
        "current": lanes[1],
        "successor": lanes[2],
        "combined": combined,
        "character_indexes_sha256": indexes,
        "index_root_sha256": root,
        "logical_identity_sha256": logical,
    }


def _fraction(value: Any, label: str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool) or isinstance(value, float):
        raise Pass183Error("P183_REJECT_FLOAT_AUTHORITY", label)
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        candidate = value.strip()
        if not candidate or any(marker in candidate for marker in (".", "e", "E")):
            raise Pass183Error("P183_REJECT_FLOAT_AUTHORITY", label)
        try:
            return Fraction(candidate)
        except (ValueError, ZeroDivisionError) as exc:
            classification = "P183_REJECT_ZERO_DENOMINATOR" if "/0" in candidate.replace(" ", "") else "P183_REJECT_PARSE"
            raise Pass183Error(classification, label) from exc
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)) and len(value) == 2:
        numerator, denominator = value
        if any(isinstance(item, (bool, float)) for item in (numerator, denominator)):
            raise Pass183Error("P183_REJECT_FLOAT_AUTHORITY", label)
        try:
            return Fraction(int(numerator), int(denominator))
        except ZeroDivisionError as exc:
            raise Pass183Error("P183_REJECT_ZERO_DENOMINATOR", label) from exc
    raise Pass183Error("P183_REJECT_PARSE", label)


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _probability(value: Any, label: str) -> Fraction:
    parsed = _fraction(value, label)
    if not Fraction(0, 1) <= parsed <= Fraction(1, 1):
        raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", label)
    return parsed


def _probabilities(values: Any, label: str, *, normalized: bool = True) -> tuple[Fraction, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
        raise Pass183Error("P183_REJECT_PARSE", label)
    if not values or len(values) > MAX_SUPPORT:
        raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", f"{label}:support")
    result = tuple(_probability(value, f"{label}[{index}]") for index, value in enumerate(values))
    if normalized and sum(result, Fraction(0, 1)) != 1:
        raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", f"{label}:normalization")
    return result


def _exact_values(values: Any, label: str) -> tuple[Fraction, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
        raise Pass183Error("P183_REJECT_PARSE", label)
    if not values or len(values) > MAX_SUPPORT:
        raise Pass183Error("P183_REJECT_PROBABILITY_DOMAIN", f"{label}:support")
    return tuple(_fraction(value, f"{label}[{index}]") for index, value in enumerate(values))


def _require_equation(adapter: str, equation: str) -> None:
    expected = ADAPTER_EQUATIONS.get(adapter)
    if expected is None:
        raise Pass183Error("P183_REJECT_PARSE", f"unknown_adapter:{adapter}")
    if equation != expected:
        raise Pass183Error("P183_REJECT_LEXICAL_IDENTITY", adapter)


def _check_source(source: str) -> bytes:
    if not isinstance(source, str) or not source:
        raise Pass183Error("P183_REJECT_PARSE", "equation")
    raw = source.encode("utf-8")
    if len(raw) > MAX_SOURCE_BYTES:
        raise Pass183Error("P183_TIMEOUT", "source_length")
    if any(byte >= 0x80 for byte in raw):
        normalized = source.replace("∩", "").replace("∪", "")
        if any(ord(character) >= 128 for character in normalized):
            raise Pass183Error("P183_REJECT_LEXICAL_IDENTITY", "unicode_lookalike")
    prohibited = ("−", "–", "—", "÷", "／", "﹣", "⁄")
    if any(token in source for token in prohibited):
        raise Pass183Error("P183_REJECT_LEXICAL_IDENTITY", "ambiguous_operator")
    return raw


@dataclass(frozen=True)
class MembraneRecord:
    membrane_id: str
    parent_membrane_id: str | None
    source_span_start: int
    source_span_end: int
    lexical_bytes_hex: str
    depth_n: int
    boundary_modulus_n_plus_1: int
    boundary_residue_n: int
    child_order: int
    parse_identity: str
    content_hash: str
    hash216_identity: str
    open_token_identity: str
    close_token_identity: str
    validation_status: str = "P183_OK"


@dataclass
class _OpenMembrane:
    start: int
    depth: int
    parent_start: int | None


def build_membrane_tree(source: str, *, max_depth: int = MAX_MEMBRANE_DEPTH) -> tuple[MembraneRecord, ...]:
    raw = _check_source(source)
    byte_positions: list[int] = []
    offset = 0
    for character in source:
        byte_positions.append(offset)
        offset += len(character.encode("utf-8"))
    byte_positions.append(offset)

    stack: list[_OpenMembrane] = []
    closed: list[dict[str, Any]] = []
    for character_index, character in enumerate(source):
        if character == "(":
            depth = len(stack)
            if depth > max_depth:
                raise Pass183Error("P183_REJECT_MEMBRANE_WITNESS", "max_depth")
            stack.append(
                _OpenMembrane(
                    start=byte_positions[character_index],
                    depth=depth,
                    parent_start=stack[-1].start if stack else None,
                )
            )
        elif character == ")":
            if not stack:
                raise Pass183Error("P183_REJECT_UNBALANCED_MEMBRANE", "close_without_open")
            opened = stack.pop()
            end = byte_positions[character_index + 1]
            lexical = raw[opened.start:end]
            closed.append(
                {
                    "start": opened.start,
                    "end": end,
                    "depth": opened.depth,
                    "parent_start": opened.parent_start,
                    "lexical": lexical,
                }
            )
    if stack:
        raise Pass183Error("P183_REJECT_UNBALANCED_MEMBRANE", "unclosed")

    by_parent: dict[int | None, list[dict[str, Any]]] = {}
    for item in closed:
        by_parent.setdefault(item["parent_start"], []).append(item)
    for siblings in by_parent.values():
        siblings.sort(key=lambda item: item["start"])

    identities: dict[int, str] = {}
    for item in sorted(closed, key=lambda value: (value["depth"], value["start"])):
        payload = {
            "schema": "P183_MEMBRANE_ID_V1",
            "source_sha256": sha256(raw).hexdigest(),
            "start": item["start"],
            "end": item["end"],
            "depth": item["depth"],
            "parent_start": item["parent_start"],
            "content_sha256": sha256(item["lexical"]).hexdigest(),
        }
        identities[item["start"]] = sha256(b"P183-MEMBRANE-ID\0" + _canonical(payload)).hexdigest()

    records: list[MembraneRecord] = []
    for item in sorted(closed, key=lambda value: value["start"]):
        siblings = by_parent[item["parent_start"]]
        child_order = next(index for index, sibling in enumerate(siblings) if sibling["start"] == item["start"])
        depth = int(item["depth"])
        residue = depth % (depth + 1)
        if residue != depth:
            raise Pass183Error("P183_REJECT_MEMBRANE_WITNESS", "boundary_identity")
        parse_payload = {
            "source_sha256": sha256(raw).hexdigest(),
            "start": item["start"],
            "end": item["end"],
            "depth": depth,
            "parent": identities.get(item["parent_start"]),
            "child_order": child_order,
        }
        hash216 = _hash216(parse_payload, item["lexical"])
        records.append(
            MembraneRecord(
                membrane_id=identities[item["start"]],
                parent_membrane_id=identities.get(item["parent_start"]),
                source_span_start=item["start"],
                source_span_end=item["end"],
                lexical_bytes_hex=item["lexical"].hex(),
                depth_n=depth,
                boundary_modulus_n_plus_1=depth + 1,
                boundary_residue_n=residue,
                child_order=child_order,
                parse_identity=sha256(b"P183-MEMBRANE-PARSE\0" + _canonical(parse_payload)).hexdigest(),
                content_hash=sha256(item["lexical"]).hexdigest(),
                hash216_identity=hash216["logical_identity_sha256"],
                open_token_identity=sha256(
                    b"P183-OPEN\0" + item["start"].to_bytes(8, "big") + b"("
                ).hexdigest(),
                close_token_identity=sha256(
                    b"P183-CLOSE\0" + item["end"].to_bytes(8, "big") + b")"
                ).hexdigest(),
            )
        )
    return tuple(records)

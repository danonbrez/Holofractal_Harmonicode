"""Pass 219 scalar-projection proof registry.

This module proves or classifies scalar projections without rewriting the
canonical HARMONICODE source and without acquiring VM81/Hash72/Hash216 state
mutation authority. Equal scalar projections never imply native identity.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
import re
from typing import Iterable, Mapping

from hhs_runtime.core.hash72_digest_v1 import hash72_digest

SCHEMA = "HHS_PASS219_SCALAR_PROJECTION_PROOF_REGISTRY_V1"
CONTRACT_ID = "HHS-P219-SCALAR-PROJECTION-PROOF-REGISTRY-1.0"
CANONICAL_SOURCE_PATH = "HHS_PASS_169_CANONICAL_ALGEBRA_CORPUS.harmonicode"
CANONICAL_SOURCE_BYTES = 632
CANONICAL_SOURCE_SHA256 = "3315641c8d6aa9fc4f3918eccda8e3a40c8445cc417a65e5dea683f68020cf53"

PROVEN = "PROVEN"
PARAMETERIZED = "PARAMETERIZED"
SYMBOLIC = "SYMBOLIC"
UNSUPPORTED = "UNSUPPORTED_DOMAIN"
TYPED_NONSCALAR = "TYPED_NONSCALAR"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True)
class ProjectionProof:
    proof_id: str
    native_expression: str
    projection_id: str
    domain: str
    result: Fraction
    dependencies: tuple[str, ...]
    derivation: tuple[str, ...]
    lost_information: tuple[str, ...] = ("native_expression_identity",)
    reverse_lift_rule: str = "NONE"
    claim_type: str = "PROJECTION_THEOREM"

    def to_dict(self) -> dict[str, object]:
        body: dict[str, object] = {
            "proof_id": self.proof_id,
            "native_expression": self.native_expression,
            "projection_id": self.projection_id,
            "domain": self.domain,
            "claim_type": self.claim_type,
            "result": {
                "type": "NORMALIZED_RATIONAL" if self.result.denominator != 1 else "BIGINT",
                "numerator": self.result.numerator,
                "denominator": self.result.denominator,
            },
            "dependencies": list(self.dependencies),
            "derivation": list(self.derivation),
            "lost_information": list(self.lost_information),
            "reverse_lift_rule": self.reverse_lift_rule,
            "projection_equality_implies_native_identity": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_persistence_authority": False,
        }
        body["proof_sha256"] = sha256(_canonical_json(body).encode("utf-8")).hexdigest()
        body["proof_receipt_hash72"] = hash72_digest(
            {"domain": "HHS-P219-SCALAR-PROJECTION-PROOF-V1", "proof_id": self.proof_id},
            body,
        )
        return body


def _p(pid: str, expr: str, value: int | Fraction, deps: Iterable[str], *steps: str,
       projection_id: str = "PI-LOSHU-NUMERAL-v1", domain: str = "EXACT_SYMBOLIC_TO_INTEGER") -> ProjectionProof:
    return ProjectionProof(pid, expr, projection_id, domain, Fraction(value), tuple(deps), tuple(steps))


PROOFS: tuple[ProjectionProof, ...] = (
    _p("SPP001", "a^2", 1, (), "registered primitive projection a^2 -> 1"),
    _p("SPP002", "b^2", 2, (), "registered primitive projection b^2 -> 2"),
    _p("SPP003", "c^2", 3, (), "registered primitive projection c^2 -> 3"),
    _p("SPP004", "d^2", 5, (), "registered primitive projection d^2 -> 5"),
    _p("SPP005", "e^2", 8, (), "registered extended projection e^2 -> 8"),
    _p("SPP006", "f^2", 13, (), "registered extended projection f^2 -> 13"),
    _p("SPP007", "g^2", 21, (), "registered extended projection g^2 -> 21"),
    _p("SPP008", "b^4", 4, ("SPP002",), "b^4=(b^2)^2", "2^2=4"),
    _p("SPP009", "c^4", 9, ("SPP003",), "c^4=(c^2)^2", "3^2=9"),
    _p("SPP010", "b^6", 8, ("SPP002",), "b^6=(b^2)^3", "2^3=8"),
    _p("SPP011", "b^2*c^2", 6, ("SPP002", "SPP003"), "2*3=6"),
    _p("SPP012", "b^2+c^2", 5, ("SPP002", "SPP003"), "2+3=5"),
    _p("SPP013", "b^4+c^2", 7, ("SPP008", "SPP003"), "4+3=7"),
    _p("SPP014", "b^2*c^2-a^2", 5, ("SPP011", "SPP001"), "6-1=5"),
    _p("SPP015", "c^2-b^2", 1, ("SPP003", "SPP002"), "3-2=1"),
    _p("SPP016", "c^4-b^2*c^2-b^4+b^2", 1, ("SPP009", "SPP011", "SPP008", "SPP002"), "9-6-4+2=1"),
    _p("SPP017", "2*c^2+b^2", 8, ("SPP003", "SPP002"), "2*3+2=8"),
    _p("SPP018", "2/b^2", 1, ("SPP002",), "2/2=1"),
    _p("SPP019", "b^2*(c^2+b^2)", 10, ("SPP002", "SPP012"), "2*5=10"),
    _p("SPP020", "(b^2*(c^2+b^2))-(c^2-b^2)", 9, ("SPP019", "SPP015"), "10-1=9"),
    _p("SPP021", "Sqrt(c^4)", 3, ("SPP009",), "principal exact radical Sqrt(9)=3", projection_id="PI-SCALAR-ORDINARY-v1", domain="NONNEGATIVE_EXACT_RADICAL"),
    _p("SPP022", "((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)", 3, ("SPP020", "SPP021"), "9/3=3"),
    _p("SPP023", "c^2*b^6-c^2", 21, ("SPP003", "SPP010"), "3*8-3=21"),
    _p("SPP024", "(c^2*b^6-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c^4))", 7, ("SPP023", "SPP022"), "21/3=7"),
    _p("SPP025", "b^6*c^4", 72, ("SPP010", "SPP009"), "8*9=72"),
    _p("SPP026", "(b^(2*c^2)*c^(b^4))^2", 5184, ("SPP002", "SPP003", "SPP008", "SPP025"), "2*c^2=6", "b^4=4", "(b^6*c^4)^2=72^2", "72^2=5184"),
    _p("SPP027", "72^2", 5184, ("SPP025",), "72*72=5184", projection_id="PI-VM5184-OP-v1", domain="EXACT_INTEGER_CARDINALITY"),
    _p("SPP028", "64*81", 5184, (), "64*81=5184", projection_id="PI-VM5184-OP-v1", domain="EXACT_INTEGER_CARDINALITY"),
    _p("SPP029", "36*144", 5184, (), "36*144=5184", projection_id="PI-VM5184-OP-v1", domain="EXACT_INTEGER_CARDINALITY"),
    _p("SPP030", "u_phase^72", 1, (), "registered phase closure u_phase^72=a^2", "a^2->1", projection_id="PI-U-PHASE-v1", domain="REGISTERED_U72_PHASE"),
    _p("SPP031", "I^4", 1, (), "registered quartic phase closure I^4->1", projection_id="PI-COMPLEX-COMPAT-v1", domain="REGISTERED_PHASE_PROJECTION"),
    _p("SPP032", "Delta", 1, (), "Pass129 rational projection: Delta^2=Delta and Delta!=0", "therefore Delta=1", projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL"),
    _p("SPP033", "P^2-p*q", 1, ("SPP032",), "Pass129 declared P^2-pq=Delta", "Delta->1", projection_id="PI-P129-DELTA-RATIONAL-v1", domain="PASS129_NONZERO_EXACT_RATIONAL"),
    _p("SPP034", "(A/B)*(B/A)", 1, (), "for exact nonzero A,B, reciprocal product closes to 1", projection_id="PI-UCE-INTEGER-SYMMETRIC-v1", domain="EXACT_NONZERO_RECIPROCAL"),
    _p("SPP035", "0^4", 0, (), "ordinary scalar projection of literal zero power", projection_id="PI-SCALAR-ORDINARY-v1", domain="EXACT_INTEGER"),
)

PROOF_BY_ID = {proof.proof_id: proof for proof in PROOFS}
PROOF_BY_EXPRESSION = {proof.native_expression: proof for proof in PROOFS}

SYMBOL_COVERAGE: Mapping[str, str] = {
    "P": PARAMETERIZED, "p": PARAMETERIZED, "q": PARAMETERIZED,
    "pq": PARAMETERIZED, "A": PARAMETERIZED, "B": PARAMETERIZED, "AB": PARAMETERIZED,
    "Delta": PARAMETERIZED, "∆": PARAMETERIZED,
    "t": UNSUPPORTED, "m": UNSUPPORTED, "s": UNSUPPORTED, "f": UNSUPPORTED,
    "At": UNSUPPORTED, "Bt": UNSUPPORTED,
    "x": TYPED_NONSCALAR, "y": TYPED_NONSCALAR, "z": TYPED_NONSCALAR, "w": TYPED_NONSCALAR,
    "xy": TYPED_NONSCALAR, "yx": TYPED_NONSCALAR, "zw": TYPED_NONSCALAR, "wz": TYPED_NONSCALAR,
    "u": TYPED_NONSCALAR, "I": TYPED_NONSCALAR,
    "a": TYPED_NONSCALAR, "b": TYPED_NONSCALAR, "c": TYPED_NONSCALAR,
}

SURFACE_COVERAGE: tuple[dict[str, str], ...] = (
    {"expression": "P^2", "status": PARAMETERIZED},
    {"expression": "pq", "status": PARAMETERIZED},
    {"expression": "t^3-t", "status": UNSUPPORTED},
    {"expression": "m^2-m", "status": UNSUPPORTED},
    {"expression": "P^3-P/(P^2-pq)", "status": PARAMETERIZED},
    {"expression": "(t^3-t)/Delta", "status": UNSUPPORTED},
    {"expression": "P^2(MOD)(pq)", "status": PARAMETERIZED},
    {"expression": "c^2-u^72", "status": SYMBOLIC},
    {"expression": "s==(b^(2*c^2)c^b^4)^2", "status": UNSUPPORTED},
    {"expression": "b^6-(xy)", "status": PARAMETERIZED},
    {"expression": "pq+xy", "status": PARAMETERIZED},
    {"expression": "x+y", "status": TYPED_NONSCALAR},
    {"expression": "Mod(f/u,72*(pq+xy))", "status": UNSUPPORTED},
    {"expression": "AB/P^2", "status": PARAMETERIZED},
    {"expression": "Sqrt[AB]", "status": PARAMETERIZED},
    {"expression": "AB/(pq+Delta)-P^2", "status": PARAMETERIZED},
    {"expression": "Delta/P=Sqrt(pq+u^72)^x^2", "status": UNSUPPORTED},
    {"expression": "x+y+z+w", "status": TYPED_NONSCALAR},
    {"expression": "NcalcMatrixPower(...,4)", "status": SYMBOLIC},
)

RESERVED_WORDS = {"NcalcMatrixPower", "List", "Sqrt", "Mod", "MOD", "where"}
TOKEN_PATTERN = re.compile(r"[A-Za-zΔ∆]+")


def verify_canonical_source(source: bytes | str) -> dict[str, object]:
    raw = source.encode("utf-8") if isinstance(source, str) else bytes(source)
    digest = sha256(raw).hexdigest()
    return {
        "path": CANONICAL_SOURCE_PATH,
        "bytes": len(raw),
        "sha256": digest,
        "expected_bytes": CANONICAL_SOURCE_BYTES,
        "expected_sha256": CANONICAL_SOURCE_SHA256,
        "verified": len(raw) == CANONICAL_SOURCE_BYTES and digest == CANONICAL_SOURCE_SHA256,
    }


def extract_source_symbols(source: bytes | str) -> tuple[str, ...]:
    text = source.decode("utf-8") if isinstance(source, (bytes, bytearray)) else source
    tokens = {token for token in TOKEN_PATTERN.findall(text) if token not in RESERVED_WORDS}
    return tuple(sorted(tokens))


def validate_dependency_graph() -> None:
    seen: set[str] = set()
    for proof in PROOFS:
        if proof.proof_id in seen:
            raise ValueError(f"DUPLICATE_PROOF_ID:{proof.proof_id}")
        for dependency in proof.dependencies:
            if dependency not in PROOF_BY_ID:
                raise ValueError(f"UNKNOWN_DEPENDENCY:{proof.proof_id}:{dependency}")
        seen.add(proof.proof_id)


def build_scalar_projection_coverage(source: bytes | str) -> dict[str, object]:
    source_identity = verify_canonical_source(source)
    if not source_identity["verified"]:
        raise ValueError("CANONICAL_SOURCE_IDENTITY_MISMATCH")
    validate_dependency_graph()
    symbols = extract_source_symbols(source)
    symbol_records = []
    uncovered = []
    aliases = {"Delta": "∆"}
    for symbol in symbols:
        lookup = aliases.get(symbol, symbol)
        status = SYMBOL_COVERAGE.get(lookup)
        if status is None:
            status = SYMBOL_COVERAGE.get(symbol)
        if status is None:
            uncovered.append(symbol)
            status = "MISSING_PROJECTION"
        symbol_records.append({"symbol": symbol, "status": status})
    proofs = [proof.to_dict() for proof in PROOFS]
    same_value_groups: dict[str, list[str]] = {}
    for proof in PROOFS:
        key = f"{proof.result.numerator}/{proof.result.denominator}"
        same_value_groups.setdefault(key, []).append(proof.proof_id)
    manifest: dict[str, object] = {
        "schema": SCHEMA,
        "contract_id": CONTRACT_ID,
        "canonical_source": source_identity,
        "proof_count": len(proofs),
        "proofs": proofs,
        "symbol_coverage": symbol_records,
        "surface_coverage": list(SURFACE_COVERAGE),
        "uncovered_symbols": uncovered,
        "same_scalar_value_distinct_native_proof_groups": {
            key: ids for key, ids in same_value_groups.items() if len(ids) > 1
        },
        "invariants": {
            "projection_equality_implies_native_identity": False,
            "source_rewrite_authorized": False,
            "commutative_reorder_authorized": False,
            "nonassociative_reassociation_authorized": False,
            "floating_point_canonical_authority": False,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_mint_authority": False,
            "canonical_hash216_persistence_authority": False,
        },
    }
    manifest["manifest_sha256"] = sha256(_canonical_json(manifest).encode("utf-8")).hexdigest()
    manifest["manifest_receipt_hash72"] = hash72_digest(
        {"domain": "HHS-P219-SCALAR-PROJECTION-COVERAGE-V1"}, manifest
    )
    return manifest


def prove(native_expression: str) -> dict[str, object]:
    try:
        return PROOF_BY_EXPRESSION[native_expression].to_dict()
    except KeyError as exc:
        raise KeyError(f"NO_FIXED_SCALAR_PROOF:{native_expression}") from exc

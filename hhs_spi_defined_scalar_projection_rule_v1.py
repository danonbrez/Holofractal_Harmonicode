"""HARMONICODE matrix/tensor-defined scalar projection rule v1.

Rule
----
A native ordered matrix/tensor expression may project to a scalar when an exact,
source-bound HARMONICODE equality edge defines a scalar projection symbol by that
matrix/tensor expression and that scalar symbol already has a registered exact
scalar projection.

If a native edge has the typed form

    S = E_matrix_or_tensor

and a registered scalar profile proves

    pi(S) = v,

then the edge authorizes the downstream correspondence

    pi_edge(E_matrix_or_tensor) = v.

This is projection inheritance through a definition edge.  It is not host
matrix evaluation, native substitution, commutation, cancellation, or reverse
reconstruction.  The native matrix/tensor node remains intact and retains its
ordered topology and authority boundary.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping

FORMAT = "HHS_SPI_DEFINED_SCALAR_PROJECTION_RULE_V1"
VERSION = "1.0.0"
PROFILE = "MATRIX_TENSOR_DEFINED_SCALAR_PROJECTION-v1"

ALLOWED_DEFINITION_KINDS = frozenset({
    "ORDERED_MATRIX",
    "ORDERED_TENSOR",
    "EXACT_SYMBOLIC_MATRIX_EXPRESSION",
    "EXACT_SYMBOLIC_TENSOR_EXPRESSION",
    "EXACT_SYMBOLIC_MATRIX_POWER",
    "EXACT_SYMBOLIC_TENSOR_POWER",
})


class SPIDefinedScalarProjectionError(ValueError):
    pass


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPIDefinedScalarProjectionError("defined scalar projection requires an exact non-float scalar")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise SPIDefinedScalarProjectionError(f"invalid exact scalar: {value!r}") from exc


def _exact_json(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"type": "EXACT_RATIONAL", "numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, tuple):
        return [_exact_json(v) for v in value]
    if isinstance(value, list):
        return [_exact_json(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _exact_json(value[k]) for k in sorted(value)}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise SPIDefinedScalarProjectionError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def defined_scalar_projection(
    *,
    scalar_symbol: str,
    scalar_proof_id: str,
    scalar_value: Any,
    defining_expression: str,
    equality_edge_source: str,
    definition_kind: str,
    edge_id: str,
) -> Dict[str, Any]:
    """Create one exact source-bound matrix/tensor -> scalar projection receipt.

    The function validates only the projection membrane.  It deliberately does
    not evaluate ``defining_expression``.  The native equality edge is the
    definition authority for the downstream scalar correspondence.
    """
    if not scalar_symbol or not scalar_proof_id or not defining_expression or not equality_edge_source or not edge_id:
        raise SPIDefinedScalarProjectionError("all source/proof identity fields are required")
    if definition_kind not in ALLOWED_DEFINITION_KINDS:
        raise SPIDefinedScalarProjectionError(f"unsupported definition kind: {definition_kind}")
    scalar = _q(scalar_value)

    # A source-bound edge must contain both exact nodes.  This is intentionally
    # lexical/source-identity validation, not algebraic reparsing or rewriting.
    if scalar_symbol not in equality_edge_source:
        raise SPIDefinedScalarProjectionError("scalar symbol is not present in the defining equality edge")
    if defining_expression not in equality_edge_source:
        raise SPIDefinedScalarProjectionError("matrix/tensor expression is not present in the defining equality edge")
    if "=" not in equality_edge_source:
        raise SPIDefinedScalarProjectionError("defining source does not contain an equality edge")

    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_DEFINED_SCALAR_PROJECTION_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "edge_id": edge_id,
        "equality_edge_source": equality_edge_source,
        "equality_edge_sha256": sha256(equality_edge_source.encode("utf-8")).hexdigest(),
        "scalar_symbol": scalar_symbol,
        "scalar_proof_id": scalar_proof_id,
        "scalar_projection": scalar,
        "defining_expression": defining_expression,
        "defining_expression_sha256": sha256(defining_expression.encode("utf-8")).hexdigest(),
        "definition_kind": definition_kind,
        "derivation": [
            "preserve the native matrix/tensor definition edge exactly",
            f"use registered scalar proof {scalar_proof_id} for pi({scalar_symbol})",
            "inherit that scalar value downstream across this exact definition edge",
            "retain the defining matrix/tensor expression as a distinct native node",
        ],
        "result": scalar,
        "residual": Fraction(0),
        "matrix_or_tensor_host_evaluated": False,
        "native_substitution_authorized": False,
        "reverse_lift_status": "none",
        "lost_information": [
            "matrix/tensor topology and ordered operand identity are not reconstructible from the scalar alone",
            "native type and equality-edge provenance must be retained separately",
            "scalar equality does not identify the native matrix/tensor node with the scalar symbol",
        ],
        "projection_only": True,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)

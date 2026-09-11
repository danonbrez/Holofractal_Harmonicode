"""Pass 219 SPI — tensor-pair three-set cubic normalization rule v1.

Operator-supplied extension:

    t³ = t + a²

for every admitted tensor-pair translation layer.

This rule is projection-scoped and is represented in the equivalent residual
form

    t³ - t = a² = ∆ = 1.

The rule does NOT solve native ``t`` as a rational/real/complex scalar.  It
preserves the three native source terms ``t³``, ``t``, and ``a²`` as distinct
nodes and closes only the scalar correspondence of their residual relation.

A tensor-pair layer therefore carries a three-set normalization witness:

    C3(L) = {t³, t, a²}

with exact projected residual

    pi_L(t³ - t - a²) = 0.

The universal denominator bridge remains

    pi_L(∆)=1,

so the cubic normalization can also be written

    pi_L(t³ - t)=pi_L(a²)=pi_L(∆)=1.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

FORMAT = "HHS_SPI_TENSOR_PAIR_CUBIC_NORMALIZATION_RULE_V1"
VERSION = "1.0.0"
PROFILE = "TENSOR-PAIR-THREE-SET-CUBIC-NORMALIZATION-v1"
SOURCE_RELATION = "t³=t+a²"
RESIDUAL_RELATION = "t³-t=a²=∆=1"
THREE_SET = ("t³", "t", "a²")


class SPITensorPairCubicNormalizationError(ValueError):
    pass


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPITensorPairCubicNormalizationError("exact cubic normalization forbids bool/float arithmetic")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise SPITensorPairCubicNormalizationError(f"invalid exact scalar: {value!r}") from exc


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
    raise SPITensorPairCubicNormalizationError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def tensor_pair_cubic_witness(
    *,
    pair_layer_id: str,
    source_tensor_id: str,
    target_tensor_id: str,
    source_shape: Sequence[int],
    target_shape: Sequence[int],
    equal_sum_normalized: bool,
    a2_projection: Any = 1,
    delta_projection: Any = 1,
    cubic_residual_projection: Any = 1,
) -> Dict[str, Any]:
    """Emit one three-set normalization witness for a tensor-pair layer.

    ``cubic_residual_projection`` is the already-registered scalar projection of
    ``t³-t``.  ``t`` itself remains unassigned and unsolved.
    """
    if not pair_layer_id or not source_tensor_id or not target_tensor_id:
        raise SPITensorPairCubicNormalizationError("stable tensor-pair identities are required")
    source_shape_tuple = tuple(int(v) for v in source_shape)
    target_shape_tuple = tuple(int(v) for v in target_shape)
    if source_shape_tuple != target_shape_tuple:
        raise SPITensorPairCubicNormalizationError("tensor-pair cubic normalization requires same-sized tensors")
    if not source_shape_tuple or any(v <= 0 for v in source_shape_tuple):
        raise SPITensorPairCubicNormalizationError("tensor shape must be non-empty and positive")
    if equal_sum_normalized is not True:
        raise SPITensorPairCubicNormalizationError("tensor pair must first close its equal-sum a² normalization")

    a2 = _q(a2_projection)
    delta = _q(delta_projection)
    cubic = _q(cubic_residual_projection)
    if a2 != 1 or delta != 1 or cubic != 1:
        raise SPITensorPairCubicNormalizationError(
            f"three-set cubic unit mismatch: t³-t={cubic}, a²={a2}, ∆={delta}"
        )

    # We do not evaluate native t.  The exact scalar proof is the residual edge:
    # (t³-t)-a² = 1-1 = 0.
    residual = cubic - a2
    universal_residual = cubic - delta
    if residual != 0 or universal_residual != 0:
        raise SPITensorPairCubicNormalizationError("cubic residual did not close")

    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_TENSOR_PAIR_CUBIC_NORMALIZATION_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "pair_layer_id": pair_layer_id,
        "source_tensor_id": source_tensor_id,
        "target_tensor_id": target_tensor_id,
        "source_shape": source_shape_tuple,
        "target_shape": target_shape_tuple,
        "three_set": THREE_SET,
        "source_relation": SOURCE_RELATION,
        "residual_relation": RESIDUAL_RELATION,
        "cubic_residual_projection": cubic,
        "local_scale_symbol": "a²",
        "local_scale_projection": a2,
        "universal_denominator_symbol": "∆",
        "universal_denominator_projection": delta,
        "projected_relation_residual": residual,
        "projected_universal_residual": universal_residual,
        "t_scalar_value_assigned": False,
        "t_scalar_value": None,
        "native_t_solved": False,
        "equal_sum_prerequisite_closed": True,
        "projection_only": True,
        "native_t3_t_a2_identity_collapse": False,
        "native_tensor_substitution_authorized": False,
        "canonical_admission_authority": False,
        "vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "canonical_persistence_authority": False,
        "floating_point_authority": False,
        "lost_information": [
            "the scalar residual does not determine a native scalar value for t",
            "tensor coordinate/cell topology is not represented by the cubic unit relation",
            "native t³, t, a², and ∆ nodes remain separately typed and source-bound",
        ],
        "reverse_lift_status": "none",
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)


def three_set_normalization_equations() -> Dict[str, Any]:
    """Return the exact symbolic normalization identities without solving t."""
    return {
        "profile": PROFILE,
        "three_set": list(THREE_SET),
        "native_relation": SOURCE_RELATION,
        "scalar_projection_equivalence": [
            "pi(t³-t)=1",
            "pi(a²)=1",
            "pi(∆)=1",
            "pi(t³-t-a²)=0",
        ],
        "native_t_solved": False,
        "projection_only": True,
    }

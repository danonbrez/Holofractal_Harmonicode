"""Pass 219 SPI — Fibonacci/Pythagorean/Golden tensor scaling law v1.

Scaling law for equal-sum tensor translation:

    a² = 1
    b² = 2
    c² = a² + b² = 3
    d² = c² + b² = 5
    e² = d² + c² = 8
    ...

The square-state scale ladder obeys the exact Fibonacci recurrence

    Q[n+1] = Q[n] + Q[n-1]

with exact finite scale ratio

    lambda[n] = Q[n+1] / Q[n].

The symbolic Golden limit is kept separate and exact:

    Phi² - Phi - 1 = 0, Phi > 0.

No finite ratio is replaced by a floating approximation of Phi.

For an equal-sum tensor equation with invariant sum M, define the exact scale
coordinate at square-state layer Q[n] by

    C_n(T) = (SumEq(T) / M) * Q[n].

When SumEq(T)=M, C_n(T)=Q[n]. Two same-sized tensors in the same equal-sum
translation class therefore share the same scale coordinate at every admitted
Fibonacci layer. Cross-layer translation is exact:

    C_{n+1}(T) = lambda[n] * C_n(T) = Q[n+1].

At the base layer Q[0]=a²=1, this reduces to the existing a² normalization.
The law is projection/scaling semantics only and never identifies native tensor
cells or replaces native Fibonacci/Golden source objects.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

FORMAT = "HHS_SPI_FIBONACCI_PYTHAGOREAN_GOLDEN_SCALING_V1"
VERSION = "1.0.0"
PROFILE = "FIBONACCI-PYTHAGOREAN-GOLDEN-TENSOR-SCALE-v1"
GOLDEN_POLYNOMIAL = "Phi²-Phi-1=0"

BASE_SQUARE_STATES: Tuple[Tuple[str, int], ...] = (
    ("a²", 1),
    ("b²", 2),
    ("c²", 3),
    ("d²", 5),
    ("e²", 8),
)


class SPIFibonacciScalingError(ValueError):
    pass


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPIFibonacciScalingError("exact Fibonacci scaling forbids bool/float arithmetic")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise SPIFibonacciScalingError(f"invalid exact scalar: {value!r}") from exc


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
    raise SPIFibonacciScalingError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def square_state_sequence(count: int) -> Tuple[Fraction, ...]:
    if not isinstance(count, int) or isinstance(count, bool) or count < 2:
        raise SPIFibonacciScalingError("square-state count must be an integer >= 2")
    values = [Fraction(1), Fraction(2)]
    while len(values) < count:
        values.append(values[-1] + values[-2])
    return tuple(values)


def finite_stage_ratios(count: int) -> Tuple[Fraction, ...]:
    values = square_state_sequence(count + 1)
    return tuple(values[i + 1] / values[i] for i in range(count))


def pythagorean_base_witness() -> Dict[str, Any]:
    a2 = Fraction(1)
    b2 = Fraction(2)
    c2 = a2 + b2
    if c2 != 3:
        raise SPIFibonacciScalingError("a²+b²=c² base closure failed")
    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_PYTHAGOREAN_BASE_WITNESS_V1",
        "profile": PROFILE,
        "a²": a2,
        "b²": b2,
        "c²": c2,
        "equation": "a²+b²=c²",
        "residual": a2 + b2 - c2,
        "fibonacci_seed": (a2, b2),
        "projection_only": True,
        "native_symbol_collapse": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)


def scale_ladder_witness(count: int = 9) -> Dict[str, Any]:
    values = square_state_sequence(count)
    ratios = finite_stage_ratios(count - 1)
    recurrence_residuals = tuple(values[i + 1] - values[i] - values[i - 1] for i in range(1, len(values) - 1))
    if any(residual != 0 for residual in recurrence_residuals):
        raise SPIFibonacciScalingError("Fibonacci square-state recurrence failed")
    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_FIBONACCI_SCALE_LADDER_WITNESS_V1",
        "profile": PROFILE,
        "square_states": values,
        "finite_stage_ratios": ratios,
        "recurrence": "Q[n+1]=Q[n]+Q[n-1]",
        "recurrence_residuals": recurrence_residuals,
        "pythagorean_seed": "c²=a²+b²",
        "golden_limit": {
            "type": "SYMBOLIC_IRRATIONAL",
            "symbol": "Phi",
            "polynomial": GOLDEN_POLYNOMIAL,
            "positive_root": True,
            "finite_ratio_substitution_authorized": False,
            "floating_approximation_authorized": False,
        },
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)


def tensor_scale_coordinate(
    *,
    equation_sum: Any,
    invariant_sum: Any,
    stage_index: int,
    sequence_count: int = 16,
) -> Dict[str, Any]:
    if not isinstance(stage_index, int) or isinstance(stage_index, bool) or stage_index < 0:
        raise SPIFibonacciScalingError("stage_index must be a nonnegative integer")
    equation = _q(equation_sum)
    invariant = _q(invariant_sum)
    if invariant == 0:
        raise SPIFibonacciScalingError("invariant_sum must be nonzero")
    if stage_index >= sequence_count:
        raise SPIFibonacciScalingError("stage_index exceeds generated square-state ladder")
    values = square_state_sequence(sequence_count)
    qn = values[stage_index]
    normalized = equation / invariant
    coordinate = normalized * qn
    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_TENSOR_FIBONACCI_SCALE_COORDINATE_V1",
        "profile": PROFILE,
        "stage_index": stage_index,
        "square_state": qn,
        "equation_sum": equation,
        "invariant_sum": invariant,
        "a2_normalized_equation": normalized,
        "scale_coordinate": coordinate,
        "equal_sum_closed": equation == invariant,
        "base_stage_is_a²": stage_index == 0,
        "projection_only": True,
        "native_tensor_scaled": False,
        "canonical_admission_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)


def cross_stage_translation_witness(
    *,
    invariant_sum: Any,
    source_stage: int,
    target_stage: int,
    sequence_count: int = 16,
) -> Dict[str, Any]:
    if target_stage != source_stage + 1:
        raise SPIFibonacciScalingError("v1 cross-stage witness requires adjacent Fibonacci scale layers")
    values = square_state_sequence(sequence_count)
    if target_stage >= len(values):
        raise SPIFibonacciScalingError("target stage exceeds generated square-state ladder")
    invariant = _q(invariant_sum)
    if invariant == 0:
        raise SPIFibonacciScalingError("invariant_sum must be nonzero")
    source_q = values[source_stage]
    target_q = values[target_stage]
    scale_ratio = target_q / source_q
    translated = source_q * scale_ratio
    if translated != target_q:
        raise SPIFibonacciScalingError("exact finite-stage translation failed")
    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_FIBONACCI_CROSS_STAGE_TRANSLATION_V1",
        "profile": PROFILE,
        "invariant_sum": invariant,
        "source_stage": source_stage,
        "target_stage": target_stage,
        "source_square_state": source_q,
        "target_square_state": target_q,
        "finite_scale_ratio": scale_ratio,
        "translation_equation": "Q[n+1]=lambda[n]*Q[n]",
        "translated_coordinate": translated,
        "residual": translated - target_q,
        "golden_limit_is_symbolic_only": True,
        "finite_ratio_replaced_by_phi": False,
        "projection_only": True,
        "canonical_admission_authority": False,
        "floating_point_authority": False,
    }
    receipt["receipt_sha256"] = sha256(_stable_json(receipt).encode("utf-8")).hexdigest()
    return _exact_json(receipt)

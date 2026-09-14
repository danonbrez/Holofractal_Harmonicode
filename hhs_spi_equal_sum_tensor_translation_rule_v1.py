"""Pass 219 SPI — equal-sum tensor translation normalization rule v1.

HARMONICODE extension
---------------------
Same-sized symmetric matrix/tensor algebra surfaces that satisfy the same exact
sum equation may translate through the common local scalar scale ``a²=1``.

For source tensor T_s and target tensor T_t with the same declared shape and the
same exact nonzero invariant sum S:

    SumEq(T_s) = S
    SumEq(T_t) = S
    pi_L(a²) = 1

then their sum equations normalize to the same scalar layer:

    N_a2(T_s) := SumEq(T_s)/S * pi_L(a²) = 1
    N_a2(T_t) := SumEq(T_t)/S * pi_L(a²) = 1.

Therefore the *equation-normalized tensor surfaces* are translatable at a².
This is not cellwise equality, native tensor identity, or permission to discard
coordinate/order/provenance.  The translation receipt binds same shape, exact
sum equality, symmetry family, and source identities.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Sequence, Tuple

FORMAT = "HHS_SPI_EQUAL_SUM_TENSOR_TRANSLATION_RULE_V1"
VERSION = "1.0.0"
PROFILE = "EQUAL-SUM-SAME-SHAPE-TENSOR-A2-NORMALIZATION-v1"

LO_SHU = (
    (4, 9, 2),
    (3, 5, 7),
    (8, 1, 6),
)
LO_SHU_MAGIC_SUM = 15
SUDOKU_GROUP = tuple(range(1, 10))
SUDOKU_GROUP_SUM = 45


class SPIEqualSumTensorTranslationError(ValueError):
    pass


def _q(value: Any) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise SPIEqualSumTensorTranslationError("exact tensor normalization forbids bool/float arithmetic")
    try:
        return Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise SPIEqualSumTensorTranslationError(f"invalid exact scalar: {value!r}") from exc


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
    raise SPIEqualSumTensorTranslationError(f"unsupported receipt type: {type(value).__name__}")


def _stable_json(value: Any) -> str:
    return json.dumps(_exact_json(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _shape_of(value: Any) -> Tuple[int, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    if not value:
        return (0,)
    child_shapes = tuple(_shape_of(child) for child in value)
    if any(shape != child_shapes[0] for shape in child_shapes[1:]):
        raise SPIEqualSumTensorTranslationError("ragged tensor is not eligible for same-shape translation")
    return (len(value),) + child_shapes[0]


def _flatten(value: Any) -> Tuple[Fraction, ...]:
    if isinstance(value, (list, tuple)):
        out = []
        for child in value:
            out.extend(_flatten(child))
        return tuple(out)
    return (_q(value),)


def _sum_exact(values: Sequence[Any]) -> Fraction:
    total = Fraction(0)
    for value in values:
        total += _q(value)
    return total


def equal_sum_translation_witness(
    *,
    source_id: str,
    target_id: str,
    source_tensor: Sequence[Any],
    target_tensor: Sequence[Any],
    invariant_sum: Any,
    source_sum_equations: Sequence[Any],
    target_sum_equations: Sequence[Any],
    symmetry_family: str,
    layer_id: str,
) -> Dict[str, Any]:
    """Prove equation-level translation between same-sized equal-sum tensors.

    ``source_sum_equations`` and ``target_sum_equations`` are the exact scalar
    sums of the declared symmetric fibers/equations (rows, columns, diagonals,
    Sudoku groups, banks, wraparound fibers, etc.). Every supplied equation must
    equal ``invariant_sum``.
    """
    if not source_id or not target_id or not symmetry_family or not layer_id:
        raise SPIEqualSumTensorTranslationError("stable tensor/layer/symmetry identities are required")
    source_shape = _shape_of(source_tensor)
    target_shape = _shape_of(target_tensor)
    if source_shape != target_shape:
        raise SPIEqualSumTensorTranslationError(f"tensor shape mismatch: {source_shape} != {target_shape}")
    if not source_shape or 0 in source_shape:
        raise SPIEqualSumTensorTranslationError("empty/scalar surfaces are not tensor translation surfaces")

    exact_sum = _q(invariant_sum)
    if exact_sum == 0:
        raise SPIEqualSumTensorTranslationError("equal-sum translation requires a nonzero normalization sum")
    if not source_sum_equations or not target_sum_equations:
        raise SPIEqualSumTensorTranslationError("sum-equation witnesses are required")
    source_sums = tuple(_q(v) for v in source_sum_equations)
    target_sums = tuple(_q(v) for v in target_sum_equations)
    if any(value != exact_sum for value in source_sums):
        raise SPIEqualSumTensorTranslationError("source tensor has a sum equation outside the invariant class")
    if any(value != exact_sum for value in target_sums):
        raise SPIEqualSumTensorTranslationError("target tensor has a sum equation outside the invariant class")
    if len(source_sums) != len(target_sums):
        raise SPIEqualSumTensorTranslationError("same-sized tensor translation requires matching sum-equation cardinality")

    a2 = Fraction(1)
    source_normalized = tuple((value / exact_sum) * a2 for value in source_sums)
    target_normalized = tuple((value / exact_sum) * a2 for value in target_sums)
    if any(value != 1 for value in source_normalized + target_normalized):
        raise SPIEqualSumTensorTranslationError("a² sum normalization did not close to unit")

    receipt: Dict[str, Any] = {
        "schema": "HHS_SPI_EQUAL_SUM_TENSOR_TRANSLATION_RECEIPT_V1",
        "format": FORMAT,
        "version": VERSION,
        "profile": PROFILE,
        "layer_id": layer_id,
        "source_id": source_id,
        "target_id": target_id,
        "source_shape": source_shape,
        "target_shape": target_shape,
        "symmetry_family": symmetry_family,
        "invariant_sum": exact_sum,
        "source_sum_equations": source_sums,
        "target_sum_equations": target_sums,
        "sum_equation_count": len(source_sums),
        "local_scale_symbol": "a²",
        "local_scale": a2,
        "normalization_rule": "N_a2(T,fiber)=fiber_sum(T)/S*a²",
        "source_normalized_equations": source_normalized,
        "target_normalized_equations": target_normalized,
        "translation_relation": "N_a2(source)=N_a2(target)=1 for every declared equal-sum equation",
        "equation_translation_authorized": True,
        "cellwise_tensor_identity_authorized": False,
        "native_tensor_substitution_authorized": False,
        "coordinate_permutation_authorized": False,
        "source_tensor_sha256": sha256(_stable_json(tuple(_flatten(source_tensor))).encode("utf-8")).hexdigest(),
        "target_tensor_sha256": sha256(_stable_json(tuple(_flatten(target_tensor))).encode("utf-8")).hexdigest(),
        "lost_information": [
            "cell values and ordering are not represented by the normalized unit equation",
            "tensor coordinate topology and symmetry orientation require retained provenance",
            "equal normalized sums do not imply native tensor equality",
        ],
        "reverse_lift_status": "none",
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


def lo_shu_translation_witness() -> Dict[str, Any]:
    rotated = (
        (8, 3, 4),
        (1, 5, 9),
        (6, 7, 2),
    )
    source_lines = (
        sum(LO_SHU[0]), sum(LO_SHU[1]), sum(LO_SHU[2]),
        LO_SHU[0][0] + LO_SHU[1][0] + LO_SHU[2][0],
        LO_SHU[0][1] + LO_SHU[1][1] + LO_SHU[2][1],
        LO_SHU[0][2] + LO_SHU[1][2] + LO_SHU[2][2],
        LO_SHU[0][0] + LO_SHU[1][1] + LO_SHU[2][2],
        LO_SHU[0][2] + LO_SHU[1][1] + LO_SHU[2][0],
    )
    target_lines = (
        sum(rotated[0]), sum(rotated[1]), sum(rotated[2]),
        rotated[0][0] + rotated[1][0] + rotated[2][0],
        rotated[0][1] + rotated[1][1] + rotated[2][1],
        rotated[0][2] + rotated[1][2] + rotated[2][2],
        rotated[0][0] + rotated[1][1] + rotated[2][2],
        rotated[0][2] + rotated[1][1] + rotated[2][0],
    )
    return equal_sum_translation_witness(
        source_id="LO_SHU_CANONICAL",
        target_id="LO_SHU_ROTATED",
        source_tensor=LO_SHU,
        target_tensor=rotated,
        invariant_sum=LO_SHU_MAGIC_SUM,
        source_sum_equations=source_lines,
        target_sum_equations=target_lines,
        symmetry_family="LO_SHU_D4_MAGIC_SQUARE",
        layer_id="A2_MAGIC_SQUARE_NORMALIZATION",
    )


def sudoku_group_translation_witness() -> Dict[str, Any]:
    source = (1, 2, 3, 4, 5, 6, 7, 8, 9)
    target = (9, 7, 5, 3, 1, 8, 6, 4, 2)
    return equal_sum_translation_witness(
        source_id="SUDOKU_GROUP_A",
        target_id="SUDOKU_GROUP_B",
        source_tensor=source,
        target_tensor=target,
        invariant_sum=SUDOKU_GROUP_SUM,
        source_sum_equations=(_sum_exact(source),),
        target_sum_equations=(_sum_exact(target),),
        symmetry_family="SUDOKU_PERMUTATION_1_TO_9",
        layer_id="A2_SUDOKU_GROUP_NORMALIZATION",
    )

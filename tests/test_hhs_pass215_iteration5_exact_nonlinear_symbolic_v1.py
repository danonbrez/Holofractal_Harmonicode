from __future__ import annotations

import pytest

from hhs_backend.runtime.hhs_pass215_iteration5_exact_nonlinear_symbolic_v1 import (
    ITERATION4_RECEIPT_HASH72,
    ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
    ITERATION4_TERMINAL_EVIDENCE_HASH216,
    ITERATION4_VALIDATED_HEAD,
    ITERATION4_VALIDATED_TREE,
    Pass215Iteration5ValidationError,
    add,
    exact_attention_scale,
    exact_rmsnorm,
    exact_rope,
    exact_sigmoid,
    exact_silu,
    exact_softmax,
    exp_expr,
    expr_root,
    expr_to_json,
    expression_complexity,
    inv,
    mul,
    pow_rational,
    q,
    rsqrt_expr,
    sqrt_expr,
    sub,
)


def test_iteration4_frozen_roots_are_bound_exactly() -> None:
    assert ITERATION4_VALIDATED_HEAD == "ce35117dd1b54574f2fc98e0254dee0ddcf0e518"
    assert ITERATION4_VALIDATED_TREE == "a1fb44e5c43e4d504a71183ba6eb01405d730293"
    assert ITERATION4_SUITE_OUTPUT_ROOT_HASH216 == "14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb"
    assert ITERATION4_TERMINAL_EVIDENCE_HASH216 == "0462738157042bbd2903ed666a3e05dbc1e27c8a43ea5d2544de9b0c174f87bf"
    assert ITERATION4_RECEIPT_HASH72 == "2SrZvFdR/*41!b++dH9qxM1IrUZMuwuRZmpNw4yl8>QYI(LA9B65A<auqlwyWoi97onfMeMc"


def test_rational_arithmetic_is_canonical_and_exact() -> None:
    assert q(2, 4) == q(1, 2)
    assert q(1, -2) == q(-1, 2)
    assert add(q(1, 6), q(1, 3)) == q(1, 2)
    assert sub(q(7, 6), q(2, 3)) == q(1, 2)
    assert mul(q(6, 5), q(10, 9)) == q(4, 3)
    assert inv(q(-3, 7)) == q(-7, 3)


def test_python_float_is_rejected_at_rational_ingress() -> None:
    with pytest.raises(Pass215Iteration5ValidationError):
        q(1.5)  # type: ignore[arg-type]
    with pytest.raises(Pass215Iteration5ValidationError):
        q(1, 2.0)  # type: ignore[arg-type]
    with pytest.raises(Pass215Iteration5ValidationError):
        expr_to_json(("q", 1.5, 1))  # type: ignore[arg-type]


def test_sqrt_and_rsqrt_reduce_perfect_square_rationals() -> None:
    assert sqrt_expr(q(81, 16)) == q(9, 4)
    assert rsqrt_expr(q(81, 16)) == q(4, 9)
    assert sqrt_expr(q(2))[0] == "sqrt"
    with pytest.raises(Pass215Iteration5ValidationError):
        sqrt_expr(q(-1))
    with pytest.raises(Pass215Iteration5ValidationError):
        rsqrt_expr(q(0))


def test_exact_rmsnorm_perfect_square_control_closes_to_rational() -> None:
    output, record = exact_rmsnorm((q(3), q(3)), epsilon=q(0))
    assert output == (q(1), q(1))
    assert record["mean_square"] == expr_to_json(q(9))
    assert record["normalization"] == expr_to_json(q(1, 3))


def test_rope_position_zero_is_exact_identity() -> None:
    values = (q(1), q(2), q(-3), q(5))
    output, record = exact_rope(values, position=0, rotary_dimension=4)
    assert output == values
    assert record["frequency_rule"] == "theta^(-2*pair_index/rotary_dimension)"


def test_rope_nonzero_retains_canonical_closed_form_without_float() -> None:
    output_a, _ = exact_rope((q(1), q(2), q(3), q(4)), position=7, rotary_dimension=4)
    output_b, _ = exact_rope((q(1), q(2), q(3), q(4)), position=7, rotary_dimension=4)
    assert output_a == output_b
    assert expr_root("test-pass215-i5-rope", output_a) == expr_root("test-pass215-i5-rope", output_b)
    assert all("." not in str(expr_to_json(value)) for value in output_a)


def test_attention_scaling_reduces_when_head_dimension_is_square() -> None:
    output, record = exact_attention_scale((q(4), q(-8)), head_dimension=16)
    assert output == (q(1), q(-2))
    assert record["scale"] == expr_to_json(q(1, 4))


def test_softmax_equal_scores_normalizes_exactly() -> None:
    output, record = exact_softmax((q(5), q(5), q(5), q(5)))
    assert output == (q(1, 4),) * 4
    assert record["numeric_exponential_approximation_performed"] is False


def test_softmax_exact_shift_is_translation_invariant_for_rational_scores() -> None:
    scores = (q(-2), q(0), q(3))
    translated = tuple(add(value, q(17, 5)) for value in scores)
    output_a, _ = exact_softmax(scores)
    output_b, _ = exact_softmax(translated)
    assert output_a == output_b


def test_sigmoid_and_silu_zero_reduce_exactly() -> None:
    assert exact_sigmoid(q(0)) == q(1, 2)
    assert exact_silu(q(0)) == q(0)
    nonzero = exact_silu(q(3, 2))
    assert nonzero[0] in {"mul", "inv", "q"}


def test_symbolic_pow_exp_and_complexity_are_deterministic() -> None:
    power = pow_rational(q(10_000), q(-1, 24))
    exponential = exp_expr(power)
    complexity = expression_complexity((exponential, exponential))
    assert complexity["output_coordinates"] == 2
    assert complexity["unique_expression_nodes"] >= 4
    assert complexity["operator_histogram"]["exp"] == 1
    assert complexity["operator_histogram"]["powq"] == 1
    assert expr_root("test-pass215-i5-expression", exponential) == expr_root("test-pass215-i5-expression", exponential)

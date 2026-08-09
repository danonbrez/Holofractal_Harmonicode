from __future__ import annotations

import pytest

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4
from hhs_backend.runtime import hhs_pass215_iteration15_certified_greedy_logit_v1 as i15


def test_iteration14_closure_is_frozen_parent() -> None:
    assert i15.ITERATION14_CLOSURE_HEAD == "9780b711fdcfa6624dc9e787b140920ca3f5f875"
    assert i15.ITERATION14_CLOSURE_TREE == "9475d1053c08f4ae6195d28407dffc86b97c6113"
    assert i15.ITERATION14_CONTINUATION_ROOT_HASH216 == "21c9ccbe769f818862a4959ee284aafe65af6d0638ce9c05c2ed52c89387b5eb"


def test_certification_policy_is_true_magnitude_not_hash_order() -> None:
    assert i15.SELECTION_POLICY == "STRICT_CERTIFIED_DYADIC_INTERVAL_ARGMAX_THEN_TOKEN_ID"
    assert i15.SELECTION_SEMANTICS == "TRUE_LOGIT_MAGNITUDE_ORDER_CERTIFIED_BY_OUTWARD_INTEGER_BOUNDS"
    assert i15.CERTIFICATION_BITS == 256


def test_float_authority_is_rejected() -> None:
    with pytest.raises(i15.Pass215Iteration15ValidationError, match="PASS215_I15_FLOAT_FORBIDDEN"):
        i15._reject_floats({"bad": 0.25})


def test_dyadic_point_encloses_exact_rational() -> None:
    ctx = i15.CertifiedDyadicContext(64)
    lo, hi = ctx.point(1, 3)
    scale = ctx.scale
    assert lo * 3 <= scale <= hi * 3
    assert hi - lo <= 1


def test_interval_mul_and_inverse_are_outward() -> None:
    ctx = i15.CertifiedDyadicContext(64)
    one_third = ctx.point(1, 3)
    three = ctx.point(3)
    product = ctx.mul(one_third, three)
    assert product[0] <= ctx.scale <= product[1]
    reciprocal = ctx.inv(three)
    assert reciprocal[0] <= one_third[1]
    assert reciprocal[1] >= one_third[0]


def test_rsqrt_exact_square_control() -> None:
    ctx = i15.CertifiedDyadicContext(64)
    result = ctx.rsqrt(ctx.point(4))
    assert result == ctx.point(1, 2)


def test_powq_exact_square_root_control() -> None:
    ctx = i15.CertifiedDyadicContext(64)
    result = ctx.pow_integer_rational(4, 1, 2)
    assert result == ctx.point(2)
    inverse = ctx.pow_integer_rational(4, -1, 2)
    assert inverse == ctx.point(1, 2)


def test_transcendental_identity_controls() -> None:
    ctx = i15.CertifiedDyadicContext(64)
    zero = (0, 0)
    assert ctx.exp(zero) == ctx.point(1)
    assert ctx.sin(zero) == zero
    assert ctx.cos(zero) == ctx.point(1)


def test_q4_interval_linear_exact_integer_control() -> None:
    ctx = i15.CertifiedDyadicContext(64)
    block = i4.CompiledBlock(1, 1, tuple(1 for _ in range(i4.Q4_0_BLOCK_ELEMENTS)))
    compiled = i4.CompiledTensor(
        name="control",
        ne0=i4.Q4_0_BLOCK_ELEMENTS,
        ne1=1,
        source_sha256="0" * 64,
        source_bytes=i4.Q4_0_BLOCK_BYTES,
        blocks_per_row=1,
        rows=((block,),),
        descriptor_root_hash216="1" * 64,
    )
    output = i15._interval_q4_linear(
        ctx,
        compiled,
        tuple(ctx.point(1) for _ in range(i4.Q4_0_BLOCK_ELEMENTS)),
    )
    assert output == (ctx.point(i4.Q4_0_BLOCK_ELEMENTS),)


def test_strict_argmax_requires_complete_separation() -> None:
    # Patch the contracted vocabulary size only inside the test surface so the
    # comparator can be tested without materializing 32,000 synthetic entries.
    original = i15.VOCABULARY_SIZE
    i15.VOCABULARY_SIZE = 3
    try:
        roots = ("a" * 64, "b" * 64, "c" * 64)
        tokenizer = {"tokens": ("a", "b", "c")}
        record = i15._certify_strict_argmax(
            ((0, 1), (5, 6), (2, 3)),
            symbolic_logit_roots=roots,
            tokenizer=tokenizer,
            interval_suite_root_hash216="d" * 64,
            bits=64,
        )
        assert record["selected_token_id"] == 1
        assert record["certified_true_argmax"] is True
        assert record["strict_margin_lower_bound"]["numerator"] == 2
        with pytest.raises(i15.Pass215Iteration15ValidationError, match="STRICT_ARGMAX_NOT_CERTIFIED"):
            i15._certify_strict_argmax(
                ((0, 5), (4, 6), (2, 3)),
                symbolic_logit_roots=roots,
                tokenizer=tokenizer,
                interval_suite_root_hash216="d" * 64,
                bits=64,
            )
    finally:
        i15.VOCABULARY_SIZE = original

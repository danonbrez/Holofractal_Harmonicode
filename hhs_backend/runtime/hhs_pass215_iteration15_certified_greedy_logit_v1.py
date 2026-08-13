"""Pass 215 Iteration 15 certified exact greedy-logit selection.

Iteration 14 proved deterministic autoregressive continuation while deliberately
selecting by Hash216 identity rather than logit magnitude.  Iteration 15 crosses
that strict barrier for the authenticated four-token ``Hello world!`` witness.

The authoritative comparison path is an integer-only outward-rounded dyadic
interval replay of the same GGUF embeddings, six transformer blocks, terminal
RMSNorm, and explicit Q8_0 vocabulary projection.  Transcendental functions are
not assigned approximate canonical values: each use is enclosed by a proven
rational interval, and greedy authority is promoted only if one logit's lower
bound is strictly greater than every other logit's upper bound.

The certified token is then appended through the frozen Iteration-14 append-only
KV continuation machinery.  This iteration proves one true greedy continuation
step for the contracted witness only.  It does not claim arbitrary generation,
arbitrary sequence length, dense-forward replacement, runtime mutation, or
canonical mutation authority.
"""
from __future__ import annotations

from hashlib import sha256
from math import factorial, gcd, isqrt
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration8_multi_token_causal_attention_v1 as i8
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration10_exact_text_token_ingress_v1 as i10
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11
from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12
from hhs_backend.runtime import hhs_pass215_iteration13_terminal_model_head_v1 as i13
from hhs_backend.runtime import hhs_pass215_iteration14_autoregressive_continuation_v1 as i14

CONTRACT = "HHS-P215-I15-CERTIFIED-EXACT-GREEDY-LOGIT-SELECTION"
PASS_NUMBER = 215
ITERATION = 15
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_15_CERTIFIED_GREEDY_LOGIT_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_15_CERTIFIED_GREEDY_LOGIT_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_15_CERTIFIED_GREEDY_LOGIT_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_15_CERTIFIED_GREEDY_LOGIT_BENCHMARK"

ITERATION14_CLOSURE_HEAD = "9780b711fdcfa6624dc9e787b140920ca3f5f875"
ITERATION14_CLOSURE_TREE = "9475d1053c08f4ae6195d28407dffc86b97c6113"
ITERATION14_GENERATED_TOKEN_IDS = (29009, 7250)
ITERATION14_SELECTION_ROOTS = (
    "1ffdd8c7eaf4adc7f529f435350aa9f4f8b1333ce45e1b009f307fe247a1cffb",
    "30647ae62a968659b525a99a824ae811185ac1c068e49a5df60a813e3d6ebfac",
)
ITERATION14_APPEND_FORWARD_ROOTS = (
    "0dc88bfad85007f7ff6447680c3c12919fd93aee0f5813e3dbc7bfcb41c04d1b",
    "2823ef988909e3c2b5a816a6e54e514d0e025e96fcb88d26df65151907238181",
)
ITERATION14_CONTINUATION_ROOT_HASH216 = "21c9ccbe769f818862a4959ee284aafe65af6d0638ce9c05c2ed52c89387b5eb"
ITERATION14_FINAL_DAG_ROOT_HASH216 = "27c8c282b7afede7873374b6377df1a763ecf50cfbcc5ff422075cc5d2f91891"
ITERATION14_SUITE_ROOT_HASH216 = "04935537843adbd98d76583be748725a63f1a04852aefee753373778b4616da3"
ITERATION14_EVIDENCE_ROOT_HASH216 = "5ff6c491e72327e602fad54ea8cdab3e989a033fb8c4be3e40348ab8206a5710"
ITERATION14_RECEIPT_HASH72 = "Afzln*6<JHol646Lz+3mVuowQB)cS673kS(Hx0z*!nSTBoygeMtJpvfN>8AoznG816seDy3H"
ITERATION14_CLOSURE_ARTIFACT_SHA256 = "ebaedbc8f3ddbd46531081eaa364c0bbb33f1d9f3476d5c0694152478876c18c"

REAL_MODEL_SHA256 = i14.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i14.CONTRACTED_PROMPT
FROZEN_TOKEN_IDS = i14.FROZEN_TOKEN_IDS
PREFIX_SEQUENCE_LENGTH = i14.PREFIX_SEQUENCE_LENGTH
EMBEDDING_WIDTH = i14.EMBEDDING_WIDTH
HEAD_COUNT = i14.HEAD_COUNT
HEAD_DIMENSION = i14.HEAD_DIMENSION
AUTHENTICATED_BLOCK_COUNT = i14.AUTHENTICATED_BLOCK_COUNT
VOCABULARY_SIZE = i14.VOCABULARY_SIZE
CERTIFICATION_BITS = 256
EXP_TAYLOR_TERMS = 48
TRIG_TAYLOR_TERMS = 40
SELECTION_POLICY = "STRICT_CERTIFIED_DYADIC_INTERVAL_ARGMAX_THEN_TOKEN_ID"
SELECTION_SEMANTICS = "TRUE_LOGIT_MAGNITUDE_ORDER_CERTIFIED_BY_OUTWARD_INTEGER_BOUNDS"
PROCESSED_GREEDY_APPEND_COUNT = 1

Interval = tuple[int, int]


class Pass215Iteration15Error(RuntimeError):
    pass


class Pass215Iteration15ValidationError(Pass215Iteration15Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration15ValidationError(f"PASS215_I15_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _floor_div(numerator: int, denominator: int) -> int:
    if denominator == 0:
        raise Pass215Iteration15ValidationError("PASS215_I15_DIVISION_BY_ZERO")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    return int(numerator) // int(denominator)


def _ceil_div(numerator: int, denominator: int) -> int:
    return -_floor_div(-int(numerator), int(denominator))


def _nth_root_floor(value: int, degree: int) -> int:
    value = int(value)
    degree = int(degree)
    if value < 0 or degree <= 0:
        raise Pass215Iteration15ValidationError("PASS215_I15_NTH_ROOT_DOMAIN_INVALID")
    if value < 2 or degree == 1:
        return value
    high_bits = (value.bit_length() + degree - 1) // degree + 1
    low, high = 0, 1 << high_bits
    while low + 1 < high:
        middle = (low + high) // 2
        if pow(middle, degree) <= value:
            low = middle
        else:
            high = middle
    return low


def _floor_sqrt_ratio(numerator: int, denominator: int) -> int:
    if numerator < 0 or denominator <= 0:
        raise Pass215Iteration15ValidationError("PASS215_I15_SQRT_RATIO_DOMAIN_INVALID")
    return isqrt(int(numerator) // int(denominator))


def _ceil_sqrt_ratio(numerator: int, denominator: int) -> int:
    lower = _floor_sqrt_ratio(numerator, denominator)
    return lower if lower * lower * denominator == numerator else lower + 1


class CertifiedDyadicContext:
    """Integer-only outward-rounded fixed-dyadic interval arithmetic."""

    def __init__(self, bits: int = CERTIFICATION_BITS) -> None:
        if bits < 64:
            raise Pass215Iteration15ValidationError("PASS215_I15_CERTIFICATION_BITS_TOO_SMALL")
        self.bits = int(bits)
        self.scale = 1 << self.bits
        self.exp_calls = 0
        self.sin_calls = 0
        self.cos_calls = 0
        self.rsqrt_calls = 0
        self._trig_cache: dict[tuple[int, int], tuple[Interval, Interval]] = {}

    def _check(self, value: Interval) -> Interval:
        lo, hi = int(value[0]), int(value[1])
        if lo > hi:
            raise Pass215Iteration15ValidationError("PASS215_I15_INTERVAL_ORDER_INVALID")
        return lo, hi

    def point(self, numerator: int, denominator: int = 1) -> Interval:
        numerator, denominator = int(numerator), int(denominator)
        if denominator <= 0:
            raise Pass215Iteration15ValidationError("PASS215_I15_RATIONAL_DENOMINATOR_INVALID")
        scaled = numerator * self.scale
        return self._check((_floor_div(scaled, denominator), _ceil_div(scaled, denominator)))

    def add(self, left: Interval, right: Interval) -> Interval:
        left, right = self._check(left), self._check(right)
        return self._check((left[0] + right[0], left[1] + right[1]))

    def neg(self, value: Interval) -> Interval:
        lo, hi = self._check(value)
        return -hi, -lo

    def sub(self, left: Interval, right: Interval) -> Interval:
        return self.add(left, self.neg(right))

    def mul_int(self, value: Interval, multiplier: int) -> Interval:
        lo, hi = self._check(value)
        multiplier = int(multiplier)
        a, b = lo * multiplier, hi * multiplier
        return (a, b) if a <= b else (b, a)

    def mul_rat(self, value: Interval, numerator: int, denominator: int = 1) -> Interval:
        lo, hi = self._check(value)
        numerator, denominator = int(numerator), int(denominator)
        if denominator <= 0:
            raise Pass215Iteration15ValidationError("PASS215_I15_RATIONAL_DENOMINATOR_INVALID")
        a, b = lo * numerator, hi * numerator
        low_num, high_num = (a, b) if a <= b else (b, a)
        return self._check((_floor_div(low_num, denominator), _ceil_div(high_num, denominator)))

    def mul(self, left: Interval, right: Interval) -> Interval:
        left, right = self._check(left), self._check(right)
        products = (
            left[0] * right[0], left[0] * right[1],
            left[1] * right[0], left[1] * right[1],
        )
        return self._check((
            _floor_div(min(products), self.scale),
            _ceil_div(max(products), self.scale),
        ))

    def inv(self, value: Interval) -> Interval:
        lo, hi = self._check(value)
        if lo <= 0 <= hi:
            raise Pass215Iteration15ValidationError("PASS215_I15_INTERVAL_INVERSE_ZERO_CROSSING")
        square = self.scale * self.scale
        return self._check((_floor_div(square, hi), _ceil_div(square, lo)))

    def rsqrt(self, value: Interval) -> Interval:
        lo, hi = self._check(value)
        if lo <= 0:
            raise Pass215Iteration15ValidationError("PASS215_I15_RSQRT_NONPOSITIVE_INTERVAL")
        self.rsqrt_calls += 1
        numerator = self.scale * self.scale * self.scale
        return self._check((
            _floor_sqrt_ratio(numerator, hi),
            _ceil_sqrt_ratio(numerator, lo),
        ))

    def pow_integer_rational(self, base: int, numerator: int, denominator: int) -> Interval:
        base, numerator, denominator = int(base), int(numerator), int(denominator)
        if base <= 0 or denominator <= 0:
            raise Pass215Iteration15ValidationError("PASS215_I15_POWQ_DOMAIN_INVALID")
        if numerator == 0:
            return self.point(1)
        common = gcd(abs(numerator), denominator)
        numerator //= common
        denominator //= common
        if numerator < 0:
            return self.inv(self.pow_integer_rational(base, -numerator, denominator))
        target = pow(base, numerator) * pow(self.scale, denominator)
        lower = _nth_root_floor(target, denominator)
        upper = lower if pow(lower, denominator) == target else lower + 1
        return self._check((lower, upper))

    def _remainder_bound(self, max_abs_scaled: int, degree: int, coefficient_denominator: int) -> int:
        max_abs_scaled = int(max_abs_scaled)
        if max_abs_scaled == 0:
            return 0
        numerator = pow(max_abs_scaled, degree)
        denominator = pow(self.scale, degree - 1) * int(coefficient_denominator)
        return _ceil_div(numerator, denominator)

    def exp(self, value: Interval) -> Interval:
        value = self._check(value)
        self.exp_calls += 1
        if value == (0, 0):
            return self.point(1)
        reduced = value
        halvings = 0
        threshold = self.scale // 8
        while max(abs(reduced[0]), abs(reduced[1])) > threshold:
            reduced = self.mul_rat(reduced, 1, 2)
            halvings += 1
            if halvings > 64:
                raise Pass215Iteration15ValidationError("PASS215_I15_EXP_RANGE_REDUCTION_UNBOUNDED")
        term = self.point(1)
        total = term
        for order in range(1, EXP_TAYLOR_TERMS + 1):
            term = self.mul(term, reduced)
            term = self.mul_rat(term, 1, order)
            total = self.add(total, term)
        maximum = max(abs(reduced[0]), abs(reduced[1]))
        remainder = self._remainder_bound(
            maximum,
            EXP_TAYLOR_TERMS + 1,
            factorial(EXP_TAYLOR_TERMS + 1),
        )
        # |reduced| <= 1/8 implies exp(|reduced|) < 2, so doubling the
        # Lagrange/Taylor term is a strict rational remainder bound.
        remainder *= 2
        total = (max(0, total[0] - remainder), total[1] + remainder)
        for _ in range(halvings):
            total = self.mul(total, total)
        return self._check(total)

    def sin(self, value: Interval) -> Interval:
        value = self._check(value)
        self.sin_calls += 1
        if value == (0, 0):
            return (0, 0)
        maximum = max(abs(value[0]), abs(value[1]))
        if maximum > 4 * self.scale:
            raise Pass215Iteration15ValidationError("PASS215_I15_SIN_ARGUMENT_OUTSIDE_CONTRACT")
        square = self.mul(value, value)
        term = value
        total = value
        for index in range(1, TRIG_TAYLOR_TERMS):
            term = self.mul(term, square)
            term = self.mul_rat(term, -1, (2 * index) * (2 * index + 1))
            total = self.add(total, term)
        degree = 2 * TRIG_TAYLOR_TERMS
        remainder = self._remainder_bound(maximum, degree, factorial(degree))
        return self._check((total[0] - remainder, total[1] + remainder))

    def cos(self, value: Interval) -> Interval:
        value = self._check(value)
        self.cos_calls += 1
        if value == (0, 0):
            return self.point(1)
        maximum = max(abs(value[0]), abs(value[1]))
        if maximum > 4 * self.scale:
            raise Pass215Iteration15ValidationError("PASS215_I15_COS_ARGUMENT_OUTSIDE_CONTRACT")
        square = self.mul(value, value)
        term = self.point(1)
        total = term
        for index in range(1, TRIG_TAYLOR_TERMS):
            term = self.mul(term, square)
            term = self.mul_rat(term, -1, (2 * index - 1) * (2 * index))
            total = self.add(total, term)
        degree = 2 * TRIG_TAYLOR_TERMS - 1
        remainder = self._remainder_bound(maximum, degree, factorial(degree))
        return self._check((total[0] - remainder, total[1] + remainder))

    def rope_trig(self, position: int, pair_index: int) -> tuple[Interval, Interval]:
        key = (int(position), int(pair_index))
        prior = self._trig_cache.get(key)
        if prior is not None:
            return prior
        if position < 0 or not 0 <= pair_index < HEAD_DIMENSION // 2:
            raise Pass215Iteration15ValidationError("PASS215_I15_ROPE_TRIG_INDEX_INVALID")
        if position == 0:
            result = (self.point(1), (0, 0))
        else:
            frequency = self.pow_integer_rational(10_000, -2 * pair_index, HEAD_DIMENSION)
            angle = self.mul_int(frequency, position)
            result = (self.cos(angle), self.sin(angle))
        self._trig_cache[key] = result
        return result

    def manifest(self) -> Mapping[str, Any]:
        payload = {
            "bits": self.bits,
            "scale_denominator": self.scale,
            "exp_taylor_terms": EXP_TAYLOR_TERMS,
            "trig_taylor_terms": TRIG_TAYLOR_TERMS,
            "arithmetic": "OUTWARD_ROUNDED_INTEGER_DYADIC_INTERVALS",
            "float_operations_authorized": False,
            "transcendental_point_values_authorized": False,
            "selection_requires_strict_interval_separation": True,
        }
        return {
            **payload,
            "exp_calls": self.exp_calls,
            "sin_calls": self.sin_calls,
            "cos_calls": self.cos_calls,
            "rsqrt_calls": self.rsqrt_calls,
            "manifest_root_hash216": i4base.hash216(
                "pass215-i15-certified-dyadic-context", i4base.canonical_bytes(payload)
            ),
        }


def _iteration14_bindings() -> Mapping[str, Any]:
    return {
        "iteration14_closure_head": ITERATION14_CLOSURE_HEAD,
        "iteration14_closure_tree": ITERATION14_CLOSURE_TREE,
        "iteration14_generated_token_ids": list(ITERATION14_GENERATED_TOKEN_IDS),
        "iteration14_selection_roots": list(ITERATION14_SELECTION_ROOTS),
        "iteration14_append_forward_roots": list(ITERATION14_APPEND_FORWARD_ROOTS),
        "iteration14_continuation_root_hash216": ITERATION14_CONTINUATION_ROOT_HASH216,
        "iteration14_final_dag_root_hash216": ITERATION14_FINAL_DAG_ROOT_HASH216,
        "iteration14_suite_root_hash216": ITERATION14_SUITE_ROOT_HASH216,
        "iteration14_evidence_root_hash216": ITERATION14_EVIDENCE_ROOT_HASH216,
        "iteration14_receipt_hash72": ITERATION14_RECEIPT_HASH72,
        "iteration14_closure_artifact_sha256": ITERATION14_CLOSURE_ARTIFACT_SHA256,
    }


def _validate_frozen_iteration14_evidence(evidence: Mapping[str, Any]) -> None:
    i14.validate_autoregressive_continuation_evidence(evidence)
    continuation = evidence["generated_continuation"]
    checks = {
        "generated_ids": (tuple(int(x) for x in continuation["generated_token_ids"]), ITERATION14_GENERATED_TOKEN_IDS),
        "selection_roots": (tuple(x["selection_root_hash216"] for x in continuation["selection_records"]), ITERATION14_SELECTION_ROOTS),
        "append_roots": (tuple(x["append_forward_root_hash216"] for x in continuation["append_records"]), ITERATION14_APPEND_FORWARD_ROOTS),
        "continuation": (continuation["continuation_root_hash216"], ITERATION14_CONTINUATION_ROOT_HASH216),
        "dag": (continuation["final_symbolic_dag"]["ordered_node_root_hash216"], ITERATION14_FINAL_DAG_ROOT_HASH216),
        "suite": (evidence["autoregressive_continuation_suite_root_hash216"], ITERATION14_SUITE_ROOT_HASH216),
        "evidence": (evidence["evidence_root_hash216"], ITERATION14_EVIDENCE_ROOT_HASH216),
        "receipt": (evidence["receipt_hash72"], ITERATION14_RECEIPT_HASH72),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise Pass215Iteration15ValidationError(f"PASS215_I15_ITERATION14_ROOT_MISMATCH:{name}")


def _interval_sum(ctx: CertifiedDyadicContext, values: Sequence[Interval]) -> Interval:
    total: Interval = (0, 0)
    for value in values:
        total = ctx.add(total, value)
    return total


def _interval_q4_linear(
    ctx: CertifiedDyadicContext,
    compiled: Any,
    inputs: Sequence[Interval],
) -> tuple[Interval, ...]:
    if len(inputs) != compiled.ne0:
        raise Pass215Iteration15ValidationError("PASS215_I15_Q4_LINEAR_GEOMETRY_INVALID")
    outputs: list[Interval] = []
    for row in compiled.rows:
        total: Interval = (0, 0)
        for block_index, block in enumerate(row):
            base = block_index * i4base.Q4_0_BLOCK_ELEMENTS
            inner: Interval = (0, 0)
            for local_index, quant in enumerate(block.quant_integers):
                inner = ctx.add(inner, ctx.mul_int(inputs[base + local_index], int(quant)))
            total = ctx.add(
                total,
                ctx.mul_rat(inner, int(block.scale_numerator), int(block.scale_denominator)),
            )
        outputs.append(total)
    return tuple(outputs)


def _interval_rmsnorm(
    ctx: CertifiedDyadicContext,
    values: Sequence[Interval],
    weights: Sequence[tuple[int, int]],
) -> tuple[Interval, ...]:
    if not values or len(values) != len(weights):
        raise Pass215Iteration15ValidationError("PASS215_I15_RMSNORM_GEOMETRY_INVALID")
    squares = tuple(ctx.mul(value, value) for value in values)
    mean = ctx.mul_rat(_interval_sum(ctx, squares), 1, len(values))
    radicand = ctx.add(mean, ctx.point(*i7.RMS_EPSILON))
    normalization = ctx.rsqrt(radicand)
    return tuple(
        ctx.mul_rat(ctx.mul(value, normalization), weight[0], weight[1])
        for value, weight in zip(values, weights)
    )


def _interval_rope_token(
    ctx: CertifiedDyadicContext,
    values: Sequence[Interval],
    *,
    position: int,
) -> tuple[Interval, ...]:
    if len(values) != EMBEDDING_WIDTH:
        raise Pass215Iteration15ValidationError("PASS215_I15_ROPE_GEOMETRY_INVALID")
    if position == 0:
        return tuple(values)
    output: list[Interval] = []
    for head in range(HEAD_COUNT):
        start = head * HEAD_DIMENSION
        for pair_index in range(HEAD_DIMENSION // 2):
            left = values[start + 2 * pair_index]
            right = values[start + 2 * pair_index + 1]
            cosine, sine = ctx.rope_trig(position, pair_index)
            output.append(ctx.sub(ctx.mul(left, cosine), ctx.mul(right, sine)))
            output.append(ctx.add(ctx.mul(left, sine), ctx.mul(right, cosine)))
    return tuple(output)


def _interval_dot(
    ctx: CertifiedDyadicContext,
    left: Sequence[Interval],
    right: Sequence[Interval],
) -> Interval:
    if len(left) != len(right) or not left:
        raise Pass215Iteration15ValidationError("PASS215_I15_DOT_GEOMETRY_INVALID")
    return _interval_sum(ctx, tuple(ctx.mul(a, b) for a, b in zip(left, right)))


def _interval_softmax(
    ctx: CertifiedDyadicContext,
    scores: Sequence[Interval],
) -> tuple[Interval, ...]:
    if not scores:
        raise Pass215Iteration15ValidationError("PASS215_I15_SOFTMAX_EMPTY")
    if len(scores) == 1:
        return (ctx.point(1),)
    exponentials = tuple(ctx.exp(score) for score in scores)
    denominator = _interval_sum(ctx, exponentials)
    inverse = ctx.inv(denominator)
    return tuple(ctx.mul(value, inverse) for value in exponentials)


def _interval_silu(ctx: CertifiedDyadicContext, value: Interval) -> Interval:
    sigmoid = ctx.inv(ctx.add(ctx.point(1), ctx.exp(ctx.neg(value))))
    return ctx.mul(value, sigmoid)


def _interval_block(
    ctx: CertifiedDyadicContext,
    hidden: Sequence[Interval],
    block_binding: Mapping[str, Any],
    cache: MutableMapping[str, list[tuple[Interval, ...]]],
    *,
    block_index: int,
    position: int,
) -> tuple[Interval, ...]:
    names = i11._block_tensor_names(block_index)
    norms = block_binding["norm_tensors"]
    attn_weights = i7._norm_values(norms[names["norms"][0]])
    ffn_weights = i7._norm_values(norms[names["norms"][1]])
    linears = block_binding["compiled_linears"]

    attn_norm = _interval_rmsnorm(ctx, hidden, attn_weights)
    q_values = _interval_q4_linear(ctx, linears[f"blk.{block_index}.attn_q.weight"], attn_norm)
    k_values = _interval_q4_linear(ctx, linears[f"blk.{block_index}.attn_k.weight"], attn_norm)
    v_values = _interval_q4_linear(ctx, linears[f"blk.{block_index}.attn_v.weight"], attn_norm)
    q_rope = _interval_rope_token(ctx, q_values, position=position)
    k_rope = _interval_rope_token(ctx, k_values, position=position)
    cache["k_rope"].append(k_rope)
    cache["v"].append(v_values)
    all_k = tuple(cache["k_rope"])
    all_v = tuple(cache["v"])
    if len(all_k) != position + 1:
        raise Pass215Iteration15ValidationError("PASS215_I15_INTERVAL_CACHE_POSITION_INVALID")

    scale = ctx.rsqrt(ctx.point(HEAD_DIMENSION))
    weighted: list[Interval] = []
    for head in range(HEAD_COUNT):
        start, end = head * HEAD_DIMENSION, (head + 1) * HEAD_DIMENSION
        scores = tuple(
            ctx.mul(
                _interval_dot(ctx, q_rope[start:end], all_k[key_position][start:end]),
                scale,
            )
            for key_position in range(position + 1)
        )
        probabilities = _interval_softmax(ctx, scores)
        for dimension in range(HEAD_DIMENSION):
            weighted.append(
                _interval_sum(
                    ctx,
                    tuple(
                        ctx.mul(probabilities[key_position], all_v[key_position][start + dimension])
                        for key_position in range(position + 1)
                    ),
                )
            )
    attn_output = _interval_q4_linear(
        ctx, linears[f"blk.{block_index}.attn_output.weight"], tuple(weighted)
    )
    post_attn = tuple(ctx.add(a, b) for a, b in zip(hidden, attn_output))
    ffn_norm = _interval_rmsnorm(ctx, post_attn, ffn_weights)
    gate = _interval_q4_linear(ctx, linears[f"blk.{block_index}.ffn_gate.weight"], ffn_norm)
    activated = tuple(_interval_silu(ctx, value) for value in gate)
    up = _interval_q4_linear(ctx, linears[f"blk.{block_index}.ffn_up.weight"], ffn_norm)
    gated = tuple(ctx.mul(a, b) for a, b in zip(activated, up))
    down = _interval_q4_linear(ctx, linears[f"blk.{block_index}.ffn_down.weight"], gated)
    return tuple(ctx.add(a, b) for a, b in zip(post_attn, down))


def _interval_q8_projection(
    ctx: CertifiedDyadicContext,
    output_payload: bytes,
    normalized: Sequence[Interval],
) -> tuple[Interval, ...]:
    if len(normalized) != EMBEDDING_WIDTH:
        raise Pass215Iteration15ValidationError("PASS215_I15_Q8_INPUT_GEOMETRY_INVALID")
    expected = VOCABULARY_SIZE * i13.Q8_ROW_BYTES
    if len(output_payload) != expected:
        raise Pass215Iteration15ValidationError("PASS215_I15_Q8_PAYLOAD_GEOMETRY_INVALID")
    scale_cache: dict[bytes, tuple[int, int]] = {}
    logits: list[Interval] = []
    cursor = 0
    for _row_index in range(VOCABULARY_SIZE):
        total: Interval = (0, 0)
        input_offset = 0
        for _block_index in range(i13.Q8_BLOCKS_PER_ROW):
            block = output_payload[cursor:cursor + i13.Q8_LAYOUT.block_bytes]
            cursor += i13.Q8_LAYOUT.block_bytes
            scale_raw = block[:2]
            scale = scale_cache.get(scale_raw)
            if scale is None:
                scale = i4base.decode_binary16_exact(scale_raw)
                scale_cache[scale_raw] = scale
            inner: Interval = (0, 0)
            for local_index, byte in enumerate(block[2:34]):
                code = int(byte) if int(byte) < 128 else int(byte) - 256
                inner = ctx.add(inner, ctx.mul_int(normalized[input_offset + local_index], code))
            total = ctx.add(total, ctx.mul_rat(inner, scale[0], scale[1]))
            input_offset += i13.Q8_LAYOUT.block_elements
        logits.append(total)
    if cursor != len(output_payload):
        raise Pass215Iteration15ValidationError("PASS215_I15_Q8_PAYLOAD_CURSOR_INVALID")
    return tuple(logits)


def _execute_certified_prefix(
    raw: bytes,
    tokenizer: Mapping[str, Any],
    bindings: Mapping[int, Mapping[str, Any]],
    terminal_binding: Mapping[str, Any],
    *,
    bits: int = CERTIFICATION_BITS,
) -> Mapping[str, Any]:
    ctx = CertifiedDyadicContext(bits)
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, FROZEN_TOKEN_IDS)
    caches: MutableMapping[int, MutableMapping[str, list[tuple[Interval, ...]]]] = {
        index: {"k_rope": [], "v": []} for index in i12.BLOCK_INDEXES
    }
    final_hidden: tuple[Interval, ...] | None = None
    for position, row in enumerate(embeddings["rows"]):
        hidden = tuple(ctx.point(numerator, denominator) for numerator, denominator in row)
        for block_index in i12.BLOCK_INDEXES:
            hidden = _interval_block(
                ctx,
                hidden,
                bindings[block_index],
                caches[block_index],
                block_index=block_index,
                position=position,
            )
        final_hidden = tuple(hidden)
    if final_hidden is None:
        raise Pass215Iteration15ValidationError("PASS215_I15_PREFIX_FORWARD_EMPTY")
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    normalized = _interval_rmsnorm(ctx, final_hidden, norm_weights)
    logits = _interval_q8_projection(ctx, terminal_binding["output_payload"], normalized)
    interval_leaf_roots = [
        i4base.hash216(
            "pass215-i15-logit-interval-leaf",
            i4base.canonical_bytes({"token_id": token_id, "lower": value[0], "upper": value[1], "bits": bits}),
        )
        for token_id, value in enumerate(logits)
    ]
    return {
        "context": ctx,
        "logits": logits,
        "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
        "interval_suite_root_hash216": i4base.hash216(
            "pass215-i15-complete-logit-interval-suite",
            i4base.canonical_bytes(interval_leaf_roots),
        ),
        "interval_leaf_count": len(interval_leaf_roots),
    }


def _certify_strict_argmax(
    logits: Sequence[Interval],
    *,
    symbolic_logit_roots: Sequence[str],
    tokenizer: Mapping[str, Any],
    interval_suite_root_hash216: str,
    bits: int,
) -> Mapping[str, Any]:
    if len(logits) != VOCABULARY_SIZE or len(symbolic_logit_roots) != VOCABULARY_SIZE:
        raise Pass215Iteration15ValidationError("PASS215_I15_ARGMAX_GEOMETRY_INVALID")
    selected_id = max(range(VOCABULARY_SIZE), key=lambda token_id: (int(logits[token_id][0]), -token_id))
    competitors = [token_id for token_id in range(VOCABULARY_SIZE) if token_id != selected_id]
    competitor_id = max(competitors, key=lambda token_id: (int(logits[token_id][1]), -token_id))
    selected = logits[selected_id]
    competitor = logits[competitor_id]
    margin = int(selected[0]) - int(competitor[1])
    if margin <= 0:
        raise Pass215Iteration15ValidationError(
            f"PASS215_I15_STRICT_ARGMAX_NOT_CERTIFIED:selected={selected_id}:competitor={competitor_id}:margin={margin}:bits={bits}"
        )
    record: dict[str, Any] = {
        "policy": SELECTION_POLICY,
        "semantics": SELECTION_SEMANTICS,
        "candidate_count": VOCABULARY_SIZE,
        "certification_bits": bits,
        "dyadic_denominator": 1 << bits,
        "complete_logit_interval_suite_root_hash216": interval_suite_root_hash216,
        "selected_token_id": selected_id,
        "selected_token": str(tokenizer["tokens"][selected_id]),
        "selected_symbolic_logit_root_hash216": str(symbolic_logit_roots[selected_id]),
        "selected_logit_interval": {"lower_scaled": selected[0], "upper_scaled": selected[1]},
        "strongest_competitor_token_id": competitor_id,
        "strongest_competitor_token": str(tokenizer["tokens"][competitor_id]),
        "strongest_competitor_symbolic_logit_root_hash216": str(symbolic_logit_roots[competitor_id]),
        "strongest_competitor_logit_interval": {"lower_scaled": competitor[0], "upper_scaled": competitor[1]},
        "strict_margin_lower_bound": {"numerator": margin, "denominator": 1 << bits},
        "strict_interval_separation": True,
        "certified_true_argmax": True,
        "numeric_logit_magnitude_ordering_performed": True,
        "numeric_logit_point_values_materialized": False,
        "probabilistic_sampling_performed": False,
        "canonical_float_interpretation_performed": False,
        "approximate_transcendental_point_evaluation_performed": False,
    }
    record["selection_root_hash216"] = i4base.hash216(
        "pass215-i15-certified-greedy-selection", i4base.canonical_bytes(record)
    )
    return record


def _symbolic_prefix_and_logits(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    prompt: str,
    expected_sha256: str | None,
) -> Mapping[str, Any]:
    frozen12 = i12.build_all_six_block_evidence(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    i13._validate_frozen_iteration12_evidence(frozen12)
    prefix = i13._reconstruct_six_block_prefix(raw, prompt=prompt, frozen_evidence=frozen12)
    tokenizer = prefix["tokenizer"]
    bindings = {index: i11._bind_block_tensors(raw, index) for index in i12.BLOCK_INDEXES}
    terminal_binding = i13._bind_terminal_tensors(raw, VOCABULARY_SIZE)
    q8_control = i13._q8_semantic_control(terminal_binding)
    if q8_control["exact"] is not True:
        raise Pass215Iteration15ValidationError("PASS215_I15_Q8_SEMANTIC_CONTROL_FAILED")
    terminal = i13._execute_terminal_head(
        prefix["dag"], prefix["blocks"][5]["output_coordinate_roots"], terminal_binding
    )
    parent_control = i14._revalidate_iteration13_semantics(prefix, terminal_binding, q8_control, terminal)
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    last_hidden = prefix["blocks"][5]["output_coordinate_roots"][-1]
    last_normalized = tuple(i7._exact_rmsnorm_dag(prefix["dag"], last_hidden, norm_weights))
    logits = i14._project_logits(
        prefix["dag"],
        last_normalized,
        terminal_binding["output_projection"],
        stage=f"terminal_output_projection:token:{PREFIX_SEQUENCE_LENGTH - 1}",
    )
    expected_vector_root = terminal["logits_stage"]["token_records"][-1]["vector_root_hash216"]
    actual_vector_root = prefix["dag"].vector(
        logits, f"terminal_output_logits:token:{PREFIX_SEQUENCE_LENGTH - 1}"
    )
    if actual_vector_root != expected_vector_root:
        raise Pass215Iteration15ValidationError("PASS215_I15_PARENT_FINAL_LOGIT_VECTOR_CHANGED")
    return {
        "prefix": prefix,
        "tokenizer": tokenizer,
        "bindings": bindings,
        "terminal_binding": terminal_binding,
        "terminal": terminal,
        "parent_control": parent_control,
        "final_position_symbolic_logits": logits,
        "final_position_vector_root_hash216": actual_vector_root,
    }


def _append_certified_greedy_token(
    raw: bytes,
    symbolic: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> Mapping[str, Any]:
    prefix = symbolic["prefix"]
    tokenizer = symbolic["tokenizer"]
    bindings = symbolic["bindings"]
    terminal_binding = symbolic["terminal_binding"]
    dag = prefix["dag"]
    cache = i14._materialize_prefix_kv_cache(dag, prefix, bindings)
    if any(len(cache[index]["k_rope"]) != PREFIX_SEQUENCE_LENGTH for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration15ValidationError("PASS215_I15_PREFIX_CACHE_GEOMETRY_INVALID")
    token_id = int(selection["selected_token_id"])
    embedding = i9._extract_authenticated_embeddings(raw, tokenizer, (token_id,))
    hidden = tuple(dag.q(numerator, denominator) for numerator, denominator in embedding["rows"][0])
    absolute_position = PREFIX_SEQUENCE_LENGTH
    block_records = []
    for block_index in i12.BLOCK_INDEXES:
        current = i14._execute_incremental_block(
            dag,
            hidden,
            bindings[block_index],
            cache[block_index],
            block_index=block_index,
            absolute_position=absolute_position,
            append_index=0,
        )
        block_records.append({key: value for key, value in current.items() if key != "output_coordinate_roots"})
        hidden = current["output_coordinate_roots"]
    terminal = i14._terminal_generated_position(
        dag,
        hidden,
        terminal_binding,
        absolute_position=absolute_position,
        append_index=0,
    )
    append_payload = {
        "absolute_position": absolute_position,
        "selected_token_id": token_id,
        "selection_root_hash216": selection["selection_root_hash216"],
        "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
        "block_forward_roots": [record["block_forward_root_hash216"] for record in block_records],
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logits_root_hash216": terminal["logits_root_hash216"],
    }
    append_root = i4base.hash216(
        "pass215-i15-certified-greedy-append-forward", i4base.canonical_bytes(append_payload)
    )
    return {
        "absolute_position": absolute_position,
        "appended_token_id": token_id,
        "appended_token": str(tokenizer["tokens"][token_id]),
        "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
        "block_records": block_records,
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logits_root_hash216": terminal["logits_root_hash216"],
        "append_forward_root_hash216": append_root,
        "prefix_recomputed": False,
        "kv_cache_reused": True,
        "prefix_hidden_rows_recomputed": sum(int(r["prefix_hidden_rows_recomputed"]) for r in block_records),
        "prior_kv_token_rows_reused": sum(int(r["prior_kv_token_rows_reused"]) for r in block_records),
        "new_kv_token_rows_materialized": sum(int(r["new_kv_token_rows_materialized"]) for r in block_records),
        "final_symbolic_dag": dag.manifest(),
    }


def build_certified_greedy_logit_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
    certification_bits: int = CERTIFICATION_BITS,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration15ValidationError("PASS215_I15_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration15ValidationError("PASS215_I15_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration15ValidationError("PASS215_I15_PROMPT_OUTSIDE_CONTRACT")
    if certification_bits != CERTIFICATION_BITS:
        raise Pass215Iteration15ValidationError("PASS215_I15_CERTIFICATION_BITS_OUTSIDE_CONTRACT")

    frozen14 = i14.build_autoregressive_continuation_evidence(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    _validate_frozen_iteration14_evidence(frozen14)

    symbolic = _symbolic_prefix_and_logits(
        raw,
        filename=filename,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
    )
    tokenizer = symbolic["tokenizer"]
    interval = _execute_certified_prefix(
        raw,
        tokenizer,
        symbolic["bindings"],
        symbolic["terminal_binding"],
        bits=certification_bits,
    )
    if interval["embedding_suite_root_hash216"] != i11.ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration15ValidationError("PASS215_I15_INTERVAL_EMBEDDING_ROOT_CHANGED")
    selection = _certify_strict_argmax(
        interval["logits"],
        symbolic_logit_roots=symbolic["final_position_symbolic_logits"],
        tokenizer=tokenizer,
        interval_suite_root_hash216=interval["interval_suite_root_hash216"],
        bits=certification_bits,
    )
    append = _append_certified_greedy_token(raw, symbolic, selection)
    if append["prefix_hidden_rows_recomputed"] != 0:
        raise Pass215Iteration15ValidationError("PASS215_I15_PREFIX_RECOMPUTED")

    source_record = {
        **dict(source),
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    }
    interval_context = interval["context"].manifest()
    proof_payload = {
        "iteration14_continuation_root_hash216": ITERATION14_CONTINUATION_ROOT_HASH216,
        "iteration13_final_position_logit_vector_root_hash216": symbolic["final_position_vector_root_hash216"],
        "interval_context_root_hash216": interval_context["manifest_root_hash216"],
        "interval_suite_root_hash216": interval["interval_suite_root_hash216"],
        "selection_root_hash216": selection["selection_root_hash216"],
        "append_forward_root_hash216": append["append_forward_root_hash216"],
        "final_symbolic_dag_root_hash216": append["final_symbolic_dag"]["ordered_node_root_hash216"],
    }
    greedy_root = i4base.hash216(
        "pass215-i15-certified-greedy-logit-forward", i4base.canonical_bytes(proof_payload)
    )
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass215_benchmark_authority_active": True,
            "no_float_canonical_authority": True,
            "certified_logit_magnitude_comparison_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            **_iteration14_bindings(),
            "iteration13_full_model_forward_root_hash216": i14.ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216,
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "contracted_text_ingress": {
            "input_text": prompt,
            "token_ids": list(FROZEN_TOKEN_IDS),
            "prefix_sequence_length": PREFIX_SEQUENCE_LENGTH,
        },
        "iteration14_semantic_reexecution": {
            "exact": True,
            **_iteration14_bindings(),
        },
        "certified_interval_executor": interval_context,
        "certified_logit_comparison": {
            "final_position_absolute_index": PREFIX_SEQUENCE_LENGTH - 1,
            "symbolic_logit_vector_root_hash216": symbolic["final_position_vector_root_hash216"],
            "complete_logit_interval_suite_root_hash216": interval["interval_suite_root_hash216"],
            "interval_leaf_count": interval["interval_leaf_count"],
            **selection,
        },
        "certified_greedy_append": append,
        "certified_greedy_forward_root_hash216": greedy_root,
        "certification_work_geometry": {
            "certification_bits": certification_bits,
            "prefix_tokens_interval_replayed": PREFIX_SEQUENCE_LENGTH,
            "transformer_blocks_interval_replayed": AUTHENTICATED_BLOCK_COUNT,
            "six_block_q4_logical_weight_products": i12._expected_linear_work_total()["logical_weight_products"],
            "terminal_q8_logical_weight_products": VOCABULARY_SIZE * EMBEDDING_WIDTH,
            "candidate_interval_comparisons": VOCABULARY_SIZE - 1,
            "greedy_append_count": PROCESSED_GREEDY_APPEND_COUNT,
        },
        "claims": {
            "authenticated_iteration14_roots_inherited_unchanged": True,
            "complete_final_position_logit_interval_vector_certified": True,
            "true_logit_magnitude_argmax_certified": True,
            "exact_greedy_token_selection_executed": True,
            "one_step_true_greedy_autoregressive_continuation_executed": True,
            "prefix_state_reused_without_recomputation": True,
            "kv_cache_reused_for_greedy_append": True,
            "hash_identity_order_used_as_greedy_authority": False,
            "probabilistic_sampling_executed": False,
            "general_generation_claimed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "numeric_transcendental_point_evaluation_performed": False,
            "approximate_transcendental_point_evaluation_performed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
    }
    suite_payload = {
        "iteration14_suite_root_hash216": ITERATION14_SUITE_ROOT_HASH216,
        "interval_suite_root_hash216": interval["interval_suite_root_hash216"],
        "selection_root_hash216": selection["selection_root_hash216"],
        "append_forward_root_hash216": append["append_forward_root_hash216"],
        "greedy_forward_root_hash216": greedy_root,
    }
    suite_root = i4base.hash216(
        "pass215-i15-certified-greedy-logit-suite", i4base.canonical_bytes(suite_payload)
    )
    evidence["certified_greedy_logit_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i15-certified-greedy-logit-evidence", i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION15_CERTIFIED_GREEDY_LOGIT"},
        {
            "sequence": 15,
            "parent_hash72": ITERATION14_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "selection_root_hash216": selection["selection_root_hash216"],
            "greedy_forward_root_hash216": greedy_root,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_certified_greedy_logit_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
    certification_bits: int = CERTIFICATION_BITS,
) -> Mapping[str, Any]:
    source_path = Path(path)
    return build_certified_greedy_logit_evidence(
        source_path.read_bytes(),
        filename=source_path.name,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
        certification_bits=certification_bits,
    )


def validate_certified_greedy_logit_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration15ValidationError("PASS215_I15_SCHEMA_OR_CONTRACT_INVALID")
    required_inherits = {
        **_iteration14_bindings(),
        "iteration13_full_model_forward_root_hash216": i14.ITERATION13_FULL_MODEL_FORWARD_ROOT_HASH216,
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if evidence.get("inherits") != required_inherits:
        raise Pass215Iteration15ValidationError("PASS215_I15_INHERITANCE_INVALID")
    comparison = evidence.get("certified_logit_comparison", {})
    if comparison.get("policy") != SELECTION_POLICY or comparison.get("semantics") != SELECTION_SEMANTICS:
        raise Pass215Iteration15ValidationError("PASS215_I15_SELECTION_POLICY_INVALID")
    if int(comparison.get("candidate_count", 0)) != VOCABULARY_SIZE:
        raise Pass215Iteration15ValidationError("PASS215_I15_CANDIDATE_COUNT_INVALID")
    if int(comparison.get("interval_leaf_count", 0)) != VOCABULARY_SIZE:
        raise Pass215Iteration15ValidationError("PASS215_I15_INTERVAL_LEAF_COUNT_INVALID")
    if comparison.get("strict_interval_separation") is not True or comparison.get("certified_true_argmax") is not True:
        raise Pass215Iteration15ValidationError("PASS215_I15_ARGMAX_CERTIFICATE_MISSING")
    margin = comparison.get("strict_margin_lower_bound", {})
    if int(margin.get("numerator", 0)) <= 0 or int(margin.get("denominator", 0)) != 1 << CERTIFICATION_BITS:
        raise Pass215Iteration15ValidationError("PASS215_I15_ARGMAX_MARGIN_INVALID")
    append = evidence.get("certified_greedy_append", {})
    if int(append.get("appended_token_id", -1)) != int(comparison.get("selected_token_id", -2)):
        raise Pass215Iteration15ValidationError("PASS215_I15_SELECTED_APPEND_TOKEN_MISMATCH")
    if append.get("prefix_recomputed") is not False or append.get("kv_cache_reused") is not True:
        raise Pass215Iteration15ValidationError("PASS215_I15_CACHE_REUSE_INVALID")
    if int(append.get("prefix_hidden_rows_recomputed", -1)) != 0:
        raise Pass215Iteration15ValidationError("PASS215_I15_PREFIX_RECOMPUTATION_INVALID")
    claims = evidence.get("claims", {})
    required_true = (
        "authenticated_iteration14_roots_inherited_unchanged",
        "complete_final_position_logit_interval_vector_certified",
        "true_logit_magnitude_argmax_certified",
        "exact_greedy_token_selection_executed",
        "one_step_true_greedy_autoregressive_continuation_executed",
        "prefix_state_reused_without_recomputation",
        "kv_cache_reused_for_greedy_append",
    )
    required_false = (
        "hash_identity_order_used_as_greedy_authority",
        "probabilistic_sampling_executed",
        "general_generation_claimed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "numeric_transcendental_point_evaluation_performed",
        "approximate_transcendental_point_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    )
    if not all(claims.get(key) is True for key in required_true):
        raise Pass215Iteration15ValidationError("PASS215_I15_REQUIRED_TRUE_CLAIM_INVALID")
    if not all(claims.get(key) is False for key in required_false):
        raise Pass215Iteration15ValidationError("PASS215_I15_REQUIRED_FALSE_CLAIM_INVALID")
    stripped = dict(evidence)
    receipt = stripped.pop("receipt_hash72", None)
    evidence_root = stripped.pop("evidence_root_hash216", None)
    expected_evidence_root = i4base.hash216(
        "pass215-i15-certified-greedy-logit-evidence", i4base.canonical_bytes(stripped)
    )
    if evidence_root != expected_evidence_root:
        raise Pass215Iteration15ValidationError("PASS215_I15_EVIDENCE_ROOT_INVALID")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION15_CERTIFIED_GREEDY_LOGIT"},
        {
            "sequence": 15,
            "parent_hash72": ITERATION14_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": evidence["certified_greedy_logit_suite_root_hash216"],
            "selection_root_hash216": comparison["selection_root_hash216"],
            "greedy_forward_root_hash216": evidence["certified_greedy_forward_root_hash216"],
        },
    )
    if receipt != expected_receipt:
        raise Pass215Iteration15ValidationError("PASS215_I15_RECEIPT_INVALID")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_certified_greedy_logit_evidence(left)
    validate_certified_greedy_logit_evidence(right)
    left_comparison = left["certified_logit_comparison"]
    right_comparison = right["certified_logit_comparison"]
    keys = (
        "certified_greedy_forward_root_hash216",
        "certified_greedy_logit_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    for key in keys:
        if left[key] != right[key]:
            raise Pass215Iteration15ValidationError(f"PASS215_I15_REPLAY_MISMATCH:{key}")
    if left_comparison["selected_token_id"] != right_comparison["selected_token_id"]:
        raise Pass215Iteration15ValidationError("PASS215_I15_REPLAY_SELECTED_TOKEN_MISMATCH")
    if left_comparison["selection_root_hash216"] != right_comparison["selection_root_hash216"]:
        raise Pass215Iteration15ValidationError("PASS215_I15_REPLAY_SELECTION_ROOT_MISMATCH")
    return {
        "schema": REPLAY_SCHEMA,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "certified_true_argmax": True,
        "selected_token_id": int(left_comparison["selected_token_id"]),
        "selected_token": str(left_comparison["selected_token"]),
        "selection_root_hash216": left_comparison["selection_root_hash216"],
        "append_forward_root_hash216": left["certified_greedy_append"]["append_forward_root_hash216"],
        "greedy_forward_root_hash216": left["certified_greedy_forward_root_hash216"],
        "suite_root_hash216": left["certified_greedy_logit_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT", "PASS_NUMBER", "ITERATION", "EVIDENCE_SCHEMA", "VALIDATION_SCHEMA", "REPLAY_SCHEMA",
    "CERTIFICATION_BITS", "SELECTION_POLICY", "SELECTION_SEMANTICS", "CertifiedDyadicContext",
    "Pass215Iteration15Error", "Pass215Iteration15ValidationError", "_interval_q4_linear",
    "_certify_strict_argmax", "build_certified_greedy_logit_evidence",
    "build_certified_greedy_logit_evidence_from_path", "validate_certified_greedy_logit_evidence", "compare_replay",
]

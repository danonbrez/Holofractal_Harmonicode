"""Pass 215 Iteration 5 exact nonlinear symbolic substrate.

This module extends the frozen Iteration 4 exact-linear benchmark with a
NO_FLOAT_CANONICAL_AUTHORITY symbolic substrate for nonlinear transformer
operators.  Algebraic operations are reduced exactly where possible; sqrt,
rational powers, trigonometric functions, and exponentials that are not
algebraically reducible remain canonical closed-form expression nodes.

This is benchmark authority only.  It does not mutate the operational runtime,
change canonical authority, numerically approximate transcendental functions,
or claim a complete transformer-layer forward.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from math import gcd, isqrt
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TypeAlias

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v4 as i4

CONTRACT = "HHS-P215-I5-EXACT-NONLINEAR-SYMBOLIC-SUBSTRATE"
PASS_NUMBER = 215
ITERATION = 5
CONTRACT_VERSION = "1.0.0-iteration5"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_5_EXACT_NONLINEAR_SYMBOLIC_BENCHMARK"
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_5_NONLINEAR_SYMBOLIC_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_5_NONLINEAR_SYMBOLIC_VALIDATION_V1"

ITERATION4_VALIDATED_HEAD = "ce35117dd1b54574f2fc98e0254dee0ddcf0e518"
ITERATION4_VALIDATED_TREE = "a1fb44e5c43e4d504a71183ba6eb01405d730293"
ITERATION4_SUITE_OUTPUT_ROOT_HASH216 = "14de39b3b326eb64bbac5d8be829c289c4a5e1f39b842bfdba59b46fea2c9acb"
ITERATION4_TERMINAL_EVIDENCE_HASH216 = "0462738157042bbd2903ed666a3e05dbc1e27c8a43ea5d2544de9b0c174f87bf"
ITERATION4_RECEIPT_HASH72 = "2SrZvFdR/*41!b++dH9qxM1IrUZMuwuRZmpNw4yl8>QYI(LA9B65A<auqlwyWoi97onfMeMc"
ITERATION4_ARTIFACT_SHA256 = "6ab0e11d7a312ff0ac99268fda906c6d3d5d367d20a20e1f800238aa5de80c5e"
REAL_MODEL_SHA256 = i4.REAL_MODEL_SHA256
TARGET_SEED_OPERATOR = "blk.0.attn_q.weight"
TARGET_SEED_SHAPE = i4.TARGET_OPERATORS[TARGET_SEED_OPERATOR]

# Iteration-5 witnesses are deliberately contracted independently from runtime
# metadata until a later iteration composes the complete transformer layer.
RMSNORM_EPSILON = (1, 100_000)
ROPE_WITNESS_DIMENSION = 48
ROPE_WITNESS_POSITION = 7
ROPE_THETA = (10_000, 1)
ATTENTION_WITNESS_HEAD_DIMENSION = 48
ATTENTION_WITNESS_SCORE_COUNT = 4
SILU_WITNESS_COUNT = 8

Expr: TypeAlias = tuple[Any, ...]

ALLOWED_OPS = frozenset({"q", "add", "mul", "inv", "sqrt", "rsqrt", "powq", "exp", "sin", "cos"})


class Pass215Iteration5Error(RuntimeError):
    pass


class Pass215Iteration5ValidationError(Pass215Iteration5Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration5ValidationError(f"PASS215_I5_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _normal_rational(numerator: int, denominator: int) -> tuple[int, int]:
    if isinstance(numerator, bool) or isinstance(denominator, bool) or not isinstance(numerator, int) or not isinstance(denominator, int):
        raise Pass215Iteration5ValidationError("PASS215_I5_NONINTEGER_RATIONAL_COMPONENT")
    if denominator == 0:
        raise Pass215Iteration5ValidationError("PASS215_I5_RATIONAL_ZERO_DENOMINATOR")
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    if numerator == 0:
        return (0, 1)
    divisor = gcd(abs(numerator), denominator)
    return (numerator // divisor, denominator // divisor)


def q(numerator: int, denominator: int = 1) -> Expr:
    n, d = _normal_rational(numerator, denominator)
    return ("q", n, d)


def is_q(value: Expr) -> bool:
    return isinstance(value, tuple) and len(value) == 3 and value[0] == "q"


def q_pair(value: Expr) -> tuple[int, int]:
    if not is_q(value):
        raise Pass215Iteration5ValidationError("PASS215_I5_EXPECTED_RATIONAL")
    if isinstance(value[1], bool) or isinstance(value[2], bool) or not isinstance(value[1], int) or not isinstance(value[2], int):
        raise Pass215Iteration5ValidationError("PASS215_I5_NONINTEGER_RATIONAL_COMPONENT")
    return (value[1], value[2])


def _expr_key(value: Expr) -> bytes:
    return i4base.canonical_bytes(expr_to_json(value))


def _coerce(value: Expr | tuple[int, int] | int) -> Expr:
    if isinstance(value, int):
        return q(value)
    if isinstance(value, tuple) and value and isinstance(value[0], str):
        validate_expr(value)
        return value
    if isinstance(value, tuple) and len(value) == 2 and all(isinstance(item, int) for item in value):
        return q(value[0], value[1])
    raise Pass215Iteration5ValidationError("PASS215_I5_EXPRESSION_COERCION_FAILED")


def add(*values: Expr | tuple[int, int] | int) -> Expr:
    flat: list[Expr] = []
    rational_numerator = 0
    rational_denominator = 1
    for raw in values:
        value = _coerce(raw)
        children = value[1:] if value[0] == "add" else (value,)
        for child in children:
            if is_q(child):
                n, d = q_pair(child)
                common = gcd(rational_denominator, d)
                rational_numerator = rational_numerator * (d // common) + n * (rational_denominator // common)
                rational_denominator = rational_denominator * (d // common)
                rational_numerator, rational_denominator = _normal_rational(rational_numerator, rational_denominator)
            else:
                flat.append(child)
    if rational_numerator:
        flat.append(q(rational_numerator, rational_denominator))
    if not flat:
        return q(0)
    flat.sort(key=_expr_key)
    if len(flat) == 1:
        return flat[0]
    return ("add", *flat)


def mul(*values: Expr | tuple[int, int] | int) -> Expr:
    flat: list[Expr] = []
    rational_numerator = 1
    rational_denominator = 1
    for raw in values:
        value = _coerce(raw)
        children = value[1:] if value[0] == "mul" else (value,)
        for child in children:
            if is_q(child):
                n, d = q_pair(child)
                if n == 0:
                    return q(0)
                rational_numerator *= n
                rational_denominator *= d
                rational_numerator, rational_denominator = _normal_rational(rational_numerator, rational_denominator)
            else:
                flat.append(child)
    rational = q(rational_numerator, rational_denominator)
    if rational != q(1):
        flat.append(rational)
    if not flat:
        return q(1)
    flat.sort(key=_expr_key)
    if len(flat) == 1:
        return flat[0]
    return ("mul", *flat)


def neg(value: Expr | tuple[int, int] | int) -> Expr:
    return mul(q(-1), value)


def sub(left: Expr | tuple[int, int] | int, right: Expr | tuple[int, int] | int) -> Expr:
    left_expr = _coerce(left)
    right_expr = _coerce(right)
    if left_expr == right_expr:
        return q(0)
    if is_q(left_expr) and is_q(right_expr):
        ln, ld = q_pair(left_expr)
        rn, rd = q_pair(right_expr)
        return q(ln * rd - rn * ld, ld * rd)
    return add(left_expr, neg(right_expr))


def inv(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if is_q(expr):
        n, d = q_pair(expr)
        if n == 0:
            raise Pass215Iteration5ValidationError("PASS215_I5_DIVISION_BY_ZERO")
        return q(d, n)
    if expr[0] == "inv":
        return expr[1]
    return ("inv", expr)


def div(left: Expr | tuple[int, int] | int, right: Expr | tuple[int, int] | int) -> Expr:
    return mul(left, inv(right))


def square(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if is_q(expr):
        n, d = q_pair(expr)
        return q(n * n, d * d)
    if expr[0] == "sqrt":
        return expr[1]
    if expr[0] == "rsqrt":
        return inv(expr[1])
    return mul(expr, expr)


def sqrt_expr(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if is_q(expr):
        n, d = q_pair(expr)
        if n < 0:
            raise Pass215Iteration5ValidationError("PASS215_I5_SQRT_NEGATIVE")
        ns = isqrt(n)
        ds = isqrt(d)
        if ns * ns == n and ds * ds == d:
            return q(ns, ds)
    if expr == q(0) or expr == q(1):
        return expr
    return ("sqrt", expr)


def rsqrt_expr(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if is_q(expr):
        n, _d = q_pair(expr)
        if n <= 0:
            raise Pass215Iteration5ValidationError("PASS215_I5_RSQRT_NONPOSITIVE")
    root = sqrt_expr(expr)
    if is_q(root):
        return inv(root)
    return ("rsqrt", expr)


def pow_rational(base: Expr | tuple[int, int] | int, exponent: Expr | tuple[int, int] | int) -> Expr:
    base_expr = _coerce(base)
    exponent_expr = _coerce(exponent)
    if not is_q(exponent_expr):
        raise Pass215Iteration5ValidationError("PASS215_I5_POW_EXPONENT_NOT_RATIONAL")
    en, ed = q_pair(exponent_expr)
    if en == 0:
        return q(1)
    if en == ed:
        return base_expr
    if is_q(base_expr):
        bn, bd = q_pair(base_expr)
        if bn <= 0:
            raise Pass215Iteration5ValidationError("PASS215_I5_POW_BASE_NONPOSITIVE")
        if ed == 1:
            if en > 0:
                return q(pow(bn, en), pow(bd, en))
            return q(pow(bd, -en), pow(bn, -en))
        bn_root = isqrt(bn) if ed == 2 else None
        bd_root = isqrt(bd) if ed == 2 else None
        if ed == 2 and bn_root is not None and bd_root is not None and bn_root * bn_root == bn and bd_root * bd_root == bd:
            return pow_rational(q(bn_root, bd_root), q(en, 1))
    return ("powq", base_expr, exponent_expr)


def exp_expr(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if expr == q(0):
        return q(1)
    return ("exp", expr)


def sin_expr(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if expr == q(0):
        return q(0)
    return ("sin", expr)


def cos_expr(value: Expr | tuple[int, int] | int) -> Expr:
    expr = _coerce(value)
    if expr == q(0):
        return q(1)
    return ("cos", expr)


def expr_to_json(value: Expr) -> Mapping[str, Any]:
    if not isinstance(value, tuple) or not value or not isinstance(value[0], str):
        raise Pass215Iteration5ValidationError("PASS215_I5_EXPRESSION_INVALID")
    op = value[0]
    if op == "q":
        if len(value) != 3:
            raise Pass215Iteration5ValidationError("PASS215_I5_RATIONAL_ARITY_INVALID")
        n, d = q_pair(value)
        return {"op": "q", "numerator": n, "denominator": d}
    if op in {"inv", "sqrt", "rsqrt", "exp", "sin", "cos"}:
        if len(value) != 2:
            raise Pass215Iteration5ValidationError(f"PASS215_I5_UNARY_ARITY_INVALID:{op}")
        return {"op": op, "arg": expr_to_json(value[1])}
    if op == "powq":
        if len(value) != 3:
            raise Pass215Iteration5ValidationError("PASS215_I5_POWQ_ARITY_INVALID")
        return {"op": op, "base": expr_to_json(value[1]), "exponent": expr_to_json(value[2])}
    if op in {"add", "mul"}:
        if len(value) < 3:
            raise Pass215Iteration5ValidationError(f"PASS215_I5_NARY_ARITY_INVALID:{op}")
        return {"op": op, "args": [expr_to_json(child) for child in value[1:]]}
    raise Pass215Iteration5ValidationError(f"PASS215_I5_EXPRESSION_OP_INVALID:{op}")


def validate_expr(value: Expr) -> None:
    encoded = expr_to_json(value)
    _reject_floats(encoded)
    if value[0] not in ALLOWED_OPS:
        raise Pass215Iteration5ValidationError("PASS215_I5_EXPRESSION_OP_NOT_ALLOWED")
    if is_q(value):
        n, d = q_pair(value)
        if d <= 0 or _normal_rational(n, d) != (n, d):
            raise Pass215Iteration5ValidationError("PASS215_I5_RATIONAL_NOT_CANONICAL")
        return
    if value[0] in {"add", "mul"}:
        children = value[1:]
    elif value[0] == "powq":
        children = value[1:3]
    else:
        children = value[1:2]
    for child in children:
        validate_expr(child)


def expr_root(domain: str, values: Sequence[Expr] | Expr) -> str:
    if isinstance(values, tuple) and values and isinstance(values[0], str):
        payload: Any = expr_to_json(values)
    else:
        payload = [expr_to_json(value) for value in values]  # type: ignore[arg-type]
    return i4base.hash216(domain, i4base.canonical_bytes(payload))


def _walk(value: Expr, seen: set[Expr], counter: Counter[str]) -> None:
    if value in seen:
        return
    seen.add(value)
    counter[value[0]] += 1
    if value[0] in {"add", "mul"}:
        children = value[1:]
    elif value[0] == "powq":
        children = value[1:3]
    elif value[0] == "q":
        children = ()
    else:
        children = value[1:2]
    for child in children:
        _walk(child, seen, counter)


def expression_complexity(values: Sequence[Expr]) -> Mapping[str, Any]:
    seen: set[Expr] = set()
    counter: Counter[str] = Counter()
    for value in values:
        validate_expr(value)
        _walk(value, seen, counter)
    return {
        "unique_expression_nodes": len(seen),
        "operator_histogram": {op: int(counter.get(op, 0)) for op in sorted(ALLOWED_OPS)},
        "output_coordinates": len(values),
    }


def exact_rmsnorm(
    values: Sequence[Expr | tuple[int, int] | int],
    *,
    epsilon: Expr | tuple[int, int] | int = RMSNORM_EPSILON,
    weights: Sequence[Expr | tuple[int, int] | int] | None = None,
) -> tuple[tuple[Expr, ...], Mapping[str, Any]]:
    if not values:
        raise Pass215Iteration5ValidationError("PASS215_I5_RMSNORM_EMPTY")
    xs = tuple(_coerce(value) for value in values)
    if weights is not None and len(weights) != len(xs):
        raise Pass215Iteration5ValidationError("PASS215_I5_RMSNORM_WEIGHT_GEOMETRY")
    mean_square = div(add(*(square(value) for value in xs)), q(len(xs)))
    radicand = add(mean_square, epsilon)
    normalization = rsqrt_expr(radicand)
    if weights is None:
        output = tuple(mul(value, normalization) for value in xs)
    else:
        output = tuple(mul(value, normalization, weight) for value, weight in zip(xs, weights))
    return output, {
        "mean_square": expr_to_json(mean_square),
        "radicand": expr_to_json(radicand),
        "normalization": expr_to_json(normalization),
        "epsilon": expr_to_json(_coerce(epsilon)),
        "width": len(xs),
        "weighted": weights is not None,
        "semantic_form": "x_i*weight_i*(mean(x^2)+epsilon)^(-1/2)",
    }


def exact_rope(
    values: Sequence[Expr | tuple[int, int] | int],
    *,
    position: int,
    rotary_dimension: int,
    theta: Expr | tuple[int, int] | int = ROPE_THETA,
) -> tuple[tuple[Expr, ...], Mapping[str, Any]]:
    if rotary_dimension <= 0 or rotary_dimension % 2:
        raise Pass215Iteration5ValidationError("PASS215_I5_ROPE_DIMENSION_INVALID")
    if len(values) != rotary_dimension:
        raise Pass215Iteration5ValidationError("PASS215_I5_ROPE_INPUT_GEOMETRY")
    if position < 0:
        raise Pass215Iteration5ValidationError("PASS215_I5_ROPE_POSITION_INVALID")
    xs = tuple(_coerce(value) for value in values)
    output: list[Expr] = []
    angle_roots: list[str] = []
    for pair_index in range(rotary_dimension // 2):
        exponent = q(-2 * pair_index, rotary_dimension)
        frequency = pow_rational(theta, exponent)
        angle = mul(q(position), frequency)
        c = cos_expr(angle)
        s = sin_expr(angle)
        left = xs[2 * pair_index]
        right = xs[2 * pair_index + 1]
        output.append(sub(mul(left, c), mul(right, s)))
        output.append(add(mul(left, s), mul(right, c)))
        angle_roots.append(expr_root("pass215-i5-rope-angle", angle))
    return tuple(output), {
        "position": int(position),
        "rotary_dimension": int(rotary_dimension),
        "theta": expr_to_json(_coerce(theta)),
        "frequency_rule": "theta^(-2*pair_index/rotary_dimension)",
        "angle_root_hash216": i4base.hash216("pass215-i5-rope-angle-suite", i4base.canonical_bytes(angle_roots)),
    }


def exact_attention_scale(
    scores: Sequence[Expr | tuple[int, int] | int], *, head_dimension: int
) -> tuple[tuple[Expr, ...], Mapping[str, Any]]:
    if head_dimension <= 0:
        raise Pass215Iteration5ValidationError("PASS215_I5_ATTENTION_HEAD_DIMENSION_INVALID")
    scale = rsqrt_expr(q(head_dimension))
    output = tuple(mul(score, scale) for score in scores)
    return output, {
        "head_dimension": int(head_dimension),
        "scale": expr_to_json(scale),
        "semantic_form": "score/sqrt(head_dimension)",
    }


def exact_softmax(scores: Sequence[Expr | tuple[int, int] | int]) -> tuple[tuple[Expr, ...], Mapping[str, Any]]:
    if not scores:
        raise Pass215Iteration5ValidationError("PASS215_I5_SOFTMAX_EMPTY")
    xs = tuple(_coerce(score) for score in scores)
    anchor = xs[0]
    shifted = tuple(sub(score, anchor) for score in xs)
    numerators = tuple(exp_expr(value) for value in shifted)
    denominator = add(*numerators)
    output = tuple(div(value, denominator) for value in numerators)
    return output, {
        "anchor": expr_to_json(anchor),
        "shifted_score_root_hash216": expr_root("pass215-i5-softmax-shifted", shifted),
        "denominator": expr_to_json(denominator),
        "normalization": "FIRST_SCORE_EXACT_SHIFT_THEN_EXP_RATIO",
        "numeric_exponential_approximation_performed": False,
    }


def exact_sigmoid(value: Expr | tuple[int, int] | int) -> Expr:
    x = _coerce(value)
    return inv(add(q(1), exp_expr(neg(x))))


def exact_silu(value: Expr | tuple[int, int] | int) -> Expr:
    x = _coerce(value)
    return mul(x, exact_sigmoid(x))


def _source_sha256(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _rational_exprs(values: Sequence[tuple[int, int]]) -> tuple[Expr, ...]:
    return tuple(q(int(n), int(d)) for n, d in values)


def _model_seed(raw: bytes) -> tuple[tuple[Expr, ...], Mapping[str, Any]]:
    parsed = i4base.parse_gguf(raw)
    by_name = {tensor.name: tensor for tensor in parsed.tensors}
    if TARGET_SEED_OPERATOR not in by_name:
        raise Pass215Iteration5ValidationError("PASS215_I5_SEED_OPERATOR_MISSING")
    tensor = by_name[TARGET_SEED_OPERATOR]
    payload = raw[tensor.data_offset : tensor.data_offset + tensor.data_size]
    compiled, descriptor = i4.compile_q4_tensor(tensor, payload, TARGET_SEED_SHAPE)
    input_vector = i4.deterministic_vector(compiled.ne0)
    output, work = i4.execute_factored(compiled, input_vector, descriptors_are_reused=True)
    output_root = i4.output_root(compiled.name, input_vector, output)
    return _rational_exprs(output), {
        "operator": TARGET_SEED_OPERATOR,
        "shape": list(TARGET_SEED_SHAPE),
        "descriptor_root_hash216": compiled.descriptor_root_hash216,
        "linear_output_root_hash216": output_root,
        "linear_output_width": len(output),
        "input_root_hash216": i4base.hash216("pass215-i5-linear-seed-input", i4base.canonical_bytes(list(input_vector))),
        "factored_work": work,
        "descriptor": descriptor,
        "container_architecture": parsed.architecture,
    }


def _controls() -> Mapping[str, Any]:
    rms_output, _ = exact_rmsnorm((q(3), q(3)), epsilon=q(0))
    rope_input = (q(1), q(2), q(3), q(4))
    rope_output, _ = exact_rope(rope_input, position=0, rotary_dimension=4)
    scaled, _ = exact_attention_scale((q(4), q(-8)), head_dimension=16)
    equal_softmax, _ = exact_softmax((q(5), q(5), q(5), q(5)))
    return {
        "rmsnorm_perfect_square": {
            "output": [expr_to_json(value) for value in rms_output],
            "expected": [expr_to_json(q(1)), expr_to_json(q(1))],
            "exact": rms_output == (q(1), q(1)),
        },
        "rope_position_zero_identity": {
            "exact": rope_output == rope_input,
            "output_root_hash216": expr_root("pass215-i5-rope-zero-control", rope_output),
        },
        "attention_scale_perfect_square": {
            "exact": scaled == (q(1), q(-2)),
            "output": [expr_to_json(value) for value in scaled],
        },
        "softmax_equal_scores": {
            "exact": equal_softmax == (q(1, 4),) * 4,
            "output": [expr_to_json(value) for value in equal_softmax],
        },
        "sigmoid_zero": {
            "exact": exact_sigmoid(q(0)) == q(1, 2),
            "output": expr_to_json(exact_sigmoid(q(0))),
        },
        "silu_zero": {
            "exact": exact_silu(q(0)) == q(0),
            "output": expr_to_json(exact_silu(q(0))),
        },
    }


def build_nonlinear_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = _source_sha256(raw)
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration5ValidationError("PASS215_I5_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration5ValidationError("PASS215_I5_AUTHENTICATED_REAL_MODEL_IDENTITY_MISMATCH")

    seed, seed_record = _model_seed(raw)
    rms_output, rms_record = exact_rmsnorm(seed, epsilon=RMSNORM_EPSILON)
    rope_seed = rms_output[:ROPE_WITNESS_DIMENSION]
    rope_output, rope_record = exact_rope(
        rope_seed,
        position=ROPE_WITNESS_POSITION,
        rotary_dimension=ROPE_WITNESS_DIMENSION,
        theta=ROPE_THETA,
    )
    attention_scores = seed[:ATTENTION_WITNESS_SCORE_COUNT]
    scaled_scores, attention_record = exact_attention_scale(
        attention_scores, head_dimension=ATTENTION_WITNESS_HEAD_DIMENSION
    )
    softmax_output, softmax_record = exact_softmax(scaled_scores)
    silu_output = tuple(exact_silu(value) for value in seed[:SILU_WITNESS_COUNT])
    sigmoid_output = tuple(exact_sigmoid(value) for value in seed[:SILU_WITNESS_COUNT])

    roots = {
        "rmsnorm_root_hash216": expr_root("pass215-i5-rmsnorm-output", rms_output),
        "rope_root_hash216": expr_root("pass215-i5-rope-output", rope_output),
        "attention_scaled_score_root_hash216": expr_root("pass215-i5-attention-scale-output", scaled_scores),
        "softmax_root_hash216": expr_root("pass215-i5-softmax-output", softmax_output),
        "sigmoid_root_hash216": expr_root("pass215-i5-sigmoid-output", sigmoid_output),
        "silu_root_hash216": expr_root("pass215-i5-silu-output", silu_output),
    }
    complexity = {
        "rmsnorm": expression_complexity(rms_output),
        "rope": expression_complexity(rope_output),
        "attention_scale": expression_complexity(scaled_scores),
        "softmax": expression_complexity(softmax_output),
        "sigmoid": expression_complexity(sigmoid_output),
        "silu": expression_complexity(silu_output),
    }
    controls = _controls()
    if not all(bool(record["exact"]) for record in controls.values()):
        raise Pass215Iteration5ValidationError("PASS215_I5_EXACT_CONTROL_FAILED")

    source_record = dict(source)
    source_record.update({
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    })
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "contract": CONTRACT,
        "pass": PASS_NUMBER,
        "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass215_benchmark_authority_active": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
            "no_float_canonical_authority": True,
        },
        "inherits": {
            "iteration4_validated_head": ITERATION4_VALIDATED_HEAD,
            "iteration4_validated_tree": ITERATION4_VALIDATED_TREE,
            "iteration4_suite_output_root_hash216": ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
            "iteration4_terminal_evidence_hash216": ITERATION4_TERMINAL_EVIDENCE_HASH216,
            "iteration4_receipt_hash72": ITERATION4_RECEIPT_HASH72,
            "iteration4_artifact_sha256": ITERATION4_ARTIFACT_SHA256,
            "iteration3_evidence_root_hash216": i4base.ITERATION3_EVIDENCE_ROOT_HASH216,
            "iteration2_evidence_root_hash216": i4base.ITERATION2_EVIDENCE_ROOT_HASH216,
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "linear_seed": seed_record,
        "nonlinear_symbolic_substrate": {
            "rmsnorm": {**rms_record, "output_root_hash216": roots["rmsnorm_root_hash216"]},
            "rope": {**rope_record, "output_root_hash216": roots["rope_root_hash216"]},
            "attention_scale": {**attention_record, "output_root_hash216": roots["attention_scaled_score_root_hash216"]},
            "softmax": {**softmax_record, "output_root_hash216": roots["softmax_root_hash216"]},
            "sigmoid": {"output_root_hash216": roots["sigmoid_root_hash216"], "witness_count": len(sigmoid_output)},
            "silu": {"output_root_hash216": roots["silu_root_hash216"], "witness_count": len(silu_output)},
        },
        "generator_transition_complexity": complexity,
        "exact_controls": controls,
        "claims": {
            "exact_rmsnorm_closed_form_symbolic_execution": True,
            "exact_rope_closed_form_symbolic_execution": True,
            "exact_attention_scaling_closed_form_symbolic_execution": True,
            "exact_exponential_softmax_closed_form_symbolic_execution": True,
            "exact_sigmoid_silu_closed_form_symbolic_execution": True,
            "numeric_transcendental_evaluation_performed": False,
            "approximate_transcendental_evaluation_performed": False,
            "full_transformer_layer_forward_executed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_performed": False,
            "canonical_mutation_performed": False,
        },
    }
    suite_root = i4base.hash216("pass215-i5-nonlinear-symbolic-suite", i4base.canonical_bytes(roots))
    evidence["nonlinear_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216("pass215-i5-nonlinear-symbolic-evidence", i4base.canonical_bytes(evidence))
    receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION5_EXACT_NONLINEAR_SYMBOLIC"},
        {
            "sequence": 5,
            "parent_hash72": ITERATION4_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "nonlinear_suite_root_hash216": suite_root,
        },
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = receipt
    _reject_floats(evidence)
    return evidence


def build_nonlinear_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    expected_sha256: str | None = None,
) -> Mapping[str, Any]:
    target = Path(path)
    return build_nonlinear_evidence(
        target.read_bytes(),
        filename=target.name,
        source=source,
        expected_sha256=expected_sha256,
    )


def validate_nonlinear_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration5ValidationError("PASS215_I5_EVIDENCE_IDENTITY_INVALID")
    authority = evidence.get("authority")
    if not isinstance(authority, Mapping):
        raise Pass215Iteration5ValidationError("PASS215_I5_AUTHORITY_MISSING")
    if authority.get("runtime_mutation_authority_promoted") is not False or authority.get("canonical_mutation_authorized") is not False or authority.get("migration_active") is not False:
        raise Pass215Iteration5ValidationError("PASS215_I5_FORBIDDEN_AUTHORITY_ESCALATION")
    inherited = evidence.get("inherits")
    required_inherited = {
        "iteration4_validated_head": ITERATION4_VALIDATED_HEAD,
        "iteration4_validated_tree": ITERATION4_VALIDATED_TREE,
        "iteration4_suite_output_root_hash216": ITERATION4_SUITE_OUTPUT_ROOT_HASH216,
        "iteration4_terminal_evidence_hash216": ITERATION4_TERMINAL_EVIDENCE_HASH216,
        "iteration4_receipt_hash72": ITERATION4_RECEIPT_HASH72,
        "iteration4_artifact_sha256": ITERATION4_ARTIFACT_SHA256,
        "iteration3_evidence_root_hash216": i4base.ITERATION3_EVIDENCE_ROOT_HASH216,
        "iteration2_evidence_root_hash216": i4base.ITERATION2_EVIDENCE_ROOT_HASH216,
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if inherited != required_inherited:
        raise Pass215Iteration5ValidationError("PASS215_I5_INHERITED_ROOT_BINDING_INVALID")
    claims = evidence.get("claims")
    if not isinstance(claims, Mapping):
        raise Pass215Iteration5ValidationError("PASS215_I5_CLAIMS_MISSING")
    for key in (
        "exact_rmsnorm_closed_form_symbolic_execution",
        "exact_rope_closed_form_symbolic_execution",
        "exact_attention_scaling_closed_form_symbolic_execution",
        "exact_exponential_softmax_closed_form_symbolic_execution",
        "exact_sigmoid_silu_closed_form_symbolic_execution",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration5ValidationError(f"PASS215_I5_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "numeric_transcendental_evaluation_performed",
        "approximate_transcendental_evaluation_performed",
        "full_transformer_layer_forward_executed",
        "dense_forward_replaced",
        "runtime_mutation_performed",
        "canonical_mutation_performed",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration5ValidationError(f"PASS215_I5_BOUNDARY_CLAIM_INVALID:{key}")
    controls = evidence.get("exact_controls")
    if not isinstance(controls, Mapping) or set(controls) != set(_controls()):
        raise Pass215Iteration5ValidationError("PASS215_I5_CONTROL_SET_INVALID")
    if not all(isinstance(record, Mapping) and record.get("exact") is True for record in controls.values()):
        raise Pass215Iteration5ValidationError("PASS215_I5_CONTROL_NOT_EXACT")
    evidence_without_root = dict(evidence)
    recorded_root = evidence_without_root.pop("evidence_root_hash216", None)
    recorded_receipt = evidence_without_root.pop("receipt_hash72", None)
    expected_root = i4base.hash216("pass215-i5-nonlinear-symbolic-evidence", i4base.canonical_bytes(evidence_without_root))
    if recorded_root != expected_root:
        raise Pass215Iteration5ValidationError("PASS215_I5_EVIDENCE_ROOT_MISMATCH")
    expected_receipt = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION5_EXACT_NONLINEAR_SYMBOLIC"},
        {
            "sequence": 5,
            "parent_hash72": ITERATION4_RECEIPT_HASH72,
            "evidence_root_hash216": expected_root,
            "nonlinear_suite_root_hash216": evidence["nonlinear_suite_root_hash216"],
        },
    )
    if recorded_receipt != expected_receipt:
        raise Pass215Iteration5ValidationError("PASS215_I5_RECEIPT_MISMATCH")


def compare_replay(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_nonlinear_evidence(left)
    validate_nonlinear_evidence(right)
    keys = (
        "nonlinear_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    if any(left.get(key) != right.get(key) for key in keys):
        raise Pass215Iteration5ValidationError("PASS215_I5_CROSS_PROCESS_REPLAY_MISMATCH")
    return {
        "schema": "HHS_PASS_215_ITERATION_5_NONLINEAR_SYMBOLIC_REPLAY_VALIDATION_V1",
        "semantic_exactness": True,
        "cross_process_replay": True,
        "nonlinear_suite_root_hash216": left["nonlinear_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }


__all__ = [
    "CONTRACT",
    "PASS_NUMBER",
    "ITERATION",
    "EVIDENCE_SCHEMA",
    "VALIDATION_SCHEMA",
    "ITERATION4_VALIDATED_HEAD",
    "ITERATION4_VALIDATED_TREE",
    "ITERATION4_SUITE_OUTPUT_ROOT_HASH216",
    "ITERATION4_TERMINAL_EVIDENCE_HASH216",
    "ITERATION4_RECEIPT_HASH72",
    "REAL_MODEL_SHA256",
    "Expr",
    "Pass215Iteration5Error",
    "Pass215Iteration5ValidationError",
    "q",
    "add",
    "mul",
    "sub",
    "div",
    "inv",
    "square",
    "sqrt_expr",
    "rsqrt_expr",
    "pow_rational",
    "exp_expr",
    "sin_expr",
    "cos_expr",
    "expr_to_json",
    "validate_expr",
    "expr_root",
    "expression_complexity",
    "exact_rmsnorm",
    "exact_rope",
    "exact_attention_scale",
    "exact_softmax",
    "exact_sigmoid",
    "exact_silu",
    "build_nonlinear_evidence",
    "build_nonlinear_evidence_from_path",
    "validate_nonlinear_evidence",
    "compare_replay",
]

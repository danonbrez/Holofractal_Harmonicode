"""Pass 215 Iteration 17 scalable RoPE certified greedy continuation.

Iteration 16 proved three consecutive true-greedy append transitions with a
certified dyadic interval executor, but its direct Taylor sine/cosine contract
was explicitly bounded to |argument| <= 8. Iteration 17 removes that fixed RoPE
argument ceiling without introducing floating point or a pi approximation.

For RoPE angles outside the frozen Iteration-16 direct domain, the authoritative
executor repeatedly halves the dyadic angle until |x| <= 1/8, evaluates sine
and cosine with the inherited rational Taylor/Lagrange enclosure, and then
reconstructs the original angle with the exact double-angle identities

    sin(2x) = 2 sin(x) cos(x)
    cos(2x) = cos(x)^2 - sin(x)^2.

Every arithmetic operation is outward-rounded integer dyadic interval work.
The first three greedy steps remain bit-for-bit compatible with the frozen
Iteration-16 witness. The contracted workload then continues for seven total
true-greedy steps so that at least one authoritative argmax is certified from a
state whose RoPE execution actually used the scalable range-reduction path.

This is still a bounded benchmark witness. It does not authorize unbounded
sequence generation, probabilistic sampling, canonical float interpretation,
dense-forward replacement, runtime mutation, canonical mutation, or migration.
"""
from __future__ import annotations

from hashlib import sha256
from math import factorial
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11
from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12
from hhs_backend.runtime import hhs_pass215_iteration14_autoregressive_continuation_v1 as i14
from hhs_backend.runtime import hhs_pass215_iteration15_certified_greedy_logit_v1 as i15
from hhs_backend.runtime import hhs_pass215_iteration16_multistep_certified_greedy_v1 as i16

CONTRACT = "HHS-P215-I17-SCALABLE-ROPE-CERTIFIED-GREEDY-CONTINUATION"
PASS_NUMBER = 215
ITERATION = 17
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_17_SCALABLE_ROPE_CERTIFIED_GREEDY_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_17_SCALABLE_ROPE_CERTIFIED_GREEDY_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_17_SCALABLE_ROPE_CERTIFIED_GREEDY_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_17_SCALABLE_ROPE_CERTIFIED_GREEDY_BENCHMARK"

ITERATION16_CLOSURE_HEAD = "9eadb5ebbbad2283b3f19ccb7d2071a1a945e8c7"
ITERATION16_CLOSURE_TREE = "2c52b754b62931db1aa50926e8a35dae6ae0b4ac"
ITERATION16_GENERATED_TOKEN_IDS = (450, 6575, 471)
ITERATION16_GENERATED_TOKENS = ("▁The", "▁sun", "▁was")
ITERATION16_SELECTION_ROOTS = (
    "aac3225975c44b9b761dd131afedfc01123a3c5da187f76bd9de5c9bf2abee94",
    "ba04d7c30b6734f7229d13e0684d7d9458803f4a5387c9c5547ef4f2d4e23050",
    "4043e960f6454b4ad0849b3997ddbbe8a5df5e92f827e8d70fcf424999bf7cba",
)
ITERATION16_APPEND_ROOTS = (
    "c76459385ed0d81c63e37784c6e2094d81322984fae400c9198ddc8a8ae23fcf",
    "6860a9e610242e40f5663f6504cc38fbfa8fea4e204f5769cc21d2a639475b10",
    "0a0d6ba7a9745807e1b31c86d27cc194886d4e7626db4977bdc0c0dd46773668",
)
ITERATION16_TRANSITION_ROOTS = (
    "ed206f708fbcfde331f743c74447f758453836073d7fed5048bb53caf683dc36",
    "ef520f4059b141fe9cb2be28a14a3fcdda9bf627e2adf4b77a910a827f108487",
    "9adc01a187186944eb106c364591862dbd528004a2c5103b06860d1ab01a7a21",
)
ITERATION16_CHAIN_ROOT_HASH216 = "28d8741be087bcb0ca6016ea7d88a24522408d965b9ee3198185dd93497f7448"
ITERATION16_FINAL_INTERVAL_SUITE_ROOT_HASH216 = "78fe60fdbe4f5d09dfb0c1f39d2478717e08d3a3d5da0cfb50c071235dc13878"
ITERATION16_FINAL_SYMBOLIC_DAG_ROOT_HASH216 = "6591757219694e1f375fa8e115f1e4d87496e93ec12d95e7745dd15033b9ac68"
ITERATION16_SUITE_ROOT_HASH216 = "13fe78e5ed5c03d3170dfb5345cf8b373ccb7b0cd98f5188c2a9532710207322"
ITERATION16_EVIDENCE_ROOT_HASH216 = "8222ea90cb157ccc98049512b7b1a6cdd42bb125e5b90db93bcb614b9f9663fb"
ITERATION16_RECEIPT_HASH72 = "pkaOYx48D?hAMtg*!bJ1(qSq-zdV/SP2LkOKB7RlZpj2CpIc06vv)6xC28H<FurVOKmP+ZSB"
ITERATION16_CLOSURE_ARTIFACT_ID = 9026948113
ITERATION16_CLOSURE_ARTIFACT_SHA256 = "2ef8d1061beb2cd48719973fefea881e2e64ff304ac3ed09db06d701659524ea"

REAL_MODEL_SHA256 = i16.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i16.CONTRACTED_PROMPT
FROZEN_TOKEN_IDS = i16.FROZEN_TOKEN_IDS
PREFIX_SEQUENCE_LENGTH = i16.PREFIX_SEQUENCE_LENGTH
EMBEDDING_WIDTH = i16.EMBEDDING_WIDTH
VOCABULARY_SIZE = i16.VOCABULARY_SIZE
CERTIFICATION_BITS = i16.CERTIFICATION_BITS
SELECTION_POLICY = i16.SELECTION_POLICY
SELECTION_SEMANTICS = i16.SELECTION_SEMANTICS
CERTIFIED_GREEDY_STEP_COUNT = 7
DIRECT_COMPATIBILITY_ARGUMENT_LIMIT = i16.TRIG_ARGUMENT_LIMIT
RANGE_REDUCTION_THRESHOLD_NUMERATOR = 1
RANGE_REDUCTION_THRESHOLD_DENOMINATOR = 8
MAX_TRIG_HALVINGS = 256
RANGE_REDUCTION_METHOD = "INTEGER_DYADIC_HALVING_TAYLOR_LAGRANGE_DOUBLE_ANGLE_RECONSTRUCTION"
PI_APPROXIMATION_AUTHORIZED = False

Interval = i15.Interval


class Pass215Iteration17Error(RuntimeError):
    pass


class Pass215Iteration17ValidationError(Pass215Iteration17Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration17ValidationError(f"PASS215_I17_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _iteration16_bindings() -> Mapping[str, Any]:
    return {
        "iteration16_closure_head": ITERATION16_CLOSURE_HEAD,
        "iteration16_closure_tree": ITERATION16_CLOSURE_TREE,
        "iteration16_generated_token_ids": list(ITERATION16_GENERATED_TOKEN_IDS),
        "iteration16_generated_tokens": list(ITERATION16_GENERATED_TOKENS),
        "iteration16_selection_roots": list(ITERATION16_SELECTION_ROOTS),
        "iteration16_append_roots": list(ITERATION16_APPEND_ROOTS),
        "iteration16_transition_roots": list(ITERATION16_TRANSITION_ROOTS),
        "iteration16_chain_root_hash216": ITERATION16_CHAIN_ROOT_HASH216,
        "iteration16_final_interval_suite_root_hash216": ITERATION16_FINAL_INTERVAL_SUITE_ROOT_HASH216,
        "iteration16_final_symbolic_dag_root_hash216": ITERATION16_FINAL_SYMBOLIC_DAG_ROOT_HASH216,
        "iteration16_suite_root_hash216": ITERATION16_SUITE_ROOT_HASH216,
        "iteration16_evidence_root_hash216": ITERATION16_EVIDENCE_ROOT_HASH216,
        "iteration16_receipt_hash72": ITERATION16_RECEIPT_HASH72,
        "iteration16_closure_artifact_id": ITERATION16_CLOSURE_ARTIFACT_ID,
        "iteration16_closure_artifact_sha256": ITERATION16_CLOSURE_ARTIFACT_SHA256,
    }


class ScalableRopeCertifiedDyadicContext(i16.MultistepCertifiedDyadicContext):
    """Iteration-16 compatible dyadic authority with scalable RoPE trig.

    Inputs inside the frozen |x| <= 8 domain use the exact Iteration-16 direct
    Taylor path, preserving the first three frozen interval identities. Larger
    RoPE angles are halved to |x| <= 1/8 and reconstructed with double-angle
    identities. No pi constant or point transcendental approximation is used.
    """

    def __init__(self, bits: int = CERTIFICATION_BITS) -> None:
        super().__init__(bits)
        self.direct_rope_pair_calls = 0
        self.range_reduced_rope_pair_calls = 0
        self.trig_halving_steps_total = 0
        self.trig_reconstruction_steps_total = 0
        self.trig_max_halving_depth = 0
        self._range_reduced_positions: set[int] = set()

    def _clip_unit(self, value: Interval) -> Interval:
        lo, hi = self._check(value)
        clipped = max(lo, -self.scale), min(hi, self.scale)
        if clipped[0] > clipped[1]:
            raise Pass215Iteration17ValidationError("PASS215_I17_TRIG_UNIT_CLIP_EMPTY")
        return self._check(clipped)

    def _range_reduced_pair(self, value: Interval) -> tuple[Interval, Interval]:
        reduced = self._check(value)
        threshold = self.scale * RANGE_REDUCTION_THRESHOLD_NUMERATOR // RANGE_REDUCTION_THRESHOLD_DENOMINATOR
        halvings = 0
        while max(abs(reduced[0]), abs(reduced[1])) > threshold:
            reduced = self.mul_rat(reduced, 1, 2)
            halvings += 1
            if halvings > MAX_TRIG_HALVINGS:
                raise Pass215Iteration17ValidationError("PASS215_I17_TRIG_RANGE_REDUCTION_UNBOUNDED")

        self.sin_calls += 1
        self.cos_calls += 1
        self.range_reduced_rope_pair_calls += 1
        self.trig_halving_steps_total += halvings
        self.trig_reconstruction_steps_total += halvings
        self.trig_max_halving_depth = max(self.trig_max_halving_depth, halvings)

        square = self.mul(reduced, reduced)

        sin_term = reduced
        sin_total = reduced
        for index in range(1, i15.TRIG_TAYLOR_TERMS):
            sin_term = self.mul(sin_term, square)
            sin_term = self.mul_rat(sin_term, -1, (2 * index) * (2 * index + 1))
            sin_total = self.add(sin_total, sin_term)
        sin_degree = 2 * i15.TRIG_TAYLOR_TERMS
        maximum = max(abs(reduced[0]), abs(reduced[1]))
        sin_remainder = self._remainder_bound(maximum, sin_degree, factorial(sin_degree))
        sine = self._check((sin_total[0] - sin_remainder, sin_total[1] + sin_remainder))

        cos_term = self.point(1)
        cos_total = cos_term
        for index in range(1, i15.TRIG_TAYLOR_TERMS):
            cos_term = self.mul(cos_term, square)
            cos_term = self.mul_rat(cos_term, -1, (2 * index - 1) * (2 * index))
            cos_total = self.add(cos_total, cos_term)
        cos_degree = 2 * i15.TRIG_TAYLOR_TERMS - 1
        cos_remainder = self._remainder_bound(maximum, cos_degree, factorial(cos_degree))
        cosine = self._check((cos_total[0] - cos_remainder, cos_total[1] + cos_remainder))

        for _ in range(halvings):
            prior_sine, prior_cosine = sine, cosine
            sine = self._clip_unit(self.mul_int(self.mul(prior_sine, prior_cosine), 2))
            cosine = self._clip_unit(
                self.sub(self.mul(prior_cosine, prior_cosine), self.mul(prior_sine, prior_sine))
            )
        return cosine, sine

    def rope_trig(self, position: int, pair_index: int) -> tuple[Interval, Interval]:
        key = (int(position), int(pair_index))
        prior = self._trig_cache.get(key)
        if prior is not None:
            return prior
        if position < 0 or not 0 <= pair_index < i15.HEAD_DIMENSION // 2:
            raise Pass215Iteration17ValidationError("PASS215_I17_ROPE_TRIG_INDEX_INVALID")
        if position == 0:
            result = (self.point(1), (0, 0))
            self._trig_cache[key] = result
            return result

        frequency = self.pow_integer_rational(10_000, -2 * pair_index, i15.HEAD_DIMENSION)
        angle = self.mul_int(frequency, position)
        maximum = max(abs(angle[0]), abs(angle[1]))
        if maximum <= DIRECT_COMPATIBILITY_ARGUMENT_LIMIT * self.scale:
            self.direct_rope_pair_calls += 1
            result = (super().cos(angle), super().sin(angle))
        else:
            self._range_reduced_positions.add(int(position))
            result = self._range_reduced_pair(angle)
        self._trig_cache[key] = result
        return result

    def manifest(self) -> Mapping[str, Any]:
        inherited = dict(super().manifest())
        inherited.pop("manifest_root_hash216", None)
        payload = {
            **inherited,
            "direct_compatibility_argument_limit_integer": DIRECT_COMPATIBILITY_ARGUMENT_LIMIT,
            "range_reduction_threshold": {
                "numerator": RANGE_REDUCTION_THRESHOLD_NUMERATOR,
                "denominator": RANGE_REDUCTION_THRESHOLD_DENOMINATOR,
            },
            "range_reduction_method": RANGE_REDUCTION_METHOD,
            "max_fail_closed_halvings": MAX_TRIG_HALVINGS,
            "pi_approximation_authorized": PI_APPROXIMATION_AUTHORIZED,
            "fixed_rope_argument_ceiling": False,
            "direct_rope_pair_calls": self.direct_rope_pair_calls,
            "range_reduced_rope_pair_calls": self.range_reduced_rope_pair_calls,
            "trig_halving_steps_total": self.trig_halving_steps_total,
            "trig_reconstruction_steps_total": self.trig_reconstruction_steps_total,
            "trig_max_halving_depth": self.trig_max_halving_depth,
            "range_reduced_positions": sorted(self._range_reduced_positions),
        }
        return {
            **payload,
            "manifest_root_hash216": i4base.hash216(
                "pass215-i17-scalable-rope-certified-dyadic-context",
                i4base.canonical_bytes(payload),
            ),
        }


def _context_counters(ctx: ScalableRopeCertifiedDyadicContext) -> Mapping[str, int]:
    return {
        "exp_calls": int(ctx.exp_calls),
        "sin_calls": int(ctx.sin_calls),
        "cos_calls": int(ctx.cos_calls),
        "rsqrt_calls": int(ctx.rsqrt_calls),
        "direct_rope_pair_calls": int(ctx.direct_rope_pair_calls),
        "range_reduced_rope_pair_calls": int(ctx.range_reduced_rope_pair_calls),
        "trig_halving_steps_total": int(ctx.trig_halving_steps_total),
        "trig_reconstruction_steps_total": int(ctx.trig_reconstruction_steps_total),
    }


def _counter_delta(before: Mapping[str, int], after: Mapping[str, int]) -> Mapping[str, int]:
    return {key: int(after[key]) - int(before[key]) for key in before}


def _interval_width_summary(
    logits: Sequence[Interval],
    *,
    selected_token_id: int,
    competitor_token_id: int,
) -> Mapping[str, int]:
    if len(logits) != VOCABULARY_SIZE:
        raise Pass215Iteration17ValidationError("PASS215_I17_INTERVAL_WIDTH_GEOMETRY_INVALID")
    widths = [int(hi) - int(lo) for lo, hi in logits]
    maximum = max(widths)
    selected = widths[int(selected_token_id)]
    competitor = widths[int(competitor_token_id)]
    return {
        "scale_denominator": 1 << CERTIFICATION_BITS,
        "maximum_logit_interval_width_numerator": maximum,
        "maximum_logit_interval_width_bit_length": maximum.bit_length(),
        "selected_logit_interval_width_numerator": selected,
        "selected_logit_interval_width_bit_length": selected.bit_length(),
        "competitor_logit_interval_width_numerator": competitor,
        "competitor_logit_interval_width_bit_length": competitor.bit_length(),
    }


def _interval_suite(logits: Sequence[Interval], *, bits: int, step_index: int) -> Mapping[str, Any]:
    if len(logits) != VOCABULARY_SIZE:
        raise Pass215Iteration17ValidationError("PASS215_I17_INTERVAL_SUITE_GEOMETRY_INVALID")
    if step_index <= i16.CERTIFIED_GREEDY_STEP_COUNT:
        return i16._interval_suite(logits, bits=bits, step_index=step_index)
    roots = [
        i4base.hash216(
            "pass215-i17-logit-interval-leaf",
            i4base.canonical_bytes({
                "step_index": step_index,
                "token_id": token_id,
                "lower": value[0],
                "upper": value[1],
                "bits": bits,
            }),
        )
        for token_id, value in enumerate(logits)
    ]
    return {
        "interval_leaf_count": len(roots),
        "interval_suite_root_hash216": i4base.hash216(
            "pass215-i17-complete-logit-interval-suite", i4base.canonical_bytes(roots)
        ),
    }


def _initialize_interval_state(
    raw: bytes,
    tokenizer: Mapping[str, Any],
    bindings: Mapping[int, Mapping[str, Any]],
    terminal_binding: Mapping[str, Any],
    *,
    bits: int,
) -> Mapping[str, Any]:
    ctx = ScalableRopeCertifiedDyadicContext(bits)
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, FROZEN_TOKEN_IDS)
    cache: MutableMapping[int, MutableMapping[str, list[tuple[Interval, ...]]]] = {
        block_index: {"k_rope": [], "v": []} for block_index in i12.BLOCK_INDEXES
    }
    final_hidden: tuple[Interval, ...] | None = None
    for position, row in enumerate(embeddings["rows"]):
        hidden = tuple(ctx.point(numerator, denominator) for numerator, denominator in row)
        for block_index in i12.BLOCK_INDEXES:
            hidden = i15._interval_block(
                ctx, hidden, bindings[block_index], cache[block_index],
                block_index=block_index, position=position,
            )
        final_hidden = tuple(hidden)
    if final_hidden is None:
        raise Pass215Iteration17ValidationError("PASS215_I17_PREFIX_INTERVAL_FORWARD_EMPTY")
    if any(len(cache[index]["k_rope"]) != PREFIX_SEQUENCE_LENGTH for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration17ValidationError("PASS215_I17_PREFIX_INTERVAL_CACHE_GEOMETRY_INVALID")
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    normalized = i15._interval_rmsnorm(ctx, final_hidden, norm_weights)
    logits = i15._interval_q8_projection(ctx, terminal_binding["output_payload"], normalized)
    return {
        "context": ctx,
        "cache": cache,
        "logits": logits,
        "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
        **_interval_suite(logits, bits=bits, step_index=0),
    }


def _append_interval_token(
    raw: bytes,
    tokenizer: Mapping[str, Any],
    bindings: Mapping[int, Mapping[str, Any]],
    terminal_binding: Mapping[str, Any],
    ctx: ScalableRopeCertifiedDyadicContext,
    cache: MutableMapping[int, MutableMapping[str, list[tuple[Interval, ...]]]],
    *,
    token_id: int,
    absolute_position: int,
    next_step_index: int,
) -> Mapping[str, Any]:
    embedding = i9._extract_authenticated_embeddings(raw, tokenizer, (int(token_id),))
    hidden = tuple(ctx.point(numerator, denominator) for numerator, denominator in embedding["rows"][0])
    pre_lengths = {index: len(cache[index]["k_rope"]) for index in i12.BLOCK_INDEXES}
    if any(length != absolute_position for length in pre_lengths.values()):
        raise Pass215Iteration17ValidationError("PASS215_I17_INTERVAL_APPEND_CACHE_POSITION_INVALID")
    before = _context_counters(ctx)
    for block_index in i12.BLOCK_INDEXES:
        hidden = i15._interval_block(
            ctx, hidden, bindings[block_index], cache[block_index],
            block_index=block_index, position=absolute_position,
        )
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    normalized = i15._interval_rmsnorm(ctx, hidden, norm_weights)
    logits = i15._interval_q8_projection(ctx, terminal_binding["output_payload"], normalized)
    after = _context_counters(ctx)
    return {
        "logits": logits,
        "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
        "prefix_recomputed": False,
        "cache_lengths_before": pre_lengths,
        "cache_lengths_after": {index: len(cache[index]["k_rope"]) for index in i12.BLOCK_INDEXES},
        "context_counter_delta": _counter_delta(before, after),
        **_interval_suite(logits, bits=ctx.bits, step_index=next_step_index),
    }


def _iteration16_compatible_transition_root(
    *,
    step_index: int,
    selected_from_position: int,
    absolute_position: int,
    token_id: int,
    selection_root_hash216: str,
    source_interval_suite_root_hash216: str,
    symbolic_append: Mapping[str, Any],
    produced_interval_suite_root_hash216: str,
) -> str:
    payload = {
        "step_index": step_index,
        "selected_from_absolute_position": selected_from_position,
        "appended_at_absolute_position": absolute_position,
        "selected_token_id": token_id,
        "selection_root_hash216": selection_root_hash216,
        "source_interval_suite_root_hash216": source_interval_suite_root_hash216,
        "symbolic_append_root_hash216": symbolic_append["append_forward_root_hash216"],
        "produced_symbolic_logits_root_hash216": symbolic_append["logits_root_hash216"],
        "produced_interval_suite_root_hash216": produced_interval_suite_root_hash216,
    }
    return i4base.hash216("pass215-i16-certified-greedy-step", i4base.canonical_bytes(payload))


def _reproduce_iteration16_chain_root(
    *,
    selected_ids: Sequence[int],
    transition_roots: Sequence[str],
    final_dag_root: str,
    final_interval_suite_root: str,
) -> str:
    payload = {
        "iteration15_evidence_root_hash216": i16.ITERATION15_EVIDENCE_ROOT_HASH216,
        "selected_token_ids": list(selected_ids),
        "step_roots": list(transition_roots),
        "final_symbolic_dag_root_hash216": final_dag_root,
        "final_interval_suite_root_hash216": final_interval_suite_root,
    }
    return i4base.hash216("pass215-i16-multistep-certified-greedy-chain", i4base.canonical_bytes(payload))


def build_scalable_rope_certified_greedy_evidence(
    raw: bytes,
    *,
    filename: str,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
    certification_bits: int = CERTIFICATION_BITS,
    greedy_steps: int = CERTIFIED_GREEDY_STEP_COUNT,
) -> Mapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration17ValidationError("PASS215_I17_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration17ValidationError("PASS215_I17_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration17ValidationError("PASS215_I17_PROMPT_OUTSIDE_CONTRACT")
    if certification_bits != CERTIFICATION_BITS:
        raise Pass215Iteration17ValidationError("PASS215_I17_CERTIFICATION_BITS_OUTSIDE_CONTRACT")
    if greedy_steps != CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration17ValidationError("PASS215_I17_GREEDY_STEP_COUNT_OUTSIDE_CONTRACT")

    symbolic = i15._symbolic_prefix_and_logits(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    prefix = symbolic["prefix"]
    tokenizer = symbolic["tokenizer"]
    bindings = symbolic["bindings"]
    terminal_binding = symbolic["terminal_binding"]
    dag = prefix["dag"]
    symbolic_cache = i14._materialize_prefix_kv_cache(dag, prefix, bindings)
    initial_node_count = int(dag.manifest()["unique_node_count"])
    if any(len(symbolic_cache[index]["k_rope"]) != PREFIX_SEQUENCE_LENGTH for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration17ValidationError("PASS215_I17_PREFIX_SYMBOLIC_CACHE_GEOMETRY_INVALID")

    interval = _initialize_interval_state(raw, tokenizer, bindings, terminal_binding, bits=certification_bits)
    if interval["embedding_suite_root_hash216"] != i11.ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration17ValidationError("PASS215_I17_INTERVAL_EMBEDDING_ROOT_CHANGED")
    if interval["interval_suite_root_hash216"] != i16.ITERATION15_INTERVAL_SUITE_ROOT_HASH216:
        raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION15_INTERVAL_SUITE_NOT_REPRODUCED")

    current_interval_logits = interval["logits"]
    current_interval_suite_root = interval["interval_suite_root_hash216"]
    current_symbolic_logits = symbolic["final_position_symbolic_logits"]
    selected_from_position = PREFIX_SEQUENCE_LENGTH - 1
    source_state_range_reduced = False
    steps: list[Mapping[str, Any]] = []
    compatible_transition_roots: list[str] = []

    for step_index in range(greedy_steps):
        selection = i15._certify_strict_argmax(
            current_interval_logits,
            symbolic_logit_roots=current_symbolic_logits,
            tokenizer=tokenizer,
            interval_suite_root_hash216=current_interval_suite_root,
            bits=certification_bits,
        )
        token_id = int(selection["selected_token_id"])
        if step_index < i16.CERTIFIED_GREEDY_STEP_COUNT:
            if token_id != ITERATION16_GENERATED_TOKEN_IDS[step_index]:
                raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION16_TOKEN_NOT_REPRODUCED")
            if selection["selection_root_hash216"] != ITERATION16_SELECTION_ROOTS[step_index]:
                raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION16_SELECTION_ROOT_NOT_REPRODUCED")

        width_summary = _interval_width_summary(
            current_interval_logits,
            selected_token_id=token_id,
            competitor_token_id=int(selection["strongest_competitor_token_id"]),
        )
        absolute_position = PREFIX_SEQUENCE_LENGTH + step_index
        symbolic_append = i16._append_symbolic_token(
            raw, tokenizer, bindings, terminal_binding, dag, symbolic_cache,
            token_id=token_id,
            selection_root_hash216=selection["selection_root_hash216"],
            absolute_position=absolute_position,
            step_index=step_index,
        )
        if symbolic_append["prefix_hidden_rows_recomputed"] != 0:
            raise Pass215Iteration17ValidationError("PASS215_I17_PREFIX_SYMBOLIC_ROWS_RECOMPUTED")

        interval_append = _append_interval_token(
            raw, tokenizer, bindings, terminal_binding,
            interval["context"], interval["cache"],
            token_id=token_id,
            absolute_position=absolute_position,
            next_step_index=step_index + 1,
        )
        if interval_append["prefix_recomputed"] is not False:
            raise Pass215Iteration17ValidationError("PASS215_I17_INTERVAL_PREFIX_RECOMPUTED")
        reduction_delta = interval_append["context_counter_delta"]
        append_used_range_reduction = int(reduction_delta["range_reduced_rope_pair_calls"]) > 0

        transition_root = _iteration16_compatible_transition_root(
            step_index=step_index,
            selected_from_position=selected_from_position,
            absolute_position=absolute_position,
            token_id=token_id,
            selection_root_hash216=selection["selection_root_hash216"],
            source_interval_suite_root_hash216=current_interval_suite_root,
            symbolic_append=symbolic_append,
            produced_interval_suite_root_hash216=interval_append["interval_suite_root_hash216"],
        )
        compatible_transition_roots.append(transition_root)
        if step_index < i16.CERTIFIED_GREEDY_STEP_COUNT and transition_root != ITERATION16_TRANSITION_ROOTS[step_index]:
            raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION16_TRANSITION_ROOT_NOT_REPRODUCED")

        step_payload = {
            "step_index": step_index,
            "selected_from_absolute_position": selected_from_position,
            "appended_at_absolute_position": absolute_position,
            "selected_token_id": token_id,
            "selection_root_hash216": selection["selection_root_hash216"],
            "source_interval_suite_root_hash216": current_interval_suite_root,
            "iteration16_compatible_transition_root_hash216": transition_root,
            "source_state_used_range_reduced_trig": source_state_range_reduced,
            "append_used_range_reduced_trig": append_used_range_reduction,
            "produced_interval_suite_root_hash216": interval_append["interval_suite_root_hash216"],
        }
        step_root = i4base.hash216(
            "pass215-i17-scalable-rope-certified-greedy-step", i4base.canonical_bytes(step_payload)
        )
        steps.append({
            "step_index": step_index,
            "selected_from_absolute_position": selected_from_position,
            "appended_at_absolute_position": absolute_position,
            "selected_token_id": token_id,
            "selected_token": str(tokenizer["tokens"][token_id]),
            "selected_symbolic_logit_root_hash216": selection["selected_symbolic_logit_root_hash216"],
            "strongest_competitor_token_id": int(selection["strongest_competitor_token_id"]),
            "strongest_competitor_token": selection["strongest_competitor_token"],
            "strict_margin_lower_bound": selection["strict_margin_lower_bound"],
            "strict_interval_separation": True,
            "certified_true_argmax": True,
            "source_state_used_range_reduced_trig": source_state_range_reduced,
            "source_interval_width_summary": width_summary,
            "source_interval_suite_root_hash216": current_interval_suite_root,
            "selection_root_hash216": selection["selection_root_hash216"],
            "symbolic_append": {key: value for key, value in symbolic_append.items() if key not in {"logit_roots", "block_records"}},
            "block_forward_roots": [record["block_forward_root_hash216"] for record in symbolic_append["block_records"]],
            "produced_interval_suite_root_hash216": interval_append["interval_suite_root_hash216"],
            "interval_cache_lengths_before": interval_append["cache_lengths_before"],
            "interval_cache_lengths_after": interval_append["cache_lengths_after"],
            "interval_context_counter_delta": reduction_delta,
            "append_used_range_reduced_trig": append_used_range_reduction,
            "iteration16_compatible_transition_root_hash216": transition_root,
            "step_root_hash216": step_root,
        })

        current_symbolic_logits = symbolic_append["logit_roots"]
        current_interval_logits = interval_append["logits"]
        current_interval_suite_root = interval_append["interval_suite_root_hash216"]
        selected_from_position = absolute_position
        source_state_range_reduced = append_used_range_reduction

        if step_index == i16.CERTIFIED_GREEDY_STEP_COUNT - 1:
            if current_interval_suite_root != ITERATION16_FINAL_INTERVAL_SUITE_ROOT_HASH216:
                raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION16_FINAL_INTERVAL_ROOT_NOT_REPRODUCED")
            current_dag_root = dag.manifest()["ordered_node_root_hash216"]
            if current_dag_root != ITERATION16_FINAL_SYMBOLIC_DAG_ROOT_HASH216:
                raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION16_FINAL_DAG_ROOT_NOT_REPRODUCED")
            reproduced_chain = _reproduce_iteration16_chain_root(
                selected_ids=ITERATION16_GENERATED_TOKEN_IDS,
                transition_roots=compatible_transition_roots[:i16.CERTIFIED_GREEDY_STEP_COUNT],
                final_dag_root=current_dag_root,
                final_interval_suite_root=current_interval_suite_root,
            )
            if reproduced_chain != ITERATION16_CHAIN_ROOT_HASH216:
                raise Pass215Iteration17ValidationError("PASS215_I17_ITERATION16_CHAIN_ROOT_NOT_REPRODUCED")

    if len(steps) != CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration17ValidationError("PASS215_I17_STEP_COUNT_INVALID")
    if not any(bool(step["source_state_used_range_reduced_trig"]) for step in steps):
        raise Pass215Iteration17ValidationError("PASS215_I17_NO_CERTIFIED_SELECTION_FROM_RANGE_REDUCED_STATE")

    final_node_count = int(dag.manifest()["unique_node_count"])
    final_cache_length = PREFIX_SEQUENCE_LENGTH + CERTIFIED_GREEDY_STEP_COUNT
    if any(len(symbolic_cache[index]["k_rope"]) != final_cache_length for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration17ValidationError("PASS215_I17_FINAL_SYMBOLIC_CACHE_GEOMETRY_INVALID")
    if any(len(interval["cache"][index]["k_rope"]) != final_cache_length for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration17ValidationError("PASS215_I17_FINAL_INTERVAL_CACHE_GEOMETRY_INVALID")

    selected_ids = [int(step["selected_token_id"]) for step in steps]
    step_roots = [str(step["step_root_hash216"]) for step in steps]
    chain_payload = {
        "iteration16_evidence_root_hash216": ITERATION16_EVIDENCE_ROOT_HASH216,
        "iteration16_chain_root_hash216": ITERATION16_CHAIN_ROOT_HASH216,
        "selected_token_ids": selected_ids,
        "step_roots": step_roots,
        "final_symbolic_dag_root_hash216": dag.manifest()["ordered_node_root_hash216"],
        "final_interval_suite_root_hash216": current_interval_suite_root,
    }
    chain_root = i4base.hash216(
        "pass215-i17-scalable-rope-certified-greedy-chain", i4base.canonical_bytes(chain_payload)
    )
    total_prior_reuse = sum(int(step["symbolic_append"]["prior_kv_token_rows_reused"]) for step in steps)
    total_new_kv = sum(int(step["symbolic_append"]["new_kv_token_rows_materialized"]) for step in steps)
    range_reduced_certified_selections = sum(bool(step["source_state_used_range_reduced_trig"]) for step in steps)
    source_record = {
        **dict(source),
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    }
    executor_manifest = interval["context"].manifest()
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
            "bounded_scalable_rope_greedy_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            **_iteration16_bindings(),
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "contracted_text_ingress": {
            "input_text": prompt,
            "token_ids": list(FROZEN_TOKEN_IDS),
            "prefix_sequence_length": PREFIX_SEQUENCE_LENGTH,
        },
        "iteration16_semantic_reproduction": {
            "exact": True,
            "selected_token_ids": selected_ids[:i16.CERTIFIED_GREEDY_STEP_COUNT],
            "selection_roots": [step["selection_root_hash216"] for step in steps[:i16.CERTIFIED_GREEDY_STEP_COUNT]],
            "append_roots": [step["symbolic_append"]["append_forward_root_hash216"] for step in steps[:i16.CERTIFIED_GREEDY_STEP_COUNT]],
            "transition_roots": compatible_transition_roots[:i16.CERTIFIED_GREEDY_STEP_COUNT],
            "final_interval_suite_root_hash216": steps[i16.CERTIFIED_GREEDY_STEP_COUNT - 1]["produced_interval_suite_root_hash216"],
            "frozen_final_symbolic_dag_root_hash216": ITERATION16_FINAL_SYMBOLIC_DAG_ROOT_HASH216,
            "frozen_chain_root_hash216": ITERATION16_CHAIN_ROOT_HASH216,
            **_iteration16_bindings(),
        },
        "scalable_rope_certified_greedy": {
            "greedy_step_count": CERTIFIED_GREEDY_STEP_COUNT,
            "selected_token_ids": selected_ids,
            "selected_tokens": [str(step["selected_token"]) for step in steps],
            "steps": steps,
            "chain_root_hash216": chain_root,
            "prefix_symbolic_reconstruction_count": 1,
            "prefix_interval_replay_count": 1,
            "prefix_replays_after_initialization": 0,
            "final_cache_sequence_length": final_cache_length,
            "final_symbolic_dag": dag.manifest(),
            "initial_symbolic_node_count": initial_node_count,
            "new_symbolic_nodes_after_prefix": final_node_count - initial_node_count,
        },
        "certified_interval_executor": executor_manifest,
        "work_geometry": {
            "certification_bits": certification_bits,
            "complete_vocabulary_certifications": CERTIFIED_GREEDY_STEP_COUNT,
            "candidate_interval_comparisons": CERTIFIED_GREEDY_STEP_COUNT * (VOCABULARY_SIZE - 1),
            "greedy_append_transitions": CERTIFIED_GREEDY_STEP_COUNT,
            "prefix_hidden_rows_recomputed_after_initialization": 0,
            "prior_kv_token_rows_reused": total_prior_reuse,
            "new_kv_token_rows_materialized": total_new_kv,
            "terminal_q8_logical_weight_products_per_certification": VOCABULARY_SIZE * EMBEDDING_WIDTH,
            "terminal_q8_logical_weight_products_total": CERTIFIED_GREEDY_STEP_COUNT * VOCABULARY_SIZE * EMBEDDING_WIDTH,
            "range_reduced_rope_pair_calls": executor_manifest["range_reduced_rope_pair_calls"],
            "trig_halving_steps_total": executor_manifest["trig_halving_steps_total"],
            "trig_max_halving_depth": executor_manifest["trig_max_halving_depth"],
            "range_reduced_certified_selections": range_reduced_certified_selections,
            "adaptive_precision_escalations": 0,
            "source_interval_width_summaries": [step["source_interval_width_summary"] for step in steps],
        },
        "claims": {
            "authenticated_iteration16_roots_inherited_unchanged": True,
            "iteration16_three_step_chain_reproduced_exactly": True,
            "seven_consecutive_complete_logit_vectors_certified": True,
            "seven_consecutive_true_logit_argmax_selections_executed": True,
            "seven_consecutive_true_greedy_appends_executed": True,
            "fixed_direct_rope_argument_ceiling_removed_by_integer_range_reduction": True,
            "certified_selection_from_range_reduced_rope_state_executed": True,
            "fixed_256_bit_certification_succeeded_without_precision_escalation": True,
            "prefix_state_reused_without_recomputation_after_initialization": True,
            "kv_cache_reused_across_all_greedy_steps": True,
            "bounded_scalable_rope_generation_witness_executed": True,
            "pi_approximation_used": False,
            "hash_identity_order_used_as_greedy_authority": False,
            "probabilistic_sampling_executed": False,
            "unbounded_or_general_generation_claimed": False,
            "general_arbitrary_sequence_length_transformer_forward_executed": False,
            "adaptive_precision_authority_promoted": False,
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
        "iteration16_suite_root_hash216": ITERATION16_SUITE_ROOT_HASH216,
        "step_roots": step_roots,
        "chain_root_hash216": chain_root,
        "final_interval_suite_root_hash216": current_interval_suite_root,
        "final_symbolic_dag_root_hash216": dag.manifest()["ordered_node_root_hash216"],
        "range_reduced_positions": executor_manifest["range_reduced_positions"],
    }
    suite_root = i4base.hash216(
        "pass215-i17-scalable-rope-certified-greedy-suite", i4base.canonical_bytes(suite_payload)
    )
    evidence["scalable_rope_certified_greedy_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i17-scalable-rope-certified-greedy-evidence", i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION17_SCALABLE_ROPE_CERTIFIED_GREEDY"},
        {
            "sequence": 17,
            "parent_hash72": ITERATION16_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "chain_root_hash216": chain_root,
            "selected_token_ids": selected_ids,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_scalable_rope_certified_greedy_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
    certification_bits: int = CERTIFICATION_BITS,
    greedy_steps: int = CERTIFIED_GREEDY_STEP_COUNT,
) -> Mapping[str, Any]:
    source_path = Path(path)
    return build_scalable_rope_certified_greedy_evidence(
        source_path.read_bytes(), filename=source_path.name, source=source,
        prompt=prompt, expected_sha256=expected_sha256,
        certification_bits=certification_bits, greedy_steps=greedy_steps,
    )


def validate_scalable_rope_certified_greedy_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration17ValidationError("PASS215_I17_SCHEMA_OR_CONTRACT_INVALID")
    required_inherits = {
        **_iteration16_bindings(),
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if evidence.get("inherits") != required_inherits:
        raise Pass215Iteration17ValidationError("PASS215_I17_INHERITANCE_INVALID")
    continuation = evidence.get("scalable_rope_certified_greedy", {})
    steps = continuation.get("steps", [])
    if int(continuation.get("greedy_step_count", 0)) != CERTIFIED_GREEDY_STEP_COUNT or len(steps) != CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration17ValidationError("PASS215_I17_STEP_COUNT_INVALID")
    if tuple(int(step.get("selected_token_id", -1)) for step in steps[:3]) != ITERATION16_GENERATED_TOKEN_IDS:
        raise Pass215Iteration17ValidationError("PASS215_I17_PARENT_TOKEN_CHAIN_INVALID")
    if tuple(step.get("selection_root_hash216") for step in steps[:3]) != ITERATION16_SELECTION_ROOTS:
        raise Pass215Iteration17ValidationError("PASS215_I17_PARENT_SELECTION_ROOTS_INVALID")
    if tuple(step.get("iteration16_compatible_transition_root_hash216") for step in steps[:3]) != ITERATION16_TRANSITION_ROOTS:
        raise Pass215Iteration17ValidationError("PASS215_I17_PARENT_TRANSITION_ROOTS_INVALID")
    for index, step in enumerate(steps):
        if int(step.get("step_index", -1)) != index:
            raise Pass215Iteration17ValidationError("PASS215_I17_STEP_INDEX_INVALID")
        if step.get("strict_interval_separation") is not True or step.get("certified_true_argmax") is not True:
            raise Pass215Iteration17ValidationError("PASS215_I17_STEP_ARGMAX_CERTIFICATE_MISSING")
        margin = step.get("strict_margin_lower_bound", {})
        if int(margin.get("numerator", 0)) <= 0 or int(margin.get("denominator", 0)) != 1 << CERTIFICATION_BITS:
            raise Pass215Iteration17ValidationError("PASS215_I17_STEP_MARGIN_INVALID")
        append = step.get("symbolic_append", {})
        if int(append.get("appended_token_id", -1)) != int(step.get("selected_token_id", -2)):
            raise Pass215Iteration17ValidationError("PASS215_I17_STEP_APPEND_TOKEN_MISMATCH")
        if append.get("prefix_recomputed") is not False or append.get("kv_cache_reused") is not True:
            raise Pass215Iteration17ValidationError("PASS215_I17_STEP_CACHE_REUSE_INVALID")
        if int(append.get("prefix_hidden_rows_recomputed", -1)) != 0:
            raise Pass215Iteration17ValidationError("PASS215_I17_STEP_PREFIX_RECOMPUTATION_INVALID")
    if not any(step.get("source_state_used_range_reduced_trig") is True for step in steps):
        raise Pass215Iteration17ValidationError("PASS215_I17_RANGE_REDUCED_SELECTION_MISSING")
    if int(continuation.get("prefix_replays_after_initialization", -1)) != 0:
        raise Pass215Iteration17ValidationError("PASS215_I17_PREFIX_REPLAY_INVALID")
    if int(continuation.get("final_cache_sequence_length", 0)) != PREFIX_SEQUENCE_LENGTH + CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration17ValidationError("PASS215_I17_FINAL_CACHE_LENGTH_INVALID")
    executor = evidence.get("certified_interval_executor", {})
    if executor.get("fixed_rope_argument_ceiling") is not False:
        raise Pass215Iteration17ValidationError("PASS215_I17_FIXED_ROPE_CEILING_NOT_REMOVED")
    if executor.get("pi_approximation_authorized") is not False:
        raise Pass215Iteration17ValidationError("PASS215_I17_PI_APPROXIMATION_AUTHORIZED")
    if int(executor.get("range_reduced_rope_pair_calls", 0)) <= 0:
        raise Pass215Iteration17ValidationError("PASS215_I17_RANGE_REDUCTION_NOT_EXECUTED")

    claims = evidence.get("claims", {})
    required_true = (
        "authenticated_iteration16_roots_inherited_unchanged",
        "iteration16_three_step_chain_reproduced_exactly",
        "seven_consecutive_complete_logit_vectors_certified",
        "seven_consecutive_true_logit_argmax_selections_executed",
        "seven_consecutive_true_greedy_appends_executed",
        "fixed_direct_rope_argument_ceiling_removed_by_integer_range_reduction",
        "certified_selection_from_range_reduced_rope_state_executed",
        "fixed_256_bit_certification_succeeded_without_precision_escalation",
        "prefix_state_reused_without_recomputation_after_initialization",
        "kv_cache_reused_across_all_greedy_steps",
        "bounded_scalable_rope_generation_witness_executed",
    )
    required_false = (
        "pi_approximation_used",
        "hash_identity_order_used_as_greedy_authority",
        "probabilistic_sampling_executed",
        "unbounded_or_general_generation_claimed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
        "adaptive_precision_authority_promoted",
        "numeric_transcendental_point_evaluation_performed",
        "approximate_transcendental_point_evaluation_performed",
        "canonical_float_interpretation_performed",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    )
    for key in required_true:
        if claims.get(key) is not True:
            raise Pass215Iteration17ValidationError(f"PASS215_I17_REQUIRED_CLAIM_FALSE:{key}")
    for key in required_false:
        if claims.get(key) is not False:
            raise Pass215Iteration17ValidationError(f"PASS215_I17_FORBIDDEN_CLAIM_TRUE:{key}")
    if evidence.get("authority", {}).get("no_float_canonical_authority") is not True:
        raise Pass215Iteration17ValidationError("PASS215_I17_NO_FLOAT_AUTHORITY_MISSING")


def compare_scalable_rope_certified_greedy_replays(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> Mapping[str, Any]:
    validate_scalable_rope_certified_greedy_evidence(left)
    validate_scalable_rope_certified_greedy_evidence(right)
    mismatches: list[str] = []
    for key in ("scalable_rope_certified_greedy_suite_root_hash216", "evidence_root_hash216", "receipt_hash72"):
        if left.get(key) != right.get(key):
            mismatches.append(key)
    left_chain = left["scalable_rope_certified_greedy"]
    right_chain = right["scalable_rope_certified_greedy"]
    for key in ("chain_root_hash216", "selected_token_ids"):
        if left_chain.get(key) != right_chain.get(key):
            mismatches.append(key)
    if mismatches:
        raise Pass215Iteration17ValidationError("PASS215_I17_REPLAY_MISMATCH:" + ",".join(mismatches))
    return {
        "schema": REPLAY_SCHEMA,
        "contract": CONTRACT,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "certified_step_count": CERTIFIED_GREEDY_STEP_COUNT,
        "selected_token_ids": list(left_chain["selected_token_ids"]),
        "chain_root_hash216": left_chain["chain_root_hash216"],
        "suite_root_hash216": left["scalable_rope_certified_greedy_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }

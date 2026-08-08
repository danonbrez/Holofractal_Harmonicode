"""Pass 215 Iteration 16 multi-step certified true-greedy continuation.

Iteration 15 proved one true greedy append for the authenticated ``Hello world!``
witness by certifying a strict 32,000-logit magnitude argmax with integer-only
outward dyadic bounds.  Iteration 16 preserves that authority across three
consecutive greedy append transitions.

The prefix is symbolically reconstructed once and interval-replayed once.  Both
the symbolic KV cache and the certified interval KV cache are then retained and
extended in place.  At every generation step all 32,000 current logits are
certified, the strict true argmax is selected, and only that new token is passed
through the six blocks at the next absolute position.  No original prefix hidden
row is recomputed after initialization.

This remains a bounded benchmark witness.  It does not authorize probabilistic
sampling, arbitrary-length generation, canonical float interpretation, dense
forward replacement, runtime mutation, canonical mutation, or migration.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration4_exact_linear_execution_v1 as i4base
from hhs_backend.runtime import hhs_pass215_iteration7_symbolic_coordinate_forward_v1 as i7
from hhs_backend.runtime import hhs_pass215_iteration9_authenticated_token_ingress_v2 as i9
from hhs_backend.runtime import hhs_pass215_iteration11_sequential_two_block_v1 as i11
from hhs_backend.runtime import hhs_pass215_iteration12_all_six_block_forward_v1 as i12
from hhs_backend.runtime import hhs_pass215_iteration14_autoregressive_continuation_v1 as i14
from hhs_backend.runtime import hhs_pass215_iteration15_certified_greedy_logit_v1 as i15

CONTRACT = "HHS-P215-I16-MULTISTEP-CERTIFIED-TRUE-GREEDY-CONTINUATION"
PASS_NUMBER = 215
ITERATION = 16
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_16_MULTISTEP_CERTIFIED_GREEDY_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_16_MULTISTEP_CERTIFIED_GREEDY_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_16_MULTISTEP_CERTIFIED_GREEDY_REPLAY_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_16_MULTISTEP_CERTIFIED_GREEDY_BENCHMARK"

ITERATION15_CLOSURE_HEAD = "7d58d29fa9690f4239b8e8f3ad30f34736f47f84"
ITERATION15_CLOSURE_TREE = "d556c1bb07e62cefba8f45df9c6cf8978645cdc8"
ITERATION15_SELECTED_TOKEN_ID = 450
ITERATION15_SELECTED_TOKEN = "▁The"
ITERATION15_SELECTED_SYMBOLIC_LOGIT_ROOT_HASH216 = "06174888c09ddb16bed56f92c0291e0bc1becd5b5baa883fcbc2375268348764"
ITERATION15_INTERVAL_SUITE_ROOT_HASH216 = "fe97babc80b71deee97250110d2bf6c50f5e51437ae53d16c745d51c5dc9e996"
ITERATION15_SELECTION_ROOT_HASH216 = "aac3225975c44b9b761dd131afedfc01123a3c5da187f76bd9de5c9bf2abee94"
ITERATION15_APPEND_FORWARD_ROOT_HASH216 = "f1757269ee3ed98a67434c799a89750da26dcaa11be9ce688a093d52febb5a75"
ITERATION15_GREEDY_FORWARD_ROOT_HASH216 = "36433241bb31e511fc24c60290bf56171cbe6b11d9efc8c3802318c71d0f7c8d"
ITERATION15_SUITE_ROOT_HASH216 = "40b5abf2ba4ecee376e7e8753ab87fef733ba9868e47a8114949a5010f6e234d"
ITERATION15_EVIDENCE_ROOT_HASH216 = "d04d5153a22883c01f1ac9f879ba46fa8afbebb4214692bf83e492091b5aca12"
ITERATION15_RECEIPT_HASH72 = "uzxAvsD/x7Kj*upEF-sxHn-DYcdOuOaWqRHGh!KaarjdEzkg!-kW?J<cw8oik4W!Qf29PoOT"
ITERATION15_CLOSURE_ARTIFACT_SHA256 = "a00c444f8d71d8a1d0fe95d25d42849297487ff711a2829167de8022e697adac"

REAL_MODEL_SHA256 = i15.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i15.CONTRACTED_PROMPT
FROZEN_TOKEN_IDS = i15.FROZEN_TOKEN_IDS
PREFIX_SEQUENCE_LENGTH = i15.PREFIX_SEQUENCE_LENGTH
EMBEDDING_WIDTH = i15.EMBEDDING_WIDTH
VOCABULARY_SIZE = i15.VOCABULARY_SIZE
CERTIFICATION_BITS = i15.CERTIFICATION_BITS
SELECTION_POLICY = i15.SELECTION_POLICY
SELECTION_SEMANTICS = i15.SELECTION_SEMANTICS
CERTIFIED_GREEDY_STEP_COUNT = 3

Interval = i15.Interval


class Pass215Iteration16Error(RuntimeError):
    pass


class Pass215Iteration16ValidationError(Pass215Iteration16Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration16ValidationError(f"PASS215_I16_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _iteration15_bindings() -> Mapping[str, Any]:
    return {
        "iteration15_closure_head": ITERATION15_CLOSURE_HEAD,
        "iteration15_closure_tree": ITERATION15_CLOSURE_TREE,
        "iteration15_selected_token_id": ITERATION15_SELECTED_TOKEN_ID,
        "iteration15_selected_token": ITERATION15_SELECTED_TOKEN,
        "iteration15_selected_symbolic_logit_root_hash216": ITERATION15_SELECTED_SYMBOLIC_LOGIT_ROOT_HASH216,
        "iteration15_interval_suite_root_hash216": ITERATION15_INTERVAL_SUITE_ROOT_HASH216,
        "iteration15_selection_root_hash216": ITERATION15_SELECTION_ROOT_HASH216,
        "iteration15_append_forward_root_hash216": ITERATION15_APPEND_FORWARD_ROOT_HASH216,
        "iteration15_greedy_forward_root_hash216": ITERATION15_GREEDY_FORWARD_ROOT_HASH216,
        "iteration15_suite_root_hash216": ITERATION15_SUITE_ROOT_HASH216,
        "iteration15_evidence_root_hash216": ITERATION15_EVIDENCE_ROOT_HASH216,
        "iteration15_receipt_hash72": ITERATION15_RECEIPT_HASH72,
        "iteration15_closure_artifact_sha256": ITERATION15_CLOSURE_ARTIFACT_SHA256,
    }


def _interval_suite(
    logits: Sequence[Interval],
    *,
    bits: int,
    step_index: int,
) -> Mapping[str, Any]:
    if len(logits) != VOCABULARY_SIZE:
        raise Pass215Iteration16ValidationError("PASS215_I16_INTERVAL_SUITE_GEOMETRY_INVALID")
    if step_index == 0:
        leaf_label = "pass215-i15-logit-interval-leaf"
        suite_label = "pass215-i15-complete-logit-interval-suite"
        leaf_payload = lambda token_id, value: {
            "token_id": token_id,
            "lower": value[0],
            "upper": value[1],
            "bits": bits,
        }
    else:
        leaf_label = "pass215-i16-logit-interval-leaf"
        suite_label = "pass215-i16-complete-logit-interval-suite"
        leaf_payload = lambda token_id, value: {
            "step_index": step_index,
            "token_id": token_id,
            "lower": value[0],
            "upper": value[1],
            "bits": bits,
        }
    roots = [
        i4base.hash216(leaf_label, i4base.canonical_bytes(leaf_payload(token_id, value)))
        for token_id, value in enumerate(logits)
    ]
    return {
        "interval_leaf_count": len(roots),
        "interval_suite_root_hash216": i4base.hash216(
            suite_label, i4base.canonical_bytes(roots)
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
    ctx = i15.CertifiedDyadicContext(bits)
    embeddings = i9._extract_authenticated_embeddings(raw, tokenizer, FROZEN_TOKEN_IDS)
    cache: MutableMapping[int, MutableMapping[str, list[tuple[Interval, ...]]]] = {
        block_index: {"k_rope": [], "v": []} for block_index in i12.BLOCK_INDEXES
    }
    final_hidden: tuple[Interval, ...] | None = None
    for position, row in enumerate(embeddings["rows"]):
        hidden = tuple(ctx.point(numerator, denominator) for numerator, denominator in row)
        for block_index in i12.BLOCK_INDEXES:
            hidden = i15._interval_block(
                ctx,
                hidden,
                bindings[block_index],
                cache[block_index],
                block_index=block_index,
                position=position,
            )
        final_hidden = tuple(hidden)
    if final_hidden is None:
        raise Pass215Iteration16ValidationError("PASS215_I16_PREFIX_INTERVAL_FORWARD_EMPTY")
    if any(len(cache[index]["k_rope"]) != PREFIX_SEQUENCE_LENGTH for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration16ValidationError("PASS215_I16_PREFIX_INTERVAL_CACHE_GEOMETRY_INVALID")
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    normalized = i15._interval_rmsnorm(ctx, final_hidden, norm_weights)
    logits = i15._interval_q8_projection(ctx, terminal_binding["output_payload"], normalized)
    suite = _interval_suite(logits, bits=bits, step_index=0)
    return {
        "context": ctx,
        "cache": cache,
        "logits": logits,
        "embedding_suite_root_hash216": embeddings["embedding_suite_root_hash216"],
        **suite,
    }


def _append_interval_token(
    raw: bytes,
    tokenizer: Mapping[str, Any],
    bindings: Mapping[int, Mapping[str, Any]],
    terminal_binding: Mapping[str, Any],
    ctx: i15.CertifiedDyadicContext,
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
        raise Pass215Iteration16ValidationError("PASS215_I16_INTERVAL_APPEND_CACHE_POSITION_INVALID")
    for block_index in i12.BLOCK_INDEXES:
        hidden = i15._interval_block(
            ctx,
            hidden,
            bindings[block_index],
            cache[block_index],
            block_index=block_index,
            position=absolute_position,
        )
    norm_weights = i7._norm_values(terminal_binding["output_norm"])
    normalized = i15._interval_rmsnorm(ctx, hidden, norm_weights)
    logits = i15._interval_q8_projection(ctx, terminal_binding["output_payload"], normalized)
    suite = _interval_suite(logits, bits=ctx.bits, step_index=next_step_index)
    return {
        "logits": logits,
        "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
        "prefix_recomputed": False,
        "cache_lengths_before": pre_lengths,
        "cache_lengths_after": {index: len(cache[index]["k_rope"]) for index in i12.BLOCK_INDEXES},
        **suite,
    }


def _append_symbolic_token(
    raw: bytes,
    tokenizer: Mapping[str, Any],
    bindings: Mapping[int, Mapping[str, Any]],
    terminal_binding: Mapping[str, Any],
    dag: Any,
    cache: MutableMapping[int, MutableMapping[str, list[tuple[str, ...]]]],
    *,
    token_id: int,
    selection_root_hash216: str,
    absolute_position: int,
    step_index: int,
) -> Mapping[str, Any]:
    embedding = i9._extract_authenticated_embeddings(raw, tokenizer, (int(token_id),))
    hidden = tuple(dag.q(numerator, denominator) for numerator, denominator in embedding["rows"][0])
    block_records: list[Mapping[str, Any]] = []
    for block_index in i12.BLOCK_INDEXES:
        current = i14._execute_incremental_block(
            dag,
            hidden,
            bindings[block_index],
            cache[block_index],
            block_index=block_index,
            absolute_position=absolute_position,
            append_index=step_index,
        )
        block_records.append({key: value for key, value in current.items() if key != "output_coordinate_roots"})
        hidden = current["output_coordinate_roots"]
    terminal = i14._terminal_generated_position(
        dag,
        hidden,
        terminal_binding,
        absolute_position=absolute_position,
        append_index=step_index,
    )
    payload = {
        "step_index": step_index,
        "absolute_position": absolute_position,
        "selected_token_id": int(token_id),
        "selection_root_hash216": selection_root_hash216,
        "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
        "block_forward_roots": [record["block_forward_root_hash216"] for record in block_records],
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logits_root_hash216": terminal["logits_root_hash216"],
    }
    i16_append_root = i4base.hash216(
        "pass215-i16-certified-greedy-append-forward", i4base.canonical_bytes(payload)
    )
    legacy_i15_root = None
    if step_index == 0:
        legacy_payload = {
            "absolute_position": absolute_position,
            "selected_token_id": int(token_id),
            "selection_root_hash216": selection_root_hash216,
            "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
            "block_forward_roots": [record["block_forward_root_hash216"] for record in block_records],
            "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
            "logits_root_hash216": terminal["logits_root_hash216"],
        }
        legacy_i15_root = i4base.hash216(
            "pass215-i15-certified-greedy-append-forward", i4base.canonical_bytes(legacy_payload)
        )
    return {
        "absolute_position": absolute_position,
        "appended_token_id": int(token_id),
        "appended_token": str(tokenizer["tokens"][int(token_id)]),
        "embedding_row_root_hash216": embedding["selected_tokens"][0]["embedding_row_root_hash216"],
        "block_records": block_records,
        "terminal_norm_root_hash216": terminal["terminal_norm_root_hash216"],
        "logit_roots": terminal["logit_roots"],
        "logits_root_hash216": terminal["logits_root_hash216"],
        "append_forward_root_hash216": i16_append_root,
        "iteration15_compatible_append_root_hash216": legacy_i15_root,
        "prefix_recomputed": False,
        "kv_cache_reused": True,
        "prefix_hidden_rows_recomputed": sum(int(r["prefix_hidden_rows_recomputed"]) for r in block_records),
        "prior_kv_token_rows_reused": sum(int(r["prior_kv_token_rows_reused"]) for r in block_records),
        "new_kv_token_rows_materialized": sum(int(r["new_kv_token_rows_materialized"]) for r in block_records),
        "projection_transition_work": terminal["projection_transition_work"],
    }


def build_multistep_certified_greedy_evidence(
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
        raise Pass215Iteration16ValidationError("PASS215_I16_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration16ValidationError("PASS215_I16_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT:
        raise Pass215Iteration16ValidationError("PASS215_I16_PROMPT_OUTSIDE_CONTRACT")
    if certification_bits != CERTIFICATION_BITS:
        raise Pass215Iteration16ValidationError("PASS215_I16_CERTIFICATION_BITS_OUTSIDE_CONTRACT")
    if greedy_steps != CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration16ValidationError("PASS215_I16_GREEDY_STEP_COUNT_OUTSIDE_CONTRACT")

    symbolic = i15._symbolic_prefix_and_logits(
        raw,
        filename=filename,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
    )
    prefix = symbolic["prefix"]
    tokenizer = symbolic["tokenizer"]
    bindings = symbolic["bindings"]
    terminal_binding = symbolic["terminal_binding"]
    dag = prefix["dag"]
    symbolic_cache = i14._materialize_prefix_kv_cache(dag, prefix, bindings)
    initial_node_count = int(dag.manifest()["unique_node_count"])
    if any(len(symbolic_cache[index]["k_rope"]) != PREFIX_SEQUENCE_LENGTH for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration16ValidationError("PASS215_I16_PREFIX_SYMBOLIC_CACHE_GEOMETRY_INVALID")

    interval = _initialize_interval_state(
        raw,
        tokenizer,
        bindings,
        terminal_binding,
        bits=certification_bits,
    )
    if interval["embedding_suite_root_hash216"] != i11.ITERATION10_EMBEDDING_ROOT_HASH216:
        raise Pass215Iteration16ValidationError("PASS215_I16_INTERVAL_EMBEDDING_ROOT_CHANGED")
    if interval["interval_suite_root_hash216"] != ITERATION15_INTERVAL_SUITE_ROOT_HASH216:
        raise Pass215Iteration16ValidationError("PASS215_I16_ITERATION15_INTERVAL_SUITE_NOT_REPRODUCED")

    current_interval_logits = interval["logits"]
    current_interval_suite_root = interval["interval_suite_root_hash216"]
    current_symbolic_logits = symbolic["final_position_symbolic_logits"]
    selected_from_position = PREFIX_SEQUENCE_LENGTH - 1
    steps: list[Mapping[str, Any]] = []

    for step_index in range(greedy_steps):
        selection = i15._certify_strict_argmax(
            current_interval_logits,
            symbolic_logit_roots=current_symbolic_logits,
            tokenizer=tokenizer,
            interval_suite_root_hash216=current_interval_suite_root,
            bits=certification_bits,
        )
        if step_index == 0:
            if int(selection["selected_token_id"]) != ITERATION15_SELECTED_TOKEN_ID:
                raise Pass215Iteration16ValidationError("PASS215_I16_ITERATION15_SELECTED_TOKEN_NOT_REPRODUCED")
            if selection["selected_symbolic_logit_root_hash216"] != ITERATION15_SELECTED_SYMBOLIC_LOGIT_ROOT_HASH216:
                raise Pass215Iteration16ValidationError("PASS215_I16_ITERATION15_SELECTED_LOGIT_ROOT_NOT_REPRODUCED")
            if selection["selection_root_hash216"] != ITERATION15_SELECTION_ROOT_HASH216:
                raise Pass215Iteration16ValidationError("PASS215_I16_ITERATION15_SELECTION_ROOT_NOT_REPRODUCED")

        token_id = int(selection["selected_token_id"])
        absolute_position = PREFIX_SEQUENCE_LENGTH + step_index
        symbolic_append = _append_symbolic_token(
            raw,
            tokenizer,
            bindings,
            terminal_binding,
            dag,
            symbolic_cache,
            token_id=token_id,
            selection_root_hash216=selection["selection_root_hash216"],
            absolute_position=absolute_position,
            step_index=step_index,
        )
        if symbolic_append["prefix_hidden_rows_recomputed"] != 0:
            raise Pass215Iteration16ValidationError("PASS215_I16_PREFIX_SYMBOLIC_ROWS_RECOMPUTED")
        if step_index == 0 and symbolic_append["iteration15_compatible_append_root_hash216"] != ITERATION15_APPEND_FORWARD_ROOT_HASH216:
            raise Pass215Iteration16ValidationError("PASS215_I16_ITERATION15_APPEND_ROOT_NOT_REPRODUCED")

        interval_append = _append_interval_token(
            raw,
            tokenizer,
            bindings,
            terminal_binding,
            interval["context"],
            interval["cache"],
            token_id=token_id,
            absolute_position=absolute_position,
            next_step_index=step_index + 1,
        )
        if interval_append["prefix_recomputed"] is not False:
            raise Pass215Iteration16ValidationError("PASS215_I16_INTERVAL_PREFIX_RECOMPUTED")

        step_payload = {
            "step_index": step_index,
            "selected_from_absolute_position": selected_from_position,
            "appended_at_absolute_position": absolute_position,
            "selected_token_id": token_id,
            "selection_root_hash216": selection["selection_root_hash216"],
            "source_interval_suite_root_hash216": current_interval_suite_root,
            "symbolic_append_root_hash216": symbolic_append["append_forward_root_hash216"],
            "produced_symbolic_logits_root_hash216": symbolic_append["logits_root_hash216"],
            "produced_interval_suite_root_hash216": interval_append["interval_suite_root_hash216"],
        }
        step_root = i4base.hash216(
            "pass215-i16-certified-greedy-step", i4base.canonical_bytes(step_payload)
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
            "source_interval_suite_root_hash216": current_interval_suite_root,
            "selection_root_hash216": selection["selection_root_hash216"],
            "symbolic_append": {key: value for key, value in symbolic_append.items() if key not in {"logit_roots", "block_records"}},
            "block_forward_roots": [record["block_forward_root_hash216"] for record in symbolic_append["block_records"]],
            "produced_interval_suite_root_hash216": interval_append["interval_suite_root_hash216"],
            "interval_cache_lengths_before": interval_append["cache_lengths_before"],
            "interval_cache_lengths_after": interval_append["cache_lengths_after"],
            "step_root_hash216": step_root,
        })
        current_symbolic_logits = symbolic_append["logit_roots"]
        current_interval_logits = interval_append["logits"]
        current_interval_suite_root = interval_append["interval_suite_root_hash216"]
        selected_from_position = absolute_position

    if len(steps) != CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration16ValidationError("PASS215_I16_STEP_COUNT_INVALID")
    final_node_count = int(dag.manifest()["unique_node_count"])
    final_cache_length = PREFIX_SEQUENCE_LENGTH + CERTIFIED_GREEDY_STEP_COUNT
    if any(len(symbolic_cache[index]["k_rope"]) != final_cache_length for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration16ValidationError("PASS215_I16_FINAL_SYMBOLIC_CACHE_GEOMETRY_INVALID")
    if any(len(interval["cache"][index]["k_rope"]) != final_cache_length for index in i12.BLOCK_INDEXES):
        raise Pass215Iteration16ValidationError("PASS215_I16_FINAL_INTERVAL_CACHE_GEOMETRY_INVALID")

    selected_ids = [int(step["selected_token_id"]) for step in steps]
    step_roots = [str(step["step_root_hash216"]) for step in steps]
    chain_payload = {
        "iteration15_evidence_root_hash216": ITERATION15_EVIDENCE_ROOT_HASH216,
        "selected_token_ids": selected_ids,
        "step_roots": step_roots,
        "final_symbolic_dag_root_hash216": dag.manifest()["ordered_node_root_hash216"],
        "final_interval_suite_root_hash216": current_interval_suite_root,
    }
    chain_root = i4base.hash216(
        "pass215-i16-multistep-certified-greedy-chain", i4base.canonical_bytes(chain_payload)
    )
    source_record = {
        **dict(source),
        "filename": filename,
        "file_size_bytes": len(raw),
        "file_sha256": actual_sha,
        "expected_sha256_verified": expected_sha256 is None or actual_sha == expected_sha256,
    }
    total_prior_reuse = sum(int(step["symbolic_append"]["prior_kv_token_rows_reused"]) for step in steps)
    total_new_kv = sum(int(step["symbolic_append"]["new_kv_token_rows_materialized"]) for step in steps)
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
            "bounded_multistep_true_greedy_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
        "inherits": {
            **_iteration15_bindings(),
            "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "source": source_record,
        "contracted_text_ingress": {
            "input_text": prompt,
            "token_ids": list(FROZEN_TOKEN_IDS),
            "prefix_sequence_length": PREFIX_SEQUENCE_LENGTH,
        },
        "iteration15_semantic_reproduction": {
            "exact": True,
            "selected_token_id": steps[0]["selected_token_id"],
            "selected_token": steps[0]["selected_token"],
            "source_interval_suite_root_hash216": steps[0]["source_interval_suite_root_hash216"],
            "selection_root_hash216": steps[0]["selection_root_hash216"],
            "iteration15_compatible_append_root_hash216": steps[0]["symbolic_append"]["iteration15_compatible_append_root_hash216"],
            **_iteration15_bindings(),
        },
        "multistep_certified_greedy": {
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
        "certified_interval_executor": interval["context"].manifest(),
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
        },
        "claims": {
            "authenticated_iteration15_roots_inherited_unchanged": True,
            "iteration15_true_argmax_reproduced_exactly": True,
            "three_consecutive_complete_logit_vectors_certified": True,
            "three_consecutive_true_logit_argmax_selections_executed": True,
            "three_consecutive_true_greedy_appends_executed": True,
            "prefix_state_reused_without_recomputation_after_initialization": True,
            "kv_cache_reused_across_all_greedy_steps": True,
            "bounded_multistep_generation_witness_executed": True,
            "hash_identity_order_used_as_greedy_authority": False,
            "probabilistic_sampling_executed": False,
            "unbounded_or_general_generation_claimed": False,
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
        "iteration15_suite_root_hash216": ITERATION15_SUITE_ROOT_HASH216,
        "step_roots": step_roots,
        "chain_root_hash216": chain_root,
        "final_interval_suite_root_hash216": current_interval_suite_root,
        "final_symbolic_dag_root_hash216": dag.manifest()["ordered_node_root_hash216"],
    }
    suite_root = i4base.hash216(
        "pass215-i16-multistep-certified-greedy-suite", i4base.canonical_bytes(suite_payload)
    )
    evidence["multistep_certified_greedy_suite_root_hash216"] = suite_root
    evidence_root = i4base.hash216(
        "pass215-i16-multistep-certified-greedy-evidence", i4base.canonical_bytes(evidence)
    )
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION16_MULTISTEP_CERTIFIED_GREEDY"},
        {
            "sequence": 16,
            "parent_hash72": ITERATION15_RECEIPT_HASH72,
            "evidence_root_hash216": evidence_root,
            "suite_root_hash216": suite_root,
            "chain_root_hash216": chain_root,
            "selected_token_ids": selected_ids,
        },
    )
    _reject_floats(evidence)
    return evidence


def build_multistep_certified_greedy_evidence_from_path(
    path: str | Path,
    *,
    source: Mapping[str, Any],
    prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None,
    certification_bits: int = CERTIFICATION_BITS,
    greedy_steps: int = CERTIFIED_GREEDY_STEP_COUNT,
) -> Mapping[str, Any]:
    source_path = Path(path)
    return build_multistep_certified_greedy_evidence(
        source_path.read_bytes(),
        filename=source_path.name,
        source=source,
        prompt=prompt,
        expected_sha256=expected_sha256,
        certification_bits=certification_bits,
        greedy_steps=greedy_steps,
    )


def validate_multistep_certified_greedy_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration16ValidationError("PASS215_I16_SCHEMA_OR_CONTRACT_INVALID")
    required_inherits = {
        **_iteration15_bindings(),
        "pass214_authority_root_hash216": i4base.PASS214_AUTHORITY_ROOT_HASH216,
        "pass215_benchmark_profile_root_hash216": i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
    }
    if evidence.get("inherits") != required_inherits:
        raise Pass215Iteration16ValidationError("PASS215_I16_INHERITANCE_INVALID")
    continuation = evidence.get("multistep_certified_greedy", {})
    steps = continuation.get("steps", [])
    if int(continuation.get("greedy_step_count", 0)) != CERTIFIED_GREEDY_STEP_COUNT or len(steps) != CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration16ValidationError("PASS215_I16_STEP_COUNT_INVALID")
    if int(steps[0].get("selected_token_id", -1)) != ITERATION15_SELECTED_TOKEN_ID:
        raise Pass215Iteration16ValidationError("PASS215_I16_PARENT_SELECTED_TOKEN_INVALID")
    if steps[0].get("selection_root_hash216") != ITERATION15_SELECTION_ROOT_HASH216:
        raise Pass215Iteration16ValidationError("PASS215_I16_PARENT_SELECTION_ROOT_INVALID")
    if steps[0].get("symbolic_append", {}).get("iteration15_compatible_append_root_hash216") != ITERATION15_APPEND_FORWARD_ROOT_HASH216:
        raise Pass215Iteration16ValidationError("PASS215_I16_PARENT_APPEND_ROOT_INVALID")
    for index, step in enumerate(steps):
        if int(step.get("step_index", -1)) != index:
            raise Pass215Iteration16ValidationError("PASS215_I16_STEP_INDEX_INVALID")
        if step.get("strict_interval_separation") is not True or step.get("certified_true_argmax") is not True:
            raise Pass215Iteration16ValidationError("PASS215_I16_STEP_ARGMAX_CERTIFICATE_MISSING")
        margin = step.get("strict_margin_lower_bound", {})
        if int(margin.get("numerator", 0)) <= 0 or int(margin.get("denominator", 0)) != 1 << CERTIFICATION_BITS:
            raise Pass215Iteration16ValidationError("PASS215_I16_STEP_MARGIN_INVALID")
        append = step.get("symbolic_append", {})
        if int(append.get("appended_token_id", -1)) != int(step.get("selected_token_id", -2)):
            raise Pass215Iteration16ValidationError("PASS215_I16_STEP_APPEND_TOKEN_MISMATCH")
        if append.get("prefix_recomputed") is not False or append.get("kv_cache_reused") is not True:
            raise Pass215Iteration16ValidationError("PASS215_I16_STEP_CACHE_REUSE_INVALID")
        if int(append.get("prefix_hidden_rows_recomputed", -1)) != 0:
            raise Pass215Iteration16ValidationError("PASS215_I16_STEP_PREFIX_RECOMPUTATION_INVALID")
    if int(continuation.get("prefix_replays_after_initialization", -1)) != 0:
        raise Pass215Iteration16ValidationError("PASS215_I16_PREFIX_REPLAY_INVALID")
    if int(continuation.get("final_cache_sequence_length", 0)) != PREFIX_SEQUENCE_LENGTH + CERTIFIED_GREEDY_STEP_COUNT:
        raise Pass215Iteration16ValidationError("PASS215_I16_FINAL_CACHE_LENGTH_INVALID")
    claims = evidence.get("claims", {})
    required_true = (
        "authenticated_iteration15_roots_inherited_unchanged",
        "iteration15_true_argmax_reproduced_exactly",
        "three_consecutive_complete_logit_vectors_certified",
        "three_consecutive_true_logit_argmax_selections_executed",
        "three_consecutive_true_greedy_appends_executed",
        "prefix_state_reused_without_recomputation_after_initialization",
        "kv_cache_reused_across_all_greedy_steps",
        "bounded_multistep_generation_witness_executed",
    )
    required_false = (
        "hash_identity_order_used_as_greedy_authority",
        "probabilistic_sampling_executed",
        "unbounded_or_general_generation_claimed",
        "general_arbitrary_sequence_length_transformer_forward_executed",
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
            raise Pass215Iteration16ValidationError(f"PASS215_I16_REQUIRED_CLAIM_FALSE:{key}")
    for key in required_false:
        if claims.get(key) is not False:
            raise Pass215Iteration16ValidationError(f"PASS215_I16_FORBIDDEN_CLAIM_TRUE:{key}")
    if evidence.get("authority", {}).get("no_float_canonical_authority") is not True:
        raise Pass215Iteration16ValidationError("PASS215_I16_NO_FLOAT_AUTHORITY_MISSING")


def compare_multistep_certified_greedy_replays(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_multistep_certified_greedy_evidence(left)
    validate_multistep_certified_greedy_evidence(right)
    keys = (
        "multistep_certified_greedy_suite_root_hash216",
        "evidence_root_hash216",
        "receipt_hash72",
    )
    mismatches = [key for key in keys if left.get(key) != right.get(key)]
    left_chain = left["multistep_certified_greedy"]
    right_chain = right["multistep_certified_greedy"]
    if left_chain.get("chain_root_hash216") != right_chain.get("chain_root_hash216"):
        mismatches.append("chain_root_hash216")
    if left_chain.get("selected_token_ids") != right_chain.get("selected_token_ids"):
        mismatches.append("selected_token_ids")
    if mismatches:
        raise Pass215Iteration16ValidationError("PASS215_I16_REPLAY_MISMATCH:" + ",".join(mismatches))
    return {
        "schema": REPLAY_SCHEMA,
        "contract": CONTRACT,
        "cross_process_replay": True,
        "semantic_exactness": True,
        "certified_step_count": CERTIFIED_GREEDY_STEP_COUNT,
        "selected_token_ids": list(left_chain["selected_token_ids"]),
        "chain_root_hash216": left_chain["chain_root_hash216"],
        "suite_root_hash216": left["multistep_certified_greedy_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"],
        "receipt_hash72": left["receipt_hash72"],
    }

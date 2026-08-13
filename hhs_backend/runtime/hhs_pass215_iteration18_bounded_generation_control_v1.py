"""Pass 215 Iteration 18 bounded certified generation-control authority.

Iteration 18 turns the frozen Iteration-17 seven-step certified witness into a
bounded generation-control surface with explicit termination policy, durable
cache-state checkpoints, zero-forward-replay restoration, and chained per-token
proof receipts. The authenticated workload remains deliberately bounded to the
same seven true-greedy tokens proven by Iteration 17.

A checkpoint serializes the symbolic DAG/hash-cons state, symbolic K/V cache,
certified interval K/V cache, current complete 32k interval logits, current
symbolic logit roots, scalable-RoPE dyadic context, generation policy, and proof
receipt chain. Restore recompiles immutable model bindings only; it does not
replay the prompt or any generated token forward transition.

No sampling, arbitrary prompt/model authority, unbounded generation, float
canonical authority, dense-forward replacement, runtime mutation, canonical
mutation, or migration is authorized.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from hhs_backend.runtime import hhs_pass215_iteration17_scalable_rope_certified_greedy_v1 as i17

CONTRACT = "HHS-P215-I18-BOUNDED-CERTIFIED-GENERATION-CONTROL"
PASS_NUMBER = 215
ITERATION = 18
EVIDENCE_SCHEMA = "HHS_PASS_215_ITERATION_18_BOUNDED_GENERATION_CONTROL_EVIDENCE_V1"
VALIDATION_SCHEMA = "HHS_PASS_215_ITERATION_18_BOUNDED_GENERATION_CONTROL_VALIDATION_V1"
REPLAY_SCHEMA = "HHS_PASS_215_ITERATION_18_BOUNDED_GENERATION_CONTROL_REPLAY_V1"
CHECKPOINT_SCHEMA = "HHS_PASS_215_ITERATION_18_GENERATION_CHECKPOINT_V1"
RUNTIME_CLASSIFICATION = "HHS_PASS_215_ITERATION_18_BOUNDED_GENERATION_CONTROL_BENCHMARK"

ITERATION17_CLOSURE_HEAD = "3d46b0eb233c6f450fa7d939e8b864a6651d3465"
ITERATION17_CLOSURE_TREE = "687db9f718d2b54c3962ecc8bbb62f49090407c9"
ITERATION17_CLOSURE_RUN = 31278114534
ITERATION17_CLOSURE_JOB = 93154902560
ITERATION17_CLOSURE_ARTIFACT_ID = 9027722990
ITERATION17_CLOSURE_ARTIFACT_SHA256 = "e8046bf49d280032a1f15f722de973d267b77e7f0d5e64338997e0a84a21a5af"
ITERATION17_SELECTED_TOKEN_IDS = (450, 6575, 471, 528, 2827, 322, 278)
ITERATION17_SELECTED_TOKENS = ("▁The", "▁sun", "▁was", "▁sh", "ining", "▁and", "▁the")
ITERATION17_SELECTION_ROOTS = (
    "aac3225975c44b9b761dd131afedfc01123a3c5da187f76bd9de5c9bf2abee94",
    "ba04d7c30b6734f7229d13e0684d7d9458803f4a5387c9c5547ef4f2d4e23050",
    "4043e960f6454b4ad0849b3997ddbbe8a5df5e92f827e8d70fcf424999bf7cba",
    "8dcd9c8a27e44e3c64f033ec92b54d7f9659acc7e188f7ebf2d55856a62e822a",
    "88fc594e0eded16e762d1641ed3246a68633c4dca7bb0056749068e46262410b",
    "7a4c232280dae7fee3ac22adab280e6daca259f07f152ca927287c529617cd54",
    "4acda044c1211ffa23a298e1a46ea24bdc55846909b4a229223b3dfdffceeb05",
)
ITERATION17_STEP_ROOTS = (
    "04f590fc90f78dc441a74a3989be770e356a9cda920230455dd2f271c05c32ca",
    "a93c05c11d7ce6df5fdf9b45ff9ac016fe1673f3b2162094a612530a8c118cf3",
    "4a97249f9358b8ba8c660a9c95331bcadd68951fb0c58f9e12be1af2333841da",
    "ff342ed47c71535192703c7dd8e3d521c4abd4c193300bc7e19eee3206304d30",
    "f666b2c134abf4bdad7313cdcb0721f27686e1c44ac2fdead3b582e8b78507d2",
    "8e3e6674e264b9292be0aef82d83b6039ba0406f382b633c7fd6f91e0db0e6cd",
    "9cb7f0bbb098005024ecd6ffac8d880df4b23cbd53047a940ff031b83f550d1e",
)
ITERATION17_CHAIN_ROOT_HASH216 = "87fe30aa3beed6c09ce724b1dfdfbf70c051cb636ab417eacea856bf50e6fc8e"
ITERATION17_FINAL_INTERVAL_SUITE_ROOT_HASH216 = "8150f402732b60a9f60b919f85facc0d24aa1c8f0d2c8756bd94369bde397b26"
ITERATION17_FINAL_SYMBOLIC_DAG_ROOT_HASH216 = "543d5327ba3970d9dd7353d37d49c8ca0a9cc50993e6af4ec2106d0bf364a9e2"
ITERATION17_SUITE_ROOT_HASH216 = "6ec09f1d71858d4483ae2f3fe120a7e0a03bd5946294200bd1d53eab1acef853"
ITERATION17_EVIDENCE_ROOT_HASH216 = "12a4b0154e4888ceb7cb6f2a5ea190b60b097dcac740fd1fd33e363c18d5eced"
ITERATION17_RECEIPT_HASH72 = "ViiSCwf9yz!wS!*YTzUniI!+Hn<7ia?r*I>bmCL1k<+mh?ky+<ypdrp7z1vjQVwGZz)qCFTW"

REAL_MODEL_SHA256 = i17.REAL_MODEL_SHA256
CONTRACTED_PROMPT = i17.CONTRACTED_PROMPT
FROZEN_TOKEN_IDS = i17.FROZEN_TOKEN_IDS
PREFIX_SEQUENCE_LENGTH = i17.PREFIX_SEQUENCE_LENGTH
VOCABULARY_SIZE = i17.VOCABULARY_SIZE
CERTIFICATION_BITS = i17.CERTIFICATION_BITS
MAX_NEW_TOKENS = 7
MAX_CONTEXT_TOKENS = PREFIX_SEQUENCE_LENGTH + MAX_NEW_TOKENS
RESUME_AFTER_STEPS = 4
DEFAULT_STOP_TOKEN_IDS = (2,)
TERMINATION_CONTINUE = "CONTINUE"
TERMINATION_STOP_TOKEN = "STOP_TOKEN"
TERMINATION_MAX_NEW_TOKENS = "MAX_NEW_TOKENS"
TERMINATION_CONTEXT_LIMIT = "CONTEXT_LIMIT"


class Pass215Iteration18Error(RuntimeError):
    pass


class Pass215Iteration18ValidationError(Pass215Iteration18Error):
    pass


def _reject_floats(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        raise Pass215Iteration18ValidationError(f"PASS215_I18_FLOAT_FORBIDDEN:{path}")
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_floats(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_floats(child, f"{path}[{index}]")


def _policy(*, max_new_tokens: int = MAX_NEW_TOKENS, stop_token_ids: Sequence[int] = DEFAULT_STOP_TOKEN_IDS) -> Mapping[str, Any]:
    max_new_tokens = int(max_new_tokens)
    stop_ids = tuple(int(value) for value in stop_token_ids)
    if max_new_tokens != MAX_NEW_TOKENS:
        raise Pass215Iteration18ValidationError("PASS215_I18_MAX_NEW_TOKENS_OUTSIDE_CONTRACT")
    if stop_ids != DEFAULT_STOP_TOKEN_IDS:
        raise Pass215Iteration18ValidationError("PASS215_I18_STOP_TOKEN_POLICY_OUTSIDE_CONTRACT")
    return {
        "selection_policy": i17.SELECTION_POLICY,
        "max_new_tokens": MAX_NEW_TOKENS,
        "max_context_tokens": MAX_CONTEXT_TOKENS,
        "stop_token_ids": list(DEFAULT_STOP_TOKEN_IDS),
        "stop_token_semantics": "APPEND_CERTIFIED_STOP_TOKEN_THEN_TERMINATE",
        "context_limit_semantics": "FAIL_CLOSED_BEFORE_APPEND_IF_NEXT_POSITION_EXCEEDS_BOUND",
        "sampling_authorized": False,
        "unbounded_generation_authorized": False,
    }


def evaluate_termination(selected_token_id: int, completed_steps: int, policy: Mapping[str, Any]) -> str:
    selected_token_id = int(selected_token_id)
    completed_steps = int(completed_steps)
    if selected_token_id in {int(value) for value in policy["stop_token_ids"]}:
        return TERMINATION_STOP_TOKEN
    if completed_steps >= int(policy["max_new_tokens"]):
        return TERMINATION_MAX_NEW_TOKENS
    if PREFIX_SEQUENCE_LENGTH + completed_steps >= int(policy["max_context_tokens"]):
        return TERMINATION_CONTEXT_LIMIT
    return TERMINATION_CONTINUE


def _serialize_symbolic_cache(cache: Mapping[int, Mapping[str, Sequence[Sequence[str]]]]) -> Mapping[str, Any]:
    return {
        str(index): {name: [list(vector) for vector in values] for name, values in block.items()}
        for index, block in cache.items()
    }


def _restore_symbolic_cache(payload: Mapping[str, Any]) -> MutableMapping[int, MutableMapping[str, list[tuple[str, ...]]]]:
    return {
        int(index): {name: [tuple(str(item) for item in vector) for vector in values] for name, values in block.items()}
        for index, block in payload.items()
    }


def _serialize_interval_cache(cache: Mapping[int, Mapping[str, Sequence[Sequence[tuple[int, int]]]]]) -> Mapping[str, Any]:
    return {
        str(index): {
            name: [[[int(interval[0]), int(interval[1])] for interval in vector] for vector in values]
            for name, values in block.items()
        }
        for index, block in cache.items()
    }


def _restore_interval_cache(payload: Mapping[str, Any]) -> MutableMapping[int, MutableMapping[str, list[tuple[tuple[int, int], ...]]]]:
    return {
        int(index): {
            name: [tuple((int(interval[0]), int(interval[1])) for interval in vector) for vector in values]
            for name, values in block.items()
        }
        for index, block in payload.items()
    }


def _serialize_context(ctx: i17.ScalableRopeCertifiedDyadicContext) -> Mapping[str, Any]:
    trig = []
    for (position, pair_index), (cosine, sine) in sorted(ctx._trig_cache.items()):
        trig.append({
            "position": int(position), "pair_index": int(pair_index),
            "cosine": [int(cosine[0]), int(cosine[1])],
            "sine": [int(sine[0]), int(sine[1])],
        })
    return {
        "bits": int(ctx.bits),
        "exp_calls": int(ctx.exp_calls), "sin_calls": int(ctx.sin_calls),
        "cos_calls": int(ctx.cos_calls), "rsqrt_calls": int(ctx.rsqrt_calls),
        "direct_rope_pair_calls": int(ctx.direct_rope_pair_calls),
        "range_reduced_rope_pair_calls": int(ctx.range_reduced_rope_pair_calls),
        "trig_halving_steps_total": int(ctx.trig_halving_steps_total),
        "trig_reconstruction_steps_total": int(ctx.trig_reconstruction_steps_total),
        "trig_max_halving_depth": int(ctx.trig_max_halving_depth),
        "range_reduced_positions": sorted(int(value) for value in ctx._range_reduced_positions),
        "trig_cache": trig,
    }


def _restore_context(payload: Mapping[str, Any]) -> i17.ScalableRopeCertifiedDyadicContext:
    ctx = i17.ScalableRopeCertifiedDyadicContext(int(payload["bits"]))
    for key in (
        "exp_calls", "sin_calls", "cos_calls", "rsqrt_calls", "direct_rope_pair_calls",
        "range_reduced_rope_pair_calls", "trig_halving_steps_total",
        "trig_reconstruction_steps_total", "trig_max_halving_depth",
    ):
        setattr(ctx, key, int(payload[key]))
    ctx._range_reduced_positions = {int(value) for value in payload["range_reduced_positions"]}
    ctx._trig_cache = {}
    for record in payload["trig_cache"]:
        ctx._trig_cache[(int(record["position"]), int(record["pair_index"]))] = (
            (int(record["cosine"][0]), int(record["cosine"][1])),
            (int(record["sine"][0]), int(record["sine"][1])),
        )
    return ctx


def _initialize_session(
    raw: bytes, *, filename: str, source: Mapping[str, Any], prompt: str,
    expected_sha256: str | None, certification_bits: int, policy: Mapping[str, Any],
) -> MutableMapping[str, Any]:
    _reject_floats(source)
    actual_sha = sha256(raw).hexdigest()
    if expected_sha256 is not None and actual_sha != expected_sha256:
        raise Pass215Iteration18ValidationError("PASS215_I18_SOURCE_SHA256_MISMATCH")
    if source.get("kind") == "public_open_transformer" and actual_sha != REAL_MODEL_SHA256:
        raise Pass215Iteration18ValidationError("PASS215_I18_AUTHENTICATED_MODEL_IDENTITY_MISMATCH")
    if prompt != CONTRACTED_PROMPT or certification_bits != CERTIFICATION_BITS:
        raise Pass215Iteration18ValidationError("PASS215_I18_INPUT_OUTSIDE_CONTRACT")
    symbolic = i17.i15._symbolic_prefix_and_logits(
        raw, filename=filename, source=source, prompt=prompt, expected_sha256=expected_sha256
    )
    prefix = symbolic["prefix"]
    dag = prefix["dag"]
    bindings = symbolic["bindings"]
    terminal_binding = symbolic["terminal_binding"]
    symbolic_cache = i17.i14._materialize_prefix_kv_cache(dag, prefix, bindings)
    interval = i17._initialize_interval_state(
        raw, symbolic["tokenizer"], bindings, terminal_binding, bits=certification_bits
    )
    if interval["interval_suite_root_hash216"] != i17.i16.ITERATION15_INTERVAL_SUITE_ROOT_HASH216:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_INITIAL_INTERVAL_ROOT_CHANGED")
    return {
        "filename": filename, "source": dict(source), "file_sha256": actual_sha,
        "tokenizer": symbolic["tokenizer"], "bindings": bindings, "terminal_binding": terminal_binding,
        "dag": dag, "symbolic_cache": symbolic_cache,
        "interval_context": interval["context"], "interval_cache": interval["cache"],
        "current_interval_logits": interval["logits"],
        "current_interval_suite_root": interval["interval_suite_root_hash216"],
        "current_symbolic_logits": symbolic["final_position_symbolic_logits"],
        "selected_from_position": PREFIX_SEQUENCE_LENGTH - 1,
        "source_state_range_reduced": False,
        "policy": dict(policy), "steps": [], "terminated": False,
        "termination_reason": TERMINATION_CONTINUE,
        "proof_parent_hash72": ITERATION17_RECEIPT_HASH72,
        "prefix_forward_replays_after_initialization": 0,
        "generated_forward_replays_after_initialization": 0,
        "resume_count": 0,
    }


def _advance_one(session: MutableMapping[str, Any], raw: bytes) -> Mapping[str, Any]:
    if session["terminated"]:
        raise Pass215Iteration18ValidationError("PASS215_I18_SESSION_ALREADY_TERMINATED")
    step_index = len(session["steps"])
    if step_index >= MAX_NEW_TOKENS:
        raise Pass215Iteration18ValidationError("PASS215_I18_STEP_BOUND_EXCEEDED")
    absolute_position = PREFIX_SEQUENCE_LENGTH + step_index
    if absolute_position >= int(session["policy"]["max_context_tokens"]):
        raise Pass215Iteration18ValidationError("PASS215_I18_CONTEXT_BOUND_EXCEEDED")
    selection = i17.i15._certify_strict_argmax(
        session["current_interval_logits"],
        symbolic_logit_roots=session["current_symbolic_logits"],
        tokenizer=session["tokenizer"],
        interval_suite_root_hash216=session["current_interval_suite_root"],
        bits=CERTIFICATION_BITS,
    )
    token_id = int(selection["selected_token_id"])
    if token_id != ITERATION17_SELECTED_TOKEN_IDS[step_index]:
        raise Pass215Iteration18ValidationError("PASS215_I18_ITERATION17_TOKEN_NOT_REPRODUCED")
    if selection["selection_root_hash216"] != ITERATION17_SELECTION_ROOTS[step_index]:
        raise Pass215Iteration18ValidationError("PASS215_I18_ITERATION17_SELECTION_ROOT_NOT_REPRODUCED")

    symbolic_append = i17.i16._append_symbolic_token(
        raw, session["tokenizer"], session["bindings"], session["terminal_binding"],
        session["dag"], session["symbolic_cache"], token_id=token_id,
        selection_root_hash216=selection["selection_root_hash216"],
        absolute_position=absolute_position, step_index=step_index,
    )
    interval_append = i17._append_interval_token(
        raw, session["tokenizer"], session["bindings"], session["terminal_binding"],
        session["interval_context"], session["interval_cache"], token_id=token_id,
        absolute_position=absolute_position, next_step_index=step_index + 1,
    )
    reduction_delta = interval_append["context_counter_delta"]
    append_used_range_reduction = int(reduction_delta["range_reduced_rope_pair_calls"]) > 0
    transition_root = i17._iteration16_compatible_transition_root(
        step_index=step_index,
        selected_from_position=int(session["selected_from_position"]),
        absolute_position=absolute_position, token_id=token_id,
        selection_root_hash216=selection["selection_root_hash216"],
        source_interval_suite_root_hash216=session["current_interval_suite_root"],
        symbolic_append=symbolic_append,
        produced_interval_suite_root_hash216=interval_append["interval_suite_root_hash216"],
    )
    i17_payload = {
        "step_index": step_index,
        "selected_from_absolute_position": int(session["selected_from_position"]),
        "appended_at_absolute_position": absolute_position,
        "selected_token_id": token_id,
        "selection_root_hash216": selection["selection_root_hash216"],
        "source_interval_suite_root_hash216": session["current_interval_suite_root"],
        "iteration16_compatible_transition_root_hash216": transition_root,
        "source_state_used_range_reduced_trig": bool(session["source_state_range_reduced"]),
        "append_used_range_reduced_trig": append_used_range_reduction,
        "produced_interval_suite_root_hash216": interval_append["interval_suite_root_hash216"],
    }
    i17_step_root = i17.i4base.hash216(
        "pass215-i17-scalable-rope-certified-greedy-step", i17.i4base.canonical_bytes(i17_payload)
    )
    if i17_step_root != ITERATION17_STEP_ROOTS[step_index]:
        raise Pass215Iteration18ValidationError("PASS215_I18_ITERATION17_STEP_ROOT_NOT_REPRODUCED")

    completed_steps = step_index + 1
    termination = evaluate_termination(token_id, completed_steps, session["policy"])
    proof_payload = {
        "step_index": step_index, "selected_token_id": token_id,
        "selection_root_hash216": selection["selection_root_hash216"],
        "iteration17_step_root_hash216": i17_step_root,
        "produced_interval_suite_root_hash216": interval_append["interval_suite_root_hash216"],
        "produced_symbolic_dag_root_hash216": session["dag"].manifest()["ordered_node_root_hash216"],
        "cache_sequence_length": PREFIX_SEQUENCE_LENGTH + completed_steps,
        "termination_decision": termination,
    }
    proof_root = i17.i4base.hash216(
        "pass215-i18-generation-token-proof", i17.i4base.canonical_bytes(proof_payload)
    )
    proof_receipt = i17.i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION18_TOKEN_PROOF"},
        {"sequence": 1801 + step_index, "parent_hash72": session["proof_parent_hash72"],
         "proof_root_hash216": proof_root, "step_index": step_index, "selected_token_id": token_id},
    )
    record = {
        **proof_payload,
        "selected_token": str(session["tokenizer"]["tokens"][token_id]),
        "strict_margin_lower_bound": selection["strict_margin_lower_bound"],
        "strict_interval_separation": True, "certified_true_argmax": True,
        "source_state_used_range_reduced_trig": bool(session["source_state_range_reduced"]),
        "append_used_range_reduced_trig": append_used_range_reduction,
        "symbolic_append_root_hash216": symbolic_append["append_forward_root_hash216"],
        "prior_kv_token_rows_reused": int(symbolic_append["prior_kv_token_rows_reused"]),
        "new_kv_token_rows_materialized": int(symbolic_append["new_kv_token_rows_materialized"]),
        "proof_root_hash216": proof_root, "proof_receipt_hash72": proof_receipt,
    }
    session["steps"].append(record)
    session["proof_parent_hash72"] = proof_receipt
    session["current_symbolic_logits"] = symbolic_append["logit_roots"]
    session["current_interval_logits"] = interval_append["logits"]
    session["current_interval_suite_root"] = interval_append["interval_suite_root_hash216"]
    session["selected_from_position"] = absolute_position
    session["source_state_range_reduced"] = append_used_range_reduction
    if termination != TERMINATION_CONTINUE:
        session["terminated"] = True
        session["termination_reason"] = termination
    return record


def snapshot_generation_session(session: Mapping[str, Any]) -> Mapping[str, Any]:
    dag = session["dag"]
    payload: dict[str, Any] = {
        "schema": CHECKPOINT_SCHEMA, "contract": CONTRACT,
        "file_sha256": session["file_sha256"], "filename": session["filename"],
        "source": dict(session["source"]), "policy": dict(session["policy"]),
        "completed_steps": len(session["steps"]), "steps": list(session["steps"]),
        "terminated": bool(session["terminated"]), "termination_reason": session["termination_reason"],
        "proof_parent_hash72": session["proof_parent_hash72"],
        "selected_from_position": int(session["selected_from_position"]),
        "source_state_range_reduced": bool(session["source_state_range_reduced"]),
        "current_interval_suite_root_hash216": session["current_interval_suite_root"],
        "current_interval_logits": [[int(v[0]), int(v[1])] for v in session["current_interval_logits"]],
        "current_symbolic_logits": list(session["current_symbolic_logits"]),
        "symbolic_dag": {
            "nodes": dict(dag._nodes), "order": list(dag._order),
            "histogram": {key: int(value) for key, value in dag._histogram.items()},
        },
        "symbolic_cache": _serialize_symbolic_cache(session["symbolic_cache"]),
        "interval_cache": _serialize_interval_cache(session["interval_cache"]),
        "interval_context": _serialize_context(session["interval_context"]),
        "prefix_forward_replays_after_initialization": int(session["prefix_forward_replays_after_initialization"]),
        "generated_forward_replays_after_initialization": int(session["generated_forward_replays_after_initialization"]),
        "resume_count": int(session["resume_count"]),
    }
    _reject_floats(payload)
    payload["checkpoint_root_hash216"] = i17.i4base.hash216(
        "pass215-i18-generation-checkpoint", i17.i4base.canonical_bytes(payload)
    )
    return payload


def restore_generation_session(raw: bytes, checkpoint: Mapping[str, Any]) -> MutableMapping[str, Any]:
    _reject_floats(checkpoint)
    if checkpoint.get("schema") != CHECKPOINT_SCHEMA or checkpoint.get("contract") != CONTRACT:
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_SCHEMA_INVALID")
    body = dict(checkpoint); root = body.pop("checkpoint_root_hash216", None)
    expected = i17.i4base.hash216("pass215-i18-generation-checkpoint", i17.i4base.canonical_bytes(body))
    if root != expected:
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_ROOT_INVALID")
    if sha256(raw).hexdigest() != checkpoint["file_sha256"]:
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_MODEL_MISMATCH")
    if checkpoint["policy"] != _policy():
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_POLICY_INVALID")

    dag = i17.i7.SymbolicDAG()
    dag._nodes = dict(checkpoint["symbolic_dag"]["nodes"])
    dag._order = [str(value) for value in checkpoint["symbolic_dag"]["order"]]
    dag._histogram = Counter({str(key): int(value) for key, value in checkpoint["symbolic_dag"]["histogram"].items()})
    tokenizer = i17.i9._read_tokenizer_metadata(raw)
    bindings = {index: i17.i11._bind_block_tensors(raw, index) for index in i17.i12.BLOCK_INDEXES}
    terminal_binding = i17.i15.i13._bind_terminal_tensors(raw, VOCABULARY_SIZE)
    if i17.i15.i13._q8_semantic_control(terminal_binding)["exact"] is not True:
        raise Pass215Iteration18ValidationError("PASS215_I18_RESUME_Q8_CONTROL_FAILED")
    completed = int(checkpoint["completed_steps"])
    expected_length = PREFIX_SEQUENCE_LENGTH + completed
    symbolic_cache = _restore_symbolic_cache(checkpoint["symbolic_cache"])
    interval_cache = _restore_interval_cache(checkpoint["interval_cache"])
    if any(len(symbolic_cache[index]["k_rope"]) != expected_length for index in i17.i12.BLOCK_INDEXES):
        raise Pass215Iteration18ValidationError("PASS215_I18_SYMBOLIC_CACHE_RESTORE_GEOMETRY_INVALID")
    if any(len(interval_cache[index]["k_rope"]) != expected_length for index in i17.i12.BLOCK_INDEXES):
        raise Pass215Iteration18ValidationError("PASS215_I18_INTERVAL_CACHE_RESTORE_GEOMETRY_INVALID")
    return {
        "filename": checkpoint["filename"], "source": dict(checkpoint["source"]),
        "file_sha256": checkpoint["file_sha256"], "tokenizer": tokenizer,
        "bindings": bindings, "terminal_binding": terminal_binding,
        "dag": dag, "symbolic_cache": symbolic_cache,
        "interval_context": _restore_context(checkpoint["interval_context"]),
        "interval_cache": interval_cache,
        "current_interval_logits": tuple((int(v[0]), int(v[1])) for v in checkpoint["current_interval_logits"]),
        "current_interval_suite_root": checkpoint["current_interval_suite_root_hash216"],
        "current_symbolic_logits": tuple(str(value) for value in checkpoint["current_symbolic_logits"]),
        "selected_from_position": int(checkpoint["selected_from_position"]),
        "source_state_range_reduced": bool(checkpoint["source_state_range_reduced"]),
        "policy": dict(checkpoint["policy"]), "steps": list(checkpoint["steps"]),
        "terminated": bool(checkpoint["terminated"]), "termination_reason": checkpoint["termination_reason"],
        "proof_parent_hash72": checkpoint["proof_parent_hash72"],
        "prefix_forward_replays_after_initialization": int(checkpoint["prefix_forward_replays_after_initialization"]),
        "generated_forward_replays_after_initialization": int(checkpoint["generated_forward_replays_after_initialization"]),
        "resume_count": int(checkpoint["resume_count"]) + 1,
    }


def _verify_iteration17_final_state(session: Mapping[str, Any]) -> None:
    if tuple(int(step["selected_token_id"]) for step in session["steps"]) != ITERATION17_SELECTED_TOKEN_IDS:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_TOKEN_CHAIN_INVALID")
    if tuple(step["iteration17_step_root_hash216"] for step in session["steps"]) != ITERATION17_STEP_ROOTS:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_STEP_ROOTS_INVALID")
    final_dag = session["dag"].manifest()["ordered_node_root_hash216"]
    if final_dag != ITERATION17_FINAL_SYMBOLIC_DAG_ROOT_HASH216:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_FINAL_DAG_INVALID")
    if session["current_interval_suite_root"] != ITERATION17_FINAL_INTERVAL_SUITE_ROOT_HASH216:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_FINAL_INTERVAL_INVALID")
    chain_payload = {
        "iteration16_evidence_root_hash216": i17.ITERATION16_EVIDENCE_ROOT_HASH216,
        "iteration16_chain_root_hash216": i17.ITERATION16_CHAIN_ROOT_HASH216,
        "selected_token_ids": list(ITERATION17_SELECTED_TOKEN_IDS),
        "step_roots": list(ITERATION17_STEP_ROOTS),
        "final_symbolic_dag_root_hash216": final_dag,
        "final_interval_suite_root_hash216": session["current_interval_suite_root"],
    }
    chain_root = i17.i4base.hash216(
        "pass215-i17-scalable-rope-certified-greedy-chain", i17.i4base.canonical_bytes(chain_payload)
    )
    if chain_root != ITERATION17_CHAIN_ROOT_HASH216:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_CHAIN_ROOT_INVALID")
    executor = session["interval_context"].manifest()
    suite_payload = {
        "iteration16_suite_root_hash216": i17.ITERATION16_SUITE_ROOT_HASH216,
        "step_roots": list(ITERATION17_STEP_ROOTS), "chain_root_hash216": chain_root,
        "final_interval_suite_root_hash216": session["current_interval_suite_root"],
        "final_symbolic_dag_root_hash216": final_dag,
        "range_reduced_positions": executor["range_reduced_positions"],
    }
    if i17.i4base.hash216("pass215-i17-scalable-rope-certified-greedy-suite", i17.i4base.canonical_bytes(suite_payload)) != ITERATION17_SUITE_ROOT_HASH216:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_SUITE_ROOT_INVALID")


def execute_bounded_generation_with_resume(
    raw: bytes, *, filename: str, source: Mapping[str, Any], prompt: str = CONTRACTED_PROMPT,
    expected_sha256: str | None = None, certification_bits: int = CERTIFICATION_BITS,
    max_new_tokens: int = MAX_NEW_TOKENS, stop_token_ids: Sequence[int] = DEFAULT_STOP_TOKEN_IDS,
    resume_after_steps: int = RESUME_AFTER_STEPS,
) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    if int(resume_after_steps) != RESUME_AFTER_STEPS:
        raise Pass215Iteration18ValidationError("PASS215_I18_RESUME_SPLIT_OUTSIDE_CONTRACT")
    policy = _policy(max_new_tokens=max_new_tokens, stop_token_ids=stop_token_ids)
    session = _initialize_session(
        raw, filename=filename, source=source, prompt=prompt,
        expected_sha256=expected_sha256, certification_bits=certification_bits, policy=policy,
    )
    while len(session["steps"]) < RESUME_AFTER_STEPS:
        _advance_one(session, raw)
    checkpoint = snapshot_generation_session(session)
    checkpoint_bytes = len(i17.i4base.canonical_bytes(checkpoint))
    session = restore_generation_session(raw, checkpoint)
    if session["prefix_forward_replays_after_initialization"] != 0 or session["generated_forward_replays_after_initialization"] != 0:
        raise Pass215Iteration18ValidationError("PASS215_I18_FORWARD_REPLAY_OCCURRED_DURING_RESTORE")
    while not session["terminated"]:
        _advance_one(session, raw)
    if len(session["steps"]) != MAX_NEW_TOKENS or session["termination_reason"] != TERMINATION_MAX_NEW_TOKENS:
        raise Pass215Iteration18ValidationError("PASS215_I18_TERMINATION_NOT_CONTRACTED")
    _verify_iteration17_final_state(session)

    step_proof_roots = [step["proof_root_hash216"] for step in session["steps"]]
    step_receipts = [step["proof_receipt_hash72"] for step in session["steps"]]
    control_payload = {
        "iteration17_chain_root_hash216": ITERATION17_CHAIN_ROOT_HASH216,
        "checkpoint_root_hash216": checkpoint["checkpoint_root_hash216"],
        "step_proof_roots": step_proof_roots,
        "step_receipts": step_receipts,
        "termination_reason": session["termination_reason"],
        "final_cache_sequence_length": MAX_CONTEXT_TOKENS,
    }
    control_root = i17.i4base.hash216(
        "pass215-i18-bounded-generation-control", i17.i4base.canonical_bytes(control_payload)
    )
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA, "contract": CONTRACT, "pass": PASS_NUMBER, "iteration": ITERATION,
        "runtime_classification": RUNTIME_CLASSIFICATION,
        "authority": {
            "pass215_benchmark_authority_active": True,
            "bounded_generation_control_authority": True,
            "durable_checkpoint_restore_authority": True,
            "no_float_canonical_authority": True,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False, "migration_active": False,
        },
        "inherits": {
            "iteration17_closure_head": ITERATION17_CLOSURE_HEAD,
            "iteration17_closure_tree": ITERATION17_CLOSURE_TREE,
            "iteration17_closure_run": ITERATION17_CLOSURE_RUN,
            "iteration17_closure_job": ITERATION17_CLOSURE_JOB,
            "iteration17_closure_artifact_id": ITERATION17_CLOSURE_ARTIFACT_ID,
            "iteration17_closure_artifact_sha256": ITERATION17_CLOSURE_ARTIFACT_SHA256,
            "iteration17_chain_root_hash216": ITERATION17_CHAIN_ROOT_HASH216,
            "iteration17_suite_root_hash216": ITERATION17_SUITE_ROOT_HASH216,
            "iteration17_evidence_root_hash216": ITERATION17_EVIDENCE_ROOT_HASH216,
            "iteration17_receipt_hash72": ITERATION17_RECEIPT_HASH72,
        },
        "source": {**dict(source), "filename": filename, "file_size_bytes": len(raw), "file_sha256": sha256(raw).hexdigest()},
        "generation_policy": policy,
        "resume_checkpoint": {
            "schema": CHECKPOINT_SCHEMA, "checkpoint_after_completed_steps": RESUME_AFTER_STEPS,
            "checkpoint_root_hash216": checkpoint["checkpoint_root_hash216"],
            "checkpoint_canonical_bytes": checkpoint_bytes,
            "symbolic_cache_sequence_length": PREFIX_SEQUENCE_LENGTH + RESUME_AFTER_STEPS,
            "interval_cache_sequence_length": PREFIX_SEQUENCE_LENGTH + RESUME_AFTER_STEPS,
            "complete_interval_logit_count": len(checkpoint["current_interval_logits"]),
            "complete_symbolic_logit_root_count": len(checkpoint["current_symbolic_logits"]),
            "resume_count": int(session["resume_count"]),
            "prefix_forward_replays_during_restore": 0,
            "generated_forward_replays_during_restore": 0,
        },
        "bounded_generation_control": {
            "completed_steps": len(session["steps"]),
            "selected_token_ids": [int(step["selected_token_id"]) for step in session["steps"]],
            "selected_tokens": [str(step["selected_token"]) for step in session["steps"]],
            "steps": list(session["steps"]),
            "termination_reason": session["termination_reason"],
            "final_cache_sequence_length": MAX_CONTEXT_TOKENS,
            "final_interval_suite_root_hash216": session["current_interval_suite_root"],
            "final_symbolic_dag_root_hash216": session["dag"].manifest()["ordered_node_root_hash216"],
            "generation_control_root_hash216": control_root,
            "per_token_proof_receipt_chain_terminal_hash72": session["proof_parent_hash72"],
        },
        "iteration17_semantic_reproduction": {
            "exact": True, "selected_token_ids": list(ITERATION17_SELECTED_TOKEN_IDS),
            "selection_roots": list(ITERATION17_SELECTION_ROOTS),
            "step_roots": list(ITERATION17_STEP_ROOTS),
            "chain_root_hash216": ITERATION17_CHAIN_ROOT_HASH216,
            "final_interval_suite_root_hash216": ITERATION17_FINAL_INTERVAL_SUITE_ROOT_HASH216,
            "final_symbolic_dag_root_hash216": ITERATION17_FINAL_SYMBOLIC_DAG_ROOT_HASH216,
            "suite_root_hash216": ITERATION17_SUITE_ROOT_HASH216,
        },
        "work_geometry": {
            "complete_vocabulary_certifications": MAX_NEW_TOKENS,
            "candidate_interval_comparisons": MAX_NEW_TOKENS * (VOCABULARY_SIZE - 1),
            "generation_forward_steps": MAX_NEW_TOKENS,
            "checkpoint_restore_model_binding_recompilation": True,
            "checkpoint_restore_prefix_forward_replays": 0,
            "checkpoint_restore_generated_forward_replays": 0,
            "complete_logit_vectors_persisted_in_checkpoint": 1,
            "symbolic_logit_root_vectors_persisted_in_checkpoint": 1,
        },
        "claims": {
            "authenticated_iteration17_roots_inherited_unchanged": True,
            "seven_step_iteration17_chain_reproduced_exactly": True,
            "bounded_generation_control_surface_executed": True,
            "deterministic_stop_token_policy_evaluated_each_step": True,
            "max_new_token_termination_executed": True,
            "context_window_limit_enforced": True,
            "durable_cache_checkpoint_serialized": True,
            "checkpoint_restored_without_prefix_forward_replay": True,
            "checkpoint_restored_without_generated_forward_replay": True,
            "per_token_hash216_proofs_emitted": True,
            "per_token_hash72_receipt_chain_emitted": True,
            "probabilistic_sampling_executed": False,
            "unbounded_or_general_generation_claimed": False,
            "arbitrary_prompt_or_model_generation_claimed": False,
            "canonical_float_interpretation_performed": False,
            "dense_forward_replaced": False,
            "runtime_mutation_authority_promoted": False,
            "canonical_mutation_authorized": False,
            "migration_active": False,
        },
    }
    suite_payload = {
        "iteration17_suite_root_hash216": ITERATION17_SUITE_ROOT_HASH216,
        "generation_control_root_hash216": control_root,
        "checkpoint_root_hash216": checkpoint["checkpoint_root_hash216"],
        "terminal_step_receipt_hash72": session["proof_parent_hash72"],
    }
    suite_root = i17.i4base.hash216("pass215-i18-bounded-generation-control-suite", i17.i4base.canonical_bytes(suite_payload))
    evidence["bounded_generation_control_suite_root_hash216"] = suite_root
    evidence_root = i17.i4base.hash216("pass215-i18-bounded-generation-control-evidence", i17.i4base.canonical_bytes(evidence))
    evidence["evidence_root_hash216"] = evidence_root
    evidence["receipt_hash72"] = i17.i4base.hash72_digest(
        {"contract": CONTRACT, "event": "PASS215_ITERATION18_BOUNDED_GENERATION_CONTROL"},
        {"sequence": 18, "parent_hash72": ITERATION17_RECEIPT_HASH72,
         "evidence_root_hash216": evidence_root, "suite_root_hash216": suite_root,
         "generation_control_root_hash216": control_root},
    )
    _reject_floats(evidence)
    return evidence, checkpoint


def execute_bounded_generation_with_resume_from_path(path: str | Path, **kwargs: Any) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    source_path = Path(path)
    return execute_bounded_generation_with_resume(source_path.read_bytes(), filename=source_path.name, **kwargs)


def validate_bounded_generation_control_evidence(evidence: Mapping[str, Any]) -> None:
    _reject_floats(evidence)
    if evidence.get("schema") != EVIDENCE_SCHEMA or evidence.get("contract") != CONTRACT:
        raise Pass215Iteration18ValidationError("PASS215_I18_SCHEMA_OR_CONTRACT_INVALID")
    control = evidence.get("bounded_generation_control", {})
    if tuple(control.get("selected_token_ids", [])) != ITERATION17_SELECTED_TOKEN_IDS:
        raise Pass215Iteration18ValidationError("PASS215_I18_SELECTED_CHAIN_INVALID")
    if control.get("termination_reason") != TERMINATION_MAX_NEW_TOKENS:
        raise Pass215Iteration18ValidationError("PASS215_I18_TERMINATION_INVALID")
    if int(control.get("final_cache_sequence_length", 0)) != MAX_CONTEXT_TOKENS:
        raise Pass215Iteration18ValidationError("PASS215_I18_FINAL_CACHE_LENGTH_INVALID")
    steps = control.get("steps", [])
    if len(steps) != MAX_NEW_TOKENS:
        raise Pass215Iteration18ValidationError("PASS215_I18_STEP_COUNT_INVALID")
    if tuple(step.get("iteration17_step_root_hash216") for step in steps) != ITERATION17_STEP_ROOTS:
        raise Pass215Iteration18ValidationError("PASS215_I18_ITERATION17_STEP_ROOTS_INVALID")
    if not all(step.get("certified_true_argmax") is True and step.get("strict_interval_separation") is True for step in steps):
        raise Pass215Iteration18ValidationError("PASS215_I18_ARGMAX_CERTIFICATE_INVALID")
    checkpoint = evidence.get("resume_checkpoint", {})
    if int(checkpoint.get("checkpoint_after_completed_steps", 0)) != RESUME_AFTER_STEPS:
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_SPLIT_INVALID")
    if int(checkpoint.get("prefix_forward_replays_during_restore", -1)) != 0 or int(checkpoint.get("generated_forward_replays_during_restore", -1)) != 0:
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_REPLAY_INVALID")
    if int(checkpoint.get("complete_interval_logit_count", 0)) != VOCABULARY_SIZE:
        raise Pass215Iteration18ValidationError("PASS215_I18_CHECKPOINT_INTERVAL_VECTOR_INVALID")
    reproduction = evidence.get("iteration17_semantic_reproduction", {})
    if reproduction.get("exact") is not True or reproduction.get("chain_root_hash216") != ITERATION17_CHAIN_ROOT_HASH216:
        raise Pass215Iteration18ValidationError("PASS215_I18_PARENT_REPRODUCTION_INVALID")
    claims = evidence.get("claims", {})
    for key in (
        "bounded_generation_control_surface_executed", "durable_cache_checkpoint_serialized",
        "checkpoint_restored_without_prefix_forward_replay", "checkpoint_restored_without_generated_forward_replay",
        "per_token_hash216_proofs_emitted", "per_token_hash72_receipt_chain_emitted",
    ):
        if claims.get(key) is not True:
            raise Pass215Iteration18ValidationError(f"PASS215_I18_REQUIRED_CLAIM_FALSE:{key}")
    for key in (
        "probabilistic_sampling_executed", "unbounded_or_general_generation_claimed",
        "arbitrary_prompt_or_model_generation_claimed", "canonical_float_interpretation_performed",
        "dense_forward_replaced", "runtime_mutation_authority_promoted", "canonical_mutation_authorized", "migration_active",
    ):
        if claims.get(key) is not False:
            raise Pass215Iteration18ValidationError(f"PASS215_I18_FORBIDDEN_CLAIM_TRUE:{key}")


def compare_bounded_generation_control_replays(left: Mapping[str, Any], right: Mapping[str, Any]) -> Mapping[str, Any]:
    validate_bounded_generation_control_evidence(left); validate_bounded_generation_control_evidence(right)
    keys = ("bounded_generation_control_suite_root_hash216", "evidence_root_hash216", "receipt_hash72")
    mismatches = [key for key in keys if left.get(key) != right.get(key)]
    lc, rc = left["bounded_generation_control"], right["bounded_generation_control"]
    for key in ("generation_control_root_hash216", "per_token_proof_receipt_chain_terminal_hash72", "selected_token_ids"):
        if lc.get(key) != rc.get(key): mismatches.append(key)
    if mismatches:
        raise Pass215Iteration18ValidationError("PASS215_I18_REPLAY_MISMATCH:" + ",".join(mismatches))
    return {
        "schema": REPLAY_SCHEMA, "contract": CONTRACT,
        "cross_process_replay": True, "semantic_exactness": True,
        "selected_token_ids": list(lc["selected_token_ids"]),
        "generation_control_root_hash216": lc["generation_control_root_hash216"],
        "checkpoint_root_hash216": left["resume_checkpoint"]["checkpoint_root_hash216"],
        "suite_root_hash216": left["bounded_generation_control_suite_root_hash216"],
        "evidence_root_hash216": left["evidence_root_hash216"], "receipt_hash72": left["receipt_hash72"],
    }

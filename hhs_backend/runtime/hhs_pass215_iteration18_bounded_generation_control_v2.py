"""Pass 215 Iteration 18 repair-forward: durable TerminalHeadSymbolicDAG restore.

The first Iteration-18 source execution correctly reached the checkpoint/restore
boundary but reconstructed the saved DAG as the older Iteration-7 SymbolicDAG.
That class cannot execute the inherited Iteration-8 RoPE powq/sin/cos nodes or
Iteration-13 Q8 terminal nodes. This repair restores the exact concrete
TerminalHeadSymbolicDAG used by the live Iteration-17 prefix and deliberately
round-trips checkpoint state through JSON before reconstruction.
"""
from __future__ import annotations

from collections import Counter
import json
from typing import Any, Mapping, MutableMapping

from hhs_backend.runtime import hhs_pass215_iteration18_bounded_generation_control_v1 as v1
from hhs_backend.runtime.hhs_pass215_iteration18_bounded_generation_control_v1 import *  # noqa: F401,F403


class Pass215Iteration18RestoreValidationError(v1.Pass215Iteration18ValidationError):
    pass


def _durable_json_roundtrip(checkpoint: Mapping[str, Any]) -> Mapping[str, Any]:
    v1._reject_floats(checkpoint)
    encoded = json.dumps(checkpoint, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    decoded = json.loads(encoded)
    v1._reject_floats(decoded)
    return decoded


def restore_generation_session(raw: bytes, checkpoint: Mapping[str, Any]) -> MutableMapping[str, Any]:
    checkpoint = _durable_json_roundtrip(checkpoint)
    if checkpoint.get("schema") != v1.CHECKPOINT_SCHEMA or checkpoint.get("contract") != v1.CONTRACT:
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_CHECKPOINT_SCHEMA_INVALID")
    body = dict(checkpoint)
    root = body.pop("checkpoint_root_hash216", None)
    expected = v1.i17.i4base.hash216(
        "pass215-i18-generation-checkpoint", v1.i17.i4base.canonical_bytes(body)
    )
    if root != expected:
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_CHECKPOINT_ROOT_INVALID")
    if v1.sha256(raw).hexdigest() != checkpoint["file_sha256"]:
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_CHECKPOINT_MODEL_MISMATCH")
    if checkpoint["policy"] != v1._policy():
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_CHECKPOINT_POLICY_INVALID")

    dag = v1.i17.i15.i13.TerminalHeadSymbolicDAG()
    dag._nodes = dict(checkpoint["symbolic_dag"]["nodes"])
    dag._order = [str(value) for value in checkpoint["symbolic_dag"]["order"]]
    dag._histogram = Counter(
        {str(key): int(value) for key, value in checkpoint["symbolic_dag"]["histogram"].items()}
    )
    if not all(hasattr(dag, name) for name in ("powq", "sin", "cos", "intern")):
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_RESTORED_DAG_CAPABILITY_INVALID")

    tokenizer = v1.i17.i9._read_tokenizer_metadata(raw)
    bindings = {
        index: v1.i17.i11._bind_block_tensors(raw, index)
        for index in v1.i17.i12.BLOCK_INDEXES
    }
    terminal_binding = v1.i17.i15.i13._bind_terminal_tensors(raw, v1.VOCABULARY_SIZE)
    if v1.i17.i15.i13._q8_semantic_control(terminal_binding)["exact"] is not True:
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_RESUME_Q8_CONTROL_FAILED")

    completed = int(checkpoint["completed_steps"])
    expected_length = v1.PREFIX_SEQUENCE_LENGTH + completed
    symbolic_cache = v1._restore_symbolic_cache(checkpoint["symbolic_cache"])
    interval_cache = v1._restore_interval_cache(checkpoint["interval_cache"])
    if any(
        len(symbolic_cache[index]["k_rope"]) != expected_length
        for index in v1.i17.i12.BLOCK_INDEXES
    ):
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_SYMBOLIC_CACHE_RESTORE_GEOMETRY_INVALID")
    if any(
        len(interval_cache[index]["k_rope"]) != expected_length
        for index in v1.i17.i12.BLOCK_INDEXES
    ):
        raise Pass215Iteration18RestoreValidationError("PASS215_I18_INTERVAL_CACHE_RESTORE_GEOMETRY_INVALID")

    return {
        "filename": checkpoint["filename"],
        "source": dict(checkpoint["source"]),
        "file_sha256": checkpoint["file_sha256"],
        "tokenizer": tokenizer,
        "bindings": bindings,
        "terminal_binding": terminal_binding,
        "dag": dag,
        "symbolic_cache": symbolic_cache,
        "interval_context": v1._restore_context(checkpoint["interval_context"]),
        "interval_cache": interval_cache,
        "current_interval_logits": tuple(
            (int(value[0]), int(value[1])) for value in checkpoint["current_interval_logits"]
        ),
        "current_interval_suite_root": checkpoint["current_interval_suite_root_hash216"],
        "current_symbolic_logits": tuple(str(value) for value in checkpoint["current_symbolic_logits"]),
        "selected_from_position": int(checkpoint["selected_from_position"]),
        "source_state_range_reduced": bool(checkpoint["source_state_range_reduced"]),
        "policy": dict(checkpoint["policy"]),
        "steps": list(checkpoint["steps"]),
        "terminated": bool(checkpoint["terminated"]),
        "termination_reason": checkpoint["termination_reason"],
        "proof_parent_hash72": checkpoint["proof_parent_hash72"],
        "prefix_forward_replays_after_initialization": int(
            checkpoint["prefix_forward_replays_after_initialization"]
        ),
        "generated_forward_replays_after_initialization": int(
            checkpoint["generated_forward_replays_after_initialization"]
        ),
        "resume_count": int(checkpoint["resume_count"]) + 1,
        "checkpoint_durable_json_roundtrip": True,
        "restored_symbolic_dag_class": "TerminalHeadSymbolicDAG",
    }


# The v1 execution loop resolves this name from the v1 module at runtime.
# Replace only the broken restore boundary; all generation/proof semantics remain v1.
v1.restore_generation_session = restore_generation_session

# Rebind public entrypoints explicitly for clarity.
execute_bounded_generation_with_resume = v1.execute_bounded_generation_with_resume
execute_bounded_generation_with_resume_from_path = v1.execute_bounded_generation_with_resume_from_path
validate_bounded_generation_control_evidence = v1.validate_bounded_generation_control_evidence
compare_bounded_generation_control_replays = v1.compare_bounded_generation_control_replays

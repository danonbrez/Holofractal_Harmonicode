from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hhs_backend.runtime import (
    hhs_pass215_iteration20_shared_checkpoint_terminal_v1 as i20,
)


def _synthetic_checkpoint(completed_steps: int, changed: str) -> dict[str, object]:
    body: dict[str, object] = {
        "schema": i20.i18.CHECKPOINT_SCHEMA,
        "contract": i20.i18.CONTRACT,
        "completed_steps": completed_steps,
        "file_sha256": "0" * 64,
        "steps": list(range(completed_steps)),
    }
    for name in i20.COMPONENT_NAMES:
        body[name] = {
            "payload": "A" * (2_300_000 if name == "symbolic_dag" else 1024),
            "changed": changed if name == "current_interval_logits" else "",
        }
    body["checkpoint_root_hash216"] = i20._hash216(
        "pass215-i18-generation-checkpoint", body
    )
    return body


@pytest.fixture(scope="module")
def synthetic_bundle():
    earlier = _synthetic_checkpoint(i20.EARLIER_CHECKPOINT_STEPS, "earlier")
    later = _synthetic_checkpoint(i20.LATER_CHECKPOINT_STEPS, "later")
    bundle, metrics = i20.build_shared_checkpoint_bundle((earlier, later))
    return earlier, later, bundle, metrics


def test_iteration19_exact_head_closure_is_frozen():
    assert i20.ITERATION19_CLOSURE_HEAD == "04745e6592f2d3bb8f227cc2dec61e25a66145d8"
    assert i20.ITERATION19_CLOSURE_TREE == "4fb5ead812c564b423f7a13155988e5384c53d0e"
    assert i20.ITERATION19_CLOSURE_RUN == 31288268305
    assert i20.ITERATION19_CLOSURE_JOB == 93180913426
    assert i20.ITERATION19_CLOSURE_ARTIFACT_ID == 9030733029


def test_iteration19_content_identities_are_frozen():
    assert i20.ITERATION19_COMPACT_CHECKPOINT_ROOT_HASH216 == "e45ffd5dc94d01b4461b65e8d940b53869676ea74e30b9b4f2d83b7d20a85630"
    assert i20.ITERATION19_CONTENT_STORE_ROOT_HASH216 == "a89677a460972945360e1a202b0ba2cf05a96b8a349427d9c03ba7298e043c06"
    assert i20.ITERATION19_SUITE_ROOT_HASH216 == "99d7efc2c94c0d721658d64a171d615d2f961cb442dd277fca91f78cb9e96e5b"
    assert i20.ITERATION19_EVIDENCE_ROOT_HASH216 == "3d35ca6574aa2dbb5d1b73988dd530cd2445e9d342e229afc40b8e5000323ddc"


def test_authenticated_workload_and_frozen_chain_are_unchanged():
    assert i20.REAL_MODEL_SHA256 == "6151b1929d7f5aa3385d9ddef3393e55587c0a55de661562322bc51dfda93a04"
    assert i20.CONTRACTED_PROMPT == "Hello world!"
    assert i20.FROZEN_SELECTED_TOKEN_IDS == (450, 6575, 471, 528, 2827, 322, 278)
    assert i20.FROZEN_SELECTED_TOKENS == ("▁The", "▁sun", "▁was", "▁sh", "ining", "▁and", "▁the")


def test_sequential_checkpoint_points_bind_iteration19_parent():
    assert i20.EARLIER_CHECKPOINT_STEPS == 3
    assert i20.LATER_CHECKPOINT_STEPS == 4
    assert i20.ITERATION18_STEP4_CHECKPOINT_ROOT_HASH216 == "bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f"


def test_content_defined_chunker_constants_are_integer_only():
    assert i20.CHUNK_MIN_BYTES == 262144
    assert i20.CHUNK_TARGET_BYTES == 1048576
    assert i20.CHUNK_MAX_BYTES == 2097152
    assert i20.CHUNK_TARGET_MASK == 1048575
    assert i20.ZLIB_LEVEL == 9
    assert len(i20.GEAR_TABLE) == 256
    assert all(isinstance(value, int) for value in i20.GEAR_TABLE)


def test_content_defined_chunking_is_deterministic_and_lossless():
    raw = (b"0123456789abcdef" * 200000) + b"tail"
    first = i20.content_defined_chunks(raw)
    second = i20.content_defined_chunks(raw)
    assert first == second
    assert b"".join(first) == raw
    assert all(0 < len(chunk) <= i20.CHUNK_MAX_BYTES for chunk in first)


def test_empty_component_has_one_addressable_chunk():
    assert i20.content_defined_chunks(b"") == (b"",)


def test_shared_bundle_reconstructs_both_parent_roots_exactly(synthetic_bundle):
    earlier, later, bundle, _ = synthetic_bundle
    assert i20.reconstruct_iteration18_checkpoint(bundle, 3) == earlier
    assert i20.reconstruct_iteration18_checkpoint(bundle, 4) == later


def test_shared_bundle_quantifies_positive_reuse_and_increment(synthetic_bundle):
    _, _, _, metrics = synthetic_bundle
    assert metrics["reused_unique_chunk_count"] > 0
    assert metrics["reused_compressed_blob_bytes"] > 0
    assert metrics["incremental_later_compressed_blob_bytes"] > 0
    assert metrics["incremental_later_compressed_blob_bytes"] < metrics["later_standalone_compressed_blob_bytes"]
    assert metrics["shared_store_savings_bytes"] == metrics["reused_compressed_blob_bytes"]


def test_shared_store_byte_accounting_is_exact(synthetic_bundle):
    _, _, _, metrics = synthetic_bundle
    assert metrics["shared_store_compressed_blob_bytes"] == (
        metrics["earlier_standalone_compressed_blob_bytes"]
        + metrics["incremental_later_compressed_blob_bytes"]
    )
    assert metrics["separate_stores_compressed_blob_bytes"] - metrics["shared_store_compressed_blob_bytes"] == metrics["shared_store_savings_bytes"]


def test_compressed_byte_metrics_are_derived_from_validated_payloads(synthetic_bundle):
    _, _, bundle, _ = synthetic_bundle
    tampered = copy.deepcopy(bundle)
    digest = next(iter(tampered["content_store"]["blobs"]))
    tampered["content_store"]["blobs"][digest]["compressed_bytes"] += 1
    with pytest.raises(
        i20.Pass215Iteration20ValidationError,
        match="COMPRESSED_BLOB_SIZE_INVALID",
    ):
        i20._reuse_metrics(
            tampered["checkpoint_manifests"],
            tampered["content_store"]["blobs"],
        )


def test_bundle_tamper_fails_closed(synthetic_bundle):
    _, _, bundle, _ = synthetic_bundle
    tampered = copy.deepcopy(bundle)
    digest = next(iter(tampered["content_store"]["blobs"]))
    tampered["content_store"]["blobs"][digest]["compressed_sha256"] = "f" * 64
    with pytest.raises(i20.Pass215Iteration20ValidationError, match="BUNDLE_ROOT_INVALID"):
        i20.reconstruct_iteration18_checkpoint(tampered, 3)


def test_float_is_rejected_recursively():
    with pytest.raises(i20.Pass215Iteration20ValidationError, match="FLOAT_FORBIDDEN"):
        i20._reject_floats({"bad": [1, 2.0]})


def test_frozen_source_evidence_recomputes_every_terminal_commitment():
    evidence = json.loads(
        Path("evidence/pass215/PASS_215_ITERATION_20_SOURCE_EVIDENCE.json").read_text()
    )
    i20.validate_shared_checkpoint_terminal_evidence(evidence)

    forged_root = copy.deepcopy(evidence)
    forged_root["evidence_root_hash216"] = "f" * 64
    with pytest.raises(
        i20.Pass215Iteration20ValidationError,
        match="EVIDENCE_COMMITMENT_INVALID",
    ):
        i20.validate_shared_checkpoint_terminal_evidence(forged_root)

    forged_receipt = copy.deepcopy(evidence)
    forged_receipt["receipt_hash72"] = "x" * 72
    with pytest.raises(
        i20.Pass215Iteration20ValidationError,
        match="RECEIPT_COMMITMENT_INVALID",
    ):
        i20.validate_shared_checkpoint_terminal_evidence(forged_receipt)

    forged_metrics = copy.deepcopy(evidence)
    forged_metrics["sequential_checkpoints"]["reuse_metrics"][
        "reused_unique_chunk_count"
    ] += 1
    with pytest.raises(
        i20.Pass215Iteration20ValidationError,
        match="REUSE_EVIDENCE_INVALID",
    ):
        i20.validate_shared_checkpoint_terminal_evidence(forged_metrics)


def test_runtime_restores_both_reconstructed_checkpoints_without_replay():
    text = Path("hhs_backend/runtime/hhs_pass215_iteration20_shared_checkpoint_terminal_v1.py").read_text()
    assert "i18.restore_generation_session(raw, reconstructed_earlier)" in text
    assert "i18.restore_generation_session(raw, reconstructed_later)" in text
    assert "FORWARD_REPLAY_DURING_" in text
    assert "_semantic_checkpoint_root(transition_checkpoint)" in text


def test_output_projection_pruning_is_evaluated_but_not_authorized():
    assert i20.OUTPUT_PROJECTION_PRUNING_STATUS == "EVALUATED_NOT_AUTHORIZED"
    contract = json.loads(Path("contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json").read_text())
    assessment = contract["output_projection_pruning_assessment"]
    assert assessment["complete_vocabulary_candidates"] == 32000
    assert assessment["candidates_pruned"] == 0
    assert assessment["strict_argmax_authority_preserved"] is True
    assert contract["constraints"]["output_projection_pruning_executed"] is False


def test_pass215_terminal_completion_is_bounded():
    contract = json.loads(Path("contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json").read_text())
    record = json.loads(Path("evidence/pass215/PASS_215_ITERATION_20_IMPLEMENTATION_RECORD.json").read_text())
    completion = contract["pass_completion"]
    assert completion["pass215_contracted_benchmark_implementation_complete"] is True
    assert completion["terminal_iteration"] == 20
    assert completion["bounded_profile_only"] is True
    assert completion["broader_generation_authority_promoted"] is False
    assert record["contract"] == contract["contract"]
    assert record["source_execution"] == contract["source_execution"]
    assert record["pass_completion"] == completion
    assert record["downstream_transition"] == contract["downstream_transition"]


def test_pass216_is_reserved_and_pass217_is_next():
    contract = json.loads(Path("contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json").read_text())
    transition = contract["downstream_transition"]
    assert i20.PASS216_STATUS == "RESERVED_NUMBER_NO_PASS"
    assert transition["pass216_status"] == i20.PASS216_STATUS
    assert transition["pass216_implementation_required"] is False
    assert transition["pass216_execution_required"] is False
    assert transition["pass216_artifacts_required"] is False
    assert transition["next_implemented_pass"] == 217


def test_contract_preserves_all_forbidden_authorities():
    contract = json.loads(Path("contracts/pass215/PASS_215_ITERATION_20_CONTRACT.json").read_text())
    constraints = contract["constraints"]
    for key in (
        "probabilistic_sampling_executed",
        "unbounded_or_general_generation_claimed",
        "arbitrary_prompt_or_model_generation_claimed",
        "canonical_float_interpretation_performed",
        "transport_compression_promoted_to_numerical_authority",
        "dense_forward_replaced",
        "runtime_mutation_authority_promoted",
        "canonical_mutation_authorized",
        "migration_active",
    ):
        assert constraints[key] is False


def test_tool_script_and_workflow_are_wired_to_iteration20():
    tool = Path("tools/pass215_iteration20_shared_checkpoint_terminal.py").read_text()
    script = Path("scripts/run_pass215_iteration20_validation.sh").read_text()
    workflow = Path(".github/workflows/pass215-iteration20-shared-checkpoint-terminal.yml")
    assert "hhs_pass215_iteration20_shared_checkpoint_terminal_v1" in tool
    assert "run_pass215_iteration19_validation.sh" in script
    assert "PASS215_ITERATION20_CUMULATIVE_TEST_COUNT" in script
    assert "IMPLEMENTATION_RECORD_SOURCE_INVALID" in script
    assert "PASS215_ITERATION20_VALIDATION_OK" in script
    assert workflow.exists()
    workflow_text = workflow.read_text()
    assert "hhs_backend/runtime/hhs_pass215_iteration*.py" in workflow_text
    assert "PASS215_I20_TEST_COUNT_FILE" in workflow_text

from __future__ import annotations

import copy

import pytest

from hhs_backend.runtime import hhs_pass215_iteration15_certified_greedy_logit_v1 as i15
from hhs_backend.runtime import hhs_pass215_iteration16_multistep_certified_greedy_v1 as i16


def test_parent_iteration15_closure_is_frozen() -> None:
    assert i16.ITERATION15_CLOSURE_HEAD == "7d58d29fa9690f4239b8e8f3ad30f34736f47f84"
    assert i16.ITERATION15_CLOSURE_TREE == "d556c1bb07e62cefba8f45df9c6cf8978645cdc8"
    assert i16.ITERATION15_SELECTED_TOKEN_ID == 450
    assert i16.ITERATION15_SELECTED_TOKEN == "▁The"
    assert i16.ITERATION15_SELECTION_ROOT_HASH216 == "aac3225975c44b9b761dd131afedfc01123a3c5da187f76bd9de5c9bf2abee94"
    assert i16.ITERATION15_APPEND_FORWARD_ROOT_HASH216 == "f1757269ee3ed98a67434c799a89750da26dcaa11be9ce688a093d52febb5a75"
    assert i16.ITERATION15_EVIDENCE_ROOT_HASH216 == "d04d5153a22883c01f1ac9f879ba46fa8afbebb4214692bf83e492091b5aca12"


def test_multistep_contract_is_strict_and_bounded() -> None:
    assert i16.CERTIFIED_GREEDY_STEP_COUNT == 3
    assert i16.CERTIFICATION_BITS == 256
    assert i16.SELECTION_POLICY == "STRICT_CERTIFIED_DYADIC_INTERVAL_ARGMAX_THEN_TOKEN_ID"
    assert i16.SELECTION_SEMANTICS == "TRUE_LOGIT_MAGNITUDE_ORDER_CERTIFIED_BY_OUTWARD_INTEGER_BOUNDS"


def test_iteration16_reuses_iteration15_certified_math() -> None:
    assert i16.i15.CertifiedDyadicContext is i15.CertifiedDyadicContext
    ctx = i16.i15.CertifiedDyadicContext(256)
    assert ctx.add(ctx.point(1, 3), ctx.point(2, 3))[0] <= 1 << 256
    assert ctx.add(ctx.point(1, 3), ctx.point(2, 3))[1] >= 1 << 256


def test_interval_suite_requires_complete_vocabulary() -> None:
    with pytest.raises(i16.Pass215Iteration16ValidationError, match="INTERVAL_SUITE_GEOMETRY"):
        i16._interval_suite(((0, 0),), bits=256, step_index=0)


def test_float_rejection_is_recursive() -> None:
    with pytest.raises(i16.Pass215Iteration16ValidationError, match="FLOAT_FORBIDDEN"):
        i16._reject_floats({"nested": [1, {"bad": 0.5}]})


def test_parent_bindings_include_terminal_artifact() -> None:
    bindings = i16._iteration15_bindings()
    assert bindings["iteration15_closure_artifact_sha256"] == "a00c444f8d71d8a1d0fe95d25d42849297487ff711a2829167de8022e697adac"
    assert bindings["iteration15_receipt_hash72"] == i16.ITERATION15_RECEIPT_HASH72


def _minimal_valid_evidence() -> dict:
    steps = []
    for index in range(3):
        steps.append({
            "step_index": index,
            "selected_token_id": 450 if index == 0 else 1 + index,
            "strict_interval_separation": True,
            "certified_true_argmax": True,
            "strict_margin_lower_bound": {"numerator": 1, "denominator": 1 << 256},
            "selection_root_hash216": i16.ITERATION15_SELECTION_ROOT_HASH216 if index == 0 else f"selection-{index}",
            "symbolic_append": {
                "appended_token_id": 450 if index == 0 else 1 + index,
                "iteration15_compatible_append_root_hash216": i16.ITERATION15_APPEND_FORWARD_ROOT_HASH216 if index == 0 else None,
                "prefix_recomputed": False,
                "kv_cache_reused": True,
                "prefix_hidden_rows_recomputed": 0,
            },
        })
    true_claims = {
        key: True for key in (
            "authenticated_iteration15_roots_inherited_unchanged",
            "iteration15_true_argmax_reproduced_exactly",
            "three_consecutive_complete_logit_vectors_certified",
            "three_consecutive_true_logit_argmax_selections_executed",
            "three_consecutive_true_greedy_appends_executed",
            "prefix_state_reused_without_recomputation_after_initialization",
            "kv_cache_reused_across_all_greedy_steps",
            "bounded_multistep_generation_witness_executed",
        )
    }
    false_claims = {
        key: False for key in (
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
    }
    return {
        "schema": i16.EVIDENCE_SCHEMA,
        "contract": i16.CONTRACT,
        "inherits": {
            **i16._iteration15_bindings(),
            "pass214_authority_root_hash216": i16.i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i16.i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "authority": {"no_float_canonical_authority": True},
        "multistep_certified_greedy": {
            "greedy_step_count": 3,
            "steps": steps,
            "prefix_replays_after_initialization": 0,
            "final_cache_sequence_length": i16.PREFIX_SEQUENCE_LENGTH + 3,
        },
        "claims": {**true_claims, **false_claims},
    }


def test_validator_accepts_structural_multistep_authority() -> None:
    i16.validate_multistep_certified_greedy_evidence(_minimal_valid_evidence())


def test_validator_rejects_nonpositive_certificate_margin() -> None:
    evidence = _minimal_valid_evidence()
    evidence["multistep_certified_greedy"]["steps"][1]["strict_margin_lower_bound"]["numerator"] = 0
    with pytest.raises(i16.Pass215Iteration16ValidationError, match="STEP_MARGIN_INVALID"):
        i16.validate_multistep_certified_greedy_evidence(evidence)


def test_validator_rejects_general_generation_claim() -> None:
    evidence = _minimal_valid_evidence()
    evidence["claims"]["unbounded_or_general_generation_claimed"] = True
    with pytest.raises(i16.Pass215Iteration16ValidationError, match="FORBIDDEN_CLAIM_TRUE"):
        i16.validate_multistep_certified_greedy_evidence(evidence)

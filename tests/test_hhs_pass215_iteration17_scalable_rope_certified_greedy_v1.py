from __future__ import annotations

import copy

import pytest

from hhs_backend.runtime import hhs_pass215_iteration16_multistep_certified_greedy_v1 as i16
from hhs_backend.runtime import hhs_pass215_iteration17_scalable_rope_certified_greedy_v1 as i17


def test_parent_iteration16_closure_is_frozen() -> None:
    assert i17.ITERATION16_CLOSURE_HEAD == "9eadb5ebbbad2283b3f19ccb7d2071a1a945e8c7"
    assert i17.ITERATION16_CLOSURE_TREE == "2c52b754b62931db1aa50926e8a35dae6ae0b4ac"
    assert i17.ITERATION16_GENERATED_TOKEN_IDS == (450, 6575, 471)
    assert i17.ITERATION16_CHAIN_ROOT_HASH216 == "28d8741be087bcb0ca6016ea7d88a24522408d965b9ee3198185dd93497f7448"
    assert i17.ITERATION16_CLOSURE_ARTIFACT_SHA256 == "2ef8d1061beb2cd48719973fefea881e2e64ff304ac3ed09db06d701659524ea"


def test_iteration17_contract_is_seven_steps_at_256_bits() -> None:
    assert i17.CERTIFIED_GREEDY_STEP_COUNT == 7
    assert i17.CERTIFICATION_BITS == 256
    assert i17.SELECTION_POLICY == i16.SELECTION_POLICY
    assert i17.SELECTION_SEMANTICS == i16.SELECTION_SEMANTICS
    assert i17.PI_APPROXIMATION_AUTHORIZED is False


def test_direct_rope_domain_is_iteration16_bit_compatible() -> None:
    old = i16.MultistepCertifiedDyadicContext(256)
    new = i17.ScalableRopeCertifiedDyadicContext(256)
    for position in (0, 1, 4, 8):
        for pair_index in (0, 1, 7, 15):
            assert new.rope_trig(position, pair_index) == old.rope_trig(position, pair_index)
    assert new.range_reduced_rope_pair_calls == 0


def test_scalable_rope_executes_beyond_iteration16_ceiling() -> None:
    ctx = i17.ScalableRopeCertifiedDyadicContext(256)
    cosine, sine = ctx.rope_trig(9, 0)
    assert ctx.range_reduced_rope_pair_calls == 1
    assert ctx.trig_halving_steps_total > 0
    assert ctx.trig_max_halving_depth > 0
    assert -ctx.scale <= cosine[0] <= cosine[1] <= ctx.scale
    assert -ctx.scale <= sine[0] <= sine[1] <= ctx.scale


def test_scalable_rope_has_no_small_fixed_position_ceiling() -> None:
    ctx = i17.ScalableRopeCertifiedDyadicContext(256)
    ctx.rope_trig(1 << 20, 0)
    manifest = ctx.manifest()
    assert manifest["fixed_rope_argument_ceiling"] is False
    assert manifest["range_reduced_rope_pair_calls"] == 1
    assert manifest["trig_max_halving_depth"] < i17.MAX_TRIG_HALVINGS
    assert manifest["pi_approximation_authorized"] is False


def test_interval_suite_requires_complete_vocabulary() -> None:
    with pytest.raises(i17.Pass215Iteration17ValidationError, match="INTERVAL_SUITE_GEOMETRY"):
        i17._interval_suite(((0, 0),), bits=256, step_index=4)


def test_float_rejection_is_recursive() -> None:
    with pytest.raises(i17.Pass215Iteration17ValidationError, match="FLOAT_FORBIDDEN"):
        i17._reject_floats({"nested": [1, {"bad": 0.5}]})


def test_parent_bindings_include_terminal_closure_artifact() -> None:
    bindings = i17._iteration16_bindings()
    assert bindings["iteration16_closure_artifact_id"] == 9026948113
    assert bindings["iteration16_receipt_hash72"] == i17.ITERATION16_RECEIPT_HASH72


def _minimal_valid_evidence() -> dict:
    steps = []
    for index in range(i17.CERTIFIED_GREEDY_STEP_COUNT):
        token_id = i17.ITERATION16_GENERATED_TOKEN_IDS[index] if index < 3 else 100 + index
        steps.append({
            "step_index": index,
            "selected_token_id": token_id,
            "strict_interval_separation": True,
            "certified_true_argmax": True,
            "strict_margin_lower_bound": {"numerator": 1, "denominator": 1 << 256},
            "selection_root_hash216": i17.ITERATION16_SELECTION_ROOTS[index] if index < 3 else f"selection-{index}",
            "iteration16_compatible_transition_root_hash216": i17.ITERATION16_TRANSITION_ROOTS[index] if index < 3 else f"transition-{index}",
            "source_state_used_range_reduced_trig": index == 6,
            "symbolic_append": {
                "appended_token_id": token_id,
                "prefix_recomputed": False,
                "kv_cache_reused": True,
                "prefix_hidden_rows_recomputed": 0,
            },
        })
    true_claims = {
        key: True for key in (
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
    }
    false_claims = {
        key: False for key in (
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
    }
    return {
        "schema": i17.EVIDENCE_SCHEMA,
        "contract": i17.CONTRACT,
        "inherits": {
            **i17._iteration16_bindings(),
            "pass214_authority_root_hash216": i17.i4base.PASS214_AUTHORITY_ROOT_HASH216,
            "pass215_benchmark_profile_root_hash216": i17.i4base.PASS215_BENCHMARK_PROFILE_ROOT_HASH216,
        },
        "authority": {"no_float_canonical_authority": True},
        "scalable_rope_certified_greedy": {
            "greedy_step_count": i17.CERTIFIED_GREEDY_STEP_COUNT,
            "steps": steps,
            "prefix_replays_after_initialization": 0,
            "final_cache_sequence_length": i17.PREFIX_SEQUENCE_LENGTH + i17.CERTIFIED_GREEDY_STEP_COUNT,
        },
        "certified_interval_executor": {
            "fixed_rope_argument_ceiling": False,
            "pi_approximation_authorized": False,
            "range_reduced_rope_pair_calls": 1,
        },
        "claims": {**true_claims, **false_claims},
    }


def test_validator_accepts_structural_scalable_rope_authority() -> None:
    i17.validate_scalable_rope_certified_greedy_evidence(_minimal_valid_evidence())


def test_validator_rejects_missing_range_reduced_selection() -> None:
    evidence = _minimal_valid_evidence()
    for step in evidence["scalable_rope_certified_greedy"]["steps"]:
        step["source_state_used_range_reduced_trig"] = False
    with pytest.raises(i17.Pass215Iteration17ValidationError, match="RANGE_REDUCED_SELECTION_MISSING"):
        i17.validate_scalable_rope_certified_greedy_evidence(evidence)


def test_validator_rejects_nonpositive_certificate_margin() -> None:
    evidence = _minimal_valid_evidence()
    evidence["scalable_rope_certified_greedy"]["steps"][4]["strict_margin_lower_bound"]["numerator"] = 0
    with pytest.raises(i17.Pass215Iteration17ValidationError, match="STEP_MARGIN_INVALID"):
        i17.validate_scalable_rope_certified_greedy_evidence(evidence)


def test_validator_rejects_general_generation_claim() -> None:
    evidence = _minimal_valid_evidence()
    evidence["claims"]["unbounded_or_general_generation_claimed"] = True
    with pytest.raises(i17.Pass215Iteration17ValidationError, match="FORBIDDEN_CLAIM_TRUE"):
        i17.validate_scalable_rope_certified_greedy_evidence(evidence)

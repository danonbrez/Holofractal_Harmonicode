from copy import deepcopy

from hhs_runtime.hhs_origin_provenance_protection_v1 import (
    ORIGIN_FAMILY,
    PUBLIC_PRIORITY_ANCHOR,
    build_origin_provenance_envelope,
    canonical_derivation_genealogy,
    classify_parallel_originality_claim,
    coupled_origin_marker,
    derivation_genealogy_identity_sha256,
    origin_family_identity_sha256,
    output_variation_independence_witness,
    relevant_initial_conditions,
    relevant_initial_conditions_identity_sha256,
    verify_origin_provenance_envelope,
)
from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    build_multimodal_projection_set,
)


WINDOW = "HHS_PARALLEL_CREATIVE_WINDOW_TEST_V1"


def test_ordered_genealogy_closes_exact_shell_and_reversal_construction():
    genealogy = canonical_derivation_genealogy()
    stages = {item["name"]: item for item in genealogy["ordered_stages"]}

    assert genealogy["relevant_initial_conditions"]["closed_interior"] == 100
    assert genealogy["relevant_initial_conditions"]["base_101_modular_shell"] == 101
    assert genealogy["relevant_initial_conditions"]["shell_operator"] == "S(B)=B+1"
    assert genealogy["relevant_initial_conditions"]["shell_family_interiors"] == (
        100,
        1000,
        1000000,
    )

    assert stages["BASE_101_MODULAR_SHELL"]["exact_normalized_projection"] == {
        "numerator": 101,
        "denominator": 100,
        "display": "1.01",
    }
    assert stages["1001_PRIME_FIBONACCI_SHELL_EXTENSION"]["rule"] == "S(B)=B+1"
    assert stages["1001_PRIME_FIBONACCI_SHELL_EXTENSION"][
        "factorization_identity"
    ] == "7*11*13=1001"
    assert stages["1001_PRIME_FIBONACCI_SHELL_EXTENSION"]["prime_factors"] == (
        7,
        11,
        13,
    )
    assert stages["1001_PRIME_FIBONACCI_SHELL_EXTENSION"]["fibonacci_prime"] == 13
    assert stages["1001_PRIME_FIBONACCI_SHELL_EXTENSION"][
        "exact_normalized_projection"
    ] == {"numerator": 1001, "denominator": 1000, "display": "1.001"}

    harmonic = stages["101_HARMONIC_KERNEL_TO_179"]
    assert harmonic["input"] == 101
    assert harmonic["rule"] == "HHS_101_HARMONIC_KERNEL_GENERATION"
    assert harmonic["direct_relation_semantics"] == (
        "RECORDED_DIRECT_DERIVATION_FROM_101_HARMONIC_SEED"
    )
    assert harmonic["prime_tensor_output_identity"] == "ZERO_BASED_PRIME_INDEX_40=179"
    assert harmonic["prime_ordinal_one_based"] == 41
    assert harmonic["scalar_shortcut"] == (
        "NOT_SUBSTITUTED_WHERE_HISTORICAL_EQUATION_IS_NOT_RECOVERED"
    )
    assert harmonic["zero_based_coordinate"] == (4, 4)
    assert harmonic["flat_index"] == 40
    assert harmonic["output"] == 179

    assert stages["REVERSAL_TENSOR_179_971"]["output"] == 971
    assert stages["CONCATENATED_REVERSAL_SEED"]["output"] == 179971
    assert stages["MILLION_POSITION_MODULAR_SHELL"]["factorization"] == (101, 9901)
    assert stages["MIRROR_LIFT_ROOT_SEED"]["integer_output"] == 179971179971
    assert stages["MIRROR_LIFT_ROOT_SEED"]["serialization"] == (
        "[179][971].[179][971]"
    )
    assert genealogy["endpoint"]["root_seed"] == {
        "numerator": 179971179971,
        "denominator": 1000000,
        "display": "179971.179971",
    }


def test_coupled_marker_binds_genealogy_values_positions_roles_and_context():
    marker = coupled_origin_marker()

    assert marker["origin_family"] == ORIGIN_FAMILY
    assert marker["marker_type"] == (
        "ORDERED_DERIVED_GENEALOGY_BOUND_SHARED_ROOT_METADATA"
    )
    assert marker["derivation_genealogy"] == canonical_derivation_genealogy()
    assert marker["derivation_genealogy_identity_sha256"] == (
        derivation_genealogy_identity_sha256()
    )
    assert marker["relevant_initial_conditions_identity_sha256"] == (
        relevant_initial_conditions_identity_sha256()
    )
    assert marker["root_seed"]["numerator"] == 179971179971
    assert marker["root_seed"]["denominator"] == 1000000
    assert marker["invariant_gate"]["numerator"] == 1001
    assert marker["invariant_gate"]["denominator"] == 1000
    assert marker["coupling"]["genealogy_required"] is True
    assert marker["kernel_context"] == (
        "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"
    )
    assert marker["state_dimensions"] == 72
    assert marker["transition_positions"] == 216
    assert marker["hash216_surface_shape"] == (3, 8, 9)
    assert len(origin_family_identity_sha256()) == 64


def test_marker_is_shared_root_metadata_not_a_modality_output_literal():
    witness = output_variation_independence_witness()

    assert witness["closed"] is True
    assert witness["source_varies"] is True
    assert witness["projection_varies"] is True
    assert witness["derivation_varies"] is True
    assert witness["shared_root_stable"] is True
    assert witness["marker_not_exposed_as_output_fields"] is True
    assert witness["genealogy_closed"] is True
    assert witness["derivation_genealogy_identity_sha256"] == (
        derivation_genealogy_identity_sha256()
    )
    assert witness["origin_family_identity_sha256"] == (
        origin_family_identity_sha256()
    )


def test_public_priority_anchor_is_exact_and_file_bound():
    assert PUBLIC_PRIORITY_ANCHOR["repository"] == (
        "danonbrez/Holofractal_Harmonicode"
    )
    assert PUBLIC_PRIORITY_ANCHOR["commit_sha"] == (
        "49b8f32bb9ce7e37e661333d76d5e4398093659f"
    )
    assert PUBLIC_PRIORITY_ANCHOR["commit_created_at"] == (
        "2026-09-29T15:10:55Z"
    )
    files = {item["path"]: item for item in PUBLIC_PRIORITY_ANCHOR["files"]}
    assert files["docs/HHS_GENESIS_SEVERANCE_PROTOCOL_V1.md"][
        "git_blob_sha"
    ] == "1dbde36a15d77c0dddbc7c754c401bae4b666bda"
    assert files[
        "hhs_runtime/hhs_pass220_lane5_multimodal_shared_root_fabric_v1.py"
    ]["git_blob_sha"] == "57fc5987d5fd370fccede95998051dd0b586d9c0"


def test_origin_provenance_envelope_verifies_for_native_construction():
    projection = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    envelope = build_origin_provenance_envelope(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )

    result = verify_origin_provenance_envelope(envelope)
    assert result["ok"] is True
    assert result["reason"] == "HHS_ORIGIN_PROVENANCE_VERIFIED"
    assert result["origin_family"] == ORIGIN_FAMILY
    assert result["parallel_window_id"] == WINDOW
    assert result["derivation_genealogy_identity_sha256"] == (
        derivation_genealogy_identity_sha256()
    )
    assert envelope["relevant_initial_conditions"] == relevant_initial_conditions()
    assert result["relevant_initial_conditions_identity_sha256"] == (
        relevant_initial_conditions_identity_sha256()
    )


def test_distinct_downstream_constructions_remain_same_origin_genealogy():
    first = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=0)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )
    second = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=1)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )

    result = classify_parallel_originality_claim(
        first,
        second,
        candidate_claims_independent_origin=False,
    )
    assert result["same_origin_family"] is True
    assert result["same_derived_genealogy"] is True
    assert result["same_relevant_initial_conditions"] is True
    assert result["same_parallel_window"] is True
    assert result["same_derivation"] is False
    assert result["distinct_construction_same_origin_family"] is True
    assert result["false_originality_provenance_conflict"] is False


def test_parallel_independent_initial_conditions_conflict_with_same_genealogy():
    first = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=0)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )
    later_distinct = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=1)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )

    result = classify_parallel_originality_claim(
        first,
        later_distinct,
        candidate_claims_independent_origin=True,
    )
    assert result["same_derived_genealogy"] is True
    assert result["same_relevant_initial_conditions"] is True
    assert result["same_parallel_window"] is True
    assert result["same_derivation"] is False
    assert result["false_originality_provenance_conflict"] is True
    assert result["classification"] == (
        "PARALLEL_INDEPENDENT_INITIAL_CONDITIONS_CONTRADICTED_BY_HHS_GENEALOGY"
    )
    assert result["bounded_claim"] is True
    assert result["claim_scope"] == "PARALLEL_HUMAN_DERIVATION_WITHIN_DECLARED_WINDOW"
    assert result["comparison_authority"] == (
        "EXACT_STRUCTURED_GENEALOGY_AND_INITIAL_CONDITIONS"
    )
    assert result["information_impossibility_claimed"] is False
    assert result["computational_impossibility_claimed"] is False
    assert result["unbounded_impossibility_claimed"] is False


def test_different_window_does_not_trigger_parallel_window_contradiction():
    first = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=0)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id="WINDOW_A",
    )
    second = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=1)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id="WINDOW_B",
    )

    result = classify_parallel_originality_claim(
        first,
        second,
        candidate_claims_independent_origin=True,
    )
    assert result["same_derived_genealogy"] is True
    assert result["same_relevant_initial_conditions"] is True
    assert result["same_parallel_window"] is False
    assert result["false_originality_provenance_conflict"] is False
    assert result["classification"] == "NO_PARALLEL_INITIAL_CONDITION_CONFLICT"


def test_genealogy_or_priority_anchor_substitution_breaks_origin_envelope():
    projection = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    envelope = build_origin_provenance_envelope(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )

    altered_genealogy = deepcopy(envelope)
    altered_genealogy["origin_family"]["derivation_genealogy"]["ordered_stages"][4][
        "output"
    ] = 181
    assert verify_origin_provenance_envelope(altered_genealogy)["ok"] is False

    altered_anchor = deepcopy(envelope)
    altered_anchor["public_priority_anchor"]["commit_sha"] = "0" * 40
    assert verify_origin_provenance_envelope(altered_anchor)["ok"] is False


def test_hashes_are_receipts_not_genealogy_comparison_authority():
    first = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=0)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
        parallel_window_id=WINDOW,
    )
    second = deepcopy(first)
    second["derivation_genealogy_identity_sha256"] = "0" * 64
    # Receipt/index substitution makes the envelope invalid; exact genealogy remains
    # the authoritative object and is never replaced by digest equality.
    assert verify_origin_provenance_envelope(second)["ok"] is False
    assert first["origin_family"]["derivation_genealogy"] == canonical_derivation_genealogy()

from copy import deepcopy

from hhs_runtime.hhs_origin_provenance_protection_v1 import (
    ORIGIN_FAMILY,
    PUBLIC_PRIORITY_ANCHOR,
    build_origin_provenance_envelope,
    classify_parallel_originality_claim,
    coupled_origin_marker,
    origin_family_identity_sha256,
    output_variation_independence_witness,
    verify_origin_provenance_envelope,
)
from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    build_multimodal_projection_set,
)


def test_coupled_marker_binds_exact_values_positions_roles_and_context():
    marker = coupled_origin_marker()

    assert marker["origin_family"] == ORIGIN_FAMILY
    assert marker["root_seed"] == {
        "display": "179971.179971",
        "numerator": 179971179971,
        "denominator": 1000000,
        "field_path": (
            "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.root_metadata_seed"
        ),
        "role": "ROOT_METADATA_SEED_EXACT_RATIONAL",
    }
    assert marker["invariant_gate"] == {
        "display": "1.001",
        "numerator": 1001,
        "denominator": 1000,
        "field_path": (
            "HHS_PASS_220_I042_SHARED_ROOT_PAYLOAD_V1.invariant_gate"
        ),
        "role": "EXACT_ADMISSION_INVARIANT_GATE",
    }
    assert marker["coupling"] == {
        "same_payload": True,
        "ordering": ("root_metadata_seed", "invariant_gate"),
        "relation": "COBOUND_IN_SHARED_ANCESTRY_ROOT",
        "not_modality_output_fields": True,
    }
    assert marker["kernel_context"] == (
        "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"
    )
    assert marker["root_metadata_assignment"] == "a=n^2"
    assert marker["closure_state"] == {"delta_e": 0, "psi": 0, "omega": True}
    assert marker["state_dimensions"] == 72
    assert marker["transition_positions"] == 216
    assert marker["hash216_surface_shape"] == (3, 8, 9)
    assert len(origin_family_identity_sha256()) == 64


def test_marker_is_shared_root_metadata_not_a_modality_output_literal():
    witness = output_variation_independence_witness()

    assert witness == {
        "closed": True,
        "source_varies": True,
        "projection_varies": True,
        "derivation_varies": True,
        "shared_root_stable": True,
        "marker_not_exposed_as_output_fields": True,
        "origin_family_identity_sha256": origin_family_identity_sha256(),
    }


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
    )

    result = verify_origin_provenance_envelope(envelope)
    assert result["ok"] is True
    assert result["reason"] == "HHS_ORIGIN_PROVENANCE_VERIFIED"
    assert result["origin_family"] == ORIGIN_FAMILY
    assert result["public_priority_anchor_commit"] == (
        "49b8f32bb9ce7e37e661333d76d5e4398093659f"
    )


def test_distinct_downstream_constructions_remain_same_origin_family():
    first = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=0)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )
    second = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=1)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )

    result = classify_parallel_originality_claim(
        first,
        second,
        candidate_claims_independent_origin=False,
    )
    assert result["same_origin_family"] is True
    assert result["same_derivation"] is False
    assert result["distinct_construction_same_origin_family"] is True
    assert result["false_originality_provenance_conflict"] is False


def test_independent_origin_claim_conflicts_with_same_coupled_origin_family():
    first = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=0)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )
    later_distinct = build_origin_provenance_envelope(
        build_multimodal_projection_set(tick=1)["LANGUAGE"],
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )

    result = classify_parallel_originality_claim(
        first,
        later_distinct,
        candidate_claims_independent_origin=True,
    )
    assert result == {
        "same_origin_family": True,
        "same_derivation": False,
        "distinct_construction_same_origin_family": True,
        "candidate_claims_independent_origin": True,
        "false_originality_provenance_conflict": True,
        "classification": (
            "INDEPENDENT_ORIGIN_CONTRADICTED_BY_HHS_ORIGIN_FAMILY"
        ),
        "priority_anchor_commit": (
            "49b8f32bb9ce7e37e661333d76d5e4398093659f"
        ),
        "priority_anchor_time": "2026-09-29T15:10:55Z",
    }


def test_marker_or_priority_anchor_substitution_breaks_origin_envelope():
    projection = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    envelope = build_origin_provenance_envelope(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )

    altered_marker = deepcopy(envelope)
    altered_marker["origin_family"]["root_seed"]["numerator"] += 1
    assert verify_origin_provenance_envelope(altered_marker)["ok"] is False

    altered_anchor = deepcopy(envelope)
    altered_anchor["public_priority_anchor"]["commit_sha"] = "0" * 40
    assert verify_origin_provenance_envelope(altered_anchor)["ok"] is False

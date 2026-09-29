from copy import deepcopy
import json

from hhs_runtime.hhs_pass220_lane5_multimodal_shared_root_fabric_v1 import (
    build_multimodal_projection_set,
)
from hhs_runtime.hhs_system_signature_watermark_v1 import (
    GENESIS_IDENTITY,
    ROOT_METADATA_ASSIGNMENT,
    SCHEMA,
    SHA256_TRANSITION_ARRAYS_PER_TICK,
    STATE_DIMENSIONS,
    canonical_bytes,
    compare_construction_derivations,
    derivation_identity,
    recognize_construction,
    system_standardization_payload,
    system_standardization_sha256,
    unwrap_recognized_construction,
    watermark_construction,
)


def test_standardization_binds_exact_system_tuple():
    payload = system_standardization_payload()

    assert payload["root_seed"] == {
        "numerator": 179971179971,
        "denominator": 1000000,
        "display": "179971.179971",
    }
    assert payload["kernel"] == (
        "F(x,y,a,b)=(x+y)^2+(xy-a^2)^2+(a^2-b)^2+(a^4-2)^2"
    )
    assert payload["kernel"] == GENESIS_IDENTITY
    assert payload["root_metadata_assignment"] == ROOT_METADATA_ASSIGNMENT == "a=n^2"
    assert payload["closure"] == {"delta_e": 0, "psi": 0, "omega": True}
    assert payload["topology"]["state_dimensions"] == STATE_DIMENSIONS == 72
    assert (
        payload["topology"]["sha256_transition_arrays_per_tick"]
        == SHA256_TRANSITION_ARRAYS_PER_TICK
        == 216
    )
    assert payload["topology"]["hash216_array_shape"] == (3, 8, 9)
    assert len(payload["topology"]["hash216_surface_root_sha256"]) == 64
    assert payload["invariant_gate"] == {
        "numerator": 1001,
        "denominator": 1000,
        "display": "1.001",
    }
    assert len(payload["shared_multimodal_root_sha256"]) == 64
    assert len(system_standardization_sha256()) == 64


def test_watermark_is_derivation_identity_not_post_hoc_tamper_seal():
    projection = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    envelope = watermark_construction(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )

    result = recognize_construction(envelope)
    assert result["recognized"] is True
    assert result["reason"] == "HHS_DERIVATION_RECOGNIZED"
    assert result["same_construction_requires_same_ancestry"] is True
    assert result["independent_parallel_same_construction"] is False

    semantics = envelope["watermark"]["formal_semantics"]
    assert semantics == {
        "same_construction": "EXACT_DERIVATION_IDENTITY_EQUALITY",
        "independent_parallel": "EXACT_DERIVATION_IDENTITY_INEQUALITY",
        "same_and_independent": False,
        "post_hoc_integrity_is_primary_purpose": False,
    }


def test_two_separate_constructor_executions_collapse_to_same_derivation_identity():
    first = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    second = build_multimodal_projection_set(tick=0)["LANGUAGE"]

    relation = compare_construction_derivations(first, second)

    assert first == second
    assert derivation_identity(first) == derivation_identity(second)
    assert relation["same_construction"] is True
    assert relation["same_derivation_identity"] is True
    assert relation["independent_parallel"] is False
    assert relation["same_and_independent"] is False
    assert relation["parallel_independent_same_construction"] is False


def test_different_valid_derivation_cannot_be_recognized_as_same_construction():
    first = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    alternate = build_multimodal_projection_set(tick=1)["LANGUAGE"]

    relation = compare_construction_derivations(first, alternate)

    assert relation["same_construction"] is False
    assert relation["same_derivation_identity"] is False
    assert relation["independent_parallel"] is True
    assert relation["same_and_independent"] is False
    assert relation["parallel_independent_same_construction"] is False

    first_envelope = watermark_construction(
        first,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )
    candidate = deepcopy(first_envelope)
    candidate["construction"] = alternate
    result = recognize_construction(candidate)

    assert result == {
        "recognized": False,
        "reason": "DERIVATION_IDENTITY_MISMATCH",
    }


def test_copying_same_exact_lineage_is_replay_not_independent_parallel_derivation():
    original = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    replay = json.loads(
        json.dumps(original, sort_keys=True, ensure_ascii=False)
    )

    relation = compare_construction_derivations(original, replay)

    assert canonical_bytes(original) == canonical_bytes(replay)
    assert relation["same_construction"] is True
    assert relation["same_derivation_identity"] is True
    assert relation["independent_parallel"] is False
    assert relation["parallel_independent_same_construction"] is False


def test_full_exact_lineage_tuple_is_authority_not_compact_hash_index():
    projection = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    envelope = watermark_construction(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )

    claimed = envelope["watermark"]["derivation_identity"]
    assert claimed == derivation_identity(projection)
    assert len(claimed["hash216_positions"]) == 216

    # Alter the full exact ancestry while leaving the compact index untouched.
    # Recognition must compare the exact tuple first and reject.
    candidate = deepcopy(envelope)
    candidate["watermark"]["derivation_identity"]["source_provenance"] += "_PARALLEL"
    result = recognize_construction(candidate)

    assert result == {
        "recognized": False,
        "reason": "DERIVATION_IDENTITY_MISMATCH",
    }


def test_recognized_construction_unwraps_to_same_exact_projection():
    projection = build_multimodal_projection_set(tick=0)["LANGUAGE"]
    envelope = watermark_construction(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )
    recovered = unwrap_recognized_construction(envelope)

    assert recovered == projection
    assert canonical_bytes(recovered) == canonical_bytes(projection)
    assert envelope["schema"] == SCHEMA

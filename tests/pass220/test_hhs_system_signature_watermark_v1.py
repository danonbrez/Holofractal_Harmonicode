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
    recognize_construction,
    system_standardization_payload,
    system_standardization_sha256,
    unwrap_recognized_construction,
    watermark_construction,
)


def test_standardization_signature_binds_exact_system_tuple():
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


def test_watermark_roundtrip_preserves_construction_without_drift():
    original = {
        "ordered": [1, 2, 3],
        "tensor": {"x": "i", "y": "-i", "phase": ("PREVIOUS", "CHANGE", "RECEIPT")},
        "closure": {"delta_e": 0, "psi": 0, "omega": True},
    }
    before = canonical_bytes(original)

    envelope = watermark_construction(
        original,
        construction_type="UNIT_EXACT_CONSTRUCTION",
    )
    recognized = recognize_construction(envelope)
    recovered = unwrap_recognized_construction(envelope)

    assert envelope["schema"] == SCHEMA
    assert recognized["recognized"] is True
    assert recognized["reason"] == "HHS_CONSTRUCTION_RECOGNIZED"
    assert recovered == original
    assert canonical_bytes(recovered) == before

    json_roundtrip = json.loads(
        json.dumps(envelope, sort_keys=True, ensure_ascii=False)
    )
    recognized_roundtrip = recognize_construction(json_roundtrip)
    assert recognized_roundtrip["recognized"] is True
    assert (
        recognized_roundtrip["signature_sha256"]
        == recognized["signature_sha256"]
    )


def test_watermark_recognizes_repository_native_multimodal_construction():
    projection = build_multimodal_projection_set()["LANGUAGE"]
    envelope = watermark_construction(
        projection,
        construction_type="PASS220_I042_LANGUAGE_PROJECTION",
    )
    result = recognize_construction(envelope)

    assert result["recognized"] is True
    assert result["construction_type"] == "PASS220_I042_LANGUAGE_PROJECTION"
    assert unwrap_recognized_construction(envelope) == projection


def test_any_construction_drift_is_rejected():
    original = {
        "state": [0, 1, 0, 1],
        "hash216": "A" * 216,
    }
    envelope = watermark_construction(original, construction_type="DRIFT_PROBE")

    tampered = deepcopy(envelope)
    tampered["construction"]["state"][2] = 1
    result = recognize_construction(tampered)
    assert result == {"recognized": False, "reason": "CONSTRUCTION_DRIFT"}


def test_any_standardization_or_signature_drift_is_rejected():
    envelope = watermark_construction(
        {"state": "nominal"},
        construction_type="STANDARDIZATION_PROBE",
    )

    tampered_seed = deepcopy(envelope)
    tampered_seed["watermark"]["standardization"]["root_seed"]["numerator"] += 1
    assert recognize_construction(tampered_seed) == {
        "recognized": False,
        "reason": "STANDARDIZATION_DRIFT",
    }

    tampered_kernel = deepcopy(envelope)
    tampered_kernel["watermark"]["standardization"]["kernel"] += " "
    assert recognize_construction(tampered_kernel) == {
        "recognized": False,
        "reason": "STANDARDIZATION_DRIFT",
    }

    tampered_topology = deepcopy(envelope)
    tampered_topology["watermark"]["standardization"]["topology"][
        "sha256_transition_arrays_per_tick"
    ] = 215
    assert recognize_construction(tampered_topology) == {
        "recognized": False,
        "reason": "STANDARDIZATION_DRIFT",
    }

    tampered_signature = deepcopy(envelope)
    tampered_signature["watermark"]["signature_sha256"] = "0" * 64
    assert recognize_construction(tampered_signature) == {
        "recognized": False,
        "reason": "SIGNATURE_DRIFT",
    }

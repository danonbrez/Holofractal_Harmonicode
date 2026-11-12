from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime.hhs_pass220_gfx4_decay_matrix_observation_v1 import (
    GFX4DecayObservationError,
    admit_decay_matrix_observation,
    decay_matrix_identity,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime


def _admit(vm81, matrix=b"\\x01\\x02\\x00\\xff", *, version=3):
    return admit_decay_matrix_observation(
        vm81=vm81,
        matrix_bytes=matrix,
        matrix_byte_length=4,
        matrix_version=version,
        scene_snapshot={"scene": "v147-test"},
        frame_state={"physics_tick": 9},
        resource_manifest={"format": "rgba8"},
        camera_state={"kind": "perspective"},
        frame_index=9,
        exact_time_num=9,
        exact_time_den=120,
    )


def test_admitted_matrix_version_and_content_are_part_of_native_gfx4_frame():
    vm81 = VMRCRuntime()
    before = vm81.epoch
    record = _admit(vm81)
    assert vm81.epoch == before + 1
    assert record["nativeAdmission"] is True
    assert record["matrixVersion"] == 3
    assert record["frameHash216"] == record["identity"]["frame_hash216"]
    assert record["decayHash216"] == record["observation"]["decay_hash216"]
    assert record["frame_state"]["decay_matrix_observation"] == record["observation"]
    assert record["witness"]["verified_live_vm81_commit"] is True
    assert record["witness"]["verified_vm81_replay"] is True
    assert record["witness"]["decay_matrix_binding_verified"] is False
    assert record["canonical_mutation_authority"] is False


def test_changed_ordered_bytes_change_native_matrix_identity():
    a = decay_matrix_identity(b"abcd", matrix_version=3, byte_length=4)
    b = decay_matrix_identity(b"abdc", matrix_version=3, byte_length=4)
    c = decay_matrix_identity(b"abcd", matrix_version=4, byte_length=4)
    assert a["decay_hash216"] != b["decay_hash216"]
    assert a["content_sha256"] != b["content_sha256"]
    assert a["decay_hash216"] != c["decay_hash216"]


def test_changed_matrix_bytes_change_admitted_frame_identity():
    a = _admit(VMRCRuntime(), b"abcd")
    b = _admit(VMRCRuntime(), b"abdc")
    assert a["frameHash216"] != b["frameHash216"]


@pytest.mark.parametrize("matrix,expected,version,diagnostic", [
    (b"abc", 4, 3, "FIXED_SIZE_MISMATCH"),
    (b"abcd", 0, 3, "FIXED_SIZE_REQUIRED"),
    ("abcd", 4, 3, "SERIALIZED_BYTES_REQUIRED"),
    (b"abcd", 4, 3.0, "EXACT_VERSION_REQUIRED"),
    (b"abcd", 4, -1, "EXACT_VERSION_REQUIRED"),
])
def test_invalid_decay_matrix_rejected_before_vm81_mutation(matrix, expected, version, diagnostic):
    vm81 = VMRCRuntime()
    with pytest.raises(GFX4DecayObservationError, match=diagnostic):
        admit_decay_matrix_observation(
            vm81=vm81, matrix_bytes=matrix,
            matrix_byte_length=expected, matrix_version=version,
            scene_snapshot={}, frame_state={}, resource_manifest={},
            camera_state={}, frame_index=1,
            exact_time_num=1, exact_time_den=120,
        )
    assert vm81.epoch == 0


def test_reserved_observation_field_cannot_be_overwritten():
    vm81 = VMRCRuntime()
    with pytest.raises(GFX4DecayObservationError, match="OBSERVATION_COLLISION"):
        admit_decay_matrix_observation(
            vm81=vm81, matrix_bytes=b"abcd", matrix_byte_length=4,
            matrix_version=3, scene_snapshot={},
            frame_state={"decay_matrix_observation": {"forged": True}},
            resource_manifest={}, camera_state={}, frame_index=1,
            exact_time_num=1, exact_time_den=120,
        )
    assert vm81.epoch == 0

from __future__ import annotations

from copy import deepcopy

import pytest

from hhs_runtime.hhs_pass220_gfx4_vm81_graphics_packet_identity_v1 import (
    build_vm81_admitted_graphics_packet_identity,
)
from hhs_runtime.hhs_pass220_gfx4_observation_witness_v1 import (
    GraphicsObservationWitnessError,
    verify_gfx4_vm81_observation_witness,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime


def _identity(vm81: VMRCRuntime):
    return build_vm81_admitted_graphics_packet_identity(
        vm81=vm81,
        scene_snapshot={"id": "pass220-observation"},
        frame_state={"tick": 1},
        resource_manifest={"texture": "native-rgba8"},
        camera_state={"phase": [0, 1]},
        frame_index=1,
        exact_time_num=1,
        exact_time_den=120,
    )


def test_live_native_gfx4_witness_matches_commit_journal_and_index():
    vm81 = VMRCRuntime()
    identity = _identity(vm81)
    witness = verify_gfx4_vm81_observation_witness(vm81=vm81, identity=identity)
    assert witness["verified_live_vm81_commit"] is True
    assert witness["verified_vm81_replay"] is True
    assert witness["epoch"] == vm81.epoch == 1
    assert witness["frame_hash216"] == identity["frame_hash216"]
    assert witness["vm81_receipt_hash72"] == identity["vm81_admission"]["receipt_hash72"]
    assert witness["canonical_mutation_authority"] is False
    assert witness["decay_matrix_binding_verified"] is False


def test_witness_rejects_other_vm81_runtime_without_matching_commit():
    source = VMRCRuntime()
    identity = _identity(source)
    with pytest.raises(GraphicsObservationWitnessError, match="COMMIT_NOT_FOUND"):
        verify_gfx4_vm81_observation_witness(vm81=VMRCRuntime(), identity=identity)


@pytest.mark.parametrize("key,value,diagnostic", [
    ("operation_hash216", "0" * 64, "LINEAGE_MISMATCH"),
    ("candidate_id", "forged", "LINEAGE_MISMATCH"),
    ("output_hash72", "0" * 72, "LINEAGE_MISMATCH"),
    ("epoch_after", 10, "EPOCH_INVALID"),
    ("capability_scope", "OTHER_SCOPE", "SCOPE_MISMATCH"),
])
def test_witness_rejects_forged_admission_fields(key, value, diagnostic):
    vm81 = VMRCRuntime()
    altered = deepcopy(_identity(vm81))
    altered["vm81_admission"][key] = value
    with pytest.raises(GraphicsObservationWitnessError, match=diagnostic):
        verify_gfx4_vm81_observation_witness(vm81=vm81, identity=altered)


def test_witness_rejects_client_claim_without_live_vm81():
    vm81 = VMRCRuntime()
    identity = _identity(vm81)
    identity["packet_identity_vm81_admitted"] = False
    with pytest.raises(GraphicsObservationWitnessError, match="ADMISSION_REQUIRED"):
        verify_gfx4_vm81_observation_witness(vm81=vm81, identity=identity)

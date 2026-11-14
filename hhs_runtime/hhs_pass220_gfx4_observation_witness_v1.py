"""Read-only witness lookup for Pass 220 GFX4 VM81-admitted graphics frames.

This module is deliberately *not* an independent receipt service. It checks a
GFX4 identity returned by the inherited native constructor against the live
VMRC journal/index and its replay status. The caller must supply the existing
VMRCRuntime, not a new runtime or a browser-provided admission flag.

The decay-matrix authority binding is a separate unresolved interface: no
decay-matrix hash is invented by this projection verifier.
"""
from __future__ import annotations

from typing import Any, Mapping

from hhs_runtime.hhs_pass220_gfx4_vm81_graphics_packet_identity_v1 import (
    CLASSIFICATION,
    CAPABILITY_SCOPE,
    THREAD,
    packet_identity_bytes,
)
from hhs_runtime.pass163.vmrc import VMRCRuntime

SCHEMA = "HHS_PASS_220_GFX4_VM81_OBSERVATION_WITNESS_V1"


class GraphicsObservationWitnessError(ValueError):
    pass


def verify_gfx4_vm81_observation_witness(
    *,
    vm81: VMRCRuntime,
    identity: Mapping[str, Any],
) -> dict[str, Any]:
    """Verify an admitted GFX4 identity against one *live* VM81 ledger.

    Read-only. Only confirms committed source/journal/index lineage for the
    provided GFX4 identity; it does NOT prove an external decay-matrix binding,
    independently recreate a historical receipt, or authorize WebGL mutation.
    """
    if not isinstance(vm81, VMRCRuntime):
        raise GraphicsObservationWitnessError("P220_OBS_INHERITED_VM81_REQUIRED")
    if not isinstance(identity, Mapping):
        raise GraphicsObservationWitnessError("P220_OBS_IDENTITY_REQUIRED")
    if identity.get("classification") != CLASSIFICATION:
        raise GraphicsObservationWitnessError("P220_OBS_GFX4_CLASSIFICATION_INVALID")
    if identity.get("packet_identity_vm81_admitted") is not True:
        raise GraphicsObservationWitnessError("P220_OBS_GFX4_ADMISSION_REQUIRED")
    if identity.get("singleton_vm81_authority") is not True:
        raise GraphicsObservationWitnessError("P220_OBS_SINGLETON_VM81_REQUIRED")
    if identity.get("packet_compatibility_unadmitted") is not False:
        raise GraphicsObservationWitnessError("P220_OBS_COMPATIBILITY_PACKET_REJECTED")
    if identity.get("gpu_or_renderer_mutation_authority") is not False:
        raise GraphicsObservationWitnessError("P220_OBS_GPU_AUTHORITY_REJECTED")

    # Use the existing constructor's lane-shape validator, never a new hash
    # constructor. This is structure checking, not a proof of admission.
    packet_identity_bytes(identity)
    admission = identity.get("vm81_admission")
    if not isinstance(admission, Mapping):
        raise GraphicsObservationWitnessError("P220_OBS_VM81_RECEIPT_REQUIRED")
    epoch = admission.get("epoch_after")
    before = admission.get("epoch_before")
    if (type(epoch) is not int or type(before) is not int or
            epoch != before + 1 or epoch <= 0):
        raise GraphicsObservationWitnessError("P220_OBS_VM81_EPOCH_INVALID")
    if admission.get("capability_scope") != CAPABILITY_SCOPE:
        raise GraphicsObservationWitnessError("P220_OBS_SCOPE_MISMATCH")
    if (not isinstance(admission.get("receipt_hash72"), str) or
            len(admission["receipt_hash72"]) != 72):
        raise GraphicsObservationWitnessError("P220_OBS_RECEIPT_HASH72_INVALID")

    # The live VM81 replay validates the journal chain and canonical replay,
    # not any browser-local reconstruction or shadow Hash216 state.
    replay = vm81.replay()
    if replay.get("deterministic_replay") is not True:
        raise GraphicsObservationWitnessError("P220_OBS_VM81_REPLAY_FAILED")

    records = [
        x for x in vm81.index_records()
        if x.get("record_class") == "COMMITTED_TRANSITION"
        and x.get("epoch") == epoch
    ]
    events = [
        x for x in vm81.journal()
        if x.get("event") == "COMMIT"
        and x.get("epoch_after") == epoch
    ]
    if len(records) != 1 or len(events) != 1:
        raise GraphicsObservationWitnessError("P220_OBS_VM81_COMMIT_NOT_FOUND")
    record, event = records[0], events[0]
    candidate = event.get("candidate") or {}
    matches = (
        record.get("thread") == THREAD
        and candidate.get("thread") == THREAD
        and record.get("capability_scope") == CAPABILITY_SCOPE
        and candidate.get("capability_scope") == CAPABILITY_SCOPE
        and record.get("journal_hash") == event.get("journal_hash")
        and record.get("hash216_operation_identity") == admission.get("operation_hash216")
        and event.get("operation_hash216") == admission.get("operation_hash216")
        and event.get("input_hash72") == admission.get("input_hash72")
        and event.get("output_hash72") == admission.get("output_hash72")
        and record.get("hash72_state_identity") == admission.get("output_hash72")
        and candidate.get("candidate_id") == admission.get("candidate_id")
        and before == epoch - 1
    )
    if not matches:
        raise GraphicsObservationWitnessError("P220_OBS_VM81_LINEAGE_MISMATCH")
    return {
        "schema": SCHEMA,
        "verified_live_vm81_commit": True,
        "verified_vm81_replay": True,
        "epoch": epoch,
        "frame_hash216": identity["frame_hash216"],
        "vm81_receipt_hash72": admission["receipt_hash72"],
        "journal_hash": event["journal_hash"],
        "index_head_hash216": record["index_head_hash216"],
        "canonical_mutation_authority": False,
        "decay_matrix_binding_verified": False,
    }

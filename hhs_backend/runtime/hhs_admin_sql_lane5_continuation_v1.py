"""Candidate-only Lane 5 continuation of administrator SQL-staged source objects.

Uses the EXISTING Pass 219 unbounded native workload bridge, not a new
VM81 frame engine or separate ingestion runtime. Byte framing is 648 bytes
(81 cells * 64 bits); no whole-file size or modality eligibility limit.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Callable

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging, StagingError
from hhs_python.runtime.hhs_pass219_lane5_unbounded_workload_scaling_bridge import (
    FULL_MANIFOLD_MODULUS,
    Lane5RouteCandidate,
    Lane5WorkloadEnvelope,
    Pass219Lane5UnboundedWorkloadBridge,
)

VM81_FRAME_BYTES = 81 * 64 // 8
_FORBIDDEN = sha256(b"HHS-LANE5-HOST-INGRESS-FORBIDDEN-BOUNDARY-V1").digest()


class NativeContinuationError(RuntimeError):
    pass


def _address(label: bytes, digest: bytes) -> int:
    return int.from_bytes(sha256(label + b"\0" + digest).digest(), "big") % FULL_MANIFOLD_MODULUS


def _candidate(digest: bytes) -> Lane5RouteCandidate:
    return Lane5RouteCandidate(
        route_witness_sha256=sha256(b"HHS-LANE5-HOST-INGRESS-ROUTE-V1\0" + digest).digest(),
        reciprocal_witness_sha256=sha256(b"HHS-LANE5-HOST-INGRESS-RECIPROCAL-V1\0" + digest).digest(),
        phase_slot=(int.from_bytes(digest[:2], "big") % 4) * 18,
        trinary_collapse=(-1, 0, 1)[digest[2] % 3],
        binary_collapse=digest[3] & 1,
    )


def continue_staged_to_lane5(
    staging: AdminStreamStaging,
    upload_id: str,
    authenticated_owner: str,
    *,
    bridge_factory: Callable[[], Pass219Lane5UnboundedWorkloadBridge] = Pass219Lane5UnboundedWorkloadBridge,
) -> dict:
    """Return noncanonical candidate proof. Canonical persistence is not performed.

    The caller is a trusted, authorized worker, never an unauthenticated HTTP
    request. This reads the exact source path granted by SQL owner identity.
    """
    record = staging.status(upload_id, authenticated_owner)
    if record["state"] != "STAGED":
        raise NativeContinuationError("SOURCE_NOT_STAGED")
    source = staging.read_staged(upload_id, authenticated_owner)
    if not isinstance(source, Path) or source.is_symlink():
        raise NativeContinuationError("SOURCE_PATH_NOT_TRUSTED")

    # Existing native workload stream logic, not a second tokenizer.
    envelope = Lane5WorkloadEnvelope.from_file(
        source,
        provenance=f"admin-sql-stage:{upload_id}:{record['source_sha256']}",
        chunk_bytes=VM81_FRAME_BYTES,
    )
    if envelope.byte_count != record["received_bytes"]:
        raise NativeContinuationError("SOURCE_LENGTH_DRIFT")
    if envelope.workload_sha256.hex() != record["source_sha256"]:
        raise NativeContinuationError("SOURCE_DIGEST_DRIFT")

    bridge = bridge_factory()
    authority = bridge.authority()
    required = (
        "any_byte_serializable_workload", "workload_class_agnostic",
        "streaming_candidate_ingress", "candidate_only",
        "requires_signed_environmental_vm81_admission",
    )
    if not all(authority.get(key) is True for key in required):
        raise NativeContinuationError("NATIVE_AUTHORITY_NOT_READY")
    if any(authority.get(key) is not False for key in
           ("canonical_vm81_mutation_authority", "canonical_hash216_authority")):
        raise NativeContinuationError("NATIVE_AUTHORITY_ESCALATION")

    digest = envelope.workload_sha256
    result = bridge.optimize(
        workload=envelope,
        previous_address=_address(b"previous", digest),
        current_address=_address(b"current", digest),
        goal_address=_address(b"goal", digest),
        forbidden_boundary_sha256=_FORBIDDEN,
        candidates=(_candidate(digest),),
    )
    if not (
        result.get("candidate_only") is True
        and result.get("canonical_vm81_mutation_authority") is False
        and result.get("canonical_hash216_authority") is False
        and result.get("requires_signed_environmental_vm81_admission") is True
        and int(result.get("admitted_candidates", 0)) >= 1
        and result.get("workload_sha256") == record["source_sha256"]
        and result.get("workload_byte_count") == record["received_bytes"]
    ):
        raise NativeContinuationError("CANDIDATE_RECEIPT_INVALID")
    return {
        "upload_id": upload_id,
        "source_sha256": record["source_sha256"],
        "native_vm81_frame_bytes": VM81_FRAME_BYTES,
        "native_candidate_receipt": result,
        "canonical_hash216_admitted": False,
        "signed_vm81_admission_required": True,
    }

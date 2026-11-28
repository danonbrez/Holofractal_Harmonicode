"""Restricted SQL-staged source handoff to inherited signed Pass219 fixture.

DIAGNOSTIC ONLY. The inherited native test executable installs a deterministic
test key and genesis Hash216 parent, so receipts do not authorize production
source admission, do not mutate SQL admission state, and do not enter RAG.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_backend.runtime.hhs_admin_sql_typed_vm81_source_v1 import inspect_exact_typed_vm81_source
from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    run_native_admission,
)
from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    raw_le_to_words,
    unpack_vm81_binding_words,
)


class StagedSignedFixtureError(RuntimeError):
    pass


def verify_staged_signed_fixture(
    staging: AdminStreamStaging,
    upload_id: str,
    authenticated_owner: str,
    *,
    native_probe: str,
    mode: str = "commit",
) -> dict[str, Any]:
    """Check exact SQL bytes before fixture execution; produce noncanonical evidence."""
    if mode != "commit":
        raise StagedSignedFixtureError("FIXTURE_POSITIVE_MODE_ONLY")
    if not isinstance(native_probe, str) or not Path(native_probe).is_file():
        raise StagedSignedFixtureError("INHERITED_NATIVE_PROBE_NOT_PRESENT")
    inspection = inspect_exact_typed_vm81_source(staging, upload_id, authenticated_owner)
    if inspection.get("typed_frame_recognized") is not True:
        raise StagedSignedFixtureError("INHERITED_TYPED_VM81_SOURCE_REQUIRED")
    record = staging.status(upload_id, authenticated_owner)
    if record["state"] != "STAGED" or record["source_sha256"] != inspection["source_sha256"]:
        raise StagedSignedFixtureError("SQL_SOURCE_IDENTITY_DRIFT")
    source = staging.read_staged(upload_id, authenticated_owner)
    raw = source.read_bytes()  # exact 648-byte fixture, not a general upload limit
    if len(raw) != 648 or sha256(raw).hexdigest() != record["source_sha256"]:
        raise StagedSignedFixtureError("SQL_SOURCE_BYTES_DRIFT")

    result = run_native_admission(raw, native_probe, mode)
    receipt = result["native"]
    committed = result["committed_raw"]
    if not (
        receipt.get("status") == 0
        and receipt.get("provider_available") == 1
        and receipt.get("parent_hash216_verified") == 1
        and receipt.get("child_hash216_verified") == 1
        and receipt.get("canonical_receipt_minted") == 1
        and receipt.get("signature_verified") == 1
        and receipt.get("environment_verified") == 1
        and receipt.get("authority_handoff_exact") == 1
        and committed == raw
    ):
        raise StagedSignedFixtureError("INHERITED_SIGNED_FIXTURE_REJECTED")
    restored = unpack_vm81_binding_words(raw_le_to_words(committed))
    if str(restored["bigint"]) != inspection["bigint"] or restored["metadata"] != inspection["metadata"]:
        raise StagedSignedFixtureError("INHERITED_TYPED_FRAME_REPLAY_DRIFT")
    # The native probe's receipt is a test-root proof only, not a source
    # authorization. Never expose its "canonical_receipt_minted" flag as a
    # production Hash216 admission result.
    return {
        "schema": "HHS_ADMIN_SQL_STAGED_SIGNED_FIXTURE_RESULT_V1",
        "upload_id": upload_id,
        "source_sha256": record["source_sha256"],
        "typed_frame_reencoded_exact": True,
        "fixture_native_signed_commit_verified": True,
        "fixture_parent_hash216_verified": True,
        "fixture_child_hash216_verified": True,
        "fixture_signature_verified": True,
        "fixture_environment_verified": True,
        "production_parent_hash216_authorized": False,
        "production_uqcel_witness_bound": False,
        "signed_vm81_admission_performed": False,
        "canonical_hash216_admitted": False,
        "production_persistence_performed": False,
        "test_root_only": True,
    }

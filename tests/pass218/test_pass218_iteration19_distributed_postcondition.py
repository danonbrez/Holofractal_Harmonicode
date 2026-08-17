from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.authority_maintenance_i12 import (
    Pass218MaintenancePolicy,
    seal_credential_rotation_plan,
    seal_member_replacement_plan,
    seal_snapshot_retention_receipt,
)
from hhs_runtime.pass218.distributed_postcondition_i19 import (
    Pass218PostconditionValidationError,
    seal_postcondition_observation,
    validate_postcondition_observation,
)


def h72(label: str) -> str:
    return hash72_digest({"domain": "HHS-P218-I19-TEST"}, {"label": label})


def credential_plan() -> dict:
    return seal_credential_rotation_plan(
        rotation_id="i19-test-rotation",
        old_ca_sha256="1" * 64,
        new_ca_sha256="2" * 64,
        old_client_cert_sha256="3" * 64,
        new_client_cert_sha256="4" * 64,
        old_client_key_sha256="5" * 64,
        new_client_key_sha256="6" * 64,
        preflight_probe_hash72=h72("credential-preflight"),
        current_global_fence=7,
    )


def test_credential_rotation_requires_observed_new_identity_and_newer_fence():
    plan = credential_plan()
    observation = seal_postcondition_observation(
        action="PREPARE_CREDENTIAL_ROTATION",
        i12_maintenance_record=plan,
        observation={
            "active_ca_sha256": "2" * 64,
            "active_client_cert_sha256": "4" * 64,
            "active_client_key_sha256": "6" * 64,
            "new_writer_fence_epoch": 8,
            "new_credentials_verified": True,
            "old_writer_released": True,
            "simultaneous_writer_identities_observed": False,
            "post_linearizable_probe_hash72": h72("credential-post"),
        },
        observed_epoch_ns=10,
    )
    value = validate_postcondition_observation(observation)
    assert value["new_writer_fence_epoch"] == 8
    assert value["new_credentials_verified"] is True
    assert value["old_writer_released"] is True
    assert value["simultaneous_writer_identities_observed"] is False
    assert value["execution_authority_minted"] is False
    assert value["retry_authority_minted"] is False


def test_credential_rotation_rejects_plan_only_or_old_identity():
    plan = credential_plan()
    with pytest.raises(Pass218PostconditionValidationError):
        seal_postcondition_observation(
            action="PREPARE_CREDENTIAL_ROTATION",
            i12_maintenance_record=plan,
            observation={
                "active_ca_sha256": "1" * 64,
                "active_client_cert_sha256": "3" * 64,
                "active_client_key_sha256": "5" * 64,
                "new_writer_fence_epoch": 8,
                "new_credentials_verified": True,
                "old_writer_released": True,
                "simultaneous_writer_identities_observed": False,
                "post_linearizable_probe_hash72": h72("credential-post"),
            },
            observed_epoch_ns=10,
        )


def test_member_replacement_requires_exact_replacement_and_post_probe():
    plan = seal_member_replacement_plan(
        replacement_id="i19-member",
        old_member_id=11,
        replacement_member_name="etcd-b-new",
        replacement_peer_url="https://10.0.0.2:2380",
        replacement_client_url="https://10.0.0.2:2379",
        preflight_probe_hash72=h72("member-preflight"),
        expected_member_count=3,
        quorum_size=2,
    )
    observation = seal_postcondition_observation(
        action="PREPARE_MEMBER_REPLACEMENT",
        i12_maintenance_record=plan,
        observation={
            "replacement_member_name": "etcd-b-new",
            "replacement_peer_url": "https://10.0.0.2:2380",
            "replacement_client_url": "https://10.0.0.2:2379",
            "observed_member_count": 3,
            "observed_quorum_size": 2,
            "old_member_absent": True,
            "replacement_present": True,
            "quorum_preserved": True,
            "post_linearizable_probe_hash72": h72("member-post"),
        },
        observed_epoch_ns=20,
    )
    value = validate_postcondition_observation(observation)
    assert value["old_member_absent"] is True
    assert value["replacement_present"] is True
    assert value["quorum_preserved"] is True


def test_snapshot_rehearsal_uses_existing_exact_i12_receipt_as_intrinsic_proof():
    policy = Pass218MaintenancePolicy.build(expected_member_count=3)
    snapshot_sha = "a" * 64
    receipt = seal_snapshot_retention_receipt(
        policy=policy,
        snapshot_sha256_values=[snapshot_sha],
        rehearsal_snapshot_sha256=snapshot_sha,
        rehearsal_manifest_hash72=h72("snapshot-manifest"),
        rehearsal_canonical_root_exact=True,
        rehearsal_vm81_snapshot_exact=True,
        rehearsal_consumed_receipt_exact=True,
        rehearsal_distributed_checkpoint_exact=True,
        restart_authorization_minted=False,
        restart_canonical_mutation_invoked=False,
    )
    observation = seal_postcondition_observation(
        action="REQUEST_SNAPSHOT_REHEARSAL",
        i12_maintenance_record=receipt,
        observation={
            "rehearsal_receipt_hash72": receipt["record_hash72"],
            "rehearsal_manifest_hash72": receipt["rehearsal_manifest_hash72"],
            "rehearsal_canonical_root_exact": True,
            "rehearsal_vm81_snapshot_exact": True,
            "rehearsal_consumed_receipt_exact": True,
            "rehearsal_distributed_checkpoint_exact": True,
            "restore_target_non_authoritative": True,
        },
        observed_epoch_ns=30,
    )
    value = validate_postcondition_observation(observation)
    assert value["restore_target_non_authoritative"] is True
    assert value["postcondition_verified"] is True


def test_tampered_postcondition_observation_is_rejected():
    plan = credential_plan()
    observation = seal_postcondition_observation(
        action="PREPARE_CREDENTIAL_ROTATION",
        i12_maintenance_record=plan,
        observation={
            "active_ca_sha256": "2" * 64,
            "active_client_cert_sha256": "4" * 64,
            "active_client_key_sha256": "6" * 64,
            "new_writer_fence_epoch": 8,
            "new_credentials_verified": True,
            "old_writer_released": True,
            "simultaneous_writer_identities_observed": False,
            "post_linearizable_probe_hash72": h72("credential-post"),
        },
        observed_epoch_ns=10,
    )
    observation["active_client_cert_sha256"] = "3" * 64
    with pytest.raises(Pass218PostconditionValidationError):
        validate_postcondition_observation(observation)


def test_i19_authoritative_sources_contain_no_float_literals():
    paths = [
        Path("hhs_runtime/pass218/distributed_postcondition_i19.py"),
        Path("hhs_backend/pass218_execution_i19_control.py"),
        Path("hhs_backend/runtime_os_pass218_postcondition_i19.py"),
    ]
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, f"{path}: authoritative float literal(s) found"

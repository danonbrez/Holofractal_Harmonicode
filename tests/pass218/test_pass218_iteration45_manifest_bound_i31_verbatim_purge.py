from __future__ import annotations

import ast
import json
from pathlib import Path
import runpy
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_manifest_i31_verbatim_purge_i45 import (
    PASS218_I45_PURGE_PATH,
    PASS218_I45_STATUS_PATH,
    install_pass218_i45_manifest_bound_i31_verbatim_purge_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import PASS218_I30_TARGET_SCOPE
from hhs_runtime.pass218.manifest_bound_i30_atomic_promotion_i44 import (
    PASS218_I44_COMPLETE_STATUS,
    PASS218_I44_PROMOTED_PENDING_I31_STATUS,
    PASS218_I44_PROOF_SCHEMA,
    PASS218_I44_RECEIPT_SCHEMA,
)
from hhs_runtime.pass218.manifest_bound_i31_verbatim_purge_i45 import (
    PASS218_I45_COMPLETE_STATUS,
    Pass218I45BindingError,
    Pass218I45ManifestBoundI31VerbatimPurge,
    Pass218I45StateError,
)
from hhs_runtime.pass218.verbatim_purge_i31 import (
    PASS218_I31_PURGED_STATUS,
    Pass218I31ManagedBufferRegistry,
    Pass218I31PurgeConfirmationError,
    Pass218I31VerbatimPurger,
)

ROOT = Path(__file__).resolve().parents[2]
I31 = runpy.run_path(
    str(ROOT / "tests" / "pass218" / "test_pass218_iteration31_verbatim_purge.py")
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


class FrozenI44Store:
    def __init__(self, receipt: dict[str, object], proof: dict[str, object]) -> None:
        self.receipt = receipt
        self.proof = proof

    def active_record(self):
        return json.loads(json.dumps(self.receipt))

    def active_proof(self):
        return json.loads(json.dumps(self.proof))


def make_i44_binding(i30_store, *, wrong_promotion_receipt: bool = False):
    generation = i30_store.active_generation()
    assert generation is not None
    i30 = generation["promotion_receipt"]
    i43_receipt_hash72 = h72("I45-I43-RECEIPT", i30["promotion_receipt_hash72"])
    i43_authorization_hash72 = h72("I45-I43-AUTH", i30["grant_hash72"])
    promotion_receipt_hash72 = (
        h72("I45-WRONG-PROMOTION-RECEIPT", i30["promotion_receipt_hash72"])
        if wrong_promotion_receipt
        else i30["promotion_receipt_hash72"]
    )
    proof_body = {
        "schema": PASS218_I44_PROOF_SCHEMA,
        "version": "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-V1",
        "scope": "PASS218_MANIFEST_BOUND_I30_ATOMIC_PROMOTION",
        "status": PASS218_I44_PROMOTED_PENDING_I31_STATUS,
        "target_surface": PASS218_I30_TARGET_SCOPE,
        "i43_receipt_hash72": i43_receipt_hash72,
        "i43_authorization_proof_hash72": i43_authorization_hash72,
        "i29_validation_request_sha256": "1" * 64,
        "i30_promotion_request_sha256": "2" * 64,
        "i30_grant_hash72": i30["grant_hash72"],
        "i30_promotion_receipt_hash72": promotion_receipt_hash72,
        "i30_promotion_hash72": i30["promotion_hash72"],
        "i30_promotion_hash216": i30["promotion_hash216"],
        "i30_promoted_object_hash72": i30["promoted_object_hash72"],
        "i30_candidate_sha256": i30["candidate_sha256"],
        "i30_target_root_before_hash72": i30["target_root_before_hash72"],
        "i30_target_root_after_hash72": i30["target_root_after_hash72"],
        "i30_root_verification_hash72": i30["root_verification_hash72"],
        "shared_identity": {},
        "i43_authorization_consumed": True,
        "i30_request_fingerprint_matches_i43": True,
        "i29_request_fingerprint_matches_i43": True,
        "i30_grant_identity_matches_i43": True,
        "i30_atomic_promotion_committed": True,
        "i30_atomic_manifest_swap_verified": True,
        "i30_durable_generation_verified": True,
        "i30_canonical_root_verified": True,
        "vm5184_authoritative_projection_verified": True,
        "vm5184_authoritative_state_committed": True,
        "i30_exactly_once_or_restart_adoption_verified": True,
        "restart_does_not_require_duplicate_i30_invocation": True,
        "i30_promotion_request_persisted": False,
        "source_payload_persisted": False,
        "pass218_i31_verbatim_purge_invoked": False,
        "pass218_i32_source_closure_invoked": False,
        "curriculum_cursor_advanced": False,
        "vm81_authorization_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    proof_hash72 = hash72_digest({"domain": PASS218_I44_PROOF_SCHEMA}, proof_body)
    proof = {**proof_body, "manifest_bound_i30_atomic_promotion_hash72": proof_hash72}
    receipt_body = {
        "schema": PASS218_I44_RECEIPT_SCHEMA,
        "version": "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-V1",
        "scope": "PASS218_MANIFEST_BOUND_I30_ATOMIC_PROMOTION",
        "status": PASS218_I44_COMPLETE_STATUS,
        "promotion_status": PASS218_I44_PROMOTED_PENDING_I31_STATUS,
        "target_surface": PASS218_I30_TARGET_SCOPE,
        "i43_receipt_hash72": i43_receipt_hash72,
        "i43_authorization_proof_hash72": i43_authorization_hash72,
        "manifest_bound_i30_atomic_promotion_hash72": proof_hash72,
        "i29_validation_request_sha256": "1" * 64,
        "i30_promotion_request_sha256": "2" * 64,
        "i30_grant_hash72": i30["grant_hash72"],
        "i30_promotion_receipt_hash72": promotion_receipt_hash72,
        "i30_promoted_object_hash72": i30["promoted_object_hash72"],
        "i30_candidate_sha256": i30["candidate_sha256"],
        "i30_target_root_after_hash72": i30["target_root_after_hash72"],
        "i44_validation_hash72": h72("I45-I44-VALIDATION", promotion_receipt_hash72),
        "i43_authorization_consumed": True,
        "i30_atomic_promotion_committed": True,
        "i30_durable_generation_verified": True,
        "i30_canonical_root_verified": True,
        "vm5184_authoritative_projection_invoked": True,
        "vm5184_authoritative_state_committed": True,
        "restart_safe_exact_promotion_adoption": True,
        "i30_promotion_request_persisted": False,
        "pass218_i31_verbatim_purge_invoked": False,
        "pass218_i32_source_closure_invoked": False,
        "curriculum_cursor_advanced": False,
        "vm81_authorization_invoked": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "verbatim_corpus_source_retained": False,
        "authoritative_float_weights_created": False,
    }
    i44_receipt_hash72 = hash72_digest({"domain": PASS218_I44_RECEIPT_SCHEMA}, receipt_body)
    receipt = {
        **receipt_body,
        "i44_receipt_hash72": i44_receipt_hash72,
        "i44_hash216": i43_receipt_hash72 + promotion_receipt_hash72 + i44_receipt_hash72,
        "i44_hash216_semantics": [
            "I43_EXACT_I30_PROMOTION_REQUEST_AUTHORIZATION_RECEIPT",
            "I30_ATOMIC_SEMANTIC_PROMOTION_RECEIPT",
            "I44_MANIFEST_BOUND_ATOMIC_PROMOTION_RECEIPT",
        ],
    }
    return FrozenI44Store(receipt, proof)


def prepare_i45(tmp_path: Path, *, managed_buffers=None, wrong_i44: bool = False):
    i30_root = tmp_path / "state" / "cognition" / "atomic-semantic-promotion-i30"
    i30_store, identity = I31["_make_i30_store"](i30_root)
    lifecycle = I31["_Lifecycle"](True)
    registry = managed_buffers or Pass218I31ManagedBufferRegistry()
    purger = Pass218I31VerbatimPurger(
        lifecycle=lifecycle,
        i30_store_root=i30_root,
        purge_store_root=tmp_path / "state" / "cognition" / "verbatim-purge-i31",
        managed_buffers=registry,
    )
    i44_store = make_i44_binding(i30_store, wrong_promotion_receipt=wrong_i44)
    runtime = Pass218I45ManifestBoundI31VerbatimPurge(
        lifecycle=lifecycle,
        i44_store=i44_store,
        i31_purger=purger,
        state_root=tmp_path / "state" / "cognition" / "manifest-bound-i31-verbatim-purge-i45",
    )
    return runtime, purger, lifecycle, i30_store, identity, i44_store, registry


def test_i45_fresh_path_invokes_i31_once_and_preserves_i30_generation(tmp_path: Path) -> None:
    runtime, purger, _, i30_store, _, _, _ = prepare_i45(tmp_path)
    before = i30_store.active_generation()
    receipt = runtime.purge()
    after = i30_store.active_generation()
    proof = runtime.store.active_proof()
    assert receipt["status"] == PASS218_I45_COMPLETE_STATUS
    assert receipt["purge_status"] == PASS218_I31_PURGED_STATUS
    assert receipt["i31_verbatim_purge_invoked"] is True
    assert receipt["i31_purge_receipt_committed"] is True
    assert receipt["i30_semantic_generation_unchanged_across_purge"] is True
    assert before == after
    assert runtime.i31_invocation_count == 1
    assert purger.purge_count == 1
    assert proof is not None
    assert proof["i31_exactly_once_or_restart_adoption_verified"] is True
    assert proof["pass218_i32_source_closure_invoked"] is False
    assert receipt["curriculum_cursor_advanced"] is False


def test_i45_restart_adopts_exact_existing_i31_without_duplicate_purge(tmp_path: Path) -> None:
    runtime, purger, lifecycle, i30_store, identity, i44_store, _ = prepare_i45(tmp_path)
    direct = purger.purge(I31["_request"](identity))
    assert purger.purge_count == 1
    receipt = runtime.purge()
    assert receipt["i31_purge_receipt_hash72"] == direct["purge_receipt_hash72"]
    assert runtime.i31_invocation_count == 0
    assert runtime.restart_adoption_count == 1
    restarted = Pass218I45ManifestBoundI31VerbatimPurge(
        lifecycle=lifecycle,
        i44_store=i44_store,
        i31_purger=purger,
        state_root=tmp_path / "state" / "cognition" / "manifest-bound-i31-verbatim-purge-i45",
    )
    assert restarted.purge() == receipt
    assert restarted.i31_invocation_count == 0
    assert purger.purge_count == 1
    assert i30_store.active_generation() is not None


def test_i45_zeroizes_managed_buffer_but_persists_no_verbatim_source(tmp_path: Path) -> None:
    registry = Pass218I31ManagedBufferRegistry()
    runtime, _, _, _, identity, _, _ = prepare_i45(tmp_path, managed_buffers=registry)
    raw = bytearray(b"I45 transient verbatim source marker 5d81f1 must never persist")
    import hashlib
    registry.register(
        "i45-source-buffer",
        promotion_receipt_hash72=identity["promotion_receipt_hash72"],
        source_sha256=hashlib.sha256(bytes(raw)).hexdigest(),
        buffer=raw,
    )
    receipt = runtime.purge()
    assert raw == bytearray()
    assert registry.count() == 0
    assert receipt["i31_purge_mode"] == "MANAGED_BUFFER_ZEROIZE_AND_CLEAR"
    serialized = b"".join(
        path.read_bytes()
        for path in sorted(runtime.store.root.rglob("*.json"))
    )
    assert b"transient verbatim source marker" not in serialized
    assert b"managed_buffer_witnesses" not in serialized
    assert receipt["verbatim_corpus_source_retained"] is False


def test_i45_valid_but_mismatched_i44_binding_fails_before_i31(tmp_path: Path) -> None:
    runtime, purger, _, _, _, _, _ = prepare_i45(tmp_path, wrong_i44=True)
    with pytest.raises(Pass218I45BindingError, match="P218_I45_I30_RECEIPT_I44_MISMATCH"):
        runtime.purge()
    assert runtime.i31_invocation_count == 0
    assert purger.purge_count == 0
    assert purger.store.active_record() is None


def test_i45_quarantined_i31_fails_closed_and_never_seals_i45(tmp_path: Path) -> None:
    runtime, purger, _, _, identity, _, _ = prepare_i45(tmp_path)
    with pytest.raises(Pass218I31PurgeConfirmationError):
        purger.purge(I31["_request"](identity), force_confirmation_failure=True)
    with pytest.raises(Pass218I45StateError, match="P218_I45_I31_QUARANTINED"):
        runtime.purge()
    assert runtime.store.active_record() is None
    assert runtime.i31_invocation_count == 0


def test_i45_runtimeos_derives_bindings_and_rejects_caller_override_payload(tmp_path: Path) -> None:
    runtime, purger, lifecycle, _, _, i44_store, _ = prepare_i45(tmp_path)
    app = FastAPI()
    i44_control = SimpleNamespace(promotion=SimpleNamespace(store=i44_store))
    i31_control = SimpleNamespace(purger=purger)
    control = install_pass218_i45_manifest_bound_i31_verbatim_purge_control(
        app,
        i44_control,
        i31_control,
        lifecycle,
        state_root=tmp_path / "state",
    )
    client = TestClient(app)
    rejected = client.post(
        PASS218_I45_PURGE_PATH,
        json={"purge_binding": {"expected_canonical_root_hash72": h72("OVERRIDE", 45)}},
    )
    assert rejected.status_code == 409
    accepted = client.post(PASS218_I45_PURGE_PATH, json={})
    assert accepted.status_code == 200
    status = client.get(PASS218_I45_STATUS_PATH).json()
    assert status["api_derives_i31_request_from_durable_i44_i30"] is True
    assert status["api_can_override_i30_promotion_identity"] is False
    assert status["api_can_supply_raw_source_payload"] is False
    assert status["api_invokes_i32"] is False
    assert control.purge_control.i31_invocation_count == 1


def test_i45_authoritative_surfaces_contain_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_i31_verbatim_purge_i45.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_i31_verbatim_purge_i45.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path

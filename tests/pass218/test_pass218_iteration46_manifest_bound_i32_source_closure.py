from __future__ import annotations

import ast
from pathlib import Path
import runpy
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_manifest_i32_source_closure_i46 import (
    PASS218_I46_CLOSE_PATH,
    PASS218_I46_STATUS_PATH,
    install_pass218_i46_manifest_bound_i32_source_closure_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PENDING_PURGE_STATUS,
    PASS218_I30_PROMOTED_OBJECT_SCHEMA,
    PASS218_I30_PROMOTION_VERSION,
    PASS218_I30_TARGET_SCOPE,
    Pass218I30AtomicSemanticStore,
)
from hhs_runtime.pass218.manifest_bound_i30_atomic_promotion_i44 import (
    PASS218_I44_COMPLETE_STATUS,
    PASS218_I44_PROMOTED_PENDING_I31_STATUS,
    PASS218_I44_PROOF_SCHEMA,
    PASS218_I44_RECEIPT_SCHEMA,
)
from hhs_runtime.pass218.manifest_bound_i31_verbatim_purge_i45 import (
    Pass218I45ManifestBoundI31VerbatimPurge,
)
from hhs_runtime.pass218.manifest_bound_i32_source_closure_i46 import (
    PASS218_I46_COMPLETE_STATUS,
    Pass218I46BindingError,
    Pass218I46ManifestBoundI32SourceClosure,
    _derive_i32_request,
    _verify_i31_receipt,
)
from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    Pass218I34ManifestSourceIngressStore,
)
from hhs_runtime.pass218.source_closure_i32 import (
    PASS218_I32_CLOSED_STATUS,
    Pass218I32SourceCloser,
)
from hhs_runtime.pass218.verbatim_purge_i31 import Pass218I31VerbatimPurger

ROOT = Path(__file__).resolve().parents[2]
I43 = runpy.run_path(
    str(ROOT / "tests" / "pass218" / "test_pass218_iteration43_manifest_bound_i30_promotion_request_authorization.py")
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


class FrozenI44Store:
    def __init__(self, receipt: dict[str, object], proof: dict[str, object]) -> None:
        self.receipt = receipt
        self.proof = proof

    def active_record(self):
        return dict(self.receipt)

    def active_proof(self):
        return dict(self.proof)


def make_i30_store(
    root: Path,
    *,
    i43_receipt: dict[str, object],
) -> Pass218I30AtomicSemanticStore:
    store = Pass218I30AtomicSemanticStore(root)
    i29_validation = str(i43_receipt["i29_validation_hash72"])
    validated_hash216 = str(i43_receipt["i29_validated_hash216"])
    grant_hash72 = str(i43_receipt["i30_grant_hash72"])
    promoted_body = {
        "schema": PASS218_I30_PROMOTED_OBJECT_SCHEMA,
        "version": PASS218_I30_PROMOTION_VERSION,
        "i29_validation_hash72": i29_validation,
        "validated_hash216": validated_hash216,
        "semantic_payload": {
            "grounded_graph": {
                "relation_count": 1,
                "source_text_retained": False,
                "source_token_stream_retained": False,
            },
            "perspective_context": {
                "perspective_order_sequence": [1],
                "source_text_retained": False,
                "source_token_stream_retained": False,
            },
        },
        "retained_artifact_allowlist": [
            "checksums_and_identity_metadata",
            "typed_relational_graph",
            "vm5184_exact_state",
            "validation_and_lineage_receipts",
        ],
        "source_text_retained": False,
        "source_token_stream_retained": False,
        "verbatim_corpus_source_retained": False,
        "purge_status": "PENDING_VERBATIM_PURGE",
        "curriculum_advance_permitted": False,
        "truth_promotion": False,
        "action_authority_minted": False,
        "canonical_learning_commit_invoked": False,
        "model_activation_invoked": False,
        "authoritative_float_weights_created": False,
    }
    promoted_hash72 = hash72_digest(
        {"domain": "HHS-P218-I30-PROMOTED-SEMANTIC-OBJECT-V1"}, promoted_body
    )
    promoted = {**promoted_body, "promoted_object_hash72": promoted_hash72}
    target_before = store.empty_root_hash72()
    candidate = {
        "schema": "HHS-P218-I30-PROMOTION-CANDIDATE-COMMIT-V1",
        "version": PASS218_I30_PROMOTION_VERSION,
        "i29_validation_hash72": i29_validation,
        "validated_hash216": validated_hash216,
        "promoted_object_hash72": promoted_hash72,
        "promoted_object": promoted,
        "grant": {
            "grant_hash72": grant_hash72,
            "truth_promotion": False,
            "action_authority_minted": False,
            "learning_authority_granted": False,
        },
        "target_root_before_hash72": target_before,
        "formal_semantic_round_trip_verified": True,
        "grounded_round_trip_verified": True,
        "perspective_round_trip_verified": True,
        "vm5184_projection_rederived": True,
        "candidate_only": True,
        "atomic_promotion_invoked": False,
        "verbatim_corpus_source_retained": False,
    }
    candidate_filename, candidate_sha256 = store.commit_candidate(candidate)
    target_after = h72(
        "HHS-P218-I46-TEST-I30-TARGET-AFTER-V1",
        {
            "target_before": target_before,
            "promoted_object_hash72": promoted_hash72,
            "candidate_sha256": candidate_sha256,
        },
    )
    root_verification = h72(
        "HHS-P218-I46-TEST-I30-ROOT-VERIFY-V1",
        {"target_after": target_after, "candidate": candidate_sha256},
    )
    promotion_hash72 = h72(
        "HHS-P218-I46-TEST-I30-PROMOTION-V1",
        {"target_after": target_after, "grant": grant_hash72},
    )
    promotion_receipt_hash72 = h72(
        "HHS-P218-I46-TEST-I30-PROMOTION-RECEIPT-V1",
        {"promotion_hash72": promotion_hash72, "promoted": promoted_hash72},
    )
    promotion_hash216 = (
        h72("HHS-P218-I46-TEST-I30-COMMIT-V1", candidate_sha256)
        + root_verification
        + promotion_receipt_hash72
    )
    receipt = store.atomic_promote(
        promoted_object=promoted,
        candidate_filename=candidate_filename,
        candidate_sha256=candidate_sha256,
        grant_hash72=grant_hash72,
        i29_validation_hash72=i29_validation,
        validated_hash216=validated_hash216,
        target_root_before_hash72=target_before,
        target_root_after_hash72=target_after,
        root_verification_hash72=root_verification,
        promotion_hash72=promotion_hash72,
        promotion_receipt_hash72=promotion_receipt_hash72,
        promotion_hash216=promotion_hash216,
    )
    assert receipt["promotion_status"] == PASS218_I30_PENDING_PURGE_STATUS
    return store


def make_i44_store(
    *,
    i43_receipt: dict[str, object],
    i30_store: Pass218I30AtomicSemanticStore,
    shared_identity: dict[str, object],
) -> FrozenI44Store:
    generation = i30_store.active_generation()
    assert generation is not None
    i30 = generation["promotion_receipt"]
    proof_body = {
        "schema": PASS218_I44_PROOF_SCHEMA,
        "version": "HHS-P218-I44-MANIFEST-BOUND-I30-ATOMIC-PROMOTION-V1",
        "scope": "PASS218_MANIFEST_BOUND_I30_ATOMIC_PROMOTION",
        "status": PASS218_I44_PROMOTED_PENDING_I31_STATUS,
        "target_surface": PASS218_I30_TARGET_SCOPE,
        "i43_receipt_hash72": i43_receipt["i43_receipt_hash72"],
        "i43_authorization_proof_hash72": i43_receipt[
            "manifest_bound_i30_request_authorization_hash72"
        ],
        "i29_validation_request_sha256": i43_receipt["i29_validation_request_sha256"],
        "i30_promotion_request_sha256": i43_receipt["i30_promotion_request_sha256"],
        "i30_grant_hash72": i30["grant_hash72"],
        "i30_promotion_receipt_hash72": i30["promotion_receipt_hash72"],
        "i30_promotion_hash72": i30["promotion_hash72"],
        "i30_promotion_hash216": i30["promotion_hash216"],
        "i30_promoted_object_hash72": i30["promoted_object_hash72"],
        "i30_candidate_sha256": i30["candidate_sha256"],
        "i30_target_root_before_hash72": i30["target_root_before_hash72"],
        "i30_target_root_after_hash72": i30["target_root_after_hash72"],
        "i30_root_verification_hash72": i30["root_verification_hash72"],
        "shared_identity": shared_identity,
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
        "i43_receipt_hash72": i43_receipt["i43_receipt_hash72"],
        "i43_authorization_proof_hash72": i43_receipt[
            "manifest_bound_i30_request_authorization_hash72"
        ],
        "manifest_bound_i30_atomic_promotion_hash72": proof_hash72,
        "i29_validation_request_sha256": i43_receipt["i29_validation_request_sha256"],
        "i30_promotion_request_sha256": i43_receipt["i30_promotion_request_sha256"],
        "i30_grant_hash72": i30["grant_hash72"],
        "i30_promotion_receipt_hash72": i30["promotion_receipt_hash72"],
        "i30_promoted_object_hash72": i30["promoted_object_hash72"],
        "i30_candidate_sha256": i30["candidate_sha256"],
        "i30_target_root_after_hash72": i30["target_root_after_hash72"],
        "i44_validation_hash72": h72(
            "HHS-P218-I46-TEST-I44-VALIDATION-V1", i30["promotion_receipt_hash72"]
        ),
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
    i44_hash72 = hash72_digest({"domain": PASS218_I44_RECEIPT_SCHEMA}, receipt_body)
    receipt = {
        **receipt_body,
        "i44_receipt_hash72": i44_hash72,
        "i44_hash216": (
            str(i43_receipt["i43_receipt_hash72"])
            + str(i30["promotion_receipt_hash72"])
            + i44_hash72
        ),
        "i44_hash216_semantics": [
            "I43_EXACT_I30_PROMOTION_REQUEST_AUTHORIZATION_RECEIPT",
            "I30_ATOMIC_SEMANTIC_PROMOTION_RECEIPT",
            "I44_MANIFEST_BOUND_ATOMIC_PROMOTION_RECEIPT",
        ],
    }
    return FrozenI44Store(receipt, proof)


def prepare_i46(
    tmp_path: Path,
    *,
    source: bytes = b"I46 closes the exact nonverbatim source transaction without advancing I33.",
):
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = I43["prepare_i42"](
        tmp_path,
        source=source,
        context_id="i46 transient request context must not persist",
    )
    request = I43["promotion_request"](validation_request, i42_receipt)
    i43 = I43["make_i43"](tmp_path, lifecycle, i42, validator)
    i43_receipt = i43.authorize(request)
    state = tmp_path / "state" / "cognition"
    i34_store = Pass218I34ManifestSourceIngressStore(state / "manifest-source-ingress-i34")
    i34 = i34_store.active_record()
    assert i34 is not None
    i42_proof = i42.store.active_proof()
    assert i42_proof is not None
    i30_root = state / "atomic-semantic-promotion-i30"
    i30_store = make_i30_store(i30_root, i43_receipt=i43_receipt)
    i44_store = make_i44_store(
        i43_receipt=i43_receipt,
        i30_store=i30_store,
        shared_identity=dict(i42_proof["shared_identity"]),
    )
    purger = Pass218I31VerbatimPurger(
        lifecycle=lifecycle,
        i30_store_root=i30_root,
        purge_store_root=state / "verbatim-purge-i31",
    )
    i45 = Pass218I45ManifestBoundI31VerbatimPurge(
        lifecycle=lifecycle,
        i44_store=i44_store,
        i31_purger=purger,
        state_root=state / "manifest-bound-i31-verbatim-purge-i45",
    )
    i45_receipt = i45.purge()
    closer = Pass218I32SourceCloser(
        lifecycle=lifecycle,
        i31_store_root=state / "verbatim-purge-i31",
        closure_store_root=state / "source-closure-i32",
    )
    runtime = Pass218I46ManifestBoundI32SourceClosure(
        lifecycle=lifecycle,
        i45_store=i45.store,
        i44_store=i44_store,
        i43_store=i43.store,
        i42_store=i42.store,
        i34_store=i34_store,
        i30_store=i30_store,
        i32_closer=closer,
        state_root=state / "manifest-bound-i32-source-closure-i46",
    )
    return {
        "source": source,
        "lifecycle": lifecycle,
        "i42": i42,
        "i43": i43,
        "i34_store": i34_store,
        "i30_store": i30_store,
        "i44_store": i44_store,
        "purger": purger,
        "i45": i45,
        "i45_receipt": i45_receipt,
        "closer": closer,
        "runtime": runtime,
    }


def test_i46_fresh_path_invokes_i32_once_and_preserves_i30_generation(tmp_path: Path) -> None:
    env = prepare_i46(tmp_path)
    runtime = env["runtime"]
    closer = env["closer"]
    before = env["i30_store"].active_generation()
    receipt = runtime.close()
    after = env["i30_store"].active_generation()
    proof = runtime.store.active_proof()
    assert receipt["status"] == PASS218_I46_COMPLETE_STATUS
    assert receipt["closure_status"] == PASS218_I32_CLOSED_STATUS
    assert receipt["i32_source_closure_invoked"] is True
    assert receipt["i32_closure_receipt_committed"] is True
    assert receipt["nonverbatim_source_transaction_durably_closed"] is True
    assert receipt["pass218_i33_curriculum_advance_invoked"] is False
    assert receipt["curriculum_cursor_advanced"] is False
    assert before == after
    assert runtime.i32_invocation_count == 1
    assert closer.close_count == 1
    assert proof is not None
    assert proof["i32_exactly_once_or_restart_adoption_verified"] is True
    assert proof["restart_does_not_require_duplicate_i32_invocation"] is True


def test_i46_restart_adopts_exact_existing_i32_without_duplicate_close(tmp_path: Path) -> None:
    env = prepare_i46(tmp_path)
    runtime = env["runtime"]
    i45 = env["i45"]
    i45_receipt = env["i45_receipt"]
    i45_proof = i45.store.active_proof()
    assert i45_proof is not None
    i31 = _verify_i31_receipt(
        env["purger"].store.active_record(),
        i45=i45_receipt,
        i45_proof=i45_proof,
    )
    i34 = env["i34_store"].active_record()
    assert i34 is not None
    request = _derive_i32_request(i31=i31, i34=i34)
    direct = env["closer"].close(request)
    assert env["closer"].close_count == 1
    receipt = runtime.close()
    assert receipt["i32_source_closure_hash72"] == direct["source_closure_hash72"]
    assert runtime.i32_invocation_count == 0
    assert runtime.restart_adoption_count == 1
    assert env["closer"].close_count == 1
    restarted = Pass218I46ManifestBoundI32SourceClosure(
        lifecycle=env["lifecycle"],
        i45_store=i45.store,
        i44_store=env["i44_store"],
        i43_store=env["i43"].store,
        i42_store=env["i42"].store,
        i34_store=env["i34_store"],
        i30_store=env["i30_store"],
        i32_closer=env["closer"],
        state_root=tmp_path / "state" / "cognition" / "manifest-bound-i32-source-closure-i46",
    )
    assert restarted.close() == receipt
    assert restarted.i32_invocation_count == 0
    assert env["closer"].close_count == 1


def test_i46_rejects_valid_but_unrelated_i34_source_identity_before_i32(tmp_path: Path) -> None:
    env = prepare_i46(tmp_path / "primary")
    other = prepare_i46(
        tmp_path / "other",
        source=b"A different valid manifest source must not inherit another I42 equality proof.",
    )
    runtime = Pass218I46ManifestBoundI32SourceClosure(
        lifecycle=env["lifecycle"],
        i45_store=env["i45"].store,
        i44_store=env["i44_store"],
        i43_store=env["i43"].store,
        i42_store=env["i42"].store,
        i34_store=other["i34_store"],
        i30_store=env["i30_store"],
        i32_closer=env["closer"],
        state_root=tmp_path / "rejected-i46",
    )
    with pytest.raises(Pass218I46BindingError, match="P218_I46_I34_I42_IDENTITY_MISMATCH"):
        runtime.close()
    assert runtime.i32_invocation_count == 0
    assert env["closer"].close_count == 0
    assert runtime.store.active_record() is None


def test_i46_persists_no_source_payload_and_makes_no_erasure_claim(tmp_path: Path) -> None:
    marker = b"I46 transient verbatim marker 4ac901 must never persist in I46 state"
    env = prepare_i46(tmp_path, source=marker)
    receipt = env["runtime"].close()
    serialized = b"".join(
        path.read_bytes()
        for path in sorted(env["runtime"].store.root.rglob("*.json"))
    )
    assert marker not in serialized
    assert receipt["verbatim_corpus_source_retained"] is False
    assert receipt["physical_memory_erasure_claimed"] is False
    assert receipt["external_source_storage_erasure_claimed"] is False
    assert receipt["authoritative_float_weights_created"] is False


def test_i46_runtimeos_derives_closure_and_rejects_caller_override(tmp_path: Path) -> None:
    env = prepare_i46(tmp_path)
    app = FastAPI()
    i45_control = SimpleNamespace(
        purge_control=env["i45"],
        i31_control=SimpleNamespace(purger=env["purger"]),
    )
    i44_control = SimpleNamespace(promotion=SimpleNamespace(store=env["i44_store"]))
    i43_control = SimpleNamespace(authorization=env["i43"])
    i42_control = SimpleNamespace(equality=env["i42"])
    i34_control = SimpleNamespace(ingress=SimpleNamespace(store=env["i34_store"]))
    i32_control = SimpleNamespace(closer=env["closer"])
    control = install_pass218_i46_manifest_bound_i32_source_closure_control(
        app,
        i45_control,
        i44_control,
        i43_control,
        i42_control,
        i34_control,
        i32_control,
        env["lifecycle"],
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    rejected = client.post(
        PASS218_I46_CLOSE_PATH,
        json={"closure_binding": {"curriculum_position": 99}},
    )
    assert rejected.status_code == 409
    accepted = client.post(PASS218_I46_CLOSE_PATH, json={})
    assert accepted.status_code == 200
    status = client.get(PASS218_I46_STATUS_PATH).json()
    assert status["api_derives_i32_request_from_durable_manifest_and_purge_chain"] is True
    assert status["api_can_override_i34_source_identity"] is False
    assert status["api_can_override_curriculum_identity"] is False
    assert status["api_invokes_i33"] is False
    assert status["api_advances_curriculum"] is False
    assert control.closure.i32_invocation_count == 1


def test_i46_authoritative_surfaces_contain_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_i32_source_closure_i46.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_i32_source_closure_i46.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, path

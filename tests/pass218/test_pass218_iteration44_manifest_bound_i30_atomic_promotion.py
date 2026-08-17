from __future__ import annotations

import ast
from pathlib import Path
import runpy
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_atomic_semantic_promotion_i30 import Pass218I30RuntimePromotionControl
from hhs_backend.runtime_os_pass218_manifest_i30_atomic_promotion_i44 import (
    PASS218_I44_PROMOTE_PATH,
    PASS218_I44_STATUS_PATH,
    install_pass218_i44_manifest_bound_i30_atomic_promotion_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_PENDING_PURGE_STATUS,
    PASS218_I30_PROMOTED_OBJECT_SCHEMA,
)
from hhs_runtime.pass218.manifest_bound_i30_atomic_promotion_i44 import (
    PASS218_I44_COMPLETE_STATUS,
    PASS218_I44_PROMOTED_PENDING_I31_STATUS,
    Pass218I44BindingError,
    Pass218I44ManifestBoundI30AtomicPromotion,
)

ROOT = Path(__file__).resolve().parents[2]
I43 = runpy.run_path(
    str(ROOT / "tests" / "pass218" / "test_pass218_iteration43_manifest_bound_i30_promotion_request_authorization.py")
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


def h216(domain: str, value: object) -> str:
    return h72(domain + "-A", value) + h72(domain + "-B", value) + h72(domain + "-C", value)


class FakeI30Store:
    def __init__(self) -> None:
        self.generation = None

    def active_generation(self):
        return self.generation


class FakeAuthorizedI30Promoter:
    """I44 membrane fixture; frozen I30 itself is covered by its inherited regression."""

    def __init__(self, i43_receipt) -> None:
        self.i43 = i43_receipt
        self.store = FakeI30Store()
        self.promotion_count = 0
        self.promote_calls = 0

    def _materialize(self):
        receipt = {
            "schema": "HHS-P218-I30-ATOMIC-PROMOTION-RECEIPT-V1",
            "i29_validation_hash72": self.i43["i29_validation_hash72"],
            "validated_hash216": self.i43["i29_validated_hash216"],
            "promoted_object_hash72": h72("I44-I30-PROMOTED", self.i43["i43_receipt_hash72"]),
            "candidate_filename": "candidate.json",
            "candidate_sha256": "b" * 64,
            "grant_hash72": self.i43["i30_grant_hash72"],
            "target_root_before_hash72": h72("I44-I30-ROOT-BEFORE", "empty"),
            "target_root_after_hash72": h72("I44-I30-ROOT-AFTER", self.i43["i43_receipt_hash72"]),
            "root_verification_hash72": h72("I44-I30-ROOT-VERIFY", self.i43["i43_receipt_hash72"]),
            "promotion_hash72": h72("I44-I30-PROMOTION", self.i43["i43_receipt_hash72"]),
            "promotion_receipt_hash72": h72("I44-I30-RECEIPT", self.i43["i43_receipt_hash72"]),
            "promotion_hash216": h216("I44-I30-PROMOTION216", self.i43["i43_receipt_hash72"]),
            "promotion_status": PASS218_I30_PENDING_PURGE_STATUS,
            "candidate_commit_verified": True,
            "prospective_root_verified": True,
            "formal_semantic_round_trip_verified": True,
            "grounded_round_trip_verified": True,
            "perspective_round_trip_verified": True,
            "vm5184_authoritative_projection_invoked": True,
            "vm5184_authoritative_state_committed": True,
            "vm81_authorization_invoked": False,
            "atomic_promotion_authorized": True,
            "atomic_promotion_invoked": True,
            "atomic_manifest_swap": True,
            "failed_partial_promotion_possible": False,
            "purge_status": "PENDING_VERBATIM_PURGE",
            "verbatim_purge_invoked": False,
            "purge_receipt_issued": False,
            "curriculum_advance_permitted": False,
            "closure_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        promoted = {
            "schema": PASS218_I30_PROMOTED_OBJECT_SCHEMA,
            "promoted_object_hash72": receipt["promoted_object_hash72"],
            "i29_validation_hash72": receipt["i29_validation_hash72"],
            "validated_hash216": receipt["validated_hash216"],
            "grant_hash72": receipt["grant_hash72"],
            "purge_status": "PENDING_VERBATIM_PURGE",
            "source_text_retained": False,
            "source_token_stream_retained": False,
            "verbatim_corpus_source_retained": False,
            "curriculum_advance_permitted": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "authoritative_float_weights_created": False,
            "vm5184_authority": {
                "authoritative_projection": True,
                "vm81_mutation": False,
                "canonical_float_fields": 0,
            },
        }
        self.store.generation = {"promoted_object": promoted, "promotion_receipt": receipt}
        return receipt

    def promote(self, request):
        self.promote_calls += 1
        if self.store.generation is not None:
            return self.store.generation["promotion_receipt"]
        self.promotion_count += 1
        return self._materialize()

    def status(self):
        if self.store.generation is None:
            return {
                "promotion_present": False,
                "atomic_promotion_invoked": False,
                "canonical_root_hash72": h72("I44-I30-EMPTY", "root"),
            }
        receipt = self.store.generation["promotion_receipt"]
        return {
            "promotion_present": True,
            "atomic_promotion_invoked": True,
            "promotion_status": receipt["promotion_status"],
            "canonical_root_hash72": receipt["target_root_after_hash72"],
            "promotion_receipt_hash72": receipt["promotion_receipt_hash72"],
            "grant_hash72": receipt["grant_hash72"],
        }


class FakeI30Control:
    def __init__(self, promoter) -> None:
        self.promoter = promoter

    @staticmethod
    def _request(payload):
        return Pass218I30RuntimePromotionControl._request(payload)

    def status(self):
        return self.promoter.status()


def prepare_i43(tmp_path: Path, *, context_id: str = "i44 transient request marker 91f7c2 must not persist"):
    source, lifecycle, _, validator, validation_request, i42, i42_receipt = I43["prepare_i42"](
        tmp_path,
        context_id=context_id,
    )
    request = I43["promotion_request"](validation_request, i42_receipt)
    i43 = I43["make_i43"](tmp_path, lifecycle, i42, validator)
    i43_receipt = i43.authorize(request)
    return source, lifecycle, request, i43, i43_receipt


def make_i44(tmp_path: Path, lifecycle, i43, promoter):
    return Pass218I44ManifestBoundI30AtomicPromotion(
        lifecycle=lifecycle,
        i43_store=i43.store,
        i30_promoter=promoter,
        state_root=tmp_path / "state" / "cognition" / "manifest-bound-i30-atomic-promotion-i44",
    )


def test_i44_fresh_path_invokes_i30_exactly_once_and_commits(tmp_path: Path) -> None:
    _, lifecycle, request, i43, i43_receipt = prepare_i43(tmp_path)
    promoter = FakeAuthorizedI30Promoter(i43_receipt)
    runtime = make_i44(tmp_path, lifecycle, i43, promoter)
    receipt = runtime.promote(request)
    proof = runtime.store.active_proof()
    assert proof is not None
    assert receipt["status"] == PASS218_I44_COMPLETE_STATUS
    assert receipt["promotion_status"] == PASS218_I44_PROMOTED_PENDING_I31_STATUS
    assert receipt["i43_authorization_consumed"] is True
    assert receipt["i30_atomic_promotion_committed"] is True
    assert receipt["vm5184_authoritative_projection_invoked"] is True
    assert receipt["vm5184_authoritative_state_committed"] is True
    assert receipt["pass218_i31_verbatim_purge_invoked"] is False
    assert receipt["pass218_i32_source_closure_invoked"] is False
    assert receipt["curriculum_cursor_advanced"] is False
    assert runtime.i30_invocation_count == 1
    assert promoter.promote_calls == 1
    assert promoter.promotion_count == 1
    assert proof["i30_exactly_once_or_restart_adoption_verified"] is True
    assert proof["restart_does_not_require_duplicate_i30_invocation"] is True


def test_i44_restart_adopts_exact_i30_without_second_invocation(tmp_path: Path) -> None:
    _, lifecycle, request, i43, i43_receipt = prepare_i43(tmp_path)
    promoter = FakeAuthorizedI30Promoter(i43_receipt)
    promoter.promote(request)
    assert promoter.promote_calls == 1
    runtime = make_i44(tmp_path, lifecycle, i43, promoter)
    receipt = runtime.promote(request)
    assert receipt["status"] == PASS218_I44_COMPLETE_STATUS
    assert runtime.i30_invocation_count == 0
    assert runtime.restart_adoption_count == 1
    assert promoter.promote_calls == 1
    restarted = make_i44(tmp_path, lifecycle, i43, promoter)
    assert restarted.promote(request) == receipt
    assert restarted.i30_invocation_count == 0
    assert promoter.promote_calls == 1


def test_i44_rejects_altered_transient_request_before_i30(tmp_path: Path) -> None:
    _, lifecycle, request, i43, i43_receipt = prepare_i43(tmp_path)
    promoter = FakeAuthorizedI30Promoter(i43_receipt)
    altered = I43["promotion_request"](
        request.validation_request,
        {"i29_validation_hash72": request.expected_i29_validation_hash72, "i29_validated_hash216": request.expected_validated_hash216},
        grant_sequence=request.grant_sequence + 1,
    )
    runtime = make_i44(tmp_path, lifecycle, i43, promoter)
    with pytest.raises(Pass218I44BindingError, match="P218_I44_I30_REQUEST_FINGERPRINT_MISMATCH"):
        runtime.promote(altered)
    assert promoter.promote_calls == 0
    assert runtime.store.active_record() is None


def test_i44_rejects_unrelated_active_i30_promotion(tmp_path: Path) -> None:
    _, lifecycle, request, i43, i43_receipt = prepare_i43(tmp_path)
    promoter = FakeAuthorizedI30Promoter(i43_receipt)
    promoter._materialize()
    promoter.store.generation["promotion_receipt"]["grant_hash72"] = h72("I44-WRONG-GRANT", "wrong")
    runtime = make_i44(tmp_path, lifecycle, i43, promoter)
    with pytest.raises(Pass218I44BindingError, match="P218_I44_I30_GRANT_HASH_MISMATCH"):
        runtime.promote(request)
    assert promoter.promote_calls == 0
    assert runtime.store.active_record() is None


def test_i44_persists_no_transient_request_or_source_payload(tmp_path: Path) -> None:
    marker = "i44 transient request marker d04cb8 must never persist"
    source, lifecycle, request, i43, i43_receipt = prepare_i43(tmp_path, context_id=marker)
    promoter = FakeAuthorizedI30Promoter(i43_receipt)
    runtime = make_i44(tmp_path, lifecycle, i43, promoter)
    runtime.promote(request)
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert source not in payload
            assert marker.encode("utf-8") not in payload
            assert b'"validation_request"' not in payload
            assert b'"promotion_authority"' not in payload
            assert b'"tokens"' not in payload


def test_runtimeos_i44_invokes_only_exact_authorized_i30_request(tmp_path: Path) -> None:
    _, lifecycle, request, i43, i43_receipt = prepare_i43(tmp_path)
    promoter = FakeAuthorizedI30Promoter(i43_receipt)
    i30_control = FakeI30Control(promoter)
    i43_control = SimpleNamespace(authorization=i43)
    app = FastAPI()
    control = install_pass218_i44_manifest_bound_i30_atomic_promotion_control(
        app,
        i43_control,
        i30_control,
        lifecycle,
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    before = client.get(PASS218_I44_STATUS_PATH).json()
    assert before["api_requires_durable_i43_authorization"] is True
    assert before["api_persists_i30_request_payload"] is False
    response = client.post(PASS218_I44_PROMOTE_PATH, json=I43["api_payload"](request))
    assert response.status_code == 200
    assert response.json()["status"] == PASS218_I44_COMPLETE_STATUS
    assert control.promotion.i30_invocation_count == 1
    assert promoter.promote_calls == 1
    after = client.get(PASS218_I44_STATUS_PATH).json()
    assert after["i30_atomic_promotion_committed"] is True
    assert after["pass218_i31_verbatim_purge_invoked"] is False
    assert after["api_invokes_i31_or_i32"] is False


def test_i44_authoritative_python_surface_contains_no_float_literals() -> None:
    paths = [
        ROOT / "hhs_runtime" / "pass218" / "manifest_bound_i30_atomic_promotion_i44.py",
        ROOT / "hhs_backend" / "runtime_os_pass218_manifest_i30_atomic_promotion_i44.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, str(path)

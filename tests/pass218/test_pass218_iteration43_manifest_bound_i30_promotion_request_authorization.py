from __future__ import annotations

import ast
from pathlib import Path
import runpy
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from hhs_backend.runtime_os_pass218_atomic_semantic_promotion_i30 import (
    Pass218I30RuntimePromotionControl,
)
from hhs_backend.runtime_os_pass218_manifest_i30_promotion_request_authorization_i43 import (
    PASS218_I43_AUTHORIZE_PATH,
    PASS218_I43_STATUS_PATH,
    install_pass218_i43_manifest_bound_i30_promotion_request_authorization_control,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass218.atomic_semantic_promotion_i30 import (
    PASS218_I30_TARGET_SCOPE,
    Pass218I30PromotionRequest,
)
from hhs_runtime.pass218.manifest_bound_i30_promotion_request_authorization_i43 import (
    PASS218_I43_AUTHORIZED_PENDING_STATUS,
    PASS218_I43_COMPLETE_STATUS,
    Pass218I43BindingError,
    Pass218I43ManifestBoundI30PromotionRequestAuthorization,
    Pass218I43StateError,
)

ROOT = Path(__file__).resolve().parents[2]
I42_HELPERS = runpy.run_path(
    str(
        ROOT
        / "tests"
        / "pass218"
        / "test_pass218_iteration42_manifest_semantic_cross_lineage_equality.py"
    )
)


def h72(domain: str, value: object) -> str:
    return hash72_digest({"domain": domain}, value)


class FakeI30Runtime:
    def __init__(self, promotion_present: bool = False) -> None:
        self.promotion_present = promotion_present
        self.promote_calls = 0

    @staticmethod
    def _request(payload):
        return Pass218I30RuntimePromotionControl._request(payload)

    def status(self):
        return {
            "target_scope": PASS218_I30_TARGET_SCOPE,
            "promotion_present": self.promotion_present,
            "atomic_promotion_invoked": self.promotion_present,
        }

    def promote(self, payload):
        self.promote_calls += 1
        raise AssertionError("I43 must never invoke I30 promote")


def prepare_i42(
    tmp_path: Path,
    *,
    source: bytes | None = None,
    context_id: str = "i43 transient request marker 71c9ab must not persist",
):
    payload = source or (
        b"I43 binds an exact frozen I30 authority grant to the exact I42 semantic identity."
    )
    lifecycle, authority, i41 = I42_HELPERS["make_i41"](tmp_path, payload)
    validator = I42_HELPERS["FakeI29Validator"]()
    validation_request = I42_HELPERS["validation_request"](
        payload,
        authority,
        context_id=context_id,
    )
    i42 = I42_HELPERS["make_i42"](
        tmp_path,
        lifecycle,
        i41,
        validator,
    )
    i42_receipt = i42.prove(validation_request)
    return payload, lifecycle, authority, validator, validation_request, i42, i42_receipt


def promotion_request(
    validation_request,
    i42_receipt,
    *,
    grantor_authority_hash72: str | None = None,
    grant_sequence: int = 7,
    expected_i29_validation_hash72: str | None = None,
    expected_validated_hash216: str | None = None,
):
    return Pass218I30PromotionRequest(
        validation_request=validation_request,
        grantor_authority_hash72=(
            grantor_authority_hash72
            or h72("HHS-P218-I43-TEST-GRANTOR-V1", {"authority": "explicit-caller"})
        ),
        grant_sequence=grant_sequence,
        expected_i29_validation_hash72=(
            expected_i29_validation_hash72
            or i42_receipt["i29_validation_hash72"]
        ),
        expected_validated_hash216=(
            expected_validated_hash216
            or i42_receipt["i29_validated_hash216"]
        ),
        target_scope=PASS218_I30_TARGET_SCOPE,
    ).validated()


def make_i43(tmp_path: Path, lifecycle, i42, validator, *, i30=None):
    i30_runtime = i30 or FakeI30Runtime()
    return Pass218I43ManifestBoundI30PromotionRequestAuthorization(
        lifecycle=lifecycle,
        i42_store=i42.store,
        i29_validator=validator,
        state_root=(
            tmp_path
            / "state"
            / "cognition"
            / "manifest-bound-i30-promotion-request-authorization-i43"
        ),
        i42_status_provider=i42.status,
        i30_status_provider=i30_runtime.status,
    )


def api_payload(request: Pass218I30PromotionRequest) -> dict:
    payload = I42_HELPERS["api_payload"](request.validation_request)
    payload["promotion_authority"] = {
        "grantor_authority_hash72": request.grantor_authority_hash72,
        "grant_sequence": request.grant_sequence,
        "expected_i29_validation_hash72": request.expected_i29_validation_hash72,
        "expected_validated_hash216": request.expected_validated_hash216,
        "target_scope": request.target_scope,
    }
    return payload


def test_i43_authorizes_exact_i30_request_without_invoking_promotion(tmp_path: Path) -> None:
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = prepare_i42(tmp_path)
    request = promotion_request(validation_request, i42_receipt)
    runtime = make_i43(tmp_path, lifecycle, i42, validator)
    receipt = runtime.authorize(request)
    proof = runtime.store.active_proof()
    assert proof is not None
    assert receipt["status"] == PASS218_I43_COMPLETE_STATUS
    assert receipt["authorization_status"] == PASS218_I43_AUTHORIZED_PENDING_STATUS
    assert receipt["i42_exact_request_identity_bound"] is True
    assert receipt["i29_independently_revalidated"] is True
    assert receipt["i30_explicit_authority_grant_present"] is True
    assert receipt["i30_grant_hash_matches_frozen_i30_derivation"] is True
    assert receipt["i30_promotion_request_authorized"] is True
    assert receipt["authorized_pending_i30_invocation"] is True
    assert receipt["pass218_i30_canonical_semantic_promotion_invoked"] is False
    assert receipt["vm5184_authoritative_projection_invoked"] is False
    assert runtime.i30_invocation_count == 0
    assert runtime.authorization_count == 1
    assert validator.validation_count == 2
    assert proof["i30_grant_hash72"] == hash72_digest(
        {"domain": "HHS-P218-I30-PROMOTION-AUTHORITY-GRANT-V1"},
        proof["grant_body"],
    )
    assert proof["i29_validation_request_sha256"] == i42_receipt[
        "i29_validation_request_sha256"
    ]


def test_i43_restart_is_idempotent_and_grant_exact(tmp_path: Path) -> None:
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = prepare_i42(tmp_path)
    request = promotion_request(validation_request, i42_receipt)
    first = make_i43(tmp_path, lifecycle, i42, validator)
    receipt = first.authorize(request)
    assert first.authorize(request) == receipt
    assert validator.validation_count == 2
    restarted = make_i43(tmp_path, lifecycle, i42, validator)
    assert restarted.authorize(request) == receipt
    assert validator.validation_count == 2
    changed = promotion_request(
        validation_request,
        i42_receipt,
        grant_sequence=request.grant_sequence + 1,
    )
    with pytest.raises(Pass218I43StateError, match="P218_I43_ACTIVE_I30_REQUEST_CONFLICT"):
        restarted.authorize(changed)


def test_i43_rejects_request_fingerprint_mismatch_before_i29_replay(tmp_path: Path) -> None:
    source, lifecycle, authority, validator, _, i42, i42_receipt = prepare_i42(tmp_path)
    alternate = I42_HELPERS["validation_request"](
        source,
        authority,
        context_id="different transient I29 request must not inherit I42 equality",
    )
    request = promotion_request(alternate, i42_receipt)
    runtime = make_i43(tmp_path, lifecycle, i42, validator)
    before = validator.validation_count
    with pytest.raises(Pass218I43BindingError, match="P218_I43_I29_REQUEST_FINGERPRINT_MISMATCH"):
        runtime.authorize(request)
    assert validator.validation_count == before
    assert runtime.store.active_record() is None


def test_i43_rejects_grant_expected_identity_mismatch(tmp_path: Path) -> None:
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = prepare_i42(tmp_path)
    wrong_validation = h72("HHS-P218-I43-WRONG-I29-VALIDATION-V1", "wrong")
    request = promotion_request(
        validation_request,
        i42_receipt,
        expected_i29_validation_hash72=wrong_validation,
    )
    runtime = make_i43(tmp_path, lifecycle, i42, validator)
    with pytest.raises(
        Pass218I43BindingError,
        match="P218_I43_I30_EXPECTED_I29_VALIDATION_MISMATCH",
    ):
        runtime.authorize(request)
    assert runtime.store.active_record() is None


def test_i43_rejects_existing_i30_promotion(tmp_path: Path) -> None:
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = prepare_i42(tmp_path)
    request = promotion_request(validation_request, i42_receipt)
    runtime = make_i43(
        tmp_path,
        lifecycle,
        i42,
        validator,
        i30=FakeI30Runtime(True),
    )
    with pytest.raises(Pass218I43BindingError, match="P218_I43_I30_PREVIOUS_PROMOTION_PENDING"):
        runtime.authorize(request)
    assert runtime.store.active_record() is None


def test_i43_persists_no_transient_i29_or_i30_request_payload(tmp_path: Path) -> None:
    marker = "i43 transient request marker 43d8af must never persist"
    source = b"I43 durable state retains identities and grant witnesses but no source payload."
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = prepare_i42(
        tmp_path,
        source=source,
        context_id=marker,
    )
    request = promotion_request(validation_request, i42_receipt)
    runtime = make_i43(tmp_path, lifecycle, i42, validator)
    runtime.authorize(request)
    for path in runtime.store.root.rglob("*"):
        if path.is_file():
            payload = path.read_bytes()
            assert source not in payload
            assert marker.encode("utf-8") not in payload
            assert b"context_id" not in payload
            assert b'"tokens"' not in payload
            assert b'"validation_request"' not in payload


def test_runtimeos_i43_authorizes_but_cannot_invoke_i30(tmp_path: Path) -> None:
    _, lifecycle, _, validator, validation_request, i42, i42_receipt = prepare_i42(tmp_path)
    request = promotion_request(validation_request, i42_receipt)
    app = FastAPI()
    i42_control = SimpleNamespace(equality=i42, status=i42.status)
    i29_control = I42_HELPERS["FakeI29Runtime"](validator)
    i30_control = FakeI30Runtime()
    control = install_pass218_i43_manifest_bound_i30_promotion_request_authorization_control(
        app,
        i42_control,
        i29_control,
        i30_control,
        lifecycle,
        state_root=tmp_path / "runtime-os-state",
    )
    client = TestClient(app)
    before = client.get(PASS218_I43_STATUS_PATH).json()
    assert before["api_can_supply_i30_authority_grant"] is True
    assert before["api_can_authorize_exact_i30_promotion_request"] is True
    assert before["api_can_invoke_i30_canonical_promotion"] is False
    response = client.post(PASS218_I43_AUTHORIZE_PATH, json=api_payload(request))
    assert response.status_code == 200
    assert response.json()["status"] == PASS218_I43_COMPLETE_STATUS
    assert response.json()["authorization_status"] == PASS218_I43_AUTHORIZED_PENDING_STATUS
    assert control.authorization.i30_invocation_count == 0
    assert i30_control.promote_calls == 0
    assert validator.validation_count == 2


def test_i43_authoritative_python_surface_contains_no_float_literals() -> None:
    paths = [
        ROOT
        / "hhs_runtime"
        / "pass218"
        / "manifest_bound_i30_promotion_request_authorization_i43.py",
        ROOT
        / "hhs_backend"
        / "runtime_os_pass218_manifest_i30_promotion_request_authorization_i43.py",
    ]
    for path in paths:
        tree = ast.parse(path.read_text("utf-8"))
        floats = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        assert not floats, str(path)

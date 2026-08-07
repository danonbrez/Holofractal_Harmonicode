from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import pytest

from hhs_backend.runtime.hhs_pass214_iteration7_live_admission_ablation_v1 import (
    ADMISSION_SCHEMA,
    CANDIDATES,
    ITERATION6_CANDIDATE_SET_ROOT,
    LIVE_CLASSIFICATION,
    PASS213_CLOSURE,
    Pass214Iteration7Error,
    build_ablation_plan,
    build_challenge,
    create_live_admission,
    inspect_runtime_dependencies,
    validate_recorded_admission,
)


def h64(char: str) -> str:
    return char * 64


def h72(char: str) -> str:
    return char * 72


class FakeProjection:
    def __init__(self, *, kind, object_id, source_root, public_data, receipt_hash72, sequence=1, prior=None, event=None):
        self.kind = kind
        self.object_id = object_id
        self.source_root_hash216 = source_root
        self.public_data = dict(public_data)
        self.receipt_hash72 = receipt_hash72
        self.sequence = sequence
        self.published_timestamp_ns = 123456789
        self.prior_event_root_hash216 = prior or h64("1")
        self.event_root_hash216 = event or h64("2")

    def to_mapping(self):
        return {
            "schema": "HHS_PASS_213_PUBLIC_PROJECTION_EVENT_V1",
            "sequence": self.sequence,
            "kind": self.kind,
            "object_id": self.object_id,
            "source_root_hash216": self.source_root_hash216,
            "receipt_hash72": self.receipt_hash72,
            "published_timestamp_ns": self.published_timestamp_ns,
            "public_data": dict(self.public_data),
            "prior_event_root_hash216": self.prior_event_root_hash216,
            "event_root_hash216": self.event_root_hash216,
        }


class FakeStore:
    def __init__(self):
        anchor = h64("a")
        tensor = h64("b")
        self.timestamp = FakeProjection(
            kind="TIMESTAMP_ANCHOR",
            object_id=anchor,
            source_root=anchor,
            receipt_hash72=h72("c"),
            public_data={
                "anchor_root_hash216": anchor,
                "authority_id": "https://tsa.example.net/rfc3161",
                "tsa_subject": "CN=Independent Timestamp Authority",
                "trust_bundle_sha256": h64("d"),
            },
            event=h64("3"),
        )
        self.tensor = FakeProjection(
            kind="MOVING_TENSOR",
            object_id=tensor,
            source_root=tensor,
            receipt_hash72=h72("e"),
            public_data={
                "tensor_root_hash216": tensor,
                "anchor_root_hash216": anchor,
                "receipt_hash72": h72("f"),
            },
            sequence=2,
            event=h64("4"),
        )
        self.published = []
        self.head = h64("4")

    def verify_chain(self):
        return True

    def summary(self):
        return {
            "projection_count": 2 + len(self.published),
            "timestamp_anchor_count": 1,
            "moving_tensor_count": 1,
            "receipt_count": len(self.published),
            "projection_head_hash216": self.head,
        }

    def latest(self, kind):
        if kind == "TIMESTAMP_ANCHOR":
            return self.timestamp
        if kind == "MOVING_TENSOR":
            return self.tensor
        if kind == "RECEIPT" and self.published:
            return self.published[-1]
        return None

    def current_head(self):
        return self.head


class FakeSurface:
    def __init__(self):
        self.store = FakeStore()

    def publish_receipt(self, *, object_id, source_root_hash216, receipt_hash72, classification, published_timestamp_ns=None):
        projection = FakeProjection(
            kind="RECEIPT",
            object_id=object_id,
            source_root=source_root_hash216,
            receipt_hash72=h72("9"),
            public_data={
                "object_id": object_id,
                "source_root_hash216": source_root_hash216,
                "receipt_hash72": receipt_hash72,
                "classification": classification,
            },
            sequence=3 + len(self.store.published),
            event=h64("8"),
        )
        self.store.published.append(projection)
        self.store.head = projection.event_root_hash216
        return projection


class FakeLedger:
    def __init__(self):
        self.record = {
            "sequence": 7,
            "receipt_hash72": h72("7"),
            "successor_state_root_hash216": h64("7"),
            "tensor_root_hash216": h64("b"),
            "lineage_root_hash216": h64("6"),
        }

    def verify_chain(self):
        return True

    def latest(self):
        return dict(self.record)


class FakeAuthority:
    def __init__(self, surface):
        self.ledger = FakeLedger()
        self.surface = surface

    def status(self):
        return {
            "schema": "HHS_PASS_213_NATIVE_DISPATCH_STATUS_V1",
            "available": True,
            "ledger_valid": True,
            "runtime_state": {
                "tensor_root_hash216": self.surface.store.tensor.public_data["tensor_root_hash216"],
                "trusted_anchor_root_hash216": self.surface.store.timestamp.public_data["anchor_root_hash216"],
                "lineage_root_hash216": h64("6"),
            },
        }


class FakeDispatchService:
    def __init__(self, surface):
        self.authority = FakeAuthority(surface)


def valid_anchor_mapping(surface):
    return {
        "anchor_root_hash216": surface.store.timestamp.public_data["anchor_root_hash216"],
        "intent": {"authority_id": "https://tsa.example.net/rfc3161"},
        "evidence": {
            "tsa_subject": "CN=Independent Timestamp Authority",
            "verification_receipt_hash216": h64("5"),
            "evidence_root_hash216": h64("e"),
            "trust_bundle_sha256": h64("d"),
            "tsa_policy_oid": "1.2.3.4",
            "gen_time_utc": "2026-08-06T20:00:00.000000Z",
        },
    }


def fake_anchor_verifier(**kwargs):
    return dict(kwargs["trusted_anchor_mapping"])


def valid_runtime():
    surface = FakeSurface()
    return surface, FakeDispatchService(surface)


def test_challenge_is_deterministic_and_bound():
    a = build_challenge(nonce="iteration7", requested_timestamp_ns=123456789)
    b = build_challenge(nonce="iteration7", requested_timestamp_ns=123456789)
    assert a == b
    assert a["pass213_closure"] == PASS213_CLOSURE
    assert a["iteration6_candidate_set_root_hash216"] == ITERATION6_CANDIDATE_SET_ROOT
    assert len(a["challenge_root_hash216"]) == 64


def test_inspection_requires_operational_rfc3161_inputs():
    surface, dispatch = valid_runtime()
    result = inspect_runtime_dependencies(surface=surface, dispatch_service=dispatch)
    assert result["ready"] is False
    assert "PASS213_OPERATIONAL_RFC3161_REVERIFICATION_INPUTS_MISSING" in result["blockers"]


def test_fixture_anchor_is_rejected_during_cross_authority_binding():
    surface, dispatch = valid_runtime()
    surface.store.timestamp.public_data["authority_id"] = "HHS FINAL EVIDENCE FIXTURE"
    result = inspect_runtime_dependencies(
        surface=surface,
        dispatch_service=dispatch,
        trusted_anchor_mapping=valid_anchor_mapping(surface),
        verifier_bundle_mapping={"ok": True},
        trust_bundle_path=Path("/tmp/trust.pem"),
        anchor_verifier=fake_anchor_verifier,
    )
    assert result["ready"] is False
    assert any("FIXTURE_OR_SYNTHETIC" in item for item in result["blockers"])


def test_tensor_dispatch_mismatch_blocks():
    surface, dispatch = valid_runtime()
    dispatch.authority.status = lambda: {
        "runtime_state": {
            "tensor_root_hash216": h64("9"),
            "trusted_anchor_root_hash216": surface.store.timestamp.public_data["anchor_root_hash216"],
            "lineage_root_hash216": h64("6"),
        }
    }
    result = inspect_runtime_dependencies(
        surface=surface,
        dispatch_service=dispatch,
        trusted_anchor_mapping=valid_anchor_mapping(surface),
        verifier_bundle_mapping={"ok": True},
        trust_bundle_path=Path("/tmp/trust.pem"),
        anchor_verifier=fake_anchor_verifier,
    )
    assert result["ready"] is False
    assert "PASS213_TENSOR_DISPATCH_BINDING_MISMATCH" in result["blockers"]


def test_live_admission_commits_candidate_challenge_and_builds_five_family_plan():
    surface, dispatch = valid_runtime()
    admission = create_live_admission(
        surface=surface,
        dispatch_service=dispatch,
        trusted_anchor_mapping=valid_anchor_mapping(surface),
        verifier_bundle_mapping={"ok": True},
        trust_bundle_path=Path("/tmp/trust.pem"),
        nonce="operational-admission",
        requested_timestamp_ns=123456789,
        anchor_verifier=fake_anchor_verifier,
        hash72_factory=lambda root: h72("a"),
    )
    assert admission["schema"] == ADMISSION_SCHEMA
    assert admission["classification"] == LIVE_CLASSIFICATION
    assert admission["candidate_execution_started"] is False
    assert len(surface.store.published) == 1
    plan = build_ablation_plan(admission)
    assert plan["family_count"] == 5
    assert [item["family"] for item in plan["families"]] == [item["family"] for item in CANDIDATES]
    assert plan["execution_policy"]["migration_active"] is False
    assert plan["execution_policy"]["pass215_authorized"] is False


def test_admission_root_tamper_rejected():
    surface, dispatch = valid_runtime()
    admission = create_live_admission(
        surface=surface,
        dispatch_service=dispatch,
        trusted_anchor_mapping=valid_anchor_mapping(surface),
        verifier_bundle_mapping={"ok": True},
        trust_bundle_path=Path("/tmp/trust.pem"),
        nonce="tamper-test",
        requested_timestamp_ns=123456789,
        anchor_verifier=fake_anchor_verifier,
        hash72_factory=lambda root: h72("b"),
    )
    tampered = deepcopy(admission)
    tampered["native_dispatch_sequence"] += 1
    with pytest.raises(Pass214Iteration7Error, match="ADMISSION_ROOT_MISMATCH"):
        validate_recorded_admission(tampered)


def test_plan_refuses_recorded_admission_without_live_recheck_flags():
    surface, dispatch = valid_runtime()
    admission = create_live_admission(
        surface=surface,
        dispatch_service=dispatch,
        trusted_anchor_mapping=valid_anchor_mapping(surface),
        verifier_bundle_mapping={"ok": True},
        trust_bundle_path=Path("/tmp/trust.pem"),
        nonce="recorded",
        requested_timestamp_ns=123456789,
        anchor_verifier=fake_anchor_verifier,
        hash72_factory=lambda root: h72("c"),
    )
    recorded = deepcopy(admission)
    recorded["trusted_timestamp_reverified_in_process"] = False
    # Recompute the record root to model a structurally coherent but non-live replay.
    from hhs_backend.runtime.hhs_pass214_iteration7_live_admission_ablation_v1 import hash216
    unsigned = {k: v for k, v in recorded.items() if k != "admission_root_hash216"}
    recorded["admission_root_hash216"] = hash216("pass214-iteration7-live-governed-admission", unsigned)
    with pytest.raises(Pass214Iteration7Error, match="REQUIRES_LIVE_RECHECK"):
        build_ablation_plan(recorded)

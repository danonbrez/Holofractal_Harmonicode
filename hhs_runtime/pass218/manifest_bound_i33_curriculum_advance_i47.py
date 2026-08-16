"""Pass 218 Iteration 47 manifest-bound one-time I33 curriculum advance.

Consumes the exact durable I46/I32 source-closure state, invokes frozen I33 once
or restart-adopts its exact receipt, proves the I30 semantic generation and
canonical root unchanged, persists only nonverbatim proof/receipt metadata, and
stops before next-source ingress, stage advancement, VM81 mutation, learning,
truth/action authority, model activation, or authoritative floating-point state.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any, Mapping, Protocol

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72
from hhs_runtime.pass218.curriculum_advance_i33 import (
    PASS218_I33_ADVANCED_STATUS,
    PASS218_I33_COMPLETE_STATUS,
    PASS218_I33_STAGE_GATE_STATUS,
    _verify_advance_receipt,
    _verify_i32_closure,
)
from hhs_runtime.pass218.manifest_bound_i32_source_closure_i46 import (
    PASS218_I46_CLOSED_PENDING_I33_STATUS,
    PASS218_I46_COMPLETE_STATUS,
    _verify_i46_proof,
    _verify_i46_receipt,
)

PASS218_I47_VERSION = "HHS-P218-I47-MANIFEST-BOUND-I33-CURRICULUM-ADVANCE-V1"
PASS218_I47_SCOPE = "PASS218_MANIFEST_BOUND_I33_CURRICULUM_ADVANCE"
PASS218_I47_PROOF_SCHEMA = "HHS-P218-I47-MANIFEST-BOUND-I33-CURRICULUM-ADVANCE-PROOF-V1"
PASS218_I47_RECEIPT_SCHEMA = "HHS-P218-I47-MANIFEST-BOUND-I33-CURRICULUM-ADVANCE-RECEIPT-V1"
PASS218_I47_STATE_SCHEMA = "HHS-P218-I47-MANIFEST-BOUND-I33-CURRICULUM-ADVANCE-STATE-V1"
PASS218_I47_STATUS_SCHEMA = "HHS-P218-I47-MANIFEST-BOUND-I33-CURRICULUM-ADVANCE-STATUS-V1"
PASS218_I47_COMPLETE_STATUS = "MANIFEST_BOUND_I33_CURRICULUM_ADVANCE_COMPLETE"
PASS218_I47_PENDING_STATUS = "MANIFEST_BOUND_I33_CURRICULUM_ADVANCE_PENDING"
_ALLOWED_I33 = {PASS218_I33_ADVANCED_STATUS, PASS218_I33_STAGE_GATE_STATUS, PASS218_I33_COMPLETE_STATUS}


class Pass218I47AdvanceError(RuntimeError):
    pass


class Pass218I47BindingError(Pass218I47AdvanceError):
    pass


class Pass218I47StateError(Pass218I47AdvanceError):
    pass


class _Lifecycle(Protocol):
    def require_ingestion_ready(self) -> None: ...


class _I46Store(Protocol):
    def active_record(self) -> dict[str, Any] | None: ...
    def active_proof(self) -> dict[str, Any] | None: ...


class _I30Store(Protocol):
    def active_generation(self) -> dict[str, Any] | None: ...
    def status(self) -> dict[str, Any]: ...


class _I33Advancer(Protocol):
    advance_count: int
    authority: Any
    i32_store: Any
    store: Any
    def advance(self) -> dict[str, Any]: ...
    def status(self) -> dict[str, Any]: ...


def _no_float(value: Any) -> None:
    if isinstance(value, float):
        raise Pass218I47BindingError("P218_I47_AUTHORITATIVE_FLOAT_FORBIDDEN")
    if isinstance(value, Mapping):
        for item in value.values():
            _no_float(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            _no_float(item)


def _bytes(value: Any) -> bytes:
    _no_float(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _copy(value: Any) -> Any:
    return json.loads(_bytes(value).decode("utf-8"))


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as handle:
        handle.write(_bytes(value) + b"\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Pass218I47StateError("P218_I47_STATE_READ_FAILED") from exc
    if not isinstance(value, dict):
        raise Pass218I47StateError("P218_I47_STATE_OBJECT_REQUIRED")
    return value


def _h72(value: object, field: str) -> str:
    text = str(value or "")
    if not validate_hash72(text):
        raise Pass218I47StateError("P218_I47_HASH72_INVALID:" + field)
    return text


def _sha(value: object, field: str) -> str:
    text = str(value or "")
    if len(text) != 64 or any(ch not in "0123456789abcdef" for ch in text):
        raise Pass218I47StateError("P218_I47_SHA256_INVALID:" + field)
    return text


def _hash216(value: object, field: str) -> str:
    text = str(value or "")
    if len(text) != 216 or any(not validate_hash72(text[i:i + 72]) for i in (0, 72, 144)):
        raise Pass218I47StateError("P218_I47_HASH216_INVALID:" + field)
    return text


def _require_flags(value: Mapping[str, Any], *, yes: tuple[str, ...], no: tuple[str, ...], code: str) -> None:
    if any(value.get(field) is not True for field in yes) or any(value.get(field) is not False for field in no):
        raise Pass218I47StateError(code)


def _verify_i30(generation: Mapping[str, Any], status: Mapping[str, Any], i46: Mapping[str, Any], proof: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    value = _copy(dict(generation))
    digest = sha256(_bytes(value)).hexdigest()
    if digest != i46.get("i30_generation_sha256") or digest != proof.get("i30_generation_sha256"):
        raise Pass218I47BindingError("P218_I47_I30_GENERATION_I46_MISMATCH")
    receipt = value.get("promotion_receipt")
    promoted = value.get("promoted_object")
    if not isinstance(receipt, Mapping) or not isinstance(promoted, Mapping):
        raise Pass218I47BindingError("P218_I47_I30_GENERATION_CONTENT_INVALID")
    checks = {
        "promotion_receipt_hash72": proof.get("i30_promotion_receipt_hash72"),
        "promoted_object_hash72": proof.get("i30_promoted_object_hash72"),
        "target_root_after_hash72": proof.get("i30_canonical_root_hash72"),
    }
    if any(receipt.get(k) != v for k, v in checks.items()):
        raise Pass218I47BindingError("P218_I47_I30_I46_IDENTITY_MISMATCH")
    if status.get("promotion_present") is not True or status.get("canonical_root_hash72") != receipt.get("target_root_after_hash72"):
        raise Pass218I47BindingError("P218_I47_I30_STATUS_MISMATCH")
    for field in ("source_text_retained", "source_token_stream_retained", "verbatim_corpus_source_retained", "curriculum_advance_permitted", "truth_promotion", "action_authority_minted", "canonical_learning_commit_invoked", "model_activation_invoked", "authoritative_float_weights_created"):
        if promoted.get(field) is not False:
            raise Pass218I47BindingError("P218_I47_I30_AUTHORITY_DRIFT:" + field)
    return value, digest


def _bind_i32(i46: Mapping[str, Any], proof: Mapping[str, Any], raw: Mapping[str, Any]) -> dict[str, Any]:
    i32 = _verify_i32_closure(raw)
    checks = {
        "source_closure_hash72": i46.get("i32_source_closure_hash72"),
        "closure_chain_root_hash72": i46.get("i32_closure_chain_root_hash72"),
        "curriculum_identity_hash72": i46.get("curriculum_identity_hash72"),
        "curriculum_position": i46.get("curriculum_position"),
        "source_id": i46.get("source_id"),
        "source_sha256": i46.get("source_sha256"),
        "source_stage": i46.get("source_stage"),
        "previous_closure_hash72": i46.get("previous_closure_hash72"),
    }
    if any(i32.get(k) != v for k, v in checks.items()):
        raise Pass218I47BindingError("P218_I47_I32_I46_IDENTITY_MISMATCH")
    if i32.get("source_closure_hash72") != proof.get("i32_source_closure_hash72") or i32.get("closure_chain_root_hash72") != proof.get("i32_closure_chain_root_hash72"):
        raise Pass218I47BindingError("P218_I47_I32_I46_PROOF_MISMATCH")
    return _copy(i32)


def _bind_i33(raw: Mapping[str, Any], i46: Mapping[str, Any], i32: Mapping[str, Any], authority: Any) -> dict[str, Any]:
    value = _verify_advance_receipt(raw)
    if value.get("advance_status") not in _ALLOWED_I33:
        raise Pass218I47StateError("P218_I47_I33_STATUS_INVALID")
    checks = {
        "authority_root_hash72": authority.record()["authority_root_hash72"],
        "manifest_hash72": authority.manifest.manifest_hash72,
        "curriculum_identity_hash72": i46.get("curriculum_identity_hash72"),
        "ordinal": i46.get("curriculum_position"),
        "source_id": i46.get("source_id"),
        "source_sha256": i46.get("source_sha256"),
        "source_stage": i46.get("source_stage"),
        "previous_closure_hash72": i46.get("previous_closure_hash72"),
        "i32_source_closure_hash72": i32.get("source_closure_hash72"),
        "i32_closure_chain_root_hash72": i32.get("closure_chain_root_hash72"),
        "i32_closure_hash216": i32.get("closure_hash216"),
    }
    if any(value.get(k) != v for k, v in checks.items()):
        raise Pass218I47StateError("P218_I47_I33_BINDING_MISMATCH")
    _require_flags(
        value,
        yes=("source_binding_matches_authoritative_manifest", "upstream_semantic_curriculum_binding_verified", "curriculum_advance_permitted", "curriculum_cursor_advanced"),
        no=("stage_advance_permitted", "vm81_authorization_invoked", "truth_promotion", "action_authority_minted", "canonical_learning_commit_invoked", "model_activation_invoked", "verbatim_corpus_source_retained", "physical_memory_erasure_claimed", "external_source_storage_erasure_claimed", "authoritative_float_weights_created"),
        code="P218_I47_I33_AUTHORITY_DRIFT",
    )
    return _copy(value)


def _verify_receipt(value: Mapping[str, Any]) -> dict[str, Any]:
    record = _copy(dict(value))
    if record.get("schema") != PASS218_I47_RECEIPT_SCHEMA or record.get("status") != PASS218_I47_COMPLETE_STATUS or record.get("curriculum_status") not in _ALLOWED_I33:
        raise Pass218I47StateError("P218_I47_RECEIPT_HEADER_INVALID")
    for field in ("i46_receipt_hash72", "i32_source_closure_hash72", "i33_advance_receipt_hash72", "i33_transition_hash72", "manifest_bound_i33_curriculum_advance_hash72", "i47_validation_hash72", "i47_receipt_hash72"):
        _h72(record.get(field), field)
    _sha(record.get("i30_generation_sha256"), "i30_generation_sha256")
    _hash216(record.get("i47_hash216"), "i47_hash216")
    _require_flags(
        record,
        yes=("i46_complete_source_closure_verified", "i32_exact_closure_verified", "i33_curriculum_advance_invoked", "i33_advance_receipt_committed", "curriculum_cursor_advanced", "i30_semantic_generation_unchanged_across_advance", "restart_safe_exact_advance_adoption"),
        no=("i33_advance_request_persisted", "next_source_ingress_invoked", "stage_advance_permitted", "vm81_authorization_invoked", "truth_promotion", "action_authority_minted", "canonical_learning_commit_invoked", "model_activation_invoked", "verbatim_corpus_source_retained", "physical_memory_erasure_claimed", "external_source_storage_erasure_claimed", "authoritative_float_weights_created"),
        code="P218_I47_RECEIPT_AUTHORITY_DRIFT",
    )
    body = {k: v for k, v in record.items() if k not in {"i47_receipt_hash72", "i47_hash216", "i47_hash216_semantics"}}
    expected = hash72_digest({"domain": PASS218_I47_RECEIPT_SCHEMA}, body)
    if expected != record.get("i47_receipt_hash72") or record.get("i47_hash216") != str(record["i46_receipt_hash72"]) + str(record["i33_advance_receipt_hash72"]) + expected:
        raise Pass218I47StateError("P218_I47_RECEIPT_HASH_MISMATCH")
    return record


def _verify_proof(value: Mapping[str, Any], receipt: Mapping[str, Any] | None = None) -> dict[str, Any]:
    record = _copy(dict(value))
    if record.get("schema") != PASS218_I47_PROOF_SCHEMA or record.get("status") != PASS218_I47_COMPLETE_STATUS:
        raise Pass218I47StateError("P218_I47_PROOF_HEADER_INVALID")
    _h72(record.get("manifest_bound_i33_curriculum_advance_hash72"), "manifest_bound_i33_curriculum_advance_hash72")
    _require_flags(
        record,
        yes=("i46_complete_source_closure_verified", "i32_exact_closure_verified", "i33_authoritative_manifest_binding_verified", "i33_advance_receipt_committed", "i33_exactly_once_or_restart_adoption_verified", "restart_does_not_require_duplicate_i33_invocation", "curriculum_cursor_advanced", "i30_semantic_generation_unchanged_across_advance", "i30_canonical_root_unchanged_across_advance"),
        no=("source_payload_persisted", "next_source_ingress_invoked", "stage_advance_permitted", "vm81_authorization_invoked", "truth_promotion", "action_authority_minted", "canonical_learning_commit_invoked", "model_activation_invoked", "verbatim_corpus_source_retained", "authoritative_float_weights_created"),
        code="P218_I47_PROOF_AUTHORITY_DRIFT",
    )
    body = {k: v for k, v in record.items() if k != "manifest_bound_i33_curriculum_advance_hash72"}
    expected = hash72_digest({"domain": PASS218_I47_PROOF_SCHEMA}, body)
    if expected != record.get("manifest_bound_i33_curriculum_advance_hash72") or (receipt is not None and expected != receipt.get("manifest_bound_i33_curriculum_advance_hash72")):
        raise Pass218I47StateError("P218_I47_PROOF_HASH_MISMATCH")
    return record


class Pass218I47AdvanceStore:
    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).resolve()
        self.receipt_path = self.root / "receipt.json"
        self.proof_path = self.root / "proof.json"
        self.state_path = self.root / "state.json"

    def active_record(self) -> dict[str, Any] | None:
        if not self.state_path.exists():
            return None
        state = _read(self.state_path)
        body = {k: v for k, v in state.items() if k != "state_root_hash72"}
        if state.get("schema") != PASS218_I47_STATE_SCHEMA or hash72_digest({"domain": PASS218_I47_STATE_SCHEMA}, body) != state.get("state_root_hash72"):
            raise Pass218I47StateError("P218_I47_STATE_INVALID")
        receipt = _verify_receipt(_read(self.receipt_path))
        proof = _verify_proof(_read(self.proof_path), receipt)
        if state.get("active_i47_receipt_hash72") != receipt["i47_receipt_hash72"] or state.get("active_proof_hash72") != proof["manifest_bound_i33_curriculum_advance_hash72"]:
            raise Pass218I47StateError("P218_I47_STATE_BINDING_MISMATCH")
        return receipt

    def active_proof(self) -> dict[str, Any] | None:
        receipt = self.active_record()
        return None if receipt is None else _verify_proof(_read(self.proof_path), receipt)

    def commit(self, receipt: Mapping[str, Any], proof: Mapping[str, Any]) -> dict[str, Any]:
        checked = _verify_receipt(receipt)
        checked_proof = _verify_proof(proof, checked)
        existing = self.active_record()
        if existing is not None:
            if existing != checked or self.active_proof() != checked_proof:
                raise Pass218I47StateError("P218_I47_ACTIVE_BINDING_CONFLICT")
            return existing
        _write(self.receipt_path, checked)
        _write(self.proof_path, checked_proof)
        body = {
            "schema": PASS218_I47_STATE_SCHEMA,
            "version": PASS218_I47_VERSION,
            "status": PASS218_I47_COMPLETE_STATUS,
            "curriculum_status": checked["curriculum_status"],
            "active_i47_receipt_hash72": checked["i47_receipt_hash72"],
            "active_proof_hash72": checked_proof["manifest_bound_i33_curriculum_advance_hash72"],
        }
        _write(self.state_path, {**body, "state_root_hash72": hash72_digest({"domain": PASS218_I47_STATE_SCHEMA}, body)})
        persisted = self.active_record()
        if persisted != checked:
            raise Pass218I47StateError("P218_I47_DURABLE_REPLAY_MISMATCH")
        return persisted


class Pass218I47ManifestBoundI33CurriculumAdvance:
    def __init__(self, *, lifecycle: _Lifecycle, i46_store: _I46Store, i30_store: _I30Store, i33_advancer: _I33Advancer, state_root: str | os.PathLike[str]) -> None:
        self.lifecycle = lifecycle
        self.i46_store = i46_store
        self.i30_store = i30_store
        self.i33_advancer = i33_advancer
        self.store = Pass218I47AdvanceStore(state_root)
        self.i33_invocation_count = 0
        self.restart_adoption_count = 0
        self.last_error_code: str | None = None

    def _inputs(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Any, dict[str, Any], str]:
        raw_i46 = self.i46_store.active_record()
        raw_proof = self.i46_store.active_proof()
        if not isinstance(raw_i46, Mapping) or not isinstance(raw_proof, Mapping):
            raise Pass218I47BindingError("P218_I47_I46_COMPLETE_SOURCE_CLOSURE_REQUIRED")
        i46 = _verify_i46_receipt(raw_i46)
        proof = _verify_i46_proof(raw_proof, i46)
        if i46.get("status") != PASS218_I46_COMPLETE_STATUS or i46.get("closure_status") != PASS218_I46_CLOSED_PENDING_I33_STATUS or i46.get("pass218_i33_curriculum_advance_invoked") is not False:
            raise Pass218I47BindingError("P218_I47_I46_PENDING_I33_REQUIRED")
        raw_i32 = self.i33_advancer.i32_store.active_record()
        if not isinstance(raw_i32, Mapping):
            raise Pass218I47BindingError("P218_I47_I32_CLOSURE_REQUIRED")
        i32 = _bind_i32(i46, proof, raw_i32)
        authority = self.i33_advancer.authority
        if authority is None:
            raise Pass218I47BindingError("P218_I47_I33_AUTHORITATIVE_CURRICULUM_REQUIRED")
        authority.validated()
        if authority.manifest.curriculum_identity_hash72 != i46.get("curriculum_identity_hash72"):
            raise Pass218I47BindingError("P218_I47_I33_CURRICULUM_IDENTITY_MISMATCH")
        generation = self.i30_store.active_generation()
        if not isinstance(generation, Mapping):
            raise Pass218I47BindingError("P218_I47_I30_DURABLE_GENERATION_REQUIRED")
        generation_value, digest = _verify_i30(generation, self.i30_store.status(), i46, proof)
        return i46, proof, i32, authority, generation_value, digest

    @staticmethod
    def _build(i46: Mapping[str, Any], proof46: Mapping[str, Any], i32: Mapping[str, Any], i33: Mapping[str, Any], i30_sha: str) -> tuple[dict[str, Any], dict[str, Any]]:
        common = {
            "curriculum_status": i33["advance_status"],
            "i46_receipt_hash72": i46["i46_receipt_hash72"],
            "i32_source_closure_hash72": i32["source_closure_hash72"],
            "i32_closure_chain_root_hash72": i32["closure_chain_root_hash72"],
            "curriculum_identity_hash72": i46["curriculum_identity_hash72"],
            "curriculum_position": i46["curriculum_position"],
            "source_id": i46["source_id"],
            "source_sha256": i46["source_sha256"],
            "source_stage": i46["source_stage"],
            "previous_closure_hash72": i46["previous_closure_hash72"],
            "i30_generation_sha256": i30_sha,
            "i33_advance_receipt_hash72": i33["advance_receipt_hash72"],
            "i33_transition_hash72": i33["transition_hash72"],
            "i33_cursor_state_sha256": i33["cursor_state_sha256"],
            "i33_advance_hash216": i33["advance_hash216"],
            "next_expected_ordinal": i33["next_expected_ordinal"],
            "next_expected_source_id": i33["next_expected_source_id"],
            "next_expected_stage": i33["next_expected_stage"],
            "stage_transition_required": i33["stage_transition_required"],
        }
        proof_body = {
            "schema": PASS218_I47_PROOF_SCHEMA,
            "version": PASS218_I47_VERSION,
            "scope": PASS218_I47_SCOPE,
            "status": PASS218_I47_COMPLETE_STATUS,
            **common,
            "manifest_bound_i32_source_closure_hash72": i46["manifest_bound_i32_source_closure_hash72"],
            "i30_canonical_root_hash72": proof46["i30_canonical_root_hash72"],
            "i33_authority_root_hash72": i33["authority_root_hash72"],
            "i33_manifest_hash72": i33["manifest_hash72"],
            "i46_complete_source_closure_verified": True,
            "i32_exact_closure_verified": True,
            "i33_authoritative_manifest_binding_verified": True,
            "i33_advance_receipt_committed": True,
            "i33_exactly_once_or_restart_adoption_verified": True,
            "restart_does_not_require_duplicate_i33_invocation": True,
            "curriculum_cursor_advanced": True,
            "i30_semantic_generation_unchanged_across_advance": True,
            "i30_canonical_root_unchanged_across_advance": True,
            "source_payload_persisted": False,
            "next_source_ingress_invoked": False,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
        }
        proof_hash = hash72_digest({"domain": PASS218_I47_PROOF_SCHEMA}, proof_body)
        proof = {**proof_body, "manifest_bound_i33_curriculum_advance_hash72": proof_hash}
        validation = hash72_digest({"domain": "HHS-P218-I47-CURRICULUM-ADVANCE-VALIDATION-V1"}, {"i46_receipt_hash72": i46["i46_receipt_hash72"], "i33_advance_receipt_hash72": i33["advance_receipt_hash72"], "i30_generation_sha256": i30_sha, "next_expected_ordinal": i33["next_expected_ordinal"]})
        body = {
            "schema": PASS218_I47_RECEIPT_SCHEMA,
            "version": PASS218_I47_VERSION,
            "scope": PASS218_I47_SCOPE,
            "status": PASS218_I47_COMPLETE_STATUS,
            **common,
            "manifest_bound_i33_curriculum_advance_hash72": proof_hash,
            "i47_validation_hash72": validation,
            "i46_complete_source_closure_verified": True,
            "i32_exact_closure_verified": True,
            "i33_curriculum_advance_invoked": True,
            "i33_advance_receipt_committed": True,
            "curriculum_cursor_advanced": True,
            "i30_semantic_generation_unchanged_across_advance": True,
            "restart_safe_exact_advance_adoption": True,
            "i33_advance_request_persisted": False,
            "next_source_ingress_invoked": False,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "canonical_learning_commit_invoked": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "physical_memory_erasure_claimed": False,
            "external_source_storage_erasure_claimed": False,
            "authoritative_float_weights_created": False,
        }
        receipt_hash = hash72_digest({"domain": PASS218_I47_RECEIPT_SCHEMA}, body)
        receipt = {**body, "i47_receipt_hash72": receipt_hash, "i47_hash216": str(i46["i46_receipt_hash72"]) + str(i33["advance_receipt_hash72"]) + receipt_hash, "i47_hash216_semantics": ["I46_MANIFEST_BOUND_SOURCE_CLOSURE_RECEIPT", "I33_AUTHORITATIVE_CURRICULUM_ADVANCE_RECEIPT", "I47_MANIFEST_BOUND_CURRICULUM_ADVANCE_RECEIPT"]}
        return _verify_proof(proof), _verify_receipt(receipt)

    def advance(self) -> dict[str, Any]:
        try:
            self.lifecycle.require_ingestion_ready()
            i46, proof46, i32, authority, before, before_sha = self._inputs()
            active47 = self.store.active_record()
            active33 = self.i33_advancer.store.last_receipt()
            if active47 is not None:
                if not isinstance(active33, Mapping):
                    raise Pass218I47StateError("P218_I47_ACTIVE_I33_RECEIPT_MISSING")
                checked = _bind_i33(active33, i46, i32, authority)
                if checked["advance_receipt_hash72"] != active47["i33_advance_receipt_hash72"] or active47["i30_generation_sha256"] != before_sha:
                    raise Pass218I47StateError("P218_I47_ACTIVE_BINDING_CONFLICT")
                return active47
            if isinstance(active33, Mapping):
                i33 = _bind_i33(active33, i46, i32, authority)
                self.restart_adoption_count += 1
            else:
                cursor = self.i33_advancer.store.current_cursor(authority)
                expected = cursor.expected_source(authority.manifest)
                if cursor.next_ordinal != int(i46["curriculum_position"]) or expected is None or expected.get("source_id") != i46.get("source_id"):
                    raise Pass218I47BindingError("P218_I47_I33_CURSOR_SOURCE_MISMATCH")
                count = int(self.i33_advancer.advance_count)
                returned = self.i33_advancer.advance()
                self.i33_invocation_count += 1
                if int(self.i33_advancer.advance_count) != count + 1:
                    raise Pass218I47StateError("P218_I47_I33_SINGLE_INVOCATION_NOT_PROVEN")
                active33 = self.i33_advancer.store.last_receipt()
                if not isinstance(active33, Mapping):
                    raise Pass218I47StateError("P218_I47_I33_DURABLE_RECEIPT_MISSING")
                i33 = _bind_i33(active33, i46, i32, authority)
                if _copy(returned) != i33:
                    raise Pass218I47StateError("P218_I47_I33_RETURNED_RECEIPT_MISMATCH")
            _, _, _, _, after, after_sha = self._inputs()
            if before != after or before_sha != after_sha or i32.get("canonical_root_hash72") != proof46.get("i30_canonical_root_hash72"):
                raise Pass218I47StateError("P218_I47_I30_CHANGED_DURING_ADVANCE")
            proof, receipt = self._build(i46, proof46, i32, i33, before_sha)
            persisted = self.store.commit(receipt, proof)
            self.last_error_code = None
            return persisted
        except Exception as exc:
            text = str(exc).strip()
            self.last_error_code = text.split(":", 1)[0] if text else exc.__class__.__name__
            raise

    def status(self) -> dict[str, Any]:
        active = self.store.active_record()
        i33 = self.i33_advancer.status()
        return {
            "schema": PASS218_I47_STATUS_SCHEMA,
            "version": PASS218_I47_VERSION,
            "status": PASS218_I47_COMPLETE_STATUS if active is not None else PASS218_I47_PENDING_STATUS,
            "curriculum_status": None if active is None else active["curriculum_status"],
            "active_i47_receipt_hash72": None if active is None else active["i47_receipt_hash72"],
            "active_i33_advance_receipt_hash72": None if active is None else active["i33_advance_receipt_hash72"],
            "i33_invocation_count_current_process": self.i33_invocation_count,
            "restart_adoption_count_current_process": self.restart_adoption_count,
            "i33_authoritative_curriculum_ready": bool(i33.get("authoritative_curriculum_ready")),
            "curriculum_cursor_advanced": active is not None,
            "next_source_ingress_invoked": False,
            "stage_advance_permitted": False,
            "vm81_authorization_invoked": False,
            "canonical_learning_commit_invoked": False,
            "truth_promotion": False,
            "action_authority_minted": False,
            "model_activation_invoked": False,
            "verbatim_corpus_source_retained": False,
            "authoritative_float_weights_created": False,
            "i47_error_code": self.last_error_code,
        }


__all__ = [
    "PASS218_I47_COMPLETE_STATUS", "PASS218_I47_PENDING_STATUS", "PASS218_I47_PROOF_SCHEMA",
    "PASS218_I47_RECEIPT_SCHEMA", "PASS218_I47_SCOPE", "PASS218_I47_STATE_SCHEMA",
    "PASS218_I47_STATUS_SCHEMA", "PASS218_I47_VERSION", "Pass218I47AdvanceError",
    "Pass218I47AdvanceStore", "Pass218I47BindingError", "Pass218I47ManifestBoundI33CurriculumAdvance",
    "Pass218I47StateError", "_verify_proof", "_verify_receipt",
]

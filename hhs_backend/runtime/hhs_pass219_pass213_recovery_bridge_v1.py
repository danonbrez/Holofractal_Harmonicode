"""Pass 219 1.33 bridge from validated Pass 213 recovery evidence to VM81.

This module does not grant canonical mutation authority.  It validates the
existing Pass 213 persistent-inventory, dual-PQC checkpoint, and RFC3161 anchor
chain, then authenticates the exact roots together with the native 1.32
checkpoint/registry/candidate identity under a domain-separated key derived
from the existing VM81 firewall root.  Native 1.33 verifies that authenticator
before candidate-only recovery is allowed to reach the hidden 1.32 primitive.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import hmac
from typing import Any

from hhs_backend.runtime.hhs_pass213_persistent_inventory_v1 import InventoryCheckpoint
from hhs_backend.runtime.hhs_pass213_pqc_enclosure_v1 import (
    PQCVerifierBundle,
    SignedInventoryCheckpoint,
)
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import (
    RFC3161TimestampVerifier,
    TrustedTimestampAnchorRecord,
)

VERSION = 0x00010021
ROOT_BYTES = 32
AUTH_BYTES = 64
ROOT_KEY_BYTES = 64
ROOT_KEY_ENV = "HHS_VM81_PQC_FIREWALL_KEY_HEX"
KEY_DOMAIN = b"HHS-P219-PASS213-RECOVERY-BRIDGE-KEY-V1"
AUTH_DOMAIN = b"HHS-P219-PASS213-RECOVERY-BRIDGE-AUTH-V1"
EVIDENCE_DOMAIN = b"HHS-P219-PASS213-RECOVERY-EVIDENCE-V1"


class Pass219Pass213RecoveryBridgeError(RuntimeError):
    pass


def _root(value: str, code: str, *, allow_zero: bool = False) -> bytes:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass219Pass213RecoveryBridgeError(code)
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise Pass219Pass213RecoveryBridgeError(code) from exc
    if len(raw) != ROOT_BYTES or (not allow_zero and not any(raw)):
        raise Pass219Pass213RecoveryBridgeError(code)
    return raw


def _sha256(value: bytes, code: str) -> bytes:
    if not isinstance(value, bytes) or len(value) != ROOT_BYTES or not any(value):
        raise Pass219Pass213RecoveryBridgeError(code)
    return value


def _candidate_hash72(value: str) -> bytes:
    if not isinstance(value, str) or len(value) != 72:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_CANDIDATE_HASH72_INVALID")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise Pass219Pass213RecoveryBridgeError(
            "PASS219_PASS213_CANDIDATE_HASH72_INVALID"
        ) from exc
    if len(encoded) != 72:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_CANDIDATE_HASH72_INVALID")
    return encoded


def _u32(value: int) -> bytes:
    if value < 0 or value > 0xFFFFFFFF:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_U32_INVALID")
    return int(value).to_bytes(4, "big")


def _u64(value: int) -> bytes:
    if value < 0 or value > 0xFFFFFFFFFFFFFFFF:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_U64_INVALID")
    return int(value).to_bytes(8, "big")


def parse_firewall_root_key_hex(value: str) -> bytes:
    if not isinstance(value, str) or len(value) != ROOT_KEY_BYTES * 2:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_ROOT_KEY_INVALID")
    try:
        key = bytes.fromhex(value)
    except ValueError as exc:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_ROOT_KEY_INVALID") from exc
    if len(key) != ROOT_KEY_BYTES or not any(key):
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_ROOT_KEY_INVALID")
    return key


@dataclass(frozen=True)
class Pass219Pass213RecoveryEvidenceV1:
    signed_sequence: int
    checkpoint_sequence: int
    inventory_checkpoint_root_hash216: bytes
    inventory_root_hash216: bytes
    signed_checkpoint_root_hash216: bytes
    verifier_bundle_root_hash216: bytes
    timestamp_intent_root_hash216: bytes
    timestamp_evidence_root_hash216: bytes
    timestamp_anchor_root_hash216: bytes
    timestamp_verification_receipt_hash216: bytes
    hash216_lineage_root: bytes
    prior_anchor_root_hash216: bytes
    trust_bundle_sha256: bytes
    message_imprint_sha256: bytes
    bridge_authenticator: bytes

    def roots(self) -> tuple[bytes, ...]:
        return (
            self.inventory_checkpoint_root_hash216,
            self.inventory_root_hash216,
            self.signed_checkpoint_root_hash216,
            self.verifier_bundle_root_hash216,
            self.timestamp_intent_root_hash216,
            self.timestamp_evidence_root_hash216,
            self.timestamp_anchor_root_hash216,
            self.timestamp_verification_receipt_hash216,
            self.hash216_lineage_root,
            self.prior_anchor_root_hash216,
            self.trust_bundle_sha256,
            self.message_imprint_sha256,
        )

    def to_mapping(self) -> dict[str, Any]:
        names = (
            "inventory_checkpoint_root_hash216",
            "inventory_root_hash216",
            "signed_checkpoint_root_hash216",
            "verifier_bundle_root_hash216",
            "timestamp_intent_root_hash216",
            "timestamp_evidence_root_hash216",
            "timestamp_anchor_root_hash216",
            "timestamp_verification_receipt_hash216",
            "hash216_lineage_root",
            "prior_anchor_root_hash216",
            "trust_bundle_sha256",
            "message_imprint_sha256",
        )
        return {
            "schema": "HHS_PASS_219_PASS213_RECOVERY_EVIDENCE_V1",
            "version": VERSION,
            "signed_sequence": self.signed_sequence,
            "checkpoint_sequence": self.checkpoint_sequence,
            **{name: value.hex() for name, value in zip(names, self.roots())},
            "bridge_authenticator": self.bridge_authenticator.hex(),
        }


def evidence_material(
    evidence: Pass219Pass213RecoveryEvidenceV1,
    *,
    native_checkpoint_root_sha256: bytes,
    native_registry_root_sha256: bytes,
    native_candidate_hash72: str,
) -> bytes:
    checkpoint_root = _sha256(
        native_checkpoint_root_sha256, "PASS219_PASS213_NATIVE_CHECKPOINT_ROOT_INVALID"
    )
    registry_root = _sha256(
        native_registry_root_sha256, "PASS219_PASS213_NATIVE_REGISTRY_ROOT_INVALID"
    )
    return b"".join(
        (
            EVIDENCE_DOMAIN,
            _u32(VERSION),
            _u64(evidence.signed_sequence),
            _u64(evidence.checkpoint_sequence),
            *evidence.roots(),
            checkpoint_root,
            registry_root,
            _candidate_hash72(native_candidate_hash72),
        )
    )


def authenticate_evidence(
    evidence: Pass219Pass213RecoveryEvidenceV1,
    *,
    root_key: bytes,
    native_checkpoint_root_sha256: bytes,
    native_registry_root_sha256: bytes,
    native_candidate_hash72: str,
) -> Pass219Pass213RecoveryEvidenceV1:
    if not isinstance(root_key, bytes) or len(root_key) != ROOT_KEY_BYTES or not any(root_key):
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_ROOT_KEY_INVALID")
    material = evidence_material(
        evidence,
        native_checkpoint_root_sha256=native_checkpoint_root_sha256,
        native_registry_root_sha256=native_registry_root_sha256,
        native_candidate_hash72=native_candidate_hash72,
    )
    bridge_key = hmac.new(root_key, KEY_DOMAIN, "sha512").digest()
    authenticator = hmac.new(bridge_key, AUTH_DOMAIN + material, "sha512").digest()
    return Pass219Pass213RecoveryEvidenceV1(
        **{
            **evidence.__dict__,
            "bridge_authenticator": authenticator,
        }
    )


def build_validated_pass213_recovery_evidence(
    *,
    anchor_record: TrustedTimestampAnchorRecord,
    verifier_bundle: PQCVerifierBundle,
    timestamp_verifier: RFC3161TimestampVerifier,
    inventory_key: bytes,
    root_key: bytes,
    expected_hash216_lineage_root: str,
    native_checkpoint_sequence: int,
    native_checkpoint_root_sha256: bytes,
    native_registry_root_sha256: bytes,
    native_candidate_hash72: str,
) -> Pass219Pass213RecoveryEvidenceV1:
    """Validate the full Pass213 chain and return an authenticated native bridge record."""
    if native_checkpoint_sequence < 1:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_NATIVE_SEQUENCE_INVALID")
    anchor_record.validate(
        verifier_bundle=verifier_bundle,
        timestamp_verifier=timestamp_verifier,
    )
    signed = SignedInventoryCheckpoint.from_mapping(anchor_record.signed_checkpoint)
    signed.validate(verifier_bundle)
    checkpoint = InventoryCheckpoint.from_mapping(signed.checkpoint)
    checkpoint.validate(inventory_key)
    if anchor_record.intent.hash216_lineage_root != expected_hash216_lineage_root:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_HASH216_LINEAGE_MISMATCH")
    if signed.signed_sequence != anchor_record.intent.signed_sequence:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_SIGNED_SEQUENCE_MISMATCH")
    if checkpoint.checkpoint_sequence < 1:
        raise Pass219Pass213RecoveryBridgeError("PASS219_PASS213_INVENTORY_SEQUENCE_INVALID")

    provisional = Pass219Pass213RecoveryEvidenceV1(
        signed_sequence=signed.signed_sequence,
        checkpoint_sequence=native_checkpoint_sequence,
        inventory_checkpoint_root_hash216=_root(
            checkpoint.checkpoint_root_hash216,
            "PASS219_PASS213_INVENTORY_CHECKPOINT_ROOT_INVALID",
        ),
        inventory_root_hash216=_root(
            checkpoint.inventory_root_hash216,
            "PASS219_PASS213_INVENTORY_ROOT_INVALID",
        ),
        signed_checkpoint_root_hash216=_root(
            signed.signed_checkpoint_root_hash216,
            "PASS219_PASS213_SIGNED_CHECKPOINT_ROOT_INVALID",
        ),
        verifier_bundle_root_hash216=_root(
            verifier_bundle.bundle_root_hash216,
            "PASS219_PASS213_VERIFIER_BUNDLE_ROOT_INVALID",
        ),
        timestamp_intent_root_hash216=_root(
            anchor_record.intent.intent_root_hash216,
            "PASS219_PASS213_TIMESTAMP_INTENT_ROOT_INVALID",
        ),
        timestamp_evidence_root_hash216=_root(
            anchor_record.evidence.evidence_root_hash216,
            "PASS219_PASS213_TIMESTAMP_EVIDENCE_ROOT_INVALID",
        ),
        timestamp_anchor_root_hash216=_root(
            anchor_record.anchor_root_hash216,
            "PASS219_PASS213_TIMESTAMP_ANCHOR_ROOT_INVALID",
        ),
        timestamp_verification_receipt_hash216=_root(
            anchor_record.evidence.verification_receipt_hash216,
            "PASS219_PASS213_TIMESTAMP_RECEIPT_ROOT_INVALID",
        ),
        hash216_lineage_root=_root(
            anchor_record.intent.hash216_lineage_root,
            "PASS219_PASS213_HASH216_LINEAGE_ROOT_INVALID",
        ),
        prior_anchor_root_hash216=_root(
            anchor_record.intent.prior_anchor_root_hash216,
            "PASS219_PASS213_PRIOR_ANCHOR_ROOT_INVALID",
            allow_zero=True,
        ),
        trust_bundle_sha256=_root(
            anchor_record.evidence.trust_bundle_sha256,
            "PASS219_PASS213_TRUST_BUNDLE_SHA256_INVALID",
        ),
        message_imprint_sha256=_root(
            anchor_record.evidence.message_imprint_sha256,
            "PASS219_PASS213_MESSAGE_IMPRINT_SHA256_INVALID",
        ),
        bridge_authenticator=b"\0" * AUTH_BYTES,
    )
    return authenticate_evidence(
        provisional,
        root_key=root_key,
        native_checkpoint_root_sha256=native_checkpoint_root_sha256,
        native_registry_root_sha256=native_registry_root_sha256,
        native_candidate_hash72=native_candidate_hash72,
    )


def evidence_root_sha256(
    evidence: Pass219Pass213RecoveryEvidenceV1,
    *,
    native_checkpoint_root_sha256: bytes,
    native_registry_root_sha256: bytes,
    native_candidate_hash72: str,
) -> str:
    return sha256(
        evidence_material(
            evidence,
            native_checkpoint_root_sha256=native_checkpoint_root_sha256,
            native_registry_root_sha256=native_registry_root_sha256,
            native_candidate_hash72=native_candidate_hash72,
        )
    ).hexdigest()

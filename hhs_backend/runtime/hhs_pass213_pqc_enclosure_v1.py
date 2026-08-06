"""Pass 213 iteration 6: post-quantum checkpoint and recovery enclosure.

The module binds the persistent inventory checkpoints established by iteration 5
into a dual-signature chain and protects recovery root material with an ML-KEM
KEM/DEM capsule. Private keys reside in iteration 3 native secure arenas and are
loaded only for bounded signing or decapsulation operations.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import asdict, dataclass
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Sequence

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    ZERO_HASH216,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_persistent_inventory_v1 import (
    InventoryCheckpoint,
)
from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import (
    NativeSecureArena,
    SecureMemoryReceipt,
)

ITERATION = 6
RUNTIME_CLASSIFICATION = "HHS_PASS_213_PQC_CHECKPOINT_ENCLOSURE_ITERATION6"
DEFAULT_ML_KEM = "ML-KEM-768"
DEFAULT_ML_DSA = "ML-DSA-65"
DEFAULT_SLH_DSA_QUERY = ("SLH-DSA", "SHA2", "128s")


class Pass213PQCError(RuntimeError):
    """Raised when a post-quantum enclosure invariant fails."""


def _oqs_module() -> Any:
    try:
        import oqs  # type: ignore
    except ImportError as exc:
        raise Pass213PQCError("PASS213_LIBOQS_PYTHON_REQUIRED") from exc
    return oqs


def _require_bytes(value: bytes, code: str, minimum: int = 1) -> bytes:
    if not isinstance(value, bytes) or len(value) < minimum:
        raise Pass213PQCError(code)
    return value


def _require_hash216(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213PQCError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213PQCError(code) from exc
    return value


def _b64(value: bytes) -> str:
    return b64encode(value).decode("ascii")


def _unb64(value: str, code: str) -> bytes:
    try:
        return b64decode(value.encode("ascii"), validate=True)
    except Exception as exc:
        raise Pass213PQCError(code) from exc


def _normalize_algorithm(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def _resolve_algorithm(
    enabled: Sequence[str],
    *,
    exact: str | None = None,
    required_tokens: Sequence[str] = (),
) -> str:
    enabled_tuple = tuple(str(item) for item in enabled)
    if exact is not None:
        target = _normalize_algorithm(exact)
        for item in enabled_tuple:
            if _normalize_algorithm(item) == target:
                return item
    tokens = tuple(_normalize_algorithm(item) for item in required_tokens)
    matches = [
        item
        for item in enabled_tuple
        if all(token in _normalize_algorithm(item) for token in tokens)
    ]
    if not matches:
        raise Pass213PQCError("PASS213_REQUIRED_PQC_ALGORITHM_UNAVAILABLE")
    return sorted(matches, key=lambda item: (len(item), item))[0]


@dataclass(frozen=True)
class PQCAlgorithmSuite:
    ml_kem: str
    ml_dsa: str
    slh_dsa: str
    liboqs_version: str
    liboqs_python_version: str

    @classmethod
    def detect(cls) -> "PQCAlgorithmSuite":
        oqs = _oqs_module()
        return cls(
            ml_kem=_resolve_algorithm(
                oqs.get_enabled_kem_mechanisms(), exact=DEFAULT_ML_KEM
            ),
            ml_dsa=_resolve_algorithm(
                oqs.get_enabled_sig_mechanisms(), exact=DEFAULT_ML_DSA
            ),
            slh_dsa=_resolve_algorithm(
                oqs.get_enabled_sig_mechanisms(),
                required_tokens=DEFAULT_SLH_DSA_QUERY,
            ),
            liboqs_version=str(oqs.oqs_version()),
            liboqs_python_version=str(oqs.oqs_python_version()),
        )

    def to_mapping(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class PQCPublicKeyRecord:
    role: str
    algorithm: str
    public_key_b64: str
    public_key_hash216: str

    @classmethod
    def create(cls, role: str, algorithm: str, public_key: bytes) -> "PQCPublicKeyRecord":
        if role not in {"recovery-kem", "operational-signature", "archival-signature"}:
            raise Pass213PQCError("PASS213_PQC_KEY_ROLE_INVALID")
        raw = _require_bytes(public_key, "PASS213_PQC_PUBLIC_KEY_EMPTY")
        return cls(
            role=role,
            algorithm=algorithm,
            public_key_b64=_b64(raw),
            public_key_hash216=hash216(
                "pqc-public-key",
                canonical_bytes(
                    {"role": role, "algorithm": algorithm, "public_key": _b64(raw)}
                ),
            ),
        )

    def public_key(self) -> bytes:
        raw = _unb64(self.public_key_b64, "PASS213_PQC_PUBLIC_KEY_ENCODING_INVALID")
        expected = hash216(
            "pqc-public-key",
            canonical_bytes(
                {"role": self.role, "algorithm": self.algorithm, "public_key": self.public_key_b64}
            ),
        )
        if not hmac.compare_digest(expected, self.public_key_hash216):
            raise Pass213PQCError("PASS213_PQC_PUBLIC_KEY_HASH_MISMATCH")
        return raw


@dataclass(frozen=True)
class PQCVerifierBundle:
    suite: PQCAlgorithmSuite
    recovery_kem: PQCPublicKeyRecord
    operational_signature: PQCPublicKeyRecord
    archival_signature: PQCPublicKeyRecord
    bundle_root_hash216: str

    @classmethod
    def create(
        cls,
        *,
        suite: PQCAlgorithmSuite,
        recovery_kem: PQCPublicKeyRecord,
        operational_signature: PQCPublicKeyRecord,
        archival_signature: PQCPublicKeyRecord,
    ) -> "PQCVerifierBundle":
        records = (recovery_kem, operational_signature, archival_signature)
        if tuple(record.role for record in records) != (
            "recovery-kem",
            "operational-signature",
            "archival-signature",
        ):
            raise Pass213PQCError("PASS213_PQC_VERIFIER_BUNDLE_ROLES_INVALID")
        payload = {
            "suite": suite.to_mapping(),
            "keys": [asdict(record) for record in records],
        }
        return cls(
            suite=suite,
            recovery_kem=recovery_kem,
            operational_signature=operational_signature,
            archival_signature=archival_signature,
            bundle_root_hash216=hash216("pqc-verifier-bundle", canonical_bytes(payload)),
        )

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "suite": self.suite.to_mapping(),
            "keys": [
                asdict(self.recovery_kem),
                asdict(self.operational_signature),
                asdict(self.archival_signature),
            ],
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "bundle_root_hash216": self.bundle_root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PQCVerifierBundle":
        suite = PQCAlgorithmSuite(**dict(value["suite"]))
        keys = [PQCPublicKeyRecord(**dict(item)) for item in value["keys"]]
        if len(keys) != 3:
            raise Pass213PQCError("PASS213_PQC_VERIFIER_BUNDLE_KEY_COUNT_INVALID")
        bundle = cls(
            suite=suite,
            recovery_kem=keys[0],
            operational_signature=keys[1],
            archival_signature=keys[2],
            bundle_root_hash216=str(value["bundle_root_hash216"]),
        )
        bundle.validate()
        return bundle

    def validate(self) -> None:
        for record in (
            self.recovery_kem,
            self.operational_signature,
            self.archival_signature,
        ):
            record.public_key()
        expected = hash216("pqc-verifier-bundle", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.bundle_root_hash216):
            raise Pass213PQCError("PASS213_PQC_VERIFIER_BUNDLE_HASH_MISMATCH")


@dataclass(frozen=True)
class ProtectedPQCSecretRecord:
    role: str
    algorithm: str
    public_key_hash216: str
    arena_id_hash216: str
    secret_key_length: int
    final_memory_receipt_hash216: str


@dataclass(frozen=True)
class PQCSignatureRecord:
    role: str
    algorithm: str
    public_key_hash216: str
    message_hash216: str
    signature_b64: str
    signature_hash216: str

    @classmethod
    def create(
        cls,
        *,
        role: str,
        algorithm: str,
        public_key_hash216: str,
        message: bytes,
        signature: bytes,
    ) -> "PQCSignatureRecord":
        payload = {
            "role": role,
            "algorithm": algorithm,
            "public_key_hash216": public_key_hash216,
            "message_hash216": hash216("pqc-signed-message", message),
            "signature_b64": _b64(signature),
        }
        return cls(
            **payload,
            signature_hash216=hash216("pqc-signature-record", canonical_bytes(payload)),
        )

    def signature(self) -> bytes:
        return _unb64(self.signature_b64, "PASS213_PQC_SIGNATURE_ENCODING_INVALID")

    def validate_record(self, message: bytes) -> None:
        _require_hash216(self.public_key_hash216, "PASS213_PQC_SIGNATURE_PUBLIC_KEY_HASH_INVALID")
        if self.message_hash216 != hash216("pqc-signed-message", message):
            raise Pass213PQCError("PASS213_PQC_SIGNATURE_MESSAGE_HASH_MISMATCH")
        payload = {
            "role": self.role,
            "algorithm": self.algorithm,
            "public_key_hash216": self.public_key_hash216,
            "message_hash216": self.message_hash216,
            "signature_b64": self.signature_b64,
        }
        expected = hash216("pqc-signature-record", canonical_bytes(payload))
        if not hmac.compare_digest(expected, self.signature_hash216):
            raise Pass213PQCError("PASS213_PQC_SIGNATURE_RECORD_HASH_MISMATCH")


class PQCProtectedAuthority:
    """ML-KEM, ML-DSA and SLH-DSA authority with native secret-key arenas."""

    def __init__(
        self,
        *,
        library_path: str | Path,
        memory_root_key: bytes,
        owner_id: str,
        suite: PQCAlgorithmSuite | None = None,
    ) -> None:
        if not isinstance(memory_root_key, bytes) or len(memory_root_key) < 32:
            raise Pass213PQCError("PASS213_PQC_MEMORY_ROOT_KEY_TOO_SHORT")
        if not owner_id:
            raise Pass213PQCError("PASS213_PQC_OWNER_ID_INVALID")
        self.suite = suite or PQCAlgorithmSuite.detect()
        self._library_path = str(Path(library_path))
        self._memory_root_key = memory_root_key
        self._owner_id = owner_id
        self._arenas: dict[str, NativeSecureArena] = {}
        self._records: dict[str, ProtectedPQCSecretRecord] = {}
        self._closed = False

        recovery_public = self._generate_kem("recovery-kem", self.suite.ml_kem)
        operational_public = self._generate_signature(
            "operational-signature", self.suite.ml_dsa
        )
        archival_public = self._generate_signature(
            "archival-signature", self.suite.slh_dsa
        )
        self.verifier_bundle = PQCVerifierBundle.create(
            suite=self.suite,
            recovery_kem=recovery_public,
            operational_signature=operational_public,
            archival_signature=archival_public,
        )

    def _require_open(self) -> None:
        if self._closed:
            raise Pass213PQCError("PASS213_PQC_AUTHORITY_CLOSED")

    def _store_secret(
        self,
        *,
        role: str,
        algorithm: str,
        public_record: PQCPublicKeyRecord,
        secret_key: bytes,
    ) -> None:
        secret = bytearray(_require_bytes(secret_key, "PASS213_PQC_SECRET_KEY_EMPTY"))
        arena = NativeSecureArena(
            library_path=self._library_path,
            requested_size=len(secret),
            owner_id=f"{self._owner_id}:{role}:{public_record.public_key_hash216}",
            root_key=self._memory_root_key,
            allocation_sequence=len(self._arenas) + 1,
        )
        try:
            arena.write(bytes(secret))
            arena.seal()
            if arena.read_internal(offset=0, length=len(secret)) != bytes(secret):
                raise Pass213PQCError("PASS213_PQC_SECRET_POST_WRITE_MISMATCH")
            record = ProtectedPQCSecretRecord(
                role=role,
                algorithm=algorithm,
                public_key_hash216=public_record.public_key_hash216,
                arena_id_hash216=arena.arena_id_hash216,
                secret_key_length=len(secret),
                final_memory_receipt_hash216=arena.receipts[-1].receipt_hash216,
            )
            self._arenas[role] = arena
            self._records[role] = record
        except Exception:
            arena.close()
            raise
        finally:
            for index in range(len(secret)):
                secret[index] = 0

    def _generate_kem(self, role: str, algorithm: str) -> PQCPublicKeyRecord:
        oqs = _oqs_module()
        with oqs.KeyEncapsulation(algorithm) as kem:
            public_key = bytes(kem.generate_keypair())
            secret_key = bytes(kem.export_secret_key())
        public_record = PQCPublicKeyRecord.create(role, algorithm, public_key)
        self._store_secret(
            role=role,
            algorithm=algorithm,
            public_record=public_record,
            secret_key=secret_key,
        )
        secret_key = b""
        return public_record

    def _generate_signature(self, role: str, algorithm: str) -> PQCPublicKeyRecord:
        oqs = _oqs_module()
        with oqs.Signature(algorithm) as signer:
            public_key = bytes(signer.generate_keypair())
            secret_key = bytes(signer.export_secret_key())
        public_record = PQCPublicKeyRecord.create(role, algorithm, public_key)
        self._store_secret(
            role=role,
            algorithm=algorithm,
            public_record=public_record,
            secret_key=secret_key,
        )
        secret_key = b""
        return public_record

    def protected_secret_records(self) -> tuple[ProtectedPQCSecretRecord, ...]:
        self._require_open()
        return tuple(self._records[role] for role in sorted(self._records))

    def _secret(self, role: str) -> bytes:
        self._require_open()
        try:
            arena = self._arenas[role]
            record = self._records[role]
        except KeyError as exc:
            raise Pass213PQCError("PASS213_PQC_SECRET_ROLE_NOT_FOUND") from exc
        return arena.read_internal(offset=0, length=record.secret_key_length)

    def sign(self, role: str, message: bytes) -> PQCSignatureRecord:
        if role not in {"operational-signature", "archival-signature"}:
            raise Pass213PQCError("PASS213_PQC_SIGNATURE_ROLE_INVALID")
        self._require_open()
        raw = _require_bytes(message, "PASS213_PQC_MESSAGE_EMPTY")
        public_record = (
            self.verifier_bundle.operational_signature
            if role == "operational-signature"
            else self.verifier_bundle.archival_signature
        )
        secret = bytearray(self._secret(role))
        try:
            oqs = _oqs_module()
            with oqs.Signature(public_record.algorithm, bytes(secret)) as signer:
                signature = bytes(signer.sign(raw))
        finally:
            for index in range(len(secret)):
                secret[index] = 0
        return PQCSignatureRecord.create(
            role=role,
            algorithm=public_record.algorithm,
            public_key_hash216=public_record.public_key_hash216,
            message=raw,
            signature=signature,
        )

    @staticmethod
    def verify_signature(
        record: PQCSignatureRecord,
        message: bytes,
        public_record: PQCPublicKeyRecord,
    ) -> bool:
        record.validate_record(message)
        public_key = public_record.public_key()
        if (
            record.role != public_record.role
            or record.algorithm != public_record.algorithm
            or record.public_key_hash216 != public_record.public_key_hash216
        ):
            raise Pass213PQCError("PASS213_PQC_SIGNATURE_KEY_BINDING_MISMATCH")
        oqs = _oqs_module()
        with oqs.Signature(record.algorithm) as verifier:
            valid = bool(verifier.verify(message, record.signature(), public_key))
        if not valid:
            raise Pass213PQCError("PASS213_PQC_SIGNATURE_VERIFICATION_FAILED")
        return True

    def encapsulate(self, public_record: PQCPublicKeyRecord) -> tuple[bytes, bytes]:
        self._require_open()
        if public_record.role != "recovery-kem":
            raise Pass213PQCError("PASS213_PQC_KEM_PUBLIC_ROLE_INVALID")
        oqs = _oqs_module()
        with oqs.KeyEncapsulation(public_record.algorithm) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_record.public_key())
        return bytes(ciphertext), bytes(shared_secret)

    def decapsulate(self, ciphertext: bytes) -> bytes:
        self._require_open()
        raw = _require_bytes(ciphertext, "PASS213_PQC_KEM_CIPHERTEXT_EMPTY")
        public_record = self.verifier_bundle.recovery_kem
        secret = bytearray(self._secret("recovery-kem"))
        try:
            oqs = _oqs_module()
            with oqs.KeyEncapsulation(public_record.algorithm, bytes(secret)) as kem:
                shared = bytes(kem.decap_secret(raw))
        finally:
            for index in range(len(secret)):
                secret[index] = 0
        return shared

    def close(self) -> tuple[SecureMemoryReceipt, ...]:
        if self._closed:
            return ()
        receipts: list[SecureMemoryReceipt] = []
        for role in sorted(self._arenas):
            receipt = self._arenas[role].close()
            if receipt is not None:
                receipts.append(receipt)
        self._arenas.clear()
        self._records.clear()
        self._memory_root_key = b"\0" * len(self._memory_root_key)
        self._closed = True
        return tuple(receipts)

    def __enter__(self) -> "PQCProtectedAuthority":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


@dataclass(frozen=True)
class PQCRecoveryCapsule:
    sequence: int
    checkpoint_root_hash216: str
    algorithm: str
    recipient_public_key_hash216: str
    kem_ciphertext_b64: str
    nonce_b64: str
    encrypted_recovery_key_b64: str
    aad_hash216: str
    capsule_root_hash216: str

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_PQC_RECOVERY_CAPSULE_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": self.sequence,
            "checkpoint_root_hash216": self.checkpoint_root_hash216,
            "algorithm": self.algorithm,
            "recipient_public_key_hash216": self.recipient_public_key_hash216,
            "kem_ciphertext_b64": self.kem_ciphertext_b64,
            "nonce_b64": self.nonce_b64,
            "encrypted_recovery_key_b64": self.encrypted_recovery_key_b64,
            "aad_hash216": self.aad_hash216,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "capsule_root_hash216": self.capsule_root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PQCRecoveryCapsule":
        capsule = cls(
            sequence=int(value["sequence"]),
            checkpoint_root_hash216=str(value["checkpoint_root_hash216"]),
            algorithm=str(value["algorithm"]),
            recipient_public_key_hash216=str(value["recipient_public_key_hash216"]),
            kem_ciphertext_b64=str(value["kem_ciphertext_b64"]),
            nonce_b64=str(value["nonce_b64"]),
            encrypted_recovery_key_b64=str(value["encrypted_recovery_key_b64"]),
            aad_hash216=str(value["aad_hash216"]),
            capsule_root_hash216=str(value["capsule_root_hash216"]),
        )
        capsule.validate_structure()
        return capsule

    def validate_structure(self) -> None:
        if self.sequence < 1:
            raise Pass213PQCError("PASS213_PQC_CAPSULE_SEQUENCE_INVALID")
        _require_hash216(self.checkpoint_root_hash216, "PASS213_PQC_CAPSULE_CHECKPOINT_HASH_INVALID")
        _require_hash216(self.recipient_public_key_hash216, "PASS213_PQC_CAPSULE_RECIPIENT_HASH_INVALID")
        _require_hash216(self.aad_hash216, "PASS213_PQC_CAPSULE_AAD_HASH_INVALID")
        _unb64(self.kem_ciphertext_b64, "PASS213_PQC_CAPSULE_KEM_ENCODING_INVALID")
        nonce = _unb64(self.nonce_b64, "PASS213_PQC_CAPSULE_NONCE_ENCODING_INVALID")
        if len(nonce) != 12:
            raise Pass213PQCError("PASS213_PQC_CAPSULE_NONCE_LENGTH_INVALID")
        _unb64(self.encrypted_recovery_key_b64, "PASS213_PQC_CAPSULE_CIPHERTEXT_ENCODING_INVALID")
        expected = hash216("pqc-recovery-capsule", canonical_bytes(self.unsigned_payload()))
        if not hmac.compare_digest(expected, self.capsule_root_hash216):
            raise Pass213PQCError("PASS213_PQC_CAPSULE_ROOT_MISMATCH")


def _capsule_aad(
    *, sequence: int, checkpoint_root_hash216: str,
    algorithm: str, recipient_public_key_hash216: str,
) -> bytes:
    return canonical_bytes(
        {
            "schema": "HHS_PASS_213_PQC_RECOVERY_AAD_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "sequence": sequence,
            "checkpoint_root_hash216": checkpoint_root_hash216,
            "algorithm": algorithm,
            "recipient_public_key_hash216": recipient_public_key_hash216,
        }
    )


def create_recovery_capsule(
    *,
    authority: PQCProtectedAuthority,
    recovery_key: bytes,
    checkpoint_root_hash216: str,
    sequence: int,
) -> PQCRecoveryCapsule:
    secret = _require_bytes(recovery_key, "PASS213_PQC_RECOVERY_KEY_TOO_SHORT", 32)
    if len(secret) != 32:
        raise Pass213PQCError("PASS213_PQC_RECOVERY_KEY_LENGTH_INVALID")
    _require_hash216(checkpoint_root_hash216, "PASS213_PQC_CHECKPOINT_ROOT_INVALID")
    if sequence < 1:
        raise Pass213PQCError("PASS213_PQC_CAPSULE_SEQUENCE_INVALID")
    recipient = authority.verifier_bundle.recovery_kem
    kem_ciphertext, shared_secret = authority.encapsulate(recipient)
    aad = _capsule_aad(
        sequence=sequence,
        checkpoint_root_hash216=checkpoint_root_hash216,
        algorithm=recipient.algorithm,
        recipient_public_key_hash216=recipient.public_key_hash216,
    )
    wrapping_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes.fromhex(checkpoint_root_hash216),
        info=b"HHS-P213-ML-KEM-RECOVERY-WRAP-V1\0" + aad,
    ).derive(shared_secret)
    nonce = os.urandom(12)
    encrypted = AESGCM(wrapping_key).encrypt(nonce, secret, aad)
    shared_secret = b""
    wrapping_key = b""
    unsigned = {
        "schema": "HHS_PASS_213_PQC_RECOVERY_CAPSULE_V1",
        "contract": CONTRACT,
        "iteration": ITERATION,
        "sequence": sequence,
        "checkpoint_root_hash216": checkpoint_root_hash216,
        "algorithm": recipient.algorithm,
        "recipient_public_key_hash216": recipient.public_key_hash216,
        "kem_ciphertext_b64": _b64(kem_ciphertext),
        "nonce_b64": _b64(nonce),
        "encrypted_recovery_key_b64": _b64(encrypted),
        "aad_hash216": hash216("pqc-recovery-aad", aad),
    }
    return PQCRecoveryCapsule(
        sequence=sequence,
        checkpoint_root_hash216=checkpoint_root_hash216,
        algorithm=recipient.algorithm,
        recipient_public_key_hash216=recipient.public_key_hash216,
        kem_ciphertext_b64=unsigned["kem_ciphertext_b64"],
        nonce_b64=unsigned["nonce_b64"],
        encrypted_recovery_key_b64=unsigned["encrypted_recovery_key_b64"],
        aad_hash216=unsigned["aad_hash216"],
        capsule_root_hash216=hash216("pqc-recovery-capsule", canonical_bytes(unsigned)),
    )


def open_recovery_capsule(
    capsule: PQCRecoveryCapsule,
    authority: PQCProtectedAuthority,
) -> bytes:
    capsule.validate_structure()
    recipient = authority.verifier_bundle.recovery_kem
    if (
        capsule.algorithm != recipient.algorithm
        or capsule.recipient_public_key_hash216 != recipient.public_key_hash216
    ):
        raise Pass213PQCError("PASS213_PQC_CAPSULE_RECIPIENT_MISMATCH")
    aad = _capsule_aad(
        sequence=capsule.sequence,
        checkpoint_root_hash216=capsule.checkpoint_root_hash216,
        algorithm=capsule.algorithm,
        recipient_public_key_hash216=capsule.recipient_public_key_hash216,
    )
    if hash216("pqc-recovery-aad", aad) != capsule.aad_hash216:
        raise Pass213PQCError("PASS213_PQC_CAPSULE_AAD_MISMATCH")
    shared_secret = authority.decapsulate(
        _unb64(capsule.kem_ciphertext_b64, "PASS213_PQC_CAPSULE_KEM_ENCODING_INVALID")
    )
    wrapping_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes.fromhex(capsule.checkpoint_root_hash216),
        info=b"HHS-P213-ML-KEM-RECOVERY-WRAP-V1\0" + aad,
    ).derive(shared_secret)
    try:
        recovered = AESGCM(wrapping_key).decrypt(
            _unb64(capsule.nonce_b64, "PASS213_PQC_CAPSULE_NONCE_ENCODING_INVALID"),
            _unb64(capsule.encrypted_recovery_key_b64, "PASS213_PQC_CAPSULE_CIPHERTEXT_ENCODING_INVALID"),
            aad,
        )
    except Exception as exc:
        raise Pass213PQCError("PASS213_PQC_CAPSULE_DECRYPTION_FAILED") from exc
    finally:
        shared_secret = b""
        wrapping_key = b""
    if len(recovered) != 32:
        raise Pass213PQCError("PASS213_PQC_RECOVERED_KEY_LENGTH_INVALID")
    return recovered


@dataclass(frozen=True)
class SignedInventoryCheckpoint:
    signed_sequence: int
    prior_signed_checkpoint_root_hash216: str
    verifier_bundle_root_hash216: str
    checkpoint: Mapping[str, Any]
    operational_signature: PQCSignatureRecord
    archival_signature: PQCSignatureRecord
    signed_checkpoint_root_hash216: str

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_SIGNED_INVENTORY_CHECKPOINT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "signed_sequence": self.signed_sequence,
            "prior_signed_checkpoint_root_hash216": self.prior_signed_checkpoint_root_hash216,
            "verifier_bundle_root_hash216": self.verifier_bundle_root_hash216,
            "checkpoint": self.checkpoint,
        }

    def signing_message(self) -> bytes:
        return b"HHS-P213-PQC-CHECKPOINT-SIGNATURE-V1\0" + canonical_bytes(self.unsigned_payload())

    def to_mapping(self) -> dict[str, Any]:
        return {
            **self.unsigned_payload(),
            "operational_signature": asdict(self.operational_signature),
            "archival_signature": asdict(self.archival_signature),
            "signed_checkpoint_root_hash216": self.signed_checkpoint_root_hash216,
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "SignedInventoryCheckpoint":
        return cls(
            signed_sequence=int(value["signed_sequence"]),
            prior_signed_checkpoint_root_hash216=str(value["prior_signed_checkpoint_root_hash216"]),
            verifier_bundle_root_hash216=str(value["verifier_bundle_root_hash216"]),
            checkpoint=dict(value["checkpoint"]),
            operational_signature=PQCSignatureRecord(**dict(value["operational_signature"])),
            archival_signature=PQCSignatureRecord(**dict(value["archival_signature"])),
            signed_checkpoint_root_hash216=str(value["signed_checkpoint_root_hash216"]),
        )

    def validate(self, verifier_bundle: PQCVerifierBundle) -> bool:
        if self.signed_sequence < 1:
            raise Pass213PQCError("PASS213_PQC_SIGNED_SEQUENCE_INVALID")
        _require_hash216(
            self.prior_signed_checkpoint_root_hash216,
            "PASS213_PQC_PRIOR_SIGNED_ROOT_INVALID",
        )
        verifier_bundle.validate()
        if self.verifier_bundle_root_hash216 != verifier_bundle.bundle_root_hash216:
            raise Pass213PQCError("PASS213_PQC_VERIFIER_BUNDLE_BINDING_MISMATCH")
        checkpoint = InventoryCheckpoint.from_mapping(self.checkpoint)
        _require_hash216(
            checkpoint.checkpoint_root_hash216,
            "PASS213_PQC_CHECKPOINT_ROOT_INVALID",
        )
        message = self.signing_message()
        PQCProtectedAuthority.verify_signature(
            self.operational_signature,
            message,
            verifier_bundle.operational_signature,
        )
        PQCProtectedAuthority.verify_signature(
            self.archival_signature,
            message,
            verifier_bundle.archival_signature,
        )
        rooted_payload = {
            **self.unsigned_payload(),
            "operational_signature": asdict(self.operational_signature),
            "archival_signature": asdict(self.archival_signature),
        }
        expected = hash216("signed-inventory-checkpoint", canonical_bytes(rooted_payload))
        if not hmac.compare_digest(expected, self.signed_checkpoint_root_hash216):
            raise Pass213PQCError("PASS213_PQC_SIGNED_CHECKPOINT_ROOT_MISMATCH")
        return True


def sign_inventory_checkpoint(
    *,
    checkpoint: InventoryCheckpoint,
    authority: PQCProtectedAuthority,
    signed_sequence: int,
    prior_signed_checkpoint_root_hash216: str,
) -> SignedInventoryCheckpoint:
    if signed_sequence < 1:
        raise Pass213PQCError("PASS213_PQC_SIGNED_SEQUENCE_INVALID")
    _require_hash216(
        prior_signed_checkpoint_root_hash216,
        "PASS213_PQC_PRIOR_SIGNED_ROOT_INVALID",
    )
    provisional = SignedInventoryCheckpoint(
        signed_sequence=signed_sequence,
        prior_signed_checkpoint_root_hash216=prior_signed_checkpoint_root_hash216,
        verifier_bundle_root_hash216=authority.verifier_bundle.bundle_root_hash216,
        checkpoint=checkpoint.to_mapping(),
        operational_signature=PQCSignatureRecord("", "", ZERO_HASH216, ZERO_HASH216, "", ZERO_HASH216),
        archival_signature=PQCSignatureRecord("", "", ZERO_HASH216, ZERO_HASH216, "", ZERO_HASH216),
        signed_checkpoint_root_hash216="",
    )
    message = provisional.signing_message()
    operational = authority.sign("operational-signature", message)
    archival = authority.sign("archival-signature", message)
    rooted_payload = {
        **provisional.unsigned_payload(),
        "operational_signature": asdict(operational),
        "archival_signature": asdict(archival),
    }
    envelope = SignedInventoryCheckpoint(
        signed_sequence=signed_sequence,
        prior_signed_checkpoint_root_hash216=prior_signed_checkpoint_root_hash216,
        verifier_bundle_root_hash216=authority.verifier_bundle.bundle_root_hash216,
        checkpoint=checkpoint.to_mapping(),
        operational_signature=operational,
        archival_signature=archival,
        signed_checkpoint_root_hash216=hash216(
            "signed-inventory-checkpoint", canonical_bytes(rooted_payload)
        ),
    )
    envelope.validate(authority.verifier_bundle)
    return envelope


class PostQuantumCheckpointStore:
    """Append-only signed-checkpoint and recovery-capsule registry."""

    def __init__(
        self,
        *,
        database_path: str | Path,
        verifier_bundle: PQCVerifierBundle,
        authority: PQCProtectedAuthority | None = None,
    ) -> None:
        verifier_bundle.validate()
        if authority is not None and (
            authority.verifier_bundle.bundle_root_hash216
            != verifier_bundle.bundle_root_hash216
        ):
            raise Pass213PQCError("PASS213_PQC_STORE_AUTHORITY_BUNDLE_MISMATCH")
        self._verifier_bundle = verifier_bundle
        self._authority = authority
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS pqc_meta(
              key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pqc_checkpoints(
              signed_sequence INTEGER PRIMARY KEY,
              signed_checkpoint_root_hash216 TEXT UNIQUE NOT NULL,
              checkpoint_root_hash216 TEXT UNIQUE NOT NULL,
              envelope_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pqc_recovery_capsules(
              signed_sequence INTEGER PRIMARY KEY,
              capsule_root_hash216 TEXT UNIQUE NOT NULL,
              capsule_json TEXT NOT NULL,
              FOREIGN KEY(signed_sequence) REFERENCES pqc_checkpoints(signed_sequence));
            """
        )
        stored_bundle = self._meta("verifier_bundle")
        if stored_bundle is None:
            with self._connection:
                self._set_meta(
                    "verifier_bundle",
                    canonical_bytes(verifier_bundle.to_mapping()).decode("utf-8"),
                )
                self._set_meta("signed_head_hash216", ZERO_HASH216)
        else:
            recovered = PQCVerifierBundle.from_mapping(json.loads(stored_bundle))
            if recovered.bundle_root_hash216 != verifier_bundle.bundle_root_hash216:
                raise Pass213PQCError("PASS213_PQC_STORE_VERIFIER_BUNDLE_MISMATCH")
        self.verify_chain()

    def _meta(self, key: str) -> str | None:
        row = self._connection.execute(
            "SELECT value FROM pqc_meta WHERE key=?", (key,)
        ).fetchone()
        return None if row is None else str(row["value"])

    def _set_meta(self, key: str, value: str) -> None:
        self._connection.execute(
            "INSERT INTO pqc_meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    def append(
        self,
        *,
        checkpoint: InventoryCheckpoint,
        recovery_key: bytes,
    ) -> tuple[SignedInventoryCheckpoint, PQCRecoveryCapsule]:
        if self._authority is None:
            raise Pass213PQCError("PASS213_PQC_STORE_SIGNING_AUTHORITY_REQUIRED")
        row = self._connection.execute(
            "SELECT COALESCE(MAX(signed_sequence),0) AS n FROM pqc_checkpoints"
        ).fetchone()
        sequence = int(row["n"]) + 1
        prior = str(self._meta("signed_head_hash216"))
        envelope = sign_inventory_checkpoint(
            checkpoint=checkpoint,
            authority=self._authority,
            signed_sequence=sequence,
            prior_signed_checkpoint_root_hash216=prior,
        )
        capsule = create_recovery_capsule(
            authority=self._authority,
            recovery_key=recovery_key,
            checkpoint_root_hash216=checkpoint.checkpoint_root_hash216,
            sequence=sequence,
        )
        with self._connection:
            self._connection.execute(
                "INSERT INTO pqc_checkpoints VALUES(?,?,?,?)",
                (
                    sequence,
                    envelope.signed_checkpoint_root_hash216,
                    checkpoint.checkpoint_root_hash216,
                    canonical_bytes(envelope.to_mapping()).decode("utf-8"),
                ),
            )
            self._connection.execute(
                "INSERT INTO pqc_recovery_capsules VALUES(?,?,?)",
                (
                    sequence,
                    capsule.capsule_root_hash216,
                    canonical_bytes(capsule.to_mapping()).decode("utf-8"),
                ),
            )
            self._set_meta("signed_head_hash216", envelope.signed_checkpoint_root_hash216)
        return envelope, capsule

    def verify_chain(self) -> bool:
        prior = ZERO_HASH216
        rows = self._connection.execute(
            "SELECT * FROM pqc_checkpoints ORDER BY signed_sequence"
        ).fetchall()
        capsules = {
            int(row["signed_sequence"]): row
            for row in self._connection.execute(
                "SELECT * FROM pqc_recovery_capsules ORDER BY signed_sequence"
            )
        }
        for expected_sequence, row in enumerate(rows, 1):
            if int(row["signed_sequence"]) != expected_sequence:
                raise Pass213PQCError("PASS213_PQC_CHECKPOINT_SEQUENCE_DISCONTINUITY")
            envelope = SignedInventoryCheckpoint.from_mapping(
                json.loads(str(row["envelope_json"]))
            )
            if (
                envelope.signed_sequence != expected_sequence
                or envelope.prior_signed_checkpoint_root_hash216 != prior
                or envelope.signed_checkpoint_root_hash216
                != str(row["signed_checkpoint_root_hash216"])
            ):
                raise Pass213PQCError("PASS213_PQC_CHECKPOINT_CHAIN_DISCONTINUITY")
            envelope.validate(self._verifier_bundle)
            checkpoint = InventoryCheckpoint.from_mapping(envelope.checkpoint)
            if checkpoint.checkpoint_root_hash216 != str(row["checkpoint_root_hash216"]):
                raise Pass213PQCError("PASS213_PQC_CHECKPOINT_DATABASE_ROOT_MISMATCH")
            capsule_row = capsules.get(expected_sequence)
            if capsule_row is None:
                raise Pass213PQCError("PASS213_PQC_RECOVERY_CAPSULE_MISSING")
            capsule = PQCRecoveryCapsule.from_mapping(
                json.loads(str(capsule_row["capsule_json"]))
            )
            if (
                capsule.sequence != expected_sequence
                or capsule.checkpoint_root_hash216 != checkpoint.checkpoint_root_hash216
                or capsule.capsule_root_hash216 != str(capsule_row["capsule_root_hash216"])
            ):
                raise Pass213PQCError("PASS213_PQC_CAPSULE_CHAIN_BINDING_MISMATCH")
            prior = envelope.signed_checkpoint_root_hash216
        if set(capsules) != set(range(1, len(rows) + 1)):
            raise Pass213PQCError("PASS213_PQC_ORPHAN_RECOVERY_CAPSULE")
        if str(self._meta("signed_head_hash216")) != prior:
            raise Pass213PQCError("PASS213_PQC_SIGNED_HEAD_MISMATCH")
        return True

    def recover_key(self, signed_sequence: int) -> bytes:
        if self._authority is None:
            raise Pass213PQCError("PASS213_PQC_STORE_RECOVERY_AUTHORITY_REQUIRED")
        row = self._connection.execute(
            "SELECT capsule_json FROM pqc_recovery_capsules WHERE signed_sequence=?",
            (signed_sequence,),
        ).fetchone()
        if row is None:
            raise Pass213PQCError("PASS213_PQC_RECOVERY_CAPSULE_NOT_FOUND")
        capsule = PQCRecoveryCapsule.from_mapping(json.loads(str(row["capsule_json"])))
        return open_recovery_capsule(capsule, self._authority)

    def current_signed_head(self) -> str:
        return str(self._meta("signed_head_hash216"))

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PostQuantumCheckpointStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


__all__ = [
    "ITERATION",
    "RUNTIME_CLASSIFICATION",
    "DEFAULT_ML_KEM",
    "DEFAULT_ML_DSA",
    "Pass213PQCError",
    "PQCAlgorithmSuite",
    "PQCPublicKeyRecord",
    "PQCVerifierBundle",
    "ProtectedPQCSecretRecord",
    "PQCSignatureRecord",
    "PQCProtectedAuthority",
    "PQCRecoveryCapsule",
    "SignedInventoryCheckpoint",
    "PostQuantumCheckpointStore",
    "create_recovery_capsule",
    "open_recovery_capsule",
    "sign_inventory_checkpoint",
]

"""Pass 213 iteration 7: RFC 3161 trusted external timestamp anchoring.

Every Iteration 6 dual-signed checkpoint is bound to an independently signed
RFC 3161 token. The token message imprint commits the signed checkpoint root,
public verifier-bundle root, exact sequence, prior anchor root, Hash216 lineage,
local request boundary, and timestamp-authority identity.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import hmac
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
from typing import Any, Mapping, Protocol
from urllib.request import Request, urlopen

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CONTRACT,
    ZERO_HASH216,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_pqc_enclosure_v1 import (
    PQCVerifierBundle,
    SignedInventoryCheckpoint,
)

ITERATION = 7
RUNTIME_CLASSIFICATION = "HHS_PASS_213_RFC3161_TRUSTED_TIMESTAMP_ANCHOR_ITERATION7"
RFC3161_CONTENT_TYPE_QUERY = "application/timestamp-query"
RFC3161_CONTENT_TYPE_REPLY = "application/timestamp-reply"


class Pass213TimestampError(RuntimeError):
    """Raised when an external timestamp anchor invariant fails."""


def _require_hash216(value: str, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise Pass213TimestampError(code)
    try:
        int(value, 16)
    except ValueError as exc:
        raise Pass213TimestampError(code) from exc
    return value


def _require_text(value: str, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Pass213TimestampError(code)
    return value


def _b64(value: bytes) -> str:
    return b64encode(value).decode("ascii")


def _unb64(value: str, code: str) -> bytes:
    try:
        result = b64decode(value.encode("ascii"), validate=True)
    except Exception as exc:
        raise Pass213TimestampError(code) from exc
    if not result:
        raise Pass213TimestampError(code)
    return result


def _file_sha256(path: Path) -> str:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise Pass213TimestampError("PASS213_TIMESTAMP_TRUST_BUNDLE_UNREADABLE") from exc


def _run(
    command: list[str],
    *,
    cwd: Path | None = None,
    code: str,
) -> subprocess.CompletedProcess[bytes]:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=None if cwd is None else str(cwd),
            check=False,
        )
    except OSError as exc:
        raise Pass213TimestampError(code) from exc
    if result.returncode:
        detail = (result.stderr or result.stdout).decode("utf-8", errors="replace")
        raise Pass213TimestampError(f"{code}:{detail.strip()}")
    return result


def _canonical_gen_time(value: str) -> str:
    match = re.fullmatch(
        r"([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})"
        r"(?:\.(\d+))?\s+(\d{4})\s+GMT",
        value.strip(),
    )
    if match is None:
        raise Pass213TimestampError("PASS213_TIMESTAMP_GENTIME_FORMAT_INVALID")
    month, day, clock, fraction, year = match.groups()
    parsed = datetime.strptime(
        f"{month} {day} {clock} {year}", "%b %d %H:%M:%S %Y"
    ).replace(tzinfo=timezone.utc)
    parsed = parsed.replace(microsecond=int(((fraction or "") + "000000")[:6]))
    return parsed.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _parse_timestamp_text(text: str) -> dict[str, str]:
    if "Status: Granted." not in text and "Status: Granted with mods." not in text:
        raise Pass213TimestampError("PASS213_TIMESTAMP_TSA_STATUS_NOT_GRANTED")

    def field(label: str, code: str) -> str:
        match = re.search(rf"^{re.escape(label)}:\s*(.+)$", text, re.MULTILINE)
        if match is None:
            raise Pass213TimestampError(code)
        return match.group(1).strip()

    algorithm = field("Hash Algorithm", "PASS213_TIMESTAMP_HASH_ALGORITHM_MISSING")
    if algorithm.lower().replace("-", "") != "sha256":
        raise Pass213TimestampError("PASS213_TIMESTAMP_HASH_ALGORITHM_INVALID")
    data = re.search(
        r"^Message data:\s*$\n(?P<body>.*?)(?=^Serial number:)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if data is None:
        raise Pass213TimestampError("PASS213_TIMESTAMP_MESSAGE_IMPRINT_MISSING")
    octets: list[str] = []
    for line in data.group("body").splitlines():
        left = re.split(r"\s{2,}", line.strip(), maxsplit=1)[0]
        if "-" in left:
            left = left.split("-", 1)[1]
        octets.extend(
            re.findall(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{2}(?![0-9A-Fa-f])", left)
        )
    imprint = "".join(octets).lower()
    if len(imprint) != 64:
        raise Pass213TimestampError("PASS213_TIMESTAMP_MESSAGE_IMPRINT_LENGTH_INVALID")
    serial = field("Serial number", "PASS213_TIMESTAMP_SERIAL_MISSING").lower()
    if not re.fullmatch(r"0x[0-9a-f]+", serial):
        raise Pass213TimestampError("PASS213_TIMESTAMP_SERIAL_INVALID")
    nonce_match = re.search(r"^Nonce:\s*(.+)$", text, re.MULTILINE)
    if nonce_match is None:
        raise Pass213TimestampError("PASS213_TIMESTAMP_NONCE_MISSING")
    nonce = nonce_match.group(1).strip().lower()
    if not re.fullmatch(r"0x[0-9a-f]+", nonce):
        raise Pass213TimestampError("PASS213_TIMESTAMP_NONCE_INVALID")
    return {
        "message_imprint_sha256": imprint,
        "tsa_policy_oid": field("Policy OID", "PASS213_TIMESTAMP_POLICY_MISSING"),
        "tsa_serial_hex": serial,
        "gen_time_utc": _canonical_gen_time(
            field("Time stamp", "PASS213_TIMESTAMP_GENTIME_MISSING")
        ),
        "tsa_subject": field("TSA", "PASS213_TIMESTAMP_TSA_SUBJECT_MISSING"),
        "nonce_hex": nonce,
    }


@dataclass(frozen=True)
class TimestampAnchorIntent:
    anchor_sequence: int
    signed_sequence: int
    signed_checkpoint_root_hash216: str
    verifier_bundle_root_hash216: str
    prior_anchor_root_hash216: str
    hash216_lineage_root: str
    requested_timestamp_ns: int
    authority_id: str
    intent_root_hash216: str

    @classmethod
    def create(
        cls,
        *,
        signed_sequence: int,
        signed_checkpoint_root_hash216: str,
        verifier_bundle_root_hash216: str,
        prior_anchor_root_hash216: str,
        hash216_lineage_root: str,
        requested_timestamp_ns: int,
        authority_id: str,
    ) -> "TimestampAnchorIntent":
        if signed_sequence < 1:
            raise Pass213TimestampError("PASS213_TIMESTAMP_SIGNED_SEQUENCE_INVALID")
        unsigned = {
            "schema": "HHS_PASS_213_TIMESTAMP_ANCHOR_INTENT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "anchor_sequence": signed_sequence,
            "signed_sequence": signed_sequence,
            "signed_checkpoint_root_hash216": _require_hash216(
                signed_checkpoint_root_hash216,
                "PASS213_TIMESTAMP_SIGNED_CHECKPOINT_ROOT_INVALID",
            ),
            "verifier_bundle_root_hash216": _require_hash216(
                verifier_bundle_root_hash216,
                "PASS213_TIMESTAMP_VERIFIER_BUNDLE_ROOT_INVALID",
            ),
            "prior_anchor_root_hash216": _require_hash216(
                prior_anchor_root_hash216,
                "PASS213_TIMESTAMP_PRIOR_ANCHOR_ROOT_INVALID",
            ),
            "hash216_lineage_root": _require_hash216(
                hash216_lineage_root,
                "PASS213_TIMESTAMP_LINEAGE_ROOT_INVALID",
            ),
            "requested_timestamp_ns": int(requested_timestamp_ns),
            "authority_id": _require_text(
                authority_id, "PASS213_TIMESTAMP_AUTHORITY_ID_INVALID"
            ),
        }
        if unsigned["requested_timestamp_ns"] < 0:
            raise Pass213TimestampError("PASS213_TIMESTAMP_REQUEST_BOUNDARY_INVALID")
        return cls(
            anchor_sequence=signed_sequence,
            signed_sequence=signed_sequence,
            signed_checkpoint_root_hash216=unsigned[
                "signed_checkpoint_root_hash216"
            ],
            verifier_bundle_root_hash216=unsigned[
                "verifier_bundle_root_hash216"
            ],
            prior_anchor_root_hash216=unsigned["prior_anchor_root_hash216"],
            hash216_lineage_root=unsigned["hash216_lineage_root"],
            requested_timestamp_ns=unsigned["requested_timestamp_ns"],
            authority_id=unsigned["authority_id"],
            intent_root_hash216=hash216(
                "external-timestamp-anchor-intent", canonical_bytes(unsigned)
            ),
        )

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_TIMESTAMP_ANCHOR_INTENT_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "anchor_sequence": self.anchor_sequence,
            "signed_sequence": self.signed_sequence,
            "signed_checkpoint_root_hash216": self.signed_checkpoint_root_hash216,
            "verifier_bundle_root_hash216": self.verifier_bundle_root_hash216,
            "prior_anchor_root_hash216": self.prior_anchor_root_hash216,
            "hash216_lineage_root": self.hash216_lineage_root,
            "requested_timestamp_ns": self.requested_timestamp_ns,
            "authority_id": self.authority_id,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "intent_root_hash216": self.intent_root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TimestampAnchorIntent":
        intent = cls(
            anchor_sequence=int(value["anchor_sequence"]),
            signed_sequence=int(value["signed_sequence"]),
            signed_checkpoint_root_hash216=str(
                value["signed_checkpoint_root_hash216"]
            ),
            verifier_bundle_root_hash216=str(
                value["verifier_bundle_root_hash216"]
            ),
            prior_anchor_root_hash216=str(value["prior_anchor_root_hash216"]),
            hash216_lineage_root=str(value["hash216_lineage_root"]),
            requested_timestamp_ns=int(value["requested_timestamp_ns"]),
            authority_id=str(value["authority_id"]),
            intent_root_hash216=str(value["intent_root_hash216"]),
        )
        intent.validate()
        return intent

    def validate(self) -> None:
        if self.anchor_sequence < 1 or self.anchor_sequence != self.signed_sequence:
            raise Pass213TimestampError("PASS213_TIMESTAMP_SEQUENCE_BINDING_INVALID")
        _require_hash216(
            self.signed_checkpoint_root_hash216,
            "PASS213_TIMESTAMP_SIGNED_CHECKPOINT_ROOT_INVALID",
        )
        _require_hash216(
            self.verifier_bundle_root_hash216,
            "PASS213_TIMESTAMP_VERIFIER_BUNDLE_ROOT_INVALID",
        )
        _require_hash216(
            self.prior_anchor_root_hash216,
            "PASS213_TIMESTAMP_PRIOR_ANCHOR_ROOT_INVALID",
        )
        _require_hash216(
            self.hash216_lineage_root, "PASS213_TIMESTAMP_LINEAGE_ROOT_INVALID"
        )
        if self.requested_timestamp_ns < 0:
            raise Pass213TimestampError("PASS213_TIMESTAMP_REQUEST_BOUNDARY_INVALID")
        _require_text(self.authority_id, "PASS213_TIMESTAMP_AUTHORITY_ID_INVALID")
        expected = hash216(
            "external-timestamp-anchor-intent",
            canonical_bytes(self.unsigned_payload()),
        )
        if not hmac.compare_digest(expected, self.intent_root_hash216):
            raise Pass213TimestampError("PASS213_TIMESTAMP_INTENT_ROOT_MISMATCH")

    def anchor_message(self) -> bytes:
        self.validate()
        return (
            b"HHS-P213-RFC3161-EXTERNAL-TIMESTAMP-ANCHOR-V1\0"
            + canonical_bytes(self.to_mapping())
        )


@dataclass(frozen=True)
class RFC3161TimestampEvidence:
    authority_id: str
    request_der_b64: str
    response_der_b64: str
    request_sha256: str
    response_sha256: str
    message_imprint_sha256: str
    tsa_policy_oid: str
    tsa_serial_hex: str
    gen_time_utc: str
    tsa_subject: str
    nonce_hex: str
    trust_bundle_sha256: str
    verification_receipt_hash216: str
    evidence_root_hash216: str

    def unsigned_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_RFC3161_TIMESTAMP_EVIDENCE_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "authority_id": self.authority_id,
            "request_der_b64": self.request_der_b64,
            "response_der_b64": self.response_der_b64,
            "request_sha256": self.request_sha256,
            "response_sha256": self.response_sha256,
            "message_imprint_sha256": self.message_imprint_sha256,
            "tsa_policy_oid": self.tsa_policy_oid,
            "tsa_serial_hex": self.tsa_serial_hex,
            "gen_time_utc": self.gen_time_utc,
            "tsa_subject": self.tsa_subject,
            "nonce_hex": self.nonce_hex,
            "trust_bundle_sha256": self.trust_bundle_sha256,
            "verification_receipt_hash216": self.verification_receipt_hash216,
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.unsigned_payload(), "evidence_root_hash216": self.evidence_root_hash216}

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "RFC3161TimestampEvidence":
        return cls(
            authority_id=str(value["authority_id"]),
            request_der_b64=str(value["request_der_b64"]),
            response_der_b64=str(value["response_der_b64"]),
            request_sha256=str(value["request_sha256"]),
            response_sha256=str(value["response_sha256"]),
            message_imprint_sha256=str(value["message_imprint_sha256"]),
            tsa_policy_oid=str(value["tsa_policy_oid"]),
            tsa_serial_hex=str(value["tsa_serial_hex"]),
            gen_time_utc=str(value["gen_time_utc"]),
            tsa_subject=str(value["tsa_subject"]),
            nonce_hex=str(value["nonce_hex"]),
            trust_bundle_sha256=str(value["trust_bundle_sha256"]),
            verification_receipt_hash216=str(value["verification_receipt_hash216"]),
            evidence_root_hash216=str(value["evidence_root_hash216"]),
        )

    def validate_structure(self, intent: TimestampAnchorIntent) -> None:
        intent.validate()
        if self.authority_id != intent.authority_id:
            raise Pass213TimestampError("PASS213_TIMESTAMP_AUTHORITY_BINDING_MISMATCH")
        request = _unb64(
            self.request_der_b64, "PASS213_TIMESTAMP_REQUEST_DER_ENCODING_INVALID"
        )
        response = _unb64(
            self.response_der_b64, "PASS213_TIMESTAMP_RESPONSE_DER_ENCODING_INVALID"
        )
        if sha256(request).hexdigest() != self.request_sha256:
            raise Pass213TimestampError("PASS213_TIMESTAMP_REQUEST_SHA256_MISMATCH")
        if sha256(response).hexdigest() != self.response_sha256:
            raise Pass213TimestampError("PASS213_TIMESTAMP_RESPONSE_SHA256_MISMATCH")
        if self.message_imprint_sha256 != sha256(intent.anchor_message()).hexdigest():
            raise Pass213TimestampError("PASS213_TIMESTAMP_MESSAGE_IMPRINT_MISMATCH")
        if not re.fullmatch(r"[0-9a-f]{64}", self.trust_bundle_sha256):
            raise Pass213TimestampError("PASS213_TIMESTAMP_TRUST_BUNDLE_HASH_INVALID")
        _require_hash216(
            self.verification_receipt_hash216,
            "PASS213_TIMESTAMP_VERIFICATION_RECEIPT_INVALID",
        )
        _require_text(self.tsa_policy_oid, "PASS213_TIMESTAMP_POLICY_MISSING")
        _require_text(self.tsa_subject, "PASS213_TIMESTAMP_TSA_SUBJECT_MISSING")
        if not re.fullmatch(r"0x[0-9a-f]+", self.tsa_serial_hex):
            raise Pass213TimestampError("PASS213_TIMESTAMP_SERIAL_INVALID")
        if not re.fullmatch(r"0x[0-9a-f]+", self.nonce_hex):
            raise Pass213TimestampError("PASS213_TIMESTAMP_NONCE_INVALID")
        if not self.gen_time_utc.endswith("Z"):
            raise Pass213TimestampError("PASS213_TIMESTAMP_GENTIME_NOT_UTC")
        parsed = datetime.fromisoformat(self.gen_time_utc.replace("Z", "+00:00"))
        if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
            raise Pass213TimestampError("PASS213_TIMESTAMP_GENTIME_NOT_UTC")
        expected = hash216(
            "rfc3161-timestamp-evidence", canonical_bytes(self.unsigned_payload())
        )
        if not hmac.compare_digest(expected, self.evidence_root_hash216):
            raise Pass213TimestampError("PASS213_TIMESTAMP_EVIDENCE_ROOT_MISMATCH")


class RFC3161Transport(Protocol):
    def submit(self, request_der: bytes) -> bytes:
        """Return a DER RFC 3161 TimeStampResp for a DER TimeStampReq."""


class HTTPRFC3161Transport:
    """HTTP transport for an independently operated RFC 3161 TSA."""

    def __init__(
        self,
        endpoint_url: str,
        *,
        timeout_seconds: float = 15.0,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.endpoint_url = _require_text(
            endpoint_url, "PASS213_TIMESTAMP_ENDPOINT_INVALID"
        )
        if timeout_seconds <= 0:
            raise Pass213TimestampError("PASS213_TIMESTAMP_HTTP_TIMEOUT_INVALID")
        self.timeout_seconds = float(timeout_seconds)
        self.headers = dict(headers or {})

    def submit(self, request_der: bytes) -> bytes:
        if not request_der:
            raise Pass213TimestampError("PASS213_TIMESTAMP_HTTP_REQUEST_EMPTY")
        request = Request(
            self.endpoint_url,
            data=request_der,
            method="POST",
            headers={
                "Content-Type": RFC3161_CONTENT_TYPE_QUERY,
                "Accept": RFC3161_CONTENT_TYPE_REPLY,
                **self.headers,
            },
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                content_type = response.headers.get_content_type()
                payload = response.read()
        except Exception as exc:
            raise Pass213TimestampError("PASS213_TIMESTAMP_HTTP_SUBMISSION_FAILED") from exc
        if content_type != RFC3161_CONTENT_TYPE_REPLY:
            raise Pass213TimestampError("PASS213_TIMESTAMP_HTTP_CONTENT_TYPE_INVALID")
        if not payload:
            raise Pass213TimestampError("PASS213_TIMESTAMP_HTTP_RESPONSE_EMPTY")
        return payload


class OpenSSLTSATransport:
    """Isolated OpenSSL TSA transport for offline deployments and tests."""

    def __init__(
        self,
        *,
        config_path: str | Path,
        section: str,
        openssl_binary: str = "openssl",
    ) -> None:
        self.config_path = Path(config_path)
        self.section = _require_text(
            section, "PASS213_TIMESTAMP_OPENSSL_TSA_SECTION_INVALID"
        )
        self.openssl_binary = _require_text(
            openssl_binary, "PASS213_TIMESTAMP_OPENSSL_BINARY_INVALID"
        )

    def submit(self, request_der: bytes) -> bytes:
        if not request_der:
            raise Pass213TimestampError("PASS213_TIMESTAMP_OPENSSL_TSA_REQUEST_EMPTY")
        with tempfile.TemporaryDirectory(prefix="hhs-pass213-tsa-") as directory:
            query_path = Path(directory) / "request.tsq"
            response_path = Path(directory) / "response.tsr"
            query_path.write_bytes(request_der)
            _run(
                [
                    self.openssl_binary,
                    "ts",
                    "-reply",
                    "-config",
                    str(self.config_path),
                    "-section",
                    self.section,
                    "-queryfile",
                    str(query_path),
                    "-out",
                    str(response_path),
                ],
                cwd=self.config_path.parent,
                code="PASS213_TIMESTAMP_OPENSSL_TSA_REPLY_FAILED",
            )
            return response_path.read_bytes()


class RFC3161TimestampVerifier:
    """Build and verify RFC 3161 requests against an explicit trust bundle."""

    def __init__(
        self,
        *,
        trust_bundle_path: str | Path,
        openssl_binary: str = "openssl",
        untrusted_chain_path: str | Path | None = None,
    ) -> None:
        self.trust_bundle_path = Path(trust_bundle_path)
        self.openssl_binary = _require_text(
            openssl_binary, "PASS213_TIMESTAMP_OPENSSL_BINARY_INVALID"
        )
        self.untrusted_chain_path = (
            None if untrusted_chain_path is None else Path(untrusted_chain_path)
        )
        self.trust_bundle_sha256 = _file_sha256(self.trust_bundle_path)

    def build_query(self, intent: TimestampAnchorIntent) -> bytes:
        imprint = sha256(intent.anchor_message()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="hhs-pass213-tsq-") as directory:
            query_path = Path(directory) / "request.tsq"
            _run(
                [
                    self.openssl_binary,
                    "ts",
                    "-query",
                    "-digest",
                    imprint,
                    "-sha256",
                    "-cert",
                    "-out",
                    str(query_path),
                ],
                code="PASS213_TIMESTAMP_QUERY_BUILD_FAILED",
            )
            query = query_path.read_bytes()
        if not query:
            raise Pass213TimestampError("PASS213_TIMESTAMP_QUERY_BUILD_EMPTY")
        return query

    def issue(
        self,
        *,
        intent: TimestampAnchorIntent,
        transport: RFC3161Transport,
    ) -> RFC3161TimestampEvidence:
        request_der = self.build_query(intent)
        return self.verify_response(
            intent=intent,
            request_der=request_der,
            response_der=transport.submit(request_der),
        )

    def verify_response(
        self,
        *,
        intent: TimestampAnchorIntent,
        request_der: bytes,
        response_der: bytes,
    ) -> RFC3161TimestampEvidence:
        intent.validate()
        if not request_der or not response_der:
            raise Pass213TimestampError("PASS213_TIMESTAMP_DER_MATERIAL_EMPTY")
        with tempfile.TemporaryDirectory(prefix="hhs-pass213-tsv-") as directory:
            query_path = Path(directory) / "request.tsq"
            response_path = Path(directory) / "response.tsr"
            query_path.write_bytes(request_der)
            response_path.write_bytes(response_der)
            command = [
                self.openssl_binary,
                "ts",
                "-verify",
                "-queryfile",
                str(query_path),
                "-in",
                str(response_path),
                "-CAfile",
                str(self.trust_bundle_path),
            ]
            if self.untrusted_chain_path is not None:
                command.extend(["-untrusted", str(self.untrusted_chain_path)])
            verification = _run(
                command,
                code="PASS213_TIMESTAMP_RFC3161_VERIFICATION_FAILED",
            )
            inspection = _run(
                [
                    self.openssl_binary,
                    "ts",
                    "-reply",
                    "-in",
                    str(response_path),
                    "-text",
                ],
                code="PASS213_TIMESTAMP_RFC3161_INSPECTION_FAILED",
            )
        parsed = _parse_timestamp_text(inspection.stdout.decode("utf-8", errors="strict"))
        expected_imprint = sha256(intent.anchor_message()).hexdigest()
        if parsed["message_imprint_sha256"] != expected_imprint:
            raise Pass213TimestampError("PASS213_TIMESTAMP_MESSAGE_IMPRINT_MISMATCH")
        request_hash = sha256(request_der).hexdigest()
        response_hash = sha256(response_der).hexdigest()
        receipt_payload = {
            "authority_id": intent.authority_id,
            "request_sha256": request_hash,
            "response_sha256": response_hash,
            **parsed,
            "trust_bundle_sha256": self.trust_bundle_sha256,
            "verification_stdout_sha256": sha256(verification.stdout).hexdigest(),
        }
        receipt = hash216(
            "rfc3161-verification-receipt", canonical_bytes(receipt_payload)
        )
        unsigned = {
            "schema": "HHS_PASS_213_RFC3161_TIMESTAMP_EVIDENCE_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "authority_id": intent.authority_id,
            "request_der_b64": _b64(request_der),
            "response_der_b64": _b64(response_der),
            "request_sha256": request_hash,
            "response_sha256": response_hash,
            **parsed,
            "trust_bundle_sha256": self.trust_bundle_sha256,
            "verification_receipt_hash216": receipt,
        }
        evidence = RFC3161TimestampEvidence(
            authority_id=intent.authority_id,
            request_der_b64=unsigned["request_der_b64"],
            response_der_b64=unsigned["response_der_b64"],
            request_sha256=request_hash,
            response_sha256=response_hash,
            message_imprint_sha256=parsed["message_imprint_sha256"],
            tsa_policy_oid=parsed["tsa_policy_oid"],
            tsa_serial_hex=parsed["tsa_serial_hex"],
            gen_time_utc=parsed["gen_time_utc"],
            tsa_subject=parsed["tsa_subject"],
            nonce_hex=parsed["nonce_hex"],
            trust_bundle_sha256=self.trust_bundle_sha256,
            verification_receipt_hash216=receipt,
            evidence_root_hash216=hash216(
                "rfc3161-timestamp-evidence", canonical_bytes(unsigned)
            ),
        )
        evidence.validate_structure(intent)
        return evidence

    def verify_evidence(
        self,
        *,
        intent: TimestampAnchorIntent,
        evidence: RFC3161TimestampEvidence,
    ) -> bool:
        evidence.validate_structure(intent)
        if evidence.trust_bundle_sha256 != self.trust_bundle_sha256:
            raise Pass213TimestampError("PASS213_TIMESTAMP_TRUST_BUNDLE_MISMATCH")
        verified = self.verify_response(
            intent=intent,
            request_der=_unb64(
                evidence.request_der_b64,
                "PASS213_TIMESTAMP_REQUEST_DER_ENCODING_INVALID",
            ),
            response_der=_unb64(
                evidence.response_der_b64,
                "PASS213_TIMESTAMP_RESPONSE_DER_ENCODING_INVALID",
            ),
        )
        for field_name in (
            "request_sha256",
            "response_sha256",
            "message_imprint_sha256",
            "tsa_policy_oid",
            "tsa_serial_hex",
            "gen_time_utc",
            "tsa_subject",
            "nonce_hex",
            "trust_bundle_sha256",
            "verification_receipt_hash216",
            "evidence_root_hash216",
        ):
            if getattr(verified, field_name) != getattr(evidence, field_name):
                raise Pass213TimestampError(
                    "PASS213_TIMESTAMP_REVERIFICATION_EVIDENCE_MISMATCH"
                )
        return True


@dataclass(frozen=True)
class TrustedTimestampAnchorRecord:
    intent: TimestampAnchorIntent
    signed_checkpoint: Mapping[str, Any]
    evidence: RFC3161TimestampEvidence
    anchor_root_hash216: str

    def rooted_payload(self) -> Mapping[str, Any]:
        return {
            "schema": "HHS_PASS_213_TRUSTED_TIMESTAMP_ANCHOR_RECORD_V1",
            "contract": CONTRACT,
            "iteration": ITERATION,
            "intent": self.intent.to_mapping(),
            "signed_checkpoint": self.signed_checkpoint,
            "evidence": self.evidence.to_mapping(),
        }

    def to_mapping(self) -> dict[str, Any]:
        return {**self.rooted_payload(), "anchor_root_hash216": self.anchor_root_hash216}

    @classmethod
    def create(
        cls,
        *,
        intent: TimestampAnchorIntent,
        signed_checkpoint: SignedInventoryCheckpoint,
        evidence: RFC3161TimestampEvidence,
    ) -> "TrustedTimestampAnchorRecord":
        provisional = cls(intent, signed_checkpoint.to_mapping(), evidence, "")
        return cls(
            provisional.intent,
            provisional.signed_checkpoint,
            provisional.evidence,
            hash216(
                "trusted-external-timestamp-anchor",
                canonical_bytes(provisional.rooted_payload()),
            ),
        )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "TrustedTimestampAnchorRecord":
        return cls(
            intent=TimestampAnchorIntent.from_mapping(dict(value["intent"])),
            signed_checkpoint=dict(value["signed_checkpoint"]),
            evidence=RFC3161TimestampEvidence.from_mapping(dict(value["evidence"])),
            anchor_root_hash216=str(value["anchor_root_hash216"]),
        )

    def validate(
        self,
        *,
        verifier_bundle: PQCVerifierBundle,
        timestamp_verifier: RFC3161TimestampVerifier,
    ) -> bool:
        self.intent.validate()
        signed = SignedInventoryCheckpoint.from_mapping(self.signed_checkpoint)
        signed.validate(verifier_bundle)
        if (
            signed.signed_sequence != self.intent.signed_sequence
            or signed.signed_checkpoint_root_hash216
            != self.intent.signed_checkpoint_root_hash216
            or signed.verifier_bundle_root_hash216
            != self.intent.verifier_bundle_root_hash216
        ):
            raise Pass213TimestampError(
                "PASS213_TIMESTAMP_SIGNED_CHECKPOINT_BINDING_MISMATCH"
            )
        timestamp_verifier.verify_evidence(intent=self.intent, evidence=self.evidence)
        expected = hash216(
            "trusted-external-timestamp-anchor", canonical_bytes(self.rooted_payload())
        )
        if not hmac.compare_digest(expected, self.anchor_root_hash216):
            raise Pass213TimestampError("PASS213_TIMESTAMP_ANCHOR_ROOT_MISMATCH")
        return True


class TrustedTimestampAnchorStore:
    """Append-only externally timestamped checkpoint chain."""

    def __init__(
        self,
        *,
        database_path: str | Path,
        verifier_bundle: PQCVerifierBundle,
        timestamp_verifier: RFC3161TimestampVerifier,
        transport: RFC3161Transport | None = None,
    ) -> None:
        verifier_bundle.validate()
        self._verifier_bundle = verifier_bundle
        self._timestamp_verifier = timestamp_verifier
        self._transport = transport
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS timestamp_anchor_meta(
              key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS timestamp_anchors(
              anchor_sequence INTEGER PRIMARY KEY,
              signed_sequence INTEGER UNIQUE NOT NULL,
              signed_checkpoint_root_hash216 TEXT UNIQUE NOT NULL,
              anchor_root_hash216 TEXT UNIQUE NOT NULL,
              authority_id TEXT NOT NULL,
              gen_time_utc TEXT NOT NULL,
              tsa_serial_hex TEXT NOT NULL,
              record_json TEXT NOT NULL);
            """
        )
        stored_bundle = self._meta("verifier_bundle")
        if stored_bundle is None:
            with self._connection:
                self._set_meta(
                    "verifier_bundle",
                    canonical_bytes(verifier_bundle.to_mapping()).decode("utf-8"),
                )
                self._set_meta(
                    "trust_bundle_sha256", timestamp_verifier.trust_bundle_sha256
                )
                self._set_meta("anchor_head_hash216", ZERO_HASH216)
        else:
            recovered = PQCVerifierBundle.from_mapping(json.loads(stored_bundle))
            if recovered.bundle_root_hash216 != verifier_bundle.bundle_root_hash216:
                raise Pass213TimestampError(
                    "PASS213_TIMESTAMP_STORE_VERIFIER_BUNDLE_MISMATCH"
                )
            if self._meta("trust_bundle_sha256") != timestamp_verifier.trust_bundle_sha256:
                raise Pass213TimestampError(
                    "PASS213_TIMESTAMP_STORE_TRUST_BUNDLE_MISMATCH"
                )
        self.verify_chain()

    def _meta(self, key: str) -> str | None:
        row = self._connection.execute(
            "SELECT value FROM timestamp_anchor_meta WHERE key=?", (key,)
        ).fetchone()
        return None if row is None else str(row["value"])

    def _set_meta(self, key: str, value: str) -> None:
        self._connection.execute(
            "INSERT INTO timestamp_anchor_meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    def append(
        self,
        *,
        signed_checkpoint: SignedInventoryCheckpoint,
        hash216_lineage_root: str,
        requested_timestamp_ns: int,
        authority_id: str,
    ) -> TrustedTimestampAnchorRecord:
        if self._transport is None:
            raise Pass213TimestampError(
                "PASS213_TIMESTAMP_STORE_SUBMISSION_TRANSPORT_REQUIRED"
            )
        signed_checkpoint.validate(self._verifier_bundle)
        row = self._connection.execute(
            "SELECT COALESCE(MAX(anchor_sequence),0) AS n FROM timestamp_anchors"
        ).fetchone()
        sequence = int(row["n"]) + 1
        if signed_checkpoint.signed_sequence != sequence:
            raise Pass213TimestampError(
                "PASS213_TIMESTAMP_SIGNED_SEQUENCE_DISCONTINUITY"
            )
        previous_row = self._connection.execute(
            "SELECT record_json FROM timestamp_anchors "
            "ORDER BY anchor_sequence DESC LIMIT 1"
        ).fetchone()
        previous = (
            None
            if previous_row is None
            else TrustedTimestampAnchorRecord.from_mapping(
                json.loads(str(previous_row["record_json"]))
            )
        )
        if (
            previous is not None
            and requested_timestamp_ns < previous.intent.requested_timestamp_ns
        ):
            raise Pass213TimestampError(
                "PASS213_TIMESTAMP_LOCAL_BOUNDARY_REGRESSION"
            )
        intent = TimestampAnchorIntent.create(
            signed_sequence=signed_checkpoint.signed_sequence,
            signed_checkpoint_root_hash216=signed_checkpoint.signed_checkpoint_root_hash216,
            verifier_bundle_root_hash216=signed_checkpoint.verifier_bundle_root_hash216,
            prior_anchor_root_hash216=str(self._meta("anchor_head_hash216")),
            hash216_lineage_root=hash216_lineage_root,
            requested_timestamp_ns=requested_timestamp_ns,
            authority_id=authority_id,
        )
        evidence = self._timestamp_verifier.issue(
            intent=intent, transport=self._transport
        )
        if previous is not None:
            prior_time = datetime.fromisoformat(
                previous.evidence.gen_time_utc.replace("Z", "+00:00")
            )
            current_time = datetime.fromisoformat(
                evidence.gen_time_utc.replace("Z", "+00:00")
            )
            if current_time < prior_time:
                raise Pass213TimestampError("PASS213_TIMESTAMP_TSA_TIME_REGRESSION")
            duplicate = self._connection.execute(
                "SELECT 1 FROM timestamp_anchors "
                "WHERE authority_id=? AND tsa_serial_hex=?",
                (authority_id, evidence.tsa_serial_hex),
            ).fetchone()
            if duplicate is not None:
                raise Pass213TimestampError("PASS213_TIMESTAMP_TSA_SERIAL_REUSE")
        record = TrustedTimestampAnchorRecord.create(
            intent=intent,
            signed_checkpoint=signed_checkpoint,
            evidence=evidence,
        )
        record.validate(
            verifier_bundle=self._verifier_bundle,
            timestamp_verifier=self._timestamp_verifier,
        )
        with self._connection:
            self._connection.execute(
                "INSERT INTO timestamp_anchors VALUES(?,?,?,?,?,?,?,?)",
                (
                    sequence,
                    signed_checkpoint.signed_sequence,
                    signed_checkpoint.signed_checkpoint_root_hash216,
                    record.anchor_root_hash216,
                    evidence.authority_id,
                    evidence.gen_time_utc,
                    evidence.tsa_serial_hex,
                    canonical_bytes(record.to_mapping()).decode("utf-8"),
                ),
            )
            self._set_meta("anchor_head_hash216", record.anchor_root_hash216)
        return record

    def verify_chain(self) -> bool:
        prior = ZERO_HASH216
        prior_signed = ZERO_HASH216
        prior_requested_ns = -1
        prior_time: datetime | None = None
        serials: set[tuple[str, str, str]] = set()
        rows = self._connection.execute(
            "SELECT * FROM timestamp_anchors ORDER BY anchor_sequence"
        ).fetchall()
        for expected_sequence, row in enumerate(rows, 1):
            record = TrustedTimestampAnchorRecord.from_mapping(
                json.loads(str(row["record_json"]))
            )
            if (
                int(row["anchor_sequence"]) != expected_sequence
                or int(row["signed_sequence"]) != expected_sequence
                or record.intent.anchor_sequence != expected_sequence
                or record.intent.signed_sequence != expected_sequence
                or record.intent.prior_anchor_root_hash216 != prior
                or record.intent.signed_checkpoint_root_hash216
                != str(row["signed_checkpoint_root_hash216"])
                or record.anchor_root_hash216 != str(row["anchor_root_hash216"])
                or record.evidence.authority_id != str(row["authority_id"])
                or record.evidence.gen_time_utc != str(row["gen_time_utc"])
                or record.evidence.tsa_serial_hex != str(row["tsa_serial_hex"])
            ):
                raise Pass213TimestampError(
                    "PASS213_TIMESTAMP_ANCHOR_CHAIN_DISCONTINUITY"
                )
            signed = SignedInventoryCheckpoint.from_mapping(record.signed_checkpoint)
            if signed.prior_signed_checkpoint_root_hash216 != prior_signed:
                raise Pass213TimestampError(
                    "PASS213_TIMESTAMP_SIGNED_CHECKPOINT_CHAIN_DISCONTINUITY"
                )
            if record.intent.requested_timestamp_ns < prior_requested_ns:
                raise Pass213TimestampError(
                    "PASS213_TIMESTAMP_LOCAL_BOUNDARY_REGRESSION"
                )
            current_time = datetime.fromisoformat(
                record.evidence.gen_time_utc.replace("Z", "+00:00")
            )
            if prior_time is not None and current_time < prior_time:
                raise Pass213TimestampError("PASS213_TIMESTAMP_TSA_TIME_REGRESSION")
            serial_key = (
                record.evidence.authority_id,
                record.evidence.tsa_subject,
                record.evidence.tsa_serial_hex,
            )
            if serial_key in serials:
                raise Pass213TimestampError("PASS213_TIMESTAMP_TSA_SERIAL_REUSE")
            record.validate(
                verifier_bundle=self._verifier_bundle,
                timestamp_verifier=self._timestamp_verifier,
            )
            serials.add(serial_key)
            prior = record.anchor_root_hash216
            prior_signed = signed.signed_checkpoint_root_hash216
            prior_requested_ns = record.intent.requested_timestamp_ns
            prior_time = current_time
        if str(self._meta("anchor_head_hash216")) != prior:
            raise Pass213TimestampError("PASS213_TIMESTAMP_ANCHOR_HEAD_MISMATCH")
        return True

    def current_anchor_head(self) -> str:
        return str(self._meta("anchor_head_hash216"))

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "TrustedTimestampAnchorStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


__all__ = [
    "ITERATION",
    "RUNTIME_CLASSIFICATION",
    "RFC3161_CONTENT_TYPE_QUERY",
    "RFC3161_CONTENT_TYPE_REPLY",
    "Pass213TimestampError",
    "TimestampAnchorIntent",
    "RFC3161TimestampEvidence",
    "RFC3161Transport",
    "HTTPRFC3161Transport",
    "OpenSSLTSATransport",
    "RFC3161TimestampVerifier",
    "TrustedTimestampAnchorRecord",
    "TrustedTimestampAnchorStore",
]

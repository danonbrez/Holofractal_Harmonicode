from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import replace
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import threading
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_backend.runtime.hhs_pass213_pqc_enclosure_v1 import (
    PQCProtectedAuthority,
    sign_inventory_checkpoint,
)
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import (
    HTTPRFC3161Transport,
    OpenSSLTSATransport,
    Pass213TimestampError,
    RFC3161TimestampVerifier,
    TimestampAnchorIntent,
    TrustedTimestampAnchorRecord,
    TrustedTimestampAnchorStore,
)
from tests.test_pass213_pqc_enclosure_v1 import synthetic_checkpoint

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
TIMESTAMP_MEMORY_KEY = bytes((index * 31 + 11) % 256 for index in range(32))


def _run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(
        command,
        cwd=None if cwd is None else str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class Pass213Iteration7TrustedTimestampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._build = tempfile.TemporaryDirectory(prefix="pass213-timestamp-build-")
        cls.library = Path(cls._build.name) / "libhhs_pass213_secure_arena.so"
        _run(
            [
                "cc", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", str(SOURCE),
                "-o", str(cls.library),
            ],
            cwd=ROOT,
        )
        cls.pqc_authority = PQCProtectedAuthority(
            library_path=cls.library,
            memory_root_key=TIMESTAMP_MEMORY_KEY,
            owner_id="PASS213_TIMESTAMP_TEST_PQC_AUTHORITY",
        )
        cls.envelope1 = sign_inventory_checkpoint(
            checkpoint=synthetic_checkpoint(1),
            authority=cls.pqc_authority,
            signed_sequence=1,
            prior_signed_checkpoint_root_hash216="0" * 64,
        )
        cls.envelope2 = sign_inventory_checkpoint(
            checkpoint=synthetic_checkpoint(2),
            authority=cls.pqc_authority,
            signed_sequence=2,
            prior_signed_checkpoint_root_hash216=(
                cls.envelope1.signed_checkpoint_root_hash216
            ),
        )
        cls._tsa = tempfile.TemporaryDirectory(prefix="pass213-rfc3161-tsa-")
        cls.tsa_dir = Path(cls._tsa.name)
        cls._create_tsa(cls.tsa_dir)
        cls.local_transport = OpenSSLTSATransport(
            config_path=cls.tsa_dir / "tsa.cnf",
            section="tsa_config1",
        )
        cls.verifier = RFC3161TimestampVerifier(
            trust_bundle_path=cls.tsa_dir / "ca.pem"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        receipts = cls.pqc_authority.close()
        assert len(receipts) == 3
        assert all(receipt.event == "DESTROY" for receipt in receipts)
        cls._tsa.cleanup()
        cls._build.cleanup()

    @classmethod
    def _create_tsa(cls, directory: Path) -> None:
        _run(
            [
                "openssl", "req", "-x509", "-newkey", "rsa:3072",
                "-keyout", "ca.key", "-out", "ca.pem", "-sha256",
                "-days", "2", "-nodes", "-subj",
                "/CN=HHS Pass 213 Test TSA Root",
            ],
            cwd=directory,
        )
        _run(
            [
                "openssl", "req", "-newkey", "rsa:3072",
                "-keyout", "tsa.key", "-out", "tsa.csr", "-sha256",
                "-nodes", "-subj", "/CN=HHS Pass 213 Test TSA",
            ],
            cwd=directory,
        )
        (directory / "tsa.ext").write_text(
            "basicConstraints=critical,CA:FALSE\n"
            "keyUsage=critical,digitalSignature,nonRepudiation\n"
            "extendedKeyUsage=critical,timeStamping\n"
            "subjectKeyIdentifier=hash\n"
            "authorityKeyIdentifier=keyid,issuer\n",
            encoding="utf-8",
        )
        _run(
            [
                "openssl", "x509", "-req", "-in", "tsa.csr",
                "-CA", "ca.pem", "-CAkey", "ca.key", "-CAcreateserial",
                "-out", "tsa.pem", "-days", "2", "-sha256",
                "-extfile", "tsa.ext",
            ],
            cwd=directory,
        )
        (directory / "tsaserial").write_text("01\n", encoding="ascii")
        (directory / "tsa.cnf").write_text(
            "[ tsa ]\n"
            "default_tsa = tsa_config1\n"
            "[ tsa_config1 ]\n"
            "dir = .\n"
            "serial = $dir/tsaserial\n"
            "crypto_device = builtin\n"
            "signer_cert = $dir/tsa.pem\n"
            "certs = $dir/ca.pem\n"
            "signer_key = $dir/tsa.key\n"
            "signer_digest = sha256\n"
            "default_policy = 1.2.3.4.1\n"
            "other_policies = 1.2.3.4.5.6\n"
            "digests = sha256, sha384, sha512\n"
            "accuracy = secs:1, millisecs:500, microsecs:100\n"
            "clock_precision_digits = 3\n"
            "ordering = yes\n"
            "tsa_name = yes\n"
            "ess_cert_id_chain = no\n"
            "ess_cert_id_alg = sha256\n",
            encoding="utf-8",
        )

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-timestamp-")
        self.database = Path(self._temp.name) / "anchors.sqlite3"

    def tearDown(self) -> None:
        self._temp.cleanup()

    def _intent(self, *, lineage: str | None = None) -> TimestampAnchorIntent:
        return TimestampAnchorIntent.create(
            signed_sequence=1,
            signed_checkpoint_root_hash216=(
                self.envelope1.signed_checkpoint_root_hash216
            ),
            verifier_bundle_root_hash216=(
                self.envelope1.verifier_bundle_root_hash216
            ),
            prior_anchor_root_hash216="0" * 64,
            hash216_lineage_root=lineage or hash216("timestamp-lineage", b"one"),
            requested_timestamp_ns=7_000_001,
            authority_id="HHS_TEST_EXTERNAL_TSA",
        )

    def test_rfc3161_evidence_round_trip_and_intent_substitution_rejection(self) -> None:
        intent = self._intent()
        evidence = self.verifier.issue(
            intent=intent,
            transport=self.local_transport,
        )
        self.assertTrue(
            self.verifier.verify_evidence(intent=intent, evidence=evidence)
        )
        self.assertEqual(
            evidence.message_imprint_sha256,
            sha256(intent.anchor_message()).hexdigest(),
        )
        self.assertTrue(evidence.nonce_hex.startswith("0x"))
        changed_intent = self._intent(
            lineage=hash216("timestamp-lineage", b"substituted")
        )
        with self.assertRaisesRegex(Pass213TimestampError, "MESSAGE_IMPRINT"):
            self.verifier.verify_evidence(
                intent=changed_intent,
                evidence=evidence,
            )

    def test_http_rfc3161_transport_uses_protocol_content_types(self) -> None:
        local_transport = self.local_transport
        observed: dict[str, str] = {}

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                observed["content_type"] = self.headers.get("Content-Type", "")
                observed["accept"] = self.headers.get("Accept", "")
                length = int(self.headers["Content-Length"])
                response = local_transport.submit(self.rfile.read(length))
                self.send_response(200)
                self.send_header("Content-Type", "application/timestamp-reply")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            endpoint = f"http://127.0.0.1:{server.server_port}/timestamp"
            evidence = self.verifier.issue(
                intent=self._intent(),
                transport=HTTPRFC3161Transport(endpoint),
            )
            self.assertEqual(evidence.authority_id, "HHS_TEST_EXTERNAL_TSA")
            self.assertEqual(
                observed["content_type"], "application/timestamp-query"
            )
            self.assertEqual(observed["accept"], "application/timestamp-reply")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_two_anchor_chain_persists_and_reopens_without_submission_authority(self) -> None:
        store = TrustedTimestampAnchorStore(
            database_path=self.database,
            verifier_bundle=self.pqc_authority.verifier_bundle,
            timestamp_verifier=self.verifier,
            transport=self.local_transport,
        )
        first = store.append(
            signed_checkpoint=self.envelope1,
            hash216_lineage_root=hash216("timestamp-lineage", b"one"),
            requested_timestamp_ns=7_000_001,
            authority_id="HHS_TEST_EXTERNAL_TSA",
        )
        second = store.append(
            signed_checkpoint=self.envelope2,
            hash216_lineage_root=hash216("timestamp-lineage", b"two"),
            requested_timestamp_ns=7_000_002,
            authority_id="HHS_TEST_EXTERNAL_TSA",
        )
        self.assertEqual(
            second.intent.prior_anchor_root_hash216,
            first.anchor_root_hash216,
        )
        self.assertTrue(store.verify_chain())
        store.close()

        verifier_only = TrustedTimestampAnchorStore(
            database_path=self.database,
            verifier_bundle=self.pqc_authority.verifier_bundle,
            timestamp_verifier=self.verifier,
        )
        try:
            self.assertTrue(verifier_only.verify_chain())
            self.assertEqual(
                verifier_only.current_anchor_head(), second.anchor_root_hash216
            )
            with self.assertRaisesRegex(
                Pass213TimestampError, "SUBMISSION_TRANSPORT_REQUIRED"
            ):
                verifier_only.append(
                    signed_checkpoint=self.envelope2,
                    hash216_lineage_root=hash216("timestamp-lineage", b"three"),
                    requested_timestamp_ns=7_000_003,
                    authority_id="HHS_TEST_EXTERNAL_TSA",
                )
        finally:
            verifier_only.close()

    def test_response_der_tamper_fails_even_when_local_roots_are_recomputed(self) -> None:
        store = TrustedTimestampAnchorStore(
            database_path=self.database,
            verifier_bundle=self.pqc_authority.verifier_bundle,
            timestamp_verifier=self.verifier,
            transport=self.local_transport,
        )
        store.append(
            signed_checkpoint=self.envelope1,
            hash216_lineage_root=hash216("timestamp-lineage", b"one"),
            requested_timestamp_ns=7_000_001,
            authority_id="HHS_TEST_EXTERNAL_TSA",
        )
        store.close()

        connection = sqlite3.connect(self.database)
        row = connection.execute(
            "SELECT record_json FROM timestamp_anchors WHERE anchor_sequence=1"
        ).fetchone()
        record = TrustedTimestampAnchorRecord.from_mapping(json.loads(row[0]))
        response = bytearray(b64decode(record.evidence.response_der_b64))
        response[-1] ^= 1
        changed = replace(
            record.evidence,
            response_der_b64=b64encode(bytes(response)).decode("ascii"),
            response_sha256=sha256(bytes(response)).hexdigest(),
            verification_receipt_hash216=hash216("tampered-verification", b"x"),
            evidence_root_hash216="",
        )
        changed = replace(
            changed,
            evidence_root_hash216=hash216(
                "rfc3161-timestamp-evidence",
                canonical_bytes(changed.unsigned_payload()),
            ),
        )
        changed_record = replace(record, evidence=changed, anchor_root_hash216="")
        changed_record = replace(
            changed_record,
            anchor_root_hash216=hash216(
                "trusted-external-timestamp-anchor",
                canonical_bytes(changed_record.rooted_payload()),
            ),
        )
        connection.execute(
            "UPDATE timestamp_anchors SET anchor_root_hash216=?, record_json=? "
            "WHERE anchor_sequence=1",
            (
                changed_record.anchor_root_hash216,
                canonical_bytes(changed_record.to_mapping()).decode("utf-8"),
            ),
        )
        connection.execute(
            "UPDATE timestamp_anchor_meta SET value=? "
            "WHERE key='anchor_head_hash216'",
            (changed_record.anchor_root_hash216,),
        )
        connection.commit()
        connection.close()

        with self.assertRaisesRegex(
            Pass213TimestampError, "RFC3161_VERIFICATION_FAILED"
        ):
            TrustedTimestampAnchorStore(
                database_path=self.database,
                verifier_bundle=self.pqc_authority.verifier_bundle,
                timestamp_verifier=self.verifier,
            )

    def test_wrong_trust_bundle_and_sequence_gap_are_rejected(self) -> None:
        evidence = self.verifier.issue(
            intent=self._intent(),
            transport=self.local_transport,
        )
        wrong_verifier = RFC3161TimestampVerifier(
            trust_bundle_path=self.tsa_dir / "tsa.pem"
        )
        with self.assertRaisesRegex(Pass213TimestampError, "TRUST_BUNDLE_MISMATCH"):
            wrong_verifier.verify_evidence(
                intent=self._intent(),
                evidence=evidence,
            )

        store = TrustedTimestampAnchorStore(
            database_path=self.database,
            verifier_bundle=self.pqc_authority.verifier_bundle,
            timestamp_verifier=self.verifier,
            transport=self.local_transport,
        )
        try:
            with self.assertRaisesRegex(
                Pass213TimestampError, "SIGNED_SEQUENCE_DISCONTINUITY"
            ):
                store.append(
                    signed_checkpoint=self.envelope2,
                    hash216_lineage_root=hash216("timestamp-lineage", b"gap"),
                    requested_timestamp_ns=7_000_002,
                    authority_id="HHS_TEST_EXTERNAL_TSA",
                )
        finally:
            store.close()

    def test_local_boundary_regression_is_rejected_before_second_submission(self) -> None:
        store = TrustedTimestampAnchorStore(
            database_path=self.database,
            verifier_bundle=self.pqc_authority.verifier_bundle,
            timestamp_verifier=self.verifier,
            transport=self.local_transport,
        )
        try:
            store.append(
                signed_checkpoint=self.envelope1,
                hash216_lineage_root=hash216("timestamp-lineage", b"one"),
                requested_timestamp_ns=7_000_002,
                authority_id="HHS_TEST_EXTERNAL_TSA",
            )
            with self.assertRaisesRegex(
                Pass213TimestampError, "LOCAL_BOUNDARY_REGRESSION"
            ):
                store.append(
                    signed_checkpoint=self.envelope2,
                    hash216_lineage_root=hash216("timestamp-lineage", b"two"),
                    requested_timestamp_ns=7_000_001,
                    authority_id="HHS_TEST_EXTERNAL_TSA",
                )
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()

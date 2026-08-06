from __future__ import annotations

from base64 import b64decode, b64encode
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import canonical_bytes, hash216
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_persistent_inventory_v1 import (
    InventoryCheckpoint,
    PersistentCompiledROMInventory,
)
from hhs_backend.runtime.hhs_pass213_pqc_enclosure_v1 import (
    PQCProtectedAuthority,
    PQCPublicKeyRecord,
    PQCVerifierBundle,
    Pass213PQCError,
    PostQuantumCheckpointStore,
    create_recovery_capsule,
    open_recovery_capsule,
    sign_inventory_checkpoint,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from tests.test_pass213_persistent_inventory_v1 import (
    ADMISSION_KEY,
    DELETION_KEY,
    INVENTORY_KEY,
    MEMORY_KEY,
)
from tests.test_pass213_recovery_admission_v1 import compiled_entry

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
PQC_MEMORY_KEY = bytes((index * 23 + 17) % 256 for index in range(32))
RECOVERY_KEY = bytes((index * 29 + 3) % 256 for index in range(32))


def synthetic_checkpoint(sequence: int = 1) -> InventoryCheckpoint:
    unsigned = {
        "schema": "HHS_PASS_213_INVENTORY_CHECKPOINT_V1",
        "contract": "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243",
        "iteration": 5,
        "checkpoint_sequence": sequence,
        "genesis_epoch": 6,
        "created_timestamp_ns": 6_000 + sequence,
        "authority_id": "pqc-test-authority",
        "label": f"PQC_TEST_{sequence}",
        "prior_checkpoint_root_hash216": "0" * 64,
        "event_chain_head_hash216": hash216("test-event-head", str(sequence).encode()),
        "inventory_root_hash216": hash216("test-inventory-root", str(sequence).encode()),
        "live_entries": [],
        "tombstones": [],
    }
    root = hash216("persistent-inventory-checkpoint", canonical_bytes(unsigned))
    return InventoryCheckpoint(
        checkpoint_sequence=sequence,
        genesis_epoch=6,
        created_timestamp_ns=6_000 + sequence,
        authority_id="pqc-test-authority",
        label=f"PQC_TEST_{sequence}",
        prior_checkpoint_root_hash216="0" * 64,
        event_chain_head_hash216=unsigned["event_chain_head_hash216"],
        inventory_root_hash216=unsigned["inventory_root_hash216"],
        live_entries=(),
        tombstones=(),
        checkpoint_root_hash216=root,
        authentication_tag="a" * 64,
    )


class Pass213Iteration6PQCEnclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._build = tempfile.TemporaryDirectory(prefix="pass213-pqc-build-")
        cls.library = Path(cls._build.name) / "libhhs_pass213_secure_arena.so"
        subprocess.run(
            [
                "cc", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", str(SOURCE),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.authority = PQCProtectedAuthority(
            library_path=cls.library,
            memory_root_key=PQC_MEMORY_KEY,
            owner_id="PASS213_PQC_TEST_AUTHORITY",
        )
        cls.sample_checkpoint = synthetic_checkpoint()
        cls.sample_envelope = sign_inventory_checkpoint(
            checkpoint=cls.sample_checkpoint,
            authority=cls.authority,
            signed_sequence=1,
            prior_signed_checkpoint_root_hash216="0" * 64,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        receipts = cls.authority.close()
        assert len(receipts) == 3
        assert all(receipt.event == "DESTROY" for receipt in receipts)
        assert all(
            receipt.details["zeroized_before_release"] for receipt in receipts
        )
        cls._build.cleanup()

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-pqc-")

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_suite_and_secret_keys_are_native_protected(self) -> None:
        suite = self.authority.suite
        self.assertIn("ML-KEM", suite.ml_kem)
        self.assertIn("ML-DSA", suite.ml_dsa)
        normalized_slh = "".join(
            character.lower()
            for character in suite.slh_dsa
            if character.isalnum()
        )
        self.assertIn("slhdsa", normalized_slh)
        self.assertIn("sha2", normalized_slh)
        self.assertIn("128s", normalized_slh)
        records = self.authority.protected_secret_records()
        self.assertEqual(len(records), 3)
        self.assertEqual(
            {record.role for record in records},
            {"recovery-kem", "operational-signature", "archival-signature"},
        )
        for role, arena in self.authority._arenas.items():
            status = arena.status()
            self.assertTrue(status["sealed"], role)
            self.assertTrue(status["locked"], role)
            self.assertTrue(status["dontdump"], role)
            self.assertTrue(status["dontfork"], role)
            self.assertFalse(status["executable"], role)
        rendered = json.dumps(self.authority.verifier_bundle.to_mapping())
        self.assertNotIn("secret", rendered.lower())

    def test_dual_checkpoint_signatures_bind_message_and_public_keys(self) -> None:
        envelope = self.sample_envelope
        self.assertTrue(envelope.validate(self.authority.verifier_bundle))
        self.assertEqual(
            envelope.operational_signature.algorithm,
            self.authority.suite.ml_dsa,
        )
        self.assertEqual(
            envelope.archival_signature.algorithm,
            self.authority.suite.slh_dsa,
        )
        altered_checkpoint = dict(envelope.checkpoint)
        altered_checkpoint["label"] = "ALTERED"
        altered = replace(envelope, checkpoint=altered_checkpoint)
        with self.assertRaises(Pass213PQCError):
            altered.validate(self.authority.verifier_bundle)

        public = self.authority.verifier_bundle.operational_signature
        changed_key = bytearray(public.public_key())
        changed_key[0] ^= 1
        wrong_operational = PQCPublicKeyRecord.create(
            public.role,
            public.algorithm,
            bytes(changed_key),
        )
        wrong_bundle = PQCVerifierBundle.create(
            suite=self.authority.suite,
            recovery_kem=self.authority.verifier_bundle.recovery_kem,
            operational_signature=wrong_operational,
            archival_signature=self.authority.verifier_bundle.archival_signature,
        )
        with self.assertRaises(Pass213PQCError):
            envelope.validate(wrong_bundle)

    def test_ml_kem_recovery_capsule_round_trip_and_tamper_rejection(self) -> None:
        capsule = create_recovery_capsule(
            authority=self.authority,
            recovery_key=RECOVERY_KEY,
            checkpoint_root_hash216=self.sample_checkpoint.checkpoint_root_hash216,
            sequence=1,
        )
        self.assertEqual(open_recovery_capsule(capsule, self.authority), RECOVERY_KEY)
        self.assertNotIn(_b64_text(RECOVERY_KEY), capsule.encrypted_recovery_key_b64)

        encrypted = bytearray(b64decode(capsule.encrypted_recovery_key_b64))
        encrypted[-1] ^= 1
        altered_unsigned = {
            **capsule.unsigned_payload(),
            "encrypted_recovery_key_b64": b64encode(bytes(encrypted)).decode("ascii"),
        }
        altered = replace(
            capsule,
            encrypted_recovery_key_b64=altered_unsigned[
                "encrypted_recovery_key_b64"
            ],
            capsule_root_hash216=hash216(
                "pqc-recovery-capsule",
                canonical_bytes(altered_unsigned),
            ),
        )
        with self.assertRaisesRegex(Pass213PQCError, "DECRYPTION_FAILED"):
            open_recovery_capsule(altered, self.authority)

    def test_signed_checkpoint_store_integrates_iteration5_and_reopens_publicly(self) -> None:
        database = Path(self._temp.name) / "integrated.sqlite3"
        native = NativeProtectedCompiledROMStore(
            library_path=self.library,
            admission_key=ADMISSION_KEY,
            memory_root_key=MEMORY_KEY,
            owner_id="PASS213_PQC_INTEGRATION_NATIVE",
        )
        inventory = PersistentCompiledROMInventory(
            database_path=database,
            protected_store=native,
            inventory_key=INVENTORY_KEY,
            deletion_key=DELETION_KEY,
            admission_key=ADMISSION_KEY,
            genesis_epoch=6,
        )
        entry = compiled_entry("PQC_SIGNED_CHECKPOINT_INTEGRATION_V1")
        inventory.admit_carrier(
            protect_compiled_rom_entry(entry, ADMISSION_KEY),
            authority_id="vm81-admission",
            timestamp_ns=6_100,
        )
        checkpoint = inventory.create_checkpoint(
            authority_id="pqc-checkpoint-authority",
            label="SIGNED_INTEGRATION",
            timestamp_ns=6_101,
        )
        inventory.close()
        native.close()

        store = PostQuantumCheckpointStore(
            database_path=database,
            verifier_bundle=self.authority.verifier_bundle,
            authority=self.authority,
        )
        envelope, capsule = store.append(
            checkpoint=checkpoint,
            recovery_key=RECOVERY_KEY,
        )
        self.assertTrue(store.verify_chain())
        self.assertEqual(store.recover_key(1), RECOVERY_KEY)
        self.assertEqual(
            envelope.signed_checkpoint_root_hash216,
            store.current_signed_head(),
        )
        self.assertEqual(
            capsule.checkpoint_root_hash216,
            checkpoint.checkpoint_root_hash216,
        )
        store.close()

        verifier_only = PostQuantumCheckpointStore(
            database_path=database,
            verifier_bundle=self.authority.verifier_bundle,
        )
        try:
            self.assertTrue(verifier_only.verify_chain())
            with self.assertRaisesRegex(Pass213PQCError, "RECOVERY_AUTHORITY_REQUIRED"):
                verifier_only.recover_key(1)
        finally:
            verifier_only.close()

    def test_database_envelope_and_capsule_tampering_fail_on_reopen(self) -> None:
        database = Path(self._temp.name) / "tamper.sqlite3"
        store = PostQuantumCheckpointStore(
            database_path=database,
            verifier_bundle=self.authority.verifier_bundle,
            authority=self.authority,
        )
        envelope, capsule = store.append(
            checkpoint=synthetic_checkpoint(9),
            recovery_key=RECOVERY_KEY,
        )
        store.close()

        connection = sqlite3.connect(database)
        original_envelope = connection.execute(
            "SELECT envelope_json FROM pqc_checkpoints WHERE signed_sequence=1"
        ).fetchone()[0]
        value = json.loads(original_envelope)
        value["checkpoint"]["label"] = "ALTERED_HISTORY"
        connection.execute(
            "UPDATE pqc_checkpoints SET envelope_json=? WHERE signed_sequence=1",
            (json.dumps(value, sort_keys=True, separators=(",", ":")),),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(Pass213PQCError):
            PostQuantumCheckpointStore(
                database_path=database,
                verifier_bundle=self.authority.verifier_bundle,
            )

        connection = sqlite3.connect(database)
        connection.execute(
            "UPDATE pqc_checkpoints SET envelope_json=? WHERE signed_sequence=1",
            (original_envelope,),
        )
        original_capsule = connection.execute(
            "SELECT capsule_json FROM pqc_recovery_capsules WHERE signed_sequence=1"
        ).fetchone()[0]
        capsule_value = json.loads(original_capsule)
        capsule_value["nonce_b64"] = b64encode(b"x" * 12).decode("ascii")
        connection.execute(
            "UPDATE pqc_recovery_capsules SET capsule_json=? WHERE signed_sequence=1",
            (json.dumps(capsule_value, sort_keys=True, separators=(",", ":")),),
        )
        connection.commit()
        connection.close()
        with self.assertRaises(Pass213PQCError):
            PostQuantumCheckpointStore(
                database_path=database,
                verifier_bundle=self.authority.verifier_bundle,
            )

        self.assertEqual(len(envelope.signed_checkpoint_root_hash216), 64)
        self.assertEqual(len(capsule.capsule_root_hash216), 64)

    def test_verifier_bundle_round_trip_and_hash_tamper_rejection(self) -> None:
        value = self.authority.verifier_bundle.to_mapping()
        rebuilt = PQCVerifierBundle.from_mapping(value)
        self.assertEqual(rebuilt, self.authority.verifier_bundle)
        altered = dict(value)
        altered["bundle_root_hash216"] = "0" * 64
        with self.assertRaisesRegex(Pass213PQCError, "BUNDLE_HASH_MISMATCH"):
            PQCVerifierBundle.from_mapping(altered)


def _b64_text(value: bytes) -> str:
    return b64encode(value).decode("ascii")


if __name__ == "__main__":
    unittest.main()

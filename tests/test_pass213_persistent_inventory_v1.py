from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_persistent_inventory_v1 import (
    Pass213PersistentInventoryError,
    PersistentCompiledROMInventory,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from tests.test_pass213_recovery_admission_v1 import (
    ADMISSION_KEY,
    compiled_entry,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
INVENTORY_KEY = bytes((index * 13 + 7) % 256 for index in range(32))
DELETION_KEY = bytes((index * 17 + 9) % 256 for index in range(32))
MEMORY_KEY = bytes((index * 19 + 11) % 256 for index in range(32))


class Pass213Iteration5PersistentInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._build = tempfile.TemporaryDirectory(prefix="pass213-inventory-build-")
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

    @classmethod
    def tearDownClass(cls) -> None:
        cls._build.cleanup()

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-inventory-")
        self.database = Path(self._temp.name) / "compiled-rom-inventory.sqlite3"

    def tearDown(self) -> None:
        self._temp.cleanup()

    def store(self, owner: str) -> NativeProtectedCompiledROMStore:
        return NativeProtectedCompiledROMStore(
            library_path=self.library,
            admission_key=ADMISSION_KEY,
            memory_root_key=MEMORY_KEY,
            owner_id=owner,
        )

    def inventory(
        self,
        store: NativeProtectedCompiledROMStore,
    ) -> PersistentCompiledROMInventory:
        return PersistentCompiledROMInventory(
            database_path=self.database,
            protected_store=store,
            inventory_key=INVENTORY_KEY,
            deletion_key=DELETION_KEY,
            admission_key=ADMISSION_KEY,
            genesis_epoch=5,
        )

    @staticmethod
    def carrier(operation_id: str):
        entry = compiled_entry(operation_id)
        return entry, protect_compiled_rom_entry(entry, ADMISSION_KEY)

    def test_admission_commits_persistent_root_and_runtime_match(self) -> None:
        entry, carrier = self.carrier("PERSISTENT_ADMIT_V1")
        store = self.store("PERSISTENT_ADMIT")
        inventory = self.inventory(store)
        try:
            record = inventory.admit_carrier(
                carrier,
                authority_id="vm81-admission",
                timestamp_ns=5_000,
            )
            report = inventory.reconcile()
            self.assertEqual(record.entry_hash216, entry.entry_hash216)
            self.assertTrue(report.valid)
            self.assertEqual(report.expected_live_count, 1)
            self.assertEqual(report.actual_protected_count, 1)
            self.assertEqual(len(report.inventory_root_hash216), 64)
            self.assertTrue(inventory.verify_persistent_chain())
        finally:
            inventory.close()
            store.close()

    def test_unexplained_native_absence_is_detected_and_repaired(self) -> None:
        entry, carrier = self.carrier("PERSISTENT_REPAIR_V1")
        store = self.store("PERSISTENT_REPAIR")
        inventory = self.inventory(store)
        try:
            inventory.admit_carrier(
                carrier,
                authority_id="admission",
                timestamp_ns=5_100,
            )
            raw_receipt = store.retire_hash216(entry.entry_hash216)
            self.assertEqual(raw_receipt.event, "DESTROY")
            report = inventory.reconcile()
            self.assertFalse(report.valid)
            self.assertEqual(
                report.missing_live_entry_hashes,
                (entry.entry_hash216,),
            )
            inventory.recover_missing_entry(
                entry.entry_hash216,
                authority_id="kernel-recovery",
                timestamp_ns=5_101,
            )
            self.assertTrue(inventory.reconcile().valid)
            self.assertEqual(store.lookup_hash216(entry.entry_hash216), entry)
        finally:
            inventory.close()
            store.close()

    def test_restart_rehydrates_every_live_entry_from_retained_carriers(self) -> None:
        entries = [
            self.carrier("PERSISTENT_RESTART_A_V1"),
            self.carrier("PERSISTENT_RESTART_B_V1"),
        ]
        first_store = self.store("PERSISTENT_RESTART_FIRST")
        first_inventory = self.inventory(first_store)
        for offset, (_, carrier) in enumerate(entries):
            first_inventory.admit_carrier(
                carrier,
                authority_id="admission",
                timestamp_ns=5_200 + offset,
            )
        first_inventory.close()
        first_store.close()

        second_store = self.store("PERSISTENT_RESTART_SECOND")
        second_inventory = self.inventory(second_store)
        try:
            before = second_inventory.reconcile()
            self.assertEqual(len(before.missing_live_entry_hashes), 2)
            recovered = second_inventory.recover_all_missing(
                authority_id="restart-recovery",
                timestamp_ns=5_300,
            )
            self.assertEqual(len(recovered), 2)
            self.assertTrue(second_inventory.reconcile().valid)
            for entry, _ in entries:
                self.assertEqual(
                    second_store.lookup_hash216(entry.entry_hash216), entry
                )
        finally:
            second_inventory.close()
            second_store.close()

    def test_authorized_retirement_retains_tombstone_and_zeroizes_arena(self) -> None:
        entry, carrier = self.carrier("PERSISTENT_TOMBSTONE_V1")
        store = self.store("PERSISTENT_TOMBSTONE")
        inventory = self.inventory(store)
        try:
            inventory.admit_carrier(
                carrier,
                authority_id="admission",
                timestamp_ns=5_400,
            )
            authorization = inventory.create_deletion_authorization(
                entry_hash216=entry.entry_hash216,
                authority_id="kernel-retirement",
                reason="SUPERSEDED_COMPILED_OPERATION",
                nonce="retire-1",
                timestamp_ns=5_401,
            )
            event, receipt = inventory.authorized_retire(authorization)
            self.assertEqual(event["event_type"], "TOMBSTONE")
            self.assertIsNotNone(receipt)
            assert receipt is not None
            self.assertEqual(receipt.event, "DESTROY")
            self.assertTrue(receipt.details["zeroized_before_release"])
            report = inventory.reconcile()
            self.assertTrue(report.valid)
            self.assertEqual(report.expected_live_count, 0)
            self.assertEqual(report.expected_tombstone_count, 1)
            with self.assertRaisesRegex(
                Pass213PersistentInventoryError,
                "TOMBSTONED_ENTRY_RECOVERY_REJECTED",
            ):
                inventory.recover_missing_entry(
                    entry.entry_hash216,
                    authority_id="invalid-recovery",
                    timestamp_ns=5_402,
                )
        finally:
            inventory.close()
            store.close()

    def test_stale_deletion_authorization_is_rejected(self) -> None:
        first_entry, first_carrier = self.carrier("PERSISTENT_STALE_A_V1")
        _, second_carrier = self.carrier("PERSISTENT_STALE_B_V1")
        store = self.store("PERSISTENT_STALE")
        inventory = self.inventory(store)
        try:
            inventory.admit_carrier(
                first_carrier,
                authority_id="admission",
                timestamp_ns=5_500,
            )
            stale = inventory.create_deletion_authorization(
                entry_hash216=first_entry.entry_hash216,
                authority_id="kernel-retirement",
                reason="STALE_TEST",
                nonce="stale-1",
                timestamp_ns=5_501,
            )
            inventory.admit_carrier(
                second_carrier,
                authority_id="admission",
                timestamp_ns=5_502,
            )
            with self.assertRaisesRegex(
                Pass213PersistentInventoryError,
                "DELETION_AUTHORIZATION_STALE",
            ):
                inventory.authorized_retire(stale)
        finally:
            inventory.close()
            store.close()

    def test_tampered_deletion_authorization_is_rejected(self) -> None:
        entry, carrier = self.carrier("PERSISTENT_AUTH_TAMPER_V1")
        store = self.store("PERSISTENT_AUTH_TAMPER")
        inventory = self.inventory(store)
        try:
            inventory.admit_carrier(
                carrier,
                authority_id="admission",
                timestamp_ns=5_600,
            )
            authorization = inventory.create_deletion_authorization(
                entry_hash216=entry.entry_hash216,
                authority_id="kernel-retirement",
                reason="AUTH_TAMPER_TEST",
                nonce="auth-tamper-1",
                timestamp_ns=5_601,
            )
            altered = replace(authorization, authentication_tag="0" * 64)
            with self.assertRaisesRegex(
                Pass213PersistentInventoryError,
                "DELETION_AUTHORIZATION_INVALID",
            ):
                inventory.authorized_retire(altered)
        finally:
            inventory.close()
            store.close()

    def test_checkpoint_material_recovers_missing_live_entry(self) -> None:
        entry, carrier = self.carrier("PERSISTENT_CHECKPOINT_RECOVERY_V1")
        store = self.store("PERSISTENT_CHECKPOINT")
        inventory = self.inventory(store)
        try:
            inventory.admit_carrier(
                carrier,
                authority_id="admission",
                timestamp_ns=5_700,
            )
            checkpoint = inventory.create_checkpoint(
                authority_id="checkpoint-authority",
                label="PRE_EXECUTION_CHECKPOINT",
                timestamp_ns=5_701,
            )
            store.retire_hash216(entry.entry_hash216)
            recovered = inventory.recover_missing_entry(
                entry.entry_hash216,
                authority_id="checkpoint-recovery",
                checkpoint_root_hash216=checkpoint.checkpoint_root_hash216,
                timestamp_ns=5_702,
            )
            self.assertEqual(recovered.entry_hash216, entry.entry_hash216)
            self.assertTrue(inventory.reconcile().valid)
        finally:
            inventory.close()
            store.close()

    def test_untracked_protected_entry_is_detected(self) -> None:
        entry, carrier = self.carrier("PERSISTENT_UNTRACKED_V1")
        store = self.store("PERSISTENT_UNTRACKED")
        inventory = self.inventory(store)
        try:
            store.inspect_correct_protect_and_admit(carrier)
            report = inventory.reconcile()
            self.assertFalse(report.valid)
            self.assertEqual(
                report.unexpected_protected_entry_hashes,
                (entry.entry_hash216,),
            )
        finally:
            inventory.close()
            store.close()

    def test_event_history_tampering_is_detected_on_reopen(self) -> None:
        _, carrier = self.carrier("PERSISTENT_EVENT_TAMPER_V1")
        store = self.store("PERSISTENT_EVENT_TAMPER")
        inventory = self.inventory(store)
        inventory.admit_carrier(
            carrier,
            authority_id="admission",
            timestamp_ns=5_800,
        )
        inventory.close()
        store.close()

        connection = sqlite3.connect(self.database)
        row = connection.execute(
            "SELECT event_json FROM events WHERE sequence = 1"
        ).fetchone()
        assert row is not None
        event = json.loads(row[0])
        event["reason"] = "ALTERED_HISTORY"
        connection.execute(
            "UPDATE events SET event_json = ? WHERE sequence = 1",
            (json.dumps(event, sort_keys=True, separators=(",", ":")),),
        )
        connection.commit()
        connection.close()

        second_store = self.store("PERSISTENT_EVENT_TAMPER_REOPEN")
        try:
            with self.assertRaisesRegex(
                Pass213PersistentInventoryError,
                "INVENTORY_EVENT_AUTHENTICATION_FAILED",
            ):
                self.inventory(second_store)
        finally:
            second_store.close()

    def test_checkpoint_tampering_is_detected_on_reopen(self) -> None:
        _, carrier = self.carrier("PERSISTENT_CHECKPOINT_TAMPER_V1")
        store = self.store("PERSISTENT_CHECKPOINT_TAMPER")
        inventory = self.inventory(store)
        inventory.admit_carrier(
            carrier,
            authority_id="admission",
            timestamp_ns=5_900,
        )
        checkpoint = inventory.create_checkpoint(
            authority_id="checkpoint-authority",
            label="TAMPER_TARGET",
            timestamp_ns=5_901,
        )
        inventory.close()
        store.close()

        connection = sqlite3.connect(self.database)
        row = connection.execute(
            "SELECT checkpoint_json FROM checkpoints "
            "WHERE checkpoint_root_hash216 = ?",
            (checkpoint.checkpoint_root_hash216,),
        ).fetchone()
        assert row is not None
        value = json.loads(row[0])
        value["label"] = "ALTERED_CHECKPOINT"
        connection.execute(
            "UPDATE checkpoints SET checkpoint_json = ? "
            "WHERE checkpoint_root_hash216 = ?",
            (
                json.dumps(value, sort_keys=True, separators=(",", ":")),
                checkpoint.checkpoint_root_hash216,
            ),
        )
        connection.commit()
        connection.close()

        second_store = self.store("PERSISTENT_CHECKPOINT_TAMPER_REOPEN")
        try:
            with self.assertRaisesRegex(
                Pass213PersistentInventoryError,
                "CHECKPOINT_AUTHENTICATION_FAILED",
            ):
                self.inventory(second_store)
        finally:
            second_store.close()


if __name__ == "__main__":
    unittest.main()

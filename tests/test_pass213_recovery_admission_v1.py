from dataclasses import replace
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    ClosurePath,
    CompiledROMEntry,
    TimestampBoundary,
    ZERO_HASH216,
    ZERO_HASH72,
    derive_key,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    CompiledROMCarrier,
    Pass213RecoveryAdmissionError,
    RecoveryGatedCompiledROMStore,
    inspect_and_correct_carrier,
    protect_compiled_rom_entry,
)

ROOT_KEY = bytes(range(32))
ADMISSION_KEY = derive_key(ROOT_KEY, "RECOVERY-ADMISSION", b"iteration-2")
KERNEL = hash216("test-kernel", b"kernel-v1")
POLICY = hash216("test-policy", b"policy-v1")


def boundary(kind: str, timestamp_ns: int, serial: int) -> TimestampBoundary:
    return TimestampBoundary.create(
        kind=kind,
        timestamp_ns=timestamp_ns,
        serial=serial,
        genesis_epoch=4,
        group_sequence=8,
        parent_hash216=ZERO_HASH216,
        previous_receipt_hash72=ZERO_HASH72,
        kernel_measurement_hash216=KERNEL,
    )


def compiled_entry(operation_id: str = "MUL_EXACT_BIGINT_V1") -> CompiledROMEntry:
    opening = boundary("open", 2_000, 21)
    closing = boundary("close", 2_100, 22)
    closure = ClosurePath.derive(
        derive_key(ROOT_KEY, "PATH", b"iteration-2"),
        5_184,
        b"group-8",
    )
    return CompiledROMEntry.create(
        operation_id=operation_id,
        canonical_operation={
            "opcode": "MUL",
            "operand_types": ["bigint", "bigint"],
        },
        constraints={"overflow": "unbounded", "ordered": True},
        vm81_cell_id=5,
        operation_slot=11,
        g243_control_id=7,
        native_dispatch_id="hhs_native.mul_bigint_v1",
        kernel_policy_hash216=POLICY,
        creation_group_sequence=opening.group_sequence,
        creation_open_boundary_hash216=opening.boundary_hash216,
        creation_close_boundary_hash216=closing.boundary_hash216,
        closure_path_root_hash216=closure.path_root_hash216,
        closure_position=31,
        parent_hash216=opening.parent_hash216,
    )


def with_missing_refs(
    carrier: CompiledROMCarrier,
    refs: set[str],
) -> CompiledROMCarrier:
    shards = tuple(
        replace(shard, payload=None) if shard.ref in refs else shard
        for shard in carrier.protected.shards
    )
    return replace(
        carrier,
        protected=replace(carrier.protected, shards=shards),
    )


def corrupt_first_present_data_shard(
    carrier: CompiledROMCarrier,
) -> CompiledROMCarrier:
    changed = []
    corrupted = False
    for shard in carrier.protected.shards:
        if (
            not corrupted
            and shard.role == "data"
            and shard.payload is not None
        ):
            payload = bytearray(shard.payload)
            payload[0] ^= 1
            changed.append(replace(shard, payload=bytes(payload)))
            corrupted = True
        else:
            changed.append(shard)
    assert corrupted
    return replace(
        carrier,
        protected=replace(carrier.protected, shards=tuple(changed)),
    )


class Pass213Iteration2RecoveryAdmissionTests(unittest.TestCase):
    def test_intact_carrier_recovers_before_admission(self):
        entry = compiled_entry()
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        admission = inspect_and_correct_carrier(carrier, ADMISSION_KEY)
        self.assertEqual(admission.entry, entry)
        self.assertEqual(admission.recovery_outcome, "INTACT")
        self.assertEqual(admission.recovered_shard_refs, ())

        store = RecoveryGatedCompiledROMStore(ADMISSION_KEY)
        admitted = store.admit(admission)
        self.assertEqual(admitted, entry.entry_hash216)
        self.assertEqual(store.lookup_hash216(admitted), entry)
        self.assertEqual(store.lookup_operation(entry.operation_id), entry)
        self.assertEqual(len(store), 1)
        self.assertEqual(len(store.inventory_root()), 64)

    def test_one_missing_data_shard_is_corrected(self):
        entry = compiled_entry()
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        data_ref = next(
            shard.ref
            for shard in carrier.protected.shards
            if shard.role == "data"
        )
        damaged = with_missing_refs(carrier, {data_ref})
        admission = inspect_and_correct_carrier(damaged, ADMISSION_KEY)
        self.assertEqual(admission.entry, entry)
        self.assertEqual(admission.recovery_outcome, "RECOVERED")
        self.assertEqual(admission.recovered_shard_refs, (data_ref,))

    def test_data_and_parity_erasure_is_corrected(self):
        entry = compiled_entry()
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        data_ref = next(
            shard.ref
            for shard in carrier.protected.shards
            if shard.role == "data"
        )
        parity_ref = next(
            shard.ref
            for shard in carrier.protected.shards
            if shard.role == "parity0"
        )
        damaged = with_missing_refs(carrier, {data_ref, parity_ref})
        admission = inspect_and_correct_carrier(damaged, ADMISSION_KEY)
        self.assertEqual(admission.entry.entry_hash216, entry.entry_hash216)
        self.assertEqual(
            admission.recovered_shard_refs,
            tuple(sorted((data_ref, parity_ref))),
        )

    def test_three_erased_shards_fail_before_deserialization(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        refs = {
            shard.ref
            for shard in carrier.protected.shards
            if shard.stripe == 0
        }
        damaged = with_missing_refs(carrier, set(sorted(refs)[:3]))
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "PASS212_RECOVERY_REJECTED",
        ):
            inspect_and_correct_carrier(damaged, ADMISSION_KEY)

    def test_corrupted_shard_fails_before_deserialization(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        damaged = corrupt_first_present_data_shard(carrier)
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "PASS212_RECOVERY_REJECTED",
        ):
            inspect_and_correct_carrier(damaged, ADMISSION_KEY)

    def test_carrier_metadata_tamper_is_rejected(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        altered = replace(
            carrier,
            expected_entry_hash216=hash216("wrong-entry", b"wrong"),
        )
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "CARRIER_ROOT_MISMATCH",
        ):
            inspect_and_correct_carrier(altered, ADMISSION_KEY)

    def test_carrier_authentication_tamper_is_rejected(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        altered = replace(carrier, authentication_tag="0" * 64)
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "CARRIER_AUTHENTICATION_FAILED",
        ):
            inspect_and_correct_carrier(altered, ADMISSION_KEY)

    def test_wrong_admission_key_is_rejected(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "CARRIER_AUTHENTICATION_FAILED",
        ):
            inspect_and_correct_carrier(carrier, b"x" * 32)

    def test_carrier_mapping_round_trip(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        rebuilt = CompiledROMCarrier.from_mapping(carrier.to_dict())
        admission = inspect_and_correct_carrier(rebuilt, ADMISSION_KEY)
        self.assertEqual(
            admission.entry.entry_hash216,
            carrier.expected_entry_hash216,
        )

    def test_store_rejects_nonadmission_objects(self):
        store = RecoveryGatedCompiledROMStore(ADMISSION_KEY)
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "RECOVERY_ADMISSION_REQUIRED",
        ):
            store.admit(compiled_entry())  # type: ignore[arg-type]

    def test_admission_tamper_is_rejected(self):
        carrier = protect_compiled_rom_entry(compiled_entry(), ADMISSION_KEY)
        admission = inspect_and_correct_carrier(carrier, ADMISSION_KEY)
        altered = replace(admission, authentication_tag="f" * 64)
        store = RecoveryGatedCompiledROMStore(ADMISSION_KEY)
        with self.assertRaisesRegex(
            Pass213RecoveryAdmissionError,
            "ADMISSION_AUTHENTICATION_FAILED",
        ):
            store.admit(altered)

    def test_inspect_correct_and_admit_is_atomic_surface(self):
        entry = compiled_entry()
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        data_ref = next(
            shard.ref
            for shard in carrier.protected.shards
            if shard.role == "data"
        )
        damaged = with_missing_refs(carrier, {data_ref})
        store = RecoveryGatedCompiledROMStore(ADMISSION_KEY)
        admission = store.inspect_correct_and_admit(damaged)
        self.assertEqual(admission.recovery_outcome, "RECOVERED")
        self.assertEqual(store.lookup_hash216(entry.entry_hash216), entry)


if __name__ == "__main__":
    unittest.main()

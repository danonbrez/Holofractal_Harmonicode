from dataclasses import replace
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    ClosurePath,
    CompiledROMEntry,
    CompiledROMStore,
    Pass213ValidationError,
    TimestampBoundary,
    ZERO_HASH216,
    ZERO_HASH72,
    create_group_receipt,
    derive_key,
    hash216,
    ordered_operation_chain,
    validate_boundary_pair,
)

ROOT_KEY = bytes(range(32))
KERNEL = hash216("test-kernel", b"kernel-v1")
POLICY = hash216("test-policy", b"policy-v1")


def boundary(
    kind: str,
    timestamp_ns: int,
    serial: int,
    sequence: int = 7,
) -> TimestampBoundary:
    return TimestampBoundary.create(
        kind=kind,
        timestamp_ns=timestamp_ns,
        serial=serial,
        genesis_epoch=3,
        group_sequence=sequence,
        parent_hash216=ZERO_HASH216,
        previous_receipt_hash72=ZERO_HASH72,
        kernel_measurement_hash216=KERNEL,
    )


class Pass213Iteration1Tests(unittest.TestCase):
    def test_boundary_round_trip_and_pair(self):
        opening = boundary("open", 1000, 11)
        closing = boundary("close", 1100, 12)
        opening.validate()
        closing.validate()
        validate_boundary_pair(opening, closing)

    def test_timestamp_rollback_rejected(self):
        with self.assertRaisesRegex(Pass213ValidationError, "TIMESTAMP_ORDER"):
            validate_boundary_pair(
                boundary("open", 1000, 11),
                boundary("close", 999, 12),
            )

    def test_boundary_tampering_rejected(self):
        original = boundary("open", 1000, 11)
        altered = replace(original, timestamp_ns=1001)
        with self.assertRaisesRegex(
            Pass213ValidationError,
            "BOUNDARY_HASH_MISMATCH",
        ):
            altered.validate()

    def test_operation_order_is_noncommutative(self):
        key = derive_key(ROOT_KEY, "GROUP", b"context")
        opening = boundary("open", 1000, 11)
        ab, _ = ordered_operation_chain(
            key,
            opening,
            ({"op": "A"}, {"op": "B"}),
        )
        ba, _ = ordered_operation_chain(
            key,
            opening,
            ({"op": "B"}, {"op": "A"}),
        )
        self.assertNotEqual(ab, ba)

    def test_closure_visits_each_cell_once(self):
        key = derive_key(ROOT_KEY, "PATH", b"context")
        closure = ClosurePath.derive(key, 5184, b"group-7")
        report = closure.verify_complete()
        self.assertTrue(report["valid"])
        self.assertEqual(report["visited_count"], 5184)
        self.assertEqual(report["unique_count"], 5184)
        self.assertEqual(report["missing_count"], 0)

    def test_closure_inverse(self):
        key = derive_key(ROOT_KEY, "PATH", b"context")
        closure = ClosurePath.derive(key, 1259712, b"group-7")
        for position in (0, 1, 243, 5183, 1259711):
            self.assertEqual(
                closure.position(closure.cell(position)),
                position,
            )

    def test_context_changes_closure_path(self):
        key = derive_key(ROOT_KEY, "PATH", b"context")
        one = ClosurePath.derive(key, 5184, b"group-7")
        two = ClosurePath.derive(key, 5184, b"group-8")
        self.assertNotEqual(
            one.path_root_hash216,
            two.path_root_hash216,
        )

    def _entry(
        self,
        opening: TimestampBoundary,
        closing: TimestampBoundary,
        closure: ClosurePath,
    ) -> CompiledROMEntry:
        return CompiledROMEntry.create(
            operation_id="ADD_EXACT_BIGINT_V1",
            canonical_operation={
                "opcode": "ADD",
                "operand_types": ["bigint", "bigint"],
            },
            constraints={"overflow": "unbounded", "ordered": True},
            vm81_cell_id=4,
            operation_slot=9,
            g243_control_id=2,
            native_dispatch_id="hhs_native.add_bigint_v1",
            kernel_policy_hash216=POLICY,
            creation_group_sequence=opening.group_sequence,
            creation_open_boundary_hash216=opening.boundary_hash216,
            creation_close_boundary_hash216=closing.boundary_hash216,
            closure_path_root_hash216=closure.path_root_hash216,
            closure_position=17,
            parent_hash216=opening.parent_hash216,
        )

    def test_compiled_entry_insert_lookup_inventory(self):
        opening = boundary("open", 1000, 11)
        closing = boundary("close", 1100, 12)
        closure = ClosurePath.derive(
            derive_key(ROOT_KEY, "PATH", b"x"),
            5184,
            b"group",
        )
        entry = self._entry(opening, closing, closure)
        store = CompiledROMStore()
        entry_hash = store.insert(entry)
        self.assertEqual(store.lookup_hash216(entry_hash), entry)
        self.assertEqual(store.lookup_operation(entry.operation_id), entry)
        self.assertEqual(len(store), 1)
        self.assertEqual(len(store.inventory_root()), 64)

    def test_compiled_entry_mutation_rejected(self):
        opening = boundary("open", 1000, 11)
        closing = boundary("close", 1100, 12)
        closure = ClosurePath.derive(
            derive_key(ROOT_KEY, "PATH", b"x"),
            5184,
            b"group",
        )
        entry = self._entry(opening, closing, closure)
        altered = replace(entry, operation_slot=10)
        with self.assertRaisesRegex(
            Pass213ValidationError,
            "ENTRY_HASH_MISMATCH",
        ):
            altered.validate()

    def test_duplicate_operation_identity_with_different_record_rejected(self):
        opening = boundary("open", 1000, 11)
        closing = boundary("close", 1100, 12)
        closure = ClosurePath.derive(
            derive_key(ROOT_KEY, "PATH", b"x"),
            5184,
            b"group",
        )
        entry = self._entry(opening, closing, closure)
        second = CompiledROMEntry.create(
            **{**entry.unsigned_payload(), "g243_control_id": 3}
        )
        store = CompiledROMStore()
        store.insert(entry)
        with self.assertRaisesRegex(
            Pass213ValidationError,
            "OPERATION_ID_ALREADY_COMPILED",
        ):
            store.insert(second)

    def test_group_receipt_is_deterministic(self):
        opening = boundary("open", 1000, 11)
        closing = boundary("close", 1100, 12)
        group_key = derive_key(ROOT_KEY, "GROUP", b"context")
        receipt_key = derive_key(ROOT_KEY, "RECEIPT", b"context")
        group_hash, _ = ordered_operation_chain(
            group_key,
            opening,
            ({"op": "A"}, {"op": "B"}),
        )
        closure = ClosurePath.derive(
            derive_key(ROOT_KEY, "PATH", b"x"),
            5184,
            b"group",
        )
        inventory = hash216("inventory", b"empty")
        one = create_group_receipt(
            receipt_key,
            opening=opening,
            closing=closing,
            ordered_group_hash216=group_hash,
            inventory_root_hash216=inventory,
            closure_path_root_hash216=closure.path_root_hash216,
        )
        two = create_group_receipt(
            receipt_key,
            opening=opening,
            closing=closing,
            ordered_group_hash216=group_hash,
            inventory_root_hash216=inventory,
            closure_path_root_hash216=closure.path_root_hash216,
        )
        self.assertEqual(one, two)


if __name__ == "__main__":
    unittest.main()

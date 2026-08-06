from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    CompiledROMEntry,
    FULL_HYDRATION_DOMAIN,
    ZERO_HASH216,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_governed_native_dispatch_v1 import (
    DISPATCH_PROFILE,
    DispatchRuntimeState,
    GovernedNativeDispatchAuthority,
    GovernedNativeDispatchService,
    NativeDispatchCapabilityAuthority,
    NativeDispatchKernel,
    NativeDispatchLedger,
    NativeDispatchRequest,
    Pass213NativeDispatchAuthorizationError,
    Pass213NativeDispatchIntegrityError,
    Pass213NativeDispatchValidationError,
    SCOPE_DISPATCH_EXECUTE,
    SCOPE_DISPATCH_READ,
)
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import MovingTensorState
from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from tests.test_pass213_moving_tensor_v1 import TENSOR_KEY, synthetic_anchor

ROOT = Path(__file__).resolve().parents[1]
SECURE_SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
DISPATCH_SOURCE = ROOT / "native/pass213/hhs_pass213_native_dispatch.c"
ADMISSION_KEY = bytes((index * 11 + 3) % 256 for index in range(32))
MEMORY_KEY = bytes((index * 13 + 5) % 256 for index in range(32))
LEDGER_KEY = bytes((index * 17 + 7) % 256 for index in range(32))
CAPABILITY_KEY = bytes((index * 19 + 9) % 256 for index in range(32))


def h(label: str) -> str:
    return hash216("pass213-iteration10-test", label.encode("utf-8"))


def baseline_receipt(state_root: str) -> str:
    return hash72_digest(
        {"domain": "HHS-P213-ITER10-TEST-BASELINE"},
        bytes.fromhex(state_root),
    )


def compiled_native_entry(
    operation_id: str,
    native_dispatch_id: str = "hhs.native.u64.add.v1",
    *,
    input_count: int = 2,
    read_set: tuple[str, ...] = ("register.a", "register.b"),
    write_set: tuple[str, ...] = ("register.result",),
    modulus: int = 0,
    policy_root: str | None = None,
    vm81_cell_id: int = 17,
    operation_slot: int = 23,
    g243_control_id: int = 144,
) -> CompiledROMEntry:
    return CompiledROMEntry.create(
        operation_id=operation_id,
        canonical_operation={
            "dispatch_profile": DISPATCH_PROFILE,
            "native_dispatch_id": native_dispatch_id,
            "semantic_operation": operation_id,
        },
        constraints={
            "dispatch_profile": DISPATCH_PROFILE,
            "input_count": input_count,
            "result_count": 1,
            "read_set": read_set,
            "write_set": write_set,
            "max_operand": (1 << 64) - 1,
            "modulus": modulus,
        },
        vm81_cell_id=vm81_cell_id,
        operation_slot=operation_slot,
        g243_control_id=g243_control_id,
        native_dispatch_id=native_dispatch_id,
        kernel_policy_hash216=policy_root or h("policy"),
        creation_group_sequence=1,
        creation_open_boundary_hash216=h("creation-open"),
        creation_close_boundary_hash216=h("creation-close"),
        closure_path_root_hash216=h("creation-closure"),
        closure_position=77,
        parent_hash216=h("compiled-parent"),
    )


class Pass213Iteration10GovernedNativeDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._native_temp = tempfile.TemporaryDirectory(prefix="pass213-iter10-native-")
        cls.secure_library = Path(cls._native_temp.name) / "libhhs_pass213_secure_arena.so"
        cls.dispatch_library = Path(cls._native_temp.name) / "libhhs_pass213_native_dispatch.so"
        for source, output in (
            (SECURE_SOURCE, cls.secure_library),
            (DISPATCH_SOURCE, cls.dispatch_library),
        ):
            subprocess.run(
                [
                    "cc", "-std=c11", "-shared", "-fPIC", "-O2",
                    "-Wall", "-Wextra", "-Werror", str(source),
                    "-o", str(output),
                ],
                check=True,
                cwd=ROOT,
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._native_temp.cleanup()

    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory(prefix="pass213-iter10-")
        self.root = Path(self._temp.name)
        self.store = NativeProtectedCompiledROMStore(
            library_path=self.secure_library,
            admission_key=ADMISSION_KEY,
            memory_root_key=MEMORY_KEY,
            owner_id="PASS213_ITER10_TEST",
        )
        self.kernel = NativeDispatchKernel(library_path=self.dispatch_library)
        self.policy_root = h("policy")
        self.entry = self.admit(compiled_native_entry("ITER10_ADD"))
        self.anchor = synthetic_anchor(1, 10_000_001)
        self.tensor = MovingTensorState.derive(
            root_key=TENSOR_KEY,
            trusted_anchor=self.anchor,
            tensor_sequence=1,
            genesis_epoch=10,
            domain_size=FULL_HYDRATION_DOMAIN,
        )
        self.initial_state_root = h("initial-runtime-state")
        self.initial_receipt = baseline_receipt(self.initial_state_root)
        self.initial_state = DispatchRuntimeState(
            next_sequence=1,
            current_state_root_hash216=self.initial_state_root,
            previous_receipt_hash72=self.initial_receipt,
            kernel_policy_hash216=self.policy_root,
            kernel_measurement_hash216=h("kernel-measurement"),
            lineage_root_hash216=self.tensor.anchor.hash216_lineage_root,
            tensor_state=self.tensor,
            last_timestamp_ns=self.tensor.anchor.requested_timestamp_ns,
        )
        self._ledgers: list[NativeDispatchLedger] = []

    def tearDown(self) -> None:
        for ledger in self._ledgers:
            try:
                ledger.close()
            except sqlite3.ProgrammingError:
                pass
        self.store.close()
        self._temp.cleanup()

    def admit(self, entry: CompiledROMEntry) -> CompiledROMEntry:
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        self.store.inspect_correct_protect_and_admit(carrier)
        return entry

    def ledger(self, name: str) -> NativeDispatchLedger:
        ledger = NativeDispatchLedger(
            database_path=self.root / name,
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=self.initial_state_root,
            anchor_receipt_hash72=self.initial_receipt,
        )
        self._ledgers.append(ledger)
        return ledger

    def authority(
        self,
        name: str,
        *,
        state: DispatchRuntimeState | None = None,
    ) -> GovernedNativeDispatchAuthority:
        return GovernedNativeDispatchAuthority(
            protected_store=self.store,
            native_kernel=self.kernel,
            ledger=self.ledger(name),
            runtime_state=state or self.initial_state,
        )

    def request(
        self,
        *,
        parent: str | None = None,
        tensor_root: str | None = None,
        timestamp_ns: int | None = None,
        operands: tuple[int, ...] = (7, 9),
        read_set: tuple[str, ...] = ("register.a", "register.b"),
        write_set: tuple[str, ...] = ("register.result",),
        hydration_lane: int = 3,
        entry: CompiledROMEntry | None = None,
    ) -> NativeDispatchRequest:
        target = entry or self.entry
        return NativeDispatchRequest(
            entry_hash216=target.entry_hash216,
            operation_id=target.operation_id,
            expected_parent_hash216=parent or self.initial_state_root,
            expected_tensor_root_hash216=tensor_root or self.tensor.tensor_root_hash216,
            timestamp_ns=timestamp_ns or self.tensor.anchor.requested_timestamp_ns + 1,
            hydration_lane=hydration_lane,
            operands=operands,
            read_set=read_set,
            write_set=write_set,
        )

    def test_native_add_executes_and_advances_singleton_vm81_state(self) -> None:
        authority = self.authority("add.sqlite3")
        result = authority.execute(self.request())
        self.assertEqual(result.result_values, (16,))
        self.assertEqual(result.sequence, 1)
        self.assertEqual(len(result.receipt_hash72), 72)
        self.assertEqual(authority.runtime_state.next_sequence, 2)
        self.assertEqual(
            authority.runtime_state.current_state_root_hash216,
            result.successor_state_root_hash216,
        )
        self.assertEqual(authority.ledger.count(), 1)
        mapping = result.to_mapping()
        self.assertTrue(mapping["singleton_vm81_admission"])
        self.assertFalse(mapping["physical_route_exposed"])
        self.assertNotIn("physical_route", mapping)
        looked_up = self.store.lookup_hash216(self.entry.entry_hash216)
        looked_up.validate()
        self.assertEqual(looked_up.entry_hash216, self.entry.entry_hash216)
        self.assertEqual(
            canonical_bytes(looked_up.to_mapping()),
            canonical_bytes(self.entry.to_mapping()),
        )

    def test_same_baseline_and_request_replay_bit_exactly(self) -> None:
        first = self.authority("deterministic-a.sqlite3").execute(self.request())
        second = self.authority("deterministic-b.sqlite3").execute(self.request())
        self.assertEqual(first.request_root_hash216, second.request_root_hash216)
        self.assertEqual(first.result_root_hash216, second.result_root_hash216)
        self.assertEqual(
            first.successor_state_root_hash216,
            second.successor_state_root_hash216,
        )
        self.assertEqual(first.receipt_hash72, second.receipt_hash72)
        self.assertEqual(first.route_commitment_hash216, second.route_commitment_hash216)

    def test_stale_parent_and_duplicate_replay_fail_without_mutation(self) -> None:
        authority = self.authority("stale.sqlite3")
        request = self.request()
        authority.execute(request)
        with self.assertRaisesRegex(
            Pass213NativeDispatchValidationError, "STALE_PARENT"
        ):
            authority.execute(request)
        self.assertEqual(authority.ledger.count(), 1)
        self.assertEqual(authority.runtime_state.next_sequence, 2)

    def test_policy_tensor_timestamp_and_access_sets_fail_closed(self) -> None:
        wrong_policy = replace(
            self.initial_state,
            kernel_policy_hash216=h("wrong-policy"),
        )
        with self.assertRaisesRegex(
            Pass213NativeDispatchValidationError, "KERNEL_POLICY"
        ):
            self.authority("wrong-policy.sqlite3", state=wrong_policy).execute(
                self.request()
            )
        authority = self.authority("context.sqlite3")
        for request, pattern in (
            (self.request(tensor_root=h("wrong-tensor")), "TENSOR_ROOT"),
            (
                self.request(timestamp_ns=self.tensor.anchor.requested_timestamp_ns),
                "TIMESTAMP_NOT_MONOTONIC",
            ),
            (
                self.request(read_set=("register.a",)),
                "ACCESS_SET_MISMATCH",
            ),
        ):
            with self.assertRaisesRegex(Pass213NativeDispatchValidationError, pattern):
                authority.execute(request)
        self.assertEqual(authority.ledger.count(), 0)

    def test_non_integer_or_out_of_range_operands_are_rejected(self) -> None:
        for value in (1.5, True, -1, 1 << 64):
            payload = self.request().to_mapping()
            payload["operands"] = (value, 2)
            with self.assertRaises(Pass213NativeDispatchValidationError):
                NativeDispatchRequest.from_mapping(payload)

    def test_native_mul_mod_rotl_and_select_workloads(self) -> None:
        cases = (
            (
                compiled_native_entry(
                    "ITER10_MUL_MOD",
                    "hhs.native.u64.mul_mod.v1",
                    modulus=97,
                    vm81_cell_id=18,
                ),
                (91, 83),
                ((91 * 83) % 97,),
            ),
            (
                compiled_native_entry(
                    "ITER10_ROTL",
                    "hhs.native.u64.rotl.v1",
                    vm81_cell_id=19,
                ),
                (1, 8),
                (256,),
            ),
            (
                compiled_native_entry(
                    "ITER10_SELECT",
                    "hhs.native.u64.select.v1",
                    input_count=3,
                    read_set=("register.a", "register.b", "register.condition"),
                    vm81_cell_id=20,
                ),
                (1, 44, 55),
                (44,),
            ),
        )
        for index, (entry, operands, expected) in enumerate(cases, start=1):
            admitted = self.admit(entry)
            authority = self.authority(f"native-case-{index}.sqlite3")
            reads = tuple(entry.constraints["read_set"])
            result = authority.execute(
                self.request(entry=admitted, operands=operands, read_set=reads)
            )
            self.assertEqual(result.result_values, expected)

    def test_tensor_change_changes_route_and_successor_commitments(self) -> None:
        first = self.authority("tensor-a.sqlite3").execute(self.request())
        anchor2 = synthetic_anchor(2, 10_000_002)
        tensor2 = MovingTensorState.derive(
            root_key=TENSOR_KEY,
            trusted_anchor=anchor2,
            tensor_sequence=2,
            genesis_epoch=10,
            prior_tensor_root_hash216=self.tensor.tensor_root_hash216,
            domain_size=FULL_HYDRATION_DOMAIN,
        )
        state2 = replace(
            self.initial_state,
            tensor_state=tensor2,
            lineage_root_hash216=tensor2.anchor.hash216_lineage_root,
            last_timestamp_ns=tensor2.anchor.requested_timestamp_ns,
        )
        second = self.authority("tensor-b.sqlite3", state=state2).execute(
            self.request(
                tensor_root=tensor2.tensor_root_hash216,
                timestamp_ns=tensor2.anchor.requested_timestamp_ns + 1,
            )
        )
        self.assertNotEqual(
            first.route_commitment_hash216,
            second.route_commitment_hash216,
        )
        self.assertNotEqual(
            first.successor_state_root_hash216,
            second.successor_state_root_hash216,
        )

    def test_ledger_reopens_and_continues_from_exact_runtime_state(self) -> None:
        path = "reopen.sqlite3"
        first_authority = self.authority(path)
        first = first_authority.execute(self.request())
        first_authority.ledger.close()
        second_state = first_authority.runtime_state
        second_ledger = NativeDispatchLedger(
            database_path=self.root / path,
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=self.initial_state_root,
            anchor_receipt_hash72=self.initial_receipt,
        )
        self._ledgers.append(second_ledger)
        second_authority = GovernedNativeDispatchAuthority(
            protected_store=self.store,
            native_kernel=self.kernel,
            ledger=second_ledger,
            runtime_state=second_state,
        )
        second = second_authority.execute(
            self.request(
                parent=first.successor_state_root_hash216,
                timestamp_ns=first.timestamp_ns + 1,
                operands=(10, 20),
            )
        )
        self.assertEqual(second.sequence, 2)
        self.assertEqual(second.result_values, (30,))
        self.assertEqual(second.prior_receipt_hash72, first.receipt_hash72)
        self.assertTrue(second_ledger.verify_chain())

    def test_ledger_tamper_and_anchor_substitution_are_detected(self) -> None:
        path = self.root / "tamper.sqlite3"
        authority = self.authority(path.name)
        authority.execute(self.request())
        authority.ledger.close()
        connection = sqlite3.connect(path)
        with connection:
            connection.execute(
                "UPDATE native_dispatch_receipts SET event_json=? WHERE sequence=1",
                ("{}",),
            )
        connection.close()
        with self.assertRaisesRegex(
            Pass213NativeDispatchIntegrityError, "AUTHENTICATION"
        ):
            NativeDispatchLedger(
                database_path=path,
                root_key=LEDGER_KEY,
                anchor_state_root_hash216=self.initial_state_root,
                anchor_receipt_hash72=self.initial_receipt,
            )
        anchor_path = self.root / "anchor.sqlite3"
        anchor_ledger = NativeDispatchLedger(
            database_path=anchor_path,
            root_key=LEDGER_KEY,
            anchor_state_root_hash216=self.initial_state_root,
            anchor_receipt_hash72=self.initial_receipt,
        )
        anchor_ledger.close()
        with self.assertRaisesRegex(
            Pass213NativeDispatchIntegrityError, "ANCHOR_MISMATCH"
        ):
            NativeDispatchLedger(
                database_path=anchor_path,
                root_key=LEDGER_KEY,
                anchor_state_root_hash216=h("different-anchor"),
                anchor_receipt_hash72=self.initial_receipt,
            )

    def test_capability_scope_authentication_and_expiry(self) -> None:
        capabilities = NativeDispatchCapabilityAuthority(
            root_key=CAPABILITY_KEY,
            epoch=10,
        )
        issued = 20_000_000_000
        execute = capabilities.issue(
            subject="native-test",
            scopes=(SCOPE_DISPATCH_EXECUTE,),
            ttl_seconds=60,
            issued_timestamp_ns=issued,
            nonce="fixed-nonce",
        )
        claims = capabilities.validate(
            execute,
            required_scope=SCOPE_DISPATCH_EXECUTE,
            now_timestamp_ns=issued + 1,
        )
        self.assertEqual(claims.subject, "native-test")
        with self.assertRaisesRegex(
            Pass213NativeDispatchAuthorizationError, "SCOPE_DENIED"
        ):
            capabilities.validate(
                execute,
                required_scope=SCOPE_DISPATCH_READ,
                now_timestamp_ns=issued + 1,
            )
        with self.assertRaisesRegex(
            Pass213NativeDispatchAuthorizationError, "EXPIRED"
        ):
            capabilities.validate(
                execute,
                required_scope=SCOPE_DISPATCH_EXECUTE,
                now_timestamp_ns=issued + 60_000_000_000,
            )
        altered = execute[:-1] + ("0" if execute[-1] != "0" else "1")
        with self.assertRaisesRegex(
            Pass213NativeDispatchAuthorizationError, "AUTHENTICATION"
        ):
            capabilities.validate(
                altered,
                required_scope=SCOPE_DISPATCH_EXECUTE,
                now_timestamp_ns=issued + 1,
            )

    def test_shared_service_requires_exact_scope_and_reads_receipt(self) -> None:
        authority = self.authority("service.sqlite3")
        capabilities = NativeDispatchCapabilityAuthority(
            root_key=CAPABILITY_KEY,
            epoch=10,
        )
        service = GovernedNativeDispatchService(
            authority=authority,
            capabilities=capabilities,
        )
        execute_token = capabilities.issue(
            subject="operator",
            scopes=(SCOPE_DISPATCH_EXECUTE,),
        )
        read_token = capabilities.issue(
            subject="auditor",
            scopes=(SCOPE_DISPATCH_READ,),
        )
        response = service.invoke(
            "native-dispatch.execute",
            self.request().to_mapping(),
            capability=execute_token,
        )
        self.assertTrue(response["canonical_runtime_mutated"])
        receipt = service.invoke(
            "native-dispatch.receipt",
            {"sequence": 1},
            capability=read_token,
        )
        self.assertEqual(
            receipt["result"]["successor_state_root_hash216"],
            response["result"]["successor_state_root_hash216"],
        )
        with self.assertRaisesRegex(
            Pass213NativeDispatchAuthorizationError, "SCOPE_DENIED"
        ):
            service.invoke(
                "native-dispatch.execute",
                self.request(parent=authority.runtime_state.current_state_root_hash216).to_mapping(),
                capability=read_token,
            )

    def test_singleton_reentry_is_rejected_before_native_execution(self) -> None:
        authority = self.authority("reentry.sqlite3")
        authority._active = True
        with self.assertRaisesRegex(
            Pass213NativeDispatchIntegrityError, "SINGLETON_VM81_REENTRY"
        ):
            authority.execute(self.request())
        self.assertEqual(authority.ledger.count(), 0)


if __name__ == "__main__":
    unittest.main()

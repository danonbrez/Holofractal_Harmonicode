from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import subprocess
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_native_protected_rom_v1 import (
    NativeProtectedCompiledROMStore,
)
from hhs_backend.runtime.hhs_pass213_parametric_delta_v1 import (
    NativeParametricCompiledROMStore,
    ParametricConstraint,
    ParametricFieldSpec,
    ParametricROMTemplate,
    Pass213ParametricValidationError,
    create_parametric_admission,
)
from hhs_backend.runtime.hhs_pass213_recovery_admission_v1 import (
    protect_compiled_rom_entry,
)
from hhs_backend.runtime.hhs_pass213_secure_memory_v1 import (
    Pass213SecureMemoryError,
)
from tests.test_pass213_recovery_admission_v1 import (
    ADMISSION_KEY,
    POLICY,
    ROOT_KEY,
    boundary,
    compiled_entry,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native/pass213/hhs_pass213_secure_arena.c"
PARAMETRIC_KEY = bytes((index * 7 + 3) % 256 for index in range(32))
MEMORY_KEY = bytes((index * 11 + 5) % 256 for index in range(32))


def invocation(
    *,
    left: int = 1,
    right: int = 2,
    policy: str = POLICY,
    mode: str = "exact",
) -> dict[str, object]:
    return {
        "operands": {"left": left, "right": right},
        "context": {"kernel_policy_hash216": policy, "mode": mode},
    }


def template_for(entry) -> ParametricROMTemplate:
    return ParametricROMTemplate.create(
        template_id=f"PARAMETRIC_{entry.operation_id}",
        base_entry_hash216=entry.entry_hash216,
        operation_id=entry.operation_id,
        field_specs=(
            ParametricFieldSpec("operands.left", "bigint", True),
            ParametricFieldSpec("operands.right", "bigint", True),
            ParametricFieldSpec(
                "context.kernel_policy_hash216",
                "string",
                False,
            ),
            ParametricFieldSpec("context.mode", "string", False),
        ),
        baseline_candidate=invocation(),
        constraints=(
            ParametricConstraint(
                "left_max_bits",
                "MAX_BITS",
                ("operands.left",),
                {"max_bits": 64},
            ),
            ParametricConstraint(
                "right_max_bits",
                "MAX_BITS",
                ("operands.right",),
                {"max_bits": 64},
            ),
            ParametricConstraint(
                "result_max_bits",
                "SUM_MAX_BITS",
                ("operands.left", "operands.right"),
                {"max_bits": 65},
            ),
            ParametricConstraint(
                "exact_mode",
                "ENUM",
                ("context.mode",),
                {"allowed": ["exact"]},
            ),
            ParametricConstraint(
                "kernel_policy",
                "ENUM",
                ("context.kernel_policy_hash216",),
                {"allowed": [POLICY]},
            ),
        ),
    )


class Pass213Iteration4ParametricDeltaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.entry = compiled_entry("PARAMETRIC_BIGINT_ADD_V1")
        self.template = template_for(self.entry)
        self.opening = boundary("open", 3_000, 31)

    def admit(self, candidate):
        return create_parametric_admission(
            template=self.template,
            base_entry=self.entry,
            candidate=candidate,
            opening_boundary=self.opening,
            validation_key=PARAMETRIC_KEY,
        )

    def test_template_baseline_witnesses_are_complete(self) -> None:
        self.template.validate()
        self.assertEqual(
            set(self.template.baseline_constraint_witnesses),
            {
                "left_max_bits",
                "right_max_bits",
                "result_max_bits",
                "exact_mode",
                "kernel_policy",
            },
        )

    def test_exact_baseline_reuses_every_constraint(self) -> None:
        admission = self.admit(invocation())
        self.assertEqual(admission.changed_paths, ())
        self.assertEqual(admission.affected_constraint_ids, ())
        self.assertEqual(len(admission.reused_constraint_ids), 5)
        admission.validate(
            PARAMETRIC_KEY,
            self.template,
            self.entry,
            self.opening,
        )

    def test_single_operand_change_revalidates_only_dependencies(self) -> None:
        admission = self.admit(invocation(left=13))
        self.assertEqual(admission.changed_paths, ("operands.left",))
        self.assertEqual(
            admission.affected_constraint_ids,
            ("left_max_bits", "result_max_bits"),
        )
        self.assertEqual(
            set(admission.reused_constraint_ids),
            {"right_max_bits", "exact_mode", "kernel_policy"},
        )

    def test_two_operand_changes_revalidate_dependency_union(self) -> None:
        admission = self.admit(invocation(left=13, right=21))
        self.assertEqual(
            admission.changed_paths,
            ("operands.left", "operands.right"),
        )
        self.assertEqual(
            admission.affected_constraint_ids,
            ("left_max_bits", "result_max_bits", "right_max_bits"),
        )
        self.assertEqual(
            admission.reused_constraint_ids,
            ("exact_mode", "kernel_policy"),
        )

    def test_immutable_context_change_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            Pass213ParametricValidationError,
            "IMMUTABLE_FIELD_CHANGED:context.mode",
        ):
            self.admit(invocation(mode="approximate"))

    def test_all_fields_still_receive_type_validation(self) -> None:
        malformed = invocation()
        malformed["operands"]["left"] = True  # type: ignore[index]
        with self.assertRaisesRegex(
            Pass213ParametricValidationError,
            "FIELD_TYPE_INVALID:operands.left:bigint",
        ):
            self.admit(malformed)

    def test_affected_constraint_failure_rejects_candidate(self) -> None:
        with self.assertRaisesRegex(
            Pass213ParametricValidationError,
            "CONSTRAINT_FAILED:left_max_bits",
        ):
            self.admit(invocation(left=1 << 80))

    def test_boundary_changes_admission_authority(self) -> None:
        first = self.admit(invocation(left=8))
        second_opening = boundary("open", 3_001, 32)
        second = create_parametric_admission(
            template=self.template,
            base_entry=self.entry,
            candidate=invocation(left=8),
            opening_boundary=second_opening,
            validation_key=PARAMETRIC_KEY,
        )
        self.assertNotEqual(
            first.vm81_admission_root_hash216,
            second.vm81_admission_root_hash216,
        )
        self.assertNotEqual(first.authentication_tag, second.authentication_tag)

    def test_wrong_key_or_tampered_admission_is_rejected(self) -> None:
        admission = self.admit(invocation(left=8))
        with self.assertRaisesRegex(
            Pass213ParametricValidationError,
            "ADMISSION_MISMATCH",
        ):
            admission.validate(
                b"z" * 32,
                self.template,
                self.entry,
                self.opening,
            )
        altered = replace(admission, delta_root_hash216="0" * 64)
        with self.assertRaisesRegex(
            Pass213ParametricValidationError,
            "ADMISSION_MISMATCH",
        ):
            altered.validate(
                PARAMETRIC_KEY,
                self.template,
                self.entry,
                self.opening,
            )

    def test_baseline_witness_tampering_is_rejected(self) -> None:
        witnesses = dict(self.template.baseline_constraint_witnesses)
        witnesses["left_max_bits"] = "0" * 64
        altered = replace(
            self.template,
            baseline_constraint_witnesses=witnesses,
        )
        with self.assertRaisesRegex(
            Pass213ParametricValidationError,
            "BASELINE_WITNESS_MISMATCH",
        ):
            altered.validate()


class Pass213Iteration4NativeParametricStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory(prefix="pass213-parametric-")
        cls.library = Path(cls._temp.name) / "libhhs_pass213_secure_arena.so"
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
        cls._temp.cleanup()

    def make_stores(self, operation_id: str):
        entry = compiled_entry(operation_id)
        base = NativeProtectedCompiledROMStore(
            library_path=self.library,
            admission_key=ADMISSION_KEY,
            memory_root_key=ROOT_KEY,
            owner_id=f"BASE_{operation_id}",
        )
        carrier = protect_compiled_rom_entry(entry, ADMISSION_KEY)
        base.inspect_correct_protect_and_admit(carrier)
        parametric = NativeParametricCompiledROMStore(
            base_store=base,
            library_path=self.library,
            validation_key=PARAMETRIC_KEY,
            memory_root_key=MEMORY_KEY,
            owner_id=f"PARAMETRIC_{operation_id}",
        )
        return entry, base, parametric

    def test_template_and_admission_reside_in_sealed_native_arenas(self) -> None:
        entry, base, store = self.make_stores("PARAMETRIC_NATIVE_V1")
        opening = boundary("open", 4_000, 41)
        try:
            template = template_for(entry)
            template_record = store.register_template(template)
            record = store.admit_candidate(
                template_id=template.template_id,
                candidate=invocation(left=34, right=55),
                opening_boundary=opening,
            )
            admission = store.lookup_admission(
                record.vm81_admission_root_hash216,
                opening,
            )
            self.assertEqual(template_record.template_hash216, template.template_hash216)
            self.assertEqual(admission.changed_paths, ("operands.left", "operands.right"))
            self.assertEqual(record.changed_path_count, 2)
            self.assertEqual(record.affected_constraint_count, 3)
            self.assertFalse(hasattr(record, "candidate"))
            self.assertEqual(len(store), 1)
            self.assertEqual(len(store.inventory_root()), 64)
        finally:
            parametric_receipts = store.close()
            base.close()
        self.assertEqual(len(parametric_receipts), 2)
        self.assertTrue(
            all(receipt.details["zeroized_before_release"] for receipt in parametric_receipts)
        )

    def test_identical_candidate_and_boundary_is_idempotent(self) -> None:
        entry, base, store = self.make_stores("PARAMETRIC_NATIVE_IDEMPOTENT_V1")
        opening = boundary("open", 4_000, 41)
        try:
            template = template_for(entry)
            store.register_template(template)
            first = store.admit_candidate(
                template_id=template.template_id,
                candidate=invocation(left=5),
                opening_boundary=opening,
            )
            second = store.admit_candidate(
                template_id=template.template_id,
                candidate=invocation(left=5),
                opening_boundary=opening,
            )
            self.assertEqual(first, second)
            self.assertEqual(len(store), 1)
        finally:
            store.close()
            base.close()

    def test_lookup_requires_the_original_boundary(self) -> None:
        entry, base, store = self.make_stores("PARAMETRIC_NATIVE_BOUNDARY_V1")
        opening = boundary("open", 4_000, 41)
        try:
            template = template_for(entry)
            store.register_template(template)
            record = store.admit_candidate(
                template_id=template.template_id,
                candidate=invocation(left=5),
                opening_boundary=opening,
            )
            with self.assertRaisesRegex(
                Pass213ParametricValidationError,
                "ADMISSION_MISMATCH",
            ):
                store.lookup_admission(
                    record.vm81_admission_root_hash216,
                    boundary("open", 4_001, 42),
                )
        finally:
            store.close()
            base.close()

    def test_template_requires_an_existing_protected_base_entry(self) -> None:
        base = NativeProtectedCompiledROMStore(
            library_path=self.library,
            admission_key=ADMISSION_KEY,
            memory_root_key=ROOT_KEY,
            owner_id="EMPTY_BASE",
        )
        store = NativeParametricCompiledROMStore(
            base_store=base,
            library_path=self.library,
            validation_key=PARAMETRIC_KEY,
            memory_root_key=MEMORY_KEY,
            owner_id="EMPTY_PARAMETRIC",
        )
        try:
            with self.assertRaisesRegex(
                Pass213SecureMemoryError,
                "PROTECTED_ROM_ENTRY_NOT_FOUND",
            ):
                store.register_template(template_for(compiled_entry("ABSENT_BASE_V1")))
        finally:
            store.close()
            base.close()


if __name__ == "__main__":
    unittest.main()

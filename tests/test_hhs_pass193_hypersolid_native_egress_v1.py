from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from hhs_backend.runtime.hhs_pass193_hypersolid_native_egress_v1 import (
    Pass193Error,
    Pass193Runtime,
    REGULAR_3D,
    REGULAR_4D,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest


LICENSE = {
    "closed": True,
    "license_id": "TEST-ONLY-LICENSE",
    "distribution_claim": "TEST_FIXTURE_ONLY",
}
EVIDENCE = {
    "compiled": True,
    "linked": True,
    "launched": True,
    "abi_validated": True,
    "deterministic_workload": True,
}


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P193_TEST_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P193_TEST_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass193RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = Pass193Runtime(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_regular_family_registry_and_exact_tesseract(self) -> None:
        self.assertEqual(len(REGULAR_3D), 5)
        self.assertEqual(len(REGULAR_4D), 6)
        solid = self.runtime.create_hypersolid(
            "8-cell", 4, authority_execution=authority(1)
        )
        self.assertEqual(len(solid["vertex_set"]), 16)
        self.assertEqual(len(solid["edge_set"]), 32)
        self.assertEqual(len(solid["phase_planes"]), 6)
        self.assertEqual(solid["exact_coordinate_model"], "EXACT_INTEGER_CARTESIAN")
        self.assertEqual(len(solid["hash216_identity"]), 216)
        self.assertTrue(self.runtime.validate_object(solid["object_id"])["ok"])

    def test_ordered_exact_rotations_preserve_noncommutative_history(self) -> None:
        root = self.runtime.create_hypersolid(
            "8-cell", 4, authority_execution=authority(1)
        )
        left_1 = self.runtime.rotate(
            root["object_id"], (0, 1), 1, 4, authority_execution=authority(2)
        )
        left_2 = self.runtime.rotate(
            left_1["object_id"], (1, 2), 1, 4, authority_execution=authority(3)
        )
        right_1 = self.runtime.rotate(
            root["object_id"], (1, 2), 1, 4, authority_execution=authority(4)
        )
        right_2 = self.runtime.rotate(
            right_1["object_id"], (0, 1), 1, 4, authority_execution=authority(5)
        )
        self.assertEqual(left_2["transform_history"][0]["plane"], [0, 1])
        self.assertEqual(left_2["transform_history"][1]["plane"], [1, 2])
        self.assertEqual(right_2["transform_history"][0]["plane"], [1, 2])
        self.assertEqual(right_2["transform_history"][1]["plane"], [0, 1])
        self.assertNotEqual(left_2["hash216_identity"], right_2["hash216_identity"])

    def test_pass192_nesting_witness_is_exact_and_address_sensitive(self) -> None:
        parent = self.runtime.create_hypersolid(
            "cube", 3, authority_execution=authority(1)
        )
        child = self.runtime.nest(
            parent["object_id"],
            child_slot=7,
            lo_shu_cell=(0, 0),
            magnitude_row=5,
            depth=8,
            authority_execution=authority(2),
        )
        nesting = child["pass192_nesting_record"]
        self.assertEqual((nesting["ratio_num"], nesting["ratio_den"]), (55, 89))
        self.assertEqual(
            (nesting["cumulative_num"], nesting["cumulative_den"]), (1, 55)
        )
        self.assertEqual((nesting["membrane_modulus"], nesting["membrane_residue"]), (9, 8))
        self.assertEqual(child["fractal_address"]["child_slot"], 7)
        self.assertEqual(child["fractal_address"]["lo_shu_cell"], [0, 0])
        self.assertEqual(child["parent_id"], parent["object_id"])

    def test_fold_produces_projection_without_replacing_canonical_source(self) -> None:
        source = self.runtime.create_hypersolid(
            "8-cell", 4, authority_execution=authority(1)
        )
        folded = self.runtime.fold(
            source["object_id"],
            "cell-hinge-0",
            (0, 3),
            1,
            8,
            target_dimension=3,
            reversible=True,
            authority_execution=authority(2),
        )
        self.assertNotEqual(folded["object_id"], source["object_id"])
        self.assertEqual(folded["render_projection"]["classification"], "NONCANONICAL_PROJECTION")
        self.assertEqual(folded["render_projection"]["source_object_id"], source["object_id"])
        self.assertEqual(self.runtime.get_object(source["object_id"])["fold_graph"], [])

    def test_projection_is_noncanonical_and_authority_free(self) -> None:
        source = self.runtime.create_hypersolid(
            "8-cell", 4, authority_execution=authority(1)
        )
        projected = self.runtime.project(source["object_id"], 3)
        self.assertEqual(projected["classification"], "NONCANONICAL_PROJECTION")
        self.assertFalse(projected["canonical_geometry_mutated"])
        self.assertEqual(projected["source_hash216_identity"], source["hash216_identity"])
        self.assertEqual(len(self.runtime.receipts_for(source["object_id"])), 1)

    def test_float_canonical_metadata_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            Pass193Error, "HHS_P193_FLOAT_CANONICAL_AUTHORITY_FORBIDDEN"
        ):
            self.runtime.create_hypersolid(
                "cube",
                3,
                constraint_registry={"approximate_tolerance": 0.001},
                authority_execution=authority(1),
            )

    def test_vm81_authority_is_required_for_mutation(self) -> None:
        with self.assertRaisesRegex(Pass193Error, "HHS_P193_VM81_AUTHORITY_REQUIRED"):
            self.runtime.create_hypersolid("cube", 3, authority_execution={})

    def test_native_evidence_package_and_nft_authorization_separation(self) -> None:
        solid = self.runtime.create_hypersolid(
            "cube", 3, authority_execution=authority(1)
        )
        with self.assertRaisesRegex(
            Pass193Error, "HHS_P193_NATIVE_TARGET_VALIDATION_INCOMPLETE"
        ):
            self.runtime.record_native_artifact(
                solid["object_id"],
                target="linux-x86_64-elf",
                binary_bytes=b"ELF-P193-TEST",
                compiler_identity="test-cc",
                compiler_flags=["-O2"],
                linker_identity="test-ld",
                build_environment={"profile": "test"},
                evidence={**EVIDENCE, "launched": False},
                license_manifest=LICENSE,
                authority_execution=authority(2),
            )

        artifact = self.runtime.record_native_artifact(
            solid["object_id"],
            target="linux-x86_64-elf",
            binary_bytes=b"ELF-P193-TEST",
            compiler_identity="test-cc",
            compiler_flags=["-O2"],
            linker_identity="test-ld",
            build_environment={"profile": "test"},
            evidence=EVIDENCE,
            license_manifest=LICENSE,
            authority_execution=authority(3),
        )
        package = self.runtime.build_portable_bundle(
            solid["object_id"],
            [artifact["artifact_id"]],
            capabilities=["filesystem:read:app"],
            license_manifest=LICENSE,
            authority_execution=authority(4),
        )
        nft = self.runtime.create_nft_executable(
            package["package_id"],
            rights={"license_manifest_identity": "TEST-ONLY-LICENSE"},
            authority_execution=authority(5),
        )
        self.assertFalse(nft["execution_authorized"])
        self.assertFalse(nft["identity_is_execution_authority"])

        with self.assertRaisesRegex(
            Pass193Error, "HHS_P193_EXECUTION_ADMISSION_DENIED"
        ):
            self.runtime.authorize_execution(
                nft["nft_executable_id"],
                identity_verified=True,
                capability_admitted=False,
                platform_validated=True,
                policy_accepted=True,
                runtime_integrity=True,
                authority_execution=authority(6),
            )

        admitted = self.runtime.authorize_execution(
            nft["nft_executable_id"],
            identity_verified=True,
            capability_admitted=True,
            platform_validated=True,
            policy_accepted=True,
            runtime_integrity=True,
            authority_execution=authority(7),
        )
        self.assertTrue(admitted["execution_authorized"])
        self.assertFalse(admitted["identity_is_execution_authority"])
        self.assertEqual(len(admitted["receipt_hash72"]), 72)

    def test_archive_path_traversal_is_rejected(self) -> None:
        with self.assertRaisesRegex(Pass193Error, "HHS_P193_ARCHIVE_PATH_TRAVERSAL"):
            self.runtime.validate_archive_entries(["manifest.json", "../escape"])
        with self.assertRaisesRegex(Pass193Error, "HHS_P193_ARCHIVE_PATH_TRAVERSAL"):
            self.runtime.validate_archive_entries(["manifest.json", "/absolute"])

    def test_bundle_is_real_zip_and_never_autoexecutes(self) -> None:
        solid = self.runtime.create_hypersolid(
            "cube", 3, authority_execution=authority(1)
        )
        artifact = self.runtime.record_native_artifact(
            solid["object_id"],
            target="linux-x86_64-elf",
            binary_bytes=b"ELF-P193-BUNDLE",
            compiler_identity="test-cc",
            compiler_flags=[],
            linker_identity="test-ld",
            build_environment={"profile": "test"},
            evidence=EVIDENCE,
            license_manifest=LICENSE,
            authority_execution=authority(2),
        )
        package = self.runtime.build_portable_bundle(
            solid["object_id"],
            [artifact["artifact_id"]],
            capabilities=[],
            license_manifest=LICENSE,
            authority_execution=authority(3),
        )
        package_files = list((self.root / "packages").glob("*.zip"))
        self.assertEqual(len(package_files), 1)
        with ZipFile(package_files[0], "r") as archive:
            self.assertIn("manifest.hhs.json", archive.namelist())
            self.assertIn("install.hhs", archive.namelist())
            manifest = __import__("json").loads(archive.read("manifest.hhs.json"))
        self.assertFalse(manifest["installer"]["automatic_execution"])
        self.assertTrue(manifest["installer"]["explicit_user_action_required"])
        self.assertEqual(len(package["archive_sha256"]), 64)

    def test_replay_verifies_hash72_chain(self) -> None:
        root = self.runtime.create_hypersolid(
            "cube", 3, authority_execution=authority(1)
        )
        self.runtime.rotate(
            root["object_id"], (0, 1), 1, 4, authority_execution=authority(2)
        )
        replay = self.runtime.replay()
        self.assertTrue(replay["ok"])
        self.assertEqual(replay["receipt_count"], 2)
        self.assertEqual(len(replay["terminal_receipt_hash72"]), 72)


if __name__ == "__main__":
    unittest.main()

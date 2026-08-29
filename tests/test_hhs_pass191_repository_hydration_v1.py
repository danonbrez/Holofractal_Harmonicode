from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass191.repository_hydration import (
    CONTRACT_ID,
    FROZEN_I134,
    HydrationBounds,
    Pass191Error,
    RepositoryHydrationRuntime,
    exact_symmetry_witness,
)


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P191_TEST_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P191_TEST_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


class Pass191RepositoryHydrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state = self.root / ".state"
        self._write_fixture()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "p191@test.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Pass191 Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.root, check=True)
        self.first_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=self.root, text=True
        ).strip()
        self.runtime = RepositoryHydrationRuntime(self.root, self.state)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_json(self, relative: str, value: object) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")

    def _write_fixture(self) -> None:
        contract = self.root / (
            "docs/pass191/"
            "HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_"
            "UNIVERSAL_INVARIANT_CLOSURE.md"
        )
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(
            "# Pass 191 fixture\n"
            "G41={G_0,...,G_40}\n"
            "sigma(G_j)=G_(40-j)\n"
            "xy != yx\nzw != wz\n",
            encoding="utf-8",
        )
        genesis = self.root / "docs/genesis/GENESIS.md"
        genesis.parent.mkdir(parents=True, exist_ok=True)
        genesis.write_text("GENESIS\n", encoding="utf-8")
        for number in (1, 42, 72, 81, 159, 169, 174, 175, 189, 190):
            path = self.root / f"docs/pass{number:03d}/PASS_{number:03d}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Pass {number}\n", encoding="utf-8")
        proof = self.root / "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md"
        proof.write_text("HHS-P191-DQPL-TENSOR-VM5184-G243-H216-H72\n", encoding="utf-8")

        self._write_json(
            "native_projects/hhs_pass190_operation_fabric/registry/HHS_OPERATION_REGISTRY_V1.json",
            {
                "schema": "HHS_OPERATION_REGISTRY_V1",
                "registry_hash216": "b" * 216,
                "operations": [
                    {
                        "operation_id": "system.status",
                        "Hash216_identity": "a" * 216,
                        "implementation_status": "EXECUTABLE_VERIFIED",
                    }
                ],
            },
        )
        self._write_json(
            "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
            "PASS_191_INTEGRATED_PROOF_SEARCH.json",
            {
                "theorem_decision": {"status": "OBSTRUCTED"},
            },
        )
        self._write_json(
            "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
            "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json",
            {
                "classification": "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED",
                "visited": 51648192,
                "exact_chain_hits": 837,
                "frontier_size": 16,
                "theorem_decision": {"status": "OBSTRUCTED"},
                "authority_path": [
                    "Pass189",
                    "Pass186",
                    "Pass175",
                    "Pass174",
                    "Hash72",
                ],
                "integrated_manifold_search_hash72": "c" * 72,
                "completion_hash72": "d" * 72,
            },
        )

    def test_exact_symmetry_and_authority_boundary(self) -> None:
        witness = exact_symmetry_witness()
        self.assertTrue(witness["valid"])
        self.assertEqual(len(witness["groups"]), 41)
        self.assertEqual(len(witness["reciprocal_pairs"]), 20)
        self.assertEqual(witness["involution"]["G_20"], "G_20")
        self.assertTrue(all(pair["phase_product"] == [1, 1] for pair in witness["reciprocal_pairs"]))

    def test_full_committed_tree_hydration(self) -> None:
        manifest = self.runtime.preview()
        self.assertEqual(manifest["contract"], CONTRACT_ID)
        self.assertEqual(len(manifest["lineage"]["records"]), 191)
        self.assertTrue(manifest["lineage"]["all_slots_represented"])
        self.assertTrue(manifest["symmetry"]["valid"])
        self.assertEqual(manifest["dqpl_inheritance"]["theorem_status"], "OBSTRUCTED")
        self.assertEqual(manifest["dqpl_inheritance"]["visited"], 51648192)
        self.assertGreaterEqual(len(manifest["function_registry"]["operations"]), 16)
        self.assertEqual(len(manifest["topology"]["hydrated_repository_root_hash216"]), 216)
        self.assertEqual(manifest["blockers"], [])
        self.assertFalse(manifest["floating_point_canonical_authority"])

    def test_incremental_changed_since_is_dependency_scoped(self) -> None:
        extra = self.root / "docs/pass190/ADDITIVE.md"
        extra.write_text("additive\n", encoding="utf-8")
        subprocess.run(["git", "add", str(extra.relative_to(self.root))], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "additive"], cwd=self.root, check=True)
        manifest = self.runtime.preview(since_commit=self.first_commit)
        self.assertEqual(manifest["mode"], "INCREMENTAL")
        self.assertEqual(manifest["object_count"], 1)
        self.assertEqual(manifest["objects"][0]["path"], "docs/pass190/ADDITIVE.md")

    def test_durable_job_vm81_receipts_verify_and_replay(self) -> None:
        job = self.runtime.create_job({}, authority_execution=authority(1))
        self.assertEqual(job["stage"], "QUEUED")
        self.assertRegex(job["job_id"], r"^P191-[0-9a-f]{40}$")
        closed = self.runtime.resume_job(job["job_id"], authority_execution=authority(2))
        self.assertEqual(closed["stage"], "COMPLETED")
        self.assertTrue(self.runtime.verify_job(job["job_id"])["ok"])
        replay = self.runtime.replay_job(job["job_id"])
        self.assertTrue(replay["ok"])
        self.assertEqual(replay["mismatches"], [])
        receipts = self.runtime.replay_receipt_chain()
        self.assertTrue(receipts["ok"])
        self.assertEqual(receipts["records"], 2)
        report = self.runtime.report(job["job_id"])
        self.assertIn("Pass 191 Repository Hydration", report)
        self.assertIn("VM81 mutation authority: INHERITED SINGLETON", report)

    def test_invalid_authority_cannot_create_persistent_job(self) -> None:
        with self.assertRaises(Pass191Error):
            self.runtime.create_job({}, authority_execution={})
        self.assertEqual(self.runtime.list_jobs(), [])
        self.assertEqual(self.runtime.receipts(), [])

    def test_resource_limit_blocks_explicitly_not_silently(self) -> None:
        with self.assertRaises(Pass191Error) as captured:
            self.runtime.preview(bounds={"max_files": 1})
        self.assertEqual(captured.exception.classification, "HHS_P191_FILE_LIMIT_BLOCKED")

    def test_operation_registry_preserves_inherited_identity_and_adds_pass191(self) -> None:
        manifest = self.runtime.preview()
        operations = manifest["function_registry"]["operations"]
        inherited = next(item for item in operations if item["operation_id"] == "system.status")
        self.assertEqual(inherited["Hash216_identity"], "a" * 216)
        ids = {item["operation_id"] for item in operations}
        self.assertIn("P191.Hydrate.Repository", ids)
        self.assertIn("P191.Hydrate.Replay", ids)

    def test_frozen_predecessor_is_declared_not_rewritten(self) -> None:
        self.assertEqual(FROZEN_I134, "4bb202e657670dac1ab2a39575821b647f691d71")


if __name__ == "__main__":
    unittest.main()

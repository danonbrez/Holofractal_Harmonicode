from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass214_cumulative_operation_census_v1 import (
    FROZEN_RUNTIME,
    FROZEN_RUNTIME_GIT_BLOB,
)
from hhs_backend.runtime.hhs_pass217_inherited_authority_freeze_v1 import (
    BASE_COMMIT,
    BASE_TREE,
    CLASSIFICATION,
    CONTRACT_PATHS,
    FOCUS_FAMILIES,
    SCHEMA,
    Pass217FreezeError,
    build_inherited_authority_freeze,
    load_inherited_authority_freeze,
    validate_inherited_authority_freeze,
)

EVIDENCE = (
    ROOT
    / "evidence"
    / "pass217"
    / "PASS_217_ITERATION_1_INHERITED_AUTHORITY_FREEZE.json"
)
SCHEMA_PATH = (
    ROOT
    / "contracts"
    / "pass217"
    / "PASS_217_ITERATION_1_INHERITED_AUTHORITY_FREEZE.schema.json"
)
MODULE = ROOT / "hhs_backend" / "runtime" / "hhs_pass217_inherited_authority_freeze_v1.py"


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args],
        text=True,
    ).strip()


class Pass217Iteration1FreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recorded = load_inherited_authority_freeze(EVIDENCE)
        cls.rebuilt = build_inherited_authority_freeze(ROOT)

    def test_exact_recorded_evidence_rebuild(self) -> None:
        self.assertEqual(self.recorded, self.rebuilt)
        self.assertEqual(self.recorded["schema"], SCHEMA)
        self.assertEqual(self.recorded["classification"], CLASSIFICATION)

    def test_base_identity_is_frozen_and_ancestral(self) -> None:
        self.assertEqual(self.recorded["base"]["commit"], BASE_COMMIT)
        self.assertEqual(self.recorded["base"]["tree"], BASE_TREE)
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASE_COMMIT, "HEAD"],
            check=False,
        )
        self.assertEqual(completed.returncode, 0)

    def test_contracts_and_protected_runtime_are_object_bound(self) -> None:
        contracts = {row["path"]: row for row in self.recorded["contracts"]}
        self.assertEqual(tuple(contracts), CONTRACT_PATHS)
        for path, row in contracts.items():
            self.assertEqual(row["git_blob"], git("rev-parse", f"{BASE_COMMIT}:{path}"))
        protected = self.recorded["protected_authority"]
        self.assertEqual(protected["c_vm81_runtime_nucleus"]["path"], FROZEN_RUNTIME)
        self.assertEqual(
            protected["c_vm81_runtime_nucleus"]["git_blob"],
            FROZEN_RUNTIME_GIT_BLOB,
        )
        self.assertFalse(protected["semantics_modified"])
        self.assertFalse(protected["abi_modified"])
        self.assertEqual(
            git("diff", "--name-only", BASE_COMMIT, "HEAD", "--", FROZEN_RUNTIME),
            "",
        )

    def test_pass214_census_authorities_are_reused_without_collapse(self) -> None:
        tree = self.recorded["repository_tree_inventory"]
        operations = self.recorded["cumulative_operation_inventory"]
        self.assertTrue(tree["coverage"]["classification_complete"])
        self.assertEqual(tree["coverage"]["static_scan_errors"], 0)
        self.assertEqual(operations["coverage"]["raw_operation_identities"], 19536)
        self.assertFalse(operations["automatic_semantic_collapse_performed"])
        anchors = operations["known_opcode_family_anchors"]
        self.assertTrue(anchors["all_satisfied"])
        self.assertEqual(anchors["raw_known_opcode_identity_minimum"], 137)

    def test_pass219_focus_is_discovery_only_and_complete_as_an_index(self) -> None:
        inventory = self.recorded["pass219_preparation_inventory"]
        families = inventory["families"]
        self.assertEqual(set(families), {name for name, _ in FOCUS_FAMILIES})
        for name, row in families.items():
            self.assertGreater(row["matched_tracked_file_count"], 0, name)
            self.assertFalse(row["semantic_equivalence_proven"], name)
            self.assertFalse(row["authority_promoted"], name)
        self.assertGreater(families["rna_molecular_constraints"]["matched_tracked_file_count"], 0)
        self.assertGreater(families["protein_fold_topology"]["matched_tracked_file_count"], 0)
        self.assertGreater(families["e6_exact_symmetry"]["matched_tracked_file_count"], 0)
        self.assertFalse(inventory["pass219_runtime_implementation_started"])

    def test_inheritance_gap_is_recorded_without_erasing_candidate_work(self) -> None:
        gate = self.recorded["inheritance_gate"]
        window = self.recorded["numbered_pass_inventory"]["required_transition_window"]
        self.assertTrue(gate["pass_215_surfaces_present_on_bound_base"])
        self.assertFalse(gate["pass_216_surfaces_present_on_bound_base"])
        self.assertGreater(window["pass_215"]["tracked_blob_count"], 0)
        self.assertEqual(window["pass_216"]["tracked_blob_count"], 0)
        self.assertEqual(
            gate["status"],
            "HOLD_FOR_PASS_215_216_AUTHORITATIVE_RECONCILIATION",
        )
        self.assertTrue(gate["contract_schema_and_inventory_preparation_may_continue"])
        self.assertFalse(gate["genesis_rom_or_runtime_authority_promotion_allowed"])

    def test_claim_boundary_does_not_promote_runtime_authority(self) -> None:
        claims = self.recorded["claim_boundary"]
        self.assertTrue(claims["iteration1_inventory_complete_for_bound_base"])
        for key in (
            "runtime_mutation_performed",
            "protected_c_runtime_modified",
            "canonical_authority_promoted",
            "genesis_rom_generated",
            "golay_physical_rom_generated",
            "migration_started",
            "authoritative_hash72_transition_receipt_minted",
            "authoritative_hash216_transition_minted",
            "pass217_implementation_complete",
            "pass219_implementation_complete",
        ):
            self.assertFalse(claims[key], key)

    def test_authoritative_source_contains_no_float_literals(self) -> None:
        tree = ast.parse(MODULE.read_text(encoding="utf-8"))
        float_literals = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, float)
        ]
        self.assertEqual(float_literals, [])

    def test_schema_coordinates_match_runtime_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema"]["const"], SCHEMA)
        self.assertEqual(
            schema["properties"]["classification"]["const"],
            CLASSIFICATION,
        )
        self.assertEqual(schema["properties"]["pass"]["const"], 217)
        self.assertEqual(schema["properties"]["iteration"]["const"], 1)

    def test_tamper_is_rejected(self) -> None:
        tampered = deepcopy(self.recorded)
        tampered["base"]["tree"] = "0" * 40
        with self.assertRaisesRegex(
            Pass217FreezeError,
            "FREEZE_SHA256_MISMATCH",
        ):
            validate_inherited_authority_freeze(tampered)


if __name__ == "__main__":
    unittest.main(verbosity=2)

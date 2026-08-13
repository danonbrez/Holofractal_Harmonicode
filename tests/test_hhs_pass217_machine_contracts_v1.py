from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass217_machine_contracts_v1 import (
    BASE_COMMIT,
    CHECKSUM_PATH,
    CLASSIFICATION,
    EVIDENCE_PATH,
    HASH216_SECTIONS,
    INHERITANCE_HOLD,
    JSON_ARTIFACT_PATHS,
    LO_SHU,
    LO_SHU_PHASE_CHANNELS,
    ORDERED_PHASE_REGISTRY,
    Pass217Iteration2Error,
    address_record,
    build_bundle,
    exhaustive_address_root,
    hash72_matrix_root,
    orbit_coordinate,
    validate_bundle,
)
from hhs_runtime.core.hash72_validator_v1 import HASH72_ALPHABET, validate_hash72


MODULE = ROOT / "hhs_backend" / "runtime" / "hhs_pass217_machine_contracts_v1.py"
CLI = ROOT / "tools" / "pass217_iteration2_machine_contracts.py"
PROTECTED_RUNTIME = "hhs_runtime/HARMONICODE_VM_RUNTIME.c"


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_float(item) for item in value)
    return False


class Pass217Iteration2MachineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.expected = build_bundle(ROOT)
        cls.actual = {path: (ROOT / path).read_bytes() for path in cls.expected}
        cls.machine = json.loads(cls.actual["contracts/pass217/machine_contract.json"])
        cls.invariants = json.loads(cls.actual["contracts/pass217/invariants.json"])
        cls.references = json.loads(cls.actual["contracts/pass217/reference_vectors.json"])
        cls.evidence = json.loads(cls.actual[EVIDENCE_PATH])

    def test_exact_bundle_rebuild_and_validation(self) -> None:
        self.assertEqual(self.actual, self.expected)
        summary = validate_bundle(ROOT, self.actual)
        self.assertEqual(summary["classification"], CLASSIFICATION)
        self.assertEqual(summary["bundle_root_sha256"], self.evidence["bundle_root_sha256"])

    def test_all_source_decisions_are_bound_to_frozen_git_objects(self) -> None:
        bindings = self.machine["source_bindings"]
        self.assertEqual(len(bindings), 9)
        by_role = {row["role"]: row for row in bindings}
        for row in bindings:
            self.assertEqual(row["git_blob"], git("rev-parse", f"{BASE_COMMIT}:{row['path']}"))
            content = subprocess.check_output(
                ["git", "-C", str(ROOT), "show", f"{BASE_COMMIT}:{row['path']}"]
            )
            self.assertEqual(row["sha256"], sha256(content).hexdigest())
        self.assertEqual(
            by_role["CANONICAL_HASH72_FORMAT"]["disposition"],
            "REUSE_CANONICAL_FORMAT",
        )
        self.assertEqual(
            by_role["LEGACY_GOLAY_STYLE_HOOK"]["disposition"],
            "REJECT_AS_GOLAY_IMPLEMENTATION_PLACEHOLDER_ONLY",
        )
        self.assertEqual(
            by_role["LEGACY_LOSHU_EMBEDDING"]["disposition"],
            "COMPATIBILITY_SOURCE_NOT_HASH72_FORMAT_AUTHORITY",
        )

    def test_exhaustive_vm5184_address_bijections(self) -> None:
        cell_operation = set()
        hash72_coordinates = set()
        for linear in range(5_184):
            row = address_record(linear)
            self.assertEqual(linear, 64 * row["cell"] + row["operation"])
            self.assertEqual(row["operation"], 8 * row["alpha"] + row["beta"])
            self.assertEqual(linear, 72 * row["hash72_row"] + row["hash72_column"])
            cell_operation.add((row["cell"], row["operation"]))
            hash72_coordinates.add((row["hash72_row"], row["hash72_column"]))
        self.assertEqual(len(cell_operation), 5_184)
        self.assertEqual(len(hash72_coordinates), 5_184)
        self.assertEqual(
            self.references["address_map"]["exhaustive_root_sha256"],
            exhaustive_address_root(),
        )

    def test_g243_projection_is_exact_and_bounded(self) -> None:
        for linear in (0, 1, 63, 64, 5_183):
            for control in (0, 1, 242):
                row = address_record(linear, control)
                self.assertEqual(row["projected"], 243 * linear + control)
                recovered_linear, recovered_control = divmod(row["projected"], 243)
                self.assertEqual((recovered_linear, recovered_control), (linear, control))
        self.assertEqual(address_record(5_183, 242)["projected"], 1_259_711)

    def test_ordered_phase_surface_and_nucleus_are_pointwise_frozen(self) -> None:
        phase = self.references["ordered_phase"]
        self.assertEqual(tuple(phase["registry"]), ORDERED_PHASE_REGISTRY)
        self.assertEqual(len(phase["pair_surface"]), 64)
        self.assertIn("xy>yx", phase["pair_surface"])
        self.assertIn("yx>xy", phase["pair_surface"])
        self.assertNotEqual(phase["pair_surface"].index("xy>yx"), phase["pair_surface"].index("yx>xy"))
        nucleus = self.machine["lo_shu_nucleus"]
        self.assertEqual(nucleus["values"], [list(row) for row in LO_SHU])
        expected_channels = [[list(cell) for cell in row] for row in LO_SHU_PHASE_CHANNELS]
        self.assertEqual(nucleus["phase_channels"], expected_channels)
        self.assertTrue(nucleus["fixed_pointwise"])

    def test_hash72_alphabet_matrix_and_orbits_are_exact(self) -> None:
        reference = self.references["hash72"]
        self.assertEqual(reference["alphabet"], HASH72_ALPHABET)
        self.assertEqual(len(HASH72_ALPHABET), 72)
        self.assertEqual(len(set(HASH72_ALPHABET)), 72)
        self.assertTrue(validate_hash72(HASH72_ALPHABET))
        self.assertEqual(reference["matrix_byte_count"], 5_184)
        self.assertEqual(reference["matrix_root_sha256"], hash72_matrix_root())
        for direction in ("x", "y", "z", "w"):
            for point in ((0, 0), (35, 36), (71, 71)):
                forward = orbit_coordinate(direction, *point, 1)
                self.assertEqual(orbit_coordinate(direction, *forward, -1), point)
                self.assertEqual(orbit_coordinate(direction, *point, 72), point)
        self.assertFalse(reference["logical_genesis_rom_materialized"])

    def test_hash216_sections_and_positional_commitments_do_not_alias(self) -> None:
        reference = self.references["hash216"]
        self.assertEqual(HASH216_SECTIONS, ("previous", "next", "receipt"))
        self.assertEqual(reference["combined"], "".join(reference[name] for name in HASH216_SECTIONS))
        self.assertEqual(len(reference["combined"]), 216)
        self.assertEqual(len(reference["position_commitments"]), 216)
        self.assertEqual(len(set(reference["position_commitments"])), 216)
        self.assertEqual(reference["previous"][0], reference["next"][71])
        self.assertNotEqual(reference["position_commitments"][0], reference["position_commitments"][143])
        self.assertEqual(reference["authority_status"], "REFERENCE_ONLY_NOT_ADMITTED")
        self.assertFalse(self.machine["hash216_contract"]["legacy_predecessor_current_successor_equivalence_proven"])
        self.assertTrue(self.machine["hash216_contract"]["legacy_lane_adapter_required"])

    def test_schemas_freeze_shapes_without_granting_authority(self) -> None:
        address = json.loads(self.actual["contracts/pass217/address_map.schema.json"])
        hash72 = json.loads(self.actual["contracts/pass217/hash72.schema.json"])
        hash216 = json.loads(self.actual["contracts/pass217/hash216.schema.json"])
        rom = json.loads(self.actual["contracts/pass217/rom_manifest.schema.json"])
        self.assertEqual(address["properties"]["linear"]["maximum"], 5_183)
        self.assertEqual(address["properties"]["projected"]["maximum"], 1_259_711)
        self.assertEqual(hash72["properties"]["serialized"]["minLength"], 72)
        self.assertEqual(hash216["properties"]["combined"]["minLength"], 216)
        self.assertEqual(rom["properties"]["logical_bytes"]["const"], 648)
        self.assertEqual(rom["properties"]["physical_bytes"]["const"], 1_296)
        self.assertIn("UNMATERIALIZED", rom["properties"]["build_status"]["enum"])

    def test_golay_profile_is_sizing_and_bound_authority_only(self) -> None:
        golay = self.references["golay"]
        self.assertEqual(golay["code"], "EXTENDED_BINARY_GOLAY_24_12_8")
        self.assertEqual(golay["word_count"] * golay["payload_bits"], 5_184)
        self.assertEqual(golay["word_count"] * golay["codeword_bits"], 10_368)
        self.assertEqual(golay["decoder_status"], "PROFILE_ONLY")
        self.assertEqual(golay["generator_definition_status"], "DEFERRED")
        self.assertFalse(golay["codewords_generated"])
        for row in golay["mixed_bound_vectors"]:
            self.assertEqual(row["admissible"], 2 * row["unknown_errors"] + row["known_erasures"] <= 7)

    def test_vector_store_reference_cannot_admit_or_alias(self) -> None:
        entry = self.references["vector_store"]
        self.assertEqual(entry["admission_status"], "REFERENCE_ONLY")
        self.assertEqual(entry["forward_support"], entry["inverse_support"])
        self.assertEqual(entry["forward_support"], sorted(set(entry["forward_support"])))
        self.assertNotEqual(entry["parent_state_sha256"], entry["candidate_state_sha256"])
        contract = self.machine["vector_store_contract"]
        self.assertTrue(contract["similarity_is_candidate_discovery_only"])
        self.assertFalse(contract["vm81_admission_bypass_allowed"])

    def test_claim_boundary_and_predecessor_hold_are_consistent(self) -> None:
        self.assertEqual(self.machine["inheritance_gate"]["status"], INHERITANCE_HOLD)
        self.assertEqual(self.evidence["inheritance_gate"]["status"], INHERITANCE_HOLD)
        for holder in (self.machine, self.invariants, self.references, self.evidence):
            claims = holder["claim_boundary"]
            self.assertTrue(claims["schema_and_reference_preparation_complete"])
            for key, value in claims.items():
                if key != "schema_and_reference_preparation_complete":
                    self.assertFalse(value, key)

    def test_checksum_and_evidence_roots_cover_the_complete_bundle(self) -> None:
        lines = self.actual[CHECKSUM_PATH].decode("utf-8").splitlines()
        self.assertEqual(len(lines), len(JSON_ARTIFACT_PATHS))
        covered = set()
        for line in lines:
            checksum, path = line.split("  ", 1)
            covered.add(path)
            self.assertEqual(checksum, sha256(self.actual[path]).hexdigest())
        self.assertEqual(covered, set(JSON_ARTIFACT_PATHS))
        evidence_rows = {row["path"]: row for row in self.evidence["bundle_files"]}
        self.assertEqual(set(evidence_rows), set(JSON_ARTIFACT_PATHS) | {CHECKSUM_PATH})

    def test_authoritative_sources_and_json_contain_no_float_values(self) -> None:
        for path in (MODULE, CLI):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            floats = [
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, float)
            ]
            self.assertEqual(floats, [], path)
        for path in JSON_ARTIFACT_PATHS + (EVIDENCE_PATH,):
            self.assertFalse(contains_float(json.loads(self.actual[path])), path)

    def test_protected_runtime_is_unchanged_and_tamper_fails_closed(self) -> None:
        self.assertEqual(
            git("diff", "--name-only", BASE_COMMIT, "HEAD", "--", PROTECTED_RUNTIME),
            "",
        )
        tampered = deepcopy(self.actual)
        machine = json.loads(tampered["contracts/pass217/machine_contract.json"])
        machine["dimensions"]["logical_bits"] = 5_183
        tampered["contracts/pass217/machine_contract.json"] = (
            json.dumps(machine, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        )
        with self.assertRaisesRegex(Pass217Iteration2Error, "BUNDLE_DRIFT"):
            validate_bundle(ROOT, tampered)


if __name__ == "__main__":
    unittest.main(verbosity=2)

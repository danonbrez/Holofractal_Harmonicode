from __future__ import annotations

import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hhs_backend.runtime.hhs_pass217_genesis_candidate_v1 import (
    ADDRESS_MAP_BYTES,
    ADDRESS_MAP_PATH,
    ADDRESS_RECORD_WIDTH,
    BUNDLE_PATHS,
    CANDIDATE_PATH,
    CHECKSUM_PATH,
    CLASSIFICATION,
    FROZEN_PHASE_TABLE,
    INHERITANCE_HOLD,
    ITERATION2_REMOTE_COMMIT,
    ITERATION2_TREE,
    LOGICAL_BITS,
    LOGICAL_BYTES,
    MANIFEST_PATH,
    MANIFEST_SCHEMA_PATH,
    PROFILE_ID,
    Pass217Iteration3Error,
    REFERENCE_PATH,
    build_address_map_bytes,
    build_bundle,
    build_candidate_bytes,
    candidate_bit,
    candidate_bit_at,
    candidate_shard_root,
    decode_address_record,
    lo_shu_cell_value,
    packed_address_record,
    source_bindings,
    validate_bundle,
)
from hhs_backend.runtime.hhs_pass217_machine_contracts_v1 import (
    BASE_COMMIT,
    LO_SHU,
    LO_SHU_PHASE_CHANNELS,
    exhaustive_address_root,
)


MODULE = ROOT / "hhs_backend" / "runtime" / "hhs_pass217_genesis_candidate_v1.py"
CLI = ROOT / "tools" / "pass217_iteration3_genesis_candidate.py"
PROTECTED_RUNTIME = "hhs_runtime/HARMONICODE_VM_RUNTIME.c"
ITERATION2_ARTIFACTS = {
    "contracts/pass217/machine_contract.json": (
        "566c5f71a03042976837d28bf3b8265f6d1073bcd0b9a12d89746536f809c3af"
    ),
    "contracts/pass217/reference_vectors.json": (
        "fbd7cb43dfa7c3c13e71254efca068211fc134469d506ba9367b819c9c4f56ae"
    ),
    "evidence/pass217/PASS_217_ITERATION_2_MACHINE_CONTRACTS.json": (
        "3e57ac3d45cfa664ff50ab709c5d78dc18f886bbecaf9c00673de759144a2e02"
    ),
}


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], text=True
    ).strip()


def contains_float(value: object) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, dict):
        return any(contains_float(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_float(item) for item in value)
    return False


class Pass217Iteration3GenesisCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.expected = build_bundle(ROOT)
        cls.actual = {path: (ROOT / path).read_bytes() for path in BUNDLE_PATHS}
        cls.summary = validate_bundle(ROOT, cls.actual)
        cls.manifest = json.loads(cls.actual[MANIFEST_PATH])
        cls.references = json.loads(cls.actual[REFERENCE_PATH])
        cls.schema = json.loads(cls.actual[MANIFEST_SCHEMA_PATH])
        cls.image = cls.actual[CANDIDATE_PATH]
        cls.addresses = cls.actual[ADDRESS_MAP_PATH]

    def test_exact_bundle_rebuild_and_validation(self) -> None:
        self.assertEqual(self.actual, self.expected)
        self.assertEqual(self.summary["classification"], CLASSIFICATION)
        self.assertEqual(self.summary["candidate_bytes"], LOGICAL_BYTES)
        self.assertEqual(self.summary["address_map_bytes"], ADDRESS_MAP_BYTES)
        self.assertFalse(self.summary["canonical_authority_promoted"])

    def test_iteration2_sources_are_exact_git_object_bindings(self) -> None:
        self.assertEqual(
            git("rev-parse", f"{ITERATION2_REMOTE_COMMIT}^{{tree}}"),
            ITERATION2_TREE,
        )
        bindings = source_bindings(ROOT)
        self.assertEqual(len(bindings), 6)
        for row in bindings:
            self.assertEqual(row["revision"], ITERATION2_REMOTE_COMMIT)
            self.assertEqual(
                row["git_blob"],
                git("rev-parse", f"{ITERATION2_REMOTE_COMMIT}:{row['path']}"),
            )
            content = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(ROOT),
                    "show",
                    f"{ITERATION2_REMOTE_COMMIT}:{row['path']}",
                ]
            )
            self.assertEqual(row["sha256"], sha256(content).hexdigest())
        by_role = {row["role"]: row for row in bindings}
        self.assertIn(
            "REJECT_ALTERNATE_HASH72",
            by_role["TILED_LOSHU_ADDRESS_IDENTITY"]["disposition"],
        )
        self.assertEqual(
            by_role["PROTECTED_VM81_RUNTIME"]["disposition"],
            "BOUND_UNMODIFIED_NO_RUNTIME_MUTATION",
        )

    def test_frozen_phase_table_is_exact_and_balanced_by_quadrant_parity(self) -> None:
        self.assertEqual(len(FROZEN_PHASE_TABLE), 64)
        self.assertEqual(
            Counter(FROZEN_PHASE_TABLE),
            Counter({0: 14, 18: 16, 36: 18, 54: 16}),
        )
        parity = Counter((phase // 18) & 1 for phase in FROZEN_PHASE_TABLE)
        self.assertEqual(parity, Counter({0: 32, 1: 32}))
        self.assertEqual(
            self.references["phase_table_degrees"], list(FROZEN_PHASE_TABLE)
        )

    def test_candidate_is_exact_5184_bit_formula_image(self) -> None:
        self.assertEqual(self.image, build_candidate_bytes())
        self.assertEqual(len(self.image), 648)
        observed_one_bits = 0
        for linear in range(LOGICAL_BITS):
            cell, operation = divmod(linear, 64)
            observed = candidate_bit_at(self.image, linear)
            self.assertEqual(observed, candidate_bit(cell, operation))
            observed_one_bits += observed
        self.assertEqual(observed_one_bits, 2_592)
        self.assertEqual(self.manifest["logical_genesis_candidate"]["one_bits"], 2_592)
        self.assertEqual(self.manifest["logical_genesis_candidate"]["zero_bits"], 2_592)

    def test_lsb0_serialization_and_every_shard_balance(self) -> None:
        for cell in range(81):
            shard = self.image[cell * 8 : cell * 8 + 8]
            self.assertEqual(sum(value.bit_count() for value in shard), 32)
            reconstructed = 0
            for operation in range(64):
                reconstructed |= candidate_bit(cell, operation) << operation
            self.assertEqual(shard, reconstructed.to_bytes(8, "little"))
        self.assertEqual(
            self.manifest["logical_genesis_candidate"]["shard_root_sha256"],
            candidate_shard_root(self.image),
        )

    def test_exhaustive_packed_address_map_and_all_inverse_views(self) -> None:
        self.assertEqual(self.addresses, build_address_map_bytes())
        self.assertEqual(len(self.addresses), 31_104)
        self.assertEqual(ADDRESS_RECORD_WIDTH, 6)
        cell_operation = set()
        phase_pair = set()
        hash72 = set()
        for linear in range(LOGICAL_BITS):
            offset = ADDRESS_RECORD_WIDTH * linear
            self.assertEqual(
                self.addresses[offset : offset + ADDRESS_RECORD_WIDTH],
                packed_address_record(linear),
            )
            row = decode_address_record(self.addresses, linear)
            self.assertEqual(linear, 64 * row["cell"] + row["operation"])
            self.assertEqual(row["operation"], 8 * row["alpha"] + row["beta"])
            self.assertEqual(linear, 72 * row["hash72_row"] + row["hash72_column"])
            cell_operation.add((row["cell"], row["operation"]))
            phase_pair.add((row["cell"], row["alpha"], row["beta"]))
            hash72.add((row["hash72_row"], row["hash72_column"]))
        self.assertEqual(len(cell_operation), LOGICAL_BITS)
        self.assertEqual(len(phase_pair), LOGICAL_BITS)
        self.assertEqual(len(hash72), LOGICAL_BITS)

    def test_g243_projection_formula_covers_complete_exact_range(self) -> None:
        count = 0
        first = None
        last = None
        for linear in range(LOGICAL_BITS):
            for control in range(243):
                projected = 243 * linear + control
                if first is None:
                    first = projected
                last = projected
                self.assertEqual(divmod(projected, 243), (linear, control))
                count += 1
        self.assertEqual(first, 0)
        self.assertEqual(last, 1_259_711)
        self.assertEqual(count, 1_259_712)

    def test_tiled_loshu_and_central_nucleus_are_pointwise_fixed(self) -> None:
        for row in range(9):
            for column in range(9):
                cell = 9 * row + column
                self.assertEqual(
                    lo_shu_cell_value(cell), LO_SHU[row % 3][column % 3]
                )
        nucleus = self.manifest["lo_shu_nucleus"]
        self.assertTrue(nucleus["fixed_pointwise"])
        self.assertEqual(
            nucleus["root_sha256"],
            "da7b33fa1a419e00ce81eeeeb5f1c435acd6ae7b95d355e3a1749a6a238e3164",
        )
        self.assertEqual(
            nucleus["central_cell_indices"],
            [30, 31, 32, 39, 40, 41, 48, 49, 50],
        )
        for index, row in enumerate(nucleus["pointwise_records"]):
            local_row, local_column = divmod(index, 3)
            value, channel = LO_SHU_PHASE_CHANNELS[local_row][local_column]
            self.assertEqual(row["value"], value)
            self.assertEqual(row["phase_channel_value"], value)
            self.assertEqual(row["phase_channel"], channel)
            self.assertEqual(row["shard_one_bits"], 32)

    def test_reference_vectors_bind_bits_addresses_and_nucleus(self) -> None:
        self.assertEqual(self.references["profile_id"], PROFILE_ID)
        self.assertEqual(
            self.references["candidate_sha256"], sha256(self.image).hexdigest()
        )
        self.assertEqual(
            self.references["address_map_sha256"], sha256(self.addresses).hexdigest()
        )
        self.assertEqual(
            self.references["iteration2_semantic_address_root_sha256"],
            exhaustive_address_root(),
        )
        for vector in self.references["boundary_vectors"]:
            linear = vector["linear"]
            cell, operation = divmod(linear, 64)
            self.assertEqual(vector["candidate_bit"], candidate_bit(cell, operation))
            self.assertEqual(vector["expected_bit"], vector["candidate_bit"])
            self.assertEqual(
                vector["packed_address_hex"], packed_address_record(linear).hex()
            )

    def test_manifest_schema_and_claim_boundary_forbid_promotion(self) -> None:
        self.assertEqual(self.manifest["classification"], CLASSIFICATION)
        self.assertEqual(self.manifest["inheritance_gate"]["status"], INHERITANCE_HOLD)
        self.assertFalse(
            self.manifest["inheritance_gate"]["predecessor_reconciliation_complete"]
        )
        self.assertFalse(
            self.manifest["inheritance_gate"]["canonical_promotion_allowed"]
        )
        self.assertEqual(
            self.manifest["candidate_profile"]["selection_status"],
            "CANDIDATE_PROFILE_NOT_CANONICAL_SELECTION",
        )
        claims = self.manifest["claim_boundary"]
        self.assertTrue(claims["logical_genesis_candidate_generated"])
        self.assertTrue(claims["address_map_artifact_generated"])
        self.assertFalse(claims["canonical_genesis_selected"])
        self.assertFalse(claims["logical_genesis_rom_generated"])
        self.assertFalse(claims["canonical_authority_promoted"])
        self.assertFalse(claims["runtime_mutation_performed"])
        claim_schema = self.schema["properties"]["claim_boundary"]
        for key, value in claims.items():
            self.assertEqual(claim_schema["properties"][key]["const"], value)

    def test_checksums_and_manifest_cover_every_payload(self) -> None:
        checksum_rows = {}
        for line in self.actual[CHECKSUM_PATH].decode("ascii").splitlines():
            checksum, path = line.split("  ", 1)
            checksum_rows[path] = checksum
            self.assertEqual(checksum, sha256(self.actual[path]).hexdigest())
        self.assertEqual(set(checksum_rows), set(BUNDLE_PATHS) - {CHECKSUM_PATH})
        manifest_rows = {row["path"]: row for row in self.manifest["artifacts"]}
        expected_manifest_paths = {
            MANIFEST_SCHEMA_PATH,
            REFERENCE_PATH,
            CANDIDATE_PATH,
            ADDRESS_MAP_PATH,
        }
        self.assertEqual(set(manifest_rows), expected_manifest_paths)
        for path, row in manifest_rows.items():
            self.assertEqual(row["sha256"], sha256(self.actual[path]).hexdigest())
            self.assertEqual(row["size_bytes"], len(self.actual[path]))

    def test_iteration2_artifacts_are_byte_unchanged(self) -> None:
        for path, expected_sha256 in ITERATION2_ARTIFACTS.items():
            self.assertEqual(
                sha256((ROOT / path).read_bytes()).hexdigest(),
                expected_sha256,
                path,
            )

    def test_no_float_authority_and_no_physical_golay_artifact(self) -> None:
        for path in (MODULE, CLI):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            floats = [
                node.value
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant) and isinstance(node.value, float)
            ]
            self.assertEqual(floats, [], path)
        for path in (MANIFEST_PATH, MANIFEST_SCHEMA_PATH, REFERENCE_PATH):
            self.assertFalse(contains_float(json.loads(self.actual[path])), path)
        self.assertFalse(
            any("GOLAY" in path and path.endswith(".bin") for path in BUNDLE_PATHS)
        )
        self.assertFalse(self.manifest["claim_boundary"]["golay_codec_implemented"])
        self.assertFalse(
            self.manifest["claim_boundary"]["golay_physical_rom_generated"]
        )

    def test_protected_runtime_unchanged_and_candidate_tamper_fails_closed(self) -> None:
        self.assertEqual(
            git("diff", "--name-only", BASE_COMMIT, "HEAD", "--", PROTECTED_RUNTIME),
            "",
        )
        tampered = dict(self.actual)
        image = bytearray(tampered[CANDIDATE_PATH])
        image[0] ^= 1
        tampered[CANDIDATE_PATH] = bytes(image)
        with self.assertRaisesRegex(Pass217Iteration3Error, "BUNDLE_DRIFT"):
            validate_bundle(ROOT, tampered)

    def test_address_tamper_fails_closed(self) -> None:
        tampered = dict(self.actual)
        addresses = bytearray(tampered[ADDRESS_MAP_PATH])
        addresses[-1] ^= 1
        tampered[ADDRESS_MAP_PATH] = bytes(addresses)
        with self.assertRaisesRegex(Pass217Iteration3Error, "BUNDLE_DRIFT"):
            validate_bundle(ROOT, tampered)


if __name__ == "__main__":
    unittest.main(verbosity=2)

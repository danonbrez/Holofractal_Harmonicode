from __future__ import annotations

from base64 import b64encode
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from hhs_backend.runtime.hhs_pass213_compiled_rom_v1 import (
    FULL_HYDRATION_DOMAIN,
    VM5184_G243_DOMAIN,
    VM5184_STATES,
    canonical_bytes,
    hash216,
)
from hhs_backend.runtime.hhs_pass213_tensor_boundary_v1 import (
    FloatingTensorProjection,
    Pass213TensorBoundaryError,
    TensorAnchorBinding,
)
from hhs_backend.runtime.hhs_pass213_tensor_closure_v1 import TensorClosureProof
from hhs_backend.runtime.hhs_pass213_moving_tensor_v1 import (
    MovingTensorState,
    Pass213TensorError,
)
from hhs_backend.runtime.hhs_pass213_tensor_store_v1 import MovingTensorStore
from hhs_backend.runtime.hhs_pass213_trusted_timestamp_v1 import (
    RFC3161TimestampEvidence,
    TimestampAnchorIntent,
    TrustedTimestampAnchorRecord,
)

TENSOR_KEY = bytes((index * 37 + 5) % 256 for index in range(32))


def synthetic_anchor(sequence: int = 1, timestamp_ns: int = 8_000_001) -> TrustedTimestampAnchorRecord:
    signed_root = hash216("tensor-test-signed-checkpoint", str(sequence).encode())
    verifier_root = hash216("tensor-test-verifier-bundle", b"public")
    intent = TimestampAnchorIntent.create(
        signed_sequence=sequence,
        signed_checkpoint_root_hash216=signed_root,
        verifier_bundle_root_hash216=verifier_root,
        prior_anchor_root_hash216=(
            "0" * 64
            if sequence == 1
            else hash216("tensor-test-prior-anchor", str(sequence - 1).encode())
        ),
        hash216_lineage_root=hash216(
            "tensor-test-hash216-lineage", str(sequence).encode()
        ),
        requested_timestamp_ns=timestamp_ns,
        authority_id="HHS_PASS213_ITER8_TEST_TSA",
    )
    request_der = f"tensor-request-{sequence}".encode()
    response_der = f"tensor-response-{sequence}".encode()
    unsigned_evidence = {
        "schema": "HHS_PASS_213_RFC3161_TIMESTAMP_EVIDENCE_V1",
        "contract": "HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243",
        "iteration": 7,
        "authority_id": intent.authority_id,
        "request_der_b64": b64encode(request_der).decode("ascii"),
        "response_der_b64": b64encode(response_der).decode("ascii"),
        "request_sha256": sha256(request_der).hexdigest(),
        "response_sha256": sha256(response_der).hexdigest(),
        "message_imprint_sha256": sha256(intent.anchor_message()).hexdigest(),
        "tsa_policy_oid": "1.2.3.4.8",
        "tsa_serial_hex": hex(sequence),
        "gen_time_utc": f"2026-08-05T22:5{sequence}:00.000000Z",
        "tsa_subject": "CN=HHS Pass 213 Iteration 8 Test TSA",
        "nonce_hex": hex(0x1000 + sequence),
        "trust_bundle_sha256": sha256(b"tensor-test-trust-bundle").hexdigest(),
        "verification_receipt_hash216": hash216(
            "tensor-test-rfc3161-verification", str(sequence).encode()
        ),
    }
    evidence = RFC3161TimestampEvidence(
        authority_id=intent.authority_id,
        request_der_b64=unsigned_evidence["request_der_b64"],
        response_der_b64=unsigned_evidence["response_der_b64"],
        request_sha256=unsigned_evidence["request_sha256"],
        response_sha256=unsigned_evidence["response_sha256"],
        message_imprint_sha256=unsigned_evidence["message_imprint_sha256"],
        tsa_policy_oid=unsigned_evidence["tsa_policy_oid"],
        tsa_serial_hex=unsigned_evidence["tsa_serial_hex"],
        gen_time_utc=unsigned_evidence["gen_time_utc"],
        tsa_subject=unsigned_evidence["tsa_subject"],
        nonce_hex=unsigned_evidence["nonce_hex"],
        trust_bundle_sha256=unsigned_evidence["trust_bundle_sha256"],
        verification_receipt_hash216=unsigned_evidence[
            "verification_receipt_hash216"
        ],
        evidence_root_hash216=hash216(
            "rfc3161-timestamp-evidence", canonical_bytes(unsigned_evidence)
        ),
    )
    signed_checkpoint = {
        "schema": "HHS_PASS_213_SIGNED_INVENTORY_CHECKPOINT_V1",
        "signed_sequence": sequence,
        "signed_checkpoint_root_hash216": signed_root,
        "verifier_bundle_root_hash216": verifier_root,
    }
    provisional = TrustedTimestampAnchorRecord(
        intent=intent,
        signed_checkpoint=signed_checkpoint,
        evidence=evidence,
        anchor_root_hash216="",
    )
    return replace(
        provisional,
        anchor_root_hash216=hash216(
            "trusted-external-timestamp-anchor",
            canonical_bytes(provisional.rooted_payload()),
        ),
    )


def assert_no_float(test: unittest.TestCase, value: object) -> None:
    if isinstance(value, float):
        test.fail(f"canonical tensor contains float: {value!r}")
    if isinstance(value, dict):
        for child in value.values():
            assert_no_float(test, child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            assert_no_float(test, child)


class Pass213Iteration8MovingTensorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.anchor1 = synthetic_anchor(1, 8_000_001)
        self.state = MovingTensorState.derive(
            root_key=TENSOR_KEY,
            trusted_anchor=self.anchor1,
            tensor_sequence=1,
            genesis_epoch=8,
        )

    def test_deterministic_anchor_bound_derivation_and_changed_history_diverges(self) -> None:
        replay = MovingTensorState.derive(
            root_key=TENSOR_KEY,
            trusted_anchor=self.anchor1,
            tensor_sequence=1,
            genesis_epoch=8,
        )
        self.assertEqual(replay, self.state)
        changed_anchor = synthetic_anchor(2, 8_000_002)
        changed = MovingTensorState.derive(
            root_key=TENSOR_KEY,
            trusted_anchor=changed_anchor,
            tensor_sequence=2,
            genesis_epoch=8,
            prior_tensor_root_hash216=self.state.tensor_root_hash216,
        )
        self.assertNotEqual(changed.tensor_root_hash216, self.state.tensor_root_hash216)
        self.assertNotEqual(changed.coordinate_map, self.state.coordinate_map)
        self.assertNotEqual(changed.closure_proof, self.state.closure_proof)

    def test_lo_shu_sudoku_fibonacci_and_hash72_invariants(self) -> None:
        self.state.validate_structure()
        self.assertEqual(
            {sum(row) for row in self.state.lo_shu_grid}, {15}
        )
        self.assertEqual(
            {sum(self.state.lo_shu_grid[row][column] for row in range(3))
             for column in range(3)},
            {15},
        )
        symbols = set(range(1, 10))
        for row in self.state.sudoku.grid:
            self.assertEqual(set(row), symbols)
        self.assertEqual(len(self.state.fibonacci_phase), 11)
        self.assertEqual(len(self.state.receipt_hash72), 72)
        self.assertTrue(
            self.state.validate_with_key(
                root_key=TENSOR_KEY, trusted_anchor=self.anchor1
            )
        )

    def test_coordinate_mapping_round_trips_vm_and_full_hydration_domains(self) -> None:
        vm_samples = (0, 1, 63, 64, 5_183, 5_184, VM5184_G243_DOMAIN - 1)
        for index in vm_samples:
            mapped = self.state.coordinate_map.map_index(index, VM5184_G243_DOMAIN)
            self.assertEqual(
                self.state.coordinate_map.unmap_index(
                    mapped, VM5184_G243_DOMAIN
                ),
                index,
            )
        full_samples = (
            0,
            1,
            VM5184_G243_DOMAIN - 1,
            VM5184_G243_DOMAIN,
            FULL_HYDRATION_DOMAIN // 2,
            FULL_HYDRATION_DOMAIN - 1,
        )
        for index in full_samples:
            mapped = self.state.coordinate_map.map_index(
                index, FULL_HYDRATION_DOMAIN
            )
            self.assertEqual(
                self.state.coordinate_map.unmap_index(
                    mapped, FULL_HYDRATION_DOMAIN
                ),
                index,
            )

    def test_exact_5184_materialized_closure_and_large_domain_bijection_proof(self) -> None:
        proof_5184 = TensorClosureProof.derive(b"c" * 32, VM5184_STATES)
        materialized = proof_5184.materialized_check()
        self.assertEqual(materialized["visited_count"], VM5184_STATES)
        self.assertEqual(materialized["unique_count"], VM5184_STATES)
        self.assertTrue(materialized["wrap_valid"])
        self.state.closure_proof.validate()
        self.assertEqual(self.state.closure_proof.gcd, 1)
        self.assertEqual(
            self.state.closure_proof.closing_successor,
            self.state.closure_proof.first_cell,
        )
        for position in (0, 1, 2, 81, 5_184, FULL_HYDRATION_DOMAIN - 1):
            cell = self.state.closure_proof.cell(position)
            self.assertEqual(self.state.closure_proof.position(cell), position)

    def test_tensor_path_and_physical_coordinate_are_jointly_reversible(self) -> None:
        for position in (0, 1, 2, 9_999, FULL_HYDRATION_DOMAIN - 1):
            physical = self.state.physical_cell(position)
            self.assertEqual(
                self.state.logical_position_from_physical(physical), position
            )

    def test_floating_geometry_is_derived_bit_committed_and_noncanonical(self) -> None:
        assert_no_float(self, self.state.to_mapping())
        projection = self.state.floating_projection()
        projection.validate()
        self.assertEqual(projection.source_tensor_root_hash216, self.state.tensor_root_hash216)
        self.assertEqual(projection.format, "IEEE-754-binary64")
        self.assertTrue(all(len(item) == 16 for item in projection.binary64_hex))
        altered = replace(
            projection,
            binary64_hex=("0000000000000000", *projection.binary64_hex[1:]),
        )
        with self.assertRaisesRegex(Pass213TensorBoundaryError, "FLOAT_BITS"):
            altered.validate()

    def test_wrong_key_anchor_or_canonical_state_tampering_fails_closed(self) -> None:
        with self.assertRaisesRegex(Pass213TensorError, "KEYED_REPLAY"):
            self.state.validate_with_key(
                root_key=b"z" * 32, trusted_anchor=self.anchor1
            )
        altered_anchor = replace(
            self.anchor1, anchor_root_hash216="0" * 64
        )
        with self.assertRaisesRegex(Pass213TensorBoundaryError, "ANCHOR_ROOT"):
            TensorAnchorBinding.from_trusted_anchor(altered_anchor)
        mapping = self.state.to_mapping()
        phase = list(mapping["fibonacci_phase"])
        phase[0] = (int(phase[0]) + 1) % 9
        mapping["fibonacci_phase"] = phase
        with self.assertRaises(Pass213TensorError):
            MovingTensorState.from_mapping(mapping)

    def test_persistent_chain_reopens_and_replays_with_root_key(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pass213-tensor-store-") as directory:
            database = Path(directory) / "tensor.sqlite3"
            store = MovingTensorStore(database_path=database, root_key=TENSOR_KEY)
            first = store.append(
                trusted_anchor=self.anchor1,
                genesis_epoch=8,
            )
            second_anchor = synthetic_anchor(2, 8_000_002)
            second = store.append(
                trusted_anchor=second_anchor,
                genesis_epoch=8,
            )
            self.assertEqual(
                second.prior_tensor_root_hash216, first.tensor_root_hash216
            )
            self.assertTrue(store.verify_chain())
            head = store.current_head()
            store.close()

            reopened = MovingTensorStore(
                database_path=database, root_key=TENSOR_KEY
            )
            try:
                self.assertTrue(reopened.verify_chain())
                self.assertEqual(reopened.current_head(), head)
                self.assertEqual(reopened.get(2), second)
            finally:
                reopened.close()

    def test_persistent_chain_rejects_boundary_regression_wrong_key_and_db_tamper(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pass213-tensor-negative-") as directory:
            database = Path(directory) / "tensor.sqlite3"
            store = MovingTensorStore(database_path=database, root_key=TENSOR_KEY)
            store.append(trusted_anchor=self.anchor1, genesis_epoch=8)
            with self.assertRaisesRegex(Pass213TensorError, "TIMESTAMP_REGRESSION"):
                store.append(
                    trusted_anchor=synthetic_anchor(2, 7_999_999),
                    genesis_epoch=8,
                )
            store.close()
            with self.assertRaisesRegex(Pass213TensorError, "KEYED_REPLAY"):
                MovingTensorStore(database_path=database, root_key=b"x" * 32)

            connection = sqlite3.connect(database)
            state_json = connection.execute(
                "SELECT state_json FROM moving_tensor_states WHERE tensor_sequence=1"
            ).fetchone()[0]
            value = json.loads(state_json)
            value["lo_shu_transform_index"] = (
                int(value["lo_shu_transform_index"]) + 1
            ) % 8
            connection.execute(
                "UPDATE moving_tensor_states SET state_json=? WHERE tensor_sequence=1",
                (json.dumps(value, sort_keys=True, separators=(",", ":")),),
            )
            connection.commit()
            connection.close()
            with self.assertRaises(Pass213TensorError):
                MovingTensorStore(database_path=database, root_key=TENSOR_KEY)


if __name__ == "__main__":
    unittest.main()

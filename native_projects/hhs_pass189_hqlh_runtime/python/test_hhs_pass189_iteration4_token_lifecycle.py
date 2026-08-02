import hashlib
import tempfile
import unittest
from pathlib import Path

from hhs_pass189_iteration3 import hash72
from hhs_pass189_iteration4 import DriverProvenanceAuthority, sign_manifest
from hhs_pass189_iteration4_token_lifecycle import DriverProvenanceLifecycleAuthority


class Iteration4TokenLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.key = b"iteration4-lifecycle-key"
        self.authority = DriverProvenanceLifecycleAuthority(
            self.root / "authority.sqlite3", quarantine_directory=self.root / "quarantine"
        )
        self.authority.register_trust_root("operator", self.key, created_ns=1)
        payload = b"lifecycle-driver"
        self.manifest = {
            "driver_id": "lifecycle-loop", "version": "1.0.0", "driver_kind": "LOOPBACK",
            "entrypoint": "driver/main.py", "signer_id": "operator",
            "payload_sha256": hashlib.sha256(payload).hexdigest(), "operations": ["WRITE"],
            "capabilities": ["software-test"], "units": ["volt"], "device_ids": ["test-device"],
            "minimum": 0, "maximum": 5, "watchdog_timeout_ms": 1000,
            "required_interlocks": ["WATCHDOG"], "created_ns": 2,
        }
        self.authority.ingest_package("package", self.manifest, payload, sign_manifest(self.manifest, self.key), self.key)
        tests = {name: True for name in (
            "manifest_identity", "payload_digest", "path_confinement", "capability_scope",
            "range_enforcement", "watchdog_fail_closed", "anti_replay", "rollback_ready",
        )}
        self.authority.record_conformance({
            "run_id": "run", "package_id": "package", "evidence_class": "SOFTWARE_FIXTURE",
            "tests": tests, "trace_hash72": hash72({"run": 1}), "physical_measurement": False, "created_ns": 3,
        })

    def tearDown(self):
        self.authority.close()
        self.temp.cleanup()

    def request(self, **overrides):
        request = {
            "promotion_id": "promotion", "package_id": "package",
            "approver_a_hash72": "a" * 72, "approver_b_hash72": "b" * 72,
            "issue_witness_hash72": "c" * 72, "issued_ns": 10, "expires_ns": 20,
        }
        request.update(overrides)
        return request

    def test_issue_witness_is_required_and_bound(self):
        with self.assertRaises(ValueError):
            self.authority.promote(self.request(issue_witness_hash72=""))
        token = self.authority.promote(self.request())
        self.assertEqual(token["issue_witness_hash72"], "c" * 72)
        self.assertEqual(token["schema"], "HHS_PASS_189_ITERATION_4_ADMISSION_TOKEN_V2")

    def test_token_validation_and_expiry(self):
        token = self.authority.promote(self.request())
        valid = self.authority.validate_promotion_token(token["token_hash72"], at_ns=15)
        self.assertTrue(valid["valid"])
        self.assertTrue(valid["executable"])
        expired = self.authority.validate_promotion_token(token["token_hash72"], at_ns=20)
        self.assertFalse(expired["valid"])
        self.assertIn("PROMOTION_EXPIRED", expired["reasons"])
        self.assertFalse(expired["executable"])
        self.assertEqual(self.authority.status()["active_drivers"], 0)

    def test_unknown_token_is_fail_closed(self):
        result = self.authority.validate_promotion_token("f" * 72, at_ns=15)
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "UNKNOWN_TOKEN")

    def test_schema_migration_from_pre_lifecycle_database(self):
        other = self.root / "migration.sqlite3"
        base = DriverProvenanceAuthority(other, quarantine_directory=self.root / "migration-q")
        base.close()
        migrated = DriverProvenanceLifecycleAuthority(other, quarantine_directory=self.root / "migration-q")
        try:
            columns = {row[1] for row in migrated._connection.execute("PRAGMA table_info(promotions)")}
            self.assertIn("issue_witness_hash72", columns)
        finally:
            migrated.close()


if __name__ == "__main__":
    unittest.main()

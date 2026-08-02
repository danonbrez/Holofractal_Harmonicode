import hashlib
import tempfile
import threading
import unittest
from pathlib import Path

from hhs_pass189_iteration3 import hash72
from hhs_pass189_iteration4 import DriverProvenanceAuthority, sign_manifest


class Iteration4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.authority = DriverProvenanceAuthority(self.root / "authority.sqlite3", quarantine_directory=self.root / "quarantine")
        self.key = b"operator-test-key-iteration4"
        self.authority.register_trust_root("operator-a", self.key, created_ns=1)

    def tearDown(self):
        self.authority.close()
        self.temp.cleanup()

    def manifest(self, *, driver_id="loop", version="1.0.0", kind="LOOPBACK", payload=b"driver-bytes"):
        return {
            "driver_id": driver_id,
            "version": version,
            "driver_kind": kind,
            "entrypoint": "drivers/main.py",
            "signer_id": "operator-a",
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "operations": ["WRITE"],
            "capabilities": ["software-test"],
            "units": ["volt"],
            "device_ids": ["test-device"],
            "minimum": 0,
            "maximum": 5,
            "watchdog_timeout_ms": 1000,
            "required_interlocks": ["WATCHDOG"],
            "created_ns": 2,
        }

    def ingest(self, package_id="pkg-loop", manifest=None, payload=b"driver-bytes"):
        manifest = manifest or self.manifest(payload=payload)
        signature = sign_manifest(manifest, self.key)
        return self.authority.ingest_package(package_id, manifest, payload, signature, self.key)

    def conformance(self, package_id="pkg-loop", run_id="run-1", evidence="SOFTWARE_FIXTURE"):
        required = [
            "manifest_identity", "payload_digest", "path_confinement", "capability_scope",
            "range_enforcement", "watchdog_fail_closed", "anti_replay", "rollback_ready",
        ]
        if evidence == "HARDWARE_IN_LOOP":
            required += ["physical_interlock", "measured_return_trace", "emergency_stop"]
        return self.authority.record_conformance({
            "run_id": run_id,
            "package_id": package_id,
            "evidence_class": evidence,
            "tests": {name: True for name in required},
            "trace_hash72": hash72({"run": run_id}),
            "physical_measurement": evidence == "HARDWARE_IN_LOOP",
            "created_ns": 3,
        })

    def test_trust_root_idempotence_and_mismatch(self):
        same = self.authority.register_trust_root("operator-a", self.key, created_ns=1)
        self.assertEqual(same["key_sha256"], hashlib.sha256(self.key).hexdigest())
        with self.assertRaises(ValueError):
            self.authority.register_trust_root("operator-a", b"different", created_ns=1)

    def test_manifest_signature_and_payload_binding(self):
        package = self.ingest()
        self.assertEqual(package["status"], "QUARANTINED")
        self.assertTrue(Path(package["quarantine_path"]).is_file())
        with self.assertRaises(ValueError):
            self.authority.ingest_package("bad", self.manifest(), b"tampered", "0" * 64, self.key)

    def test_entrypoint_confinement(self):
        manifest = self.manifest()
        manifest["entrypoint"] = "../../escape.py"
        with self.assertRaises(ValueError):
            sign_manifest(manifest, self.key)

    def test_software_conformance_and_dual_promotion(self):
        self.ingest()
        self.assertEqual(self.conformance()["status"], "PASS")
        token = self.authority.promote({
            "promotion_id": "prom-1", "package_id": "pkg-loop",
            "approver_a_hash72": "a" * 72, "approver_b_hash72": "b" * 72,
            "issued_ns": 10, "expires_ns": 20,
        })
        self.assertEqual(token["promotion_class"], "SOFTWARE_TEST_EXECUTABLE")
        self.assertTrue(token["executable"])
        self.assertFalse(token["real_hardware_dispatch_authorized"])

    def test_duplicate_approver_rejected(self):
        self.ingest(); self.conformance()
        with self.assertRaises(ValueError):
            self.authority.promote({
                "promotion_id": "prom-1", "package_id": "pkg-loop",
                "approver_a_hash72": "a" * 72, "approver_b_hash72": "a" * 72,
                "issued_ns": 10, "expires_ns": 20,
            })

    def test_real_driver_requires_hil_and_remains_nonexecuting(self):
        payload = b"gpio-driver"
        manifest = self.manifest(driver_id="gpio", kind="GPIO", payload=payload)
        self.ingest("pkg-gpio", manifest, payload)
        self.conformance("pkg-gpio", "run-soft", "SOFTWARE_FIXTURE")
        with self.assertRaises(ValueError):
            self.authority.promote({
                "promotion_id": "prom-gpio", "package_id": "pkg-gpio",
                "approver_a_hash72": "a" * 72, "approver_b_hash72": "b" * 72,
                "issued_ns": 10, "expires_ns": 20,
            })
        self.conformance("pkg-gpio", "run-hil", "HARDWARE_IN_LOOP")
        token = self.authority.promote({
            "promotion_id": "prom-gpio", "package_id": "pkg-gpio",
            "approver_a_hash72": "a" * 72, "approver_b_hash72": "b" * 72,
            "issued_ns": 10, "expires_ns": 20,
        })
        self.assertEqual(token["promotion_class"], "HARDWARE_CANDIDATE_NONEXECUTABLE")
        self.assertFalse(token["executable"])
        self.assertFalse(token["real_hardware_dispatch_authorized"])

    def test_hil_cannot_be_faked_as_software(self):
        self.ingest()
        with self.assertRaises(ValueError):
            self.authority.record_conformance({
                "run_id": "bad", "package_id": "pkg-loop", "evidence_class": "HARDWARE_IN_LOOP",
                "tests": {}, "trace_hash72": "a" * 72, "physical_measurement": False, "created_ns": 3,
            })

    def test_revoke_trust_root_cascades(self):
        self.ingest(); self.conformance()
        self.authority.promote({
            "promotion_id": "prom-1", "package_id": "pkg-loop",
            "approver_a_hash72": "a" * 72, "approver_b_hash72": "b" * 72,
            "issued_ns": 10, "expires_ns": 20,
        })
        result = self.authority.revoke_trust_root("operator-a", created_ns=30)
        self.assertIn("pkg-loop", result["packages_revoked"])
        self.assertEqual(self.authority.status()["active_drivers"], 0)

    def test_rollback(self):
        old_payload = b"old"
        old_manifest = self.manifest(driver_id="loop", version="0.9.0", payload=old_payload)
        self.ingest("pkg-old", old_manifest, old_payload)
        self.conformance("pkg-old", "run-old")
        new_payload = b"new"
        new_manifest = self.manifest(driver_id="loop", version="1.0.0", payload=new_payload)
        self.ingest("pkg-new", new_manifest, new_payload)
        self.conformance("pkg-new", "run-new")
        self.authority.promote({
            "promotion_id": "prom-new", "package_id": "pkg-new", "rollback_package_id": "pkg-old",
            "approver_a_hash72": "a" * 72, "approver_b_hash72": "b" * 72,
            "issued_ns": 10, "expires_ns": 20,
        })
        result = self.authority.rollback("prom-new", created_ns=15)
        self.assertEqual(result["to_package_id"], "pkg-old")

    def test_concurrent_duplicate_package_is_idempotent(self):
        manifest = self.manifest()
        signature = sign_manifest(manifest, self.key)
        errors = []
        def worker():
            try:
                self.authority.ingest_package("pkg-loop", manifest, b"driver-bytes", signature, self.key)
            except Exception as exc:
                errors.append(exc)
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads: thread.start()
        for thread in threads: thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(self.authority.status()["packages"], 1)

    def test_chain_checkpoint_and_recovery(self):
        self.ingest(); self.conformance()
        chain = self.authority.verify_chain()
        self.assertTrue(chain["valid"])
        checkpoint = self.authority.checkpoint(self.root / "checkpoint.sqlite3", "cp-1", created_ns=9)
        verification = self.authority.verify_checkpoint(
            checkpoint["path"], checkpoint["digest_sha256"], checkpoint["captured_sequence"], checkpoint["captured_root_hash72"]
        )
        self.assertTrue(verification["valid"])
        recovered = DriverProvenanceAuthority.recover(
            checkpoint["path"], self.root / "recovered.sqlite3", checkpoint["digest_sha256"],
            checkpoint["captured_sequence"], checkpoint["captured_root_hash72"],
        )
        try:
            self.assertTrue(recovered.verify_chain()["valid"])
        finally:
            recovered.close()

    def test_status_preserves_honest_boundary(self):
        status = self.authority.status()
        self.assertFalse(status["real_hardware_dispatch_authorized"])
        self.assertFalse(status["vercel_required"])
        self.assertEqual(status["deployment_authority"], "DIGITALOCEAN_SELF_HOSTED")


if __name__ == "__main__":
    unittest.main()

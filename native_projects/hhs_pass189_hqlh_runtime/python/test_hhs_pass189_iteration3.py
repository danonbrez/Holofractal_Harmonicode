import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from hhs_pass189_iteration3 import DeviceAuthority, ZERO_HASH72, exact_fraction


class Pass189Iteration3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.authority = DeviceAuthority(self.root / "authority.sqlite3", state_directory=self.root)

    def tearDown(self):
        self.authority.close()
        self.temp.cleanup()

    def adapter(self, adapter_id="loop", driver="LOOPBACK"):
        return self.authority.register_adapter({
            "adapter_id": adapter_id,
            "device_id": f"device-{adapter_id}",
            "driver_kind": driver,
            "unit": "volt",
            "minimum": 0,
            "maximum": 5,
            "allowed_operations": ["SET", "HOLD"],
            "watchdog_timeout_ms": 100,
            "max_commands_per_lease": 4,
            "software_attested": True,
            "sink_directory": "sinks",
            "created_ns": 10,
        })

    def lease(self, adapter_id="loop", lease_id="lease-1", issued=1000, expires=10_000_000_000):
        return self.authority.issue_lease({
            "lease_id": lease_id,
            "adapter_id": adapter_id,
            "issued_ns": issued,
            "expires_ns": expires,
            "max_commands": 4,
            "allowed_operations": ["SET"],
            "arm_token_hash72": "a" * 72,
        })

    @staticmethod
    def candidate():
        return {
            "candidate_hash72": "b" * 72,
            "profile_id": "measured-profile-1",
            "physical_output_authorized": True,
            "dispatch_class": "CANDIDATE_ONLY_NO_DEVICE_DRIVER",
            "candidate_receipt_index": 7,
        }

    def prepare(self, command_id="cmd-1", sequence=1, issued=2000, lease_id="lease-1"):
        return self.authority.prepare_command({
            "command_id": command_id,
            "lease_id": lease_id,
            "sequence": sequence,
            "operation": "SET",
            "value": {"numerator": 5, "denominator": 2},
            "unit": "volt",
            "issued_ns": issued,
            "arm_token_hash72": "a" * 72,
            "candidate": self.candidate(),
        })

    def test_float_ingress_and_forbidden_driver_rejected(self):
        with self.assertRaises(ValueError):
            exact_fraction(0.5)
        with self.assertRaises(ValueError):
            self.authority.register_adapter({
                "adapter_id": "gpio", "device_id": "gpio0", "driver_kind": "GPIO", "unit": "volt",
                "minimum": 0, "maximum": 5, "allowed_operations": ["SET"],
                "watchdog_timeout_ms": 100, "max_commands_per_lease": 1, "software_attested": True,
            })

    def test_adapter_idempotence_and_payload_sensitivity(self):
        first = self.adapter()
        second = self.adapter()
        self.assertEqual(first["adapter_hash72"], second["adapter_hash72"])
        with self.assertRaises(ValueError):
            self.authority.register_adapter({
                "adapter_id": "loop", "device_id": "changed", "driver_kind": "LOOPBACK", "unit": "volt",
                "minimum": 0, "maximum": 5, "allowed_operations": ["SET"],
                "watchdog_timeout_ms": 100, "max_commands_per_lease": 1, "software_attested": True,
            })

    def test_lease_bounds_and_arm_identity(self):
        self.adapter()
        lease = self.lease()
        self.assertEqual(lease["status"], "ACTIVE")
        with self.assertRaises(ValueError):
            self.authority.prepare_command({
                "command_id": "bad-arm", "lease_id": "lease-1", "sequence": 1, "operation": "SET",
                "value": 1, "unit": "volt", "issued_ns": 2000,
                "arm_token_hash72": "c" * 72, "candidate": self.candidate(),
            })

    def test_candidate_gate_rejects_unadmitted_output(self):
        self.adapter(); self.lease()
        candidate = self.candidate(); candidate["physical_output_authorized"] = False
        with self.assertRaises(ValueError):
            self.authority.prepare_command({
                "command_id": "bad-candidate", "lease_id": "lease-1", "sequence": 1, "operation": "SET",
                "value": 1, "unit": "volt", "issued_ns": 2000,
                "arm_token_hash72": "a" * 72, "candidate": candidate,
            })

    def test_loopback_execution_trace_and_event_chain(self):
        self.adapter(); self.lease(); prepared = self.prepare()
        trace = self.authority.execute_command("cmd-1", execution_ns=3000)
        self.assertEqual(trace["dispatch_status"], "SOFTWARE_TEST_DRIVER_ONLY")
        self.assertEqual(trace["requested"], trace["observed"])
        self.assertEqual(trace["residual"], {"numerator": 0, "denominator": 1})
        self.assertFalse(trace["hardware_measurement"])
        self.assertEqual(self.authority.get_command("cmd-1")["status"], "EXECUTED")
        self.assertTrue(self.authority.verify_event_chain()["valid"])
        self.assertEqual(len(prepared["command_hash72"]), 72)

    def test_file_sink_is_sandboxed_and_idempotent_per_command(self):
        self.adapter("sink", "FILE_SINK")
        self.lease("sink", "lease-sink")
        self.prepare("sink-cmd", 1, lease_id="lease-sink")
        result = self.authority.execute_command("sink-cmd", execution_ns=3000)
        target = self.root / "sinks" / "sink-cmd.json"
        self.assertTrue(target.is_file())
        payload = json.loads(target.read_text())
        self.assertEqual(payload["trace_hash72"], result["trace_hash72"])
        with self.assertRaises(ValueError):
            self.authority.execute_command("sink-cmd", execution_ns=4000)

    def test_watchdog_expiry_persists(self):
        self.adapter(); self.lease(); self.prepare(issued=2000)
        result = self.authority.execute_command("cmd-1", execution_ns=2000 + 101_000_000)
        self.assertFalse(result["executed"])
        self.assertEqual(self.authority.get_command("cmd-1")["status"], "EXPIRED")
        self.assertTrue(self.authority.verify_event_chain()["valid"])

    def test_revoke_and_disable_fail_closed(self):
        self.adapter(); self.lease(); self.prepare()
        self.authority.revoke_lease("lease-1", created_ns=2500)
        with self.assertRaises(ValueError):
            self.authority.execute_command("cmd-1", execution_ns=3000)
        self.authority.set_adapter_enabled("loop", False, created_ns=3500)
        self.assertFalse(self.authority.get_adapter("loop")["enabled"])

    def test_sequence_anti_replay_under_concurrency(self):
        self.adapter(); self.lease()
        def submit(command_id):
            try:
                self.prepare(command_id, sequence=1)
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(submit, ["cmd-a", "cmd-b"]))
        self.assertEqual(sorted(results), [False, True])
        self.assertTrue(self.authority.verify_event_chain()["valid"])

    def test_checkpoint_verification_and_recovery(self):
        self.adapter(); self.lease(); self.prepare(); self.authority.execute_command("cmd-1", execution_ns=3000)
        checkpoint_path = self.root / "checkpoint.sqlite3"
        checkpoint = self.authority.checkpoint(checkpoint_path, checkpoint_id="cp-1", created_ns=4000)
        verified = DeviceAuthority.verify_checkpoint(
            checkpoint_path, checkpoint["digest_sha256"], checkpoint["captured_sequence"], checkpoint["captured_root_hash72"]
        )
        self.assertTrue(verified["valid"])
        recovered_path = self.root / "recovered.sqlite3"
        recovered = DeviceAuthority.recover_checkpoint(
            checkpoint_path, recovered_path,
            digest_sha256=checkpoint["digest_sha256"],
            captured_sequence=checkpoint["captured_sequence"],
            captured_root_hash72=checkpoint["captured_root_hash72"],
        )
        self.assertTrue(recovered["recovered"])
        restored = DeviceAuthority(recovered_path, state_directory=self.root / "restored-state")
        try:
            self.assertTrue(restored.verify_event_chain()["valid"])
        finally:
            restored.close()

    def test_status_preserves_nonphysical_boundary(self):
        status = self.authority.status()
        self.assertFalse(status["actual_physical_dispatch"])
        self.assertFalse(status["vercel_required"])
        self.assertEqual(status["root_hash72"], ZERO_HASH72)
        self.assertEqual(status["supported_drivers"], ["LOOPBACK", "FILE_SINK"])


if __name__ == "__main__":
    unittest.main()

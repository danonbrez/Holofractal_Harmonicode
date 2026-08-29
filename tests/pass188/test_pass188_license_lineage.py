from __future__ import annotations

import json
import sqlite3
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

from hhs_runtime.pass188.license_lineage import (
    COMPLETION_CLASSIFICATION,
    LicenseLineageAuthority,
    execute_operation,
)
from hhs_runtime.pass188.license_server import Handler

AUTH_A = "1" * 72
AUTH_B = "2" * 72
AUTH_C = "3" * 72


class Pass188LicenseAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "authority.sqlite3"
        self.a = LicenseLineageAuthority(self.db)

    def tearDown(self) -> None:
        self.a.close()
        self.temp.cleanup()

    def _content_license_v1(self) -> tuple[str, str]:
        content = self.a.content_create(
            logical_content_id="content.alpha",
            content_hash="sha256:alpha-v1",
            authority_hash72=AUTH_A,
        )
        cv1 = content["result"]["content_version_id"]
        license_result = self.a.license_create(
            logical_license_id="license.alpha",
            controlled_content_ids=["content.alpha"],
            rights=["derive", "egress", "publish", "read", "revoke_me", "stream"],
            obligations={
                "attribution": "Alpha Author",
                "license_family": "A",
                "incompatible_with": [],
            },
            legacy_policy="LEGACY_BOUND",
            controller="alice",
            authority_hash72=AUTH_A,
            revocable_rights=["revoke_me"],
            compatibility_floor_rights=["read"],
            royalty=[1, 10],
            external_anchor_status="UNAVAILABLE",
        )
        return cv1, license_result["result"]["license_version_id"]

    def test_full_contract_acceptance_scenarios(self) -> None:
        cv1, lv1 = self._content_license_v1()

        # 1. Two projects are admitted under exact content/license v1.
        b1 = self.a.binding_create(
            binding_id="binding.upgrade",
            project_id="project.one",
            principal="alice",
            content_version_id=cv1,
            license_version_id=lv1,
            operation="read",
            target_egress="internal",
            authority_hash72=AUTH_A,
        )
        bkeep = self.a.binding_create(
            binding_id="binding.keep",
            project_id="project.keep",
            principal="alice",
            content_version_id=cv1,
            license_version_id=lv1,
            operation="read",
            target_egress="internal",
            authority_hash72=AUTH_A,
        )
        self.assertEqual(b1["result"]["decision"]["decision"], "ALLOW")

        # Pass 187 graph closure used later by explicit upgrade.
        self.a.graph_edge_create(
            project_id="project.one",
            source_node="binding.upgrade",
            target_node="node.render",
            authority_hash72=AUTH_A,
        )
        self.a.graph_edge_create(
            project_id="project.one",
            source_node="node.render",
            target_node="node.export",
            authority_hash72=AUTH_A,
        )

        # 2. Publish license v2; legacy binding remains byte-for-byte on v1.
        v2 = self.a.license_update(
            parent_license_version_id=lv1,
            delta={
                "rights": ["derive", "egress", "publish", "read", "revoke_me", "stream"],
                "obligations": {
                    "attribution": "Alpha Author v2",
                    "license_family": "A",
                    "incompatible_with": [],
                },
            },
            authority_hash72=AUTH_A,
        )
        lv2 = v2["result"]["license_version_id"]
        self.assertEqual(self.a.binding_inspect("binding.upgrade")["license_version_id"], lv1)
        self.assertEqual(
            self.a.license_decision(
                logical_license_id="license.alpha",
                logical_content_id="content.alpha",
                principal="alice",
                operation="read",
                target_egress="internal",
                binding_id="binding.upgrade",
            )["license_version_id"],
            lv1,
        )

        # 3. New project admits under current v2.
        self.a.binding_create(
            binding_id="binding.new",
            project_id="project.new",
            principal="alice",
            content_version_id=cv1,
            license_version_id=lv2,
            operation="publish",
            target_egress="archive",
            authority_hash72=AUTH_A,
        )
        self.assertEqual(self.a.binding_inspect("binding.new")["license_version_id"], lv2)

        # 4. Existing project explicitly opts into v2; only graph closure is affected.
        upgrade_license = self.a.binding_upgrade(
            binding_id="binding.upgrade",
            new_content_version_id=None,
            new_license_version_id=lv2,
            authority_hash72=AUTH_A,
            operation="read",
            target_egress="internal",
        )
        self.assertEqual(
            upgrade_license["result"]["affected_closure"],
            ["binding.upgrade", "node.export", "node.render"],
        )
        self.assertEqual(self.a.binding_inspect("binding.keep")["license_version_id"], lv1)

        # 5. New content version does not alter prior content.
        c2 = self.a.content_version(
            logical_content_id="content.alpha",
            content_hash="sha256:alpha-v2",
            authority_hash72=AUTH_A,
        )
        cv2 = c2["result"]["content_version_id"]
        compared = self.a.content_compare(cv1, cv2)
        self.assertTrue(compared["same_logical_content"])
        self.assertFalse(compared["same_content_hash"])

        # 6. One project stays on old content while another explicitly upgrades.
        self.a.binding_upgrade(
            binding_id="binding.upgrade",
            new_content_version_id=cv2,
            new_license_version_id=lv2,
            authority_hash72=AUTH_A,
            operation="read",
            target_egress="internal",
        )
        self.assertEqual(self.a.binding_inspect("binding.keep")["content_version_id"], cv1)
        self.assertEqual(self.a.binding_inspect("binding.upgrade")["content_version_id"], cv2)

        # 7. Territory/modality fork wins only for matching request.
        branch = self.a.license_branch(
            parent_license_version_id=lv2,
            delta={"territory": "US", "modality": "video"},
            authority_hash72=AUTH_A,
        )
        lv_branch = branch["result"]["license_version_id"]
        decision_branch = self.a.license_decision(
            logical_license_id="license.alpha",
            logical_content_id="content.alpha",
            principal="alice",
            operation="stream",
            target_egress="public",
            territory="US",
            modality="video",
        )
        self.assertEqual(decision_branch["license_version_id"], lv_branch)

        # 8. Transfer preserves prior operation receipts and controller history.
        before_transfer_ops = list(
            self.a._connection.execute(
                "SELECT operation_id,receipt_hash72 FROM admitted_operations ORDER BY operation_id"
            )
        )
        ownership = self.a.ownership_inspect("license.alpha")
        transferred = self.a.ownership_transfer(
            logical_license_id="license.alpha",
            current_controller="alice",
            new_controller="bob",
            expected_root_hash72=ownership["root_hash72"],
            authority_hash72=AUTH_B,
        )
        self.assertEqual(self.a.ownership_inspect("license.alpha")["controller"], "bob")
        after_transfer_ops = list(
            self.a._connection.execute(
                "SELECT operation_id,receipt_hash72 FROM admitted_operations ORDER BY operation_id"
            )
        )
        self.assertEqual([(r[0], r[1]) for r in before_transfer_ops], [(r[0], r[1]) for r in after_transfer_ops])
        self.assertNotEqual(transferred["result"]["ownership_root_hash72"], ownership["root_hash72"])

        # Delegated operation authority is bounded to explicit rights.
        self.a.delegation_create(
            delegation_id="delegation.reader",
            logical_license_id="license.alpha",
            controller="bob",
            principal="reader-agent",
            rights=["read"],
            authority_hash72=AUTH_B,
        )
        delegated = self.a.license_decision(
            logical_license_id="license.alpha",
            logical_content_id="content.alpha",
            principal="reader-agent",
            operation="read",
            target_egress="internal",
        )
        self.assertEqual(delegated["decision"], "ALLOW")
        self.assertTrue(delegated["delegated"])

        # 9. Narrow revocable capability stops future use, not historical evidence.
        rev_binding = self.a.binding_create(
            binding_id="binding.revocable",
            project_id="project.revocable",
            principal="bob",
            content_version_id=cv2,
            license_version_id=lv2,
            operation="revoke_me",
            target_egress="internal",
            authority_hash72=AUTH_B,
        )
        historical_receipt = rev_binding["result"]["operation_id"]
        self.a.revoke(
            revocation_id="revocation.one",
            license_version_id=lv2,
            principal="bob",
            operation="revoke_me",
            authority_hash72=AUTH_B,
        )
        denied = self.a.license_decision(
            logical_license_id="license.alpha",
            logical_content_id="content.alpha",
            principal="bob",
            operation="revoke_me",
            target_egress="internal",
        )
        self.assertEqual(denied["reason"], "REVOCABLE_CAPABILITY_REVOKED")
        self.assertIsNotNone(
            self.a._connection.execute(
                "SELECT 1 FROM admitted_operations WHERE operation_id=?", (historical_receipt,)
            ).fetchone()
        )

        # 10. A non-revocable historical right cannot be retroactively revoked.
        with self.assertRaises(PermissionError):
            self.a.revoke(
                revocation_id="revocation.illegal",
                license_version_id=lv2,
                principal="bob",
                operation="read",
                authority_hash72=AUTH_B,
            )

        # 11. Nested incompatible licenses fail egress compilation.
        content_b = self.a.content_create(
            logical_content_id="content.beta",
            content_hash="sha256:beta-v1",
            authority_hash72=AUTH_C,
        )["result"]["content_version_id"]
        license_b = self.a.license_create(
            logical_license_id="license.beta",
            controlled_content_ids=["content.beta"],
            rights=["read"],
            obligations={
                "attribution": "Beta",
                "license_family": "B",
                "incompatible_with": ["A"],
            },
            legacy_policy="LEGACY_BOUND",
            controller="carol",
            authority_hash72=AUTH_C,
            royalty=[1, 20],
        )["result"]["license_version_id"]
        self.a.binding_create(
            binding_id="binding.beta",
            project_id="project.egress",
            principal="carol",
            content_version_id=content_b,
            license_version_id=license_b,
            operation="read",
            target_egress="bundle",
            authority_hash72=AUTH_C,
        )
        incompatible = self.a.compile_egress(["binding.new", "binding.beta"])
        self.assertFalse(incompatible["compatible"])

        # 12. Compatible royalty + attribution package is exact rational arithmetic.
        content_c = self.a.content_create(
            logical_content_id="content.gamma",
            content_hash="sha256:gamma-v1",
            authority_hash72=AUTH_C,
        )["result"]["content_version_id"]
        license_c = self.a.license_create(
            logical_license_id="license.gamma",
            controlled_content_ids=["content.gamma"],
            rights=["read"],
            obligations={
                "attribution": "Gamma",
                "license_family": "C",
                "incompatible_with": [],
            },
            legacy_policy="LEGACY_BOUND",
            controller="carol",
            authority_hash72=AUTH_C,
            royalty=[1, 20],
        )["result"]["license_version_id"]
        self.a.binding_create(
            binding_id="binding.gamma",
            project_id="project.egress",
            principal="carol",
            content_version_id=content_c,
            license_version_id=license_c,
            operation="read",
            target_egress="bundle",
            authority_hash72=AUTH_C,
        )
        compatible = self.a.compile_egress(["binding.new", "binding.gamma"])
        self.assertTrue(compatible["compatible"])
        self.assertEqual(compatible["royalties"]["aggregate_royalty"], [3, 20])
        self.assertEqual(
            compatible["obligations"]["obligations"][0]["obligations"]["attribution"],
            "Alpha Author v2",
        )

        # 13a. Stale ownership root fails closed.
        with self.assertRaises(ValueError):
            self.a.ownership_transfer(
                logical_license_id="license.alpha",
                current_controller="bob",
                new_controller="mallory",
                expected_root_hash72=ownership["root_hash72"],
                authority_hash72=AUTH_B,
            )

        # 13b. Duplicate logical transitions fail without appending an event.
        events_before_duplicate = self.a.replay()["events"]
        with self.assertRaises(ValueError):
            self.a.content_create(
                logical_content_id="content.alpha",
                content_hash="sha256:duplicate",
                authority_hash72=AUTH_A,
            )
        self.assertEqual(self.a.replay()["events"], events_before_duplicate)

        # 13c. Tampered materialized terms are detected.
        original_rights = self.a._connection.execute(
            "SELECT rights_json FROM license_versions WHERE license_version_id=?", (lv2,)
        ).fetchone()[0]
        self.a._connection.execute(
            "UPDATE license_versions SET rights_json='[\"forged\"]' WHERE license_version_id=?",
            (lv2,),
        )
        self.a._connection.commit()
        self.assertFalse(self.a.verify()["materialized_state"]["valid"])
        self.a._connection.execute(
            "UPDATE license_versions SET rights_json=? WHERE license_version_id=?",
            (original_rights, lv2),
        )
        self.a._connection.commit()

        # 13d. Altered receipt chain is detected, then restored.
        event_row = self.a._connection.execute(
            "SELECT sequence,successor_hash72 FROM events ORDER BY sequence LIMIT 1"
        ).fetchone()
        self.a._connection.execute(
            "UPDATE events SET successor_hash72=? WHERE sequence=?",
            ("f" * 72, event_row["sequence"]),
        )
        self.a._connection.commit()
        self.assertFalse(self.a.replay()["valid"])
        self.a._connection.execute(
            "UPDATE events SET successor_hash72=? WHERE sequence=?",
            (event_row["successor_hash72"], event_row["sequence"]),
        )
        self.a._connection.commit()

        # 13e. Forged binding materialization is detected.
        self.a._connection.execute(
            """INSERT INTO bindings VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "binding.forged",
                "project.forged",
                "mallory",
                "content.alpha",
                cv1,
                "license.alpha",
                lv1,
                "[]",
                "{}",
                "ACTIVE",
                1,
            ),
        )
        self.a._connection.commit()
        self.assertFalse(self.a.verify()["materialized_state"]["valid"])
        self.a._connection.execute("DELETE FROM bindings WHERE binding_id='binding.forged'")
        self.a._connection.commit()
        self.assertTrue(self.a.verify()["materialized_state"]["valid"])

        # Exact compatibility floor cannot be silently removed.
        with self.assertRaises(ValueError):
            self.a.license_update(
                parent_license_version_id=lv2,
                delta={"rights": ["publish"]},
                authority_hash72=AUTH_B,
            )

        # Expiry blocks new admissions while historical operation rows remain.
        sunset_content = self.a.content_create(
            logical_content_id="content.sunset",
            content_hash="sha256:sunset",
            authority_hash72=AUTH_B,
        )["result"]["content_version_id"]
        sunset_license = self.a.license_create(
            logical_license_id="license.sunset",
            controlled_content_ids=["content.sunset"],
            rights=["read"],
            obligations={},
            legacy_policy="SUNSET",
            controller="bob",
            authority_hash72=AUTH_B,
        )["result"]["license_version_id"]
        self.a.expire(license_version_id=sunset_license, authority_hash72=AUTH_B)
        sunset_denied = self.a.license_decision(
            logical_license_id="license.sunset",
            logical_content_id="content.sunset",
            principal="bob",
            operation="read",
            target_egress="internal",
        )
        self.assertEqual(sunset_denied["decision"], "DENY")
        self.assertTrue(sunset_content.startswith("cv_"))

        # 14. Cold restart replay and checkpoint recovery preserve exact root.
        before = self.a.replay()
        checkpoint_path = self.root / "checkpoint.sqlite3"
        checkpoint = self.a.checkpoint(checkpoint_path)
        recovered_path = self.root / "recovered.sqlite3"
        recovered = LicenseLineageAuthority.recover(
            checkpoint_path,
            recovered_path,
            checkpoint["sha256"],
            checkpoint["events"],
            checkpoint["root_hash72"],
        )
        try:
            self.assertEqual(recovered.replay(), before)
            self.assertEqual(
                recovered.binding_inspect("binding.keep")["license_version_id"],
                lv1,
            )
        finally:
            recovered.close()

        # 15. External-chain unavailability never blocks local canonical decision.
        offline = self.a.license_decision(
            logical_license_id="license.alpha",
            logical_content_id="content.alpha",
            principal="bob",
            operation="read",
            target_egress="internal",
            external_context={"chain": "UNAVAILABLE"},
        )
        self.assertEqual(offline["decision"], "ALLOW")
        self.assertFalse(offline["external_context_authority"])

        # 16. Browser/wallet/marketplace display cannot grant runtime authorization.
        forged_display = self.a.license_decision(
            logical_license_id="license.alpha",
            logical_content_id="content.alpha",
            principal="mallory",
            operation="read",
            target_egress="internal",
            external_context={
                "wallet_display_owner": "mallory",
                "browser_local_grant": True,
                "marketplace_owner": "mallory",
            },
        )
        self.assertEqual(forged_display["decision"], "DENY")
        self.assertEqual(forged_display["reason"], "PRINCIPAL_NOT_AUTHORIZED")

        final = self.a.verify()
        self.assertEqual(final["classification"], COMPLETION_CLASSIFICATION)
        self.assertTrue(final["replay"]["valid"])
        self.assertTrue(final["materialized_state"]["valid"])
        self.assertFalse(final["external_chain_required"])
        self.assertFalse(final["wallet_authority"])
        self.assertFalse(final["browser_local_authority"])
        self.assertFalse(final["marketplace_authority"])
        self.assertFalse(final["floating_point_canonical_authority"])
        self.assertFalse(final["new_vm81_authority"])
        self.assertFalse(final["new_hash72_clock"])

    def test_float_and_zero_authority_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.a.content_create(
                logical_content_id="float",
                content_hash="x",
                authority_hash72=AUTH_A,
                embedded_license_ids=[1.5],  # type: ignore[list-item]
            )
        with self.assertRaises(ValueError):
            self.a.content_create(
                logical_content_id="zero",
                content_hash="x",
                authority_hash72="0" * 72,
            )

    def test_cli_operation_dispatch_and_http_surface(self) -> None:
        result = execute_operation(
            self.a,
            "content-create",
            {
                "logical_content_id": "content.http",
                "content_hash": "sha256:http",
                "authority_hash72": AUTH_A,
            },
        )
        self.assertTrue(result["result"]["content_version_id"].startswith("cv_"))

        Handler.authority = self.a
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            port = server.server_address[1]
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/pass188/license/health", timeout=3
            ) as response:
                health = json.loads(response.read())
            self.assertTrue(health["ok"])
            self.assertEqual(health["contract"], "HHS-P188-VNFTCLL-LOSP-VM81-H72-H216")

            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/pass188/license/execute",
                data=json.dumps({"operation": "verify", "args": {}}).encode(),
                headers={"content-type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=3) as response:
                verify = json.loads(response.read())
            self.assertTrue(verify["ok"])
            self.assertTrue(verify["result"]["replay"]["valid"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()

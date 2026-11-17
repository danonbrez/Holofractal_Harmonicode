"""Full ASGI HTTP roundtrip using a REAL Pass190 signed capability.

Tests source upload, restart-like offset reporting, finalization and streamed
exact byte egress against the actual FastAPI router. Does not fake VM81
admission or create a canonical Hash216 knowledge record.
"""
from __future__ import annotations

import asyncio
from hashlib import sha256
import tempfile
import unittest

from fastapi import FastAPI
import httpx

from hhs_backend.api import hhs_admin_source_stream_routes_v1 as routes
from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging
from hhs_runtime.pass220.application_vm_control_plane import ApplicationVMControlPlane


class TestSignedAdminASGIRoundtrip(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        self.staging = AdminStreamStaging(self.root.name + "/sql")
        self.addCleanup(self.staging.close)
        self.previous_staging = routes._STAGING
        self.previous_authority = routes._signed_authority
        routes._STAGING = self.staging
        self.addCleanup(lambda: setattr(routes, "_STAGING", self.previous_staging))
        self.addCleanup(lambda: setattr(routes, "_signed_authority", self.previous_authority))
        self.authority = ApplicationVMControlPlane.create(
            repository_root=".",
            state_root=self.root.name + "/application-vm",
            capability_secret="fixture-only-nonproduction-key-" * 3,
            require_pinned_python=False,
        )
        routes._signed_authority = lambda: self.authority
        self.app = FastAPI()
        self.app.include_router(routes.router)

    def test_signed_http_upload_and_original_byte_egress(self):
        async def execute():
            token = self.authority.issue_token(principal="authoritative-owner", scopes=["admin.source.upload"])
            other = self.authority.issue_token(principal="other-owner", scopes=["admin.source.upload"])
            readonly = self.authority.issue_token(principal="authoritative-owner", scopes=["vm.inspect"])
            content = bytes(range(256)) * 13 + b"\\x00exact-opaque-end"
            authorization = {"Authorization": "HHS-Capability " + token}
            base = "/api/runtime/admin-source-stream/uploads"
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=self.app), base_url="http://hhs.test",
            ) as client:
                start = await client.post(base, json={"source_name": "unknown.bin"}, headers=authorization)
                self.assertEqual(start.status_code, 200, start.text)
                upload_id = start.json()["upload_id"]
                count = 0
                for chunk in (content[:31], content[31:682], content[682:]):
                    patch = await client.patch(
                        base + "/" + upload_id,
                        params={"offset": count},
                        content=chunk,
                        headers={**authorization, "Content-Type": "application/octet-stream"},
                    )
                    self.assertEqual(patch.status_code, 200, patch.text)
                    count += len(chunk)
                    self.assertEqual(patch.json()["received_bytes"], count)
                state = await client.get(base + "/" + upload_id, headers=authorization)
                self.assertEqual(state.status_code, 200)
                self.assertEqual(state.json()["received_bytes"], len(content))
                finalized = await client.post(
                    base + "/" + upload_id + "/finalize",
                    json={"expected_sha256": sha256(content).hexdigest()}, headers=authorization,
                )
                self.assertEqual(finalized.status_code, 200, finalized.text)
                self.assertEqual(finalized.json()["state"], "STAGED")
                self.assertIs(finalized.json()["canonical_hash216_admitted"], False)
                async with client.stream("GET", base + "/" + upload_id + "/source", headers=authorization) as response:
                    self.assertEqual(response.status_code, 200, await response.aread())
                    self.assertEqual(response.headers["x-hhs-source-sha256"], sha256(content).hexdigest())
                    self.assertEqual(response.headers["x-hhs-canonical-hash216-admitted"], "false")
                    self.assertEqual(await response.aread(), content)

                foreign = await client.get(base + "/" + upload_id + "/source", headers={
                    "Authorization": "HHS-Capability " + other,
                })
                self.assertEqual(foreign.status_code, 409)
                insufficient = await client.get(base + "/" + upload_id + "/source", headers={
                    "Authorization": "HHS-Capability " + readonly,
                })
                self.assertEqual(insufficient.status_code, 403)
                missing = await client.get(base + "/" + upload_id + "/source")
                self.assertEqual(missing.status_code, 403)
                forged = await client.get(base + "/" + upload_id + "/source", headers={
                    "Authorization": "HHS-Capability " + token[:-1] + ("A" if token[-1] != "A" else "B"),
                })
                self.assertEqual(forged.status_code, 401)
                self.assertEqual(self.staging.read_staged(upload_id, "authoritative-owner").read_bytes(), content)

        asyncio.run(execute())


if __name__ == "__main__":
    unittest.main()

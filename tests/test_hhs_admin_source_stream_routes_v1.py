"""Route contract tests: no public owner spoofing and exact streamed staging."""
import asyncio
import tempfile
import unittest
from fastapi import HTTPException
from starlette.requests import Request

from hhs_backend.api import hhs_admin_source_stream_routes_v1 as route
from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging


def request(chunks=(), principal=None, headers=()):
    queue = [{"type": "http.request", "body": data, "more_body": True} for data in chunks]
    queue.append({"type": "http.request", "body": b"", "more_body": False})
    async def receive():
        return queue.pop(0)
    scope = {
        "type": "http", "method": "PATCH", "path": "/api/runtime/admin-source-stream",
        "headers": headers, "query_string": b"",
    }
    if principal is not None:
        scope["hhs_authenticated_principal"] = principal
    return Request(scope, receive=receive)


class TestAdminSourceStreamRoutes(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        self.stage = AdminStreamStaging(self.root.name)
        self.addCleanup(self.stage.close)
        self.old_authority = route._signed_authority
        self.addCleanup(lambda: setattr(route, "_signed_authority", self.old_authority))
        self.old = route._STAGING
        route._STAGING = self.stage
        self.addCleanup(lambda: setattr(route, "_STAGING", self.old))
        self.owner = {"subject": "root", "admin_source_upload": True}

    def test_untrusted_header_never_grants_authority(self):
        forged = request(headers=[(b"x-hhs-authenticated-principal", b"root")])
        with self.assertRaises(HTTPException) as raised:
            route.create_upload(route.BeginBody(source_name="private.bin"), forged)
        self.assertEqual(raised.exception.status_code, 403)

    def test_principal_requires_verified_permission_and_subject(self):
        for principal in ({"subject": "root"}, {"subject": "root", "admin_source_upload": "true"},
                          {"admin_source_upload": True}):
            with self.assertRaises(HTTPException):
                route.create_upload(route.BeginBody(source_name="private.bin"), request(principal=principal))

    def test_exact_bytes_and_owner_bound_finalize(self):
        created = route.create_upload(route.BeginBody(source_name="unknown.zzz"), request(principal=self.owner))
        id_ = created["upload_id"]
        data = bytes(range(256)) * 5 + b"END"
        received = asyncio.run(route.append_upload(id_, request([data[:17], data[17:]],
                                                              principal=self.owner), 0))
        self.assertEqual(received["received_bytes"], len(data))
        staged = route.finish_upload(id_, route.FinalizeBody(), request(principal=self.owner))
        self.assertEqual(staged["state"], "STAGED")
        self.assertFalse(staged["canonical_hash216_admitted"])
        self.assertEqual(self.stage.read_staged(id_, "root").read_bytes(), data)
        with self.assertRaises(HTTPException):
            route.read_upload(id_, request(principal={"subject": "another", "admin_source_upload": True}))

    def test_verified_pass190_capability_scope_is_required(self):
        class VerifiedControl:
            def authenticate_header(self, value):
                if value != "HHS-Capability signed":
                    raise ValueError("invalid")
                return {"principal": "signed-admin", "scopes": ["admin.source.upload"]}

        route._signed_authority = lambda: VerifiedControl()
        signed = request(headers=[(b"authorization", b"HHS-Capability signed")])
        created = route.create_upload(route.BeginBody(source_name="signed.bin"), signed)
        self.assertEqual(created["state"], "UPLOADING")
        self.assertEqual(self.stage._get(created["upload_id"], "signed-admin")["owner"], "signed-admin")
        with self.assertRaises(HTTPException):
            route.read_upload(created["upload_id"], request(principal={"subject": "anonymous"}))

        class OtherScope:
            def authenticate_header(self, value):
                return {"principal": "signed-admin", "scopes": ["vm.inspect"]}
        route._signed_authority = lambda: OtherScope()
        with self.assertRaises(HTTPException) as rejected:
            route.create_upload(route.BeginBody(source_name="denied"), signed)
        self.assertEqual(rejected.exception.status_code, 403)

    def test_invalid_signed_capability_fails_closed(self):
        class BadControl:
            def authenticate_header(self, value):
                raise ValueError("rejected")
        route._signed_authority = lambda: BadControl()
        signed = request(headers=[(b"authorization", b"HHS-Capability forged")])
        with self.assertRaises(HTTPException) as rejected:
            route.create_upload(route.BeginBody(source_name="denied"), signed)
        self.assertEqual(rejected.exception.status_code, 503)

    def test_owner_scoped_lane5_candidate_without_canonical_promotion(self):
        created = route.create_upload(route.BeginBody(source_name="candidate.bin"), request(principal=self.owner))
        upload_id = created["upload_id"]
        payload = bytes(range(256)) * 4 + b"tail"
        asyncio.run(route.append_upload(upload_id, request([payload], principal=self.owner), 0))
        route.finish_upload(upload_id, route.FinalizeBody(), request(principal=self.owner))

        seen = []
        old_continue = route.continue_staged_to_lane5
        self.addCleanup(lambda: setattr(route, "continue_staged_to_lane5", old_continue))

        def native_stub(staging, id_, owner):
            seen.append((id_, owner, staging.read_staged(id_, owner).read_bytes()))
            return {
                "upload_id": id_, "canonical_hash216_admitted": False,
                "signed_vm81_admission_required": True,
            }

        route.continue_staged_to_lane5 = native_stub
        result = route.native_lane5_candidate(upload_id, request(principal=self.owner))
        self.assertEqual(seen, [(upload_id, "root", payload)])
        self.assertFalse(result["canonical_hash216_admitted"])
        self.assertTrue(result["signed_vm81_admission_required"])
        with self.assertRaises(HTTPException) as denied:
            route.native_lane5_candidate(
                upload_id, request(principal={"subject": "another", "admin_source_upload": True})
            )
        self.assertEqual(denied.exception.status_code, 409)
        self.assertEqual(len(seen), 1)

    def test_unfinalized_candidate_rejected(self):
        created = route.create_upload(route.BeginBody(source_name="unfinished"), request(principal=self.owner))
        with self.assertRaises(HTTPException) as denied:
            route.native_lane5_candidate(created["upload_id"], request(principal=self.owner))
        self.assertEqual(denied.exception.status_code, 409)

    def test_exact_owner_scoped_streamed_source_egress(self):
        from hashlib import sha256
        payload = bytes(range(256)) * 11 + b"\\0egress"
        created = route.create_upload(route.BeginBody(source_name="egress.unknown"), request(principal=self.owner))
        upload_id = created["upload_id"]
        asyncio.run(route.append_upload(upload_id, request([payload[:23], payload[23:]], principal=self.owner), 0))
        route.finish_upload(upload_id, route.FinalizeBody(), request(principal=self.owner))
        streamed = route.read_exact_staged_source(upload_id, request(principal=self.owner))
        assert streamed.headers["x-hhs-source-sha256"] == sha256(payload).hexdigest()
        assert streamed.headers["x-hhs-canonical-hash216-admitted"] == "false"
        assert streamed.headers["content-length"] == str(len(payload))
        async def collect():
            return b"".join([piece async for piece in streamed.body_iterator])
        assert asyncio.run(collect()) == payload
        with self.assertRaises(HTTPException) as denied:
            route.read_exact_staged_source(
                upload_id, request(principal={"subject": "foreign", "admin_source_upload": True})
            )
        self.assertEqual(denied.exception.status_code, 409)

    def test_staged_readback_rejects_corrupted_blob_and_unfinished_source(self):
        created = route.create_upload(route.BeginBody(source_name="pending"), request(principal=self.owner))
        upload_id = created["upload_id"]
        with self.assertRaises(HTTPException):
            route.read_exact_staged_source(upload_id, request(principal=self.owner))
        asyncio.run(route.append_upload(upload_id, request([b"immutable"], principal=self.owner), 0))
        route.finish_upload(upload_id, route.FinalizeBody(), request(principal=self.owner))
        source_path = self.stage.read_staged(upload_id, "root")
        source_path.chmod(0o600)
        try:
            source_path.write_bytes(b"altered!!")
            with self.assertRaises(HTTPException) as denied:
                route.read_exact_staged_source(upload_id, request(principal=self.owner))
            self.assertEqual(denied.exception.status_code, 409)
        finally:
            source_path.chmod(0o400)

    def test_retry_of_committed_chunk_uses_existing_storage_semantics(self):
        created = route.create_upload(route.BeginBody(source_name="retry.bin"), request(principal=self.owner))
        upload_id = created["upload_id"]
        payload = b"authoritative transport bytes"
        first = asyncio.run(route.append_upload(upload_id, request([payload], principal=self.owner), 0))
        retried = asyncio.run(route.append_upload(upload_id, request([payload], principal=self.owner), 0))
        self.assertEqual(first["received_bytes"], len(payload))
        self.assertEqual(retried["received_bytes"], len(payload))
        self.assertEqual(self.stage.status(upload_id, "root")["received_bytes"], len(payload))
        with self.assertRaises(HTTPException) as conflict:
            asyncio.run(route.append_upload(upload_id, request([b"wrong bytes"], principal=self.owner), 0))
        self.assertEqual(conflict.exception.status_code, 409)
        self.assertEqual(self.stage.status(upload_id, "root")["received_bytes"], len(payload))

    def test_empty_transport_body_returns_existing_status(self):
        created = route.create_upload(route.BeginBody(source_name="empty.bin"), request(principal=self.owner))
        status = asyncio.run(route.append_upload(created["upload_id"], request([], principal=self.owner), 0))
        self.assertEqual(status["state"], "UPLOADING")
        self.assertEqual(status["received_bytes"], 0)

    def test_conflicting_offset_rejected(self):
        created = route.create_upload(route.BeginBody(source_name="source"), request(principal=self.owner))
        with self.assertRaises(HTTPException) as raised:
            asyncio.run(route.append_upload(created["upload_id"], request([b"bad"], principal=self.owner), 2))
        self.assertEqual(raised.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()

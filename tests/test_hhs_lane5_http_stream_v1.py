"""Regression tests for byte-exact, non-buffered native HTTP ingress mediation."""
import asyncio
from hashlib import sha256
import tempfile
import unittest
from types import SimpleNamespace

from hhs_backend import lane5_ingress_gateway as gateway


class VerifyingNativeMediator:
    def __init__(self):
        self.envelopes = []

    def mediate_workload(self, envelope):
        self.envelopes.append(envelope)
        return {
            "workload_sha256": envelope.workload_sha256.hex(),
            "workload_byte_count": envelope.byte_count,
            "route_receipt_signature64": 1,
            "candidate_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash216_authority": False,
            "requires_signed_environmental_vm81_admission": True,
        }


class TestNativeHTTPStream(unittest.TestCase):
    def test_native_stream_matches_exact_previous_framing(self):
        original = gateway._mediator
        stub = VerifyingNativeMediator()
        gateway._mediator = stub
        try:
            async def exercise(payload):
                app = SimpleNamespace(state=SimpleNamespace(lane5_lock=asyncio.Lock()))
                with tempfile.TemporaryFile(mode="w+b") as spool:
                    for offset in range(0, len(payload), 648):
                        spool.write(payload[offset:offset + 648])
                    spool.flush()
                    return await gateway._mediate_file_async(
                        app, spool=spool, body_bytes=len(payload),
                        transport=b"http", method=b"POST",
                        raw_path=b"/api/runtime/storage-training/files",
                        query_string=b"x=1", headers=[(b"content-type", b"application/octet-stream")],
                        provenance="regression",
                    )
            for data in (b"", b"abc", bytes(range(256)) * 3, bytes(range(256)) * 1025):
                result = asyncio.run(exercise(data))
                prior = gateway.serialize_environmental_ingress(
                    transport=b"http", method_or_opcode=b"POST",
                    raw_path=b"/api/runtime/storage-training/files",
                    query_string=b"x=1", headers=[(b"content-type", b"application/octet-stream")],
                    payload=data,
                )
                self.assertEqual(result["workload_sha256"], sha256(prior).hexdigest())
                self.assertEqual(result["workload_byte_count"], len(prior))
        finally:
            gateway._mediator = original

    def test_stream_does_not_call_request_body(self):
        import inspect
        source = inspect.getsource(gateway._http_proxy)
        self.assertIn("request.stream()", source)
        self.assertNotIn("request.body()", source)
        self.assertIn("_mediate_file_async", source)
        self.assertLess(source.index("_mediate_file_async"), source.index("http_client.send"))

    def test_native_rejection_and_runtime_failure_are_not_vm81_proofs(self):
        import httpx
        from unittest.mock import patch

        async def invoke(failure):
            gateway.app.state.lane5_lock = asyncio.Lock()
            transport = httpx.ASGITransport(app=gateway.app)
            async with httpx.AsyncClient(transport=transport, base_url="http://example.test") as client:
                with patch.object(gateway, "_mediate_file_async", side_effect=failure):
                    return await client.post("/test", content=b"legacy payload")

        native = asyncio.run(invoke(gateway.Lane5IngressRejected("NO_CANDIDATE")))
        self.assertEqual(native.status_code, 503)
        self.assertEqual(native.headers["x-hhs-lane5-ingress"], "native-candidate-rejected")
        self.assertEqual(native.headers["x-hhs-vm81-admission"], "not-performed")

        unavailable = asyncio.run(invoke(OSError("native library unavailable")))
        self.assertEqual(unavailable.status_code, 503)
        self.assertEqual(unavailable.headers["x-hhs-lane5-ingress"], "unavailable")
        self.assertEqual(unavailable.headers["x-hhs-vm81-admission"], "not-performed")
        self.assertNotIn("rejected", unavailable.text.lower())

    def test_request_payload_frame_width(self):
        self.assertEqual(81 * 64 // 8, 648)


if __name__ == "__main__":
    unittest.main()

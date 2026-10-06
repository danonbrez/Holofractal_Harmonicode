"""Fail-closed host ingress gateway for HHS production.

Public HTTP/WebSocket traffic is terminated by nginx and sent here before it may
reach the private :8080 Runtime OS or :8720 application-VM service. Every
client-originated request/frame is bound to the existing arbitrary-byte Lane 5
1.48 native membrane. Lane 5 remains candidate-only; canonical mutation stays
owned by the inherited signed environmental VM81 admission boundary.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from hashlib import sha256
import inspect
import os
from typing import Iterable, Sequence

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.responses import Response
import httpx
import websockets

from hhs_python.runtime.hhs_pass219_lane5_unbounded_workload_scaling_bridge import (
    FULL_MANIFOLD_MODULUS,
    Lane5RouteCandidate,
    Lane5WorkloadEnvelope,
    Pass219Lane5UnboundedWorkloadBridge,
)

GATEWAY_SCHEMA = "HHS_LANE5_HOST_INGRESS_MEMBRANE_V1"
GATEWAY_PORT = 8715
DEFAULT_HTTP_UPSTREAM = "http://127.0.0.1:8080"
DEFAULT_WS_UPSTREAM = "ws://127.0.0.1:8080"
DEFAULT_VM_HTTP_UPSTREAM = "http://127.0.0.1:8720"
DEFAULT_VM_WS_UPSTREAM = "ws://127.0.0.1:8720"
HEALTH_PATH = "/__hhs_lane5_ingress_health"

_HOP_BY_HOP = {
    b"connection",
    b"keep-alive",
    b"proxy-authenticate",
    b"proxy-authorization",
    b"te",
    b"trailer",
    b"transfer-encoding",
    b"upgrade",
}
_RESERVED_INGRESS_HEADER_PREFIX = b"x-hhs-lane5-"
_FORBIDDEN_BOUNDARY = sha256(
    b"HHS-LANE5-HOST-INGRESS-FORBIDDEN-BOUNDARY-V1"
).digest()


def _field(raw: bytes) -> bytes:
    return len(raw).to_bytes(8, "big") + raw


def serialize_environmental_ingress(
    *,
    transport: bytes,
    method_or_opcode: bytes,
    raw_path: bytes,
    query_string: bytes,
    headers: Sequence[tuple[bytes, bytes]],
    payload: bytes,
) -> bytes:
    """Length-frame exact network ingress without text re-encoding."""
    chunks = [
        GATEWAY_SCHEMA.encode("ascii") + b"\0",
        _field(transport),
        _field(method_or_opcode),
        _field(raw_path),
        _field(query_string),
        len(headers).to_bytes(4, "big"),
    ]
    for name, value in headers:
        chunks.append(_field(bytes(name)))
        chunks.append(_field(bytes(value)))
    chunks.append(_field(payload))
    return b"".join(chunks)


def _address(label: bytes, workload_sha256: bytes) -> int:
    return int.from_bytes(
        sha256(label + b"\0" + workload_sha256).digest(), "big"
    ) % FULL_MANIFOLD_MODULUS


def _route_candidate(workload_sha256: bytes) -> Lane5RouteCandidate:
    phase_slot = (int.from_bytes(workload_sha256[:2], "big") % 4) * 18
    trinary = (-1, 0, 1)[workload_sha256[2] % 3]
    binary = workload_sha256[3] & 1
    return Lane5RouteCandidate(
        route_witness_sha256=sha256(
            b"HHS-LANE5-HOST-INGRESS-ROUTE-V1\0" + workload_sha256
        ).digest(),
        reciprocal_witness_sha256=sha256(
            b"HHS-LANE5-HOST-INGRESS-RECIPROCAL-V1\0" + workload_sha256
        ).digest(),
        phase_slot=phase_slot,
        trinary_collapse=trinary,
        binary_collapse=binary,
    )


class Lane5IngressRejected(RuntimeError):
    pass


class Lane5IngressMediator:
    def __init__(self, bridge_factory=Pass219Lane5UnboundedWorkloadBridge) -> None:
        self._bridge_factory = bridge_factory
        self._bridge = None

    def _native(self):
        if self._bridge is None:
            self._bridge = self._bridge_factory()
        return self._bridge

    @staticmethod
    def _verify_authority(authority: dict[str, object]) -> None:
        for key in (
            "any_byte_serializable_workload",
            "workload_class_agnostic",
            "streaming_candidate_ingress",
            "candidate_only",
            "requires_signed_environmental_vm81_admission",
        ):
            if authority.get(key) is not True:
                raise Lane5IngressRejected(
                    f"HHS_LANE5_HOST_INGRESS_AUTHORITY_MISSING:{key}"
                )
        for key in (
            "canonical_vm81_mutation_authority",
            "canonical_hash216_authority",
        ):
            if authority.get(key) is not False:
                raise Lane5IngressRejected(
                    f"HHS_LANE5_HOST_INGRESS_AUTHORITY_ESCALATION:{key}"
                )

    def health(self) -> dict[str, object]:
        authority = self._native().authority()
        self._verify_authority(authority)
        probe = serialize_environmental_ingress(
            transport=b"health",
            method_or_opcode=b"SELFTEST",
            raw_path=HEALTH_PATH.encode("ascii"),
            query_string=b"",
            headers=(),
            payload=b"HHS-LANE5-HOST-INGRESS-SELFTEST-V1",
        )
        receipt = self.mediate(
            probe,
            provenance="host-ingress:startup-selftest",
        )
        return {
            "schema": GATEWAY_SCHEMA,
            "status": "ready",
            "lane5_candidate_only": True,
            "requires_signed_environmental_vm81_admission": True,
            "direct_backend_public_bypass": False,
            "native_mediation_selftest": True,
            "route_receipt_signature64": receipt["route_receipt_signature64"],
        }

    def mediate(self, exact_ingress: bytes, *, provenance: str) -> dict[str, object]:
        bridge = self._native()
        authority = bridge.authority()
        self._verify_authority(authority)
        workload = Lane5WorkloadEnvelope.from_bytes(
            exact_ingress,
            provenance=provenance,
        )
        digest = workload.workload_sha256
        receipt = bridge.optimize(
            workload=workload,
            previous_address=_address(b"previous", digest),
            current_address=_address(b"current", digest),
            goal_address=_address(b"goal", digest),
            forbidden_boundary_sha256=_FORBIDDEN_BOUNDARY,
            candidates=(_route_candidate(digest),),
        )
        if int(receipt.get("admitted_candidates", 0)) < 1:
            raise Lane5IngressRejected("HHS_LANE5_HOST_INGRESS_NO_ADMITTED_CANDIDATE")
        if receipt.get("candidate_only") is not True:
            raise Lane5IngressRejected("HHS_LANE5_HOST_INGRESS_NOT_CANDIDATE_ONLY")
        if receipt.get("canonical_vm81_mutation_authority") is not False:
            raise Lane5IngressRejected("HHS_LANE5_HOST_INGRESS_VM81_AUTHORITY_ESCALATION")
        if receipt.get("canonical_hash216_authority") is not False:
            raise Lane5IngressRejected("HHS_LANE5_HOST_INGRESS_HASH216_AUTHORITY_ESCALATION")
        if receipt.get("requires_signed_environmental_vm81_admission") is not True:
            raise Lane5IngressRejected("HHS_LANE5_HOST_INGRESS_SIGNED_VM81_BYPASS")
        return receipt


def _filtered_headers(
    headers: Iterable[tuple[bytes, bytes]],
) -> list[tuple[bytes, bytes]]:
    result: list[tuple[bytes, bytes]] = []
    for name, value in headers:
        lowered = bytes(name).lower()
        if lowered in _HOP_BY_HOP:
            continue
        if lowered.startswith(_RESERVED_INGRESS_HEADER_PREFIX):
            continue
        result.append((bytes(name), bytes(value)))
    return result


def _target(
    *,
    raw_path: bytes,
    query_string: bytes,
    websocket: bool,
) -> str:
    path = raw_path.decode("latin-1")
    query = query_string.decode("latin-1")
    is_vm = path == "/vm-api" or path.startswith("/vm-api/")
    if is_vm:
        path = path[len("/vm-api") :] or "/"
        base = (
            os.environ.get("HHS_LANE5_INGRESS_VM_WS_UPSTREAM", DEFAULT_VM_WS_UPSTREAM)
            if websocket
            else os.environ.get(
                "HHS_LANE5_INGRESS_VM_HTTP_UPSTREAM", DEFAULT_VM_HTTP_UPSTREAM
            )
        )
    else:
        base = (
            os.environ.get("HHS_LANE5_INGRESS_WS_UPSTREAM", DEFAULT_WS_UPSTREAM)
            if websocket
            else os.environ.get(
                "HHS_LANE5_INGRESS_HTTP_UPSTREAM", DEFAULT_HTTP_UPSTREAM
            )
        )
    return base.rstrip("/") + path + (("?" + query) if query else "")


def _receipt_headers(receipt: dict[str, object]) -> list[tuple[bytes, bytes]]:
    return [
        (b"x-hhs-lane5-ingress", b"mediated"),
        (
            b"x-hhs-lane5-workload-sha256",
            str(receipt["workload_sha256"]).encode("ascii"),
        ),
        (
            b"x-hhs-lane5-receipt-signature64",
            str(receipt["route_receipt_signature64"]).encode("ascii"),
        ),
        (b"x-hhs-lane5-requires-signed-vm81", b"1"),
    ]


_mediator = Lane5IngressMediator()


@asynccontextmanager
async def _lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=5.0),
        follow_redirects=False,
    )
    app.state.lane5_lock = asyncio.Lock()
    try:
        yield
    finally:
        await app.state.http_client.aclose()


app = FastAPI(
    title="HHS Lane 5 Host Ingress Membrane",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=_lifespan,
)


async def _mediate_async(app_obj: FastAPI, exact: bytes, provenance: str):
    async with app_obj.state.lane5_lock:
        return await asyncio.to_thread(_mediator.mediate, exact, provenance=provenance)


@app.get(HEALTH_PATH)
async def ingress_health(request: Request):
    if request.url.hostname not in {"127.0.0.1", "localhost"}:
        raise HTTPException(status_code=404)
    try:
        return await asyncio.to_thread(_mediator.health)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def _http_proxy(request: Request, path: str = "") -> Response:
    raw_path = bytes(request.scope.get("raw_path") or ("/" + path).encode("utf-8"))
    query = bytes(request.scope.get("query_string") or b"")
    raw_headers = [
        (bytes(name), bytes(value))
        for name, value in request.scope.get("headers", ())
    ]
    body = await request.body()
    exact = serialize_environmental_ingress(
        transport=b"http",
        method_or_opcode=request.method.encode("ascii"),
        raw_path=raw_path,
        query_string=query,
        headers=raw_headers,
        payload=body,
    )
    try:
        receipt = await _mediate_async(
            request.app,
            exact,
            f"network:http:{request.method}:{raw_path.decode('latin-1')}",
        )
    except Exception:
        return Response(
            content=b"HHS Lane 5 ingress rejected environmental request\n",
            status_code=503,
            media_type="text/plain",
            headers={"X-HHS-Lane5-Ingress": "rejected"},
        )

    headers = _filtered_headers(raw_headers) + _receipt_headers(receipt)
    target = _target(raw_path=raw_path, query_string=query, websocket=False)
    try:
        upstream = await request.app.state.http_client.request(
            request.method,
            target,
            headers=headers,
            content=body,
        )
    except httpx.HTTPError:
        return Response(
            content=b"HHS backend unavailable behind Lane 5 ingress\n",
            status_code=503,
            media_type="text/plain",
            headers={
                "X-HHS-Lane5-Ingress": "mediated",
                "X-HHS-Upstream": "unavailable",
            },
        )
    response_headers: dict[str, str] = {}
    set_cookies: list[str] = []
    for name, value in upstream.headers.multi_items():
        lowered = name.lower().encode("ascii", "ignore")
        if lowered in _HOP_BY_HOP or lowered in {b"content-length", b"content-encoding"}:
            continue
        if name.lower() == "set-cookie":
            set_cookies.append(value)
            continue
        response_headers[name] = value
    response_headers["X-HHS-Lane5-Ingress"] = "mediated"
    response = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
    for value in set_cookies:
        response.headers.append("set-cookie", value)
    return response


app.add_api_route(
    "/",
    _http_proxy,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
app.add_api_route(
    "/{path:path}",
    _http_proxy,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)


def _websocket_connect_kwargs(
    headers: list[tuple[bytes, bytes]],
    subprotocols: list[str],
) -> dict[str, object]:
    text_headers = [
        (name.decode("latin-1"), value.decode("latin-1"))
        for name, value in _filtered_headers(headers)
        if name.lower()
        not in {
            b"sec-websocket-key",
            b"sec-websocket-version",
            b"sec-websocket-extensions",
            b"sec-websocket-protocol",
        }
    ]
    kwargs: dict[str, object] = {
        "subprotocols": subprotocols or None,
        "max_size": None,
        "open_timeout": 5,
        "close_timeout": 5,
    }
    params = inspect.signature(websockets.connect).parameters
    if "additional_headers" in params:
        kwargs["additional_headers"] = text_headers
    elif "extra_headers" in params:
        kwargs["extra_headers"] = text_headers
    if "proxy" in params:
        # The authoritative upstream is always a private loopback service.
        # Ambient proxy discovery would move the second hop outside the
        # Lane-5-mediated host boundary and can break local WebSocket upgrade.
        kwargs["proxy"] = None
    return kwargs


@app.websocket("/")
@app.websocket("/{path:path}")
async def websocket_proxy(websocket: WebSocket, path: str = "") -> None:
    raw_path = bytes(websocket.scope.get("raw_path") or ("/" + path).encode("utf-8"))
    query = bytes(websocket.scope.get("query_string") or b"")
    raw_headers = [
        (bytes(name), bytes(value))
        for name, value in websocket.scope.get("headers", ())
    ]
    handshake = serialize_environmental_ingress(
        transport=b"websocket-handshake",
        method_or_opcode=b"CONNECT",
        raw_path=raw_path,
        query_string=query,
        headers=raw_headers,
        payload=b"",
    )
    try:
        handshake_receipt = await _mediate_async(
            websocket.app,
            handshake,
            f"network:websocket-handshake:{raw_path.decode('latin-1')}",
        )
    except Exception:
        await websocket.close(code=1013)
        return

    requested = websocket.headers.get("sec-websocket-protocol", "")
    subprotocols = [part.strip() for part in requested.split(",") if part.strip()]
    target = _target(raw_path=raw_path, query_string=query, websocket=True)
    handshake_headers = raw_headers + _receipt_headers(handshake_receipt)
    kwargs = _websocket_connect_kwargs(handshake_headers, subprotocols)

    try:
        async with websockets.connect(target, **kwargs) as upstream:
            selected = getattr(upstream, "subprotocol", None)
            await websocket.accept(subprotocol=selected)

            async def client_to_runtime() -> None:
                frame_index = 0
                while True:
                    event = await websocket.receive()
                    if event["type"] == "websocket.disconnect":
                        return
                    text_value = event.get("text")
                    bytes_value = event.get("bytes")
                    if text_value is not None:
                        payload = text_value.encode("utf-8")
                        opcode = b"text"
                        outbound = text_value
                    elif bytes_value is not None:
                        payload = bytes(bytes_value)
                        opcode = b"binary"
                        outbound = payload
                    else:
                        continue
                    exact = serialize_environmental_ingress(
                        transport=b"websocket-frame",
                        method_or_opcode=opcode,
                        raw_path=raw_path,
                        query_string=query,
                        headers=(),
                        payload=payload,
                    )
                    await _mediate_async(
                        websocket.app,
                        exact,
                        f"network:websocket-frame:{frame_index}:{raw_path.decode('latin-1')}",
                    )
                    frame_index += 1
                    await upstream.send(outbound)

            async def runtime_to_client() -> None:
                async for message in upstream:
                    if isinstance(message, bytes):
                        await websocket.send_bytes(message)
                    else:
                        await websocket.send_text(message)

            first = asyncio.create_task(client_to_runtime())
            second = asyncio.create_task(runtime_to_client())
            done, pending = await asyncio.wait(
                {first, second},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            for task in done:
                task.result()
    except Exception:
        try:
            await websocket.close(code=1011)
        except Exception:
            pass


__all__ = [
    "GATEWAY_PORT",
    "GATEWAY_SCHEMA",
    "HEALTH_PATH",
    "Lane5IngressMediator",
    "Lane5IngressRejected",
    "app",
    "serialize_environmental_ingress",
]

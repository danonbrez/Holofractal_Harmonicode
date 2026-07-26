from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
from typing import Any, Mapping

from hash216_projection_scheduler import FrameTelemetry, Hash216ProjectionScheduler

API_VERSION = "1.0.0"
CONTRACT_ID = "HHS-P158-LLABI-NFTC-API"
BASE = "/api/v1/hhs/pass158/gui/projection"


def envelope(*, status: str, classification: str, obj: Any = None, errors: list[Any] | None = None) -> dict[str, Any]:
    return {
        "api_version": API_VERSION,
        "contract_id": CONTRACT_ID,
        "status": status,
        "classification": classification,
        "authority_level": "A1_EXECUTION_EVIDENCE",
        "object": obj if obj is not None else {},
        "errors": errors or [],
    }


class Pass158GuiProjectionRuntime:
    def __init__(self, scheduler: Hash216ProjectionScheduler | None = None) -> None:
        self.scheduler = scheduler or Hash216ProjectionScheduler()

    def dispatch(
        self,
        method: str,
        path: str,
        body: Mapping[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any]]:
        payload = dict(body or {})
        try:
            return 200, self._dispatch(method.upper(), path, payload)
        except Exception as error:
            return 200, envelope(
                status="REJECTED",
                classification=str(error).strip("'") or error.__class__.__name__,
                errors=[{"type": error.__class__.__name__, "message": str(error)}],
            )

    def _dispatch(self, method: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
        if method == "GET" and path == f"{BASE}/status":
            return envelope(
                status="READY",
                classification="HHS_PASS_158_HASH216_GUI_PROJECTION_SCHEDULER_READY",
                obj=self.scheduler.status(),
            )

        if method == "POST" and path == f"{BASE}/objects/register":
            result = self.scheduler.observe_runtime_state(
                str(body["object_id"]),
                str(body["object_class"]),
                body.get("value"),
                authoritative=bool(body.get("authoritative", False)),
                static=bool(body.get("static", False)),
                dependencies=tuple(str(item) for item in body.get("dependencies", [])),
                delta_offset_vector=body.get("delta_offset_vector"),
            )
            return envelope(status="INDEXED", classification=result["classification"], obj=result)

        if method == "POST" and path == f"{BASE}/runtime/observe":
            result = self.scheduler.observe_runtime_state(
                str(body["object_id"]),
                str(body["object_class"]),
                body.get("state"),
                authoritative=bool(body.get("authoritative", False)),
                dependencies=tuple(str(item) for item in body.get("dependencies", [])),
                delta_offset_vector=body.get("delta_offset_vector"),
            )
            return envelope(status="OBSERVED", classification=result["classification"], obj=result)

        if method == "POST" and path == f"{BASE}/frame/telemetry":
            telemetry = FrameTelemetry(
                frame_sequence=int(body["frame_sequence"]),
                target_frame_ns=int(body["target_frame_ns"]),
                physics_ns=int(body.get("physics_ns", 0)),
                projection_ns=int(body.get("projection_ns", 0)),
                buffer_upload_ns=int(body.get("buffer_upload_ns", 0)),
                render_ns=int(body.get("render_ns", 0)),
                runtime_ingress_ns=int(body.get("runtime_ingress_ns", 0)),
                receipt_ns=int(body.get("receipt_ns", 0)),
                backlog_count=int(body.get("backlog_count", 0)),
            )
            decision = self.scheduler.observe_frame_telemetry(telemetry)
            return envelope(status="OBSERVED", classification=decision["classification"], obj=decision)

        if method == "POST" and path == f"{BASE}/packages/next":
            package = self.scheduler.build_projection_package(
                int(body["frame_sequence"]),
                projection_profile=str(body.get("projection_profile", "BALANCED")),
            )
            return envelope(status="PENDING_VM81", classification=package["classification"], obj=package)

        match = re.fullmatch(re.escape(BASE) + r"/packages/([^/]+)/admit", path)
        if method == "POST" and match:
            package = self.scheduler.acknowledge_vm81(
                match.group(1),
                admitted=bool(body.get("admitted", False)),
                receipt_hash72=body.get("receipt_hash72"),
                classification=body.get("classification"),
            )
            return envelope(
                status=package["vm81_admission"],
                classification=package["classification"],
                obj=package,
            )

        if method == "GET" and path == f"{BASE}/snapshot":
            return envelope(
                status="OK",
                classification="HHS_PASS_158_HASH216_GUI_PROJECTION_SNAPSHOT",
                obj=self.scheduler.snapshot(),
            )

        if method == "POST" and path == f"{BASE}/recover":
            status = self.scheduler.recover(body["snapshot"])
            return envelope(
                status="RECOVERED",
                classification="HHS_PASS_158_HASH216_GUI_PROJECTION_RECOVERED",
                obj=status,
            )

        raise KeyError("ENDPOINT_NOT_FOUND")


class Handler(BaseHTTPRequestHandler):
    runtime: Pass158GuiProjectionRuntime

    def _send(self, code: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _body(self) -> dict[str, Any]:
        size = int(self.headers.get("Content-Length", "0") or 0)
        if size == 0:
            return {}
        payload = json.loads(self.rfile.read(size))
        if not isinstance(payload, dict):
            raise ValueError("REQUEST_BODY_MUST_BE_OBJECT")
        return payload

    def do_GET(self) -> None:  # noqa: N802
        code, payload = self.runtime.dispatch("GET", self.path, {})
        self._send(code, payload)

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._body()
        except Exception as error:
            self._send(200, envelope(status="REJECTED", classification=str(error)))
            return
        code, payload = self.runtime.dispatch("POST", self.path, body)
        self._send(code, payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


def run_self_test() -> dict[str, Any]:
    receipt_registry: dict[str, str] = {}
    scheduler = Hash216ProjectionScheduler(
        receipt_verifier=lambda receipt, root: receipt_registry.get(receipt) == root
    )
    runtime = Pass158GuiProjectionRuntime(scheduler)
    checks: list[bool] = []

    _, registered = runtime.dispatch(
        "POST",
        f"{BASE}/objects/register",
        {
            "object_id": "hash72-address-table",
            "object_class": "STATIC_ADDRESS_OBJECT",
            "value": {"particle_count": 5184, "mapping": "72x72"},
            "static": True,
        },
    )
    checks.append(registered["status"] == "INDEXED")

    _, observed = runtime.dispatch(
        "POST",
        f"{BASE}/runtime/observe",
        {
            "object_id": "particle-positions",
            "object_class": "PHYSICS_POSITION_OBJECT",
            "state": {"step": 1, "positions": [[0, 0, 0]]},
            "delta_offset_vector": {"relative": "0/1"},
        },
    )
    checks.append(observed["object"]["changed"] is True)

    _, telemetry = runtime.dispatch(
        "POST",
        f"{BASE}/frame/telemetry",
        {
            "frame_sequence": 1,
            "target_frame_ns": 16_666_667,
            "physics_ns": 4_000_000,
            "projection_ns": 1_000_000,
            "buffer_upload_ns": 2_000_000,
            "render_ns": 5_000_000,
        },
    )
    checks.append(telemetry["classification"] == "FRAME_BUDGET_NORMAL")

    _, built = runtime.dispatch(
        "POST",
        f"{BASE}/packages/next",
        {"frame_sequence": 1, "projection_profile": "BALANCED"},
    )
    package = built["object"]
    checks.extend(
        [
            len(package["projection_hash216_positions"]) == 216,
            package["mutation_authority"] is False,
            package["requires_vm81_validation"] is True,
            package["changed_chunk_count"] == 2,
        ]
    )

    receipt_hash72 = "0" * 72
    receipt_registry[receipt_hash72] = package["projection_root_hash216"]
    _, admitted = runtime.dispatch(
        "POST",
        f"{BASE}/packages/{package['projection_root_hash216']}/admit",
        {"admitted": True, "receipt_hash72": receipt_hash72},
    )
    checks.append(admitted["status"] == "ADMITTED")

    _, snapshot = runtime.dispatch("GET", f"{BASE}/snapshot", {})
    checks.append(snapshot["object"]["mutation_authority"] is False)

    _, status = runtime.dispatch("GET", f"{BASE}/status", {})
    checks.append(status["object"]["objects"] == 2)

    if not all(checks):
        raise AssertionError({"checks": checks})
    return {
        "classification": "HHS_PASS_158_HASH216_GUI_PROJECTION_SCHEDULER_VERIFIED",
        "integration_cases": len(checks),
        "all_passed": True,
        "status": runtime.scheduler.status(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self-test")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8158)
    args = parser.parse_args(argv)
    if args.command == "self-test":
        print(json.dumps(run_self_test(), sort_keys=True))
        return 0
    Handler.runtime = Pass158GuiProjectionRuntime()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

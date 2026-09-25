from __future__ import annotations

import argparse
from base64 import b64decode, b64encode
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave
from typing import Any

from playwright.sync_api import Page, sync_playwright


REPO = Path(__file__).resolve().parents[2]
ENTRYPOINT = "hhs_backend.production_visual_server:app"
CANONICAL_MAX_SOURCE_BYTES = 16 * 1024 * 1024
PROBE_PATH = "/api/interface/status"


def free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = int(sock.getsockname()[1])
    sock.close()
    return port


def http_fetch(url: str, *, timeout: float = 10.0) -> tuple[int, str, bytes]:
    request = urllib.request.Request(url, headers={"Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return (
                int(response.status),
                str(response.headers.get("content-type", "")),
                response.read(),
            )
    except urllib.error.HTTPError as exc:
        return int(exc.code), str(exc.headers.get("content-type", "")), exc.read()


class ExternalFrontendServer:
    def __init__(self, port: int, evidence_dir: Path) -> None:
        self.port = port
        self.evidence_dir = evidence_dir
        self.process: subprocess.Popen[str] | None = None
        self.log_path = evidence_dir / "external-frontend-server.log"
        self._log = None

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def start(self, deadline_seconds: int = 120) -> dict[str, Any]:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        state_root = self.evidence_dir / "runtime-state"
        env = os.environ.copy()
        env.update(
            {
                "PYTHONPATH": str(REPO),
                "HHS_COGNITION_AUTO_TICK": "0",
                "HHS_DISABLE_C_AUTOBUILD": "1",
                "HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS": "0.25",
                "HHS_RUNTIME_STATUS_PROBE_START_DELAY_SECONDS": "600",
                "HHS_DATA_DIR": str(state_root / "data"),
                "HHS_PASS174_STATE_DIR": str(state_root / "pass174"),
                "HHS_PASS165_STORAGE_DIR": str(state_root / "pass165"),
                "HHS_PASS218_STATE_ROOT": str(state_root / "pass218"),
                "HHS_PASS220_LANE5_TOOL_STATE_ROOT": str(state_root / "pass220-lane5-tools"),
            }
        )
        self._log = self.log_path.open("w", encoding="utf-8")
        started = time.perf_counter_ns()
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                ENTRYPOINT,
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--workers",
                "1",
                "--log-level",
                "info",
            ],
            cwd=REPO,
            env=env,
            stdout=self._log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        timeline: list[dict[str, Any]] = []
        deadline_ns = started + deadline_seconds * 1_000_000_000
        while time.perf_counter_ns() < deadline_ns:
            if self.process.poll() is not None:
                self._log.flush()
                raise AssertionError(
                    {
                        "classification": "EXTERNAL_FRONTEND_SERVER_EXITED_BEFORE_READY",
                        "returncode": self.process.returncode,
                        "log": self.log_path.read_text(
                            encoding="utf-8", errors="replace"
                        )[-12000:],
                    }
                )
            try:
                status, content_type, body = http_fetch(self.base_url + "/", timeout=1.0)
                elapsed_ms = (time.perf_counter_ns() - started) // 1_000_000
                timeline.append({"elapsed_ms": elapsed_ms, "status": status})
                if status == 200 and b"HHS Visual Runtime OS Workspace" in body:
                    return {
                        "entrypoint": ENTRYPOINT,
                        "pid": self.process.pid,
                        "ready_ms": elapsed_ms,
                        "content_type": content_type,
                        "timeline": timeline[-30:],
                    }
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
                timeline.append(
                    {
                        "elapsed_ms": (time.perf_counter_ns() - started) // 1_000_000,
                        "status": "not-listening",
                    }
                )
            time.sleep(0.2)
        self._log.flush()
        raise AssertionError(
            {
                "classification": "EXTERNAL_FRONTEND_SERVER_READY_TIMEOUT",
                "timeline": timeline[-50:],
                "log": self.log_path.read_text(encoding="utf-8", errors="replace")[-12000:],
            }
        )

    def stop(self) -> dict[str, Any]:
        if self.process is None:
            return {"stopped": True, "returncode": None}
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)
        if self._log is not None:
            self._log.flush()
            self._log.close()
            self._log = None
        return {"stopped": True, "returncode": self.process.returncode}


def wav_fixture() -> bytes:
    target = io.BytesIO()
    with wave.open(target, "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(1)
        stream.setframerate(8000)
        stream.writeframes(bytes((128 + ((index % 17) - 8) * 5) & 0xFF for index in range(256)))
    return target.getvalue()


def fixture_matrix() -> list[dict[str, Any]]:
    png = b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    pdf = (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
        b"xref\n0 2\n0000000000 65535 f \n0000000009 00000 n \n"
        b"trailer\n<< /Root 1 0 R /Size 2 >>\nstartxref\n45\n%%EOF\n"
    )
    video = (
        b"\x00\x00\x00\x18ftypisom"
        + b"\x00\x00\x02\x00isomiso2"
        + b"\x00\x00\x00\x08free"
    )
    binary = (bytes(range(256)) * 256) + b"\x00\xff\x80\x00HHS-BINARY-END"
    raw648 = bytes(((index * 37 + 11) & 0xFF) for index in range(648))
    stress = bytes(range(256)) * 1024
    return [
        {
            "name": "exact-source.hhs",
            "mime": "text/plain",
            "modality": "HARMONICODE_SOURCE",
            "expected_detected": "SOURCE_CODE",
            "bytes": (
                "a²=1\nb²=2\nc²=3\nP=72\np=64\nq=81\n"
                "Δ=P²-pq\n(P²-pq)-Δ=0\nx+y=0\n"
            ).encode("utf-8"),
            "require_compute": True,
        },
        {
            "name": "exact.json",
            "mime": "application/json",
            "modality": "JSON",
            "expected_detected": "JSON",
            "bytes": json.dumps(
                {
                    "schema": "HHS_EXTERNAL_FRONTEND_EXACT_JSON_V1",
                    "value": 123,
                    "lexical": "000123.4500",
                    "unicode": "Δ²→Ω",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n",
            "require_compute": False,
        },
        {
            "name": "exact.pdf",
            "mime": "application/pdf",
            "modality": "PDF",
            "expected_detected": "PDF",
            "bytes": pdf,
            "require_compute": False,
        },
        {
            "name": "exact.png",
            "mime": "image/png",
            "modality": "IMAGE",
            "expected_detected": "IMAGE",
            "bytes": png,
            "require_compute": False,
        },
        {
            "name": "exact.wav",
            "mime": "audio/wav",
            "modality": "AUDIO",
            "expected_detected": "AUDIO",
            "bytes": wav_fixture(),
            "require_compute": False,
        },
        {
            "name": "exact.mp4",
            "mime": "video/mp4",
            "modality": "VIDEO",
            "expected_detected": "VIDEO",
            "bytes": video,
            "require_compute": False,
        },
        {
            "name": "exact.bin",
            "mime": "application/octet-stream",
            "modality": "BINARY",
            "expected_detected": "BINARY_OBJECT",
            "bytes": binary,
            "require_compute": False,
        },
        {
            "name": "raw5184.bin",
            "mime": "application/octet-stream",
            "modality": "BINARY",
            "expected_detected": "BINARY_OBJECT",
            "bytes": raw648,
            "require_compute": False,
        },
        {
            "name": "stress-256k.bin",
            "mime": "application/octet-stream",
            "modality": "BINARY",
            "expected_detected": "BINARY_OBJECT",
            "bytes": stress,
            "require_compute": False,
        },
    ]


def source_payload(name: str, modality: str, raw: bytes, *, project_id: str | None = None) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "project_name": "Pass 220 External Frontend Benchmark",
        "source_name": name,
        "source_modality": modality,
        "source_payload": {
            "source_b64": b64encode(raw).decode("ascii"),
            "mime_type": "application/octet-stream",
            "source_size_bytes": len(raw),
        },
        "requested_output": "VALIDATED_ARTIFACT",
        "expression": None,
        "target": "HHS_IR",
        "steps": 8,
        "provenance": "PASS220_EXTERNAL_FRONTEND_BENCHMARK",
        "authorization_scope": "P220_EXTERNAL_FRONTEND_LOSSLESS_PIPELINE",
        "thread": 0,
    }


def page_post_json(page: Page, path: str, body: dict[str, Any], timeout_ms: int = 180000) -> dict[str, Any]:
    result = page.evaluate(
        """
        async ({path, body, timeoutMs}) => {
          const controller = new AbortController();
          const timer = setTimeout(() => controller.abort("benchmark-timeout"), timeoutMs);
          const started = performance.now();
          try {
            const response = await fetch(path, {
              method: "POST",
              headers: {accept: "application/json", "content-type": "application/json"},
              body: JSON.stringify(body),
              signal: controller.signal,
            });
            const raw = await response.text();
            let payload = {};
            try { payload = raw ? JSON.parse(raw) : {}; }
            catch { payload = {raw}; }
            return {
              status: response.status,
              ok: response.ok,
              elapsed_ms: Math.round(performance.now() - started),
              payload,
            };
          } finally {
            clearTimeout(timer);
          }
        }
        """,
        {"path": path, "body": body, "timeoutMs": timeout_ms},
    )
    assert isinstance(result, dict)
    return result


def assert_lossless_result(
    result: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    raw = bytes(fixture["bytes"])
    expected_sha = sha256(raw).hexdigest()
    assert result.get("ok") is True, {
        "fixture": fixture["name"],
        "classification": result.get("classification"),
    }
    assert result.get("frontend_result_fabricated") is False
    assert result.get("source_identity_sha256") == expected_sha

    inherited = result["inherited_lifecycle"]
    ingress_source = inherited["ingress"]["source"]
    snapshot = inherited["vm_snapshot"]
    egress = inherited["egress"]["manifest"]
    continuation = result["pass174_continuation"]
    vector_object = continuation["object"]
    hash216 = vector_object["hash216"]

    assert ingress_source["source_hash"] == expected_sha
    assert ingress_source["byte_length"] == len(raw)
    assert ingress_source["detected_media_type"] == fixture["expected_detected"]
    assert egress["source_sha256"] == expected_sha
    recovered = b64decode(egress["source_b64"], validate=True)
    assert recovered == raw
    assert sha256(recovered).hexdigest() == expected_sha
    assert egress["original_source_preserved"] is True
    assert egress["projection_replaces_source"] is False

    assert snapshot["snapshot_bits"] == 5184
    assert snapshot["snapshot_bytes"] == 648
    assert snapshot["vm81_cells"] == 81
    assert snapshot["bits_per_cell"] == 64
    assert len(b64decode(snapshot["projection_b64"], validate=True)) == 648
    assert len(snapshot["projection_hash72"]) == 72
    assert len(snapshot["ingestion_positions_hash216"]) == 216

    assert len(hash216["predecessor"]) == 72
    assert len(hash216["current"]) == 72
    assert len(hash216["successor"]) == 72
    assert len(hash216["combined"]) == 216
    assert hash216["combined"] == (
        hash216["predecessor"] + hash216["current"] + hash216["successor"]
    )
    assert len(hash216["character_indexes_sha256"]) == 216
    assert vector_object["plaintext_exposed"] is False
    assert len(continuation["receipt"]["receipt_hash72"]) == 72

    stages = {str(item["stage"]): str(item["status"]) for item in result["stages"]}
    for stage in ("PLAN", "GENERATE", "VALIDATE", "RECEIPT"):
        assert stages.get(stage) == "COMPLETED", (fixture["name"], stage, stages)
    if fixture.get("require_compute"):
        for stage in ("INTERPRET", "COMPILE", "RUN"):
            assert stages.get(stage) == "COMPLETED", (fixture["name"], stage, stages)

    return {
        "source_sha256": expected_sha,
        "source_bytes": len(raw),
        "projection_hash72": snapshot["projection_hash72"],
        "operation_key": continuation["operation_key"],
        "vector_hash216": hash216["combined"],
        "egress_source_b64": egress["source_b64"],
        "project_id": result.get("project_id"),
        "stages": stages,
    }


def run_visible_fixture(
    page: Page,
    base_url: str,
    panel,
    file_input,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    raw = bytes(fixture["bytes"])
    file_input.set_input_files(
        {
            "name": fixture["name"],
            "mimeType": fixture["mime"],
            "buffer": raw,
        }
    )
    panel.get_by_text(fixture["name"], exact=True).wait_for(timeout=10000)

    button = panel.get_by_role("button", name="Hydrate vector store", exact=True)
    started = time.perf_counter_ns()
    with page.expect_response(
        lambda response: response.url == base_url + "/api/v1/pass174/sdlc/run"
        and response.request.method == "POST",
        timeout=180000,
    ) as response_info:
        button.click()
    response = response_info.value
    elapsed_ns = time.perf_counter_ns() - started
    body = response.json()
    assert response.status == 200
    proof = assert_lossless_result(body, fixture)

    panel.get_by_text(str(body["classification"]), exact=True).wait_for(timeout=30000)
    operation_key = proof["operation_key"]
    assert isinstance(operation_key, str) and len(operation_key) == 64

    query_started = time.perf_counter_ns()
    with page.expect_response(
        lambda candidate: candidate.url == base_url + "/api/v1/pass174/hash216/query"
        and candidate.request.method == "POST",
        timeout=60000,
    ) as query_info:
        panel.get_by_role("button", name="Read persisted vector", exact=True).click()
    query_response = query_info.value
    query_elapsed_ns = time.perf_counter_ns() - query_started
    query = query_response.json()
    assert query_response.status == 200
    assert query["classification"] == "HHS_PASS_174_VECTOR_QUERY_HIT"
    assert query["mutation_authority"] is False
    assert query["object"]["operation_key"] == operation_key
    assert query["object"]["plaintext_exposed"] is False
    assert len(query["object"]["hash216"]["combined"]) == 216

    # Re-enter the exact source emitted by backend egress through a browser-originated
    # request. Source identity and Pass165 projection must remain stable.
    replay_payload = source_payload(
        fixture["name"],
        fixture["modality"],
        b64decode(proof["egress_source_b64"], validate=True),
        project_id=proof["project_id"],
    )
    reingress = page_post_json(page, "/api/v1/pass174/sdlc/run", replay_payload)
    assert reingress["status"] == 200
    second = assert_lossless_result(reingress["payload"], fixture)
    assert second["source_sha256"] == proof["source_sha256"]
    assert second["projection_hash72"] == proof["projection_hash72"]

    return {
        "name": fixture["name"],
        "modality": fixture["modality"],
        "detected_media_type": fixture["expected_detected"],
        "source_bytes": len(raw),
        "source_sha256": proof["source_sha256"],
        "projection_hash72": proof["projection_hash72"],
        "request_elapsed_ns": elapsed_ns,
        "request_elapsed_ms": elapsed_ns // 1_000_000,
        "throughput_bytes_per_second": (len(raw) * 1_000_000_000) // max(1, elapsed_ns),
        "vector_query_elapsed_ns": query_elapsed_ns,
        "vector_query_elapsed_ms": query_elapsed_ns // 1_000_000,
        "browser_reingress_elapsed_ms": int(reingress["elapsed_ms"]),
        "exact_egress_bytes_equal": True,
        "source_sha256_equal": True,
        "projection_hash72_replay_equal": True,
        "snapshot_5184_exact": True,
        "hash216_216_exact": True,
        "vector_readback": True,
    }


def percentile(values: list[int], percent: int) -> int:
    assert values
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, ((len(ordered) * percent + 99) // 100) - 1))
    return ordered[index]


def run_nonblocking_probe(page: Page, base_url: str) -> dict[str, Any]:
    raw = bytes(range(256)) * 4096  # exactly 1 MiB
    payload = source_payload("nonblocking-1m.bin", "BINARY", raw)
    page.evaluate(
        """
        ({body}) => {
          const state = {
            done: false,
            status: null,
            ok: false,
            error: null,
            started: performance.now(),
            ended: null,
            frames: [],
            payload: null,
          };
          window.__hhsNoBlockBenchmark = state;
          let last = null;
          const tick = (timestamp) => {
            if (last !== null) state.frames.push(Math.round(timestamp - last));
            last = timestamp;
            if (!state.done) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
          fetch("/api/v1/pass174/sdlc/run", {
            method: "POST",
            headers: {accept: "application/json", "content-type": "application/json"},
            body: JSON.stringify(body),
          })
            .then(async (response) => {
              state.status = response.status;
              const rawText = await response.text();
              try { state.payload = rawText ? JSON.parse(rawText) : {}; }
              catch { state.payload = {raw: rawText}; }
              state.ok = response.ok;
            })
            .catch((error) => { state.error = String(error?.message || error); })
            .finally(() => {
              state.ended = performance.now();
              state.done = true;
            });
          return {started: true};
        }
        """,
        {"body": payload},
    )

    probe_ms: list[int] = []
    in_flight = 0
    probe_records: list[dict[str, Any]] = []
    for index in range(16):
        done_before = bool(page.evaluate("window.__hhsNoBlockBenchmark?.done === true"))
        if not done_before:
            in_flight += 1
        started = time.perf_counter_ns()
        status, content_type, body = http_fetch(base_url + PROBE_PATH, timeout=5.0)
        elapsed_ms = (time.perf_counter_ns() - started) // 1_000_000
        probe_ms.append(elapsed_ms)
        assert status == 200, (index, status, body[:500])
        assert "json" in content_type.lower(), (index, content_type)
        probe_records.append(
            {
                "index": index,
                "elapsed_ms": elapsed_ms,
                "request_in_flight_before_probe": not done_before,
            }
        )
        if done_before and in_flight > 0:
            break
        time.sleep(0.03)

    page.wait_for_function(
        "() => window.__hhsNoBlockBenchmark?.done === true",
        timeout=180000,
    )
    state = page.evaluate("window.__hhsNoBlockBenchmark")
    assert state["error"] is None, state
    assert state["status"] == 200, state
    assert state["ok"] is True, state
    fixture = {
        "name": "nonblocking-1m.bin",
        "modality": "BINARY",
        "expected_detected": "BINARY_OBJECT",
        "bytes": raw,
        "require_compute": False,
    }
    assert_lossless_result(state["payload"], fixture)
    assert in_flight >= 1, {
        "classification": "NO_STATUS_PROBE_OBSERVED_WHILE_INGRESS_IN_FLIGHT",
        "state": state,
        "probes": probe_records,
    }
    frame_gaps = [int(value) for value in state.get("frames") or []]
    max_gap = max(frame_gaps) if frame_gaps else 0
    assert max_gap < 1500, {"max_browser_animation_frame_gap_ms": max_gap}
    assert max(probe_ms) < 5000, {"probe_ms": probe_ms}

    return {
        "source_bytes": len(raw),
        "source_sha256": sha256(raw).hexdigest(),
        "request_elapsed_ms": round(int(state["ended"]) - int(state["started"])),
        "status_probe_count": len(probe_ms),
        "status_probes_while_ingress_in_flight": in_flight,
        "status_probe_p50_ms": percentile(probe_ms, 50),
        "status_probe_p95_ms": percentile(probe_ms, 95),
        "status_probe_max_ms": max(probe_ms),
        "browser_animation_frame_samples": len(frame_gaps),
        "browser_animation_frame_max_gap_ms": max_gap,
        "event_loop_responsive": True,
        "server_status_responsive": True,
        "lossless": True,
    }


def run_concurrent_browser_ingress(page: Page) -> dict[str, Any]:
    fixtures: list[tuple[str, bytes]] = []
    for ordinal in range(3):
        prefix = bytes([0xFF, ordinal, 0x00, 0x80])
        raw = prefix + (bytes(range(256)) * 512) + f"END-{ordinal}".encode("ascii")
        fixtures.append((f"concurrent-{ordinal}.bin", raw))
    bodies = [
        source_payload(name, "BINARY", raw)
        for name, raw in fixtures
    ]
    started = time.perf_counter_ns()
    results = page.evaluate(
        """
        async (bodies) => Promise.all(bodies.map(async (body) => {
          const started = performance.now();
          try {
            const response = await fetch("/api/v1/pass174/sdlc/run", {
              method: "POST",
              headers: {accept: "application/json", "content-type": "application/json"},
              body: JSON.stringify(body),
            });
            const payload = await response.json();
            return {
              status: response.status,
              ok: response.ok,
              elapsed_ms: Math.round(performance.now() - started),
              payload,
            };
          } catch (error) {
            return {status: 0, ok: false, elapsed_ms: Math.round(performance.now() - started), error: String(error)};
          }
        }))
        """,
        bodies,
    )
    total_ns = time.perf_counter_ns() - started
    assert len(results) == len(fixtures)

    rows = []
    for (name, raw), result in zip(fixtures, results):
        assert result["status"] == 200 and result["ok"] is True, result
        fixture = {
            "name": name,
            "modality": "BINARY",
            "expected_detected": "BINARY_OBJECT",
            "bytes": raw,
            "require_compute": False,
        }
        proof = assert_lossless_result(result["payload"], fixture)
        rows.append(
            {
                "name": name,
                "source_bytes": len(raw),
                "source_sha256": proof["source_sha256"],
                "elapsed_ms": int(result["elapsed_ms"]),
                "lossless": True,
            }
        )

    return {
        "request_count": len(rows),
        "total_elapsed_ns": total_ns,
        "total_elapsed_ms": total_ns // 1_000_000,
        "all_completed": True,
        "all_lossless": True,
        "requests": rows,
    }


def run_frontend_oversize_preflight(page: Page, base_url: str, panel, file_input) -> dict[str, Any]:
    sdlc_requests: list[str] = []
    handler = lambda request: sdlc_requests.append(request.url) if request.url == base_url + "/api/v1/pass174/sdlc/run" else None
    page.on("request", handler)
    before = len(sdlc_requests)
    page.evaluate(
        """
        ({selector, size}) => {
          const root = document.querySelector(selector);
          const input = root?.querySelector('input[type="file"]');
          if (!input) throw new Error("EXTERNAL_FILE_INPUT_NOT_FOUND");
          const bytes = new Uint8Array(size);
          bytes[0] = 0xff;
          bytes[size - 1] = 0x7f;
          const file = new File([bytes], "oversize.bin", {type: "application/octet-stream"});
          const transfer = new DataTransfer();
          transfer.items.add(file);
          input.files = transfer.files;
          input.dispatchEvent(new Event("change", {bubbles: true}));
        }
        """,
        {
            "selector": '[data-testid="production-mobile-control-center"]',
            "size": CANONICAL_MAX_SOURCE_BYTES + 1,
        },
    )
    panel.get_by_text("oversize.bin", exact=True).wait_for(timeout=10000)
    panel.get_by_role("button", name="Hydrate vector store", exact=True).click()
    page.wait_for_timeout(300)
    after = len(sdlc_requests)
    assert after == before, {
        "classification": "OVERSIZE_FRONTEND_REQUEST_REACHED_BACKEND",
        "before": before,
        "after": after,
    }
    assert "canonical Pass 165 limit of 16 MB" in panel.inner_text()
    page.remove_listener("request", handler)
    return {
        "canonical_limit_bytes": CANONICAL_MAX_SOURCE_BYTES,
        "attempted_bytes": CANONICAL_MAX_SOURCE_BYTES + 1,
        "sdlc_requests_emitted": after - before,
        "blocked_before_network": True,
    }


def run_negative_transport_cases(page: Page) -> dict[str, Any]:
    spoof = page_post_json(
        page,
        "/api/v1/pass174/sdlc/run",
        source_payload("spoof.png", "IMAGE", b"plain text pretending to be a png\n"),
    )
    assert spoof["status"] == 422, spoof
    detail = spoof["payload"].get("detail") or {}
    assert detail.get("classification") == "P165_MEDIA_TYPE_SPOOFING", spoof

    unknown = page.evaluate(
        """
        async () => {
          const response = await fetch("/api/pass220/external-frontend/not-a-route", {
            headers: {accept: "application/json"},
          });
          const contentType = response.headers.get("content-type") || "";
          const text = await response.text();
          return {status: response.status, contentType, text};
        }
        """
    )
    assert unknown["status"] == 404, unknown
    assert "json" in unknown["contentType"].lower(), unknown
    payload = json.loads(unknown["text"])
    assert payload["status"] == "HHS_API_ROUTE_NOT_FOUND"
    assert payload["detail"]["static_fallback_used"] is False
    assert payload["detail"]["frontend_result_fabricated"] is False

    return {
        "media_spoof_status": spoof["status"],
        "media_spoof_classification": detail.get("classification"),
        "unknown_api_status": unknown["status"],
        "unknown_api_json": True,
        "spa_fallback_used": False,
    }


def run_browser(base_url: str, evidence_dir: Path) -> dict[str, Any]:
    page_errors: list[str] = []
    request_failures: list[dict[str, str]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000},
            accept_downloads=True,
        )
        page = context.new_page()
        page.set_default_timeout(45000)
        page.set_default_navigation_timeout(120000)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: request_failures.append(
                {"url": request.url, "failure": request.failure or "unknown"}
            ),
        )

        navigation_started = time.perf_counter_ns()
        response = page.goto(base_url + "/", wait_until="domcontentloaded")
        assert response is not None and response.ok, getattr(response, "status", None)
        page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=90000)
        page.wait_for_selector('[data-testid="production-mobile-control-center"]', timeout=90000)
        frontend_interactive_ms = (time.perf_counter_ns() - navigation_started) // 1_000_000

        panel = page.get_by_test_id("production-mobile-control-center")
        file_input = panel.locator('input[type="file"]').first
        assert file_input.count() == 1

        fixtures = []
        for fixture in fixture_matrix():
            fixtures.append(run_visible_fixture(page, base_url, panel, file_input, fixture))

        nonblocking = run_nonblocking_probe(page, base_url)
        concurrent = run_concurrent_browser_ingress(page)
        negative = run_negative_transport_cases(page)
        oversize = run_frontend_oversize_preflight(page, base_url, panel, file_input)

        page.screenshot(
            path=str(evidence_dir / "external-frontend-lossless-nonblocking.png"),
            full_page=True,
        )
        context.close()
        browser.close()

    relevant_failures = [
        item
        for item in request_failures
        if (
            "/api/v1/pass174/" in item["url"]
            or "/api/runtime/workspace/" in item["url"]
        )
    ]
    assert not page_errors, page_errors
    assert not relevant_failures, relevant_failures

    return {
        "frontend_interactive_ms": frontend_interactive_ms,
        "fixture_count": len(fixtures),
        "fixtures": fixtures,
        "all_fixture_egress_lossless": all(row["exact_egress_bytes_equal"] for row in fixtures),
        "all_fixture_reingress_stable": all(row["projection_hash72_replay_equal"] for row in fixtures),
        "all_fixture_vector_readback": all(row["vector_readback"] for row in fixtures),
        "nonblocking": nonblocking,
        "concurrent": concurrent,
        "negative": negative,
        "oversize_preflight": oversize,
        "page_errors": page_errors,
        "relevant_request_failures": relevant_failures,
        "frontend_runtime_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    server = ExternalFrontendServer(free_port(), evidence_dir)
    started = server.start()
    total_started = time.perf_counter_ns()
    try:
        browser = run_browser(server.base_url, evidence_dir)
        warm_status_code, warm_content_type, warm_body = http_fetch(
            server.base_url + "/api/runtime/pass220/lane5/tools/warm-status",
            timeout=10.0,
        )
        assert warm_status_code == 200
        assert "json" in warm_content_type.lower()
        warm_status = json.loads(warm_body)
        assert warm_status["lane5_selection_changed"] is False
        assert warm_status["candidate_only"] is True

        result = {
            "schema": "HHS_PASS_220_EXTERNAL_FRONTEND_INGRESS_EGRESS_LOSSLESS_NONBLOCKING_BENCHMARK_V1",
            "ok": True,
            "classification": "HHS_PASS_220_EXTERNAL_FRONTEND_PIPELINE_LOSSLESS_NONBLOCKING_VERIFIED",
            "entrypoint": ENTRYPOINT,
            "server": started,
            "browser": browser,
            "lane5_tool_warm_status": warm_status,
            "canonical_source_limit_bytes": CANONICAL_MAX_SOURCE_BYTES,
            "lossless_information_preservation": True,
            "external_frontend_nonblocking": True,
            "lane5_selection_changed": False,
            "benchmark_timing_is_canonical_authority": False,
            "frontend_runtime_authority": False,
            "elapsed_ms": (time.perf_counter_ns() - total_started) // 1_000_000,
        }
        output = evidence_dir / "external-frontend-lossless-nonblocking.json"
        output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        server.stop()


if __name__ == "__main__":
    main()

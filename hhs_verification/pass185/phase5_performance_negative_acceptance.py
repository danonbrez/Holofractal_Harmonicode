from __future__ import annotations

import argparse
import json
import math
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

from playwright.sync_api import Browser, BrowserContext, Page, Route, sync_playwright

from hhs_verification.pass185.phase2_degradation_negative_acceptance import (
    ProductionServer,
    free_port,
)

ENTRYPOINT = "hhs_backend.runtime_os_application_server:app"
STARTUP_DEADLINE_MS = 45_000
HEALTH_P95_GATE_MS = 250.0
EVENT_LOOP_YIELD_GATE_MS = 100.0
IDLE_CPU_WINDOW_SECONDS = 10.5
IDLE_FULL_CORE_GATE_PERCENT = 95.0
BROWSER_EDITOR_GATE_MS = 500.0
BROWSER_LONG_TASK_RECORD_MS = 200.0
BROWSER_LONG_TASK_HARD_BOUND_MS = 1000.0


def request(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 2.0,
) -> tuple[int, str, bytes, float]:
    data = None
    headers = {"accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["content-type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read()
            elapsed_ms = (time.perf_counter() - started) * 1000
            return int(response.status), str(response.headers.get("content-type", "")), body, elapsed_ms
    except urllib.error.HTTPError as exc:
        body = exc.read()
        elapsed_ms = (time.perf_counter() - started) * 1000
        return int(exc.code), str(exc.headers.get("content-type", "")), body, elapsed_ms


def json_request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 2.0,
    expected_status: int = 200,
) -> tuple[dict[str, Any], float]:
    status, content_type, body, elapsed_ms = request(
        base_url + path,
        method=method,
        payload=payload,
        timeout=timeout,
    )
    assert status == expected_status, {
        "path": path,
        "status": status,
        "body": body[:1000].decode("utf-8", "replace"),
    }
    assert "json" in content_type.lower(), {"path": path, "content_type": content_type}
    value = json.loads(body)
    assert isinstance(value, dict)
    return value, elapsed_ms


def proc_sample(pid: int) -> dict[str, Any]:
    stat = Path(f"/proc/{pid}/stat").read_text().split()
    status_lines = Path(f"/proc/{pid}/status").read_text().splitlines()
    io_lines = Path(f"/proc/{pid}/io").read_text().splitlines()
    status = {}
    for line in status_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            status[key] = value.strip()
    io = {}
    for line in io_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            io[key] = int(value.strip())
    rss_kib = int(status.get("VmRSS", "0 kB").split()[0])
    return {
        "monotonic": time.monotonic(),
        "cpu_ticks": int(stat[13]) + int(stat[14]),
        "rss_kib": rss_kib,
        "read_bytes": int(io.get("read_bytes", 0)),
        "write_bytes": int(io.get("write_bytes", 0)),
    }


def cpu_percent(first: dict[str, Any], last: dict[str, Any]) -> float:
    ticks_per_second = float(os.sysconf(os.sysconf_names["SC_CLK_TCK"]))
    cpu_seconds = (last["cpu_ticks"] - first["cpu_ticks"]) / ticks_per_second
    wall = max(0.000001, last["monotonic"] - first["monotonic"])
    return (cpu_seconds / wall) * 100.0


def percentile(values: list[float], fraction: float) -> float:
    assert values
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1))
    return ordered[index]


def runtime_projection(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        if (
            "state_hash72" in payload
            and ("step" in payload or "receipt_hash72" in payload)
        ):
            return payload
        for value in payload.values():
            found = runtime_projection(value)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = runtime_projection(value)
            if found is not None:
                return found
    return None


def wait_ready_with_samples(
    server: ProductionServer,
    *,
    deadline_ms: int = STARTUP_DEADLINE_MS,
) -> dict[str, Any]:
    assert server.process is not None
    started = time.monotonic()
    samples: list[dict[str, Any]] = []
    timeline: list[dict[str, Any]] = []
    deadline = started + deadline_ms / 1000
    while time.monotonic() < deadline:
        if server.process.poll() is not None:
            raise AssertionError(
                {
                    "classification": "PHASE5_SERVER_EXITED_BEFORE_READY",
                    "returncode": server.process.returncode,
                }
            )
        samples.append(proc_sample(server.process.pid))
        try:
            status, content_type, body, latency = request(
                server.base_url + "/",
                timeout=0.8,
            )
            timeline.append(
                {
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "status": status,
                    "latency_ms": round(latency, 3),
                }
            )
            if status == 200 and b"HHS Visual Runtime OS Workspace" in body:
                ready_ms = round((time.monotonic() - started) * 1000)
                assert ready_ms < deadline_ms
                return {
                    "ready_ms": ready_ms,
                    "content_type": content_type,
                    "samples": samples,
                    "timeline": timeline[-40:],
                }
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            timeline.append(
                {
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "status": "not-listening",
                }
            )
        time.sleep(0.25)
    raise AssertionError(
        {
            "classification": "PHASE5_STARTUP_DEADLINE_EXCEEDED",
            "deadline_ms": deadline_ms,
            "timeline": timeline[-40:],
        }
    )


def resolve_lightweight_health_path(base_url: str) -> str:
    attempts: list[dict[str, Any]] = []
    for path in ("/api/health", "/health"):
        try:
            status, content_type, body, elapsed_ms = request(
                base_url + path,
                timeout=1.0,
            )
            attempts.append({
                "path": path,
                "status": status,
                "content_type": content_type,
                "elapsed_ms": round(elapsed_ms, 3),
            })
            if status == 200 and "json" in content_type.lower():
                payload = json.loads(body)
                if isinstance(payload, dict):
                    return path
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            attempts.append({"path": path, "error": f"{type(exc).__name__}: {exc}"})
    raise AssertionError({
        "classification": "PHASE5_LIGHTWEIGHT_HEALTH_ROUTE_UNAVAILABLE",
        "attempts": attempts,
    })


def health_latency_gate(base_url: str, health_path: str) -> dict[str, Any]:
    latencies: list[float] = []
    timeout_samples = 0
    timeout_ms = 1000.0
    for _ in range(40):
        try:
            payload, elapsed_ms = json_request(
                base_url,
                health_path,
                timeout=timeout_ms / 1000,
            )
            assert isinstance(payload, dict)
            latencies.append(elapsed_ms)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            timeout_samples += 1
            latencies.append(timeout_ms)
        time.sleep(0.025)
    p95 = percentile(latencies, 0.95)
    assert p95 < HEALTH_P95_GATE_MS, {
        "health_path": health_path,
        "p95_ms": p95,
        "timeout_samples": timeout_samples,
        "samples_ms": latencies,
    }
    return {
        "health_path": health_path,
        "count": len(latencies),
        "timeout_samples": timeout_samples,
        "p50_ms": round(percentile(latencies, 0.50), 3),
        "p95_ms": round(p95, 3),
        "max_ms": round(max(latencies), 3),
        "gate_ms": HEALTH_P95_GATE_MS,
    }


def idle_resource_gate(server: ProductionServer) -> dict[str, Any]:
    assert server.process is not None
    before_authority, _ = json_request(server.base_url, "/api/runtime/authority/status")
    before_runtime = runtime_projection(before_authority)
    assert before_runtime is not None, before_authority

    samples = [proc_sample(server.process.pid)]
    deadline = time.monotonic() + IDLE_CPU_WINDOW_SECONDS
    while time.monotonic() < deadline:
        time.sleep(0.5)
        samples.append(proc_sample(server.process.pid))

    after_authority, _ = json_request(server.base_url, "/api/runtime/authority/status")
    after_runtime = runtime_projection(after_authority)
    assert after_runtime is not None, after_authority

    cpu = cpu_percent(samples[0], samples[-1])
    assert cpu < IDLE_FULL_CORE_GATE_PERCENT, {
        "idle_cpu_percent": cpu,
        "gate_percent": IDLE_FULL_CORE_GATE_PERCENT,
    }
    assert before_runtime.get("step") == after_runtime.get("step"), {
        "before_step": before_runtime.get("step"),
        "after_step": after_runtime.get("step"),
    }
    assert before_runtime.get("state_hash72") == after_runtime.get("state_hash72"), {
        "before_state_hash72": before_runtime.get("state_hash72"),
        "after_state_hash72": after_runtime.get("state_hash72"),
    }
    assert after_authority.get("frontend_is_authority") is False
    assert after_authority.get("authority") == "HHS_FASTAPI_KERNEL_RUNTIME_AUTHORITY_V1"

    return {
        "window_seconds": round(samples[-1]["monotonic"] - samples[0]["monotonic"], 3),
        "cpu_percent": round(cpu, 3),
        "full_core_gate_percent": IDLE_FULL_CORE_GATE_PERCENT,
        "max_rss_kib": max(sample["rss_kib"] for sample in samples),
        "read_bytes_delta": samples[-1]["read_bytes"] - samples[0]["read_bytes"],
        "write_bytes_delta": samples[-1]["write_bytes"] - samples[0]["write_bytes"],
        "runtime_step_stable": True,
        "runtime_state_hash72_stable": True,
        "canonical_authority": after_authority.get("authority"),
        "frontend_is_authority": False,
    }


def event_loop_yield_gate(base_url: str, health_path: str) -> dict[str, Any]:
    samples: list[float] = []
    failures: list[str] = []
    stop = threading.Event()

    def sampler() -> None:
        while not stop.is_set():
            try:
                _, elapsed_ms = json_request(
                    base_url,
                    health_path,
                    timeout=0.5,
                )
                samples.append(elapsed_ms)
            except Exception as exc:  # evidence captured below
                failures.append(f"{type(exc).__name__}: {exc}")
            time.sleep(0.01)

    thread = threading.Thread(target=sampler, daemon=True)
    thread.start()
    time.sleep(0.15)
    step_latencies: list[float] = []
    try:
        for _ in range(3):
            body, elapsed_ms = json_request(
                base_url,
                "/api/runtime/step",
                method="POST",
                payload={"steps": 1},
                timeout=15.0,
            )
            assert body
            step_latencies.append(elapsed_ms)
    finally:
        time.sleep(0.2)
        stop.set()
        thread.join(timeout=2)

    assert not failures, failures
    assert samples, "no concurrent health samples"
    maximum = max(samples)
    assert maximum < EVENT_LOOP_YIELD_GATE_MS, {
        "max_health_latency_ms": maximum,
        "gate_ms": EVENT_LOOP_YIELD_GATE_MS,
        "samples_ms": samples,
        "step_latencies_ms": step_latencies,
    }
    return {
        "health_samples": len(samples),
        "max_health_latency_ms": round(maximum, 3),
        "p95_health_latency_ms": round(percentile(samples, 0.95), 3),
        "yield_gate_ms": EVENT_LOOP_YIELD_GATE_MS,
        "authorized_step_latencies_ms": [round(value, 3) for value in step_latencies],
    }


def open_workspace(page: Page) -> None:
    page.locator('[data-testid="hhs-product-workspace"] > nav').get_by_role(
        "button", name="Workspace", exact=True
    ).click()
    page.wait_for_selector('[data-testid="hhs-visual-runtime-os-workspace"]')


def open_tab(page: Page, name: str) -> None:
    page.locator('[data-testid="hhs-visual-runtime-os-workspace"]').get_by_role(
        "button", name=name, exact=True
    ).click()


def healthy_browser_gate(browser: Browser, base_url: str, evidence_dir: Path) -> dict[str, Any]:
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    context.add_init_script(
        """(() => {
          window.__HHS_PHASE5_LONG_TASKS__ = [];
          if ('PerformanceObserver' in window) {
            try {
              const observer = new PerformanceObserver(list => {
                for (const entry of list.getEntries()) {
                  window.__HHS_PHASE5_LONG_TASKS__.push({
                    startTime: entry.startTime,
                    duration: entry.duration,
                    name: entry.name
                  });
                }
              });
              observer.observe({ type: 'longtask', buffered: true });
              window.__HHS_PHASE5_LONG_TASK_OBSERVER__ = observer;
            } catch (_) {}
          }
        })();"""
    )
    page = context.new_page()
    page.set_default_timeout(30_000)
    response = page.goto(base_url + "/", wait_until="domcontentloaded")
    assert response is not None and response.ok
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    open_workspace(page)

    # Duplicate visible control binding: one Right click must move exactly one cell.
    open_tab(page, "Multimodal")
    page.wait_for_selector('[data-testid="pass185-multimodal-lifecycle"]')
    page.get_by_test_id("pass185-mm-mode-game").click()
    position = page.get_by_test_id("pass185-mm-game-position")
    assert position.inner_text() == "x=1 y=1"
    page.get_by_test_id("pass185-mm-game-right").click()
    assert position.inner_text() == "x=2 y=1"

    # Editor responsiveness while optional product-health/provider probes run.
    page.get_by_test_id("pass185-mm-mode-document").click()
    editor = page.get_by_test_id("pass185-mm-document-editor")
    preview = page.get_by_test_id("pass185-mm-document-preview")
    page.evaluate(
        """() => {
          window.__HHS_PHASE5_PROBES__ = Promise.all(
            Array.from({length: 6}, () =>
              fetch('/api/product/health', {cache: 'no-store'})
                .then(r => r.json())
                .catch(error => ({ok: false, error: String(error)}))
            )
          );
        }"""
    )
    marker = "Phase 5 editor remains responsive during optional capability probes."
    started = time.perf_counter()
    editor.fill(marker)
    page.wait_for_function(
        """expected => document.querySelector('[data-testid="pass185-mm-document-preview"]')?.textContent === expected""",
        arg=marker,
        timeout=3_000,
    )
    editor_latency_ms = (time.perf_counter() - started) * 1000
    assert editor_latency_ms < BROWSER_EDITOR_GATE_MS, editor_latency_ms
    probes = page.evaluate("async () => await window.__HHS_PHASE5_PROBES__")
    assert isinstance(probes, list) and len(probes) == 6

    # Malformed recovery payload must be ignored and fall back to the empty lifecycle.
    page.evaluate(
        """() => localStorage.setItem(
          'hhs.pass185.production-lifecycle.v1',
          JSON.stringify({schema:'WRONG_SCHEMA', sourceText: 42, projectId: {bad:true}})
        )"""
    )
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    open_workspace(page)
    open_tab(page, "Application")
    page.wait_for_selector('[data-testid="pass185-application-lifecycle"]')
    app_status = page.get_by_test_id("pass185-lifecycle-status").inner_text()
    assert app_status == "EMPTY", app_status

    long_tasks = page.evaluate("() => window.__HHS_PHASE5_LONG_TASKS__ || []")
    durations = [float(item.get("duration", 0)) for item in long_tasks if isinstance(item, dict)]
    over_record = [value for value in durations if value > BROWSER_LONG_TASK_RECORD_MS]
    maximum = max(durations, default=0.0)
    assert maximum < BROWSER_LONG_TASK_HARD_BOUND_MS, {
        "max_long_task_ms": maximum,
        "hard_bound_ms": BROWSER_LONG_TASK_HARD_BOUND_MS,
        "long_tasks": long_tasks,
    }

    page.screenshot(path=str(evidence_dir / "phase5-healthy-browser.png"), full_page=True)
    context.close()
    return {
        "duplicate_control_binding": "ONE_CLICK_ONE_GAME_CELL",
        "editor_probe_latency_ms": round(editor_latency_ms, 3),
        "editor_gate_ms": BROWSER_EDITOR_GATE_MS,
        "optional_probe_count": len(probes),
        "long_task_count": len(durations),
        "long_tasks_above_200ms": len(over_record),
        "max_long_task_ms": round(maximum, 3),
        "long_task_hard_bound_ms": BROWSER_LONG_TASK_HARD_BOUND_MS,
        "malformed_recovery_status": app_status,
    }


def boot_watchdog_case(
    browser: Browser,
    base_url: str,
    evidence_dir: Path,
    *,
    name: str,
    main_body: str,
    extra_routes: Callable[[Page], None] | None = None,
) -> dict[str, Any]:
    context = browser.new_context(viewport={"width": 1100, "height": 780})
    page = context.new_page()
    if extra_routes is not None:
        extra_routes(page)
    page.route(
        "**/assets/*.js",
        lambda route: route.fulfill(
            status=200,
            content_type="text/javascript",
            body=main_body,
        ),
    )
    response = page.goto(base_url + "/", wait_until="domcontentloaded")
    assert response is not None and response.ok
    page.wait_for_function(
        "() => Boolean(document.documentElement.dataset.hhsBootFailure)",
        timeout=15_000,
    )
    failure = page.locator("html").get_attribute("data-hhs-boot-failure")
    assert failure
    assert page.locator("#runtime_boot_overlay").is_visible()
    assert page.locator("#runtime_boot_reload").is_visible()

    page.unroute("**/assets/*.js")
    page.locator("#runtime_boot_reload").click()
    page.wait_for_selector('[data-testid="hhs-canonical-runtime-ide"]', timeout=60_000)
    page.screenshot(path=str(evidence_dir / f"phase5-negative-{name}.png"), full_page=True)
    context.close()
    return {
        "finite_visible_failure": True,
        "boot_failure": failure,
        "reload_recovered": True,
    }


def residual_negative_gate(browser: Browser, base_url: str, evidence_dir: Path) -> dict[str, Any]:
    never = boot_watchdog_case(
        browser,
        base_url,
        evidence_dir,
        name="never-resolving-boot",
        main_body="await new Promise(() => {});",
    )
    parser = boot_watchdog_case(
        browser,
        base_url,
        evidence_dir,
        name="self-dependent-parser-event",
        main_body=(
            "await new Promise(resolve => "
            "addEventListener('hhs-phase5-parser-complete', resolve, {once:true}));"
            "dispatchEvent(new Event('hhs-phase5-parser-complete'));"
        ),
    )
    missing_dom = boot_watchdog_case(
        browser,
        base_url,
        evidence_dir,
        name="missing-required-dom",
        main_body=(
            "if (!document.getElementById('hhs-phase5-required-dom')) "
            "throw new Error('HHS_PHASE5_MISSING_REQUIRED_DOM');"
        ),
    )

    def cycle_routes(page: Page) -> None:
        page.route(
            "**/phase5-cycle-a.js",
            lambda route: route.fulfill(
                status=200,
                content_type="text/javascript",
                body="await import('/phase5-cycle-b.js');",
            ),
        )
        page.route(
            "**/phase5-cycle-b.js",
            lambda route: route.fulfill(
                status=200,
                content_type="text/javascript",
                body="await import('/phase5-cycle-a.js');",
            ),
        )

    circular = boot_watchdog_case(
        browser,
        base_url,
        evidence_dir,
        name="circular-boot-dependency",
        main_body="await import('/phase5-cycle-a.js');",
        extra_routes=cycle_routes,
    )

    collision, _ = json_request(
        base_url,
        "/api/pass185-does-not-exist",
        timeout=5.0,
        expected_status=404,
    )
    assert collision.get("status") == "HHS_API_ROUTE_NOT_FOUND", collision
    return {
        "never_resolving_boot": never,
        "self_dependent_parser_event": parser,
        "missing_required_dom": missing_dom,
        "circular_boot_dependency": circular,
        "api_route_collision": {
            "status": 404,
            "classification": collision.get("status"),
            "html_spa_fallback": False,
        },
    }


def browser_gate(base_url: str, evidence_dir: Path) -> dict[str, Any]:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        healthy = healthy_browser_gate(browser, base_url, evidence_dir)
        negatives = residual_negative_gate(browser, base_url, evidence_dir)
        browser.close()
    return {"healthy": healthy, "negatives": negatives}


def recovery_gate(evidence_dir: Path, previous: ProductionServer) -> tuple[dict[str, Any], ProductionServer]:
    started = time.perf_counter()
    stopped = previous.stop()
    stop_ms = (time.perf_counter() - started) * 1000
    assert stop_ms < 10_000, stop_ms

    recovered = ProductionServer(
        previous.port,
        evidence_dir,
        env={
            "HHS_COGNITION_AUTO_TICK": "0",
            "HHS_DISABLE_C_AUTOBUILD": "1",
            "HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS": "0.25",
        },
        label="phase5-recovery-server",
    )
    recovered.start(wait_ready=False)
    startup = wait_ready_with_samples(recovered)
    recovery_health_path = resolve_lightweight_health_path(recovered.base_url)
    health = health_latency_gate(recovered.base_url, recovery_health_path)
    return (
        {
            "stop": stopped,
            "stop_ms": round(stop_ms, 3),
            "restart": startup,
            "post_recovery_health": health,
        },
        recovered,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()
    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)

    port = free_port()
    server = ProductionServer(
        port,
        evidence_dir,
        env={
            "HHS_COGNITION_AUTO_TICK": "0",
            "HHS_DISABLE_C_AUTOBUILD": "1",
            "HHS_ASSISTANT_HEALTH_TIMEOUT_SECONDS": "0.25",
        },
        label="phase5-production-server",
    )
    server.start(wait_ready=False)
    active_server = server
    overall_started = time.monotonic()

    try:
        startup = wait_ready_with_samples(server)
        health_path = resolve_lightweight_health_path(server.base_url)
        health = health_latency_gate(server.base_url, health_path)
        idle = idle_resource_gate(server)
        event_loop = event_loop_yield_gate(server.base_url, health_path)
        browser = browser_gate(server.base_url, evidence_dir)
        recovery, active_server = recovery_gate(evidence_dir, server)

        result = {
            "schema": "HHS_PASS185_I141_PHASE5_PERFORMANCE_NEGATIVE_ACCEPTANCE_V1",
            "ok": True,
            "classification": "HHS_PASS_185_PHASE5_PERFORMANCE_NEGATIVE_VERIFIED",
            "entrypoint": ENTRYPOINT,
            "startup": startup,
            "idle_health": health,
            "idle_resources": idle,
            "event_loop": event_loop,
            "browser": browser,
            "recovery": recovery,
            "gates": {
                "startup_deadline_ms": STARTUP_DEADLINE_MS,
                "health_p95_ms": HEALTH_P95_GATE_MS,
                "event_loop_yield_ms": EVENT_LOOP_YIELD_GATE_MS,
                "idle_full_core_percent": IDLE_FULL_CORE_GATE_PERCENT,
                "browser_editor_ms": BROWSER_EDITOR_GATE_MS,
                "browser_long_task_record_ms": BROWSER_LONG_TASK_RECORD_MS,
                "browser_long_task_hard_bound_ms": BROWSER_LONG_TASK_HARD_BOUND_MS,
            },
            "timing_and_resource_values_are_noncanonical_evidence": True,
            "frontend_runtime_authority": False,
            "terminal_pass185_completion_claimed": False,
            "elapsed_ms": round((time.monotonic() - overall_started) * 1000),
        }
        (evidence_dir / "phase5-performance-negative.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        active_server.stop()


if __name__ == "__main__":
    main()

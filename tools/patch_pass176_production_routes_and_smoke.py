#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
server_path = ROOT / "hhs_backend" / "production_server.py"
server = server_path.read_text(encoding="utf-8")

import_anchor = "from hhs_backend.api.pass166_word2vec_routes import router as word2vec_router\n"
import_addition = """from hhs_backend.api.pass175_runtime_routes import router as pass175_runtime_router
from hhs_backend.api.pass175_terminal_routes import router as pass175_terminal_router
from hhs_backend.api.pass175_terminal_ws_routes import router as pass175_terminal_ws_router
from hhs_backend.api.pass175_ws_routes import router as pass175_ws_router
from hhs_backend.api.repository_history_routes import router as repository_history_router
"""
if import_addition not in server:
    if import_anchor not in server:
        raise SystemExit("PASS176_PRODUCTION_IMPORT_ANCHOR_MISSING")
    server = server.replace(import_anchor, import_anchor + import_addition)

route_anchor = """if not _has_route_prefix("/api/runtime/development"):
    app.include_router(development_lifecycle_router)
"""
route_addition = """if not _has_route_prefix("/api/runtime/repository"):
    app.include_router(repository_history_router)
if not _has_route_prefix("/api/v1/pass175/terminal"):
    app.include_router(pass175_terminal_router)
if not _has_route_prefix("/api/v1/pass175"):
    app.include_router(pass175_runtime_router)
if not _has_route_prefix("/api/v1/pass175/terminal/ws"):
    app.include_router(pass175_terminal_ws_router)
if not _has_route_prefix("/api/v1/pass175/ws"):
    app.include_router(pass175_ws_router)
"""
if route_addition not in server:
    if route_anchor not in server:
        raise SystemExit("PASS176_PRODUCTION_ROUTE_ANCHOR_MISSING")
    server = server.replace(route_anchor, route_anchor + route_addition)

for token in [
    "repository_history_router",
    "pass175_runtime_router",
    "pass175_terminal_router",
    "pass175_ws_router",
    "pass175_terminal_ws_router",
]:
    if token not in server:
        raise SystemExit(f"PASS176_PRODUCTION_ROUTE_TOKEN_MISSING:{token}")
server_path.write_text(server, encoding="utf-8")

smoke_path = ROOT / "applications" / "holofractal_harmonizer" / "ux_lab" / "pass176_stability_smoke.py"
smoke = smoke_path.read_text(encoding="utf-8")
smoke = smoke.replace(
    "        request_failures: list[dict[str, str]] = []\n",
    "        request_failures: list[dict[str, str]] = []\n        http_errors: list[dict[str, object]] = []\n",
)
request_anchor = """        page.on(
            "requestfailed",
            lambda request: request_failures.append({
                "url": request.url,
                "failure": request.failure or "unknown request failure",
            }),
        )
"""
response_listener = """        page.on(
            "response",
            lambda response: http_errors.append({
                "url": response.url,
                "status": response.status,
            }) if response.status >= 400 else None,
        )
"""
if response_listener not in smoke:
    if request_anchor not in smoke:
        raise SystemExit("PASS176_SMOKE_REQUEST_ANCHOR_MISSING")
    smoke = smoke.replace(request_anchor, request_anchor + response_listener)

old_mobile = """            current_phase = "mobile-pane-cycle-setup"
            dock = page.locator(".ide-mobile-dock [data-mobile-pane]")
            dock_count = dock.count()
            if dock_count <= 0:
                raise AssertionError("Pass 176 mobile pane controls are absent")
            for index in range(100):
                current_phase = f"mobile-pane-cycle-{index + 1}"
                dock.nth(index % dock_count).dispatch_event("click", timeout=2_000)
                if (index + 1) % 10 == 0:
                    phase("mobile-pane-cycle-progress", completed=index + 1, controls=dock_count)
"""
new_mobile = """            current_phase = "mobile-pane-cycle-setup"
            stable_panes = page.evaluate("""() => {
                const supported = new Set(['editor', 'lifecycle', 'terminal', 'spatial']);
                return [...document.querySelectorAll('.ide-mobile-dock [data-mobile-pane]')]
                    .map((button) => button.dataset.mobilePane)
                    .filter((pane, index, values) => supported.has(pane) && values.indexOf(pane) === index);
            }""")
            if set(stable_panes) != {"editor", "lifecycle", "terminal", "spatial"}:
                raise AssertionError(f"Pass 176 stable mobile panes are incomplete: {stable_panes}")
            for pane in stable_panes:
                page.locator(f'.ide-mobile-dock [data-mobile-pane="{pane}"]').first.dispatch_event(
                    "click", timeout=2_000
                )
            for index in range(100):
                current_phase = f"mobile-pane-cycle-{index + 1}"
                pane = stable_panes[index % len(stable_panes)]
                selected = page.evaluate("""(requested) => {
                    window.HHSGUIReliability.selectMobilePane(requested);
                    return {
                        requested,
                        selected: window.HHSGUIReliability.mobilePane,
                        layout: document.querySelector('#ide-layout')?.dataset.mobilePane,
                    };
                }""", pane)
                if selected["selected"] != pane or selected["layout"] != pane:
                    raise AssertionError(f"mobile pane selection diverged: {selected}")
                if (index + 1) % 10 == 0:
                    phase("mobile-pane-cycle-progress", completed=index + 1, controls=len(stable_panes))
"""
if old_mobile not in smoke:
    raise SystemExit("PASS176_SMOKE_MOBILE_BLOCK_MISSING")
smoke = smoke.replace(old_mobile, new_mobile)

smoke = smoke.replace(
    '            if console_errors:\n                raise AssertionError(f"console errors observed: {console_errors}")\n',
    '            if http_errors:\n                raise AssertionError(f"HTTP errors observed: {http_errors}")\n            if console_errors:\n                raise AssertionError(f"console errors observed: {console_errors}")\n',
)
smoke = smoke.replace(
    '                "request_failures": request_failures,\n                "external_vercel_status_considered": False,\n',
    '                "request_failures": request_failures,\n                "http_errors": http_errors,\n                "external_vercel_status_considered": False,\n',
)
smoke = smoke.replace(
    '                "request_failures": request_failures,\n                "elapsed_ms": round((time.monotonic() - started) * 1000),\n',
    '                "request_failures": request_failures,\n                "http_errors": http_errors,\n                "elapsed_ms": round((time.monotonic() - started) * 1000),\n',
)
for token in ["stable_panes", "HHSGUIReliability.selectMobilePane", "http_errors"]:
    if token not in smoke:
        raise SystemExit(f"PASS176_SMOKE_PATCH_TOKEN_MISSING:{token}")
smoke_path.write_text(smoke, encoding="utf-8")

verify_path = ROOT / "hhs_verification" / "pass176" / "verify.py"
verify = verify_path.read_text(encoding="utf-8")
verify = verify.replace(
    '        "page_errors_clean": browser.get("page_errors") == [],\n',
    '        "page_errors_clean": browser.get("page_errors") == [],\n        "http_errors_clean": browser.get("http_errors") == [],\n',
)
verify_path.write_text(verify, encoding="utf-8")

print("PASS176_PRODUCTION_ROUTES_AND_STABLE_MOBILE_SMOKE_PATCHED")

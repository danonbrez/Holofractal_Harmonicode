from __future__ import annotations

# Validation-only carrier: functional behavior is already merged on main.
import asyncio
from contextlib import asynccontextmanager

from hhs_backend import pass174_server as server


def test_readiness_failure_preserves_web_service(monkeypatch) -> None:
    async def rejected_probe() -> None:
        raise RuntimeError("SIMULATED_HEROKU_PEER_FAILURE")

    monkeypatch.setattr(server, "_pass174_readiness_probe", rejected_probe)
    result = asyncio.run(server.initialize_pass174_overlay())

    assert result is False
    assert server.PASS174_BOOT_STATE["service_available"] is True
    assert server.PASS174_BOOT_STATE["authority_ready"] is False
    assert server.PASS174_BOOT_STATE["degraded"] is True
    assert server.PASS174_BOOT_STATE["classification"] == "HHS_P174_BOOT_PEER_FAILURE"
    assert "SIMULATED_HEROKU_PEER_FAILURE" in server.PASS174_BOOT_STATE["detail"]


def test_lifespan_yields_while_background_probe_is_degraded(monkeypatch) -> None:
    entered = {"inherited": False, "probe": False, "served": False}

    @asynccontextmanager
    async def inherited_lifespan(_app):
        entered["inherited"] = True
        yield

    async def degraded_initialize() -> bool:
        entered["probe"] = True
        server.PASS174_BOOT_STATE.update({
            "classification": "HHS_P174_BOOT_PEER_FAILURE",
            "ready": False,
            "authority_ready": False,
            "service_available": True,
            "degraded": True,
        })
        return False

    monkeypatch.setattr(server, "_inherited_lifespan", inherited_lifespan)
    monkeypatch.setattr(server, "initialize_pass174_overlay", degraded_initialize)

    async def exercise() -> None:
        async with server._pass174_lifespan(object()):
            entered["served"] = True
            await asyncio.sleep(0)

    asyncio.run(exercise())

    assert entered == {"inherited": True, "probe": True, "served": True}
    assert server.PASS174_BOOT_STATE["service_available"] is True
    assert server.PASS174_BOOT_STATE["authority_ready"] is False
    assert server.PASS174_BOOT_STATE["degraded"] is True


def test_pass174_routes_precede_static_root() -> None:
    paths = [str(getattr(route, "path", "")) for route in server.app.router.routes]
    names = [getattr(route, "name", None) for route in server.app.router.routes]

    assert "/api/v1/pass174/status" in paths
    assert "/api/v1/pass174/deployment/status" in paths
    assert "hhs-pass174-visual-ide" in names
    assert paths.index("/api/v1/pass174/status") < names.index("hhs-pass174-visual-ide")

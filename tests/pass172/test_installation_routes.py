from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from hhs_backend.api import installation_routes


@pytest.mark.asyncio
async def test_installation_routes_are_read_only(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HHS_HOME", str(tmp_path / "home"))
    before = list(tmp_path.rglob("*"))
    status = await installation_routes.installation_status_route()
    profile = await installation_routes.installation_profile_route()
    receipts = await installation_routes.installation_receipts_route()
    after = list(tmp_path.rglob("*"))
    assert status["host_mutation_performed"] is False
    assert profile["host_mutation_performed"] is False
    assert receipts["host_mutation_performed"] is False
    assert before == after


def test_router_exposes_required_read_only_paths() -> None:
    paths = {route.path for route in installation_routes.router.routes}
    assert paths == {
        "/api/runtime/installation/status",
        "/api/runtime/installation/environment",
        "/api/runtime/installation/profile",
        "/api/runtime/installation/dependencies",
        "/api/runtime/installation/receipts",
        "/api/runtime/installation/health",
    }
    for route in installation_routes.router.routes:
        assert route.methods == {"GET"}

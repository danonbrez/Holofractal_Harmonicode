from __future__ import annotations

import asyncio

from hhs_backend.api.a0_repository_status_routes import bounded_repository_history_status
from hhs_backend.runtime.hhs_pass201_public_api_federation_v1 import PublicAPIFederation


def test_repository_status_is_bounded_and_defers_catalog_hydration() -> None:
    payload = asyncio.run(bounded_repository_history_status())
    assert payload["ok"] is True
    assert payload["catalog_state"] == "DEFERRED_UNTIL_EXPLICIT_PASS_CATALOG_REQUEST"
    assert payload["history_hydration"] == "USER_INITIATED"
    assert payload["status_read_is_bounded"] is True
    assert payload["pass_count"] is None
    assert payload["pass_file_count"] is None


def test_bounded_repository_status_precedes_heavy_catalog_router_in_federation() -> None:
    names = PublicAPIFederation._iter_module_names("hhs_backend.api")
    bounded = "hhs_backend.api.a0_repository_status_routes"
    catalog = "hhs_backend.api.repository_history_routes"
    assert bounded in names
    assert catalog in names
    assert names.index(bounded) < names.index(catalog)

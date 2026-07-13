"""
HHS Live GUI Command Router v1
==============================

Pass 047 command-route metadata and bounded route self-test.  The FastAPI app
mounts concrete endpoints in hhs_backend.server so the route can access the live
workflow instance without introducing import cycles.
"""

from __future__ import annotations

from typing import Any, Dict

from hhs_backend.runtime.live_gui_command_contract_v1 import (
    AUTHORITY,
    COMMAND_SCHEMA,
    VERSION,
    build_gui_command_contract,
    normalize_gui_command,
    validate_gui_command_envelope,
)

COMMAND_ROUTES = [
    {
        "method": "POST",
        "path": "/api/runtime/gui/command",
        "authority": AUTHORITY,
        "semantics": "submit command envelope to FastAPI authority loop",
    },
    {
        "method": "GET",
        "path": "/api/runtime/gui/command/status/{command_id}",
        "authority": AUTHORITY,
        "semantics": "read bounded command status/result record",
    },
    {
        "method": "GET",
        "path": "/api/runtime/gui/command/history",
        "authority": AUTHORITY,
        "semantics": "read bounded command history without expanded metadata persistence",
    },
]


def list_live_gui_command_routes() -> Dict[str, Any]:
    return {
        "schema": "HHS_LIVE_GUI_COMMAND_ROUTE_MAP_V1",
        "version": VERSION,
        "authority": AUTHORITY,
        "routes": list(COMMAND_ROUTES),
        "command_schema": COMMAND_SCHEMA,
        "node_role": "GUI_PROXY_ONLY_NO_RUNTIME_EVENT_AUTHORITY",
    }


def live_gui_command_router_self_test() -> Dict[str, Any]:
    command = normalize_gui_command({"requested_operation": "runtime.tick", "client_sequence_id": 3})
    validation = validate_gui_command_envelope(command)
    contract = build_gui_command_contract(command)
    routes = list_live_gui_command_routes()
    return {
        "schema": "HHS_LIVE_GUI_COMMAND_ROUTER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(validation.get("ok") and contract.get("contract_root_hash72") and len(routes.get("routes", [])) == 3),
        "routes": routes,
        "validation": validation,
        "contract_root_hash72": contract.get("contract_root_hash72"),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(live_gui_command_router_self_test(), indent=2, sort_keys=True, default=str))

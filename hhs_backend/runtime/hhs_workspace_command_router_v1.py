"""Workspace command router map for Pass 049."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from hhs_backend.runtime.runtime_workspace_object_v1 import VERSION, AUTHORITY, hash72

WORKSPACE_COMMAND_SCHEMA = "HHS_WORKSPACE_COMMAND_ENVELOPE_V1"

COMMAND_TIERS: Dict[str, str] = {
    "panel.resize": "PRESENTATION_ONLY",
    "panel.move": "PRESENTATION_ONLY",
    "canvas.zoom": "PRESENTATION_ONLY",
    "selection.change": "PRESENTATION_ONLY",
    "project.inspect": "READ_ONLY",
    "object.inspect": "READ_ONLY",
    "receipt.verify": "AUTHORIZED_NONMUTATING",
    "graph.query": "AUTHORIZED_NONMUTATING",
    "memory.search": "AUTHORIZED_NONMUTATING",
    "project.create": "ADMINISTRATIVE_PROJECT_OPERATION",
    "project.fork": "ADMINISTRATIVE_PROJECT_OPERATION",
    "object.create": "AUTHORIZED_MUTATING",
    "object.rename": "AUTHORIZED_MUTATING",
    "object.move": "AUTHORIZED_MUTATING",
    "object.delete": "AUTHORIZED_MUTATING",
    "object.restore": "AUTHORIZED_MUTATING",
    "source.patch": "AUTHORIZED_MUTATING",
    "ingress.register": "AUTHORIZED_MUTATING",
    "semantic.reference.create": "AUTHORIZED_MUTATING",
    "interpret.execute": "AUTHORIZED_NONMUTATING",
    "compile.execute": "AUTHORIZED_NONMUTATING",
    "emulator.create": "AUTHORIZED_MUTATING",
    "emulator.step": "AUTHORIZED_MUTATING",
    "emulator.run": "AUTHORIZED_MUTATING",
    "emulator.pause": "AUTHORIZED_MUTATING",
    "emulator.resume": "AUTHORIZED_MUTATING",
    "emulator.stop": "AUTHORIZED_MUTATING",
    "emulator.snapshot": "AUTHORIZED_MUTATING",
    "emulator.restore": "AUTHORIZED_MUTATING",
    "emulator.replay": "AUTHORIZED_MUTATING",
    "emulator.branch": "AUTHORIZED_MUTATING",
}


def build_workspace_command(operation: str, *, project_id: str = "project:default", object_id: str | None = None, payload: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    tier = COMMAND_TIERS.get(operation, "PROPOSE_ONLY")
    envelope = {
        "schema": WORKSPACE_COMMAND_SCHEMA,
        "version": VERSION,
        "command_id": f"workspace-command:{hash72('HHS_WORKSPACE_COMMAND_ID_SEED_V1', {'operation': operation, 'payload': dict(payload or {})})[:16]}",
        "project_id": project_id,
        "object_id": object_id,
        "operation": operation,
        "authority_tier": tier,
        "payload": dict(payload or {}),
        "requires_fastapi_authority": tier != "PRESENTATION_ONLY",
        "frontend_may_commit_runtime_truth": False,
        "authority": AUTHORITY,
    }
    envelope["command_root_hash72"] = hash72(WORKSPACE_COMMAND_SCHEMA, envelope)
    return envelope


def list_workspace_command_routes() -> Dict[str, Any]:
    return {
        "schema": "HHS_WORKSPACE_COMMAND_ROUTE_MAP_V1",
        "version": VERSION,
        "commands": COMMAND_TIERS,
        "hard_invariant": "NO_OPERATION_INFERS_AUTHORITY_TIER_FROM_UI_CONTROL",
    }


def workspace_command_router_self_test() -> Dict[str, Any]:
    presentation = build_workspace_command("panel.resize")
    mutation = build_workspace_command("source.patch", object_id="object:source")
    unknown = build_workspace_command("direct.gui.mutate")
    return {
        "schema": "HHS_WORKSPACE_COMMAND_ROUTER_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(
            presentation.get("authority_tier") == "PRESENTATION_ONLY"
            and not presentation.get("requires_fastapi_authority")
            and mutation.get("requires_fastapi_authority")
            and unknown.get("authority_tier") == "PROPOSE_ONLY"
        ),
        "presentation": presentation,
        "mutation": mutation,
        "unknown": unknown,
        "route_map": list_workspace_command_routes(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(workspace_command_router_self_test(), indent=2, sort_keys=True, default=str))

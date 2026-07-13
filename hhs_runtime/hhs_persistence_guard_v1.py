"""
HHS Persistence Guard v1
========================

Canonical filesystem/database/export containment helper for release pass 010.

This module extends the sealed-runtime rule from live API/event paths into
persistence surfaces. Runtime-readable or user-exportable artifacts are not an
alternate state authority: writes must be committed as canonical ingress or
egress records, and reads intended to influence runtime behavior must be
committed as canonical ingress records before the payload is returned.

The guard deliberately stores payloads through the existing HHSIOGateway and
unified Hash72 ledger instead of creating a parallel persistence ledger.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional
import json

from hhs_python.runtime.hhs_runtime_controller import HHSRuntimeController
from hhs_runtime.hhs_io_gateway_v1 import HHSIOGateway, HHSIOGatewayError, canonical_json, payload_hash72
from hhs_runtime.hhs_unified_hash72_ledger_v1 import verify_unified_ledger
from hhs_runtime.hhs_closure_harness_bounded_runtime_v1 import bounded_verify_unified_ledger


PERSISTENCE_SCHEMA = "HHS_PERSISTENCE_GUARD_RECORD_V1"
_PERSISTENCE_CONTROLLER: Optional[HHSRuntimeController] = None
_PERSISTENCE_GATEWAY: Optional[HHSIOGateway] = None


def persistence_gateway() -> HHSIOGateway:
    """Return the process-local persistence gateway."""

    global _PERSISTENCE_CONTROLLER, _PERSISTENCE_GATEWAY
    if _PERSISTENCE_GATEWAY is None:
        _PERSISTENCE_CONTROLLER = HHSRuntimeController()
        _PERSISTENCE_GATEWAY = HHSIOGateway(_PERSISTENCE_CONTROLLER)
    return _PERSISTENCE_GATEWAY


def _safe_path(path: str | Path) -> Path:
    p = Path(path)
    if not str(p):
        raise HHSIOGatewayError("persistence path is required")
    return p


def _artifact_projection(path: Path, payload: Any, *, mode: str, source: str) -> Dict[str, Any]:
    return {
        "schema": PERSISTENCE_SCHEMA,
        "mode": mode,
        "source": source,
        "path": str(path),
        "payload_hash72": payload_hash72(payload),
        "payload": payload,
    }


def write_json_artifact(
    path: str | Path,
    payload: Mapping[str, Any],
    *,
    source: str = "persistence.write_json_artifact",
    indent: int = 2,
) -> Dict[str, Any]:
    """Write JSON only after an egress receipt is committed.

    This is the canonical replacement for direct json.dump/write_text paths
    when the artifact leaves runtime memory or becomes a future runtime input.
    """

    p = _safe_path(path)
    payload_dict = dict(payload or {})
    projection = _artifact_projection(p, payload_dict, mode="WRITE_JSON", source=source)
    egress = persistence_gateway().egress(source, projection)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload_dict, indent=indent, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return {
        "schema": "HHS_PERSISTENCE_WRITE_JSON_RESULT_V1",
        "path": str(p),
        "payload_hash72": projection["payload_hash72"],
        "io_egress_record": egress,
        "ledger": verify_unified_ledger(),
    }


def read_json_artifact(
    path: str | Path,
    *,
    source: str = "persistence.read_json_artifact",
) -> Dict[str, Any]:
    """Read JSON through an ingress receipt before returning payload data."""

    p = _safe_path(path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    projection = _artifact_projection(p, payload, mode="READ_JSON", source=source)
    ingress = persistence_gateway().ingress(source, projection)
    return {
        "schema": "HHS_PERSISTENCE_READ_JSON_RESULT_V1",
        "path": str(p),
        "payload_hash72": projection["payload_hash72"],
        "payload": payload,
        "io_ingress_record": ingress,
        "ledger": verify_unified_ledger(),
    }


def export_text_artifact(
    path: str | Path,
    text: str,
    *,
    source: str = "persistence.export_text_artifact",
) -> Dict[str, Any]:
    """Export text only after a canonical egress receipt is committed."""

    p = _safe_path(path)
    text_value = str(text)
    projection = _artifact_projection(
        p,
        {"text": text_value, "text_hash72": payload_hash72(text_value)},
        mode="EXPORT_TEXT",
        source=source,
    )
    egress = persistence_gateway().egress(source, projection)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text_value, encoding="utf-8")
    return {
        "schema": "HHS_PERSISTENCE_EXPORT_TEXT_RESULT_V1",
        "path": str(p),
        "payload_hash72": projection["payload_hash72"],
        "io_egress_record": egress,
        "ledger": verify_unified_ledger(),
    }


def guard_persistence_payload(source: str, payload: Mapping[str, Any], *, bounded_ledger: bool = False) -> Dict[str, Any]:
    """Commit a generic database/file persistence propagation record.

    Pass 041 allows the closure harness to request a bounded ledger summary so
    short certification runs do not become proportional to accumulated ledger history.
    """

    payload_dict = dict(payload or {})
    propagation = persistence_gateway().propagate(source, {
        "schema": PERSISTENCE_SCHEMA,
        "mode": "PERSISTENCE_PROPAGATION",
        "source": source,
        "payload_hash72": payload_hash72(payload_dict),
        "payload": payload_dict,
    })
    return {
        "schema": "HHS_PERSISTENCE_PROPAGATION_RESULT_V1",
        "payload_hash72": payload_hash72(payload_dict),
        "io_propagation_record": propagation,
        "ledger": bounded_verify_unified_ledger() if bounded_ledger else verify_unified_ledger(),
    }


def persistence_guard_self_test() -> Dict[str, Any]:
    from hhs_runtime.hhs_repo_paths_v1 import runtime_artifact_path

    path = runtime_artifact_path("persistence_guard_self_test.json")
    payload = {"b": 2, "a": 1, "message": "sealed persistence"}
    write = write_json_artifact(path, payload, source="persistence_guard_self_test.write")
    read = read_json_artifact(path, source="persistence_guard_self_test.read")
    export = export_text_artifact(
        runtime_artifact_path("persistence_guard_self_test.txt"),
        canonical_json({"ok": True, "payload_hash72": write["payload_hash72"]}),
        source="persistence_guard_self_test.export",
    )
    return {
        "schema": "HHS_PERSISTENCE_GUARD_SELF_TEST_V1",
        "write_ok": write["ledger"].get("ok"),
        "read_ok": read["ledger"].get("ok"),
        "export_ok": export["ledger"].get("ok"),
        "payload_hash72": write["payload_hash72"],
        "read_payload_hash72": read["payload_hash72"],
        "ledger": verify_unified_ledger(),
    }


if __name__ == "__main__":
    print(persistence_guard_self_test())

from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from hhs_runtime.pass219.pass170_public_registry_i170 import (
    NEXT_BOUNDARY,
    Pass170PublicRegistryError,
    verify_public_registries,
)

ROOT = Path(__file__).resolve().parents[2]
_REQUIRED_FIXTURE_FILES = (
    "HHS_PUBLIC_OPERATION_REGISTRY.json",
    "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json",
    "native_projects/hhs_pass190_operation_fabric/registry/HHS_OPERATION_REGISTRY_V1.json",
    "hhs_backend/public_api_server.py",
    "hhs_backend/pass168_parameter_circuit_routes.py",
    "hhs_backend/pass169_algebra_routes.py",
)


def _fixture_root(tmp_path: Path) -> Path:
    for relative in _REQUIRED_FIXTURE_FILES:
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return tmp_path


def test_repository_public_registry_verification_is_green() -> None:
    report = verify_public_registries(ROOT)
    assert report["registry_evidence_verified"] is True
    assert report["blockers"] == []
    assert report["direct_gateway_route_count"] == 12
    assert report["registered_direct_gateway_route_count"] == 12
    assert report["router_delegate_count"] == 2
    assert report["dispatch_source_operation_count"] > 0
    assert len(report["dispatch_source_registry_hash216"]) == 216
    assert report["public_gateway_port_count"] == 1
    assert report["canonical_state_mutated"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["floating_point_canonical_authority"] is False
    assert report["pass170_terminal_contract_verified"] is False
    assert report["next_boundary"] == NEXT_BOUNDARY


def test_duplicate_direct_route_fails_closed(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    path = root / "HHS_PUBLIC_OPERATION_REGISTRY.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["direct_gateway_routes"].append(dict(payload["direct_gateway_routes"][0]))
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report = verify_public_registries(root, fail_closed=False)
    assert report["registry_evidence_verified"] is False
    assert "PASS170_DIRECT_GATEWAY_ROUTE_SIGNATURE_DUPLICATE" in report["blockers"]


def test_second_public_gateway_port_fails_closed(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    path = root / "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    duplicate = dict(payload["ports"][0])
    duplicate["port_id"] = "hhs.public.api.duplicate"
    duplicate["default_port"] = 8001
    payload["ports"].append(duplicate)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    report = verify_public_registries(root, fail_closed=False)
    assert report["registry_evidence_verified"] is False
    assert "PASS170_PUBLIC_GATEWAY_PORT_CARDINALITY_INVALID" in report["blockers"]


def test_missing_registry_raises_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(Pass170PublicRegistryError, match="PASS170_REGISTRY_UNREADABLE"):
        verify_public_registries(tmp_path)


def test_gateway_declares_pass170_factory_and_compatibility_alias() -> None:
    source = (ROOT / "hhs_backend/public_api_server.py").read_text(encoding="utf-8")
    assert "def create_public_api_app(" in source
    assert "def create_app(" in source
    assert "registry_report = verify_public_registries(registry_root)" in source
    assert "app = create_public_api_app()" in source

from __future__ import annotations

import json
from pathlib import Path
import shutil

import pytest

from hhs_runtime.pass219.pass170_public_app_route_parity_i171 import (
    CLASSIFICATION,
    EXPECTED_TARGET_BLOCKERS,
    NEXT_BOUNDARY,
    Pass170I171VerificationError,
    verify_i171_public_app_route_parity,
)

ROOT = Path(__file__).resolve().parents[2]
_FIXTURE_FILES = (
    "HHS_PASS_169_COMPLETION_RECEIPT.json",
    "HHS_PUBLIC_OPERATION_REGISTRY.json",
    "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json",
    "native_projects/hhs_pass190_operation_fabric/registry/HHS_OPERATION_REGISTRY_V1.json",
    "hhs_backend/public_api_server.py",
    "hhs_backend/runtime_os_application_server.py",
    "hhs_backend/pass168_parameter_circuit_routes.py",
    "hhs_backend/pass169_algebra_routes.py",
)


def _fixture_root(tmp_path: Path) -> Path:
    for relative in _FIXTURE_FILES:
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # Preserve an explicit legacy production constructor in fixture-space so
    # the inherited I169 raw-constructor blocker remains testable without
    # copying the entire repository.
    legacy = tmp_path / "legacy_public_server.py"
    legacy.write_text(
        "from fastapi import FastAPI\napp = FastAPI(title='legacy-fixture')\n",
        encoding="utf-8",
    )
    return tmp_path


def test_repository_i171_evidence_is_green_and_nonterminal() -> None:
    report = verify_i171_public_app_route_parity(ROOT)
    assert report["i171_evidence_verified"] is True
    assert report["evidence_blockers"] == []
    assert report["classification"] == CLASSIFICATION
    assert report["production_application_identity_verified"] is True
    assert report["delegate_count"] == 2
    assert report["delegate_route_count"] == 35
    assert report["delegate_route_operation_id_count"] == 35
    assert report["direct_gateway_route_count"] == 12
    assert report["combined_registered_route_count"] == 47
    assert sorted(report["target_blockers"]) == sorted(EXPECTED_TARGET_BLOCKERS)
    assert report["raw_fastapi_constructor_count"] > 1
    assert report["inherited_i169_blockers"] == ["PASS170_MULTIPLE_FASTAPI_CONSTRUCTORS_PRESENT"]
    assert report["pass170_terminal_contract_verified"] is False
    assert report["canonical_state_mutated"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["floating_point_canonical_authority"] is False
    assert report["next_boundary"] == NEXT_BOUNDARY


def test_delegate_route_source_mismatch_fails_closed(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    source = root / "hhs_backend/pass169_algebra_routes.py"
    text = source.read_text(encoding="utf-8")
    text = text.replace('@router.get("/v1/algebra")', '# removed route decorator for parity fixture', 1)
    source.write_text(text, encoding="utf-8")

    with pytest.raises(Pass170I171VerificationError, match="PASS170_I171_DELEGATE_ROUTE_PARITY_MISMATCH"):
        verify_i171_public_app_route_parity(root)


def test_duplicate_delegate_operation_identity_fails_closed(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    path = root / "HHS_PUBLIC_OPERATION_REGISTRY.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    routes = payload["router_delegates"][0]["routes"]
    routes[1]["route_operation_id"] = routes[0]["route_operation_id"]
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(Pass170I171VerificationError, match="PASS170_I171_DELEGATE_OPERATION_ID_DUPLICATE"):
        verify_i171_public_app_route_parity(root)


def test_missing_production_dispatch_identity_assertion_fails_closed(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    path = root / "hhs_backend/runtime_os_application_server.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        'if app is not _pass170_public_gateway.app:',
        'if False and app is not _pass170_public_gateway.app:',
        1,
    )
    path.write_text(text, encoding="utf-8")

    with pytest.raises(Pass170I171VerificationError, match="PASS170_I171_PRODUCTION_DISPATCH_IDENTITY_INVALID"):
        verify_i171_public_app_route_parity(root)


def test_isolated_factory_is_explicit_but_not_public_entrypoint(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    report = verify_i171_public_app_route_parity(root)
    checks = report["production_identity"]["gateway_checks"]
    assert checks["normal_factory_uses_production_base_app"] is True
    assert checks["isolated_factory_is_explicit"] is True
    assert checks["compatibility_factory_requests_ephemeral"] is True
    assert checks["module_app_uses_public_factory"] is True
    assert report["raw_fastapi_constructor_count"] > 1
    assert "PASS170_LEGACY_FASTAPI_CONSTRUCTORS_REMAIN" in report["target_blockers"]


def test_i171_report_is_deterministic_for_same_tree(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    first = verify_i171_public_app_route_parity(root)
    second = verify_i171_public_app_route_parity(root)
    assert first == second

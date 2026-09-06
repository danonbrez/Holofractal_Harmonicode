from __future__ import annotations

import copy
import json
from pathlib import Path

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)
from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172 import (
    CLASSIFICATION,
    EXPECTED_TARGET_BLOCKERS,
    NEXT_BOUNDARY,
    _verify_constructor_registry,
    _verify_router_manifest,
)
from hhs_runtime.pass219.pass170_legacy_constructor_router_manifest_i172_gate import (
    verify_i172_legacy_constructor_router_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def _json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_repository_i172_constructor_and_router_manifest_evidence_is_green() -> None:
    report = verify_i172_legacy_constructor_router_manifest(ROOT)
    assert report["evidence_verified"] is True
    assert report["evidence_blockers"] == []
    assert report["classification"] == CLASSIFICATION
    assert report["inherited_i171_verified"] is True
    assert report["inherited_raw_constructor_count"] == 10
    assert report["constructor_registry_verified"] is True
    assert report["constructor_evidence"]["observed_constructor_count"] == 10
    assert report["constructor_evidence"]["registered_constructor_count"] == 10
    assert report["constructor_evidence"]["canonical_constructor_count"] == 1
    assert report["constructor_evidence"]["degraded_gateway_count"] == 1
    assert report["constructor_evidence"]["observed_launcher_count"] == 6
    assert report["constructor_evidence"]["pending_launcher_count"] == 5
    assert report["router_manifest_verified"] is True
    assert report["router_evidence"]["stage_count"] == 9
    assert report["router_evidence"]["pass201_closure_stage_present"] is True
    assert report["router_evidence"]["route_summary"]["direct_plus_delegate_routes"] == 47
    assert report["target_blockers"] == list(EXPECTED_TARGET_BLOCKERS)
    assert "PASS170_FULL_ROUTER_MANIFEST_PENDING" not in report["target_blockers"]
    assert report["pass170_terminal_contract_verified"] is False
    assert report["canonical_state_mutated"] is False
    assert report["new_vm81_authority"] is False
    assert report["new_hash72_mint_authority"] is False
    assert report["hash216_persistence_authority"] is False
    assert report["floating_point_canonical_authority"] is False
    assert report["next_boundary"] == NEXT_BOUNDARY


def test_constructor_registry_fails_closed_when_one_observed_constructor_is_unclassified() -> None:
    registry = _json("HHS_FASTAPI_CONSTRUCTOR_REGISTRY.json")
    mutated = copy.deepcopy(registry)
    mutated["constructor_records"] = mutated["constructor_records"][:-1]
    inventory = build_i169_pass170_public_authority_inventory(ROOT)
    blockers, _evidence, _targets = _verify_constructor_registry(ROOT, mutated, inventory)
    assert "PASS170_I172_CONSTRUCTOR_REGISTRY_CENSUS_MISMATCH" in blockers


def test_router_manifest_fails_closed_on_duplicate_stage_order() -> None:
    manifest = _json("HHS_PUBLIC_ROUTER_MANIFEST.json")
    mutated = copy.deepcopy(manifest)
    mutated["stages"][1]["order"] = mutated["stages"][0]["order"]
    blockers, _evidence = _verify_router_manifest(ROOT, mutated)
    assert "PASS170_I172_ROUTER_STAGE_ORDER_NOT_STRICT" in blockers


def test_pass201_closure_contract_is_explicit_and_deterministic() -> None:
    manifest = _json("HHS_PUBLIC_ROUTER_MANIFEST.json")
    stage = next(item for item in manifest["stages"] if item["stage_id"] == "pass201-api-package-closure")
    assert stage["package"] == "hhs_backend.api"
    assert stage["closure_requirements"] == {
        "module_order": "SORTED",
        "attach_policy": "MISSING_SIGNATURES_ONLY",
        "import_failure_count": 0,
        "unexposed_route_count": 0,
    }


def test_websocket_compatibility_launcher_routes_through_pass170() -> None:
    source = (ROOT / "hhs_runtime/runtime_ws_server.py").read_text(encoding="utf-8")
    assert "from hhs_backend.public_api_server import app" in source
    assert '"hhs_backend.public_api_server:app"' in source
    assert '"hhs_backend.server:app"' not in source

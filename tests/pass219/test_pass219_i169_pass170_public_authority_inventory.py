from __future__ import annotations

import json
from pathlib import Path

from hhs_runtime.pass219.pass170_public_authority_inventory_i169 import (
    build_i169_pass170_public_authority_inventory,
)


def _write_parent_receipt(root: Path, **overrides: object) -> None:
    receipt = {
        "schema": "HHS_PASS_169_COMPLETION_RECEIPT_V3",
        "contract_id": "HHS-P169-HSAE-VM81-ESCPR",
        "verified": True,
        "terminal_verified": True,
        "classification": "HHS_PASS_169_HARMONICODE_SYNTAX_ALGEBRA_ENFORCEMENT_AND_VM81_EXACT_SYMBOLIC_CONSTRAINT_PROOF_RUNTIME_VERIFIED",
        "operation_verified_mask": 4095,
        "terminal_blockers": [],
        "new_vm81_authority": False,
        "new_hash72_mint_authority": False,
        "hash216_persistence_authority": False,
        "floating_point_canonical_authority": False,
        "fallback_used": False,
    }
    receipt.update(overrides)
    (root / "HHS_PASS_169_COMPLETION_RECEIPT.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def test_clean_inventory_has_no_i169_authority_blockers(tmp_path: Path) -> None:
    _write_parent_receipt(tmp_path)
    (tmp_path / "hhs_backend").mkdir()
    (tmp_path / "hhs_backend" / "public_api_server.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.get('/v1/status')\n"
        "def status(): return {'ok': True}\n",
        encoding="utf-8",
    )
    (tmp_path / "HHS_PUBLIC_OPERATION_REGISTRY.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json").write_text("{}\n", encoding="utf-8")

    report = build_i169_pass170_public_authority_inventory(tmp_path)

    assert report["parent_pass169"]["verified"] is True
    assert report["inventory"]["fastapi_constructor_count"] == 1
    assert report["inventory"]["route_decorator_count"] == 1
    assert report["blockers"] == []
    assert report["inventory_evidence_verified"] is True
    assert report["pass170_terminal_contract_verified"] is False
    assert report["next_boundary"] == "PASS170_OPERATION_REGISTRY_AND_ROUTE_PARITY"
    assert report["canonical_state_mutated"] is False


def test_inventory_detects_missing_registries_and_multiple_apps(tmp_path: Path) -> None:
    _write_parent_receipt(tmp_path)
    (tmp_path / "hhs_backend").mkdir()
    (tmp_path / "hhs_runtime").mkdir()
    (tmp_path / "hhs_backend" / "server.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )
    (tmp_path / "hhs_runtime" / "main.py").write_text(
        "import fastapi\napp = fastapi.FastAPI()\n",
        encoding="utf-8",
    )

    report = build_i169_pass170_public_authority_inventory(tmp_path)

    assert report["inventory"]["fastapi_constructor_count"] == 2
    assert "PASS170_CANONICAL_PUBLIC_GATEWAY_ABSENT" in report["blockers"]
    assert "PASS170_PUBLIC_OPERATION_REGISTRY_ABSENT" in report["blockers"]
    assert "PASS170_PUBLIC_NETWORK_PORT_REGISTRY_ABSENT" in report["blockers"]
    assert "PASS170_MULTIPLE_FASTAPI_CONSTRUCTORS_PRESENT" in report["blockers"]
    assert report["next_boundary"] == "PASS170_CANONICAL_GATEWAY_AND_REGISTRY_REPAIR"


def test_inventory_fails_closed_when_pass169_parent_is_not_terminal(tmp_path: Path) -> None:
    _write_parent_receipt(tmp_path, terminal_verified=False, verified=False)
    (tmp_path / "hhs_backend").mkdir()
    (tmp_path / "hhs_backend" / "public_api_server.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n",
        encoding="utf-8",
    )
    (tmp_path / "HHS_PUBLIC_OPERATION_REGISTRY.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json").write_text("{}\n", encoding="utf-8")

    report = build_i169_pass170_public_authority_inventory(tmp_path)

    assert report["parent_pass169"]["verified"] is False
    assert "PASS169_TERMINAL_PARENT_NOT_VERIFIED" in report["blockers"]
    assert report["inventory_evidence_verified"] is False


def test_public_surface_parse_error_is_explicit_blocker(tmp_path: Path) -> None:
    _write_parent_receipt(tmp_path)
    (tmp_path / "hhs_backend").mkdir()
    (tmp_path / "hhs_backend" / "public_api_server.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI(\n",
        encoding="utf-8",
    )
    (tmp_path / "HHS_PUBLIC_OPERATION_REGISTRY.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "HHS_PUBLIC_NETWORK_PORT_REGISTRY.json").write_text("{}\n", encoding="utf-8")

    report = build_i169_pass170_public_authority_inventory(tmp_path)

    assert report["inventory"]["parse_errors"]
    assert "PASS170_PUBLIC_SURFACE_PARSE_ERRORS" in report["blockers"]
    assert report["inventory_evidence_verified"] is False


def test_inventory_is_deterministic_for_same_tree(tmp_path: Path) -> None:
    _write_parent_receipt(tmp_path)
    (tmp_path / "hhs_backend").mkdir()
    (tmp_path / "hhs_backend" / "server.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.post('/v1/example')\n"
        "def example(): return {'ok': True}\n",
        encoding="utf-8",
    )

    first = build_i169_pass170_public_authority_inventory(tmp_path)
    second = build_i169_pass170_public_authority_inventory(tmp_path)

    assert first == second

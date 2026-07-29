"""Read-only Pass 172 installation status projections.

These routes expose committed installer state only. They cannot create plans,
install packages, update, repair, roll back, uninstall, or mutate the host.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os
import platform

from fastapi import APIRouter

from hhs_installer.dependencies import DependencyManifest
from hhs_installer.management import doctor, installation_status, receipt_status
from hhs_installer.probe import EnvironmentProbe

router = APIRouter(prefix="/api/runtime/installation", tags=["installation"])


def _home() -> Path:
    raw = os.environ.get("HHS_HOME")
    return Path(raw).expanduser().resolve() if raw else (Path.home() / ".hhs").resolve()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@router.get("/status")
async def installation_status_route() -> dict[str, Any]:
    return installation_status(_home())


@router.get("/environment")
async def installation_environment_route() -> dict[str, Any]:
    report = EnvironmentProbe(command_timeout=3).run(target=_home().parent)
    return {
        "schema": "HHS_PASS_172_INSTALLATION_ENVIRONMENT_ROUTE_V1",
        "probe": report.to_dict(),
        "host_mutation_performed": False,
    }


@router.get("/profile")
async def installation_profile_route() -> dict[str, Any]:
    status = installation_status(_home())
    active = status.get("active") or {}
    return {
        "schema": "HHS_PASS_172_INSTALLATION_PROFILE_ROUTE_V1",
        "requested_profile": active.get("requested_profile"),
        "resolved_profile": active.get("resolved_profile") or active.get("profile"),
        "provider_state": active.get("provider") or active.get("provider_state") or "unclassified",
        "host_mutation_performed": False,
    }


@router.get("/dependencies")
async def installation_dependencies_route() -> dict[str, Any]:
    path = _repo_root() / "manifests" / "pass172" / "dependencies.json"
    if not path.is_file():
        return {
            "schema": "HHS_PASS_172_INSTALLATION_DEPENDENCIES_ROUTE_V1",
            "classification": "P172_DEPENDENCY_MANIFEST_MISSING",
            "dependencies": [],
            "host_mutation_performed": False,
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    manifest = DependencyManifest.load(path)
    return {
        "schema": "HHS_PASS_172_INSTALLATION_DEPENDENCIES_ROUTE_V1",
        "manifest_identity": manifest.manifest_identity,
        "lock_status": payload.get("lock_status"),
        "dependencies": [item.to_dict() for item in manifest.records],
        "host_mutation_performed": False,
    }


@router.get("/receipts")
async def installation_receipts_route() -> dict[str, Any]:
    result = receipt_status(_home())
    return {
        "schema": "HHS_PASS_172_INSTALLATION_RECEIPTS_ROUTE_V1",
        **result,
        "host_mutation_performed": False,
    }


@router.get("/health")
async def installation_health_route() -> dict[str, Any]:
    result = doctor(_home())
    return {
        "schema": "HHS_PASS_172_INSTALLATION_HEALTH_ROUTE_V1",
        "healthy": not result["repair_required"],
        "doctor": result,
        "runtime_authority": "singleton VM81 authority remains external to installer status projection",
        "host_mutation_performed": False,
    }

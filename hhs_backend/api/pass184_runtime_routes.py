"""Pass 184 portable runtime package and readiness routes."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hhs_runtime.pass184.runtime import (
    HEALTH_PATH,
    PROFILE_SEEDS,
    Pass184Error,
    PortableRuntimeAuthority,
    ensure_within,
)

router = APIRouter(prefix="/api/v1/pass184", tags=["pass184-portable-runtime"])
authority = PortableRuntimeAuthority()


class PlanRequest(BaseModel):
    profile: str = "full"
    install_name: str = "hhs-runtime"
    repository_root: str | None = None
    host: str = "0.0.0.0"
    port: int = Field(default=8080, ge=1, le=65535)


class PackageRequest(PlanRequest):
    clean: bool = True


class VerifyRequest(BaseModel):
    install_name: str = "hhs-runtime"


class ProbeRequest(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(default=8080, ge=1, le=65535)
    health_path: str = HEALTH_PATH
    timeout: float = Field(default=2.0, gt=0, le=30)


def _repository_root(requested: str | None = None) -> Path:
    return Path(requested or os.environ.get("HHS_REPOSITORY_ROOT") or Path.cwd()).expanduser().resolve()


def _package_root(repository: Path) -> Path:
    return Path(
        os.environ.get("HHS_PASS184_PACKAGE_ROOT")
        or repository / ".hhs" / "pass184" / "packages"
    ).expanduser().resolve()


def _install_root(repository: Path, install_name: str) -> Path:
    if (
        not install_name
        or install_name in {".", ".."}
        or Path(install_name).name != install_name
        or any(character in install_name for character in ("/", "\\", "\0", "\n", "\r"))
    ):
        raise Pass184Error(
            "P184_REJECT_INSTALL_NAME",
            "install_name must be one safe path segment",
            details={"install_name": install_name},
        )
    root = _package_root(repository)
    return ensure_within(root, root / install_name)


def _raise_http(error: Pass184Error) -> None:
    status_code = 409 if error.status in {
        "P184_REJECT_PACKAGE_TAMPER",
        "P184_REJECT_PACKAGE_FILE_SET",
        "P184_REJECT_PORT_OCCUPIED",
    } else 400
    raise HTTPException(status_code=status_code, detail=error.to_dict()) from error


@router.get("/status")
def pass184_status() -> dict[str, Any]:
    result = authority.status()
    result["environment"] = authority.detect(repository_root=_repository_root())
    return result


@router.post("/plan")
def pass184_plan(request: PlanRequest) -> dict[str, Any]:
    try:
        repository = _repository_root(request.repository_root)
        install = _install_root(repository, request.install_name)
        plan = authority.plan(
            profile=request.profile,
            install_root=install,
            repository_root=repository,
            host=request.host,
            port=request.port,
        )
        result = plan.to_dict()
        result["classification"] = "HHS_PASS_184_DETERMINISTIC_PACKAGE_PLAN_VERIFIED"
        result["package_root"] = str(_package_root(repository))
        return result
    except Pass184Error as error:
        _raise_http(error)


@router.post("/package")
def pass184_package(request: PackageRequest) -> dict[str, Any]:
    try:
        repository = _repository_root(request.repository_root)
        install = _install_root(repository, request.install_name)
        plan = authority.plan(
            profile=request.profile,
            install_root=install,
            repository_root=repository,
            host=request.host,
            port=request.port,
        )
        return authority.build(plan, clean=request.clean)
    except Pass184Error as error:
        _raise_http(error)


@router.post("/verify")
def pass184_verify(request: VerifyRequest) -> dict[str, Any]:
    try:
        repository = _repository_root()
        install = _install_root(repository, request.install_name)
        return authority.verify(install)
    except Pass184Error as error:
        _raise_http(error)


@router.post("/probe")
def pass184_probe(request: ProbeRequest) -> dict[str, Any]:
    if request.host not in {"127.0.0.1", "localhost", "::1", "0.0.0.0", "::"}:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "P184_REJECT_NON_LOOPBACK_PROBE",
                "message": "Pass 184 API probes are restricted to loopback targets",
            },
        )
    try:
        return authority.probe(
            host=request.host,
            port=request.port,
            health_path=request.health_path,
            timeout=request.timeout,
        )
    except Pass184Error as error:
        _raise_http(error)

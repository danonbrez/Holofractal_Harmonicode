"""RuntimeOS composition for Pass 218 Iteration 34 manifest-bound source ingress."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from hhs_runtime.pass218.manifest_bound_source_ingress_i34 import (
    PASS218_I34_INGRESS_SCOPE,
    PASS218_I34_INGRESS_VERSION,
    Pass218I34AuthorityError,
    Pass218I34BindingError,
    Pass218I34IngressError,
    Pass218I34ManifestBoundSourceIngress,
    Pass218I34StateError,
)

PASS218_I34_STATUS_PATH = "/api/runtime/pass218/cognition/manifest-source-ingress/status"
PASS218_I34_BIND_PATH = "/api/runtime/pass218/cognition/manifest-source-ingress/bind"
PASS218_I34_STATE_KEY = "hhs_pass218_manifest_source_ingress_i34"
PASS218_I34_STORE_DIRNAME = "cognition/manifest-source-ingress-i34"


class Pass218I34BindPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    source_text: str


class Pass218I34RuntimeManifestSourceIngressControl:
    """RuntimeOS membrane using the already configured read-only I33 authority."""

    def __init__(
        self,
        i33_control: Any,
        *,
        lifecycle: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.i33_control = i33_control
        self.lifecycle = lifecycle
        self.state_root = Path(state_root).resolve()
        self.store_root = self.state_root / PASS218_I34_STORE_DIRNAME
        self.ingress = Pass218I34ManifestBoundSourceIngress(
            lifecycle=lifecycle,
            authority=i33_control.advancer.authority,
            i33_store_root=i33_control.store_root,
            ingress_store_root=self.store_root,
        )

    def bind(self, payload: Pass218I34BindPayload) -> dict[str, Any]:
        return self.ingress.bind(
            source_id=payload.source_id,
            source_bytes=payload.source_text.encode("utf-8"),
        )

    def status(self) -> dict[str, Any]:
        return {
            **self.ingress.status(),
            "authority_configuration_error": self.i33_control.configuration_error,
            "authority_configuration_source": self.i33_control.status().get(
                "authority_configuration_source"
            ),
            "api_can_mint_curriculum_authority": False,
            "api_can_advance_curriculum_stage": False,
            "request_source_payload_persisted": False,
        }


def install_pass218_i34_manifest_source_ingress_control(
    app: Any,
    i33_control: Any,
    lifecycle: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I34RuntimeManifestSourceIngressControl:
    existing = getattr(app.state, PASS218_I34_STATE_KEY, None)
    if isinstance(existing, Pass218I34RuntimeManifestSourceIngressControl):
        return existing

    control = Pass218I34RuntimeManifestSourceIngressControl(
        i33_control,
        lifecycle=lifecycle,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I34_STATE_KEY, control)

    managed_paths = {PASS218_I34_STATUS_PATH, PASS218_I34_BIND_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def manifest_source_ingress_status() -> dict[str, Any]:
        return control.status()

    async def bind_manifest_source(payload: Pass218I34BindPayload) -> dict[str, Any]:
        if control.i33_control.configuration_error is not None:
            raise HTTPException(
                status_code=503,
                detail=control.i33_control.configuration_error,
            )
        try:
            return control.bind(payload)
        except Pass218I34AuthorityError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except (Pass218I34BindingError, Pass218I34StateError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Pass218I34IngressError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I34_STATUS_PATH,
        manifest_source_ingress_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-manifest-source-ingress-status-i34",
    )
    app.add_api_route(
        PASS218_I34_BIND_PATH,
        bind_manifest_source,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-manifest-source-ingress-bind-i34",
    )
    return control


__all__ = [
    "PASS218_I34_BIND_PATH",
    "PASS218_I34_INGRESS_SCOPE",
    "PASS218_I34_INGRESS_VERSION",
    "PASS218_I34_STATE_KEY",
    "PASS218_I34_STATUS_PATH",
    "PASS218_I34_STORE_DIRNAME",
    "Pass218I34BindPayload",
    "Pass218I34RuntimeManifestSourceIngressControl",
    "install_pass218_i34_manifest_source_ingress_control",
]

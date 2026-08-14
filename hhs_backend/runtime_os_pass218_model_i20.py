"""RuntimeOS composition for Pass 218 Iteration 20 Pass 166 model binding."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Any

from hhs_runtime.pass218.model_activation_i20 import (
    PASS218_I20_MODEL_BINDING_VERSION,
    Pass218I20ModelBindingError,
    Pass218I20ModelConfiguration,
    Pass218Pass166ModelBinding,
)

PASS218_I20_STATUS_PATH = "/api/runtime/pass218/cognition/pass166-model/status"
PASS218_I20_STATE_KEY = "hhs_pass218_pass166_model_i20"


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


class Pass218I20RuntimeModelControl:
    """Configuration/status membrane around the exact I20 model binding."""

    def __init__(
        self,
        *,
        lifecycle: Any,
        postcondition_control: Any,
        state_root: str | os.PathLike[str],
    ) -> None:
        self.lifecycle = lifecycle
        self.postcondition_control = postcondition_control
        self.state_root = Path(state_root).resolve()
        self.binding: Pass218Pass166ModelBinding | None = None
        self.configuration_error: str | None = None
        self.last_error_code: str | None = None

        model_id = os.environ.get("HHS_PASS218_P166_MODEL_ID", "").strip()
        expected_model_root = os.environ.get("HHS_PASS218_P166_MODEL_ROOT", "").strip()
        expected_index_root = os.environ.get("HHS_PASS218_P166_INDEX_ROOT", "").strip()
        activate = _enabled(os.environ.get("HHS_PASS218_P166_ACTIVATE"))
        if not model_id and not expected_model_root and not expected_index_root:
            return
        if not model_id or not expected_model_root or not expected_index_root:
            self.configuration_error = "P218_I20_COMPLETE_MODEL_IDENTITY_REQUIRED"
            return
        try:
            from hhs_runtime.pass166.service import Word2VecService

            service = Word2VecService(
                os.environ.get("HHS_PASS166_STORAGE_DIR") or None
            )
            configuration = Pass218I20ModelConfiguration(
                model_id=model_id,
                expected_model_root=expected_model_root,
                expected_index_root=expected_index_root,
                activate_if_needed=activate,
            )
            self.binding = Pass218Pass166ModelBinding(
                state_root=self.state_root,
                service=service,
                lifecycle=self.lifecycle,
                postcondition_control=self.postcondition_control,
                configuration=configuration,
            )
        except Exception as exc:
            self.configuration_error = self._code(exc)

    @staticmethod
    def _code(exc: BaseException) -> str:
        text = str(exc)
        if text.startswith("P218_") or text.startswith("P166_"):
            return text.split(":", 1)[0]
        return type(exc).__name__

    def synchronize(self) -> dict[str, Any]:
        if self.binding is None:
            return self.status()
        try:
            result = self.binding.synchronize()
            self.last_error_code = None
            return result
        except Exception as exc:
            self.last_error_code = self._code(exc)
            return self.status()

    def exact_provider(self) -> Any:
        if self.binding is None:
            raise Pass218I20ModelBindingError("P218_I20_MODEL_BINDING_NOT_CONFIGURED")
        return self.binding.exact_provider()

    def status(self) -> dict[str, Any]:
        if self.binding is None:
            return {
                "schema": "HHS-P218-I20-RUNTIME-MODEL-STATUS-V1",
                "version": PASS218_I20_MODEL_BINDING_VERSION,
                "configured": False,
                "configuration_error": self.configuration_error,
                "i20_error_code": self.last_error_code,
                "relational_candidate_provider_ready": False,
                "browser_model_activation_permitted": False,
                "canonical_learning_commit_invoked": False,
                "truth_promotion": False,
                "action_authority_minted": False,
                "pass165_source_retaining_learning_commit_invoked": False,
                "verbatim_corpus_source_retained": False,
                "authoritative_float_weights_created": False,
            }
        result = self.binding.status()
        return {
            **result,
            "schema": "HHS-P218-I20-RUNTIME-MODEL-STATUS-V1",
            "configuration_error": self.configuration_error,
            "i20_error_code": self.last_error_code or result.get("i20_error_code"),
        }


def install_pass218_i20_model_control(
    app: Any,
    lifecycle: Any,
    postcondition_control: Any,
    *,
    state_root: str | os.PathLike[str],
) -> Pass218I20RuntimeModelControl:
    existing = getattr(app.state, PASS218_I20_STATE_KEY, None)
    if isinstance(existing, Pass218I20RuntimeModelControl):
        return existing

    control = Pass218I20RuntimeModelControl(
        lifecycle=lifecycle,
        postcondition_control=postcondition_control,
        state_root=state_root,
    )
    setattr(app.state, PASS218_I20_STATE_KEY, control)

    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) != PASS218_I20_STATUS_PATH
    ]

    async def model_status() -> dict[str, Any]:
        return control.status()

    app.add_api_route(
        PASS218_I20_STATUS_PATH,
        model_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-pass166-model-status-i20",
    )

    inherited_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def i20_lifespan(app_instance):
        async with inherited_lifespan(app_instance):
            if control.binding is not None:
                await asyncio.to_thread(control.synchronize)
            yield

    app.router.lifespan_context = i20_lifespan
    return control


__all__ = [
    "PASS218_I20_STATE_KEY",
    "PASS218_I20_STATUS_PATH",
    "Pass218I20RuntimeModelControl",
    "install_pass218_i20_model_control",
]

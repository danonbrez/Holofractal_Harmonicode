"""RuntimeOS composition for Pass 218 Iteration 25 perspective/context candidates."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_backend.runtime_os_pass218_narrative_beat_i24 import (
    Pass218I24RuntimeNarrativeBeatControl,
)
from hhs_runtime.pass218.perspective_context_i25 import (
    PASS218_I25_PERSPECTIVE_CONTEXT_VERSION,
    Pass218I25PerspectiveContextError,
    Pass218I25PerspectiveContextHydrator,
    Pass218I25PerspectiveProfile,
    Pass218I25PerspectiveRequest,
    Pass218I25PerspectiveRule,
)

PASS218_I25_STATUS_PATH = "/api/runtime/pass218/cognition/perspective-context/status"
PASS218_I25_CANDIDATES_PATH = "/api/runtime/pass218/cognition/perspective-context/candidates"
PASS218_I25_STATE_KEY = "hhs_pass218_perspective_context_i25"


class Pass218I25RuntimePerspectiveContextControl:
    """Browser-safe membrane over frozen I24 narrative-beat candidates."""

    def __init__(self, i24_control: Any) -> None:
        self.i24_control = i24_control
        self.hydrator = Pass218I25PerspectiveContextHydrator(i24_control)

    @staticmethod
    def _profile(payload: Mapping[str, Any]) -> Pass218I25PerspectiveProfile:
        profile = payload.get("perspective_profile")
        if not isinstance(profile, Mapping):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_PERSPECTIVE_PROFILE_OBJECT_REQUIRED"
            )
        for field in ("profile_id", "profile_version", "profile_origin"):
            if not isinstance(profile.get(field), str):
                raise Pass218I25PerspectiveContextError(
                    f"P218_I25_{field.upper()}_STRING_REQUIRED"
                )
        raw_rules = profile.get("rules", [])
        if not isinstance(raw_rules, list):
            raise Pass218I25PerspectiveContextError(
                "P218_I25_PROFILE_RULES_LIST_REQUIRED"
            )
        rules: list[Pass218I25PerspectiveRule] = []
        for raw_rule in raw_rules:
            if not isinstance(raw_rule, Mapping):
                raise Pass218I25PerspectiveContextError(
                    "P218_I25_PROFILE_RULE_OBJECT_REQUIRED"
                )
            for field in ("rule_id", "rule_payload_hash72"):
                if not isinstance(raw_rule.get(field), str):
                    raise Pass218I25PerspectiveContextError(
                        f"P218_I25_RULE_{field.upper()}_STRING_REQUIRED"
                    )
            selectors: dict[str, tuple[str, ...]] = {}
            for field in ("relation_types", "source_tokens", "target_tokens"):
                raw_values = raw_rule.get(field, [])
                if not isinstance(raw_values, list) or not all(
                    isinstance(item, str) for item in raw_values
                ):
                    raise Pass218I25PerspectiveContextError(
                        f"P218_I25_RULE_{field.upper()}_STRING_LIST_REQUIRED"
                    )
                selectors[field] = tuple(raw_values)
            rules.append(
                Pass218I25PerspectiveRule(
                    rule_id=str(raw_rule["rule_id"]),
                    rule_payload_hash72=str(raw_rule["rule_payload_hash72"]),
                    salience_delta=raw_rule.get("salience_delta"),
                    relation_types=selectors["relation_types"],
                    source_tokens=selectors["source_tokens"],
                    target_tokens=selectors["target_tokens"],
                )
            )
        return Pass218I25PerspectiveProfile(
            profile_id=str(profile["profile_id"]),
            profile_version=str(profile["profile_version"]),
            profile_origin=str(profile["profile_origin"]),
            rules=tuple(rules),
        ).validated()

    @classmethod
    def _request(cls, payload: Mapping[str, Any]) -> Pass218I25PerspectiveRequest:
        beat_request = Pass218I24RuntimeNarrativeBeatControl._request(payload)
        return Pass218I25PerspectiveRequest(
            beat_request=beat_request,
            perspective_profile=cls._profile(payload),
        ).validated()

    def hydrate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.hydrator.hydrate(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.hydrator.status()


def install_pass218_i25_perspective_context_control(
    app: Any,
    i24_control: Any,
) -> Pass218I25RuntimePerspectiveContextControl:
    existing = getattr(app.state, PASS218_I25_STATE_KEY, None)
    if isinstance(existing, Pass218I25RuntimePerspectiveContextControl):
        return existing

    control = Pass218I25RuntimePerspectiveContextControl(i24_control)
    setattr(app.state, PASS218_I25_STATE_KEY, control)

    managed_paths = {PASS218_I25_STATUS_PATH, PASS218_I25_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def perspective_context_status() -> dict[str, Any]:
        return control.status()

    async def perspective_context_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.hydrate(payload)
        except Pass218I25PerspectiveContextError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I25_STATUS_PATH,
        perspective_context_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-perspective-context-status-i25",
    )
    app.add_api_route(
        PASS218_I25_CANDIDATES_PATH,
        perspective_context_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-perspective-context-candidates-i25",
    )
    return control


__all__ = [
    "PASS218_I25_CANDIDATES_PATH",
    "PASS218_I25_PERSPECTIVE_CONTEXT_VERSION",
    "PASS218_I25_STATE_KEY",
    "PASS218_I25_STATUS_PATH",
    "Pass218I25RuntimePerspectiveContextControl",
    "install_pass218_i25_perspective_context_control",
]

"""RuntimeOS composition for Pass 218 Iteration 24 narrative-beat candidates."""
from __future__ import annotations

from typing import Any, Mapping

from fastapi import HTTPException

from hhs_runtime.pass218.narrative_beat_i24 import (
    PASS218_I24_NARRATIVE_BEAT_VERSION,
    Pass218I24BeatRequest,
    Pass218I24NarrativeBeatAssembler,
    Pass218I24NarrativeBeatError,
)

PASS218_I24_STATUS_PATH = "/api/runtime/pass218/cognition/narrative-beat/status"
PASS218_I24_CANDIDATES_PATH = "/api/runtime/pass218/cognition/narrative-beat/candidates"
PASS218_I24_STATE_KEY = "hhs_pass218_narrative_beat_i24"


class Pass218I24RuntimeNarrativeBeatControl:
    """Browser-safe membrane over frozen I23 contextual-state candidates."""

    def __init__(self, i23_control: Any) -> None:
        self.i23_control = i23_control
        self.assembler = Pass218I24NarrativeBeatAssembler(i23_control)

    @staticmethod
    def _request(payload: Mapping[str, Any]) -> Pass218I24BeatRequest:
        tokens = payload.get("tokens")
        if not isinstance(tokens, list) or not all(isinstance(item, str) for item in tokens):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_QUERY_TOKENS_STRING_LIST_REQUIRED"
            )
        attention_tokens = payload.get("attention_tokens", [])
        if not isinstance(attention_tokens, list) or not all(
            isinstance(item, str) for item in attention_tokens
        ):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_ATTENTION_TOKENS_STRING_LIST_REQUIRED"
            )
        allowed_relation_families = payload.get("allowed_relation_families", [])
        if not isinstance(allowed_relation_families, list) or not all(
            isinstance(item, str) for item in allowed_relation_families
        ):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_RELATION_FAMILIES_STRING_LIST_REQUIRED"
            )
        context_id = payload.get("context_id")
        if not isinstance(context_id, str):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_CONTEXT_ID_STRING_REQUIRED"
            )

        source_identity = payload.get("source_identity")
        if not isinstance(source_identity, Mapping):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_SOURCE_IDENTITY_OBJECT_REQUIRED"
            )
        evidence = payload.get("evidence")
        if not isinstance(evidence, Mapping):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_EVIDENCE_OBJECT_REQUIRED"
            )

        required_source_fields = (
            "source_id",
            "source_checksum_sha256",
            "source_authority",
            "rights_class",
        )
        for field in required_source_fields:
            if not isinstance(source_identity.get(field), str):
                raise Pass218I24NarrativeBeatError(
                    f"P218_I24_SOURCE_{field.upper()}_STRING_REQUIRED"
                )
        required_evidence_fields = (
            "evidence_id",
            "evidence_type",
            "epistemic_status",
            "payload_hash72",
        )
        for field in required_evidence_fields:
            if not isinstance(evidence.get(field), str):
                raise Pass218I24NarrativeBeatError(
                    f"P218_I24_EVIDENCE_{field.upper()}_STRING_REQUIRED"
                )
        curriculum_identity_hash72 = payload.get("curriculum_identity_hash72")
        if not isinstance(curriculum_identity_hash72, str):
            raise Pass218I24NarrativeBeatError(
                "P218_I24_CURRICULUM_IDENTITY_STRING_REQUIRED"
            )

        return Pass218I24BeatRequest(
            tokens=tuple(tokens),
            context_id=context_id,
            curriculum_identity_hash72=curriculum_identity_hash72,
            curriculum_position=payload.get("curriculum_position"),
            source_id=str(source_identity["source_id"]),
            source_checksum_sha256=str(source_identity["source_checksum_sha256"]),
            source_authority=str(source_identity["source_authority"]),
            rights_class=str(source_identity["rights_class"]),
            evidence_id=str(evidence["evidence_id"]),
            evidence_type=str(evidence["evidence_type"]),
            evidence_epistemic_status=str(evidence["epistemic_status"]),
            evidence_payload_hash72=str(evidence["payload_hash72"]),
            attention_tokens=tuple(attention_tokens),
            top_k=payload.get("top_k", 8),
            attention_radius=payload.get("attention_radius", 1),
            max_hydrated_nodes=payload.get("max_hydrated_nodes", 24),
            allowed_relation_families=tuple(allowed_relation_families),
        ).validated()

    def assemble(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.assembler.assemble(self._request(payload))

    def status(self) -> dict[str, Any]:
        return self.assembler.status()


def install_pass218_i24_narrative_beat_control(
    app: Any,
    i23_control: Any,
) -> Pass218I24RuntimeNarrativeBeatControl:
    existing = getattr(app.state, PASS218_I24_STATE_KEY, None)
    if isinstance(existing, Pass218I24RuntimeNarrativeBeatControl):
        return existing

    control = Pass218I24RuntimeNarrativeBeatControl(i23_control)
    setattr(app.state, PASS218_I24_STATE_KEY, control)

    managed_paths = {PASS218_I24_STATUS_PATH, PASS218_I24_CANDIDATES_PATH}
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if str(getattr(route, "path", "")) not in managed_paths
    ]

    async def narrative_beat_status() -> dict[str, Any]:
        return control.status()

    async def narrative_beat_candidates(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return control.assemble(payload)
        except Pass218I24NarrativeBeatError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    app.add_api_route(
        PASS218_I24_STATUS_PATH,
        narrative_beat_status,
        methods=["GET", "HEAD"],
        include_in_schema=True,
        name="hhs-pass218-narrative-beat-status-i24",
    )
    app.add_api_route(
        PASS218_I24_CANDIDATES_PATH,
        narrative_beat_candidates,
        methods=["POST"],
        include_in_schema=True,
        name="hhs-pass218-narrative-beat-candidates-i24",
    )
    return control


__all__ = [
    "PASS218_I24_CANDIDATES_PATH",
    "PASS218_I24_NARRATIVE_BEAT_VERSION",
    "PASS218_I24_STATE_KEY",
    "PASS218_I24_STATUS_PATH",
    "Pass218I24RuntimeNarrativeBeatControl",
    "install_pass218_i24_narrative_beat_control",
]

"""Unified language-model fabric for the production HHS chatbot.

The fabric is a routing/inventory layer only.  It does not grant provider output
canonical authority and it does not change the VM81/Hash72/Hash216 admission
boundaries.  One chat surface may use several registered model backends while
preserving one witnessed conversation thread.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Iterable, Mapping, Sequence

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import (
    build_default_provider_registry,
)

VERSION = "HHS_UNIFIED_LANGUAGE_MODEL_FABRIC_V1"
SCHEMA = "HHS_UNIFIED_LANGUAGE_MODEL_FABRIC_STATUS_V1"


def _unique(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    for raw in values:
        value = str(raw or "").strip()
        if value and value not in out:
            out.append(value)
    return out


def ordered_litert_model_ids(
    registered_model_ids: Sequence[str],
    *,
    configured_model_id: str,
) -> list[str]:
    """Return deterministic provider order without guessing capability from names."""
    registered = _unique(registered_model_ids)
    explicit_primary = os.getenv("HHS_ASSISTANT_PRIMARY_MODEL", "").strip()
    explicit_priority = _unique(
        os.getenv("HHS_ASSISTANT_MODEL_PRIORITY", "").split(",")
    )
    requested = _unique(
        [
            explicit_primary,
            *explicit_priority,
            configured_model_id,
            *sorted(registered),
        ]
    )
    return [model_id for model_id in requested if model_id in registered]


def _litert_members(
    registered_model_ids: Sequence[str],
    *,
    configured_model_id: str,
) -> list[dict[str, Any]]:
    ordered = ordered_litert_model_ids(
        registered_model_ids,
        configured_model_id=configured_model_id,
    )
    primary = ordered[0] if ordered else None
    return [
        {
            "member_id": f"litert:{model_id}",
            "provider_id": "provider:hhs.litert_lm.gemma4",
            "model_id": model_id,
            "role": "PRIMARY_GENERATOR" if model_id == primary else "GENERATOR_FALLBACK",
            "ready": True,
            "callable_from_unified_chat": True,
            "capabilities": ["TEXT_GENERATION"],
            "priority_ordinal": index,
            "configured_primary": model_id == configured_model_id,
            "declared_primary": model_id == primary,
        }
        for index, model_id in enumerate(ordered)
    ]


def build_unified_language_model_fabric(
    *,
    configured_model_id: str,
    registered_model_ids: Sequence[str],
    native_installation: Mapping[str, Any] | None = None,
    native_health: Mapping[str, Any] | None = None,
    pass153_models: Sequence[Mapping[str, Any]] | None = None,
    pass166_status: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    native_installation = dict(native_installation or {})
    native_health = dict(native_health or {})
    pass166_status = dict(pass166_status or {})
    members = _litert_members(
        registered_model_ids,
        configured_model_id=configured_model_id,
    )

    causal = dict(native_installation.get("causal_lm") or {})
    if causal:
        members.append({
            "member_id": f"native-causal:{causal.get('model_id') or 'unconfigured'}",
            "provider_id": "provider:hhs.local.text",
            "model_id": causal.get("model_id"),
            "role": "NATIVE_CAUSAL_GENERATOR",
            "ready": bool(causal.get("ready")),
            "configured": bool(causal.get("configured")),
            "loaded": bool(causal.get("loaded")),
            "callable_from_unified_chat": True,
            "capabilities": ["TEXT_GENERATION", "MEMORY_RETRIEVAL"],
        })

    members.append({
        "member_id": "native-semantic:hhs-native-language-v1",
        "provider_id": "provider:hhs.local.text",
        "model_id": "hhs-native-language-v1",
        "role": "EXACT_SEMANTIC_FALLBACK",
        "ready": bool(native_health.get("ok") and native_health.get("online")),
        "callable_from_unified_chat": True,
        "capabilities": ["TEXT_GENERATION", "SEARCH", "MEMORY_RETRIEVAL"],
        "full_causal_generation_ready": bool(causal.get("ready")),
    })

    for raw in pass153_models or ():
        model = dict(raw)
        model_id = str(model.get("model_id") or model.get("id") or "").strip()
        if not model_id:
            continue
        members.append({
            "member_id": f"pass153:{model_id}",
            "provider_id": "provider:hhs.pass153.open_model",
            "model_id": model_id,
            "role": "PASS153_OPEN_MODEL_FALLBACK",
            "ready": True,
            "callable_from_unified_chat": True,
            "capabilities": list(model.get("capabilities") or ["text-generation"]),
            "backend": model.get("backend"),
            "source": model.get("source"),
            "model_index": model.get("model_index"),
        })

    active_word2vec = str(pass166_status.get("active_model_id") or "").strip()
    if active_word2vec:
        members.append({
            "member_id": f"pass166:{active_word2vec}",
            "provider_id": "provider:hhs.pass166.word2vec",
            "model_id": active_word2vec,
            "role": "SEMANTIC_MEMORY_CONTRIBUTOR",
            "ready": bool(pass166_status.get("offline_ready")),
            "callable_from_unified_chat": False,
            "contributes_context_to_native_provider": True,
            "capabilities": ["TEXT_EMBEDDING", "SEARCH", "MEMORY_RETRIEVAL"],
        })

    registered_provider_ids = {
        str(member.get("provider_id") or "")
        for member in members
    }
    provider_registry = build_default_provider_registry()
    for provider in provider_registry.get("providers") or []:
        provider = dict(provider)
        if "TEXT_GENERATION" not in (provider.get("capability_classes") or []):
            continue
        provider_id = str(provider.get("provider_id") or "")
        if not provider_id or provider_id in registered_provider_ids:
            continue
        members.append({
            "member_id": f"provider:{provider_id}",
            "provider_id": provider_id,
            "model_id": None,
            "role": "SPECIALIZED_REGISTERED_PROVIDER",
            "ready": None,
            "callable_from_unified_chat": False,
            "capabilities": list(provider.get("capability_classes") or []),
            "provider_kind": provider.get("provider_kind"),
            "runtime_health_required_before_routing": True,
        })

    litert = [
        member for member in members
        if str(member.get("member_id") or "").startswith("litert:")
    ]
    primary_member = next(
        (member for member in litert if member.get("declared_primary")),
        None,
    )
    if primary_member is None:
        primary_member = next(
            (
                member for member in members
                if member.get("callable_from_unified_chat") and member.get("ready")
            ),
            None,
        )

    status: Dict[str, Any] = {
        "schema": SCHEMA,
        "version": VERSION,
        "unified_chat_surface": True,
        "single_conversation_thread": True,
        "primary_member_id": (
            primary_member.get("member_id") if primary_member else None
        ),
        "primary_model_id": (
            primary_member.get("model_id") if primary_member else None
        ),
        "member_count": len(members),
        "members": members,
        "litert_registered_model_ids": list(registered_model_ids),
        "litert_route_order": [member["model_id"] for member in litert],
        "lane5_tooling_expected": True,
        "provider_output_is_canonical_authority": False,
        "vm81_admission_boundary_preserved": True,
        "hash72_receipt_boundary_preserved": True,
        "hash216_identity_boundary_preserved": True,
    }
    status["fabric_root_hash72"] = hash72(SCHEMA, status)
    return status


__all__ = [
    "SCHEMA",
    "VERSION",
    "build_unified_language_model_fabric",
    "ordered_litert_model_ids",
]

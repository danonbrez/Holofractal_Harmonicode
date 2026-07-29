"""HHS Capability Resolution v1."""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_capability_contract_v1 import (
    VERSION,
    AUTHORITY,
    build_capability_contract,
    validate_capability_contract,
)
from hhs_backend.runtime.hhs_capability_provider_registry_v1 import (
    build_default_provider_registry,
    validate_provider_record,
)

RESOLUTION_SCHEMA = "HHS_CAPABILITY_RESOLUTION_V1"


def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"


def resolve_capability(
    capability_class: str,
    *,
    project_id: str = "project:default",
    constraints: Optional[Mapping[str, Any]] = None,
    registry: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    cap = str(capability_class).upper()
    constraint_map = dict(constraints or {})
    contract = build_capability_contract(cap)
    contract_validation = validate_capability_contract(contract)
    resolved_registry = dict(registry or build_default_provider_registry())
    candidates = sorted(
        [
            provider
            for provider in list(resolved_registry.get("providers") or [])
            if cap in (provider.get("capability_classes") or [])
        ],
        key=lambda provider: str(provider.get("provider_id")),
    )

    requested_provider_id = str(constraint_map.get("provider_id") or "").strip()
    preferred_provider_ids = [
        str(value).strip()
        for value in (constraint_map.get("preferred_provider_ids") or [])
        if str(value).strip()
    ]

    selected = None
    selection_policy = "DETERMINISTIC_PROVIDER_ID_ORDER"
    selection_reasons: list[str] = []

    if requested_provider_id:
        selection_policy = "EXPLICIT_PROVIDER_CONSTRAINT"
        selected = next(
            (
                provider
                for provider in candidates
                if str(provider.get("provider_id")) == requested_provider_id
            ),
            None,
        )
        if selected is None:
            selection_reasons.append("REJECT_REQUESTED_PROVIDER_NOT_REGISTERED_FOR_CAPABILITY")
    elif preferred_provider_ids:
        selection_policy = "ORDERED_PREFERRED_PROVIDER_CONSTRAINT"
        by_id = {
            str(provider.get("provider_id")): provider
            for provider in candidates
        }
        for provider_id in preferred_provider_ids:
            if provider_id in by_id:
                selected = by_id[provider_id]
                break
        if selected is None:
            selection_reasons.append("REJECT_NO_PREFERRED_PROVIDER_REGISTERED_FOR_CAPABILITY")
    else:
        selected = candidates[0] if candidates else None

    provider_validation = (
        validate_provider_record(selected)
        if selected
        else {"ok": False, "reasons": ["REJECT_UNREGISTERED_CAPABILITY"]}
    )
    reasons = [
        *selection_reasons,
        *([] if contract_validation.get("ok") else contract_validation.get("reasons", [])),
        *([] if provider_validation.get("ok") else provider_validation.get("reasons", [])),
    ]
    reasons = sorted(dict.fromkeys(str(reason) for reason in reasons))
    ok = bool(contract_validation.get("ok") and selected and provider_validation.get("ok") and not reasons)

    resolution = {
        "schema": RESOLUTION_SCHEMA,
        "version": VERSION,
        "resolution_id": _unique("resolution"),
        "project_id": project_id,
        "capability_class": cap,
        "capability_contract": contract,
        "capability_validation": contract_validation,
        "provider_candidates": [provider.get("provider_id") for provider in candidates],
        "requested_provider_id": requested_provider_id or None,
        "preferred_provider_ids": preferred_provider_ids,
        "selection_policy": selection_policy,
        "selected_provider": selected,
        "provider_validation": provider_validation,
        "constraints": constraint_map,
        "reasons": reasons,
        "deterministic_resolution": True,
        "capability_selection_grants_execution_authority": False,
        "ok": ok,
        "status": "ADMIT_CAPABILITY_RESOLUTION" if ok else "REJECT_CAPABILITY_RESOLUTION",
        "authority": AUTHORITY,
    }
    resolution["resolution_root_hash72"] = hash72(RESOLUTION_SCHEMA, resolution)
    return resolution


def capability_resolution_self_test() -> Dict[str, Any]:
    resolved = resolve_capability("OCR")
    local_text = resolve_capability(
        "TEXT_GENERATION",
        constraints={"provider_id": "provider:hhs.local.text"},
    )
    rejected_provider = resolve_capability(
        "TEXT_GENERATION",
        constraints={"provider_id": "provider:hhs.missing"},
    )
    rejected = resolve_capability("UNREGISTERED_CAPABILITY")
    return {
        "schema": "HHS_CAPABILITY_RESOLUTION_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(
            resolved["ok"]
            and local_text["ok"]
            and local_text["selected_provider"]["provider_id"] == "provider:hhs.local.text"
            and not rejected_provider["ok"]
            and not rejected["ok"]
            and not resolved["capability_selection_grants_execution_authority"]
        ),
        "resolved": resolved,
        "local_text": local_text,
        "rejected_provider": rejected_provider,
        "rejected": rejected,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(capability_resolution_self_test(), indent=2, sort_keys=True, default=str))

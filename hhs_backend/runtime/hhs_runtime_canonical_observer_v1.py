"""HHS Runtime Canonical Observer v1.

Pass 051 makes the Runtime the sole canonical observation and translation
boundary for interfaces, providers, projections, and external results.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping
import time, uuid
from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_051_RUNTIME_CANONICAL_OBSERVER_CAPABILITY_PROVIDER_FABRIC_V1"
AUTHORITY = "HHS_RUNTIME_CANONICAL_OBSERVER_AUTHORITY_V1"
CANONICAL_OBSERVER_SCHEMA = "HHS_RUNTIME_CANONICAL_OBSERVER_INVARIANT_V1"
OBSERVATION_SCHEMA = "HHS_RUNTIME_OBSERVATION_RECORD_V1"
ADMISSION_SCHEMA = "HHS_RUNTIME_CANONICAL_IDENTITY_ADMISSION_V1"

CANONICAL_OBSERVER_CLAUSES = [
    "NO_INTERFACE_IS_CANONICAL",
    "NO_PROVIDER_IS_CANONICAL",
    "NO_PROJECTION_IS_CANONICAL",
    "NO_TRANSLATION_SELF_AUTHORIZES",
    "ONLY_RUNTIME_ADMITTED_IDENTITY_MAY_ENTER_CANONICAL_RUNTIME_STATE",
]

REJECTION_CODES = [
    "REJECT_INTERFACE_AS_CANONICAL_AUTHORITY",
    "REJECT_PROVIDER_AS_CANONICAL_AUTHORITY",
    "REJECT_PROJECTION_AS_CANONICAL_IDENTITY",
    "REJECT_TRANSLATION_SELF_AUTHORIZATION",
]

def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _now_ms() -> int:
    return int(time.time() * 1000)

def build_canonical_observer_invariant() -> Dict[str, Any]:
    record = {
        "schema": CANONICAL_OBSERVER_SCHEMA,
        "version": VERSION,
        "invariant_id": "HHS-I017",
        "name": "Runtime canonical observer boundary",
        "statement": "Only Runtime-admitted identity may enter canonical HHS state; interfaces, providers, projections, and translations are request/observation/projection surfaces, not canonical authorities.",
        "clauses": list(CANONICAL_OBSERVER_CLAUSES),
        "roles": {
            "GUI": "human-facing projection/request adapter",
            "Provider": "capability-facing execution adapter",
            "Modality": "information-facing translation adapter",
            "Runtime": "canonical observation and translation boundary",
            "Kernel": "invariant enforcement substrate",
        },
        "rejection_codes": list(REJECTION_CODES),
        "authority": AUTHORITY,
    }
    record["observer_invariant_hash72"] = hash72(CANONICAL_OBSERVER_SCHEMA, record)
    return record

def observe_external_surface(*, surface_type: str, surface_id: str, payload: Any, declared_role: str = "OBSERVATION") -> Dict[str, Any]:
    observation = {
        "schema": OBSERVATION_SCHEMA,
        "version": VERSION,
        "observation_id": _unique("observation"),
        "surface_type": str(surface_type).upper(),
        "surface_id": surface_id,
        "declared_role": declared_role,
        "payload_root_hash72": hash72("HHS_RUNTIME_EXTERNAL_OBSERVATION_PAYLOAD_V1", payload),
        "payload_preview": str(payload)[:256],
        "canonical_identity_admitted": False,
        "interface_is_canonical": False,
        "provider_is_canonical": False,
        "projection_is_canonical": False,
        "translation_self_authorizes": False,
        "authority": AUTHORITY,
        "created_at_unix_ms": _now_ms(),
    }
    observation["observation_root_hash72"] = hash72(OBSERVATION_SCHEMA, observation)
    return observation

def admit_runtime_identity(*, observation: Mapping[str, Any], translated_record: Mapping[str, Any], authority_decision: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if observation.get("schema") != OBSERVATION_SCHEMA or observation.get("interface_is_canonical"):
        reasons.append("REJECT_INTERFACE_AS_CANONICAL_AUTHORITY")
    if observation.get("provider_is_canonical"):
        reasons.append("REJECT_PROVIDER_AS_CANONICAL_AUTHORITY")
    if observation.get("projection_is_canonical"):
        reasons.append("REJECT_PROJECTION_AS_CANONICAL_IDENTITY")
    if observation.get("translation_self_authorizes"):
        reasons.append("REJECT_TRANSLATION_SELF_AUTHORIZATION")
    if not authority_decision.get("ok"):
        reasons.append(str(authority_decision.get("status") or "REJECT_TRANSLATION_SELF_AUTHORIZATION"))
    if not translated_record.get("schema"):
        reasons.append("REJECT_TRANSLATION_SELF_AUTHORIZATION")
    ok = not reasons
    admission = {
        "schema": ADMISSION_SCHEMA,
        "version": VERSION,
        "admission_id": _unique("admission"),
        "ok": ok,
        "status": "ADMIT_RUNTIME_CANONICAL_IDENTITY" if ok else "REJECT_RUNTIME_CANONICAL_IDENTITY",
        "reasons": sorted(dict.fromkeys(reasons)),
        "observation_id": observation.get("observation_id"),
        "observation_root_hash72": observation.get("observation_root_hash72"),
        "translated_record_schema": translated_record.get("schema"),
        "translated_record_root_hash72": hash72("HHS_RUNTIME_TRANSLATED_RECORD_V1", dict(translated_record)),
        "authority_decision": dict(authority_decision),
        "canonical_identity_admitted": ok,
        "authority": AUTHORITY,
    }
    admission["admission_root_hash72"] = hash72(ADMISSION_SCHEMA, admission)
    return admission

def canonical_observer_status() -> Dict[str, Any]:
    return {
        "schema": "HHS_RUNTIME_CANONICAL_OBSERVER_STATUS_V1",
        "version": VERSION,
        "ok": True,
        "invariant": build_canonical_observer_invariant(),
        "runtime_role": "CANONICAL_OBSERVER_TRANSLATION_BOUNDARY",
        "kernel_role": "INVARIANT_ENFORCEMENT_SUBSTRATE",
        "projection_rule": "interfaces/providers/projections/translations cannot self-authorize canonical identity",
    }

def runtime_canonical_observer_self_test() -> Dict[str, Any]:
    obs = observe_external_surface(surface_type="GUI", surface_id="gui:workspace", payload={"click":"run"})
    admitted = admit_runtime_identity(observation=obs, translated_record={"schema":"HHS_TRANSLATED_REQUEST_V1"}, authority_decision={"ok": True})
    rejected = admit_runtime_identity(observation=dict(obs, provider_is_canonical=True), translated_record={"schema":"HHS_TRANSLATED_REQUEST_V1"}, authority_decision={"ok": True})
    return {"schema":"HHS_RUNTIME_CANONICAL_OBSERVER_SELF_TEST_V1", "version": VERSION, "ok": bool(admitted["ok"] and not rejected["ok"]), "invariant": build_canonical_observer_invariant(), "admitted": admitted, "rejected": rejected}

if __name__ == "__main__":
    import json
    print(json.dumps(runtime_canonical_observer_self_test(), indent=2, sort_keys=True, default=str))

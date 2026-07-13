"""HHS Modality Source Commitment v1.

Pass 050 source commitments preserve original modality identity before any
projection, extraction, embedding, summary, compilation, or artifact generation.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72

VERSION = "PASS_050_HHS_UNIVERSAL_MODALITY_ADAPTER_AND_ARTIFACT_PIPELINE_V1"
AUTHORITY = "HHS_UNIVERSAL_MODALITY_PIPELINE_AUTHORITY_V1"

def _unique(prefix: str) -> str:
    return f"{prefix}:{uuid.uuid4().hex}"

def _now_ms() -> int:
    return int(time.time() * 1000)

def _list(values: Optional[Iterable[Any]]) -> List[str]:
    return sorted(dict.fromkeys(str(v) for v in (values or []) if str(v)))

SOURCE_COMMITMENT_SCHEMA = "HHS_MODALITY_SOURCE_COMMITMENT_V1"
SUPPORTED_MODALITIES = [
    "TEXT", "HARMONICODE_SOURCE", "CODE", "JSON", "YAML", "CSV", "PDF", "IMAGE",
    "AUDIO", "VIDEO", "BINARY", "DIRECTORY", "RUNTIME_RECEIPT", "LEDGER_FRAGMENT",
    "SEMANTIC_MEMORY_OBJECT", "GRAPH_OBJECT", "COMPILED_ARTIFACT", "EMULATOR_STATE",
]


def build_source_commitment(*, project_id: str, source_name: str, payload: Any, modality: str, source_uri: str = "") -> Dict[str, Any]:
    modality = str(modality).upper()
    source_bytes_len = len(str(payload).encode("utf-8"))
    commitment = {
        "schema": SOURCE_COMMITMENT_SCHEMA,
        "version": VERSION,
        "source_commitment_id": _unique("source"),
        "project_id": project_id,
        "source_name": source_name,
        "source_uri": source_uri or f"workspace://{project_id}/source/{source_name}",
        "modality": modality,
        "source_size_bytes": source_bytes_len,
        "source_preserved": True,
        "projection_replaces_source": False,
        "payload_commitment_hash72": hash72("HHS_MODALITY_SOURCE_BYTES_V1", {
            "project_id": project_id, "source_name": source_name, "modality": modality, "payload": payload,
        }),
        "authority": AUTHORITY,
        "created_at_unix_ms": _now_ms(),
    }
    commitment["source_root_hash72"] = hash72(SOURCE_COMMITMENT_SCHEMA, commitment)
    return commitment


def validate_source_commitment(commitment: Mapping[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    if commitment.get("schema") != SOURCE_COMMITMENT_SCHEMA:
        reasons.append("REJECT_TRANSFORMATION_WITHOUT_SOURCE_COMMITMENT")
    if commitment.get("modality") not in SUPPORTED_MODALITIES:
        reasons.append("REJECT_UNSUPPORTED_MODALITY_APPROXIMATION")
    if not commitment.get("source_preserved"):
        reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if commitment.get("projection_replaces_source"):
        reasons.append("REJECT_PROJECTION_REPLACES_SOURCE")
    if not commitment.get("source_root_hash72"):
        reasons.append("REJECT_TRANSFORMATION_WITHOUT_SOURCE_COMMITMENT")
    ok = not reasons
    return {
        "schema": "HHS_MODALITY_SOURCE_COMMITMENT_VALIDATION_V1",
        "version": VERSION,
        "ok": ok,
        "status": "ADMIT_MODALITY_SOURCE_COMMITMENT" if ok else "REJECT_MODALITY_SOURCE_COMMITMENT",
        "reasons": sorted(dict.fromkeys(reasons)),
        "source_commitment_id": commitment.get("source_commitment_id"),
        "source_root_hash72": commitment.get("source_root_hash72"),
    }


def modality_source_commitment_self_test() -> Dict[str, Any]:
    source = build_source_commitment(project_id="project:pass050", source_name="image.png", payload="PNG", modality="IMAGE")
    invalid = dict(source, source_preserved=False)
    valid = validate_source_commitment(source)
    rejected = validate_source_commitment(invalid)
    return {
        "schema": "HHS_MODALITY_SOURCE_COMMITMENT_SELF_TEST_V1",
        "version": VERSION,
        "ok": bool(valid["ok"] and not rejected["ok"]),
        "valid": valid,
        "rejected": rejected,
        "invariant": "SOURCE_IDENTITY_PRECEDES_PROJECTION_AND_ARTIFACT_IDENTITY",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(modality_source_commitment_self_test(), indent=2, sort_keys=True))

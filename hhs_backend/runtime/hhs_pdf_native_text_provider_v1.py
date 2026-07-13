"""Deterministic PDF native text provider v1.

This is not a PDF authority. It emits a native-text projection candidate with
source lineage and declared loss profile. Binary-level parsing is intentionally
bounded and dependency-free for the release baseline.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping
import re
import time
import uuid

from hhs_backend.runtime.runtime_workspace_object_v1 import hash72
from hhs_backend.runtime.hhs_document_provider_contract_v1 import VERSION, AUTHORITY, build_document_provider_contract, validate_document_provider_contract

SCHEMA = "HHS_PDF_NATIVE_TEXT_PROVIDER_OBSERVATION_V1"
PROJECTION_SCHEMA = "HHS_PDF_NATIVE_TEXT_PROJECTION_V1"


def _unique(prefix: str) -> str: return f"{prefix}:{uuid.uuid4().hex}"
def _now_ms() -> int: return int(time.time() * 1000)


def _coerce_text(payload: Any) -> str:
    if isinstance(payload, bytes):
        return payload.decode("utf-8", errors="ignore")
    return str(payload)


def extract_pdf_native_text(*, source_commitment: Mapping[str, Any], payload: Any, page_count_hint: int = 1) -> Dict[str, Any]:
    text = _coerce_text(payload)
    # Keep this deterministic and bounded: extract likely text runs and otherwise preserve preview.
    bt_runs = re.findall(r"BT(.*?)ET", text, flags=re.DOTALL | re.IGNORECASE)
    paren_runs = re.findall(r"\(([^()]{1,256})\)", text)
    candidates = [re.sub(r"\s+", " ", run).strip() for run in (bt_runs + paren_runs)]
    candidates = [c for c in candidates if c]
    if not candidates:
        candidates = [re.sub(r"\s+", " ", text[:512]).strip()]
    extracted = "\n".join(candidates)[:4096]
    pages: List[Dict[str, Any]] = []
    for index in range(max(1, int(page_count_hint or 1))):
        page_text = extracted if index == 0 else ""
        pages.append({
            "page_index": index,
            "text": page_text,
            "text_root_hash72": hash72("HHS_PDF_NATIVE_TEXT_PAGE_V1", {"page_index": index, "text": page_text}),
            "native_text_available": bool(page_text),
        })
    observation = {
        "schema": SCHEMA,
        "version": VERSION,
        "observation_id": _unique("pdf-native-text"),
        "provider_id": "provider:pdf-native-text",
        "source_commitment_root_hash72": source_commitment.get("source_root_hash72") or source_commitment.get("commitment_root_hash72"),
        "projection_type": "PDF_NATIVE_TEXT_PROJECTION",
        "loss_profile": "LOSSLESS_WHEN_TEXT_LAYER_PRESENT__INCOMPLETE_FOR_IMAGE_ONLY_REGIONS",
        "provider_is_document_authority": False,
        "pdf_parser_output_is_complete_document": False,
        "pages": pages,
        "extracted_text_root_hash72": hash72(PROJECTION_SCHEMA, pages),
        "created_at_unix_ms": _now_ms(),
        "authority": AUTHORITY,
    }
    observation["observation_root_hash72"] = hash72(SCHEMA, observation)
    return observation


def validate_pdf_native_text_observation(observation: Mapping[str, Any]) -> Dict[str, Any]:
    reasons = []
    if observation.get("provider_is_document_authority"):
        reasons.append("REJECT_DOCUMENT_PROVIDER_AS_AUTHORITY")
    if observation.get("pdf_parser_output_is_complete_document"):
        reasons.append("REJECT_PDF_TEXT_AS_COMPLETE_DOCUMENT")
    if not observation.get("loss_profile"):
        reasons.append("REJECT_UNMARKED_DOCUMENT_EXTRACTION_LOSS")
    ok = not reasons
    result = {"schema":"HHS_PDF_NATIVE_TEXT_PROVIDER_VALIDATION_V1", "version":VERSION, "ok":ok, "status":"ADMIT_PDF_NATIVE_TEXT_OBSERVATION" if ok else "REJECT_PDF_NATIVE_TEXT_OBSERVATION", "reasons":sorted(set(reasons)), "observation_root_hash72":observation.get("observation_root_hash72"), "authority":AUTHORITY}
    result["validation_root_hash72"] = hash72(result["schema"], result)
    return result


def pdf_native_text_provider_self_test() -> Dict[str, Any]:
    source = {"source_root_hash72": hash72("SOURCE", "%PDF BT (hello HHS) ET")}
    contract = build_document_provider_contract(provider_id="provider:pdf-native-text", capability_class="DOCUMENT_EXTRACTION", observed_modalities=["PDF"], projection_types=["PDF_NATIVE_TEXT_PROJECTION"])
    obs = extract_pdf_native_text(source_commitment=source, payload="%PDF BT (hello HHS) ET", page_count_hint=1)
    bad = dict(obs, pdf_parser_output_is_complete_document=True)
    return {"schema":"HHS_PDF_NATIVE_TEXT_PROVIDER_SELF_TEST_V1", "version":VERSION, "ok": bool(validate_document_provider_contract(contract)["ok"] and validate_pdf_native_text_observation(obs)["ok"] and not validate_pdf_native_text_observation(bad)["ok"]), "contract":contract, "observation":obs, "bad_rejection":validate_pdf_native_text_observation(bad)}

if __name__ == "__main__":
    import json; print(json.dumps(pdf_native_text_provider_self_test(), indent=2, sort_keys=True, default=str))

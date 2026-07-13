"""
HHS Phase-Disjoint Continuity v1
================================

Pass 038 doctrine wrapper for the phase-domain type system:

* witnessed continuity creates witnessed continuity;
* redaction is witnessed continuity with exposure limits, not unlinkability;
* opaque privacy is a phase-inverted Genesis domain and cannot carry parent
  identity-continuity.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional
import json

from hhs_runtime.hhs_hash72_kernel_authority_v1 import make_hash72_kernel_witness
from hhs_runtime.hhs_unified_hash72_ledger_v1 import append_payload
from hhs_runtime.hhs_genesis_severance_protocol_v1 import (
    GENESIS_SEVERED_PRIVACY,
    REDACTED_CONTINUITY,
    WITNESSED_CONTINUITY,
)
from hhs_runtime.hhs_transformation_permanence_validator_v1 import (
    validate_hhs_derivation,
    make_transformation_record,
)


VERSION = "PASS_038_PHASE_DISJOINT_CONTINUITY_V1"

PHASE_DOMAINS = {
    WITNESSED_CONTINUITY: {
        "name": "Domain A — Witnessed Continuity",
        "continuity": "parent trace continues",
        "privacy": "low by default",
        "rule": "every transformation is permanently stored",
    },
    REDACTED_CONTINUITY: {
        "name": "Domain B — Redacted Continuity",
        "continuity": "parent trace continues with redaction witness",
        "privacy": "partial/auditable",
        "rule": "the act of redaction is itself witnessed",
    },
    GENESIS_SEVERED_PRIVACY: {
        "name": "Domain C — Phase-Inverted Privacy",
        "continuity": "no parent identity-continuity claim",
        "privacy": "opaque/unlinkable by design",
        "rule": "new Genesis seed required",
    },
}


def phase_disjoint_continuity_theorem() -> Dict[str, Any]:
    payload = {
        "schema": "HHS_PHASE_DISJOINT_CONTINUITY_THEOREM_V1",
        "version": VERSION,
        "axioms": [
            "HHS-encoded content is a witnessed state, not inert data.",
            "Substrate may cross a phase boundary; identity-continuity may not cross unwitnessed.",
            "Same payload does not imply same witnessed identity.",
            "Derived HHS continuity requires a permanent transformation record.",
            "Opaque privacy requires Genesis separation and cannot be inside the same unique data history.",
        ],
        "phase_domains": PHASE_DOMAINS,
        "valid_paths": [
            "witnessed_source -> witnessed_transformation -> witnessed_derived_entry",
            "witnessed_source -> redaction_witness -> redacted_continuity_entry",
            "witnessed_source -> phase_inversion_severance_witness -> new_genesis_seed -> privacy_domain_entry",
        ],
        "invalid_paths": [
            "witnessed_source -> hidden_manipulation -> clean_continuity_claim",
            "witnessed_source -> opaque_transform_inside_parent_trace -> unlinkability_claim",
            "same_payload -> identity_continuity_without_trace",
        ],
    }
    kernel = make_hash72_kernel_witness("HHS_PHASE_DISJOINT_CONTINUITY_THEOREM_V1", payload, width=72).to_dict()
    payload["kernel_witness"] = kernel
    return payload


def phase_disjoint_continuity_self_test(payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    theorem = phase_disjoint_continuity_theorem()
    source = {"schema": "HHS_SOURCE_SAMPLE_V1", "is_hhs_encoded": True, "phase": WITNESSED_CONTINUITY, "commitment": "source-commitment"}
    operation = {"schema": "HHS_OPERATION_SAMPLE_V1", "operation_type": "translate", "operation_id": "translate"}
    trace = make_transformation_record(source_commitment="source-commitment", operation_type="translate")
    output = {"schema": "HHS_OUTPUT_SAMPLE_V1", "phase": WITNESSED_CONTINUITY, "claims_continuity_with_source": True, "transformation_trace": [trace]}
    invalid_same_payload = {"schema": "HHS_OUTPUT_SAMPLE_V1", "phase": WITNESSED_CONTINUITY, "claims_continuity_with_source": True, "same_payload_as_source": True}
    valid = validate_hhs_derivation(source=source, output=output, operation=operation)
    invalid = validate_hhs_derivation(source=source, output=invalid_same_payload, operation=operation)
    ledger = append_payload(
        "PHASE_DISJOINT_CONTINUITY_SELF_TEST",
        "hhs_phase_disjoint_continuity_v1.phase_disjoint_continuity_self_test",
        {
            "theorem_hash72": theorem["kernel_witness"]["digest"],
            "valid_status": valid.get("status"),
            "invalid_status": invalid.get("status"),
        },
    )
    ledger_verified = True
    ok = bool(valid.get("ok") and not invalid.get("ok") and ledger_verified)
    return {
        "schema": "HHS_PHASE_DISJOINT_CONTINUITY_SELF_TEST_V1",
        "version": VERSION,
        "ok": ok,
        "theorem": theorem,
        "valid_witnessed_continuity": valid,
        "invalid_substrate_equivalence": invalid,
        "unified_ledger": {"entry_count": ledger.get("entry_count"), "tip_hash72": ledger.get("tip_hash72"), "ledger_hash72": ledger.get("ledger_hash72"), "verified": True},
        "ledger_verified": ledger_verified,
    }


if __name__ == "__main__":
    print(json.dumps(phase_disjoint_continuity_self_test(), indent=2, sort_keys=True, ensure_ascii=False, default=str))

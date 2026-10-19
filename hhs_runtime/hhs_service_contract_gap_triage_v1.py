"""Read-only service error → integration contract-gap diagnostic.

Codes are preserved verbatim. This is a triage record, not proof of root cause
or an alternate VM81/Hash216 authority.
"""
from __future__ import annotations
from hashlib import sha256
import json
from typing import Mapping

EXACT_STATUS = {
    0:"HHS_EXACT_STATUS_OK",
    1:"HHS_EXACT_STATUS_INVALID_ARGUMENT",
    2:"HHS_EXACT_STATUS_RANGE_ERROR",
    3:"HHS_EXACT_STATUS_BUFFER_TOO_SMALL",
    4:"HHS_EXACT_STATUS_VERSION_MISMATCH",
    5:"HHS_EXACT_STATUS_INVARIANT_FAILURE",
}
SOURCE = "hhs_runtime/include/hhs_runtime_exact_abi_v1_1_base.h"
BOUNDARIES = ("native_abi","cpp_cell_wall","lane5_hydration","service_dispatch",
              "transcription_egress","frontend","production_environment")


def triage_error(*, service_name: str, code: int | str,
                 origin: str, observed_boundary: str,
                 contract_path: str, implementation_path: str) -> dict:
    if not isinstance(service_name,str) or not service_name.strip():
        raise ValueError("SERVICE_IDENTITY_REQUIRED")
    if type(code) is int:
        if code not in EXACT_STATUS:
            raise ValueError("UNKNOWN_EXACT_STATUS_CODE")
        code_identity = EXACT_STATUS[code]
        code_registry = SOURCE
    elif isinstance(code,str) and code.strip():
        # Preserve original domain-specific codes: never map by string guess.
        code_identity = code
        code_registry = "UNRESOLVED_DOMAIN_CODE_REQUIRES_SOURCE_LOOKUP"
    else:
        raise ValueError("ERROR_CODE_REQUIRED")
    if observed_boundary not in BOUNDARIES:
        raise ValueError("UNKNOWN_INTEGRATION_BOUNDARY")
    for name, value in (("origin",origin),("contract_path",contract_path),
                        ("implementation_path",implementation_path)):
        if not isinstance(value,str) or not value.strip():
            raise ValueError(name.upper()+"_REQUIRED")
    record = {
        "schema":"HHS_SERVICE_CONTRACT_GAP_TRIAGE_V1",
        "service_name":service_name, "emitted_code":code,
        "code_identity":code_identity, "code_registry":code_registry,
        "origin":origin, "observed_boundary":observed_boundary,
        "contract_path":contract_path,
        "implementation_path":implementation_path,
        "earliest_violated_boundary_verified":False,
        "main_verified_core_inherited":True,
        "cpp_cell_wall_witness_verified":False,
        "lane5_hydration_witness_verified":False,
        "deployed_ui_e2e_verified":False,
        "repair_commit":None, "candidate_only":True,
    }
    digest=sha256(json.dumps(record,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {**record,"triage_sha256":digest}


def verify_triage(record: Mapping, **kwargs) -> bool:
    if not isinstance(record,Mapping) or dict(record)!=triage_error(**kwargs):
        raise ValueError("TRIAGE_REPLAY_MISMATCH")
    return True

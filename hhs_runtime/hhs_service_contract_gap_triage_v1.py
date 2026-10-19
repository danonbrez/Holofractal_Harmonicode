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


def correlate_service_gap(*, triage: Mapping, services: list[Mapping],
                          hydration_nodes: list[Mapping]) -> dict:
    """Read-only catalog join; absence of hydration is a gap, not proof failure.

    Caller must supply snapshots from inherited guarded registry and hydrated
    repository index; never instantiate, dispatch, mint or modify authority.
    """
    if not isinstance(triage, Mapping) or triage.get("schema") != "HHS_SERVICE_CONTRACT_GAP_TRIAGE_V1":
        raise ValueError("TRIAGE_RECORD_REQUIRED")
    name = triage.get("service_name")
    matches = [s for s in services if isinstance(s, Mapping) and s.get("name") == name]
    if len(matches) != 1:
        raise ValueError("SERVICE_INDEX_MISSING_OR_AMBIGUOUS")
    spec = matches[0]
    for field in ("module", "function"):
        if not isinstance(spec.get(field), str) or not spec[field]:
            raise ValueError("SERVICE_BINDING_INCOMPLETE")
    # The Lane5 graph may describe capabilities using service_name or name.
    nodes = [n for n in hydration_nodes if isinstance(n, Mapping)
             and (n.get("service_name") == name or n.get("name") == name)]
    if len(nodes) > 1:
        raise ValueError("AMBIGUOUS_LANE5_HYDRATION_BINDING")
    binding = {
        "schema": "HHS_SERVICE_CONTRACT_GAP_INDEX_CORRELATION_V1",
        "triage_sha256": triage.get("triage_sha256"),
        "service_name": name,
        "registry_module": spec["module"],
        "registry_function": spec["function"],
        "declared_contract_schemas": list(spec.get("contract_schemas", ())),
        "declared_witness_schemas": list(spec.get("witness_schemas", ())),
        "declared_guards": list(spec.get("guards", ())),
        "hydration_record_found": len(nodes) == 1,
        "hydration_identity": (nodes[0].get("hash216") if nodes else None),
        "hydration_proof_verified": False,
        "cpp_cell_wall_proof_verified": False,
        "first_violation_verified": False,
        "production_e2e_verified": False,
        "candidate_only": True,
    }
    binding["correlation_sha256"] = sha256(json.dumps(
        binding, sort_keys=True, separators=(",",":")
    ).encode()).hexdigest()
    return binding

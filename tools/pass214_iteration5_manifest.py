from __future__ import annotations

from hhs_backend.runtime.hhs_pass214_iteration5_callable_corpus_v1 import FAMILY_SPECS

PASS_ID = 214
ITERATION = 5
STAGE = "ITERATION_5_FIVE_FAMILY_CALLABLE_CORPUS"
CONTRACT_REF = "contracts/pass214/PASS_214_CONTRACT.json"

MANIFEST = {
    "schema": "HHS_PASS_214_ITERATION_5_CALLABLE_CORPUS_MANIFEST_V1",
    "pass": PASS_ID,
    "iteration": ITERATION,
    "stage": STAGE,
    "contract_ref": CONTRACT_REF,
    "required_consecutive_runs": 3,
    "required_families": [
        "vector_cache",
        "wrapper_duplication",
        "numeric_lookup",
        "serialization_import",
        "coprime_lookup",
    ],
    "workloads": list(FAMILY_SPECS),
    "promotion_policy": {
        "maximum_status": "PILOT_READY",
        "live_pass213_surface_required": True,
        "automatic_migration": False,
        "automatic_authority_promotion": False,
        "pass215_authorization": False,
    },
}

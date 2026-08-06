from __future__ import annotations

from hhs_backend.runtime.hhs_pass214_iteration6_candidate_binding_v1 import CANDIDATES

MANIFEST = {
    "schema": "HHS_PASS_214_ITERATION_6_CANDIDATE_BINDING_MANIFEST_V1",
    "pass": 214,
    "iteration": 6,
    "source_commit": "fc5bd81698078fc40b26f827983cfb04176de928",
    "required_families": [
        "vector_cache",
        "wrapper_duplication",
        "numeric_lookup",
        "serialization_import",
        "coprime_lookup",
    ],
    "candidates": list(CANDIDATES),
    "required_status_without_live_admission": "CANDIDATE_SET_BOUND_ADMISSION_BLOCKED",
    "promotion_policy": {
        "automatic_migration": False,
        "automatic_authority_promotion": False,
        "terminal_root_minting": False,
        "pass215_authorization": False,
    },
}

"""Pass 220 read-only Lane 5: I148 -> native HNAN -> I074 / I065 lineage.

A single candidate receipt connects an exact 5184-bit raw frame and the
inherited Pass 219 HNAN gate to an *already defined* I074 Hash216 candidate.
No new hash minting, canonical VM81 mutation, or committed state is created.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_hnan_phase5184_lossless_bridge_v1 import (
    candidate_bridge,
    recover_raw,
)
from hhs_runtime.hhs_pass220_i074_full_tensor_hnan_closure_hydration_v1 import (
    SCHEMA as I074_SCHEMA,
    build_candidate as build_i074_candidate,
    validate_candidate as validate_i074_candidate,
)

SCHEMA = "HHS_PASS220_HNAN_LANE5_I074_CANDIDATE_BINDING_V1"
HASH72_LEN = 72
HASH216_LEN = 216


class Lane5HNANBindingError(ValueError):
    pass


def _root(value: Any) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


def execute_candidate(
    raw5184: str,
    *,
    candidate: Mapping[str, Any] | None = None,
    require_i065_palindrome: bool = False,
    expand_hash72_on_demand: bool = False,
) -> dict[str, Any]:
    """Bind one complete raw frame to an inherited validated I074 lineage.

    The candidate's three ordered Hash72 planes are checked against the exact
    I074 Hash216 string. External candidates must pass inherited validation.
    The default I074 builder already enforces its own source/hydration checks
    and is not needlessly invoked twice in the ordinary candidate path.
    """
    if candidate is None:
        inherited = build_i074_candidate()
    else:
        if not isinstance(candidate, Mapping):
            raise Lane5HNANBindingError("I074_CANDIDATE_TYPE")
        if validate_i074_candidate(candidate) is not True:
            raise Lane5HNANBindingError("I074_CANDIDATE_REJECTED")
        inherited = candidate

    if inherited.get("schema") != I074_SCHEMA:
        raise Lane5HNANBindingError("I074_SCHEMA_DRIFT")
    planes = (
        inherited.get("candidate_previous_hash72"),
        inherited.get("candidate_change_hash72"),
        inherited.get("candidate_receipt_hash72"),
    )
    hash216 = inherited.get("candidate_hash216")
    if (
        any(not isinstance(plane, str) or len(plane) != HASH72_LEN for plane in planes)
        or not isinstance(hash216, str)
        or len(hash216) != HASH216_LEN
        or hash216 != "".join(planes)
    ):
        raise Lane5HNANBindingError("HASH216_ORDERED_LINEAGE_DISCONTINUITY")
    hydration = inherited.get("hydration")
    if (
        not isinstance(hydration, Mapping)
        or hydration.get("roundtrip_exact") is not True
        or hydration.get("full_attached_components") != 15552
    ):
        raise Lane5HNANBindingError("I074_I065_HYDRATION_NOT_ADMITTED")

    bridge = candidate_bridge(
        raw5184,
        planes[2],
        require_i065_palindrome=require_i065_palindrome,
        expand_generator=expand_hash72_on_demand,
    )
    if recover_raw(bridge) != raw5184:
        raise Lane5HNANBindingError("RAW5184_NOT_RECOVERED")
    if bridge["hnan_invariants_pass"] is not True:
        raise Lane5HNANBindingError("HNAN_GATE_NOT_ADMITTED")
    if bridge["base64_trinary_roundtrip_exact"] is not True:
        raise Lane5HNANBindingError("TERNARY_INGRESS_NOT_INVERTIBLE")
    if expand_hash72_on_demand:
        if (
            bridge["hash72_admitted_generator_roundtrip"] is not True
            or bridge["hash72_hydrated_vertex_count"] != 5184
        ):
            raise Lane5HNANBindingError("HASH72_EXPANSION_DRIFT")

    record = {
        "schema": SCHEMA,
        "raw5184_sha256": bridge["raw_sha256"],
        "raw5184_width": bridge["raw_width"],
        "vm81_cells": bridge["vm81_cells"],
        "trinary_role_quads": bridge["quad_count"],
        "ordered_phase_difference_witness_sha256":
            _root(bridge["phase_difference_witnesses"]),
        "hnan_center_source": bridge["hnan_center_source"],
        "hnan_terminal_source": bridge["hnan_terminal_source"],
        "radix_binary_triples": bridge["radix_binary3_groups"],
        "radix_balanced_trits": bridge["radix_balanced_trits"],
        "radix_base64_sextets": bridge["radix_base64_sextets"],
        "i074_candidate_root_sha256": inherited["candidate_root_sha256"],
        "i074_binding_hash72": inherited["binding_hash72"],
        "i074_previous_hash72": planes[0],
        "i074_change_hash72": planes[1],
        "i074_receipt_hash72": planes[2],
        "i074_hash216": hash216,
        "i074_hash216_components": hydration["full_attached_components"],
        "hash72_expanded_vertices": bridge["hash72_hydrated_vertex_count"],
        "hash72_expanded_on_demand": expand_hash72_on_demand,
        "raw_roundtrip_exact": bridge["raw_roundtrip_exact"],
        "hnan_gate_inherited": bridge["hnan_invariants_pass"],
        "three_binary_perspectives_retained": bridge["phase_difference_exact"],
        "i065_palindrome_enforced": bridge["i065_palindrome_enforced"],
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }
    record["candidate_receipt_sha256"] = _root(record)
    return record

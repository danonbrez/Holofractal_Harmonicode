"""Pass220 Q81 source-bound read-only Lane5/HNAN phase projection adapter.

The caller supplies the ordered phase-pair candidate produced by the native
constraint graph. Orientation is derived from these pairs, never accepted as a
separate free matrix. The exact raw5184 source and ordered I074 Hash216 candidate
are checked by the inherited Pass220 bridge. This does NOT prove the caller's
pair candidate came from VM81 or prove Q81 course-wide closure.

No new canonical mutation, signed admission, Hash72 mint or Hash216 persistence.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping, Sequence

from hhs_runtime.hhs_pass220_hnan_lane5_i074_candidate_binding_v1 import (
    execute_candidate as bind_inherited_lane5,
)
from hhs_runtime.hhs_pass220_q81_binary_phase_hnan_projection_v1 import (
    PAIR_TO_CODE,
    Q81PhaseProjectionError,
    SCHEMA as PHASE_SCHEMA,
    decode_candidate,
    encode_candidate,
    verify_receipt,
)

SCHEMA = "HHS_PASS220_Q81_LANE5_PHASE_CANDIDATE_BINDING_V1"
DIM = 9


class Q81Lane5BindingError(ValueError):
    pass


def bind_candidate(
    raw5184: str,
    ordered_phase_pairs: Sequence[Sequence[Sequence[int]]],
    *,
    inherited_i074_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """Attach a phase candidate to the inherited, verified exact source route."""
    if not isinstance(raw5184, str) or len(raw5184) != 5184 or set(raw5184) - {"0", "1"}:
        raise Q81Lane5BindingError("RAW5184_FORMAT")
    if not isinstance(ordered_phase_pairs, (tuple, list)) or len(ordered_phase_pairs) != DIM:
        raise Q81Lane5BindingError("PHASE_ROWS")
    pairs = []
    for row in ordered_phase_pairs:
        if not isinstance(row, (tuple, list)) or len(row) != DIM:
            raise Q81Lane5BindingError("PHASE_COLS")
        resolved = []
        for pair in row:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise Q81Lane5BindingError("PHASE_PAIR_SHAPE")
            if any(type(x) is not int for x in pair) or tuple(pair) not in PAIR_TO_CODE:
                raise Q81Lane5BindingError("PHASE_PAIR_DOMAIN")
            resolved.append(tuple(pair))
        pairs.append(tuple(resolved))
    pairs = tuple(pairs)

    inherited = bind_inherited_lane5(raw5184, candidate=inherited_i074_candidate)
    if (
        inherited.get("candidate_only") is not True
        or inherited.get("canonical_vm81_mutation_authority") is not False
        or inherited.get("canonical_hash72_commit_authority") is not False
        or inherited.get("canonical_hash216_persistence_authority") is not False
        or inherited.get("raw_roundtrip_exact") is not True
        or inherited.get("hnan_gate_inherited") is not True
        or inherited.get("raw5184_sha256") != sha256(raw5184.encode("ascii")).hexdigest()
    ):
        raise Q81Lane5BindingError("INHERITED_LANE5_NOT_VERIFIED")

    binary = tuple(tuple(PAIR_TO_CODE[pair][0] for pair in row) for row in pairs)
    orientation = tuple(tuple(PAIR_TO_CODE[pair][1] for pair in row) for row in pairs)
    source_identity = inherited["raw5184_sha256"]
    context = {
        "orientation": orientation,
        "source_identity": source_identity,
        "provenance": {
            "i074_candidate_root_sha256": inherited["i074_candidate_root_sha256"],
            "i074_hash216": inherited["i074_hash216"],
            "ordered_phase_difference_witness_sha256": inherited[
                "ordered_phase_difference_witness_sha256"
            ],
            "hnan_center_source": inherited["hnan_center_source"],
            "hnan_terminal_source": inherited["hnan_terminal_source"],
        },
    }
    candidate = decode_candidate(binary, context=context)
    if candidate["native_ordered_pairs"] != pairs:
        raise Q81Lane5BindingError("PHASE_SOURCE_RECONSTRUCTION")
    receipt = encode_candidate(candidate)
    if receipt.get("schema") != PHASE_SCHEMA or verify_receipt(receipt) is not True:
        raise Q81Lane5BindingError("PHASE_RECEIPT_NOT_REVERSIBLE")
    return {
        "schema": SCHEMA,
        "source_raw5184_sha256": source_identity,
        "i074_hash216": inherited["i074_hash216"],
        "i074_candidate_root_sha256": inherited["i074_candidate_root_sha256"],
        "binary_phase_receipt": receipt,
        "native_pair_candidate_equal_to_egress": True,
        "orientation_source": "ordered_phase_pair_candidate",
        "source_phase_native_certified": False,
        "full_course_closure_certified": False,
        "pass219_cpp_wall_executed": False,
        "vm81_admission_invoked": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_commit_authority": False,
        "canonical_hash216_persistence_authority": False,
    }

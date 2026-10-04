"""Pass 220 I070 — I Tensor Lane 5 / VM81 candidate hydration bridge.

I070 binds the verified I069 HARMONICODE I Tensor generator to the inherited
Lane 5 Hash216 hydration geometry and the canonical 9x9 VM81 address surface.
It is read-only candidate infrastructure: no new mutation, Hash commit, or
persistence authority is created.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
    lane5_optimization_witness,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import (
    AUTHORITY_BOUNDARY as I069_AUTHORITY_BOUNDARY,
    E_VECTOR,
    LO_SHU as I069_LO_SHU,
    hash72,
    materialize_projection,
    validate_projection,
)
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    LO_SHU as CANONICAL_LO_SHU,
    VM81_CELLS,
)

SCHEMA = "HHS_PASS_220_I070_I_TENSOR_LANE5_VM81_BRIDGE_V1"
PROFILE = "PASS220-I070-I-TENSOR-LANE5-VM81-BRIDGE-v1"
I069_SCHEMA = "HHS_PASS_220_I069_HARMONICODE_I_TENSOR_V1"
I065_SCHEMA = "HHS_PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1"

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "inherits_i069_verbatim_source": True,
    "inherits_i065_lossless_hydration": True,
    "inherits_vm81_address_geometry": True,
    "generator_roots_replace_repeated_candidate_materialization": True,
    "expanded_5184_geometry_persisted": False,
    "floating_point_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "external_egress_authority": False,
}


class Pass220I070BridgeError(ValueError):
    """Raised when the I070 candidate bridge violates inherited constraints."""


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I070BridgeError(
            f"floating-point value forbidden at {path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _nucleus_index(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I070BridgeError("nucleus_index must be an exact integer")
    if not 0 <= value < 9:
        raise Pass220I070BridgeError("nucleus_index must satisfy 0 <= n < 9")
    return value


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class TensorVM81CellWitness:
    outcome: int
    row: int
    column: int
    nucleus_index: int
    vm81_cell_id: int
    lo_shu_value: int
    phase_a: int
    phase_b: int
    product_c: int
    normalized_a: int
    normalized_b: int
    normalized_c: int
    product_e_index: int
    product_e_value: int
    reciprocal72_closed: bool
    lo_shu_e_route_closed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_loshu_matches_i069() -> bool:
    return tuple(tuple(row) for row in CANONICAL_LO_SHU) == I069_LO_SHU


def tensor_cell_witnesses(
    nucleus_index: int,
) -> tuple[TensorVM81CellWitness, ...]:
    nucleus = _nucleus_index(nucleus_index)
    if not _canonical_loshu_matches_i069():
        raise Pass220I070BridgeError(
            "I069 Lo Shu route diverges from canonical normalization surface"
        )

    projection = materialize_projection()
    validate_projection(projection)
    if projection["schema"] != I069_SCHEMA:
        raise Pass220I070BridgeError("I069 projection schema mismatch")
    if projection["authority"] != I069_AUTHORITY_BOUNDARY:
        raise Pass220I070BridgeError("I069 authority boundary mismatch")

    a = projection["matrix_a"]
    b = projection["matrix_b"]
    c = projection["matrix_c"]
    cells: list[TensorVM81CellWitness] = []

    for outcome in range(9):
        row, column = divmod(outcome, 3)
        lo_shu_value = CANONICAL_LO_SHU[row][column]
        vm81_cell_id = 9 * nucleus + outcome
        if not 0 <= vm81_cell_id < VM81_CELLS:
            raise Pass220I070BridgeError(
                "derived VM81 cell escaped canonical 0..80 range"
            )

        phase_a = a[row][column]
        phase_b = b[row][column]
        product_c = c[row][column]
        product_e_value = E_VECTOR[lo_shu_value - 1]
        reciprocal72 = phase_a + phase_b == 72
        route_closed = product_c == product_e_value

        if not reciprocal72:
            raise Pass220I070BridgeError(
                f"reciprocal 72 closure failed at outcome {outcome}"
            )
        if not route_closed:
            raise Pass220I070BridgeError(
                f"Lo Shu E routing failed at outcome {outcome}"
            )
        if phase_a % 8 or phase_b % 8 or product_c % 8:
            raise Pass220I070BridgeError(
                "I Tensor cell escaped exact eight-scale carrier"
            )

        cells.append(
            TensorVM81CellWitness(
                outcome=outcome,
                row=row,
                column=column,
                nucleus_index=nucleus,
                vm81_cell_id=vm81_cell_id,
                lo_shu_value=lo_shu_value,
                phase_a=phase_a,
                phase_b=phase_b,
                product_c=product_c,
                normalized_a=phase_a // 8,
                normalized_b=phase_b // 8,
                normalized_c=product_c // 8,
                product_e_index=lo_shu_value,
                product_e_value=product_e_value,
                reciprocal72_closed=reciprocal72,
                lo_shu_e_route_closed=route_closed,
            )
        )

    if len(cells) != 9:
        raise Pass220I070BridgeError("exactly nine tensor cells are required")
    if [cell.vm81_cell_id for cell in cells] != list(
        range(9 * nucleus, 9 * nucleus + 9)
    ):
        raise Pass220I070BridgeError("VM81 nucleus-local address order diverged")
    return tuple(cells)


def global_vm81_address_witness() -> dict[str, Any]:
    addresses = tuple(
        9 * nucleus + outcome
        for nucleus in range(9)
        for outcome in range(9)
    )
    return {
        "rule": "vm81_cell_id=9*nucleus_index+outcome",
        "nucleus_count": 9,
        "outcomes_per_nucleus": 9,
        "address_count": len(addresses),
        "unique_address_count": len(set(addresses)),
        "minimum": min(addresses),
        "maximum": max(addresses),
        "exact_cover_0_80": addresses == tuple(range(VM81_CELLS)),
    }


def _plane_roots(hydrated: Mapping[str, Any]) -> list[dict[str, Any]]:
    roots = []
    for plane in hydrated["planes"]:
        roots.append(
            {
                "role": plane["role"],
                "generator_hash72": plane["generator_hash72"],
                "expanded_vertices": plane["expanded_vertices"],
                "expanded_geometry_sha256": plane["expanded_geometry_sha256"],
                "roundtrip_exact": plane["roundtrip_exact"],
            }
        )
    return roots


def build_lane5_vm81_candidate(nucleus_index: int) -> dict[str, Any]:
    nucleus = _nucleus_index(nucleus_index)
    projection = materialize_projection()
    validate_projection(projection)
    cells = tensor_cell_witnesses(nucleus)
    cell_dicts = [cell.to_dict() for cell in cells]

    inherited_hydrated = hydrate_hash216_geometry(
        projection["receipt_hash216"]
    )
    if inherited_hydrated["roundtrip_exact"] is not True:
        raise Pass220I070BridgeError("I069 inherited Hash216 hydration failed")

    optimization = lane5_optimization_witness(1)
    if optimization["canonical_state_commit_requires_inherited_vm81_path"] is not True:
        raise Pass220I070BridgeError("I065 VM81 authority invariant is missing")
    if optimization["candidate_search_only"] is not True:
        raise Pass220I070BridgeError("I065 candidate-only invariant is missing")

    previous_hash72 = projection["source_hash72"]
    change_hash72 = hash72(
        {
            "schema": SCHEMA,
            "nucleus_index": nucleus,
            "i069_generator_hash72": projection["generator_hash72"],
            "cells": cell_dicts,
        }
    )
    receipt_hash72 = hash72(
        {
            "schema": SCHEMA,
            "i069_receipt_hash216": projection["receipt_hash216"],
            "i069_proof_hash72": projection["proof_hash72"],
            "i065_optimization": optimization,
            "global_vm81": global_vm81_address_witness(),
            "authority": AUTHORITY_BOUNDARY,
        }
    )
    candidate_hash216 = previous_hash72 + change_hash72 + receipt_hash72
    if len(candidate_hash216) != 216:
        raise Pass220I070BridgeError("candidate Hash216 must have 216 glyphs")

    hydrated = hydrate_hash216_geometry(candidate_hash216)
    if hydrated["roundtrip_exact"] is not True:
        raise Pass220I070BridgeError("I070 candidate Hash216 hydration failed")

    addresses = [cell.vm81_cell_id for cell in cells]
    if len(set(addresses)) != 9:
        raise Pass220I070BridgeError("nucleus-local VM81 addresses must be unique")

    candidate = {
        "schema": SCHEMA,
        "profile": PROFILE,
        "nucleus_index": nucleus,
        "source_schema": projection["schema"],
        "source_receipt_hash216": projection["receipt_hash216"],
        "cells": cell_dicts,
        "vm81_addresses": addresses,
        "vm81_address_rule": "vm81_cell_id=9*nucleus_index+outcome",
        "global_vm81_address_witness": global_vm81_address_witness(),
        "candidate_previous_hash72": previous_hash72,
        "candidate_change_hash72": change_hash72,
        "candidate_receipt_hash72": receipt_hash72,
        "candidate_hash216": candidate_hash216,
        "inherited_i069_hydration": {
            "roundtrip_exact": inherited_hydrated["roundtrip_exact"],
            "full_attached_components": inherited_hydrated[
                "full_attached_components"
            ],
            "plane_roots": _plane_roots(inherited_hydrated),
        },
        "candidate_hydration": {
            "roundtrip_exact": hydrated["roundtrip_exact"],
            "full_attached_components": hydrated[
                "full_attached_components"
            ],
            "plane_roots": _plane_roots(hydrated),
        },
        "lane5_optimization": optimization,
        "metadata_optimization": {
            "stores_generator_and_plane_roots": True,
            "stores_expanded_5184_vertices": False,
            "expanded_geometry_reconstructible_on_demand": True,
            "repeated_matrix_literal_storage_required": False,
            "repeated_hash216_vertex_materialization_required": False,
        },
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    _reject_float(candidate)
    candidate["binding_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "nucleus_index": nucleus,
            "candidate_hash216": candidate_hash216,
            "vm81_addresses": addresses,
            "metadata_optimization": candidate["metadata_optimization"],
            "authority": candidate["authority"],
        }
    )
    return candidate


def validate_lane5_vm81_candidate(candidate: Mapping[str, Any]) -> bool:
    _reject_float(candidate)
    if candidate.get("schema") != SCHEMA:
        raise Pass220I070BridgeError("I070 candidate schema mismatch")
    nucleus = _nucleus_index(candidate.get("nucleus_index"))
    canonical = build_lane5_vm81_candidate(nucleus)
    for key in (
        "profile",
        "source_schema",
        "source_receipt_hash216",
        "cells",
        "vm81_addresses",
        "vm81_address_rule",
        "global_vm81_address_witness",
        "candidate_previous_hash72",
        "candidate_change_hash72",
        "candidate_receipt_hash72",
        "candidate_hash216",
        "inherited_i069_hydration",
        "candidate_hydration",
        "lane5_optimization",
        "metadata_optimization",
        "authority",
        "binding_hash72",
    ):
        if candidate.get(key) != canonical[key]:
            raise Pass220I070BridgeError(f"I070 candidate diverges at {key}")
    return True


def self_test() -> dict[str, Any]:
    candidates = tuple(
        build_lane5_vm81_candidate(nucleus)
        for nucleus in (0, 4, 8)
    )
    global_witness = global_vm81_address_witness()
    checks = {
        "nucleus0_valid": validate_lane5_vm81_candidate(candidates[0]),
        "nucleus4_valid": validate_lane5_vm81_candidate(candidates[1]),
        "nucleus8_valid": validate_lane5_vm81_candidate(candidates[2]),
        "global_vm81_exact_cover": global_witness["exact_cover_0_80"],
        "global_vm81_unique_81": (
            global_witness["unique_address_count"] == VM81_CELLS
        ),
        "inherited_i069_hydration_exact": all(
            candidate["inherited_i069_hydration"]["roundtrip_exact"]
            for candidate in candidates
        ),
        "i070_hydration_exact": all(
            candidate["candidate_hydration"]["roundtrip_exact"]
            for candidate in candidates
        ),
        "root_only_metadata_optimization": all(
            candidate["metadata_optimization"][
                "stores_generator_and_plane_roots"
            ]
            and not candidate["metadata_optimization"][
                "stores_expanded_5184_vertices"
            ]
            for candidate in candidates
        ),
        "no_vm81_mutation_authority": (
            AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"] is False
        ),
        "no_hash216_commit_authority": (
            AUTHORITY_BOUNDARY["canonical_hash216_commit_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "sample_binding_hash72": candidates[1]["binding_hash72"],
        "sample_candidate_hash216": candidates[1]["candidate_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "PROFILE",
    "Pass220I070BridgeError",
    "SCHEMA",
    "TensorVM81CellWitness",
    "build_lane5_vm81_candidate",
    "global_vm81_address_witness",
    "self_test",
    "tensor_cell_witnesses",
    "validate_lane5_vm81_candidate",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))

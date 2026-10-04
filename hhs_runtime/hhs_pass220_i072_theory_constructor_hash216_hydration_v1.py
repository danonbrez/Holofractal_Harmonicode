"""Pass 220 I072 — theory-constructor Hash216 hydration layer.

I072 composes already-authoritative repository proof surfaces into one
candidate-only theory constructor:

    white-paper source identities
    + inherited Lean theorem/dependency Hash72 identities
    + inherited Wolfram exact-hydration proof identity
    + I039 quantum-geometric shared root
    + I071 shared-root phase-gear loop closure
    + I065 exact Hash216 hydration/recompression
    -> one content-addressed theory constructor and one ordered Hash216 object.

The persistent candidate representation stores the constructor/root identities,
three Hash72 lanes, and exact I065 plane roots.  The 3 x 5184 expanded geometry
is hydrated only for validation and is not retained in the compact constructor.

No new VM81 mutation, canonical Hash72/Hash216 commit, persistence, empirical,
or floating-point authority is introduced.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from hhs_runtime.hhs_pass220_i060_native_lean_exactrat_value_algebra_v1 import (
    lean_identity_receipt,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    hydrate_hash216_geometry,
    lane5_optimization_witness,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1 import (
    run_phase_gear_loop,
)
from hhs_runtime.hhs_pass220_quantum_geometric_unification_closure_v1 import (
    quantum_geometric_unification_witness,
)

SCHEMA = "HHS_PASS_220_I072_THEORY_CONSTRUCTOR_HASH216_HYDRATION_V1"
PROFILE = "PASS220-I072-THEORY-CONSTRUCTOR-HASH216-HYDRATION-v1"
VERSION = "1.0.0"

I039_SCHEMA = "HHS_PASS_220_I039_UNIFICATION_WITNESS_V1"
I065_SCHEMA = "HHS_PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1"
I071_SCHEMA = "HHS_PASS_220_I071_SHARED_ROOT_PHASE_GEAR_LOOP_CLOSURE_V1"

HASH72_WIDTH = 72
HASH216_WIDTH = 216
EXPANDED_PER_LANE = 5184
FULL_ATTACHED_COMPONENTS = 3 * EXPANDED_PER_LANE

# Exact repository content identities inherited by this constructor.
# Values are Git blob object ids for the authoritative parent-main files.
SOURCE_BUNDLE = (
    {
        "role": "PRIMARY_HHS_WHITEPAPER",
        "path": "whitepapers/HOLOFRACTAL_HARMONICODE.md",
        "git_blob_sha": "74fd2571d0615f650f2c9b703a58e75dab247861",
    },
    {
        "role": "QUANTUM_GEOMETRIC_SHARED_ROOT_WHITEPAPER",
        "path": (
            "docs/whitepapers/"
            "HARMONICODE_QUANTUM_GEOMETRIC_SHARED_ROOT_CLOSURE_THEOREM.md"
        ),
        "git_blob_sha": "342e36f18e1d3ac6c96c2ef57cb97724e3e19210",
    },
    {
        "role": "LOSSLESS_HYDRATION_WHITEPAPER",
        "path": (
            "docs/whitepapers/"
            "HHS_PASS_220_I065_LOSSLESS_EMERGENT_COMPRESSION_HYDRATION_V1.md"
        ),
        "git_blob_sha": "2479c9ddfa5b0e53598580bbec4d1851cfb8be39",
    },
    {
        "role": "LEAN_I065_HYDRATION_THEOREM",
        "path": "formal/lean/HHS/Pass220/LosslessEmergentCompressionHydration.lean",
        "git_blob_sha": "50236e3fed4ea077cbf6d38656203b6440ee8ba4",
    },
    {
        "role": "WOLFRAM_I065_HYDRATION_FORMALIZATION",
        "path": (
            "formal/wolfram/"
            "pass220_i065_lossless_emergent_compression_hydration_v1.wl"
        ),
        "git_blob_sha": "ddde76bdabfe481303997eb2a6d8d950cc7cd1b2",
    },
    {
        "role": "I039_QUANTUM_GEOMETRIC_RUNTIME",
        "path": "hhs_runtime/hhs_pass220_quantum_geometric_unification_closure_v1.py",
        "git_blob_sha": "01e1c516e15a07541b19122b2da935148c86c7c2",
    },
    {
        "role": "I071_PHASE_GEAR_LOOP_RUNTIME",
        "path": "hhs_runtime/hhs_pass220_i071_shared_root_phase_gear_loop_closure_v1.py",
        "git_blob_sha": "dbeb445b7049d870b9c167ddabcfc109576af2d8",
    },
)

AUTHORITY_BOUNDARY = {
    "candidate_only": True,
    "theory_constructor_is_projection": True,
    "formal_validity_not_empirical_validation": True,
    "expanded_geometry_persisted": False,
    "generator_and_plane_roots_persisted": True,
    "hydrate_on_demand": True,
    "floating_point_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "empirical_claim_authority": False,
    "external_egress_authority": False,
}


class Pass220I072TheoryHydrationError(ValueError):
    """Raised when the theory constructor or its hydration diverges."""


def _reject_float(value: Any, path: str = "root") -> None:
    if isinstance(value, float):
        raise Pass220I072TheoryHydrationError(
            f"floating-point value forbidden at {path}"
        )
    if isinstance(value, Mapping):
        for key, child in value.items():
            _reject_float(child, f"{path}.{key}")
    elif isinstance(value, (tuple, list)):
        for index, child in enumerate(value):
            _reject_float(child, f"{path}[{index}]")


def _canonical_bytes(value: Any) -> bytes:
    _reject_float(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _exact_int(value: Any, name: str, lower: int, upper: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220I072TheoryHydrationError(f"{name} must be an exact integer")
    if not lower <= value <= upper:
        raise Pass220I072TheoryHydrationError(
            f"{name} must satisfy {lower} <= {name} <= {upper}"
        )
    return value


def _hash72_word(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH72_WIDTH:
        raise Pass220I072TheoryHydrationError(
            f"{name} must be a 72-character Hash72 word"
        )
    return value


def _hash216_word(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != HASH216_WIDTH:
        raise Pass220I072TheoryHydrationError(
            f"{name} must be a 216-character Hash216 word"
        )
    return value


def theory_source_bundle() -> dict[str, Any]:
    bundle = {
        "schema": f"{SCHEMA}_SOURCE_BUNDLE_V1",
        "sources": [dict(row) for row in SOURCE_BUNDLE],
        "source_count": len(SOURCE_BUNDLE),
        "roles_unique": (
            len({row["role"] for row in SOURCE_BUNDLE}) == len(SOURCE_BUNDLE)
        ),
        "paths_unique": (
            len({row["path"] for row in SOURCE_BUNDLE}) == len(SOURCE_BUNDLE)
        ),
    }
    bundle["source_bundle_root_sha256"] = _sha256(bundle)
    return bundle


def _formal_proof_identity() -> dict[str, Any]:
    lean = lean_identity_receipt()
    if lean.get("theorem_identity_valid") is not True:
        raise Pass220I072TheoryHydrationError("Lean theorem identity invalid")
    if lean.get("dependency_identity_valid") is not True:
        raise Pass220I072TheoryHydrationError("Lean dependency identity invalid")
    if lean.get("runtime_claims_live_kernel_execution") is not False:
        raise Pass220I072TheoryHydrationError("Lean runtime scope widened")
    if lean.get("hash72_commit_authority") is not False:
        raise Pass220I072TheoryHydrationError("Lean Hash72 authority widened")
    if lean.get("hash216_persistence_authority") is not False:
        raise Pass220I072TheoryHydrationError("Lean Hash216 authority widened")

    return {
        "schema": f"{SCHEMA}_FORMAL_PROOF_IDENTITY_V1",
        "lean_inherited_via": "PASS_220_I061_UNIFIED_SCIENTIFIC_PHYSICS_SYNTHESIS",
        "lean_module": lean["module"],
        "lean_theorem_identity_hash72": _hash72_word(
            lean["theorem_identity_hash72"],
            "lean_theorem_identity_hash72",
        ),
        "lean_dependency_identity_hash72": _hash72_word(
            lean["dependency_identity_hash72"],
            "lean_dependency_identity_hash72",
        ),
        "lean_kernel_validation_scope": lean["kernel_validation_scope"],
        "i065_lean_module": "HHS.Pass220.I065",
        "i072_lean_module": "HHS.Pass220.I072",
        "wolfram_parent": (
            "formal/wolfram/"
            "pass220_i065_lossless_emergent_compression_hydration_v1.wl"
        ),
        "wolfram_parent_exact_checks": 12,
        "wolfram_i072_exact_checks": 42,
        "formal_validity_only": True,
        "empirical_correspondence_claimed": False,
    }


def _shared_root_witness() -> dict[str, Any]:
    witness = quantum_geometric_unification_witness()
    if witness.get("schema") != I039_SCHEMA:
        raise Pass220I072TheoryHydrationError("I039 witness schema mismatch")
    if witness.get("ok") is not True:
        raise Pass220I072TheoryHydrationError("I039 shared-root witness open")
    root = witness.get("shared_state_root_sha256")
    if not isinstance(root, str) or len(root) != 64:
        raise Pass220I072TheoryHydrationError("I039 shared root malformed")
    return {
        "schema": f"{SCHEMA}_SHARED_ROOT_BINDING_V1",
        "i039_witness_receipt_sha256": witness["receipt_sha256"],
        "i039_constructor_receipt_sha256": witness["constructor_receipt_sha256"],
        "shared_state_root_sha256": root,
        "phase_orbit_shared": witness["phase_orbit_shared"],
        "palindromic_return_gate_closed": witness[
            "palindromic_return_gate_closed"
        ],
        "canonical_admission_authority": False,
    }


def _phase_loop_binding(
    *,
    shared_root_sha256: str,
    nucleus_index: int,
    nesting_depth: int,
) -> dict[str, Any]:
    loop = run_phase_gear_loop(
        shared_root_sha256=shared_root_sha256,
        nucleus_index=nucleus_index,
        nesting_depth=nesting_depth,
        halt_on_orbit=True,
        orientation_closed=True,
        constraint_closed=True,
        max_steps=72,
    )
    if loop.get("schema") != I071_SCHEMA:
        raise Pass220I072TheoryHydrationError("I071 loop schema mismatch")
    required = {
        "orbit_period": 72,
        "transport_closed": True,
        "orientation_closed": True,
        "constraint_closed": True,
        "converged": True,
        "geometry_returned": True,
        "lineage_advanced": True,
        "halted": True,
    }
    for key, expected in required.items():
        if loop.get(key) != expected:
            raise Pass220I072TheoryHydrationError(
                f"I071 loop binding diverged at {key}"
            )
    return {
        "schema": f"{SCHEMA}_PHASE_LOOP_BINDING_V1",
        "nucleus_index": nucleus_index,
        "nesting_depth": nesting_depth,
        "shared_root_sha256": shared_root_sha256,
        "phase_loop_receipt_hash72": _hash72_word(
            loop["receipt_hash72"],
            "phase_loop_receipt_hash72",
        ),
        "orbit_period": loop["orbit_period"],
        "phase_lock_period": loop["phase_gear"]["phase_lock_period"],
        "geometry_returned": loop["geometry_returned"],
        "lineage_advanced": loop["lineage_advanced"],
        "converged": loop["converged"],
        "final_lineage_hash216": _hash216_word(
            loop["final_lineage_hash216"],
            "final_lineage_hash216",
        ),
    }


def _plane_roots(hydrated: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    roots = tuple(
        {
            "role": plane["role"],
            "generator_hash72": plane["generator_hash72"],
            "expanded_vertices": plane["expanded_vertices"],
            "expanded_geometry_sha256": plane["expanded_geometry_sha256"],
            "roundtrip_exact": plane["roundtrip_exact"],
        }
        for plane in hydrated["planes"]
    )
    if tuple(item["role"] for item in roots) != (
        "PREVIOUS",
        "CHANGE",
        "RECEIPT",
    ):
        raise Pass220I072TheoryHydrationError("I065 plane order diverged")
    return roots


def build_theory_constructor(
    *,
    nucleus_index: int = 0,
    nesting_depth: int = 0,
) -> dict[str, Any]:
    nucleus = _exact_int(nucleus_index, "nucleus_index", 0, 8)
    depth = _exact_int(nesting_depth, "nesting_depth", 0, 1_000_000)

    source_bundle = theory_source_bundle()
    formal = _formal_proof_identity()
    shared = _shared_root_witness()
    loop = _phase_loop_binding(
        shared_root_sha256=shared["shared_state_root_sha256"],
        nucleus_index=nucleus,
        nesting_depth=depth,
    )
    optimization = lane5_optimization_witness(1)
    if optimization.get("candidate_search_only") is not True:
        raise Pass220I072TheoryHydrationError("I065 candidate-only gate missing")
    if optimization.get(
        "canonical_state_commit_requires_inherited_vm81_path"
    ) is not True:
        raise Pass220I072TheoryHydrationError("I065 VM81 admission gate missing")

    previous_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_PREVIOUS_THEORY_LANE_V1",
            "shared_root_binding": shared,
            "source_bundle_root_sha256": source_bundle[
                "source_bundle_root_sha256"
            ],
        }
    )
    change_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_CHANGE_THEORY_LANE_V1",
            "phase_loop_binding": loop,
            "constructor_rule": (
                "SOURCE+FORMAL+SHARED_ROOT+PHASE_LOOP"
                "->HASH216->I065_ON_DEMAND_HYDRATION"
            ),
        }
    )
    receipt_hash72 = hash72(
        {
            "schema": f"{SCHEMA}_RECEIPT_THEORY_LANE_V1",
            "lean_theorem_identity_hash72": formal[
                "lean_theorem_identity_hash72"
            ],
            "lean_dependency_identity_hash72": formal[
                "lean_dependency_identity_hash72"
            ],
            "wolfram_i072_exact_checks": formal["wolfram_i072_exact_checks"],
            "i065_roundtrip_required": True,
            "authority": AUTHORITY_BOUNDARY,
        }
    )
    theory_hash216 = _hash216_word(
        previous_hash72 + change_hash72 + receipt_hash72,
        "theory_hash216",
    )

    hydrated = hydrate_hash216_geometry(theory_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I072TheoryHydrationError(
            "theory Hash216 hydration did not roundtrip"
        )
    if hydrated.get("full_attached_components") != FULL_ATTACHED_COMPONENTS:
        raise Pass220I072TheoryHydrationError(
            "theory hydration attached-component count drift"
        )

    roots = _plane_roots(hydrated)
    theory_material = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "source_bundle": source_bundle,
        "formal_proof_identity": formal,
        "shared_root_binding": shared,
        "phase_loop_binding": loop,
        "theory_hash216": theory_hash216,
        "plane_roots": roots,
        "lane5_optimization": optimization,
        "storage": {
            "stores_constructor_root": True,
            "stores_theory_hash216": True,
            "stores_generator_and_plane_roots": True,
            "stores_expanded_3x5184_geometry": False,
            "expanded_geometry_reconstructible_on_demand": True,
            "fully_hydrated_attached_components_if_materialized": (
                FULL_ATTACHED_COMPONENTS
            ),
            "generic_unconstrained_payload_compression_claimed": False,
        },
        "authority": dict(AUTHORITY_BOUNDARY),
    }
    theory_material["theory_constructor_root_sha256"] = _sha256(
        theory_material
    )
    theory_material["binding_hash72"] = hash72(
        {
            "schema": SCHEMA,
            "theory_constructor_root_sha256": theory_material[
                "theory_constructor_root_sha256"
            ],
            "theory_hash216": theory_hash216,
            "shared_state_root_sha256": shared["shared_state_root_sha256"],
            "phase_loop_receipt_hash72": loop[
                "phase_loop_receipt_hash72"
            ],
            "plane_roots": roots,
        }
    )
    return theory_material


def hydrate_theory_constructor(
    constructor: Mapping[str, Any],
) -> dict[str, Any]:
    validate_theory_constructor(constructor)
    theory_hash216 = _hash216_word(
        constructor["theory_hash216"],
        "theory_hash216",
    )
    hydrated = hydrate_hash216_geometry(theory_hash216)
    if hydrated.get("roundtrip_exact") is not True:
        raise Pass220I072TheoryHydrationError(
            "on-demand theory hydration failed exact roundtrip"
        )
    return {
        "schema": f"{SCHEMA}_ON_DEMAND_HYDRATION_V1",
        "theory_constructor_root_sha256": constructor[
            "theory_constructor_root_sha256"
        ],
        "theory_hash216": theory_hash216,
        "hash216_positions": hydrated["hash216_positions"],
        "three_dimensional_vertex_count": hydrated[
            "three_dimensional_vertex_count"
        ],
        "components_per_vertex": hydrated["components_per_vertex"],
        "full_attached_components": hydrated["full_attached_components"],
        "vertex72_geometry": hydrated["vertex72_geometry"],
        "planes": hydrated["planes"],
        "roundtrip_exact": hydrated["roundtrip_exact"],
        "canonical_mutation_authority": False,
        "canonical_persistence_authority": False,
    }


def validate_theory_constructor(
    constructor: Mapping[str, Any],
) -> bool:
    if not isinstance(constructor, Mapping):
        raise Pass220I072TheoryHydrationError("constructor must be a mapping")
    if constructor.get("schema") != SCHEMA:
        raise Pass220I072TheoryHydrationError("constructor schema mismatch")

    phase = constructor.get("phase_loop_binding")
    if not isinstance(phase, Mapping):
        raise Pass220I072TheoryHydrationError("phase-loop binding missing")
    nucleus = _exact_int(phase.get("nucleus_index"), "nucleus_index", 0, 8)
    depth = _exact_int(
        phase.get("nesting_depth"),
        "nesting_depth",
        0,
        1_000_000,
    )
    canonical = build_theory_constructor(
        nucleus_index=nucleus,
        nesting_depth=depth,
    )

    for key in (
        "version",
        "profile",
        "source_bundle",
        "formal_proof_identity",
        "shared_root_binding",
        "phase_loop_binding",
        "theory_hash216",
        "plane_roots",
        "lane5_optimization",
        "storage",
        "authority",
        "theory_constructor_root_sha256",
        "binding_hash72",
    ):
        if constructor.get(key) != canonical[key]:
            raise Pass220I072TheoryHydrationError(
                f"theory constructor diverges at {key}"
            )
    return True


def self_test() -> dict[str, Any]:
    constructor = build_theory_constructor(
        nucleus_index=4,
        nesting_depth=3,
    )
    hydrated = hydrate_theory_constructor(constructor)
    checks = {
        "constructor_valid": validate_theory_constructor(constructor),
        "source_bundle_unique": (
            constructor["source_bundle"]["roles_unique"]
            and constructor["source_bundle"]["paths_unique"]
        ),
        "i039_shared_root_bound": (
            len(
                constructor["shared_root_binding"][
                    "shared_state_root_sha256"
                ]
            )
            == 64
        ),
        "lean_theorem_bound": (
            len(
                constructor["formal_proof_identity"][
                    "lean_theorem_identity_hash72"
                ]
            )
            == 72
        ),
        "lean_dependency_bound": (
            len(
                constructor["formal_proof_identity"][
                    "lean_dependency_identity_hash72"
                ]
            )
            == 72
        ),
        "i071_loop_period_72": (
            constructor["phase_loop_binding"]["orbit_period"] == 72
        ),
        "i071_phase_lock_5184": (
            constructor["phase_loop_binding"]["phase_lock_period"] == 5184
        ),
        "geometry_returns_history_advances": (
            constructor["phase_loop_binding"]["geometry_returned"]
            and constructor["phase_loop_binding"]["lineage_advanced"]
        ),
        "hash216_width_216": len(constructor["theory_hash216"]) == 216,
        "three_plane_roots": len(constructor["plane_roots"]) == 3,
        "on_demand_roundtrip_exact": hydrated["roundtrip_exact"] is True,
        "full_attached_15552": (
            hydrated["full_attached_components"]
            == FULL_ATTACHED_COMPONENTS
        ),
        "compact_constructor_omits_expansion": (
            constructor["storage"]["stores_expanded_3x5184_geometry"]
            is False
        ),
        "no_vm81_mutation_authority": (
            AUTHORITY_BOUNDARY["canonical_vm81_mutation_authority"]
            is False
        ),
        "no_hash216_persistence_authority": (
            AUTHORITY_BOUNDARY[
                "canonical_hash216_persistence_authority"
            ]
            is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": [name for name, passed in checks.items() if not passed],
        "checks": checks,
        "theory_constructor_root_sha256": constructor[
            "theory_constructor_root_sha256"
        ],
        "binding_hash72": constructor["binding_hash72"],
        "theory_hash216": constructor["theory_hash216"],
    }


__all__ = [
    "AUTHORITY_BOUNDARY",
    "FULL_ATTACHED_COMPONENTS",
    "Pass220I072TheoryHydrationError",
    "PROFILE",
    "SCHEMA",
    "SOURCE_BUNDLE",
    "build_theory_constructor",
    "hydrate_theory_constructor",
    "self_test",
    "theory_source_bundle",
    "validate_theory_constructor",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))

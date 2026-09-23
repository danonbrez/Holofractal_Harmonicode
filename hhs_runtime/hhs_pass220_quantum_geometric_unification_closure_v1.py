"""Pass 220 I039: quantum-geometric unification closure constructor.

I039 does not introduce a second physics engine.  It binds the already merged
exact quantum, relativistic/cosmological, 24D Lo Shu/q=-1, palindromic IEEE,
and fixed-width BigInt surfaces to one shared state-root witness.

The executable closure is structural:

    quantum exact orbit
    + relativistic exact transfer
    + identical nine-step phase orbit
    + I037 mandatory 24D equation/proof bundle
    + I038 parallel exact numeric/IEEE/BigInt carrier
    + typed Delta-e/Psi/Omega closure
    -> one shared-state projection root

Every projection is read-only.  No canonical VM81/Hash72/Hash216 authority is
created by this constructor.

The root metadata seed 179971.179971 is carried as exact source text/rational,
nearest-even raw IEEE binary64, exact dyadic residue, palindromic reciprocal
state, and 5,184-character BigInt geometry in parallel.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Tuple

from hhs_runtime.hhs_authority_gate_v1 import audit_runtime_authority
from hhs_runtime.hhs_pass220_24d_mandatory_constraint_spacetime_v1 import (
    constructor_bundle_root,
    twentyfour_d_constraint_spacetime_witness,
)
from hhs_runtime.hhs_pass220_cosmological_clock_cadence_v1 import PHASE_ORBIT
from hhs_runtime.hhs_pass220_desi_lane5_parallel_exact_egress_v1 import (
    build_parallel_observation_carrier,
    validate_parallel_observation_carrier,
)
from hhs_runtime.hhs_pass220_exact_friedmann_transfer_v1 import (
    build_exact_trajectory,
    make_transfer_receipt,
    transfer_contract_descriptor,
)
from hhs_runtime.hhs_pass220_background_continuity_v1 import (
    background_contract_descriptor,
)
from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import (
    PHASE_MODULUS,
    firing_order,
    full_orbit_receipt,
    quantum_contract_descriptor,
)

SCHEMA = "HHS_PASS_220_I039_QUANTUM_GEOMETRIC_UNIFICATION_CLOSURE_V1"
VERSION = "1.0.0-checkpoint.39"
PROFILE = "PASS220-I039-QUANTUM-GEOMETRIC-UNIFICATION-CLOSURE-v1"
CONSTRUCTOR_SCHEMA = "HHS_PASS_220_I039_UNIFICATION_CONSTRUCTOR_V1"
WITNESS_SCHEMA = "HHS_PASS_220_I039_UNIFICATION_WITNESS_V1"

ROOT_METADATA_SEED = "179971.179971"
ROOT_METADATA_SOURCE_ID = "HHS_I039_ROOT_METADATA_SEED"
RETURN_GATE_SOURCE = "(A_p/B_q)(B_q/A_p)≡1"
TYPED_CLOSURE_SOURCE = "Delta e=0; Psi=0; Omega=true"

LOCAL_CONSTRAINTS: Tuple[str, ...] = (
    "QUANTUM_AND_RELATIVISTIC_PROJECTIONS_SHARE_ONE_STATE_ROOT",
    "QUANTUM_AND_RELATIVISTIC_PHASE_ORBITS_IDENTICAL",
    "QUANTUM_FULL_ORBIT_IS_EXACT_72_STATE_CYCLOTOMIC_EXECUTION",
    "RELATIVISTIC_TRANSFER_IS_EXACT_SYMBOLIC_RATIONAL_EXECUTION",
    "I037_MANDATORY_24D_EQUATION_PROOF_BUNDLE_PRESERVED",
    "I038_PALINDROMIC_IEEE_BIGINT_PARALLEL_CARRIER_PRESERVED",
    "ROOT_METADATA_SEED_PRESERVED_EXACTLY",
    "IEEE_RESIDUE_RETAINED_EXACTLY",
    "BIGINT_SERIALIZATION_WIDTH_5184",
    "PALINDROMIC_SYMBOL_RETURN_CLOSED",
    "PALINDROMIC_IEEE_RETURN_CLOSED",
    "DELTA_E_ZERO",
    "PSI_ZERO",
    "OMEGA_TRUE",
    "THETA15_TRUE",
    "ALGEBRAIC_CLOSURE_TRUE",
    "NO_HOST_FLOAT_ARITHMETIC",
    "NO_PROBABILITY_SOLVE",
    "NO_LIKELIHOOD_SOLVE",
    "NO_MCMC_SOLVE",
    "NO_COMMUTATIVE_REORDERING_AUTHORIZED",
)


class Pass220I039UnificationError(ValueError):
    pass


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _receipt(payload: Mapping[str, Any]) -> Dict[str, Any]:
    record = dict(payload)
    record["receipt_sha256"] = sha256(
        _stable_json(record).encode("utf-8")
    ).hexdigest()
    return record


def _receipt_matches(record: Mapping[str, Any]) -> bool:
    if "receipt_sha256" not in record:
        return False
    body = dict(record)
    claimed = body.pop("receipt_sha256")
    return claimed == sha256(_stable_json(body).encode("utf-8")).hexdigest()


def _source_sha(*parts: Any) -> str:
    return sha256(
        _stable_json(parts).encode("utf-8")
    ).hexdigest()


def build_root_metadata_parallel_carrier() -> Dict[str, Any]:
    return build_parallel_observation_carrier(
        observable="root_metadata_seed",
        decimal_text=ROOT_METADATA_SEED,
        source_release_id=ROOT_METADATA_SOURCE_ID,
    )


def build_relativistic_phase_orbit_trajectory() -> Dict[str, Any]:
    receipts = tuple(
        make_transfer_receipt(
            transition_index=index,
            lambda_increment=1,
            theta=1,
            background_h2=0,
            source_receipt_sha256=_source_sha(
                "I039_RELATIVISTIC_PHASE_ORBIT",
                index,
                ROOT_METADATA_SEED,
            ),
        )
        for index in range(len(PHASE_ORBIT))
    )
    return build_exact_trajectory(
        receipts,
        tau=1,
        c0=1,
        curvature_sign=0,
    )


def _shared_state_base() -> Dict[str, Any]:
    seed_carrier = build_root_metadata_parallel_carrier()
    seed_validation = validate_parallel_observation_carrier(seed_carrier)
    i037 = twentyfour_d_constraint_spacetime_witness()
    quantum = full_orbit_receipt()
    relativity = build_relativistic_phase_orbit_trajectory()

    if seed_validation.get("ok") is not True:
        raise Pass220I039UnificationError("root metadata carrier did not validate")
    if i037.get("ok") is not True:
        raise Pass220I039UnificationError("I037 24D witness did not validate")
    if quantum.get("status") != "PASS":
        raise Pass220I039UnificationError("quantum full-orbit receipt failed")

    return {
        "root_metadata_seed": ROOT_METADATA_SEED,
        "root_metadata_carrier_receipt_sha256": seed_carrier["receipt_sha256"],
        "i037_mandatory_constructor_bundle_root_sha256": constructor_bundle_root(),
        "i037_witness_receipt_sha256": i037["receipt_sha256"],
        "phase_orbit": tuple(PHASE_ORBIT),
        "phase_modulus": PHASE_MODULUS,
        "vm5184": 5184,
        "quantum_receipt_sha256": quantum["receipt_sha256"],
        "relativistic_trajectory_receipt_sha256": relativity["receipt_sha256"],
    }


def shared_state_root_sha256() -> str:
    return sha256(
        _stable_json(_shared_state_base()).encode("utf-8")
    ).hexdigest()


def build_quantum_projection(shared_root: str) -> Dict[str, Any]:
    quantum = full_orbit_receipt()
    descriptor = quantum_contract_descriptor()
    return _receipt({
        "schema": "HHS_PASS_220_I039_QUANTUM_PROJECTION_V1",
        "shared_state_root_sha256": shared_root,
        "full_orbit_receipt": quantum,
        "contract_descriptor": descriptor,
        "phase_orbit": firing_order(),
        "state_space": descriptor["full_orbit_state_space"],
        "state_count": PHASE_MODULUS,
        "exact_committed_node_gate": quantum["exact_committed_node_gate"],
        "floating_point_authority": False,
        "numerical_eigensolver_authority": False,
        "canonical_admission_authority": False,
    })


def build_relativistic_projection(shared_root: str) -> Dict[str, Any]:
    trajectory = build_relativistic_phase_orbit_trajectory()
    transfer = transfer_contract_descriptor()
    background = background_contract_descriptor()
    return _receipt({
        "schema": "HHS_PASS_220_I039_RELATIVISTIC_PROJECTION_V1",
        "shared_state_root_sha256": shared_root,
        "trajectory": trajectory,
        "transfer_contract_descriptor": transfer,
        "background_contract_descriptor": background,
        "phase_orbit": tuple(trajectory["phase_orbit"]),
        "receipt_count": trajectory["receipt_count"],
        "friedmann_rule": transfer["friedmann_rule"],
        "free_background_function_authority": False,
        "floating_point_authority": False,
        "inverse_hz_state_authority": False,
        "canonical_admission_authority": False,
    })


def typed_closure_witness() -> Dict[str, Any]:
    audit = audit_runtime_authority(
        {
            "entropy_delta": 0,
            "semantic_drift": 0,
        },
        source="pass220_i039_quantum_geometric_unification_closure",
        require_receipt=False,
    )
    packet = audit.to_dict()
    return _receipt({
        "schema": "HHS_PASS_220_I039_TYPED_CLOSURE_V1",
        "source": TYPED_CLOSURE_SOURCE,
        "delta_e": packet["delta_e"],
        "psi": packet["psi"],
        "theta15": packet["theta15"],
        "omega": packet["omega"],
        "algebraic_closure": packet["algebraic_closure"],
        "gate_ok": packet["ok"],
        "reasons": packet["reasons"],
        "receipt_required_for_this_read_only_projection": False,
        "canonical_admission_authority": False,
    })


def build_quantum_geometric_unification_constructor() -> Dict[str, Any]:
    seed_carrier = build_root_metadata_parallel_carrier()
    seed_validation = validate_parallel_observation_carrier(seed_carrier)
    i037 = twentyfour_d_constraint_spacetime_witness()
    shared_root = shared_state_root_sha256()
    quantum_projection = build_quantum_projection(shared_root)
    relativistic_projection = build_relativistic_projection(shared_root)
    closure = typed_closure_witness()

    phase_orbit_shared = (
        tuple(quantum_projection["phase_orbit"])
        == tuple(relativistic_projection["phase_orbit"])
        == tuple(PHASE_ORBIT)
    )
    multirep_validation = seed_carrier["multirepresentational_validation"]

    return _receipt({
        "schema": CONSTRUCTOR_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "constructor_kind": "VALIDATED_OPERATION_CONSTRUCTOR",
        "contains_constraints": True,
        "local_constraints": LOCAL_CONSTRAINTS,
        "constraint_authority": "CONSTRUCTOR_LOCAL_ONLY",
        "canonical_service": False,
        "canonical_constraint_creation_authority": False,
        "canonical_constraint_enforcement_authority": False,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_authority": False,
        "canonical_hash216_authority": False,
        "direct_canonical_persistence_authority": False,
        "root_metadata_seed": ROOT_METADATA_SEED,
        "root_metadata_parallel_carrier": seed_carrier,
        "root_metadata_validation": seed_validation,
        "shared_state_base": _shared_state_base(),
        "shared_state_root_sha256": shared_root,
        "quantum_projection": quantum_projection,
        "relativistic_projection": relativistic_projection,
        "i037_24d_witness": i037,
        "i037_mandatory_constructor_bundle_root_sha256": constructor_bundle_root(),
        "typed_closure": closure,
        "phase_orbit_shared": phase_orbit_shared,
        "phase_orbit": tuple(PHASE_ORBIT),
        "return_gate_source": RETURN_GATE_SOURCE,
        "return_gate_witness": {
            "symbol_reciprocal_roundtrip": multirep_validation[
                "symbol_reciprocal_roundtrip"
            ],
            "ieee_reciprocal_roundtrip": multirep_validation[
                "ieee_reciprocal_roundtrip"
            ],
            "co_resident_views_preserved": multirep_validation[
                "co_resident_views_preserved"
            ],
        },
        "dimension_closure": {
            "24D": 3 * 8,
            "3x24": 3 * 24,
            "72+9": 72 + 9,
            "81x64": 81 * 64,
            "72^2": 72**2,
        },
        "simultaneous_projection_closure": all((
            phase_orbit_shared,
            quantum_projection["full_orbit_receipt"]["status"] == "PASS",
            relativistic_projection["receipt_count"] == 9,
            i037["ok"] is True,
            seed_validation["ok"] is True,
            seed_validation["bigint_5184_characters"] == 5184,
            multirep_validation["symbol_reciprocal_roundtrip"] is True,
            multirep_validation["ieee_reciprocal_roundtrip"] is True,
            closure["delta_e"] == 0,
            closure["psi"] == 0,
            closure["theta15"] is True,
            closure["omega"] is True,
            closure["algebraic_closure"] is True,
            closure["gate_ok"] is True,
        )),
        "host_float_arithmetic_used": False,
        "probability_used_in_equation_solve": False,
        "likelihood_used_in_equation_solve": False,
        "mcmc_used_in_equation_solve": False,
        "commutative_reordering_authorized": False,
        "repository_os_hydration_role": (
            "VALIDATED_PR_CONSTRUCTOR_INPUT_TO_EXISTING_DATA_FLOW_PIPELINE"
        ),
    })


def validate_quantum_geometric_unification_constructor(
    constructor: Mapping[str, Any],
) -> Dict[str, Any]:
    if not isinstance(constructor, Mapping):
        raise Pass220I039UnificationError("constructor must be a mapping")
    if constructor.get("schema") != CONSTRUCTOR_SCHEMA:
        raise Pass220I039UnificationError("constructor schema mismatch")
    if not _receipt_matches(constructor):
        raise Pass220I039UnificationError("constructor receipt mismatch")
    if tuple(constructor.get("local_constraints", ())) != LOCAL_CONSTRAINTS:
        raise Pass220I039UnificationError("local constraint set mismatch")

    if constructor.get("root_metadata_seed") != ROOT_METADATA_SEED:
        raise Pass220I039UnificationError("root metadata seed drift")

    seed = constructor.get("root_metadata_parallel_carrier")
    if not isinstance(seed, Mapping):
        raise Pass220I039UnificationError("root metadata parallel carrier missing")
    seed_validation = validate_parallel_observation_carrier(seed)
    if seed_validation != constructor.get("root_metadata_validation"):
        raise Pass220I039UnificationError("root metadata validation drift")
    if seed_validation["bigint_5184_characters"] != 5184:
        raise Pass220I039UnificationError("5184-character BigInt carrier lost")

    expected_base = _shared_state_base()
    if constructor.get("shared_state_base") != expected_base:
        raise Pass220I039UnificationError("shared state base drift")
    expected_root = sha256(
        _stable_json(expected_base).encode("utf-8")
    ).hexdigest()
    if constructor.get("shared_state_root_sha256") != expected_root:
        raise Pass220I039UnificationError("shared state root mismatch")

    quantum = constructor.get("quantum_projection")
    relativity = constructor.get("relativistic_projection")
    if not isinstance(quantum, Mapping) or not isinstance(relativity, Mapping):
        raise Pass220I039UnificationError("projection surfaces missing")
    if quantum != build_quantum_projection(expected_root):
        raise Pass220I039UnificationError("quantum projection drift")
    if relativity != build_relativistic_projection(expected_root):
        raise Pass220I039UnificationError("relativistic projection drift")
    if quantum["shared_state_root_sha256"] != relativity["shared_state_root_sha256"]:
        raise Pass220I039UnificationError("projection ancestry roots differ")
    if quantum["shared_state_root_sha256"] != expected_root:
        raise Pass220I039UnificationError("projection root is not constructor root")

    if tuple(quantum["phase_orbit"]) != tuple(PHASE_ORBIT):
        raise Pass220I039UnificationError("quantum phase orbit drift")
    if tuple(relativity["phase_orbit"]) != tuple(PHASE_ORBIT):
        raise Pass220I039UnificationError("relativistic phase orbit drift")
    if constructor.get("phase_orbit_shared") is not True:
        raise Pass220I039UnificationError("shared phase-orbit closure failed")
    if constructor.get("phase_orbit") != tuple(PHASE_ORBIT):
        raise Pass220I039UnificationError("top-level phase orbit drift")

    i037 = constructor.get("i037_24d_witness")
    if i037 != twentyfour_d_constraint_spacetime_witness():
        raise Pass220I039UnificationError("I037 24D witness drift")
    if constructor.get(
        "i037_mandatory_constructor_bundle_root_sha256"
    ) != constructor_bundle_root():
        raise Pass220I039UnificationError("I037 mandatory bundle root mismatch")

    closure = constructor.get("typed_closure")
    if closure != typed_closure_witness():
        raise Pass220I039UnificationError("typed closure witness drift")
    if not (
        closure["delta_e"] == 0
        and closure["psi"] == 0
        and closure["theta15"] is True
        and closure["omega"] is True
        and closure["algebraic_closure"] is True
        and closure["gate_ok"] is True
    ):
        raise Pass220I039UnificationError("Delta/Psi/Omega closure failed")

    if constructor.get("return_gate_source") != RETURN_GATE_SOURCE:
        raise Pass220I039UnificationError("return-gate source drift")
    return_gate = constructor.get("return_gate_witness")
    if not isinstance(return_gate, Mapping) or not all(
        return_gate.get(field) is True
        for field in (
            "symbol_reciprocal_roundtrip",
            "ieee_reciprocal_roundtrip",
            "co_resident_views_preserved",
        )
    ):
        raise Pass220I039UnificationError("palindromic return gate failed")

    if constructor.get("dimension_closure") != {
        "24D": 24,
        "3x24": 72,
        "72+9": 81,
        "81x64": 5184,
        "72^2": 5184,
    }:
        raise Pass220I039UnificationError("dimension closure drift")
    if constructor.get("simultaneous_projection_closure") is not True:
        raise Pass220I039UnificationError("simultaneous projection closure failed")

    for field in (
        "host_float_arithmetic_used",
        "probability_used_in_equation_solve",
        "likelihood_used_in_equation_solve",
        "mcmc_used_in_equation_solve",
        "commutative_reordering_authorized",
        "canonical_service",
        "canonical_constraint_creation_authority",
        "canonical_constraint_enforcement_authority",
        "canonical_vm81_mutation_authority",
        "canonical_hash72_authority",
        "canonical_hash216_authority",
        "direct_canonical_persistence_authority",
    ):
        if constructor.get(field) is not False:
            raise Pass220I039UnificationError(f"forbidden escalation/path: {field}")

    return {
        "ok": True,
        "shared_state_root_sha256": expected_root,
        "root_metadata_seed": ROOT_METADATA_SEED,
        "phase_orbit": tuple(PHASE_ORBIT),
        "quantum_state_count": quantum["state_count"],
        "relativistic_receipt_count": relativity["receipt_count"],
        "i037_bundle_root_sha256": constructor_bundle_root(),
        "bigint_5184_characters": seed_validation["bigint_5184_characters"],
        "delta_e": closure["delta_e"],
        "psi": closure["psi"],
        "omega": closure["omega"],
        "simultaneous_projection_closure": True,
    }


def quantum_geometric_unification_witness() -> Dict[str, Any]:
    constructor = build_quantum_geometric_unification_constructor()
    result = validate_quantum_geometric_unification_constructor(constructor)
    return _receipt({
        "schema": WITNESS_SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "ok": result["ok"],
        "result": result,
        "constructor_receipt_sha256": constructor["receipt_sha256"],
        "shared_state_root_sha256": result["shared_state_root_sha256"],
        "phase_orbit_shared": True,
        "palindromic_return_gate_closed": True,
        "typed_closure_source": TYPED_CLOSURE_SOURCE,
        "canonical_admission_authority": False,
    })


def quantum_geometric_unification_self_test() -> Dict[str, Any]:
    return quantum_geometric_unification_witness()

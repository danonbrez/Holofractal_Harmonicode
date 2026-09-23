from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_cosmological_clock_cadence_v1 import PHASE_ORBIT
from hhs_runtime.hhs_pass220_quantum_geometric_unification_closure_v1 import (
    LOCAL_CONSTRAINTS,
    ROOT_METADATA_SEED,
    RETURN_GATE_SOURCE,
    TYPED_CLOSURE_SOURCE,
    Pass220I039UnificationError,
    build_quantum_geometric_unification_constructor,
    build_quantum_projection,
    build_relativistic_phase_orbit_trajectory,
    build_relativistic_projection,
    build_root_metadata_parallel_carrier,
    quantum_geometric_unification_self_test,
    shared_state_root_sha256,
    typed_closure_witness,
    validate_quantum_geometric_unification_constructor,
)
from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import firing_order
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_quantum_and_relativistic_phase_orbit_is_identical():
    expected = (8, 24, 40, 56, 72, 16, 32, 48, 64)
    assert tuple(PHASE_ORBIT) == expected
    assert firing_order() == expected

    trajectory = build_relativistic_phase_orbit_trajectory()
    assert tuple(trajectory["phase_orbit"]) == expected
    assert trajectory["receipt_count"] == 9


def test_root_metadata_seed_runs_parallel_ieee_bigint_and_24d_path():
    carrier = build_root_metadata_parallel_carrier()
    assert ROOT_METADATA_SEED == "179971.179971"
    assert carrier["decimal_source_text"] == ROOT_METADATA_SEED
    assert carrier["source_release_id"] == "HHS_I039_ROOT_METADATA_SEED"
    assert carrier["bigint_5184_characters"] == 5184
    assert carrier["lane5_parallel_execution"] is True
    assert carrier["probability_used_in_equation_solve"] is False
    assert carrier["likelihood_used_in_equation_solve"] is False
    assert carrier["mcmc_used_in_equation_solve"] is False
    assert carrier["host_float_arithmetic_used"] is False

    multirep = carrier["multirepresentational_validation"]
    assert multirep["symbol_reciprocal_roundtrip"] is True
    assert multirep["ieee_reciprocal_roundtrip"] is True
    assert multirep["bigint_5184_roundtrip"] is True
    assert multirep["co_resident_views_preserved"] is True


def test_quantum_and_relativistic_projections_share_exact_same_state_root():
    root = shared_state_root_sha256()
    quantum = build_quantum_projection(root)
    relativity = build_relativistic_projection(root)

    assert len(root) == 64
    assert quantum["shared_state_root_sha256"] == root
    assert relativity["shared_state_root_sha256"] == root
    assert quantum["full_orbit_receipt"]["status"] == "PASS"
    assert quantum["state_space"] == "Q(zeta72)^72"
    assert quantum["state_count"] == 72
    assert relativity["receipt_count"] == 9
    assert tuple(quantum["phase_orbit"]) == tuple(relativity["phase_orbit"])
    assert tuple(quantum["phase_orbit"]) == tuple(PHASE_ORBIT)


def test_relativistic_projection_uses_exact_symbolic_friedmann_path():
    root = shared_state_root_sha256()
    relativity = build_relativistic_projection(root)

    transfer = relativity["transfer_contract_descriptor"]
    background = relativity["background_contract_descriptor"]
    trajectory = relativity["trajectory"]

    assert transfer["friedmann_rule"] == (
        "H_n^2=background_h2_n+(lambda_n/(tau*theta_n))^2"
    )
    assert transfer["floating_point_authority"] is False
    assert transfer["inverse_hz_state_authority"] is False
    assert background["floating_point_authority"] is False
    assert background["free_background_function_authority"] is False
    assert trajectory["floating_point_authority"] is False
    assert trajectory["canonical_admission_authority"] is False
    assert tuple(trajectory["phase_orbit"]) == tuple(PHASE_ORBIT)


def test_typed_delta_psi_omega_closure_is_exact():
    closure = typed_closure_witness()
    assert closure["source"] == TYPED_CLOSURE_SOURCE
    assert closure["delta_e"] == 0
    assert closure["psi"] == 0
    assert closure["theta15"] is True
    assert closure["omega"] is True
    assert closure["algebraic_closure"] is True
    assert closure["gate_ok"] is True
    assert closure["reasons"] == []
    assert closure["receipt_required_for_this_read_only_projection"] is False
    assert closure["canonical_admission_authority"] is False


def test_full_constructor_closes_all_shared_math_and_code_surfaces():
    constructor = build_quantum_geometric_unification_constructor()
    result = validate_quantum_geometric_unification_constructor(constructor)

    assert result["ok"] is True
    assert result["root_metadata_seed"] == ROOT_METADATA_SEED
    assert result["quantum_state_count"] == 72
    assert result["relativistic_receipt_count"] == 9
    assert result["bigint_5184_characters"] == 5184
    assert result["delta_e"] == 0
    assert result["psi"] == 0
    assert result["omega"] is True
    assert result["simultaneous_projection_closure"] is True

    assert constructor["phase_orbit_shared"] is True
    assert constructor["phase_orbit"] == tuple(PHASE_ORBIT)
    assert constructor["return_gate_source"] == RETURN_GATE_SOURCE
    assert constructor["return_gate_witness"] == {
        "symbol_reciprocal_roundtrip": True,
        "ieee_reciprocal_roundtrip": True,
        "co_resident_views_preserved": True,
    }
    assert constructor["dimension_closure"] == {
        "24D": 24,
        "3x24": 72,
        "72+9": 81,
        "81x64": 5184,
        "72^2": 5184,
    }
    assert constructor["simultaneous_projection_closure"] is True


def test_i037_equation_proof_bundle_is_same_root_in_shared_state():
    constructor = build_quantum_geometric_unification_constructor()
    root = constructor["i037_mandatory_constructor_bundle_root_sha256"]
    assert root == constructor["shared_state_base"][
        "i037_mandatory_constructor_bundle_root_sha256"
    ]
    assert root == constructor["root_metadata_parallel_carrier"][
        "i037_mandatory_constructor_bundle_root_sha256"
    ]
    assert constructor["i037_24d_witness"]["ok"] is True
    assert constructor["i037_24d_witness"]["result"][
        "dimensions_per_qutrit_manifold"
    ] == 24
    assert constructor["i037_24d_witness"]["result"][
        "phase_cover_dimensions"
    ] == 72


def test_constructor_retains_all_local_constraints_without_authority_escalation():
    constructor = build_quantum_geometric_unification_constructor()
    assert tuple(constructor["local_constraints"]) == LOCAL_CONSTRAINTS
    assert constructor["contains_constraints"] is True
    assert constructor["constraint_authority"] == "CONSTRUCTOR_LOCAL_ONLY"
    assert constructor["host_float_arithmetic_used"] is False
    assert constructor["probability_used_in_equation_solve"] is False
    assert constructor["likelihood_used_in_equation_solve"] is False
    assert constructor["mcmc_used_in_equation_solve"] is False
    assert constructor["commutative_reordering_authorized"] is False
    assert constructor["canonical_service"] is False
    assert constructor["canonical_constraint_creation_authority"] is False
    assert constructor["canonical_constraint_enforcement_authority"] is False
    assert constructor["canonical_vm81_mutation_authority"] is False
    assert constructor["canonical_hash72_authority"] is False
    assert constructor["canonical_hash216_authority"] is False
    assert constructor["direct_canonical_persistence_authority"] is False


def test_tampering_and_projection_ancestry_split_fail_closed():
    constructor = build_quantum_geometric_unification_constructor()

    tampered = deepcopy(constructor)
    tampered["phase_orbit_shared"] = False
    with pytest.raises(Pass220I039UnificationError, match="receipt mismatch"):
        validate_quantum_geometric_unification_constructor(tampered)

    tampered = deepcopy(constructor)
    tampered["quantum_projection"]["shared_state_root_sha256"] = "0" * 64
    with pytest.raises(Pass220I039UnificationError, match="receipt mismatch"):
        validate_quantum_geometric_unification_constructor(tampered)


def test_self_test_closes():
    result = quantum_geometric_unification_self_test()
    assert result["ok"] is True
    assert result["result"]["quantum_state_count"] == 72
    assert result["result"]["relativistic_receipt_count"] == 9
    assert result["result"]["simultaneous_projection_closure"] is True
    assert result["phase_orbit_shared"] is True
    assert result["palindromic_return_gate_closed"] is True
    assert result["canonical_admission_authority"] is False


def test_service_registry_declares_i039_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.quantum_geometric_unification_closure.self_test" in source
    assert "hhs_pass220_quantum_geometric_unification_closure_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.quantum_geometric_unification_closure.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_quantum_geometric_unification_closure_v1"
        ),
        "function": "quantum_geometric_unification_self_test",
        "service_type": "pass220_validated_operation_constructor",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_I039_QUANTUM_GEOMETRIC_UNIFICATION_CLOSURE_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I039_UNIFICATION_WITNESS_V1",
        ],
        "validators": [
            "validate_quantum_geometric_unification_constructor",
            "quantum_geometric_unification_self_test",
        ],
        "rejection_codes": [
            "REJECT_I039_SHARED_ROOT_SPLIT",
            "REJECT_I039_PHASE_ORBIT_DIVERGENCE",
            "REJECT_I039_QUANTUM_CLOSURE_FAILURE",
            "REJECT_I039_RELATIVISTIC_CLOSURE_FAILURE",
            "REJECT_I039_I037_BUNDLE_DRIFT",
            "REJECT_I039_BIGINT_5184_LOSS",
            "REJECT_I039_PALINDROMIC_RETURN_FAILURE",
            "REJECT_I039_TYPED_CLOSURE_FAILURE",
            "REJECT_I039_FLOAT_OR_PROBABILITY_PATH",
            "REJECT_I039_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_UNIFICATION_CLOSURE_NO_VM81_MUTATION",
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True

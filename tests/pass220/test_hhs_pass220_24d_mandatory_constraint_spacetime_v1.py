from copy import deepcopy
import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_24d_mandatory_constraint_spacetime_v1 import (
    CONSTRUCTOR_SCHEMA,
    DIRECT_EXCHANGE_FRAME,
    DIMENSIONS_PER_QUTRIT_MANIFOLD,
    FLIPPED_EXCHANGE_FRAME,
    MANDATORY_NATIVE_EQUATIONS,
    PHASE8,
    PHASE_COVER_DIMENSIONS,
    TRINARY_LABELS,
    TRINARY_PHASE_TENSOR,
    Pass220I037SpacetimeError,
    build_24d_constraint_spacetime_constructor,
    build_24d_qutrit_manifold,
    constructor_bundle_root,
    epsilon_phase_residue_carrier,
    flip_variable_exchange_frame,
    mandatory_equation_constructors,
    mandatory_proof_lemmas,
    twentyfour_d_constraint_spacetime_self_test,
    validate_24d_constraint_spacetime_constructor,
    variable_exchange_frame,
)
from hhs_runtime.hhs_pass220_multidimensional_constraint_manifold_v1 import (
    VERBATIM_CONSTRAINT_EQUATIONS,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_full_ordered_trinary_phase_tensor_is_preserved_verbatim():
    assert TRINARY_PHASE_TENSOR == (
        ("yx", "y+x", "xy"),
        (
            "yx-wz",
            "x+y-z-w+xy+yx-zw-wz",
            "zw-xy",
        ),
        ("wz", "z+w", "zw"),
    )
    equations = {
        item["equation_id"]: item
        for item in mandatory_equation_constructors()
    }
    assert equations["I037-E001-TRINARY-PHASE-TENSOR"]["source"] == (
        "(-1,0,+1)={yx,y+x,xy},"
        "{yx-wz,(x+y-z-w+xy+yx-zw-wz),zw-xy},"
        "{wz,z+w,zw}"
    )
    assert equations["I037-E001-TRINARY-PHASE-TENSOR"][
        "commutative_reordering_authorized"
    ] is False


def test_mandatory_native_equations_include_full_exchange_and_scale_surfaces():
    sources = {
        equation_id: source
        for equation_id, source, _ in MANDATORY_NATIVE_EQUATIONS
    }
    assert sources["I037-E002-P4-INVARIANT"] == "P⁴=AB=c⁴=(a²+b²)²"
    assert sources["I037-E003-PYTHAGOREAN-INVARIANT"] == "a²+b²=c²"
    assert sources["I037-E004-P8-TRINARY-FRACTAL-SCALE"] == (
        "A²+B²=P⁸={-,0,+}/∆"
    )
    assert sources["I037-E005-VARIABLE-EXCHANGE"] == (
        "(A:B,a:b,p:q,z:w)↔(B:A,b:a,q:p,w:z)"
    )
    assert sources["I037-E006-P2-RELATIONAL-CLOSURE"] == (
        "P²=P+(p+q)=pq=a²+b²+c²"
    )
    assert sources["I037-E007-C2-PHASE-OFFSET-CHAIN"] == (
        "c²=P⁴/(a²+b²)=a²+b²+c²=a²b²c²; c²-t³=a²"
    )


def test_all_equations_and_inherited_i017_surfaces_are_mandatory_constructors():
    equations = mandatory_equation_constructors()
    assert len(equations) == len(MANDATORY_NATIVE_EQUATIONS) + len(
        VERBATIM_CONSTRAINT_EQUATIONS
    )
    assert all(item["mandatory"] is True for item in equations)
    assert all(item["constructor"] is True for item in equations)
    assert all(item["ordered_source_identity_preserved"] is True for item in equations)
    assert all(
        item["commutative_reordering_authorized"] is False
        for item in equations
    )
    inherited = [
        item for item in equations
        if item["equation_id"].startswith("I037-INHERITED-I017-")
    ]
    assert tuple(item["source"] for item in inherited) == VERBATIM_CONSTRAINT_EQUATIONS


def test_all_proof_lemmas_are_mandatory_verified_constructors():
    lemmas = mandatory_proof_lemmas()
    assert len(lemmas) >= 13
    assert all(item["mandatory"] is True for item in lemmas)
    assert all(item["constructor"] is True for item in lemmas)
    assert all(item["verified"] is True for item in lemmas)
    by_id = {item["lemma_id"]: item for item in lemmas}
    assert by_id["I037-L001-24D-FACTOR"]["statement"] == "3*8=24"
    assert by_id["I037-L002-TRINARY-COVER"]["statement"] == "3*24=72"
    assert by_id["I037-L003-QUDIT-CLOSURE"]["statement"] == "72+9=81"
    assert by_id["I037-L004-VM5184-CROSSWALK"]["statement"] == (
        "81*64=72^2=5184"
    )
    assert by_id["I037-L011-GOLAY-CLAIM-BOUNDARY"]["proof_mode"] == (
        "CLAIM_BOUNDARY"
    )


def test_variable_exchange_is_full_and_involutive():
    direct = variable_exchange_frame(flipped=False)
    flipped = flip_variable_exchange_frame(direct)
    assert direct == DIRECT_EXCHANGE_FRAME == {
        "A:B": "A:B",
        "a:b": "a:b",
        "p:q": "p:q",
        "z:w": "z:w",
    }
    assert flipped == FLIPPED_EXCHANGE_FRAME == {
        "A:B": "B:A",
        "a:b": "b:a",
        "p:q": "q:p",
        "z:w": "w:z",
    }
    assert flip_variable_exchange_frame(flipped) == direct

    with pytest.raises(Pass220I037SpacetimeError):
        flip_variable_exchange_frame({"A:B": "A:B"})


@pytest.mark.parametrize("phase", TRINARY_LABELS)
def test_each_qutrit_manifold_is_a_full_24d_information_copy(phase):
    manifold = build_24d_qutrit_manifold(phase)
    assert manifold["trinary_phase"] == phase
    assert manifold["dimensions"] == DIMENSIONS_PER_QUTRIT_MANIFOLD == 24
    assert manifold["factorization"] == "3*8=24"
    assert manifold["carrier_positions"] == tuple(range(24))
    assert len(manifold["carriers"]) == 24
    assert manifold["full_information_copy"] is True
    assert manifold["partial_information_slice"] is False
    assert manifold["epsilon_residue_carriers_present"] is True
    assert manifold["variable_exchange_involution_carried"] is True
    assert manifold["p4_invariant_source"] == "P⁴=AB=c⁴=(a²+b²)²"
    assert manifold["p8_fractal_scale_source"] == "A²+B²=P⁸={-,0,+}/∆"
    assert manifold["phase_specific_scale_source"] == f"A²+B²=P⁸={phase}/∆"

    root = constructor_bundle_root()
    assert manifold["mandatory_constructor_bundle_root_sha256"] == root
    assert all(
        item["mandatory"] is True
        for item in manifold["mandatory_equation_constructors"]
    )
    assert all(
        item["mandatory"] is True
        for item in manifold["mandatory_proof_lemmas"]
    )


def test_three_24d_manifolds_form_72d_redundant_phase_cover():
    manifolds = tuple(build_24d_qutrit_manifold(p) for p in TRINARY_LABELS)
    assert len(manifolds) == 3
    assert sum(m["dimensions"] for m in manifolds) == PHASE_COVER_DIMENSIONS == 72
    roots = {
        m["mandatory_constructor_bundle_root_sha256"]
        for m in manifolds
    }
    assert roots == {constructor_bundle_root()}
    assert all(m["full_information_copy"] for m in manifolds)


def test_epsilon_residue_carrier_retains_expression_phase_and_exchange():
    minus = epsilon_phase_residue_carrier(
        trinary_phase="-",
        lo_shu_axis=1,
        phase_channel="yx",
    )
    zero = epsilon_phase_residue_carrier(
        trinary_phase="0",
        lo_shu_axis=1,
        phase_channel="yx",
    )
    plus = epsilon_phase_residue_carrier(
        trinary_phase="+",
        lo_shu_axis=1,
        phase_channel="yx",
    )

    assert minus["raw_phase_expression"] == "yx-wz"
    assert zero["raw_phase_expression"] == "x+y-z-w+xy+yx-zw-wz"
    assert plus["raw_phase_expression"] == "zw-xy"
    assert minus["trinary_scalar_projection"] == -1
    assert zero["trinary_scalar_projection"] == 0
    assert plus["trinary_scalar_projection"] == 1

    for carrier in (minus, zero, plus):
        assert carrier["direct_exchange_frame"] == DIRECT_EXCHANGE_FRAME
        assert carrier["flipped_exchange_frame"] == FLIPPED_EXCHANGE_FRAME
        assert carrier["normalization_erases_raw_expression"] is False
        assert carrier["normalization_erases_exchange_provenance"] is False
        assert carrier["normalization_erases_phase_identity"] is False
        assert carrier["golay_profile_only"] is True
        assert carrier["golay_codec_authority"] is False
        assert carrier["mandatory_constructor_bundle_root_sha256"] == (
            constructor_bundle_root()
        )


def test_all_72_epsilon_residue_carriers_have_unique_branch_position_identity():
    all_carriers = []
    for phase in TRINARY_LABELS:
        manifold = build_24d_qutrit_manifold(phase)
        all_carriers.extend(manifold["carriers"])
    identities = {
        (
            c["trinary_phase"],
            c["golay24_profile_position"],
            c["ordered_phase_channel"],
            c["lo_shu_axis"],
        )
        for c in all_carriers
    }
    assert len(all_carriers) == 72
    assert len(identities) == 72


def test_golay24_is_a_profile_carrier_not_an_unimplemented_codec_claim():
    manifold = build_24d_qutrit_manifold("-")
    profile = manifold["golay_profile"]
    assert profile["code"] == "EXTENDED_BINARY_GOLAY_24_12_8"
    assert profile["payload_bits"] == 12
    assert profile["codeword_bits"] == 24
    assert profile["distance"] == 8
    assert profile["profile_position_count"] == 24
    assert profile["profile_only"] is True
    assert profile["codec_implemented_by_i037"] is False
    assert profile["decoder_implemented_by_i037"] is False


def test_full_constructor_binds_equations_lemmas_residues_and_nucleus():
    constructor = build_24d_constraint_spacetime_constructor()
    result = validate_24d_constraint_spacetime_constructor(constructor)

    assert result["ok"] is True
    assert result["dimensions_per_qutrit_manifold"] == 24
    assert result["qutrit_manifold_count"] == 3
    assert result["phase_cover_dimensions"] == 72
    assert result["vm81_cells"] == 81
    assert result["vm5184"] == 5184
    assert result["epsilon_residue_carrier_count"] == 72
    assert result["full_copy_redundancy"] is True
    assert result["golay_profile_only"] is True

    assert constructor["dimension_closure"] == {
        "3*8": 24,
        "3*24": 72,
        "72+9": 81,
        "81*64": 5184,
        "72^2": 5184,
        "5184": 5184,
    }
    assert constructor["genesis_projection"] == {
        "a²": 1,
        "b²": 2,
        "c²": 3,
        "c⁴": 9,
        "P⁴": 9,
        "a²+b²=c²": True,
        "P⁴=c⁴=(a²+b²)²": True,
    }
    assert constructor["all_three_qutrit_copies_full_information"] is True
    assert constructor["all_three_qutrit_copies_share_constructor_root"] is True
    assert constructor["all_epsilon_residue_carriers_present"] is True
    assert constructor["commutative_reordering_authorized"] is False


def test_constructor_has_no_canonical_or_golay_codec_authority():
    constructor = build_24d_constraint_spacetime_constructor()
    assert constructor["constraint_authority"] == "CONSTRUCTOR_LOCAL_ONLY"
    assert constructor["canonical_service"] is False
    assert constructor["canonical_constraint_creation_authority"] is False
    assert constructor["canonical_constraint_enforcement_authority"] is False
    assert constructor["canonical_vm81_mutation_authority"] is False
    assert constructor["canonical_hash72_authority"] is False
    assert constructor["canonical_hash216_authority"] is False
    assert constructor["direct_canonical_persistence_authority"] is False
    golay = constructor["golay24_claim_boundary"]
    assert golay["profile_only"] is True
    assert golay["codec_authority"] is False
    assert golay["decoder_authority"] is False
    assert golay["physical_rom_authority"] is False


def test_tampering_and_invalid_carriers_fail_closed():
    constructor = build_24d_constraint_spacetime_constructor()
    tampered = deepcopy(constructor)
    tampered["canonical_service"] = True
    with pytest.raises(Pass220I037SpacetimeError, match="receipt mismatch"):
        validate_24d_constraint_spacetime_constructor(tampered)

    with pytest.raises(Pass220I037SpacetimeError):
        build_24d_qutrit_manifold("x")
    with pytest.raises(Pass220I037SpacetimeError):
        epsilon_phase_residue_carrier(
            trinary_phase="-",
            lo_shu_axis=3,
            phase_channel="x",
        )
    with pytest.raises(Pass220I037SpacetimeError):
        epsilon_phase_residue_carrier(
            trinary_phase="-",
            lo_shu_axis=0,
            phase_channel="xx",
        )


def test_self_test_closes():
    result = twentyfour_d_constraint_spacetime_self_test()
    assert result["ok"] is True
    assert result["result"]["dimensions_per_qutrit_manifold"] == 24
    assert result["result"]["phase_cover_dimensions"] == 72
    assert result["result"]["epsilon_residue_carrier_count"] == 72
    assert result["all_three_full_copies"] is True
    assert result["all_epsilon_residue_carriers_present"] is True
    assert result["golay24_profile_only"] is True


def test_service_registry_declares_i037_constructor():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.24d_mandatory_constraint_spacetime.self_test" in source
    assert "hhs_pass220_24d_mandatory_constraint_spacetime_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.24d_mandatory_constraint_spacetime.self_test",
        "module": (
            "hhs_runtime."
            "hhs_pass220_24d_mandatory_constraint_spacetime_v1"
        ),
        "function": "twentyfour_d_constraint_spacetime_self_test",
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
            "HHS_PASS_220_I037_24D_MANDATORY_CONSTRAINT_SPACETIME_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_I037_24D_SPACETIME_WITNESS_V1",
        ],
        "validators": [
            "validate_24d_constraint_spacetime_constructor",
            "twentyfour_d_constraint_spacetime_self_test",
        ],
        "rejection_codes": [
            "REJECT_I037_MANDATORY_EQUATION_LOSS",
            "REJECT_I037_MANDATORY_LEMMA_LOSS",
            "REJECT_I037_24D_CARRIER_DRIFT",
            "REJECT_I037_TRINARY_COPY_LOSS",
            "REJECT_I037_EPSILON_RESIDUE_LOSS",
            "REJECT_I037_VARIABLE_EXCHANGE_DRIFT",
            "REJECT_I037_GOLAY_AUTHORITY_ESCALATION",
            "REJECT_I037_COMMUTATIVE_REORDER",
            "REJECT_I037_AUTHORITY_ESCALATION",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": (
            "READ_ONLY_24D_CONSTRAINT_SPACETIME_NO_VM81_MUTATION"
        ),
        "persistence_policy": (
            "REPOSITORY_OS_HYDRATION_ONLY_NO_DIRECT_CANONICAL_PERSISTENCE"
        ),
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True

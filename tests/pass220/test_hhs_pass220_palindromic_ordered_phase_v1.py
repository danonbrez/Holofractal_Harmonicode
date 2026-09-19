import inspect

import pytest

from hhs_runtime.hhs_kernel_conformance_registration_interposer_v1 import (
    interpose_service_registration,
)
from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
    CANONICAL_CLASS_REPRESENTATIVES,
    FORWARD_EDGES,
    MIRROR_CLASS_REPRESENTATIVES,
    MIRROR_EDGES,
    PHASE_MATRIX,
    PHASE_PATH,
    X_VECTOR,
    Y_VECTOR,
    Pass220PalindromicPhaseError,
    braid_associative_witness,
    combined_g41_witness,
    combined_lo_shu_phase_tensor,
    combined_reciprocal_transform,
    conventional_commutative_projection_witness,
    dot,
    edge_class,
    lifted_xy_witness,
    mirror4,
    palindromic_ordered_phase_self_test,
    path_edges,
    projected_edge_sequence,
    residual_witness,
    reverse_edge_path,
    rewrite_word,
    rotate180,
)
from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry


def test_x_y_are_exact_orthogonal_equal_norm_4d_mirror_pair():
    assert X_VECTOR == (0, 1, 1, 0)
    assert Y_VECTOR == (0, -1, 1, 0)
    assert dot(X_VECTOR, Y_VECTOR) == 0
    assert dot(X_VECTOR, X_VECTOR) == 2
    assert dot(Y_VECTOR, Y_VECTOR) == 2
    assert mirror4(X_VECTOR) == Y_VECTOR
    assert mirror4(Y_VECTOR) == X_VECTOR


def test_nine_symbol_phase_path_is_exact_palindrome():
    assert PHASE_PATH == tuple(reversed(PHASE_PATH))
    assert PHASE_PATH == ("x", "y", "z", "w", "x", "w", "z", "y", "x")
    assert path_edges(PHASE_PATH) == FORWARD_EDGES + MIRROR_EDGES


def test_phase_matrix_is_centrosymmetric_3x3_projection_of_palindrome():
    assert PHASE_MATRIX == (
        ("x", "y", "z"),
        ("w", "x", "w"),
        ("z", "y", "x"),
    )
    assert rotate180(PHASE_MATRIX) == PHASE_MATRIX


def test_forward_and_mirror_halves_are_exact_endpoint_reversals():
    assert reverse_edge_path(FORWARD_EDGES) == MIRROR_EDGES
    assert FORWARD_EDGES == (
        ("x", "y"),
        ("y", "z"),
        ("z", "w"),
        ("w", "x"),
    )
    assert MIRROR_EDGES == (
        ("x", "w"),
        ("w", "z"),
        ("z", "y"),
        ("y", "x"),
    )


def test_four_user_edge_equalities_define_componentwise_mirror_representatives():
    assert CANONICAL_CLASS_REPRESENTATIVES == ("xy", "yx", "zw", "wz")
    assert MIRROR_CLASS_REPRESENTATIVES == ("xw", "yz", "zy", "wx")
    assert tuple(
        edge_class(symbol)
        for symbol in MIRROR_CLASS_REPRESENTATIVES
    ) == CANONICAL_CLASS_REPRESENTATIVES


def test_forward_and_mirror_paths_preserve_order_before_projection():
    assert tuple(edge_class(edge) for edge in FORWARD_EDGES) == (
        "xy", "yx", "zw", "wz"
    )
    assert tuple(edge_class(edge) for edge in MIRROR_EDGES) == (
        "xy", "wz", "zw", "yx"
    )
    assert tuple(edge_class(edge) for edge in FORWARD_EDGES) != tuple(
        edge_class(edge) for edge in MIRROR_EDGES
    )


def test_q_minus_one_projection_makes_both_mirror_views_identical():
    assert projected_edge_sequence(FORWARD_EDGES) == (1, -1, 1, -1)
    assert projected_edge_sequence(MIRROR_EDGES) == (1, -1, 1, -1)
    assert pytest.approx(
        projected_edge_sequence(FORWARD_EDGES)[0]
        * projected_edge_sequence(FORWARD_EDGES)[1]
        * projected_edge_sequence(FORWARD_EDGES)[2]
        * projected_edge_sequence(FORWARD_EDGES)[3]
    ) == 1


def test_residual_tensor_is_invariant_under_mirror_representatives():
    witness = residual_witness()
    assert witness["R0"] == (("x", "1"), ("y", "1"))
    assert witness["R1"] == (("zw", "xy"), ("wz", "yx"))
    assert witness["R1_mirror"] == (("zy", "xw"), ("wx", "yz"))
    assert witness["R2"] == (("xy", "x"), ("yx", "y"))
    assert witness["R2_mirror"] == (("xw", "x"), ("yz", "y"))
    assert witness["R1_representative_invariant"] is True
    assert witness["R2_representative_invariant"] is True


def test_braid_plus_yx_negative_x_derives_x_squared_equals_xy_without_commuting():
    witness = braid_associative_witness()
    assert witness["braid"] == "xyx=yxy"
    assert witness["ordered_relation"] == "yx=-x"
    assert witness["lhs_associative_reduction"] == "x(yx)=-x^2"
    assert witness["rhs_associative_reduction"] == "(yx)y=-(xy)"
    assert witness["derived_relation"] == "x^2=xy"
    assert witness["edge_extensions"] == ("xw=xy=x^2", "yz=yx=-x")
    assert witness["typed_reciprocal_extension"] == "xy=1/y => x^2=1/y"
    assert witness["commutativity_assumed"] is False


def test_local_ordered_rewrite_reduces_X_and_Y_but_not_lifted_X_equals_YXY():
    witness = lifted_xy_witness()
    assert rewrite_word("xyz") == "yxy"
    assert rewrite_word("wxy") == "wzw"
    assert witness["X_local_normal_form"] == "yxy"
    assert witness["Y_local_normal_form"] == "wzw"
    assert witness["YXY_local_normal_form"] == "wzwyxywzw"
    assert witness["X_equals_YXY_is_explicit_constraint"] is True
    assert witness["X_equals_YXY_derived_from_local_rules_only"] is False


def test_conventional_commutative_scalar_projection_fails_closed():
    witness = conventional_commutative_projection_witness()
    assert witness["candidate_from_first_two_relations"] == {"x": 1, "y": -1}
    assert witness["braid_lhs"] == -1
    assert witness["braid_rhs"] == 1
    assert witness["admitted"] is False
    assert witness["internal_typed_ordered_algebra_falsified"] is False


def test_combined_lo_shu_phase_center_is_fixed_by_joint_involution():
    tensor = combined_lo_shu_phase_tensor()
    assert tensor == (
        ((4, "x"), (9, "y"), (2, "z")),
        ((3, "w"), (5, "x"), (7, "w")),
        ((8, "z"), (1, "y"), (6, "x")),
    )
    assert combined_reciprocal_transform(tensor) == tensor


def test_combined_phase_layer_preserves_all_41_g41_reciprocal_classes():
    witness = combined_g41_witness()
    assert witness["combined_reciprocal_all_81"] is True
    assert witness["combined_fingerprint_class_count"] == 41
    assert witness["center_combined_fixed"] is True


def test_self_test_closes_all_exact_palindromic_phase_checks():
    result = palindromic_ordered_phase_self_test()
    assert result["ok"] is True
    assert "HHS-I014" in result["invariant_ids"]
    assert "HHS-I015" in result["invariant_ids"]
    assert result["canonical_vm81_mutation_authority"] is False
    assert result["canonical_hash72_authority"] is False
    assert result["canonical_hash216_authority"] is False
    witness = result["witness"]
    assert witness["phase_path_palindrome"] is True
    assert witness["projected_views_equal"] is True
    assert witness["combined_g41"]["combined_fingerprint_class_count"] == 41


def test_service_registry_declares_i015_palindromic_surface_and_kernel_derives_it():
    source = inspect.getsource(make_default_service_registry)
    assert "pass220.palindromic_ordered_phase.self_test" in source
    assert "hhs_pass220_palindromic_ordered_phase_v1" in source

    decision = interpose_service_registration({
        "name": "pass220.palindromic_ordered_phase.self_test",
        "module": "hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1",
        "function": "palindromic_ordered_phase_self_test",
        "service_type": "pass220_exact_ordered_phase_projection",
        "invariant_ids": [
            "HHS-I008",
            "HHS-I010",
            "HHS-I011",
            "HHS-I012",
            "HHS-I014",
            "HHS-I015",
        ],
        "contract_schemas": [
            "HHS_PASS_220_PALINDROMIC_ORDERED_PHASE_V1",
        ],
        "witness_schemas": [
            "HHS_PASS_220_PALINDROMIC_PHASE_CLOSURE_WITNESS_V1",
        ],
        "validators": [
            "validate_palindromic_ordered_phase",
            "palindromic_ordered_phase_self_test",
        ],
        "rejection_codes": [
            "REJECT_PALINDROMIC_PHASE_MIRROR_MISMATCH",
            "REJECT_ORDERED_EDGE_CLASS_COLLAPSE",
            "REJECT_UNDERIVED_RUNTIME_SURFACE",
        ],
        "mutation_policy": "READ_ONLY_ORDERED_PHASE_PROOF_NO_VM81_MUTATION",
        "persistence_policy": "NO_CANONICAL_PERSISTENCE",
    })
    assert decision["ok"] is True
    assert decision["decision"]["derivation_complete"] is True
    assert "HHS-I015" in decision["declaration"]["invariant_ids"]


def test_invalid_inputs_fail_closed():
    with pytest.raises(Pass220PalindromicPhaseError):
        dot((1, 2), (1,))
    with pytest.raises(Pass220PalindromicPhaseError):
        mirror4((1, 2, 3))
    with pytest.raises(Pass220PalindromicPhaseError):
        edge_class("xz")
    with pytest.raises(Pass220PalindromicPhaseError):
        rewrite_word("xyq")
    with pytest.raises(Pass220PalindromicPhaseError):
        combined_reciprocal_transform((((1, "x"),),))

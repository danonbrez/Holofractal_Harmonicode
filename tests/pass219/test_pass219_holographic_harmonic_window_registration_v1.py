from hhs_runtime.hhs_pass219_execution_composer_registration_v1 import (
    pass219_execution_registration_manifest,
    pass219_execution_surface_declaration,
)
from hhs_runtime.hhs_pass219_holographic_harmonic_window_registration_v1 import (
    BRANCH_SYMBOL,
    INVARIANT_SYMBOL,
    MANDATORY_HOLOGRAPHIC_WINDOW_GUARD,
    SCHEMA,
    VALIDATE_SYMBOL,
    pass219_holographic_harmonic_window_manifest,
    pass219_holographic_harmonic_window_surface_declaration,
)
from hhs_runtime.hhs_pass219_mandatory_data_ml_registration_v1 import (
    pass219_mandatory_data_ml_manifest,
    pass219_mandatory_data_ml_surface_declaration,
)


def test_holographic_window_manifest_is_exact_and_bounded() -> None:
    manifest = pass219_holographic_harmonic_window_manifest()
    assert manifest["contract_schema"] == SCHEMA
    assert manifest["mandatory_guard"] == MANDATORY_HOLOGRAPHIC_WINDOW_GUARD
    assert manifest["algebra"]["closed_ratio"] == {"numerator": 25, "denominator": 3}
    assert manifest["algebra"]["closed_residue_reference"] == {
        "t^3-t": 1,
        "m^2-m": 1,
    }
    recursive = manifest["recursive_window"]
    assert recursive["law"] == "W_k=W_0*(3/25)^k"
    assert recursive["maximum_current_depth"] == 9
    assert recursive["direct_layer_addressed"] is True
    assert recursive["recursion_stack_required"] is False
    assert recursive["pointer_tree_traversal_required"] is False
    assert recursive["one_layer_fixed_width_work"] is True
    assert recursive["whole_path_depth_bounded"] is True
    assert recursive["unbounded_depth_constant_time_claim"] is False
    assert manifest["branch"]["floating_point_authority"] is False
    assert manifest["authority"]["canonical_mutation"] is False


def test_holographic_window_guard_declares_exact_symbols() -> None:
    declaration = pass219_holographic_harmonic_window_surface_declaration()
    assert declaration["symbol"] == BRANCH_SYMBOL
    assert INVARIANT_SYMBOL in declaration["validators"]
    assert VALIDATE_SYMBOL in declaration["validators"]
    assert BRANCH_SYMBOL in declaration["validators"]
    assert declaration["mutation_policy"] == "NO_EXTERNAL_STATE_MUTATION"
    assert declaration["persistence_policy"] == "NO_PERSISTENCE_MUTATION"


def test_mandatory_data_ml_requires_holographic_window() -> None:
    declaration = pass219_mandatory_data_ml_surface_declaration()
    manifest = pass219_mandatory_data_ml_manifest()
    assert MANDATORY_HOLOGRAPHIC_WINDOW_GUARD in declaration["guards"]
    assert SCHEMA in declaration["contract_schemas"]
    assert INVARIANT_SYMBOL in declaration["validators"]
    assert VALIDATE_SYMBOL in declaration["validators"]
    assert BRANCH_SYMBOL in declaration["validators"]
    assert (
        manifest["mandatory_holographic_window_guard"]
        == MANDATORY_HOLOGRAPHIC_WINDOW_GUARD
    )
    assert manifest["mandatory_holographic_window_schema"] == SCHEMA
    assert manifest["holographic_window"]["maximum_current_depth"] == 9
    assert (
        manifest["holographic_window"]["unbounded_depth_constant_time_claim"]
        is False
    )


def test_execution_composer_requires_holographic_window() -> None:
    declaration = pass219_execution_surface_declaration()
    manifest = pass219_execution_registration_manifest()
    assert MANDATORY_HOLOGRAPHIC_WINDOW_GUARD in declaration["guards"]
    assert SCHEMA in declaration["contract_schemas"]
    assert INVARIANT_SYMBOL in declaration["validators"]
    assert VALIDATE_SYMBOL in declaration["validators"]
    assert BRANCH_SYMBOL in declaration["validators"]
    assert (
        manifest["mandatory_holographic_window_guard"]
        == MANDATORY_HOLOGRAPHIC_WINDOW_GUARD
    )
    assert manifest["mandatory_holographic_window_schema"] == SCHEMA
    assert manifest["holographic_window_direct_layer_addressed"] is True
    assert manifest["holographic_window_maximum_current_depth"] == 9
    assert manifest["holographic_window_unbounded_depth_constant_time_claim"] is False

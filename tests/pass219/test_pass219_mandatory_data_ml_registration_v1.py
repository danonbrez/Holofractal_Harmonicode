from __future__ import annotations

from pathlib import Path

from hhs_runtime.hhs_pass219_cross_modal_reversible_state_registration_v1 import (
    MANDATORY_GUARD as CROSS_MODAL_MANIFOLD_GUARD,
    SCHEMA as CROSS_MODAL_MANIFOLD_SCHEMA,
    STATE_VALIDATE_SYMBOL as CROSS_MODAL_STATE_VALIDATE_SYMBOL,
    WORK_PLAN_SYMBOL as CROSS_MODAL_WORK_PLAN_SYMBOL,
)
from hhs_runtime.hhs_pass219_raw5184_octonion_audio_hydration_registration_v1 import (
    BIT_EXPORT_SYMBOL as AUDIO5184_BIT_EXPORT_SYMBOL,
    BIT_IMPORT_SYMBOL as AUDIO5184_BIT_IMPORT_SYMBOL,
    FRAME_TO_PCM_SYMBOL as AUDIO5184_FRAME_TO_PCM_SYMBOL,
    HYDRATE_SYMBOL as AUDIO5184_HYDRATE_SYMBOL,
    MANDATORY_GUARD as AUDIO5184_GUARD,
    PCM_TO_FRAME_SYMBOL as AUDIO5184_PCM_TO_FRAME_SYMBOL,
    PIPELINE_SYMBOL as AUDIO5184_PIPELINE_SYMBOL,
    SCHEMA as AUDIO5184_SCHEMA,
    VALIDATE_SYMBOL as AUDIO5184_VALIDATE_SYMBOL,
)
from hhs_runtime.hhs_pass219_execution_composer_registration_v1 import (
    pass219_execution_registration_manifest,
    pass219_execution_surface_declaration,
)
from hhs_runtime.hhs_pass219_global_latency_policy_registration_v1 import (
    CLASSIFY_SYMBOL as LATENCY_CLASSIFY_SYMBOL,
    MANDATORY_LATENCY_GUARD,
    POLICY_VALIDATE_SYMBOL as LATENCY_POLICY_VALIDATE_SYMBOL,
    SCHEMA as LATENCY_POLICY_SCHEMA,
    SELECT_SYMBOL as LATENCY_SELECT_SYMBOL,
    WINDOW_SYMBOL as LATENCY_WINDOW_SYMBOL,
)
from hhs_runtime.hhs_pass219_mandatory_data_ml_registration_v1 import (
    GENESIS_SYMBOL,
    GENESIS_VALIDATE_SYMBOL,
    MANDATORY_GUARD,
    PLAN_SYMBOL,
    SCHEMA,
    STAGE_ORDER,
    VERIFY_SYMBOL,
    WORK_CLASSES,
    pass219_mandatory_data_ml_manifest,
    pass219_mandatory_data_ml_surface_declaration,
)


def test_mandatory_manifest_covers_all_declared_data_ml_classes() -> None:
    manifest = pass219_mandatory_data_ml_manifest()
    assert manifest["contract_schema"] == SCHEMA
    assert manifest["mandatory_guard"] == MANDATORY_GUARD
    assert manifest["mandatory_for_all_pass219_data_processing"] is True
    assert manifest["mandatory_for_all_pass219_machine_learning"] is True
    assert tuple(manifest["work_classes"]) == WORK_CLASSES
    assert tuple(manifest["stage_order"]) == STAGE_ORDER
    assert manifest["genesis"]["cells"] == 81
    assert manifest["genesis"]["addresses"] == 5184
    assert manifest["genesis"]["trit_rule"] == "(sudoku_symbol mod 3) - 1"
    assert manifest["genesis"]["zero_sum_units"] == [
        "rows",
        "columns",
        "blocks",
        "diagonals",
    ]
    assert manifest["fallbacks"]["missing_exact_phase_selector"] == "DENSE_COMPLETE_PATH"
    assert manifest["fallbacks"]["incomplete_dirty_witness"] == "FULL_DERIVED_PROJECTION_PATH"
    assert manifest["canonical_authority"]["pass207"] is False
    assert manifest["canonical_authority"]["pass208"] is False
    assert manifest["canonical_authority"]["singleton_vm81"] == "INHERITED_C_ONLY"
    assert manifest["mandatory_latency_guard"] == MANDATORY_LATENCY_GUARD
    assert manifest["mandatory_latency_schema"] == LATENCY_POLICY_SCHEMA
    assert manifest["mandatory_cross_modal_manifold_guard"] == CROSS_MODAL_MANIFOLD_GUARD
    assert manifest["mandatory_cross_modal_manifold_schema"] == CROSS_MODAL_MANIFOLD_SCHEMA
    assert manifest["mandatory_audio5184_guard"] == AUDIO5184_GUARD
    assert manifest["mandatory_audio5184_schema"] == AUDIO5184_SCHEMA
    assert manifest["latency_policy"]["quantum_ms"] == {"numerator": 25, "denominator": 3}
    assert manifest["latency_policy"]["tiers_fps"] == [120, 60, 30]
    assert manifest["latency_policy"]["timing_is_noncanonical"] is True
    assert manifest["latency_policy"]["unmet_budget_preserves_complete_correct_route"] is True
    assert manifest["floating_point_authority"] is False


def test_mandatory_guard_surface_exposes_exact_abi() -> None:
    declaration = pass219_mandatory_data_ml_surface_declaration()
    assert declaration["symbol"] == PLAN_SYMBOL
    assert declaration["declared_operations"] == [PLAN_SYMBOL, VERIFY_SYMBOL]
    assert SCHEMA in declaration["contract_schemas"]
    assert GENESIS_SYMBOL in declaration["validators"]
    assert GENESIS_VALIDATE_SYMBOL in declaration["validators"]
    assert PLAN_SYMBOL in declaration["validators"]
    assert VERIFY_SYMBOL in declaration["validators"]
    assert LATENCY_POLICY_SCHEMA in declaration["contract_schemas"]
    assert MANDATORY_LATENCY_GUARD in declaration["guards"]
    assert AUDIO5184_GUARD in declaration["guards"]
    assert CROSS_MODAL_MANIFOLD_GUARD in declaration["guards"]
    assert CROSS_MODAL_MANIFOLD_SCHEMA in declaration["contract_schemas"]
    assert CROSS_MODAL_STATE_VALIDATE_SYMBOL in declaration["validators"]
    assert CROSS_MODAL_WORK_PLAN_SYMBOL in declaration["validators"]
    assert AUDIO5184_GUARD in declaration["guards"]
    assert AUDIO5184_SCHEMA in declaration["contract_schemas"]
    assert AUDIO5184_BIT_IMPORT_SYMBOL in declaration["validators"]
    assert AUDIO5184_BIT_EXPORT_SYMBOL in declaration["validators"]
    assert AUDIO5184_FRAME_TO_PCM_SYMBOL in declaration["validators"]
    assert AUDIO5184_PCM_TO_FRAME_SYMBOL in declaration["validators"]
    assert AUDIO5184_HYDRATE_SYMBOL in declaration["validators"]
    assert AUDIO5184_VALIDATE_SYMBOL in declaration["validators"]
    assert AUDIO5184_PIPELINE_SYMBOL in declaration["validators"]
    assert LATENCY_POLICY_VALIDATE_SYMBOL in declaration["validators"]
    assert LATENCY_CLASSIFY_SYMBOL in declaration["validators"]
    assert LATENCY_WINDOW_SYMBOL in declaration["validators"]
    assert LATENCY_SELECT_SYMBOL in declaration["validators"]
    assert "REJECT_PASS219_DATA_ML_WITHOUT_GLOBAL_LATENCY_POLICY" in declaration["rejection_codes"]
    assert "REJECT_PASS219_DATA_ML_WITHOUT_CROSS_MODAL_MANIFOLD_PROOF" in declaration["rejection_codes"]
    assert "REJECT_PASS219_SERIALIZATION_WITHOUT_RAW5184_PCM64_HYDRATION" in declaration["rejection_codes"]
    assert declaration["mutation_policy"] == "INHERITED_SINGLETON_VM81_ONLY"
    assert declaration["persistence_policy"] == "INHERITED_HASH72_HASH216_PATHS_ONLY"


def test_pass219_execution_composer_requires_mandatory_guard() -> None:
    declaration = pass219_execution_surface_declaration()
    manifest = pass219_execution_registration_manifest()
    assert MANDATORY_GUARD in declaration["guards"]
    assert SCHEMA in declaration["contract_schemas"]
    assert GENESIS_SYMBOL in declaration["validators"]
    assert GENESIS_VALIDATE_SYMBOL in declaration["validators"]
    assert PLAN_SYMBOL in declaration["validators"]
    assert VERIFY_SYMBOL in declaration["validators"]
    assert LATENCY_POLICY_SCHEMA in declaration["contract_schemas"]
    assert MANDATORY_LATENCY_GUARD in declaration["guards"]
    assert LATENCY_POLICY_VALIDATE_SYMBOL in declaration["validators"]
    assert LATENCY_CLASSIFY_SYMBOL in declaration["validators"]
    assert LATENCY_WINDOW_SYMBOL in declaration["validators"]
    assert LATENCY_SELECT_SYMBOL in declaration["validators"]
    assert manifest["mandatory_data_ml_guard"] == MANDATORY_GUARD
    assert manifest["mandatory_data_ml_schema"] == SCHEMA
    assert manifest["mandatory_genesis_scaling_applies_before_route_selection"] is True
    assert manifest["mandatory_latency_guard"] == MANDATORY_LATENCY_GUARD
    assert manifest["mandatory_latency_schema"] == LATENCY_POLICY_SCHEMA
    assert manifest["mandatory_cross_modal_manifold_guard"] == CROSS_MODAL_MANIFOLD_GUARD
    assert manifest["mandatory_cross_modal_manifold_schema"] == CROSS_MODAL_MANIFOLD_SCHEMA
    assert manifest["mandatory_audio5184_guard"] == AUDIO5184_GUARD
    assert manifest["mandatory_audio5184_schema"] == AUDIO5184_SCHEMA
    assert manifest["latency_route_selection_requires_exact_semantic_equality"] is True
    assert manifest["latency_budget_unmet_preserves_correct_route"] is True
    assert manifest["latency_timing_is_noncanonical"] is True
    assert manifest["genesis_replay_default"] is False
    assert manifest["genesis_data_plane_normalization_default"] is True


def test_no_registered_pass219_data_ml_executor_bypasses_mandatory_guard() -> None:
    root = Path(__file__).resolve().parents[2]
    registration_files = sorted(
        (root / "hhs_runtime").glob("hhs_pass219_*registration*.py")
    )
    assert registration_files

    data_ml_executor_count = 0
    for path in registration_files:
        text = path.read_text(encoding="utf-8")
        is_executor = '"surface_type": "EXECUTOR"' in text
        is_explicit_data_ml = (
            "mandatory_for_all_pass219_data_processing" in text
            or "mandatory_for_all_pass219_machine_learning" in text
        )
        if is_executor:
            data_ml_executor_count += 1
            assert "MANDATORY_GUARD" in text, path
            assert "PASS219_MANDATORY_SUDOKU_GENESIS_SCALING_DATA_ML" in text, path
        if is_explicit_data_ml:
            assert "MANDATORY_GUARD" in text, path

    assert data_ml_executor_count >= 1

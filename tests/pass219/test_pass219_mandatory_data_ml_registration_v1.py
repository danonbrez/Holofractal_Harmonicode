from __future__ import annotations

from pathlib import Path

from hhs_runtime.hhs_pass219_execution_composer_registration_v1 import (
    pass219_execution_registration_manifest,
    pass219_execution_surface_declaration,
)
from hhs_runtime.hhs_pass219_compression_debt_closure_registration_v1 import (
    BOUNDARY_SYMBOL as DEBT_BOUNDARY_SYMBOL,
    MANDATORY_COMPRESSION_DEBT_GUARD,
    POLICY_VALIDATE_SYMBOL as DEBT_POLICY_VALIDATE_SYMBOL,
    SCHEMA as COMPRESSION_DEBT_SCHEMA,
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
    assert manifest["mandatory_compression_debt_guard"] == MANDATORY_COMPRESSION_DEBT_GUARD
    assert manifest["mandatory_compression_debt_schema"] == COMPRESSION_DEBT_SCHEMA
    assert manifest["compression_debt_policy"]["conserved_quantity"] == "COMPRESSION_DEBT"
    assert manifest["compression_debt_policy"]["elapsed_time_is_debt"] is False
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
    assert COMPRESSION_DEBT_SCHEMA in declaration["contract_schemas"]
    assert MANDATORY_COMPRESSION_DEBT_GUARD in declaration["guards"]
    assert DEBT_POLICY_VALIDATE_SYMBOL in declaration["validators"]
    assert DEBT_BOUNDARY_SYMBOL in declaration["validators"]
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
    assert MANDATORY_COMPRESSION_DEBT_GUARD in declaration["guards"]
    assert COMPRESSION_DEBT_SCHEMA in declaration["contract_schemas"]
    assert DEBT_POLICY_VALIDATE_SYMBOL in declaration["validators"]
    assert DEBT_BOUNDARY_SYMBOL in declaration["validators"]
    assert manifest["mandatory_data_ml_guard"] == MANDATORY_GUARD
    assert manifest["mandatory_data_ml_schema"] == SCHEMA
    assert manifest["mandatory_genesis_scaling_applies_before_route_selection"] is True
    assert manifest["mandatory_compression_debt_guard"] == MANDATORY_COMPRESSION_DEBT_GUARD
    assert manifest["mandatory_compression_debt_schema"] == COMPRESSION_DEBT_SCHEMA
    assert manifest["compression_debt_conserved_quantity"] == "COMPRESSION_DEBT"
    assert manifest["compression_debt_elapsed_time_is_debt"] is False
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
            assert "MANDATORY_COMPRESSION_DEBT_GUARD" in text, path
        if is_explicit_data_ml:
            assert "MANDATORY_GUARD" in text, path

    assert data_ml_executor_count >= 1

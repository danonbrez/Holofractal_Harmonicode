from __future__ import annotations

from hhs_runtime.hhs_pass219_compression_debt_closure_registration_v1 import (
    MANDATORY_COMPRESSION_DEBT_GUARD,
    SCHEMA as COMPRESSION_DEBT_SCHEMA,
    SCHEDULE_SYMBOL as DEBT_SCHEDULE_SYMBOL,
)
from hhs_runtime.hhs_pass219_execution_composer_registration_v1 import (
    pass219_execution_registration_manifest,
    pass219_execution_surface_declaration,
)
from hhs_runtime.hhs_pass219_global_latency_policy_registration_v1 import (
    CLASSIFY_SYMBOL,
    MANDATORY_LATENCY_GUARD,
    POLICY_VALIDATE_SYMBOL,
    SCHEMA,
    SELECT_SYMBOL,
    WINDOW_SYMBOL,
    pass219_global_latency_manifest,
    pass219_global_latency_surface_declaration,
)
from hhs_runtime.hhs_pass219_mandatory_data_ml_registration_v1 import (
    WORK_CLASSES,
    pass219_mandatory_data_ml_manifest,
    pass219_mandatory_data_ml_surface_declaration,
)


def test_global_latency_manifest_is_exact_noncanonical_policy() -> None:
    manifest = pass219_global_latency_manifest()
    assert manifest["contract_schema"] == SCHEMA
    assert manifest["mandatory_guard"] == MANDATORY_LATENCY_GUARD
    assert manifest["mandatory_for_compatible_latency_sensitive_pass219_surfaces"] is True
    assert manifest["exact_latency_quantum_ms"] == {"numerator": 25, "denominator": 3}
    assert manifest["tiers"] == [
        {"tier": 1, "fps": 120, "multiplier": 1},
        {"tier": 2, "fps": 60, "multiplier": 2},
        {"tier": 3, "fps": 30, "multiplier": 4},
    ]
    assert manifest["window_policy"] == {
        "mean_max_tier": 1,
        "p95_max_tier": 2,
        "max_max_tier": 3,
    }
    assert manifest["route_policy"]["exact_semantic_equality_required"] is True
    assert manifest["route_policy"]["unmet_budget_preserves_correct_route"] is True
    assert manifest["route_policy"]["timing_can_change_semantic_identity"] is False
    assert manifest["timing_is_noncanonical"] is True
    assert manifest["performance_guarantee"] is False
    assert manifest["canonical_authority"]["latency_policy"] is False
    assert manifest["canonical_authority"]["singleton_vm81"] == "INHERITED_C_ONLY"
    assert manifest["compression_debt_coupling"]["mandatory_guard"] == MANDATORY_COMPRESSION_DEBT_GUARD
    assert manifest["compression_debt_coupling"]["schema"] == COMPRESSION_DEBT_SCHEMA
    assert manifest["compression_debt_coupling"]["elapsed_time_is_debt"] is False
    assert manifest["compression_debt_coupling"]["physical_time_monotonic"] is True


def test_latency_guard_exposes_exact_abi_surface() -> None:
    declaration = pass219_global_latency_surface_declaration()
    assert declaration["symbol"] == SELECT_SYMBOL
    assert SCHEMA in declaration["contract_schemas"]
    for symbol in (
        POLICY_VALIDATE_SYMBOL,
        CLASSIFY_SYMBOL,
        WINDOW_SYMBOL,
        SELECT_SYMBOL,
        DEBT_SCHEDULE_SYMBOL,
    ):
        assert symbol in declaration["validators"]
    assert COMPRESSION_DEBT_SCHEMA in declaration["contract_schemas"]
    assert MANDATORY_COMPRESSION_DEBT_GUARD in declaration["guards"]
    assert declaration["mutation_policy"] == "INHERITED_SINGLETON_VM81_ONLY"
    assert declaration["persistence_policy"] == "INHERITED_HASH72_HASH216_PATHS_ONLY"


def test_mandatory_data_ml_guard_inherits_global_latency_policy() -> None:
    declaration = pass219_mandatory_data_ml_surface_declaration()
    manifest = pass219_mandatory_data_ml_manifest()
    assert len(WORK_CLASSES) == 12
    assert MANDATORY_LATENCY_GUARD in declaration["guards"]
    assert SCHEMA in declaration["contract_schemas"]
    assert POLICY_VALIDATE_SYMBOL in declaration["validators"]
    assert CLASSIFY_SYMBOL in declaration["validators"]
    assert WINDOW_SYMBOL in declaration["validators"]
    assert SELECT_SYMBOL in declaration["validators"]
    assert manifest["mandatory_latency_guard"] == MANDATORY_LATENCY_GUARD
    assert manifest["mandatory_latency_schema"] == SCHEMA
    assert manifest["latency_policy"]["tiers_fps"] == [120, 60, 30]
    assert manifest["latency_policy"]["timing_is_noncanonical"] is True
    assert manifest["latency_policy"]["unmet_budget_preserves_complete_correct_route"] is True


def test_pass219_execution_composer_inherits_global_latency_policy() -> None:
    declaration = pass219_execution_surface_declaration()
    manifest = pass219_execution_registration_manifest()
    assert MANDATORY_LATENCY_GUARD in declaration["guards"]
    assert SCHEMA in declaration["contract_schemas"]
    assert POLICY_VALIDATE_SYMBOL in declaration["validators"]
    assert SELECT_SYMBOL in declaration["validators"]
    assert "PASS219_GLOBAL_LATENCY_POLICY_25_OVER_3" in manifest["default_preconditions"]
    assert manifest["mandatory_latency_guard"] == MANDATORY_LATENCY_GUARD
    assert manifest["mandatory_latency_schema"] == SCHEMA
    assert manifest["latency_route_selection_requires_exact_semantic_equality"] is True
    assert manifest["latency_budget_unmet_preserves_correct_route"] is True
    assert manifest["latency_timing_is_noncanonical"] is True

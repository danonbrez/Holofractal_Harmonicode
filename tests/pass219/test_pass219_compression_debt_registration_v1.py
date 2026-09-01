from __future__ import annotations

from hhs_runtime.hhs_pass219_compression_debt_closure_registration_v1 import (
    BOUNDARY_SYMBOL,
    GLOBAL_CLOSE_SYMBOL,
    LAYER_CLOSE_SYMBOL,
    MANDATORY_COMPRESSION_DEBT_GUARD,
    POLICY_VALIDATE_SYMBOL,
    SCHEMA,
    SCHEDULE_SYMBOL,
    TRANSFER_BOUND_SYMBOL,
    pass219_compression_debt_manifest,
    pass219_compression_debt_surface_declaration,
)
from hhs_runtime.hhs_pass219_mandatory_data_ml_registration_v1 import (
    pass219_mandatory_data_ml_manifest,
    pass219_mandatory_data_ml_surface_declaration,
)


def test_compression_debt_manifest_freezes_native_boundary() -> None:
    manifest = pass219_compression_debt_manifest()
    assert manifest["contract_schema"] == SCHEMA
    assert manifest["mandatory_guard"] == MANDATORY_COMPRESSION_DEBT_GUARD
    assert manifest["conserved_quantity"] == "COMPRESSION_DEBT"
    assert manifest["elapsed_time_is_conserved_debt"] is False
    assert manifest["physical_time_monotonic"] is True
    assert manifest["native_boundary"] == {
        "bits": 5184,
        "bytes": 648,
        "vm81_cells": 81,
        "x86_word_bits": 64,
        "hash72_lanes": 3,
        "hash216_occurrences": 216,
        "sha256_bytes_per_occurrence": 32,
    }
    assert manifest["reciprocal_normalization"]["compression_debt"] == {
        "numerator": 3,
        "denominator": 25,
    }
    assert manifest["reciprocal_normalization"]["execution_capacity"] == {
        "numerator": 25,
        "denominator": 3,
    }
    assert manifest["active_surface"]["immediate_cells_max"] == 7
    assert manifest["active_surface"]["total_vm81_cells"] == 81
    assert manifest["active_surface"]["reference_reduction_x1000"] == 11571
    assert manifest["latency_coupling"]["timing_is_noncanonical"] is True
    assert manifest["latency_coupling"]["over_budget_does_not_credit_time_back"] is True
    assert manifest["canonical_authority"]["debt_ledger"] is False
    assert manifest["canonical_authority"]["singleton_vm81"] == "INHERITED_C_ONLY"


def test_compression_debt_surface_declares_fail_closed_guards() -> None:
    surface = pass219_compression_debt_surface_declaration()
    assert surface["symbol"] == BOUNDARY_SYMBOL
    assert POLICY_VALIDATE_SYMBOL in surface["validators"]
    assert LAYER_CLOSE_SYMBOL in surface["validators"]
    assert TRANSFER_BOUND_SYMBOL in surface["validators"]
    assert GLOBAL_CLOSE_SYMBOL in surface["validators"]
    assert SCHEDULE_SYMBOL in surface["validators"]
    assert BOUNDARY_SYMBOL in surface["validators"]
    assert "physical_time_monotonic_no_time_credit" in surface["guards"]
    assert "no_anonymous_debt_cross_native_boundary" in surface["guards"]
    assert "immediate_active_surface_at_most_7_of_81" in surface["guards"]
    assert surface["mutation_policy"] == "INHERITED_SINGLETON_VM81_ONLY"
    assert surface["persistence_policy"] == "INHERITED_HASH72_HASH216_PATHS_ONLY"


def test_mandatory_data_ml_guard_inherits_compression_debt_policy() -> None:
    surface = pass219_mandatory_data_ml_surface_declaration()
    manifest = pass219_mandatory_data_ml_manifest()
    assert MANDATORY_COMPRESSION_DEBT_GUARD in surface["guards"]
    assert SCHEMA in surface["contract_schemas"]
    assert POLICY_VALIDATE_SYMBOL in surface["validators"]
    assert BOUNDARY_SYMBOL in surface["validators"]
    assert manifest["mandatory_compression_debt_guard"] == MANDATORY_COMPRESSION_DEBT_GUARD
    assert manifest["mandatory_compression_debt_schema"] == SCHEMA
    assert manifest["compression_debt_policy"]["conserved_quantity"] == "COMPRESSION_DEBT"
    assert manifest["compression_debt_policy"]["elapsed_time_is_debt"] is False
    assert manifest["compression_debt_policy"]["anonymous_debt_allowed"] is False

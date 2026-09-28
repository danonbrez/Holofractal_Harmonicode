from __future__ import annotations

import json
from pathlib import Path

from hhs_runtime.hhs_pass220_numpy_four_phase_ab_v1 import (
    CHANNELS,
    PHASE_PLAN,
)
from hhs_runtime.hhs_pass220_schrodinger_firing_order_v1 import firing_order


HEADER = Path(
    "hhs_runtime/include/hhs_pass220_lane5_priority_offset_hydration_1_0.h"
)
SOURCE = Path(
    "hhs_runtime/c/hhs_pass220_lane5_priority_offset_hydration_1_0.inc"
)
AGG_HEADER = Path("hhs_runtime/include/hhs_runtime_exact_abi.h")
AGG_SOURCE = Path("hhs_runtime/c/hhs_runtime_exact_abi.c")


def test_native_priority_offset_surface_is_in_cumulative_exact_abi():
    assert HEADER.exists()
    assert SOURCE.exists()
    assert (
        '#include "hhs_pass220_lane5_priority_offset_hydration_1_0.h"'
        in AGG_HEADER.read_text(encoding="utf-8")
    )
    assert (
        '#include "hhs_pass220_lane5_priority_offset_hydration_1_0.inc"'
        in AGG_SOURCE.read_text(encoding="utf-8")
    )


def test_native_surface_preserves_literal_firing_constructor():
    text = SOURCE.read_text(encoding="utf-8")
    assert firing_order() == (8, 24, 40, 56, 72, 16, 32, 48, 64)
    assert "HHS_P220_FIRING_ORDER[9]" in text
    for value in firing_order():
        assert str(value) in text
    assert "HHS_EXACT_PASS220_PRIORITY_OFFSET_FIRING_STEP" in text
    assert "hhs_p220_priority_validate_firing_pattern" in text


def test_native_scalar_symbols_and_channel_factors_match_python_ab_plan():
    text = SOURCE.read_text(encoding="utf-8")
    scalar_symbols = tuple(row["scalar_symbol"] for row in PHASE_PLAN)
    assert scalar_symbols == (-1, 4, -3, -2, 0, 2, 3, -4, 1)
    assert "HHS_P220_SCALAR_SYMBOLS[9]" in text
    assert "HHS_P220_CHANNEL_FACTORS[4]" in text
    assert CHANNELS == ("xy", "yx", "zw", "wz")


def test_native_mediation_calls_existing_lane5_hnan_preflight_boundary():
    text = SOURCE.read_text(encoding="utf-8")
    assert "hhs_exact_pass219_lane5_mediate_candidate" in text
    assert "receipt.zero_sum_closure_passed != 1U" in text
    assert "receipt.exact_vm5184_bound != 1U" in text
    assert "receipt.rna_cell_wall_bound != 1U" in text


def test_dense_substitution_has_no_native_runtime_authority():
    text = SOURCE.read_text(encoding="utf-8")
    assert "descriptor.dense_substitution_runtime_authority = 0U;" in text
    assert "descriptor.scalar_offset_priority_candidate = 1U;" in text
    assert "witness.canonical_vm81_mutation_authority = 0U;" in text
    assert "witness.canonical_hash72_authority = 0U;" in text
    assert "witness.canonical_hash216_authority = 0U;" in text


def test_restart_and_contract_document_native_scope():
    doc = Path(
        "docs/pass220/PASS_220_LANE5_PRIORITY_OFFSET_NATIVE_AB_V1.md"
    ).read_text(encoding="utf-8")
    restart = Path(
        "docs/operations/restart/"
        "PASS_220_LANE5_PRIORITY_OFFSET_NATIVE_AB_RESTART_20260927.md"
    ).read_text(encoding="utf-8")
    for token in (
        "8 -> 24 -> 40 -> 56 -> 72 -> 16 -> 32 -> 48 -> 64 -> 8",
        "hhs_exact_pass219_lane5_mediate_candidate",
        "HNAN",
        "candidate-only",
        "dense",
        "compact",
    ):
        assert token in doc
        assert token in restart

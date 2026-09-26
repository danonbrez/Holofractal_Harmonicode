from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_global_constraint_graph_matches_wolfram_receipt():
    graph = json.loads(
        (ROOT / "contracts/pass219/PASS_219_LANE5_HNAN_GLOBAL_CONSTRAINT_GRAPH_1_63.json")
        .read_text(encoding="utf-8")
    )
    proof = json.loads(
        (ROOT / "evidence/pass219/lane5_hnan_global_constraint_1_63_wolfram_20260926_v1.output.json")
        .read_text(encoding="utf-8")
    )
    assert graph["mandatory_rule_count"] == 15
    assert graph["mandatory_rule_mask"] == 0x7FFF
    assert graph["ordered_zero_closure_source"] == "0=∅=AB/P⁴∅=HNAN"
    assert proof["status"] == "PASS"
    assert proof["check_count"] == 25
    assert proof["pass_count"] == 25
    assert proof["failed"] == []
    assert proof["zero_closure"] == ["ZERO", "EMPTYSET", "AB_P4_EMPTYSET", "HNAN"]
    assert proof["reciprocal_chain"] == ["INFINITY", "DELTA", "X"]
    assert proof["hnan_order"] == ["x", "y", "-z", "-w", "xy", "yx", "-zw", "-wz"]
    assert proof["generic_lift_conditions"] == ["r!=s", "r+s!=0"]


def test_c_runtime_is_bound_into_lane5_and_signed_vm81_preflight():
    exact = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text(encoding="utf-8")
    aggregate = (ROOT / "hhs_runtime/include/hhs_runtime_exact_abi.h").read_text(encoding="utf-8")
    lane5 = (
        ROOT / "hhs_runtime/c/hhs_pass219_lane5_global_holographic_nucleus_1_34.inc"
    ).read_text(encoding="utf-8")
    env = (
        ROOT / "hhs_runtime/c/hhs_pass219_vm81_environmental_recovery_1_32.inc"
    ).read_text(encoding="utf-8")

    assert '#include "hhs_pass219_lane5_hnan_global_constraint_1_63.h"' in aggregate
    assert '#include "hhs_pass219_lane5_hnan_global_constraint_1_63.inc"' in exact
    assert "hhs_exact_pass219_hnan_global_system_verify" in lane5
    assert "hhs_exact_pass219_hnan_global_system_verify" in env


def test_whitepaper_and_global_nucleus_contract_bind_same_algorithm():
    paper = (
        ROOT / "docs/whitepapers/HHS_HNAN_JORDAN_GLOBAL_CONSTRAINT_RESOLUTION_THEOREM_V1.md"
    ).read_text(encoding="utf-8")
    nucleus = (
        ROOT / "contracts/pass219/PASS_219_LANE5_GLOBAL_HOLOGRAPHIC_NUCLEUS_V1.md"
    ).read_text(encoding="utf-8")
    for literal in (
        "0=∅=AB/P⁴∅=HNAN",
        "J2(0)",
        "∞∆=Bx^5184",
        "R(∞)=∆",
        "R(∆)=x",
        "u^72 -> u^0",
    ):
        assert literal in paper
    assert "HNAN global constraint and contradiction resolver" in nucleus
    assert "signed environmental VM81 admission" in nucleus

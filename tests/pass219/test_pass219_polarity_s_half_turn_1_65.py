from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DEFINITIONS = "xy=s/zw yx=-s/zw zw=s/xy wz=-s/xy"
NEGATIVE_S = "-s=x²(((p÷q)−(q÷p))+((q÷p)−(p÷q))×(q−p)−(p−q))"


def test_polarity_sources_and_wolfram_proof_are_frozen():
    proof = json.loads(
        (
            ROOT
            / "evidence/pass219/polarity_s_half_turn_wolfram_20260926_v1.output.json"
        ).read_text(encoding="utf-8")
    )
    assert proof["status"] == "PASS"
    assert " ".join(proof["native_definitions"]) == DEFINITIONS
    assert proof["negative_s_source"] == NEGATIVE_S
    assert hashlib.sha256(DEFINITIONS.encode()).hexdigest() == proof["definitions_sha256"]
    assert hashlib.sha256(NEGATIVE_S.encode()).hexdigest() == proof["negative_s_sha256"]
    assert proof["s_plus_one_sign_vector"] == [1, -1, 1, -1]
    assert proof["s_minus_one_sign_vector"] == [-1, 1, -1, 1]
    assert proof["p_minus_q_q_minus_p_before"] == [-2, 2]
    assert proof["p_minus_q_q_minus_p_after_s_minus_one"] == [2, -2]
    assert proof["phase_operator"] == "u^36"
    assert proof["phase_steps"] == 36
    assert proof["rotation_self_inverse"] is True
    assert proof["opposition_preserved"] is True
    assert proof["native_scalar_rewrite_authority"] is False


def test_contract_binds_existing_rml5_half_turn():
    contract = (
        ROOT / "contracts/pass219/PASS_219_POLARITY_S_HALF_TURN_1_65.md"
    ).read_text(encoding="utf-8")
    for literal in (
        "xy=s/zw",
        "yx=-s/zw",
        "zw=s/xy",
        "wz=-s/xy",
        "u^36",
        "phase modulus = 72",
        "(p-q):(q-p)=(-2):(+2)",
        "SCALAR_PROOF_ONLY",
    ):
        assert literal in contract


def test_both_runtime_boundaries_require_1_65():
    lane5 = (
        ROOT / "hhs_runtime/c/hhs_pass219_lane5_global_holographic_nucleus_1_34.inc"
    ).read_text(encoding="utf-8")
    env = (
        ROOT / "hhs_runtime/c/hhs_pass219_vm81_environmental_recovery_1_32.inc"
    ).read_text(encoding="utf-8")
    for source in (lane5, env):
        assert "hhs_exact_pass219_polarity_s_verify" in source
        assert "polarity_s.chiral_pairs_opposed" in source
        assert "polarity_s.half_turn_self_inverse" in source
        assert "polarity_s.p_q_pair_rotation_verified" in source

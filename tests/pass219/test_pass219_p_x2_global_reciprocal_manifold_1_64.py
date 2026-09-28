from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

RAW = "((p/q)*(q/p))/(P²-pq)=(q-p))P/(p+q)"
PARSED = "((p/q)*(q/p))/(P²-pq)=((q-p)*P)/(p+q)"


def test_correction_source_and_balanced_parse_are_distinct_and_frozen():
    raw = (
        ROOT
        / "contracts/pass219/PASS_219_P_X2_RECIPROCAL_CORRECTION_1_64.raw.hhs"
    ).read_text(encoding="utf-8")
    assert raw == RAW
    assert raw.count("(") == 6
    assert raw.count(")") == 7

    proof = json.loads(
        (
            ROOT
            / "evidence/pass219/px2_reciprocal_correction_wolfram_20260926_v1.output.json"
        ).read_text(encoding="utf-8")
    )
    assert proof["status"] == "PASS"
    assert proof["raw_source"] == RAW
    assert proof["balanced_ordered_parse"] == PARSED
    assert hashlib.sha256(RAW.encode()).hexdigest() == proof["raw_source_sha256"]
    assert hashlib.sha256(PARSED.encode()).hexdigest() == proof["balanced_parse_sha256"]
    assert proof["native_rewrite_authority"] is False
    assert proof["projected_lhs"] == "1"
    assert proof["projected_rhs"] == "1"
    assert proof["difference"] == "0"
    assert proof["closes"] is True


def test_runtime_preflights_require_the_correction_receipt():
    lane5 = (
        ROOT / "hhs_runtime/c/hhs_pass219_lane5_global_holographic_nucleus_1_34.inc"
    ).read_text(encoding="utf-8")
    env = (
        ROOT / "hhs_runtime/c/hhs_pass219_vm81_environmental_recovery_1_32.inc"
    ).read_text(encoding="utf-8")

    for source in (lane5, env):
        assert "hhs_exact_pass219_px2_manifold_verify" in source
        assert "px2_manifold.correction_raw_hash_verified" in source
        assert "px2_manifold.correction_parse_hash_verified" in source
        assert "px2_manifold.correction_native_order_preserved" in source
        assert "px2_manifold.correction_scalar_projection_closed" in source


def test_contract_preserves_native_and_scalar_projection_separation():
    contract = (
        ROOT
        / "contracts/pass219/PASS_219_P_X2_GLOBAL_RECIPROCAL_MANIFOLD_1_64.md"
    ).read_text(encoding="utf-8")
    assert RAW in contract
    assert PARSED in contract
    assert "SCALAR_PROOF_ONLY" in contract
    assert "p=P-1" in contract
    assert "q=P+1" in contract
    assert "P²-pq=1" in contract
    assert "Delta cancellation authority" in contract

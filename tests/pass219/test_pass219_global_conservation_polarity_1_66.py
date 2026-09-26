from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SOURCE = (
    "c²*P*(q-p)/(p+q)==((P²-pq)*m*c²)/∆==a²+b²\n"
    "P²-pq==(q-p)*P/(p+q)\n"
    "p=√6+√2 q=√6-√2 P=√3 s=-1\n"
    "(b^(b²/12))^72==2^6 b^6*c^4==72 b²=2 c²=3\n"
    "t^3-t==m²-m==(P³-P)/(P²-pq)\n"
    "p=P-1 q=P+1 p+q=2P q-p=2 P²-pq=1\n"
    "b²P-(p+q)==x+y+z+w+xy+yx+zw+wz\n"
    "xy+yx=0 zw+wz=0 x+y=z+w\n"
    "ratio!=qr_symbol; polarity_s independent unless explicit gate binds it\n"
)


def test_source_and_wolfram_receipt_are_frozen():
    path = (
        ROOT
        / "contracts/pass219/PASS_219_GLOBAL_CONSERVATION_POLARITY_1_66.hhs"
    )
    assert path.read_text(encoding="utf-8") == SOURCE
    assert len(SOURCE.encode("utf-8")) == 344
    assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
        "014216202745bbc0fa021b9eefa6e8fdbaf5510f544cb5a44a3012b2c96b2cd9"
    )

    proof = json.loads(
        (
            ROOT
            / "evidence/pass219/global_conservation_polarity_wolfram_20260926_v1.output.json"
        ).read_text(encoding="utf-8")
    )
    assert proof["status"] == "PASS"
    assert all(proof["checks"].values())
    assert proof["pell_branch"]["defect"] == "-1"
    assert proof["pell_branch"]["ratio_product"] == "1"
    assert proof["phase72_witness"]["b6c4"] == 72
    assert proof["master_conditional"]["solution"] == "Delta=m"
    assert proof["signed_metric_projection"]["canonical"]["c2"] == 3
    assert proof["signed_metric_projection"]["c2_metric"] == -3
    assert proof["signed_metric_projection"]["canonical_c2_overwritten"] is False
    assert proof["native_global_rewrite_authority"] is False


def test_contract_forbids_cross_gate_and_operator_collapse():
    contract = (
        ROOT
        / "contracts/pass219/PASS_219_GLOBAL_CONSERVATION_POLARITY_1_66.md"
    ).read_text(encoding="utf-8")
    for literal in (
        "ordinary exact quotient",
        "Legendre/Jacobi",
        "independent polarity selector",
        "This is not the Pell branch.",
        "MUST NOT rewrite canonical",
        "cross-gate substitution authority",
        "Browser/WebGL/Three.js surfaces remain downstream",
    ):
        assert literal in contract


def test_lane5_and_signed_vm81_require_1_66():
    lane5 = (
        ROOT / "hhs_runtime/c/hhs_pass219_lane5_global_holographic_nucleus_1_34.inc"
    ).read_text(encoding="utf-8")
    env = (
        ROOT / "hhs_runtime/c/hhs_pass219_vm81_environmental_recovery_1_32.inc"
    ).read_text(encoding="utf-8")
    for source in (lane5, env):
        assert "hhs_exact_pass219_conservation_1_66_verify" in source
        assert "conservation_1_66.operator_typing_verified" in source
        assert "conservation_1_66.canonical_c2_preserved" in source
        assert "conservation_1_66.unit_shell_x_plus_y_zero_verified" in source

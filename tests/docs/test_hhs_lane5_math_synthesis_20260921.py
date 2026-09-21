from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PAPER = ROOT / "docs/whitepapers/HHS_LANE5_MATHEMATICAL_EXTENSIONS_1_50_1_62_V1.md"
APPENDIX = ROOT / "docs/pass219/APPENDIX_J_LANE5_1_50_1_62_MATHEMATICAL_EXTENSIONS.md"
OUTPUT = ROOT / "evidence/pass219/hhs_lane5_mathematical_synthesis_20260921_v1.output.json"
RECEIPT = ROOT / "evidence/pass219/hhs_lane5_mathematical_synthesis_20260921_v1.receipt.json"
COMPENDIUM = ROOT / "docs/whitepapers/HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md"
INDEX = ROOT / "docs/whitepapers/HHS_LANE5_WHITEPAPER_INDEX_V1.md"
SPEC = ROOT / "docs/HARMONICODE_SPEC_v1.md"
ROOT_PAPER = ROOT / "whitepapers/HOLOFRACTAL_HARMONICODE.md"
DOCS_README = ROOT / "docs/README.md"


def test_wolfram_synthesis_is_green() -> None:
    payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
    assert payload["schema"] == "HHS_LANE5_MATHEMATICAL_SYNTHESIS_WOLFRAM_20260921_V1"
    assert payload["status"] == "PASS"
    assert payload["check_count"] == 44
    assert payload["pass_count"] == 44
    assert payload["failed"] == []
    assert payload["phase_orbit_lift72"] == [8, 24, 40, 56, 72, 16, 32, 48, 64]
    assert payload["t64_count"] == 64
    assert payload["reciprocal_pair_mean_residual"] == 0
    assert all(payload["checks"].values())


def test_receipt_binds_latest_main_and_stacked_source() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "PASS"
    assert receipt["main_base"] == "2dec42e192338cd1c1f7bb6d1994511be3bceeff"
    assert receipt["stacked_source_head"] == "d08572ef0f5d0a416637721322289cf3d686f26e"
    assert receipt["authority"] == "DOCUMENTATION_WOLFRAM_AUDIT_ONLY"


def test_whitepaper_preserves_core_mathematics() -> None:
    text = PAPER.read_text(encoding="utf-8")
    required = (
        "m_D n_D = A^2 + B^2 + Delta_D - Lambda_D",
        "AB != BA",
        "A/B != B/A",
        "(P=√(pq+(P⁴/AB)))/∆",
        "Cancel_∆(S)=forbidden",
        "144*36 = 5184",
        "72^72 = 5184^36 = 2^216 * 3^144",
        "T64 = {x,y,z,w}^3",
        "81 = 1 + 40*2",
        "q = n/9",
        "E = (8,24,40,56,72,16,32,48,64)",
        "Gamma * P * (q-p) = Sigma * (p+q)",
        "R_before --event--> R_after",
        "HHS-T5184-005 / Lane5-1.60",
        "HHS-T5184-005 / Lane5-1.61",
        "HHS-T5184-006",
    )
    for token in required:
        assert token in text


def test_appendix_and_indexes_reference_synthesis() -> None:
    assert "checks = 44/44" in APPENDIX.read_text(encoding="utf-8")
    marker = "HHS_LANE5_MATHEMATICAL_EXTENSIONS_1_50_1_62_V1.md"
    for path in (COMPENDIUM, INDEX, SPEC, ROOT_PAPER, DOCS_README):
        assert marker in path.read_text(encoding="utf-8"), path

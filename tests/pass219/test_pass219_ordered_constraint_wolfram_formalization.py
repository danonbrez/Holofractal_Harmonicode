from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "contracts/pass219/PASS_219_ORDERED_CONSTRAINT_WOLFRAM_FORMALIZATION_1_0.harmonicode"
WOLFRAM_PATH = ROOT / "formal/wolfram/pass219_ordered_constraint_formalization_1_0.wl"
MANIFEST_PATH = ROOT / "contracts/pass219/PASS_219_ORDERED_CONSTRAINT_WOLFRAM_FORMALIZATION_1_0.json"

EXPECTED_SOURCE_SHA256 = "d6d7da60e3e9520c0ec802fa8ec63121ffbee9313263012d021907e210bc652c"
EXPECTED_WOLFRAM_SHA256 = "7e4203b0eb578cd10303971fb715576d7fd3af5c8921bd46d5a522d61a950a98"
EXPECTED_OUTER_ORDER_HASH = "9049d2ff6db8aae344af85c2f34926bf76e5074013d3ab87fb07aecea692fe2f"

REQUIRED_DECIMALS = (
    "0.123456789",
    "0.987654321",
    "123456789.123456789",
    "0.999999999999999999",
    "0.00000000810000007371000067",
    "8.10000005751000053",
    "0.99999999999999999999999999",
    "0.000000008100000073710000670761006",
    "8.1000000575100005395410047",
    "0.000000008100000073710001",
    "8.10000005751",
    "2.133185666641251470403352397272",
)

PHASE_WITNESSES = (
    "List(I*x,I^3*y,I*z,I^3*w)",
    "List((-I)*x+123456789/(a^2*s*x),I*y+987654321/(a^2*s*y),(-I)*z+0.123456789/(a^2*s*z),I*w+0.987654321/(a^2*s*w))",
    "List(-I*x+123456789/(a^2*s*x),I*y+987654321/(a^2*s*y),-I*z+0.123456789/(a^2*s*z),I*w+0.987654321/(a^2*s*w))",
)

QUARTIC_WITNESSES = (
    "(x*y+z*w)/(y^4*w^4)",
    "(w*z+x*y)/(w^4*y^4)",
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _depth_before(text: str) -> list[int]:
    depth = 0
    out: list[int] = []
    for char in text:
        out.append(depth)
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        assert depth >= 0, "delimiter depth went negative"
    assert depth == 0, "unbalanced delimiters"
    return out


def _top_level_positions(text: str, operator: str) -> list[int]:
    depth = _depth_before(text)
    return [
        index
        for index in range(0, len(text) - len(operator) + 1)
        if depth[index] == 0 and text.startswith(operator, index)
    ]


def _split_at_positions(text: str, positions: list[int], width: int) -> list[str]:
    start = 0
    parts: list[str] = []
    for position in positions:
        parts.append(text[start:position])
        start = position + width
    parts.append(text[start:])
    return parts


def test_canonical_source_is_exact_and_byte_stable() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert len(source.encode("utf-8")) == 1321
    assert _sha256(source) == EXPECTED_SOURCE_SHA256
    assert "`" not in source


def test_outer_constraint_topology_is_ordered_4_edges_5_segments() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    eq_positions = _top_level_positions(source, "==")
    segments = _split_at_positions(source, eq_positions, 2)
    assert len(eq_positions) == 4
    assert len(segments) == 5
    assert len(_top_level_positions(segments[0], "/")) == 1
    assert segments[-2] == "e^(y*Pi)"
    assert segments[-1] == "x((a²,b²i,c²,(-c²-b²i)))"


def test_exact_decimal_phase_and_order_witnesses_survive() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert all(value in source for value in REQUIRED_DECIMALS)
    assert len({"0.999999999999999999", "0.99999999999999999999999999", "1"}) == 3
    assert all(value in source for value in PHASE_WITNESSES)
    assert all(value in source for value in QUARTIC_WITNESSES)
    assert source.count("List(x,y,z,w)") >= 2


def test_u72_relational_carrier_is_not_booleanized() -> None:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert "(u==2.133185666641251470403352397272)^72" in source
    assert "u=True" not in source
    assert "u=False" not in source


def test_wolfram_formalization_is_pinned_and_fail_closed() -> None:
    wolfram = WOLFRAM_PATH.read_text(encoding="utf-8")
    assert _sha256(wolfram) == EXPECTED_WOLFRAM_SHA256
    assert 'canonicalSource = Import[sourcePath, "Text"]' in wolfram
    assert "VerificationTest[" in wolfram
    assert "TestReport[tests]" in wolfram
    assert 'TestID -> "outer-equality-count"' in wolfram
    assert 'TestID -> "outer-ordered-constraint-arity"' in wolfram
    assert 'TestID -> "ordered-quartic-corrections"' in wolfram
    assert 'If[report["TestsFailedCount"] =!= 0, Exit[1]];' in wolfram


def test_manifest_binds_source_wolfram_and_external_proof_receipt() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    canonical = manifest["canonical_source"]
    wolfram = manifest["wolfram_formalization"]

    assert manifest["schema"] == "HHS_PASS219_ORDERED_CONSTRAINT_WOLFRAM_FORMALIZATION_CONTRACT_V1"
    assert manifest["base_main_sha"] == "ea3948afecb40a35b61eb7473f094eee6fd63cb0"
    assert canonical["sha256"] == EXPECTED_SOURCE_SHA256
    assert canonical["bytes_utf8"] == 1321
    assert canonical["host_boolean_evaluation_permitted"] is False
    assert canonical["commutative_reorder_permitted"] is False
    assert canonical["scalar_projection_substitution_authority"] is False

    assert wolfram["sha256"] == EXPECTED_WOLFRAM_SHA256
    assert wolfram["tests_run"] == 13
    assert wolfram["tests_succeeded"] == 13
    assert wolfram["tests_failed"] == 0
    assert wolfram["all_succeeded"] is True
    assert wolfram["outer_top_level_equality_edges"] == 4
    assert wolfram["outer_ordered_segments"] == 5
    assert wolfram["first_outer_segment_top_level_quotients"] == 1
    assert wolfram["outer_segment_order_hash_sha256"] == EXPECTED_OUTER_ORDER_HASH


def test_inherited_authority_boundaries_remain_explicit() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    nonclaims = "\n".join(manifest["nonclaims"])
    assert "does not authorize commutation" in nonclaims
    assert "Canonical VM81 mutation and Hash72/Hash216 mint authority are unchanged." in nonclaims

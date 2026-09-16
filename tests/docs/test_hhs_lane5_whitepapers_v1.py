from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
WHITEPAPERS = ROOT / "docs" / "whitepapers"

MAIN = WHITEPAPERS / "HHS_UNIFIED_TECHNICAL_WHITE_PAPER_LANE5_1_48_V1.md"
EQUATIONS = WHITEPAPERS / "HHS_LANE5_EQUATION_AND_LOGIC_COMPENDIUM_V1.md"
PERFORMANCE = WHITEPAPERS / "HHS_LANE5_PERFORMANCE_VERIFICATION_EVIDENCE_V1.md"
INDEX = WHITEPAPERS / "HHS_LANE5_WHITEPAPER_INDEX_V1.md"
BOUNDARY = ROOT / "contracts" / "pass219" / "PASS_219_LANE5_EXACT_BOUNDARY_QUANTUM_THERMO_MANIFOLD_V1.md"
LEAN = ROOT / "formal" / "lean" / "HHS_GFE_Field_Quotient.lean"
COQ = ROOT / "formal" / "coq" / "HHS_GFE_Field_Quotient.v"

VERIFIED_MAIN = "a8fc0646e21b2a67804468575f364fef1762ec6a"
BOUNDARY_SHA256 = "938a39487f1841999609d7c75f944b26694c5aadfc6e540c29576c1bb7d57d8d"
MANIFOLD = 72**72
MANIFOLD_DECIMAL = (
    "53449019547361999534025300140057538544940601393106611570269540644280818850419033099696863861289188541180498511377339362341642322313216"
)


def read(path: Path) -> str:
    assert path.is_file(), path
    return path.read_text(encoding="utf-8")


def canonical_boundary_source() -> str:
    text = read(BOUNDARY)
    section = text.split("## 2. Canonical governing boundary source", 1)[1]
    match = re.search(r"```text\n(.*?)\n```", section, flags=re.DOTALL)
    assert match is not None
    return match.group(1)


def test_whitepaper_set_exists_and_targets_verified_main() -> None:
    for path in (MAIN, EQUATIONS, PERFORMANCE, INDEX):
        text = read(path)
        assert VERIFIED_MAIN in text


def test_exact_manifold_cardinality_and_address_width() -> None:
    assert str(MANIFOLD) == MANIFOLD_DECIMAL
    assert MANIFOLD.bit_length() == 445
    assert 56 * 8 >= MANIFOLD.bit_length()
    assert (MANIFOLD - 1).bit_length() == 445

    combined = read(MAIN) + read(EQUATIONS) + read(PERFORMANCE)
    assert MANIFOLD_DECIMAL in combined
    assert "ceil(log2(72^72)) = 445" in combined
    assert "56 bytes" in combined


def test_current_canonical_boundary_is_preserved_byte_for_byte() -> None:
    source = canonical_boundary_source()
    assert len(source.encode("utf-8")) == 681
    assert sha256(source.encode("utf-8")).hexdigest() == BOUNDARY_SHA256

    compendium = read(EQUATIONS)
    assert source in compendium
    assert BOUNDARY_SHA256 in compendium
    assert "`CANONICAL_VERBATIM`" in compendium
    assert "`DEVELOPMENT_VERBATIM`" in compendium


def test_development_tensor_and_collapse_surfaces_are_preserved() -> None:
    compendium = read(EQUATIONS)
    required = (
        "List(List((x*y),x+y,(y*x)),List((x*y)-(z*w)",
        "MatrixTimes(List(List((x*y),x+y,(y*x))",
        "NcalcMatrixPower",
        "List(List((1*u)==u^72,0,(1*u^18))",
        "(a²+b²=c²)²=P⁴",
        "E^(O x)=x²",
        "0/0 := two-qubit entanglement-superposition slot",
        "72^72 = 5184^36",
        "materialized_intermediate_states = 0",
    )
    for needle in required:
        assert needle in compendium, needle


def test_primary_1_48_performance_baseline_is_exactly_documented() -> None:
    performance = read(PERFORMANCE)
    required = (
        "1,000,000",
        "3,791,766,778 ns",
        "263,727 candidates/s",
        "568 bytes",
        "56 bytes",
        "1,984,238",
        "197,797 bytes/s",
        "1,000 ledger entries",
        "223 appends/s",
        "102,577,250",
        "105,291,642",
        "50,388,480",
        "5,820,705",
        "59,492 ns = 59.492 microseconds",
    )
    for needle in required:
        assert needle in performance, needle


def test_authority_boundary_is_explicit() -> None:
    combined = read(MAIN) + read(PERFORMANCE)
    required = (
        "canonical VM81 mutation",
        "canonical Hash72",
        "canonical Hash216",
        "signed environmental VM81 admission",
        "candidate-only",
        "observational",
    )
    for needle in required:
        assert needle.lower() in combined.lower(), needle


def test_formal_mirror_status_is_not_overstated() -> None:
    lean = read(LEAN)
    coq = read(COQ)
    main = read(MAIN)

    assert "sorry" in lean
    assert "style-complete sketch" in lean
    assert "Qed." in coq
    assert "does not claim a completed compiled Lean proof" in main
    assert "completed `Qed` theorem bodies" in main


def test_legacy_overclaims_are_absent() -> None:
    combined = read(MAIN) + read(PERFORMANCE) + read(INDEX)
    forbidden = (
        "4.3M represented states/sec/core",
        "0.23 ns/state",
        "10¹¹⁹×",
        "Infinite (structural)",
        "all possible x86_64 operations and memory states",
        "Quantum volume: 72⁷²",
        "Bell inequality violation\tFactor",
    )
    for phrase in forbidden:
        assert phrase not in combined, phrase


def test_evidence_classification_is_indexed() -> None:
    index = read(INDEX)
    for label in (
        "CANONICAL_VERBATIM",
        "DEVELOPMENT_VERBATIM",
        "EXECUTED_EXACT",
        "HHS_NATIVE_SEMANTIC",
        "REFERENCE_ONLY",
        "OBSERVATIONAL",
    ):
        assert label in index


def test_docs_index_links_all_whitepapers() -> None:
    docs_index = read(ROOT / "docs" / "README.md")
    for path in (MAIN, EQUATIONS, PERFORMANCE, INDEX):
        assert path.name in docs_index

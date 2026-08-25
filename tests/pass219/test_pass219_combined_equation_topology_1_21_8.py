from __future__ import annotations

from pathlib import Path

from hhs_runtime.core_sandbox.hhs_pass219_combined_equation_optimizer_1_21_8 import DENOMINATOR_SOURCE

ROOT = Path(__file__).resolve().parents[2]
NUMERATOR = ROOT / "contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode"
COMBINED = ROOT / "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode"


def _paren_census(source: str) -> tuple[int, int]:
    depth = 0
    pairs = 0
    max_depth = 0
    for ch in source:
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            assert depth > 0
            depth -= 1
            pairs += 1
    assert depth == 0
    return pairs, max_depth


def test_raw_source_topology_counts_are_exact() -> None:
    numerator = NUMERATOR.read_text(encoding="utf-8")
    combined = COMBINED.read_text(encoding="utf-8")

    numerator_pairs, _ = _paren_census(numerator)
    denominator_pairs, _ = _paren_census(DENOMINATOR_SOURCE)
    combined_pairs, _ = _paren_census(combined)

    assert numerator_pairs == 34
    assert denominator_pairs == 14
    assert combined_pairs == 64
    assert numerator.count("=") == 15
    assert numerator.count("==") == 5
    assert combined.count("=") == 16
    assert combined.count("==") == 5
    assert combined.count(DENOMINATOR_SOURCE) == 2


def test_common_subexpression_reuse_preserves_two_source_spans() -> None:
    combined = COMBINED.read_text(encoding="utf-8")
    first = combined.find(DENOMINATOR_SOURCE)
    second = combined.find(DENOMINATOR_SOURCE, first + 1)
    assert first >= 0
    assert second > first
    assert combined[first:first + len(DENOMINATOR_SOURCE)] == DENOMINATOR_SOURCE
    assert combined[second:second + len(DENOMINATOR_SOURCE)] == DENOMINATOR_SOURCE

    # Candidate compiled execution may intern one immutable D node, but source
    # provenance must keep both occurrences.  Fourteen shell evaluations are
    # duplicated by the raw tree representation; this is a CSE work candidate,
    # not permission to erase the second source span.
    raw_parenthesis_pairs, _ = _paren_census(combined)
    duplicate_denominator_shells = _paren_census(DENOMINATOR_SOURCE)[0]
    candidate_unique_shell_evaluations = raw_parenthesis_pairs - duplicate_denominator_shells
    assert raw_parenthesis_pairs == 64
    assert duplicate_denominator_shells == 14
    assert candidate_unique_shell_evaluations == 50


def test_sixty_four_parenthesis_match_is_evidence_not_thread_authority() -> None:
    combined = COMBINED.read_text(encoding="utf-8")
    pairs, _ = _paren_census(combined)
    assert pairs == 64

    # The combined source also carries 16 literal equality characters.  The
    # exact coincidence with the inherited 64-operation fabric is therefore a
    # topology fact to test through Pass159/Pass169 lowering, not a license to
    # assign one parenthesis directly to one canonical VM thread here.
    assert combined.count("=") == 16
    canonical_thread_mapping_proven = False
    assert canonical_thread_mapping_proven is False


def main() -> int:
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print(f"PASS219 I121.8 topology census: {len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

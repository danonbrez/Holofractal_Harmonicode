import pytest

from hhs_general_runtime_layer_v1 import AuditedRunner
from terminal_hhsprog_v4_symbolic import HHSSymbolicParseError, HHSSymbolicParserV1


def test_symbolic_parser_preserves_exact_rational_identity_without_truth_promotion():
    runner = AuditedRunner()
    parser = HHSSymbolicParserV1(runner.authority)
    parsed = parser.parse("E^(I*Pi*(1/2+I*t)) == I*E^(-Pi*t)")
    assert parsed["structure"]["form"] == "EQUALITY_CHAIN"
    assert parsed["structure"]["truth_evaluated"] is False
    assert parsed["structure"]["contains_float_literal"] is False
    assert parsed["source_hash72"]
    assert parsed["symbolic_hash72"]


def test_symbolic_parser_marks_decimal_literals():
    runner = AuditedRunner()
    parser = HHSSymbolicParserV1(runner.authority)
    parsed = parser.parse("t==14.1347")
    assert parsed["structure"]["contains_float_literal"] is True


def test_symbolic_parser_rejects_unbalanced_source():
    runner = AuditedRunner()
    parser = HHSSymbolicParserV1(runner.authority)
    with pytest.raises(HHSSymbolicParseError):
        parser.parse("List(1,2")

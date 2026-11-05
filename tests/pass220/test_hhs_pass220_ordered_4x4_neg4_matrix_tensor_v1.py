"""Dependency-scoped source, operator-order, and denied-authority regression."""
from pathlib import Path
import pytest

from hhs_runtime.pass220.hhs_pass220_ordered_4x4_neg4_matrix_tensor_v1 import (
    MatrixTensorHIRReject, OrderedSourceParser, stage_hir, _locked_tree,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode"


def test_verbatim_source_hir_and_native_boundary():
    result = stage_hir(ROOT)
    assert result["source_bytes"] == 366
    assert result["source_preserved_verbatim"] is True
    assert result["pass169_type"] == "ExactMatrixPower"
    assert result["node_kind"] == "EXACT_SYMBOLIC_MATRIX_POWER"
    assert result["source_shape"] == [4, 4]
    assert result["exponent_token"] == "(-4)"
    assert result["typed_symbols"] == ["s", "v"]
    assert result["ordered_matrix_operators"] == ["MatrixTimes"] * 3
    assert len(result["matrix_occurrences"]) == 4
    assert [x["cell_count"] for x in result["matrix_occurrences"]] == [16] * 4
    assert result["matrix_occurrences"][3]["ordered_cells"][3] == ["1", "1", "1", "0"]
    assert result["ordered_ast"]["kind"] == "ORDERED_EQUALITY_GATE"
    for flag in (
        "matrix_power_value_derived", "matrix_division_evaluated",
        "typed_s_v_substituted", "host_matrixpower_used",
        "floating_point_authority", "vm81_execution_verified",
        "hash72_commit_authority", "hash216_commit_authority",
        "canonical_vm81_mutation_authority",
    ):
        assert result[flag] is False


def test_source_sha256_drift_fails_closed(tmp_path):
    dest = tmp_path / "contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode"
    dest.parent.mkdir(parents=True)
    dest.write_text(SOURCE.read_text().replace("(-4)", "(-2)"))
    with pytest.raises(MatrixTensorHIRReject, match="VERBATIM_SOURCE_IDENTITY_DRIFT"):
        stage_hir(tmp_path)


@pytest.mark.parametrize("change", [
    lambda s: s.replace("MatrixTimes(v,", "MatrixTimes(s,"),
    lambda s: s.replace("/MatrixTimes(", "/List("),
    lambda s: s.replace("(-4)", "(-1)"),
    lambda s: s.replace("==MatrixTimes", "/MatrixTimes"),
    lambda s: s.replace("List(1,1,1,0)", "List(1,1,1,1)"),
    lambda s: s.replace("NcalcMatrixPower", "MatrixPower"),
    lambda s: s.replace("(-1)", "1", 1),
    lambda s: s.replace("1,1,1,1)", "1,1,1,1,1)", 1),
    lambda s: s + "*2",
    lambda s: s.replace("List(4,4,4,2)", "List(4,4,4,3)"),
])
def test_operator_source_topology_mutations_rejected(change):
    with pytest.raises(MatrixTensorHIRReject):
        _locked_tree(change(SOURCE.read_text()))


def test_unsupported_host_algebra_rejected():
    with pytest.raises(MatrixTensorHIRReject, match="UNSUPPORTED_LEXICAL_GLYPH"):
        OrderedSourceParser("MatrixTimes(v,s)^2")

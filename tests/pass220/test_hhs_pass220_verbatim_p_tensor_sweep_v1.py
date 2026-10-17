"""Focused non-evaluating HHS P-sweep ingress and negative authority tests."""
from pathlib import Path
import pytest

from hhs_runtime.pass220.hhs_pass220_verbatim_p_tensor_sweep_v1 import (
    BINDING_SCHEMA,
    VerbatimPSweepError,
    stage_verbatim_p_sweep,
    verify_verbatim_source,
)

ROOT = Path(__file__).resolve().parents[2]


def _binding(marker="X", *, cell=4, opcode=9):
    return {
        "schema": BINDING_SCHEMA,
        "symbol": "P",
        "vm81_cell": cell,
        "vm81_opcode": opcode,
        "harmonicode_5184": marker * 5184,
        "predecessor_hash216": marker * 216,
        "native_receipt_ref": "SYNTHETIC-SHAPE-TEST-NOT-AN-ADMITTED-RECEIPT",
    }


def test_source_is_exact_and_relations_are_ordered():
    result = verify_verbatim_source(ROOT)
    assert result["source_bytes"] == 180
    assert result["source_characters"] == 176
    assert len(result["ordered_list_spans"]) == 2
    assert [x["operator"] for x in result["relation_spans"]] == ["==", "==", "==", "=", "==", "=", "=="]
    assert len(result["P_symbol_spans"]) == 4
    assert result["scalar_interpretation_applied"] is False


def test_two_typed_states_staged_without_values_or_receipts():
    result = stage_verbatim_p_sweep([_binding("X"), _binding("Y", cell=5, opcode=2)], root=ROOT)
    assert result["candidate_count"] == 2
    assert result["global_ordered_closure_constraint"] == "P⁴=AB=c⁴"
    assert result["genesis_equality_universally_enforced"] is False
    assert result["requires_existing_singleton_mutation_authority"] is True
    assert result["hash72_commit_authority"] is False
    assert result["hash216_commit_authority"] is False
    assert result["canonical_vm81_mutation_authority"] is False
    first, second = result["candidates"]
    assert first["typed_P_binding"]["vm5184_address"] == 265
    assert second["typed_P_binding"]["vm5184_address"] == 322
    assert first["binding_diagnostic_sha256"] != second["binding_diagnostic_sha256"]
    for candidate in result["candidates"]:
        assert candidate["evaluation_status"] == "PENDING_SIGNED_VM81_WHOLE_EXPRESSION_EXECUTION"
        assert candidate["native_values"] is None
        assert candidate["hash72_receipt"] is None
        assert candidate["hash216_transition"] is None
        assert candidate["canonical_mutation"] is False
        assert candidate["typed_P_binding"]["binding_authenticity_verified"] is False


def test_source_drift_fails_closed(tmp_path):
    path = tmp_path / "contracts/pass220/PASS_220_VERBATIM_P_TENSOR_SWEEP_V1.harmonicode"
    path.parent.mkdir(parents=True)
    source = (ROOT / "contracts/pass220/PASS_220_VERBATIM_P_TENSOR_SWEEP_V1.harmonicode").read_text()
    path.write_text(source.replace("q-P=P-p", "q-P=P-q"))
    with pytest.raises(VerbatimPSweepError, match="VERBATIM_SOURCE_IDENTITY_DRIFT"):
        verify_verbatim_source(tmp_path)


@pytest.mark.parametrize("mutate", [
    lambda b: dict(b, symbol="p"),
    lambda b: dict(b, vm81_cell=81),
    lambda b: dict(b, vm81_opcode=64),
    lambda b: dict(b, vm81_cell=True),
    lambda b: dict(b, harmonicode_5184="1"),
    lambda b: dict(b, predecessor_hash216="bad"),
    lambda b: dict(b, native_receipt_ref=""),
    lambda b: dict(b, P=1.5),
    lambda b: dict(b, P=2),
])
def test_invalid_state_rejected(mutate):
    with pytest.raises(VerbatimPSweepError):
        stage_verbatim_p_sweep([mutate(_binding())], root=ROOT)


def test_duplicates_and_empty_sweeps_fail_closed():
    with pytest.raises(VerbatimPSweepError, match="DUPLICATE_TYPED_P_STATE"):
        stage_verbatim_p_sweep([_binding(), _binding()], root=ROOT)
    with pytest.raises(VerbatimPSweepError, match="SWEEP_CARDINALITY_OUT_OF_RANGE"):
        stage_verbatim_p_sweep([], root=ROOT)

from copy import deepcopy
import pytest

from hhs_runtime.hhs_pass111_predictive_continuation_cache_v1 import _hash
from hhs_runtime.hhs_pass114_palindromic_decimal_state_v1 import NumeralRecoveryContract
from hhs_runtime.hhs_pass115_canonical_qudit_serialization_v1 import (
    CanonicalQuditSerializationEngine,
    ManifoldContract,
    QuditSerializationError,
    pass115_self_test,
)


def _values():
    return [((r * 3 + r // 3 + c) % 9) for r in range(9) for c in range(9)]


def test_pass115_full_round_trip():
    result = pass115_self_test()
    assert result["status"] == "PASS"
    assert result["recovered"]["recovery_receipt"]["recovery_status"] == "QUDIT_MANIFOLD_RECOVERY_VALIDATED"


def test_position_coordinate_bijection_row_major():
    engine = CanonicalQuditSerializationEngine()
    contract = ManifoldContract()
    for i in range(81):
        rc = engine.index_to_coordinate(i, contract)
        assert engine.coordinate_to_index(*rc, contract) == i


def test_box_major_differs_but_round_trips():
    engine = CanonicalQuditSerializationEngine()
    contract = ManifoldContract(traversal_contract="SUDOKU_BOX_MAJOR")
    assert engine.index_to_coordinate(9, contract) != (1, 0)
    for i in range(81):
        rc = engine.index_to_coordinate(i, contract)
        assert engine.coordinate_to_index(*rc, contract) == i


def test_rotation_is_preserved():
    engine = CanonicalQuditSerializationEngine()
    contract = ManifoldContract(orientation="ROTATE_90")
    manifold = engine.serialize(_values(), contract=contract)
    recovered = engine.reconstruct(manifold)
    assert recovered["values"] == _values()


def test_rejects_wrong_cell_count():
    with pytest.raises(QuditSerializationError) as exc:
        CanonicalQuditSerializationEngine().serialize(_values()[:-1], contract=ManifoldContract())
    assert exc.value.code == "REJECT_CELL_COUNT_DIMENSION_MISMATCH"


def test_rejects_duplicate_coordinate_after_reroot():
    engine = CanonicalQuditSerializationEngine()
    manifold = engine.serialize(_values(), contract=ManifoldContract())
    bad = deepcopy(manifold)
    bad["cells"][1]["coordinate"] = bad["cells"][0]["coordinate"]
    bad["cells"][1]["cell_state_root_hash72"] = _hash("hhs_pass115_cell_state_v1", {k: deepcopy(v) for k, v in bad["cells"][1].items() if k != "cell_state_root_hash72"})
    bad["serialization_root_hash72"] = _hash("hhs_pass115_serialization_v1", {k: deepcopy(v) for k, v in bad.items() if k != "serialization_root_hash72"})
    with pytest.raises(QuditSerializationError) as exc:
        engine.validate(bad)
    assert exc.value.code == "REJECT_DUPLICATE_CELL_COORDINATE"


def test_rejects_cell_root_corruption():
    engine = CanonicalQuditSerializationEngine()
    manifold = engine.serialize(_values(), contract=ManifoldContract())
    bad = deepcopy(manifold)
    bad["cells"][0]["value"] = 8
    bad["serialization_root_hash72"] = _hash("hhs_pass115_serialization_v1", {k: deepcopy(v) for k, v in bad.items() if k != "serialization_root_hash72"})
    with pytest.raises(QuditSerializationError) as exc:
        engine.validate(bad)
    assert exc.value.code == "REJECT_CELL_ROOT_MISMATCH"


def test_pass114_numeral_source_is_exact():
    engine = CanonicalQuditSerializationEngine()
    manifold = engine.serialize(_values(), contract=ManifoldContract())
    authority = _hash("test_authority", {"p": 115})
    bundle = engine.encode_with_pass114(manifold, recovery_contract=NumeralRecoveryContract(30_000_000,80_000_000,50_000_000,2048), authority_root_hash72=authority)
    out = engine.recover_from_pass114(bundle["numeral"], available_work_units=80_000_000, available_memory_bytes=50_000_000, authority_root_hash72=authority)
    assert out["manifold"] == manifold


def test_pass115_service_registered_and_conformance_derived():
    from hhs_runtime.hhs_service_registry_v1 import make_default_service_registry
    registry = make_default_service_registry()
    service = next(x for x in registry.services() if x["name"] == "runtime.canonical_qudit_serialization.pass115")
    assert service["conformance_decision"]["derivation_complete"] is True
    assert "position_coordinate_bijection_required" in service["guards"]
    assert "pass114_palindromic_embedding_required" in service["guards"]

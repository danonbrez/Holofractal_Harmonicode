from fractions import Fraction as Q
from hhs_runtime.pass220_complex_phase_loshu_v1 import audit, SOURCE_GATE, TRANSFER_GATE

def test_complex_loshu_exact_residual():
    result=audit()
    assert result["sum"] == (Q(1),Q(-1,2))
    assert result["product"] == (Q(1,2),Q(-1,2))
    assert result["exhaust_residual"] == (Q(1,2),Q(0))
    assert result["sum"] != result["product"]
    assert not result["canonical_hash216_minted"]
    assert not result["signed_vm81_admitted"]
    assert not result["exhaust_ledger_committed"]

def test_source_gates_preserved():
    assert "45==" in SOURCE_GATE
    assert "/(x*y)" in SOURCE_GATE
    assert "y^2" in SOURCE_GATE
    assert TRANSFER_GATE == "1-(x/2)==c²-a/b"
    result=audit()
    assert len(result["lhs"]) == len(result["rhs"]) == 3
    assert all(len(row)==3 for row in result["lhs"])

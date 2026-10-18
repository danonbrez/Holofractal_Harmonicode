import pytest
from hhs_runtime.pass220_lane5_order5_loshu_nucleus_v1 import build_order5, hydrate_order5_in_loshu
def test_order5_65_horizon_central_placement():
    witness=hydrate_order5_in_loshu()
    assert witness["rows"]==(65,)*5
    assert witness["columns"]==(65,)*5
    assert witness["diagonals"]==(65,65)
    assert len(witness["vm81_cell_addresses"])==25
    assert witness["vm81_cell_addresses"][0]==20
    assert witness["vm81_cell_addresses"][-1]==60
    assert witness["existing_order_circuits"]==(2,3,4,6,8,9)
    assert not witness["genesis_rom_mutated"]
def test_altered_square_fails_closed():
    bad=[list(row) for row in build_order5()]
    bad[0][0],bad[0][1]=bad[0][1],bad[0][0]
    with pytest.raises(ValueError):
        hydrate_order5_in_loshu(bad)

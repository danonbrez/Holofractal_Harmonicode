import pytest
from hhs_runtime.pass220_lane5_h36_111_hydration_v1 import (
    hydrate_h36, hydrate_service, source_quadrants, HYDRATION_SERVICES, MAGIC, SWAPS,
)
def test_all_twelve_hydration_services_and_diagonals():
    witness=hydrate_h36()
    assert MAGIC==111
    assert len(HYDRATION_SERVICES)==12
    assert witness["hydration_service_count"]==12
    assert all(s["sum"]==111 and s["closed"] for s in witness["services"])
    assert witness["diagonal_witnesses"]==(111,111)
    assert tuple(tuple(v["ordered_exchange"]) for v in witness["swaps"])==SWAPS
    assert sorted(v for row in witness["completed"] for v in row)==list(range(1,37))
    assert not witness["canonical_hash216_minted"]
    for service in HYDRATION_SERVICES:
        assert hydrate_service(service)["sum"]==111

def test_reverse_three_swaps_exact():
    source=source_quadrants()
    assert hydrate_h36(source)["source"]==source

def test_fail_closed_mutation():
    source=[list(row) for row in source_quadrants()]
    source[0][0]=source[0][1]
    with pytest.raises(ValueError):
        hydrate_h36(source)
    with pytest.raises(ValueError):
        hydrate_h36(swaps=tuple(reversed(SWAPS)))
    with pytest.raises(ValueError):
        hydrate_service("H36_DIAGONAL_0")

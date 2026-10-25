import pytest
from hhs_runtime.pass220.lane5_nucleus_group_selection import select_group

def graph():
    return {i:(i,0,0) for i in range(10368)}

def test_nearest_deterministic():
    p=graph()
    p[0]=(0,0,0)
    p[1]=(1,0,0)
    p[2]=(-1,0,0)
    result=select_group(p,0,2,7)
    assert result["selected_ids"]==[0,1,2]
    assert result["squared_distances"]==[1,1]
    assert result["candidate_only"]
    assert not result["canonical_vm81_mutation_authority"]

def test_all_particles_and_empty_neighborhood():
    p=graph()
    assert select_group(p,99,0,2)["selected_ids"]==[99]
    ids=select_group(p,99,10367,2)["selected_ids"]
    assert len(ids)==len(set(ids))==10368

def test_toroidal_distance_is_spatial():
    p=graph()
    p[0]=(0,0,0)
    p[1]=(8,0,0)
    p[2]=(2,0,0)
    result=select_group(p,0,1,42,periods=(9,100000,100000))
    assert result["selected_ids"]==[0,1]
    assert result["squared_distances"]==[1]
    assert result["tick"]==42

@pytest.mark.parametrize("change", [
    {"neighbors":10368},{"neighbors":-1},{"nucleus":10368},
    {"tick":-1},{"neighbors":True},{"periods":(0,9,9)},
    {"periods":(9,9,9,9)},
])
def test_invalid_request(change):
    args={"coordinates":graph(),"nucleus":0,"neighbors":8,"tick":0}
    args.update(change)
    with pytest.raises(ValueError):
        select_group(**args)

def test_incomplete_or_float_snapshot():
    p=graph()
    del p[3]
    with pytest.raises(ValueError):
        select_group(p,0,8,0)
    p=graph()
    p[3]=(1.5,0,0)
    with pytest.raises(ValueError):
        select_group(p,0,8,0)

import pytest
from hhs_runtime.pass150 import Hash216Genome, Base20BigIntCodec, KeyEpoch

@pytest.mark.parametrize("case", range(54))
def test_positive_contract_matrix(case):
    data=f"positive-{case}".encode(); positions=Hash216Genome.positions(data,sequence=case)
    assert len(positions)==216 and Hash216Genome.root(positions)==Hash216Genome.root(tuple(positions))

@pytest.mark.parametrize("case", range(120))
def test_negative_contract_matrix(case):
    mode=case%4
    if mode==0:
        with pytest.raises(ValueError): Hash216Genome.root(("0"*64,)*215)
    elif mode==1:
        with pytest.raises(ValueError): Base20BigIntCodec.encode([19])
    elif mode==2:
        with pytest.raises(ValueError): KeyEpoch.genesis(b"short")
    else:
        with pytest.raises(TypeError): Hash216Genome.positions("not-bytes")

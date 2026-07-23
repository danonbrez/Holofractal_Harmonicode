import json, os, time
from pathlib import Path
import pytest
from hhs_runtime.pass150 import Hash216Genome, Hash216ImmuneSystem, KeyEpoch, Base20BigIntCodec

@pytest.fixture
def system(tmp_path):
    return Hash216ImmuneSystem(tmp_path, KeyEpoch.genesis(bytes(range(32))), max_spool_records=8)

def test_216_sha256_positions():
    p=Hash216Genome.positions(b"abc")
    assert len(p)==216 and len(set(p))==216 and all(len(x)==64 for x in p)

def test_root_deterministic_and_sensitive():
    assert Hash216Genome.root(Hash216Genome.positions(b"a"))==Hash216Genome.root(Hash216Genome.positions(b"a"))
    assert Hash216Genome.root(Hash216Genome.positions(b"a"))!=Hash216Genome.root(Hash216Genome.positions(b"b"))

def test_inspect_flush_validate_echo(system):
    r=system.inspect("UNWITNESSED_CALL","actor",{"x":1})
    e=system.echo_for_vm81(r)
    assert e["requires_vm81_validation"] and not e["mutation_authority"]
    assert system.flush()==1 and system.validate_chain()

def test_recovery_repairs_replica(system):
    system.inspect("X","a",{}); system.flush()
    system.replicas[0].write_text("corrupt\n")
    out=system.recover()
    assert out["repaired_replicas"]==1 and system.validate_chain()

def test_reversal_is_append_only(system):
    a=system.inspect("WRITE","actor",{"v":1}); system.flush()
    b=system.reverse(a.record_id,"auditor","compensate"); system.flush()
    assert b.reversal_of==a.record_id and len(system._majority_chain())==2

def test_key_rotation_dual_signed(system):
    old=system.key_epoch; new=system.rotate_key(bytes(reversed(range(32))))
    assert new.verify_transition(old)

def test_worker_flush(system):
    system.start_worker(0.01); system.inspect("SIGNAL","actor",{}); time.sleep(.05); system.stop_worker()
    assert system.validate_chain() and len(system._majority_chain())==1

def test_spool_bound(tmp_path):
    s=Hash216ImmuneSystem(tmp_path,KeyEpoch.genesis(bytes(range(32))),max_spool_records=1)
    s.inspect("A","a",{})
    with pytest.raises(BufferError): s.inspect("B","a",{})

@pytest.mark.parametrize("ops", [(),(0,),(18,),tuple(range(19)),(0,0,1,18)])
def test_base20_roundtrip(ops): assert Base20BigIntCodec.decode(Base20BigIntCodec.encode(ops))==ops

@pytest.mark.parametrize("bad", [-1,19,20,999])
def test_invalid_opcode(bad):
    with pytest.raises(ValueError): Base20BigIntCodec.encode([bad])

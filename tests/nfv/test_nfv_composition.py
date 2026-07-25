import pytest
from hhs_runtime.nfv.core import NFVError,NFVObject
from hhs_runtime.nfv.chunks import NFVChunk,AlgorithmChunk,compose_chunks
from hhs_runtime.nfv.branching import MergeWitness,fork_object,merge_branches
from hhs_runtime.nfv.graph import DependencyGraph,DependencyEdge
from hhs_runtime.nfv.module import NFVModule

def admit(_o,_s): return True

def test_chunk_identity_survives_relocation_and_cow_changes_generation():
    c=NFVChunk('STATE_VECTOR',{'v':3},1,4,'VM81',storage_slot='a')
    moved=c.relocate('b'); assert moved.chunk_index==c.chunk_index and moved.storage_slot=='b'
    revised=c.revise({'v':4},copy_on_write=True); assert revised.version==1 and revised.generation==1 and revised.chunk_index!=c.chunk_index

def test_chunk_rejects_float_and_capacity_overflow():
    with pytest.raises(NFVError,match='NFV_FLOAT_FORBIDDEN'): NFVChunk('STATE_VECTOR',{'v':1.2},1,2,'VM81')
    with pytest.raises(NFVError,match='NFV_INVALID_CHUNK_CAPACITY'): NFVChunk('STATE_VECTOR',{},3,2,'VM81')

def test_algorithm_readiness_and_nested_execution():
    root=NFVChunk('ALGORITHM_VECTOR',{'op':'inc'},1,1,'VM81')
    childc=NFVChunk('ALGORITHM_VECTOR',{'op':'double'},1,1,'VM81')
    child=AlgorithmChunk(childc,'double',(root.chunk_index,),('closed',),2,(),1,3)
    alg=AlgorithmChunk(root,'inc',(),('closed',),1,(child,),0,3)
    assert not alg.ready(resolved_dependencies=(),resolved_constraints=(),authority_root='VM81',available_steps=3)
    trace=alg.execute({'v':2},operation_registry={'inc':lambda s:{'v':s['v']+1},'double':lambda s:{'v':s['v']*2}},resolved_constraints=('closed',),authority_root='VM81',available_steps=3)
    assert trace.output=={'v':6} and trace.steps_used==3 and trace.execution_order==(root.chunk_index,childc.chunk_index)

def test_algorithm_resource_and_recursion_fail_closed():
    c=NFVChunk('ALGORITHM_VECTOR',{},1,1,'VM81')
    alg=AlgorithmChunk(c,'noop',maximum_steps=2)
    with pytest.raises(NFVError,match='NFV_ALGORITHM_NOT_READY'): alg.execute({},operation_registry={'noop':lambda s:s},authority_root='VM81',available_steps=1)
    with pytest.raises(NFVError,match='RESOURCE_BOUNDED'): AlgorithmChunk(c,'noop',recursion_depth=2,maximum_recursion_depth=1)

def test_parent_closure_rejects_locally_valid_chunks():
    a=NFVChunk('STATE_VECTOR',{'v':2},1,1,'VM81'); b=NFVChunk('STATE_VECTOR',{'v':3},1,1,'VM81')
    ok=compose_chunks((a,b),parent_projector=lambda cs:{'sum':sum(c.payload['v'] for c in cs)},parent_constraint=lambda p:p['sum']==5,authority_root='VM81',maximum_chunks=2)
    assert ok.parent_projection=={'sum':5}
    with pytest.raises(NFVError,match='NFV_PARENT_MANIFOLD_REJECTED'): compose_chunks((a,b),parent_projector=lambda cs:{'sum':sum(c.payload['v'] for c in cs)},parent_constraint=lambda p:p['sum']==4,authority_root='VM81',maximum_chunks=2)

def test_fork_distinct_identity_and_valid_merge():
    ancestor=NFVObject('STATE_VECTOR',{'v':1},('v>=0',),(),'VM81')
    left,right=fork_object(ancestor,('left','right'),vm81_admit=admit)
    assert left.object.object_index!=right.object.object_index and left.ancestor_index==right.ancestor_index==ancestor.object_index
    witness=MergeWitness(True,True,True,True,True,True,True,True)
    merged=merge_branches(ancestor,left,right,witness=witness,merge_state=lambda l,r:{'v':l['v']+r['v']},vm81_admit=admit)
    assert merged.object.state['v']==2 and merged.object.version==2

def test_merge_failure_preserves_branches_and_rejects_incomplete_witness():
    ancestor=NFVObject('STATE_VECTOR',{'v':1},(),(),'VM81'); left,right=fork_object(ancestor,('a','b'),vm81_admit=admit)
    before=(left.object,right.object)
    bad=MergeWitness(True,True,True,True,True,False,True,True)
    with pytest.raises(NFVError,match='NFV_MERGE_WITNESS_INCOMPLETE'): merge_branches(ancestor,left,right,witness=bad,merge_state=lambda l,r:l,vm81_admit=admit)
    assert (left.object,right.object)==before

def test_stale_ancestry_rejected():
    a=NFVObject('STATE_VECTOR',{'v':1},(),(),'VM81'); b=NFVObject('STATE_VECTOR',{'v':9},(),(),'VM81')
    left,right=fork_object(a,('a','b'),vm81_admit=admit); witness=MergeWitness(*([True]*8))
    with pytest.raises(NFVError,match='NFV_MERGE_ANCESTRY_CONFLICT'): merge_branches(b,left,right,witness=witness,merge_state=lambda l,r:l,vm81_admit=admit)

def test_module_encapsulation_preserves_closed_topology_and_becomes_object():
    a=NFVObject('STATE_VECTOR',{'v':1},(),(),'VM81'); b=NFVObject('STATE_VECTOR',{'v':2},(),(a.object_index,),'VM81')
    g=DependencyGraph(); g.add_node(a.object_index,a.to_dict()); g.add_node(b.object_index,b.to_dict()); g.add_edge(DependencyEdge(a.object_index,b.object_index,'VALUE_DEPENDS_ON'))
    m=NFVModule('pair',(a,b),g,('INVOKE',),('STATE_VECTOR',),('STATE_VECTOR',),(),('VM81',),{'max_steps':10},'EXACT_RECONSTRUCTION','SER','MOD','PRESERVE','LOSHU5')
    obj=m.as_object(); assert obj.object_type=='NFV_MODULE' and obj.state['module_index']==m.module_index and g.to_dict()==m.identity_payload()['graph']

def test_module_rejects_external_graph_node_and_missing_authority():
    a=NFVObject('STATE_VECTOR',{'v':1},(),(),'VM81'); g=DependencyGraph(); g.add_node(a.object_index,{}); g.add_node('external',{})
    args=('bad',(a,),g,('INVOKE',),(),(),(),('VM81',),{'max':1},'EXACT','SER','MOD','PRESERVE','LOSHU5')
    with pytest.raises(NFVError,match='NFV_MODULE_GRAPH_CLOSURE_FAILURE'): NFVModule(*args)
    g2=DependencyGraph(); g2.add_node(a.object_index,{})
    with pytest.raises(NFVError,match='NFV_MODULE_AUTHORITY_REQUIREMENT_MISSING'): NFVModule('bad',(a,),g2,('INVOKE',),(),(),(),(),{'max':1},'EXACT','SER','MOD','PRESERVE','LOSHU5')

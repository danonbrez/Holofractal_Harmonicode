import pytest
from hhs_runtime.nfv.audio import ExactScalar
from hhs_runtime.nfv.core import LocalizedModulus,NFVError,NFVObject,hash216
from hhs_runtime.nfv.interaction import *
def sample(receipt='R72'):
    return InteractionSample(ExactScalar(2),(ExactScalar(1),ExactScalar(0),ExactScalar(-1)),ExactScalar(3),ExactScalar(1,4),(ExactScalar(0),ExactScalar(1),ExactScalar(0)),(ExactScalar(1),ExactScalar(1),ExactScalar(1)),ExactScalar(5),4,0,LocalizedModulus.normalize(17,9),5,hash216({'graph':1}),receipt)
def test_receipt_bundle_requires_equality():
    with pytest.raises(NFVError,match='NFV_INTERACTION_RECEIPT_MISMATCH'): InteractionReceiptBundle('A','B','A')
def test_shader_projection_is_non_authoritative_and_bound():
    s=sample(); p=project_shader_gradient(s); assert p.authoritative is False and p.source_sample_index==s.sample_index and p.source_receipt==s.source_receipt
def test_collision_force_localizes_without_loss():
    s=sample(); c=project_collision_force(s,alpha=ExactScalar(2),beta=ExactScalar(1),gamma=ExactScalar(1),contact_force=(ExactScalar(1),ExactScalar(1),ExactScalar(1)),modulus=9)
    assert [x.exact for x in c.components]==[ExactScalar(-2),ExactScalar(-1),ExactScalar(2)]
    assert all(x.localized.exact==x.exact.fraction for x in c.components)
def test_collision_admission_atomic_preflight():
    a=NFVObject('STATE_VECTOR',{'p':0},(),(),'VM81'); b=NFVObject('STATE_VECTOR',{'p':1},(),(),'VM81'); c=project_collision_force(sample(),alpha=ExactScalar(1),beta=ExactScalar(1),gamma=ExactScalar(1),contact_force=(0,0,0),modulus=9); receipts=InteractionReceiptBundle('R72','R72','R72')
    before=(a,b)
    with pytest.raises(NFVError,match='NFV_VM81_COLLISION_REJECTED'): admit_collision_pair(a,b,{'p':2},{'p':3},candidate=c,receipts=receipts,vm81_admit=lambda o,s:o is a)
    assert (a,b)==before
    result=admit_collision_pair(a,b,{'p':2},{'p':3},candidate=c,receipts=receipts,vm81_admit=lambda o,s:True)
    assert result.object_a.state['_nfv_interaction_receipt']=='R72' and result.object_b.state['_nfv_interaction_receipt']=='R72'
def test_graph_edges_project_exact_kernel_without_authority():
    edges=(GraphConvolutionEdge('a','x',ExactScalar(1,2),1,'R72'),GraphConvolutionEdge('b','x',ExactScalar(1,3),1,'R72'))
    p=project_graph_edges_to_kernel(edges,lane_id='x',source_receipt='R72',maximum_delay=2)
    assert p.authoritative is False and p.kernel.coefficients[1]==ExactScalar(5,6) and len(p.edge_indices)==2
def test_graph_projection_bounds_and_receipts():
    e=GraphConvolutionEdge('a','x',ExactScalar(1),4,'R72')
    with pytest.raises(NFVError,match='RESOURCE_BOUNDED'): project_graph_edges_to_kernel((e,),lane_id='x',source_receipt='R72',maximum_delay=2)
    with pytest.raises(NFVError,match='NFV_INTERACTION_RECEIPT_MISMATCH'): project_graph_edges_to_kernel((e,),lane_id='x',source_receipt='OTHER',maximum_delay=4)

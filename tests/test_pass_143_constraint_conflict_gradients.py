import copy, pytest
from hhs_runtime.harmonicode_constraint_conflict_gradient_simulation_v1 import ConstraintConflictSimulator, ConflictSimulationError

def request():
 return {"request_id":"p143","dimensions":["x","y"],"initial_state":{"x":"4","y":"-3"},"iterations":8,"parallel_branches":4,"step":"1/3",
 "constraints":[
  {"id":"sum","coefficients":{"x":1,"y":1},"target":1,"priority":3,"temperature":2,"children":["x_anchor"]},
  {"id":"difference","coefficients":{"x":1,"y":-1},"target":0,"priority":2,"temperature":3},
  {"id":"x_anchor","coefficients":{"x":1},"target":"1/2","priority":1,"temperature":5}]}

def test_smooths_and_is_orthogonal():
 r=ConstraintConflictSimulator().execute(request())
 assert r['smoothed_or_equal'] and r['orthogonality_closed']
 assert r['simulation_projections']['authority']=='SIMULATION_PROJECTION_ONLY'

def test_deterministic():
 rt=ConstraintConflictSimulator(); assert rt.execute(request())==rt.execute(request())

def test_receipt_mutation_detected():
 rt=ConstraintConflictSimulator(); r=rt.execute(request()); r['final_state']['x']='999'
 assert not rt.validate_receipt(r)['valid']

def test_float_rejected():
 q=request(); q['initial_state']['x']=1.5
 with pytest.raises(ConflictSimulationError,match='NO_FLOAT'): ConstraintConflictSimulator().execute(q)

def test_cycle_rejected():
 q=request(); q['constraints'][2]['children']=['sum']
 with pytest.raises(ConflictSimulationError,match='CYCLE'): ConstraintConflictSimulator().execute(q)

def test_unknown_nested_rejected():
 q=request(); q['constraints'][0]['children']=['missing']
 with pytest.raises(ConflictSimulationError,match='UNKNOWN'): ConstraintConflictSimulator().execute(q)

def test_invalid_temperature_rejected():
 q=request(); q['constraints'][0]['temperature']=0
 with pytest.raises(ConflictSimulationError,match='TEMPERATURE'): ConstraintConflictSimulator().execute(q)

def test_parallel_trace_shape():
 r=ConstraintConflictSimulator().execute(request())
 assert len(r['trace'])==8 and all(len(x['branch_constraints'])==4 for x in r['trace'])

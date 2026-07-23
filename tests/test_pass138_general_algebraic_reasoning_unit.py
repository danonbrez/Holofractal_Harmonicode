import copy, json, pytest
from hhs_runtime.harmonicode_general_algebraic_reasoning_unit_v1 import execute_request, GeneralAlgebraicReasoningUnit, ReasoningError

def request():
 return {"request_id":"gfe-5-4","agent":"test-agent","assignments":{"g":"5/4","h":"4/5","rho":"1/20","xy":1},"constraints":[{"id":"inverse","lhs":"g*h","rhs":"xy"},{"id":"residual","lhs":"rho","rhs":"g+h-2*xy"}],"goals":[{"id":"poly","lhs":"rho*g","rhs":"(g-xy)**2"}]}

def test_proved_and_looking_glass_closed():
 r=execute_request(request()); assert r['conclusion']=='PROVED'; assert r['looking_glass']['closed']; assert GeneralAlgebraicReasoningUnit().validate_receipt(r)['valid']

def test_constraint_failure_blocks_goal():
 p=request(); p['assignments']['h']='3/4'; r=execute_request(p); assert r['conclusion']=='CONSTRAINT_REJECTED'; assert r['goals']==[]

def test_goal_failure_is_not_promoted():
 p=request(); p['goals'][0]['rhs']='0'; r=execute_request(p); assert r['conclusion']=='GOAL_NOT_PROVED'

def test_float_rejected():
 p=request(); p['assignments']['g']=1.25
 with pytest.raises(ReasoningError,match='FLOAT_OR_BOOL_REJECTED'): execute_request(p)

def test_unbound_symbol_rejected():
 p=request(); p['goals'][0]['rhs']='unknown'
 with pytest.raises(ReasoningError,match='UNBOUND_SYMBOL'): execute_request(p)

def test_receipt_tamper_detected():
 r=execute_request(request()); r['conclusion']='PROVED_BY_ASSERTION'; assert not GeneralAlgebraicReasoningUnit().validate_receipt(r)['valid']

def test_deterministic(): assert execute_request(request())==execute_request(request())

def test_noninteger_power_rejected():
 p=request(); p['goals']=[{'id':'bad','lhs':'g**(1/2)','rhs':'1'}]
 with pytest.raises(ReasoningError,match='NONINTEGER_POWER'): execute_request(p)

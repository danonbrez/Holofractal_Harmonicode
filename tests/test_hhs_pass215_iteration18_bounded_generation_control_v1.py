from pathlib import Path
import pytest
from hhs_backend.runtime import hhs_pass215_iteration18_bounded_generation_control_v2 as i18


def test_iteration17_closure_inherited():
    assert i18.ITERATION17_CLOSURE_HEAD == '3d46b0eb233c6f450fa7d939e8b864a6651d3465'
    assert i18.ITERATION17_CLOSURE_TREE == '687db9f718d2b54c3962ecc8bbb62f49090407c9'
    assert i18.ITERATION17_CLOSURE_ARTIFACT_SHA256 == 'e8046bf49d280032a1f15f722de973d267b77e7f0d5e64338997e0a84a21a5af'


def test_frozen_iteration17_chain_has_seven_tokens():
    assert i18.ITERATION17_SELECTED_TOKEN_IDS == (450,6575,471,528,2827,322,278)
    assert i18.ITERATION17_SELECTED_TOKENS == ('▁The','▁sun','▁was','▁sh','ining','▁and','▁the')
    assert len(i18.ITERATION17_STEP_ROOTS) == 7


def test_policy_is_bounded_and_no_sampling():
    p=i18.v1._policy(); assert p['max_new_tokens']==7; assert p['max_context_tokens']==11
    assert p['stop_token_ids']==[2]; assert p['sampling_authorized'] is False
    assert p['unbounded_generation_authorized'] is False


def test_policy_rejects_larger_generation_bound():
    with pytest.raises(i18.Pass215Iteration18ValidationError,match='MAX_NEW_TOKENS_OUTSIDE_CONTRACT'):
        i18.v1._policy(max_new_tokens=8)


def test_policy_rejects_alternate_stop_tokens():
    with pytest.raises(i18.Pass215Iteration18ValidationError,match='STOP_TOKEN_POLICY_OUTSIDE_CONTRACT'):
        i18.v1._policy(stop_token_ids=(1,))


def test_termination_stop_token_precedes_other_bounds():
    assert i18.evaluate_termination(2,7,i18.v1._policy()) == i18.TERMINATION_STOP_TOKEN


def test_termination_max_new_tokens():
    assert i18.evaluate_termination(278,7,i18.v1._policy()) == i18.TERMINATION_MAX_NEW_TOKENS


def test_termination_continues_before_bound():
    assert i18.evaluate_termination(450,1,i18.v1._policy()) == i18.TERMINATION_CONTINUE


def test_float_rejected_recursively():
    with pytest.raises(i18.Pass215Iteration18ValidationError,match='FLOAT_FORBIDDEN'):
        i18.v1._reject_floats({'checkpoint':{'bad':[1,2.0]}})


def test_checkpoint_split_is_inside_bound():
    assert 0 < i18.RESUME_AFTER_STEPS < i18.MAX_NEW_TOKENS
    assert i18.PREFIX_SEQUENCE_LENGTH + i18.RESUME_AFTER_STEPS == 8


def test_repaired_restore_uses_full_terminal_head_dag_capabilities():
    dag=i18.v1.i17.i15.i13.TerminalHeadSymbolicDAG()
    assert all(hasattr(dag,name) for name in ('powq','sin','cos','intern'))
    assert dag.__class__.__name__ == 'TerminalHeadSymbolicDAG'


def test_checkpoint_roundtrip_is_json_durable_and_float_free():
    payload={'schema':'x','values':[1,2,3],'nested':{'root':'abc'}}
    out=i18._durable_json_roundtrip(payload)
    assert out==payload
    with pytest.raises(i18.Pass215Iteration18ValidationError,match='FLOAT_FORBIDDEN'):
        i18._durable_json_roundtrip({'bad':1.5})


def test_runtime_contains_zero_forward_replay_restore_contract():
    text=Path('hhs_backend/runtime/hhs_pass215_iteration18_bounded_generation_control_v2.py').read_text()
    assert 'TerminalHeadSymbolicDAG' in text
    assert 'checkpoint_durable_json_roundtrip' in text
    assert 'v1.restore_generation_session = restore_generation_session' in text


def test_contract_preserves_forbidden_authorities():
    import json
    c=json.loads(Path('contracts/pass215/PASS_215_ITERATION_18_CONTRACT.json').read_text())
    assert c['requirements']['restore_without_prefix_or_generated_forward_replay'] is True
    assert c['constraints']['probabilistic_sampling_executed'] is False
    assert c['constraints']['unbounded_or_general_generation_claimed'] is False
    assert c['constraints']['canonical_float_interpretation_performed'] is False

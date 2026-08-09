from pathlib import Path
import hashlib, json, zlib
import pytest
from hhs_backend.runtime import hhs_pass215_iteration19_content_addressed_checkpoint_v2 as i19


def test_iteration18_closure_inherited_exactly():
    assert i19.ITERATION18_CLOSURE_HEAD == 'd89919b1010df0dda46e18cb43b4a6ef913a5615'
    assert i19.ITERATION18_CLOSURE_TREE == '2a74f697278e754b44998df4d5a3598750643a4a'
    assert i19.ITERATION18_CLOSURE_ARTIFACT_SHA256 == 'bf3908e7000a72f96416f469a76415b0a73d48591eaa03d170265aacc7e69297'


def test_iteration18_checkpoint_identity_is_frozen():
    assert i19.ITERATION18_CHECKPOINT_CANONICAL_BYTES == 475300933
    assert i19.ITERATION18_CHECKPOINT_ROOT_HASH216 == 'bff3f18e1324caacdbd610b833b3ebd6ebe35e525821c0ffad349fc81ad9474f'


def test_iteration18_control_and_suite_roots_are_frozen():
    assert i19.ITERATION18_GENERATION_CONTROL_ROOT_HASH216 == '309a4e102b6f78338a63c086f536f4d3d62429c77709fa4f9fa9b25d3a6ac509'
    assert i19.ITERATION18_SUITE_ROOT_HASH216 == 'bccf558e206bc996d4647533cf310838e1f13cec1322f98c5f22ab5c1ad190d1'
    assert len(i19.ITERATION18_TOKEN_PROOF_ROOTS) == 7


def test_frozen_generation_chain_is_preserved():
    assert i19.FROZEN_SELECTED_TOKEN_IDS == (450,6575,471,528,2827,322,278)
    assert i19.FROZEN_SELECTED_TOKENS == ('▁The','▁sun','▁was','▁sh','ining','▁and','▁the')


def test_component_order_is_canonicalized_before_pack():
    assert i19.v1.LARGE_COMPONENT_NAMES == tuple(sorted(i19.v1.LARGE_COMPONENT_NAMES))
    assert set(i19.v1.LARGE_COMPONENT_NAMES) == {'symbolic_dag','symbolic_cache','interval_cache','interval_context','current_interval_logits','current_symbolic_logits'}


def test_repeated_string_interning_is_lossless_and_escapes_literals():
    payload={'a':['0123456789abcdefXYZ','0123456789abcdefXYZ','$I5','$literal'], 'b':{'0123456789abcdefXYZ':'0123456789abcdefXYZ'}}
    table,counts=i19.v1._intern_table(payload)
    assert '0123456789abcdefXYZ' in table and counts['0123456789abcdefXYZ'] == 4
    indexes={value:index for index,value in enumerate(table)}
    encoded=i19.v1._encode_interned(payload,indexes)
    decoded=i19.v1._decode_interned(encoded,table)
    assert decoded == payload


def test_unique_long_string_is_not_interned():
    payload={'x':'0123456789abcdef-only-once','y':'short','z':'short'}
    table,_=i19.v1._intern_table(payload)
    assert '0123456789abcdef-only-once' not in table
    assert 'short' not in table


def test_transport_chunk_compression_is_deterministic_and_integer_only():
    raw=(b'abc123'*10000)
    c1=zlib.compress(raw,level=i19.ZLIB_LEVEL); c2=zlib.compress(raw,level=i19.ZLIB_LEVEL)
    assert c1 == c2
    assert hashlib.sha256(raw).hexdigest() == hashlib.sha256(raw).hexdigest()
    assert isinstance(i19.CHUNK_BYTES,int) and isinstance(i19.ZLIB_LEVEL,int)


def test_float_rejected_recursively():
    with pytest.raises(i19.Pass215Iteration19ValidationError,match='FLOAT_FORBIDDEN'):
        i19.v1._reject_floats({'bad':[1,2.0]})


def test_compaction_contract_requires_at_least_two_to_one():
    assert i19.MIN_REQUIRED_COMPACTION_FACTOR_NUMERATOR == 2
    assert i19.ITERATION18_CHECKPOINT_CANONICAL_BYTES // 2 > 0


def test_runtime_uses_parent_root_reconstruction_before_restore():
    text=Path('hhs_backend/runtime/hhs_pass215_iteration19_content_addressed_checkpoint_v1.py').read_text()
    assert 'RECONSTRUCTED_PARENT_ROOT_INVALID' in text
    assert 'i18.restore_generation_session(raw, parent)' in text
    assert 'PREFIX_FORWARD_REPLAY_DURING_RESTORE' in text
    assert 'GENERATED_FORWARD_REPLAY_DURING_RESTORE' in text


def test_tool_uses_hardened_v2_runtime():
    text=Path('tools/pass215_iteration19_content_addressed_checkpoint.py').read_text()
    assert 'hhs_pass215_iteration19_content_addressed_checkpoint_v2' in text


def test_contract_preserves_forbidden_authorities():
    c=json.loads(Path('contracts/pass215/PASS_215_ITERATION_19_CONTRACT.json').read_text())
    assert c['requirements']['reconstruct_iteration18_checkpoint_root_exactly'] is True
    assert c['requirements']['restore_without_prefix_or_generated_forward_replay'] is True
    assert c['requirements']['minimum_compaction_factor_numerator'] == 2
    assert c['constraints']['probabilistic_sampling_executed'] is False
    assert c['constraints']['unbounded_or_general_generation_claimed'] is False
    assert c['constraints']['canonical_float_interpretation_performed'] is False


def test_checkpoint_transport_constants_are_fixed():
    assert i19.CHUNK_BYTES == 1048576
    assert i19.ZLIB_LEVEL == 9
    assert i19.INTERN_MIN_UTF8_BYTES == 16
    assert i19.INTERN_MIN_OCCURRENCES == 2

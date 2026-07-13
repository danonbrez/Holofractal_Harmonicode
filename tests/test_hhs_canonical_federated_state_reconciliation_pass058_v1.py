from hhs_backend.runtime.hhs_canonical_federated_state_reconciliation_v1 import run_canonical_federated_state_reconciliation, canonical_federated_state_reconciliation_self_test, merge_federated_states, validate_canonical_merge

def test_conflict_preserving_merge_and_canonical_continuation():
    r=run_canonical_federated_state_reconciliation()
    assert r['ok']
    assert r['conflict_set']['conflict_count']==1
    assert r['conflict_set']['conflicts_preserved'] is True
    assert r['merge_candidate']['silent_overwrite_performed'] is False
    assert r['merge_candidate']['remote_clock_used_as_precedence'] is False
    assert r['merge_decision']['canonical_continuation'] is True
    assert r['merge_decision']['reconciliation_result_confers_retroactive_authority'] is False

def test_broken_ancestry_and_unresolved_conflict_fail_closed():
    s=canonical_federated_state_reconciliation_self_test()
    assert s['ok']
    assert 'REJECT_FEDERATED_MERGE_WITHOUT_COMMON_ANCESTOR' in s['negative_cases']['broken_ancestor']['reasons']
    assert 'REJECT_MERGED_STATE_WITHOUT_LOCAL_REVALIDATION' in s['negative_cases']['unresolved_without_revalidation']['reasons']
    assert 'REJECT_CONFLICT_FREE_CLAIM_WITH_UNRESOLVED_CONFLICTS' in s['negative_cases']['unresolved_without_revalidation']['reasons']

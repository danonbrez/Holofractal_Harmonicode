import pytest

from hhs_runtime.hhs_control_flow_transition_audit_v1 import (
    ADMIT_CONTROL_FLOW_TRANSITION_AUDIT,
    REJECT_CONTROL_FLOW_FLOAT_STATE,
    REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY,
    control_flow_transition_audit_self_test,
    make_control_flow_transition_audit,
    validate_control_flow_transition_audit,
)


def _assert_hash72(value):
    assert isinstance(value, str)
    assert len(value) == 72


def test_control_flow_transition_audit_commits_rich_state():
    audit = make_control_flow_transition_audit(
        gate="IF",
        label="RICH_BRANCH",
        transition_index=0,
        pre_state={"condition": True, "available": ["THEN", "ELSE"]},
        post_state={"result": {"nested": {"value": 5}}},
        result={"nested": {"value": 5}},
        decision="THEN_SELECTED",
        condition=True,
    )
    assert audit["ok"] is True
    assert audit["status"] == ADMIT_CONTROL_FLOW_TRANSITION_AUDIT
    fields = audit["canonical_transition_fields"]
    assert fields["rich_transition_audited"] is True
    assert fields["scalar_proxy_used"] is False
    _assert_hash72(fields["pre_state_hash72"])
    _assert_hash72(fields["post_state_hash72"])
    _assert_hash72(fields["transition_root_hash72"])
    assert audit["residue_chain"]["validation"]["ok"] is True


def test_control_flow_transition_audit_rejects_scalar_proxy_only():
    audit = make_control_flow_transition_audit(
        gate="LOOP",
        label="NO_PROXY",
        transition_index=1,
        pre_state={"n": 2},
        post_state={"n": 1},
        result={"n": 1},
        decision="STEP",
        condition=True,
        variant={"current": "2", "next": "1"},
    )
    bad = dict(audit)
    bad["canonical_transition_fields"] = dict(audit["canonical_transition_fields"])
    bad["canonical_transition_fields"]["scalar_proxy_used"] = True
    assert validate_control_flow_transition_audit(bad)["status"] == REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY


def test_control_flow_transition_audit_rejects_float_state():
    with pytest.raises(ValueError):
        make_control_flow_transition_audit(
            gate="IF",
            label="FLOAT_REJECT",
            transition_index=0,
            pre_state={"x": 1.001},
            post_state={"x": 1},
            result={"x": 1},
            decision="THEN_SELECTED",
        )
    assert validate_control_flow_transition_audit({"canonical_transition_fields": {"x": 1.001}})["status"] == REJECT_CONTROL_FLOW_FLOAT_STATE


def test_control_flow_transition_audit_self_test_passes():
    result = control_flow_transition_audit_self_test()
    assert result["ok"] is True
    assert result["valid_status"] == ADMIT_CONTROL_FLOW_TRANSITION_AUDIT
    assert result["scalar_proxy_rejection_status"] == REJECT_CONTROL_FLOW_SCALAR_PROXY_ONLY

from hhs_control_flow_gates_v1 import HHSControlFlowGatesV1


def test_audited_if_uses_full_transition_audit_for_rich_result():
    gates = HHSControlFlowGatesV1()
    result = gates.audited_if(
        condition=True,
        then_fn=lambda: {"branch": "then", "state": {"value": 7}},
        else_fn=lambda: {"branch": "else"},
        label="PASS041_IF",
    )
    assert result.ok is True
    audit = result.witness["transition_audit"]
    assert audit["status"] == "ADMIT_CONTROL_FLOW_TRANSITION_AUDIT"
    assert audit["canonical_transition_fields"]["rich_transition_audited"] is True
    assert audit["canonical_transition_fields"]["scalar_proxy_used"] is False


def test_audited_loop_uses_full_transition_audit_for_each_step():
    gates = HHSControlFlowGatesV1()
    result = gates.audited_loop(
        initial_state={"n": 3},
        condition_fn=lambda state: state["n"] > 0,
        step_fn=lambda state: {"n": state["n"] - 1},
        variant_fn=lambda state: state["n"],
        max_steps=5,
        label="PASS041_LOOP",
    )
    assert result.ok is True
    assert result.terminated is True
    assert result.quarantine is False
    assert result.iterations == 3
    first = result.witness["path"][0]["transition_audit"]
    assert first["status"] == "ADMIT_CONTROL_FLOW_TRANSITION_AUDIT"
    assert first["canonical_transition_fields"]["rich_transition_audited"] is True
    assert first["canonical_transition_fields"]["scalar_proxy_used"] is False

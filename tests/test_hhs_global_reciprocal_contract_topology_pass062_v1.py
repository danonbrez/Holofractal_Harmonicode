from hhs_backend.runtime.hhs_global_reciprocal_contract_topology_v1 import (
    global_reciprocal_contract_topology_self_test,
    run_global_reciprocal_contract_topology,
)


def test_pass062_self_test():
    assert global_reciprocal_contract_topology_self_test()["ok"]


def test_pass062_expansion_contraction_closure():
    result = run_global_reciprocal_contract_topology()
    assert result["ok"]
    assert result["global_topology"]["local_identities_preserved"]
    assert result["contraction"]["left_inverse_verified"]
    assert result["validation"]["authority_non_amplifying"]
    assert result["validation"]["rejection_non_amplifying"]


def test_pass062_xyzw_typed_equality_semantics():
    result = run_global_reciprocal_contract_topology()
    algebra = result["xyzw_algebra_contracts"][0]
    relations = algebra["relations"]
    expressions = {item.get("expression") for item in relations if item.get("expression")}
    assert algebra["internal_contradiction_detected"] is False
    assert algebra["external_untyped_equality_assumption_allowed"] is False
    assert algebra["contradiction_boundary"] == "ONLY_IF_EQUALITY_FRAMES_ARE_ERASED"
    assert "xy = -yx" in expressions
    assert "x = 1/y" in expressions
    assert "y = -x" in expressions
    assert "xyXY = xyzw = 1" in expressions
    assert "x + y - z - w = 0" in expressions
    assert {"IDENTITY_EQ", "RELATIONAL_EQ", "PHASE_EQ", "NORMALIZED_EQ", "ALIAS_EQ", "CLOSURE_EQ"} <= set(algebra["equality_frames"])
    assert algebra["transport_constant"]["floating_point_used"] is False


def test_pass062_distinct_states_survive_alias_and_normalization():
    result = run_global_reciprocal_contract_topology()
    algebra = result["xyzw_algebra_contracts"][0]
    distinct = [r for r in algebra["relations"] if r["relation"] == "DISTINCT"]
    aliases = [r for r in algebra["relations"] if r["relation"] == "ALIAS"]
    normalized = [r for r in algebra["relations"] if r["relation"] == "NORMALIZED_UNIT"]
    assert any(r["members"] == ["x", "y", "0", "1"] for r in distinct)
    assert any(r["members"] == ["X", "xy", "z"] for r in aliases)
    assert any(r["members"] == ["Y", "yx", "w"] for r in aliases)
    assert {r["lhs"] for r in normalized} == {"xy", "yx"}

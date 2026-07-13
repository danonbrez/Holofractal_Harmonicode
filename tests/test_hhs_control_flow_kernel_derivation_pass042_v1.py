from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map


def test_control_flow_gates_are_kernel_derived():
    surface_map = build_surface_map()
    gates = [s for s in surface_map["surfaces"] if s["surface_type"] == "CONTROL_FLOW_GATE"]
    assert {g["surface_id"] for g in gates} == {"control_flow_gate:audited_if", "control_flow_gate:audited_loop"}
    for gate in gates:
        assert gate["derivation_complete"] is True
        assert "HHS-I003" in gate["invariant_ids"]
        assert gate["witness_schemas"]

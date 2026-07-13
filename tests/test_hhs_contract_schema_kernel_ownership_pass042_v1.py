from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map


def test_every_executable_surface_has_contract_and_witness_binding():
    surface_map = build_surface_map()
    for surface in surface_map["surfaces"]:
        assert surface["contract_schemas"]
        assert surface["witness_schemas"]
        assert surface["validators"]
        assert surface["rejection_codes"]

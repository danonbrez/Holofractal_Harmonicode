from hhs_runtime.hhs_kernel_conformance_surface_map_v1 import build_surface_map


def test_conformance_map_uses_bounded_summary_mode():
    surface_map = build_surface_map()
    assert surface_map["bounded_summary_mode"] == "compact_roots_not_full_recompute"
    assert surface_map["validation"]["underived_surface_count"] == 0

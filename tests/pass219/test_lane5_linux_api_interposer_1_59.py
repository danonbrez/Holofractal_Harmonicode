from __future__ import annotations

from hhs_runtime.pass219.lane5_linux_api_interposer_1_59 import (
    NATIVE_GATEWAY,
    interpose_linux_api_request,
)


def test_linux_api_request_is_redirected_through_lane5() -> None:
    receipt = interpose_linux_api_request(
        operation_id="test.runtime.operation",
        surface="authorized_execution.call",
        payload={"kind": "opaque", "ieee_bits": "7fc00001"},
    )
    assert receipt["redirected"] is True
    assert receipt["propagation_allowed"] is True
    assert receipt["native_gateway"] == NATIVE_GATEWAY
    assert receipt["lane5_bios_required"] is True
    assert receipt["rna_cpp_cell_wall_required"] is True
    assert receipt["pqc_environmental_firewall_required"] is True
    assert receipt["four_lane_hydration_required"] is True
    assert receipt["constraint_forced_execution"] is True
    assert receipt["policy_choice_authority"] is False
    assert receipt["hash216_validated_scoped_reuse_only"] is True
    assert receipt["hash216_cache_is_commit_authority"] is False
    assert receipt["floating_point_canonical_authority"] is False
    assert len(receipt["interposition_token_digest72"]) == 72

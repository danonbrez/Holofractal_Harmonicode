from __future__ import annotations

from pathlib import Path

import pytest

from hhs_runtime.hhs_zero_bypass_runtime_interposer_v1 import PROPAGATION_SURFACES
from hhs_runtime.pass219.lane5_universal_abi_kernel_interceptor import (
    ADMIT_DOWNSTREAM,
    BLOCK_DIRECT,
    Lane5UniversalTrafficError,
    TRAFFIC_CLASSES,
    TRAFFIC_LINUX_KERNEL_ABI,
    TRAFFIC_RUNTIME_ABI,
    authorize_downstream_dispatch,
    direct_dispatch_rejection,
    intercept_abi_traffic,
)


def test_all_universal_traffic_classes_are_pass036_surfaces() -> None:
    assert set(TRAFFIC_CLASSES).issubset(PROPAGATION_SURFACES)


def test_read_only_runtime_abi_is_still_lane5_intercepted() -> None:
    record = intercept_abi_traffic(
        traffic_class=TRAFFIC_RUNTIME_ABI,
        operation="status",
        payload={"schema": "TEST_STATUS_V1"},
        read_only=True,
    )
    envelope = record["envelope"]
    assert envelope["read_only"] is True
    assert envelope["state_affecting"] is False
    assert envelope["zero_bypass_interposed"] is True
    assert envelope["redirected_through_lane5"] is True
    assert envelope["mandatory_optimization_dispatch"] is True
    assert envelope["mandatory_capability_count"] > 0
    decision = authorize_downstream_dispatch(record)
    assert decision["decision"] == ADMIT_DOWNSTREAM
    assert decision["canonical_mutation_allowed"] is False
    assert decision["pqc_required"] is False


def test_state_affecting_linux_traffic_is_blocked_before_mediation() -> None:
    record = intercept_abi_traffic(
        traffic_class=TRAFFIC_LINUX_KERNEL_ABI,
        operation="write",
        payload={"path": "/tmp/example"},
        read_only=False,
    )
    envelope = record["envelope"]
    assert envelope["direct_dispatch_action"] == BLOCK_DIRECT
    assert envelope["rna_cpp_cell_wall_required"] is True
    assert envelope["signed_environmental_pqc_required"] is True
    assert envelope["linux_host_result_is_external_evidence"] is True

    with pytest.raises(
        Lane5UniversalTrafficError,
        match="MISSING_MEDIATION",
    ):
        authorize_downstream_dispatch(record)


def test_state_affecting_dispatch_requires_both_lane5_and_signed_pqc() -> None:
    record = intercept_abi_traffic(
        traffic_class=TRAFFIC_RUNTIME_ABI,
        operation="canonical_commit",
        read_only=False,
    )
    lane5 = {
        "lane5_mediation_verified": True,
        "mandatory_optimization_dispatch": True,
        "rna_cpp_cell_wall_routed": True,
        "candidate_only": True,
    }
    with pytest.raises(
        Lane5UniversalTrafficError,
        match="MISSING_SIGNED_PQC",
    ):
        authorize_downstream_dispatch(record, lane5_receipt=lane5)

    pqc = {
        "signed_environmental_admission": True,
        "pqc_authenticated": True,
        "decision": "ADMIT",
        "singleton_vm81_authority": True,
    }
    decision = authorize_downstream_dispatch(
        record,
        lane5_receipt=lane5,
        pqc_receipt=pqc,
    )
    assert decision["decision"] == ADMIT_DOWNSTREAM
    assert decision["canonical_mutation_allowed"] is True
    assert decision["pqc_required"] is True


def test_direct_dispatch_record_forces_lane5_redirect() -> None:
    result = direct_dispatch_rejection(
        traffic_class=TRAFFIC_RUNTIME_ABI,
        operation="legacy_vmrc_execute",
    )
    assert result["pqc_boundary_action"] == BLOCK_DIRECT
    assert result["redirect_action"] == "LANE5_REMEDIATION_REQUIRED"
    assert result["direct_fallback_allowed"] is False
    assert result["canonical_mutation_allowed"] is False

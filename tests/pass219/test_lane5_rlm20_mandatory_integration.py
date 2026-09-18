from __future__ import annotations

from pathlib import Path

from hhs_runtime.pass219.lane5_mandatory_optimization_dispatcher import (
    MANDATORY_CAPABILITY_ROLES,
    MANDATORY_LANE5_LINEAGE,
    Pass219Lane5LatencyCompositionAgent,
    RLM20_CLOSURE_CAPABILITY_ID,
)

ROOT = Path(__file__).resolve().parents[2]


def test_rlm20_closure_is_mandatory_agent_capability(tmp_path: Path) -> None:
    assert RLM20_CLOSURE_CAPABILITY_ID in MANDATORY_LANE5_LINEAGE
    assert MANDATORY_CAPABILITY_ROLES[RLM20_CLOSURE_CAPABILITY_ID] == (
        "MANDATORY_CANONICAL_ADMISSION_MEDIATION"
    )
    with Pass219Lane5LatencyCompositionAgent(state_root=tmp_path) as agent:
        status = agent.status()
    assert status["rlm20_lane5_internal_state_closure"] == (
        "MANDATORY_NATIVE_ADMISSION_SEAM"
    )
    assert status["rlm20_preflight_export"] == (
        "hhs_exact_pass219_lane5_runtime_preflight"
    )
    assert status["canonical_admission_export"] == (
        "hhs_exact_pass219_vm81_environment_admit_signed"
    )
    assert status["raw_environmental_admission_exported"] is False


def test_rlm20_is_wired_before_later_lane5_iterations() -> None:
    aggregate = (ROOT / "hhs_runtime/c/hhs_runtime_exact_abi.c").read_text()
    raw_define = (
        "#define hhs_exact_pass219_vm81_environment_admit_signed "
        "\\\n    hhs_exact_pass219_vm81_environment_admit_signed_raw"
    )
    assert raw_define in aggregate
    assert aggregate.index(
        '#include "hhs_pass219_vm81_environmental_recovery_1_32.inc"'
    ) < aggregate.index(
        '#include "hhs_pass219_rlm20_lane5_internal_state_closure_1_37.inc"'
    )
    assert aggregate.index(
        '#include "hhs_pass219_rlm20_lane5_internal_state_closure_1_37.inc"'
    ) < aggregate.index(
        '#include "hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.inc"'
    )
    assert aggregate.index(
        '#include "hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.inc"'
    ) < aggregate.index(
        '#include "hhs_pass219_lane5_unbounded_workload_scaling_1_48.inc"'
    )


def test_raw_environmental_mutator_is_local_only() -> None:
    exports = (
        ROOT / "hhs_runtime/c/hhs_pass219_vm81_authority_exports.map"
    ).read_text()
    assert "hhs_exact_pass219_vm81_environment_admit_signed_raw;" in exports

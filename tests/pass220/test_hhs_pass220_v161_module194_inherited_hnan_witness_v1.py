"""V161 inherited HNAN/Lo Shu proof boundary, never native promotion."""
from __future__ import annotations

from pathlib import Path
import pytest

from hhs_runtime.hhs_pass220_v161_module194_inherited_hnan_witness_v1 import (
    REQUIRED_COURSE_GATES, V161WitnessError, inspect_module194_hnan_boundary,
)


def source_fixture() -> bytes:
    # Source-shape fixture only. No native HNAN execution is implied.
    return b"\n".join((
        b"m194Weight=new Uint8Array([4,9,2,3,5,7,8,1,6])",
        b"m194Group[i]=Math.floor(local/64)",
        b"m194Local[i]=local%64",
        b"m194Cluster[i]=i>=5184?1:0",
        b"partner:i<5184?i+5184:i-5184",
        b"h===4?0:Math.sin(phase)",
        b"M194_NONMONOTONE_TICK",
        b"brown<0 ? (-brown)*(l/9)*signed:0",
        b"m194Prob[g]-=mean",
        b"nativeAdmissionVerified:false",
        b"particleForcesAdded:0",
        b"HHS_V144_GAIN=0.001",
        b"0.035*localBias",
        b"HHS_M193.clusteringGain*rgbBias",
        b"rgbBrownianTick=tick;\nm193Advance(tick);\nm194Advance(tick);",
    ))


def test_binds_frozen_course_and_real_inherited_read_only_checker():
    witness = inspect_module194_hnan_boundary(
        source_fixture(), require_upload_identity=False,
    )
    assert witness["module194_groups"] == 81
    assert witness["module194_reciprocal_pairs"] == 5184
    assert witness["module194_particle_count"] == 10368
    assert witness["inherited_lo_shu_phase_factorization_exact"] is True
    assert witness["inherited_hash72_reciprocal_exact"] is True
    assert witness["inherited_5184_addresses_bijective"] is True
    assert [x["module_index"] for x in witness["course_required_gate_modules"]] == list(REQUIRED_COURSE_GATES)
    assert witness["course_ordered_ab_ba_native_proof_executed"] is False
    assert witness["course_hnan_passthrough_native_proof_executed"] is False
    assert witness["module194_hnan_center_native_gate_executed"] is False
    assert witness["module194_force_equivalence_verified"] is False
    assert witness["vm81_mutation_authority"] is False
    assert witness["hash72_hash216_minted"] is False


def test_rejects_source_identity_and_address_drift():
    with pytest.raises(ValueError, match="SOURCE_IDENTITY_MISMATCH"):
        inspect_module194_hnan_boundary(source_fixture())
    with pytest.raises(ValueError, match="SOURCE_CONTRACT_MISMATCH"):
        inspect_module194_hnan_boundary(
            source_fixture().replace(b"i+5184", b"i+5183"),
            require_upload_identity=False,
        )


def test_cannot_promote_arbitrary_report_to_proof(monkeypatch):
    import hhs_runtime.hhs_pass220_v161_module194_inherited_hnan_witness_v1 as gate
    monkeypatch.setattr(gate, "verify_read_only_candidate", lambda: {
        "candidate_only": False, "vm81_mutation_authority": True,
        "matrix_factorization_exact": True, "hash72_reciprocal_exact": True,
        "bigint_5184_addresses_bijective": True,
    })
    with pytest.raises(V161WitnessError, match="INHERITED_READ_ONLY_GATE_REJECTED"):
        gate.inspect_module194_hnan_boundary(source_fixture(), require_upload_identity=False)


def test_rejects_missing_frozen_course(tmp_path: Path):
    with pytest.raises(Exception):
        inspect_module194_hnan_boundary(
            source_fixture(), repository_root=tmp_path,
            require_upload_identity=False,
        )

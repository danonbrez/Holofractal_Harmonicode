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


def test_v161_refuses_course_source_freeze_drift_without_bypass():
    from hhs_runtime.hhs_pass220_whitepaper_corpus_ingress_v1 import ProofCorpusError
    # Source-frozen corpus currently differs from its declared git blob.
    # V161 must keep rejecting it; no synthesized proof or updated freeze.
    with pytest.raises(ProofCorpusError, match="SOURCE_BLOB_CHANGED:whitepapers/Harmonicode Algebra - Course"):
        inspect_module194_hnan_boundary(
            source_fixture(), require_upload_identity=False,
        )


def test_inherited_read_only_witness_remains_independently_executable():
    from hhs_runtime.pass220.hnan_lane5_exact_witness_v1 import verify_read_only_candidate
    witness = verify_read_only_candidate()
    assert witness["matrix_factorization_exact"] is True
    assert witness["hash72_reciprocal_exact"] is True
    assert witness["bigint_5184_addresses_bijective"] is True
    assert witness["candidate_only"] is True
    assert witness["vm81_mutation_authority"] is False


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

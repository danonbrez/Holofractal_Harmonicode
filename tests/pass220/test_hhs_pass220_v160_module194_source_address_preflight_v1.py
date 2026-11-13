"""V160 source guard tests: executable address bijection and fail-closed drift."""
from __future__ import annotations

from pathlib import Path
import pytest
from hhs_runtime.hhs_pass220_v160_module194_source_address_preflight_v1 import (
    GROUPS, HALF, LO_SHU, PARTICLES, REQUIRED, V160SourceError, address,
    audit_source,
)


def candidate() -> bytes:
    # Standalone minimal fixture for source-shape regression; the uploaded
    # complete file must separately pass its fixed SHA256 identity gate.
    items = ["m194Weight=new Uint8Array([4,9,2,3,5,7,8,1,6])"]
    items.extend({
        "group_map": "m194Group[i]=Math.floor(local/64)",
        "local_map": "m194Local[i]=local%64",
        "cluster_map": "m194Cluster[i]=i>=5184?1:0",
        "partner_map": "partner:i<5184?i+5184:i-5184",
        "center_projection": "h===4?0:Math.sin(phase)",
        "nonmonotone_guard": "'M194_NONMONOTONE_TICK'",
        "negative_impulse": "brown<0 ? (-brown)*(l/9)*signed:0",
        "zero_mean_projection": "m194Prob[g]-=mean",
        "native_nonadmission": "nativeAdmissionVerified:false",
        "no_added_forces": "particleForcesAdded:0",
        "original_gain": "HHS_V144_GAIN=0.001",
        "local_gain": "0.035*localBias",
        "m193_gain": "HHS_M193.clusteringGain*rgbBias",
        "advance_after_matrix": "rgbBrownianTick=tick;\nm193Advance(tick);\nm194Advance(tick);",
    }.values())
    assert len(REQUIRED) == len(items) - 1
    return "\n".join(items).encode()


def test_group_and_partner_exhaustive():
    assert len(LO_SHU) == 9
    seen = set()
    for i in range(PARTICLES):
        a = address(i)
        b = address(a["partner"])
        assert b["partner"] == i
        assert b["group"] == a["group"]
        assert b["local_slot"] == a["local_slot"]
        assert b["reciprocal_cluster"] != a["reciprocal_cluster"]
        assert 0 <= a["group"] < GROUPS
        assert (a["group"], a["reciprocal_cluster"], a["local_slot"]) not in seen
        seen.add((a["group"], a["reciprocal_cluster"], a["local_slot"]))
    assert len(seen) == 10368
    assert address(0)["partner"] == HALF
    assert address(HALF)["partner"] == 0
    assert address(PARTICLES-1)["group"] == 80
    assert address(PARTICLES-1)["lo_shu"] == 6
    assert address(4*64)["hnan"] == 4


def test_candidate_shape_is_not_native_proof():
    r = audit_source(candidate(), require_upload_identity=False)
    assert r["source_shape_checked"] is True
    assert r["course_gates_executed"] is False
    assert r["canonical_vm81_admission"] is False
    assert r["physical_producer_origin_verified"] is False
    assert r["update_order"] == "RGB_MATRIX_THEN_M193_THEN_M194"


def test_exact_uploaded_source_identity_is_separate_from_structural_fixture():
    with pytest.raises(V160SourceError, match="UPLOAD_SOURCE_IDENTITY_MISMATCH"):
        audit_source(candidate())
    with pytest.raises(V160SourceError, match="SOURCE_CONTRACT_MISMATCH"):
        audit_source(candidate().replace(b"0.035*localBias", b"0.35*localBias"),
                     require_upload_identity=False)
    with pytest.raises(V160SourceError, match="SOURCE_CONTRACT_MISMATCH"):
        audit_source(candidate().replace(b"h===4?0", b"h===4?1"),
                     require_upload_identity=False)
    with pytest.raises(V160SourceError, match="SOURCE_CONTRACT_MISMATCH"):
        audit_source(candidate().replace(b"i+5184", b"i+5183"),
                     require_upload_identity=False)
    with pytest.raises(V160SourceError, match="SOURCE_CONTRACT_MISMATCH"):
        audit_source(candidate().replace(b"4,9,2,3,5,7,8,1,6", b"4,9,2,3,5,7,8,6,1"),
                     require_upload_identity=False)


def test_invalid_index():
    for i in (-1, PARTICLES, 1.0, True):
        with pytest.raises(V160SourceError):
            address(i)

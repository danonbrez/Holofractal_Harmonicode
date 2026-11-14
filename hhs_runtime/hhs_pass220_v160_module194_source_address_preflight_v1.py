"""Pass 220 V160: Module 194 source/reciprocal addressing gate inventory.

A fail-closed STATIC SOURCE preflight for an uploaded browser candidate.
This is not a typed native HNAN evaluator, Lean proof, trusted physics
producer, or a VM81/Hash72/Hash216 admission receipt.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

SCHEMA = "HHS_PASS_220_V160_MODULE194_SOURCE_ADDRESS_PREFLIGHT_V1"
UPLOAD_SHA256 = "09532443888f645819687c7b562e6f7ce4441f2bc3c04ea54b684ac49e3edfcc"
LO_SHU = (4, 9, 2, 3, 5, 7, 8, 1, 6)
PARTICLES = 10368
HALF = 5184
GROUPS = 81
SLOTS = 64

# These exact source fragments are checked only as a static structural audit,
# never as a replacement for machine-checked equivalence or gate execution.
REQUIRED = {
    "group_map": r"m194Group\[i\]\s*=\s*Math\.floor\(local/64\)",
    "local_map": r"m194Local\[i\]\s*=\s*local%64",
    "cluster_map": r"m194Cluster\[i\]\s*=\s*i>=5184\?1:0",
    "partner_map": r"partner:i<5184\?i\+5184:i-5184",
    "center_projection": r"h===4\?0:Math\.sin",
    "nonmonotone_guard": r"M194_NONMONOTONE_TICK",
    "negative_impulse": r"brown<0\s*\?\s*\(-brown\)\*\(l/9\)\*signed:0",
    "zero_mean_projection": r"m194Prob\[g\]-=mean",
    "native_nonadmission": r"nativeAdmissionVerified:false",
    "no_added_forces": r"particleForcesAdded:0",
    "original_gain": r"HHS_V144_GAIN=0\.001",
    "local_gain": r"0\.035\*localBias",
    "m193_gain": r"HHS_M193\.clusteringGain\*rgbBias",
    "advance_after_matrix": r"rgbBrownianTick=tick;\s*m193Advance\(tick\);\s*m194Advance\(tick\)",
}


class V160SourceError(ValueError):
    pass


def address(index: int) -> dict[str, int]:
    if type(index) is not int or not 0 <= index < PARTICLES:
        raise V160SourceError("V160_INDEX_OUT_OF_RANGE")
    local = index % HALF
    group = local // SLOTS
    return {
        "index": index, "group": group,
        "lo_shu": LO_SHU[group // 9],
        "hnan": group % 9,
        "reciprocal_cluster": int(index >= HALF),
        "local_slot": local % SLOTS,
        "partner": index + HALF if index < HALF else index - HALF,
    }


def audit_source(source: bytes, *, require_upload_identity: bool = True) -> dict[str, Any]:
    if type(source) is not bytes:
        raise V160SourceError("V160_SOURCE_BYTES_REQUIRED")
    digest = sha256(source).hexdigest()
    if require_upload_identity and digest != UPLOAD_SHA256:
        raise V160SourceError("V160_UPLOAD_SOURCE_IDENTITY_MISMATCH")
    try:
        raw = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise V160SourceError("V160_SOURCE_UTF8_REQUIRED") from exc
    missing = [name for name, pattern in REQUIRED.items()
               if re.search(pattern, raw) is None]
    literal = re.search(
        r"m194Weight\s*=\s*new Uint8Array\(\[([^\]]+)\]\)", raw
    )
    if literal is None or tuple(int(x.strip()) for x in literal.group(1).split(",")) != LO_SHU:
        missing.append("lo_shu_order")
    if missing:
        raise V160SourceError("V160_SOURCE_CONTRACT_MISMATCH:" + ",".join(missing))
    groups = [0] * GROUPS
    partners = [0] * GROUPS
    for i in range(PARTICLES):
        a = address(i)
        b = address(a["partner"])
        if (a["group"] != b["group"] or
            a["lo_shu"] != b["lo_shu"] or a["hnan"] != b["hnan"] or
            a["local_slot"] != b["local_slot"] or
            a["reciprocal_cluster"] == b["reciprocal_cluster"] or
            b["partner"] != i):
            raise V160SourceError("V160_RECIPROCAL_ADDRESS_MISMATCH")
        groups[a["group"]] += 1
        if a["reciprocal_cluster"] == 0:
            partners[a["group"]] += 1
    if groups != [128] * GROUPS or partners != [64] * GROUPS:
        raise V160SourceError("V160_GROUP_CARDINALITY_MISMATCH")
    return {
        "schema": SCHEMA, "source_sha256": digest,
        "source_byte_length": len(source), "source_shape_checked": True,
        "groups": GROUPS, "particles": PARTICLES, "particles_per_group": 128,
        "reciprocal_pairs": HALF, "lo_shu": list(LO_SHU),
        "hnan_center_address": 4,
        "update_order": "RGB_MATRIX_THEN_M193_THEN_M194",
        "course_gates_required": [
            "ORDERED_TYPED_A_NOT_B", "AB_P4", "BA_NEG_P4",
            "INTERIOR_DELTA_E_NONZERO", "OUTER_DELTA_E_ZERO",
            "HNAN_GAIN_ONE_NO_PHASE_WRITE", "LEAN_NATIVE_RECEIPT",
        ],
        "course_gates_executed": False,
        "native_hnan_center_verified": False,
        "physical_producer_origin_verified": False,
        "canonical_vm81_admission": False,
        "hash72_hash216_minted": False,
    }


def audit_file(path: Path, *, require_upload_identity: bool = True) -> dict[str, Any]:
    return audit_source(Path(path).read_bytes(),
                        require_upload_identity=require_upload_identity)

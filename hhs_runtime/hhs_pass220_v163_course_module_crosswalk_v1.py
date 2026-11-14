"""Pass 220 V163: read-only, dual-source course-module crosswalk.

The frozen source is read from the immutable Git object named in the source
freeze. The working source is inspected as-is. Index correspondence is
diagnostic only: it is NOT mathematical equivalence, a course proof, a
replacement freeze, or an authority to change VM81/Hash72/Hash216 state.
"""
from __future__ import annotations

from hashlib import sha256
import re
from pathlib import Path
from typing import Any

from hhs_runtime.hhs_pass220_v162_course_source_divergence_v1 import (
    COURSE, V162CourseSourceError, _git, inspect_divergence,
)

SCHEMA = "HHS_PASS220_V163_COURSE_MODULE_CROSSWALK_V1"
FROZEN_HEADER = re.compile(rb"^MODULE ([0-9]+) \xe2\x80\x94 ([^\r\n]+)$", re.M)
CURRENT_HEADER = re.compile(rb"^# Module ([0-9]+) \xe2\x80\x94 ([^\r\n]+)$", re.M)


class V163CourseCrosswalkError(ValueError):
    pass


def _sections(data: bytes, pattern: re.Pattern[bytes]) -> dict[int, dict[str, Any]]:
    matches = list(pattern.finditer(data))
    if not matches:
        raise V163CourseCrosswalkError("V163_MODULE_HEADERS_MISSING")
    result = {}
    for i, match in enumerate(matches):
        index = int(match.group(1))
        if index in result:
            raise V163CourseCrosswalkError("V163_DUPLICATE_MODULE_INDEX")
        end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
        section = data[match.start():end]
        result[index] = {
            "index": index,
            "title": match.group(2).decode("utf-8"),
            "sha256": sha256(section).hexdigest(),
            "bytes": len(section),
            "start_byte": match.start(),
            "end_byte": end,
        }
    return result


def inspect_crosswalk(root: Path = Path(".")) -> dict[str, Any]:
    root = root.resolve()
    provenance = inspect_divergence(root)
    frozen = _git(root, "cat-file", "blob", provenance["frozen_git_blob_sha"])
    current = (root / COURSE).read_bytes()
    if sha256(frozen).hexdigest() != provenance["frozen_sha256"]:
        raise V163CourseCrosswalkError("V163_FROZEN_IDENTITY_CHANGED")
    if sha256(current).hexdigest() != provenance["working_sha256"]:
        raise V163CourseCrosswalkError("V163_WORKING_IDENTITY_CHANGED")
    originals = _sections(frozen, FROZEN_HEADER)
    expanded = _sections(current, CURRENT_HEADER)
    if tuple(originals) != tuple(range(13)):
        raise V163CourseCrosswalkError("V163_FROZEN_MODULE_RANGE_CHANGED")
    overlap = []
    for i, source in originals.items():
        target = expanded.get(i)
        overlap.append({
            "module_index": i,
            "frozen_section_sha256": source["sha256"],
            "current_section_sha256": target["sha256"] if target else None,
            "frozen_title": source["title"],
            "current_title": target["title"] if target else None,
            "frozen_bytes": source["bytes"],
            "current_bytes": target["bytes"] if target else None,
            "byte_identical": (
                target is not None and source["bytes"] == target["bytes"]
                and source["sha256"] == target["sha256"]
            ),
            "index_correspondence_only": True,
            "typed_equivalence_verified": False,
            "native_proof_executed": False,
        })
    return {
        "schema": SCHEMA,
        "frozen_git_blob_sha": provenance["frozen_git_blob_sha"],
        "current_git_blob_sha": provenance["working_git_blob_sha"],
        "frozen_sha256": provenance["frozen_sha256"],
        "current_sha256": provenance["working_sha256"],
        "frozen_module_count": len(originals),
        "current_numbered_module_count": len(expanded),
        "unmatched_current_indices": sorted(set(expanded) - set(originals)),
        "unmatched_frozen_indices": sorted(set(originals) - set(expanded)),
        "overlap": overlap,
        "source_integrity_gate_satisfied": provenance["source_integrity_gate_satisfied"],
        "course_equivalence_verified": False,
        "native_hnan_proof_executed": False,
        "lane5_producer_origin_verified": False,
        "vm81_admission_authority": False,
        "hash72_hash216_minted": False,
    }


def require_frozen_equivalence(root: Path = Path(".")) -> dict[str, Any]:
    """Fail closed; this crosswalk cannot attest typed ordered equivalence."""
    report = inspect_crosswalk(root)
    if not report["source_integrity_gate_satisfied"] or not report["course_equivalence_verified"]:
        raise V163CourseCrosswalkError("V163_TYPED_EQUIVALENCE_WITNESS_REQUIRED")
    return report

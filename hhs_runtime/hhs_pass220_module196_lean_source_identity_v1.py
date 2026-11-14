"""Module 196 Lean proof-source binding; read-only evidence, never canonical authority."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.core.hash72_validator_v1 import validate_hash72

ROOT = Path(__file__).resolve().parents[1]
LEAN_PATH = "formal/lean/HHS/Module196.lean"
SCHEMA = "HHS_PASS220_MODULE196_LEAN_SOURCE_IDENTITY_V1"
THEOREMS = (
    "collapse_preserves_both",
    "square_cell_partition",
    "hnan_child_positions",
    "fractal_square",
    "ordered_return_requires_witness",
)
DEPENDENCIES = ("LEAN4_KERNEL", "HHS.Module196", "HHS.Mathlib.Native")
EXPECTED_MARKERS = tuple(("theorem " + t) for t in THEOREMS)


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def build_module196_proof_identity(
    *, source: bytes | None = None, expected_sha256: str | None = None
) -> dict[str, Any]:
    data = (ROOT / LEAN_PATH).read_bytes() if source is None else source
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValueError("M196_LEAN_SOURCE_SHA256_MISMATCH")
    text = data.decode("utf-8")
    if "sorry" in text or "admit" in text:
        # Reject explicit incomplete proof terms (not proof-theorem names).
        import re
        if re.search(r"\b(sorry|admit)\b", text):
            raise ValueError("M196_LEAN_UNCHECKED_PROOF_TERM")
    if "namespace HHS.Module196" not in text or any(x not in text for x in EXPECTED_MARKERS):
        raise ValueError("M196_LEAN_DECLARATIONS_MISSING")
    theorem_material = {"schema": SCHEMA, "source_sha256": digest,
                        "module": "HHS.Module196", "theorems": THEOREMS}
    dependency_material = {"schema": SCHEMA, "source_sha256": digest,
                           "dependencies": DEPENDENCIES}
    theorem_hash72 = hash72_digest({"domain": SCHEMA, "label": "theorem"},
                                   _canonical(theorem_material))
    dependency_hash72 = hash72_digest({"domain": SCHEMA, "label": "dependency"},
                                      _canonical(dependency_material))
    if not validate_hash72(theorem_hash72) or not validate_hash72(dependency_hash72):
        raise ValueError("M196_LEAN_IDENTITY_HASH72_INVALID")
    return {
        "schema": SCHEMA,
        "source": LEAN_PATH,
        "source_sha256": digest,
        "module": "HHS.Module196",
        "theorems": list(THEOREMS),
        "dependencies": list(DEPENDENCIES),
        "theorem_identity_hash72": theorem_hash72,
        "dependency_identity_hash72": dependency_hash72,
        "kernel_proof_status": "REQUIRES_PINNED_CI_LEAN_CHECK",
        "vm81_mutation_authority": False,
        "hash72_commit_authority": False,
        "hash216_persistence_authority": False,
    }

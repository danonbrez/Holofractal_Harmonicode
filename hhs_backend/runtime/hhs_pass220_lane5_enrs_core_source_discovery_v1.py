"""Lane 5 four-pillar source identity projection (noncanonical).

Extends existing SQL source custody and repository hydration discovery.
Preserves exact original bytes, distinct source roles, and missing-branch
visibility; it never parses a new language, executes content, or mints
VM81/Hash72/Hash216 receipts. ENRS consumes source relationships downstream.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from hhs_backend.runtime.hhs_admin_sql_stream_staging_v1 import AdminStreamStaging

SCHEMA = "HHS_PASS220_LANE5_ENRS_CORE_SOURCE_DISCOVERY_V1"
PILLARS = (
    ("MATHEMATICAL_CORPUS", "docs/course/HARMONICODE_Algebra_Course_Expanded_0_189.md"),
    ("PARTICLE_SIMULATION", "examples/ParticleSimulation.html"),
    ("NARRATIVE_COGNITION", "creative_writing/novels/PANTHEON_OF_THE_PANOPTICON_COMPLETE_MANUSCRIPT.md"),
    ("OPERATIONAL_GOVERNANCE", "AGENTS.md"),
)
PASS219_GRAPH = "hhs_backend/runtime/hhs_pass219_lane5_repository_hydration_knowledge_graph_1_69.py"
PASS220_PARTICLE = "hhs_runtime/hhs_pass220_i085_particle_neural_layer_membrane_v1.py"
SOURCE_DOMAINS = {
    "MATHEMATICAL_CORPUS": "EXACT_ORDERED_EQUATIONS_AND_MODULE_GATES",
    "PARTICLE_SIMULATION": "PHYSICS_NEURAL_VISUAL_STATE",
    "NARRATIVE_COGNITION": "ENRS_NARRATIVE_RELATIONSHIPS_MEMORY_AND_AGENCY",
    "OPERATIONAL_GOVERNANCE": "REPOSITORY_EXECUTION_AND_PRESERVATION",
}


def _repo_source(repo_root: Path, rel_path: str) -> Path:
    p = (repo_root / rel_path).resolve()
    if not p.is_relative_to(repo_root):
        raise ValueError("CORE_SOURCE_ESCAPED_REPOSITORY_ROOT")
    return p


def _digest_file(path: Path) -> tuple[str, int]:
    h = sha256()
    n = 0
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
            n += len(block)
    return h.hexdigest(), n


def inspect_core_source_inventory(repo_root: str | Path) -> dict[str, Any]:
    """Report each path independently; missing sources never become fake nodes."""
    root = Path(repo_root).resolve()
    rows = []
    for role, rel in PILLARS:
        p = _repo_source(root, rel)
        exists = p.is_file() and not p.is_symlink()
        digest, count = _digest_file(p) if exists else (None, None)
        rows.append({
            "role": role,
            "relative_path": rel,
            "domain": SOURCE_DOMAINS[role],
            "present_in_checked_tree": exists,
            "source_sha256": digest,
            "source_bytes": count,
            "candidate_only": True,
        })
    return {
        "schema": SCHEMA,
        "pillars": rows,
        "all_four_present_in_checked_tree": all(x["present_in_checked_tree"] for x in rows),
        "lane5_hydration_graph": PASS219_GRAPH,
        "particle_neural_membrane": PASS220_PARTICLE,
        "enrs_source_class": "NARRATIVE_COGNITION",
        "new_canonical_vm81_mutation_authority": False,
        "new_hash72_receipt_authority": False,
        "new_hash216_provenance_authority": False,
        "enrs_execution_performed": False,
    }


def inspect_staged_core_source(
    staging: AdminStreamStaging,
    upload_id: str,
    authenticated_owner: str,
    repo_root: str | Path,
) -> dict[str, Any]:
    """Read-only exact source match; an absent branch file remains unresolved."""
    record = staging.status(upload_id, authenticated_owner)
    if record["state"] != "STAGED":
        raise ValueError("CORE_SOURCE_REQUIRES_FINALIZED_STAGING")
    staged_path = staging.read_staged(upload_id, authenticated_owner)
    digest, count = _digest_file(staged_path)
    if digest != record["source_sha256"] or count != record["received_bytes"]:
        raise ValueError("CORE_SOURCE_STAGING_IDENTITY_DRIFT")
    inv = inspect_core_source_inventory(repo_root)
    matching = [
        row for row in inv["pillars"]
        if row["present_in_checked_tree"]
        and row["source_sha256"] == digest and row["source_bytes"] == count
    ]
    selected = matching[0] if len(matching) == 1 else None
    return {
        "schema": SCHEMA,
        "upload_id": upload_id,
        "source_sha256": digest,
        "source_bytes": count,
        "matched_pillar": selected["role"] if selected else None,
        "matched_repo_path": selected["relative_path"] if selected else None,
        "matching_method": "EXACT_CONTENT_SHA256_AND_BYTE_COUNT" if selected else None,
        "core_inventory_complete": inv["all_four_present_in_checked_tree"],
        "unmatched_source_still_staged_and_retrievable": selected is None,
        "candidate_only": True,
        "enrs_execution_performed": False,
        "vm81_admission_performed": False,
        "hash72_receipt_minted": False,
        "hash216_provenance_committed": False,
    }

"""Exact relational trajectory candidate for Lane 5 algorithm-geometry learning.

No Hash216 minted: a future native receipt must bind the verified candidate.
"""
from __future__ import annotations

from hhs_runtime.pass220.lane5_neighborhood_phase_exchange import SCHEMA as EXCHANGE_SCHEMA

SCHEMA = "HHS_PASS220_LANE5_TRAJECTORY_RELATIONS_CANDIDATE_V1"

def compare_trajectory_exchanges(previous, current):
    """Describe what evolved in one nucleus' ordered 72-position neighborhood."""
    for item in (previous, current):
        if not isinstance(item, dict) or item.get("schema") != EXCHANGE_SCHEMA:
            raise ValueError("exact neighborhood exchange candidate required")
        if item.get("candidate_only") is not True or item.get("hash72_receipt_minted") is not False:
            raise ValueError("candidate-only unsigned source required")
        ids = item.get("ordered_particle_ids")
        if not isinstance(ids, list) or len(ids) != 9 or len(set(ids)) != 9:
            raise ValueError("nine distinct ordered particle identities required")
        for name in ("character_offsets", "phase_offsets", "reciprocal_phase_offsets"):
            values = item.get(name)
            if not isinstance(values, list) or len(values) != 72 or any(type(v) is not int for v in values):
                raise ValueError("exact 72-position offset arrays required")
        if item["character_offsets"] != list(range(72)):
            raise ValueError("ordered positional character identity required")
        if any(a+b != 0 for a,b in zip(item["phase_offsets"],item["reciprocal_phase_offsets"])):
            raise ValueError("reciprocal phase relation violated")
        if type(item.get("source_tick")) is not int or type(item.get("target_tick")) is not int:
            raise ValueError("exact computational tick required")
        if item["target_tick"] != item["source_tick"]+1:
            raise ValueError("one-tick ordered transition required")
    if previous["target_tick"] != current["source_tick"]:
        raise ValueError("discontinuous computational trajectory")
    if previous["nucleus_id"] != current["nucleus_id"]:
        raise ValueError("nucleus identity must be conserved")
    old, new = previous["phase_offsets"], current["phase_offsets"]
    delta = [b-a for a,b in zip(old,new)]
    before_ids, after_ids = previous["ordered_particle_ids"], current["ordered_particle_ids"]
    return {
        "schema": SCHEMA,
        "source_tick": previous["source_tick"],
        "middle_tick": current["source_tick"],
        "target_tick": current["target_tick"],
        "nucleus_id": previous["nucleus_id"],
        "ordered_neighbor_id_before": list(before_ids),
        "ordered_neighbor_id_after": list(after_ids),
        "neighbor_identity_changed": before_ids != after_ids,
        "phase_delta_72": delta,
        "reciprocal_phase_delta_72": [-v for v in delta],
        "changed_phase_positions": [i for i,v in enumerate(delta) if v],
        "unchanged_phase_positions": 72-sum(bool(v) for v in delta),
        "canonical_hash216_verified": False,
        "hash72_receipt_minted": False,
        "candidate_only": True,
        "requires_exact_cpu_vm81_replay": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
    }

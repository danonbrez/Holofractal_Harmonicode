"""Pass220 nine-by-eight reciprocal phase exchange *candidate* descriptor.

The 72 indexed character offsets and 72 oriented phase offsets describe a
constraint preimage. Only canonical VM81 may mint the actual Hash72 primitive
and its Hash216 receipt. Source tick is resolved before any next-tick edits.
"""
from __future__ import annotations

from hhs_runtime.pass220.lane5_nucleus_group_selection import PARTICLES

SCHEMA = "HHS_PASS220_NINE_BY_EIGHT_PHASE_EXCHANGE_CANDIDATE_V1"
SLOTS = 9
PHASES = 8
POSITIONS = 72


def prepare_neighborhood_exchange(*, group, phase_by_particle, reciprocal_phase_by_particle, tick):
    """Build ordered 72+72 offsets; reject forged or incomplete neighborhoods."""
    if type(tick) is not int or tick < 0:
        raise ValueError("exact nonnegative computational tick required")
    if (not isinstance(group, dict)
            or group.get("schema") != "HHS_PASS220_LANE5_NUCLEUS_GROUP_CANDIDATE_V1"
            or group.get("candidate_only") is not True
            or group.get("tick") != tick):
        raise ValueError("same-tick native group candidate required")
    ids = group.get("selected_ids")
    if (not isinstance(ids, list) or len(ids) != SLOTS
            or len(set(ids)) != SLOTS
            or any(type(i) is not int or i < 0 or i >= PARTICLES for i in ids)
            or ids[0] != group.get("nucleus")):
        raise ValueError("nucleus and exactly eight unique neighbors required")
    if (not isinstance(phase_by_particle, dict)
            or not isinstance(reciprocal_phase_by_particle, dict)
            or set(phase_by_particle) != set(ids)
            or set(reciprocal_phase_by_particle) != set(ids)):
        raise ValueError("both complete ordered local and reciprocal phase records required")
    for pid in ids:
        for phases in (phase_by_particle[pid], reciprocal_phase_by_particle[pid]):
            if (not isinstance(phases, (tuple,list)) or len(phases) != PHASES
                    or any(type(p) is not int for p in phases)):
                raise ValueError("eight exact integer phase offsets per particle required")
        if any(a + b != 0 for a,b in zip(phase_by_particle[pid], reciprocal_phase_by_particle[pid])):
            raise ValueError("reciprocal phase opposition violated")
    # Each of the nine Lo Shu slots carries eight ordered phase relationships.
    # A local64 address is not confused with a Hash72 token occurrence.
    character_offsets = list(range(POSITIONS))
    phase_offsets = [p for pid in ids for p in phase_by_particle[pid]]
    reciprocal_offsets = [p for pid in ids for p in reciprocal_phase_by_particle[pid]]
    return {
        "schema": SCHEMA,
        "source_tick": tick,
        "target_tick": tick + 1,
        "nucleus_id": ids[0],
        "ordered_particle_ids": list(ids),
        "character_offsets": character_offsets,
        "phase_offsets": phase_offsets,
        "reciprocal_phase_offsets": reciprocal_offsets,
        "expanded_phase_occurrences": POSITIONS * 2,
        "paired_positions": POSITIONS,
        "reciprocal_phase_opposition_checked": True,
        "requires_all_edits_resolved": True,
        "requires_native_hash72_receipt": True,
        "hash72_receipt_minted": False,
        "native_geometry_projection_verified": False,
        "candidate_only": True,
        "requires_exact_cpu_vm81_replay": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
    }

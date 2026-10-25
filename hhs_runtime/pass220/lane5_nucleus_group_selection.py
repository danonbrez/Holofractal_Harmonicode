"""Exact nucleus neighbor candidate projection; no canonical mutation authority."""
from __future__ import annotations

PARTICLES = 10368
SERIAL_POSITIONS = 5184

def select_group(coordinates, nucleus, neighbors, tick, periods=None):
    """Select the nucleus and k closest spatial particle identities."""
    if any(type(v) is not int for v in (nucleus, neighbors, tick)):
        raise ValueError("integer nucleus, neighbor count, and tick required")
    if not (0 <= nucleus < PARTICLES and 0 <= neighbors < PARTICLES and tick >= 0):
        raise ValueError("selection outside conserved population or time")
    if not isinstance(coordinates, dict) or set(coordinates) != set(range(PARTICLES)):
        raise ValueError("complete particle snapshot required")
    if periods is not None and (len(periods) != 3 or any(type(x) is not int or x <= 0 for x in periods)):
        raise ValueError("three positive integer wrap periods required")
    for xyz in coordinates.values():
        if not isinstance(xyz, (tuple, list)) or len(xyz) != 3 or any(type(v) is not int for v in xyz):
            raise ValueError("exact integer xyz coordinates required")
    origin = coordinates[nucleus]
    def measure(pid):
        delta = [abs(a-b) for a,b in zip(origin, coordinates[pid])]
        if periods is not None:
            delta = [min(d % p, p - d % p) for d,p in zip(delta, periods)]
        return (sum(d*d for d in delta), pid)
    chosen = sorted((pid for pid in coordinates if pid != nucleus), key=measure)[:neighbors]
    return {
        "schema": "HHS_PASS220_LANE5_NUCLEUS_GROUP_CANDIDATE_V1",
        "tick": tick, "nucleus": nucleus,
        "selected_ids": [nucleus, *chosen],
        "squared_distances": [measure(pid)[0] for pid in chosen],
        "particle_count": PARTICLES,
        "serialization_positions": SERIAL_POSITIONS,
        "candidate_only": True,
        "native_geometry_projection_verified": False,
        "requires_exact_cpu_vm81_replay": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
    }


def describe_relative_geometry(coordinates, selection, phases):
    """Immutable candidate descriptor of selected relative xyz and ordered phase.

    Copies no physical state. Source/destination momentum and absolute
    placements are deliberately outside this descriptor. Phase inputs are
    exact signed integers (native phase IDs supplied by a higher authority).
    """
    if (selection.get("schema") != "HHS_PASS220_LANE5_NUCLEUS_GROUP_CANDIDATE_V1"
            or selection.get("candidate_only") is not True):
        raise ValueError("nucleus candidate selection required")
    ids = selection.get("selected_ids")
    if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
        raise ValueError("unique selected particle IDs required")
    if not isinstance(coordinates, dict) or set(coordinates) != set(range(PARTICLES)):
        raise ValueError("complete source snapshot required")
    if not isinstance(phases, dict) or set(phases) != set(range(PARTICLES)):
        raise ValueError("complete exact source phase snapshot required")
    if any(type(phases[i]) is not int for i in phases):
        raise ValueError("exact integer phase coordinates required")
    if any(type(v) is not int for v in (selection.get("tick"), selection.get("nucleus"))):
        raise ValueError("exact tick and nucleus required")
    if not 0 <= selection["nucleus"] < PARTICLES or ids[0] != selection["nucleus"]:
        raise ValueError("nucleus identity mismatch")
    if any(type(i) is not int or i < 0 or i >= PARTICLES for i in ids):
        raise ValueError("invalid particle identity")
    for xyz in coordinates.values():
        if (not isinstance(xyz, (tuple, list)) or len(xyz) != 3
                or any(type(v) is not int for v in xyz)):
            raise ValueError("exact integer xyz snapshot required")
    origin = coordinates[ids[0]]
    anchor_phase = phases[ids[0]]
    return {
        "schema": "HHS_PASS220_LANE5_RELATIVE_GEOMETRY_DESCRIPTOR_V1",
        "source_tick": selection["tick"],
        "source_nucleus": ids[0],
        "particle_ids": list(ids),
        "relative_xyz": [
            tuple(coordinates[i][j] - origin[j] for j in range(3)) for i in ids
        ],
        "relative_oriented_phase": [phases[i] - anchor_phase for i in ids],
        "particle_count_unchanged": PARTICLES,
        "shared_serialization_positions": SERIAL_POSITIONS,
        "copies_absolute_location": False,
        "copies_momentum": False,
        "copies_canonical_state": False,
        "candidate_only": True,
        "native_geometry_projection_verified": False,
        "requires_exact_cpu_vm81_replay": True,
        "canonical_vm81_mutation_authority": False,
        "canonical_hash72_mint_authority": False,
        "canonical_hash216_mint_authority": False,
    }

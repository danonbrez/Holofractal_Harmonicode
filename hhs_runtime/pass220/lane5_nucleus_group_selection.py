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

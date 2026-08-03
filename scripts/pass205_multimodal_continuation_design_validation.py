#!/usr/bin/env python3
"""Pass 205 design validation: deterministic 5,184-bit multimodal continuation runtime.

Representation-level validation for the inherited HHS model:
- 81 cells x 64 bits = 5,184-bit canonical state
- 243 five-trit controls per bit
- 1,259,712 hydration addresses q = 243*s + g
- persistent parent-addressed continuations
- sparse game/graphics/physics/lighting/ML projection hydration

The fixed-width digests in this standalone harness are deterministic transport
witnesses. Production implementation remains bound to inherited Hash216,
Hash72, and VM81 authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableSequence, Sequence, Tuple

CELLS = 81
CELL_BITS = 64
STATE_BITS = CELLS * CELL_BITS
CONTROLS = 243
HYDRATION_CAPACITY = STATE_BITS * CONTROLS
CHANNELS = 32
MASK64 = (1 << 64) - 1
HASH216_BYTES = 27
HASH72_BYTES = 9
SCHEMA_ID = "HHS_P205_STATE_81X64_V1"

# Packed 64-bit cell fields.
X_SHIFT, X_BITS = 0, 6
Y_SHIFT, Y_BITS = 6, 6
Z_SHIFT, Z_BITS = 12, 6
VX_SHIFT, V_BITS = 18, 4
VY_SHIFT = 22
VZ_SHIFT = 26
GEOMETRY_SHIFT, GEOMETRY_BITS = 30, 5
HUE_SHIFT, HUE_BITS = 35, 8
EMISSION_SHIFT, EMISSION_BITS = 43, 8
ACTIVE_SHIFT, ACTIVE_BITS = 51, 1
POLICY_SHIFT, POLICY_BITS = 52, 12

FIELD_MASKS = {
    "x": ((1 << X_BITS) - 1) << X_SHIFT,
    "y": ((1 << Y_BITS) - 1) << Y_SHIFT,
    "z": ((1 << Z_BITS) - 1) << Z_SHIFT,
    "vx": ((1 << V_BITS) - 1) << VX_SHIFT,
    "vy": ((1 << V_BITS) - 1) << VY_SHIFT,
    "vz": ((1 << V_BITS) - 1) << VZ_SHIFT,
    "geometry": ((1 << GEOMETRY_BITS) - 1) << GEOMETRY_SHIFT,
    "hue": ((1 << HUE_BITS) - 1) << HUE_SHIFT,
    "emission": ((1 << EMISSION_BITS) - 1) << EMISSION_SHIFT,
    "active": ((1 << ACTIVE_BITS) - 1) << ACTIVE_SHIFT,
    "policy": ((1 << POLICY_BITS) - 1) << POLICY_SHIFT,
}
VISUAL_MASK = FIELD_MASKS["x"] | FIELD_MASKS["y"] | FIELD_MASKS["z"] | FIELD_MASKS["geometry"] | FIELD_MASKS["hue"] | FIELD_MASKS["emission"]


def _hash(width: int, person: bytes, *parts: bytes) -> bytes:
    h = hashlib.blake2b(digest_size=width, person=person)
    for part in parts:
        h.update(len(part).to_bytes(8, "little"))
        h.update(part)
    return h.digest()


def h216(*parts: bytes) -> bytes:
    return _hash(HASH216_BYTES, b"HHS-P205-H216", *parts)


def h72(*parts: bytes) -> bytes:
    return _hash(HASH72_BYTES, b"HHS-P205-H72", *parts)


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def encode_trits(trits: Sequence[int]) -> int:
    if len(trits) != 5 or any(t not in (0, 1, 2) for t in trits):
        raise ValueError("control must contain five trits")
    return trits[0] + 3 * trits[1] + 9 * trits[2] + 27 * trits[3] + 81 * trits[4]


def decode_trits(g: int) -> Tuple[int, int, int, int, int]:
    if not 0 <= g < CONTROLS:
        raise ValueError("control outside 0..242")
    values: List[int] = []
    value = g
    for _ in range(5):
        values.append(value % 3)
        value //= 3
    return tuple(values)  # type: ignore[return-value]


def q_from_sg(s: int, g: int) -> int:
    if not 0 <= s < STATE_BITS or not 0 <= g < CONTROLS:
        raise ValueError("hydration coordinate outside range")
    return CONTROLS * s + g


def sg_from_q(q: int) -> Tuple[int, int]:
    if not 0 <= q < HYDRATION_CAPACITY:
        raise ValueError("hydration address outside range")
    return divmod(q, CONTROLS)


def _get(word: int, shift: int, bits: int) -> int:
    return (word >> shift) & ((1 << bits) - 1)


def _set(word: int, shift: int, bits: int, value: int) -> int:
    if not 0 <= value < (1 << bits):
        raise ValueError(f"value {value} does not fit {bits} bits")
    mask = ((1 << bits) - 1) << shift
    return ((word & ~mask) | (value << shift)) & MASK64


def encode_velocity(value: int) -> int:
    if not -7 <= value <= 7:
        raise ValueError("velocity outside -7..7")
    return value + 8


def decode_velocity(value: int) -> int:
    return value - 8


def pack_cell(*, x: int, y: int, z: int, vx: int, vy: int, vz: int, geometry: int, hue: int, emission: int, active: int, policy: int) -> int:
    word = 0
    word = _set(word, X_SHIFT, X_BITS, x)
    word = _set(word, Y_SHIFT, Y_BITS, y)
    word = _set(word, Z_SHIFT, Z_BITS, z)
    word = _set(word, VX_SHIFT, V_BITS, encode_velocity(vx))
    word = _set(word, VY_SHIFT, V_BITS, encode_velocity(vy))
    word = _set(word, VZ_SHIFT, V_BITS, encode_velocity(vz))
    word = _set(word, GEOMETRY_SHIFT, GEOMETRY_BITS, geometry)
    word = _set(word, HUE_SHIFT, HUE_BITS, hue)
    word = _set(word, EMISSION_SHIFT, EMISSION_BITS, emission)
    word = _set(word, ACTIVE_SHIFT, ACTIVE_BITS, active)
    word = _set(word, POLICY_SHIFT, POLICY_BITS, policy)
    return word


def unpack_cell(word: int) -> Dict[str, int]:
    return {
        "x": _get(word, X_SHIFT, X_BITS),
        "y": _get(word, Y_SHIFT, Y_BITS),
        "z": _get(word, Z_SHIFT, Z_BITS),
        "vx": decode_velocity(_get(word, VX_SHIFT, V_BITS)),
        "vy": decode_velocity(_get(word, VY_SHIFT, V_BITS)),
        "vz": decode_velocity(_get(word, VZ_SHIFT, V_BITS)),
        "geometry": _get(word, GEOMETRY_SHIFT, GEOMETRY_BITS),
        "hue": _get(word, HUE_SHIFT, HUE_BITS),
        "emission": _get(word, EMISSION_SHIFT, EMISSION_BITS),
        "active": _get(word, ACTIVE_SHIFT, ACTIVE_BITS),
        "policy": _get(word, POLICY_SHIFT, POLICY_BITS),
    }


def position(word: int) -> Tuple[int, int, int]:
    return (_get(word, X_SHIFT, X_BITS), _get(word, Y_SHIFT, Y_BITS), _get(word, Z_SHIFT, Z_BITS))


def state_bytes(state: Sequence[int]) -> bytes:
    if len(state) != CELLS:
        raise ValueError("state must contain 81 cell words")
    return b"".join(int(word & MASK64).to_bytes(8, "little") for word in state)


def state_content_root(state: Sequence[int]) -> bytes:
    return h216(b"STATE", SCHEMA_ID.encode(), state_bytes(state))


def initial_state(seed: int) -> Tuple[int, ...]:
    rng = random.Random(seed)
    words: List[int] = []
    occupied = set()
    for i in range(CELLS):
        x = (i % 9) * 7
        y = (i // 9) * 7
        z = (i * 5 + seed) % 64
        while (x, y, z) in occupied:
            z = (z + 1) % 64
        occupied.add((x, y, z))
        active = 1 if i < 12 else 0
        vx = rng.choice((-2, -1, 0, 1, 2)) if active else 0
        vy = rng.choice((-1, 0, 1)) if active else 0
        vz = rng.choice((-1, 0, 1)) if active else 0
        words.append(pack_cell(
            x=x, y=y, z=z,
            vx=vx, vy=vy, vz=vz,
            geometry=(i * 7 + seed) % 32,
            hue=(i * 29 + seed * 3) % 256,
            emission=(i * 11 + seed) % 96,
            active=active,
            policy=(i * 41 + seed) % 4096,
        ))
    return tuple(words)


@dataclass(frozen=True)
class Event:
    cell: int
    control: int

    def to_bytes(self) -> bytes:
        return self.cell.to_bytes(1, "little") + self.control.to_bytes(1, "little")


def event_stream(seed: int, ticks: int, events_per_tick: int = 4) -> List[Tuple[Event, ...]]:
    rng = random.Random(seed ^ 0x205205)
    stream: List[Tuple[Event, ...]] = []
    for _ in range(ticks):
        cells = rng.sample(range(CELLS), events_per_tick)
        stream.append(tuple(Event(cell, rng.randrange(CONTROLS)) for cell in cells))
    return stream


def apply_events(state: Sequence[int], events: Sequence[Event]) -> Tuple[Tuple[int, ...], set[int]]:
    words = list(state)
    targeted: set[int] = set()
    for event in sorted(events, key=lambda e: (e.cell, e.control)):
        targeted.add(event.cell)
        t0, t1, t2, t3, t4 = decode_trits(event.control)
        data = unpack_cell(words[event.cell])
        data["vx"] = max(-7, min(7, data["vx"] + (t0 - 1)))
        data["vy"] = max(-7, min(7, data["vy"] + (t1 - 1)))
        data["vz"] = max(-7, min(7, data["vz"] + (t2 - 1)))
        data["hue"] = (data["hue"] + (t3 - 1) * 7) % 256
        data["emission"] = max(0, min(255, data["emission"] + (t4 - 1) * 9))
        # Event targeting does not silently promote a cell into a persistent mover.
        data["active"] = data["active"]
        data["policy"] = (data["policy"] * 17 + event.control + event.cell) % 4096
        words[event.cell] = pack_cell(**data)
    return tuple(words), targeted


def _bounded_move(coord: int, velocity: int) -> Tuple[int, int]:
    candidate = coord + velocity
    if candidate < 0:
        return -candidate, -velocity
    if candidate > 63:
        return 126 - candidate, -velocity
    return candidate, velocity


def _manhattan(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def evolve_state(state: Sequence[int], events: Sequence[Event], *, full_scan: bool) -> Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[int, ...]]:
    injected, targeted = apply_events(state, events)
    active = {i for i, word in enumerate(injected) if _get(word, ACTIVE_SHIFT, ACTIVE_BITS)}
    moving = active | targeted

    # Synchronous proposed movement.
    proposals: Dict[int, Tuple[int, int, int, int, int, int]] = {}
    for i in moving:
        data = unpack_cell(injected[i])
        nx, nvx = _bounded_move(data["x"], data["vx"])
        ny, nvy = _bounded_move(data["y"], data["vy"])
        nz, nvz = _bounded_move(data["z"], data["vz"])
        proposals[i] = (nx, ny, nz, nvx, nvy, nvz)

    # Deterministic collision resolution. Existing stationary cells reserve their positions;
    # moving cells are then admitted in ascending identity order.
    stationary = set(range(CELLS)) - moving
    reserved = {position(injected[i]): i for i in stationary}
    admitted: Dict[int, Tuple[int, int, int, int, int, int]] = {}
    for i in sorted(moving):
        proposal = proposals[i]
        p = proposal[:3]
        if p in reserved:
            data = unpack_cell(injected[i])
            admitted[i] = (data["x"], data["y"], data["z"], -proposal[3], -proposal[4], -proposal[5])
        else:
            admitted[i] = proposal
            reserved[p] = i

    result = list(injected)
    candidates: Iterable[int] = range(CELLS) if full_scan else sorted(moving)
    for i in candidates:
        if i not in admitted:
            continue
        data = unpack_cell(injected[i])
        nx, ny, nz, nvx, nvy, nvz = admitted[i]
        data.update({"x": nx, "y": ny, "z": nz, "vx": nvx, "vy": nvy, "vz": nvz})
        # Deterministic activity decay; target events always remain active for the tick.
        if i not in targeted and ((data["policy"] + nx + ny + nz) % 17 == 0):
            data["active"] = 0
        result[i] = pack_cell(**data)

    changed = tuple(i for i, (before, after) in enumerate(zip(state, result)) if before != after)
    # Projection dependencies: changed objects plus all objects influenced by their old/new light fields.
    dirty = set(changed)
    changed_positions = [position(state[i]) for i in changed] + [position(result[i]) for i in changed]
    if full_scan:
        projection_dirty = tuple(range(CELLS))
    else:
        for j, word in enumerate(result):
            pj = position(word)
            if any(_manhattan(pj, pc) <= 12 for pc in changed_positions):
                dirty.add(j)
        projection_dirty = tuple(sorted(dirty))
    return tuple(result), changed, projection_dirty


def _normal_for_geometry(geometry: int) -> Tuple[int, int, int]:
    # Exact integer normal catalogue; values are in [-7, 7].
    return (
        ((geometry * 5 + 1) % 15) - 7,
        ((geometry * 7 + 3) % 15) - 7,
        ((geometry * 11 + 5) % 15) - 7,
    )


def _lighting(state: Sequence[int], cell: int) -> Tuple[int, int, int, int]:
    target = unpack_cell(state[cell])
    tp = (target["x"], target["y"], target["z"])
    nx, ny, nz = _normal_for_geometry(target["geometry"])
    intensity = 24
    weighted_hue = target["hue"] * 24
    weight_total = 24
    for j, word in enumerate(state):
        if j == cell:
            continue
        source = unpack_cell(word)
        if source["emission"] == 0:
            continue
        sp = (source["x"], source["y"], source["z"])
        dx, dy, dz = sp[0] - tp[0], sp[1] - tp[1], sp[2] - tp[2]
        distance = abs(dx) + abs(dy) + abs(dz)
        if distance > 12:
            continue
        facing = max(0, nx * dx + ny * dy + nz * dz)
        contribution = (source["emission"] * (13 - distance) * (8 + facing)) // 2048
        if contribution:
            intensity += contribution
            weighted_hue += source["hue"] * contribution
            weight_total += contribution
    intensity = max(0, min(255, intensity))
    hue = (weighted_hue // max(1, weight_total)) % 256
    # Integer HSV-like projection.
    sector = hue // 43
    fraction = (hue % 43) * 6
    p = intensity // 4
    q = (intensity * (255 - fraction)) // 255
    t = (intensity * fraction) // 255
    if sector == 0:
        r, g, b = intensity, t, p
    elif sector == 1:
        r, g, b = q, intensity, p
    elif sector == 2:
        r, g, b = p, intensity, t
    elif sector == 3:
        r, g, b = p, q, intensity
    elif sector == 4:
        r, g, b = t, p, intensity
    else:
        r, g, b = intensity, p, q
    return r, g, b, intensity


def projection_channels(state: Sequence[int], cell: int) -> Tuple[int, ...]:
    data = unpack_cell(state[cell])
    r, g, b, light = _lighting(state, cell)
    position_word = data["x"] | (data["y"] << 6) | (data["z"] << 12)
    velocity_word = (data["vx"] + 8) | ((data["vy"] + 8) << 4) | ((data["vz"] + 8) << 8)
    base = [
        data["geometry"],
        position_word,
        velocity_word,
        data["hue"] | (data["emission"] << 8),
        r | (g << 8) | (b << 16) | (light << 24),
        data["policy"],
        data["active"],
        cell,
    ]
    channels = list(base)
    seed = state[cell] ^ (cell * 0x9E3779B97F4A7C15)
    while len(channels) < CHANNELS:
        idx = len(channels)
        mix = (seed ^ (idx * 0x85EBCA6B) ^ (position_word << (idx % 7))) & MASK64
        mix ^= mix >> 33
        mix = (mix * 0xFF51AFD7ED558CCD) & MASK64
        mix ^= mix >> 29
        channels.append(mix & 0xFFFFFFFF)
    return tuple(channels)


def build_projection(state: Sequence[int]) -> Tuple[Tuple[int, ...], ...]:
    return tuple(projection_channels(state, i) for i in range(CELLS))


def update_projection(previous: Sequence[Sequence[int]], state: Sequence[int], dirty: Sequence[int]) -> Tuple[Tuple[int, ...], ...]:
    result = [tuple(row) for row in previous]
    for i in dirty:
        result[i] = projection_channels(state, i)
    return tuple(result)


def projection_root(projection: Sequence[Sequence[int]]) -> bytes:
    payload = bytearray()
    for row in projection:
        for word in row:
            payload += int(word).to_bytes(4, "little")
    return h216(b"PROJECTION32", bytes(payload))


def feature_for_cell(word: int) -> Tuple[int, ...]:
    d = unpack_cell(word)
    speed = abs(d["vx"]) + abs(d["vy"]) + abs(d["vz"])
    return (
        1,
        d["x"], d["y"], d["z"],
        d["vx"], d["vy"], d["vz"], speed,
        d["geometry"], d["hue"], d["emission"], d["active"],
        d["policy"] & 0xFF, d["policy"] >> 8,
        (d["x"] * d["y"] + d["z"]) % 4096,
        (d["hue"] * (1 + d["emission"])) % 65536,
    )


def full_features(state: Sequence[int]) -> Tuple[int, ...]:
    totals = [0] * 16
    for word in state:
        feature = feature_for_cell(word)
        for i, value in enumerate(feature):
            totals[i] += value
    return tuple(totals)


def update_features(previous: Sequence[int], old_state: Sequence[int], new_state: Sequence[int], changed: Sequence[int]) -> Tuple[int, ...]:
    totals = list(previous)
    for cell in changed:
        old = feature_for_cell(old_state[cell])
        new = feature_for_cell(new_state[cell])
        for i in range(16):
            totals[i] += new[i] - old[i]
    return tuple(totals)


def feature_root(features: Sequence[int]) -> bytes:
    return h216(b"MLFEATURE16", b"".join(int(v).to_bytes(8, "little", signed=True) for v in features))


def delta_between(parent: Sequence[int], child: Sequence[int]) -> Tuple[Tuple[int, int], ...]:
    return tuple((i, (a ^ b) & MASK64) for i, (a, b) in enumerate(zip(parent, child)) if a != b)


def apply_delta(state: Sequence[int], delta: Sequence[Tuple[int, int]]) -> Tuple[int, ...]:
    result = list(state)
    for cell, xor_mask in delta:
        result[cell] ^= xor_mask
    return tuple(result)


def delta_root(delta: Sequence[Tuple[int, int]]) -> bytes:
    return h216(b"DELTA", *[cell.to_bytes(1, "little") + mask.to_bytes(8, "little") for cell, mask in delta])


def hydration_addresses(delta: Sequence[Tuple[int, int]], control: int) -> Tuple[int, ...]:
    addresses: List[int] = []
    for cell, mask in delta:
        for bit in range(CELL_BITS):
            if (mask >> bit) & 1:
                s = cell * CELL_BITS + bit
                addresses.append(q_from_sg(s, control))
    return tuple(addresses)


@dataclass(frozen=True)
class Snapshot:
    generation: int
    parent_continuation_root: bytes
    content_root: bytes
    continuation_root: bytes
    receipt72: bytes
    delta: Tuple[Tuple[int, int], ...]
    event_root: bytes
    projection_root: bytes
    feature_root: bytes
    state: Tuple[int, ...]
    compatibility: str


def make_snapshot(parent: Snapshot | None, state: Tuple[int, ...], events: Sequence[Event], projection: Sequence[Sequence[int]], features: Sequence[int], compatibility: str = SCHEMA_ID) -> Snapshot:
    parent_root = b"\x00" * HASH216_BYTES if parent is None else parent.continuation_root
    parent_state = tuple(0 for _ in range(CELLS)) if parent is None else parent.state
    generation = 0 if parent is None else parent.generation + 1
    delta = delta_between(parent_state, state)
    droot = delta_root(delta)
    eroot = h216(b"EVENTS", *[event.to_bytes() for event in sorted(events, key=lambda e: (e.cell, e.control))])
    proot = projection_root(projection)
    froot = feature_root(features)
    croot = state_content_root(state)
    continuation = h216(
        b"CONTINUATION",
        compatibility.encode(),
        generation.to_bytes(8, "little"),
        parent_root,
        croot,
        droot,
        eroot,
        proot,
        froot,
    )
    receipt = h72(b"COMMIT", generation.to_bytes(8, "little"), parent_root, continuation, droot)
    return Snapshot(generation, parent_root, croot, continuation, receipt, delta, eroot, proot, froot, state, compatibility)


def visual_root(state: Sequence[int]) -> bytes:
    return h216(b"VISUAL-STATE", *[(word & VISUAL_MASK).to_bytes(8, "little") for word in state])


def exact_state_distance(a: Sequence[int], b: Sequence[int]) -> int:
    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def vector_embedding(state: Sequence[int]) -> Tuple[int, ...]:
    # 324-dimensional exact-ish integer state projection: four 16-bit lanes per cell.
    values: List[int] = []
    for word in state:
        values.extend(((word >> shift) & 0xFFFF) for shift in (0, 16, 32, 48))
    return tuple(values)


def vector_distance(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))


def nearest_compatible(query: Sequence[int], snapshots: Sequence[Snapshot], compatibility: str, top_k: int = 32) -> Tuple[Snapshot, bool, int]:
    candidates = [snapshot for snapshot in snapshots if snapshot.compatibility == compatibility]
    qvec = vector_embedding(query)
    ranked = sorted(candidates, key=lambda snapshot: vector_distance(qvec, vector_embedding(snapshot.state)))
    shortlist = ranked[:min(top_k, len(ranked))]
    selected = min(shortlist, key=lambda snapshot: exact_state_distance(query, snapshot.state))
    exact = min(candidates, key=lambda snapshot: exact_state_distance(query, snapshot.state))
    return selected, selected.continuation_root == exact.continuation_root, exact_state_distance(query, selected.state)


def assert_geometry(state: Sequence[int]) -> None:
    positions = [position(word) for word in state]
    if len(set(positions)) != CELLS:
        raise AssertionError("collision invariant violated")
    for word in state:
        d = unpack_cell(word)
        if not all(0 <= d[name] <= 63 for name in ("x", "y", "z")):
            raise AssertionError("position out of range")
        if not all(-7 <= d[name] <= 7 for name in ("vx", "vy", "vz")):
            raise AssertionError("velocity out of range")


def test_dimensions() -> Dict[str, object]:
    if STATE_BITS != 5184 or HYDRATION_CAPACITY != 1_259_712:
        raise AssertionError("canonical dimensions changed")
    seen_controls = set()
    for g in range(CONTROLS):
        trits = decode_trits(g)
        if encode_trits(trits) != g:
            raise AssertionError("five-trit control mapping failed")
        seen_controls.add(trits)
    if len(seen_controls) != CONTROLS:
        raise AssertionError("five-trit controls are not bijective")
    for s in (0, 1, 63, 64, 5183):
        for g in (0, 1, 121, 242):
            q = q_from_sg(s, g)
            if sg_from_q(q) != (s, g):
                raise AssertionError("hydration address mapping failed")
    if q_from_sg(5183, 242) != 1_259_711:
        raise AssertionError("upper hydration address mismatch")
    return {"status": "PASS", "state_bits": STATE_BITS, "controls": CONTROLS, "hydration_addresses": HYDRATION_CAPACITY}


def test_pack_roundtrip(seed: int, trials: int = 100_000) -> Dict[str, object]:
    rng = random.Random(seed)
    for _ in range(trials):
        fields = {
            "x": rng.randrange(64), "y": rng.randrange(64), "z": rng.randrange(64),
            "vx": rng.randrange(-7, 8), "vy": rng.randrange(-7, 8), "vz": rng.randrange(-7, 8),
            "geometry": rng.randrange(32), "hue": rng.randrange(256), "emission": rng.randrange(256),
            "active": rng.randrange(2), "policy": rng.randrange(4096),
        }
        if unpack_cell(pack_cell(**fields)) != fields:
            raise AssertionError("64-bit cell roundtrip failed")
    return {"status": "PASS", "roundtrips": trials}


def run_workload(seed: int, ticks: int) -> Dict[str, object]:
    events = event_stream(seed, ticks)
    initial = initial_state(seed)
    assert_geometry(initial)

    full_state = initial
    delta_state = initial
    full_projection = build_projection(initial)
    delta_projection = full_projection
    full_feature = full_features(initial)
    delta_feature = full_feature
    genesis = make_snapshot(None, initial, (), full_projection, full_feature)
    snapshots = [genesis]
    parent = genesis

    full_seconds = 0.0
    delta_seconds = 0.0
    changed_counts: List[int] = []
    projection_counts: List[int] = []
    hydration_counts: List[int] = []
    delta_payload_bytes = 0

    for tick, tick_events in enumerate(events, start=1):
        t0 = time.perf_counter()
        next_full, full_changed, _ = evolve_state(full_state, tick_events, full_scan=True)
        next_full_projection = build_projection(next_full)
        next_full_feature = full_features(next_full)
        full_seconds += time.perf_counter() - t0

        t1 = time.perf_counter()
        next_delta, delta_changed, projection_dirty = evolve_state(delta_state, tick_events, full_scan=False)
        next_delta_projection = update_projection(delta_projection, next_delta, projection_dirty)
        next_delta_feature = update_features(delta_feature, delta_state, next_delta, delta_changed)
        delta_seconds += time.perf_counter() - t1

        if next_full != next_delta:
            raise AssertionError(f"full/delta state mismatch at tick {tick}")
        if next_full_projection != next_delta_projection:
            raise AssertionError(f"full/delta projection mismatch at tick {tick}")
        if next_full_feature != next_delta_feature:
            raise AssertionError(f"full/delta ML feature mismatch at tick {tick}")
        if tuple(full_changed) != tuple(delta_changed):
            raise AssertionError("changed frontier mismatch")
        assert_geometry(next_delta)

        for row in next_delta_projection:
            if len(row) != CHANNELS or any(not 0 <= word <= 0xFFFFFFFF for word in row):
                raise AssertionError("32-channel projection invalid")
            rgba = row[4]
            if any(not 0 <= ((rgba >> shift) & 0xFF) <= 255 for shift in (0, 8, 16, 24)):
                raise AssertionError("lighting/color channel invalid")

        snapshot = make_snapshot(parent, next_delta, tick_events, next_delta_projection, next_delta_feature)
        reconstructed = apply_delta(parent.state, snapshot.delta)
        if reconstructed != snapshot.state:
            raise AssertionError("forward delta reconstruction failed")
        if apply_delta(snapshot.state, snapshot.delta) != parent.state:
            raise AssertionError("XOR inverse continuation failed")
        control = tick_events[0].control if tick_events else 0
        addresses = hydration_addresses(snapshot.delta, control)
        if len(addresses) != len(set(addresses)):
            raise AssertionError("duplicate hydration address in one continuation")
        if any(not 0 <= q < HYDRATION_CAPACITY for q in addresses):
            raise AssertionError("hydration address outside graph")

        snapshots.append(snapshot)
        parent = snapshot
        full_state = next_full
        delta_state = next_delta
        full_projection = next_full_projection
        delta_projection = next_delta_projection
        full_feature = next_full_feature
        delta_feature = next_delta_feature
        changed_counts.append(len(delta_changed))
        projection_counts.append(len(projection_dirty))
        hydration_counts.append(len(addresses))
        delta_payload_bytes += len(snapshot.delta) * 9

    # Replay lineage from genesis using persisted deltas.
    replay_state = snapshots[0].state
    replay_projection = build_projection(replay_state)
    replay_feature = full_features(replay_state)
    replay_parent = snapshots[0]
    for tick, snapshot in enumerate(snapshots[1:], start=1):
        replay_state = apply_delta(replay_state, snapshot.delta)
        replay_projection = build_projection(replay_state)
        replay_feature = full_features(replay_state)
        replay = make_snapshot(replay_parent, replay_state, events[tick - 1], replay_projection, replay_feature)
        if replay.content_root != snapshot.content_root or replay.continuation_root != snapshot.continuation_root or replay.receipt72 != snapshot.receipt72:
            raise AssertionError(f"deterministic replay failed at generation {tick}")
        replay_parent = replay

    # Parent-addressed branching.
    branch_parent = snapshots[len(snapshots) // 2]
    branch_projection = build_projection(branch_parent.state)
    branch_features = full_features(branch_parent.state)
    branch_events_a = (Event(3, 1), Event(17, 242))
    branch_events_b = (Event(3, 2), Event(17, 241))
    state_a, _, _ = evolve_state(branch_parent.state, branch_events_a, full_scan=False)
    state_b, _, _ = evolve_state(branch_parent.state, branch_events_b, full_scan=False)
    snap_a = make_snapshot(branch_parent, state_a, branch_events_a, build_projection(state_a), full_features(state_a))
    snap_b = make_snapshot(branch_parent, state_b, branch_events_b, build_projection(state_b), full_features(state_b))
    if snap_a.continuation_root == snap_b.continuation_root or snap_a.parent_continuation_root != snap_b.parent_continuation_root:
        raise AssertionError("branch continuation identity failed")
    if branch_parent.state != snapshots[len(snapshots) // 2].state:
        raise AssertionError("branch mutated parent")

    # Same visible state with different hidden physics/policy remains non-fungible.
    hidden_a = list(branch_parent.state)
    hidden_b = list(branch_parent.state)
    d = unpack_cell(hidden_b[0])
    d["policy"] = (d["policy"] + 1) % 4096
    hidden_b[0] = pack_cell(**d)
    if visual_root(hidden_a) != visual_root(hidden_b):
        raise AssertionError("hidden-state visual equivalence fixture failed")
    if state_content_root(hidden_a) == state_content_root(hidden_b):
        raise AssertionError("hidden-state non-fungibility failed")

    # Same content reached from different parents has one content root but distinct continuation roots.
    target_state = branch_parent.state
    parent_a = snapshots[max(0, len(snapshots) // 3)]
    parent_b = snapshots[max(1, len(snapshots) // 3 + 1)]
    target_projection = build_projection(target_state)
    target_features = full_features(target_state)
    lineage_a = make_snapshot(parent_a, target_state, (), target_projection, target_features)
    lineage_b = make_snapshot(parent_b, target_state, (), target_projection, target_features)
    if lineage_a.content_root != lineage_b.content_root or lineage_a.continuation_root == lineage_b.continuation_root:
        raise AssertionError("content/continuation identity separation failed")

    dense_state_bytes = ticks * CELLS * 8
    dense_projection_bytes = ticks * CELLS * CHANNELS * 4
    delta_projection_bytes = sum(count * CHANNELS * 4 for count in projection_counts)
    return {
        "status": "PASS",
        "seed": seed,
        "ticks": ticks,
        "final_content_root216": snapshots[-1].content_root.hex(),
        "final_continuation_root216": snapshots[-1].continuation_root.hex(),
        "final_receipt72": snapshots[-1].receipt72.hex(),
        "full_seconds": full_seconds,
        "delta_seconds": delta_seconds,
        "speedup": full_seconds / max(delta_seconds, 1e-12),
        "changed_cells_mean": statistics.mean(changed_counts),
        "changed_cells_p95": sorted(changed_counts)[max(0, int(0.95 * len(changed_counts)) - 1)],
        "projection_dirty_mean": statistics.mean(projection_counts),
        "projection_dirty_p95": sorted(projection_counts)[max(0, int(0.95 * len(projection_counts)) - 1)],
        "hydration_addresses_mean": statistics.mean(hydration_counts),
        "dense_state_bytes": dense_state_bytes,
        "delta_state_payload_bytes": delta_payload_bytes,
        "state_payload_reduction": dense_state_bytes / max(delta_payload_bytes, 1),
        "dense_projection_bytes": dense_projection_bytes,
        "delta_projection_bytes": delta_projection_bytes,
        "projection_payload_reduction": dense_projection_bytes / max(delta_projection_bytes, 1),
        "snapshots": len(snapshots),
        "replay_generations": ticks,
    }


def test_vector_retrieval(seed: int, branches: int = 8, snapshots_per_branch: int = 80, queries: int = 120) -> Dict[str, object]:
    rng = random.Random(seed ^ 0xC0FFEE)
    database: List[Snapshot] = []
    for branch in range(branches):
        compatibility = SCHEMA_ID if branch < branches - 2 else f"INCOMPATIBLE_{branch}"
        state = initial_state(seed + branch * 1009)
        projection = build_projection(state)
        features = full_features(state)
        parent = make_snapshot(None, state, (), projection, features, compatibility)
        database.append(parent)
        stream = event_stream(seed + branch * 313, snapshots_per_branch)
        for events in stream:
            state, _, dirty = evolve_state(state, events, full_scan=False)
            projection = update_projection(projection, state, dirty)
            features = full_features(state)
            parent = make_snapshot(parent, state, events, projection, features, compatibility)
            database.append(parent)

    compatible = [snapshot for snapshot in database if snapshot.compatibility == SCHEMA_ID]
    recall = 0
    exact_selected = 0
    distances: List[int] = []
    for _ in range(queries):
        base = rng.choice(compatible)
        query_events = tuple(Event(cell, rng.randrange(CONTROLS)) for cell in rng.sample(range(CELLS), 2))
        query_state, _, _ = evolve_state(base.state, query_events, full_scan=False)
        selected, hit, distance = nearest_compatible(query_state, database, SCHEMA_ID, top_k=32)
        recall += int(hit)
        distances.append(distance)
        # Exact selected parent is always continuation-compatible and should reconstruct a child.
        query_projection = build_projection(query_state)
        query_features = full_features(query_state)
        continuation = make_snapshot(selected, query_state, query_events, query_projection, query_features, SCHEMA_ID)
        if apply_delta(selected.state, continuation.delta) != query_state:
            raise AssertionError("retrieved-parent continuation reconstruction failed")
        exact_selected += 1

    recall_rate = recall / queries
    if recall_rate < 0.95:
        raise AssertionError(f"vector shortlist recall below threshold: {recall_rate:.4f}")
    return {
        "status": "PASS",
        "database_snapshots": len(database),
        "compatible_snapshots": len(compatible),
        "queries": queries,
        "top_k": 32,
        "exact_rerank_recall": recall_rate,
        "continuations_constructed": exact_selected,
        "selected_delta_bits_mean": statistics.mean(distances),
        "selected_delta_bits_p95": sorted(distances)[max(0, int(0.95 * len(distances)) - 1)],
    }


def test_negative_guards(seed: int) -> Dict[str, object]:
    rejected = 0
    for fn, args in (
        (q_from_sg, (-1, 0)),
        (q_from_sg, (STATE_BITS, 0)),
        (q_from_sg, (0, CONTROLS)),
        (sg_from_q, (-1,)),
        (sg_from_q, (HYDRATION_CAPACITY,)),
        (decode_trits, (-1,)),
        (decode_trits, (CONTROLS,)),
        (encode_trits, ((0, 1, 2, 0),)),
        (encode_trits, ((0, 1, 2, 0, 3),)),
    ):
        try:
            fn(*args)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError(f"negative guard failed for {fn.__name__}{args}")

    state = initial_state(seed)
    projection = build_projection(state)
    features = full_features(state)
    parent = make_snapshot(None, state, (), projection, features)
    events = (Event(0, encode_trits((1, 1, 1, 1, 2))),)
    child_state, changed, dirty = evolve_state(state, events, full_scan=False)
    child_projection = update_projection(projection, child_state, dirty)
    child_features = update_features(features, state, child_state, changed)
    child = make_snapshot(parent, child_state, events, child_projection, child_features)

    mutated = list(child_state)
    mutated[0] ^= 1 << POLICY_SHIFT
    mutated_projection = build_projection(mutated)
    mutated_features = full_features(mutated)
    mutated_child = make_snapshot(parent, tuple(mutated), events, mutated_projection, mutated_features)
    if child.content_root == mutated_child.content_root or child.continuation_root == mutated_child.continuation_root or child.receipt72 == mutated_child.receipt72:
        raise AssertionError("one-bit mutation did not change all continuation witnesses")

    alternate_state = initial_state(seed + 1)
    alternate_parent = make_snapshot(None, alternate_state, (), build_projection(alternate_state), full_features(alternate_state))
    wrong_lineage = make_snapshot(alternate_parent, child_state, events, child_projection, child_features)
    if wrong_lineage.continuation_root == child.continuation_root or wrong_lineage.receipt72 == child.receipt72:
        raise AssertionError("wrong parent lineage was not distinguished")

    # Omitting dependency-complete projection cells must be detectable.
    dependency_detected = False
    for source_cell in range(CELLS):
        light_state = list(state)
        light_data = unpack_cell(light_state[source_cell])
        light_data["emission"] = 255
        light_data["hue"] = (light_data["hue"] + 127) % 256
        light_state[source_cell] = pack_cell(**light_data)
        light_state_tuple = tuple(light_state)
        full_light_projection = build_projection(light_state_tuple)
        affected = [i for i in range(CELLS) if full_light_projection[i] != projection[i]]
        if any(i != source_cell for i in affected):
            insufficient_projection = update_projection(projection, light_state_tuple, (source_cell,))
            if insufficient_projection == full_light_projection:
                raise AssertionError("incomplete projection frontier was not detected")
            dependency_detected = True
            break
    if not dependency_detected:
        raise AssertionError("lighting dependency fixture could not be constructed")

    incompatible_exact = make_snapshot(None, child_state, (), child_projection, child_features, "INCOMPATIBLE_EXACT")
    compatible_other = parent
    selected, _, _ = nearest_compatible(child_state, (incompatible_exact, compatible_other), SCHEMA_ID, top_k=2)
    if selected.compatibility != SCHEMA_ID or selected.continuation_root == incompatible_exact.continuation_root:
        raise AssertionError("compatibility membrane failed during vector retrieval")

    return {
        "status": "PASS",
        "invalid_inputs_rejected": rejected,
        "mutation_sensitivity": "PASS",
        "wrong_parent_rejected_by_identity": "PASS",
        "incomplete_projection_frontier_detected": "PASS",
        "incompatible_vector_candidate_rejected": "PASS",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticks", type=int, default=1200)
    parser.add_argument("--seeds", default="1,72,216,5184,1259713")
    parser.add_argument("--output", type=Path, default=Path("pass205_multimodal_continuation_design_results.json"))
    args = parser.parse_args()

    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    started = time.perf_counter()
    dimensions = test_dimensions()
    pack = test_pack_roundtrip(seeds[0])
    workloads = [run_workload(seed, args.ticks) for seed in seeds]
    retrieval = test_vector_retrieval(seeds[-1])
    negative_guards = test_negative_guards(seeds[0])
    result = {
        "schema": "HHS_PASS_205_MULTIMODAL_CONTINUATION_DESIGN_VALIDATION_V1",
        "classification": "HHS_PASS_205_DESIGN_VALIDATION_PASSED",
        "digest_transport": "standalone fixed-width BLAKE2b witnesses; production inherits repository Hash216/Hash72/VM81",
        "dimensions": dimensions,
        "pack_roundtrip": pack,
        "workloads": workloads,
        "vector_retrieval": retrieval,
        "negative_guards": negative_guards,
        "aggregate": {
            "seeds": seeds,
            "ticks_per_seed": args.ticks,
            "total_ticks": len(seeds) * args.ticks,
            "speedup_mean": statistics.mean(item["speedup"] for item in workloads),
            "speedup_min": min(item["speedup"] for item in workloads),
            "changed_cells_mean": statistics.mean(item["changed_cells_mean"] for item in workloads),
            "projection_dirty_mean": statistics.mean(item["projection_dirty_mean"] for item in workloads),
            "state_payload_reduction_mean": statistics.mean(item["state_payload_reduction"] for item in workloads),
            "projection_payload_reduction_mean": statistics.mean(item["projection_payload_reduction"] for item in workloads),
            "elapsed_seconds": time.perf_counter() - started,
        },
        "tests": {
            "dimension_and_address_closure": "PASS",
            "five_trit_control_bijection": "PASS",
            "cell_pack_roundtrip": "PASS",
            "deterministic_full_delta_equivalence": "PASS",
            "fixed_point_3d_geometry": "PASS",
            "collision_consistency": "PASS",
            "lighting_and_color_consistency": "PASS",
            "thirty_two_channel_projection": "PASS",
            "incremental_ml_feature_hydration": "PASS",
            "persistent_continuation_lineage": "PASS",
            "xor_reversible_delta": "PASS",
            "branch_independence": "PASS",
            "visual_equivalence_hidden_state_nonfungibility": "PASS",
            "same_content_distinct_lineage": "PASS",
            "deterministic_replay": "PASS",
            "vector_candidate_compatibility": "PASS",
            "nearest_snapshot_exact_rerank": "PASS",
            "invalid_coordinate_rejection": "PASS",
            "one_bit_mutation_sensitivity": "PASS",
            "wrong_parent_lineage_rejection": "PASS",
            "incomplete_projection_frontier_detection": "PASS",
            "incompatible_vector_candidate_rejection": "PASS",
        },
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

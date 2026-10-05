"""Pass 220 I080 — BigInt/memristor Hash216 deterministic probability synthesis.

I080 binds the canonical I041 browser seed in examples/ParticleSimulation.html
to the already-merged exact substrates that make its Lane-5 state reusable:

* 81 x 64 = 5184 fixed-width BigInt/VM81 serialization;
* Pass 163 exact path-dependent virtual-memristor state;
* Pass 220 I065 three-plane Hash216 hydration;
* deterministic, replayable probability/event synthesis.

The browser seed intentionally contains Math.random()-based projection/demo
sampling.  I080 does not promote that host PRNG to authority.  The exact Lane-5
sampler is derived only from Hash216 + typed graph state using domain-separated
SHA-256 and rejection sampling.  Same admitted inputs therefore replay
bit-for-bit; changed Hash216/graph state changes the synthesized schedule.

This module is candidate/read-only with respect to shared VM81/Hash72/Hash216
state.  It creates an isolated in-memory Pass-163 runtime solely to execute and
witness memristor semantics.  No repository-global VMRC, canonical VM81,
Hash72/Hash216 commit, persistence, GPU, float, or browser Math.random authority
is granted.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha1, sha256
import json
from math import lcm
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    HASH216_LEN,
    coordinate_5184,
    split_hash216,
)
from hhs_runtime.hhs_pass220_i065_lossless_emergent_compression_hydration_v1 import (
    FULL_HASH216_COMPONENTS,
    hydrate_hash216_geometry,
    validate_serialized5184,
)
from hhs_runtime.hhs_pass220_i069_harmonicode_i_tensor_v1 import hash72
from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    SERIALIZED_CHARACTERS,
    VM81_CELLS,
    serialize_offsets_5184,
)
from hhs_runtime.pass163 import VMRCRuntime
from hhs_runtime.pass219.fold_primitive_probe import (
    ab_p4_probe,
    directed_ratio_flip,
    pair_flip,
)

SCHEMA = "HHS_PASS_220_I080_BIGINT_MEMRISTOR_HASH216_PROBABILITY_SYNTHESIS_V1"
VERSION = "1.0.0"
PROFILE = "PASS220-I080-BIGINT-MEMRISTOR-QPU-PROBABILITY-v1"

HASH72_WIDTH = 72
HASH216_WIDTH = 216
VM81_THREADS = 64
VM81_COORDINATES = VM81_CELLS * VM81_THREADS
PARTICLE_LATTICE = 2 * VM81_COORDINATES  # I041 twin 5184 lattice = 10368
Q144 = 144
RING72 = 72
UINT256_MODULUS = 1 << 256

REPO_ROOT = Path(__file__).resolve().parents[1]

I041_SOURCE_PATH = "examples/ParticleSimulation.html"
I041_SOURCE_GIT_BLOB_SHA = "218d89d67803b5b10ab86b1cdb97434438e25082"

I041_DOC_PATH = "docs/pass220/PASS_220_I041_HOLOFRACTAL_RELATIVISTIC_GAME_ENGINE.md"
I041_DOC_GIT_BLOB_SHA = "5dd0a44953ff6c8afa4558627caa584b55ff3366"

P163_VMRC_PATH = "hhs_runtime/pass163/vmrc.py"
P163_VMRC_GIT_BLOB_SHA = "9bdcab13739e98ad4189c5d2a6e5ee001fce17a2"

I065_PATH = "hhs_runtime/hhs_pass220_i065_lossless_emergent_compression_hydration_v1.py"
I065_GIT_BLOB_SHA = "fc998ef613c9d22c6f105016a649d4d96bc5e766"

FOLD_PROBE_PATH = "hhs_runtime/pass219/fold_primitive_probe.py"
FOLD_PROBE_GIT_BLOB_SHA = "d72d6fe3d994ecab77aad31828fbe82e87141b48"

HNAN_GATE_PATH = "hhs_runtime/pass219/hnan_4x4_recursive_gate_v1.py"
HNAN_GATE_GIT_BLOB_SHA = "a0ccd47620301ef2cc864e9e86834c8608b7b200"

LOSHU_SERIALIZER_PATH = "hhs_runtime/hhs_pass220_lo_shu_normalization_v1.py"
LOSHU_SERIALIZER_GIT_BLOB_SHA = "cb18ec3f1d35017cb6c7b2b40848b398930270bc"

I041_MARKERS = (
    "function computeManifoldHash()",
    "function virtualDecay(forceIdx)",
    "const fractalSeeds=[];",
    "const CONSTRUCTOR_CYCLE=72;",
    "const MEMW=8;",
    "const respawnRing=new Int32Array(CONSTRUCTOR_CYCLE).fill(-1);",
    "const CORE_N = 2592, EXC_N = 324;",
    "const LAYER_SPLIT=CORE_N+8*EXC_N;",
    "function fractalLayer2Receipt()",
    "function hnanGate(a,b)",
    "function composeBlock648(n)",
    "Math.random()",
)

AUTHORITY = {
    "candidate_only": True,
    "i041_browser_seed_is_semantic_source": True,
    "browser_math_random_authority": False,
    "deterministic_probability_authority": True,
    "deterministic_probability_domain": "I080_CANDIDATE_ONLY",
    "isolated_vmrc_execution_allowed": True,
    "shared_vmrc_mutation_authority": False,
    "canonical_vm81_mutation_authority": False,
    "canonical_hash72_commit_authority": False,
    "canonical_hash216_commit_authority": False,
    "canonical_hash216_persistence_authority": False,
    "gpu_float_authority": False,
    "host_float_probability_authority": False,
    "external_egress_authority": False,
}


class Pass220I080Error(ValueError):
    """Fail-closed I080 validation error."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return sha256(value if isinstance(value, bytes) else _canonical(value)).hexdigest()


def _git_blob_sha(raw: bytes) -> str:
    return sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _read_blob_bound(relative_path: str, expected_sha: str) -> str:
    raw = (REPO_ROOT / relative_path).read_bytes()
    actual = _git_blob_sha(raw)
    if actual != expected_sha:
        raise Pass220I080Error(
            f"source blob drift at {relative_path}: {actual} != {expected_sha}"
        )
    return raw.decode("utf-8")


def source_bindings() -> dict[str, Any]:
    i041 = _read_blob_bound(I041_SOURCE_PATH, I041_SOURCE_GIT_BLOB_SHA)
    i041_doc = _read_blob_bound(I041_DOC_PATH, I041_DOC_GIT_BLOB_SHA)
    p163 = _read_blob_bound(P163_VMRC_PATH, P163_VMRC_GIT_BLOB_SHA)
    i065 = _read_blob_bound(I065_PATH, I065_GIT_BLOB_SHA)
    fold_probe = _read_blob_bound(FOLD_PROBE_PATH, FOLD_PROBE_GIT_BLOB_SHA)
    hnan_gate = _read_blob_bound(HNAN_GATE_PATH, HNAN_GATE_GIT_BLOB_SHA)
    serializer = _read_blob_bound(
        LOSHU_SERIALIZER_PATH,
        LOSHU_SERIALIZER_GIT_BLOB_SHA,
    )

    missing = tuple(marker for marker in I041_MARKERS if marker not in i041)
    if missing:
        raise Pass220I080Error(f"I041 source markers missing: {missing!r}")
    if "provenance-bearing knowledge graph" not in i041_doc:
        raise Pass220I080Error("I041 knowledge-graph contract marker missing")
    if "path-dependent exact memristor state" not in p163:
        raise Pass220I080Error("Pass 163 exact memristor marker missing")
    if "hydrate_hash216_geometry" not in i065:
        raise Pass220I080Error("I065 Hash216 hydration marker missing")
    for marker in ("AB_RATIO_FORWARD = \"A/B\"", "AB_RATIO_REVERSE = \"B/A\"", "COMMUTATIVE_P4_SHADOW = \"AB=P^4\"", "phase_inversion_steps"):
        if marker not in fold_probe:
            raise Pass220I080Error(f"fold primitive marker missing: {marker}")
    for marker in ("HNAN", "PHASE_MODULUS", "xy", "yx", "zw", "wz"):
        if marker not in hnan_gate:
            raise Pass220I080Error(f"HNAN gate marker missing: {marker}")
    if "def serialize_offsets_5184" not in serializer:
        raise Pass220I080Error("5184 BigInt serializer marker missing")

    return {
        "schema": f"{SCHEMA}_SOURCE_BINDINGS_V1",
        "i041_browser_seed": {
            "path": I041_SOURCE_PATH,
            "git_blob_sha": I041_SOURCE_GIT_BLOB_SHA,
            "math_random_occurrences": i041.count("Math.random()"),
            "math_random_authority": False,
            "marker_count": len(I041_MARKERS),
        },
        "i041_knowledge_graph_doc": {
            "path": I041_DOC_PATH,
            "git_blob_sha": I041_DOC_GIT_BLOB_SHA,
        },
        "pass163_vmrc": {
            "path": P163_VMRC_PATH,
            "git_blob_sha": P163_VMRC_GIT_BLOB_SHA,
            "exact_memristor": True,
        },
        "i065_hash216_hydration": {
            "path": I065_PATH,
            "git_blob_sha": I065_GIT_BLOB_SHA,
        },
        "fold_primitive": {
            "path": FOLD_PROBE_PATH,
            "git_blob_sha": FOLD_PROBE_GIT_BLOB_SHA,
            "directed_ratio_pair": ("A/B", "B/A"),
            "closure": "AB=P^4",
            "u36_half_turn": True,
        },
        "hnan_gate": {
            "path": HNAN_GATE_PATH,
            "git_blob_sha": HNAN_GATE_GIT_BLOB_SHA,
            "phase_modulus": 72,
        },
        "bigint_5184_serializer": {
            "path": LOSHU_SERIALIZER_PATH,
            "git_blob_sha": LOSHU_SERIALIZER_GIT_BLOB_SHA,
        },
    }


def default_seed_hash216() -> str:
    """Bind the four repository source identities into one valid Hash216 seed."""
    bindings = source_bindings()
    lanes = (
        hash72({"role": "state", "source": bindings["i041_browser_seed"]}),
        hash72({"role": "graph", "source": bindings["pass163_vmrc"]}),
        hash72({
            "role": "receipt",
            "hydration": bindings["i065_hash216_hydration"],
            "serializer": bindings["bigint_5184_serializer"],
        }),
    )
    seed = "".join(lanes)
    if len(seed) != HASH216_WIDTH:
        raise Pass220I080Error("default Hash216 seed width drift")
    hydrate_hash216_geometry(seed)
    return seed


def _seed_bytes(
    hash216: str,
    *,
    domain: str,
    graph_root: str = "",
    epoch: int = 0,
) -> bytes:
    if len(hash216) != HASH216_LEN:
        raise Pass220I080Error("Hash216 seed must contain exactly 216 symbols")
    split_hash216(hash216)  # validates lane alphabet/geometry
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise Pass220I080Error("epoch must be a nonnegative exact integer")
    return _canonical({
        "schema": SCHEMA,
        "hash216": hash216,
        "domain": domain,
        "graph_root": graph_root,
        "epoch": epoch,
    })


def _u256(
    seed: bytes,
    *,
    label: str,
    index: int,
    attempt: int = 0,
) -> int:
    if not isinstance(index, int) or isinstance(index, bool) or index < 0:
        raise Pass220I080Error("sample index must be a nonnegative exact integer")
    if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 0:
        raise Pass220I080Error("sample attempt must be a nonnegative exact integer")
    digest = sha256(
        b"HHS-P220-I080-PRNG-V1\0"
        + seed
        + b"\0"
        + label.encode("utf-8")
        + b"\0"
        + index.to_bytes(16, "big")
        + attempt.to_bytes(8, "big")
    ).digest()
    return int.from_bytes(digest, "big")


def sample_below(
    hash216: str,
    bound: int,
    *,
    label: str,
    index: int,
    graph_root: str = "",
    epoch: int = 0,
) -> dict[str, Any]:
    """Unbiased deterministic integer in [0,bound) via SHA-256 rejection."""
    if not isinstance(bound, int) or isinstance(bound, bool) or bound <= 0:
        raise Pass220I080Error("bound must be a positive exact integer")
    seed = _seed_bytes(
        hash216,
        domain="SAMPLE_BELOW",
        graph_root=graph_root,
        epoch=epoch,
    )
    limit = UINT256_MODULUS - (UINT256_MODULUS % bound)
    attempt = 0
    while True:
        value = _u256(seed, label=label, index=index, attempt=attempt)
        if value < limit:
            return {
                "value": value % bound,
                "bound": bound,
                "attempt": attempt,
                "raw_u256": value,
                "uniform_rational": (
                    str(value),
                    str(UINT256_MODULUS),
                ),
                "rejection_limit": limit,
                "float_authority": False,
            }
        attempt += 1
        if attempt > 1024:
            raise Pass220I080Error("deterministic rejection sampler did not converge")


def _exact_weighted_choice(
    hash216: str,
    weights: Sequence[Fraction],
    *,
    label: str,
    index: int,
    graph_root: str,
) -> dict[str, Any]:
    if not weights or any(weight <= 0 for weight in weights):
        raise Pass220I080Error("weighted choice requires positive exact weights")
    denominator_lcm = 1
    for weight in weights:
        denominator_lcm = lcm(denominator_lcm, weight.denominator)
    integers = tuple(
        weight.numerator * (denominator_lcm // weight.denominator)
        for weight in weights
    )
    total = sum(integers)
    draw = sample_below(
        hash216,
        total,
        label=label,
        index=index,
        graph_root=graph_root,
    )
    cursor = 0
    chosen = None
    for position, weight in enumerate(integers):
        cursor += weight
        if draw["value"] < cursor:
            chosen = position
            break
    if chosen is None:
        raise AssertionError("weighted choice failed to choose")
    probability = Fraction(integers[chosen], total)
    return {
        "index": chosen,
        "draw": draw["value"],
        "integer_total": total,
        "integer_weight": integers[chosen],
        "probability": (str(probability.numerator), str(probability.denominator)),
        "float_authority": False,
    }


def bigint_serialization_layer(hash216: str) -> dict[str, Any]:
    """Derive 81 exact 0..8 offsets and serialize the canonical 5184 carrier."""
    offsets = tuple(
        sample_below(
            hash216,
            9,
            label="BIGINT_OFFSET",
            index=cell,
        )["value"]
        for cell in range(VM81_CELLS)
    )
    serialized = serialize_offsets_5184(offsets)
    recovered = validate_serialized5184(serialized)
    if tuple(recovered) != offsets:
        raise Pass220I080Error("BigInt 5184 serialization roundtrip mismatch")
    cells = []
    for cell, offset in enumerate(offsets):
        start = cell * VM81_THREADS
        end = start + VM81_THREADS
        cells.append({
            "cell81": cell,
            "offset": offset,
            "block_start": start,
            "block_end_exclusive": end,
            "block_width": VM81_THREADS,
            "first_coordinate": coordinate_5184(start),
            "last_coordinate": coordinate_5184(end - 1),
        })
    return {
        "schema": f"{SCHEMA}_BIGINT_LAYER_V1",
        "offsets81": offsets,
        "serialized5184": serialized,
        "serialized_characters": len(serialized),
        "cells": tuple(cells),
        "serialized_sha256": sha256(serialized.encode("utf-8")).hexdigest(),
        "roundtrip_exact": True,
    }


def memristor_knowledge_graph(
    hash216: str,
    bigint_layer: Mapping[str, Any],
) -> dict[str, Any]:
    """Execute a private Pass-163 graph with exact, path-dependent edge updates."""
    runtime = VMRCRuntime()
    final_edges = []
    receipts = []
    for cell in bigint_layer["cells"]:
        cell81 = int(cell["cell81"])
        offset = int(cell["offset"])
        source = f"vm81:{cell81}"
        target = f"hash216-vertex:{cell81 % RING72}"
        polarity = 1 if (offset + cell81) % 2 == 0 else -1

        first = runtime.propose_memristor(
            source,
            target,
            conductance=Fraction(offset + 1, 9),
            polarity=polarity,
        )
        first_admitted = runtime.admit_memristor(first)

        lane_digit = sample_below(
            hash216,
            9,
            label="MEMRISTOR_REUSE",
            index=cell81,
        )["value"]
        second = runtime.propose_memristor(
            source,
            target,
            conductance=Fraction(lane_digit + 1, 9),
            polarity=polarity,
            prior_identity=first.identity,
        )
        second_admitted = runtime.admit_memristor(second)
        edge = second_admitted["edge"]
        if edge["reuse_count"] != 1:
            raise Pass220I080Error("memristor path-dependent reuse count drift")
        final_edges.append({
            "cell81": cell81,
            "source": source,
            "target": target,
            "identity": edge["identity"],
            "hash216_vector": edge["hash216_vector"],
            "conductance": edge["conductance"],
            "resistance": edge["resistance"],
            "polarity": edge["polarity"],
            "reuse_count": edge["reuse_count"],
            "history": tuple(edge["admitted_history"]),
        })
        receipts.append(second_admitted["receipt"])

    status = runtime.status()
    graph_root = sha256(_canonical(final_edges)).hexdigest()
    if len(final_edges) != VM81_CELLS:
        raise Pass220I080Error("memristor graph must contain one final edge per VM81 cell")
    if status["coordinates"] != VM81_COORDINATES:
        raise Pass220I080Error("isolated VMRC coordinate geometry drift")

    return {
        "schema": f"{SCHEMA}_MEMRISTOR_GRAPH_V1",
        "edge_count": len(final_edges),
        "edges": tuple(final_edges),
        "graph_root_sha256": graph_root,
        "vmrc_index_head": status["index_head_hash216"],
        "vmrc_state_hash72": status["state_hash72"],
        "receipt_count": len(receipts),
        "path_dependent_reuse_exact": all(
            edge["reuse_count"] == 1 and len(edge["history"]) == 1
            for edge in final_edges
        ),
        "isolated_ephemeral_runtime": True,
        "isolated_runtime_internal_mutation_authority": status["mutation_authority"],
        "shared_or_canonical_mutation_authority": False,
    }


def lane5_tick_optimization_operation(
    tick: int,
    *,
    P: int = 5,
    A: int = 5,
    B: int = 125,
) -> dict[str, Any]:
    """Execute one exact Lane-5 optimization witness for one simulation tick.

    The tick operation is a typed reciprocal phase inversion, not a
    commutative rewrite.  It preserves the ordered A/B:B/A roles; flips the
    (a,b), (x,y), (z,w), and (p,q) role pairs as order-2 operations; carries
    the inherited AB=P^4 closure witness; and records the concave/convex
    reciprocal topology as exact rational duals.

    The phase ring is Z_72.  u^36 is the reciprocal half-turn and is
    self-inverse.  The larger 5184 geometry closes at the same phase because
    5184 = 81*64 = 72^2 and 5184 mod 72 = 0.  The 72^72 saturation exponent
    also lands at residue zero mod 72.  These exact modular closures are
    recorded as the I080 HNAN periodicity witness; no scalar cancellation,
    commutation, float authority, or canonical mutation follows from it.
    """
    if not isinstance(tick, int) or isinstance(tick, bool) or tick < 0:
        raise Pass220I080Error("tick must be a nonnegative exact integer")

    closure = ab_p4_probe(P, A, B)
    if closure["AB_equals_P4"] is not True:
        raise Pass220I080Error("AB=P^4 closure failed")

    ratio_before = "A/B"
    ratio_after = directed_ratio_flip(ratio_before)
    if ratio_after != "B/A" or directed_ratio_flip(ratio_after) != ratio_before:
        raise Pass220I080Error("A/B:B/A reciprocal inversion failed")

    pair_roles = {
        "a:b": ("a", "b"),
        "x:y": ("x", "y"),
        "z:w": ("z", "w"),
        "p:q": ("p", "q"),
    }
    pair_inversions = {}
    for name, pair in pair_roles.items():
        once = pair_flip(*pair)
        twice = pair_flip(*once)
        if twice != pair:
            raise Pass220I080Error(f"{name} pair inversion is not order-2")
        pair_inversions[name] = {
            "before": pair,
            "after": once,
            "restored": twice,
            "order_2": True,
        }

    # Exact reciprocal topology dual: concave * convex = 1.
    # The tick chooses an exact interior rational displacement; no float is
    # used and the two topology views remain reciprocal rather than merged.
    radius2 = Fraction(9, 1)
    displacement2 = Fraction((tick % 8) + 1, 9)
    concave = radius2 / (radius2 - displacement2)
    convex = (radius2 - displacement2) / radius2
    if concave * convex != 1:
        raise Pass220I080Error("concave/convex reciprocal topology failed")

    phase = tick % RING72
    reciprocal_phase = (phase + 36) % RING72
    restored_phase = (reciprocal_phase + 36) % RING72
    if restored_phase != phase:
        raise Pass220I080Error("u^36 half-turn did not self-invert")

    geometry_index = tick % VM81_COORDINATES
    coordinate = coordinate_5184(geometry_index)
    period_5184 = (phase + VM81_COORDINATES) % RING72
    saturation_mod72 = pow(RING72, RING72, RING72)
    period_72pow72 = (phase + saturation_mod72) % RING72
    hnan_periodic = (
        VM81_COORDINATES == 81 * 64 == RING72 * RING72
        and VM81_COORDINATES % RING72 == 0
        and saturation_mod72 == 0
        and period_5184 == phase
        and period_72pow72 == phase
    )
    if not hnan_periodic:
        raise Pass220I080Error("HNAN Z72 periodicity witness failed")

    return {
        "schema": f"{SCHEMA}_LANE5_TICK_OPERATION_V1",
        "tick": tick,
        "one_tick_one_lane5_optimization_operation": True,
        "operation_index_5184": geometry_index,
        "coordinate_5184": coordinate,
        "directed_ratio_phase_inversion": {
            "before": ratio_before,
            "after": ratio_after,
            "restored_after_second_inversion": directed_ratio_flip(ratio_after),
            "ordered_roles_preserved": True,
            "commutative_cancellation_permitted": False,
        },
        "typed_pair_phase_inversions": pair_inversions,
        "concave_convex_geometry_phase_inversion": {
            "before": "CONCAVE",
            "after": "CONVEX",
            "concave_exact": (str(concave.numerator), str(concave.denominator)),
            "convex_exact": (str(convex.numerator), str(convex.denominator)),
            "reciprocal_product_exact": True,
            "next_inversion_restores": "CONCAVE",
        },
        "AB_P4_closure": {
            "source": closure["commutative_shadow_source"],
            "directional_source": closure["directional_closure_source"],
            "P": closure["P"],
            "A": closure["A"],
            "B": closure["B"],
            "P4": closure["P4"],
            "AB_equals_P4": closure["AB_equals_P4"],
            "full_directional_closure_scalarized": False,
        },
        "phase_ring": {
            "phase_modulus": RING72,
            "u_tick": phase,
            "u36_reciprocal": reciprocal_phase,
            "u36_twice_restores": restored_phase == phase,
            "u72_is_u0": (phase + RING72) % RING72 == phase,
        },
        "hnan_periodicity": {
            "source_expression": "u^(5184=81*64=72²/72⁷²MOD72)=HNAN periodicity",
            "geometry_5184": VM81_COORDINATES,
            "81x64": 81 * 64,
            "72_squared": RING72 * RING72,
            "5184_mod_72": VM81_COORDINATES % RING72,
            "72_pow_72_mod_72": saturation_mod72,
            "u_tick_plus_5184_restores": period_5184 == phase,
            "u_tick_plus_72pow72_mod72_restores": period_72pow72 == phase,
            "passes": hnan_periodic,
        },
        "authority": {
            "optimization_projection_only": True,
            "canonical_vm81_mutation_authority": False,
            "canonical_hash72_commit_authority": False,
            "canonical_hash216_commit_authority": False,
            "floating_point_authority": False,
        },
    }


def probability_synthesis_layer(
    hash216: str,
    bigint_layer: Mapping[str, Any],
    graph: Mapping[str, Any],
    *,
    events: int = RING72,
) -> dict[str, Any]:
    """Synthesize a deterministic holographic event schedule with exact weights."""
    if not isinstance(events, int) or isinstance(events, bool) or not 1 <= events <= 5184:
        raise Pass220I080Error("events must be an exact integer in [1,5184]")
    weights = tuple(
        Fraction(int(edge["conductance"].split("/")[0]), int(edge["conductance"].split("/")[1]))
        if "/" in edge["conductance"]
        else Fraction(int(edge["conductance"]), 1)
        for edge in graph["edges"]
    )
    if len(weights) != VM81_CELLS:
        raise Pass220I080Error("probability weights must cover 81 VM81 cells")

    schedule = []
    for event in range(events):
        graph_choice = _exact_weighted_choice(
            hash216,
            weights,
            label="GRAPH_WEIGHTED_CELL",
            index=event,
            graph_root=graph["graph_root_sha256"],
        )
        cell81 = graph_choice["index"]
        operation64 = sample_below(
            hash216,
            VM81_THREADS,
            label="OPERATION64",
            index=event,
            graph_root=graph["graph_root_sha256"],
        )["value"]
        linear5184 = cell81 * VM81_THREADS + operation64
        victim = sample_below(
            hash216,
            PARTICLE_LATTICE,
            label="I041_VIRTUAL_DECAY_VICTIM",
            index=event,
            graph_root=graph["graph_root_sha256"],
        )
        phase144 = sample_below(
            hash216,
            Q144,
            label="Q144_PHASE",
            index=event,
            graph_root=graph["graph_root_sha256"],
        )
        seed_lane = event % 3
        hash72_vertex = event % RING72
        coordinate = coordinate_5184(linear5184)
        tick_operation = lane5_tick_optimization_operation(event)
        schedule.append({
            "event": event,
            "lane5_tick_operation": tick_operation,
            "cell81": cell81,
            "operation64": operation64,
            "linear5184": linear5184,
            "coordinate": coordinate,
            "graph_choice": graph_choice,
            "victim10368": victim["value"],
            "victim_probability_per_turn": ("1", str(PARTICLE_LATTICE)),
            "phase144": phase144["value"],
            "hash216_plane": seed_lane,
            "hash72_vertex": hash72_vertex,
            "fractal_seed_seal": (event + 1) % RING72 == 0,
        })

    schedule_root = sha256(_canonical(schedule)).hexdigest()
    return {
        "schema": f"{SCHEMA}_PROBABILITY_LAYER_V1",
        "events": tuple(schedule),
        "event_count": len(schedule),
        "schedule_root_sha256": schedule_root,
        "one_tick_one_lane5_optimization_operation": all(
            event["lane5_tick_operation"]["one_tick_one_lane5_optimization_operation"]
            for event in schedule
        ),
        "A_over_B_B_over_A_phase_inversion_each_tick": all(
            event["lane5_tick_operation"]["directed_ratio_phase_inversion"]["after"] == "B/A"
            for event in schedule
        ),
        "AB_equals_P4_each_tick": all(
            event["lane5_tick_operation"]["AB_P4_closure"]["AB_equals_P4"]
            for event in schedule
        ),
        "HNAN_periodicity_each_tick": all(
            event["lane5_tick_operation"]["hnan_periodicity"]["passes"]
            for event in schedule
        ),
        "same_input_same_schedule": True,
        "browser_math_random_used": False,
        "exact_rational_probability": True,
        "rejection_sampling_unbiased_for_discrete_bounds": True,
        "i041_virtual_decay_rate_semantics": {
            "particles": PARTICLE_LATTICE,
            "probability_per_particle_per_turn": ("1", str(PARTICLE_LATTICE)),
            "scheduled_victims_per_turn": 1,
        },
        "ring72_seed_rule": "event 71 seals one deterministic (x,y):(z,w) bookkeeping seed",
    }


def build_candidate(seed_hash216: str | None = None) -> dict[str, Any]:
    seed = default_seed_hash216() if seed_hash216 is None else seed_hash216
    input_hydration = hydrate_hash216_geometry(seed)
    bindings = source_bindings()
    bigint = bigint_serialization_layer(seed)
    graph = memristor_knowledge_graph(seed, bigint)
    probability = probability_synthesis_layer(seed, bigint, graph)

    lanes = {
        "bigint_state": hash72({
            "serialized_sha256": bigint["serialized_sha256"],
            "offsets81": bigint["offsets81"],
        }),
        "memristor_graph": hash72({
            "graph_root_sha256": graph["graph_root_sha256"],
            "vmrc_index_head": graph["vmrc_index_head"],
            "vmrc_state_hash72": graph["vmrc_state_hash72"],
        }),
        "probability_schedule": hash72({
            "schedule_root_sha256": probability["schedule_root_sha256"],
            "event_count": probability["event_count"],
        }),
    }
    output_hash216 = "".join(lanes.values())
    if len(output_hash216) != HASH216_WIDTH:
        raise Pass220I080Error("output Hash216 width drift")
    output_hydration = hydrate_hash216_geometry(output_hash216)
    if output_hydration["full_attached_components"] != FULL_HASH216_COMPONENTS:
        raise Pass220I080Error("output Hash216 hydration component drift")

    candidate = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "source_bindings": bindings,
        "input_hash216": seed,
        "input_hash216_hydration_roundtrip": input_hydration["roundtrip_exact"],
        "bigint_layer": bigint,
        "memristor_graph": graph,
        "probability_synthesis": probability,
        "hash72_lanes": lanes,
        "candidate_hash216": output_hash216,
        "candidate_hash216_hydration": {
            "roundtrip_exact": output_hydration["roundtrip_exact"],
            "full_attached_components": output_hydration["full_attached_components"],
        },
        "authority": dict(AUTHORITY),
    }
    candidate["candidate_root_sha256"] = _sha256(candidate)
    return candidate


def validate_candidate(candidate: Mapping[str, Any]) -> bool:
    if not isinstance(candidate, Mapping) or candidate.get("schema") != SCHEMA:
        raise Pass220I080Error("candidate schema mismatch")
    seed = candidate.get("input_hash216")
    canonical = build_candidate(seed)
    if candidate != canonical:
        raise Pass220I080Error("candidate diverges from deterministic I080 reconstruction")
    return True


def self_test() -> dict[str, Any]:
    candidate = build_candidate()
    replay = build_candidate(candidate["input_hash216"])

    alternate_seed = (
        hash72({"alternate": 1, "prior": candidate["input_hash216"]})
        + candidate["input_hash216"][HASH72_WIDTH:2 * HASH72_WIDTH]
        + candidate["input_hash216"][2 * HASH72_WIDTH:]
    )
    alternate = build_candidate(alternate_seed)

    checks = {
        "candidate_valid": validate_candidate(candidate),
        "i041_source_blob_bound": (
            candidate["source_bindings"]["i041_browser_seed"]["git_blob_sha"]
            == I041_SOURCE_GIT_BLOB_SHA
        ),
        "browser_random_explicitly_non_authoritative": (
            candidate["source_bindings"]["i041_browser_seed"]["math_random_occurrences"] > 0
            and candidate["authority"]["browser_math_random_authority"] is False
        ),
        "bigint_width_5184": (
            candidate["bigint_layer"]["serialized_characters"] == SERIALIZED_CHARACTERS
        ),
        "bigint_81_cells": len(candidate["bigint_layer"]["cells"]) == VM81_CELLS,
        "vm81_blocks_cover_5184": (
            candidate["bigint_layer"]["cells"][0]["block_start"] == 0
            and candidate["bigint_layer"]["cells"][-1]["block_end_exclusive"] == 5184
        ),
        "memristor_edge_count_81": candidate["memristor_graph"]["edge_count"] == 81,
        "memristor_path_reuse_exact": (
            candidate["memristor_graph"]["path_dependent_reuse_exact"] is True
        ),
        "isolated_vmrc_only": (
            candidate["memristor_graph"]["isolated_ephemeral_runtime"] is True
            and candidate["memristor_graph"]["shared_or_canonical_mutation_authority"] is False
        ),
        "probability_72_events": (
            candidate["probability_synthesis"]["event_count"] == RING72
        ),
        "one_tick_one_lane5_optimization": (
            candidate["probability_synthesis"]["one_tick_one_lane5_optimization_operation"] is True
        ),
        "directed_ratio_phase_inversion_each_tick": (
            candidate["probability_synthesis"]["A_over_B_B_over_A_phase_inversion_each_tick"] is True
        ),
        "AB_P4_closure_each_tick": (
            candidate["probability_synthesis"]["AB_equals_P4_each_tick"] is True
        ),
        "HNAN_periodicity_each_tick": (
            candidate["probability_synthesis"]["HNAN_periodicity_each_tick"] is True
        ),
        "probability_no_browser_random": (
            candidate["probability_synthesis"]["browser_math_random_used"] is False
        ),
        "virtual_decay_exact_rate_semantics": (
            candidate["probability_synthesis"]["i041_virtual_decay_rate_semantics"][
                "probability_per_particle_per_turn"
            ] == ("1", str(PARTICLE_LATTICE))
        ),
        "ring72_seed_closure": (
            sum(
                1
                for event in candidate["probability_synthesis"]["events"]
                if event["fractal_seed_seal"]
            )
            == 1
        ),
        "three_hash72_lanes": (
            len(candidate["hash72_lanes"]) == 3
            and all(len(value) == HASH72_WIDTH for value in candidate["hash72_lanes"].values())
        ),
        "hash216_width_216": len(candidate["candidate_hash216"]) == HASH216_WIDTH,
        "hash216_hydration_15552": (
            candidate["candidate_hash216_hydration"]["roundtrip_exact"] is True
            and candidate["candidate_hash216_hydration"]["full_attached_components"]
            == FULL_HASH216_COMPONENTS
        ),
        "replay_bit_exact": candidate == replay,
        "changed_seed_changes_schedule": (
            candidate["probability_synthesis"]["schedule_root_sha256"]
            != alternate["probability_synthesis"]["schedule_root_sha256"]
        ),
        "no_shared_mutation_authority": (
            candidate["authority"]["canonical_vm81_mutation_authority"] is False
            and candidate["authority"]["canonical_hash216_commit_authority"] is False
            and candidate["authority"]["canonical_hash216_persistence_authority"] is False
        ),
        "no_float_probability_authority": (
            candidate["authority"]["host_float_probability_authority"] is False
        ),
    }
    return {
        "schema": f"{SCHEMA}_SELF_TEST",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "check_count": len(checks),
        "pass_count": sum(bool(value) for value in checks.values()),
        "failed": tuple(name for name, passed in checks.items() if not passed),
        "checks": checks,
        "candidate_root_sha256": candidate["candidate_root_sha256"],
        "input_hash216": candidate["input_hash216"],
        "candidate_hash216": candidate["candidate_hash216"],
        "bigint_serialized_sha256": candidate["bigint_layer"]["serialized_sha256"],
        "memristor_graph_root_sha256": candidate["memristor_graph"]["graph_root_sha256"],
        "probability_schedule_root_sha256": candidate["probability_synthesis"][
            "schedule_root_sha256"
        ],
    }


__all__ = [
    "AUTHORITY",
    "I041_SOURCE_GIT_BLOB_SHA",
    "I041_SOURCE_PATH",
    "PARTICLE_LATTICE",
    "PROFILE",
    "Pass220I080Error",
    "SCHEMA",
    "VERSION",
    "bigint_serialization_layer",
    "build_candidate",
    "default_seed_hash216",
    "memristor_knowledge_graph",
    "probability_synthesis_layer",
    "sample_below",
    "self_test",
    "source_bindings",
    "validate_candidate",
]


if __name__ == "__main__":
    print(json.dumps(self_test(), sort_keys=True, indent=2))

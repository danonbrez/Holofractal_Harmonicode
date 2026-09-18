"""Pass 220 I002: holographic Hash216 query composition over the I001 5184 ABI.

Candidate-only formalization and search metadata.  This module never commits
VM81, Hash72, or Hash216 state.  It binds existing authoritative surfaces and
constructs exact, replayable query witnesses around them.
"""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256, sha512
import json
from math import prod
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence, Tuple

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
    FRACTAL_123,
    SERIALIZED_CHARACTERS,
    deserialize_offsets_5184,
    fractal_123_geometry_witness,
    offsets_to_bigint,
    serialize_offsets_5184,
)
from hhs_spi_fibonacci_pythagorean_scaling_rule_v1 import square_state_sequence

SCHEMA = "HHS_PASS_220_HOLOGRAPHIC_HASH216_QUERY_MANIFOLD_V1"
VERSION = "1.0.0-checkpoint.2"
PROFILE = "PASS220-I002-HOLOGRAPHIC-HASH216-QUERY-v1"

HASH72_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?"
HASH72_LEN = 72
HASH216_LEN = 216
VM5184 = 5184
VM81_CELLS = 81
LOCAL64 = 64
HASH72_ROWS = 72
HASH72_MANIFOLD_CARDINALITY = 72**72
DEFAULT_PRIMES = (17, 19, 23, 29, 31, 37, 41, 43)
LANE_ORDER = ("PREVIOUS", "CHANGE", "RECEIPT")
PASS068_EXECUTION_ORDER = ("POSITIVE", "PLASTIC", "ZERO_SUM")
Q_MINUS_ONE_X = (("yx", -1), ("x+y", 0), ("xy", 1))
Q_MINUS_ONE_Z = (("wz", -1), ("z+w", 0), ("zw", 1))


class Pass220HolographicQueryError(ValueError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _root(value: Any) -> str:
    if isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = _canonical(value).encode("utf-8")
    return sha256(payload).hexdigest()


def _exact_int(value: Any, *, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Pass220HolographicQueryError(f"{name} must be an exact integer")
    return value


def _validate_hash72_word(value: str, *, name: str = "Hash72") -> str:
    if not isinstance(value, str) or len(value) != HASH72_LEN:
        raise Pass220HolographicQueryError(f"{name} must contain exactly 72 symbols")
    alphabet = set(HASH72_ALPHABET)
    bad = next((ch for ch in value if ch not in alphabet), None)
    if bad is not None:
        raise Pass220HolographicQueryError(f"{name} contains non-HARMONICODE symbol {bad!r}")
    return value


def split_hash216(value: str) -> Tuple[str, str, str]:
    if not isinstance(value, str) or len(value) != HASH216_LEN:
        raise Pass220HolographicQueryError("Hash216 must contain exactly 216 symbols")
    lanes = (
        value[:HASH72_LEN],
        value[HASH72_LEN : 2 * HASH72_LEN],
        value[2 * HASH72_LEN :],
    )
    for role, lane in zip(LANE_ORDER, lanes):
        _validate_hash72_word(lane, name=f"Hash216 {role} lane")
    return lanes


def compose_hash216(previous: str, change: str, receipt: str) -> str:
    lanes = tuple(
        _validate_hash72_word(value, name=f"Hash216 {role} lane")
        for role, value in zip(LANE_ORDER, (previous, change, receipt))
    )
    result = "".join(lanes)
    if len(result) != HASH216_LEN:
        raise AssertionError("internal Hash216 width invariant failed")
    return result


def hash72_rows_from_5184(serialized: str) -> Tuple[str, ...]:
    if not isinstance(serialized, str) or len(serialized) != SERIALIZED_CHARACTERS:
        raise Pass220HolographicQueryError("normalized carrier must contain exactly 5184 characters")
    alphabet = set(HASH72_ALPHABET)
    bad = next((ch for ch in serialized if ch not in alphabet), None)
    if bad is not None:
        raise Pass220HolographicQueryError(f"carrier contains non-HARMONICODE symbol {bad!r}")
    rows = tuple(serialized[i : i + HASH72_LEN] for i in range(0, VM5184, HASH72_LEN))
    if len(rows) != HASH72_ROWS or any(len(row) != HASH72_LEN for row in rows):
        raise AssertionError("internal 72x72 manifold partition failed")
    return rows


def coordinate_5184(index: int) -> Dict[str, int]:
    k = _exact_int(index, name="index")
    if not 0 <= k < VM5184:
        raise Pass220HolographicQueryError("5184 coordinate index out of range")
    hash72_row, hash72_column = divmod(k, HASH72_LEN)
    vm81_cell, local64 = divmod(k, LOCAL64)
    if 72 * hash72_row + hash72_column != 64 * vm81_cell + local64:
        raise AssertionError("coordinate factorization mismatch")
    return {
        "linear_index": k,
        "hash72_row": hash72_row,
        "hash72_column": hash72_column,
        "vm81_cell": vm81_cell,
        "local64": local64,
    }


def expanded_5184_witness(serialized: str) -> Dict[str, Any]:
    rows = hash72_rows_from_5184(serialized)
    return {
        "schema": "HHS_PASS_220_5184_HASH72_ALPHANUMERIC_MANIFOLD_V1",
        "serialized_characters": len(serialized),
        "alphabet": HASH72_ALPHABET,
        "alphabet_size": len(HASH72_ALPHABET),
        "hash72_rows": len(rows),
        "row_width": HASH72_LEN,
        "normalized_state_root_sha256": _root(serialized),
        "factorizations": {"72x72": 72 * 72, "81x64": 81 * 64},
        "coordinate_rule": "k=72*r+c=64*q+l",
        "floating_point_authority": False,
    }


def _is_prime(value: int) -> bool:
    n = _exact_int(value, name="prime")
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    factor = 3
    while factor * factor <= n:
        if n % factor == 0:
            return False
        factor += 2
    return True


def prime_modular_fingerprint(value: int, primes: Sequence[int] = DEFAULT_PRIMES) -> Dict[str, Any]:
    n = _exact_int(value, name="value")
    if n < 0:
        raise Pass220HolographicQueryError("fingerprint scalar must be nonnegative")
    ps = tuple(_exact_int(p, name="prime") for p in primes)
    if not ps or len(set(ps)) != len(ps) or any(not _is_prime(p) for p in ps):
        raise Pass220HolographicQueryError("fingerprint moduli must be distinct primes")
    residues = tuple(n % p for p in ps)
    modulus_product = prod(ps)
    return {
        "schema": "HHS_PASS_220_MULTI_PRIME_TENSOR_FINGERPRINT_V1",
        "scalar": n,
        "primes": ps,
        "residues": residues,
        "modulus_product": modulus_product,
        "injective_for_scalar_below_modulus_product": n < modulus_product,
        "floating_point_authority": False,
    }


def fibonacci_fractal_metadata(count: int = 9) -> Dict[str, Any]:
    c = _exact_int(count, name="count")
    if c < 3:
        raise Pass220HolographicQueryError("Fibonacci nesting requires at least three stages")
    states = square_state_sequence(c)
    exact = tuple((q.numerator, q.denominator) for q in states)
    return {
        "schema": "HHS_PASS_220_FIBONACCI_123_NESTING_V1",
        "fibonacci_square_states": exact,
        "fractal_123": FRACTAL_123,
        "fractal_geometry": fractal_123_geometry_witness(),
        "recurrence": "Q[n+1]=Q[n]+Q[n-1]",
        "floating_point_authority": False,
    }


def ordered_phase_metadata() -> Dict[str, Any]:
    return {
        "schema": "HHS_PASS_220_Q_MINUS_ONE_ORDERED_PHASE_METADATA_V1",
        "x_triangle": Q_MINUS_ONE_X,
        "z_triangle": Q_MINUS_ONE_Z,
        "trits": (-1, 0, 1),
        "ordered_products_collapsed": False,
        "floating_point_authority": False,
    }


def q3_lo_shu_triangle_metadata() -> Dict[str, Any]:
    """Three mutually constrained projections: magnitude, Lo Shu geometry, phase."""
    distance_spectra = ((2, 5, 5), (4, 4, 8), (2, 5, 5))
    if distance_spectra[1][0] + distance_spectra[1][1] != distance_spectra[1][2]:
        raise AssertionError("middle Lo Shu Pythagorean distance closure failed")
    return {
        "schema": "HHS_PASS_220_Q3_LO_SHU_TRIANGULAR_ENTANGLEMENT_V1",
        "axes": ("MAGNITUDE", "LO_SHU_GEOMETRY", "Q_MINUS_ONE_PHASE"),
        "magnitude_triangles": FRACTAL_123,
        "geometry_squared_distance_spectra": distance_spectra,
        "phase_triangles": (Q_MINUS_ONE_X, Q_MINUS_ONE_Z),
        "middle_geometry_pythagorean_residual": distance_spectra[1][0] + distance_spectra[1][1] - distance_spectra[1][2],
        "same_state_index_required": True,
        "floating_point_authority": False,
    }


def fibonacci_modular_nesting(count: int = 9, moduli: Sequence[int] = (2, 3, 5, 7, 72)) -> Dict[str, Any]:
    c = _exact_int(count, name="count")
    if c < 3:
        raise Pass220HolographicQueryError("Fibonacci nesting requires at least three stages")
    ms = tuple(_exact_int(m, name="modulus") for m in moduli)
    if not ms or any(m <= 1 for m in ms) or len(set(ms)) != len(ms):
        raise Pass220HolographicQueryError("Fibonacci modular nesting requires distinct moduli > 1")
    states = square_state_sequence(c)
    if any(q.denominator != 1 for q in states):
        raise AssertionError("square-state sequence unexpectedly left integer lattice")
    values = tuple(q.numerator for q in states)
    residues = tuple(tuple(value % modulus for modulus in ms) for value in values)
    return {
        "schema": "HHS_PASS_220_FIBONACCI_MODULAR_NESTING_V1",
        "states": values,
        "moduli": ms,
        "residue_rows": residues,
        "recurrence": "Q[n+1]=Q[n]+Q[n-1]",
        "floating_point_authority": False,
    }


def _read_pass068_artifact(path: str | Path | None, artifact: Mapping[str, Any] | None) -> Dict[str, Any]:
    if artifact is not None:
        return dict(artifact)
    if path is None:
        path = Path(__file__).resolve().parents[1] / "THREE_LANE_81_CELL_QUDIT_KERNEL_PASS_068.json"
    return json.loads(Path(path).read_text(encoding="utf-8"))


def bind_normalization_to_pass068(
    offsets: Sequence[int],
    serialized: str,
    *,
    path: str | Path | None = None,
    artifact: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    delta = tuple(_exact_int(v, name="offset") for v in offsets)
    if len(delta) != VM81_CELLS or any(not 0 <= v <= 8 for v in delta):
        raise Pass220HolographicQueryError("Pass068 binding requires 81 canonical normalization offsets")
    if deserialize_offsets_5184(serialized) != delta:
        raise Pass220HolographicQueryError("serialized carrier does not match supplied normalization offsets")
    data = _read_pass068_artifact(path, artifact)
    if data.get("cell_count") != VM81_CELLS or not data.get("all_cells_have_three_lanes") or not data.get("all_local_subgrids_closed"):
        raise Pass220HolographicQueryError("Pass068 kernel artifact is not a closed 81-cell three-lane state")
    cells = data.get("cells")
    if not isinstance(cells, list) or len(cells) != VM81_CELLS:
        raise Pass220HolographicQueryError("Pass068 kernel artifact must expose exactly 81 cells")
    chunks = tuple(serialized[i : i + LOCAL64] for i in range(0, VM5184, LOCAL64))
    if len(chunks) != VM81_CELLS:
        raise AssertionError("internal 81x64 carrier split failed")

    bindings = []
    seen = set()
    for raw in cells:
        if not isinstance(raw, Mapping):
            raise Pass220HolographicQueryError("Pass068 cell is not a mapping")
        index = _exact_int(raw.get("global_index"), name="global_index")
        if index in seen or not 0 <= index < VM81_CELLS:
            raise Pass220HolographicQueryError("Pass068 global indices must be unique 0..80")
        seen.add(index)
        transition = raw.get("transition")
        if not isinstance(transition, Mapping) or not transition.get("transition_admitted"):
            raise Pass220HolographicQueryError("Pass068 transition must be admitted")
        if tuple(transition.get("execution_order", ())) != PASS068_EXECUTION_ORDER:
            raise Pass220HolographicQueryError("Pass068 three-lane execution order mismatch")
        positive = transition.get("positive_lane")
        plastic = transition.get("plastic_lane")
        zero = transition.get("zero_sum_lane")
        if not all(isinstance(lane, Mapping) for lane in (positive, plastic, zero)):
            raise Pass220HolographicQueryError("Pass068 transition is missing a lane")
        lane_triplet = (
            ("POSITIVE", positive, 1),
            ("PLASTIC", plastic, 0),
            ("ZERO_SUM", zero, -1),
        )
        roots = {}
        for role, lane, expected_trit in lane_triplet:
            if lane.get("trit") != expected_trit:
                raise Pass220HolographicQueryError("Pass068 lane trit mismatch")
            roots[role] = _validate_hash72_word(str(lane.get("lane_root_hash72", "")), name=f"Pass068 {role} root")
        residue = zero.get("zero_sum_residue")
        if zero.get("closure_state") != "CLOSED" or not isinstance(residue, Mapping) or residue.get("numerator") != 0:
            raise Pass220HolographicQueryError("Pass068 zero-sum lane is not closed")
        bindings.append({
            "global_index": index,
            "cell_id": raw.get("cell_id"),
            "domain_id": raw.get("domain_id"),
            "lo_shu_value": raw.get("lo_shu_value"),
            "phase_tensor": raw.get("phase_tensor"),
            "normalized_offset": delta[index],
            "scientific_token64": chunks[index],
            "lane_trits": {"POSITIVE": 1, "PLASTIC": 0, "ZERO_SUM": -1},
            "lane_root_hash72": roots,
        })
    bindings.sort(key=lambda item: item["global_index"])
    return {
        "schema": "HHS_PASS_220_I002_PASS068_NORMALIZATION_BINDING_V1",
        "authority": data.get("authority"),
        "lattice_root_hash72": _validate_hash72_word(str(data.get("lattice_root_hash72", "")), name="Pass068 lattice root"),
        "cell_count": len(bindings),
        "lane_projection_count": len(bindings) * 3,
        "bindings": bindings,
        "normalization_is_mutation_authority": False,
        "canonical_vm81_mutation_authority": False,
    }


def build_perspective_projection_matrix(modalities: Mapping[str, str], serialized: str) -> Dict[str, Any]:
    hash72_rows_from_5184(serialized)
    if not isinstance(modalities, Mapping) or not modalities:
        raise Pass220HolographicQueryError("at least one modality is required")
    items = []
    for name, verbatim in modalities.items():
        if not isinstance(name, str) or not name or not isinstance(verbatim, str):
            raise Pass220HolographicQueryError("modalities require nonempty names and verbatim string metadata")
        items.append((name, verbatim))
    names = tuple(sorted(name for name, _ in items))
    verbatim_by_name = dict(items)
    shared_root = _root(serialized)
    edges = {}
    for source in names:
        for target in names:
            payload = {
                "shared_normalization_root": shared_root,
                "source_modality": source,
                "target_modality": target,
                "source_verbatim": verbatim_by_name[source],
                "target_verbatim": verbatim_by_name[target],
            }
            edges[f"{source}->{target}"] = {
                **payload,
                "projection_root_sha256": _root(payload),
                "self_projection": source == target,
            }
    return {
        "schema": "HHS_PASS_220_MODALITY_PERSPECTIVE_MATRIX_V1",
        "modalities": names,
        "shared_normalization_root": shared_root,
        "projection_count": len(edges),
        "expected_projection_count": len(names) ** 2,
        "edges": edges,
    }


def projection_cycle_closes(matrix: Mapping[str, Any], cycle: Sequence[str]) -> bool:
    names = tuple(cycle)
    if len(names) < 2 or names[0] != names[-1]:
        return False
    edges = matrix.get("edges")
    shared = matrix.get("shared_normalization_root")
    if not isinstance(edges, Mapping) or not isinstance(shared, str):
        return False
    for left, right in zip(names, names[1:]):
        edge = edges.get(f"{left}->{right}")
        if not isinstance(edge, Mapping) or edge.get("shared_normalization_root") != shared:
            return False
    return True


def path_index_to_word(index: int) -> str:
    value = _exact_int(index, name="path index")
    if not 0 <= value < HASH72_MANIFOLD_CARDINALITY:
        raise Pass220HolographicQueryError("path index outside 72^72 manifold")
    digits = [HASH72_ALPHABET[0]] * HASH72_LEN
    remaining = value
    for pos in range(HASH72_LEN - 1, -1, -1):
        remaining, digit = divmod(remaining, 72)
        digits[pos] = HASH72_ALPHABET[digit]
    return "".join(digits)


def path_word_to_index(word: str) -> int:
    canonical = _validate_hash72_word(word, name="composition path")
    lookup = {symbol: index for index, symbol in enumerate(HASH72_ALPHABET)}
    value = 0
    for symbol in canonical:
        value = value * 72 + lookup[symbol]
    return value


def collapse_composition_path(path_word: str, serialized: str) -> str:
    _validate_hash72_word(path_word, name="composition path")
    hash72_rows_from_5184(serialized)
    # The path is retained as lineage/search ancestry.  Closure is calibrated by
    # the I001 normalized state and therefore does not mutate with route choice.
    return serialized


def superposition_collapse_witness(serialized: str) -> Dict[str, Any]:
    hash72_rows_from_5184(serialized)
    probability = Fraction(1, HASH72_MANIFOLD_CARDINALITY)
    total = probability * HASH72_MANIFOLD_CARDINALITY
    if total != 1:
        raise AssertionError("uniform path mass failed exact closure")
    return {
        "schema": "HHS_PASS_220_RECIPROCAL_SUPERPOSITION_COLLAPSE_V1",
        "path_cardinality": HASH72_MANIFOLD_CARDINALITY,
        "per_path_probability": {"numerator": 1, "denominator": HASH72_MANIFOLD_CARDINALITY},
        "total_probability_mass": {"numerator": total.numerator, "denominator": total.denominator},
        "collapse_target_root_sha256": _root(serialized),
        "collapse_target_characters": len(serialized),
        "path_identity_preserved_in_lineage": True,
        "collapse_target_is_path_independent": True,
        "floating_point_authority": False,
    }


def _uniform_integer(seed: bytes, upper: int, ordinal: int, *, domain: bytes) -> int:
    if upper <= 0:
        raise Pass220HolographicQueryError("uniform upper bound must be positive")
    o = _exact_int(ordinal, name="sample ordinal")
    if o < 0:
        raise Pass220HolographicQueryError("sample ordinal must be nonnegative")
    space = 1 << 512
    limit = space - (space % upper)
    nonce = 0
    while True:
        digest = sha512(domain + b"\0" + seed + o.to_bytes(8, "big") + nonce.to_bytes(8, "big")).digest()
        value = int.from_bytes(digest, "big")
        if value < limit:
            return value % upper
        nonce += 1


def deterministic_path_sample(query_hash216: str, ordinal: int) -> Dict[str, Any]:
    split_hash216(query_hash216)
    index = _uniform_integer(query_hash216.encode("ascii"), HASH72_MANIFOLD_CARDINALITY, ordinal, domain=b"HHS-P220-I002-PATH")
    word = path_index_to_word(index)
    return {
        "ordinal": ordinal,
        "path_index": index,
        "path_word": word,
        "roundtrip_index": path_word_to_index(word),
        "sampling_space": HASH72_MANIFOLD_CARDINALITY,
        "candidate_only": True,
    }


def _hash216_distance(left: str, right: str) -> int:
    split_hash216(left)
    split_hash216(right)
    return sum(a != b for a, b in zip(left, right))


def _candidate_features(query: Mapping[str, Any], candidate: Mapping[str, Any]) -> Dict[str, int]:
    query_hash = str(query.get("hash216", ""))
    candidate_hash = str(candidate.get("hash216", ""))
    distance = _hash216_distance(query_hash, candidate_hash)
    qfp = query.get("prime_fingerprint", {})
    cfp = candidate.get("prime_fingerprint", {})
    q_primes = tuple(qfp.get("primes", ())) if isinstance(qfp, Mapping) else ()
    c_primes = tuple(cfp.get("primes", ())) if isinstance(cfp, Mapping) else ()
    q_res = tuple(qfp.get("residues", ())) if isinstance(qfp, Mapping) else ()
    c_res = tuple(cfp.get("residues", ())) if isinstance(cfp, Mapping) else ()
    if q_primes != c_primes or len(q_res) != len(c_res):
        raise Pass220HolographicQueryError("candidate prime fingerprint profile mismatch")
    prime_matches = sum(a == b for a, b in zip(q_res, c_res))
    qfib = tuple(query.get("fibonacci_square_states", ()))
    cfib = tuple(candidate.get("fibonacci_square_states", ()))
    fib_matches = sum(a == b for a, b in zip(qfib, cfib))
    phase_matches = sum(
        a == b for a, b in zip(tuple(query.get("phase_signature", ())), tuple(candidate.get("phase_signature", ())))
    )
    perspective_matches = len(set(query.get("perspective_roots", ())) & set(candidate.get("perspective_roots", ())))
    return {
        "hash216_similarity": HASH216_LEN - distance,
        "prime_matches": prime_matches,
        "fibonacci_matches": fib_matches,
        "phase_matches": phase_matches,
        "perspective_matches": perspective_matches,
    }


def rank_and_sample_candidates(
    query: Mapping[str, Any],
    candidates: Sequence[Mapping[str, Any]],
    *,
    sample_ordinal: int = 0,
) -> Dict[str, Any]:
    query_hash = str(query.get("hash216", ""))
    split_hash216(query_hash)
    if not candidates:
        return {"schema": "HHS_PASS_220_EXACT_WEIGHTED_QUERY_RANKING_V1", "ranked": [], "sampled": None, "candidate_only": True}
    ranked = []
    ids = set()
    for source_ordinal, candidate in enumerate(candidates):
        cid = candidate.get("candidate_id")
        if not isinstance(cid, str) or not cid or cid in ids:
            raise Pass220HolographicQueryError("candidate IDs must be nonempty and unique")
        ids.add(cid)
        features = _candidate_features(query, candidate)
        totals = {
            "hash216_similarity": HASH216_LEN,
            "prime_matches": len(tuple(query.get("prime_fingerprint", {}).get("primes", ()))),
            "fibonacci_matches": len(tuple(query.get("fibonacci_square_states", ()))),
            "phase_matches": len(tuple(query.get("phase_signature", ()))),
            "perspective_matches": len(tuple(query.get("perspective_roots", ()))),
        }
        closed_channels = sum(features[key] == total for key, total in totals.items())
        # Composition weight uses no learned/float coefficient: every independent
        # agreement channel multiplies the exact candidate-search mass.
        sampling_weight = prod(features[key] + 1 for key in (
            "hash216_similarity",
            "prime_matches",
            "fibonacci_matches",
            "phase_matches",
            "perspective_matches",
        ))
        ranked.append({
            "candidate_id": cid,
            "hash216": candidate["hash216"],
            "features": features,
            "closed_channels": closed_channels,
            "sampling_weight": sampling_weight,
            "source_ordinal": source_ordinal,
        })
    ranked.sort(key=lambda item: (-item["closed_channels"], -item["sampling_weight"], item["hash216"], item["candidate_id"], item["source_ordinal"]))
    total_weight = sum(item["sampling_weight"] for item in ranked)
    for item in ranked:
        item["sampling_probability"] = {
            "numerator": item["sampling_weight"],
            "denominator": total_weight,
        }
    draw = _uniform_integer(query_hash.encode("ascii"), total_weight, sample_ordinal, domain=b"HHS-P220-I002-RANK")
    cursor = 0
    sampled = None
    for item in ranked:
        cursor += item["sampling_weight"]
        if draw < cursor:
            sampled = {"candidate_id": item["candidate_id"], "draw": draw, "total_weight": total_weight}
            break
    if sampled is None:
        raise AssertionError("weighted sample failed")
    return {
        "schema": "HHS_PASS_220_EXACT_WEIGHTED_QUERY_RANKING_V1",
        "ranked": ranked,
        "sampled": sampled,
        "probability_allocates_search_effort_only": True,
        "probability_may_authorize_state": False,
        "candidate_only": True,
        "canonical_vm81_mutation_authority": False,
    }


def build_holographic_query_record(
    *,
    offsets: Sequence[int],
    hash216: str,
    modalities: Mapping[str, str],
    pass068_artifact: Mapping[str, Any],
    primes: Sequence[int] = DEFAULT_PRIMES,
    fibonacci_count: int = 9,
) -> Dict[str, Any]:
    delta = tuple(_exact_int(v, name="offset") for v in offsets)
    if len(delta) != VM81_CELLS or any(not 0 <= v <= 8 for v in delta):
        raise Pass220HolographicQueryError("query record requires 81 canonical offsets")
    serialized = serialize_offsets_5184(delta)
    rows = hash72_rows_from_5184(serialized)
    scalar = offsets_to_bigint(delta)
    lanes = split_hash216(hash216)
    prime = prime_modular_fingerprint(scalar, primes)
    fib = fibonacci_fractal_metadata(fibonacci_count)
    fib_modular = fibonacci_modular_nesting(fibonacci_count)
    phase = ordered_phase_metadata()
    q3 = q3_lo_shu_triangle_metadata()
    perspective = build_perspective_projection_matrix(modalities, serialized)
    pass068 = bind_normalization_to_pass068(delta, serialized, artifact=pass068_artifact)
    collapse = superposition_collapse_witness(serialized)
    record = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": PROFILE,
        "normalized_offsets": delta,
        "scalar_bigint": scalar,
        "serialized_5184": serialized,
        "serialized_root_sha256": _root(serialized),
        "hash72_row_count": len(rows),
        "hash216": hash216,
        "hash216_lanes": dict(zip(LANE_ORDER, lanes)),
        "prime_fingerprint": prime,
        "fibonacci_123": fib,
        "fibonacci_modular_nesting": fib_modular,
        "phase": phase,
        "q3_lo_shu": q3,
        "perspective_matrix": perspective,
        "pass068_binding": pass068,
        "superposition_collapse": collapse,
        "candidate_only": True,
        "hash72_commit_authority": False,
        "hash216_commit_authority": False,
        "canonical_vm81_mutation_authority": False,
        "floating_point_authority": False,
    }
    record["record_root_sha256"] = _root(record)
    return record


__all__ = [
    "DEFAULT_PRIMES",
    "HASH72_ALPHABET",
    "HASH72_MANIFOLD_CARDINALITY",
    "Pass220HolographicQueryError",
    "bind_normalization_to_pass068",
    "build_holographic_query_record",
    "build_perspective_projection_matrix",
    "collapse_composition_path",
    "compose_hash216",
    "coordinate_5184",
    "deterministic_path_sample",
    "expanded_5184_witness",
    "fibonacci_fractal_metadata",
    "fibonacci_modular_nesting",
    "hash72_rows_from_5184",
    "ordered_phase_metadata",
    "path_index_to_word",
    "path_word_to_index",
    "prime_modular_fingerprint",
    "q3_lo_shu_triangle_metadata",
    "projection_cycle_closes",
    "rank_and_sample_candidates",
    "split_hash216",
    "superposition_collapse_witness",
]

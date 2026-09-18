from fractions import Fraction
from pathlib import Path
import pytest

from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import serialize_offsets_5184
from hhs_runtime.hhs_pass220_holographic_hash216_query_v1 import (
    DEFAULT_PRIMES,
    HASH72_ALPHABET,
    HASH72_MANIFOLD_CARDINALITY,
    Pass220HolographicQueryError,
    bind_normalization_to_pass068,
    build_holographic_query_record,
    build_perspective_projection_matrix,
    collapse_composition_path,
    compose_hash216,
    coordinate_5184,
    deterministic_path_sample,
    expanded_5184_witness,
    fibonacci_fractal_metadata,
    fibonacci_modular_nesting,
    hash72_rows_from_5184,
    ordered_phase_metadata,
    path_index_to_word,
    path_word_to_index,
    prime_modular_fingerprint,
    q3_lo_shu_triangle_metadata,
    projection_cycle_closes,
    rank_and_sample_candidates,
    split_hash216,
    superposition_collapse_witness,
)


def word(seed: int) -> str:
    return "".join(HASH72_ALPHABET[(seed + i) % 72] for i in range(72))


def hash216(seed: int = 0) -> str:
    return compose_hash216(word(seed), word(seed + 1), word(seed + 2))


def pass068_fixture():
    cells = []
    for i in range(81):
        cells.append({
            "global_index": i,
            "cell_id": f"cell:{i:02d}",
            "domain_id": f"D{i//9}",
            "lo_shu_value": (i % 9) + 1,
            "phase_tensor": ("x", "y", "z", "w", "xy", "yx", "zw", "wz")[i % 8],
            "transition": {
                "transition_admitted": True,
                "execution_order": ["POSITIVE", "PLASTIC", "ZERO_SUM"],
                "positive_lane": {"trit": 1, "lane_root_hash72": word(i)},
                "plastic_lane": {"trit": 0, "lane_root_hash72": word(i + 1)},
                "zero_sum_lane": {
                    "trit": -1,
                    "lane_root_hash72": word(i + 2),
                    "closure_state": "CLOSED",
                    "zero_sum_residue": {"numerator": 0, "denominator": 1},
                },
            },
        })
    return {
        "authority": "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1",
        "cell_count": 81,
        "all_cells_have_three_lanes": True,
        "all_local_subgrids_closed": True,
        "lattice_root_hash72": word(7),
        "cells": cells,
    }


def test_hash72_alphabet_is_literal_72_symbol_harmonicode_set_and_carrier_partitions_72x72():
    assert len(HASH72_ALPHABET) == 72
    carrier = serialize_offsets_5184(tuple(i % 9 for i in range(81)))
    assert set(carrier) <= set(HASH72_ALPHABET)
    rows = hash72_rows_from_5184(carrier)
    assert len(rows) == 72
    assert all(len(row) == 72 for row in rows)
    witness = expanded_5184_witness(carrier)
    assert witness["factorizations"] == {"72x72": 5184, "81x64": 5184}


def test_all_5184_linear_positions_have_exact_dual_coordinate_factorization():
    seen72 = set()
    seen8164 = set()
    for k in range(5184):
        c = coordinate_5184(k)
        assert k == 72 * c["hash72_row"] + c["hash72_column"]
        assert k == 64 * c["vm81_cell"] + c["local64"]
        seen72.add((c["hash72_row"], c["hash72_column"]))
        seen8164.add((c["vm81_cell"], c["local64"]))
    assert len(seen72) == len(seen8164) == 5184


def test_hash216_is_exactly_three_ordered_hash72_lanes():
    lanes = (word(1), word(2), word(3))
    value = compose_hash216(*lanes)
    assert len(value) == 216
    assert split_hash216(value) == lanes


def test_pass068_binding_attaches_81_offsets_to_real_three_lane_shape():
    offsets = tuple(i % 9 for i in range(81))
    serialized = serialize_offsets_5184(offsets)
    result = bind_normalization_to_pass068(offsets, serialized, artifact=pass068_fixture())
    assert result["cell_count"] == 81
    assert result["lane_projection_count"] == 243
    assert result["bindings"][0]["normalized_offset"] == 0
    assert result["bindings"][8]["normalized_offset"] == 8
    assert result["bindings"][0]["lane_trits"] == {"POSITIVE": 1, "PLASTIC": 0, "ZERO_SUM": -1}
    assert result["canonical_vm81_mutation_authority"] is False


def test_repository_pass068_artifact_binds_when_checkout_artifact_is_present():
    root = Path(__file__).resolve().parents[2]
    artifact = root / "THREE_LANE_81_CELL_QUDIT_KERNEL_PASS_068.json"
    if not artifact.exists():
        pytest.skip("isolated staging does not materialize the repository Pass068 artifact")
    offsets = (0,) * 81
    result = bind_normalization_to_pass068(offsets, serialize_offsets_5184(offsets), path=artifact)
    assert result["authority"] == "HHS_THREE_LANE_QUDIT_KERNEL_AUTHORITY_V1"
    assert result["cell_count"] == 81
    assert result["lane_projection_count"] == 243


def test_pass068_binding_fails_closed_on_broken_zero_sum():
    artifact = pass068_fixture()
    artifact["cells"][10]["transition"]["zero_sum_lane"]["zero_sum_residue"]["numerator"] = 1
    offsets = (0,) * 81
    with pytest.raises(Pass220HolographicQueryError):
        bind_normalization_to_pass068(offsets, serialize_offsets_5184(offsets), artifact=artifact)


def test_multi_prime_fingerprint_is_exact_and_reports_crt_bound():
    f = prime_modular_fingerprint(123456789, (17, 19, 23, 29, 31, 37))
    assert f["residues"] == tuple(123456789 % p for p in f["primes"])
    assert f["modulus_product"] == 17 * 19 * 23 * 29 * 31 * 37
    with pytest.raises(Pass220HolographicQueryError):
        prime_modular_fingerprint(5, (17, 21))


def test_fibonacci_123_q3_and_q_minus_one_metadata_remain_exact():
    fib = fibonacci_fractal_metadata(9)
    assert fib["fibonacci_square_states"] == tuple((v, 1) for v in (1, 2, 3, 5, 8, 13, 21, 34, 55))
    assert fib["fractal_123"] == ((1, 2, 3), (2, 4, 6), (3, 6, 9))
    nested = fibonacci_modular_nesting(9, (2, 3, 5, 7, 72))
    assert nested["states"] == (1, 2, 3, 5, 8, 13, 21, 34, 55)
    assert nested["residue_rows"][4] == tuple(8 % m for m in (2, 3, 5, 7, 72))
    phase = ordered_phase_metadata()
    assert phase["x_triangle"] == (("yx", -1), ("x+y", 0), ("xy", 1))
    assert phase["z_triangle"] == (("wz", -1), ("z+w", 0), ("zw", 1))
    q3 = q3_lo_shu_triangle_metadata()
    assert q3["axes"] == ("MAGNITUDE", "LO_SHU_GEOMETRY", "Q_MINUS_ONE_PHASE")
    assert q3["middle_geometry_pythagorean_residual"] == 0


def test_every_modality_carries_directed_projection_to_every_other_modality():
    carrier = serialize_offsets_5184((0,) * 81)
    matrix = build_perspective_projection_matrix({"text": "alpha", "audio": "beta", "image": "gamma"}, carrier)
    assert matrix["projection_count"] == matrix["expected_projection_count"] == 9
    assert projection_cycle_closes(matrix, ("text", "audio", "image", "text"))
    assert matrix["edges"]["audio->image"]["shared_normalization_root"] == matrix["shared_normalization_root"]


def test_72_power_72_path_indexing_and_uniform_probability_close_exactly():
    assert path_word_to_index(path_index_to_word(0)) == 0
    assert path_word_to_index(path_index_to_word(HASH72_MANIFOLD_CARDINALITY - 1)) == HASH72_MANIFOLD_CARDINALITY - 1
    carrier = serialize_offsets_5184((0,) * 81)
    witness = superposition_collapse_witness(carrier)
    p = Fraction(witness["per_path_probability"]["numerator"], witness["per_path_probability"]["denominator"])
    assert p == Fraction(1, 72**72)
    assert p * witness["path_cardinality"] == 1
    assert witness["total_probability_mass"] == {"numerator": 1, "denominator": 1}


def test_deterministic_pseudorandom_paths_preserve_one_fixed_collapse_target():
    h = hash216(4)
    carrier = serialize_offsets_5184(tuple(i % 9 for i in range(81)))
    first = [deterministic_path_sample(h, i) for i in range(8)]
    second = [deterministic_path_sample(h, i) for i in range(8)]
    assert first == second
    assert len({item["path_index"] for item in first}) > 1
    assert all(item["roundtrip_index"] == item["path_index"] for item in first)
    assert all(collapse_composition_path(item["path_word"], carrier) == carrier for item in first)


def test_full_query_record_composes_all_metadata_on_one_hash216_identity():
    offsets = tuple(i % 9 for i in range(81))
    record = build_holographic_query_record(
        offsets=offsets,
        hash216=hash216(9),
        modalities={"text": "prompt", "audio": "tone", "image": "frame", "code": "x==x"},
        pass068_artifact=pass068_fixture(),
    )
    assert record["hash72_row_count"] == 72
    assert record["pass068_binding"]["lane_projection_count"] == 243
    assert record["perspective_matrix"]["projection_count"] == 16
    assert record["superposition_collapse"]["path_cardinality"] == 72**72
    assert record["q3_lo_shu"]["middle_geometry_pythagorean_residual"] == 0
    assert record["fibonacci_modular_nesting"]["states"][:5] == (1, 2, 3, 5, 8)
    assert record["candidate_only"] is True
    assert record["hash216_commit_authority"] is False
    assert record["canonical_vm81_mutation_authority"] is False


def candidate_from_record(record, cid, *, tweak_hash=0, tweak_residue=False):
    fp = dict(record["prime_fingerprint"])
    fp["primes"] = tuple(fp["primes"])
    fp["residues"] = tuple(fp["residues"])
    if tweak_residue:
        values = list(fp["residues"])
        values[0] = (values[0] + 1) % fp["primes"][0]
        fp["residues"] = tuple(values)
    perspectives = tuple(edge["projection_root_sha256"] for edge in record["perspective_matrix"]["edges"].values())
    return {
        "candidate_id": cid,
        "hash216": hash216(tweak_hash) if tweak_hash else record["hash216"],
        "prime_fingerprint": fp,
        "fibonacci_square_states": tuple(record["fibonacci_123"]["fibonacci_square_states"]),
        "phase_signature": tuple(record["phase"]["x_triangle"] + record["phase"]["z_triangle"]),
        "perspective_roots": perspectives,
    }


def query_features(record):
    perspectives = tuple(edge["projection_root_sha256"] for edge in record["perspective_matrix"]["edges"].values())
    return {
        "hash216": record["hash216"],
        "prime_fingerprint": record["prime_fingerprint"],
        "fibonacci_square_states": tuple(record["fibonacci_123"]["fibonacci_square_states"]),
        "phase_signature": tuple(record["phase"]["x_triangle"] + record["phase"]["z_triangle"]),
        "perspective_roots": perspectives,
    }


def test_exact_hierarchical_ranking_and_weighted_sampling_are_candidate_only():
    record = build_holographic_query_record(
        offsets=(0,) * 81,
        hash216=hash216(12),
        modalities={"text": "prompt", "image": "frame"},
        pass068_artifact=pass068_fixture(),
        primes=DEFAULT_PRIMES,
    )
    query = query_features(record)
    candidates = [
        candidate_from_record(record, "exact"),
        candidate_from_record(record, "different-hash", tweak_hash=33),
        candidate_from_record(record, "different-prime", tweak_residue=True),
    ]
    result1 = rank_and_sample_candidates(query, candidates, sample_ordinal=5)
    result2 = rank_and_sample_candidates(query, candidates, sample_ordinal=5)
    assert result1 == result2
    assert result1["ranked"][0]["candidate_id"] == "exact"
    assert sum(Fraction(item["sampling_probability"]["numerator"], item["sampling_probability"]["denominator"]) for item in result1["ranked"]) == 1
    assert result1["probability_allocates_search_effort_only"] is True
    assert result1["probability_may_authorize_state"] is False
    assert result1["canonical_vm81_mutation_authority"] is False


def test_malformed_hash216_and_nonexact_scalars_fail_closed():
    with pytest.raises(Pass220HolographicQueryError):
        split_hash216("0" * 215)
    with pytest.raises(Pass220HolographicQueryError):
        coordinate_5184(1.0)
    with pytest.raises(Pass220HolographicQueryError):
        deterministic_path_sample(hash216(), -1)

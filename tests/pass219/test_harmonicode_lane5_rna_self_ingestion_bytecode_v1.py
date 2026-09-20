from hhs_runtime.harmonicode_lane5_rna_self_ingestion_bytecode_v1 import (
    all_triplets,
    external_spelling_payload,
    iterate_projected_word,
    projected_self_ingest,
    typed_native_code,
    validate_self_ingestion,
)


def test_typed_native_operation_byte_is_identity_for_all_64():
    records = [typed_native_code(state) for state in all_triplets()]
    assert len(records) == 64
    assert all(record["fixed_point"] for record in records)
    assert len({tuple(record["decoded_triplet"]) for record in records}) == 64


def test_external_ascii_bigint_mod64_depends_only_on_last_byte():
    for state in all_triplets():
        payload = external_spelling_payload(state)
        projected = projected_self_ingest(state)
        assert projected["projected_operation64"] == payload["last_byte"] % 64


def test_compact_and_explicit_multiplication_spellings_have_same_mod64_projection():
    for state in all_triplets():
        projected = projected_self_ingest(state)
        assert projected["compact_bigint"] % 64 == projected["explicit_bigint"] % 64


def test_external_projection_has_exact_four_fixed_points():
    fixed = []
    for state in all_triplets():
        projected = tuple(projected_self_ingest(state)["decoded_triplet"])
        if projected == state:
            fixed.append("".join(state))
    assert sorted(fixed) == ["wyw", "wzx", "wzy", "wzz"]


def test_all_nonfixed_states_reach_one_of_four_attractors_in_one_step():
    terminals = {}
    for state in all_triplets():
        orbit = iterate_projected_word(state)
        terminal = "".join(orbit["terminal"])
        terminals[terminal] = terminals.get(terminal, 0) + 1
        assert orbit["cycle_length"] == 1
        assert orbit["transient_length"] in (0, 1)
    assert terminals == {"wyw": 16, "wzx": 16, "wzy": 16, "wzz": 16}


def test_full_self_ingestion_validation():
    report = validate_self_ingestion()
    assert report["result"] == "PASS"
    assert report["check_count"] == 15
    assert all(report["checks"].values())
    assert report["typed_native"]["fixed_point_count"] == 64
    assert report["external_numeric_projection"]["image_size_after_one_step"] == 4
    assert report["post_projection_t004_resolution"]["resolved_count"] == 64

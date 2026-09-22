from hhs_runtime.hhs_pass220_g3_ouroboros_opcode_registry_v1 import (
    AUTHORITY_SCOPE,
    build_g3_opcode_registry,
    resolve_g3_opcode,
)


def test_g3_registry_is_append_only_24_through_34():
    registry = build_g3_opcode_registry()
    entries = registry["entries"]
    assert registry["registered_opcodes"] == 11
    assert [entry["numeric_opcode"] for entry in entries] == list(range(24, 35))
    assert entries[0]["native_opcode"] == "OP_G3_IEEE_INGRESS"
    assert entries[-1]["native_opcode"] == "OP_G3_OUROBOROS"
    assert registry["historical_pass079_registry_mutated"] is False


def test_each_g3_opcode_has_distinct_root_and_witness():
    entries = build_g3_opcode_registry()["entries"]
    roots = [entry["binding_root_hash72"] for entry in entries]
    witnesses = [entry["witness_class"] for entry in entries]
    assert len(set(roots)) == 11
    assert len(set(witnesses)) == 11
    assert all(len(root) == 72 for root in roots)
    assert all(entry["compiler_may_synthesize"] is False for entry in entries)


def test_ieee_and_bigint_authority_boundaries_are_explicit():
    entries = build_g3_opcode_registry()["entries"]
    assert all(entry["ieee_is_boundary_only"] is True for entry in entries)
    assert all(
        entry["input_schema"]["floating_arithmetic_authority"] is False
        for entry in entries
    )
    assert all(
        entry["bigint_physical_5184_character_offset_resolved"] is False
        for entry in entries
    )
    assert all(
        entry["bigint_semantic_register"] == "LO_SHU_VALUE_1_A2"
        for entry in entries
    )


def test_fused_opcode_requires_all_constituent_witnesses():
    fused = build_g3_opcode_registry()["entries"][-1]
    required = fused["pre_state_witness_requirements"]
    assert len(required) == 10
    assert "G3_P4_C4_BOUND_NO_P2_BRANCH" in required
    assert "G3_C5_CONSTRAINT_BOUND" in required
    assert "G3_C7_CONSTRAINT_BOUND" in required
    assert "G3_EXACT_BIGINT_REGISTER_BOUND" in required
    assert "G3_NUCLEUS_ZERO_SUM_CLOSED" in required
    assert "IEEE_OUT_EQ_IEEE_IN_RAW_BITS" in required


def test_resolver_requires_root_authority_lease_and_lane():
    binding = build_g3_opcode_registry()["entries"][0]
    good = {
        "binding_root_hash72": binding["binding_root_hash72"],
        "authority_scope": AUTHORITY_SCOPE,
        "lease_status": "ACTIVE_VALIDATED",
        "vm81_lane_binding_status": "BOUND_WITNESSED",
    }
    resolved = resolve_g3_opcode(binding["native_opcode"], good)
    assert resolved["numeric_opcode"] == 24
    assert resolved["witness_class"] == "W_G3_IEEE_INGRESS"

    for key, bad in (
        ("binding_root_hash72", "bad"),
        ("authority_scope", "bad"),
        ("lease_status", "bad"),
        ("vm81_lane_binding_status", "bad"),
    ):
        request = dict(good)
        request[key] = bad
        try:
            resolve_g3_opcode(binding["native_opcode"], request)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{key} shortcut unexpectedly resolved")


def test_multimodal_and_four_lane_surfaces_do_not_gain_authority():
    registry = build_g3_opcode_registry()
    assert registry["lane5_bios_relation"] == "OUROBOROS_MANIFOLD_ALGORITHM"
    assert registry["four_lane_hydration_authority"] is False
    assert registry["graphics_projection_authority"] is False
    for entry in registry["entries"]:
        assert (
            entry["four_lane_hydration_relation"]
            == "COORDINATED_TYPED_VIEW_NO_INDEPENDENT_CANONICAL_AUTHORITY"
        )
        assert (
            entry["multimodal_geometry_relation"]
            == "PLATONIC_COLOR_WHEEL_SPRITE_PROJECTION_DOWNSTREAM_ONLY"
        )

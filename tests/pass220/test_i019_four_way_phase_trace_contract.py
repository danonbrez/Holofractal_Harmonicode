"""Pass 220: four-way ordered phase proof-trace admission boundary.

The equations are typed source obligations, never host scalar quotients.
This is a dependency-scoped source/geometry regression, not a substitute
for the inherited native VM81 ingress/egress equality receipt.
"""
from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
    edge_class, reverse_edge_path,
)
from hhs_runtime.hhs_pass220_g3_ouroboros_opcode_registry_v1 import (
    build_lane5_g3_pipeline_contract,
)


def test_directional_reciprocals_are_distinct_and_involutive():
    # A=LHS, B=RHS; AB/BA is forward; BA/AB is reverse.
    forward = (("A", "B"), ("B", "A"))
    backward = tuple(reversed(forward))
    assert forward != backward
    assert tuple(reversed(backward)) == forward
    # Existing ordered phase library must not normalize xy into yx.
    assert edge_class("xy") == "xy"
    assert edge_class("yx") == "yx"
    assert edge_class("xy") != edge_class("yx")
    edges = (("x", "y"), ("z", "w"))
    assert reverse_edge_path(reverse_edge_path(edges)) == edges


def test_proof_trace_uses_inherited_hash216_and_vm81_authority():
    contract = build_lane5_g3_pipeline_contract()
    stages = contract["stages"]
    assert stages.index("PASS219_CPP_RNA_CELL_WALL") < stages.index(
        "LANE5_MANDATORY_CONSTRUCTOR_COMPOSITION"
    )
    assert stages.index("HASH216_SELF_SOLVING_VALIDATION") < stages.index(
        "SIGNED_ENVIRONMENTAL_VM81_ADMISSION_IF_MUTATING"
    )
    assert stages.index("SIGNED_ENVIRONMENTAL_VM81_ADMISSION_IF_MUTATING") < stages.index(
        "INVERSE_EGRESS_COMPILATION"
    )
    assert contract["unmerged_evidence_canonical_authority"] is False
    assert contract["lane5_hash72_mint_authority"] is False
    assert contract["lane5_hash216_canonical_mint_authority"] is False
    assert contract["candidate_ieee_egress_is_external_emission"] is False


def test_siamese_forward_reverse_actual_i019_payload_roundtrip():
    from hhs_runtime.hhs_pass220_lo_shu_normalization_v1 import (
        siamese_vm81_cell_order,
        serialize_siamese_offsets_5184,
        deserialize_siamese_offsets_5184,
        serialize_offsets_5184,
        deserialize_offsets_5184,
    )
    order = siamese_vm81_cell_order()
    assert order[0] == 4
    assert len(set(order)) == 81
    for values in (
        tuple(i % 9 for i in range(81)),
        tuple((i * 7 + 3) % 9 for i in range(81)),
        tuple(0 for _ in range(81)),
    ):
        forward = serialize_siamese_offsets_5184(values)
        assert len(forward) == 5184
        assert deserialize_siamese_offsets_5184(forward) == values
        # Independently decode I019 cell tokens to prove traversal, not merely
        # an encode/decode pair that makes the same address-order mistake.
        assert deserialize_offsets_5184(forward) == tuple(values[i] for i in order)
        assert serialize_offsets_5184(deserialize_offsets_5184(forward)) == forward
        backward = serialize_siamese_offsets_5184(
            deserialize_siamese_offsets_5184(forward)
        )
        assert backward == forward
        # An incorrect traversal permutation must not masquerade as a
        # round-trip preserving the original genesis-offset assignments.
        if values[order[0]] != values[0]:
            assert forward != serialize_offsets_5184(values)


def test_four_way_trace_executes_payload_and_keeps_gate_authority_separate():
    from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
        four_way_ingress_phase_trace,
    )
    offsets = tuple((i * 7 + 3) % 9 for i in range(81))
    trace = four_way_ingress_phase_trace("A=LHS", "B=RHS", offsets)
    assert trace["ordered_gates"] == (
        ("forward_closure", "AB", "P^4"),
        ("reverse_closure", "BA", "P^4"),
        ("forward_rank1", "AB", "BA"),
        ("reverse_rank1", "BA", "AB"),
    )
    assert trace["serial_width"] == 5184
    assert trace["original_offsets"] == offsets
    assert trace["reverse_offsets"] == offsets
    assert trace["lossless_i019_address_roundtrip"] is True
    assert trace["phase_relation_gate_executed"] is False
    assert trace["canonical_hash72_mint_authority"] is False
    assert trace["canonical_hash216_mint_authority"] is False

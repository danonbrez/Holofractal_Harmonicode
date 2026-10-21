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


def test_verbatim_module29_72_cell_map_survives_four_way_trace():
    from hashlib import sha256
    from hhs_runtime.hhs_pass220_palindromic_ordered_phase_v1 import (
        MODULE29_72_CELL_PHASE_MAP_SOURCE, four_way_ingress_phase_trace,
    )
    expected = "List(NcalcMatrixPower((I^List(List(List(List(1,x,2),List(w,z,y),List(4,z,3)),List(List(-x,1,-y),List(4,y,2),List(-w,3,-z))),List(List(List(4,3,3),List(2,z,4),List(1,1,2)),List(List(w,3,-z),List(2,w,4),List(-x,1,y))))/List(List(4,9,2),List(3,5,7),List(8,1,6))),(-1)),I^List(List(List(List(1,x,2),List(w,z,y),List(4,z,3)),List(List(-x,1,-y),List(4,y,2),List(-w,3,-z))),List(List(List(4,3,3),List(2,z,4),List(1,1,2)),List(List(w,3,-z),List(2,w,4),List(-x,1,y))))/List(List(4,9,2),List(3,5,7),List(8,1,6)))"
    assert MODULE29_72_CELL_PHASE_MAP_SOURCE == expected
    trace = four_way_ingress_phase_trace('LHS','RHS',tuple(range(9))*9)
    assert trace['module29_72_cell_phase_map_source'] == expected
    assert trace['module29_72_cell_phase_map_sha256'] == sha256(expected.encode('utf-8')).hexdigest()
    assert trace['module29_phase_map_executed'] is False


def test_i073_hash216_to_inverse_egress_exact_payload_and_phase_provenance():
    from hhs_runtime.hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1 import (
        build_generator, trace_hash216_inverse_egress,
    )
    offsets = tuple((i * 7 + 3) % 9 for i in range(81))
    generator = build_generator(
        decimal_text="179971.179971", offsets=offsets, fibonacci_depth=10,
    )
    trace = trace_hash216_inverse_egress(generator)
    expected = generator["palindromic_rna_ingress"]["scientific_serialization"]["serialized_sha256"]
    assert trace["source_serial_sha256"] == expected
    assert trace["egress_serial_sha256"] == expected
    assert trace["generator_hash216"] == generator["generator_hash216"]
    assert trace["binary64_bits_hex"] == generator["palindromic_rna_ingress"]["binary64_bits_hex"]
    assert len(trace["genesis_offset_metadata_sha256"]) == 64
    assert trace["carrier_receipt_sha256"] == generator["palindromic_rna_ingress"]["carrier_receipt_sha256"]
    assert trace["rna_witness_receipt_sha256"] == generator["palindromic_rna_ingress"]["rna_witness_receipt_sha256"]
    assert trace["rna_double_reverse_exact"] is True
    assert trace["decimal_ieee_co_resident"] is True
    assert trace["i065_hash216_72_vertex_count"] == 72
    assert len(trace["i065_hash216_72_vertex_geometry_sha256"]) == 64
    assert trace["i019_exact_inverse_egress"] is True
    assert trace["hash216_hydration_roundtrip_exact"] is True
    assert trace["phase_gate_executed"] is False
    assert trace["external_egress_authorized"] is False
    assert trace["canonical_vm81_mint_authority"] is False


def test_i073_hash216_egress_trace_replay_fails_closed_on_metadata_mutation():
    from copy import deepcopy
    import pytest
    from hhs_runtime.hhs_pass220_i073_palindromic_rna_fibonacci_symbolic_tensor_v1 import (
        build_generator, trace_hash216_inverse_egress,
        validate_hash216_inverse_egress_trace, Pass220I073GeneratorError,
    )
    generator = build_generator(
        decimal_text="179971.179971",
        offsets=tuple((i * 7 + 3) % 9 for i in range(81)),
        fibonacci_depth=10,
    )
    trace = trace_hash216_inverse_egress(generator)
    assert validate_hash216_inverse_egress_trace(generator, trace) is True
    for key, mutation in (
        ("genesis_offset_metadata_sha256", "0" * 64),
        ("module29_phase_map_sha256", "0" * 64),
        ("i065_hash216_72_vertex_geometry_sha256", "0" * 64),
        ("i065_hash216_72_vertex_count", 71),
        ("generator_hash216", "0" * 216),
        ("binary64_bits_hex", "0" * 16),
        ("rna_double_reverse_exact", False),
        ("i019_exact_inverse_egress", False),
        ("external_egress_authorized", True),
    ):
        forged = deepcopy(trace)
        forged[key] = mutation
        with pytest.raises(Pass220I073GeneratorError):
            validate_hash216_inverse_egress_trace(generator, forged)
    forged = deepcopy(trace)
    forged["unauthorized_extra_authority"] = True
    with pytest.raises(Pass220I073GeneratorError):
        validate_hash216_inverse_egress_trace(generator, forged)

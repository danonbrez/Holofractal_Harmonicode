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

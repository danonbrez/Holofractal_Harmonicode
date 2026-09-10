#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <string.h>

static int ck(int v) { return v ? 0 : 1; }

int main(void) {
    const uint8_t q = (uint8_t)(HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS / 4U);
    HHSExactPass219HHCQSymbolicPhaseDescriptorV1 d;
    HHSExactPass219HHCQSymbolicCarrierV1 direct;
    HHSExactPass219HHCQSymbolicCarrierV1 reverse;
    HHSExactPass219HHCQSymbolicCarrierV1 mixed;
    HHSExactPass219HHCQSymbolicCarrierV1 tampered;
    HHSExactPass219OctonionStateV1 raw_direct;
    HHSExactPass219OctonionStateV1 raw_zero;
    HHSExactPass219OctonionStateV1 raw_arbitrary;
    HHSExactPass219HHCQSymbolicAdmissionV1 admission;
    HHSExactPass219HHCQSymbolicEquilibriumV1 equilibrium;
    HHSExactPass219HHCQSymbolicGateV1 gate;
    HHSExactPass219HHCQSymbolicManifoldV1 manifold_a;
    HHSExactPass219HHCQSymbolicManifoldV1 manifold_b;

    memset(&d, 0, sizeof(d));
    if (ck(hhs_exact_pass219_hhcq_symbolic_phase_version() ==
           HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION)) return 1;
    if (ck(hhs_exact_pass219_hhcq_symbolic_phase_descriptor(&d) == HHS_EXACT_STATUS_OK)) return 2;
    if (ck(d.struct_size == sizeof(d) &&
           d.version == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION &&
           d.phase_modulus == 72U && d.parameter_count == 5184U && d.basis_count == 8U &&
           d.inherited_policy_state_bytes == 112U && d.phase11_source_bytes == 700U &&
           d.symbolic_phase_symbols == 1U && d.global_constraint_graph_required == 1U &&
           d.reciprocal_opposition_relations_required == 1U &&
           d.ordered_noncommutative_products_required == 1U &&
           d.symbolic_phi8_equilibrium == 1U && d.symbolic_x_squared_gate == 1U &&
           d.phase11_scalar_equilibrium_superseded == 1U &&
           d.phase11_scalar_parity_superseded == 1U &&
           d.raw_phase_residue_authority == 0U && d.scalar_phase_sum_authority == 0U &&
           d.scalar_x_parity_authority == 0U && d.phase10_projection_witness_only == 1U &&
           d.candidate_only == 1U && d.canonical_mutation_authority == 0U &&
           d.canonical_hash72_authority == 0U && d.canonical_hash216_authority == 0U &&
           d.canonical_persistence_authority == 0U && d.floating_point_authority == 0U)) return 3;

    memset(&direct, 0, sizeof(direct));
    if (ck(hhs_exact_pass219_hhcq_symbolic_carrier_construct(
               HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT,
               HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT,
               &direct) == HHS_EXACT_STATUS_OK)) return 4;
    if (ck(direct.x_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I &&
           direct.y_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3 &&
           direct.z_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I &&
           direct.w_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3 &&
           direct.xy_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4 &&
           direct.yx_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           direct.zw_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4 &&
           direct.wz_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           direct.x_inverse_y == 1U && direct.y_opposes_x == 1U &&
           direct.z_inverse_w == 1U && direct.w_opposes_z == 1U &&
           direct.ordered_noncommutative_products == 1U && direct.global_relation_graph_exact == 1U &&
           direct.projection_residue72[HHS_EXACT_PHASE_X] == q &&
           direct.projection_residue72[HHS_EXACT_PHASE_Y] == (uint8_t)(3U*q) &&
           direct.projection_residue72[HHS_EXACT_PHASE_XY] == 0U &&
           direct.projection_residue72[HHS_EXACT_PHASE_YX] == (uint8_t)(2U*q) &&
           direct.projection_residue_authority == 0U &&
           direct.canonical_authority_changed == 0U && direct.floating_point_authority == 0U)) return 5;

    memset(&reverse, 0, sizeof(reverse));
    if (ck(hhs_exact_pass219_hhcq_symbolic_carrier_construct(
               HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED,
               HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED,
               &reverse) == HHS_EXACT_STATUS_OK)) return 6;
    if (ck(reverse.x_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3 &&
           reverse.y_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I &&
           reverse.z_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3 &&
           reverse.w_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I &&
           reverse.xy_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4 &&
           reverse.yx_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           reverse.global_relation_graph_exact == 1U)) return 7;

    memset(&mixed, 0, sizeof(mixed));
    if (ck(hhs_exact_pass219_hhcq_symbolic_carrier_construct(
               HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT,
               HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED,
               &mixed) == HHS_EXACT_STATUS_OK && mixed.global_relation_graph_exact == 1U)) return 8;
    if (ck(hhs_exact_pass219_hhcq_symbolic_carrier_validate(&direct) == HHS_EXACT_STATUS_OK &&
           hhs_exact_pass219_hhcq_symbolic_carrier_validate(&reverse) == HHS_EXACT_STATUS_OK &&
           hhs_exact_pass219_hhcq_symbolic_carrier_validate(&mixed) == HHS_EXACT_STATUS_OK)) return 9;
    tampered = direct;
    tampered.x_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
    if (ck(hhs_exact_pass219_hhcq_symbolic_carrier_validate(&tampered) ==
           HHS_EXACT_STATUS_INVARIANT_FAILURE)) return 10;

    memset(&raw_direct, 0, sizeof(raw_direct));
    if (ck(hhs_exact_pass219_octonion_expand(q, (uint8_t)(3U*q), q, (uint8_t)(3U*q),
                                             &raw_direct) == HHS_EXACT_STATUS_OK)) return 11;
    memset(&admission, 0, sizeof(admission));
    if (ck(hhs_exact_pass219_hhcq_symbolic_admit_projection(&raw_direct, &admission) ==
               HHS_EXACT_STATUS_OK && admission.raw_projection_valid == 1U &&
           admission.raw_projection_matches_symbolic_carrier == 1U &&
           admission.symbolic_carrier_admitted == 1U &&
           admission.raw_projection_authority == 0U &&
           admission.scalar_zero_reinterpreted_as_symbolic_zero == 0U)) return 12;

    memset(&raw_zero, 0, sizeof(raw_zero));
    if (ck(hhs_exact_pass219_octonion_expand(0U, 0U, q, (uint8_t)(3U*q), &raw_zero) ==
           HHS_EXACT_STATUS_OK)) return 13;
    memset(&admission, 0, sizeof(admission));
    if (ck(hhs_exact_pass219_hhcq_symbolic_admit_projection(&raw_zero, &admission) ==
               HHS_EXACT_STATUS_OK && admission.raw_projection_valid == 1U &&
           admission.symbolic_carrier_admitted == 0U && admission.raw_projection_authority == 0U &&
           admission.scalar_zero_reinterpreted_as_symbolic_zero == 0U)) return 14;

    memset(&raw_arbitrary, 0, sizeof(raw_arbitrary));
    if (ck(hhs_exact_pass219_octonion_expand(2U, 3U, 5U, 7U, &raw_arbitrary) ==
           HHS_EXACT_STATUS_OK)) return 15;
    memset(&admission, 0, sizeof(admission));
    if (ck(hhs_exact_pass219_hhcq_symbolic_admit_projection(&raw_arbitrary, &admission) ==
               HHS_EXACT_STATUS_OK && admission.symbolic_carrier_admitted == 0U)) return 16;

    memset(&equilibrium, 0, sizeof(equilibrium));
    if (ck(hhs_exact_pass219_hhcq_symbolic_equilibrium(&direct, 2U, 3U, &equilibrium) ==
               HHS_EXACT_STATUS_OK && equilibrium.phi8_symbolic == 1U &&
           equilibrium.macro_p_symbolic == 1U && equilibrium.equilibrium_relation_present == 1U &&
           equilibrium.equilibrium_relation_well_typed == 1U &&
           equilibrium.scalar_phase_sum_evaluated == 0U &&
           equilibrium.scalar_macro_p_constructed == 0U && equilibrium.prime_seed_pair_valid == 1U &&
           equilibrium.canonical_authority_changed == 0U && equilibrium.floating_point_authority == 0U)) return 17;

    memset(&gate, 0, sizeof(gate));
    if (ck(hhs_exact_pass219_hhcq_symbolic_gate(&direct, 2U, 3U, 0U, &gate) ==
               HHS_EXACT_STATUS_OK &&
           gate.x_squared_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           gate.negative_xy_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           gate.carrier_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT &&
           gate.symbolic_exponent_retained == 1U && gate.symbolic_square_relation_exact == 1U &&
           gate.typed_gate_well_formed == 1U && gate.scalar_x_parity_evaluated == 0U &&
           gate.ordinary_power_evaluated == 0U && gate.phase10_projection_executed == 1U &&
           gate.phase10_projection_authority == 0U && gate.resolution_noncoarsening == 1U &&
           gate.canonical_authority_changed == 0U && gate.floating_point_authority == 0U)) return 18;
    memset(&gate, 0, sizeof(gate));
    if (ck(hhs_exact_pass219_hhcq_symbolic_gate(&reverse, 2U, 3U, 0U, &gate) ==
               HHS_EXACT_STATUS_OK &&
           gate.x_squared_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 &&
           gate.carrier_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED &&
           gate.scalar_x_parity_evaluated == 0U)) return 19;

    memset(&manifold_a, 0, sizeof(manifold_a));
    memset(&manifold_b, 0, sizeof(manifold_b));
    if (ck(hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
               &direct, 2U, 3U, 0U, &manifold_a) == HHS_EXACT_STATUS_OK &&
           hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
               &direct, 2U, 3U, 0U, &manifold_b) == HHS_EXACT_STATUS_OK &&
           memcmp(&manifold_a, &manifold_b, sizeof(manifold_a)) == 0 &&
           manifold_a.symbolic_carrier_admitted == 1U &&
           manifold_a.global_relation_graph_exact == 1U &&
           manifold_a.symbolic_equilibrium_exact == 1U &&
           manifold_a.symbolic_square_gate_exact == 1U &&
           manifold_a.ordered_products_exact == 1U &&
           manifold_a.constraint_intersection_satisfied == 1U &&
           manifold_a.raw_projection_authority == 0U &&
           manifold_a.scalar_integer_semantic_authority == 0U &&
           manifold_a.canonical_mutation_authority == 0U &&
           manifold_a.canonical_hash72_authority == 0U &&
           manifold_a.canonical_hash216_authority == 0U &&
           manifold_a.canonical_persistence_authority == 0U &&
           manifold_a.floating_point_authority == 0U)) return 20;

    memset(&manifold_a, 0, sizeof(manifold_a));
    if (ck(hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
               &raw_zero, 2U, 3U, 0U, &manifold_a) == HHS_EXACT_STATUS_OK &&
           manifold_a.admission.raw_projection_valid == 1U &&
           manifold_a.symbolic_carrier_admitted == 0U &&
           manifold_a.constraint_intersection_satisfied == 0U &&
           manifold_a.raw_projection_authority == 0U &&
           manifold_a.scalar_integer_semantic_authority == 0U)) return 21;

    if (ck(hhs_exact_pass219_hhcq_symbolic_equilibrium(&direct, 4U, 3U, &equilibrium) ==
           HHS_EXACT_STATUS_RANGE_ERROR)) return 22;
    if (ck(hhs_exact_pass219_hhcq_symbolic_carrier_construct(0U,
           HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT, &direct) ==
           HHS_EXACT_STATUS_RANGE_ERROR)) return 23;

    return 0;
}

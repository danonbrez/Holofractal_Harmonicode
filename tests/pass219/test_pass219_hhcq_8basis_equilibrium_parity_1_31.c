#include "../../hhs_runtime/include/hhs_runtime_exact_abi.h"

#include <stdint.h>
#include <string.h>

static int check(int condition) {
    return condition ? 0 : 1;
}

static int make_state(
    uint8_t x,
    uint8_t y,
    uint8_t z,
    uint8_t w,
    HHSExactPass219OctonionStateV1 *out
) {
    if (hhs_exact_pass219_octonion_expand(x, y, z, w, out) != HHS_EXACT_STATUS_OK)
        return 0;
    return hhs_exact_pass219_octonion_validate_state(out) == HHS_EXACT_STATUS_OK;
}

int main(void) {
    static const uint8_t expected_sha[32] = {
        0x7dU, 0x87U, 0xd4U, 0x68U, 0xe5U, 0x28U, 0xf3U, 0x0dU,
        0xf6U, 0x76U, 0x8bU, 0x13U, 0x0fU, 0x62U, 0x60U, 0x77U,
        0xabU, 0x97U, 0x86U, 0xe8U, 0x2dU, 0x2dU, 0xbeU, 0x57U,
        0x7aU, 0x12U, 0x07U, 0x53U, 0xcdU, 0xaeU, 0xdcU, 0x60U
    };
    static const char expected_source[] =
        "P^2/{(t^3-t=(P\302\263-P/(P\302\262-pq)=(t\302\263-t)/\342\210\206=P\302\262(MOD)(pq))=m^2-m)-(({{b^4,c^4,c^2-u^(b\342\201\266c\342\201\264)},{c^2,((b^2)(c^2)-(a^2))/u^((s==(b^(2c^2)c^b^4)^2)/((b\342\201\266c\342\201\264)P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b\342\201\266c\342\201\264)*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+\342\210\206)-P^2)/(t^3-t)*u^72} where \342\210\206/P=\342\210\232(pq+u\342\201\267\302\262)^x\302\262 and b\302\262P-(p+q)=x+y+z+w+xy+yx+zw+wz\n\na\302\262=(NcalcMatrixPower((List(List(x,w,(yx)),List((wz),x+y+z+w,(zw)),List((xy),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))^b\342\201\264\n\nSqrt((AB))(AB)/Sqrt((AB))==A/BB/A==((-xy)^(((x+y^2)(y+x^2))/((x\302\262+y\302\262)\302\262Sqrt((a*b)))))^x\302\262 where A,B are two primes and AB=P\342\201\264";
    HHSExactPass219HHCQ8BasisParityDescriptorV1 descriptor;
    HHSExactPass219OctonionStateV1 even_state;
    HHSExactPass219OctonionStateV1 odd_state;
    HHSExactPass219HHCQ8BasisEquilibriumV1 constructed;
    HHSExactPass219HHCQ8BasisEquilibriumV1 validated;
    HHSExactPass219HHCQ8BasisEquilibriumV1 drifted;
    HHSExactPass219HHCQParityGateV1 even_gate;
    HHSExactPass219HHCQParityGateV1 odd_gate;
    HHSExactPass219HHCQ8BasisManifoldV1 manifold_a;
    HHSExactPass219HHCQ8BasisManifoldV1 manifold_b;
    HHSExactPass219OctonionSurfaceV1 vm_surface;
    HHSExactVM81Frame frame;
    uint8_t source[HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES];
    size_t source_length = 0U;
    uint32_t direct_count = 0U;
    uint32_t reversed_count = 0U;
    uint32_t x;
    uint32_t i;

    memset(&descriptor, 0, sizeof(descriptor));
    if (check(hhs_exact_pass219_hhcq_8basis_parity_version() ==
              HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION)) return 1;
    if (check(hhs_exact_pass219_hhcq_8basis_parity_descriptor(&descriptor) ==
              HHS_EXACT_STATUS_OK)) return 2;
    if (check(descriptor.struct_size == sizeof(descriptor) &&
              descriptor.version == HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION &&
              descriptor.source_bytes == 700U &&
              descriptor.inherited_policy_state_bytes == 112U &&
              descriptor.a2 == 1U && descriptor.b2 == 2U && descriptor.c2 == 3U &&
              descriptor.update_quantum == 5U && descriptor.phase_modulus == 72U &&
              descriptor.parameter_count == 5184U && descriptor.basis_count == 8U &&
              descriptor.verbatim_source_preserved == 1U &&
              descriptor.basis_constants_derived == 1U &&
              descriptor.complete_8basis_equilibrium == 1U &&
              descriptor.ordered_noncommutative_products_preserved == 1U &&
              descriptor.exact_rational_macro_p == 1U &&
              descriptor.independent_equilibrium_validator == 1U &&
              descriptor.candidate_transport_delta_only == 1U &&
              descriptor.squared_coordinate_orientation_gate == 1U &&
              descriptor.x2_parity_equals_x_parity == 1U &&
              descriptor.symbolic_exponent_retained == 1U &&
              descriptor.ordinary_negative_base_exponent_evaluated == 0U &&
              descriptor.matrix_order_contract_preserved == 1U &&
              descriptor.phase10_prime_rational_semantics_inherited == 1U &&
              descriptor.eval_under_vm81_constraint_intersection == 1U &&
              descriptor.candidate_only == 1U && descriptor.exact_integer_only == 1U &&
              descriptor.canonical_mutation_authority == 0U &&
              descriptor.canonical_hash72_authority == 0U &&
              descriptor.canonical_hash216_authority == 0U &&
              descriptor.canonical_persistence_authority == 0U &&
              descriptor.floating_point_authority == 0U &&
              memcmp(descriptor.source_sha256, expected_sha, sizeof(expected_sha)) == 0)) return 3;

    if (check(sizeof(expected_source) - 1U ==
              HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES)) return 4;
    if (check(hhs_exact_pass219_hhcq_8basis_parity_source(
                  source, sizeof(source), &source_length) == HHS_EXACT_STATUS_OK &&
              source_length == sizeof(source) &&
              memcmp(source, expected_source, sizeof(source)) == 0)) return 5;

    if (check(make_state(2U, 3U, 5U, 7U, &even_state))) return 6;
    if (check(make_state(3U, 2U, 5U, 7U, &odd_state))) return 7;
    if (check(even_state.xy != even_state.yx && even_state.zw != even_state.wz &&
              odd_state.xy != odd_state.yx && odd_state.zw != odd_state.wz)) return 8;

    memset(&constructed, 0, sizeof(constructed));
    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
                  2U, 3U, &even_state, &constructed) == HHS_EXACT_STATUS_OK)) return 9;
    if (check(constructed.macro_p_constructed_from_phase_state == 1U &&
              constructed.macro_p_supplied_independently == 0U &&
              constructed.equilibrium_exact == 1U &&
              constructed.transport_reconciliation_required == 0U &&
              constructed.transport_delta_numerator == 0 &&
              constructed.transport_delta_denominator == 1U &&
              constructed.ordered_products_preserved == 1U &&
              constructed.candidate_only == 1U &&
              constructed.canonical_authority_changed == 0U &&
              constructed.floating_point_authority == 0U &&
              2U * constructed.macro_p_numerator ==
                  constructed.macro_p_denominator *
                  ((uint64_t)constructed.phase_sum + 2U + 3U))) return 10;

    memset(&validated, 0, sizeof(validated));
    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
                  2U, 3U, &even_state,
                  constructed.macro_p_numerator,
                  constructed.macro_p_denominator,
                  &validated) == HHS_EXACT_STATUS_OK)) return 11;
    if (check(validated.macro_p_constructed_from_phase_state == 0U &&
              validated.macro_p_supplied_independently == 1U &&
              validated.equilibrium_exact == 1U &&
              validated.transport_reconciliation_required == 0U)) return 12;

    memset(&drifted, 0, sizeof(drifted));
    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
                  2U, 3U, &even_state,
                  constructed.macro_p_numerator + constructed.macro_p_denominator,
                  constructed.macro_p_denominator,
                  &drifted) == HHS_EXACT_STATUS_OK)) return 13;
    if (check(drifted.equilibrium_exact == 0U &&
              drifted.transport_reconciliation_required == 1U &&
              drifted.transport_delta_numerator == 2 &&
              drifted.transport_delta_denominator == 1U &&
              drifted.transport_delta_integral == 1U &&
              drifted.canonical_authority_changed == 0U)) return 14;

    memset(&even_gate, 0, sizeof(even_gate));
    if (check(hhs_exact_pass219_hhcq_parity_gate(
                  2U, 3U, &even_state, 0U, &even_gate) == HHS_EXACT_STATUS_OK)) return 15;
    if (check(even_gate.x_squared_parity == 0U &&
              even_gate.orientation == HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_DIRECT &&
              even_gate.orientation_sign == 1 &&
              even_gate.x2_parity_identity_exact == 1U &&
              even_gate.symbolic_exponent_retained == 1U &&
              even_gate.ordinary_negative_base_exponent_evaluated == 0U &&
              even_gate.matrix_order_exact == 1U &&
              even_gate.ordered_xy_phase == even_state.xy &&
              even_gate.ordered_yx_phase == even_state.yx &&
              even_gate.ordered_zw_phase == even_state.zw &&
              even_gate.ordered_wz_phase == even_state.wz &&
              even_gate.canonical_authority_changed == 0U &&
              even_gate.floating_point_authority == 0U)) return 16;

    memset(&odd_gate, 0, sizeof(odd_gate));
    if (check(hhs_exact_pass219_hhcq_parity_gate(
                  2U, 3U, &odd_state, 0U, &odd_gate) == HHS_EXACT_STATUS_OK)) return 17;
    if (check(odd_gate.x_squared_parity == 1U &&
              odd_gate.orientation == HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_REVERSED &&
              odd_gate.orientation_sign == -1 &&
              odd_gate.x2_parity_identity_exact == 1U)) return 18;

    for (x = 0U; x < 72U; ++x) {
        HHSExactPass219OctonionStateV1 state;
        HHSExactPass219HHCQParityGateV1 gate;
        if (check(make_state((uint8_t)x, 1U, 2U, 3U, &state))) return 19;
        memset(&gate, 0, sizeof(gate));
        if (check(hhs_exact_pass219_hhcq_parity_gate(
                      2U, 3U, &state, 0U, &gate) == HHS_EXACT_STATUS_OK)) return 20;
        if (check(gate.x_squared_parity == (uint8_t)(x & 1U) &&
                  gate.x2_parity_identity_exact == 1U)) return 21;
        if (gate.orientation == HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_DIRECT)
            ++direct_count;
        else if (gate.orientation == HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_REVERSED)
            ++reversed_count;
        else
            return 22;
    }
    if (check(direct_count == 36U && reversed_count == 36U)) return 23;

    memset(&manifold_a, 0, sizeof(manifold_a));
    memset(&manifold_b, 0, sizeof(manifold_b));
    if (check(hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
                  2U, 3U, &even_state,
                  constructed.macro_p_numerator,
                  constructed.macro_p_denominator,
                  0U, &manifold_a) == HHS_EXACT_STATUS_OK)) return 24;
    if (check(hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
                  2U, 3U, &even_state,
                  constructed.macro_p_numerator,
                  constructed.macro_p_denominator,
                  0U, &manifold_b) == HHS_EXACT_STATUS_OK)) return 25;
    if (check(memcmp(&manifold_a, &manifold_b, sizeof(manifold_a)) == 0 &&
              manifold_a.octonion_state_valid == 1U &&
              manifold_a.full_octonion_surface_validated == 0U &&
              manifold_a.phase10_product_closure_valid == 1U &&
              manifold_a.matrix_order_exact == 1U &&
              manifold_a.equilibrium_exact == 1U &&
              manifold_a.parity_orientation_exact == 1U &&
              manifold_a.constraint_intersection_satisfied == 1U &&
              manifold_a.candidate_only == 1U &&
              manifold_a.exact_integer_only == 1U &&
              manifold_a.canonical_mutation_authority == 0U &&
              manifold_a.canonical_hash72_authority == 0U &&
              manifold_a.canonical_hash216_authority == 0U &&
              manifold_a.canonical_persistence_authority == 0U &&
              manifold_a.floating_point_authority == 0U)) return 26;

    memset(&manifold_b, 0, sizeof(manifold_b));
    if (check(hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
                  2U, 3U, &even_state,
                  constructed.macro_p_numerator + constructed.macro_p_denominator,
                  constructed.macro_p_denominator,
                  0U, &manifold_b) == HHS_EXACT_STATUS_OK)) return 27;
    if (check(manifold_b.equilibrium_exact == 0U &&
              manifold_b.equilibrium.transport_reconciliation_required == 1U &&
              manifold_b.constraint_intersection_satisfied == 0U &&
              manifold_b.canonical_mutation_authority == 0U)) return 28;

    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
                  4U, 3U, &even_state, &constructed) == HHS_EXACT_STATUS_RANGE_ERROR)) return 29;
    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
                  2U, 2U, &even_state, &constructed) == HHS_EXACT_STATUS_RANGE_ERROR)) return 30;
    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
                  2U, 3U, &even_state, 1U, 0U, &validated) ==
              HHS_EXACT_STATUS_RANGE_ERROR)) return 31;

    memset(&frame, 0, sizeof(frame));
    for (i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x9e3779b97f4a7c15) ^
            ((uint64_t)i * UINT64_C(0x100000001b3));
    memset(&vm_surface, 0, sizeof(vm_surface));
    if (check(hhs_exact_pass219_octonion_from_vm81(
                  &frame, 0U, 1U, 2U, 3U, &vm_surface) == HHS_EXACT_STATUS_OK &&
              hhs_exact_pass219_octonion_validate_surface(&vm_surface) ==
                  HHS_EXACT_STATUS_OK)) return 32;
    memset(&constructed, 0, sizeof(constructed));
    if (check(hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
                  2U, 3U, &vm_surface.state, &constructed) == HHS_EXACT_STATUS_OK)) return 33;
    memset(&manifold_a, 0, sizeof(manifold_a));
    if (check(hhs_exact_pass219_hhcq_8basis_from_vm81(
                  &frame, 0U, 1U, 2U, 3U,
                  2U, 3U,
                  constructed.macro_p_numerator,
                  constructed.macro_p_denominator,
                  0U, &manifold_a) == HHS_EXACT_STATUS_OK)) return 34;
    if (check(manifold_a.full_octonion_surface_validated == 1U &&
              manifold_a.constraint_intersection_satisfied == 1U &&
              manifold_a.canonical_mutation_authority == 0U &&
              manifold_a.floating_point_authority == 0U)) return 35;

    return 0;
}

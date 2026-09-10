#include "../include/hhs_pass219_hhcq_8basis_equilibrium_parity_1_31.h"

#include <limits.h>
#include <string.h>

static const char HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE[] =
    "P^2/{(t^3-t=(P\302\263-P/(P\302\262-pq)=(t\302\263-t)/\342\210\206=P\302\262(MOD)(pq))=m^2-m)-(({{b^4,c^4,c^2-u^(b\342\201\266c\342\201\264)},{c^2,((b^2)(c^2)-(a^2))/u^((s==(b^(2c^2)c^b^4)^2)/((b\342\201\266c\342\201\264)P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b\342\201\266c\342\201\264)*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+\342\210\206)-P^2)/(t^3-t)*u^72} where \342\210\206/P=\342\210\232(pq+u\342\201\267\302\262)^x\302\262 and b\302\262P-(p+q)=x+y+z+w+xy+yx+zw+wz\n\na\302\262=(NcalcMatrixPower((List(List(x,w,(yx)),List((wz),x+y+z+w,(zw)),List((xy),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))^b\342\201\264\n\nSqrt((AB))(AB)/Sqrt((AB))==A/BB/A==((-xy)^(((x+y^2)(y+x^2))/((x\302\262+y\302\262)\302\262Sqrt((a*b)))))^x\302\262 where A,B are two primes and AB=P\342\201\264";

static const uint8_t HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_SHA256[
    HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SHA256_BYTES
] = {
    0x7dU, 0x87U, 0xd4U, 0x68U, 0xe5U, 0x28U, 0xf3U, 0x0dU,
    0xf6U, 0x76U, 0x8bU, 0x13U, 0x0fU, 0x62U, 0x60U, 0x77U,
    0xabU, 0x97U, 0x86U, 0xe8U, 0x2dU, 0x2dU, 0xbeU, 0x57U,
    0x7aU, 0x12U, 0x07U, 0x53U, 0xcdU, 0xaeU, 0xdcU, 0x60U
};

_Static_assert(sizeof(HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE) - 1U ==
               HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES,
               "Phase11 8-basis source byte length drift");

static uint64_t hhs_p219_p11_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static uint64_t hhs_p219_p11_gcd64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        uint64_t r = a % b;
        a = b;
        b = r;
    }
    return a;
}

static int hhs_p219_p11_is_prime(uint32_t n) {
    uint32_t d;
    if (n < 2U || n > HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_MAX_PRIME)
        return 0;
    if (n == 2U)
        return 1;
    if ((n & 1U) == 0U)
        return 0;
    for (d = 3U; d <= n / d; d += 2U) {
        if (n % d == 0U)
            return 0;
    }
    return 1;
}

static int hhs_p219_p11_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL || (a != 0U && b > UINT64_MAX / a))
        return 0;
    *out = a * b;
    return 1;
}

static HHSExactStatus hhs_p219_p11_validate_primes(uint16_t prime_p, uint16_t prime_q) {
    if (!hhs_p219_p11_is_prime(prime_p) ||
        !hhs_p219_p11_is_prime(prime_q) ||
        prime_p == prime_q)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_p11_phase_sum(
    const HHSExactPass219OctonionStateV1 *state,
    uint16_t *out_sum
) {
    uint32_t sum;
    HHSExactStatus status;
    if (state == NULL || out_sum == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_octonion_validate_state(state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    sum = (uint32_t)state->x + (uint32_t)state->y +
          (uint32_t)state->z + (uint32_t)state->w +
          (uint32_t)state->xy + (uint32_t)state->yx +
          (uint32_t)state->zw + (uint32_t)state->wz;
    if (sum > UINT16_MAX)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    *out_sum = (uint16_t)sum;
    return HHS_EXACT_STATUS_OK;
}

static int hhs_p219_p11_order_contract(
    const HHSExactPass219OctonionStateV1 *state
) {
    HHSExactPass219OctonionProductV1 xy;
    HHSExactPass219OctonionProductV1 yx;
    HHSExactPass219OctonionProductV1 zw;
    HHSExactPass219OctonionProductV1 wz;
    if (state == NULL ||
        hhs_exact_pass219_octonion_validate_state(state) != HHS_EXACT_STATUS_OK)
        return 0;
    if (hhs_exact_pass219_octonion_multiply(
            state, HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &xy) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_octonion_multiply(
            state, HHS_EXACT_PHASE_Y, HHS_EXACT_PHASE_X, &yx) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_octonion_multiply(
            state, HHS_EXACT_PHASE_Z, HHS_EXACT_PHASE_W, &zw) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_octonion_multiply(
            state, HHS_EXACT_PHASE_W, HHS_EXACT_PHASE_Z, &wz) != HHS_EXACT_STATUS_OK)
        return 0;
    return xy.phase == state->xy && yx.phase == state->yx &&
           zw.phase == state->zw && wz.phase == state->wz &&
           state->xy != state->yx && state->zw != state->wz;
}

static uint64_t hhs_p219_p11_state_signature(
    const HHSExactPass219OctonionStateV1 *state
) {
    uint64_t packed = 0U;
    packed |= (uint64_t)state->x;
    packed |= (uint64_t)state->y << 8U;
    packed |= (uint64_t)state->z << 16U;
    packed |= (uint64_t)state->w << 24U;
    packed |= (uint64_t)state->xy << 32U;
    packed |= (uint64_t)state->yx << 40U;
    packed |= (uint64_t)state->zw << 48U;
    packed |= (uint64_t)state->wz << 56U;
    return hhs_p219_p11_mix64(packed ^ UINT64_C(0x2198ba51131));
}

static HHSExactStatus hhs_p219_p11_equilibrium_fill(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    uint8_t constructed,
    uint8_t supplied,
    HHSExactPass219HHCQ8BasisEquilibriumV1 *out_equilibrium
) {
    HHSExactStatus status;
    uint16_t phase_sum;
    uint64_t rational_gcd;
    uint64_t twice_p;
    uint64_t rhs_scale;
    uint64_t delta_abs;
    uint64_t delta_gcd;
    int64_t delta_num;
    uint64_t delta_den;
    uint64_t signature;

    if (phase_state == NULL || out_equilibrium == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_p219_p11_validate_primes(prime_p, prime_q);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (macro_p_denominator == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    status = hhs_p219_p11_phase_sum(phase_state, &phase_sum);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hhs_p219_p11_order_contract(phase_state))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    rational_gcd = hhs_p219_p11_gcd64(macro_p_numerator, macro_p_denominator);
    if (rational_gcd == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    macro_p_numerator /= rational_gcd;
    macro_p_denominator /= rational_gcd;

    if (!hhs_p219_p11_mul_u64(macro_p_numerator, 2U, &twice_p) ||
        !hhs_p219_p11_mul_u64(
            macro_p_denominator,
            (uint64_t)prime_p + (uint64_t)prime_q + (uint64_t)phase_sum,
            &rhs_scale))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    if (twice_p >= rhs_scale) {
        delta_abs = twice_p - rhs_scale;
        if (delta_abs > (uint64_t)INT64_MAX)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        delta_num = (int64_t)delta_abs;
    } else {
        delta_abs = rhs_scale - twice_p;
        if (delta_abs > (uint64_t)INT64_MAX)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        delta_num = -(int64_t)delta_abs;
    }

    if (delta_abs == 0U) {
        delta_den = 1U;
    } else {
        delta_gcd = hhs_p219_p11_gcd64(delta_abs, macro_p_denominator);
        if (delta_gcd == 0U)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        delta_num /= (int64_t)delta_gcd;
        delta_den = macro_p_denominator / delta_gcd;
    }

    memset(out_equilibrium, 0, sizeof(*out_equilibrium));
    out_equilibrium->struct_size = (uint32_t)sizeof(*out_equilibrium);
    out_equilibrium->version = HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION;
    out_equilibrium->prime_p = prime_p;
    out_equilibrium->prime_q = prime_q;
    out_equilibrium->phase_state = *phase_state;
    out_equilibrium->phase_sum = phase_sum;
    out_equilibrium->macro_p_numerator = macro_p_numerator;
    out_equilibrium->macro_p_denominator = macro_p_denominator;
    out_equilibrium->transport_delta_numerator = delta_num;
    out_equilibrium->transport_delta_denominator = delta_den;
    out_equilibrium->macro_p_constructed_from_phase_state = constructed;
    out_equilibrium->macro_p_supplied_independently = supplied;
    out_equilibrium->equilibrium_exact = delta_num == 0 ? 1U : 0U;
    out_equilibrium->transport_reconciliation_required = delta_num == 0 ? 0U : 1U;
    out_equilibrium->transport_delta_integral = delta_den == 1U ? 1U : 0U;
    out_equilibrium->ordered_products_preserved = 1U;
    out_equilibrium->candidate_only = 1U;
    out_equilibrium->exact_integer_only = 1U;

    signature = UINT64_C(0x2198ba511310001) ^
        ((uint64_t)prime_p << 48U) ^ ((uint64_t)prime_q << 32U) ^
        (uint64_t)phase_sum ^ hhs_p219_p11_state_signature(phase_state) ^
        hhs_p219_p11_mix64(macro_p_numerator) ^
        hhs_p219_p11_mix64(macro_p_denominator) ^
        hhs_p219_p11_mix64((uint64_t)delta_num) ^
        hhs_p219_p11_mix64(delta_den) ^
        ((uint64_t)constructed << 2U) ^ ((uint64_t)supplied << 3U);
    out_equilibrium->equilibrium_signature64 = hhs_p219_p11_mix64(signature);
    return HHS_EXACT_STATUS_OK;
}

static uint64_t hhs_p219_p11_manifold_signature(
    const HHSExactPass219HHCQ8BasisManifoldV1 *manifold
) {
    uint64_t x = UINT64_C(0x2198ba51131f00d) ^
        manifold->equilibrium.equilibrium_signature64 ^
        manifold->parity_gate.parity_signature64 ^
        ((uint64_t)manifold->octonion_state_valid << 1U) ^
        ((uint64_t)manifold->full_octonion_surface_validated << 2U) ^
        ((uint64_t)manifold->phase10_product_closure_valid << 3U) ^
        ((uint64_t)manifold->matrix_order_exact << 4U) ^
        ((uint64_t)manifold->equilibrium_exact << 5U) ^
        ((uint64_t)manifold->parity_orientation_exact << 6U) ^
        ((uint64_t)manifold->constraint_intersection_satisfied << 7U);
    return hhs_p219_p11_mix64(x);
}

uint32_t hhs_exact_pass219_hhcq_8basis_parity_version(void) {
    return HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_8basis_parity_descriptor(
    HHSExactPass219HHCQ8BasisParityDescriptorV1 *out_descriptor
) {
    uint32_t derived72;
    uint32_t derived5184;
    uint32_t derived5;
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    derived5 = 2U * 3U - 1U;
    derived72 = (2U * 2U * 2U) * (3U * 3U);
    derived5184 = derived72 * derived72;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION;
    out_descriptor->source_bytes = HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES;
    out_descriptor->inherited_policy_state_bytes = (uint32_t)sizeof(HHSExactPass219HHCQJointStateV1);
    out_descriptor->a2 = 1U;
    out_descriptor->b2 = 2U;
    out_descriptor->c2 = 3U;
    out_descriptor->update_quantum = HHS_EXACT_PASS219_CORE_CIRCUIT_UPDATE_QUANTUM;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS;
    out_descriptor->parameter_count = HHS_EXACT_VM81_FRAME_BITS;
    out_descriptor->basis_count = HHS_EXACT_PHASE_BASIS_COUNT;
    memcpy(out_descriptor->source_sha256,
           HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_SHA256,
           sizeof(out_descriptor->source_sha256));
    out_descriptor->verbatim_source_preserved = 1U;
    out_descriptor->basis_constants_derived = 1U;
    out_descriptor->complete_8basis_equilibrium = 1U;
    out_descriptor->ordered_noncommutative_products_preserved = 1U;
    out_descriptor->exact_rational_macro_p = 1U;
    out_descriptor->independent_equilibrium_validator = 1U;
    out_descriptor->candidate_transport_delta_only = 1U;
    out_descriptor->squared_coordinate_orientation_gate = 1U;
    out_descriptor->x2_parity_equals_x_parity = 1U;
    out_descriptor->symbolic_exponent_retained = 1U;
    out_descriptor->ordinary_negative_base_exponent_evaluated = 0U;
    out_descriptor->matrix_order_contract_preserved = 1U;
    out_descriptor->phase10_prime_rational_semantics_inherited = 1U;
    out_descriptor->eval_under_vm81_constraint_intersection = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_only = 1U;

    if (derived5 != out_descriptor->update_quantum ||
        derived72 != out_descriptor->phase_modulus ||
        derived5184 != out_descriptor->parameter_count ||
        out_descriptor->basis_count != HHS_EXACT_PASS219_HHCQ_8BASIS_COUNT ||
        out_descriptor->inherited_policy_state_bytes != 112U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_8basis_parity_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length != NULL)
        *out_length = HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES;
    if (out_bytes == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (capacity < HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    memcpy(out_bytes,
           HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE,
           HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_8basis_equilibrium_construct(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    HHSExactPass219HHCQ8BasisEquilibriumV1 *out_equilibrium
) {
    HHSExactStatus status;
    uint16_t phase_sum;
    uint64_t numerator;
    uint64_t denominator = 2U;
    uint64_t gcd;

    if (phase_state == NULL || out_equilibrium == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_p219_p11_validate_primes(prime_p, prime_q);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_p219_p11_phase_sum(phase_state, &phase_sum);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    numerator = (uint64_t)phase_sum + (uint64_t)prime_p + (uint64_t)prime_q;
    gcd = hhs_p219_p11_gcd64(numerator, denominator);
    if (gcd == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    numerator /= gcd;
    denominator /= gcd;
    status = hhs_p219_p11_equilibrium_fill(
        prime_p, prime_q, phase_state, numerator, denominator,
        1U, 0U, out_equilibrium);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (out_equilibrium->equilibrium_exact != 1U ||
        out_equilibrium->transport_reconciliation_required != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    HHSExactPass219HHCQ8BasisEquilibriumV1 *out_equilibrium
) {
    return hhs_p219_p11_equilibrium_fill(
        prime_p, prime_q, phase_state,
        macro_p_numerator, macro_p_denominator,
        0U, 1U, out_equilibrium);
}

HHSExactStatus hhs_exact_pass219_hhcq_parity_gate(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQParityGateV1 *out_gate
) {
    HHSExactStatus status;
    HHSExactPass219HHCQPrimeRationalExpansionV1 expansion;
    uint16_t x_squared;
    uint8_t parity;
    uint64_t signature;

    if (phase_state == NULL || out_gate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_p219_p11_validate_primes(prime_p, prime_q);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_octonion_validate_state(phase_state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hhs_p219_p11_order_contract(phase_state))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_hhcq_prime_rational_expand(
        prime_p, prime_q,
        phase_state->x, phase_state->y,
        base_resolution_index,
        &expansion);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    x_squared = (uint16_t)((uint16_t)phase_state->x * (uint16_t)phase_state->x);
    parity = (uint8_t)(x_squared & 1U);

    memset(out_gate, 0, sizeof(*out_gate));
    out_gate->struct_size = (uint32_t)sizeof(*out_gate);
    out_gate->version = HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION;
    out_gate->prime_p = prime_p;
    out_gate->prime_q = prime_q;
    out_gate->x_phase72 = phase_state->x;
    out_gate->y_phase72 = phase_state->y;
    out_gate->x_squared_mod72 = (uint8_t)(x_squared % HHS_EXACT_PASS219_CORE_CIRCUIT_PHASE_MODULUS);
    out_gate->x_squared_parity = parity;
    out_gate->orientation = parity == 0U
        ? HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_DIRECT
        : HHS_EXACT_PASS219_HHCQ_PARITY_ORIENTATION_REVERSED;
    out_gate->orientation_sign = parity == 0U ? INT8_C(1) : INT8_C(-1);
    out_gate->ordered_xy_phase = phase_state->xy;
    out_gate->ordered_yx_phase = phase_state->yx;
    out_gate->ordered_zw_phase = phase_state->zw;
    out_gate->ordered_wz_phase = phase_state->wz;
    out_gate->matrix_order_exact = 1U;
    out_gate->symbolic_exponent_retained = expansion.symbolic_sqrt_a_times_b_retained;
    out_gate->ordinary_negative_base_exponent_evaluated = 0U;
    out_gate->x2_parity_identity_exact =
        parity == (uint8_t)(phase_state->x & 1U) ? 1U : 0U;
    out_gate->candidate_only = 1U;
    out_gate->exact_integer_only = 1U;
    out_gate->expansion = expansion;

    signature = UINT64_C(0x2198ba511310002) ^
        hhs_p219_p11_state_signature(phase_state) ^
        expansion.expansion_signature64 ^
        ((uint64_t)x_squared << 32U) ^
        ((uint64_t)out_gate->orientation << 16U) ^
        (uint64_t)(uint8_t)out_gate->orientation_sign;
    out_gate->parity_signature64 = hhs_p219_p11_mix64(signature);

    if (out_gate->symbolic_exponent_retained != 1U ||
        out_gate->x2_parity_identity_exact != 1U ||
        out_gate->matrix_order_exact != 1U ||
        out_gate->expansion.candidate_only != 1U ||
        out_gate->expansion.canonical_authority_changed != 0U ||
        out_gate->expansion.floating_point_authority != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
    uint16_t prime_p,
    uint16_t prime_q,
    const HHSExactPass219OctonionStateV1 *phase_state,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQ8BasisManifoldV1 *out_manifold
) {
    HHSExactStatus status;
    HHSExactPass219HHCQ8BasisEquilibriumV1 equilibrium;
    HHSExactPass219HHCQParityGateV1 gate;
    int matrix_order;
    int product_closure;

    if (phase_state == NULL || out_manifold == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_octonion_validate_state(phase_state);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    matrix_order = hhs_p219_p11_order_contract(phase_state);
    if (!matrix_order)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_hhcq_8basis_equilibrium_validate(
        prime_p, prime_q, phase_state,
        macro_p_numerator, macro_p_denominator,
        &equilibrium);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hhcq_parity_gate(
        prime_p, prime_q, phase_state, base_resolution_index, &gate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    product_closure = gate.expansion.product_ab_equals_p4 == 1U &&
        gate.expansion.sqrt_ab_equals_p2 == 1U &&
        gate.expansion.reciprocal_product_equals_one == 1U &&
        gate.expansion.polynomial_fraction_reduced == 1U &&
        gate.expansion.symbolic_sqrt_a_times_b_retained == 1U;

    memset(out_manifold, 0, sizeof(*out_manifold));
    out_manifold->struct_size = (uint32_t)sizeof(*out_manifold);
    out_manifold->version = HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_VERSION;
    out_manifold->equilibrium = equilibrium;
    out_manifold->parity_gate = gate;
    out_manifold->octonion_state_valid = 1U;
    out_manifold->full_octonion_surface_validated = 0U;
    out_manifold->phase10_product_closure_valid = product_closure ? 1U : 0U;
    out_manifold->matrix_order_exact = matrix_order ? 1U : 0U;
    out_manifold->equilibrium_exact = equilibrium.equilibrium_exact;
    out_manifold->parity_orientation_exact =
        gate.x2_parity_identity_exact == 1U &&
        gate.ordinary_negative_base_exponent_evaluated == 0U ? 1U : 0U;
    out_manifold->constraint_intersection_satisfied =
        out_manifold->octonion_state_valid == 1U &&
        out_manifold->phase10_product_closure_valid == 1U &&
        out_manifold->matrix_order_exact == 1U &&
        out_manifold->equilibrium_exact == 1U &&
        out_manifold->parity_orientation_exact == 1U ? 1U : 0U;
    out_manifold->candidate_only = 1U;
    out_manifold->exact_integer_only = 1U;
    out_manifold->manifold_signature64 = hhs_p219_p11_manifold_signature(out_manifold);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_8basis_from_vm81(
    const HHSExactVM81Frame *frame,
    uint8_t x_cell,
    uint8_t y_cell,
    uint8_t z_cell,
    uint8_t w_cell,
    uint16_t prime_p,
    uint16_t prime_q,
    uint64_t macro_p_numerator,
    uint64_t macro_p_denominator,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQ8BasisManifoldV1 *out_manifold
) {
    HHSExactStatus status;
    HHSExactPass219OctonionSurfaceV1 surface;
    if (frame == NULL || out_manifold == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_octonion_from_vm81(
        frame, x_cell, y_cell, z_cell, w_cell, &surface);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_octonion_validate_surface(&surface);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hhcq_8basis_manifold_evaluate(
        prime_p, prime_q, &surface.state,
        macro_p_numerator, macro_p_denominator,
        base_resolution_index, out_manifold);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_manifold->full_octonion_surface_validated = 1U;
    out_manifold->manifold_signature64 = hhs_p219_p11_manifold_signature(out_manifold);
    return HHS_EXACT_STATUS_OK;
}

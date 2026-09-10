#include "../include/hhs_pass219_hhcq_symbolic_phase_gear_1_32.h"

#include <string.h>

static uint64_t p12_mix(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static int p12_prime(uint32_t n) {
    uint32_t d;
    if (n < 2U || n > HHS_EXACT_PASS219_HHCQ_PRIME_RATIONAL_MAX_PRIME) return 0;
    if (n == 2U) return 1;
    if ((n & 1U) == 0U) return 0;
    for (d = 3U; d <= n / d; d += 2U)
        if (n % d == 0U) return 0;
    return 1;
}

static int p12_orientation(uint8_t v) {
    return v == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT ||
           v == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED;
}

static uint8_t p12_inverse(uint8_t s) {
    switch (s) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:  return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
        default: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_INVALID;
    }
}

static uint8_t p12_negate(uint8_t s) {
    switch (s) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:  return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
        default: return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_INVALID;
    }
}

static uint8_t p12_square(uint8_t s) {
    switch (s) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2:
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
        default:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_INVALID;
    }
}

static HHSExactStatus p12_residue(uint8_t s, uint8_t *out) {
    uint32_t q;
    if (out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS == 0U ||
        HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS % 4U != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    q = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS / 4U;
    switch (s) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:  *out = (uint8_t)q; return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2: *out = (uint8_t)(2U * q); return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3: *out = (uint8_t)(3U * q); return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4: *out = 0U; return HHS_EXACT_STATUS_OK;
        default: return HHS_EXACT_STATUS_RANGE_ERROR;
    }
}

static uint64_t p12_carrier_sig(const HHSExactPass219HHCQSymbolicCarrierV1 *c) {
    uint64_t v = UINT64_C(0x2195132000000000);
    v ^= (uint64_t)c->x_symbol;
    v ^= (uint64_t)c->y_symbol << 4U;
    v ^= (uint64_t)c->z_symbol << 8U;
    v ^= (uint64_t)c->w_symbol << 12U;
    v ^= (uint64_t)c->xy_symbol << 16U;
    v ^= (uint64_t)c->yx_symbol << 20U;
    v ^= (uint64_t)c->zw_symbol << 24U;
    v ^= (uint64_t)c->wz_symbol << 28U;
    v ^= (uint64_t)c->xy_ring_orientation << 32U;
    v ^= (uint64_t)c->zw_ring_orientation << 40U;
    return p12_mix(v);
}

static HHSExactStatus p12_fill_carrier(
    uint8_t xy_orientation,
    uint8_t zw_orientation,
    HHSExactPass219HHCQSymbolicCarrierV1 *c
) {
    uint8_t symbols[HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT];
    uint32_t i;
    if (c == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!p12_orientation(xy_orientation) || !p12_orientation(zw_orientation))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(c, 0, sizeof(*c));
    c->struct_size = (uint32_t)sizeof(*c);
    c->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    c->xy_ring_orientation = xy_orientation;
    c->zw_ring_orientation = zw_orientation;
    c->x_symbol = xy_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT
        ? HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I : HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
    c->y_symbol = p12_negate(c->x_symbol);
    c->z_symbol = zw_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT
        ? HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I : HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
    c->w_symbol = p12_negate(c->z_symbol);
    c->xy_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
    c->yx_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
    c->zw_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
    c->wz_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
    c->x_inverse_y = p12_inverse(c->y_symbol) == c->x_symbol;
    c->y_opposes_x = p12_negate(c->x_symbol) == c->y_symbol;
    c->z_inverse_w = p12_inverse(c->w_symbol) == c->z_symbol;
    c->w_opposes_z = p12_negate(c->z_symbol) == c->w_symbol;
    c->xy_is_i4 = 1U;
    c->yx_is_i2 = 1U;
    c->zw_is_i4 = 1U;
    c->wz_is_i2 = 1U;
    c->ordered_noncommutative_products = 1U;
    c->global_relation_graph_exact =
        c->x_inverse_y && c->y_opposes_x && c->z_inverse_w && c->w_opposes_z;
    symbols[HHS_EXACT_PHASE_X] = c->x_symbol;
    symbols[HHS_EXACT_PHASE_Y] = c->y_symbol;
    symbols[HHS_EXACT_PHASE_Z] = c->z_symbol;
    symbols[HHS_EXACT_PHASE_W] = c->w_symbol;
    symbols[HHS_EXACT_PHASE_XY] = c->xy_symbol;
    symbols[HHS_EXACT_PHASE_YX] = c->yx_symbol;
    symbols[HHS_EXACT_PHASE_ZW] = c->zw_symbol;
    symbols[HHS_EXACT_PHASE_WZ] = c->wz_symbol;
    for (i = 0U; i < HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT; ++i) {
        HHSExactStatus status = p12_residue(symbols[i], &c->projection_residue72[i]);
        if (status != HHS_EXACT_STATUS_OK) return status;
    }
    c->projection_residue_authority = 0U;
    c->candidate_only = 1U;
    c->exact_integer_storage_only = 1U;
    c->canonical_authority_changed = 0U;
    c->floating_point_authority = 0U;
    c->carrier_signature64 = p12_carrier_sig(c);
    return HHS_EXACT_STATUS_OK;
}

static int p12_projection_matches(
    const HHSExactPass219OctonionStateV1 *p,
    const HHSExactPass219HHCQSymbolicCarrierV1 *c
) {
    return p->x  == c->projection_residue72[HHS_EXACT_PHASE_X] &&
           p->y  == c->projection_residue72[HHS_EXACT_PHASE_Y] &&
           p->z  == c->projection_residue72[HHS_EXACT_PHASE_Z] &&
           p->w  == c->projection_residue72[HHS_EXACT_PHASE_W] &&
           p->xy == c->projection_residue72[HHS_EXACT_PHASE_XY] &&
           p->yx == c->projection_residue72[HHS_EXACT_PHASE_YX] &&
           p->zw == c->projection_residue72[HHS_EXACT_PHASE_ZW] &&
           p->wz == c->projection_residue72[HHS_EXACT_PHASE_WZ];
}

static uint64_t p12_manifold_sig(const HHSExactPass219HHCQSymbolicManifoldV1 *m) {
    return p12_mix(UINT64_C(0x21951320f00d0001) ^
                   m->admission.admission_signature64 ^
                   m->equilibrium.equilibrium_signature64 ^
                   m->gate.gate_signature64 ^
                   ((uint64_t)m->symbolic_carrier_admitted << 1U) ^
                   ((uint64_t)m->constraint_intersection_satisfied << 2U));
}

uint32_t hhs_exact_pass219_hhcq_symbolic_phase_version(void) {
    return HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_phase_descriptor(
    HHSExactPass219HHCQSymbolicPhaseDescriptorV1 *out
) {
    HHSExactPass219HHCQ8BasisParityDescriptorV1 inherited;
    HHSExactStatus status;
    if (out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&inherited, 0, sizeof(inherited));
    status = hhs_exact_pass219_hhcq_8basis_parity_descriptor(&inherited);
    if (status != HHS_EXACT_STATUS_OK) return status;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out->phase_modulus = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    out->parameter_count = HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT;
    out->basis_count = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT;
    out->inherited_policy_state_bytes = inherited.inherited_policy_state_bytes;
    out->phase11_source_bytes = inherited.source_bytes;
    memcpy(out->phase11_source_sha256, inherited.source_sha256, sizeof(out->phase11_source_sha256));
    out->symbolic_phase_symbols = 1U;
    out->global_constraint_graph_required = 1U;
    out->reciprocal_opposition_relations_required = 1U;
    out->ordered_noncommutative_products_required = 1U;
    out->symbolic_phi8_equilibrium = 1U;
    out->symbolic_x_squared_gate = 1U;
    out->phase11_scalar_equilibrium_superseded = 1U;
    out->phase11_scalar_parity_superseded = 1U;
    out->raw_phase_residue_authority = 0U;
    out->scalar_phase_sum_authority = 0U;
    out->scalar_x_parity_authority = 0U;
    out->phase10_projection_witness_only = 1U;
    out->candidate_only = 1U;
    out->exact_integer_storage_only = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_carrier_construct(
    uint8_t xy_ring_orientation,
    uint8_t zw_ring_orientation,
    HHSExactPass219HHCQSymbolicCarrierV1 *out
) {
    return p12_fill_carrier(xy_ring_orientation, zw_ring_orientation, out);
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_carrier_validate(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier
) {
    HHSExactPass219HHCQSymbolicCarrierV1 expected;
    HHSExactStatus status;
    if (carrier == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (carrier->struct_size < sizeof(*carrier) ||
        carrier->version != HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    status = p12_fill_carrier(carrier->xy_ring_orientation, carrier->zw_ring_orientation, &expected);
    if (status != HHS_EXACT_STATUS_OK) return status;
    return memcmp(carrier, &expected, sizeof(expected)) == 0
        ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_admit_projection(
    const HHSExactPass219OctonionStateV1 *raw,
    HHSExactPass219HHCQSymbolicAdmissionV1 *out
) {
    static const uint8_t orientation[2] = {
        HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT,
        HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED
    };
    uint32_t i, j;
    HHSExactStatus status;
    if (raw == NULL || out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out->candidate_only = 1U;
    status = hhs_exact_pass219_octonion_validate_state(raw);
    if (status != HHS_EXACT_STATUS_OK) return status;
    out->raw_projection_valid = 1U;
    for (i = 0U; i < 2U; ++i) {
        for (j = 0U; j < 2U; ++j) {
            HHSExactPass219HHCQSymbolicCarrierV1 c;
            status = p12_fill_carrier(orientation[i], orientation[j], &c);
            if (status != HHS_EXACT_STATUS_OK) return status;
            if (p12_projection_matches(raw, &c)) {
                out->carrier = c;
                out->raw_projection_matches_symbolic_carrier = 1U;
                out->symbolic_carrier_admitted = 1U;
                out->admission_signature64 = p12_mix(c.carrier_signature64 ^ UINT64_C(0x21951320ad001001));
                return HHS_EXACT_STATUS_OK;
            }
        }
    }
    out->raw_projection_authority = 0U;
    out->scalar_zero_reinterpreted_as_symbolic_zero = 0U;
    out->admission_signature64 = p12_mix(UINT64_C(0x21951320ad00dead) ^
        ((uint64_t)raw->x << 8U) ^ ((uint64_t)raw->y << 16U) ^
        ((uint64_t)raw->z << 24U) ^ ((uint64_t)raw->w << 32U));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_equilibrium(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    HHSExactPass219HHCQSymbolicEquilibriumV1 *out
) {
    HHSExactStatus status;
    if (carrier == NULL || out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(carrier);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (!p12_prime(prime_p) || !p12_prime(prime_q) || prime_p == prime_q)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out->carrier = *carrier;
    out->prime_p = prime_p;
    out->prime_q = prime_q;
    out->phi8_symbolic = 1U;
    out->macro_p_symbolic = 1U;
    out->equilibrium_relation_present = 1U;
    out->equilibrium_relation_well_typed = carrier->global_relation_graph_exact;
    out->scalar_phase_sum_evaluated = 0U;
    out->scalar_macro_p_constructed = 0U;
    out->prime_seed_pair_valid = 1U;
    out->candidate_only = 1U;
    out->equilibrium_signature64 = p12_mix(carrier->carrier_signature64 ^
        ((uint64_t)prime_p << 16U) ^ ((uint64_t)prime_q << 32U) ^ UINT64_C(0x21951320e0010001));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_gate(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicGateV1 *out
) {
    HHSExactStatus status;
    if (carrier == NULL || out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(carrier);
    if (status != HHS_EXACT_STATUS_OK) return status;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out->carrier = *carrier;
    status = hhs_exact_pass219_hhcq_prime_rational_expand(
        prime_p, prime_q,
        carrier->projection_residue72[HHS_EXACT_PHASE_X],
        carrier->projection_residue72[HHS_EXACT_PHASE_Y],
        base_resolution_index,
        &out->phase10_projection);
    if (status != HHS_EXACT_STATUS_OK) return status;
    out->x_squared_symbol = p12_square(carrier->x_symbol);
    out->negative_xy_symbol = p12_negate(carrier->xy_symbol);
    out->carrier_orientation = carrier->xy_ring_orientation;
    out->symbolic_exponent_retained = 1U;
    out->symbolic_square_relation_exact = out->x_squared_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
    out->typed_gate_well_formed = out->symbolic_square_relation_exact &&
        out->negative_xy_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
    out->scalar_x_parity_evaluated = 0U;
    out->ordinary_power_evaluated = 0U;
    out->phase10_projection_executed = 1U;
    out->phase10_projection_authority = 0U;
    out->resolution_noncoarsening = out->phase10_projection.noncoarsening;
    out->candidate_only = 1U;
    out->gate_signature64 = p12_mix(carrier->carrier_signature64 ^
        out->phase10_projection.expansion_signature64 ^
        ((uint64_t)out->x_squared_symbol << 8U) ^
        ((uint64_t)out->negative_xy_symbol << 16U) ^ UINT64_C(0x21951320a7e00001));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus p12_manifold_carrier(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out
) {
    HHSExactStatus status;
    if (carrier == NULL || out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(carrier);
    if (status != HHS_EXACT_STATUS_OK) return status;
    memset(out, 0, sizeof(*out));
    out->struct_size = (uint32_t)sizeof(*out);
    out->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out->admission.struct_size = (uint32_t)sizeof(out->admission);
    out->admission.version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out->admission.carrier = *carrier;
    out->admission.symbolic_carrier_admitted = 1U;
    out->admission.candidate_only = 1U;
    out->admission.admission_signature64 = p12_mix(carrier->carrier_signature64 ^ UINT64_C(0x21951320ad001111));
    status = hhs_exact_pass219_hhcq_symbolic_equilibrium(carrier, prime_p, prime_q, &out->equilibrium);
    if (status != HHS_EXACT_STATUS_OK) return status;
    status = hhs_exact_pass219_hhcq_symbolic_gate(carrier, prime_p, prime_q, base_resolution_index, &out->gate);
    if (status != HHS_EXACT_STATUS_OK) return status;
    out->symbolic_carrier_admitted = 1U;
    out->global_relation_graph_exact = carrier->global_relation_graph_exact;
    out->symbolic_equilibrium_exact = out->equilibrium.equilibrium_relation_well_typed;
    out->symbolic_square_gate_exact = out->gate.typed_gate_well_formed;
    out->ordered_products_exact = carrier->ordered_noncommutative_products;
    out->constraint_intersection_satisfied = out->global_relation_graph_exact &&
        out->symbolic_equilibrium_exact && out->symbolic_square_gate_exact &&
        out->ordered_products_exact && out->gate.resolution_noncoarsening;
    out->raw_projection_authority = 0U;
    out->scalar_integer_semantic_authority = 0U;
    out->candidate_only = 1U;
    out->manifold_signature64 = p12_manifold_sig(out);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out
) {
    return p12_manifold_carrier(carrier, prime_p, prime_q, base_resolution_index, out);
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
    const HHSExactPass219OctonionStateV1 *raw,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out
) {
    HHSExactPass219HHCQSymbolicAdmissionV1 admission;
    HHSExactPass219HHCQSymbolicManifoldV1 admitted;
    HHSExactStatus status;
    if (raw == NULL || out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&admission, 0, sizeof(admission));
    status = hhs_exact_pass219_hhcq_symbolic_admit_projection(raw, &admission);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (!admission.symbolic_carrier_admitted) {
        memset(out, 0, sizeof(*out));
        out->struct_size = (uint32_t)sizeof(*out);
        out->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
        out->admission = admission;
        out->candidate_only = 1U;
        out->raw_projection_authority = 0U;
        out->scalar_integer_semantic_authority = 0U;
        out->manifold_signature64 = p12_manifold_sig(out);
        return HHS_EXACT_STATUS_OK;
    }
    status = p12_manifold_carrier(&admission.carrier, prime_p, prime_q, base_resolution_index, &admitted);
    if (status != HHS_EXACT_STATUS_OK) return status;
    admitted.admission = admission;
    admitted.manifold_signature64 = p12_manifold_sig(&admitted);
    *out = admitted;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_vm81(
    const HHSExactVM81Frame *frame,
    uint8_t x_cell,
    uint8_t y_cell,
    uint8_t z_cell,
    uint8_t w_cell,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out
) {
    HHSExactPass219OctonionSurfaceV1 surface;
    HHSExactStatus status;
    if (frame == NULL || out == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&surface, 0, sizeof(surface));
    status = hhs_exact_pass219_octonion_from_vm81(frame, x_cell, y_cell, z_cell, w_cell, &surface);
    if (status != HHS_EXACT_STATUS_OK) return status;
    return hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
        &surface.state, prime_p, prime_q, base_resolution_index, out);
}

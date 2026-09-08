#include "../include/hhs_pass219_hhcq_symbolic_phase_gear_1_32.h"

#include <string.h>

static uint64_t hhs_p219_p12_mix64(uint64_t x) {
    x ^= x >> 30U;
    x *= UINT64_C(0xbf58476d1ce4e5b9);
    x ^= x >> 27U;
    x *= UINT64_C(0x94d049bb133111eb);
    x ^= x >> 31U;
    return x;
}

static int hhs_p219_p12_is_prime(uint32_t n) {
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

static int hhs_p219_p12_orientation_valid(uint8_t orientation) {
    return orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT ||
           orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED;
}

static uint8_t hhs_p219_p12_symbol_inverse(uint8_t symbol) {
    switch (symbol) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
        default:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_INVALID;
    }
}

static uint8_t hhs_p219_p12_symbol_negate(uint8_t symbol) {
    switch (symbol) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
        default:
            return HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_INVALID;
    }
}

static uint8_t hhs_p219_p12_symbol_square(uint8_t symbol) {
    switch (symbol) {
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

static HHSExactStatus hhs_p219_p12_symbol_residue72(
    uint8_t symbol,
    uint8_t *out_residue
) {
    uint32_t quarter;
    if (out_residue == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS == 0U ||
        HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS % 4U != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    quarter = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS / 4U;
    switch (symbol) {
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I:
            *out_residue = (uint8_t)quarter;
            return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2:
            *out_residue = (uint8_t)(quarter * 2U);
            return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3:
            *out_residue = (uint8_t)(quarter * 3U);
            return HHS_EXACT_STATUS_OK;
        case HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4:
            *out_residue = 0U;
            return HHS_EXACT_STATUS_OK;
        default:
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }
}

static uint64_t hhs_p219_p12_carrier_signature(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier
) {
    uint64_t packed = UINT64_C(0x2195132000000000);
    packed ^= (uint64_t)carrier->x_symbol;
    packed ^= (uint64_t)carrier->y_symbol << 4U;
    packed ^= (uint64_t)carrier->z_symbol << 8U;
    packed ^= (uint64_t)carrier->w_symbol << 12U;
    packed ^= (uint64_t)carrier->xy_symbol << 16U;
    packed ^= (uint64_t)carrier->yx_symbol << 20U;
    packed ^= (uint64_t)carrier->zw_symbol << 24U;
    packed ^= (uint64_t)carrier->wz_symbol << 28U;
    packed ^= (uint64_t)carrier->xy_ring_orientation << 32U;
    packed ^= (uint64_t)carrier->zw_ring_orientation << 40U;
    return hhs_p219_p12_mix64(packed);
}

static int hhs_p219_p12_projection_matches(
    const HHSExactPass219OctonionStateV1 *projection,
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier
) {
    return projection->x == carrier->projection_residue72[HHS_EXACT_PHASE_X] &&
           projection->y == carrier->projection_residue72[HHS_EXACT_PHASE_Y] &&
           projection->z == carrier->projection_residue72[HHS_EXACT_PHASE_Z] &&
           projection->w == carrier->projection_residue72[HHS_EXACT_PHASE_W] &&
           projection->xy == carrier->projection_residue72[HHS_EXACT_PHASE_XY] &&
           projection->yx == carrier->projection_residue72[HHS_EXACT_PHASE_YX] &&
           projection->zw == carrier->projection_residue72[HHS_EXACT_PHASE_ZW] &&
           projection->wz == carrier->projection_residue72[HHS_EXACT_PHASE_WZ];
}

static uint64_t hhs_p219_p12_manifold_signature(
    const HHSExactPass219HHCQSymbolicManifoldV1 *manifold
) {
    uint64_t x = UINT64_C(0x21951320f00d0001);
    x ^= manifold->admission.admission_signature64;
    x ^= manifold->equilibrium.equilibrium_signature64;
    x ^= manifold->gate.gate_signature64;
    x ^= (uint64_t)manifold->constraint_intersection_satisfied << 1U;
    x ^= (uint64_t)manifold->symbolic_carrier_admitted << 2U;
    return hhs_p219_p12_mix64(x);
}

uint32_t hhs_exact_pass219_hhcq_symbolic_phase_version(void) {
    return HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_phase_descriptor(
    HHSExactPass219HHCQSymbolicPhaseDescriptorV1 *out_descriptor
) {
    HHSExactPass219HHCQ8BasisParityDescriptorV1 inherited;
    HHSExactStatus status;
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&inherited, 0, sizeof(inherited));
    status = hhs_exact_pass219_hhcq_8basis_parity_descriptor(&inherited);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_descriptor->phase_modulus = HHS_EXACT_PASS219_HHCQ_PHASE_MODULUS;
    out_descriptor->parameter_count = HHS_EXACT_PASS219_HHCQ_PARAMETER_COUNT;
    out_descriptor->basis_count = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT;
    out_descriptor->inherited_policy_state_bytes = inherited.inherited_policy_state_bytes;
    out_descriptor->phase11_source_bytes = inherited.source_bytes;
    memcpy(out_descriptor->phase11_source_sha256, inherited.source_sha256,
           sizeof(out_descriptor->phase11_source_sha256));
    out_descriptor->symbolic_phase_symbols = 1U;
    out_descriptor->global_constraint_graph_required = 1U;
    out_descriptor->reciprocal_opposition_relations_required = 1U;
    out_descriptor->ordered_noncommutative_products_required = 1U;
    out_descriptor->symbolic_phi8_equilibrium = 1U;
    out_descriptor->symbolic_x_squared_gate = 1U;
    out_descriptor->phase11_scalar_equilibrium_superseded = 1U;
    out_descriptor->phase11_scalar_parity_superseded = 1U;
    out_descriptor->raw_phase_residue_authority = 0U;
    out_descriptor->scalar_phase_sum_authority = 0U;
    out_descriptor->scalar_x_parity_authority = 0U;
    out_descriptor->phase10_projection_witness_only = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->exact_integer_storage_only = 1U;
    out_descriptor->canonical_mutation_authority = 0U;
    out_descriptor->canonical_hash72_authority = 0U;
    out_descriptor->canonical_hash216_authority = 0U;
    out_descriptor->canonical_persistence_authority = 0U;
    out_descriptor->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_carrier_construct(
    uint8_t xy_ring_orientation,
    uint8_t zw_ring_orientation,
    HHSExactPass219HHCQSymbolicCarrierV1 *out_carrier
) {
    uint8_t symbols[HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT];
    uint32_t i;
    if (out_carrier == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_p219_p12_orientation_valid(xy_ring_orientation) ||
        !hhs_p219_p12_orientation_valid(zw_ring_orientation))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_carrier, 0, sizeof(*out_carrier));
    out_carrier->struct_size = (uint32_t)sizeof(*out_carrier);
    out_carrier->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_carrier->xy_ring_orientation = xy_ring_orientation;
    out_carrier->zw_ring_orientation = zw_ring_orientation;

    out_carrier->x_symbol =
        xy_ring_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT
            ? HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I
            : HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
    out_carrier->y_symbol = hhs_p219_p12_symbol_negate(out_carrier->x_symbol);
    out_carrier->z_symbol =
        zw_ring_orientation == HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT
            ? HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I
            : HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3;
    out_carrier->w_symbol = hhs_p219_p12_symbol_negate(out_carrier->z_symbol);
    out_carrier->xy_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
    out_carrier->yx_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;
    out_carrier->zw_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4;
    out_carrier->wz_symbol = HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2;

    out_carrier->x_inverse_y =
        hhs_p219_p12_symbol_inverse(out_carrier->y_symbol) == out_carrier->x_symbol ? 1U : 0U;
    out_carrier->y_opposes_x =
        hhs_p219_p12_symbol_negate(out_carrier->x_symbol) == out_carrier->y_symbol ? 1U : 0U;
    out_carrier->z_inverse_w =
        hhs_p219_p12_symbol_inverse(out_carrier->w_symbol) == out_carrier->z_symbol ? 1U : 0U;
    out_carrier->w_opposes_z =
        hhs_p219_p12_symbol_negate(out_carrier->z_symbol) == out_carrier->w_symbol ? 1U : 0U;
    out_carrier->xy_is_i4 = 1U;
    out_carrier->yx_is_i2 = 1U;
    out_carrier->zw_is_i4 = 1U;
    out_carrier->wz_is_i2 = 1U;
    out_carrier->ordered_noncommutative_products = 1U;
    out_carrier->global_relation_graph_exact =
        out_carrier->x_inverse_y && out_carrier->y_opposes_x &&
        out_carrier->z_inverse_w && out_carrier->w_opposes_z ? 1U : 0U;

    symbols[HHS_EXACT_PHASE_X] = out_carrier->x_symbol;
    symbols[HHS_EXACT_PHASE_Y] = out_carrier->y_symbol;
    symbols[HHS_EXACT_PHASE_Z] = out_carrier->z_symbol;
    symbols[HHS_EXACT_PHASE_W] = out_carrier->w_symbol;
    symbols[HHS_EXACT_PHASE_XY] = out_carrier->xy_symbol;
    symbols[HHS_EXACT_PHASE_YX] = out_carrier->yx_symbol;
    symbols[HHS_EXACT_PHASE_ZW] = out_carrier->zw_symbol;
    symbols[HHS_EXACT_PHASE_WZ] = out_carrier->wz_symbol;
    for (i = 0U; i < HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT; ++i) {
        HHSExactStatus status = hhs_p219_p12_symbol_residue72(
            symbols[i], &out_carrier->projection_residue72[i]);
        if (status != HHS_EXACT_STATUS_OK) {
            memset(out_carrier, 0, sizeof(*out_carrier));
            return status;
        }
    }

    out_carrier->projection_residue_authority = 0U;
    out_carrier->candidate_only = 1U;
    out_carrier->exact_integer_storage_only = 1U;
    out_carrier->canonical_authority_changed = 0U;
    out_carrier->floating_point_authority = 0U;
    out_carrier->carrier_signature64 = hhs_p219_p12_carrier_signature(out_carrier);
    return hhs_exact_pass219_hhcq_symbolic_carrier_validate(out_carrier);
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_carrier_validate(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier
) {
    HHSExactPass219HHCQSymbolicCarrierV1 expected;
    if (carrier == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (carrier->struct_size < sizeof(*carrier) ||
        carrier->version != HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION)
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (!hhs_p219_p12_orientation_valid(carrier->xy_ring_orientation) ||
        !hhs_p219_p12_orientation_valid(carrier->zw_ring_orientation))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(&expected, 0, sizeof(expected));
    if (hhs_exact_pass219_hhcq_symbolic_carrier_construct(
            carrier->xy_ring_orientation, carrier->zw_ring_orientation,
            &expected) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (memcmp(carrier, &expected, sizeof(expected)) != 0)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_admit_projection(
    const HHSExactPass219OctonionStateV1 *raw_projection,
    HHSExactPass219HHCQSymbolicAdmissionV1 *out_admission
) {
    static const uint8_t orientations[2] = {
        HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT,
        HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED
    };
    uint32_t i;
    uint32_t j;
    HHSExactStatus status;
    if (raw_projection == NULL || out_admission == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_admission, 0, sizeof(*out_admission));
    out_admission->struct_size = (uint32_t)sizeof(*out_admission);
    out_admission->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_admission->raw_projection_authority = 0U;
    out_admission->scalar_zero_reinterpreted_as_symbolic_zero = 0U;
    out_admission->candidate_only = 1U;
    out_admission->canonical_authority_changed = 0U;
    out_admission->floating_point_authority = 0U;

    status = hhs_exact_pass219_octonion_validate_state(raw_projection);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    out_admission->raw_projection_valid = 1U;

    for (i = 0U; i < 2U; ++i) {
        for (j = 0U; j < 2U; ++j) {
            HHSExactPass219HHCQSymbolicCarrierV1 carrier;
            memset(&carrier, 0, sizeof(carrier));
            status = hhs_exact_pass219_hhcq_symbolic_carrier_construct(
                orientations[i], orientations[j], &carrier);
            if (status != HHS_EXACT_STATUS_OK)
                return status;
            if (hhs_p219_p12_projection_matches(raw_projection, &carrier)) {
                out_admission->carrier = carrier;
                out_admission->raw_projection_matches_symbolic_carrier = 1U;
                out_admission->symbolic_carrier_admitted = 1U;
                out_admission->admission_signature64 = hhs_p219_p12_mix64(
                    carrier.carrier_signature64 ^ UINT64_C(0x21951320ad001001));
                return HHS_EXACT_STATUS_OK;
            }
        }
    }

    out_admission->admission_signature64 = hhs_p219_p12_mix64(
        UINT64_C(0x21951320ad00dead) ^
        ((uint64_t)raw_projection->x << 8U) ^
        ((uint64_t)raw_projection->y << 16U) ^
        ((uint64_t)raw_projection->z << 24U) ^
        ((uint64_t)raw_projection->w << 32U));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_equilibrium(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    HHSExactPass219HHCQSymbolicEquilibriumV1 *out_equilibrium
) {
    HHSExactStatus status;
    if (carrier == NULL || out_equilibrium == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(carrier);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (!hhs_p219_p12_is_prime(prime_p) || !hhs_p219_p12_is_prime(prime_q) ||
        prime_p == prime_q)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_equilibrium, 0, sizeof(*out_equilibrium));
    out_equilibrium->struct_size = (uint32_t)sizeof(*out_equilibrium);
    out_equilibrium->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_equilibrium->carrier = *carrier;
    out_equilibrium->prime_p = prime_p;
    out_equilibrium->prime_q = prime_q;
    out_equilibrium->phi8_symbolic = 1U;
    out_equilibrium->macro_p_symbolic = 1U;
    out_equilibrium->equilibrium_relation_present = 1U;
    out_equilibrium->equilibrium_relation_well_typed = carrier->global_relation_graph_exact;
    out_equilibrium->scalar_phase_sum_evaluated = 0U;
    out_equilibrium->scalar_macro_p_constructed = 0U;
    out_equilibrium->prime_seed_pair_valid = 1U;
    out_equilibrium->candidate_only = 1U;
    out_equilibrium->canonical_authority_changed = 0U;
    out_equilibrium->floating_point_authority = 0U;
    out_equilibrium->equilibrium_signature64 = hhs_p219_p12_mix64(
        carrier->carrier_signature64 ^ ((uint64_t)prime_p << 16U) ^
        ((uint64_t)prime_q << 32U) ^ UINT64_C(0x21951320e0010001));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_gate(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicGateV1 *out_gate
) {
    HHSExactStatus status;
    if (carrier == NULL || out_gate == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(carrier);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_gate, 0, sizeof(*out_gate));
    out_gate->struct_size = (uint32_t)sizeof(*out_gate);
    out_gate->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_gate->carrier = *carrier;
    status = hhs_exact_pass219_hhcq_prime_rational_expand(
        prime_p, prime_q,
        carrier->projection_residue72[HHS_EXACT_PHASE_X],
        carrier->projection_residue72[HHS_EXACT_PHASE_Y],
        base_resolution_index,
        &out_gate->phase10_projection);
    if (status != HHS_EXACT_STATUS_OK) {
        memset(out_gate, 0, sizeof(*out_gate));
        return status;
    }

    out_gate->x_squared_symbol = hhs_p219_p12_symbol_square(carrier->x_symbol);
    out_gate->negative_xy_symbol = hhs_p219_p12_symbol_negate(carrier->xy_symbol);
    out_gate->carrier_orientation = carrier->xy_ring_orientation;
    out_gate->symbolic_exponent_retained = 1U;
    out_gate->symbolic_square_relation_exact =
        out_gate->x_squared_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 ? 1U : 0U;
    out_gate->typed_gate_well_formed =
        out_gate->symbolic_square_relation_exact &&
        out_gate->negative_xy_symbol == HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 ? 1U : 0U;
    out_gate->scalar_x_parity_evaluated = 0U;
    out_gate->ordinary_power_evaluated = 0U;
    out_gate->phase10_projection_executed = 1U;
    out_gate->phase10_projection_authority = 0U;
    out_gate->resolution_noncoarsening = out_gate->phase10_projection.noncoarsening;
    out_gate->candidate_only = 1U;
    out_gate->canonical_authority_changed = 0U;
    out_gate->floating_point_authority = 0U;
    out_gate->gate_signature64 = hhs_p219_p12_mix64(
        carrier->carrier_signature64 ^ out_gate->phase10_projection.expansion_signature64 ^
        ((uint64_t)out_gate->x_squared_symbol << 8U) ^
        ((uint64_t)out_gate->negative_xy_symbol << 16U) ^
        UINT64_C(0x21951320a7e00001));
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus hhs_p219_p12_manifold_from_admitted_carrier(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold
) {
    HHSExactStatus status;
    if (carrier == NULL || out_manifold == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_manifold, 0, sizeof(*out_manifold));
    out_manifold->struct_size = (uint32_t)sizeof(*out_manifold);
    out_manifold->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_manifold->admission.struct_size = (uint32_t)sizeof(out_manifold->admission);
    out_manifold->admission.version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
    out_manifold->admission.carrier = *carrier;
    out_manifold->admission.symbolic_carrier_admitted = 1U;
    out_manifold->admission.raw_projection_authority = 0U;
    out_manifold->admission.candidate_only = 1U;
    out_manifold->admission.admission_signature64 = hhs_p219_p12_mix64(
        carrier->carrier_signature64 ^ UINT64_C(0x21951320ad001111));

    status = hhs_exact_pass219_hhcq_symbolic_equilibrium(
        carrier, prime_p, prime_q, &out_manifold->equilibrium);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hhcq_symbolic_gate(
        carrier, prime_p, prime_q, base_resolution_index, &out_manifold->gate);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_manifold->symbolic_carrier_admitted = 1U;
    out_manifold->global_relation_graph_exact = carrier->global_relation_graph_exact;
    out_manifold->symbolic_equilibrium_exact =
        out_manifold->equilibrium.equilibrium_relation_well_typed;
    out_manifold->symbolic_square_gate_exact = out_manifold->gate.typed_gate_well_formed;
    out_manifold->ordered_products_exact = carrier->ordered_noncommutative_products;
    out_manifold->constraint_intersection_satisfied =
        out_manifold->symbolic_carrier_admitted &&
        out_manifold->global_relation_graph_exact &&
        out_manifold->symbolic_equilibrium_exact &&
        out_manifold->symbolic_square_gate_exact &&
        out_manifold->ordered_products_exact &&
        out_manifold->gate.resolution_noncoarsening ? 1U : 0U;
    out_manifold->raw_projection_authority = 0U;
    out_manifold->scalar_integer_semantic_authority = 0U;
    out_manifold->candidate_only = 1U;
    out_manifold->canonical_mutation_authority = 0U;
    out_manifold->canonical_hash72_authority = 0U;
    out_manifold->canonical_hash216_authority = 0U;
    out_manifold->canonical_persistence_authority = 0U;
    out_manifold->floating_point_authority = 0U;
    out_manifold->manifold_signature64 = hhs_p219_p12_manifold_signature(out_manifold);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold
) {
    HHSExactStatus status = hhs_exact_pass219_hhcq_symbolic_carrier_validate(carrier);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_p219_p12_manifold_from_admitted_carrier(
        carrier, prime_p, prime_q, base_resolution_index, out_manifold);
}

HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
    const HHSExactPass219OctonionStateV1 *raw_projection,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold
) {
    HHSExactPass219HHCQSymbolicAdmissionV1 admission;
    HHSExactPass219HHCQSymbolicManifoldV1 admitted;
    HHSExactStatus status;
    if (raw_projection == NULL || out_manifold == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&admission, 0, sizeof(admission));
    status = hhs_exact_pass219_hhcq_symbolic_admit_projection(raw_projection, &admission);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    if (admission.symbolic_carrier_admitted == 0U) {
        memset(out_manifold, 0, sizeof(*out_manifold));
        out_manifold->struct_size = (uint32_t)sizeof(*out_manifold);
        out_manifold->version = HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION;
        out_manifold->admission = admission;
        out_manifold->raw_projection_authority = 0U;
        out_manifold->scalar_integer_semantic_authority = 0U;
        out_manifold->candidate_only = 1U;
        out_manifold->manifold_signature64 = hhs_p219_p12_manifold_signature(out_manifold);
        return HHS_EXACT_STATUS_OK;
    }

    memset(&admitted, 0, sizeof(admitted));
    status = hhs_p219_p12_manifold_from_admitted_carrier(
        &admission.carrier, prime_p, prime_q, base_resolution_index, &admitted);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    admitted.admission = admission;
    admitted.raw_projection_authority = 0U;
    admitted.scalar_integer_semantic_authority = 0U;
    admitted.manifold_signature64 = hhs_p219_p12_manifold_signature(&admitted);
    *out_manifold = admitted;
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
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold
) {
    HHSExactPass219OctonionSurfaceV1 surface;
    HHSExactStatus status;
    if (frame == NULL || out_manifold == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(&surface, 0, sizeof(surface));
    status = hhs_exact_pass219_octonion_from_vm81(
        frame, x_cell, y_cell, z_cell, w_cell, &surface);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
        &surface.state, prime_p, prime_q, base_resolution_index, out_manifold);
}

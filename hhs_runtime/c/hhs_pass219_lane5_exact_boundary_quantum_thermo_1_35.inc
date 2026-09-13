#include "../include/hhs_pass219_lane5_exact_boundary_quantum_thermo_1_35.h"

#include <limits.h>
#include <string.h>

static const uint8_t HHS_PASS219_LANE5_BOUNDARY_SOURCE[] =
    "(P²=pq+(2P/(p+q)) /{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-(({{b^4,c^4,(c^2-u^(b⁶c⁴))=b²/2u⁷²=((b^(b^2/12))^72==2^6)},{c^2,((b^2)(c^2)-(a^2))/u^((s==(b^(2c^2)c^b^4)^2)/((b⁶c⁴)P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b⁶c⁴)(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/(t^3-t)u^72} where ∆/P=√(pq+u⁷²)^x² and b²P-(p+q)=x+y+z+w+xy+yx+zw+wz=((b^(b^2/(b^4c^2)))^(b^6c^4)/(c^b^2-a^b^2)^(b^2*c^2)-a^2==c^2-b^2-a^2)\n\n"
    "(u^(Mod(72^72,5184)-Factorial((u^v/(((xy)z)w)))-(x+y+z+w+(xy)+(yx)+(zw)+(w*z)))t^3)/u^72-t==(u^0+E^(x^2Pi))/(t^3-t)=P²-pq-c²+b²+a²";

static const uint8_t HHS_PASS219_LANE5_BOUNDARY_SHA256[32] = {
    0x93, 0x8a, 0x39, 0x48, 0x7f, 0x18, 0x41, 0x99,
    0x96, 0x09, 0xd7, 0xc7, 0x5f, 0x94, 0x4b, 0x26,
    0x69, 0x4c, 0x5a, 0xad, 0xfc, 0x6e, 0x54, 0x0c,
    0x29, 0x57, 0x6c, 0x1b, 0xb7, 0xd5, 0x7d, 0x8d
};

_Static_assert(
    sizeof(HHS_PASS219_LANE5_BOUNDARY_SOURCE) - 1U == HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES,
    "Lane 5 boundary source byte count drifted"
);

static uint64_t hhs_lane5_qt_mix64(uint64_t h, uint64_t v) {
    h ^= v;
    h *= UINT64_C(1099511628211);
    h ^= h >> 32U;
    return h;
}

static uint64_t hhs_lane5_qt_bytes64(uint64_t h, const uint8_t *bytes, size_t length) {
    size_t i;
    for (i = 0U; i < length; ++i) {
        h = hhs_lane5_qt_mix64(h, (uint64_t)bytes[i]);
    }
    return h;
}

static uint32_t hhs_lane5_qt_mod_pow_u32(uint32_t base, uint32_t exponent, uint32_t modulus) {
    uint64_t result = 1U;
    uint64_t b = (uint64_t)(base % modulus);
    uint32_t e = exponent;
    while (e != 0U) {
        if ((e & 1U) != 0U) {
            result = (result * b) % modulus;
        }
        b = (b * b) % modulus;
        e >>= 1U;
    }
    return (uint32_t)result;
}

static int hhs_lane5_qt_biguint_canonical(const HHSExactBigUIntView *view, int allow_zero) {
    if (view == NULL || view->struct_size != sizeof(*view) || view->bytes_be == NULL ||
        view->byte_length == 0U || view->byte_length > HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES) {
        return 0;
    }
    if (view->byte_length > 1U && view->bytes_be[0] == 0U) {
        return 0;
    }
    if (!allow_zero && view->byte_length == 1U && view->bytes_be[0] == 0U) {
        return 0;
    }
    return 1;
}

static int hhs_lane5_qt_fixed_compare(
    const uint8_t a[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES],
    const uint8_t b[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES]
) {
    size_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES; ++i) {
        if (a[i] < b[i]) return -1;
        if (a[i] > b[i]) return 1;
    }
    return 0;
}

static void hhs_lane5_qt_fixed_subtract(
    uint8_t a[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES],
    const uint8_t b[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES]
) {
    size_t i = HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES;
    uint16_t borrow = 0U;
    while (i != 0U) {
        uint16_t av;
        uint16_t bv;
        --i;
        av = (uint16_t)a[i];
        bv = (uint16_t)b[i] + borrow;
        if (av >= bv) {
            a[i] = (uint8_t)(av - bv);
            borrow = 0U;
        } else {
            a[i] = (uint8_t)(UINT16_C(256) + av - bv);
            borrow = 1U;
        }
    }
}

static void hhs_lane5_qt_fixed_shift_add(
    uint8_t a[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES],
    uint8_t bit
) {
    size_t i = HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES;
    uint16_t carry = (uint16_t)(bit & 1U);
    while (i != 0U) {
        uint16_t v;
        --i;
        v = (uint16_t)((uint16_t)a[i] * UINT16_C(2) + carry);
        a[i] = (uint8_t)(v & UINT16_C(0xff));
        carry = (uint16_t)(v >> 8U);
    }
}

static int hhs_lane5_qt_biguint_divisible(
    const HHSExactBigUIntView *numerator,
    const HHSExactBigUIntView *denominator
) {
    uint8_t rem[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES];
    uint8_t den[HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES];
    size_t offset;
    size_t byte_index;
    memset(rem, 0, sizeof(rem));
    memset(den, 0, sizeof(den));
    offset = HHS_EXACT_PASS219_LANE5_BOUNDARY_MAX_BIGINT_BYTES - denominator->byte_length;
    memcpy(&den[offset], denominator->bytes_be, denominator->byte_length);
    for (byte_index = 0U; byte_index < numerator->byte_length; ++byte_index) {
        int bit_index;
        uint8_t current = numerator->bytes_be[byte_index];
        for (bit_index = 7; bit_index >= 0; --bit_index) {
            hhs_lane5_qt_fixed_shift_add(rem, (uint8_t)((current >> (unsigned)bit_index) & 1U));
            if (hhs_lane5_qt_fixed_compare(rem, den) >= 0) {
                hhs_lane5_qt_fixed_subtract(rem, den);
            }
        }
    }
    for (byte_index = 0U; byte_index < sizeof(rem); ++byte_index) {
        if (rem[byte_index] != 0U) return 0;
    }
    return 1;
}

static uint64_t hhs_lane5_qt_gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        const uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a;
}

static int hhs_lane5_qt_mul_u64(uint64_t a, uint64_t b, uint64_t *out) {
    if (out == NULL) return 0;
    if (a != 0U && b > UINT64_MAX / a) return 0;
    *out = a * b;
    return 1;
}

uint32_t hhs_exact_pass219_lane5_boundary_qt_version(void) {
    return HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
}

HHSExactStatus hhs_exact_pass219_lane5_boundary_qt_authority(
    HHSExactPass219Lane5BoundaryQTAuthorityV1 *out_authority
) {
    if (out_authority == NULL || out_authority->struct_size != sizeof(*out_authority)) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    memset(out_authority, 0, sizeof(*out_authority));
    out_authority->struct_size = sizeof(*out_authority);
    out_authority->version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    out_authority->boundary_source_bytes = HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES;
    memcpy(out_authority->boundary_source_sha256, HHS_PASS219_LANE5_BOUNDARY_SHA256, sizeof(HHS_PASS219_LANE5_BOUNDARY_SHA256));
    out_authority->verbatim_boundary_preserved = 1U;
    out_authority->indivisible_constraint_surface = 1U;
    out_authority->mod72_72_5184_exact_zero = 1U;
    out_authority->factorial_bigint_domain_exact = 1U;
    out_authority->symbolic_transcendentals_required = 1U;
    out_authority->pass117_exact_quantum_semantics_bound = 1U;
    out_authority->pass118_symbolic_harmonicode_bound = 1U;
    out_authority->quantum_probability_candidate_only = 1U;
    out_authority->hyperbolic_projection_candidate_only = 1U;
    out_authority->thermodynamic_witness_candidate_only = 1U;
    out_authority->deterministic_sampling_replayable = 1U;
    out_authority->physical_quantum_execution_claim = 0U;
    out_authority->exact_integer_canonical_authority = 0U;
    out_authority->floating_point_canonical_authority = 0U;
    out_authority->canonical_vm81_mutation_authority = 0U;
    out_authority->canonical_hash72_authority = 0U;
    out_authority->canonical_hash216_authority = 0U;
    out_authority->canonical_persistence_authority = 0U;
    out_authority->pqc_key_authority = 0U;
    out_authority->receipt_clock_authority = 0U;
    out_authority->requires_lane5_mediation = 1U;
    out_authority->requires_signed_environmental_vm81_admission = 1U;
    out_authority->initial_full_residual_evaluator_available = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_boundary_source(
    uint8_t *out_bytes,
    size_t capacity,
    size_t *out_length
) {
    if (out_length == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_length = HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES;
    if (out_bytes == NULL || capacity < HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES) {
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    }
    memcpy(out_bytes, HHS_PASS219_LANE5_BOUNDARY_SOURCE, HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_boundary_source_sha256(
    uint8_t out_sha256[HHS_EXACT_PASS219_LANE5_BOUNDARY_SHA256_BYTES]
) {
    if (out_sha256 == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memcpy(out_sha256, HHS_PASS219_LANE5_BOUNDARY_SHA256, sizeof(HHS_PASS219_LANE5_BOUNDARY_SHA256));
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_boundary_mod_anchor(uint32_t *out_remainder) {
    if (out_remainder == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_remainder = hhs_lane5_qt_mod_pow_u32(UINT32_C(72), UINT32_C(72), UINT32_C(5184));
    return (*out_remainder == 0U) ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

HHSExactStatus hhs_exact_pass219_lane5_factorial_domain_check(
    const HHSExactPass219Lane5FactorialDomainV1 *domain,
    uint8_t *out_encoding_canonical,
    uint8_t *out_denominator_nonzero,
    uint8_t *out_integral
) {
    int numerator_ok;
    int denominator_ok;
    if (domain == NULL || domain->struct_size != sizeof(*domain) ||
        domain->version != HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION ||
        out_encoding_canonical == NULL || out_denominator_nonzero == NULL || out_integral == NULL) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    *out_encoding_canonical = 0U;
    *out_denominator_nonzero = 0U;
    *out_integral = 0U;
    numerator_ok = hhs_lane5_qt_biguint_canonical(&domain->numerator, 1);
    denominator_ok = hhs_lane5_qt_biguint_canonical(&domain->denominator, 0);
    if (!numerator_ok || !denominator_ok) return HHS_EXACT_STATUS_OK;
    *out_encoding_canonical = 1U;
    *out_denominator_nonzero = 1U;
    *out_integral = (uint8_t)(hhs_lane5_qt_biguint_divisible(&domain->numerator, &domain->denominator) ? 1U : 0U);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_lane5_boundary_preflight(
    const HHSExactPass219Lane5BoundaryPreflightV1 *request,
    HHSExactPass219Lane5BoundaryReceiptV1 *out_receipt
) {
    HHSExactPass219Lane5MediationReceiptV1 recomputed;
    uint8_t encoding = 0U;
    uint8_t denominator_nonzero = 0U;
    uint8_t integral = 0U;
    HHSExactStatus status;
    uint32_t mod_anchor = UINT32_MAX;
    uint64_t h = UINT64_C(1469598103934665603);
    uint64_t exploration = UINT64_C(1469598103934665603);

    if (request == NULL || out_receipt == NULL ||
        request->struct_size != sizeof(*request) ||
        request->version != HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION ||
        out_receipt->struct_size != sizeof(*out_receipt)) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    out_receipt->boundary_class = HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT;
    out_receipt->candidate_only = 1U;
    out_receipt->requires_environmental_admission = 1U;

    if (memcmp(request->boundary_source_sha256, HHS_PASS219_LANE5_BOUNDARY_SHA256, sizeof(HHS_PASS219_LANE5_BOUNDARY_SHA256)) != 0) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_SOURCE_IDENTITY;
        return HHS_EXACT_STATUS_OK;
    }
    out_receipt->source_identity_verified = 1U;

    memset(&recomputed, 0, sizeof(recomputed));
    recomputed.struct_size = sizeof(recomputed);
    status = hhs_exact_pass219_lane5_mediate_candidate(&request->lane5_request, &recomputed);
    if (status != HHS_EXACT_STATUS_OK || memcmp(&recomputed, &request->lane5_receipt, sizeof(recomputed)) != 0 ||
        recomputed.decision != HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY ||
        recomputed.candidate_only != 1U || recomputed.canonical_mutation_authority != 0U ||
        recomputed.requires_environmental_admission != 1U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_LANE5_MEDIATION;
        return HHS_EXACT_STATUS_OK;
    }
    out_receipt->lane5_mediation_recomputed = 1U;
    out_receipt->lane5_mediation_signature64 = recomputed.mediation_signature64;

    status = hhs_exact_pass219_lane5_factorial_domain_check(
        &request->factorial_domain, &encoding, &denominator_nonzero, &integral
    );
    if (status != HHS_EXACT_STATUS_OK) return status;
    out_receipt->factorial_encoding_canonical = encoding;
    out_receipt->factorial_denominator_nonzero = denominator_nonzero;
    out_receipt->factorial_argument_integral = integral;
    if (encoding == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_ENCODING;
        return HHS_EXACT_STATUS_OK;
    }
    if (denominator_nonzero == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_DENOMINATOR_ZERO;
        return HHS_EXACT_STATUS_OK;
    }
    if (integral == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_NONINTEGRAL;
        return HHS_EXACT_STATUS_OK;
    }
    if (request->symbolic_transcendentals_preserved == 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_SYMBOLIC_TRANSCENDENTAL;
        return HHS_EXACT_STATUS_OK;
    }
    out_receipt->symbolic_transcendentals_preserved = 1U;
    if (request->floating_point_canonical_requested != 0U) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FLOAT_CANONICAL_REQUEST;
        return HHS_EXACT_STATUS_OK;
    }
    status = hhs_exact_pass219_lane5_boundary_mod_anchor(&mod_anchor);
    if (status != HHS_EXACT_STATUS_OK) return status;
    out_receipt->mod72_72_5184 = mod_anchor;

    if (request->exact_full_residual_evaluator_receipt_present != 0U ||
        request->exact_full_residual_evaluator_signature64 != 0U ||
        request->exact_full_residual_classification != HHS_EXACT_PASS219_LANE5_BOUNDARY_UNRESOLVED) {
        out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_EVALUATOR_PROVENANCE;
        return HHS_EXACT_STATUS_OK;
    }

    out_receipt->boundary_class = HHS_EXACT_PASS219_LANE5_BOUNDARY_UNRESOLVED;
    out_receipt->reason = HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FULL_RESIDUAL_UNRESOLVED;
    out_receipt->full_residual_unresolved = 1U;

    h = hhs_lane5_qt_bytes64(h, HHS_PASS219_LANE5_BOUNDARY_SHA256, sizeof(HHS_PASS219_LANE5_BOUNDARY_SHA256));
    h = hhs_lane5_qt_mix64(h, recomputed.closure_signature64);
    h = hhs_lane5_qt_mix64(h, recomputed.mediation_signature64);
    h = hhs_lane5_qt_mix64(h, (uint64_t)mod_anchor);
    h = hhs_lane5_qt_mix64(h, (uint64_t)encoding);
    h = hhs_lane5_qt_mix64(h, (uint64_t)integral);
    h = hhs_lane5_qt_mix64(h, (uint64_t)request->symbolic_transcendentals_preserved);
    out_receipt->boundary_witness_signature64 = h;

    exploration = hhs_lane5_qt_mix64(exploration, request->quantum_witness_signature64);
    exploration = hhs_lane5_qt_mix64(exploration, request->hyperbolic_witness_signature64);
    exploration = hhs_lane5_qt_mix64(exploration, request->thermodynamic_witness_signature64);
    exploration = hhs_lane5_qt_mix64(exploration, request->deterministic_sampling_signature64);
    out_receipt->exploration_witness_signature64 = exploration;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_thermo_reciprocal_closure(
    const HHSExactPass219ThermoReciprocalInputV1 *input,
    HHSExactPass219ThermoReciprocalReceiptV1 *out_receipt
) {
    uint64_t diff;
    uint64_t numerator;
    uint64_t denominator;
    uint64_t divisor;
    uint64_t h = UINT64_C(1469598103934665603);
    if (input == NULL || out_receipt == NULL ||
        input->struct_size != sizeof(*input) ||
        input->version != HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION ||
        out_receipt->struct_size != sizeof(*out_receipt)) {
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    }
    memset(out_receipt, 0, sizeof(*out_receipt));
    out_receipt->struct_size = sizeof(*out_receipt);
    out_receipt->version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    out_receipt->candidate_only = 1U;
    if (input->g_numerator == 0U || input->g_denominator == 0U) {
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    }
    out_receipt->positive_domain = 1U;
    diff = (input->g_numerator >= input->g_denominator)
        ? input->g_numerator - input->g_denominator
        : input->g_denominator - input->g_numerator;
    if (!hhs_lane5_qt_mul_u64(diff, diff, &numerator) ||
        !hhs_lane5_qt_mul_u64(input->g_numerator, input->g_denominator, &denominator)) {
        return HHS_EXACT_STATUS_RANGE_ERROR;
    }
    divisor = hhs_lane5_qt_gcd_u64(numerator, denominator);
    if (divisor == 0U) divisor = denominator;
    out_receipt->reduced_numerator = numerator / divisor;
    out_receipt->reduced_denominator = denominator / divisor;
    out_receipt->reciprocal_equilibrium = (uint8_t)(numerator == 0U ? 1U : 0U);
    out_receipt->logarithm_cancelled_symbolically = 1U;
    out_receipt->exact_rational = 1U;
    h = hhs_lane5_qt_mix64(h, input->g_numerator);
    h = hhs_lane5_qt_mix64(h, input->g_denominator);
    h = hhs_lane5_qt_mix64(h, out_receipt->reduced_numerator);
    h = hhs_lane5_qt_mix64(h, out_receipt->reduced_denominator);
    out_receipt->witness_signature64 = h;
    return HHS_EXACT_STATUS_OK;
}

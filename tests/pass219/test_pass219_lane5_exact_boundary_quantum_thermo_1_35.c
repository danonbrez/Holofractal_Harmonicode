#include "hhs_pass219_lane5_exact_boundary_quantum_thermo_1_35.h"

#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHECK(expr) do { if (!(expr)) { \
    fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); return 1; \
} } while (0)

static const uint8_t EXPECTED_SOURCE[] =
    "(P²=pq+(2P/(p+q)) /{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-(({{b^4,c^4,(c^2-u^(b⁶c⁴))=b²/2u⁷²=((b^(b^2/12))^72==2^6)},{c^2,((b^2)(c^2)-(a^2))/u^((s==(b^(2c^2)c^b^4)^2)/((b⁶c⁴)P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b⁶c⁴)(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/(t^3-t)u^72} where ∆/P=√(pq+u⁷²)^x² and b²P-(p+q)=x+y+z+w+xy+yx+zw+wz=((b^(b^2/(b^4c^2)))^(b^6c^4)/(c^b^2-a^b^2)^(b^2*c^2)-a^2==c^2-b^2-a^2)\n\n"
    "(u^(Mod(72^72,5184)-Factorial((u^v/(((xy)z)w)))-(x+y+z+w+(xy)+(yx)+(zw)+(w*z)))t^3)/u^72-t==(u^0+E^(x^2Pi))/(t^3-t)=P²-pq-c²+b²+a²";

static const uint8_t EXPECTED_SHA256[32] = {
    0x93, 0x8a, 0x39, 0x48, 0x7f, 0x18, 0x41, 0x99,
    0x96, 0x09, 0xd7, 0xc7, 0x5f, 0x94, 0x4b, 0x26,
    0x69, 0x4c, 0x5a, 0xad, 0xfc, 0x6e, 0x54, 0x0c,
    0x29, 0x57, 0x6c, 0x1b, 0xb7, 0xd5, 0x7d, 0x8d
};

static void make_lane5_request(HHSExactPass219Lane5MediationRequestV1 *r) {
    memset(r, 0, sizeof(*r));
    r->struct_size = sizeof(*r);
    r->version = HHS_EXACT_PASS219_LANE5_NUCLEUS_VERSION;
    r->namespace_id = HHS_EXACT_PASS219_LANE5_NAMESPACE;
    r->hash216_reference_count = 1U;
    r->capability_reference_count = 1U;
    r->learning_stage = 5U;
    r->request_signature64 = UINT64_C(0x101);
    r->candidate_signature64 = UINT64_C(0x202);
    r->parent_hash216_signature64 = UINT64_C(0x303);
    r->bigint_address_signature64 = UINT64_C(0x404);
    r->hydration_signature64 = UINT64_C(0x505);
    r->compression_signature64 = UINT64_C(0x606);
    r->capability_registry_signature64 = UINT64_C(0x707);
    r->learning_iteration_signature64 = UINT64_C(0x808);
    r->rna_prepared_signature64 = UINT64_C(0x909);
    r->rna_decision_signature64 = UINT64_C(0xa0a);
    r->hash216_reference_signature64[0] = UINT64_C(0xb0b);
    r->capability_reference_signature64[0] = UINT64_C(0xc0c);
}

static void make_factorial_domain(
    HHSExactPass219Lane5FactorialDomainV1 *d,
    const uint8_t *num, uint32_t num_len,
    const uint8_t *den, uint32_t den_len
) {
    memset(d, 0, sizeof(*d));
    d->struct_size = sizeof(*d);
    d->version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    d->numerator.struct_size = sizeof(d->numerator);
    d->numerator.byte_length = num_len;
    d->numerator.bytes_be = num;
    d->denominator.struct_size = sizeof(d->denominator);
    d->denominator.byte_length = den_len;
    d->denominator.bytes_be = den;
}

static int preflight(
    const HHSExactPass219Lane5MediationRequestV1 *lane5_request,
    const HHSExactPass219Lane5MediationReceiptV1 *lane5_receipt,
    const HHSExactPass219Lane5FactorialDomainV1 *factorial,
    HHSExactPass219Lane5BoundaryReceiptV1 *out
) {
    HHSExactPass219Lane5BoundaryPreflightV1 q;
    memset(&q, 0, sizeof(q));
    q.struct_size = sizeof(q);
    q.version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    memcpy(q.boundary_source_sha256, EXPECTED_SHA256, sizeof(EXPECTED_SHA256));
    q.lane5_request = *lane5_request;
    q.lane5_receipt = *lane5_receipt;
    q.factorial_domain = *factorial;
    q.symbolic_transcendentals_preserved = 1U;
    q.quantum_witness_signature64 = UINT64_C(0x1111);
    q.hyperbolic_witness_signature64 = UINT64_C(0x2222);
    q.thermodynamic_witness_signature64 = UINT64_C(0x3333);
    q.deterministic_sampling_signature64 = UINT64_C(0x4444);
    memset(out, 0, sizeof(*out));
    out->struct_size = sizeof(*out);
    return (int)hhs_exact_pass219_lane5_boundary_preflight(&q, out);
}

int main(void) {
    HHSExactPass219Lane5BoundaryQTAuthorityV1 authority;
    HHSExactPass219Lane5MediationRequestV1 lane5_request;
    HHSExactPass219Lane5MediationReceiptV1 lane5_receipt;
    HHSExactPass219Lane5FactorialDomainV1 factorial;
    HHSExactPass219Lane5BoundaryReceiptV1 boundary;
    HHSExactPass219ThermoReciprocalInputV1 thermo;
    HHSExactPass219ThermoReciprocalReceiptV1 thermo_receipt;
    uint8_t source[HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES];
    uint8_t digest[32];
    uint8_t exposed_digest[32];
    size_t source_len = 0U;
    uint32_t mod_anchor = UINT32_MAX;
    uint8_t num12[] = {12U};
    uint8_t den3[] = {3U};
    uint8_t num5[] = {5U};
    uint8_t den2[] = {2U};
    uint8_t bad_leading[] = {0U, 12U};
    uint8_t zero[] = {0U};
    HHSExactPass219Lane5BoundaryPreflightV1 forged;

    memset(&authority, 0, sizeof(authority));
    authority.struct_size = sizeof(authority);
    CHECK(hhs_exact_pass219_lane5_boundary_qt_authority(&authority) == HHS_EXACT_STATUS_OK);
    CHECK(authority.version == HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION);
    CHECK(authority.verbatim_boundary_preserved == 1U);
    CHECK(authority.indivisible_constraint_surface == 1U);
    CHECK(authority.mod72_72_5184_exact_zero == 1U);
    CHECK(authority.factorial_bigint_domain_exact == 1U);
    CHECK(authority.pass117_exact_quantum_semantics_bound == 1U);
    CHECK(authority.pass118_symbolic_harmonicode_bound == 1U);
    CHECK(authority.physical_quantum_execution_claim == 0U);
    CHECK(authority.floating_point_canonical_authority == 0U);
    CHECK(authority.canonical_vm81_mutation_authority == 0U);
    CHECK(authority.canonical_hash72_authority == 0U);
    CHECK(authority.canonical_hash216_authority == 0U);
    CHECK(authority.requires_lane5_mediation == 1U);
    CHECK(authority.requires_signed_environmental_vm81_admission == 1U);
    CHECK(authority.initial_full_residual_evaluator_available == 0U);

    CHECK(hhs_exact_pass219_lane5_boundary_source(source, sizeof(source), &source_len) == HHS_EXACT_STATUS_OK);
    CHECK(source_len == sizeof(EXPECTED_SOURCE) - 1U);
    CHECK(source_len == HHS_EXACT_PASS219_LANE5_BOUNDARY_SOURCE_BYTES);
    CHECK(memcmp(source, EXPECTED_SOURCE, source_len) == 0);
    CHECK(SHA256(source, source_len, digest) != NULL);
    CHECK(memcmp(digest, EXPECTED_SHA256, sizeof(digest)) == 0);
    CHECK(hhs_exact_pass219_lane5_boundary_source_sha256(exposed_digest) == HHS_EXACT_STATUS_OK);
    CHECK(memcmp(exposed_digest, EXPECTED_SHA256, sizeof(exposed_digest)) == 0);

    CHECK(hhs_exact_pass219_lane5_boundary_mod_anchor(&mod_anchor) == HHS_EXACT_STATUS_OK);
    CHECK(mod_anchor == 0U);

    make_lane5_request(&lane5_request);
    memset(&lane5_receipt, 0, sizeof(lane5_receipt));
    lane5_receipt.struct_size = sizeof(lane5_receipt);
    CHECK(hhs_exact_pass219_lane5_mediate_candidate(&lane5_request, &lane5_receipt) == HHS_EXACT_STATUS_OK);
    CHECK(lane5_receipt.decision == HHS_EXACT_PASS219_LANE5_DECISION_CANDIDATE_READY);

    make_factorial_domain(&factorial, num12, sizeof(num12), den3, sizeof(den3));
    CHECK(preflight(&lane5_request, &lane5_receipt, &factorial, &boundary) == HHS_EXACT_STATUS_OK);
    CHECK(boundary.boundary_class == HHS_EXACT_PASS219_LANE5_BOUNDARY_UNRESOLVED);
    CHECK(boundary.reason == HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FULL_RESIDUAL_UNRESOLVED);
    CHECK(boundary.source_identity_verified == 1U);
    CHECK(boundary.lane5_mediation_recomputed == 1U);
    CHECK(boundary.factorial_argument_integral == 1U);
    CHECK(boundary.mod72_72_5184 == 0U);
    CHECK(boundary.full_residual_unresolved == 1U);
    CHECK(boundary.candidate_only == 1U);
    CHECK(boundary.canonical_mutation_authority == 0U);
    CHECK(boundary.boundary_witness_signature64 != 0U);

    make_factorial_domain(&factorial, num5, sizeof(num5), den2, sizeof(den2));
    CHECK(preflight(&lane5_request, &lane5_receipt, &factorial, &boundary) == HHS_EXACT_STATUS_OK);
    CHECK(boundary.boundary_class == HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT);
    CHECK(boundary.reason == HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_NONINTEGRAL);

    make_factorial_domain(&factorial, bad_leading, sizeof(bad_leading), den3, sizeof(den3));
    CHECK(preflight(&lane5_request, &lane5_receipt, &factorial, &boundary) == HHS_EXACT_STATUS_OK);
    CHECK(boundary.boundary_class == HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT);
    CHECK(boundary.reason == HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FACTORIAL_ENCODING);

    make_factorial_domain(&factorial, num12, sizeof(num12), zero, sizeof(zero));
    CHECK(preflight(&lane5_request, &lane5_receipt, &factorial, &boundary) == HHS_EXACT_STATUS_OK);
    CHECK(boundary.boundary_class == HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT);

    make_factorial_domain(&factorial, num12, sizeof(num12), den3, sizeof(den3));
    memset(&forged, 0, sizeof(forged));
    forged.struct_size = sizeof(forged);
    forged.version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    memcpy(forged.boundary_source_sha256, EXPECTED_SHA256, sizeof(EXPECTED_SHA256));
    forged.lane5_request = lane5_request;
    forged.lane5_receipt = lane5_receipt;
    forged.factorial_domain = factorial;
    forged.symbolic_transcendentals_preserved = 1U;
    forged.exact_full_residual_evaluator_receipt_present = 1U;
    forged.exact_full_residual_classification = HHS_EXACT_PASS219_LANE5_BOUNDARY_ADMIT;
    forged.exact_full_residual_evaluator_signature64 = UINT64_C(0xfeed);
    memset(&boundary, 0, sizeof(boundary)); boundary.struct_size = sizeof(boundary);
    CHECK(hhs_exact_pass219_lane5_boundary_preflight(&forged, &boundary) == HHS_EXACT_STATUS_OK);
    CHECK(boundary.boundary_class == HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT);
    CHECK(boundary.reason == HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_EVALUATOR_PROVENANCE);

    forged.exact_full_residual_evaluator_receipt_present = 0U;
    forged.exact_full_residual_classification = HHS_EXACT_PASS219_LANE5_BOUNDARY_UNRESOLVED;
    forged.exact_full_residual_evaluator_signature64 = 0U;
    forged.floating_point_canonical_requested = 1U;
    memset(&boundary, 0, sizeof(boundary)); boundary.struct_size = sizeof(boundary);
    CHECK(hhs_exact_pass219_lane5_boundary_preflight(&forged, &boundary) == HHS_EXACT_STATUS_OK);
    CHECK(boundary.boundary_class == HHS_EXACT_PASS219_LANE5_BOUNDARY_REJECT);
    CHECK(boundary.reason == HHS_EXACT_PASS219_LANE5_BOUNDARY_REASON_FLOAT_CANONICAL_REQUEST);

    memset(&thermo, 0, sizeof(thermo));
    thermo.struct_size = sizeof(thermo);
    thermo.version = HHS_EXACT_PASS219_LANE5_BOUNDARY_QT_VERSION;
    thermo.g_numerator = 2U; thermo.g_denominator = 1U;
    memset(&thermo_receipt, 0, sizeof(thermo_receipt)); thermo_receipt.struct_size = sizeof(thermo_receipt);
    CHECK(hhs_exact_pass219_thermo_reciprocal_closure(&thermo, &thermo_receipt) == HHS_EXACT_STATUS_OK);
    CHECK(thermo_receipt.reduced_numerator == 1U);
    CHECK(thermo_receipt.reduced_denominator == 2U);
    CHECK(thermo_receipt.logarithm_cancelled_symbolically == 1U);
    CHECK(thermo_receipt.exact_rational == 1U);
    CHECK(thermo_receipt.canonical_mutation_authority == 0U);

    thermo.g_numerator = 1U; thermo.g_denominator = 1U;
    memset(&thermo_receipt, 0, sizeof(thermo_receipt)); thermo_receipt.struct_size = sizeof(thermo_receipt);
    CHECK(hhs_exact_pass219_thermo_reciprocal_closure(&thermo, &thermo_receipt) == HHS_EXACT_STATUS_OK);
    CHECK(thermo_receipt.reduced_numerator == 0U);
    CHECK(thermo_receipt.reduced_denominator == 1U);
    CHECK(thermo_receipt.reciprocal_equilibrium == 1U);

    thermo.g_numerator = 0U; thermo.g_denominator = 1U;
    memset(&thermo_receipt, 0, sizeof(thermo_receipt)); thermo_receipt.struct_size = sizeof(thermo_receipt);
    CHECK(hhs_exact_pass219_thermo_reciprocal_closure(&thermo, &thermo_receipt) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    thermo.g_numerator = UINT64_MAX; thermo.g_denominator = UINT64_MAX - 1U;
    memset(&thermo_receipt, 0, sizeof(thermo_receipt)); thermo_receipt.struct_size = sizeof(thermo_receipt);
    CHECK(hhs_exact_pass219_thermo_reciprocal_closure(&thermo, &thermo_receipt) == HHS_EXACT_STATUS_RANGE_ERROR);

    printf("PASS219_LANE5_BOUNDARY_QT_PASS source_bytes=%zu mod=%u lane5=%llu boundary=%llu thermo=%llu unresolved=1 forged_admit_rejected=1\n",
        source_len,
        mod_anchor,
        (unsigned long long)lane5_receipt.mediation_signature64,
        (unsigned long long)boundary.boundary_witness_signature64,
        (unsigned long long)thermo_receipt.witness_signature64);
    return 0;
}

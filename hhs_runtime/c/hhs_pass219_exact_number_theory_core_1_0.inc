#include "../include/hhs_pass219_exact_number_theory_core_1_0.h"

#include <stddef.h>
#include <string.h>

/*
 * Pass 219 exact number-theory core circuit.
 *
 * The source equation is retained as the authoritative relation graph.
 * Scalar substitution is not an execution rewrite.  The small integer
 * assertions below are witness-only sanity projections of inherited
 * a^2,b^2,c^2,d^2 bindings and never replace the source graph.
 */
static const char HHS219_EXACT_NUMBER_THEORY_EQUATION_SET[] =
    "P^2/{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-(({{b^4,c^4,c^2"
    "-u^(b⁶c⁴)},{c^2,(((b^2)*(c^2)-(a^2))=((a^2+b^2==c^2)+(a^2+a^2==b^2))/("
    "c^2-b^2)==d^2/a^2==((b^((x*y)+(z*w))+c^((x*y)+(z*w)))*I^(x^b^4+y^b^4+z"
    "^b^4+w^b^4))/(((x*y)*z)*w))/u^((s==(b^(2c^2)c^b^4)^2)/((b⁶c⁴)P^2)),((b"
    "^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2*(c^2+b^2))-(c^2-b^2))/Sqrt(c"
    "^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b⁶c⁴)*(pq+xy)))/B"
    "t==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/(t^3-t)*u^72} where ∆/P=√(pq+u⁷²"
    ")^x² and b²P-(p+q)=x+y+z+w+xy+yx+zw+wz\n\na²=(NcalcMatrixPower((List(Lis"
    "t(x,w,(y*x)),List((w*z),x+y+z+w,(z*w)),List((x*y),z,y))/List(List(I,I^"
    "3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))^b⁴\n\n\nSqrt((A*B))*(A*B)/Sq"
    "rt((A*B))==A/B*B/A==((-x*y)^(((x+y^2)*(y+x^2))/((x²+y²)²*Sqrt((a*b))))"
    ")^x² where A,B are two primes and AB=P⁴\nP⁴≠1 because P²-pq=1";

enum {
    HHS219_NT_PROOF_A2 = 1,
    HHS219_NT_PROOF_B2 = 2,
    HHS219_NT_PROOF_C2 = 3,
    HHS219_NT_PROOF_D2 = 5
};

_Static_assert(HHS_EXACT_PASS219_NUMBER_THEORY_RELATION_COUNT <= 64U,
               "number-theory relation mask must fit uint64_t");
_Static_assert(HHS219_NT_PROOF_A2 + HHS219_NT_PROOF_B2 == HHS219_NT_PROOF_C2,
               "witness projection: a^2+b^2==c^2");
_Static_assert(HHS219_NT_PROOF_A2 + HHS219_NT_PROOF_A2 == HHS219_NT_PROOF_B2,
               "witness projection: a^2+a^2==b^2");
_Static_assert((HHS219_NT_PROOF_B2 * HHS219_NT_PROOF_C2) - HHS219_NT_PROOF_A2 ==
               HHS219_NT_PROOF_D2,
               "witness projection: b^2*c^2-a^2==d^2/a^2");
_Static_assert((HHS219_NT_PROOF_B2 * HHS219_NT_PROOF_B2 * HHS219_NT_PROOF_B2) *
               (HHS219_NT_PROOF_C2 * HHS219_NT_PROOF_C2) == 72,
               "witness projection: b^6*c^4==72");

static uint32_t hhs219_nt_version_word(void) {
    return (HHS_EXACT_PASS219_NUMBER_THEORY_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_NUMBER_THEORY_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_NUMBER_THEORY_VERSION_PATCH;
}

static int hhs219_nt_flag(uint8_t value) {
    return value == 0U || value == 1U;
}

static uint64_t hhs219_nt_fnv1a64(const char *text) {
    uint64_t hash = UINT64_C(0xcbf29ce484222325);
    const unsigned char *p = (const unsigned char *)text;

    while (*p != 0U) {
        hash ^= (uint64_t)*p++;
        hash *= UINT64_C(0x100000001b3);
    }
    return hash;
}

static uint32_t hhs219_nt_first_missing(uint64_t mask) {
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_NUMBER_THEORY_RELATION_COUNT; ++i) {
        if ((mask & (UINT64_C(1) << i)) != 0U)
            return i;
    }
    return HHS_EXACT_PASS219_NUMBER_THEORY_RELATION_COUNT;
}

uint32_t hhs_exact_pass219_number_theory_version(void) {
    return hhs219_nt_version_word();
}

uint64_t hhs_exact_pass219_number_theory_required_mask(void) {
    return (UINT64_C(1) << HHS_EXACT_PASS219_NUMBER_THEORY_RELATION_COUNT) - UINT64_C(1);
}

const char *hhs_exact_pass219_number_theory_equation_set(void) {
    return HHS219_EXACT_NUMBER_THEORY_EQUATION_SET;
}

uint64_t hhs_exact_pass219_number_theory_source_fnv1a64(void) {
    return hhs219_nt_fnv1a64(HHS219_EXACT_NUMBER_THEORY_EQUATION_SET);
}

int hhs_exact_pass219_number_theory_selfcheck(void) {
    const uint64_t required = hhs_exact_pass219_number_theory_required_mask();

    if (required != UINT64_C(0x0fff))
        return 0;
    if (hhs_exact_pass219_number_theory_source_fnv1a64() !=
        HHS_EXACT_PASS219_NUMBER_THEORY_SOURCE_FNV1A64)
        return 0;
    if (strstr(HHS219_EXACT_NUMBER_THEORY_EQUATION_SET, "P²-pq=1") == NULL)
        return 0;
    if (strstr(HHS219_EXACT_NUMBER_THEORY_EQUATION_SET, "AB=P⁴") == NULL)
        return 0;
    if (strstr(HHS219_EXACT_NUMBER_THEORY_EQUATION_SET, "b⁶c⁴") == NULL)
        return 0;
    if (strstr(HHS219_EXACT_NUMBER_THEORY_EQUATION_SET,
               "x+y+z+w+xy+yx+zw+wz") == NULL)
        return 0;
    if (strstr(HHS219_EXACT_NUMBER_THEORY_EQUATION_SET,
               "NcalcMatrixPower") == NULL)
        return 0;
    return 1;
}

int hhs_exact_pass219_number_theory_evaluate(
    const HHSExactPass219NumberTheoryInputV1 *input,
    HHSExactPass219NumberTheoryResultV1 *out_result
) {
    uint32_t reasons = 0U;
    uint64_t required;
    uint64_t observed;
    uint64_t missing;

    if (input == NULL || out_result == NULL)
        return 0;
    if (input->struct_size < sizeof(*input) ||
        input->version != hhs219_nt_version_word())
        return 0;
    if (!hhs219_nt_flag(input->source_identity_exact) ||
        !hhs219_nt_flag(input->equality_chain_preserved) ||
        !hhs219_nt_flag(input->scalar_projection_witness_only) ||
        !hhs219_nt_flag(input->noncommutative_order_preserved) ||
        !hhs219_nt_flag(input->no_float_authority))
        return 0;

    required = hhs_exact_pass219_number_theory_required_mask();
    observed = input->relation_witness_mask & required;
    missing = required & ~observed;

    if (missing != 0U)
        reasons |= HHS_EXACT_PASS219_NT_REASON_MISSING_RELATION;
    if (input->source_identity_exact == 0U)
        reasons |= HHS_EXACT_PASS219_NT_REASON_SOURCE_IDENTITY;
    if (input->equality_chain_preserved == 0U)
        reasons |= HHS_EXACT_PASS219_NT_REASON_EQUALITY_CHAIN;
    if (input->scalar_projection_witness_only == 0U)
        reasons |= HHS_EXACT_PASS219_NT_REASON_SCALAR_AUTHORITY;
    if (input->noncommutative_order_preserved == 0U)
        reasons |= HHS_EXACT_PASS219_NT_REASON_NONCOMMUTATIVE_ORDER;
    if (input->no_float_authority == 0U)
        reasons |= HHS_EXACT_PASS219_NT_REASON_FLOAT_AUTHORITY;
    if (!hhs_exact_pass219_number_theory_selfcheck())
        reasons |= HHS_EXACT_PASS219_NT_REASON_SOURCE_SELFCHECK;

    memset(out_result, 0, sizeof(*out_result));
    out_result->struct_size = (uint32_t)sizeof(*out_result);
    out_result->version = hhs219_nt_version_word();
    out_result->reason_mask = reasons;
    out_result->required_relation_mask = required;
    out_result->observed_relation_mask = observed;
    out_result->missing_relation_mask = missing;
    out_result->source_fnv1a64 = hhs_exact_pass219_number_theory_source_fnv1a64();
    out_result->first_missing_relation = hhs219_nt_first_missing(missing);
    out_result->source_identity_exact = input->source_identity_exact;
    out_result->equality_chain_preserved = input->equality_chain_preserved;
    out_result->scalar_projection_witness_only = input->scalar_projection_witness_only;
    out_result->noncommutative_order_preserved = input->noncommutative_order_preserved;
    out_result->no_float_authority = input->no_float_authority;
    out_result->scalar_projection_authority = 0U;
    out_result->floating_point_authority = 0U;
    out_result->decision = reasons == 0U
        ? HHS_EXACT_PASS219_NUMBER_THEORY_PROPAGATE
        : HHS_EXACT_PASS219_NUMBER_THEORY_REJECT;
    return 1;
}

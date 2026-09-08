#include "hhs_pass219_exact_number_theory_core_1_0.h"

#include <assert.h>
#include <string.h>

static HHSExactPass219NumberTheoryInputV1 complete_input(void) {
    HHSExactPass219NumberTheoryInputV1 input;
    memset(&input, 0, sizeof(input));
    input.struct_size = (uint32_t)sizeof(input);
    input.version = hhs_exact_pass219_number_theory_version();
    input.relation_witness_mask = hhs_exact_pass219_number_theory_required_mask();
    input.source_identity_exact = 1U;
    input.equality_chain_preserved = 1U;
    input.scalar_projection_witness_only = 1U;
    input.noncommutative_order_preserved = 1U;
    input.no_float_authority = 1U;
    return input;
}

int main(void) {
    HHSExactPass219NumberTheoryInputV1 input = complete_input();
    HHSExactPass219NumberTheoryResultV1 result;
    const char *equation_set = hhs_exact_pass219_number_theory_equation_set();

    assert(hhs_exact_pass219_number_theory_selfcheck());
    assert(hhs_exact_pass219_number_theory_source_fnv1a64() ==
           HHS_EXACT_PASS219_NUMBER_THEORY_SOURCE_FNV1A64);
    assert(strstr(equation_set, "P²-pq=1") != NULL);
    assert(strstr(equation_set, "AB=P⁴") != NULL);
    assert(strstr(equation_set, "b⁶c⁴") != NULL);
    assert(strstr(equation_set, "x+y+z+w+xy+yx+zw+wz") != NULL);
    assert(strstr(equation_set, "NcalcMatrixPower") != NULL);

    assert(hhs_exact_pass219_number_theory_evaluate(&input, &result));
    assert(result.decision == HHS_EXACT_PASS219_NUMBER_THEORY_PROPAGATE);
    assert(result.reason_mask == 0U);
    assert(result.missing_relation_mask == 0U);
    assert(result.scalar_projection_authority == 0U);
    assert(result.floating_point_authority == 0U);

    input = complete_input();
    input.relation_witness_mask &= ~(UINT64_C(1) << HHS_EXACT_PASS219_NT_AB_EQUALS_P4);
    assert(hhs_exact_pass219_number_theory_evaluate(&input, &result));
    assert(result.decision == HHS_EXACT_PASS219_NUMBER_THEORY_REJECT);
    assert((result.reason_mask & HHS_EXACT_PASS219_NT_REASON_MISSING_RELATION) != 0U);
    assert(result.first_missing_relation == HHS_EXACT_PASS219_NT_AB_EQUALS_P4);

    input = complete_input();
    input.equality_chain_preserved = 0U;
    assert(hhs_exact_pass219_number_theory_evaluate(&input, &result));
    assert(result.decision == HHS_EXACT_PASS219_NUMBER_THEORY_REJECT);
    assert((result.reason_mask & HHS_EXACT_PASS219_NT_REASON_EQUALITY_CHAIN) != 0U);

    input = complete_input();
    input.scalar_projection_witness_only = 0U;
    assert(hhs_exact_pass219_number_theory_evaluate(&input, &result));
    assert(result.decision == HHS_EXACT_PASS219_NUMBER_THEORY_REJECT);
    assert((result.reason_mask & HHS_EXACT_PASS219_NT_REASON_SCALAR_AUTHORITY) != 0U);

    input = complete_input();
    input.noncommutative_order_preserved = 0U;
    assert(hhs_exact_pass219_number_theory_evaluate(&input, &result));
    assert(result.decision == HHS_EXACT_PASS219_NUMBER_THEORY_REJECT);
    assert((result.reason_mask & HHS_EXACT_PASS219_NT_REASON_NONCOMMUTATIVE_ORDER) != 0U);

    input = complete_input();
    input.no_float_authority = 0U;
    assert(hhs_exact_pass219_number_theory_evaluate(&input, &result));
    assert(result.decision == HHS_EXACT_PASS219_NUMBER_THEORY_REJECT);
    assert((result.reason_mask & HHS_EXACT_PASS219_NT_REASON_FLOAT_AUTHORITY) != 0U);

    return 0;
}

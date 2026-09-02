#include "../include/hhs_pass219_dynamic_paradox_phase_cycle_1_0.h"

#include <stddef.h>
#include <string.h>

static uint32_t hhs_p219_paradox_gcd(uint32_t a, uint32_t b) {
    while (b != 0U) {
        const uint32_t t = a % b;
        a = b;
        b = t;
    }
    return a == 0U ? 1U : a;
}

static HHSExactPass219ParadoxStatusV1 hhs_p219_paradox_normalize(
    HHSExactPass219RationalV1 in,
    HHSExactPass219RationalV1 *out) {
    uint32_t g;
    if (out == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    if (in.denominator == 0U) {
        return HHS_EXACT_PASS219_PARADOX_DENOMINATOR_ZERO;
    }
    if (in.numerator > HHS_EXACT_PASS219_PARADOX_MAX_COMPONENT ||
        in.denominator > HHS_EXACT_PASS219_PARADOX_MAX_COMPONENT ||
        in.numerator > in.denominator) {
        return HHS_EXACT_PASS219_PARADOX_RANGE_ERROR;
    }
    g = hhs_p219_paradox_gcd(in.numerator, in.denominator);
    out->numerator = in.numerator / g;
    out->denominator = in.denominator / g;
    return HHS_EXACT_PASS219_PARADOX_OK;
}

static int hhs_p219_paradox_equal(
    HHSExactPass219RationalV1 a,
    HHSExactPass219RationalV1 b) {
    return (uint64_t)a.numerator * (uint64_t)b.denominator ==
           (uint64_t)b.numerator * (uint64_t)a.denominator;
}

static HHSExactPass219ParadoxStatusV1 hhs_p219_paradox_map(
    const HHSExactPass219ParadoxProblemV1 *problem,
    HHSExactPass219RationalV1 value,
    HHSExactPass219RationalV1 *out) {
    uint32_t count = 0U;
    uint32_t i;
    HHSExactPass219RationalV1 normalized;
    HHSExactPass219ParadoxStatusV1 status;

    if (problem == NULL || out == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    status = hhs_p219_paradox_normalize(value, &normalized);
    if (status != HHS_EXACT_PASS219_PARADOX_OK) {
        return status;
    }
    for (i = 0U; i < (uint32_t)problem->option_count; ++i) {
        HHSExactPass219RationalV1 option;
        status = hhs_p219_paradox_normalize(problem->options[i], &option);
        if (status != HHS_EXACT_PASS219_PARADOX_OK) {
            return status;
        }
        if (hhs_p219_paradox_equal(option, normalized)) {
            ++count;
        }
    }
    out->numerator = count;
    out->denominator = problem->option_count;
    return hhs_p219_paradox_normalize(*out, out);
}

static HHSExactPass219ParadoxStatusV1 hhs_p219_paradox_problem_validate(
    const HHSExactPass219ParadoxProblemV1 *problem) {
    uint32_t i;
    const uint32_t expected_bound =
        problem == NULL ? 0U : (uint32_t)problem->option_count + 2U;

    if (problem == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    if (problem->version != HHS_EXACT_PASS219_PARADOX_VERSION ||
        problem->option_count < 2U ||
        problem->option_count > HHS_EXACT_PASS219_PARADOX_MAX_OPTIONS ||
        problem->seed_option_index >= problem->option_count ||
        problem->permit_meta_closure > 1U ||
        problem->promote_meta_zero_to_object_correct > 1U) {
        return HHS_EXACT_PASS219_PARADOX_RANGE_ERROR;
    }
    if ((uint32_t)problem->declared_visit_bound != expected_bound ||
        expected_bound > HHS_EXACT_PASS219_PARADOX_MAX_TRAJECTORY) {
        return HHS_EXACT_PASS219_PARADOX_BOUND_ERROR;
    }
    if (problem->promote_meta_zero_to_object_correct != 0U) {
        return HHS_EXACT_PASS219_PARADOX_TYPE_LEVEL_CONFLATION;
    }
    for (i = 0U; i < (uint32_t)problem->option_count; ++i) {
        HHSExactPass219RationalV1 tmp;
        const HHSExactPass219ParadoxStatusV1 status =
            hhs_p219_paradox_normalize(problem->options[i], &tmp);
        if (status != HHS_EXACT_PASS219_PARADOX_OK) {
            return status;
        }
    }
    return HHS_EXACT_PASS219_PARADOX_OK;
}

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_paradox_analyze(
    const HHSExactPass219ParadoxProblemV1 *problem,
    HHSExactPass219ParadoxWitnessV1 *out) {
    uint32_t i;
    uint32_t valid_count = 0U;
    uint32_t trajectory_count = 1U;
    HHSExactPass219RationalV1 current;
    HHSExactPass219ParadoxStatusV1 status;

    if (problem == NULL || out == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    status = hhs_p219_paradox_problem_validate(problem);
    if (status != HHS_EXACT_PASS219_PARADOX_OK) {
        return status;
    }

    memset(out, 0, sizeof(*out));
    out->version = HHS_EXACT_PASS219_PARADOX_VERSION;
    out->option_count = problem->option_count;
    out->seed_option_index = problem->seed_option_index;
    out->finite_visit_bound = problem->declared_visit_bound;
    out->typed_level_separation_preserved = 1U;
    out->ordered_trajectory_preserved = 1U;
    out->canonical_mutation_authority = 0U;
    out->canonical_hash72_authority = 0U;
    out->canonical_persistence_authority = 0U;
    out->floating_point_authority = 0U;

    for (i = 0U; i < (uint32_t)problem->option_count; ++i) {
        HHSExactPass219RationalV1 option;
        HHSExactPass219RationalV1 mapped;
        status = hhs_p219_paradox_normalize(problem->options[i], &option);
        if (status != HHS_EXACT_PASS219_PARADOX_OK) {
            return status;
        }
        status = hhs_p219_paradox_map(problem, option, &mapped);
        if (status != HHS_EXACT_PASS219_PARADOX_OK) {
            return status;
        }
        if (hhs_p219_paradox_equal(option, mapped)) {
            ++valid_count;
            if (i == (uint32_t)problem->seed_option_index) {
                out->seed_option_object_correct = 1U;
            }
        }
    }

    out->object_valid_option_count = (uint8_t)valid_count;
    out->object_has_fixed_point = valid_count > 0U ? 1U : 0U;
    out->seed_candidate_trinary =
        out->seed_option_object_correct != 0U ? ((int8_t)1) : ((int8_t)-1);

    status = hhs_p219_paradox_normalize(
        problem->options[problem->seed_option_index],
        &current);
    if (status != HHS_EXACT_PASS219_PARADOX_OK) {
        return status;
    }
    out->trajectory[0] = current;

    while (trajectory_count < (uint32_t)problem->declared_visit_bound) {
        HHSExactPass219RationalV1 next;
        uint32_t match = trajectory_count;

        status = hhs_p219_paradox_map(problem, current, &next);
        if (status != HHS_EXACT_PASS219_PARADOX_OK) {
            return status;
        }

        for (i = 0U; i < trajectory_count; ++i) {
            if (hhs_p219_paradox_equal(out->trajectory[i], next)) {
                match = i;
                break;
            }
        }

        out->trajectory[trajectory_count] = next;
        ++trajectory_count;

        if (match < trajectory_count - 1U) {
            out->cycle_detected = 1U;
            out->preperiod = (uint8_t)match;
            out->period = (uint8_t)((trajectory_count - 1U) - match);
            if (out->period == 1U &&
                hhs_p219_paradox_equal(
                    out->trajectory[trajectory_count - 2U],
                    out->trajectory[trajectory_count - 1U])) {
                out->fixed_point_reached = 1U;
            }
            break;
        }
        current = next;
    }

    out->trajectory_count = (uint8_t)trajectory_count;
    if (out->cycle_detected == 0U) {
        return HHS_EXACT_PASS219_PARADOX_NO_FINITE_CLOSURE;
    }

    out->cycle_motion_trinary =
        out->period > 1U ? ((int8_t)1) : ((int8_t)0);

    if (problem->permit_meta_closure != 0U && valid_count == 0U) {
        out->meta_empty_valid_set = 1U;
        out->meta_probability_zero = 1U;
        out->meta_probability.numerator = 0U;
        out->meta_probability.denominator = 1U;
        out->meta_closure_trinary = ((int8_t)0);
    } else {
        out->meta_probability.numerator = 0U;
        out->meta_probability.denominator = 1U;
        out->meta_closure_trinary =
            valid_count == 0U ? ((int8_t)-1) : ((int8_t)1);
    }

    out->bounded_closure = 1U;
    return HHS_EXACT_PASS219_PARADOX_OK;
}

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_paradox_witness_validate(
    const HHSExactPass219ParadoxProblemV1 *problem,
    const HHSExactPass219ParadoxWitnessV1 *witness) {
    HHSExactPass219ParadoxWitnessV1 expected;
    HHSExactPass219ParadoxStatusV1 status;
    uint32_t i;

    if (problem == NULL || witness == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    status = hhs_exact_pass219_paradox_analyze(problem, &expected);
    if (status != HHS_EXACT_PASS219_PARADOX_OK) {
        return status;
    }
    if (witness->version != expected.version ||
        witness->option_count != expected.option_count ||
        witness->seed_option_index != expected.seed_option_index ||
        witness->object_has_fixed_point != expected.object_has_fixed_point ||
        witness->object_valid_option_count != expected.object_valid_option_count ||
        witness->seed_option_object_correct != expected.seed_option_object_correct ||
        witness->cycle_detected != expected.cycle_detected ||
        witness->fixed_point_reached != expected.fixed_point_reached ||
        witness->preperiod != expected.preperiod ||
        witness->period != expected.period ||
        witness->trajectory_count != expected.trajectory_count ||
        witness->finite_visit_bound != expected.finite_visit_bound ||
        witness->meta_empty_valid_set != expected.meta_empty_valid_set ||
        witness->meta_probability_zero != expected.meta_probability_zero ||
        witness->seed_candidate_trinary != expected.seed_candidate_trinary ||
        witness->cycle_motion_trinary != expected.cycle_motion_trinary ||
        witness->meta_closure_trinary != expected.meta_closure_trinary ||
        witness->typed_level_separation_preserved != 1U ||
        witness->bounded_closure != 1U ||
        witness->ordered_trajectory_preserved != 1U ||
        witness->canonical_mutation_authority != 0U ||
        witness->canonical_hash72_authority != 0U ||
        witness->canonical_persistence_authority != 0U ||
        witness->floating_point_authority != 0U ||
        !hhs_p219_paradox_equal(witness->meta_probability, expected.meta_probability)) {
        return HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR;
    }
    for (i = 0U; i < (uint32_t)expected.trajectory_count; ++i) {
        if (!hhs_p219_paradox_equal(
                witness->trajectory[i],
                expected.trajectory[i])) {
            return HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR;
        }
    }
    return HHS_EXACT_PASS219_PARADOX_OK;
}

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_h36_closure_identity(
    HHSExactPass219H36ClosureWitnessV1 *out) {
    if (out == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    memset(out, 0, sizeof(*out));
    out->version = HHS_EXACT_PASS219_PARADOX_VERSION;
    out->a2 = 1U;
    out->b2 = 2U;
    out->c2 = 3U;
    out->b4 = out->b2 * out->b2;
    out->b6 = out->b4 * out->b2;
    out->c4 = out->c2 * out->c2;
    out->denominator = out->c2 - out->a2;
    if (out->denominator == 0U) {
        return HHS_EXACT_PASS219_PARADOX_DENOMINATOR_ZERO;
    }
    out->lhs_numerator = out->b6 * out->c4;
    out->lhs_denominator = out->denominator;
    if (out->lhs_numerator % out->lhs_denominator != 0U) {
        return HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR;
    }
    out->lhs_value = out->lhs_numerator / out->lhs_denominator;
    out->rhs_value =
        (out->a2 + out->b2) * (out->a2 + out->b2) * out->b4;
    out->h36_value = HHS_EXACT_PASS219_PARADOX_H36_VALUE;
    out->manifold_base = HHS_EXACT_PASS219_PARADOX_MANIFOLD_BASE;
    out->manifold_power = HHS_EXACT_PASS219_PARADOX_MANIFOLD_POWER;
    out->manifold_cardinality =
        HHS_EXACT_PASS219_PARADOX_MANIFOLD_CARDINALITY;
    out->identity_equal =
        out->lhs_value == out->rhs_value &&
        out->lhs_value == out->h36_value ? 1U : 0U;
    out->manifold_cardinality_equal =
        UINT64_C(5184) * UINT64_C(5184) *
        UINT64_C(5184) * UINT64_C(5184) ==
        out->manifold_cardinality ? 1U : 0U;
    out->canonical_mutation_authority = 0U;
    out->canonical_hash72_authority = 0U;
    out->canonical_persistence_authority = 0U;
    out->floating_point_authority = 0U;
    return out->identity_equal != 0U &&
           out->manifold_cardinality_equal != 0U
        ? HHS_EXACT_PASS219_PARADOX_OK
        : HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR;
}

HHSExactPass219ParadoxStatusV1
hhs_exact_pass219_h36_closure_identity_validate(
    const HHSExactPass219H36ClosureWitnessV1 *witness) {
    HHSExactPass219H36ClosureWitnessV1 expected;
    const HHSExactPass219ParadoxStatusV1 status =
        hhs_exact_pass219_h36_closure_identity(&expected);
    if (witness == NULL) {
        return HHS_EXACT_PASS219_PARADOX_NULL;
    }
    if (status != HHS_EXACT_PASS219_PARADOX_OK) {
        return status;
    }
    if (witness->version != expected.version ||
        witness->a2 != expected.a2 ||
        witness->b2 != expected.b2 ||
        witness->c2 != expected.c2 ||
        witness->b4 != expected.b4 ||
        witness->b6 != expected.b6 ||
        witness->c4 != expected.c4 ||
        witness->denominator != expected.denominator ||
        witness->lhs_numerator != expected.lhs_numerator ||
        witness->lhs_denominator != expected.lhs_denominator ||
        witness->lhs_value != expected.lhs_value ||
        witness->rhs_value != expected.rhs_value ||
        witness->h36_value != expected.h36_value ||
        witness->manifold_base != expected.manifold_base ||
        witness->manifold_power != expected.manifold_power ||
        witness->manifold_cardinality != expected.manifold_cardinality ||
        witness->identity_equal != 1U ||
        witness->manifold_cardinality_equal != 1U ||
        witness->canonical_mutation_authority != 0U ||
        witness->canonical_hash72_authority != 0U ||
        witness->canonical_persistence_authority != 0U ||
        witness->floating_point_authority != 0U) {
        return HHS_EXACT_PASS219_PARADOX_WITNESS_ERROR;
    }
    return HHS_EXACT_PASS219_PARADOX_OK;
}

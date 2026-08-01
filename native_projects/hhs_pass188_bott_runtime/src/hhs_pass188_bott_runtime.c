#include "hhs_pass188_bott_runtime.h"

#include <stddef.h>

static const char *const HHS188_TAGS[8] = {
    "x", "y", "z", "w", "xy", "yx", "zw", "wz"
};

const char *hhs188_ordered_tag(uint8_t basis8) {
    return basis8 < 8U ? HHS188_TAGS[basis8] : "INVALID";
}

uint8_t hhs188_bott_step(uint8_t basis8) {
    uint32_t value = (uint32_t)basis8 & UINT32_C(7);
    uint32_t mismatch = (((value >> 2U) ^ (value >> 1U)) & UINT32_C(1));
    uint32_t mask = mismatch - UINT32_C(1);
    return (uint8_t)(((value ^ UINT32_C(1)) & mask) & UINT32_C(7));
}

#if !defined(__x86_64__)
uint8_t hhs188_bott_step_x86_64(uint8_t basis8) {
    return hhs188_bott_step(basis8);
}
#endif

HHS188Status hhs188_decode_projected(uint32_t projected_address, HHS188Coordinate *out) {
    uint32_t state;
    uint32_t operation;
    uint32_t q144;

    if (out == NULL) {
        return HHS188_STATUS_NULL;
    }
    if (projected_address >= HHS188_HYDRATED_STATES) {
        return HHS188_STATUS_RANGE;
    }

    state = projected_address / HHS188_G243_CONTROLS;
    operation = state % HHS188_OPERATIONS_PER_CELL;
    q144 = state % HHS188_Q144_STATES;

    out->projected_address = projected_address;
    out->permanent_state = state;
    out->g243 = (uint16_t)(projected_address % HHS188_G243_CONTROLS);
    out->vm81_cell = (uint8_t)(state / HHS188_OPERATIONS_PER_CELL);
    out->operation64 = (uint8_t)operation;
    out->operation_class8 = (uint8_t)(operation >> 3U);
    out->basis8 = (uint8_t)(operation & UINT32_C(7));
    out->layer36 = (uint8_t)(state / HHS188_Q144_STATES);
    out->q144 = (uint8_t)q144;
    out->row12 = (uint8_t)(q144 / UINT32_C(12));
    out->column12 = (uint8_t)(q144 % UINT32_C(12));
    out->pair72 = (uint8_t)(q144 / UINT32_C(72));
    out->index72 = (uint8_t)(q144 % UINT32_C(72));
    out->factorial_admitted = (uint8_t)(state < HHS188_FACTORIAL_STATES);
    out->closure_q144 = (uint8_t)(state >= HHS188_FACTORIAL_STATES);
    return HHS188_STATUS_OK;
}

HHS188Status hhs188_transition_projected(uint32_t projected_address, HHS188Transition *out) {
    uint8_t next_basis;
    uint8_t next_operation;
    uint32_t next_state;
    uint32_t next_projected;
    HHS188Status status;

    if (out == NULL) {
        return HHS188_STATUS_NULL;
    }
    status = hhs188_decode_projected(projected_address, &out->input);
    if (status != HHS188_STATUS_OK) {
        return status;
    }

    next_basis = hhs188_bott_step(out->input.basis8);
    next_operation = (uint8_t)((out->input.operation_class8 << 3U) | next_basis);
    next_state = (uint32_t)out->input.vm81_cell * HHS188_OPERATIONS_PER_CELL + (uint32_t)next_operation;
    next_projected = next_state * HHS188_G243_CONTROLS + (uint32_t)out->input.g243;

    status = hhs188_decode_projected(next_projected, &out->output);
    if (status != HHS188_STATUS_OK) {
        return status;
    }
    if (out->output.g243 != out->input.g243 ||
        out->output.vm81_cell != out->input.vm81_cell ||
        out->output.operation_class8 != out->input.operation_class8 ||
        out->output.basis8 != next_basis) {
        return HHS188_STATUS_COORDINATE_DRIFT;
    }

    out->classification =
        (out->input.basis8 == 0U || out->input.basis8 == 1U ||
         out->input.basis8 == 6U || out->input.basis8 == 7U)
            ? HHS188_PERIOD_TWO_ACTIVE
            : HHS188_ASYMMETRIC_DRIFT_COLLAPSE;
    out->ordered_input_tag = hhs188_ordered_tag(out->input.basis8);
    out->ordered_output_tag = hhs188_ordered_tag(out->output.basis8);
    return HHS188_STATUS_OK;
}

HHS188Status hhs188_replay_transition(const HHS188Transition *receipt) {
    HHS188Transition replay;
    HHS188Status status;

    if (receipt == NULL) {
        return HHS188_STATUS_NULL;
    }
    status = hhs188_transition_projected(receipt->input.projected_address, &replay);
    if (status != HHS188_STATUS_OK) {
        return status;
    }
    if (replay.output.projected_address != receipt->output.projected_address ||
        replay.input.basis8 != receipt->input.basis8 ||
        replay.output.basis8 != receipt->output.basis8 ||
        replay.classification != receipt->classification) {
        return HHS188_STATUS_REPLAY_MISMATCH;
    }
    return HHS188_STATUS_OK;
}

HHS188Status hhs188_hydrate(HHS188HydrationSummary *out) {
    uint32_t projected;
    uint64_t checksum = UINT64_C(1469598103934665603);

    if (out == NULL) {
        return HHS188_STATUS_NULL;
    }
    out->hydrated_states = 0;
    out->active_period_two_states = 0;
    out->asymmetric_collapse_states = 0;
    out->gear_preserved_states = 0;
    out->coordinate_drift_states = 0;
    out->deterministic_checksum = 0;

    for (projected = 0; projected < HHS188_HYDRATED_STATES; ++projected) {
        HHS188Transition transition;
        HHS188Status status = hhs188_transition_projected(projected, &transition);
        if (status == HHS188_STATUS_COORDINATE_DRIFT) {
            ++out->coordinate_drift_states;
            continue;
        }
        if (status != HHS188_STATUS_OK) {
            return status;
        }
        ++out->hydrated_states;
        if (transition.classification == HHS188_PERIOD_TWO_ACTIVE) {
            ++out->active_period_two_states;
        } else {
            ++out->asymmetric_collapse_states;
        }
        if (transition.input.g243 == transition.output.g243) {
            ++out->gear_preserved_states;
        }
        checksum ^= (uint64_t)transition.output.projected_address +
                    ((uint64_t)transition.input.basis8 << 32U) +
                    (uint64_t)transition.output.basis8;
        checksum *= UINT64_C(1099511628211);
    }
    out->deterministic_checksum = checksum;
    return out->coordinate_drift_states == 0U ? HHS188_STATUS_OK : HHS188_STATUS_COORDINATE_DRIFT;
}

const char *hhs188_status_name(HHS188Status status) {
    switch (status) {
        case HHS188_STATUS_OK: return "HHS188_STATUS_OK";
        case HHS188_STATUS_NULL: return "HHS188_STATUS_NULL";
        case HHS188_STATUS_RANGE: return "HHS188_STATUS_RANGE";
        case HHS188_STATUS_COORDINATE_DRIFT: return "HHS188_STATUS_COORDINATE_DRIFT";
        case HHS188_STATUS_REPLAY_MISMATCH: return "HHS188_STATUS_REPLAY_MISMATCH";
        default: return "HHS188_STATUS_UNKNOWN";
    }
}

const char *hhs188_classification_name(HHS188TransitionClass classification) {
    switch (classification) {
        case HHS188_PERIOD_TWO_ACTIVE: return "HHS_P188_PERIOD_TWO_ACTIVE";
        case HHS188_ASYMMETRIC_DRIFT_COLLAPSE: return "HHS_P188_ASYMMETRIC_DRIFT_COLLAPSE";
        default: return "HHS_P188_UNKNOWN_TRANSITION";
    }
}

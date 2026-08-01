#ifndef HHS_PASS188_BOTT_RUNTIME_H
#define HHS_PASS188_BOTT_RUNTIME_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS188_VM81_CELLS UINT32_C(81)
#define HHS188_OPERATIONS_PER_CELL UINT32_C(64)
#define HHS188_PERMANENT_STATES UINT32_C(5184)
#define HHS188_G243_CONTROLS UINT32_C(243)
#define HHS188_HYDRATED_STATES UINT32_C(1259712)
#define HHS188_Q144_STATES UINT32_C(144)
#define HHS188_FACTORIAL_STATES UINT32_C(5040)
#define HHS188_OUTER_ENVELOPE UINT32_C(1259713)

#define HHS188_CHECKSUM_EXPECTED UINT64_C(0x11e3bbf0214751c3)

typedef enum HHS188Status {
    HHS188_STATUS_OK = 0,
    HHS188_STATUS_NULL = 1,
    HHS188_STATUS_RANGE = 2,
    HHS188_STATUS_COORDINATE_DRIFT = 3,
    HHS188_STATUS_REPLAY_MISMATCH = 4
} HHS188Status;

typedef enum HHS188TransitionClass {
    HHS188_PERIOD_TWO_ACTIVE = 1,
    HHS188_ASYMMETRIC_DRIFT_COLLAPSE = 2
} HHS188TransitionClass;

typedef struct HHS188Coordinate {
    uint32_t projected_address;
    uint32_t permanent_state;
    uint16_t g243;
    uint8_t vm81_cell;
    uint8_t operation64;
    uint8_t operation_class8;
    uint8_t basis8;
    uint8_t layer36;
    uint8_t q144;
    uint8_t row12;
    uint8_t column12;
    uint8_t pair72;
    uint8_t index72;
    uint8_t factorial_admitted;
    uint8_t closure_q144;
} HHS188Coordinate;

typedef struct HHS188Transition {
    HHS188Coordinate input;
    HHS188Coordinate output;
    HHS188TransitionClass classification;
    const char *ordered_input_tag;
    const char *ordered_output_tag;
} HHS188Transition;

typedef struct HHS188HydrationSummary {
    uint64_t hydrated_states;
    uint64_t active_period_two_states;
    uint64_t asymmetric_collapse_states;
    uint64_t gear_preserved_states;
    uint64_t coordinate_drift_states;
    uint64_t deterministic_checksum;
} HHS188HydrationSummary;

const char *hhs188_ordered_tag(uint8_t basis8);
uint8_t hhs188_bott_step(uint8_t basis8);
uint8_t hhs188_bott_step_x86_64(uint8_t basis8);
HHS188Status hhs188_decode_projected(uint32_t projected_address, HHS188Coordinate *out);
HHS188Status hhs188_transition_projected(uint32_t projected_address, HHS188Transition *out);
HHS188Status hhs188_replay_transition(const HHS188Transition *receipt);
HHS188Status hhs188_hydrate(HHS188HydrationSummary *out);
const char *hhs188_status_name(HHS188Status status);
const char *hhs188_classification_name(HHS188TransitionClass classification);

#ifdef __cplusplus
}
#endif

#endif

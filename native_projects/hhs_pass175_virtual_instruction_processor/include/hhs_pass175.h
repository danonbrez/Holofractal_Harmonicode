#ifndef HHS_PASS175_H
#define HHS_PASS175_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS175_VM81_CELLS 81u
#define HHS175_OPERATIONS_PER_CELL 64u
#define HHS175_INSTRUCTION_COUNT 5184u
#define HHS175_CONTROL_COUNT 243u
#define HHS175_PROJECTED_COUNT 1259712u
#define HHS175_CONTROL_TRITS 5u

typedef struct HHS175Address {
    uint32_t state;
    uint16_t cell;
    uint8_t operation;
    uint8_t phase;
} HHS175Address;

typedef struct HHS175Candidate {
    uint64_t epoch;
    uint32_t sequence;
    uint16_t thread_id;
    uint16_t reserved;
    uint32_t state;
    uint16_t control;
    uint16_t write_cell;
    int8_t write_value;
    uint8_t phase;
    uint16_t reserved2;
    uint64_t identity;
} HHS175Candidate;

int hhs175_address_encode(uint32_t cell, uint32_t operation, uint32_t *state_out);
int hhs175_address_decode(uint32_t state, HHS175Address *address_out);
int hhs175_projected_encode(uint32_t state, uint32_t control, uint32_t *projected_out);
int hhs175_projected_decode(uint32_t projected, uint32_t *state_out, uint32_t *control_out);
int hhs175_control_encode(const uint8_t trits[HHS175_CONTROL_TRITS], uint16_t *control_out);
int hhs175_control_decode(uint32_t control, uint8_t trits_out[HHS175_CONTROL_TRITS]);
uint8_t hhs175_phase_for_operation(uint32_t operation);
int hhs175_candidate_conflict(const uint8_t left_read[HHS175_VM81_CELLS],
                              const uint8_t left_write[HHS175_VM81_CELLS],
                              const uint8_t right_read[HHS175_VM81_CELLS],
                              const uint8_t right_write[HHS175_VM81_CELLS]);
uint64_t hhs175_candidate_identity(uint64_t epoch, uint32_t sequence, uint32_t thread_id,
                                   uint32_t state, uint32_t control, uint32_t write_cell,
                                   int32_t write_value);
int hhs175_candidate_build(uint64_t epoch, uint32_t sequence, uint32_t thread_id,
                           uint32_t state, uint32_t control, uint32_t write_cell,
                           int32_t write_value, HHS175Candidate *candidate_out);
uint64_t hhs175_singular_commit_root(uint64_t prior_root,
                                     const HHS175Candidate *candidates,
                                     size_t candidate_count);

#ifdef __cplusplus
}
#endif

#endif

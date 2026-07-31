#ifndef VM81_INVARIANT_KERNEL_H
#define VM81_INVARIANT_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS175_KERNEL_ABI_VERSION UINT32_C(0x00017501)
#define HHS175_KERNEL_STATE_COUNT 5184u
#define HHS175_KERNEL_VM81_CELLS 81u
#define HHS175_KERNEL_OPERATIONS_PER_CELL 64u
#define HHS175_KERNEL_CONTROL_COUNT 243u
#define HHS175_KERNEL_CONTROL_TRITS 5u
#define HHS175_KERNEL_MAX_BATCH 256u
#define HHS175_KERNEL_BITSET_WORDS 2u

typedef enum HHS175KernelStatus {
    HHS175_KERNEL_OK = 0,
    HHS175_KERNEL_INVALID_ARGUMENT = -1,
    HHS175_KERNEL_ADDRESS_RANGE = -2,
    HHS175_KERNEL_CONTROL_RANGE = -3,
    HHS175_KERNEL_CONFLICT = -4,
    HHS175_KERNEL_ORDER = -5,
    HHS175_KERNEL_VM81_REJECTED = -6,
    HHS175_KERNEL_EXACT_IDENTITY = -7
} HHS175KernelStatus;

typedef struct HHS175KernelAddress {
    uint32_t state;
    uint16_t cell;
    uint8_t operation;
    uint8_t phase;
} HHS175KernelAddress;

typedef struct HHS175KernelBitset {
    uint64_t words[HHS175_KERNEL_BITSET_WORDS];
} HHS175KernelBitset;

typedef struct HHS175KernelCandidateInput {
    uint64_t epoch;
    uint32_t sequence;
    uint16_t thread_id;
    uint16_t control;
    uint32_t state;
    uint16_t write_cell;
    int8_t write_value;
    uint8_t reserved;
    HHS175KernelBitset read_set;
    HHS175KernelBitset write_set;
    uint64_t instruction_identity;
} HHS175KernelCandidateInput;

typedef struct HHS175KernelCandidate {
    HHS175KernelCandidateInput input;
    uint32_t projected_address;
    uint8_t phase;
    uint8_t control_trits[HHS175_KERNEL_CONTROL_TRITS];
    uint16_t reserved;
    uint64_t candidate_identity;
} HHS175KernelCandidate;

typedef struct HHS175KernelState {
    int8_t cells[HHS175_KERNEL_VM81_CELLS];
    uint64_t epoch;
    uint64_t ordered_commit_root;
    uint64_t admitted_candidates;
    uint64_t rejected_candidates;
} HHS175KernelState;

typedef int (*HHS175VM81AdmitFn)(
    void *context,
    const HHS175KernelCandidate *ordered_candidates,
    size_t candidate_count,
    const HHS175KernelState *predecessor,
    HHS175KernelState *successor,
    uint64_t *hash72_receipt_token
);

uint32_t hhs175_kernel_abi_version(void);
const uint8_t *hhs175_kernel_scalar_lo(size_t *length_out);
const uint8_t *hhs175_kernel_scalar_hi(size_t *length_out);

int hhs175_kernel_address_encode(uint32_t cell, uint32_t operation, uint32_t *state_out);
int hhs175_kernel_address_decode(uint32_t state, HHS175KernelAddress *address_out);
int hhs175_kernel_projected_encode(uint32_t state, uint32_t control, uint32_t *projected_out);
int hhs175_kernel_projected_decode(uint32_t projected, uint32_t *state_out, uint32_t *control_out);
int hhs175_kernel_control_encode(const uint8_t trits[HHS175_KERNEL_CONTROL_TRITS], uint16_t *control_out);
int hhs175_kernel_control_decode(uint32_t control, uint8_t trits_out[HHS175_KERNEL_CONTROL_TRITS]);

void hhs175_kernel_bitset_clear(HHS175KernelBitset *set);
int hhs175_kernel_bitset_add(HHS175KernelBitset *set, uint32_t cell);
int hhs175_kernel_bitset_intersects(const HHS175KernelBitset *left, const HHS175KernelBitset *right);
int hhs175_kernel_candidate_conflict(
    const HHS175KernelCandidateInput *left,
    const HHS175KernelCandidateInput *right
);

int hhs175_kernel_prepare_candidates(
    const HHS175KernelCandidateInput *inputs,
    size_t input_count,
    HHS175KernelCandidate *candidates_out
);

int hhs175_kernel_sort_candidates(
    HHS175KernelCandidate *candidates,
    size_t candidate_count
);

void hhs175_kernel_state_reset(HHS175KernelState *state);

int hhs175_kernel_commit_candidates(
    const HHS175KernelCandidate *ordered_candidates,
    size_t candidate_count,
    HHS175KernelState *canonical_state,
    HHS175VM81AdmitFn vm81_admit,
    void *vm81_context,
    uint64_t *hash72_receipt_token_out
);

#ifdef __cplusplus
}
#endif
#endif

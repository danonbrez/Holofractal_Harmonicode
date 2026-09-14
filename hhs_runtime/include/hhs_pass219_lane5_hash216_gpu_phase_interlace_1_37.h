#ifndef HHS_PASS219_LANE5_HASH216_GPU_PHASE_INTERLACE_1_37_H
#define HHS_PASS219_LANE5_HASH216_GPU_PHASE_INTERLACE_1_37_H

#include "hhs_pass219_delta_reciprocal_constructor_1_36.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_VERSION UINT32_C(0x00010025)
#define HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_CYCLE UINT32_C(20020)
#define HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_QUARTER UINT32_C(5005)
#define HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES UINT32_C(4)
#define HHS_EXACT_PASS219_LANE5_PHASE_STATES UINT32_C(4)
#define HHS_EXACT_PASS219_LANE5_PRIME_MATRIX_ENTRIES UINT32_C(16)

typedef struct HHSExactPass219Lane5PhaseInterlaceAuthorityV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t full_cycle;
    uint32_t quarter_cycle;
    uint32_t lane_count;
    uint32_t phase_states_per_lane;
    uint32_t base_periods[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES];
    uint8_t fixed_full_cycle_20020;
    uint8_t quarter_sync_5005;
    uint8_t prime_matrix_fingerprint_routing;
    uint8_t consecutive_prime_cells_supported;
    uint8_t validated_hash216_read_only;
    uint8_t hash216_three_hash72_vector_search;
    uint8_t pass205_continuation_hash216_bound;
    uint8_t pass207_gpu_vector_search_bound;
    uint8_t four_lane_parallel_encoding_search;
    uint8_t gpu_candidate_only;
    uint8_t exact_cpu_vm81_replay_required;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t requires_lane5_mediation;
    uint8_t requires_signed_environmental_vm81_admission;
    uint8_t floating_point_canonical_authority;
    uint8_t reserved0[6];
} HHSExactPass219Lane5PhaseInterlaceAuthorityV1;

typedef struct HHSExactPass219Lane5PhaseAddressV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t tick_mod_cycle;
    uint32_t quarter_index;
    uint32_t residues[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES];
    uint32_t phases[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES];
    uint64_t address_signature64;
} HHSExactPass219Lane5PhaseAddressV1;

typedef struct HHSExactPass219Lane5PrimeMatrixV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t cell[HHS_EXACT_PASS219_LANE5_PRIME_MATRIX_ENTRIES];
    uint32_t offset[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES];
} HHSExactPass219Lane5PrimeMatrixV1;

typedef struct HHSExactPass219Lane5PrimeRouteReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t tick_mod_cycle;
    uint32_t routed_slot[HHS_EXACT_PASS219_LANE5_PHASE_INTERLACE_LANES];
    uint64_t matrix_signature64;
    uint64_t route_signature64;
    uint8_t prime_cells_validated;
    uint8_t upper_triangular;
    uint8_t invertible_mod_cycle;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t requires_exact_cpu_vm81_replay;
} HHSExactPass219Lane5PrimeRouteReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_phase_interlace_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_interlace_authority(
    HHSExactPass219Lane5PhaseInterlaceAuthorityV1 *out_authority
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_phase_address(
    uint64_t tick,
    HHSExactPass219Lane5PhaseAddressV1 *out_address
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_prime_route(
    uint64_t tick,
    const HHSExactPass219Lane5PrimeMatrixV1 *matrix,
    HHSExactPass219Lane5PrimeRouteReceiptV1 *out_receipt
);

#ifdef __cplusplus
}
#endif

#endif

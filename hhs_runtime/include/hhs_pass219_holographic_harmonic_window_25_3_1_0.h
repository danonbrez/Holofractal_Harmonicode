#ifndef HHS_PASS219_HOLOGRAPHIC_HARMONIC_WINDOW_25_3_1_0_H
#define HHS_PASS219_HOLOGRAPHIC_HARMONIC_WINDOW_25_3_1_0_H

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_VERSION_PATCH 0U

#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_A2 1U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_B2 2U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_C2 3U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_D2 5U

#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_RATIO_NUMERATOR 25U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_RATIO_DENOMINATOR 3U
#define HHS_EXACT_PASS219_HOLOGRAPHIC_WINDOW_MAX_DEPTH 9U

typedef enum HHSExactPass219HolographicBranchDecisionV1 {
    HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_INVALID = 0,
    HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_THEN = 1,
    HHS_EXACT_PASS219_HOLOGRAPHIC_BRANCH_ELSE = 2
} HHSExactPass219HolographicBranchDecisionV1;

typedef struct HHSExactPass219HolographicWindowResiduesV1 {
    uint32_t struct_size;
    uint32_t version;
    int64_t t3_minus_t_numerator;
    int64_t m2_minus_m_numerator;
    uint64_t common_denominator;
    uint8_t exact_residue_witness;
    uint8_t canonical_authority_requested;
    uint8_t reserved0[6];
} HHSExactPass219HolographicWindowResiduesV1;

typedef struct HHSExactPass219HolographicWindowInvariantV1 {
    uint32_t struct_size;
    uint32_t version;

    int64_t combined_residue_numerator;
    uint64_t common_denominator;

    uint32_t ratio_numerator;
    uint32_t ratio_denominator;

    uint8_t exact_residue_witness;
    uint8_t positive_root;
    uint8_t negative_root;
    uint8_t harmonic_window_closed;
    uint8_t canonical_authority;
    uint8_t floating_point_authority;
    uint8_t singleton_vm81_authority_preserved;
    uint8_t hash72_hash216_authority_preserved;
} HHSExactPass219HolographicWindowInvariantV1;

typedef struct HHSExactPass219HolographicBranchRequestV1 {
    uint32_t struct_size;
    uint32_t version;

    HHSExactPass219HolographicWindowResiduesV1 residues;

    uint32_t layer;
    uint32_t reserved0;

    uint64_t root_window_numerator;
    uint64_t root_window_denominator;

    uint64_t phase_coordinate_numerator;
    uint64_t phase_coordinate_denominator;

    uint8_t include_upper_boundary;
    uint8_t reserved1[7];
} HHSExactPass219HolographicBranchRequestV1;

typedef struct HHSExactPass219HolographicBranchResultV1 {
    uint32_t struct_size;
    uint32_t version;

    uint32_t layer;
    uint32_t decision;

    uint64_t active_window_numerator;
    uint64_t active_window_denominator;

    uint64_t phase_coordinate_numerator;
    uint64_t phase_coordinate_denominator;

    uint8_t harmonic_window_closed;
    uint8_t inside_active_window;
    uint8_t direct_layer_addressed;
    uint8_t recursion_stack_allocated;
    uint8_t pointer_tree_traversal_required;
    uint8_t bounded_fixed_width_branch_work;
    uint8_t whole_path_depth_bounded;
    uint8_t unbounded_depth_constant_time_claim;
    uint8_t canonical_authority;
    uint8_t floating_point_authority;
    uint8_t complete_fallback_required_on_failure;
    uint8_t reserved0[5];
} HHSExactPass219HolographicBranchResultV1;

HHS_EXACT_API uint32_t
hhs_exact_pass219_holographic_harmonic_window_version(void);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_holographic_harmonic_window_invariant(
    const HHSExactPass219HolographicWindowResiduesV1 *residues,
    HHSExactPass219HolographicWindowInvariantV1 *out_invariant);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_holographic_harmonic_window_validate(void);

HHS_EXACT_API HHSExactStatus
hhs_exact_pass219_holographic_branch_evaluate(
    const HHSExactPass219HolographicBranchRequestV1 *request,
    HHSExactPass219HolographicBranchResultV1 *out_result);

#ifdef __cplusplus
}
#endif

#endif

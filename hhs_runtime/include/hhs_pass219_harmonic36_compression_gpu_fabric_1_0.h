#ifndef HHS_PASS219_HARMONIC36_COMPRESSION_GPU_FABRIC_1_0_H
#define HHS_PASS219_HARMONIC36_COMPRESSION_GPU_FABRIC_1_0_H

#include "hhs_pass219_harmonic36_hash216_rna_binding_1_0.h"
#include "hhs_pass219_inherited_pass207_1_17.h"
#include "hhs_pass219_inherited_pass208_1_16.h"
#include "hhs_pass219_inherited_pass210_1_16.h"
#include "hhs_pass192_fibonacci_compression_1_9.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_H36_CGPU_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_H36_CGPU_VERSION_MINOR 0U
#define HHS_EXACT_PASS219_H36_CGPU_VERSION_PATCH 1U

#define HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES 5184U
#define HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT 36U
#define HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH 288U
#define HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_STRIDE 144U
#define HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_BYTES     (HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT *      HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_WIDTH)

typedef struct HHSExactPass219H36CompressionWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t register_bytes;
    uint32_t snapshot_count;
    uint32_t snapshot_width;
    uint32_t snapshot_stride;
    uint32_t single_snapshot_erasure_drills;
    uint32_t fibonacci_depth;
    uint32_t fibonacci_descriptor_length;
    uint8_t vm81_boolean_expand_equal;
    uint8_t hfc_double_coverage_equal;
    uint8_t hfc_all_single_erasure_recoveries_equal;
    uint8_t fibonacci_descriptor_equal;
    uint8_t h36_roundtrip_equal;
    uint8_t exact_reconstruction_equal;
    uint8_t pass210_binding_preserved;
    uint8_t compression_path_mandatory;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36CompressionWitnessV1;

typedef struct HHSExactPass219H36GPULocalityPlanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint16_t first_word144;
    uint16_t word_count;
    uint16_t first_bit36;
    uint16_t bit_count;
    uint32_t selected_lane_count;
    uint32_t full_lane_count;
    uint32_t avoided_lane_count;
    HHSExactPass219BPhaseLocalityPlanV1 locality;
    uint8_t pass207_bound;
    uint8_t pass208_bound;
    uint8_t candidate_only;
    uint8_t exact_cpu_vm81_equality_required;
    uint8_t stable_lane_identity_required;
    uint8_t hash216_lineage_required;
    uint8_t physical_completion_order_noncanonical;
    uint8_t singleton_vm81_admission_required;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36GPULocalityPlanV1;

typedef struct HHSExactPass219H36GPUEqualityWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t realized_lane_count;
    uint8_t gpu_cpu_frame_equal;
    uint8_t h36_gpu_roundtrip_equal;
    uint8_t h36_cpu_roundtrip_equal;
    uint8_t locality_realization_equal;
    uint8_t candidate_only_preserved;
    uint8_t singleton_vm81_admission_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219H36GPUEqualityWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_h36_compression_gpu_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_boolean_expand(
    const HHSExactVM81Frame *frame,
    uint8_t out_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_boolean_contract(
    const uint8_t register_bytes[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES],
    HHSExactVM81Frame *out_frame
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hfc_snapshot_encode(
    const uint8_t register_bytes[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES],
    uint8_t *out_snapshots,
    size_t capacity
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hfc_snapshot_reconstruct(
    const uint8_t *snapshots,
    size_t snapshot_bytes,
    const uint8_t available[HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT],
    uint8_t out_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_hfc_snapshot_reconstruct_blocks(
    const uint8_t *snapshots,
    size_t snapshot_bytes,
    const uint8_t available[HHS_EXACT_PASS219_H36_HFC_SNAPSHOT_COUNT],
    uint8_t out_register[HHS_EXACT_PASS219_H36_HFC_REGISTER_BYTES]
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_compression_verify(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219InheritedPass210BindingV1 *pass210,
    HHSExactPass219H36CompressionWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_gpu_locality_plan(
    const HHSExactPass219InheritedPass207BindingV1 *pass207,
    const HHSExactPass219InheritedPass208BindingV1 *pass208,
    uint16_t first_word144,
    uint16_t word_count,
    uint16_t first_bit36,
    uint16_t bit_count,
    HHSExactPass219H36GPULocalityPlanV1 *out_plan
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_gpu_locality_lane(
    const HHSExactPass219H36GPULocalityPlanV1 *plan,
    uint32_t ordinal,
    HHSExactPass219H36FactorizationCircuitV1 *out_circuit
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_h36_gpu_candidate_verify(
    const HHSExactPass219H36GPULocalityPlanV1 *plan,
    uint32_t realized_lane_count,
    const HHSExactVM81Frame *gpu_candidate,
    const HHSExactVM81Frame *cpu_vm81_oracle,
    HHSExactPass219H36GPUEqualityWitnessV1 *out_witness
);

#ifdef __cplusplus
}
#endif
#endif

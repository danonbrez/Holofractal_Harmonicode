#ifndef HHS_PASS220_RNA_HASH72_DNA_QUDIT_PHASE_LOCK_1_0_H
#define HHS_PASS220_RNA_HASH72_DNA_QUDIT_PHASE_LOCK_1_0_H

#include "hhs_pass219_rna_vm5184_abi_1_33.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_PHASE_LOCK_VERSION UINT32_C(0x00010002)
#define HHS_EXACT_PASS220_SERIALIZED_CHARACTERS UINT32_C(5184)
#define HHS_EXACT_PASS220_HASH72_CHUNKS UINT32_C(72)
#define HHS_EXACT_PASS220_HASH72_CHUNK_CHARACTERS UINT32_C(72)
#define HHS_EXACT_PASS220_RNA_WINDOW_CHARACTERS UINT32_C(3)
#define HHS_EXACT_PASS220_RNA_WINDOWS_PER_CHUNK UINT32_C(24)
#define HHS_EXACT_PASS220_RNA_WINDOWS_TOTAL UINT32_C(1728)
#define HHS_EXACT_PASS220_QUDIT_CELLS UINT32_C(81)
#define HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS UINT32_C(64)
#define HHS_EXACT_PASS220_H36_CELLS UINT32_C(36)
#define HHS_EXACT_PASS220_H36_MAGIC_LINE UINT32_C(111)
#define HHS_EXACT_PASS220_PRECISION_DENOMINATOR UINT32_C(1000)

typedef struct HHSExactPass220PhaseLockDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t serialized_characters;
    uint32_t hash72_chunks;
    uint32_t hash72_chunk_characters;
    uint32_t rna_window_characters;
    uint32_t rna_windows_per_chunk;
    uint32_t rna_windows_total;
    uint32_t qudit_cells;
    uint32_t cell_token_characters;
    uint32_t h36_cells;
    uint32_t h36_magic_line;
    uint8_t bidirectional_rna_scan;
    uint8_t hash72_chunk_folding;
    uint8_t xyzw_digital_dna_bound;
    uint8_t vm81_qudit_bound;
    uint8_t complete_state_is_operand;
    uint8_t exact_integer_only;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[4];
} HHSExactPass220PhaseLockDescriptorV1;

typedef struct HHSExactPass220PhaseLockWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t serialized_characters;
    uint32_t hash72_chunks;
    uint32_t rna_windows_total;
    uint32_t qudit_cells;
    uint32_t forward_characters;
    uint32_t reverse_characters;
    uint64_t forward_signature64;
    uint64_t reverse_signature64;
    uint64_t state_offset_signature64;
    uint64_t scaled_palindrome_signature64[3];
    uint16_t precision_remainder_numerator[3];
    uint16_t precision_remainder_denominator[3];
    uint8_t scale_rows[3][3];
    uint8_t palindrome_rows[3][6];
    int8_t q_minus_one_phase[4];
    uint32_t q_minus_one_pair_counts[4];
    uint64_t ordered_phase_binding_signature64;
    uint8_t serialized_operand_phase_binding;
    uint8_t all_cells_cover_operation64;
    uint8_t canonical_token_layout;
    uint8_t canonical_roundtrip_shape;
    uint8_t coordinate_bijection;
    uint8_t double_reverse_exact;
    uint8_t palindromic_precision_exact;
    uint8_t ordered_phase_lock;
    uint8_t phase_locked;
    uint8_t complete_state_is_operand;
    uint8_t candidate_only;
    uint8_t canonical_vm81_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[4];
} HHSExactPass220PhaseLockWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass220_phase_lock_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_phase_lock_descriptor(
    HHSExactPass220PhaseLockDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_phase_lock_analyze(
    const char *serialized,
    size_t serialized_length,
    HHSExactPass220PhaseLockWitnessV1 *out_witness
);

#ifdef __cplusplus
}
#endif

#endif

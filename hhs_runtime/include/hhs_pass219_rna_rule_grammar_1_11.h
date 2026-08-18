#ifndef HHS_PASS219_RNA_RULE_GRAMMAR_1_11_H
#define HHS_PASS219_RNA_RULE_GRAMMAR_1_11_H

#include "hhs_pass219_rna_transcription_1_10.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_RNA_RULE_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219_RNA_RULE_VERSION_MINOR 11U
#define HHS_EXACT_PASS219_RNA_RULE_VERSION_PATCH 0U
#define HHS_EXACT_PASS219_RNA_MAX_DOMAINS 8U
#define HHS_EXACT_PASS219_RNA_MAX_RULES 16U

#define HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD UINT32_C(0x0001)
#define HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN UINT32_C(0x0002)

#define HHS_EXACT_PASS219_RNA_STATE_COMPLEMENT UINT32_C(0x0001)
#define HHS_EXACT_PASS219_RNA_STATE_BOUND UINT32_C(0x0002)
#define HHS_EXACT_PASS219_RNA_STATE_EXPOSED UINT32_C(0x0004)
#define HHS_EXACT_PASS219_RNA_STATE_FOLDED UINT32_C(0x0008)
#define HHS_EXACT_PASS219_RNA_STATE_ACTIVE UINT32_C(0x0010)
#define HHS_EXACT_PASS219_RNA_STATE_INHIBITED UINT32_C(0x0020)
#define HHS_EXACT_PASS219_RNA_STATE_CLEAVED UINT32_C(0x0040)
#define HHS_EXACT_PASS219_RNA_STATE_RELEASED UINT32_C(0x0080)

typedef enum HHSExactPass219RNARuleKind {
    HHS_EXACT_PASS219_RNA_RULE_COMPLEMENT = 1,
    HHS_EXACT_PASS219_RNA_RULE_BINDING = 2,
    HHS_EXACT_PASS219_RNA_RULE_TOEHOLD = 3,
    HHS_EXACT_PASS219_RNA_RULE_HAIRPIN = 4,
    HHS_EXACT_PASS219_RNA_RULE_ACTIVATION = 5,
    HHS_EXACT_PASS219_RNA_RULE_INHIBITION = 6,
    HHS_EXACT_PASS219_RNA_RULE_CLEAVAGE = 7,
    HHS_EXACT_PASS219_RNA_RULE_RELEASE = 8
} HHSExactPass219RNARuleKind;

typedef struct HHSExactPass219RNADomainV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t domain_id;
    uint32_t complement_domain_id;
    uint32_t role_flags;
    uint8_t phase_basis;
    uint8_t orientation;
    uint8_t reserved0[2];
} HHSExactPass219RNADomainV1;

typedef struct HHSExactPass219RNAStrandV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t strand_id;
    uint32_t domain_count;
    HHSExactPass219RNADomainV1 domains[HHS_EXACT_PASS219_RNA_MAX_DOMAINS];
} HHSExactPass219RNAStrandV1;

typedef struct HHSExactPass219RNARuleV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t rule_id;
    uint32_t kind;
    uint32_t source_domain_id;
    uint32_t target_domain_id;
} HHSExactPass219RNARuleV1;

typedef struct HHSExactPass219RNAProgramV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t program_id;
    uint32_t rule_count;
    HHSExactPass219RNARuleV1 rules[HHS_EXACT_PASS219_RNA_MAX_RULES];
} HHSExactPass219RNAProgramV1;

typedef struct HHSExactPass219RNALineageV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219NativePhaseWitnessV1 native_phase;
    HHSExactPass219TrinaryPhaseGateV1 trinary_gate;
    HHSExactPass219HydrationCoordinateV1 coordinate;
    char predecessor_hash72[HHS_EXACT_HASH72_STRLEN];
    char predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_STRLEN];
} HHSExactPass219RNALineageV1;

typedef struct HHSExactPass219RNADomainStateV1 {
    uint32_t domain_id;
    uint32_t state_flags;
} HHSExactPass219RNADomainStateV1;

typedef struct HHSExactPass219TranscriptionWitnessV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t strand_id;
    uint32_t program_id;
    uint32_t executed_rule_count;
    uint32_t last_rule_id;
    uint32_t domain_count;
    uint32_t rollback_available;
    HHSExactPass219RNALineageV1 lineage;
    HHSExactPass219RNADomainStateV1 before[HHS_EXACT_PASS219_RNA_MAX_DOMAINS];
    HHSExactPass219RNADomainStateV1 after[HHS_EXACT_PASS219_RNA_MAX_DOMAINS];
} HHSExactPass219TranscriptionWitnessV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_rna_rule_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_domain_init(
    uint32_t domain_id,
    uint32_t complement_domain_id,
    uint8_t phase_basis,
    uint8_t orientation,
    uint32_t role_flags,
    HHSExactPass219RNADomainV1 *out_domain
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_strand_init(
    uint32_t strand_id,
    HHSExactPass219RNAStrandV1 *out_strand
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_strand_add_domain(
    HHSExactPass219RNAStrandV1 *strand,
    const HHSExactPass219RNADomainV1 *domain
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_rule_init(
    uint32_t rule_id,
    uint32_t kind,
    uint32_t source_domain_id,
    uint32_t target_domain_id,
    HHSExactPass219RNARuleV1 *out_rule
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_program_init(
    uint32_t program_id,
    HHSExactPass219RNAProgramV1 *out_program
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_program_add_rule(
    HHSExactPass219RNAProgramV1 *program,
    const HHSExactPass219RNARuleV1 *rule
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_lineage_from_admission(
    const HHSExactPass219RNAAdmissionV1 *admission,
    HHSExactPass219RNALineageV1 *out_lineage
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_program_execute(
    const HHSExactPass219RNAStrandV1 *strand,
    const HHSExactPass219RNAProgramV1 *program,
    const HHSExactPass219RNALineageV1 *lineage,
    HHSExactPass219TranscriptionWitnessV1 *out_witness
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_rna_witness_rollback(
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    HHSExactPass219RNADomainStateV1 out_states[HHS_EXACT_PASS219_RNA_MAX_DOMAINS],
    uint32_t *out_domain_count
);

#ifdef __cplusplus
}
#endif

#endif

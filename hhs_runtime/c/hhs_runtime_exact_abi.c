/* Additive exact ABI aggregate through Pass 219B global zero-sum closure. */
#include "hhs_runtime_exact_abi_v1_1_base.inc"
#include "hhs_runtime_uqcel_1_8_bigint.inc"
#include "hhs_runtime_uqcel_1_8_validate.inc"
#include "hhs_runtime_uqcel_1_8_receipt.inc"
#include "hhs_pass192_fibonacci_compression_1_9.inc"
#include "hhs_pass219_rna_transcription_1_10.inc"
#include "hhs_pass219_rna_rule_grammar_1_11.inc"
#include "hhs_pass219_rna_admission_lowering_1_12.inc"
#include "hhs_pass219_rna_state_retrieval_1_13.inc"
#include "hhs_pass219_rna_execution_composer_1_14.inc"
#include "hhs_pass219_inherited_pass218_1_16.inc"
#include "hhs_pass219_inherited_pass217_1_16.inc"
#include "hhs_pass219_inherited_pass216_1_16.inc"
#include "hhs_pass219_inherited_pass215_1_16.inc"
#include "hhs_pass219_inherited_pass214_1_16.inc"
#include "hhs_pass219_inherited_pass213_1_16.inc"
#include "hhs_pass219_inherited_pass212_1_16.inc"
#include "hhs_pass219_inherited_pass211_1_16.inc"
#include "hhs_pass219_inherited_pass210_1_16.inc"
#include "hhs_pass219_inherited_pass209_1_16.inc"
#include "hhs_pass219_inherited_pass208_1_16.inc"
#include "hhs_pass219_inherited_pass207_1_17.inc"
#include "hhs_pass219_inherited_pass206_1_18.inc"
#include "hhs_pass219b_phase_quantized_hydration_1_0.inc"
#include "hhs_pass219b_universal_phase_locality_1_0.inc"

/*
 * Preserve the pre-repair I6 admission body for forensic lineage, but do not
 * expose it as the public ABI symbol.  On ELF/Mach-O the renamed body is hidden;
 * on Windows it is not marked for DLL export because it has no HHS_EXACT_API.
 */
#if defined(_WIN32)
#define hhs_exact_pass219b_global_relation_hydration_admit \
    hhs_exact_pass219b_global_relation_hydration_admit_legacy_i6_1_2
#else
#define hhs_exact_pass219b_global_relation_hydration_admit \
    __attribute__((visibility("hidden"))) \
    hhs_exact_pass219b_global_relation_hydration_admit_legacy_i6_1_2
#endif
#include "hhs_pass219b_global_zero_sum_closure_1_0.inc"
#undef hhs_exact_pass219b_global_relation_hydration_admit

/* Public ABI replacement: no VM81 copy before full composed validation. */
#include "hhs_pass219b_global_relation_hydration_admit_1_3.inc"

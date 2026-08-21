#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"

#include <string.h>

static uint32_t HHS219_I12111_TEST_MODE = 0U;

void hhs_i12111_test_provider_set_mode(uint32_t mode) {
    HHS219_I12111_TEST_MODE = mode;
}

static void hhs_i12111_fill_hash(char *out, size_t length, char symbol) {
    memset(out, (unsigned char)symbol, length);
    out[length] = '\0';
}

HHSExactStatus hhs_pass169_verify_combined_gate_authority_1_21_11(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    HHSExactPass219Pass169AuthorityProofV1 *out_proof
) {
    size_t i;
    if (provenance == NULL || out_proof == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_proof, 0, sizeof(*out_proof));
    out_proof->struct_size = (uint32_t)sizeof(*out_proof);
    out_proof->version = hhs_exact_pass219_pass169_binding_version();
    memcpy(out_proof->combined_source_sha256,
           provenance->combined_source_sha256,
           sizeof(out_proof->combined_source_sha256));
    memcpy(out_proof->pass159_provenance_root,
           provenance->global_symbol_environment_root,
           sizeof(out_proof->pass159_provenance_root));

#define COPY_STAGE(field) \
    memcpy(out_proof->field, provenance->field, sizeof(out_proof->field))
    COPY_STAGE(source_hash216);
    COPY_STAGE(tokens_hash216);
    COPY_STAGE(cst_hash216);
    COPY_STAGE(ast_hash216);
    COPY_STAGE(type_environment_hash216);
    COPY_STAGE(constraint_graph_hash216);
    COPY_STAGE(hir_hash216);
    COPY_STAGE(vmir_hash216);
#undef COPY_STAGE

    if (HHS219_I12111_TEST_MODE == 2U) {
        out_proof->vmir_hash216[0] =
            out_proof->vmir_hash216[0] == '0' ? '1' : '0';
    }

    memcpy(out_proof->canonical_global_symbol_environment_root,
           provenance->global_symbol_environment_root,
           sizeof(out_proof->canonical_global_symbol_environment_root));
    out_proof->canonical_global_symbol_environment_root[0] ^= 0xA5U;
    out_proof->gate_count = HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT;

    for (i = 0U; i < HHS_EXACT_PASS219_PASS169_BINDING_GATE_COUNT; ++i) {
        HHSExactPass219GlobalGateWitnessV1 *gate = &out_proof->gates[i];
        gate->struct_size = (uint32_t)sizeof(*gate);
        gate->version = hhs_exact_pass219_global_membrane_version();
        gate->gate_index = (uint32_t)i;
        gate->source_offset = provenance->gate_offsets[i];
        gate->boolean_result =
            (uint8_t)(HHS219_I12111_TEST_MODE == 1U && i == 2U ? 0U : 1U);
        memcpy(gate->combined_source_sha256,
               provenance->combined_source_sha256,
               sizeof(gate->combined_source_sha256));
        memcpy(gate->global_symbol_environment_root,
               out_proof->canonical_global_symbol_environment_root,
               sizeof(gate->global_symbol_environment_root));
    }

    hhs_i12111_fill_hash(
        out_proof->proof_hash216,
        HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN,
        HHS_EXACT_HASH72_ALPHABET[0]);
    hhs_i12111_fill_hash(
        out_proof->transition_hash216,
        HHS_EXACT_PASS219_PASS169_BINDING_HASH216_LEN,
        HHS_EXACT_HASH72_ALPHABET[1]);
    hhs_i12111_fill_hash(
        out_proof->receipt_hash72,
        HHS_EXACT_PASS219_PASS169_BINDING_HASH72_LEN,
        HHS_EXACT_HASH72_ALPHABET[2]);
    hhs_i12111_fill_hash(
        out_proof->replay_hash72,
        HHS_EXACT_PASS219_PASS169_BINDING_HASH72_LEN,
        HHS_EXACT_HASH72_ALPHABET[3]);

    out_proof->vm81_steps = 81U;
    out_proof->replay_vm81_steps = 81U;
    out_proof->whole_expression_constraint_graph_verified = 1U;
    out_proof->exact_vm81_admission_verified = 1U;
    out_proof->atomic_commit_verified = 1U;
    out_proof->hash72_receipt_verified =
        (uint8_t)(HHS219_I12111_TEST_MODE == 3U ? 0U : 1U);
    out_proof->hash216_proof_identity_verified = 1U;
    out_proof->deterministic_replay_verified = 1U;
    out_proof->source_reconstruction_verified = 1U;
    out_proof->shared_environment_revalidated = 1U;
    out_proof->local_symbol_shadowing_detected = 0U;
    out_proof->canonical_monolithic_proof = 1U;
    out_proof->floating_point_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

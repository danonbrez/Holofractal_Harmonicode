#include "hhs_pass219_main_authority_composition_1_21_4.h"
#include "hhs_hash216_bytes.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define HHS219_MAIN_AUTHORITY_MATERIAL_CAPACITY 8192U

static uint32_t hhs219_main_authority_version_word(void) {
    return (HHS_EXACT_PASS219_MAIN_AUTHORITY_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_MAIN_AUTHORITY_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_MAIN_AUTHORITY_VERSION_PATCH;
}

static int hhs219_main_hash216_valid(
    const char value[HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_STRLEN]
) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_MAIN_AUTHORITY_HASH216_LEN; ++i) {
        if (value[i] == '\0' || strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int hhs219_main_append(
    uint8_t *material,
    size_t capacity,
    size_t *used,
    const void *data,
    size_t length
) {
    if (material == NULL || used == NULL || data == NULL ||
        *used > capacity || length > capacity - *used)
        return 0;
    memcpy(material + *used, data, length);
    *used += length;
    return 1;
}

static int hhs219_main_append_u8(
    uint8_t *material,
    size_t capacity,
    size_t *used,
    uint8_t value
) {
    return hhs219_main_append(material, capacity, used, &value, 1U);
}

static int hhs219_main_append_u32_le(
    uint8_t *material,
    size_t capacity,
    size_t *used,
    uint32_t value
) {
    uint8_t bytes[4];
    bytes[0] = (uint8_t)(value & UINT32_C(0xFF));
    bytes[1] = (uint8_t)((value >> 8U) & UINT32_C(0xFF));
    bytes[2] = (uint8_t)((value >> 16U) & UINT32_C(0xFF));
    bytes[3] = (uint8_t)((value >> 24U) & UINT32_C(0xFF));
    return hhs219_main_append(material, capacity, used, bytes, sizeof(bytes));
}

static int hhs219_main_append_u64_le(
    uint8_t *material,
    size_t capacity,
    size_t *used,
    uint64_t value
) {
    uint8_t bytes[8];
    uint32_t i;
    for (i = 0U; i < 8U; ++i)
        bytes[i] = (uint8_t)((value >> (8U * i)) & UINT64_C(0xFF));
    return hhs219_main_append(material, capacity, used, bytes, sizeof(bytes));
}

static int hhs219_main_append_program(
    uint8_t *material,
    size_t capacity,
    size_t *used,
    const HHSExactPass219VM81ProgramV1 *program
) {
    uint32_t i;
    uint32_t edge;
    if (program == NULL)
        return 0;
    if (!hhs219_main_append_u32_le(material, capacity, used, program->instruction_count) ||
        !hhs219_main_append_u32_le(material, capacity, used, program->source_structure_thread_count) ||
        !hhs219_main_append_u32_le(material, capacity, used, program->derived_thread_count) ||
        !hhs219_main_append_u32_le(material, capacity, used, program->semantic_family_coverage_mask) ||
        !hhs219_main_append_u64_le(material, capacity, used, program->equality_edge_coverage_mask) ||
        !hhs219_main_append(material, capacity, used, program->source_sha256,
                            HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) ||
        !hhs219_main_append(material, capacity, used, program->symbol_cell81,
                            HHS_EXACT_PASS219_VM81_SYMBOL_COUNT) ||
        !hhs219_main_append_u8(material, capacity, used, program->source_structure_complete) ||
        !hhs219_main_append_u8(material, capacity, used, program->effectful_lowering_complete) ||
        !hhs219_main_append_u8(material, capacity, used, program->source_semantics_complete) ||
        !hhs219_main_append_u8(material, capacity, used, program->full_symbolic_identity_required))
        return 0;

    for (i = 0U; i < program->instruction_count; ++i) {
        const HHSExactPass219VM81InstructionV1 *instruction = &program->instructions[i];
        if (!hhs219_main_append_u8(material, capacity, used, instruction->opcode) ||
            !hhs219_main_append_u8(material, capacity, used, instruction->a) ||
            !hhs219_main_append_u8(material, capacity, used, instruction->b) ||
            !hhs219_main_append_u8(material, capacity, used, instruction->c) ||
            !hhs219_main_append_u8(material, capacity, used, instruction->constraint_group) ||
            !hhs219_main_append_u8(material, capacity, used, instruction->phase))
            return 0;
        for (edge = 0U; edge < HHS_EXACT_PASS219_VM81_NEXT_EDGES; ++edge) {
            if (!hhs219_main_append_u8(
                    material, capacity, used, instruction->next_enabled[edge]) ||
                !hhs219_main_append_u8(
                    material, capacity, used, instruction->next_target[edge]))
                return 0;
        }
    }
    return 1;
}

static int hhs219_main_build_identity(
    HHSExactPass219MainAuthorityCompositionV1 *composition
) {
    uint8_t material[HHS219_MAIN_AUTHORITY_MATERIAL_CAPACITY];
    uint8_t before_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    uint8_t after_bytes[HHS_EXACT_VM81_FRAME_BYTES];
    size_t before_length = 0U;
    size_t after_length = 0U;
    size_t used = 0U;

    if (composition == NULL)
        return 0;
    if (hhs_exact_vm81_frame_export_le(
            &composition->candidate_execution.before_frame,
            before_bytes, sizeof(before_bytes), &before_length) != HHS_EXACT_STATUS_OK ||
        hhs_exact_vm81_frame_export_le(
            &composition->candidate_execution.after_frame,
            after_bytes, sizeof(after_bytes), &after_length) != HHS_EXACT_STATUS_OK ||
        before_length != sizeof(before_bytes) || after_length != sizeof(after_bytes))
        return 0;

    memset(material, 0, sizeof(material));

    if (!hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.source_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.ast_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.constraint_graph_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.vmir_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.receipt_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.replay_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.receipt_hash72,
            HHS_EXACT_HASH72_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->pass159.replay_hash72,
            HHS_EXACT_HASH72_LEN) ||
        !hhs219_main_append_program(
            material, sizeof(material), &used, &composition->candidate_program) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            before_bytes, sizeof(before_bytes)) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            after_bytes, sizeof(after_bytes)) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->candidate_execution.previous_hash72,
            HHS_EXACT_HASH72_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->candidate_execution.state_hash72,
            HHS_EXACT_HASH72_LEN) ||
        !hhs219_main_append(
            material, sizeof(material), &used,
            composition->candidate_execution.receipt_hash72,
            HHS_EXACT_HASH72_LEN) ||
        !hhs219_main_append_u64_le(
            material, sizeof(material), &used,
            composition->candidate_execution.steps_executed) ||
        !hhs219_main_append_u32_le(
            material, sizeof(material), &used,
            composition->candidate_execution.witness_flags) ||
        !hhs219_main_append_u32_le(
            material, sizeof(material), &used,
            composition->decision) ||
        !hhs219_main_append_u8(
            material, sizeof(material), &used,
            composition->pass159_vmir_effect_binding_observed) ||
        !hhs219_main_append_u8(
            material, sizeof(material), &used,
            composition->whole_expression_semantics_resolved) ||
        !hhs219_main_append_u8(
            material, sizeof(material), &used,
            composition->canonical_monolithic_proof))
        return 0;

    hhs_hash216_compute_bytes(material, used, composition->composition_hash216);
    return hhs219_main_hash216_valid(composition->composition_hash216);
}

uint32_t hhs_exact_pass219_main_authority_version(void) {
    return hhs219_main_authority_version_word();
}

HHSExactStatus hhs_exact_pass219_compose_main_authority(
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219MainAuthorityCompositionV1 *out_composition
) {
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    uint8_t native_source[HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH];
    size_t native_source_length = 0U;
    HHSExactStatus status;

    if (candidate_frame == NULL || out_composition == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_composition, 0, sizeof(*out_composition));
    out_composition->struct_size = (uint32_t)sizeof(*out_composition);
    out_composition->version = hhs219_main_authority_version_word();
    out_composition->decision = HHS_EXACT_PASS219_MAIN_AUTHORITY_INVALID;
    out_composition->requires_pass169_authority = 1U;
    out_composition->floating_point_authority = 0U;
    out_composition->vm81_mutation_authority = 0U;
    out_composition->hash72_commit_authority = 0U;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK ||
        hhs_exact_pass219_monolithic_native_source(
            native_source, sizeof(native_source), &native_source_length) !=
            HHS_EXACT_STATUS_OK ||
        native_source_length != sizeof(native_source))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_pass159_prove_monolithic(&out_composition->pass159);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_composition->native_source_identity_equal =
        memcmp(out_composition->pass159.source_bytes,
               native_source,
               sizeof(native_source)) == 0
            ? 1U
            : 0U;
    out_composition->pass159_source_pipeline_verified =
        out_composition->pass159.source_pipeline_verified == 1U &&
        out_composition->pass159.source_exact == 1U &&
        out_composition->pass159.frontend_chain_complete == 1U &&
        out_composition->pass159.vmir_complete == 1U
            ? 1U
            : 0U;
    out_composition->pass159_vmir_identity_present =
        hhs219_main_hash216_valid(out_composition->pass159.vmir_hash216)
            ? 1U
            : 0U;

    if (out_composition->native_source_identity_equal != 1U ||
        out_composition->pass159_source_pipeline_verified != 1U ||
        out_composition->pass159_vmir_identity_present != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_vm81_lower_monolithic_structure(
        &out_composition->candidate_program);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_composition->candidate_program_source_bound =
        memcmp(out_composition->candidate_program.source_sha256,
               descriptor.native_source_sha256,
               HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) == 0
            ? 1U
            : 0U;
    out_composition->candidate_completion_only =
        out_composition->candidate_program.derived_thread_count ==
            HHS_EXACT_PASS219_VM81_CANDIDATE_COMPLETION_THREADS &&
        out_composition->candidate_program.source_structure_thread_count ==
            HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS &&
        out_composition->candidate_program.effectful_lowering_complete == 1U &&
        out_composition->candidate_program.source_semantics_complete == 0U
            ? 1U
            : 0U;

    if (out_composition->candidate_program_source_bound != 1U ||
        out_composition->candidate_completion_only != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    status = hhs_exact_pass219_vm81_execute_candidate(
        &out_composition->candidate_program,
        candidate_frame,
        &out_composition->candidate_execution);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_composition->candidate_exact_kernel_execution_verified =
        out_composition->candidate_execution.exact_kernel_execution_observed == 1U &&
        out_composition->candidate_execution.candidate_frame_bound == 1U &&
        out_composition->candidate_execution.source_identity_valid == 1U &&
        out_composition->candidate_execution.source_semantics_complete == 0U &&
        out_composition->candidate_execution.canonical_monolithic_proof == 0U
            ? 1U
            : 0U;

    status = hhs_exact_pass219_vm81_replay_candidate(
        &out_composition->candidate_program,
        candidate_frame,
        &out_composition->candidate_execution,
        &out_composition->candidate_replay);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_composition->candidate_exact_replay_verified =
        out_composition->candidate_replay.replay_verified == 1U
            ? 1U
            : 0U;

    if (out_composition->candidate_exact_kernel_execution_verified != 1U ||
        out_composition->candidate_exact_replay_verified != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    /*
     * Main-history authority lock: Pass159 currently proves the source pipeline
     * and VMIR identity, while I121.3 proves exact execution of a separately
     * completed candidate circuit. No repository authority yet proves those
     * candidate-completion effects are the effects emitted by that Pass159 VMIR.
     */
    out_composition->pass159_vmir_effect_binding_observed = 0U;
    out_composition->whole_expression_semantics_resolved = 0U;
    out_composition->canonical_monolithic_proof = 0U;
    out_composition->decision =
        HHS_EXACT_PASS219_MAIN_AUTHORITY_VMIR_EFFECT_BINDING_REQUIRED;

    if (!hhs219_main_build_identity(out_composition))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

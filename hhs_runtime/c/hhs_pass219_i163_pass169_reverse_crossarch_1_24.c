#include "hhs_pass219_i163_pass169_reverse_crossarch_1_24.h"

#include "hhs_pass159_api.h"
#include "hhs159_internal.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const char HHS219_I163_ALPHABET[HHS_EXACT_PASS219_I163_HASH72_STRLEN] =
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

extern int hhs219_i163_hash72_ring_reverse_witness(
    const char receipt_hash72[HHS_EXACT_PASS219_I163_HASH72_STRLEN]
);

static uint32_t hhs219_i163_version_word(void) {
    return (HHS_EXACT_PASS219_I163_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_I163_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_I163_VERSION_PATCH;
}

static int hhs219_i163_hash_string_valid(const char *value, size_t length) {
    size_t i;
    if (value == NULL || value[length] != '\0')
        return 0;
    for (i = 0U; i < length; ++i) {
        if (value[i] == '\0' || strchr(HHS219_I163_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static HHS159Status hhs219_i163_copy_hash216(
    const void *handle,
    char out[HHS_EXACT_PASS219_I163_HASH216_STRLEN]
) {
    HHS159MutableByteSpan span;
    HHS159Status status;
    if (handle == NULL || out == NULL)
        return HHS159_STATUS_INVALID_ARGUMENT;
    memset(out, 0, HHS_EXACT_PASS219_I163_HASH216_STRLEN);
    span.data = (uint8_t *)out;
    span.capacity = HHS_EXACT_PASS219_I163_HASH216_LEN;
    span.size_written = 0U;
    status = hhs159_get_hash216(handle, &span);
    if (status != HHS159_STATUS_OK ||
        span.size_written != HHS_EXACT_PASS219_I163_HASH216_LEN)
        return HHS159_STATUS_HASH_MISMATCH;
    out[HHS_EXACT_PASS219_I163_HASH216_LEN] = '\0';
    return hhs219_i163_hash_string_valid(
        out, HHS_EXACT_PASS219_I163_HASH216_LEN)
        ? HHS159_STATUS_OK
        : HHS159_STATUS_HASH_MISMATCH;
}

uint32_t hhs_exact_pass219_i163_version(void) {
    return hhs219_i163_version_word();
}

HHSExactStatus hhs_exact_pass219_i163_descriptor(
    HHSExactPass219I163DescriptorV1 *out_descriptor
) {
    if (out_descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_i163_version_word();
    out_descriptor->pass169_reverse_runtime_required = 1U;
    out_descriptor->pass159_reverse_api_used = 1U;
    out_descriptor->hash72_reverse_state_api_used = 1U;
    out_descriptor->interpreter_compiler_equality_required = 1U;
    out_descriptor->prior_committed_state_restoration_required = 1U;
    out_descriptor->cross_architecture_receipt_identity_required = 1U;
    out_descriptor->python_native_parity_required = 1U;
    out_descriptor->i162_parent_immutable = 1U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->canonical_mutation_authority = 0U;
    out_descriptor->hash216_persistence_authority = 0U;
    out_descriptor->pass169_terminal_contract_claimed = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_i163_verify_reverse(
    const uint8_t *source_bytes,
    size_t source_length,
    HHSExactPass219I163ReverseExecutionV1 *out_execution
) {
    static const uint8_t source_name_bytes[] = "pass219-i163-pass169-reverse";
    static const uint8_t encoding_bytes[] = "UTF-8";
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 provenance;
    HHS159ContextConfig config;
    HHS159SourceOpenOptions source_options;
    HHS159ExecutionOptions execution_options;
    HHS159CompareResult compare_result;
    HHS159Context *context = NULL;
    HHS159Source *source = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Receipt *forward = NULL;
    HHS159Receipt *reverse = NULL;
    HHS159Receipt *repeat = NULL;
    HHS159Status status;
    HHS159ByteSpan source_span;
    HHSExactStatus exact_status = HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (source_bytes == NULL || out_execution == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_execution, 0, sizeof(*out_execution));
    out_execution->struct_size = (uint32_t)sizeof(*out_execution);
    out_execution->version = hhs219_i163_version_word();
    out_execution->decision = HHS_EXACT_PASS219_I163_UNRESOLVED;
    out_execution->reason = HHS_EXACT_PASS219_I163_REASON_NONE;
    out_execution->floating_point_authority = 0U;
    out_execution->canonical_mutation_authority = 0U;
    out_execution->hash216_persistence_authority = 0U;
    out_execution->pass169_terminal_contract_claimed = 0U;

    memset(&provenance, 0, sizeof(provenance));
    if (hhs_exact_pass219_pass159_global_witness_produce(
            source_bytes, source_length, &provenance) != HHS_EXACT_STATUS_OK ||
        provenance.source_identity_exact != 1U ||
        provenance.frontend_chain_complete != 1U ||
        provenance.source_root_lineage_exact != 1U ||
        provenance.pass159_whole_expression_provenance_verified != 1U) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_SOURCE_PROVENANCE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_execution->source_provenance_exact = 1U;
    memcpy(out_execution->source_hash216,
           provenance.source_hash216, sizeof(out_execution->source_hash216));

    memset(&config, 0, sizeof(config));
    config.header.struct_size = (uint32_t)sizeof(config);
    config.header.struct_version = HHS159_STRUCT_VERSION_1;
    config.max_source_bytes = UINT64_C(1048576);
    config.max_tokens = UINT64_C(200000);
    config.max_nesting = UINT64_C(4096);
    config.max_output_bytes = UINT64_C(4194304);
    config.deterministic_epoch = UINT64_C(0);
    config.flags = HHS159_FLAG_ORDERED | HHS159_FLAG_AUTHORITATIVE;

    status = hhs159_context_create(&config, &context);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    memset(&source_options, 0, sizeof(source_options));
    source_options.header.struct_size = (uint32_t)sizeof(source_options);
    source_options.header.struct_version = HHS159_STRUCT_VERSION_1;
    source_options.source_name.data = source_name_bytes;
    source_options.source_name.size = sizeof(source_name_bytes) - 1U;
    source_options.encoding.data = encoding_bytes;
    source_options.encoding.size = sizeof(encoding_bytes) - 1U;
    source_options.preserve_bom = 1U;
    source_options.flags = HHS159_FLAG_ORDERED | HHS159_FLAG_AUTHORITATIVE;

    source_span.data = source_bytes;
    source_span.size = source_length;
    status = hhs159_source_open_bytes(context, source_span, &source_options, &source);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    status = hhs159_interpreter_create(context, &interpreter);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    memset(&execution_options, 0, sizeof(execution_options));
    execution_options.header.struct_size = (uint32_t)sizeof(execution_options);
    execution_options.header.struct_version = HHS159_STRUCT_VERSION_1;
    execution_options.mode = HHS159_MODE_EXECUTE_AND_COMMIT;
    execution_options.commit_policy = 1U;
    execution_options.max_vm81_steps = UINT64_C(1000000);
    execution_options.max_recursion = UINT64_C(4096);
    execution_options.max_output_bytes = UINT64_C(4194304);
    execution_options.cancel_flag = NULL;

    status = hhs159_interpret(interpreter, source, &execution_options, &forward);
    if (status != HHS159_STATUS_OK || forward == NULL ||
        hhs159_artifact_kind(forward) != HHS159_ARTIFACT_RECEIPT ||
        forward->status != HHS159_STATUS_OK || forward->committed != 1U) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_FORWARD_COMMIT;
        goto cleanup;
    }
    out_execution->forward_commit_verified = 1U;
    out_execution->forward_vm81_steps = forward->vm81_steps;
    memcpy(out_execution->forward_semantic_root_hash216,
           forward->semantic_root,
           sizeof(out_execution->forward_semantic_root_hash216));
    memcpy(out_execution->prior_semantic_root_hash216,
           forward->base.parent_root,
           sizeof(out_execution->prior_semantic_root_hash216));
    memcpy(out_execution->forward_receipt_hash72,
           forward->hash72, sizeof(out_execution->forward_receipt_hash72));
    out_execution->forward_receipt_hash72_valid =
        hhs219_i163_hash_string_valid(
            out_execution->forward_receipt_hash72,
            HHS_EXACT_PASS219_I163_HASH72_LEN) ? 1U : 0U;
    status = hhs219_i163_copy_hash216(
        forward, out_execution->forward_receipt_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_execution->forward_receipt_hash216_valid = 1U;

    status = hhs159_reverse(context, forward, &reverse);
    if (status != HHS159_STATUS_OK || reverse == NULL ||
        hhs159_artifact_kind(reverse) != HHS159_ARTIFACT_RECEIPT ||
        reverse->status != HHS159_STATUS_OK) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_REVERSE_RUNTIME;
        goto cleanup;
    }
    out_execution->reverse_runtime_verified = 1U;
    out_execution->reverse_vm81_steps = reverse->vm81_steps;
    memcpy(out_execution->reverse_semantic_root_hash216,
           reverse->semantic_root,
           sizeof(out_execution->reverse_semantic_root_hash216));
    memcpy(out_execution->reverse_receipt_hash72,
           reverse->hash72, sizeof(out_execution->reverse_receipt_hash72));
    out_execution->reverse_receipt_hash72_valid =
        hhs219_i163_hash_string_valid(
            out_execution->reverse_receipt_hash72,
            HHS_EXACT_PASS219_I163_HASH72_LEN) ? 1U : 0U;
    status = hhs219_i163_copy_hash216(
        reverse, out_execution->reverse_receipt_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_execution->reverse_receipt_hash216_valid = 1U;

    out_execution->reverse_restored_prior_semantic_root =
        memcmp(out_execution->reverse_semantic_root_hash216,
               out_execution->prior_semantic_root_hash216,
               HHS_EXACT_PASS219_I163_HASH216_LEN) == 0 ? 1U : 0U;
    if (out_execution->reverse_restored_prior_semantic_root != 1U) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_PRIOR_STATE_MISMATCH;
        goto cleanup;
    }

    memset(&compare_result, 0, sizeof(compare_result));
    compare_result.header.struct_size = (uint32_t)sizeof(compare_result);
    compare_result.header.struct_version = HHS159_STRUCT_VERSION_1;
    status = hhs159_compare_interpreter_compiler(
        context, source, &execution_options, &compare_result);
    if (status != HHS159_STATUS_OK || compare_result.status != HHS159_STATUS_OK ||
        compare_result.matched != 1U || compare_result.fallback_used != 0U) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_INTERPRETER_COMPILER;
        goto cleanup;
    }
    out_execution->interpreter_compiler_match = 1U;

    if (!hhs219_i163_hash72_ring_reverse_witness(
            out_execution->forward_receipt_hash72)) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_RING_REVERSE;
        goto cleanup;
    }
    out_execution->hash72_ring_reverse_verified = 1U;
    out_execution->hash72_ring_restored_prior_state = 1U;

    status = hhs159_interpret(interpreter, source, &execution_options, &repeat);
    if (status != HHS159_STATUS_OK || repeat == NULL ||
        repeat->status != HHS159_STATUS_OK || repeat->committed != 1U ||
        strcmp(forward->hash72, repeat->hash72) != 0 ||
        strcmp(forward->semantic_root, repeat->semantic_root) != 0) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_RECEIPT_IDENTITY;
        goto cleanup;
    }
    out_execution->deterministic_repeat_verified = 1U;

    if (!out_execution->forward_receipt_hash72_valid ||
        !out_execution->forward_receipt_hash216_valid ||
        !out_execution->reverse_receipt_hash72_valid ||
        !out_execution->reverse_receipt_hash216_valid) {
        out_execution->decision = HHS_EXACT_PASS219_I163_REJECTED;
        out_execution->reason = HHS_EXACT_PASS219_I163_REASON_RECEIPT_IDENTITY;
        goto cleanup;
    }

    out_execution->decision = HHS_EXACT_PASS219_I163_VERIFIED;
    out_execution->reason = HHS_EXACT_PASS219_I163_REASON_NONE;
    exact_status = HHS_EXACT_STATUS_OK;

cleanup:
    if (repeat != NULL)
        hhs159_receipt_release(repeat);
    if (reverse != NULL)
        hhs159_receipt_release(reverse);
    if (forward != NULL)
        hhs159_receipt_release(forward);
    if (interpreter != NULL)
        hhs159_interpreter_release(interpreter);
    if (source != NULL)
        hhs159_source_release(source);
    if (context != NULL)
        hhs159_context_release(context);
    return exact_status;
}

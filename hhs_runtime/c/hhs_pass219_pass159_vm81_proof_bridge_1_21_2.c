#include "hhs_pass219_pass159_vm81_proof_bridge_1_21_2.h"

#include "hhs_pass159_api.h"
#include "hhs159_internal.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static int hhs219_pass159_hash216_valid(const char *value) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN; ++i) {
        if (value[i] == '\0' ||
            strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static int hhs219_pass159_hash72_valid(const char *value) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i) {
        if (value[i] == '\0' ||
            strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL)
            return 0;
    }
    return 1;
}

static HHS159Status hhs219_pass159_copy_hash216(
    const void *handle,
    char out[HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN]
) {
    HHS159MutableByteSpan span;
    HHS159Status status;
    if (handle == NULL || out == NULL)
        return HHS159_STATUS_INVALID_ARGUMENT;
    memset(out, 0, HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN);
    span.data = (uint8_t *)out;
    span.capacity = HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN;
    span.size_written = 0U;
    status = hhs159_get_hash216(handle, &span);
    if (status != HHS159_STATUS_OK)
        return status;
    if (span.size_written != HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN)
        return HHS159_STATUS_HASH_MISMATCH;
    out[HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN] = '\0';
    return hhs219_pass159_hash216_valid(out)
        ? HHS159_STATUS_OK
        : HHS159_STATUS_HASH_MISMATCH;
}

static void hhs219_pass159_release_artifact(void **handle) {
    if (handle != NULL && *handle != NULL) {
        hhs159_artifact_release(*handle);
        *handle = NULL;
    }
}

uint32_t hhs_exact_pass219_pass159_proof_version(void) {
    return (HHS_EXACT_PASS219_PASS159_PROOF_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS159_PROOF_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS159_PROOF_VERSION_PATCH;
}

HHSExactStatus hhs_exact_pass219_pass159_prove_monolithic(
    HHSExactPass219Pass159ProofV1 *out_proof
) {
    static const uint8_t source_name_bytes[] = "pass219-monolithic-native-1.20";
    static const uint8_t encoding_bytes[] = "UTF-8";
    HHS159ContextConfig config;
    HHS159SourceOpenOptions source_options;
    HHS159ExecutionOptions execution_options;
    HHS159CompareResult compare_result;
    HHS159Context *context = NULL;
    HHS159Source *source = NULL;
    HHS159IR *tokens = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159IR *hir = NULL;
    HHS159IR *vmir = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Receipt *receipt = NULL;
    HHS159Receipt *replay_receipt = NULL;
    HHS159Status status = HHS159_STATUS_OK;
    HHSExactStatus exact_status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
    HHS159ByteSpan source_span;
    size_t source_length = 0U;

    if (out_proof == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_proof, 0, sizeof(*out_proof));
    out_proof->struct_size = (uint32_t)sizeof(*out_proof);
    out_proof->version = hhs_exact_pass219_pass159_proof_version();
    out_proof->pass159_status = (int32_t)HHS159_STATUS_INVALID_STATE;
    out_proof->floating_point_authority = 0U;
    out_proof->vm81_mutation_authority = 0U;
    out_proof->hash72_commit_authority = 0U;
    out_proof->pass159_vmir_effectful = 0U;
    out_proof->pass159_vm81_execution_observed = 0U;
    out_proof->pass159_replay_reexecuted = 0U;
    out_proof->pass159_step_counter_authoritative = 0U;
    out_proof->candidate_binding_supported = 0U;
    out_proof->canonical_vm81_proof_observed = 0U;
    out_proof->candidate_vm81_proof_required = 1U;

    if (hhs_exact_pass219_monolithic_native_source(
            out_proof->source_bytes,
            sizeof(out_proof->source_bytes),
            &source_length) != HHS_EXACT_STATUS_OK ||
        source_length != sizeof(out_proof->source_bytes)) {
        out_proof->pass159_status = (int32_t)HHS159_STATUS_INVALID_STATE;
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    out_proof->source_exact = 1U;

    memset(&config, 0, sizeof(config));
    config.header.struct_size = (uint32_t)sizeof(config);
    config.header.struct_version = HHS159_STRUCT_VERSION_1;
    config.max_source_bytes = UINT64_C(1048576);
    config.max_tokens = UINT64_C(200000);
    config.max_nesting = UINT64_C(4096);
    config.max_output_bytes = UINT64_C(4194304);
    config.deterministic_epoch = UINT64_C(0);
    config.flags = HHS159_FLAG_ORDERED;

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
    source_options.flags = HHS159_FLAG_ORDERED;

    source_span.data = out_proof->source_bytes;
    source_span.size = source_length;
    status = hhs159_source_open_bytes(context, source_span, &source_options, &source);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_SOURCE_OPEN;

    status = hhs219_pass159_copy_hash216(source, out_proof->source_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    status = hhs159_lex(context, source, &tokens);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_LEX;

    status = hhs159_parse_cst(context, source, &cst);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_CST;

    status = hhs159_build_ast(context, cst, &ast);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_AST;
    status = hhs219_pass159_copy_hash216(ast, out_proof->ast_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    status = hhs159_typecheck(context, ast, &types);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_TYPECHECK;

    status = hhs159_build_constraint_graph(context, ast, types, &graph);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_CONSTRAINT_GRAPH;
    status = hhs219_pass159_copy_hash216(graph, out_proof->constraint_graph_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    status = hhs159_lower_hir(context, ast, types, graph, &hir);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_HIR;

    status = hhs159_lower_vmir(context, hir, &vmir);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_VMIR;
    status = hhs219_pass159_copy_hash216(vmir, out_proof->vmir_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->frontend_chain_complete = 1U;
    out_proof->vmir_complete = 1U;

    status = hhs159_interpreter_create(context, &interpreter);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    memset(&execution_options, 0, sizeof(execution_options));
    execution_options.header.struct_size = (uint32_t)sizeof(execution_options);
    execution_options.header.struct_version = HHS159_STRUCT_VERSION_1;
    execution_options.mode = HHS159_MODE_EXECUTE_AND_HOLD;
    execution_options.commit_policy = 0U;
    execution_options.max_vm81_steps = UINT64_C(1000000);
    execution_options.max_recursion = UINT64_C(4096);
    execution_options.max_output_bytes = UINT64_C(4194304);
    execution_options.cancel_flag = NULL;

    status = hhs159_interpret(interpreter, source, &execution_options, &receipt);
    if (status != HHS159_STATUS_OK || receipt == NULL)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_INTERPRET;
    out_proof->interpret_ok = 1U;

    if (hhs159_artifact_kind(receipt) != HHS159_ARTIFACT_RECEIPT) {
        status = HHS159_STATUS_INVALID_STATE;
        goto cleanup;
    }
    out_proof->receipt_status_ok = receipt->status == HHS159_STATUS_OK ? 1U : 0U;
    out_proof->vm81_steps = receipt->vm81_steps;
    out_proof->fallback_used = receipt->fallback_used;
    out_proof->committed = receipt->committed;
    memcpy(
        out_proof->semantic_root_hash216,
        receipt->semantic_root,
        HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN);
    memcpy(
        out_proof->receipt_hash72,
        receipt->hash72,
        HHS_EXACT_PASS219_PASS159_PROOF_HASH72_STRLEN);
    out_proof->receipt_hash72_valid =
        hhs219_pass159_hash72_valid(out_proof->receipt_hash72) ? 1U : 0U;
    status = hhs219_pass159_copy_hash216(receipt, out_proof->receipt_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    status = hhs159_interpreter_replay(interpreter, receipt, &replay_receipt);
    if (status != HHS159_STATUS_OK || replay_receipt == NULL)
        goto cleanup;
    out_proof->completed_stage_mask |= HHS_EXACT_PASS219_STAGE_REPLAY;
    out_proof->replay_ok = 1U;

    if (hhs159_artifact_kind(replay_receipt) != HHS159_ARTIFACT_RECEIPT) {
        status = HHS159_STATUS_INVALID_STATE;
        goto cleanup;
    }
    out_proof->replay_receipt_status_ok =
        replay_receipt->status == HHS159_STATUS_OK ? 1U : 0U;
    out_proof->replay_vm81_steps = replay_receipt->vm81_steps;
    out_proof->replay_committed = replay_receipt->committed;
    memcpy(
        out_proof->replay_semantic_root_hash216,
        replay_receipt->semantic_root,
        HHS_EXACT_PASS219_PASS159_PROOF_HASH216_STRLEN);
    memcpy(
        out_proof->replay_hash72,
        replay_receipt->hash72,
        HHS_EXACT_PASS219_PASS159_PROOF_HASH72_STRLEN);
    out_proof->replay_hash72_valid =
        hhs219_pass159_hash72_valid(out_proof->replay_hash72) ? 1U : 0U;
    status = hhs219_pass159_copy_hash216(replay_receipt, out_proof->replay_hash216);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    out_proof->semantic_root_equal =
        memcmp(
            out_proof->semantic_root_hash216,
            out_proof->replay_semantic_root_hash216,
            HHS_EXACT_PASS219_MONOLITHIC_HASH216_LEN) == 0
            ? 1U
            : 0U;

    memset(&compare_result, 0, sizeof(compare_result));
    compare_result.header.struct_size = (uint32_t)sizeof(compare_result);
    compare_result.header.struct_version = HHS159_STRUCT_VERSION_1;
    status = hhs159_compare_interpreter_compiler(
        context, source, &execution_options, &compare_result);
    if (status != HHS159_STATUS_OK)
        goto cleanup;
    out_proof->interpreter_compiler_match =
        compare_result.status == HHS159_STATUS_OK && compare_result.matched == 1U
            ? 1U
            : 0U;
    if (compare_result.fallback_used != 0U)
        out_proof->fallback_used = compare_result.fallback_used;

    /*
     * Canonical main authority alignment:
     * Pass159's merged toolchain is inherited foundation authority for source,
     * typed graph, VMIR and receipt construction. The receipt fields accessed
     * through hhs159_internal.h are diagnostic observations only: they are not
     * a public-ABI grant of candidate-bound VM81 proof authority. Current
     * Pass159 VMIR remains a fixed EXACT_PROGRAM foundation artifact and replay
     * re-wraps receipt identity, so no internal field below may self-promote to
     * canonical VM81 execution/proof evidence.
     */
    out_proof->source_pipeline_verified =
        out_proof->source_exact == 1U &&
        out_proof->frontend_chain_complete == 1U &&
        out_proof->vmir_complete == 1U &&
        out_proof->interpret_ok == 1U &&
        out_proof->replay_ok == 1U &&
        out_proof->receipt_status_ok == 1U &&
        out_proof->replay_receipt_status_ok == 1U &&
        out_proof->receipt_hash72_valid == 1U &&
        out_proof->replay_hash72_valid == 1U &&
        out_proof->semantic_root_equal == 1U &&
        out_proof->interpreter_compiler_match == 1U &&
        out_proof->fallback_used == 0U &&
        out_proof->committed == 0U &&
        out_proof->replay_committed == 0U &&
        (out_proof->completed_stage_mask &
         HHS_EXACT_PASS219_PASS159_SOURCE_PIPELINE_REQUIRED) ==
            HHS_EXACT_PASS219_PASS159_SOURCE_PIPELINE_REQUIRED
            ? 1U
            : 0U;

    out_proof->vm81_execution_verified = 0U;
    out_proof->native_shared_invariant_proven = 0U;
    out_proof->canonical_vm81_proof_observed = 0U;

    status = out_proof->source_pipeline_verified == 1U
        ? HHS159_STATUS_OK
        : HHS159_STATUS_INVALID_STATE;
    exact_status = out_proof->source_pipeline_verified == 1U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;

cleanup:
    out_proof->pass159_status = (int32_t)status;
    if (replay_receipt != NULL)
        hhs159_receipt_release(replay_receipt);
    if (receipt != NULL)
        hhs159_receipt_release(receipt);
    if (interpreter != NULL)
        hhs159_interpreter_release(interpreter);
    hhs219_pass159_release_artifact((void **)&vmir);
    hhs219_pass159_release_artifact((void **)&hir);
    hhs219_pass159_release_artifact((void **)&graph);
    hhs219_pass159_release_artifact((void **)&types);
    hhs219_pass159_release_artifact((void **)&ast);
    hhs219_pass159_release_artifact((void **)&cst);
    hhs219_pass159_release_artifact((void **)&tokens);
    if (source != NULL)
        hhs159_source_release(source);
    if (context != NULL)
        hhs159_context_release(context);

    return exact_status;
}
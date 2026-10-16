#include "hhs_pass159_api.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EXPECTED_SOURCE_BYTES 283U

static int read_file(const char *path, uint8_t **out, size_t *out_size) {
    FILE *fp;
    long size;
    uint8_t *buffer;
    if (path == NULL || out == NULL || out_size == NULL)
        return 0;
    fp = fopen(path, "rb");
    if (fp == NULL)
        return 0;
    if (fseek(fp, 0L, SEEK_END) != 0) {
        fclose(fp);
        return 0;
    }
    size = ftell(fp);
    if (size < 0 || fseek(fp, 0L, SEEK_SET) != 0) {
        fclose(fp);
        return 0;
    }
    buffer = (uint8_t *)malloc((size_t)size);
    if (buffer == NULL) {
        fclose(fp);
        return 0;
    }
    if (fread(buffer, 1U, (size_t)size, fp) != (size_t)size) {
        free(buffer);
        fclose(fp);
        return 0;
    }
    fclose(fp);
    *out = buffer;
    *out_size = (size_t)size;
    return 1;
}

static int copy_hash216(const void *handle, char out[HHS159_HASH216_LENGTH + 1U]) {
    HHS159MutableByteSpan span;
    memset(out, 0, HHS159_HASH216_LENGTH + 1U);
    span.data = (uint8_t *)out;
    span.capacity = HHS159_HASH216_LENGTH;
    span.size_written = 0U;
    if (hhs159_get_hash216(handle, &span) != HHS159_STATUS_OK)
        return 0;
    if (span.size_written != HHS159_HASH216_LENGTH)
        return 0;
    out[HHS159_HASH216_LENGTH] = '\0';
    return 1;
}

int main(void) {
    static const uint8_t source_name[] = "pass220-ordered-five-gate-phase36-72";
    static const uint8_t encoding[] = "UTF-8";
    const char *path =
        "contracts/pass220/PASS_220_ORDERED_FIVE_GATE_PHASE36_72_SOURCE_V1.harmonicode";
    uint8_t *bytes = NULL;
    size_t byte_count = 0U;
    HHS159ContextConfig config;
    HHS159SourceOpenOptions options;
    HHS159ByteSpan source_span;
    HHS159Context *context = NULL;
    HHS159Source *source = NULL;
    HHS159Source *mutated_source = NULL;
    HHS159CST *mutated_cst = NULL;
    HHS159AST *mutated_ast = NULL;
    HHS159TypeEnvironment *mutated_types = NULL;
    HHS159ConstraintGraph *mutated_graph = NULL;
    uint8_t *mutated_bytes = NULL;
    HHS159IR *tokens = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159IR *hir = NULL;
    HHS159IR *vmir = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Receipt *execution = NULL;
    HHS159Receipt *replay = NULL;
    HHS159ExecutionOptions execution_options;
    char source_hash[HHS159_HASH216_LENGTH + 1U];
    char ast_hash[HHS159_HASH216_LENGTH + 1U];
    char mutated_source_hash[HHS159_HASH216_LENGTH + 1U];
    char graph_hash[HHS159_HASH216_LENGTH + 1U];
    char mutated_ast_hash[HHS159_HASH216_LENGTH + 1U];
    char mutated_types_hash[HHS159_HASH216_LENGTH + 1U];
    char types_hash[HHS159_HASH216_LENGTH + 1U];
    char mutated_graph_hash[HHS159_HASH216_LENGTH + 1U];
    char vmir_hash[HHS159_HASH216_LENGTH + 1U];
    int ok = 0;

    if (!read_file(path, &bytes, &byte_count) || byte_count != EXPECTED_SOURCE_BYTES)
        goto cleanup;

    memset(&config, 0, sizeof(config));
    config.header.struct_size = (uint32_t)sizeof(config);
    config.header.struct_version = HHS159_STRUCT_VERSION_1;
    config.max_source_bytes = UINT64_C(1048576);
    config.max_tokens = UINT64_C(200000);
    config.max_nesting = UINT64_C(4096);
    config.max_output_bytes = UINT64_C(4194304);
    config.deterministic_epoch = UINT64_C(0);
    config.flags = HHS159_FLAG_ORDERED;
    if (hhs159_context_create(&config, &context) != HHS159_STATUS_OK)
        goto cleanup;

    memset(&options, 0, sizeof(options));
    options.header.struct_size = (uint32_t)sizeof(options);
    options.header.struct_version = HHS159_STRUCT_VERSION_1;
    options.source_name.data = source_name;
    options.source_name.size = sizeof(source_name) - 1U;
    options.encoding.data = encoding;
    options.encoding.size = sizeof(encoding) - 1U;
    options.preserve_bom = 1U;
    options.flags = HHS159_FLAG_ORDERED;

    source_span.data = bytes;
    source_span.size = byte_count;
    if (hhs159_source_open_bytes(context, source_span, &options, &source) != HHS159_STATUS_OK)
        goto cleanup;
    if (!copy_hash216(source, source_hash))
        goto cleanup;

    if (hhs159_lex(context, source, &tokens) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(tokens) != HHS159_ARTIFACT_TOKEN_STREAM)
        goto cleanup;
    if (hhs159_parse_cst(context, source, &cst) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(cst) != HHS159_ARTIFACT_CST)
        goto cleanup;
    if (hhs159_build_ast(context, cst, &ast) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(ast) != HHS159_ARTIFACT_AST ||
        !copy_hash216(ast, ast_hash))
        goto cleanup;
    if (hhs159_typecheck(context, ast, &types) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV ||
        !copy_hash216(types, types_hash))
        goto cleanup;
    if (hhs159_build_constraint_graph(context, ast, types, &graph) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(graph) != HHS159_ARTIFACT_CONSTRAINT_GRAPH ||
        !copy_hash216(graph, graph_hash))
        goto cleanup;
    if (hhs159_lower_hir(context, ast, types, graph, &hir) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(hir) != HHS159_ARTIFACT_HIR)
        goto cleanup;
    if (hhs159_lower_vmir(context, hir, &vmir) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(vmir) != HHS159_ARTIFACT_VMIR ||
        !copy_hash216(vmir, vmir_hash))
        goto cleanup;

    /* Hashes are identities, not proof authority.  They must be populated and
     * deterministic, and must not be promoted to canonical proof authority. */
    if (source_hash[0] == '\0' || ast_hash[0] == '\0' ||
        graph_hash[0] == '\0' || vmir_hash[0] == '\0')
        goto cleanup;

    /* Interpreter/replay receipts are diagnostic: Pass219's inherited bridge
     * does not authorize their promotion to canonical VM81 proof. */
    if (hhs159_interpreter_create(context, &interpreter) != HHS159_STATUS_OK)
        goto cleanup;
    memset(&execution_options, 0, sizeof(execution_options));
    execution_options.header.struct_size = (uint32_t)sizeof(execution_options);
    execution_options.header.struct_version = HHS159_STRUCT_VERSION_1;
    execution_options.mode = HHS159_MODE_EXECUTE_AND_HOLD;
    execution_options.commit_policy = 0U;
    execution_options.max_vm81_steps = UINT64_C(1000000);
    execution_options.max_recursion = UINT64_C(4096);
    execution_options.max_output_bytes = UINT64_C(4194304);
    if (hhs159_interpret(interpreter, source, &execution_options, &execution) !=
            HHS159_STATUS_OK || execution == NULL ||
        hhs159_artifact_kind(execution) != HHS159_ARTIFACT_RECEIPT)
        goto cleanup;
    if (hhs159_interpreter_replay(interpreter, execution, &replay) !=
            HHS159_STATUS_OK || replay == NULL ||
        hhs159_artifact_kind(replay) != HHS159_ARTIFACT_RECEIPT)
        goto cleanup;
    /* Source-dependency negative control: a one-byte, same-width phase
     * mutation must produce a distinct source identity. This is not an
     * assertion that the interpreter proves the changed mathematics. */
    mutated_bytes = (uint8_t *)malloc(byte_count);
    if (mutated_bytes == NULL)
        goto cleanup;
    memcpy(mutated_bytes, bytes, byte_count);
    {
        static const char needle[] = "u^36==z^2";
        size_t i;
        int changed = 0;
        for (i = 0U; i + sizeof(needle) - 1U <= byte_count; ++i) {
            if (memcmp(mutated_bytes + i, needle, sizeof(needle) - 1U) == 0) {
                mutated_bytes[i + 3U] = (uint8_t)'7'; /* 36 -> 37 */
                changed = 1;
                break;
            }
        }
        if (!changed)
            goto cleanup;
    }
    source_span.data = mutated_bytes;
    source_span.size = byte_count;
    if (hhs159_source_open_bytes(context, source_span, &options, &mutated_source)
            != HHS159_STATUS_OK ||
        !copy_hash216(mutated_source, mutated_source_hash) ||
        memcmp(source_hash, mutated_source_hash, HHS159_HASH216_LENGTH) == 0)
        goto cleanup;
    /* Prove that a same-width source mutation propagates through the
     * Pass159 AST and typed constraint graph as distinct artifacts. */
    if (hhs159_parse_cst(context, mutated_source, &mutated_cst) != HHS159_STATUS_OK ||
        hhs159_build_ast(context, mutated_cst, &mutated_ast) != HHS159_STATUS_OK ||
        !copy_hash216(mutated_ast, mutated_ast_hash) ||
        hhs159_typecheck(context, mutated_ast, &mutated_types) != HHS159_STATUS_OK ||
        !copy_hash216(mutated_types, mutated_types_hash) ||
        hhs159_build_constraint_graph(context, mutated_ast, mutated_types, &mutated_graph)
            != HHS159_STATUS_OK ||
        !copy_hash216(mutated_graph, mutated_graph_hash) ||
        types_hash[0] == '\0' || mutated_types_hash[0] == '\0' ||
        memcmp(ast_hash, mutated_ast_hash, HHS159_HASH216_LENGTH) == 0 ||
        memcmp(graph_hash, mutated_graph_hash, HHS159_HASH216_LENGTH) == 0)
        goto cleanup;
    ok = 1;

cleanup:
    if (mutated_graph != NULL) hhs159_artifact_release(mutated_graph);
    if (mutated_types != NULL) hhs159_artifact_release(mutated_types);
    if (mutated_ast != NULL) hhs159_artifact_release(mutated_ast);
    if (mutated_cst != NULL) hhs159_artifact_release(mutated_cst);
    if (replay != NULL) hhs159_receipt_release(replay);
    if (execution != NULL) hhs159_receipt_release(execution);
    if (interpreter != NULL) hhs159_interpreter_release(interpreter);
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (mutated_source != NULL) hhs159_source_release(mutated_source);
    if (source != NULL) hhs159_source_release(source);
    if (context != NULL) hhs159_context_release(context);
    free(mutated_bytes);
    free(bytes);

    if (!ok) {
        fprintf(stderr, "PASS220 ordered five-gate Pass159 frontend: FAIL\n");
        return 1;
    }
    puts("PASS220 ordered five-gate Pass159 frontend: PASS");
    return 0;
}

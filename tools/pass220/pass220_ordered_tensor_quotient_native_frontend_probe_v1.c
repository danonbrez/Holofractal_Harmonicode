#include "hhs_pass159_api.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_all(const char *path, uint8_t **out, size_t *out_count) {
    FILE *fp = fopen(path, "rb");
    long n;
    uint8_t *bytes;
    if (fp == NULL) return 0;
    if (fseek(fp, 0L, SEEK_END) != 0 || (n = ftell(fp)) <= 0 ||
        fseek(fp, 0L, SEEK_SET) != 0) { fclose(fp); return 0; }
    bytes = (uint8_t *)malloc((size_t)n);
    if (bytes == NULL) { fclose(fp); return 0; }
    if (fread(bytes, 1U, (size_t)n, fp) != (size_t)n) {
        free(bytes); fclose(fp); return 0;
    }
    fclose(fp);
    *out = bytes;
    *out_count = (size_t)n;
    return 1;
}

static int hash216(const void *artifact, char out[HHS159_HASH216_LENGTH + 1U]) {
    HHS159MutableByteSpan span;
    HHS159Status result;
    memset(out, 0, HHS159_HASH216_LENGTH + 1U);
    span.data = (uint8_t *)out;
    span.capacity = HHS159_HASH216_LENGTH;
    span.size_written = 0U;
    result = hhs159_get_hash216(artifact, &span);
    if (result != HHS159_STATUS_OK || span.size_written != HHS159_HASH216_LENGTH)
        return 0;
    out[HHS159_HASH216_LENGTH] = '\0';
    return 1;
}

int main(int argc, char **argv) {
    static const uint8_t source_name[] = "pass220-user-ordered-tensor-quotient-20261009";
    static const uint8_t encoding[] = "UTF-8";
    uint8_t *source_bytes = NULL;
    size_t byte_count = 0U;
    HHS159ContextConfig cfg;
    HHS159SourceOpenOptions options;
    HHS159ExecutionOptions execution;
    HHS159ByteSpan bytes;
    HHS159Context *ctx = NULL;
    HHS159Source *source = NULL;
    HHS159IR *tokens = NULL, *hir = NULL, *vmir = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Receipt *validation_receipt = NULL;
    HHS159Status validation_status = HHS159_STATUS_INVALID_STATE;
    char source_root[HHS159_HASH216_LENGTH + 1U];
    char graph_root[HHS159_HASH216_LENGTH + 1U];
    char vmir_root[HHS159_HASH216_LENGTH + 1U];
    int frontend_ok = 0;

    if (argc != 2 || !read_all(argv[1], &source_bytes, &byte_count)) {
        fprintf(stderr, "SOURCE_NOT_READABLE\n");
        return 2;
    }
    memset(&cfg, 0, sizeof(cfg));
    cfg.header.struct_size = (uint32_t)sizeof(cfg);
    cfg.header.struct_version = HHS159_STRUCT_VERSION_1;
    cfg.max_source_bytes = UINT64_C(1048576);
    cfg.max_tokens = UINT64_C(200000);
    cfg.max_nesting = UINT64_C(4096);
    cfg.max_output_bytes = UINT64_C(4194304);
    cfg.deterministic_epoch = UINT64_C(0);
    cfg.flags = HHS159_FLAG_ORDERED;
    if (hhs159_context_create(&cfg, &ctx) != HHS159_STATUS_OK) goto cleanup;

    memset(&options, 0, sizeof(options));
    options.header.struct_size = (uint32_t)sizeof(options);
    options.header.struct_version = HHS159_STRUCT_VERSION_1;
    options.source_name.data = source_name;
    options.source_name.size = sizeof(source_name) - 1U;
    options.encoding.data = encoding;
    options.encoding.size = sizeof(encoding) - 1U;
    options.preserve_bom = 1U;
    options.flags = HHS159_FLAG_ORDERED;
    bytes.data = source_bytes;
    bytes.size = byte_count;
    if (hhs159_source_open_bytes(ctx, bytes, &options, &source) != HHS159_STATUS_OK)
        goto cleanup;
    if (!hash216(source, source_root)) goto cleanup;
    if (hhs159_lex(ctx, source, &tokens) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(tokens) != HHS159_ARTIFACT_TOKEN_STREAM) goto cleanup;
    if (hhs159_parse_cst(ctx, source, &cst) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(cst) != HHS159_ARTIFACT_CST) goto cleanup;
    if (hhs159_build_ast(ctx, cst, &ast) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(ast) != HHS159_ARTIFACT_AST) goto cleanup;
    if (hhs159_typecheck(ctx, ast, &types) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV) goto cleanup;
    if (hhs159_build_constraint_graph(ctx, ast, types, &graph) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(graph) != HHS159_ARTIFACT_CONSTRAINT_GRAPH ||
        !hash216(graph, graph_root)) goto cleanup;
    if (hhs159_lower_hir(ctx, ast, types, graph, &hir) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(hir) != HHS159_ARTIFACT_HIR) goto cleanup;
    if (hhs159_lower_vmir(ctx, hir, &vmir) != HHS159_STATUS_OK ||
        hhs159_artifact_kind(vmir) != HHS159_ARTIFACT_VMIR ||
        !hash216(vmir, vmir_root)) goto cleanup;
    frontend_ok = 1;
    printf("source_bytes=%zu\nsource_hash216=%s\ngraph_hash216=%s\nvmir_hash216=%s\n",
           byte_count, source_root, graph_root, vmir_root);

    /* Bounded existing native path. Never substitute an older 632-byte source
     * proof or admit a candidate without new source-specific gate witnesses. */
    if (hhs159_interpreter_create(ctx, &interpreter) == HHS159_STATUS_OK) {
        memset(&execution, 0, sizeof(execution));
        execution.header.struct_size = (uint32_t)sizeof(execution);
        execution.header.struct_version = HHS159_STRUCT_VERSION_1;
        execution.mode = HHS159_MODE_VALIDATE_ONLY;
        execution.max_vm81_steps = UINT64_C(100000);
        execution.max_recursion = UINT64_C(4096);
        execution.max_output_bytes = UINT64_C(4194304);
        validation_status = hhs159_interpret(interpreter, source, &execution,
                                             &validation_receipt);
    }
    printf("native_validate_only_status=%d\n", (int)validation_status);
    if (validation_status == HHS159_STATUS_OK && validation_receipt != NULL) {
        char receipt_root[HHS159_HASH216_LENGTH + 1U];
        if (hash216(validation_receipt, receipt_root))
            printf("native_validate_only_receipt_hash216=%s\n", receipt_root);
    }
    puts("vm81_source_specific_commit_verified=false");
    puts("hash72_source_specific_execution_receipt_verified=false");
    puts("source_ingress_authority=PASS159_FRONTEND_AND_NATIVE_VALIDATE_ONLY");

cleanup:
    if (validation_receipt != NULL) hhs159_receipt_release(validation_receipt);
    if (interpreter != NULL) hhs159_interpreter_release(interpreter);
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (source != NULL) hhs159_source_release(source);
    if (ctx != NULL) hhs159_context_release(ctx);
    free(source_bytes);
    if (!frontend_ok) fprintf(stderr, "PASS159_ORDERED_TENSOR_FRONTEND_NOT_VERIFIED\n");
    return frontend_ok ? 0 : 1;
}

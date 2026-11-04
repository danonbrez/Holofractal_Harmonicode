/* Pass 220 nucleus-5 source -> inherited Pass159 frontend and diagnostic interpreter.
 * No canonical VM81 commit: verifies native parser, graph, held receipt and replay.
 * Input is supplied as a byte-exact HARMONICODE circuit source file.
 */
#include "hhs_pass159_api.h"
#include "hhs159_internal.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_source(const char *path, uint8_t **out, size_t *len) {
    FILE *f = fopen(path, "rb");
    long count;
    uint8_t *bytes;
    if (f == NULL) return 0;
    if (fseek(f, 0, SEEK_END) != 0 || (count = ftell(f)) <= 0 ||
        count > 1048576L || fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    bytes = (uint8_t *)malloc((size_t)count);
    if (bytes == NULL) { fclose(f); return 0; }
    if (fread(bytes, 1, (size_t)count, f) != (size_t)count) {
        free(bytes); fclose(f); return 0;
    }
    fclose(f);
    *out = bytes; *len = (size_t)count;
    return 1;
}

static int read_hash216(const void *artifact, char value[HHS159_HASH216_LENGTH + 1U]) {
    memset(value, 0, HHS159_HASH216_LENGTH + 1U);
    HHS159MutableByteSpan span = {
        (uint8_t *)value, HHS159_HASH216_LENGTH, 0U
    };
    return hhs159_get_hash216(artifact, &span) == HHS159_STATUS_OK &&
           span.size_written == HHS159_HASH216_LENGTH;
}

static int hash216(const void *artifact) {
    char digest[HHS159_HASH216_LENGTH + 1U];
    return read_hash216(artifact, digest);
}

int main(int argc, char **argv) {
    static const uint8_t source_name[] = "pass220-nucleus5-ABP";
    static const uint8_t utf8[] = "UTF-8";
    HHS159ContextConfig cfg = {0};
    HHS159SourceOpenOptions opts = {0};
    HHS159Context *ctx = NULL;
    HHS159Source *src = NULL;
    HHS159IR *tokens = NULL, *hir = NULL, *vmir = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Receipt *receipt = NULL, *replay_receipt = NULL;
    HHS159ExecutionOptions execution = {0};
    HHS159CompareResult compare = {0};
    HHS159ByteSpan span;
    HHS159Status status = HHS159_STATUS_INVALID_STATE;
    uint8_t *bytes = NULL;
    size_t size = 0U;
    int ok = 0;
    uint64_t observed_steps = 0U;
    char observed_semantic_root[HHS159_HASH216_LENGTH + 1U] = {0};
    uint32_t observed_commit = 0U;
    uint32_t observed_fallback = 0U;
    char source_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char ast_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char graph_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char vmir_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char receipt_id[HHS159_HASH216_LENGTH + 1U] = {0};
    if (argc != 2 || !read_source(argv[1], &bytes, &size))
        goto cleanup;

    cfg.header.struct_size = (uint32_t)sizeof(cfg);
    cfg.header.struct_version = HHS159_STRUCT_VERSION_1;
    cfg.max_source_bytes = UINT64_C(1048576);
    cfg.max_tokens = UINT64_C(200000);
    cfg.max_nesting = UINT64_C(4096);
    cfg.max_output_bytes = UINT64_C(4194304);
    cfg.flags = HHS159_FLAG_ORDERED;
    status = hhs159_context_create(&cfg, &ctx);
    if (status != HHS159_STATUS_OK) goto cleanup;

    opts.header.struct_size = (uint32_t)sizeof(opts);
    opts.header.struct_version = HHS159_STRUCT_VERSION_1;
    opts.source_name.data = source_name;
    opts.source_name.size = sizeof(source_name) - 1U;
    opts.encoding.data = utf8;
    opts.encoding.size = sizeof(utf8) - 1U;
    opts.flags = HHS159_FLAG_ORDERED;
    opts.preserve_bom = 1U;
    span.data = bytes; span.size = size;
    status = hhs159_source_open_bytes(ctx, span, &opts, &src);
    if (status != HHS159_STATUS_OK || !read_hash216(src, source_id)) goto cleanup;
    status = hhs159_lex(ctx, src, &tokens);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(tokens) != HHS159_ARTIFACT_TOKEN_STREAM)
        goto cleanup;
    status = hhs159_parse_cst(ctx, src, &cst);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(cst) != HHS159_ARTIFACT_CST)
        goto cleanup;
    status = hhs159_build_ast(ctx, cst, &ast);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(ast) != HHS159_ARTIFACT_AST ||
        !read_hash216(ast, ast_id)) goto cleanup;
    status = hhs159_typecheck(ctx, ast, &types);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV)
        goto cleanup;
    status = hhs159_build_constraint_graph(ctx, ast, types, &graph);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(graph) != HHS159_ARTIFACT_CONSTRAINT_GRAPH ||
        !read_hash216(graph, graph_id)) goto cleanup;
    status = hhs159_lower_hir(ctx, ast, types, graph, &hir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(hir) != HHS159_ARTIFACT_HIR)
        goto cleanup;
    status = hhs159_lower_vmir(ctx, hir, &vmir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(vmir) != HHS159_ARTIFACT_VMIR ||
        !read_hash216(vmir, vmir_id)) goto cleanup;
    /* Invoke the existing Pass159 interpreter without canonical commit.
     * Current VMIR execution may use a fixed EXACT_PROGRAM: these receipts
     * demonstrate ABI/path and replay health, not tensor semantic closure.
     */
    status = hhs159_interpreter_create(ctx, &interpreter);
    if (status != HHS159_STATUS_OK) goto cleanup;
    execution.header.struct_size = (uint32_t)sizeof(execution);
    execution.header.struct_version = HHS159_STRUCT_VERSION_1;
    execution.mode = HHS159_MODE_EXECUTE_AND_HOLD;
    execution.commit_policy = 0U;
    execution.max_vm81_steps = UINT64_C(1000000);
    execution.max_recursion = UINT64_C(4096);
    execution.max_output_bytes = UINT64_C(4194304);
    status = hhs159_interpret(interpreter, src, &execution, &receipt);
    if (status != HHS159_STATUS_OK || receipt == NULL ||
        hhs159_artifact_kind(receipt) != HHS159_ARTIFACT_RECEIPT ||
        !read_hash216(receipt, receipt_id)) goto cleanup;
    observed_steps = receipt->vm81_steps;
    observed_commit = receipt->committed;
    observed_fallback = receipt->fallback_used;
    memcpy(observed_semantic_root, receipt->semantic_root,
           sizeof(observed_semantic_root));
    if (receipt->committed != 0U || receipt->fallback_used != 0U ||
        receipt->status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_interpreter_replay(interpreter, receipt, &replay_receipt);
    if (status != HHS159_STATUS_OK || replay_receipt == NULL ||
        hhs159_artifact_kind(replay_receipt) != HHS159_ARTIFACT_RECEIPT ||
        !hash216(replay_receipt)) goto cleanup;
    compare.header.struct_size = (uint32_t)sizeof(compare);
    compare.header.struct_version = HHS159_STRUCT_VERSION_1;
    status = hhs159_compare_interpreter_compiler(ctx, src, &execution, &compare);
    if (status != HHS159_STATUS_OK ||
        compare.status != HHS159_STATUS_OK ||
        compare.matched != 1U || compare.fallback_used != 0U)
        goto cleanup;
    ok = 1;
cleanup:
    if (replay_receipt != NULL) hhs159_receipt_release(replay_receipt);
    if (receipt != NULL) hhs159_receipt_release(receipt);
    if (interpreter != NULL) hhs159_interpreter_release(interpreter);
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (src != NULL) hhs159_source_release(src);
    if (ctx != NULL) hhs159_context_release(ctx);
    free(bytes);
    if (!ok) {
        fprintf(stderr, "NUCLEUS5_PASS159_FRONTEND_REJECTED status=%d %s\n",
                (int)status, hhs159_status_string(status));
        return 1;
    }
    printf("SOURCE_HASH216=%s\n", source_id);
    printf("AST_HASH216=%s\n", ast_id);
    printf("CONSTRAINT_HASH216=%s\n", graph_id);
    printf("VMIR_HASH216=%s\n", vmir_id);
    printf("HELD_RECEIPT_HASH216=%s\n", receipt_id);
    printf("HELD_SEMANTIC_ROOT_HASH216=%s\n", observed_semantic_root);
    printf("HELD_VM81_STEPS=%llu\n", (unsigned long long)observed_steps);
    printf("HELD_COMMITTED=%u\n", observed_commit);
    printf("HELD_FALLBACK=%u\n", observed_fallback);
    puts("NUCLEUS5_PASS159_FRONTEND_HELD_INTERPRET_REPLAY_PASS (NO_CANONICAL_TENSOR_CLOSURE)");
    return 0;
}

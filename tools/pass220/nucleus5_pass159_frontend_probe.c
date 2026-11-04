/* Pass 220 nucleus-5 source -> inherited Pass159 exact frontend.
 * No interpreter/VM81 commit: validates the actual native parser and graph.
 * Input is supplied as a byte-exact HARMONICODE circuit source file.
 */
#include "hhs_pass159_api.h"
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

static int hash216(const void *artifact) {
    char value[HHS159_HASH216_LENGTH + 1U] = {0};
    HHS159MutableByteSpan span = {
        (uint8_t *)value, HHS159_HASH216_LENGTH, 0U
    };
    return hhs159_get_hash216(artifact, &span) == HHS159_STATUS_OK &&
           span.size_written == HHS159_HASH216_LENGTH;
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
    HHS159ByteSpan span;
    HHS159Status status = HHS159_STATUS_INVALID_STATE;
    uint8_t *bytes = NULL;
    size_t size = 0U;
    int ok = 0;
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
    if (status != HHS159_STATUS_OK || !hash216(src)) goto cleanup;
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
        !hash216(ast)) goto cleanup;
    status = hhs159_typecheck(ctx, ast, &types);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV)
        goto cleanup;
    status = hhs159_build_constraint_graph(ctx, ast, types, &graph);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(graph) != HHS159_ARTIFACT_CONSTRAINT_GRAPH ||
        !hash216(graph)) goto cleanup;
    status = hhs159_lower_hir(ctx, ast, types, graph, &hir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(hir) != HHS159_ARTIFACT_HIR)
        goto cleanup;
    status = hhs159_lower_vmir(ctx, hir, &vmir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(vmir) != HHS159_ARTIFACT_VMIR ||
        !hash216(vmir)) goto cleanup;
    ok = 1;
cleanup:
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
    puts("NUCLEUS5_PASS159_SOURCE_GRAPH_VMIR_PASS");
    return 0;
}

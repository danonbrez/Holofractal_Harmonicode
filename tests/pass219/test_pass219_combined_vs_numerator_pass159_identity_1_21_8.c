#include "hhs_pass159_api.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HASH_N HHS159_HASH216_LENGTH

typedef struct PipelineIds {
    char source[HASH_N + 1U];
    char tokens[HASH_N + 1U];
    char cst[HASH_N + 1U];
    char ast[HASH_N + 1U];
    char types[HASH_N + 1U];
    char graph[HASH_N + 1U];
    char hir[HASH_N + 1U];
    char vmir[HASH_N + 1U];
} PipelineIds;

static int read_file(const char *path, uint8_t **out, size_t *out_size) {
    FILE *fp = NULL;
    long n;
    uint8_t *p = NULL;
    if (path == NULL || out == NULL || out_size == NULL)
        return 0;
    fp = fopen(path, "rb");
    if (fp == NULL)
        return 0;
    if (fseek(fp, 0L, SEEK_END) != 0 || (n = ftell(fp)) < 0 ||
        fseek(fp, 0L, SEEK_SET) != 0) {
        fclose(fp);
        return 0;
    }
    p = (uint8_t *)malloc((size_t)n);
    if (p == NULL) {
        fclose(fp);
        return 0;
    }
    if (fread(p, 1U, (size_t)n, fp) != (size_t)n) {
        free(p);
        fclose(fp);
        return 0;
    }
    fclose(fp);
    *out = p;
    *out_size = (size_t)n;
    return 1;
}

static int copy_hash(const void *handle, char out[HASH_N + 1U]) {
    HHS159MutableByteSpan span;
    memset(out, 0, HASH_N + 1U);
    span.data = (uint8_t *)out;
    span.capacity = HASH_N;
    span.size_written = 0U;
    if (hhs159_get_hash216(handle, &span) != HHS159_STATUS_OK ||
        span.size_written != HASH_N)
        return 0;
    out[HASH_N] = '\0';
    return 1;
}

static int build_ids(HHS159Context *context, const char *path, PipelineIds *ids) {
    static const uint8_t source_name[] = "pass219-i1218-identity-census";
    static const uint8_t encoding[] = "UTF-8";
    uint8_t *bytes = NULL;
    size_t count = 0U;
    HHS159SourceOpenOptions options;
    HHS159ByteSpan source_span;
    HHS159Source *source = NULL;
    HHS159IR *tokens = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159IR *hir = NULL;
    HHS159IR *vmir = NULL;
    int ok = 0;

    if (!read_file(path, &bytes, &count))
        goto cleanup;
    memset(ids, 0, sizeof(*ids));
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
    source_span.size = count;

    if (hhs159_source_open_bytes(context, source_span, &options, &source) != HHS159_STATUS_OK ||
        !copy_hash(source, ids->source))
        goto cleanup;
    if (hhs159_lex(context, source, &tokens) != HHS159_STATUS_OK ||
        !copy_hash(tokens, ids->tokens))
        goto cleanup;
    if (hhs159_parse_cst(context, source, &cst) != HHS159_STATUS_OK ||
        !copy_hash(cst, ids->cst))
        goto cleanup;
    if (hhs159_build_ast(context, cst, &ast) != HHS159_STATUS_OK ||
        !copy_hash(ast, ids->ast))
        goto cleanup;
    if (hhs159_typecheck(context, ast, &types) != HHS159_STATUS_OK ||
        !copy_hash(types, ids->types))
        goto cleanup;
    if (hhs159_build_constraint_graph(context, ast, types, &graph) != HHS159_STATUS_OK ||
        !copy_hash(graph, ids->graph))
        goto cleanup;
    if (hhs159_lower_hir(context, ast, types, graph, &hir) != HHS159_STATUS_OK ||
        !copy_hash(hir, ids->hir))
        goto cleanup;
    if (hhs159_lower_vmir(context, hir, &vmir) != HHS159_STATUS_OK ||
        !copy_hash(vmir, ids->vmir))
        goto cleanup;
    ok = 1;

cleanup:
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (source != NULL) hhs159_source_release(source);
    free(bytes);
    return ok;
}

static int same(const char a[HASH_N + 1U], const char b[HASH_N + 1U]) {
    return memcmp(a, b, HASH_N) == 0;
}

int main(void) {
    const char *numerator =
        "contracts/pass219/PASS_219_MONOLITHIC_UQCEL_NATIVE_VERBATIM_1_20.harmonicode";
    const char *combined =
        "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode";
    HHS159ContextConfig config;
    HHS159Context *context = NULL;
    PipelineIds n;
    PipelineIds c;
    int source_equal, tokens_equal, cst_equal, ast_equal;
    int types_equal, graph_equal, hir_equal, vmir_equal;

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
        return 1;
    if (!build_ids(context, numerator, &n) || !build_ids(context, combined, &c)) {
        hhs159_context_release(context);
        return 1;
    }

    source_equal = same(n.source, c.source);
    tokens_equal = same(n.tokens, c.tokens);
    cst_equal = same(n.cst, c.cst);
    ast_equal = same(n.ast, c.ast);
    types_equal = same(n.types, c.types);
    graph_equal = same(n.graph, c.graph);
    hir_equal = same(n.hir, c.hir);
    vmir_equal = same(n.vmir, c.vmir);

    printf(
        "PASS219 I121.8 identity census: "
        "source_equal=%d tokens_equal=%d cst_equal=%d ast_equal=%d "
        "types_equal=%d graph_equal=%d hir_equal=%d vmir_equal=%d\n",
        source_equal, tokens_equal, cst_equal, ast_equal,
        types_equal, graph_equal, hir_equal, vmir_equal);

    hhs159_context_release(context);

    /* The denominator must remain visible at least through the ordered graph.
     * HIR/VMIR equality is reported as diagnostic evidence rather than treated
     * as a defect in frozen Pass159 on this thread. */
    if (source_equal || tokens_equal || cst_equal || ast_equal || graph_equal)
        return 1;
    return 0;
}

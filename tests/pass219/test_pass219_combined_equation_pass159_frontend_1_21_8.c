#include "hhs_pass159_api.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EXPECTED_SOURCE_BYTES 632U

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
    static const uint8_t source_name[] = "pass219-combined-equation-1.21.8";
    static const uint8_t encoding[] = "UTF-8";
    const char *path =
        "contracts/pass219/PASS_219_COMBINED_QUOTIENT_MATRIX_POWER_NATIVE_1_21_8.harmonicode";
    uint8_t *bytes = NULL;
    size_t byte_count = 0U;
    HHS159ContextConfig config;
    HHS159SourceOpenOptions options;
    HHS159ByteSpan source_span;
    HHS159Context *context = NULL;
    HHS159Source *source = NULL;
    HHS159IR *tokens = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159IR *hir = NULL;
    HHS159IR *vmir = NULL;
    char source_hash[HHS159_HASH216_LENGTH + 1U];
    char ast_hash[HHS159_HASH216_LENGTH + 1U];
    char graph_hash[HHS159_HASH216_LENGTH + 1U];
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
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV)
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
     * deterministic, but this test deliberately does not interpret/commit. */
    if (source_hash[0] == '\0' || ast_hash[0] == '\0' ||
        graph_hash[0] == '\0' || vmir_hash[0] == '\0')
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
    if (context != NULL) hhs159_context_release(context);
    free(bytes);

    if (!ok) {
        fprintf(stderr, "PASS219 I121.8 combined Pass159 frontend: FAIL\n");
        return 1;
    }
    puts("PASS219 I121.8 combined Pass159 frontend: PASS");
    return 0;
}

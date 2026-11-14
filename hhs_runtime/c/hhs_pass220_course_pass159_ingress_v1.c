#include "hhs_pass220_course_pass159_ingress_v1.h"
#include "hhs_pass220_course_module_lines_v1.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

HHSExactStatus hhs_exact_pass220_course_module_source(
    uint32_t module_number,
    const char *course_file,
    uint8_t *out_bytes,
    size_t out_capacity,
    size_t *out_size
) {
    FILE *fp = NULL;
    uint8_t *source = NULL;
    long file_length;
    size_t size, i, line, begin = SIZE_MAX, end = SIZE_MAX;
    const uint32_t start = module_number < 191U
        ? hhs_course_module_start_lines[module_number] : 0U;
    const uint32_t stop = module_number < 190U
        ? hhs_course_module_start_lines[module_number + 1U] : UINT32_MAX;
    HHSExactStatus status = HHS_EXACT_STATUS_INVALID_ARGUMENT;

    if (out_size == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *out_size = 0U;
    if (module_number >= 191U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (course_file == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    fp = fopen(course_file, "rb");
    if (fp == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (fseek(fp, 0L, SEEK_END) != 0 || (file_length = ftell(fp)) < 0 ||
        fseek(fp, 0L, SEEK_SET) != 0)
        goto cleanup;
    size = (size_t)file_length;
    if (size == 0U)
        goto cleanup;
    source = (uint8_t *)malloc(size);
    if (source == NULL || fread(source, 1U, size, fp) != size)
        goto cleanup;

    line = 1U;
    for (i = 0U; i < size; ++i) {
        if (line == start && begin == SIZE_MAX)
            begin = i;
        if (line == stop && end == SIZE_MAX) {
            end = i;
            break;
        }
        if (source[i] == (uint8_t)'\n')
            ++line;
    }
    if (begin == SIZE_MAX)
        goto cleanup;
    if (end == SIZE_MAX)
        end = size;
    if (end <= begin)
        goto cleanup;
    *out_size = end - begin;
    if (out_bytes == NULL || out_capacity < *out_size) {
        status = HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
        goto cleanup;
    }
    memcpy(out_bytes, source + begin, *out_size);
    status = HHS_EXACT_STATUS_OK;

cleanup:
    free(source);
    fclose(fp);
    return status;
}

static HHS159Status hhs_course_hash216(
    const void *artifact,
    char output[HHS159_HASH216_LENGTH + 1U]
) {
    HHS159MutableByteSpan span;
    HHS159Status status;
    memset(output, 0, HHS159_HASH216_LENGTH + 1U);
    span.data = (uint8_t *)output;
    span.capacity = HHS159_HASH216_LENGTH;
    span.size_written = 0U;
    status = hhs159_get_hash216(artifact, &span);
    if (status != HHS159_STATUS_OK)
        return status;
    if (span.size_written != HHS159_HASH216_LENGTH)
        return HHS159_STATUS_HASH_MISMATCH;
    output[HHS159_HASH216_LENGTH] = '\0';
    return HHS159_STATUS_OK;
}

HHS159Status hhs_exact_pass220_course_module_pass159_vmir(
    uint32_t module_number,
    const char *course_file,
    HHS159MutableByteSpan *out_vmir,
    char source_hash216[HHS159_HASH216_LENGTH + 1U],
    char vmir_hash216[HHS159_HASH216_LENGTH + 1U]
) {
    static const uint8_t name[] = "HARMONICODE-course-module";
    static const uint8_t encoding[] = "UTF-8";
    HHS159ContextConfig config = {0};
    HHS159SourceOpenOptions options = {0};
    HHS159ByteSpan bytes;
    HHS159Context *ctx = NULL;
    HHS159Source *source = NULL;
    HHS159IR *tokens = NULL, *hir = NULL, *vmir = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    uint8_t *buffer = NULL;
    size_t size = 0U;
    HHSExactStatus extracted;
    HHS159Status status = HHS159_STATUS_INVALID_ARGUMENT;

    if (out_vmir == NULL || source_hash216 == NULL || vmir_hash216 == NULL)
        return status;
    out_vmir->size_written = 0U;
    memset(source_hash216, 0, HHS159_HASH216_LENGTH + 1U);
    memset(vmir_hash216, 0, HHS159_HASH216_LENGTH + 1U);
    extracted = hhs_exact_pass220_course_module_source(
        module_number, course_file, NULL, 0U, &size);
    if (extracted != HHS_EXACT_STATUS_BUFFER_TOO_SMALL)
        return HHS159_STATUS_INVALID_ARGUMENT;
    buffer = (uint8_t *)malloc(size);
    if (buffer == NULL)
        return HHS159_STATUS_OUT_OF_MEMORY;
    extracted = hhs_exact_pass220_course_module_source(
        module_number, course_file, buffer, size, &size);
    if (extracted != HHS_EXACT_STATUS_OK)
        goto cleanup;

    config.header.struct_size = sizeof(config);
    config.header.struct_version = HHS159_STRUCT_VERSION_1;
    config.max_source_bytes = UINT64_C(1048576);
    config.max_tokens = UINT64_C(200000);
    config.max_nesting = UINT64_C(4096);
    config.max_output_bytes = UINT64_C(4194304);
    config.flags = HHS159_FLAG_ORDERED;
    status = hhs159_context_create(&config, &ctx);
    if (status != HHS159_STATUS_OK) goto cleanup;

    options.header.struct_size = sizeof(options);
    options.header.struct_version = HHS159_STRUCT_VERSION_1;
    options.source_name.data = name;
    options.source_name.size = sizeof(name) - 1U;
    options.encoding.data = encoding;
    options.encoding.size = sizeof(encoding) - 1U;
    options.preserve_bom = 1U;
    options.flags = HHS159_FLAG_ORDERED;
    bytes.data = buffer;
    bytes.size = size;
    status = hhs159_source_open_bytes(ctx, bytes, &options, &source);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs_course_hash216(source, source_hash216);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_lex(ctx, source, &tokens);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_parse_cst(ctx, source, &cst);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_build_ast(ctx, cst, &ast);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_typecheck(ctx, ast, &types);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_build_constraint_graph(ctx, ast, types, &graph);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_lower_hir(ctx, ast, types, graph, &hir);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_lower_vmir(ctx, hir, &vmir);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs_course_hash216(vmir, vmir_hash216);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_serialize(vmir, out_vmir);

cleanup:
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (source != NULL) hhs159_source_release(source);
    if (ctx != NULL) hhs159_context_release(ctx);
    free(buffer);
    return status;
}
